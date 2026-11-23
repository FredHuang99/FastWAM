"""RoboMME counting demos -> our intermediate per-episode format (11-23, Opus; plan R0 section 3 "data conversion",
step 1; user 11-22 chose option 1 "as planned"). Runs inside RoboMME's own image robomme:582ab30 (numpy + h5py; the
5090 launcher robomme_convert_5090.sh), CPU only. Reads record_dataset_<Task>.h5 read-only; writes only under --out;
never deletes; resumable (a finished episode is never rewritten).

Per task (default PickXtimes and BinFill: their counts show in gripper events; SwingXtimes waits on Fable's event
decision), per episode of the HDF5 (RoboMME's own layout, doc/h5_data_format.md; keys timestep_<i>[_dup<k>] ordered by
(i, k); steps of the conditioning video, info/is_video_demo, are skipped as RoboMME's dataset_replay.py does):
  <out>/<Task>/episode_<k:07d>.npz   front_rgb, wrist_rgb uint8 [T, H, W, 3] (the recorded 256 x 256 unless --size);
                                     joint_state [T, 7], gripper_state [T, 2], is_gripper_close [T], eef_state [T, 6]
                                     (x y z roll pitch yaw); joint_action [T, 8] (7 joints + gripper, -1 close / +1 open),
                                     eef_action [T, 7] (pose + gripper), action_valid [T] (False where the recorder wrote
                                     "None"; those rows are NaN); is_subgoal_boundary [T], is_completed [T];
                                     source_step [T] (the HDF5 timestep index of each row)
  <out>/<Task>/episode_<k:07d>.json  goal (task_goal[0]), goals (all), count N (h5_events.count_of), seed, difficulty,
                                     robomme_split (the seed found in RoboMME's env_metadata train / val / test lists),
                                     length, skipped video-demo steps, subgoal runs [[start, end, text]] of the simple and
                                     grounded subgoals (kept for reference; training does not use them). Written last =
                                     the episode is complete.
  <out>/events_<Task>.json           {"rule", "episodes"}: our rule unchanged (fullft events.py, EventRule()), single arm
                                     = arm 0 (arm 1 a still dummy), gripper = (joint_action[7] + 1) / 2, height =
                                     eef_state z; exactly h5_events.py's reading. Frames index the rows above.
  <out>/RECORDS.json                 one row per complete episode: episode_id "<Task>/episode_<k:07d>", task, split
                                     (= robomme_split for now; the hold-out for validation is chosen at encoding), N,
                                     length, seed, difficulty, file
  <out>/IDENTITY.json                sources (path, bytes, sha256), this script's sha256, --commit, parameters
Images stay at the recorded 256 x 256 by default: Fast-WAM's LIBERO base was trained with ToTensor -> torchvision
Resize([224, 224]) on float tensors (configs/data/libero_2cam.yaml), so the encoding step applies that same transform;
--size 224 resizes here instead (torch bilinear with antialias, the operation torchvision's Resize runs, then rounded
to uint8).
  uv run --no-sync python /tools/robomme_convert.py --data /data --out /out --metadata /app/src/robomme/env_metadata
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m                      # dataclasses need the module registered
    spec.loader.exec_module(m)
    return m


if not (HERE / "events.py").exists():          # the launcher copies events.py, h5_events.py and this file together
    raise SystemExit(f"no events.py next to {Path(__file__).name} (copy src/fastwam/fullft/events.py here)")
events_mod = _module("events", "events.py")
h5_events = _module("h5_events", "h5_events.py")


def step_key(k: str):
    parts = k.split("_")
    return int(parts[1]), int(parts[2][3:]) if len(parts) > 2 and parts[2].startswith("dup") else 0


def as_str(raw) -> str:
    if isinstance(raw, np.ndarray):
        raw = raw.reshape(-1)[0] if raw.size else ""
    if isinstance(raw, (bytes, np.bytes_)):
        return raw.decode("utf-8", errors="replace")
    return str(raw)


def flag(ts, key) -> bool:
    info = ts.get("info")
    return bool(np.reshape(np.asarray(info[key][()]), -1)[0]) if info is not None and key in info else False


def vector(ds, n):
    """A numeric dataset as float32 [n]; None when the recorder wrote a string ("None")."""
    v = ds[()]
    if isinstance(v, (bytes, str, np.bytes_)) or (isinstance(v, np.ndarray) and v.dtype.kind in "OSU"):
        return None
    v = np.asarray(v, dtype=np.float32).reshape(-1)
    if v.size != n:
        raise ValueError(f"{ds.name}: {v.size} numbers, expected {n}")
    return v


def runs(texts):
    out = []
    for i, t in enumerate(texts):
        if out and out[-1][2] == t:
            out[-1][1] = i
        else:
            out.append([i, i, t])
    return out


def resize(frames: np.ndarray, size: int) -> np.ndarray:
    import torch
    import torch.nn.functional as F
    x = torch.from_numpy(frames).permute(0, 3, 1, 2).float() / 255.0
    y = F.interpolate(x, size=(size, size), mode="bilinear", align_corners=False, antialias=True)
    return (y.clamp(0, 1) * 255.0).round().to(torch.uint8).permute(0, 2, 3, 1).numpy()


def split_table(metadata: Path, task: str):
    out = {}
    for split in ("train", "val", "test"):
        f = metadata / split / f"record_dataset_{task}_metadata.json"
        if f.exists():
            for r in json.loads(f.read_text())["records"]:
                out.setdefault(int(r["seed"]), split)
    return out


def sha256(path: Path, block=1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(block)
            if not b:
                return h.hexdigest()
            h.update(b)


def convert_episode(task: str, ep, size: int):
    keys = sorted((k for k in ep.keys() if k.startswith("timestep_")), key=step_key)
    cols = {k: [] for k in ("front_rgb", "wrist_rgb", "joint_state", "gripper_state", "is_gripper_close", "eef_state",
                            "joint_action", "eef_action", "action_valid", "is_subgoal_boundary", "is_completed",
                            "source_step")}
    simple, grounded, skipped = [], [], 0
    for k in keys:
        ts = ep[k]
        if flag(ts, "is_video_demo"):
            skipped += 1
            continue
        obs, act = ts["obs"], ts["action"]
        cols["front_rgb"].append(np.asarray(obs["front_rgb"][()], dtype=np.uint8))
        cols["wrist_rgb"].append(np.asarray(obs["wrist_rgb"][()], dtype=np.uint8))
        cols["joint_state"].append(vector(obs["joint_state"], 7))
        cols["gripper_state"].append(vector(obs["gripper_state"], 2))
        cols["is_gripper_close"].append(bool(np.reshape(np.asarray(obs["is_gripper_close"][()]), -1)[0]))
        cols["eef_state"].append(vector(obs["eef_state"], 6))
        ja = vector(act["joint_action"], 8) if "joint_action" in act else None
        ea = vector(act["eef_action"], 7) if "eef_action" in act else None
        ok = ja is not None and ea is not None
        cols["joint_action"].append(ja if ja is not None else np.full(8, np.nan, np.float32))
        cols["eef_action"].append(ea if ea is not None else np.full(7, np.nan, np.float32))
        cols["action_valid"].append(ok)
        cols["is_subgoal_boundary"].append(flag(ts, "is_subgoal_boundary"))
        cols["is_completed"].append(flag(ts, "is_completed"))
        cols["source_step"].append(step_key(k)[0])
        info = ts.get("info")
        simple.append(as_str(info["simple_subgoal"][()]) if info is not None and "simple_subgoal" in info else "")
        grounded.append(as_str(info["grounded_subgoal"][()]) if info is not None and "grounded_subgoal" in info else "")
    if not cols["front_rgb"]:
        raise ValueError("no steps left after skipping the video-demo steps")
    arrays = {k: np.stack(v) if k in ("front_rgb", "wrist_rgb", "joint_state", "gripper_state", "eef_state",
                                       "joint_action", "eef_action") else np.asarray(v)
              for k, v in cols.items()}
    if size:
        arrays["front_rgb"], arrays["wrist_rgb"] = resize(arrays["front_rgb"], size), resize(arrays["wrist_rgb"], size)
    # events: h5_events.py's reading (gripper command of the action; invalid action rows hold the last command)
    cmd, last = [], 1.0
    for ok, a in zip(arrays["action_valid"], arrays["joint_action"]):
        last = (float(a[7]) + 1.0) / 2.0 if ok else last
        cmd.append([last, 1.0])
    z = arrays["eef_state"][:, :3].astype(np.float64)
    pos = np.stack([z, np.zeros_like(z)], axis=1)
    ev = events_mod.detect(np.asarray(cmd), pos, events_mod.EventRule())
    setup = ep["setup"]
    goals = [as_str(g) for g in np.reshape(np.asarray(setup["task_goal"][()], dtype=object), -1)] \
        if "task_goal" in setup else [""]
    meta = {"goal": goals[0], "goals": goals, "N": h5_events.count_of(task, goals[0]),
            "seed": int(np.reshape(np.asarray(setup["seed"][()]), -1)[0]) if "seed" in setup else None,
            "difficulty": as_str(setup["difficulty"][()]) if "difficulty" in setup else "",
            "length": int(len(arrays["front_rgb"])), "skipped_video_demo_steps": skipped,
            "invalid_action_rows": int((~arrays["action_valid"]).sum()),
            "simple_subgoal_runs": runs(simple), "grounded_subgoal_runs": runs(grounded)}
    return arrays, ev, meta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="folder with record_dataset_<Task>.h5")
    ap.add_argument("--out", required=True)
    ap.add_argument("--metadata", default="/app/src/robomme/env_metadata", help="RoboMME's env_metadata folder")
    ap.add_argument("--tasks", nargs="+", default=["PickXtimes", "BinFill"])
    ap.add_argument("--limit", type=int, default=0, help="first N episodes per task (0 = all)")
    ap.add_argument("--size", type=int, default=0, help="0 = keep the recorded size; 224 = resize here")
    ap.add_argument("--commit", default="", help="the repository commit the script came from (logged)")
    ap.add_argument("--min-free-gb", type=float, default=20.0)
    args = ap.parse_args(argv)
    data, out, metadata = Path(args.data), Path(args.out), Path(args.metadata)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    identity = {"script_sha256": sha256(Path(__file__)), "commit": args.commit, "tasks": args.tasks, "size": args.size,
                "limit": args.limit, "rule": str(events_mod.EventRule()), "sources": []}
    records = []
    for task in args.tasks:
        f = data / f"record_dataset_{task}.h5"
        if not f.exists():
            print(f"[convert] {task}: no {f}: skipped", flush=True)
            continue
        identity["sources"].append({"path": str(f), "bytes": f.stat().st_size, "sha256": sha256(f.resolve())})
        splits = split_table(metadata, task)
        if not splits:
            print(f"[convert] {task}: no RoboMME metadata under {metadata}: robomme_split = unknown", flush=True)
        folder = out / task
        folder.mkdir(exist_ok=True)
        events = {}
        with h5py.File(f, "r") as h:
            eps = sorted((k for k in h.keys() if k.startswith("episode_")), key=lambda k: int(k.split("_")[1]))
            if args.limit:
                eps = eps[:args.limit]
            done = written = 0
            for i, k in enumerate(eps):
                n = int(k.split("_")[1])
                stem = folder / f"episode_{n:07d}"
                npz, js = stem.with_suffix(".npz"), stem.with_suffix(".json")
                eid = f"{task}/episode_{n:07d}"
                if js.exists() and npz.exists():
                    meta = json.loads(js.read_text())
                    done += 1
                else:
                    arrays, ev, meta = convert_episode(task, h[k], args.size)
                    meta["robomme_split"] = splits.get(meta["seed"], "unknown")
                    meta["events"] = ev
                    tmp = stem.with_suffix(".tmp.npz")
                    np.savez_compressed(tmp, **arrays)
                    os.replace(tmp, npz)
                    js.write_text(json.dumps(meta) + "\n")      # last: the episode is complete
                    written += 1
                    if written == 1:
                        need = npz.stat().st_size * (len(eps) - i - 1) / 2 ** 30
                        free = shutil.disk_usage(out).free / 2 ** 30
                        print(f"[convert] {task}: first episode {npz.stat().st_size / 2 ** 20:.1f} MiB; about "
                              f"{need:.1f} GiB more for this task; {free:.0f} GiB free", flush=True)
                        if free - need < args.min_free_gb:
                            print(f"[convert] FAILED: not enough room (keep {args.min_free_gb} GiB free)", flush=True)
                            return 1
                events[eid] = meta["events"]
                records.append({"episode_id": eid, "task": task, "split": meta["robomme_split"],
                                "robomme_split": meta["robomme_split"], "N": meta["N"], "length": meta["length"],
                                "seed": meta["seed"], "difficulty": meta["difficulty"], "file": str(npz.relative_to(out))})
                if (i + 1) % 10 == 0 or i + 1 == len(eps):
                    print(f"[convert] {task}: {i + 1}/{len(eps)} episodes ({written} written, {done} already done); "
                          f"{time.time() - t0:.0f} s", flush=True)
        (out / f"events_{task}.json").write_text(json.dumps({"rule": str(events_mod.EventRule()),
                                                             "episodes": events}) + "\n")
        rows = [r for r in records if r["task"] == task]
        lengths = [r["length"] for r in rows]
        ns = {}
        for r in rows:
            ns[str(r["N"])] = ns.get(str(r["N"]), 0) + 1
        kinds = {kd: [sum(1 for e in events[r["episode_id"]] if e["kind"] == kd) for r in rows]
                 for kd in ("close", "open", "bottom", "top")}
        sp = {}
        for r in rows:
            sp[r["robomme_split"]] = sp.get(r["robomme_split"], 0) + 1
        mm = lambda xs: f"{min(xs)}/{int(np.median(xs))}/{max(xs)}" if xs else "-"     # noqa: E731
        print(f"[convert] {task}: {len(rows)} episodes, {sum(lengths)} frames (per episode {mm(lengths)}); "
              f"N {dict(sorted(ns.items()))}; splits {sp}; events per episode close {mm(kinds['close'])}, "
              f"open {mm(kinds['open'])}, bottom {mm(kinds['bottom'])}, top {mm(kinds['top'])}", flush=True)
    (out / "RECORDS.json").write_text(json.dumps(records, indent=0) + "\n")
    identity["seconds"] = round(time.time() - t0, 1)
    (out / "IDENTITY.json").write_text(json.dumps(identity, indent=1) + "\n")
    print(f"[convert] DONE: {len(records)} episodes -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
