"""Durable episode queue; this module deliberately has no CUDA dependencies."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import socket
import time


class EvaluationInterrupted(Exception):
    pass


def check_stop(root):
    if root and stop_mode(root) == "now":
        raise EvaluationInterrupted("Stop requested before the next simulator operation.")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def cuda_gpu_uuid(logical_device=0):
    import ctypes
    import pynvml
    driver = ctypes.CDLL("libcuda.so.1")
    device = ctypes.c_int()
    buffer = ctypes.create_string_buffer(32)
    if driver.cuInit(0) != 0 or driver.cuDeviceGet(ctypes.byref(device), int(logical_device)) != 0:
        raise RuntimeError("CUDA driver device identification failed.")
    if driver.cuDeviceGetPCIBusId(buffer, len(buffer), device) != 0:
        raise RuntimeError("CUDA driver PCI identification failed.")
    pynvml.nvmlInit()
    try:
        uuid = pynvml.nvmlDeviceGetUUID(pynvml.nvmlDeviceGetHandleByPciBusId(buffer.value))
        return uuid.decode() if isinstance(uuid, bytes) else uuid
    finally:
        pynvml.nvmlShutdown()


def durable_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def process_identity(pid=None):
    pid = os.getpid() if pid is None else int(pid)
    try:
        # The comm field can contain spaces and parentheses.
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return {"pid": pid, "start_ticks": fields[19], "state": fields[0],
                "host": socket.gethostname(), "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}
    except FileNotFoundError:
        return None


def is_alive(owner):
    here = process_identity()
    if not owner or owner.get("host") != here["host"] or owner.get("boot") != here["boot"]:
        return False
    current = process_identity(owner["pid"])
    return current is not None and current["state"] != "Z" and current["start_ticks"] == owner["start_ticks"]


@contextmanager
def locked(path, blocking=True):
    import fcntl
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def stop_mode(root):
    path = Path(root) / "STOP.json"
    return read(path)["mode"] if path.exists() else None


class EpisodeQueue:
    def __init__(self, root):
        self.root = Path(root)
        self.path = self.root / "queue.json"

    def initialize(self, identity, scenes, conditions, resume=False):
        self.root.mkdir(parents=True, exist_ok=True)
        with locked(self.root / "queue.lock"):
            if self.path.exists():
                value = read(self.path)
                if value["identity"] != identity:
                    raise ValueError("Evaluation identity changed. Use a new output directory.")
                if not resume:
                    raise ValueError("Existing evaluation requires --resume.")
                for job in value["jobs"]:
                    if job["state"] == "complete":
                        self.result(job, identity)
                    elif job.get("directory") and (self.root / job["directory"] / "complete.json").exists():
                        self.result(job, identity)
                        job["state"] = "complete"
                    elif is_alive(job.get("owner")):
                        raise RuntimeError(f"Job is still owned by a live process: {job['id']}")
                    else:
                        job["state"] = "pending"
                        job.pop("owner", None)
                (self.root / "STOP.json").unlink(missing_ok=True)
                (self.root / "ABORT.json").unlink(missing_ok=True)
            else:
                jobs = []
                for condition in conditions:
                    for scene in scenes:
                        identifier = f"{condition}/{scene['task']}/ep_{scene['ordinal']:03d}_{scene['seed']}"
                        jobs.append({"id": identifier, "scene": scene, "condition": condition,
                                     "state": "pending", "attempt": 0,
                                     "estimate_seconds": 740 if scene["task"] == "swap_blocks" else 370})
                value = {"schema": 1, "identity": identity, "jobs": jobs, "created": time.time()}
            durable_json(self.path, value)

    def claim(self, worker):
        with locked(self.root / "queue.lock"):
            if stop_mode(self.root) or (self.root / "ABORT.json").exists():
                return None
            value = read(self.path)
            candidates = [job for job in value["jobs"] if job["state"] == "pending"]
            if not candidates:
                return None
            # Long scenes start early; queue identity does not depend on this order.
            job = max(candidates, key=lambda item: item["estimate_seconds"])
            job.update(state="running", owner=process_identity(), worker=worker, started=time.time(), attempt=job["attempt"] + 1)
            directory = self.root / job["id"] / f"attempt_{job['attempt']:03d}"
            directory.mkdir(parents=True, exist_ok=False)
            job["directory"] = str(directory.relative_to(self.root))
            durable_json(directory / "job.json", {**job, "identity": value["identity"]})
            durable_json(self.path, value)
            return dict(job)

    def finish(self, job, state, error=None):
        with locked(self.root / "queue.lock"):
            value = read(self.path)
            saved = next(item for item in value["jobs"] if item["id"] == job["id"])
            if saved["attempt"] != job["attempt"] or saved.get("owner") != job.get("owner"):
                raise RuntimeError("Episode lease changed while its worker was running.")
            if state == "complete":
                result = self.result(saved, value["identity"])
                matching = [self.result(item, value["identity"])["wall_seconds"] for item in value["jobs"]
                            if item["state"] == "complete" and item["scene"]["task"] == saved["scene"]["task"]]
                mean_seconds = (sum(matching) + result["wall_seconds"]) / (len(matching) + 1)
                for item in value["jobs"]:
                    if item["state"] == "pending" and item["scene"]["task"] == saved["scene"]["task"]:
                        item["estimate_seconds"] = mean_seconds
            saved.update(state=state, finished=time.time(), error=error)
            durable_json(self.path, value)
            if state == "error":
                durable_json(self.root / "ABORT.json", {"job": job["id"], "error": error})

    def result(self, job, identity):
        directory = self.root / job["directory"]
        marker = read(directory / "complete.json")
        if marker["identity"] != identity or marker["job_id"] != job["id"]:
            raise ValueError("Completed episode identity mismatch.")
        for filename, expected in marker["files"].items():
            if digest(directory / filename) != expected:
                raise ValueError(f"Completed episode checksum mismatch: {directory / filename}")
        value = read(directory / "result.json")
        if value.get("status") != "complete" or not isinstance(value.get("success"), bool):
            raise ValueError("Infrastructure failure cannot be counted as an episode failure.")
        return value

    def publish(self, job, result):
        directory = self.root / job["directory"]
        value = read(self.path)
        durable_json(directory / "result.json", result)
        files = {}
        for name in ("result.json", "decisions.jsonl", "simulator.log", "job.json"):
            path = directory / name
            if path.exists():
                with path.open("rb") as stream:
                    os.fsync(stream.fileno())
                files[name] = digest(path)
        durable_json(directory / "complete.json", {"identity": value["identity"], "job_id": job["id"], "files": files})
        self.finish(job, "complete")

    def snapshot(self):
        return read(self.path)


def summarize(root, mode, require_complete=False):
    queue = EpisodeQueue(root)
    state = queue.snapshot()
    jobs = state["jobs"]
    rows = [queue.result(job, state["identity"]) for job in jobs if job["state"] == "complete"]
    complete = len(rows) == len(jobs)
    if require_complete and not complete:
        raise RuntimeError("Closed-loop evaluation is incomplete; it cannot select a checkpoint.")
    import math
    def rate(selected):
        count = len(selected)
        if not count:
            return {"episodes": 0, "success_rate": None, "wilson_95": None}
        p = sum(row["success"] for row in selected) / count
        denom = 1 + 1.96**2 / count
        center = (p + 1.96**2 / (2 * count)) / denom
        half = 1.96 * math.sqrt(p * (1-p) / count + 1.96**2 / (4 * count**2)) / denom
        return {"episodes": count, "success_rate": p, "wilson_95": [center-half, center+half]}
    conditions = list(dict.fromkeys(job["condition"] for job in jobs))
    tasks = list(dict.fromkeys(job["scene"]["task"] for job in jobs))
    summary = {"mode": mode, "complete": complete, "identity": state["identity"], "episodes": rows,
               "planned_episodes": len(jobs), "completed_episodes": len(rows),
               "success_rate": rate([r for r in rows if r["condition"] == conditions[0]])["success_rate"],
               "conditions": {c: rate([r for r in rows if r["condition"] == c]) for c in conditions},
               "by_task": {t: {c: rate([r for r in rows if r["task"] == t and r["condition"] == c]) for c in conditions} for t in tasks},
               "protocol": "Fixed official expert-feasible candidate order, frozen instructions, episode-boundary resume."}
    durable_json(Path(root) / "summary.json", summary)
    return summary
