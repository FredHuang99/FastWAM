"""Capacity accounting and readiness identities; importable by the isolated HF tools."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import time


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            result.update(block)
    return result.hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def current_identity(cfg):
    root, run = Path(cfg["root"]), Path(cfg["paths"]["run"])
    config = {key: value for key, value in cfg.items() if key != "training_python"}
    portable = root / "scripts/memory_s1/portable"
    code = [p for directory in (root / "src", root / "scripts/memory_s1")
            for p in directory.rglob("*") if p.is_file() and p.suffix in (".py", ".sh", ".json")]
    return {"schema": "s1-phase-readiness-v1", "config_sha256": canonical(config),
            "code_sha256": canonical({p.relative_to(root).as_posix(): digest(p) for p in sorted(code)}),
            "admission_sha256": digest(run / "integration_admission.json"),
            "prepared_sha256": digest(Path(cfg["paths"]["prepared"]) / "manifest.json"),
            "alignment_sha256": digest(Path(cfg["paths"]["prepared"]) / "alignment_approved.json"),
            "cache_manifest_sha256": digest(Path(cfg["paths"]["cache"]) / "manifest.json"),
            "portable_sha256": canonical({p.relative_to(root).as_posix(): digest(p)
                for p in sorted(portable.rglob("*")) if p.is_file() and p.suffix in (".py", ".sh", ".json")})}


def _bytes(path):
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()
               and not {".cache", "__pycache__"}.intersection(p.parts)) if path.exists() else 0


def lease_elapsed(cfg):
    path = Path(cfg["root"]) / cfg.get("time_budget", {}).get("lease_file", "outputs/lease.json")
    if not path.is_file():
        return None
    value = json.loads(path.read_text()).get("started_unix")
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not 0 < value <= time.time():
        return None
    return time.time() - value


def ready_upper_bound(cfg):
    root, run = Path(cfg["root"]), Path(cfg["paths"]["run"])
    recovery = Path(os.environ.get("RECOVERY_ROOT", root / cfg.get("recovery", {}).get("output", "outputs/recovery_aws_h100")))
    selected = [root / name for name in ("src", "scripts/memory_s1", "configs", "requirements")]
    selected += [Path(cfg["paths"]["prepared"]), run / "integration_evidence", run / "parent_provenance",
                 recovery / "environment", root / ".git"]
    approval_path = Path(cfg["paths"]["prepared"]) / "alignment_approved.json"
    if approval_path.exists():
        approval = json.loads(approval_path.read_text())
        selected += [Path(item["path"]).parent for item in approval.get("recovery_evidence", {}).values()]
    old = root / cfg.get("recovery", {}).get("ready_directory", "outputs/recovery_aws_h100/restored")
    archives = ("FastWAM.source.tar.gz", "RMBench.source.tar.gz", "PyTorch3D.source.tar.gz", "reference.source.tar.gz")
    size = sum(_bytes(p) for p in selected) + sum(p.stat().st_size for p in old.rglob("*") if p.is_file() and p.name in archives)
    # Source bundle, JSON envelopes and an incompressible tar/zstd upper allowance.
    return int(size * 1.10) + 256 * 2**20


def disk_budget(cfg, full_checkpoint, parameter_bytes, auxiliary_bytes, ready_bytes=None):
    root, run = Path(cfg["root"]), Path(cfg["paths"]["run"])
    recovery = Path(os.environ.get("RECOVERY_ROOT", root / cfg.get("recovery", {}).get("output", "outputs/recovery_aws_h100")))
    hub = Path(os.environ.get("HF_HUB_CACHE", Path(os.environ.get("HF_HOME", Path.home() / ".cache/huggingface")) / "hub"))
    ready = ready_upper_bound(cfg) if ready_bytes is None else int(ready_bytes)
    allocations = [("run", run, 3 * full_checkpoint + 6 * parameter_bytes + auxiliary_bytes),
                   ("ready_staging_and_archive", recovery, 2 * ready),
                   ("hub_readback", hub, ready + full_checkpoint),
                   ("temporary", Path(tempfile.gettempdir()), full_checkpoint)]
    reserve = int(cfg.get("startup", {}).get("local_reserve_gib", 20) * 2**30)
    devices = {}
    for name, path, required in allocations:
        existing = path.resolve()
        while not existing.exists():
            existing = existing.parent
        device = str(existing.stat().st_dev)
        row = devices.setdefault(device, {"probe_path": str(existing), "free_bytes": shutil.disk_usage(existing).free,
                                          "additional_bytes": 0, "reserve_bytes": reserve, "allocations": []})
        row["additional_bytes"] += required
        row["allocations"].append({"purpose": name, "path": str(path), "bytes": required})
    for row in devices.values():
        row["passed"] = row["free_bytes"] >= row["additional_bytes"] + row["reserve_bytes"]
    return {"passed": all(row["passed"] for row in devices.values()), "filesystems": devices,
            "ready_estimate_bytes": ready, "checked_unix": time.time()}


def verify_materials(cfg, require_ready=False, micro=None):
    from .common import read_json, fingerprint
    from .history import recipe
    from .schedule import validation_policy
    from .integration_contract import binding, verify_admission
    run = Path(cfg["paths"]["run"])
    expected = binding(cfg)
    admission = verify_admission(cfg, expected["cache_signature"])
    plan = read_json(run / "storage_plan.json")
    identity = current_identity(cfg)
    if plan.get("startup_identity") != identity or plan.get("recipe_sha") != fingerprint(recipe(cfg)):
        raise ValueError("Capacity report is stale. Re-run storage_plan.py for this exact configuration.")
    if plan.get("validation") != validation_policy(cfg) or plan.get("checkpoint_every") != cfg["checkpoint_every"]:
        raise ValueError("Capacity schedule differs from the training schedule.")
    local = disk_budget(cfg, plan["full_checkpoint_estimate_bytes"], plan["parameter_bytes_fp32"],
                        plan["auxiliary_history_bytes"], plan["local_disk_check"]["ready_estimate_bytes"])
    if not local["passed"]:
        raise ValueError(f"Local free-space guard failed: {local}")
    if not plan.get("training_quota_check"):
        raise ValueError("HF account capacity has not been checked.")
    if micro is not None:
        report = read_json(run / "integration_evidence/training.json")
        functional = report.get("phase_preflight", {})
        if micro not in functional.get("allowed_micro_batches", [functional.get("micro_batch")]) or functional.get("optimizer_updates") != 0:
            raise ValueError("Run the phase training preflight for the selected micro-batch before launch.")
    if require_ready:
        receipt = read_json(run / "LATEST_READY_REMOTE.json")
        if receipt.get("startup_identity") != identity or receipt.get("readback_verified") is not True:
            raise ValueError("First launch requires a matching, readback-verified ready package.")
        if receipt.get("phase") != "admitted_not_started" or receipt.get("run_id") != run.name:
            raise ValueError("Ready receipt belongs to another run or phase.")
        for key in ("revision", "pointer_revision", "package", "sha256"):
            if not receipt.get(key):
                raise ValueError(f"Incomplete ready receipt: {key}")
    return {"passed": True, "startup_identity": identity, "local_disk_check": local,
            "admission_sha256": digest(run / "integration_admission.json")}
