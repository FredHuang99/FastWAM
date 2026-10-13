"""Identity-bound, 24-sample H100 memory probe; no optimizer or simulator jobs."""
from __future__ import annotations

import argparse
import copy
import csv
import importlib.metadata
import json
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

STAGES = ("prepare", "probe", "report", "pack")
TOOLS = ("src/fastwam/memory_s1/memory_probe.py", "src/fastwam/memory_s1/memory_probe_worker.py",
         "scripts/memory_s1/portable/h100/memory_probe.sh", "configs/memory_s1/memory_probe_h100.json")
CORE = ("model.py", "modules.py", "common.py", "data.py", "history.py", "protocol.py",
        "integration_contract.py", "grasp_diagnosis.py", "sim_bridge.py", "diagnosis_gpu.py")
VARIANTS = ("original", "mean_readout", "memory_fp32")


def sources(root):
    names = ["src/fastwam/memory_s1/" + name for name in CORE]
    names += [p.relative_to(root).as_posix() for p in (root / "src/fastwam/models/wan22").rglob("*.py")
              if "__pycache__" not in p.parts]
    names += ["configs/model/fastwam.yaml"]
    return {name: sha(root / name) for name in sorted(names)}


def profile(root):
    spec = read(root / TOOLS[-1])
    expected = ["put_train_initial", "swap_val_initial", "put_expert_080", "swap_expert_048"]
    if (spec.get("machine") != "h100" or spec.get("checkpoint_step") != 2000
            or spec.get("modes") != list(VARIANTS) or spec.get("noises") != ["production", "independent"]
            or [row["id"] for row in spec["cases"]] != expected or spec.get("gradient_tau") != .9):
        raise ValueError("Expected the reviewed four-window, two-noise, three-mode protocol")
    for name in ("output", "intervention_output", "intervention_archive"):
        if not checked_path(root, spec[name]).is_relative_to(root / "outputs"):
            raise ValueError(f"Expected an outputs path: {name}")
    return spec


def archive_manifest(path, expected, name):
    if not path.is_file() or sha(path) != expected:
        raise ValueError(f"Historical archive missing or changed: {path}; expected={expected}")
    with tarfile.open(path, "r:gz") as archive:
        member = archive.getmember(name)
        if not member.isfile():
            raise ValueError(f"Historical manifest must be a regular file: {name}")
        with archive.extractfile(member) as stream:
            return json.load(stream)


def copy_verified(origin, relative, manifest, destination):
    if relative not in manifest:
        raise ValueError(f"Authenticated archive has no required file: {relative}")
    path = checked_path(origin, relative)
    verify(origin, {relative: manifest[relative]})
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
    return {"source": str(path), "sha256": manifest[relative]}


def runtime():
    packages = {d.metadata["Name"].lower().replace("_", "-"): d.version
                for d in importlib.metadata.distributions() if d.metadata["Name"]}
    names = ("torch", "numpy", "pillow", "transformers", "safetensors", "sentencepiece")
    return {"python": sys.version, "packages": {name: packages.get(name) for name in names},
            "gpu": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid,name,driver_version",
                                             "--format=csv,noheader"], text=True).strip()}


def stop_check(output):
    if (output / "STOP.json").exists():
        raise InterruptedError("Stopped at a probe boundary; resume is explicit")


