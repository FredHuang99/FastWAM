"""Script-owned logs, container-visible GPU selection and detached launches.

Every memory_v2 entry point writes its own log file (created with its folder) and,
with --background, starts itself detached on GPUs chosen *inside this container*,
so no shell redirection, nohup or pre-created directories are needed.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

CHILD_ENV = "FW_MEMORY_V2_CHILD"


class Tee:
    """Mirror a stream into a log file."""

    def __init__(self, stream, handle):
        self.stream, self.handle = stream, handle

    def write(self, text):
        self.handle.write(text)
        self.handle.flush()
        if self.stream is not None:
            try:
                self.stream.write(text)
                self.stream.flush()
            except (OSError, ValueError):
                self.stream = None
        return len(text)

    def flush(self):
        self.handle.flush()

    def isatty(self):
        return False


def header() -> str:
    return (f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} pid={os.getpid()} "
            f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')} argv={sys.argv[1:]}\n")


def open_log(path: Path) -> Path:
    """Foreground: tee stdout/stderr (tracebacks included) into `path`. Child of --background: no-op,
    its stdout/stderr already are that file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.environ.get(CHILD_ENV) == str(path):
        print(header(), end="", flush=True)
        return path
    handle = path.open("a", encoding="utf-8", buffering=1)
    handle.write(header())
    sys.stdout = Tee(sys.stdout, handle)
    sys.stderr = Tee(sys.stderr, handle)
    return path


def visible_gpus() -> List[Dict]:
    """GPUs visible in THIS container, PCI order. Host nvidia-smi ids do not apply inside it."""
    try:
        text = subprocess.run(["nvidia-smi", "--query-gpu=index,uuid,name,memory.used,memory.total",
                               "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"nvidia-smi failed inside this environment: {error}") from None
    gpus = []
    for line in text.strip().splitlines():
        index, uuid, name, used, total = (x.strip() for x in line.split(","))
        gpus.append({"index": index, "uuid": uuid, "name": name, "used_mib": int(used), "total_mib": int(total)})
    return gpus


def gpu_table(gpus: Sequence[Dict]) -> str:
    return "\n".join(f"  index={g['index']} {g['name']} used={g['used_mib']}/{g['total_mib']} MiB {g['uuid']}" for g in gpus)


def choose_gpus(spec: str, count: int = 0, free_mib: int = 2000) -> Tuple[List[Dict], str]:
    """spec: 'auto' | 'auto:N' | comma-separated container indices / UUIDs. Busy or invisible GPUs are refused."""
    gpus = visible_gpus()
    table = gpu_table(gpus)
    compute = [g for g in gpus if any(k in g["name"] for k in ("A100", "H100", "H200", "A800", "H800", "L40"))]
    if spec.startswith("auto"):
        free = [g for g in compute if g["used_mib"] <= free_mib]
        want = int(spec.split(":")[1]) if ":" in spec else (count or 1)
        if want < 1 or len(free) < want:
            raise SystemExit(f"Need {want} free GPU(s) (<= {free_mib} MiB used); visible in this container:\n{table}")
        return free[:want], table
    chosen = []
    for item in (x.strip() for x in spec.split(",") if x.strip()):
        match = [g for g in gpus if item in (g["index"], g["uuid"])]
        if not match:
            raise SystemExit(f"GPU {item!r} is not visible in this container (host nvidia-smi ids do not apply). "
                             f"Visible:\n{table}\nUse these indices/UUIDs, or 'auto'.")
        if match[0]["used_mib"] > free_mib:
            raise SystemExit(f"GPU {item} already uses {match[0]['used_mib']} MiB; pick a free one or raise --free-mib.\n{table}")
        chosen.append(match[0])
    return chosen, table


def spawn(cmd: Sequence[str], gpus: Sequence[Dict], log: Path, check_seconds: int = 30) -> Dict:
    """Start `cmd` detached on `gpus`; stdout/stderr (incl. import errors and tracebacks) go to `log`."""
    log = Path(log)
    log.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=",".join(g["uuid"] for g in gpus), CUDA_DEVICE_ORDER="PCI_BUS_ID")
    env[CHILD_ENV] = str(log)
    with log.open("a", encoding="utf-8") as handle:
        proc = subprocess.Popen(list(cmd), env=env, stdin=subprocess.DEVNULL, stdout=handle, stderr=subprocess.STDOUT,
                                start_new_session=True, cwd=os.getcwd())
    record = {"pid": proc.pid, "gpus": [g["uuid"] for g in gpus], "gpu_indices": [g["index"] for g in gpus],
              "log": str(log), "cmd": list(cmd), "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    (log.parent / (log.stem + ".launch.json")).write_text(json.dumps(record, indent=2))
    time.sleep(check_seconds)
    code = proc.poll()
    record["state"] = "running" if code is None else f"exited code={code}"
    print(f"[launch] pid={proc.pid} gpus={record['gpu_indices']} {record['state']}")
    print(f"[launch] log: {log}")
    if code not in (None, 0):
        lines = log.read_text(errors="replace").splitlines()
        print("[launch] last log lines:\n" + "\n".join(lines[-25:]))
    else:
        print(f"[launch] follow: tail -f {log}")
    return record
