"""Explicit H100 startup interventions; never schedules benchmark or training."""
from __future__ import annotations

import argparse
import copy
import csv
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

from .grasp_bridge import (read, write, sha, signature, verify, checked_path, files,
                           process, alive, owned_popen, stop_children, stop_owned_tree)

STAGES = ("prepare", "first-noise", "expert-prefix", "micro", "report", "pack")
TASKS = ("put_back_block", "swap_blocks")
REVISION = "31784b6f37815f4d6b4e06377fa158b3a5965fda"
SOURCE_FOLDERS = ("src/fastwam", "scripts/memory_s1")


def profile(root):
    value = read(root / "configs/memory_s1/initial_intervention_h100.json")
    if (value["machine"] != "h100" or value["tasks"] != list(TASKS)
            or value["checkpoint_step"] != 2000 or value["target_cap"] != 128
            or value["expert_prefix_targets"] != 48 or value["micro_updates"] != 16):
        raise ValueError("This bounded protocol requires H100, step 2000, two tasks, 48/128 targets, 16 isolated updates")
    for key in ("output", "grasp_output", "sampler"):
        if not checked_path(root, value[key]).is_relative_to(root / "outputs"):
            raise ValueError(f"Expected outputs directory: {key}")
    return value


def code_files(root):
    # A100-only recovery changes cannot change this H100 experiment identity.
    return {p.relative_to(root).as_posix(): sha(p) for folder in SOURCE_FOLDERS
            for p in sorted((root / folder).rglob("*"))
            if p.is_file() and p.suffix in (".py", ".sh")
            and "portable" not in p.relative_to(root).parts
            and "__pycache__" not in p.parts} | {
        "scripts/memory_s1/portable/h100/intervene.sh": sha(root / "scripts/memory_s1/portable/h100/intervene.sh"),
        "configs/model/fastwam.yaml": sha(root / "configs/model/fastwam.yaml")}


def runtime(cfg):
    import importlib.metadata
    from .integration_contract import simulator_sources
    return {
        "python": sys.version,
        "packages": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions() if d.metadata["Name"]},
        "gpu_driver": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid,name,driver_version", "--format=csv,noheader"], text=True),
        "simulator_sources": simulator_sources(cfg),
    }


