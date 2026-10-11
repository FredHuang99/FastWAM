"""Explicit, restartable post-training evaluation of four exported milestones."""
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
import time

from .common import atomic_json, code_version, fingerprint, load_config, read_json, sha256
from .eval_state import EvaluationInterrupted, check_stop, locked, process_identity
from .schedule import milestone_steps


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
                 scenes=None, period=8, cycle=None, evidence=None):
    directory.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-u", "-m", "fastwam.memory_s1.eval_parallel", "run",
               "--config", str(cfg_file), "--weights", str(weights), "--output", str(directory),
               "--mode", mode, "--conditions", *conditions, "--gpus", args.gpus,
               "--episode-timeout", str(args.episode_timeout)]
    if scenes is not None:
        command += ["--scenes-from", str(scenes)]
    if cycle:
        command += ["--history-cycle", cycle]
    else:
        command += ["--history-period", str(period)]
    if evidence:
        command += ["--evidence", str(evidence)]
    if (directory / "queue.json").exists():
        command.append("--resume")
    if args.hf_results:
        command.append("--hf-results")
    atomic_json(root / "active.json", {"directory": str(directory), "command": command})
    with (directory / "launcher.log").open("a", encoding="utf-8") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while process.poll() is None:
                if (root / "STOP_REQUESTED").exists():
                    atomic_json(directory / "STOP.json", {"mode": "now", "reason": "post-training stop"})
                time.sleep(0.5)
            check_stop(root)
            if process.returncode:
                raise RuntimeError(f"Evaluation exited {process.returncode}; inspect {directory / 'launcher.log'}")
        finally:
            if process.poll() is None:
                from .eval_parallel import terminate_owned
                terminate_owned(process)
    value = read_json(directory / "summary.json")
    if not value.get("complete") or value.get("success_rate") is None:
        raise ValueError("A partial/prefix evaluation cannot select a checkpoint.")
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
    for step in milestone_steps(cfg):
        checked = checked_result(root / "offline" / f"step_{step:06d}" / "T8.json", identity)
        if checked is None:
            raise ValueError("Run the offline phase before checkpoint selection.")
    baseline = root / "selection" / "base"
    closed_child(cfg_file, weights[0], root, baseline, "internal", ["gate_zero"], args)
    scenes = baseline / "scenes.json"
    records = []
    for step in milestone_steps(cfg):
        check_stop(root)
        result = closed_child(cfg_file, weights[step], root, root / "selection" / f"step_{step:06d}",
                              "internal", ["full"], args, scenes=scenes)
        fm = read_json(root / "offline" / f"step_{step:06d}" / "T8.json")["result"]["fm"]
        records.append({"step": step, "success_rate": result["success_rate"], "fm": fm,
                        "weight_sha256": sha256(weights[step])})
        atomic_json(root / "candidates.json", {"identity": identity, "candidates": records})
    best = min(records, key=lambda row: (-row["success_rate"], row["fm"], row["step"]))
    temporary = run / "weights" / "best.pt.partial"
    shutil.copy2(weights[best["step"]], temporary)
    temporary.replace(run / "weights" / "best.pt")
    value = {**best, "identity": identity, "criterion": "internal_success_then_T8_FM_then_earlier_update",
             "candidate_steps": milestone_steps(cfg), "scenes_sha256": sha256(scenes),
             "scope": "best_of_four_milestones_not_all_training_updates"}
    atomic_json(root / "BEST.json", value)
    atomic_json(run / "BEST.json", value)
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
    files = [p for p in root.rglob("*") if p.is_file() and
             not set(p.relative_to(root).parts) & {"packages", "frames", "attempt_001", "workers"} and
             p.suffix in (".json", ".csv", ".png", ".pdf") and p.stat().st_size < 16 * 2**20]
    if phase == "selection":
        files.append(run / "weights" / "best.pt")
    manifest = {str(p.relative_to(root)) if p.is_relative_to(root) else "weights/best.pt": sha256(p) for p in files}
    atomic_json(directory / "manifest.json", {"files": manifest, "phase": phase})
    with package.open("wb") as stream:
        process = subprocess.Popen(["zstd", "-T2", "-3", "-c"], stdin=subprocess.PIPE, stdout=stream)
        try:
            with tarfile.open(fileobj=process.stdin, mode="w|") as archive:
                for path in files:
                    name = str(path.relative_to(root)) if path.is_relative_to(root) else "weights/best.pt"
                    archive.add(path, arcname=name, recursive=False)
                archive.add(directory / "manifest.json", arcname="manifest.json", recursive=False)
        finally:
            process.stdin.close()
            code = process.wait()
        if code:
            raise RuntimeError("Compact report compression failed.")
    prefix = f"posttrain/{run.name}/{phase}/{directory.name}"
    environment = dict(os.environ)
    for name in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
        environment.pop(name, None)
    command = [cfg["hf"]["python"], str(Path(cfg["root"]) / "scripts/memory_s1/hf_tools.py"),
               "upload-package", "--repo", cfg["hf"]["backup_repo"], "--repo-type", "model", "--directory", str(directory),
               "--prefix", prefix, "--quota-gib", str(cfg["hf"]["quota_gib"]),
               "--reserve-gib", str(cfg["hf"]["reserve_gib"])]
    result = subprocess.run(command, env=environment, check=True, capture_output=True, text=True)
    print(result.stdout, flush=True)
    revision = re.search(r"revision=([0-9a-f]{40})", result.stdout)
    if revision is None:
        raise ValueError("HF upload returned no immutable revision.")
    # Call the installed CLI executable, whose module entry point varies by release.
    download = [str(Path(cfg["hf"]["python"]).with_name("hf")), "download", cfg["hf"]["backup_repo"],
                f"{prefix}/posttrain.tar.zst", "--revision", revision[1], "--local-dir", str(directory / "readback")]
    subprocess.run(download, check=True, env=environment)
    recovered = directory / "readback" / prefix / "posttrain.tar.zst"
    if sha256(recovered) != sha256(package):
        raise ValueError("HF post-training package failed readback.")
    atomic_json(root / f"HF_{phase}.json", {"revision": revision[1], "package": f"{prefix}/posttrain.tar.zst",
                                           "sha256": sha256(package), "repo": cfg["hf"]["backup_repo"]})


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("run", "status", "stop"))
    parser.add_argument("--config")
    parser.add_argument("--run")
    parser.add_argument("--output", required=True)
    parser.add_argument("--phase", choices=("offline", "selection", "official", "memory"))
    parser.add_argument("--gpus", default="0")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--hf-results", action="store_true")
    parser.add_argument("--evidence")
    parser.add_argument("--selection-from", help="Verified unpacked selection evidence from another evaluation environment")
    parser.add_argument("--episode-timeout", type=int, default=3600)
    args = parser.parse_args()
    root = Path(args.output).resolve()
    if args.command == "stop":
        atomic_json(root / "STOP.json", {"mode": "now", "time": time.time()})
        (root / "STOP_REQUESTED").touch()
        return
    if args.command == "status":
        for name in ("status.json", "active.json", "BEST.json", "launcher.json"):
            if (root / name).exists():
                print(name, json.dumps(read_json(root / name), indent=2))
        active = root / "active.json"
        if active.exists():
            child_status = Path(read_json(active)["directory"]) / "status.json"
            if child_status.exists():
                print("evaluation_progress", json.dumps(read_json(child_status), indent=2))
        return
    if not args.config or not args.phase:
        parser.error("run requires --config and --phase; phases are never chained implicitly")
    if args.selection_from and args.phase not in ("official", "memory"):
        parser.error("--selection-from applies only to official or memory evaluation")
    cfg = load_config(args.config)
    run = Path(args.run or cfg["paths"]["run"]).resolve()
    identity, weights = verified_weights(run)
    if read_json(run / "MILESTONES.json")["candidate_steps"] != milestone_steps(cfg):
        raise ValueError("Candidate schedule differs from the exported training schedule.")
    actual_code = code_version(cfg["root"])
    for key in ("core_sha", "implementation_sha", "support_sha"):
        if actual_code[key] != identity["code"][key]:
            raise ValueError(f"Restore the exact training code before evaluating: {key}")
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
                           "config_sha": fingerprint(cfg), "candidate_steps": milestone_steps(cfg), "runtime": runtime}
    marker = root / "identity.json"
    if marker.exists() and read_json(marker) != evaluation_identity:
        raise ValueError("Evaluation environment/weights changed; use a separate output directory.")
    atomic_json(marker, evaluation_identity)
    with locked(root / "launcher.lock", blocking=False):
        if (root / "STOP_REQUESTED").exists() or (root / "STOP.json").exists():
            if not args.resume:
                raise ValueError("A stop marker exists; inspect status and pass --resume.")
            (root / "STOP_REQUESTED").unlink(missing_ok=True)
            (root / "STOP.json").unlink(missing_ok=True)
        atomic_json(root / "launcher.json", {"owner": process_identity(), "phase": args.phase, "argv": sys.argv})
        def stop(signum, frame):
            atomic_json(root / "STOP.json", {"mode": "now", "signal": signum})
            (root / "STOP_REQUESTED").touch()
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        started = time.monotonic()
        atomic_json(root / "status.json", {"phase": args.phase, "state": "running"})
        try:
            if args.selection_from:
                import_selection(args.selection_from, run, root, weights, evaluation_identity, cfg)
            if args.phase == "offline":
                offline(cfg, run, root, weights, evaluation_identity, args)
            elif args.phase == "selection":
                selection(cfg, cfg_file, run, root, weights, evaluation_identity, args)
            else:
                final_evaluation(cfg_file, run, root, weights, evaluation_identity, args)
            if args.hf_results:
                upload_compact(cfg, run, root, args.phase)
            atomic_json(root / "status.json", {"phase": args.phase, "state": "complete", "seconds": time.monotonic()-started})
        except EvaluationInterrupted:
            atomic_json(root / "status.json", {"phase": args.phase, "state": "stopped", "seconds": time.monotonic()-started})
            raise SystemExit(2)
        except Exception as error:
            atomic_json(root / "status.json", {"phase": args.phase, "state": "error", "error": repr(error), "seconds": time.monotonic()-started})
            raise


if __name__ == "__main__":
    main()
