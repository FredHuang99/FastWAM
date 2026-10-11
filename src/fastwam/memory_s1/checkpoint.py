"""Completed-update checkpoints and synchronous, isolated-environment HF calls."""
from __future__ import annotations

import os
from pathlib import Path
import random
import subprocess
import sys
import time
import shutil

import numpy as np
import torch

from .common import SCHEMA, atomic_json, atomic_torch, read_json, sha256


def to_cpu(value):
    if isinstance(value, torch.Tensor):
        return value.detach().cpu()
    if isinstance(value, dict):
        return {key: to_cpu(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_cpu(item) for item in value]
    if isinstance(value, tuple):
        return tuple(to_cpu(item) for item in value)
    return value


def random_state():
    return {"python": random.getstate(), "numpy": np.random.get_state(), "torch": torch.get_rng_state(),
            "cuda": torch.cuda.get_rng_state()}


def restore_random_state(value):
    random.setstate(value["python"])
    np.random.set_state(value["numpy"])
    torch.set_rng_state(value["torch"])
    torch.cuda.set_rng_state(value["cuda"])


def _publish(directory, run, step):
    final = directory.with_name(directory.name.removeprefix(".").removesuffix(".tmp"))
    os.replace(directory, final)
    for folder in (final, final.parent):
        descriptor = os.open(folder, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    atomic_json(Path(run) / "LATEST_LOCAL.json", {"directory": str(final.relative_to(run)), "step": step})
    return final


def _generation(run, step):
    directory = Path(run) / "checkpoints" / f".step_{step:06d}_g{time.time_ns()}.tmp"
    directory.mkdir(parents=True, exist_ok=False)
    return directory


def save_checkpoint(model, optimizer, scheduler, run, step, cfg, identity, rng_states, progress, best):
    directory = _generation(run, step)
    value = {"schema": SCHEMA, "memory": to_cpu(model.memory.state_dict()),
             "optimizer": to_cpu(optimizer.state_dict()), "scheduler": scheduler.state_dict(),
             "completed_updates": step, "sampler_next_update": step, "rng_states": rng_states,
             "config": cfg, "identity": identity, "progress": dict(progress), "best": dict(best)}
    atomic_torch(directory / "resume.pt", value)
    atomic_json(directory / "complete.json", {"schema": SCHEMA, "completed_updates": step,
               "sha256": sha256(directory / "resume.pt"), "identity": identity, "phase": progress.get("phase", "train")})
    return _publish(directory, run, step)


def verified_load(path, weights_only=False):
    path = Path(path)
    if path.is_dir():
        path = path / "resume.pt"
    marker = read_json(path.parent / "complete.json")
    if marker["sha256"] != sha256(path):
        raise ValueError(f"Incomplete or corrupt resume file: {path}.")
    value = torch.load(path, map_location="cpu", weights_only=weights_only)
    if marker["completed_updates"] != value["completed_updates"] or marker["identity"] != value["identity"]:
        raise ValueError("Checkpoint completion marker does not match its payload identity/update.")
    continuation_path = path.parent / "continuation.json"
    if continuation_path.exists():
        if marker.get("continuation_sha256") != sha256(continuation_path):
            raise ValueError("Continuation checksum mismatch.")
        continuation = read_json(continuation_path)
        if continuation["step"] != value["completed_updates"] or continuation["identity"] != value["identity"]:
            raise ValueError("Continuation refers to a different completed update.")
        value.update(progress=continuation["progress"], best=continuation["best"])
    return value


def save_continuation(directory, step, identity, progress, best):
    directory = Path(directory)
    verified_load(directory)
    run = directory.parent.parent
    target = _generation(run, step)
    try:
        os.link(directory / "resume.pt", target / "resume.pt")
    except OSError:
        shutil.copy2(directory / "resume.pt", target / "resume.pt")
    atomic_json(target / "continuation.json", {"step": step, "identity": identity, "progress": progress, "best": best})
    marker = read_json(directory / "complete.json")
    marker["continuation_sha256"] = sha256(target / "continuation.json")
    marker["phase"] = progress.get("phase", "train")
    atomic_json(target / "complete.json", marker)
    return _publish(target, run, step)


def upload_checkpoint(cfg, directory):
    if not cfg["hf"]["enabled"]:
        raise ValueError("HF backup is required by this recipe; use a separate documented local-only configuration if needed.")
    script = Path(cfg["root"]) / "scripts/memory_s1/hf_tools.py"
    environment = dict(os.environ)
    environment.pop("HF_HUB_OFFLINE", None)
    environment.pop("TRANSFORMERS_OFFLINE", None)
    subprocess.run([cfg["hf"]["python"], str(script), "checkpoint", "--repo", cfg["hf"]["backup_repo"],
                    "--run", cfg["paths"]["run"], "--checkpoint", str(directory),
                    "--quota-gib", str(cfg["hf"]["quota_gib"]), "--reserve-gib", str(cfg["hf"]["reserve_gib"])], check=True, env=environment)


def prune_local(run):
    # Delete only checkpoint directories proven complete and strictly inside this run.
    import shutil
    root = (Path(run) / "checkpoints").resolve()
    checkpoints = sorted(path for path in root.glob("step_*") if (path / "complete.json").is_file())
    for path in checkpoints[:-2]:
        target = path.resolve()
        if target.parent != root or not target.name.startswith("step_"):
            raise ValueError("Checkpoint cleanup escaped its run directory.")
        shutil.rmtree(target)


def save_weights(model, path, step, identity):
    atomic_torch(path, {"schema": SCHEMA, "completed_updates": step,
                        "memory": to_cpu(model.memory.state_dict()), "identity": identity})