def prepare(root, spec, output):
    print("[prepare] authenticating completed sampler, frozen inputs, checkpoint and current runtime", flush=True)
    sampler = root / spec["sampler"]
    if sha(sampler / "probe.tar.gz") != spec["sampler_archive_sha256"]:
        raise ValueError("Sampler archive differs from the reviewed download")
    with tarfile.open(sampler / "probe.tar.gz", "r:gz") as archive:
        manifest = json.load(archive.extractfile("FILES.json"))
    if read(sampler / "FILES.json") != manifest:
        raise ValueError("Sampler file manifest differs from the authenticated archive")
    verify(sampler, manifest)
    result = read(sampler / "RESULT.json")
    if not result.get("complete") or [result.get(k) for k in ("action_samples", "fm_forwards", "reference_exact_cases")] != [36, 48, 12]:
        raise ValueError("Expected the completed 36/48/12 sampler diagnostic")
    sampler_bound = read(sampler / "IDENTITY.json")
    if sampler_bound["evidence_revision"] != REVISION:
        raise ValueError("Different historical grasp evidence")
    verify(root, sampler_bound["sources"])
    old = root / spec["grasp_output"]
    old_receipt = read(old / "HF_grasp.json")
    if old_receipt.get("revision") != REVISION or not old_receipt.get("readback_verified"):
        raise ValueError("Original grasp backup must have its verified fixed revision")
    old_archive = old / "packages" / Path(old_receipt["package"]).parent.name / "grasp.tar.gz"
    if sha(old_archive) != sampler_bound["archive_sha256"] or old_receipt["sha256"] != sampler_bound["archive_sha256"]:
        raise ValueError("Original grasp archive differs from sampler provenance")
    with tarfile.open(old_archive, "r:gz") as archive:
        old_manifest = json.load(archive.extractfile("BACKUP_FILES.json"))
    verify(old, {"CURRENT.json": old_manifest["CURRENT.json"]})
    old_bound = read(old / "CURRENT.json")
    cfg = copy.deepcopy(sampler_bound["config"])
    if Path(cfg["root"]).resolve() != root or cfg["history"]["archive_stride"] != 1:
        raise ValueError("Expected original H100 workspace and dense observation archive")
    if (cfg["history"].get("online_period") != 8 or cfg["history"].get("online_mode", "fixed") != "fixed"
            or cfg["history"].get("online_cycle") or cfg["history"].get("online_phase") != "episode_seeded"):
        raise ValueError("Expected unchanged fixed T=8 and episode phase")
    origin = checked_path(root, old_bound["profile"]["inputs"])
    verify(origin, {name.removeprefix("frozen/"): expected for name, expected in old_manifest.items() if name.startswith("frozen/")})
    verify(origin, read(origin / "FILES.json"))
    bundle = read(origin / "FROZEN.json")
    if bundle["weights"] != sampler_bound["weights"]:
        raise ValueError("Frozen and sampler weight identities differ")
    weight = bundle["weights"]["step_002000"]
    verify(root, {weight["relative"]: weight["sha256"]})
    for key, expected in bundle["resources"].items():
        if sha(cfg["paths"][key]) != expected:
            raise ValueError(f"Resource differs: {cfg['paths'][key]}")
    verify(cfg["paths"]["tokenizer"], bundle["tokenizer_files"])
    actual_runtime = runtime(cfg)
    if actual_runtime["simulator_sources"] != old_bound["simulator_sources_sha256"]:
        raise ValueError("Simulator/task/asset sources changed since the paired expert evidence")
    install = checked_path(root, old_bound["profile"]["simulator_receipt"])
    if sha(install) != old_bound["simulator_install"]:
        raise ValueError("Fused simulator installation receipt changed")
    # Reuse the same planner warmup lock; only diagnostic results get a new root.
    bound = {"protocol": spec, "config": cfg, "code": code_files(root), "runtime": actual_runtime,
             "weight": weight, "frozen_files_sha256": sha(origin / "FILES.json"),
             "sampler_identity_sha256": sha(sampler / "IDENTITY.json"), "simulator_receipt": str(install),
             "simulator_receipt_sha256": sha(install), "historical_revision": REVISION}
    if (output / "IDENTITY.json").exists():
        if read(output / "IDENTITY.json") != bound:
            raise ValueError("Run identity changed; preserve this run and choose a new output profile")
        verify(output, read(output / "PREPARED.json")["files"])
        print("[reuse] prepared inputs verified", flush=True)
        return
    # An incomplete preparation is never trusted and may be copied again.
    frozen = output / "frozen"
    for name in ("FROZEN.json", "FILES.json", *read(origin / "FILES.json")):
        target = checked_path(frozen, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(checked_path(origin, name), target)
    for task in TASKS:
        for noise in ("online", "offline"):
            name = f"cases/{task}_2000_{noise}/bf16_10.npz"
            target = output / "baselines" / f"{task}_{noise}.npz"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sampler / name, target)
    write(output / "IDENTITY.json", bound)
    mapping = {**{f"frozen/{k}": v for k, v in files(frozen).items()},
               "frozen/FILES.json": sha(frozen / "FILES.json"),
               **{f"baselines/{k}": v for k, v in files(output / "baselines").items()},
               "IDENTITY.json": sha(output / "IDENTITY.json")}
    write(output / "PREPARED.json", {"identity": signature(bound), "files": mapping})
    print("[prepared] first-noise: 2 x 128 targets; expert-prefix: separate command, 48 expert + at most 80 policy targets; no task accuracy", flush=True)


def require_prepared(root, spec, output):
    bound = read(output / "IDENTITY.json")
    if bound["protocol"] != spec or bound["code"] != code_files(root):
        raise ValueError("Code/protocol changed after prepare; do not reuse old completed cases")
    verify(output, read(output / "PREPARED.json")["files"])
    verify(root, {bound["weight"]["relative"]: bound["weight"]["sha256"]})
    cfg = bound["config"]
    bundle = read(output / "frozen/FROZEN.json")
    for key, expected in bundle["resources"].items():
        if sha(cfg["paths"][key]) != expected:
            raise ValueError(f"Resource differs: {key}")
    verify(cfg["paths"]["tokenizer"], bundle["tokenizer_files"])
    if runtime(cfg) != bound["runtime"] or sha(bound["simulator_receipt"]) != bound["simulator_receipt_sha256"]:
        raise ValueError("Environment changed since prepare; keep results separate")
    return bound


def check_stop(output):
    if (output / "STOP.json").exists():
        raise InterruptedError("Explicit stop requested; use resume STAGE")


