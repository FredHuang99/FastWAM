"""Bounded H100 query repair: zero updates, paired 64-update fits, gated prefixes."""
from __future__ import annotations

import argparse
import copy
import csv
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import traceback

from .grasp_bridge import (alive, checked_path, files, owned_popen, process, read,
                           sha, signature, stop_children, stop_owned_tree, verify, write)
from .memory_probe import archive_manifest, copy_verified, runtime, sources
from .memory_repair_math import MODES, QUERY_SCALE

STAGES = ("prepare", "zero", "fit", "physical", "report", "pack")
TOOLS = ("src/fastwam/memory_s1/memory_repair.py", "src/fastwam/memory_s1/memory_repair_worker.py",
         "src/fastwam/memory_s1/memory_repair_math.py", "scripts/memory_s1/portable/h100/memory_repair.sh",
         "configs/memory_s1/memory_repair_h100.json", "src/fastwam/memory_s1/memory_probe.py",
         "src/fastwam/memory_s1/memory_probe_worker.py", "src/fastwam/memory_s1/initial_intervention.py",
         "src/fastwam/memory_s1/initial_intervention_worker.py", "src/fastwam/memory_s1/grasp_bridge.py",
         "src/fastwam/memory_s1/eval_parallel.py", "src/fastwam/memory_s1/selection_runtime.py",
         "src/fastwam/memory_s1/simulator_backend.py", "src/fastwam/memory_s1/fused_evaluation.py",
         "scripts/memory_s1/sim_eval.py")
PROBE_CASES = ("put_train_initial", "swap_val_initial", "put_expert_080", "swap_expert_048")


def profile(root):
    spec = read(root / "configs/memory_s1/memory_repair_h100.json")
    if (spec["schema"] != "memory-query-repair-v1" or spec["machine"] != "h100"
            or spec["modes"] != list(MODES) or spec["query_scale"] != QUERY_SCALE
            or spec["updates_per_arm"] != 64 or spec["global_batch"] != 16
            or spec["micro_batch"] * spec["accumulation"] != 16 or spec["target_cap"] != 128
            or spec["evaluation_noises"] != ["production", "independent", "heldout"]
            or spec["checkpoint_every"] != 16):
        raise ValueError("Expected the approved two-arm 64-update, 32/16/10, 128-target protocol")
    for name in ("output", "probe_output", "probe_archive"):
        if not checked_path(root, spec[name]).is_relative_to(root / "outputs"):
            raise ValueError(f"Expected an outputs path: {name}")
    return spec


def stop_check(output):
    if (output / "STOP.json").exists():
        raise InterruptedError("Stopped at an update/case boundary; use explicit resume")


def simulator_runtime(cfg):
    import json
    command = [cfg["closed_loop"]["simulator_python"], "-B", "-c",
               "import json,sys,importlib.metadata as m; "
               "d={x.metadata['Name']:x.version for x in m.distributions() if x.metadata['Name']}; "
               "print(json.dumps({'python':sys.version,'packages':d},sort_keys=True))"]
    return json.loads(subprocess.check_output(command, text=True, timeout=30))


def require_completion(output, stage, identity, *, passed=False):
    path = output / stage / "COMPLETE.json"
    if not path.exists():
        raise FileNotFoundError(f"Complete prerequisite first: {path}")
    value = read(path)
    if value["identity"] != identity:
        raise ValueError(f"Stage identity changed: {path}")
    verify(path.parent, value["files"])
    if stage == "physical":
        if not value.get("external_files"):
            raise ValueError("Physical receipt lacks the actual two simulator case manifests")
        verify(output, value["external_files"])
    result = read(path.parent / "result.json")
    if passed:
        gate = result.get("gate", {})
        if not gate.get("passed", gate.get("eligible_for_physical", False)):
            raise ValueError(f"{stage} diagnostic gate blocked; inspect {path.parent / 'result.json'}. Report/pack remain available.")
    return result


