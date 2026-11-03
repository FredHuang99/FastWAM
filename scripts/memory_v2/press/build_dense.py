"""Dense cache for a NEW task in the exact format of the two-task dense output (week plan v6 2.5, press_button).

memory_v2 reads cache/<episode>/encodings.pt (latent, video_latent, video_valid, text, text_valid, proprio, actions),
IDENTITY.json / RECORDS.json / WINDOWS.json / PREPARED.json and COMPLETE.json markers. Codex's build_cache only accepts
its authenticated two-task run, so this script repeats its encoding loop line by line, calling Codex's own, unmodified
functions (data_path.Raw / mosaic / window_indices, memory_s1 encoders and the released normalizer), and writes into a
NEW folder. Nothing under /restore-tmp/dense_joint_v1, /workspace/FastWAM/outputs or the two-task cache is written.

    # 1) parity: rebuild put_back_block/episode_0000000 into a scratch output and compare it with the two-task cache,
    #    then run memory_v2 on it (identity check, episode store, frozen base model, history features vs the existing
    #    features_dense_v1 file). Writes PARITY.json; exit code 0 only if every check passes.
    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/press/build_dense.py parity
    # 2) the new task (45 train / 5 val, seed-17 split), resumable:
    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/press/build_dense.py build --task press_button

Output (default): /workspace/FastWAM-memory2/outputs/memory_v2/press/dense_<task>_v1/
"""
import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys
import time
from collections import OrderedDict
from pathlib import Path

ROOT = Path(os.environ.get("FW_ROOT", "/workspace/FastWAM"))
CODE = Path("/restore-tmp/dense_joint_v1")
BASE = ROOT / "outputs/s1_dense_joint_h100_v1"
M = Path("/workspace/FastWAM-memory2")
O = Path(os.environ.get("MEMV2_OUT", str(M / "outputs/memory_v2")))
PRESS = O / "press"
BASE_FEATURES = O / "features_dense_v1"
PARITY_EPISODE = "put_back_block/episode_0000000"
SCHEMA = "memv2-dense-task-v1"


def setup():
    os.environ.setdefault("FW_ROOT", str(ROOT))
    if str(CODE) not in sys.path:
        sys.path.insert(0, str(CODE))
    import common      # noqa: E402  (dense_joint_v1, unmodified)
    import data_path   # noqa: E402
    return common, data_path


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def log(msg):
    print(f"[dense-task] {time.strftime('%F %T')} {msg}", flush=True)


# ============================================================================ records / windows / receipts
def make_record(common, path, task, split, raw_sha=None):
    from fastwam.memory_s1.data import read_episode, choose_instruction
    import numpy as np
    states, targets, cameras, kind, metadata, embedded = read_episode(path)
    instruction, source = choose_instruction(path, embedded)
    delta = np.abs(np.diff(targets, axis=0)) if len(targets) > 1 else np.zeros((1, 14), np.float32)
    return {"episode_id": f"{task}/{Path(path).stem}", "task": task, "raw": str(Path(path).resolve()),
            "raw_sha256": raw_sha or common.sha(path), "file": None, "length": int(len(states)),
            "camera_paths": list(cameras), "instruction": instruction, "instruction_sha": sha_text(instruction),
            "instruction_source": source, "source_kind": kind,
            "attributes": {"source_format": metadata.get("source_format", "RMBench"),
                           "source_path": metadata.get("source_path"),
                           "stored_frequency": metadata.get("stored_frequency")},
            "split": split,
            "joint_delta_abs_percentiles": np.percentile(delta, [0, 50, 90, 99, 100], axis=0).tolist()}