def completed(output, stage, identity):
    path = output / stage / "COMPLETE.json"
    if not path.exists():
        return False
    record = read(path)
    if record["identity"] != identity:
        raise ValueError(f"Completed stage identity differs: {path}")
    verify(path.parent, record["files"])
    return True


def gpu_stage(root, spec, output, stage):
    bound = require_prepared(root, spec, output)
    identity = signature(bound)
    if completed(output, stage, identity):
        print(f"[reuse] {stage} complete and verified", flush=True)
        return
    # Conditional interventions are explicit, never automatic continuations.
    if stage in ("expert-prefix", "micro") and not completed(output, "first-noise", identity):
        raise ValueError("Complete and review first-noise before starting the conditional stage")
    rows = subprocess.check_output(["nvidia-smi", "--query-gpu=uuid,name", "--format=csv,noheader"], text=True).strip().splitlines()
    if len(rows) != 1 or "H100" not in rows[0]:
        raise ValueError("This entry requires exactly one H100")
    gpu = rows[0].split(",")[0].strip()
    active = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"], text=True)
    if any(line.split(",")[0].strip() == gpu for line in active.splitlines()):
        raise RuntimeError("H100 already has a compute process; stop its owning task explicitly before this diagnostic")
    directory = output / stage
    directory.mkdir(parents=True, exist_ok=True)
    log_path = directory / f"worker_{time.time_ns()}.log"
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu, PYTHONUNBUFFERED="1")
    env.pop("CUDA_LAUNCH_BLOCKING", None)
    command = ["/opt/mwam/bin/python", "-u", "-m", "fastwam.memory_s1.initial_intervention_worker",
               stage, "--root", str(root), "--output", str(output), "--gpu-uuid", gpu]
    write(directory / "command.json", command)
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8") as stream:
        child = owned_popen(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            heartbeat = started
            with log_path.open(encoding="utf-8", errors="replace") as reader:
                while child.poll() is None:
                    text = reader.read()
                    if text:
                        print(text, end="", flush=True)
                    check_stop(output)
                    if time.monotonic() - started > spec["stage_timeout_seconds"]:
                        raise TimeoutError(f"Bounded stage timeout; inspect {log_path}")
                    if time.monotonic() - heartbeat >= 15:
                        status_path = directory / "progress.json"
                        status = read(status_path) if status_path.exists() else {}
                        age = time.time() - status.get("started_unix", time.time())
                        print(f"[heartbeat] stage={stage} elapsed={time.monotonic()-started:.0f}s "
                              f"current={status.get('stage', 'worker_start')} task={status.get('task', '-')} "
                              f"initialization_elapsed={age:.0f}s; rollout ETA is reported from executed targets", flush=True)
                        heartbeat = time.monotonic()
                    time.sleep(1)
                print(reader.read(), end="", flush=True)
            if child.returncode:
                raise RuntimeError(f"{stage} worker exited {child.returncode}; direct error is in {log_path}")
            if not completed(output, stage, identity):
                raise ValueError("Worker exited without a verified completion receipt")
        finally:
            stop_children([child])


def report(output):
    identity = signature(read(output / "IDENTITY.json"))
    stages, rows = {}, []
    for stage in ("first-noise", "expert-prefix", "micro"):
        done = completed(output, stage, identity)
        cases = []
        for path in sorted((output / stage).glob("*/COMPLETE.json")):
            value = read(path)
            if value["identity"] != identity:
                raise ValueError(f"Case identity differs: {path}")
            verify(path.parent, value["files"])
            result = read(path.parent / "result.json")
            cases.append(result)
            rows.append({"stage": stage, "task": result["task"], "targets": result["executed_targets"],
                         "policy_targets": result["policy_targets"], "first_right_close": result["first_right_close"],
                         "wrist_tracking_mae_rad": result["wrist_tracking_mae_rad"],
                         "object_lifts_m": json.dumps(result["object_lifts_m"], sort_keys=True),
                         "termination": result["termination"], "task_accuracy": "not_applicable"})
        stages[stage] = {"state": "complete" if done else "partial_or_not_run", "cases": cases}
        if stage == "micro" and done:
            stages[stage]["result"] = read(output / stage / "result.json")
    write(output / "REPORT.json", {"identity": identity, "stages": stages,
          "root_cause": "requires causal comparison; no automatic root-cause claim",
          "scope": "bounded interventions, expert-assisted prefixes and isolated fitting; not benchmark accuracy"})
    columns = ["stage", "task", "targets", "policy_targets", "first_right_close", "wrist_tracking_mae_rad", "object_lifts_m", "termination", "task_accuracy"]
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    for stage, value in stages.items():
        print(f"[{stage}] {value['state']}", flush=True)
    for row in rows:
        print(json.dumps(row, ensure_ascii=False), flush=True)


def pack(root, output):
    report(output)
    directory = output / "packages" / str(time.time_ns())
    directory.mkdir(parents=True)
    selected = [p for p in output.rglob("*") if p.is_file() and not p.is_symlink()
                and not set(p.relative_to(output).parts) & {"packages", "interrupted", "__pycache__", "launches"}
                and p.name not in ("job.lock", "LAUNCH.json", "latest_log.txt")]
    for name in code_files(root):
        target = directory / "source" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, target)
    source = [p for p in (directory / "source").rglob("*") if p.is_file()]
    mapping = {p.relative_to(output).as_posix(): sha(p) for p in selected}
    mapping.update({p.relative_to(directory).as_posix(): sha(p) for p in source})
    write(directory / "FILES.json", mapping)
    archive = directory / "initial_intervention.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in selected:
            tar.add(path, arcname=path.relative_to(output).as_posix(), recursive=False)
        for path in source + [directory / "FILES.json"]:
            tar.add(path, arcname=path.relative_to(directory).as_posix(), recursive=False)
    (directory / "SHA256SUMS").write_text(sha(archive) + "  initial_intervention.tar.gz\n", encoding="utf-8")
    write(output / "LATEST_PACKAGE.json", {"archive": str(archive), "sha256": sha(archive)})
    print(f"[package] {archive}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("stage", choices=(*STAGES, "status", "stop"))
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    spec = profile(root)
    output = root / spec["output"]
    output.mkdir(parents=True, exist_ok=True)
    launch = read(output / "LAUNCH.json") if (output / "LAUNCH.json").exists() else {}
    if args.stage == "status":
        print(json.dumps({"running": alive(launch.get("owner")), "launch": launch,
                          "status": read(output / "STATUS.json") if (output / "STATUS.json").exists() else None}, indent=2))
        return
    if args.stage == "stop":
        write(output / "STOP.json", {"mode": "now", "time": time.time()})
        stop_owned_tree(launch.get("owner"))
        print("Stopped only the recorded intervention process tree. Resume is explicit.")
        return
    if alive(launch.get("owner")) and launch["owner"]["pid"] != os.getpgrp():
        raise RuntimeError("Another intervention is active")
    # Only our setsid wrapper may become a stoppable owner; never record a user's
    # interactive shell group when someone invokes this module directly.
    owner = process(os.getpgrp())
    exit_file = os.environ.get("FW_INITIAL_EXIT", "")
    if (not owner or owner["pid"] != os.getppid() or os.getsid(0) != owner["pid"]
            or not exit_file or not Path(exit_file).resolve().is_relative_to(output / "launches")):
        raise ValueError("Launch through scripts/memory_s1/portable/h100/intervene.sh (owned nohup session required)")
    if (output / "STOP.json").exists() and args.stage not in ("report", "pack"):
        if not args.resume:
            raise ValueError("STOP present; use resume STAGE")
        (output / "STOP.json").rename(output / f"STOP.resumed_{time.time_ns()}.json")
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Launch terminated")))
    write(output / "LAUNCH.json", {"owner": owner, "worker": process(os.getpid()),
                                   "stage": args.stage, "started": time.time(), "argv": sys.argv})
    started = time.monotonic()
    write(output / "STATUS.json", {"stage": args.stage, "state": "running"})
    try:
        if args.stage == "prepare":
            prepare(root, spec, output)
        elif args.stage == "report":
            report(output)
        elif args.stage == "pack":
            pack(root, output)
        else:
            gpu_stage(root, spec, output, args.stage)
        write(output / "STATUS.json", {"stage": args.stage, "state": "complete", "seconds": time.monotonic()-started})
        print(f"[complete] {args.stage} seconds={time.monotonic()-started:.1f}", flush=True)
    except BaseException as error:
        write(output / "STATUS.json", {"stage": args.stage, "state": "interrupted" if isinstance(error, InterruptedError) else "error",
              "error": repr(error), "traceback": traceback.format_exc(), "seconds": time.monotonic()-started})
        raise


if __name__ == "__main__":
    main()
