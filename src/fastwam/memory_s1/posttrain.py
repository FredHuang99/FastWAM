"""Explicit, restartable post-training evaluation of selected exported milestones."""
from __future__ import annotations

import argparse
import csv
import gc
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import copy
import time

from .common import atomic_json, code_version, fingerprint, load_config, read_json, sha256
from .eval_state import EvaluationInterrupted, check_stop, locked, process_identity
from .schedule import milestone_steps
from .eval_state import stop_mode, is_alive
from .selection_runtime import duration, source_migration, import_offline, stop_request, format_active, failure_report, episode_work, live_details
from .fused_evaluation import comparison_spec


def verified_weights(run):
    index = read_json(run / "MILESTONES.json")
    identity = read_json(run / "identity.json")
    if index["identity"] != identity:
        raise ValueError("Exported weights and training identity differ.")
    result = {}
    for step in [0, *index["candidate_steps"]]:
        row = index["weights"].get(str(step))
        if row is None:
            raise ValueError(f"Missing exported weight at update {step}; training must finish first.")
        path = (run / row["file"]).resolve()
        if not path.is_relative_to(run) or sha256(path) != row["sha256"]:
            raise ValueError(f"Weight path/checksum mismatch at update {step}.")
        result[step] = path
    return identity, result


def checked_result(path, identity):
    if path.exists():
        value = read_json(path)
        if value.get("identity") != identity:
            raise ValueError(f"Evaluation identity changed: {path}")
        return value
    return None


def closed_child(cfg_file, weights, root, directory, mode, conditions, args,
                 scenes=None, period=None, cycle=None, evidence=None):
    if stop_mode(root):
        raise EvaluationInterrupted("Stopped before starting another evaluation group.")
    directory.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-u", "-m", "fastwam.memory_s1.eval_parallel", "run",
               "--config", str(cfg_file), "--weights", str(weights), "--output", str(directory),
               "--mode", mode, "--conditions", *conditions, "--gpus", args.gpus,
               "--episode-timeout", str(args.episode_timeout)]
    if scenes is not None:
        command += ["--scenes-from", str(scenes)]
    from .history import override_online, online_arguments
    sampling_cfg = load_config(cfg_file)
    override_online(sampling_cfg, period=period, cycle=cycle)
    command += online_arguments(sampling_cfg)
    if evidence:
        command += ["--evidence", str(evidence)]
    if any((directory / name).exists() for name in ("queue.json", "launcher.json", "STOP.json")):
        command.append("--resume")
    # The parent backs up all groups together and verifies immutable readback.
    atomic_json(root / "active.json", {"directory": str(directory), "command": command})
    with (directory / "launcher.log").open("a", encoding="utf-8") as log:
        offset = log.tell()
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        atomic_json(root / "active.json", {"directory": str(directory), "command": command, "owner": process_identity(process.pid)})
        last_log, last_backup, uploaded = 0, time.monotonic(), completed_count(root)
        try:
            while process.poll() is None:
                if stop_mode(root):
                    atomic_json(directory / "STOP.json", read_json(root / "STOP.json"))
                if time.monotonic()-last_log >= 15:
                    with (directory / "launcher.log").open(encoding="utf-8", errors="replace") as stream:
                        stream.seek(offset)
                        lines = stream.read().splitlines()
                        offset = stream.tell()
                    for line in lines[-40:]:
                        # The parent prints a single structured progress block.
                        if not line.startswith(("[progress]", "[active]")):
                            print(f"[{directory.name}] {line}", flush=True)
                    print_overall(root, args.phase)
                    if args.phase == "selection" and getattr(args, "runtime_profile", "") == "fused-resident":
                        from .fused_evaluation import comparison_table
                        comparison_table(root, load_config(cfg_file), read_json(root / "identity.json"))
                    last_log = time.monotonic()
                count = completed_count(root)
                if args.hf_results and not stop_mode(root) and count > uploaded and (count-uploaded >= 5 or time.monotonic()-last_backup >= 600):
                    try:
                        upload_compact(load_config(cfg_file), Path(load_config(cfg_file)["paths"]["run"]), root, args.phase)
                        uploaded, last_backup = count, time.monotonic()
                    except Exception as error:
                        atomic_json(root / "BACKUP_PENDING.json", {"phase": args.phase, "error": repr(error)})
                        stop_request(root, "drain", 120)
                if stop_mode(root) == "now":
                    deadline = read_json(root / "STOP.json").get("deadline", time.time())
                    if time.time() > deadline+30:
                        from .eval_parallel import terminate_owned, cleanup_simulators
                        terminate_owned(process)
                        cleanup_simulators(directory)
                        break
                time.sleep(.5)
            if stop_mode(root):
                raise EvaluationInterrupted("Stopped; completed episodes remain reusable.")
            if process.returncode:
                details = failure_report(directory)
                (root / "FAILURE_DETAILS.txt").write_text(details+"\n", encoding="utf-8")
                raise RuntimeError(f"Evaluation exited {process.returncode}. Child diagnostics:\n{details}")
        finally:
            if process.poll() is None:
                from .eval_parallel import terminate_owned
                terminate_owned(process)
    value = read_json(directory / "summary.json")
    if not value.get("complete") or (mode != "diagnostic" and value.get("success_rate") is None):
        raise ValueError("A partial/prefix evaluation cannot select a checkpoint.")
    if args.hf_results:
        upload_compact(load_config(cfg_file), Path(load_config(cfg_file)["paths"]["run"]), root, args.phase)
    return value