def prepare(root, spec, output):
    import h5py
    import numpy as np
    import torch
    from PIL import Image
    from .common import fingerprint, seed_for
    from .data import official_decoder, read_episode
    from .history import resolve_online, select_ids
    old = checked_path(root, spec["probe_output"])
    manifest = archive_manifest(checked_path(root, spec["probe_archive"]), spec["probe_archive_sha256"], "FILES.json")
    verify(old, {name: manifest[name] for name in ("IDENTITY.json", "PREPARED.json", "probe/COMPLETE.json", "probe/result.json")})
    prior = read(old / "IDENTITY.json")
    require_completion(old, "probe", signature(prior))
    if sources(root) != prior["sources"]:
        raise ValueError("Production code changed since authenticated probe; do not bypass this identity check")
    now = runtime()
    if now != prior["runtime"]:
        raise ValueError("H100 model runtime/GPU identity differs from authenticated probe")
    cfg = copy.deepcopy(prior["config"])
    if cfg["history"].get("online_period") != 8 or cfg["history"].get("online_mode", "fixed") != "fixed":
        raise ValueError("Expected fixed T=8 and unchanged episode phase rule")
    prepared = Path(cfg["paths"]["prepared"])
    data_manifest, approval = read(prepared / "manifest.json"), read(prepared / "alignment_approved.json")
    if approval.get("approved") is not True or approval.get("manifest_sha") != fingerprint(data_manifest):
        raise ValueError("Prepared data lacks its matching authentic alignment approval")
    decoder_path = root / cfg["closed_loop"]["simulator_root"] / "data/decode_image_bit.py"
    if sha(decoder_path) != data_manifest["decoder_sha256"]:
        raise ValueError("Official image decoder differs from prepared manifest")
    bound = {"schema": spec["schema"], "protocol": spec, "config": cfg,
             "sources": sources(root), "tools": {name: sha(root / name) for name in TOOLS}, "runtime": now,
             "weights": prior["weights"], "resources": prior["resources"],
             "tokenizer_files": files(Path(cfg["paths"]["tokenizer"])),
             "probe_identity": signature(prior), "probe_archive_sha256": spec["probe_archive_sha256"],
             "data_manifest_sha256": sha(prepared / "manifest.json"), "alignment_sha256": sha(prepared / "alignment_approved.json"),
             "simulator_runtime": simulator_runtime(cfg),
             "git": {"commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
                     "working_diff_sha256": __import__('hashlib').sha256(subprocess.check_output(["git", "-C", str(root), "diff", "HEAD", "--binary"])).hexdigest()},
             "scope": "isolated fitting diagnostic; original checkpoints and training identity stay immutable"}
    if (output / "IDENTITY.json").exists() and read(output / "IDENTITY.json") != bound:
        raise ValueError("Repair identity changed; preserve this run and use a new profile/output")
    if (output / "PREPARED.json").exists():
        verify(output, read(output / "PREPARED.json")["files"])
        print("[reuse] four train + four held-out windows, noises and sources verified", flush=True)
        return
    if shutil.disk_usage(output).free < spec["local_reserve_gib"] * 2**30:
        raise ValueError("Need at least 20 GiB free for immutable paired optimizer checkpoints")
    windows = []
    for key in PROBE_CASES:
        prefix = f"inputs/{key}/"
        for name in manifest:
            if name.startswith(prefix):
                copy_verified(old, name, manifest, output / name)
        window = read(output / prefix / "window.json")
        window["group"] = "train" if key == "put_train_initial" else "heldout"
        windows.append(window)
        copy_verified(old, f"probe/cases/{key}_production_original/trace.npz", manifest,
                      output / "references" / f"{key}.npz")
    # Recover only signed durable frozen inputs, never temporary Torch modules.
    old_spec = prior["protocol"]
    intervention = checked_path(root, old_spec["intervention_output"])
    saved = archive_manifest(checked_path(root, old_spec["intervention_archive"]),
                             old_spec["intervention_archive_sha256"], "FILES.json")
    copy_verified(intervention, "frozen/FROZEN.json", saved, output / "frozen/FROZEN.json")
    bundle = read(output / "frozen/FROZEN.json")
    needed = set()
    for item in bundle["inputs"].values(): needed.update(item["images"])
    for record in bundle["experts"].values(): needed.add(record["path"])
    for records in bundle["noise"].values(): needed.update(x["path"] for x in records.values())
    for name in sorted(needed):
        copy_verified(intervention, "frozen/" + name, saved, output / "frozen" / name)
    for name in ("REPORT.json", "first-noise/put_back_block/executed_actions.jsonl", "expert-prefix/swap_blocks/executed_actions.jsonl"):
        copy_verified(intervention, name, saved, output / "historical" / name)
    decoder = official_decoder(decoder_path.parent.parent)
    episodes = data_manifest["episodes"]
    put_raw = windows[0]["item"]["origin"]["raw"]
    put = next(x for x in episodes if x["raw"] == put_raw and x["split"] == "train")
    if put["raw_sha256"] != windows[0]["item"]["origin"]["sha256"]:
        raise ValueError("Training initial window and prepared source identity disagree")
    if read(output / "inputs/swap_val_initial/window.json")["item"]["origin"]["split"] != "val":
        raise ValueError("Historical swap validation window was not held out")
    swap = min((x for x in episodes if x["task"] == "swap_blocks" and x["split"] == "train" and x["length"] >= 64),
               key=lambda x: x["episode_id"])
    put_val = min((x for x in episodes if x["task"] == "put_back_block" and x["split"] == "val" and x["length"] >= 32),
                  key=lambda x: x["episode_id"])

    def add_window(key, record, closing, group):
        stop_check(output)
        raw = checked_path(root, record["raw"])
        verify(root, {record["raw"]: record["raw_sha256"]})
        state, targets, cameras, *_ = read_episode(raw)
        if cameras != record["camera_paths"] or len(state) != record["length"]:
            raise ValueError("Demo camera/length differs from reviewed record")
        anchor = 0
        if closing:
            crosses = [i for i in range(16, len(targets)-31)
                       if any(targets[i, g] < .5 <= targets[i-1, g] for g in (6, 13))]
            if not crosses:
                raise ValueError(f"No real closing transition with 32 following targets in {record['episode_id']}")
            anchor = (crosses[0] // 16) * 16
        seed = seed_for(cfg["seed"], record["episode_id"], 0, "query-repair-demo-episode-v1")
        sampling = resolve_online(cfg, record["task"], seed, anchor)
        selected = select_ids(range(anchor+1), anchor, sampling["period"], phase=sampling["phase"])
        folder = output / "inputs" / key
        observations = []
        with h5py.File(raw, "r") as stream:
            for index in selected:
                names = []
                for camera, column in enumerate(cameras):
                    pixels = decoder(stream[column][index])
                    if pixels.dtype != np.uint8 or pixels.ndim != 3 or pixels.shape[-1] != 3:
                        raise ValueError("Invalid three-view RGB decode")
                    name = f"images/{index:06d}_{camera}.png"
                    (folder / name).parent.mkdir(parents=True, exist_ok=True)
                    Image.fromarray(pixels).save(folder / name)
                    names.append(name)
                observations.append({"frame_id": index, "proprio": state[index].tolist(), "images": names})
        item = {"task": record["task"], "seed": seed, "anchor": anchor, "instruction": record["instruction"],
                "proprio": state[anchor].tolist(), "targets": targets[anchor:anchor+32].tolist(),
                "origin": {"raw": record["raw"], "sha256": record["raw_sha256"], "split": record["split"],
                           "episode_id": record["episode_id"], "stage_rule": "first target gripper crossing .5; not a physical grasp label"}}
        window = {"id": key, "item": item, "observations": observations, "sampling": sampling,
                  "noise": {}, "group": group}
        windows.append(window)

    add_window("swap_train_initial", swap, False, "train")
    add_window("put_train_closing", put, True, "train")
    add_window("swap_train_closing", swap, True, "train")
    add_window("put_val_initial", put_val, False, "heldout")
    for window in windows:
        folder = output / "inputs" / window["id"]
        folder.mkdir(parents=True, exist_ok=True)
        for name in spec["evaluation_noises"]:
            if name in window["noise"]:
                info = window["noise"][name]
                verify(folder, {info["path"]: info["sha256"]})
                continue
            seed = seed_for(cfg["seed"], window["id"], window["item"]["anchor"], "query-repair-eval:" + name)
            path = folder / f"noise_{name}.npy"
            np.save(path, torch.randn(1, 32, 14, generator=torch.Generator(device="cpu").manual_seed(seed)).numpy(), allow_pickle=False)
            window["noise"][name] = {"seed": seed, "path": path.name, "sha256": sha(path)}
        write(folder / "window.json", window)
        print(f"[freeze] {window['id']} group={window['group']} anchor={window['item']['anchor']} history={len(window['observations'])}", flush=True)
    if sum(x["group"] == "train" for x in windows) != 4 or sum(x["group"] == "heldout" for x in windows) != 4:
        raise ValueError("Expected exactly four train and four held-out windows")
    for name in ("manifest.json", "alignment_approved.json"):
        shutil.copy2(prepared / name, output / ("prepared_" + name))
    write(output / "WINDOWS.json", windows)
    write(output / "IDENTITY.json", bound)
    mapping = {name: sha(output / name) for name in ("IDENTITY.json", "WINDOWS.json", "prepared_manifest.json", "prepared_alignment_approved.json")}
    for folder in ("inputs", "references", "frozen", "historical"):
        mapping.update({folder + "/" + key: value for key, value in files(output / folder).items()})
    write(output / "PREPARED.json", {"identity": signature(bound), "files": mapping})
    print("[prepared] zero: 16 backwards + 16 action samples; fit: 2x64 updates, global16=2x8, 96 paired action samples; physical: gated two prefixes", flush=True)


def require_prepared(root, output):
    bound = read(output / "IDENTITY.json")
    if (bound["protocol"] != profile(root) or bound["sources"] != sources(root)
            or bound["tools"] != {name: sha(root / name) for name in TOOLS} or bound["runtime"] != runtime()):
        raise ValueError("Code/protocol/runtime changed; preserve the current experiment")
    verify(output, read(output / "PREPARED.json")["files"])
    for record in bound["weights"].values(): verify(root, {record["relative"]: record["sha256"]})
    for name, expected in bound["resources"].items():
        if sha(bound["config"]["paths"][name]) != expected: raise ValueError(f"Model resource changed: {name}")
    verify(bound["config"]["paths"]["tokenizer"], bound["tokenizer_files"])
    if simulator_runtime(bound["config"]) != bound["simulator_runtime"]:
        raise ValueError("Simulator Python/package runtime changed since preparation")
    return bound


def compute(root, output, stage):
    bound = require_prepared(root, output)
    identity = signature(bound)
    if (output / stage / "COMPLETE.json").exists():
        require_completion(output, stage, identity)
        print(f"[reuse] {stage} complete; artifacts verified", flush=True)
        return
    if stage == "fit": require_completion(output, "zero", identity, passed=True)
    if stage == "physical": require_completion(output, "fit", identity, passed=True)
    gpu = bound["runtime"]["gpu"].split(",")[0].strip()
    active = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"], text=True)
    if any(line.split(",")[0].strip() == gpu for line in active.splitlines()):
        raise RuntimeError("Bound H100 is occupied; explicitly stop its owning task first")
    directory = output / stage
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / f"worker_{time.time_ns()}.log"
    command = ["/opt/mwam/bin/python", "-B", "-u", "-m", "fastwam.memory_s1.memory_repair_worker",
               stage, "--root", str(root), "--output", str(output), "--gpu-uuid", gpu]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu)
    env.pop("CUDA_LAUNCH_BLOCKING", None)
    write(directory / "command.json", command)
    start, heartbeat = time.monotonic(), 0.0
    with log.open("w", encoding="utf-8") as stream:
        child = owned_popen(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            with log.open(encoding="utf-8", errors="replace") as reader:
                while child.poll() is None:
                    print(reader.read(), end="", flush=True)
                    stop_check(output)
                    elapsed = time.monotonic()-start
                    if elapsed > bound["protocol"]["stage_timeout_seconds"]:
                        raise TimeoutError(f"Stage exceeded bounded wall time: {log}")
                    state = read(directory / "progress.json") if (directory / "progress.json").exists() else {}
                    if (state.get("operation_started_unix") is not None
                            and time.time()-state["operation_started_unix"] > bound["protocol"]["case_timeout_seconds"]):
                        raise TimeoutError(f"Current operation exceeded its wall-time bound: {state}; {log}")
                    if elapsed-heartbeat >= 15:
                        eta = state.get("eta_seconds")
                        print(f"[heartbeat] {stage} mode={state.get('mode','-')} case={state.get('case','-')} "
                              f"phase={state.get('stage','startup')} progress={state.get('completed',0)}/{state.get('total','-')} "
                              f"elapsed={elapsed:.0f}s ETA={'unmeasured initialization' if eta is None else f'~{eta:.0f}s'} "
                              f"scope={state.get('eta_scope','current stage only')}", flush=True)
                        heartbeat = elapsed
                    time.sleep(1)
                print(reader.read(), end="", flush=True)
            if child.returncode:
                raise RuntimeError(f"Repair worker exited {child.returncode}: {log}\n{log.read_text(errors='replace')[-16000:]}")
            require_completion(output, stage, identity)
        finally:
            stop_children([child])


def report(output):
    bound = read(output / "IDENTITY.json")
    stages = {}
    for stage in ("zero", "fit", "physical"):
        stages[stage] = (require_completion(output, stage, signature(bound))
                         if (output / stage / "COMPLETE.json").exists() else {"state": "not_complete"})
    write(output / "REPORT.json", {"identity": signature(bound), "stages": stages,
          "root_cause_confirmed": False, "benchmark_accuracy": None,
          "interpretation": "Mechanism/held-out improvement gates do not prove all zero-success causes. Review physical divergence before formal retraining.",
          "original_checkpoints_unchanged": True, "automatic_full_S1_training": False})
    rows = stages["fit"].get("measurements", [])
    if rows:
        columns = ["case", "task", "group", "mode", "phase", "noise", "arm_rmse_first16_rad", "wrist_mae_first16_rad", "gripper_mae_first16", "seconds"]
        with (output / "actions.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
            writer.writeheader(); writer.writerows(rows)
    for stage, result in stages.items():
        print(f"[{stage}] state={result.get('state','complete')} gate={result.get('gate')} root_cause=requires_evidence_review", flush=True)


def pack(root, output):
    report(output)
    bound = read(output / "IDENTITY.json")
    package = output / "packages" / str(time.time_ns())
    package.mkdir(parents=True)
    excluded = {"packages", "tmp", "interrupted", "__pycache__", "launches", "checkpoints", "encoded"}
    selected = [p for p in output.rglob("*") if p.is_file() and not p.is_symlink()
                and not set(p.relative_to(output).parts) & excluded and p.suffix != ".pt"
                and p.name not in ("job.lock", "LAUNCH.json", "latest_log.txt", "LATEST_PACKAGE.json", "STOP.json")
                and not p.name.endswith(".partial")]
    source_files = []
    for name in sorted(set(bound["sources"]) | set(TOOLS)):
        target = package / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(root / name, target); source_files.append(target)
    mapping = {p.relative_to(output).as_posix(): sha(p) for p in selected}
    mapping.update({p.relative_to(package).as_posix(): sha(p) for p in source_files})
    write(package / "FILES.json", mapping)
    archive = package / "memory_repair.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in selected: tar.add(path, arcname=path.relative_to(output).as_posix(), recursive=False)
        for path in source_files + [package / "FILES.json"]: tar.add(path, arcname=path.relative_to(package).as_posix(), recursive=False)
    checksum = sha(archive)
    # No upload, no large optimizer/model payloads in this small evidence archive.
    (package / "SHA256SUMS").write_text(checksum + "  memory_repair.tar.gz\n", encoding="utf-8")
    write(output / "LATEST_PACKAGE.json", {"archive": str(archive), "sha256": checksum, "identity": signature(bound),
                                            "excluded_large_payloads": ["encoded tensors", "optimizer checkpoints", "candidate weights"]})
    print(f"[package] {archive}\nSHA256={checksum}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("stage", choices=(*STAGES, "status", "stop"))
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(); root = args.root.resolve(); spec = profile(root)
    output = checked_path(root, spec["output"]); output.mkdir(parents=True, exist_ok=True)
    launch = read(output / "LAUNCH.json") if (output / "LAUNCH.json").exists() else {}
    if args.stage == "status":
        result = {"running": alive(launch.get("owner")), "launch": launch, "stop": (output / "STOP.json").exists()}
        for stage in ("zero", "fit", "physical"):
            path = output / stage / "result.json"
            result[stage] = read(path).get("gate", "complete") if path.exists() else "not_complete"
        result["status"] = read(output / "STATUS.json") if (output / "STATUS.json").exists() else None
        print(__import__('json').dumps(result, indent=2)); return
    if args.stage == "stop":
        write(output / "STOP.json", {"time": time.time(), "scope": "only this recorded repair tree"})
        stop_owned_tree(launch.get("owner")); print("Stop requested; complete cases/checkpoints preserved; resume is explicit"); return
    owner = process(os.getpgrp()); exit_path = os.environ.get("FW_MEMORY_REPAIR_EXIT", "")
    if (not owner or owner["pid"] != os.getppid() or os.getsid(0) != owner["pid"] or not exit_path
            or not Path(exit_path).resolve().is_relative_to(output / "launches")):
        raise ValueError("Use the owned nohup entry scripts/memory_s1/portable/h100/memory_repair.sh")
    if alive(launch.get("owner")) and launch["owner"]["pid"] != owner["pid"]:
        raise RuntimeError("Another repair stage is active")
    if (output / "STOP.json").exists() and args.stage not in ("report", "pack"):
        if not args.resume: raise InterruptedError("STOP present; use resume STAGE")
        (output / "STOP.json").rename(output / f"STOP.resumed_{time.time_ns()}.json")
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Repair launcher terminated")))
    write(output / "LAUNCH.json", {"owner": owner, "worker": process(os.getpid()), "stage": args.stage, "started": time.time(), "argv": sys.argv})
    write(output / "STATUS.json", {"stage": args.stage, "state": "running"})
    started = time.monotonic()
    try:
        if args.stage == "prepare": prepare(root, spec, output)
        elif args.stage in ("zero", "fit", "physical"): compute(root, output, args.stage)
        else:
            require_prepared(root, output)
            report(output) if args.stage == "report" else pack(root, output)
        write(output / "STATUS.json", {"stage": args.stage, "state": "complete", "seconds": time.monotonic()-started})
        print(f"[complete] {args.stage} seconds={time.monotonic()-started:.1f}", flush=True)
    except BaseException as error:
        write(output / "STATUS.json", {"stage": args.stage, "state": "interrupted" if isinstance(error, InterruptedError) else "error",
              "error": repr(error), "traceback": traceback.format_exc()}); raise


if __name__ == "__main__": main()