def make_windows(common, cfg, records, rows_per_train=2):
    """Validation windows in the two-task WINDOWS.json shape: every 16th anchor + gripper events, T=8, the dense
    evaluation phase. All val episodes and the first `rows_per_train` train episodes (as in the two-task output)."""
    import numpy as np
    from fastwam.memory_s1.data import read_episode
    from fastwam.memory_s1.history import evaluation_phase
    rows = []
    train_seen = 0
    for r in records:
        if r["split"] == "train":
            if train_seen >= rows_per_train:
                continue
            train_seen += 1
        _, targets, _, _, _, _ = read_episode(r["raw"] if Path(r["raw"]).is_absolute() else ROOT / r["raw"])
        events = []
        for side, col in (("left", 6), ("right", 13)):
            g = targets[:, col]
            events += [(int(t), f"{side}_close_{int(t)}") for t in np.flatnonzero((g[1:] < .5) & (g[:-1] >= .5)) + 1]
            events += [(int(t), f"{side}_release_{int(t)}") for t in np.flatnonzero((g[1:] >= .5) & (g[:-1] < .5)) + 1]
        anchors = sorted(set(range(0, r["length"], 16)) | {max(0, t - 8) for t, _ in events})
        phase = evaluation_phase(cfg, 8, r["episode_id"], "validation")
        for a in anchors:
            labels = (["initial"] if a == 0 else []) + [name for t, name in events if a <= t < a + 32]
            rows.append({"id": f"{r['episode_id']}:{a}", "episode_id": r["episode_id"], "task": r["task"],
                         "split": r["split"], "anchor": int(a), "T": 8, "phase": int(phase), "labels": labels})
    return rows


def prepare(common, out, records, task, note):
    """IDENTITY / RECORDS / WINDOWS / PLAN / PREPARED for a new output, derived from the two-task identity."""
    base = common.read(BASE / "IDENTITY.json")
    ident = copy.deepcopy(base)
    ident["schema"] = SCHEMA
    ident["recipe"] = dict(base["recipe"], tasks=[task], output=str(out),
                           scope=f"memory_v2 single-task dense cache ({task}); same encoders, image path and normalizer")
    ident["code"] = common.code()
    ident["encoder_software"] = common.encoder_software()
    ident["memory_v2"] = {"builder": "scripts/memory_v2/press/build_dense.py", "builder_sha256": common.sha(Path(__file__)),
                          "derived_from_identity": common.sig(base), "derived_from_output": str(BASE), "note": note}
    out.mkdir(parents=True, exist_ok=True)
    common.write(out / "IDENTITY.json", ident)
    common.write(out / "RECORDS.json", records)
    common.write(out / "WINDOWS.json", make_windows(common, ident["config"], records))
    n = sum(r["length"] for r in records if r["split"] == "train")
    common.write(out / "PLAN.json", {"training_anchors": n, "tasks": [task], "episodes": len(records),
                                     "note": "memory_v2 plans its own epochs; Codex's dense plans are not used"})
    names = ["IDENTITY.json", "RECORDS.json", "PLAN.json", "WINDOWS.json"]
    common.write(out / "PREPARED.json", {"files": {x: common.sha(out / x) for x in names}})
    return common.identity(out)


