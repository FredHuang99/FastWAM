"""Inspect, request an episode-boundary stop, or salvage and stop a legacy run."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src/fastwam/memory_s1"))
from eval_state import digest, durable_json, is_alive, process_identity, read


def children_of(pid):
    entries = {}
    for directory in Path("/proc").iterdir():
        if not directory.name.isdigit():
            continue
        try:
            fields = (directory / "stat").read_text().rsplit(")", 1)[1].split()
            entries[int(directory.name)] = int(fields[1])
        except (FileNotFoundError, ProcessLookupError):
            pass
    owned = {pid}
    while True:
        added = {child for child, parent in entries.items() if parent in owned} - owned
        if not added:
            break
        owned.update(added)
    return [owner for child in sorted(owned) if (owner := process_identity(child)) is not None]


def command_line(pid):
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except FileNotFoundError:
        return ""


def legacy_snapshot(args, suffix):
    destination = Path(args.snapshot) / suffix
    destination.mkdir(parents=True, exist_ok=False)
    source = Path(args.diagnostic_root)
    if source.exists():
        shutil.copytree(source, destination / "diagnostic", ignore=shutil.ignore_patterns("*.sock"))
    logs = []
    base = Path(args.root) / "resources/RMBench/eval_result"
    for task in ("put_back_block", "swap_blocks"):
        for path in (base / task / "deploy_policy/demo_clean/memory_s1_diagnostic").glob("*/eval_log.txt"):
            target = destination / "official_logs" / path.relative_to(base)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            rows = []
            for match in re.finditer(r"episode_id=(\d+),\s*seed=(\d+),\s*result=(Success|Fail)", path.read_text()):
                rows.append({"task": task, "ordinal": int(match[1]), "seed": int(match[2]), "success": match[3] == "Success",
                             "instruction": None, "executed_targets": None, "max_reward": None,
                             "reuse": False, "reason": "The legacy log does not identify the literal instruction or full evaluation contract."})
            logs.append({"source": str(path), "sha256": digest(target), "records": rows})
    for name in ("base_diagnostic.pid", "base_diagnostic_latest_log.txt", "config_resolved.json", "identity.json"):
        path = source.parent / name
        if path.is_file():
            shutil.copy2(path, destination / name)
    durable_json(destination / "legacy_records.json", {"logs": logs, "note": "Confirmed old outcomes are preserved separately; frame directories do not prove completion."})
    print(f"[legacy snapshot] {destination}", flush=True)


def stop_legacy(args):
    pid = int(Path(args.launcher_pid_file).read_text().strip())
    owner = process_identity(pid)
    if owner is None or owner["state"] == "Z":
        legacy_snapshot(args, "already_stopped")
        print("Legacy launcher is no longer running. No process was signalled.")
        return
    command = command_line(pid)
    cwd = Path(f"/proc/{pid}/cwd").resolve()
    if "fastwam.memory_s1.sim_bridge" not in command or "diagnostic" not in command or cwd != Path(args.root).resolve():
        raise ValueError(f"PID file does not identify the legacy diagnostic launcher: pid={pid}, cwd={cwd}, command={command}")
    owners = children_of(pid)
    inventory = [{**item, "command": command_line(item["pid"])} for item in owners]
    print(json.dumps(inventory, indent=2))
    if not args.apply:
        print("Inspection only. Repeat with --apply to preserve records and stop this exact process tree.")
        return
    legacy_snapshot(args, "before_stop")
    durable_json(Path(args.snapshot) / "owned_processes.json", inventory)
    # nohup may have inherited SIGINT=ignored; only send it to an eligible policy process.
    for item in owners:
        if "fastwam.memory_s1.sim_bridge" not in command_line(item["pid"]):
            continue
        try:
            ignored = int(re.search(r"^SigIgn:\s*([0-9a-f]+)", Path(f"/proc/{item['pid']}/status").read_text(), re.M)[1], 16)
            if not ignored & (1 << (signal.SIGINT - 1)) and is_alive(item):
                os.kill(item["pid"], signal.SIGINT)
        except FileNotFoundError:
            pass
    deadline = time.monotonic() + args.grace_seconds
    while time.monotonic() < deadline and any(is_alive(item) for item in owners):
        time.sleep(0.5)
    for item in reversed(owners):
        if is_alive(item):
            os.kill(item["pid"], signal.SIGTERM)
    deadline = time.monotonic() + args.grace_seconds
    while time.monotonic() < deadline and any(is_alive(item) for item in owners):
        time.sleep(0.5)
    remaining = [item for item in owners if is_alive(item)]
    legacy_snapshot(args, "after_stop")
    if remaining:
        raise RuntimeError(f"Verified processes still alive after SIGTERM; inspect before escalating: {remaining}")
    print("Legacy diagnostic tree stopped. Container, environments, resources and unrelated processes were preserved.")


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    stop = sub.add_parser("stop")
    stop.add_argument("--output", required=True)
    stop.add_argument("--mode", choices=("now", "drain"), default="now")
    status = sub.add_parser("status")
    status.add_argument("--output", required=True)
    old = sub.add_parser("stop-legacy")
    old.add_argument("--root", required=True)
    old.add_argument("--diagnostic-root", required=True)
    old.add_argument("--launcher-pid-file", required=True)
    old.add_argument("--snapshot", required=True)
    old.add_argument("--grace-seconds", type=int, default=15)
    old.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if args.command == "stop":
        output = Path(args.output).resolve()
        if not output.is_dir():
            raise ValueError("Evaluation output directory does not exist.")
        durable_json(output / "STOP.json", {"mode": args.mode, "time": time.time()})
        print(f"Stop requested: {args.mode}. Wait for launcher exit before packaging mutable logs.")
    elif args.command == "status":
        output = Path(args.output)
        for name in ("status.json", "launcher.json", "UPLOAD_FAILED.json", "ABORT.json"):
            path = output / name
            if path.exists():
                value = read(path)
                if name == "launcher.json":
                    value["alive"] = is_alive(value["owner"])
                print(name, json.dumps(value, indent=2))
    else:
        stop_legacy(args)


if __name__ == "__main__":
    main()
