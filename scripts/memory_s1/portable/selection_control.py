"""Stop a recorded posttrain process tree, including older deployed launchers."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import socket
import time


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def identity(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return {"pid": int(pid), "start_ticks": fields[19], "state": fields[0], "parent": int(fields[1]),
                "host": socket.gethostname(), "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}
    except (OSError, IndexError):
        return None


def alive(owner):
    current = identity(owner["pid"]) if owner else None
    return bool(current and current["state"] != "Z" and all(current[k] == owner[k] for k in ("host", "boot", "start_ticks")))


def tree(owner):
    if not alive(owner):
        return []
    processes = [identity(p.name) for p in Path("/proc").iterdir() if p.name.isdigit()]
    processes = [p for p in processes if p]
    selected = {owner["pid"]}
    while True:
        children = {p["pid"] for p in processes if p["parent"] in selected}
        if children <= selected:
            break
        selected |= children
    return [p for p in processes if p["pid"] in selected]


def wait(root, deadline):
    known, sent = {}, None
    last_print = 0
    while True:
        parent = read(root / "launcher.json").get("owner") if (root / "launcher.json").exists() else None
        active = read(root / "active.json") if (root / "active.json").exists() else {}
        child = active.get("owner")
        if active and (Path(active["directory"]) / "launcher.json").exists():
            child = child or read(Path(active["directory"]) / "launcher.json").get("owner")
        for owner in tree(child):
            known[(owner["pid"], owner["start_ticks"])] = owner
        # Qualification can run scene planning directly under the posttrain parent.
        if (root / "planning.json").exists():
            plan_root = Path(read(root / "planning.json")["directory"])
            for path in plan_root.glob("*.owner.json"):
                for owner in tree(read(path)):
                    known[(owner["pid"], owner["start_ticks"])] = owner
        survivors = [owner for owner in known.values() if alive(owner)]
        if time.time() > deadline+30 and survivors:
            sig = signal.SIGTERM if sent is None or time.time()-sent < 10 else signal.SIGKILL
            for owner in reversed(survivors):
                if alive(owner):
                    try:
                        os.kill(owner["pid"], sig)
                    except ProcessLookupError:
                        pass
            sent = sent or time.time()
        if not alive(parent) and not alive(child) and not survivors:
            write(root / f"STOP_REPORT_{time.time_ns()}.json", {"complete": True, "observed_owners": list(known.values()), "time": time.time()})
            print("Stopped: recorded evaluation tree exited; completed files preserved.", flush=True)
            return
        if time.time()-last_print >= 15:
            print(f"[stopping] launcher_alive={alive(parent)} evaluation_processes={len(survivors)}; waiting for local publication/backup", flush=True)
            last_print = time.time()
        if time.time() > deadline+1350:
            raise TimeoutError("Launcher/backup is still active; inspect logs. No unrecorded processes were signaled.")
        time.sleep(.5)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mode", choices=("drain", "now"), default="now")
    parser.add_argument("--grace-seconds", type=int, default=120)
    parser.add_argument("--wait-only", action="store_true")
    parser.add_argument("--deadline", type=float)
    args = parser.parse_args()
    if args.grace_seconds < 0:
        parser.error("grace-seconds must be nonnegative")
    root = Path(args.output).resolve()
    deadline = args.deadline if args.deadline is not None else time.time()+args.grace_seconds
    if not args.wait_only:
        request = {"mode": args.mode, "deadline": deadline, "time": time.time()}
        write(root / "STOP.json", request)
        (root / "STOP_REQUESTED").touch()
        if (root / "active.json").exists():
            write(Path(read(root / "active.json")["directory"]) / "STOP.json", request)
    wait(root, deadline)


if __name__ == "__main__":
    main()