def prepare(root, spec, output):
    import numpy as np
    import torch
    from .common import seed_for
    from .history import resolve_online, select_ids
    old = checked_path(root, spec["intervention_output"])
    manifest = archive_manifest(checked_path(root, spec["intervention_archive"]),
                                spec["intervention_archive_sha256"], "FILES.json")
    verify(old, {"IDENTITY.json": manifest["IDENTITY.json"], "REPORT.json": manifest["REPORT.json"]})
    prior = read(old / "IDENTITY.json")
    report = read(old / "REPORT.json")
    if any(report["stages"][name]["state"] != "complete" for name in ("first-noise", "expert-prefix", "micro")):
        raise ValueError("The reviewed interventions must all be complete")
    if report["stages"]["micro"]["result"].get("original_weights_restored") is not True:
        raise ValueError("Original step-2000 weights were not restored by the prior micro experiment")
    cfg = copy.deepcopy(prior["config"])
    if Path(cfg["root"]).resolve() != root or cfg["history"].get("online_period") != 8:
        raise ValueError("Expected original H100 root and fixed T=8")
    current_sources = sources(root)
    changed = {name: {"old": prior["code"].get(name), "current": value}
               for name, value in current_sources.items() if prior["code"].get(name) != value}
    if changed:
        raise ValueError(f"Production/probe dependencies changed since reviewed evidence: {changed}")
    current_runtime = runtime()
    old_packages = {name.lower().replace("_", "-"): version
                    for name, version in prior["runtime"]["packages"].items()}
    if (current_runtime["python"] != prior["runtime"]["python"]
            or any(old_packages.get(name) != value for name, value in current_runtime["packages"].items())):
        raise ValueError("Model Python/package versions changed since reviewed H100 evidence")
    if "H100" not in current_runtime["gpu"] or len(current_runtime["gpu"].splitlines()) != 1:
        raise ValueError("Expose exactly one H100")
    frozen_manifest = read(old / "frozen/FILES.json")
    verify(old, {"frozen/FILES.json": manifest["frozen/FILES.json"],
                 "frozen/FROZEN.json": manifest["frozen/FROZEN.json"]})
    bundle = read(old / "frozen/FROZEN.json")
    for key, expected in bundle["resources"].items():
        verify(root, {Path(cfg["paths"][key]).relative_to(root).as_posix(): expected})
    verify(Path(cfg["paths"]["tokenizer"]), bundle["tokenizer_files"])
    weight = bundle["weights"]["step_002000"]
    zero = bundle["weights"].get("step_000000")
    if zero is None:
        raise ValueError("Reviewed frozen bundle lacks true step-zero weight identity; do not substitute base")
    weights = {"step_000000": zero, "step_002000": weight}
    for record in weights.values():
        verify(root, {record["relative"]: record["sha256"]})
    grasp = checked_path(root, prior["protocol"]["grasp_output"])
    receipt = read(grasp / "HF_grasp.json")
    if receipt.get("revision") != "31784b6f37815f4d6b4e06377fa158b3a5965fda" or not receipt.get("readback_verified"):
        raise ValueError("Expected the reviewed immutable grasp backup")
    grasp_archive = grasp / "packages" / Path(receipt["package"]).parent.name / "grasp.tar.gz"
    if receipt["sha256"] != spec["grasp_archive_sha256"]:
        raise ValueError("Grasp backup identity differs from reviewed evidence")
    grasp_manifest = archive_manifest(grasp_archive, spec["grasp_archive_sha256"], "BACKUP_FILES.json")
    bound = {"protocol": spec, "config": cfg, "sources": current_sources,
             "tools": {name: sha(root / name) for name in TOOLS}, "runtime": current_runtime,
             "weights": weights, "resources": bundle["resources"],
             "history": {"intervention_archive_sha256": spec["intervention_archive_sha256"],
                         "grasp_archive_sha256": spec["grasp_archive_sha256"],
                         "intervention_identity_sha256": sha(old / "IDENTITY.json")}}
    if (output / "IDENTITY.json").exists():
        if read(output / "IDENTITY.json") != bound:
            raise ValueError("Prepared identity changed; preserve this run and use a new output profile")
        if (output / "PREPARED.json").exists():
            verify(output, read(output / "PREPARED.json")["files"])
            print("[reuse] four frozen windows and current identities verified", flush=True)
            return
        print("[prepare] recovering an interrupted preparation with the same authenticated sources", flush=True)
    provenance, windows = {}, []
    for case in spec["cases"]:
        stop_check(output)
        directory = output / "inputs" / case["id"]
        if case.get("input"):
            item = copy.deepcopy(bundle["inputs"][case["input"]])
            observations = [{"frame_id": item["anchor"], "proprio": item["proprio"], "images": item["images"]}]
            for name in item["images"]:
                if frozen_manifest.get(name) != manifest.get("frozen/" + name):
                    raise ValueError(f"Frozen manifest disagrees with archive: {name}")
                provenance[case["id"] + "/" + name] = copy_verified(old, "frozen/" + name, manifest, directory / name)
        else:
            task, anchor = case["task"], case["anchor"]
            prefix = f"expert-observe/worker_0/cases/{task}_{0 if task == 'put_back_block' else 1}"
            relative = prefix + "/observations.jsonl"
            verify(grasp, {relative: grasp_manifest[relative]})
            observations = [json.loads(line) for line in (grasp / relative).read_text().splitlines() if line.strip()]
            if [row["frame_id"] for row in observations[:anchor + 1]] != list(range(anchor + 1)):
                raise ValueError(f"Incomplete expert observation prefix: {relative}")
            row = observations[anchor]
            if row["completed_targets"] != anchor or row["next_target_index"] != anchor:
                raise ValueError("Observation and following expert targets are shifted")
            expert_name = bundle["experts"][task]["path"]
            verify(old, {"frozen/" + expert_name: manifest["frozen/" + expert_name]})
            expert = read(old / "frozen" / expert_name)
            item = {"task": task, "seed": expert["scene"]["seed"], "instruction": expert["scene"]["instruction"],
                    "anchor": anchor, "proprio": row["proprio"], "targets": expert["targets"][anchor:anchor + 32]}
            sampling = resolve_online(cfg, task, item["seed"], anchor)
            selected = select_ids(range(anchor + 1), anchor, sampling["period"], phase=sampling["phase"])
            observations = [observations[index] for index in selected]
            for observation in observations:
                for name in observation["images"]:
                    provenance[case["id"] + "/" + name] = copy_verified(grasp, prefix + "/" + name,
                                                                            grasp_manifest, directory / name)
            provenance[relative] = {"source": str(grasp / relative), "sha256": grasp_manifest[relative]}
        target = np.asarray(item["targets"], np.float32)
        if target.shape != (32, 14) or not np.isfinite(target).all():
            raise ValueError("Each window requires 32 real expert targets; no invented padding")
        sampling = resolve_online(cfg, item["task"], item["seed"], item["anchor"])
        noise_records = {}
        for name in spec["noises"]:
            if item["anchor"] == 0:
                old_name = "online" if name == "production" else "independent"
                noise_info = bundle["noise"][item["task"]][old_name]
                path = "frozen/" + noise_info["path"]
                copy_verified(old, path, manifest, directory / f"noise_{name}.npy")
                seed = noise_info["seed"]
            else:
                seed = (seed_for(cfg["seed"], item["seed"], item["anchor"], "closed-loop-noise")
                        if name == "production" else seed_for(cfg["seed"], item["seed"], item["anchor"],
                                                             "memory-probe-independent-v1:" + item["task"]))
                directory.mkdir(parents=True, exist_ok=True)
                noise = torch.randn(1, 32, 14, generator=torch.Generator(device="cpu").manual_seed(seed)).numpy()
                np.save(directory / f"noise_{name}.npy", noise, allow_pickle=False)
            noise = np.load(directory / f"noise_{name}.npy", allow_pickle=False)
            if noise.shape != (1, 32, 14) or noise.dtype != np.float32 or not np.isfinite(noise).all():
                raise ValueError("Invalid frozen diagnostic noise")
            noise_records[name] = {"seed": seed, "path": f"noise_{name}.npy", "sha256": sha(directory / f"noise_{name}.npy")}
        window = {"id": case["id"], "item": item, "observations": observations,
                  "sampling": sampling, "noise": noise_records, "source": case}
        write(directory / "window.json", window)
        windows.append(window)
        print(f"[freeze] {case['id']} anchor={item['anchor']} real_history_frames={len(observations)}", flush=True)
    write(output / "WINDOWS.json", windows)
    # Keep old diagnostics as authenticated historical material, without changing
    # their signatures or treating them as this experiment's execution records.
    for name in ("REPORT.json", "micro/result.json", "micro/updates.jsonl",
                 "first-noise/put_back_block/executed_actions.jsonl", "expert-prefix/swap_blocks/executed_actions.jsonl"):
        provenance["historical/" + name] = copy_verified(old, name, manifest, output / "historical" / name)
    for name in ("put_back_block_train_initial_2000", "swap_blocks_val_initial_2000"):
        relative = f"paths/worker_0/cases/{name}/offline.npz"
        copy_verified(grasp, relative, grasp_manifest, output / "references" / f"{name}.npz")
    for task in ("put_back_block", "swap_blocks"):
        relative = f"expert-observe/worker_0/cases/{task}_{0 if task == 'put_back_block' else 1}/executed_actions.jsonl"
        provenance["expert/" + task] = copy_verified(grasp, relative, grasp_manifest,
                                                    output / "historical" / f"expert_{task}.jsonl")
    write(output / "PROVENANCE.json", provenance)
    write(output / "IDENTITY.json", bound)
    mapping = {"IDENTITY.json": sha(output / "IDENTITY.json"), "WINDOWS.json": sha(output / "WINDOWS.json"),
               "PROVENANCE.json": sha(output / "PROVENANCE.json")}
    for folder in ("inputs", "historical", "references"):
        mapping.update({folder + "/" + name: value for name, value in files(output / folder).items()})
    write(output / "PREPARED.json", {"identity": signature(bound), "files": mapping})
    print("[prepared] 24 action samples + 4 FM backward probes; optimizer_updates=0; simulation_episodes=0", flush=True)