# ============================================================================ the encoding loop (= data_path.build_cache)
def encode(common, data_path, out, limit=None):
    import torch
    from fastwam.memory_s1.model import load_observation_encoders, encode_text
    from fastwam.memory_s1.common import ReleaseNormalizer
    identity = common.identity(out)
    cfg = common.read(out / "IDENTITY.json")["config"]
    records = common.read(out / "RECORDS.json")[:limit]
    vae, text, tokenizer = load_observation_encoders(cfg, torch.device("cuda:0"))
    norm = ReleaseNormalizer(cfg["paths"]["stats"])
    num = common.read(CODE / "recipe.json")["numerical"]
    total = sum(r["length"] for r in records)
    done = encoded = 0
    started = time.monotonic()
    for rec in records:
        d = data_path.paths(out, rec["episode_id"])
        marker = d / "COMPLETE.json"
        if marker.exists():
            m = common.read(marker)
            if m["identity"] != identity:
                raise ValueError(f"cache identity differs for {rec['episode_id']}: use a new output folder")
            common.verify(d, m["files"])
            done += rec["length"]
            continue
        d.mkdir(parents=True, exist_ok=True)
        raw = data_path.Raw(cfg, rec)
        try:
            latents, clips, masks = [], [], []
            with torch.no_grad():
                context, valid = encode_text(text, tokenizer, rec["instruction"], "cuda:0")
                images = OrderedDict()

                def frame(i):
                    if i not in images:
                        images[i] = data_path.mosaic(raw.images(i))
                    images.move_to_end(i)
                    while len(images) > 40:
                        images.popitem(last=False)
                    return images[i]
                max_prefix_error = 0.0
                for a in range(rec["length"]):
                    _, _, ids, pad = data_path.window_indices(a, rec["length"], raw.image_length)
                    video = torch.stack([frame(int(i)) for i in ids], dim=1)[None].to("cuda:0", torch.bfloat16)
                    z = vae.model.encode(video, vae.scale).detach()
                    single = vae.model.encode(video[:, :, :1], vae.scale).detach()
                    err = float((single.float() - z[:, :, :1].float()).abs().max())
                    max_prefix_error = max(max_prefix_error, err)
                    if not torch.allclose(single, z[:, :, :1], atol=num["vae_atol"], rtol=num["vae_rtol"]):
                        raise ValueError(f"causal VAE first-frame mismatch {rec['episode_id']}:{a}: {err}")
                    latents.append(single[0].cpu())
                    clips.append(z[0].cpu())
                    masks.append(torch.from_numpy(pad))
                    done += 1
                    encoded += 1
                    if a % 64 == 0:
                        el = time.monotonic() - started
                        log(f"{rec['episode_id']}:{a}  {done}/{total} frames, ETA {(total - done) * el / max(1, encoded) / 60:.0f} min")
            common.torch_save(d / "encodings.pt", {
                "identity": identity, "episode_id": rec["episode_id"],
                "latent": torch.stack(latents), "video_latent": torch.stack(clips), "video_valid": torch.stack(masks),
                "text": context[0].cpu(), "text_valid": valid[0].cpu(),
                "proprio": norm.normalize(torch.from_numpy(raw.states), "state"),
                "actions": norm.normalize(torch.from_numpy(raw.targets), "action")})
            check = torch.load(d / "encodings.pt", map_location="cpu", weights_only=True, mmap=True)
            if check["latent"].shape[0] != rec["length"] or not all(
                    bool(check[k].isfinite().all()) for k in ("latent", "video_latent", "text", "proprio", "actions")):
                raise ValueError("cache readback invalid")
            common.write(marker, {"identity": identity, "files": {"encodings.pt": common.sha(d / "encodings.pt")},
                                  "max_first_latent_difference": max_prefix_error})
            log(f"{rec['episode_id']}: cached ({rec['length']} frames)")
        finally:
            raw.close()
    del vae, text
    torch.cuda.empty_cache()
    common.write(out / "CACHE.json", {"passed": True, "episodes": len(records), "frames": total, "identity": identity,
                                      "minutes": round((time.monotonic() - started) / 60, 1)})
    return identity


# ============================================================================ parity against the two-task output
def compare(a, b, atol, rtol):
    import torch
    out = {}
    for k in ("latent", "video_latent", "video_valid", "text", "text_valid", "proprio", "actions"):
        x, y = a[k], b[k]
        row = {"shape": list(x.shape), "same_shape": x.shape == y.shape, "dtype": str(x.dtype)}
        if row["same_shape"]:
            row["exact"] = bool(torch.equal(x, y))
            if x.dtype.is_floating_point:
                row["max_abs"] = float((x.float() - y.float()).abs().max())
                row["close"] = bool(torch.allclose(x.float(), y.float(), atol=atol, rtol=rtol))
            else:
                row["close"] = row["exact"]
        else:
            row["exact"] = row["close"] = False
        out[k] = row
    return out