def offline(cfg, run, root, weights, identity, args):
    import torch
    from .data import CachedEpisodes
    from .evaluate import validate
    from .model import S1Model
    from .eval_parallel import gpu_inventory
    gpu = int(args.gpus.split(",")[0])
    os.environ["CUDA_VISIBLE_DEVICES"] = gpu_inventory()[gpu]
    device = torch.device("cuda:0")
    model = S1Model(cfg, device)
    data = CachedEpisodes(cfg, "val")
    if data.signature != identity["training"]["cache_signature"]:
        raise ValueError("Offline evaluation requires the training cache contract; rebuild matching cache if absent.")
    records = []
    try:
        for step in milestone_steps(cfg):
            check_stop(root)
            payload = torch.load(weights[step], map_location="cpu", weights_only=True)
            if payload["identity"] != identity["training"] or payload["completed_updates"] != step:
                raise ValueError("Weight tensor payload differs from its export index.")
            model.memory.load_state_dict(payload["memory"], strict=True)
            for period in (1, 4, 8, 16):
                output = root / "offline" / f"step_{step:06d}" / f"T{period}.json"
                row = checked_result(output, identity)
                if row is None:
                    result = validate(model, data, cfg, device, period=period,
                                      progress_path=output.with_name(f"T{period}_cursor.json"), stop_root=root)
                    row = {"identity": identity, "step": step, "period": period, "result": result}
                    atomic_json(output, row)
                records.append(row)
                print(f"[offline] step={step} T={period} FM={row['result']['fm']:.6f}", flush=True)
    finally:
        del model
        gc.collect()
        torch.cuda.empty_cache()
    with (root / "offline.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("step", "period", "task", "fm", "sample_mse"))
        writer.writeheader()
        for row in records:
            for task, metrics in row["result"]["by_task"].items():
                writer.writerow({"step": row["step"], "period": row["period"], "task": task, **metrics})
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    figure, axes = plt.subplots(1, 2, figsize=(11, 4))
    for period in (1, 4, 8, 16):
        selected = [r for r in records if r["period"] == period]
        for axis, key in zip(axes, ("fm", "sample_mse")):
            axis.plot([r["step"] for r in selected], [r["result"][key] for r in selected], marker="o", label=f"T={period}")
            axis.set(xlabel="Completed optimizer updates", ylabel=key)
            axis.grid(alpha=.25)
            axis.legend()
    figure.tight_layout()
    for suffix in ("png", "pdf"):
        figure.savefig(root / f"offline.{suffix}", dpi=160)
    plt.close(figure)


def selection(cfg, cfg_file, run, root, weights, identity, args):
    fused = args.runtime_profile == "fused-resident"
    spec = comparison_spec(cfg)
    steps = spec["steps"]
    candidates = [step for step in steps if step > 0]
    scene_source = None
    if fused:
        from .fused_evaluation import inherit_scenes, comparison_table
        scene_source = inherit_scenes(cfg, root)
        comparison_table(root, cfg, identity, render=True)
    labels = ["base" if step == 0 else f"step {step}" for step in steps]
    print(f"[protocol] {' -> '.join(labels)} | put_back_block + swap_blocks | "
          f"10 shared scenes/task = {20 * len(steps)} episodes | T=8 | predict/execute/denoise=32/16/10", flush=True)
    for step in candidates:
        checked = checked_result(root / "offline" / f"step_{step:06d}" / "T8.json", identity)
        if checked is None:
            raise ValueError("Run the offline phase before checkpoint selection.")
    scenes = scene_source
    records = []
    for step in steps:
        check_stop(root)
        directory = root / "selection" / ("base" if step == 0 else f"step_{step:06d}")
        result = closed_child(cfg_file, weights[step], root, directory,
                              "internal", ["gate_zero" if step == 0 else "full"], args, scenes=scenes)
        if scenes is None:
            scenes = directory / "scenes.json"
        if fused:
            table = comparison_table(root, cfg, identity, render=True)
            row = next(r for r in table["models"] if r["step"] == step)
            if not row["complete"] or row["mean_success_rate"] != result["success_rate"]:
                raise ValueError("Candidate macro average/completeness differs from episode summary")
        if step == 0:
            continue
        fm = read_json(root / "offline" / f"step_{step:06d}" / "T8.json")["result"]["fm"]
        records.append({"step": step, "success_rate": result["success_rate"], "fm": fm,
                        "weight_sha256": sha256(weights[step])})
        atomic_json(root / "candidates.json", {"identity": identity, "candidates": records})
    best = min(records, key=lambda row: (-row["success_rate"], row["fm"], row["step"]))
    winner_root = root if fused else run
    (winner_root / "weights").mkdir(exist_ok=True)
    temporary = winner_root / "weights" / "best.pt.partial"
    shutil.copy2(weights[best["step"]], temporary)
    temporary.replace(winner_root / "weights" / "best.pt")
    value = {**best, "identity": identity, "criterion": "internal_success_then_T8_FM_then_earlier_update",
             "candidate_steps": candidates, "evaluated_steps": steps, "scenes_sha256": sha256(scenes),
             "scope": f"best_of_{len(candidates)}_selected_milestones_not_all_training_updates",
             "tied_success_steps": [r["step"] for r in records if r["success_rate"] == best["success_rate"]],
             "independent_test": False, "weight_file": str(weights[best["step"]])}
    atomic_json(root / "BEST.json", value)
    if not fused:
        atomic_json(run / "BEST.json", value)
    else:
        comparison_table(root, cfg, identity, render=True)
    with (root / "candidates.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f"[best] step={best['step']} success={best['success_rate']:.4f} FM={best['fm']:.6f}", flush=True)


def final_evaluation(cfg_file, run, root, weights, identity, args):
    best = checked_result(root / "BEST.json", identity)
    if best is None:
        raise ValueError("Complete the selection phase first.")
    weight = weights[best["step"]]
    base = root / "official" / "base"
    if args.phase == "official":
        closed_child(cfg_file, weights[0], root, base, "official", ["gate_zero"], args)
        closed_child(cfg_file, weight, root, root / "official" / "best", "official", ["full"], args,
                     scenes=base / "scenes.json")
        return
    if not (base / "summary.json").exists() or not read_json(base / "summary.json").get("complete"):
        raise ValueError("Complete the official phase first to freeze the shared scene bank.")
    scenes = base / "scenes.json"
    closed_child(cfg_file, weight, root, root / "memory" / "ablations", "official",
                 ["full", "current_only", "gate_zero"], args, scenes=scenes)
    for period in (1, 4, 8, 16):
        check_stop(root)
        closed_child(cfg_file, weight, root, root / "memory" / f"T{period}", "official", ["full"],
                     args, scenes=scenes, period=period)
    closed_child(cfg_file, weight, root, root / "memory" / "cycle_8_4_16", "official", ["full"],
                 args, scenes=scenes, cycle="8,4,16")
    if args.evidence:
        closed_child(cfg_file, weight, root, root / "memory" / "deletion", "official",
                     ["full", "delete_critical", "delete_irrelevant"], args, scenes=scenes, evidence=args.evidence)
    else:
        atomic_json(root / "memory" / "DELETION_PENDING.json", {"reason": "Reviewed evidence interval annotations are required; none were invented."})


def import_selection(source, run, root, weights, identity, cfg):
    """Carry a verified selection into a new evaluation environment without merging scores."""
    source = Path(source).resolve()
    best = read_json(source / "BEST.json")
    prior = best["identity"]
    if prior["training"] != identity["training"] or prior["weights"] != identity["weights"]:
        raise ValueError("Imported selection refers to another training run or candidate weights.")
    candidates = read_json(source / "candidates.json")
    rows = candidates["candidates"]
    if candidates["identity"] != prior or sorted(row["step"] for row in rows) != milestone_steps(cfg):
        raise ValueError("Imported selection lacks a complete candidate table.")
    scene_path = source / "selection/base/scenes.json"
    if best["scenes_sha256"] != sha256(scene_path):
        raise ValueError("Imported selection scene bank changed.")
    from .eval_parallel import protocol
    if read_json(scene_path)["contract"] != protocol(cfg, "internal"):
        raise ValueError("Imported selection uses another internal evaluation protocol.")
    if not read_json(source / "selection/base/summary.json").get("complete"):
        raise ValueError("Imported selection baseline is incomplete.")
    for row in rows:
        step = row["step"]
        if row["weight_sha256"] != sha256(weights[step]):
            raise ValueError("Imported candidate checksum differs.")
        offline = checked_result(source / "offline" / f"step_{step:06d}" / "T8.json", prior)
        summary = read_json(source / "selection" / f"step_{step:06d}" / "summary.json")
        scenes = source / "selection" / f"step_{step:06d}" / "scenes.json"
        if (offline is None or offline["result"]["fm"] != row["fm"] or
                not summary.get("complete") or summary.get("success_rate") != row["success_rate"] or
                sha256(scenes) != best["scenes_sha256"]):
            raise ValueError("Imported candidate results or shared scenes changed.")
    winner = min(rows, key=lambda row: (-row["success_rate"], row["fm"], row["step"]))
    if any(best[key] != value for key, value in winner.items()):
        raise ValueError("Imported best does not match the declared selection rule.")
    value = {**best, "identity": identity, "selection_identity": prior,
             "selection_source_sha256": sha256(source / "BEST.json"),
             "selection_source": str(source), "note": "Selection scores belong to the recorded source environment."}
    existing = checked_result(root / "BEST.json", identity)
    if existing is not None and existing != value:
        raise ValueError("A different selection already exists; use another output directory.")
    shutil.copy2(weights[best["step"]], run / "weights/best.pt")
    atomic_json(root / "BEST.json", value)
    atomic_json(run / "BEST.json", value)


def upload_compact(cfg, run, root, phase):
    directory = root / "packages" / f"{phase}_{time.time_ns()}"
    directory.mkdir(parents=True)
    package = directory / "posttrain.tar.zst"
    snapshot = root / "packages" / f"snapshot_{time.time_ns()}"
    snapshot.mkdir()
    print(f"[backup] snapshot started: {directory.name}", flush=True)
    backed_up = 0
    backup_started = time.monotonic()
    try:
        files = [p for p in root.rglob("*") if p.is_file() and
                 not set(p.relative_to(root).parts) & ({"packages"} if phase == 'diagnosis' else {"packages", "frames"}) and
                 (p.suffix in (".json", ".jsonl", ".csv", ".png", ".pdf", ".log", ".yaml") or
                  (phase == 'diagnosis' and p.suffix in ('.npz','.mp4','.command','.exit')) or
                  (phase == 'diagnosis' and 'evidence' in p.relative_to(root).parts and
                   (p.suffix in ('.py','.sh','.yml','.patch','.txt','.bundle') or p.name in ('simulator_sources.tar.gz','reference_sources.tar.gz'))))
                 and p.stat().st_size < (64 if phase == 'diagnosis' else 16) * 2**20]
        for path in files:
            target = snapshot / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        if phase == 'diagnosis':
            # New completion records bind physical/video evidence as well as
            # scalar reports. Never publish a compact package with dangling
            # artifact hashes or silently omit an oversized dependency.
            from .diagnosis_followup import validate_manifest
            for marker in root.glob('*.json'):
                value = read_json(marker)
                if not isinstance(value,dict) or value.get('complete') is not True or 'artifacts' not in value:
                    continue
                validate_manifest(root,value['artifacts'])
                for relative in value['artifacts']:
                    path=root/relative
                    if path.stat().st_size >= 64*2**20:
                        raise ValueError(f'Checksummed diagnostic exceeds compact backup limit: {path}; preserve separately before release')
                    target=snapshot/relative;target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(path,target)
        # Capture every checksummed completed-episode dependency, including larger logs.
        from .eval_state import EpisodeQueue
        for queue_path in root.rglob("queue.json"):
            if "packages" in queue_path.relative_to(root).parts:
                continue
            with locked(queue_path.parent / "queue.lock"):
                value = read_json(queue_path)
                backed_up += sum(job["state"] == "complete" for job in value["jobs"])
                for job in value["jobs"]:
                    if job["state"] == "complete":
                        EpisodeQueue(queue_path.parent).result(job, value["identity"])
                        attempt = queue_path.parent / job["directory"]
                        for name in (*read_json(attempt / "complete.json")["files"], "complete.json"):
                            target = snapshot / attempt.relative_to(root) / name
                            target.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(attempt / name, target)
                    else:
                        job["state"] = "pending"
                        job.pop("owner", None)
                if phase == 'diagnosis' and (all(j['state'] == 'complete' for j in value['jobs']) or
                                              'historical' in queue_path.relative_to(root).parts):
                    # Historical and completed queues are signed evidence;
                    # preserve their original bytes, not a reserialization.
                    shutil.copy2(queue_path, snapshot/queue_path.relative_to(root))
                else:
                    atomic_json(snapshot / queue_path.relative_to(root), value)
        # Include partial scene manifests even before the first policy episode exists.
        for plan in root.rglob("planning.json"):
            if "packages" in plan.relative_to(root).parts:
                continue
            scene_root = Path(read_json(plan)["directory"])
            for path in scene_root.glob("*.json"):
                target = snapshot / "scene_manifests" / scene_root.name / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
        migration = Path(cfg["root"]) / "scripts/memory_s1/portable/selection_migration.json"
        if migration.exists():
            for name in ["scripts/memory_s1/portable/selection_migration.json", *read_json(migration)["files"]]:
                target = snapshot / "evaluation_code" / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(Path(cfg["root"]) / name, target)
        if (root / "BEST.json").exists():
            best_record = read_json(root / "BEST.json")
            best_weight = root / "weights/best.pt"
            if not best_weight.exists():
                best_weight = run / "weights/best.pt"
            if sha256(best_weight) != best_record["weight_sha256"]:
                raise ValueError("Best weight differs from this comparison; refusing to upload another run's winner")
            target = snapshot / "weights/best.pt"
            target.parent.mkdir(exist_ok=True)
            shutil.copy2(best_weight, target)
        if phase == 'diagnosis':
            for marker in root.glob('*.json'):
                value=read_json(marker)
                if isinstance(value,dict) and value.get('complete') is True and 'artifacts' in value:
                    validate_manifest(snapshot,value['artifacts'])
        files = sorted(p for p in snapshot.rglob("*") if p.is_file())
        manifest = {p.relative_to(snapshot).as_posix(): sha256(p) for p in files}
        atomic_json(directory / "manifest.json", {"files": manifest, "phase": phase, "selection_completed": backed_up})
        with package.open("wb") as stream:
            process = subprocess.Popen(["zstd", "-T2", "-3", "-c"], stdin=subprocess.PIPE, stdout=stream)
            try:
                with tarfile.open(fileobj=process.stdin, mode="w|") as archive:
                    for path in files:
                        archive.add(path, arcname=path.relative_to(snapshot).as_posix(), recursive=False)
                    archive.add(directory / "manifest.json", arcname="manifest.json", recursive=False)
            finally:
                process.stdin.close()
                code = process.wait()
            if code:
                raise RuntimeError("Compact report compression failed")
    finally:
        shutil.rmtree(snapshot)
    prefix = f"posttrain/{run.name}/{phase}/{directory.name}"
    environment = dict(os.environ)
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
        environment.pop(name, None)
    command = [cfg["hf"]["python"], str(Path(cfg["root"]) / "scripts/memory_s1/hf_tools.py"),
               "upload-package", "--repo", cfg["hf"]["backup_repo"], "--repo-type", "model", "--directory", str(directory),
               "--prefix", prefix, "--quota-gib", str(cfg["hf"]["quota_gib"]),
               "--reserve-gib", str(cfg["hf"]["reserve_gib"])]
    result = subprocess.run(command, env=environment, check=True, capture_output=True, text=True, timeout=600)
    print(result.stdout, flush=True)
    revision = re.search(r"revision=([0-9a-f]{40})", result.stdout)
    if revision is None:
        raise ValueError("HF upload returned no immutable revision.")
    # Call the installed CLI executable, whose module entry point varies by release.
    download = [str(Path(cfg["hf"]["python"]).with_name("hf")), "download", cfg["hf"]["backup_repo"],
                f"{prefix}/posttrain.tar.zst", "--revision", revision[1], "--local-dir", str(directory / "readback")]
    subprocess.run(download, check=True, env=environment, timeout=600)
    recovered = directory / "readback" / prefix / "posttrain.tar.zst"
    if sha256(recovered) != sha256(package):
        raise ValueError("HF post-training package failed readback.")
    atomic_json(root / f"HF_{phase}.json", {"revision": revision[1], "package": f"{prefix}/posttrain.tar.zst",
                                           "sha256": sha256(package), "repo": cfg["hf"]["backup_repo"], "readback_verified": True,
                                           "completed": backed_up, "seconds": time.monotonic()-backup_started, "time": time.time()})
    (root / "BACKUP_PENDING.json").unlink(missing_ok=True)
    print(f"[backup] verified revision={revision[1]} completed={backed_up} seconds={time.monotonic()-backup_started:.1f}", flush=True)


def completed_count(root):
    state = read_json(Path(root) / "status.json") if (Path(root) / "status.json").exists() else {}
    prefix = "qualification" if state.get("phase") == "qualify" else "selection"
    return sum(sum(j["state"] == "complete" for j in read_json(path)["jobs"])
               for path in Path(root).glob(f"{prefix}/*/queue.json"))


def print_overall(root, phase):
    root = Path(root)
    cfg_path = root / "evaluation_config.yaml"
    cfg = load_config(cfg_path) if cfg_path.exists() else None
    spec = comparison_spec(cfg) if cfg else None
    labels = [("base" if step == 0 else f"step_{step:06d}") for step in spec["steps"]] if spec else None
    pattern = "qualification/*/queue.json" if phase == "qualify" else "selection/*/queue.json"
    jobs, results, live, limits, existing = [], [], [], {}, set()
    nominal = cfg.get("selection_runtime", {}).get("eta_target_limits", {}) if cfg else {}
    if phase == "qualify" and cfg and cfg.get("selection_runtime", {}).get("profile") == "fused-resident":
        nominal = {task: 32 for task in spec["tasks"]}
    for path in root.glob(pattern):
        if phase == "selection" and labels is not None and path.parent.name not in labels:
            raise ValueError(f"Unexpected model queue in this comparison: {path.parent.name}")
        label = path.parent.name
        existing.add(label)
        # Rates may be borrowed across memory checkpoints, never from base.
        family = "base" if label == "base" else "memory"
        prefix = f"{label}:"
        value = read_json(path)
        for job in value["jobs"]:
            task = job["scene"]["task"]
            key = f"{family}:{task}"
            if task in nominal:
                limits[key] = nominal[task]
            jobs.append({**job, "id": prefix+job["id"], "scene": {**job["scene"], "task": key}})
            if job["state"] == "complete":
                row = read_json(path.parent / job["directory"] / "result.json")
                results.append({**row, "task": key})
        for row in live_details(path.parent / "simulator_progress"):
            if row.get("phase") == "rollout" and row.get("task"):
                live.append({**row, "job_id": prefix+row.get("job_id", ""),
                             "task": f"{family}:{row['task']}"})
    total = len(jobs)
    if cfg:
        total = (2 if cfg.get("selection_runtime", {}).get("profile") == "fused-resident" else 12) if phase == "qualify" else len(spec["tasks"]) * spec["episodes_per_task"] * len(labels)
    if phase == "selection" and spec:
        for label in labels:
            if label in existing:
                continue
            family = "base" if label == "base" else "memory"
            for task in spec["tasks"]:
                key = f"{family}:{task}"
                if task in nominal:
                    limits[key] = nominal[task]
                for ordinal in range(spec["episodes_per_task"]):
                    jobs.append({"id": f"{label}:{task}:{ordinal}", "state": "pending",
                                 "scene": {"task": key, "seed": None}})
    projection = episode_work(jobs, results, live, limits)
    unknown = projection["unknown_duration_episodes"] + max(0, total-len(jobs))
    estimate = projection["eta_seconds"] if not unknown else None
    launcher = read_json(root / "launcher.json") if (root / "launcher.json").exists() else {}
    elapsed = time.time()-launcher["started"] if "started" in launcher else None
    progress_record = {**projection, "eta_seconds": estimate, "unknown_duration_episodes": unknown,
                       "phase": phase, "completed": len(results), "total": total, "elapsed_seconds": elapsed}
    atomic_json(root / "progress.json", progress_record)
    partial = (f" | calibrated_work~{duration(projection['known_remaining_work_seconds'])}; "
               f"uncalibrated_episodes={unknown}") if unknown else ""
    print(f"[{phase}] overall={len(results)}/{total or '?'} | elapsed={duration(elapsed)} "
          f"| remaining_rollout_work~{duration(estimate)}{partial} "
          "(GPU-time to target limits; includes current remaining targets; "
          "initialization/cleanup/upload excluded; task/checkpoint rates provisional)", flush=True)
    if (root / "active.json").exists():
        active = Path(read_json(root / "active.json")["directory"])
        if (active / "status.json").exists():
            status = read_json(active / "status.json")
            print(f"[current {active.name}] stage={status.get('stage')} "
                  f"completed={status.get('completed', status.get('accepted'))}/{status.get('total', '?')} "
                  f"elapsed={duration(status.get('elapsed_seconds'))} "
                  f"remaining_rollout~{duration(status.get('eta_seconds'))} "
                  f"source={status.get('eta_reason', 'waiting for startup')}", flush=True)
            for row in live_details(active / "simulator_progress") + live_details(active / "workers"):
                print(f"  {format_active(row)}", flush=True)


def wait_stopped(root, deadline):
    helper = Path(__file__).resolve().parents[3] / "scripts/memory_s1/portable/selection_control.py"
    subprocess.run([sys.executable, str(helper), "--output", str(root), "--wait-only",
                    "--deadline", str(deadline)], check=True)


def runtime_options(profile):
    if profile == "fused-resident":
        return {"version": "selection-runtime-v4", "profile": profile, "resident_simulator": True,
                "backend": "fused_graph_v1", "one_planning_task_per_gpu": True, "serialize_arm_warmup": True,
                # Projection only; the actual environment still enforces step_lim.
                # Live observations override these nominal target caps.
                "eta_target_limits": {"put_back_block": 500, "swap_blocks": 1000}}
    return {"version": "selection-runtime-v2", "profile": profile,
            "resident_simulator": profile in ("resident", "async-resident"),
            "backend": "builtin_torch_async_v2" if profile in ("async", "async-resident") else "builtin_torch_v1",
            "one_planning_task_per_gpu": True, "serialize_arm_warmup": True}


def qualification_binding(cfg, profile):
    if profile == "fused-resident":
        from .fused_evaluation import qualification_key
        return qualification_key(cfg)
    from .eval_parallel import protocol
    from .simulator_backend import backend_contract
    contract = protocol(cfg, "internal")
    contract["simulator_backend"] = backend_contract("builtin_torch_v1")
    contract.pop("scene_filter_backend", None)
    return {"source": code_version(cfg["root"]), "protocol": contract, "profile": profile,
            "base_sha256": sha256(cfg["paths"]["base"]), "stats_sha256": sha256(cfg["paths"]["stats"]),
            "runtime": subprocess.check_output([cfg["closed_loop"]["simulator_python"], "-c",
                "import sys,torch; print(sys.version); print(torch.__version__,torch.version.cuda); print(torch.cuda.get_device_name(0))"], text=True)}


def verify_qualification(cfg, args):
    if not args.qualification_report:
        raise ValueError("This acceleration profile requires --qualification-report; serial is the safe fallback.")
    report = read_json(args.qualification_report)
    if report.get("passed") is not True or report.get("binding") != qualification_binding(cfg, args.runtime_profile):
        raise ValueError("Acceleration qualification is absent, failed, or belongs to a different environment/source.")
    source_root = Path(report["directory"])
    for name, expected in report["files"].items():
        if sha256(source_root / name) != expected:
            raise ValueError(f"Qualification evidence changed: {name}")


def qualify(cfg, run, root, weights, args):
    """Real simulator checks, explicitly requested; never part of selection itself."""
    if args.runtime_profile == "fused-resident":
        from .fused_evaluation import qualify_fused
        return qualify_fused(cfg, run, root, weights, args)
    import yaml
    from .eval_parallel import prepare_scenes, gpu_inventory
    from .eval_state import EpisodeQueue
    if args.runtime_profile == "serial":
        raise ValueError("Select the acceleration profile to qualify")
    base_cfg = copy.deepcopy(cfg)
    base_cfg["selection_runtime"] = runtime_options("serial")
    inventory = gpu_inventory()
    gpu = [inventory[int(args.gpus.split(",")[0])]]
    contract, scenes, _ = prepare_scenes(base_cfg, "internal", gpu, root)
    scene_file = root / "qualification_scenes.json"
    atomic_json(scene_file, {"contract": contract, "scenes": scenes})
    summaries = {}
    for name, profile in (("reference", "serial"), ("reference_repeat", "serial"), ("candidate", args.runtime_profile)):
        check_stop(root)
        current = copy.deepcopy(base_cfg)
        current["selection_runtime"] = {**runtime_options(profile), "qualification": True}
        current["diagnostic"] = {"scenes_from": str(scene_file), "episodes_per_task": 2,
                                 "max_targets": 32, "record_feedback": True}
        # The original frozen scenes/instructions stay identical; only the declared backend changes.
        from .eval_parallel import protocol
        profile_scenes = root / f"{name}_scenes.json"
        atomic_json(profile_scenes, {"contract": protocol(current, "internal"), "scenes": scenes})
        current["diagnostic"]["scenes_from"] = str(profile_scenes)
        path = root / f"{name}.yaml"
        path.write_text(yaml.safe_dump(current, sort_keys=False), encoding="utf-8")
        prefix_args = copy.copy(args)
        prefix_args.gpus = args.gpus.split(",")[0]
        closed_child(path, weights[0], root, root / "qualification" / name,
                     "diagnostic", ["gate_zero"], prefix_args)
        summaries[name] = EpisodeQueue(root / "qualification" / name)
    files, comparisons, timings = {}, [], []
    reference = summaries["reference"].snapshot()
    for name, queue in summaries.items():
        state = queue.snapshot()
        if len(state["jobs"]) != 4 or any(j["state"] != "complete" for j in state["jobs"]):
            raise ValueError("Qualification requires two complete prefix scenes per task")
        for job in state["jobs"]:
            result = queue.result(job, state["identity"])
            timings.append({"group": name, "job": job["id"], "wall_seconds": result["wall_seconds"],
                            "setup_seconds": result["timings"]["setup_seconds"], "executed_targets": result["executed_targets"]})
            prior = next(j for j in reference["jobs"] if j["id"] == job["id"])
            for filename in ("qualification_trace.jsonl", "executed_actions.jsonl"):
                path = queue.root / job["directory"] / filename
                baseline = summaries["reference"].root / prior["directory"] / filename
                actual = [json.loads(line) for line in path.read_text().splitlines()]
                expected = [json.loads(line) for line in baseline.read_text().splitlines()]
                equal = bool(actual) and actual == expected
                files[str(path.relative_to(root))] = sha256(path)
                first = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b),
                             min(len(actual), len(expected)) if len(actual) != len(expected) else None)
                comparisons.append({"group": name, "job": job["id"], "file": filename, "exact": equal,
                                    "first_different_row": first, "rows": len(actual)})
            if not result.get("executed_targets"):
                raise ValueError("Qualification did not execute targets")
    passed = all(row["exact"] for row in comparisons)
    with (root / "qualification_timings.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=tuple(timings[0]))
        writer.writeheader()
        writer.writerows(timings)
    atomic_json(root / "QUALIFICATION.json", {"passed": passed, "binding": qualification_binding(cfg, args.runtime_profile),
                "directory": str(root), "files": files, "comparisons": comparisons, "timings": timings,
                "scope": "same inputs/actions/physical feedback for two 32-target scenes per task; no full-task success claim"})
    if not passed:
        raise ValueError("Acceleration changed observed results (or reference was not repeatable); keep serial profile and inspect QUALIFICATION.json")
    print("[qualification] exact reference repeat and accelerated reset/action comparisons passed", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("run", "status", "stop", "backup"))
    parser.add_argument("--config")
    parser.add_argument("--run")
    parser.add_argument("--output", required=True)
    parser.add_argument("--phase", choices=("offline", "selection", "official", "memory", "qualify"))
    parser.add_argument("--gpus", default="0")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--hf-results", action="store_true")
    parser.add_argument("--evidence")
    parser.add_argument("--offline-from", help="Import matching previous offline metrics with explicit provenance")
    parser.add_argument("--runtime-profile", choices=("serial", "async", "resident", "async-resident", "fused-resident"), default="serial")
    parser.add_argument("--frozen-scenes", help="Existing complete twenty-scene bank; fused mode never searches new seeds")
    parser.add_argument("--qualification-report")
    parser.add_argument("--mode", choices=("drain", "now"), default="drain")
    parser.add_argument("--grace-seconds", type=int, default=120)
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--selection-from", help="Verified unpacked selection evidence from another evaluation environment")
    parser.add_argument("--episode-timeout", type=int, default=3600)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    if args.command == "stop":
        request = stop_request(root, args.mode, args.grace_seconds)
        print(f"Stop requested: {args.mode}; deadline={time.ctime(request['deadline'])}", flush=True)
        if args.wait:
            wait_stopped(root, request["deadline"])
        return
    if args.command == "status":
        phase = read_json(root / "status.json").get("phase", "selection") if (root / "status.json").exists() else "selection"
        print_overall(root, phase)
        if (root / "comparison.csv").exists():
            print((root / "comparison.csv").read_text(encoding="utf-8-sig"))
        for name in ("status.json", "BACKUP_PENDING.json", "HF_selection.json", "BEST.json"):
            if (root / name).exists():
                value = read_json(root / name)
                print(name, json.dumps({k: v for k, v in value.items() if k != "identity"}, indent=2))
        return
    if args.command == "backup":
        with locked(root / "launcher.lock", blocking=False):
            cfg = load_config(root / "evaluation_config.yaml")
            upload_compact(cfg, Path(cfg["paths"]["run"]), root, args.phase or "selection")
            previous = read_json(root / "status.json") if (root / "status.json").exists() else {}
            previous.update(backup_pending=False, backup_verified=True)
            if (root / "BEST.json").exists() and (args.phase or "selection") == "selection":
                previous["state"] = "complete"
            atomic_json(root / "status.json", previous)
        return
    with locked(root / "launcher.lock", blocking=False):
        run_phase(args, root)


def run_phase(args, root):
    if not args.config or not args.phase:
        raise ValueError("run requires --config and --phase")
    if args.selection_from and args.phase not in ("official", "memory"):
        raise ValueError("--selection-from applies only to official or memory evaluation")
    cfg = load_config(args.config)
    run = Path(args.run or cfg["paths"]["run"]).resolve()
    identity, weights = verified_weights(run)
    if read_json(run / "MILESTONES.json")["candidate_steps"] != milestone_steps(cfg):
        raise ValueError("Candidate schedule differs from the exported training schedule.")
    migration = source_migration(cfg, identity["code"])
    cfg["selection_runtime"] = runtime_options(args.runtime_profile)
    spec = comparison_spec(cfg)
    if spec["steps"] != [0, 500, 1000, 1500, 2000] and args.runtime_profile != "fused-resident":
        raise ValueError("Selected-checkpoint comparison requires fused-resident and an existing frozen scene bank")
    if args.runtime_profile == "fused-resident":
        from .fused_evaluation import runtime_binding
        if args.phase not in ("qualify", "selection") or not args.frozen_scenes:
            raise ValueError("fused-resident requires --frozen-scenes and phase qualify|selection")
        if args.gpus != "0":
            raise ValueError("This H100 comparison profile uses exactly GPU 0")
        os.environ.pop("CUDA_LAUNCH_BLOCKING", None)
        cfg["selection_runtime"]["frozen_scenes"] = str(Path(args.frozen_scenes).resolve())
        cfg["selection_runtime"]["environment"] = runtime_binding(cfg)
        atomic_json(root / "SIMULATOR_ENVIRONMENT.json", cfg["selection_runtime"]["environment"])
    atomic_json(root / "SOURCE_MIGRATION.json", migration)
    if args.phase not in ("qualify", "offline") and args.runtime_profile != "serial":
        verify_qualification(cfg, args)
        cfg["selection_runtime"]["qualification_report"] = str(Path(args.qualification_report).resolve())
    if identity["base_sha256"] != sha256(cfg["paths"]["base"]) or identity["stats_sha256"] != sha256(cfg["paths"]["stats"]):
        raise ValueError("Evaluation base/statistics differ from training.")
    cfg["paths"]["run"] = str(run)
    cfg["closed_loop"]["enabled"] = True
    root.mkdir(parents=True, exist_ok=True)
    import yaml
    cfg_file = root / "evaluation_config.yaml"
    resolved = yaml.safe_dump(cfg, sort_keys=False)
    if cfg_file.exists() and cfg_file.read_text(encoding="utf-8") != resolved:
        raise ValueError("Evaluation configuration changed; use another output directory.")
    cfg_file.write_text(resolved, encoding="utf-8")
    import torch
    runtime = {"torch": torch.__version__, "cuda": torch.version.cuda, "python": sys.version,
               "gpus": subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"], text=True)}
    evaluation_identity = {"training": identity, "weights": {str(k): sha256(v) for k, v in weights.items()},
                           "config_sha": fingerprint(cfg), "candidate_steps": milestone_steps(cfg), "runtime": runtime, "evaluation_code": migration["code"]}
    if cfg.get("comparison"):
        evaluation_identity["comparison"] = spec
    marker = root / "identity.json"
    if marker.exists() and read_json(marker) != evaluation_identity:
        raise ValueError("Evaluation environment/weights changed; use a separate output directory.")
    atomic_json(marker, evaluation_identity)
    if (root / "STOP_REQUESTED").exists() or (root / "STOP.json").exists():
        if not args.resume:
            raise ValueError("A stop marker exists; inspect status and pass --resume.")
        (root / "STOP_REQUESTED").unlink(missing_ok=True)
        (root / "STOP.json").unlink(missing_ok=True)
    atomic_json(root / "launcher.json", {"owner": process_identity(), "phase": args.phase, "argv": sys.argv, "started": time.time()})
    def stop(signum, frame):
        stop_request(root, "now", 30)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    started = time.monotonic()
    atomic_json(root / "status.json", {"phase": args.phase, "state": "running"})
    try:
        if args.offline_from:
            import_offline(args.offline_from, root, evaluation_identity, migration)
        if args.selection_from:
            import_selection(args.selection_from, run, root, weights, evaluation_identity, cfg)
        if args.phase == "qualify":
            qualify(cfg, run, root, weights, args)
        elif args.phase == "offline":
            offline(cfg, run, root, weights, evaluation_identity, args)
        elif args.phase == "selection":
            selection(cfg, cfg_file, run, root, weights, evaluation_identity, args)
        else:
            final_evaluation(cfg_file, run, root, weights, evaluation_identity, args)
        if args.hf_results:
            upload_compact(cfg, run, root, args.phase)
        atomic_json(root / "status.json", {"phase": args.phase, "state": "complete", "seconds": time.monotonic()-started})
    except EvaluationInterrupted:
        if args.hf_results:
            try:
                upload_compact(cfg, run, root, args.phase)
            except Exception as error:
                atomic_json(root / "BACKUP_PENDING.json", {"phase": args.phase, "error": repr(error)})
        atomic_json(root / "status.json", {"phase": args.phase, "state": "stopped", "seconds": time.monotonic()-started})
        raise SystemExit(2)
    except Exception as error:
        if args.hf_results:
            atomic_json(root / "BACKUP_PENDING.json", {"phase": args.phase, "error": repr(error)})
        atomic_json(root / "status.json", {"phase": args.phase, "state": "error", "error": repr(error), "seconds": time.monotonic()-started})
        raise


if __name__ == "__main__":
    main()
