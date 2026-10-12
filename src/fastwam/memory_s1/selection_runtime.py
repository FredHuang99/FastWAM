"""Selection telemetry, planner scheduling, and checked source migration."""
from __future__ import annotations

import csv
import functools
import json
import os
from pathlib import Path
import signal
import time

try:
    from .eval_state import durable_json, digest, is_alive, locked, process_identity, read
except ImportError:
    from eval_state import durable_json, digest, is_alive, locked, process_identity, read


def duration(seconds):
    if seconds is None:
        return "unknown (waiting for completed samples)"
    days, seconds = divmod(max(0, int(seconds)), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return (f"{days}d " if days else "") + f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def event(root, phase, state="running", **fields):
    if not root:
        return
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    row = {"time": time.time(), "owner": process_identity(), "phase": phase, "state": state, **fields}
    durable_json(root / f"progress_{os.getpid()}.json", row)
    with locked(root / "events.lock"):
        with (root / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        if "seconds" in fields:
            path = root / "timings.csv"
            exists = path.exists()
            with path.open("a", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                if not exists:
                    writer.writerow(["time", "pid", "phase", "state", "seconds", "task", "seed", "batch"])
                writer.writerow([row["time"], os.getpid(), phase, state, fields["seconds"],
                                 fields.get("task"), fields.get("seed"), fields.get("batch")])
    details = " ".join(f"{k}={v}" for k, v in fields.items() if k != "error")
    print(f"[{phase}] {state} {details}", flush=True)


def live_details(root):
    rows = []
    for path in Path(root).rglob("progress_*.json"):
        if "packages" in path.parts:
            continue
        value = read(path)
        if value.get("state") in ("running", "waiting") and is_alive(value.get("owner")):
            rows.append({**value, "phase_age_seconds": time.time() - value["time"]})
    return sorted(rows, key=lambda row: row["time"])


def install_warmup_observer(MotionGen):
    """Serialize complete single/batch warmups without changing planner settings."""
    if getattr(MotionGen.warmup, "_selection_observed", False):
        return
    original = MotionGen.warmup

    @functools.wraps(original)
    def observed(self, *args, **kwargs):
        root = os.environ.get("MEMORY_S1_PROGRESS_ROOT")
        lock_path = os.environ.get("MEMORY_S1_WARMUP_LOCK")
        if not root or not lock_path:
            return original(self, *args, **kwargs)
        batch = kwargs.get("batch", args[0] if args else 1)
        event(root, "planner_warmup", "waiting", batch=batch)
        started = time.monotonic()
        with locked(lock_path):
            event(root, "planner_warmup", batch=batch, wait_seconds=time.monotonic()-started)
            import torch
            torch.cuda.synchronize()
            started = time.monotonic()
            try:
                result = original(self, *args, **kwargs)
                torch.cuda.synchronize()
            except BaseException as error:
                event(root, "planner_warmup", "error", batch=batch, seconds=time.monotonic()-started, error=repr(error))
                raise
            event(root, "planner_warmup", "complete", batch=batch, seconds=time.monotonic()-started)
            return result
    observed._selection_observed = True
    MotionGen.warmup = observed


def stop_request(root, mode="drain", grace=120):
    root = Path(root)
    if grace < 0:
        raise ValueError("grace-seconds must be nonnegative")
    value = {"mode": mode, "time": time.time(), "deadline": time.time()+grace,
             "reason": "user requested selection stop"}
    durable_json(root / "STOP.json", value)
    (root / "STOP_REQUESTED").touch()
    if (root / "active.json").exists():
        durable_json(Path(read(root / "active.json")["directory"]) / "STOP.json", value)
    return value


def terminate_recorded(owner, timeout=10):
    if not is_alive(owner):
        return
    pid = int(owner["pid"])
    if os.getpgid(pid) != pid:
        raise RuntimeError(f"Refusing to signal a foreign process group: {pid}")
    os.killpg(pid, signal.SIGTERM)
    deadline = time.monotonic()+timeout
    while is_alive(owner) and time.monotonic() < deadline:
        time.sleep(.2)
    if is_alive(owner):
        os.killpg(pid, signal.SIGKILL)


def source_migration(cfg, training_code):
    """Reconstruct training hashes using only the explicit evaluation edit list."""
    from .common import code_version, fingerprint
    root = Path(cfg["root"])
    current = code_version(root)
    keys = ("core_sha", "implementation_sha", "support_sha")
    if all(current[k] == training_code[k] for k in keys):
        return {"mode": "exact", "code": current}
    manifest_path = root / "scripts/memory_s1/portable/selection_migration.json"
    manifest = read(manifest_path)
    if current["core_sha"] != training_code["core_sha"]:
        raise ValueError("Frozen model core differs from training; evaluation migration cannot approve it.")
    for name, row in manifest["files"].items():
        if digest(root / name) != row["after"]:
            raise ValueError(f"Unreviewed evaluation edit: {name}")
    for variant in ("before_lf", "before"):
        implementation = {p.name: digest(p) for p in sorted((root / "src/fastwam/memory_s1").glob("*.py"))}
        support = {p.relative_to(root).as_posix(): digest(p) for p in sorted((root / "scripts/memory_s1").glob("*"))
                   if p.is_file() and p.suffix in (".py", ".sh")}
        for name, row in manifest["files"].items():
            table = implementation if name.startswith("src/fastwam/memory_s1/") else support
            key = Path(name).name if table is implementation else name
            if row.get(variant) is None:
                table.pop(key, None)
            else:
                table[key] = row[variant]
        if (fingerprint(implementation) == training_code["implementation_sha"] and
                fingerprint(support) == training_code["support_sha"]):
            return {"mode": "evaluation_only", "manifest_sha256": digest(manifest_path),
                    "training_code": training_code, "code": current, "files": manifest["files"]}
    raise ValueError("Changes outside the reviewed evaluation files differ from training; preserve server patches and inspect them.")


def import_offline(source, destination, identity, migration):
    """Copy verified metrics with lineage; never rewrite source evidence."""
    from .common import fingerprint
    import shutil
    import yaml
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination:
        raise ValueError("Offline import requires a separate destination")
    prior = read(source / "identity.json")
    for name in ("training", "weights", "runtime", "candidate_steps"):
        if prior[name] != identity[name]:
            raise ValueError(f"Offline evidence differs: {name}")
    old_cfg = yaml.safe_load((source / "evaluation_config.yaml").read_text())
    new_cfg = yaml.safe_load((destination / "evaluation_config.yaml").read_text())
    new_cfg.pop("selection_runtime", None)
    if fingerprint(old_cfg) != prior["config_sha"] or new_cfg != old_cfg:
        raise ValueError("Offline inference/data configuration changed")
    evidence = {}
    for step in identity["candidate_steps"]:
        for period in (1, 4, 8, 16):
            relative = f"offline/step_{step:06d}/T{period}.json"
            path = source / relative
            row = read(path)
            if row["identity"] != prior or row["step"] != step or row["period"] != period:
                raise ValueError(f"Invalid offline evidence: {path}")
            inherited = {**row, "identity": identity, "inherited_from": {"path": str(path), "sha256": digest(path), "identity": prior}}
            target = destination / relative
            if target.exists() and read(target) != inherited:
                raise ValueError(f"Conflicting imported result: {target}")
            durable_json(target, inherited)
            evidence[relative] = digest(path)
    for name in ("offline.csv", "offline.png", "offline.pdf"):
        if (source / name).is_file():
            shutil.copy2(source / name, destination / name)
            evidence[name] = digest(source / name)
    durable_json(destination / "OFFLINE_IMPORT.json", {"source": str(source), "files": evidence, "migration": migration})