def cmd_parity(args):
    import torch
    common, data_path = setup()
    out = PRESS / "parity_put_v1"
    base_records = {r["episode_id"]: r for r in common.read(BASE / "RECORDS.json")}
    rec = dict(base_records[PARITY_EPISODE])
    result = {"episode": PARITY_EPISODE, "output": str(out), "checks": {}}
    if not (out / "PREPARED.json").exists():
        prepare(common, out, [rec], "put_back_block", "parity rebuild of one two-task episode")
    encode(common, data_path, out)
    num = common.read(CODE / "recipe.json")["numerical"]
    ours = torch.load(data_path.paths(out, PARITY_EPISODE) / "encodings.pt", map_location="cpu", weights_only=True)
    theirs = torch.load(data_path.paths(BASE, PARITY_EPISODE) / "encodings.pt", map_location="cpu", weights_only=True)
    cmp = compare(ours, theirs, num["vae_atol"], num["vae_rtol"])
    result["encodings_vs_two_task_cache"] = cmp
    result["checks"]["encodings"] = all(v["close"] for v in cmp.values()) and all(
        cmp[k]["exact"] for k in ("proprio", "actions", "video_valid", "text_valid"))
    log(f"encodings vs the two-task cache: {json.dumps({k: (v.get('exact'), v.get('max_abs')) for k, v in cmp.items()})}")
    # memory_v2 on the new output: identity check, episode store, the base model's own dataset, history features
    sys.path.insert(0, str(M / "src"))
    from fastwam.memory_v2 import dense
    spec = dense.DenseSpec.from_dict({"root": str(ROOT), "code": str(CODE), "output": str(out), "verify_identity": True})
    _, identity = dense.bind(spec)
    e = dense.EpisodeStore(spec)(PARITY_EPISODE)
    result["checks"]["memory_v2_bind_and_store"] = len(e["actions"]) == rec["length"]
    ab, info = dense.load_ab_model(spec, "source", "cuda:0")
    data = dense.ab_dataset(spec, identity, "cuda:0")
    row = dense.windows(spec)[3]
    b = data.at(dict(row, T=8, phase=dense.s1_phase(spec, row, 8)))
    result["checks"]["ab_dataset_at"] = tuple(b["latent"].shape[1:]) == tuple(ours["latent"].shape[1:])
    fdir = out / "features"
    store = dense.FeatureStore(fdir)
    store.build(ab, info, spec, [PARITY_EPISODE], batch=16, log=log)
    mine = torch.load(store.path(PARITY_EPISODE), map_location="cpu", weights_only=True).float()
    ref_path = BASE_FEATURES / (PARITY_EPISODE.replace("/", "_") + ".pt")
    if ref_path.exists():
        ref = torch.load(ref_path, map_location="cpu", weights_only=True).float()
        rel = float((mine - ref).flatten(1).norm(dim=1).max() / ref.flatten(1).norm(dim=1).min().clamp_min(1e-6))
        result["features_vs_features_dense_v1"] = {"max_abs": float((mine - ref).abs().max()), "max_relative_l2": rel}
        result["checks"]["features"] = rel <= 0.05            # latents may differ within the VAE tolerance (other GPU type)
        log(f"history features vs features_dense_v1: max relative L2 {rel:.2e}")
    else:
        result["checks"]["features"] = None
        log(f"no reference feature file {ref_path}: feature parity not checked")
    result["passed"] = all(v is not False for v in result["checks"].values())
    common.write(out / "PARITY.json", result)
    print(json.dumps(result, indent=1))
    print(f"PARITY: {'PASS' if result['passed'] else 'FAIL'} ({out / 'PARITY.json'})")
    sys.exit(0 if result["passed"] else 1)


def cmd_build(args):
    common, data_path = setup()
    raw_dir = Path(args.raw or PRESS / "demo_clean" / args.task / "aloha_agilex" / "data")
    out = Path(args.out or PRESS / f"dense_{args.task}_v1")
    if not (out / "PREPARED.json").exists():
        files = sorted(raw_dir.glob("*.hdf5"))
        if not files:
            raise SystemExit(f"no hdf5 under {raw_dir} (run press/fetch.py first)")
        marker = raw_dir.parent.parent / "DOWNLOAD.json"
        shas = (common.read(marker).get("hdf5_sha256") or {}) if marker.exists() else {}
        val = set(random.Random(17).sample(range(len(files)), args.val))
        records = [make_record(common, f, args.task, "val" if i in val else "train", shas.get(f.name))
                   for i, f in enumerate(files)]
        for f in files:                                 # the download receipt must still hold
            if f.name in shas and common.sha(f) != shas[f.name]:
                raise SystemExit(f"{f} changed since the download (sha256 differs from DOWNLOAD.json)")
        prepare(common, out, records, args.task, f"RMBench demo_clean {args.task}; DOWNLOAD.json {marker}")
        log(f"prepared {out}: {len(records)} episodes ({len(val)} val), {sum(r['length'] for r in records)} frames")
    encode(common, data_path, out, args.limit)
    log(f"done: {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("parity")
    b = sub.add_parser("build")
    b.add_argument("--task", default="press_button")
    b.add_argument("--raw")
    b.add_argument("--out")
    b.add_argument("--val", type=int, default=5)
    b.add_argument("--limit", type=int, default=None, help="encode only the first N records (smoke)")
    args = ap.parse_args()
    {"parity": cmd_parity, "build": cmd_build}[args.cmd](args)


if __name__ == "__main__":
    main()