def require_prepared(root, output):
    bound = read(output / "IDENTITY.json")
    if (bound["protocol"] != profile(root) or bound["sources"] != sources(root)
            or bound["tools"] != {name: sha(root / name) for name in TOOLS} or bound["runtime"] != runtime()):
        raise ValueError("Current code/protocol/runtime differs from this prepared run")
    verify(output, read(output / "PREPARED.json")["files"])
    for record in bound["weights"].values():
        verify(root, {record["relative"]: record["sha256"]})
    for name, value in bound["resources"].items():
        if sha(bound["config"]["paths"][name]) != value:
            raise ValueError(f"Model resource changed: {name}")
    return bound


def completion(output, bound):
    path = output / "probe/COMPLETE.json"
    if not path.exists():
        return False
    record = read(path)
    if record["identity"] != signature(bound):
        raise ValueError("Probe completion identity differs")
    verify(path.parent, record["files"])
    return True


def probe(root, output, spec):
    bound = require_prepared(root, output)
    if completion(output, bound):
        print("[reuse] 24 action cases and four backward probes verified", flush=True)
        return
    gpu = bound["runtime"]["gpu"].split(",")[0].strip()
    active = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"], text=True)
    if any(line.split(",")[0].strip() == gpu for line in active.splitlines()):
        raise RuntimeError("H100 has an active compute process; stop its owning task explicitly")
    directory = output / "probe"
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / f"worker_{time.time_ns()}.log"
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu)
    env.pop("CUDA_LAUNCH_BLOCKING", None)
    command = ["/opt/mwam/bin/python", "-u", "-m", "fastwam.memory_s1.memory_probe_worker",
               "--root", str(root), "--output", str(output), "--gpu-uuid", gpu]
    write(directory / "command.json", command)
    start = time.monotonic()
    with log.open("w", encoding="utf-8") as stream:
        child = owned_popen(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            heartbeat = start
            with log.open(encoding="utf-8", errors="replace") as reader:
                while child.poll() is None:
                    print(reader.read(), end="", flush=True)
                    stop_check(output)
                    if time.monotonic() - start > spec["stage_timeout_seconds"]:
                        raise TimeoutError(f"Probe timeout; direct worker log: {log}")
                    progress_path = directory / "progress.json"
                    state = read(progress_path) if progress_path.exists() else {}
                    if (state.get("stage") == "action_sample" and state.get("case_started_unix")
                            and time.time()-state["case_started_unix"] > spec["case_timeout_seconds"]):
                        raise TimeoutError(f"Action-case timeout: {state}; direct worker log: {log}")
                    if time.monotonic() - heartbeat >= 15:
                        elapsed = time.monotonic() - start
                        estimate = state.get("remaining_sample_seconds")
                        eta = f"~{estimate:.0f}s sampling" if estimate is not None else "unknown (no measured sample yet)"
                        print(f"[heartbeat] stage={state.get('stage', 'worker_start')} case={state.get('case', '-')} "
                              f"mode={state.get('mode', '-')} actions={state.get('completed', 0)}/24 "
                              f"elapsed={elapsed:.0f}s ETA={eta}; excludes pending encoding/backward/pack", flush=True)
                        heartbeat = time.monotonic()
                    time.sleep(1)
                print(reader.read(), end="", flush=True)
            if child.returncode:
                tail = log.read_text(encoding="utf-8", errors="replace")[-16000:]
                raise RuntimeError(f"Memory-probe worker exited {child.returncode}; {log}\n{tail}")
            if not completion(output, bound):
                raise ValueError("Worker exited without a verified completion receipt")
        finally:
            stop_children([child])


def historical_findings(output):
    def rows(path):
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    put = rows(output / "historical/first-noise/put_back_block/executed_actions.jsonl")
    contact = []
    for row in put:
        pairs = row["object_contacts"]["objects"]["block"]["matched_pairs"]
        fingers = {p["a"] if p["a"].startswith("fr_link") else p["b"]
                   for p in pairs if p["impulse"] > 1e-6}
        if {"fr_link7", "fr_link8"} <= fingers:
            contact.append(row["completed_target_id"])
    initial_height = put[0]["objects_before"]["block"]["p"][2]
    lifts = [row["objects_after"]["block"]["p"][2] - initial_height for row in put]
    swap = rows(output / "historical/expert-prefix/swap_blocks/executed_actions.jsonl")
    expert = rows(output / "historical/expert_swap_blocks.jsonl")
    paired = []
    for target in (48,49,56,64,68,80):
        left, right = swap[target-1], expert[target-1]
        a = left["joint_details"]["right"]["ee_pose"]["p"]
        b = right["joint_details"]["right"]["ee_pose"]["p"]
        paired.append({"target": target, "right_ee_delta_mm": [(x-y)*1000 for x,y in zip(a,b)],
                       "gripper_policy": left["target"][13], "gripper_expert": right["target"][13]})
    micro = read(output / "historical/micro/result.json")["measurements"]
    before = {(row["input"],row["noise"]): row for row in micro if row["phase"] == "before"}
    arms = (0,1,2,3,4,5,7,8,9,10,11,12)
    # These historical rows contain per-joint MAE, so report MAE explicitly;
    # no conversion of MAE into RMSE is made without the original action arrays.
    changed = [{"input": row["input"], "noise": row["noise"],
                "before_arm_mae_rad": sum(before[(row["input"],row["noise"])]["joint_mae_first16"][i] for i in arms)/12,
                "after_arm_mae_rad": sum(row["joint_mae_first16"][i] for i in arms)/12}
               for row in micro if row["phase"] == "after"]
    return {"put_first_noise": {"max_lift_m": max(lifts), "peak_target": 1+lifts.index(max(lifts)),
                "two_finger_positive_impulse_first_target": min(contact) if contact else None,
                "two_finger_positive_impulse_last_target": max(contact) if contact else None,
                "scope": "historical instantaneous samples; lift alone does not establish sustained grasp"},
            "swap_expert_handoff": paired, "micro_arm_mae_pairs": changed,
            "micro_loss_caution": "updates use different tau; first/last loss is not a fixed-condition convergence curve"}


def report(output):
    bound = read(output / "IDENTITY.json")
    done = completion(output, bound)
    result = read(output / "probe/result.json") if done else None
    write(output / "REPORT.json", {"identity": signature(bound), "complete": done, "result": result,
        "historical_findings": historical_findings(output),
        "interpretation": {"readout_similarity": "redundancy evidence; alone does not establish cause of zero success",
            "mean_readout": "paired output sensitivity to slot diversity; compare exact and numerical differences",
            "memory_fp32": "reader, injector and residual arithmetic only; frozen backbone remains BF16",
            "next": "Review results before choosing a single-factor repair and bounded paired fitting",
            "automatic_retraining": False, "benchmark_accuracy": None}})
    if not done:
        print("[report] partial: probe completion missing; no passed/root-cause claim", flush=True)
        return
    rows = result["cases"]
    columns = ["case", "noise", "mode", "arm_rmse_first16_rad", "wrist_mae_first16_rad",
               "gripper_mae_first16", "max_action_delta_from_original", "readout_centered_norm_ratio",
               "readout_min_cosine", "seconds"]
    with (output / "actions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[report] actions={len(rows)}/24 backward={len(result['gradients'])}/4 updates=0", flush=True)
    for row in rows:
        print(f"{row['case']} {row['noise']} {row['mode']}: arm_RMSE={row['arm_rmse_first16_rad']:.6f}rad "
              f"delta={row['max_action_delta_from_original']:.8g} cosine={row['readout_min_cosine']:.9f}", flush=True)


def pack(root, output):
    report(output)
    bound = read(output / "IDENTITY.json")
    directory = output / "packages" / str(time.time_ns())
    directory.mkdir(parents=True)
    excluded = {"packages", "interrupted", "tmp", "__pycache__", "launches"}
    selected = [p for p in output.rglob("*") if p.is_file() and not p.is_symlink()
                and not set(p.relative_to(output).parts) & excluded
                and p.name not in ("job.lock", "LAUNCH.json", "latest_log.txt", "LATEST_PACKAGE.json")]
    for name in sorted(set(bound["sources"]) | set(TOOLS)):
        destination = directory / "source" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, destination)
    source_files = [p for p in (directory / "source").rglob("*") if p.is_file()]
    mapping = {p.relative_to(output).as_posix(): sha(p) for p in selected}
    mapping.update({p.relative_to(directory).as_posix(): sha(p) for p in source_files})
    write(directory / "FILES.json", mapping)
    archive = directory / "memory_probe.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in selected:
            tar.add(path, arcname=path.relative_to(output).as_posix(), recursive=False)
        for path in source_files + [directory / "FILES.json"]:
            tar.add(path, arcname=path.relative_to(directory).as_posix(), recursive=False)
    checksum = sha(archive)
    (directory / "SHA256SUMS").write_text(checksum + "  memory_probe.tar.gz\n", encoding="utf-8")
    write(output / "LATEST_PACKAGE.json", {"archive": str(archive), "sha256": checksum,
          "complete": completion(output, bound), "identity": signature(bound)})
    print(f"[package] archive={archive}\nSHA256={checksum}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("stage", choices=(*STAGES, "status", "stop"))
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    spec = profile(root)
    output = checked_path(root, spec["output"])
    output.mkdir(parents=True, exist_ok=True)
    launch = read(output / "LAUNCH.json") if (output / "LAUNCH.json").exists() else {}
    if args.stage == "status":
        print(json.dumps({"running": alive(launch.get("owner")), "launch": launch,
              "status": read(output / "STATUS.json") if (output / "STATUS.json").exists() else None,
              "progress": read(output / "probe/progress.json") if (output / "probe/progress.json").exists() else None}, indent=2))
        return
    if args.stage == "stop":
        write(output / "STOP.json", {"time": time.time(), "scope": "owned memory-probe process tree"})
        stop_owned_tree(launch.get("owner"))
        print("Stopped only the recorded memory-probe tree; completed cases remain reusable")
        return
    owner = process(os.getpgrp())
    exit_path = os.environ.get("FW_MEMORY_PROBE_EXIT", "")
    if (not owner or owner["pid"] != os.getppid() or os.getsid(0) != owner["pid"]
            or not exit_path or not Path(exit_path).resolve().is_relative_to(output / "launches")):
        raise ValueError("Use scripts/memory_s1/portable/h100/memory_probe.sh (owned nohup session required)")
    if alive(launch.get("owner")) and launch["owner"]["pid"] != owner["pid"]:
        raise RuntimeError("Another probe stage is active")
    if (output / "STOP.json").exists() and args.stage not in ("report", "pack"):
        if not args.resume:
            raise InterruptedError("STOP present; use resume STAGE")
        (output / "STOP.json").rename(output / f"STOP.resumed_{time.time_ns()}.json")
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Probe launch terminated")))
    write(output / "LAUNCH.json", {"owner": owner, "worker": process(os.getpid()),
          "stage": args.stage, "started": time.time(), "argv": sys.argv})
    start = time.monotonic()
    write(output / "STATUS.json", {"stage": args.stage, "state": "running"})
    try:
        if args.stage == "prepare":
            prepare(root, spec, output)
        elif args.stage == "probe":
            probe(root, output, spec)
        elif args.stage == "report":
            require_prepared(root, output)
            report(output)
        else:
            require_prepared(root, output)
            pack(root, output)
        write(output / "STATUS.json", {"stage": args.stage, "state": "complete", "seconds": time.monotonic() - start})
        print(f"[complete] {args.stage} seconds={time.monotonic()-start:.1f}", flush=True)
    except BaseException as error:
        write(output / "STATUS.json", {"stage": args.stage,
              "state": "interrupted" if isinstance(error, InterruptedError) else "error",
              "error": repr(error), "traceback": traceback.format_exc()})
        raise


if __name__ == "__main__":
    main()
