"""Install a verified HF snapshot without losing local interrupted training logs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import time
from fastwam.memory_s1.common import load_config, read_json, sha256, atomic_json
from fastwam.memory_s1.checkpoint import verified_load
from fastwam.memory_s1.eval_state import process_identity


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--snapshot", required=True, help="Downloaded runs/run_id folder")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    source, destination = Path(args.snapshot).resolve(), Path(cfg["paths"]["run"]).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Restore source and destination must be distinct nonoverlapping directories.")
    pid_file = destination / "launcher.pid"
    if pid_file.exists() and process_identity(int(pid_file.read_text())) is not None:
        raise ValueError("A recorded launcher is alive. Stop and inspect it before restoring.")
    pointer = read_json(source / "RESTORE_REMOTE.json")
    directory = source / "checkpoints" / pointer["directory"]
    saved = verified_load(directory)
    if saved["completed_updates"] != pointer["step"]:
        raise ValueError("Downloaded pointer and checkpoint disagree.")
    manifest = read_json(directory / "backup_manifest.json")
    for relative, expected in manifest["files"].items():
        path = (source / relative).resolve()
        if source not in path.parents or not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Invalid restore material: {relative}")
    destination.mkdir(parents=True, exist_ok=True)
    interrupted = destination / "interrupted_logs" / str(time.time_ns())
    for name in ("metrics.jsonl", "samples.jsonl"):
        path = destination / name
        if path.exists():
            interrupted.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, interrupted / name)
    for relative in manifest["files"]:
        if relative.startswith(("code/", "resource_metadata/")):
            continue
        path = source / relative
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    old_root = saved["config"]["root"]
    def rebase(value):
        if isinstance(value, str) and value.startswith(old_root + "/"):
            return cfg["root"] + value[len(old_root):]
        if isinstance(value, list):
            return [rebase(item) for item in value]
        if isinstance(value, dict):
            return {key: rebase(item) for key, item in value.items()}
        return value
    for path in (destination / "validation").rglob("evaluation.json"):
        # This file controls local executable/config paths and is not an immutable episode result.
        atomic_json(path, rebase(read_json(path)))
    restored_checkpoint = destination / "checkpoints" / pointer["directory"]
    continuation_name = f"checkpoints/{pointer['directory']}/continuation.json"
    if continuation_name not in manifest["files"]:
        (restored_checkpoint / "continuation.json").unlink(missing_ok=True)
    for relative in ("weights/best.pt", "BEST.json"):
        target = destination / relative
        if relative not in manifest["files"] and target.exists():
            interrupted.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), interrupted / target.name)
    shutil.copy2(directory / "backup_manifest.json", destination / "checkpoints" / pointer["directory"] / "backup_manifest.json")
    atomic_json(destination / "RESTORE_REMOTE.json", pointer)
    atomic_json(destination / "LATEST_LOCAL.json", {"step": pointer["step"], "directory": f"checkpoints/{pointer['directory']}"})
    atomic_json(destination / "LATEST_REMOTE.json", pointer)
    (destination / "STOP_REQUESTED").unlink(missing_ok=True)
    print(f"[restore] update={pointer['step']} phase={saved['progress'].get('phase', 'train')}")
    print(f"RESUME={destination / 'checkpoints' / pointer['directory'] / 'resume.pt'}")

if __name__ == "__main__":
    main()
