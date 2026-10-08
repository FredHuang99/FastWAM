"""Completed-update checkpoints and synchronous, isolated-environment HF calls."""
from __future__ import annotations

import os
from pathlib import Path
import random
import subprocess
import sys

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


def save_checkpoint(model, optimizer, scheduler, run, step, cfg, identity, rng_states, progress, best):
    directory = Path(run) / "checkpoints" / f"step_{step:06d}"
    value = {"schema": SCHEMA, "memory": to_cpu(model.memory.state_dict()),
             "optimizer": to_cpu(optimizer.state_dict()), "scheduler": scheduler.state_dict(),
             "completed_updates": step, "sampler_next_update": step, "rng_states": rng_states,
             "config": cfg, "identity": identity, "progress": progress, "best": best}
    (directory / "continuation.json").unlink(missing_ok=True)
    atomic_torch(directory / "resume.pt", value)
    atomic_json(directory / "complete.json", {"schema": SCHEMA, "completed_updates": step,
                                              "sha256": sha256(directory / "resume.pt"), "identity": identity, "phase": progress.get("phase", "train")})
    atomic_json(Path(run) / "LATEST_LOCAL.json", {"directory": str(directory.relative_to(run)), "step": step})
    return directory


def verified_load(path, weights_only=False):
    path = Path(path)
    if path.is_dir():
        path = path / "resume.pt"
    marker = read_json(path.parent / "complete.json")
    if marker["sha256"] != sha256(path):
        raise ValueError(f"Incomplete or corrupt resume file: {path}.")
    value = torch.load(path, map_location="cpu", weights_only=weights_only)
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
    atomic_json(directory / "continuation.json", {"step": step, "identity": identity, "progress": progress, "best": best})
    marker = read_json(directory / "complete.json")
    marker["continuation_sha256"] = sha256(directory / "continuation.json")
    marker["phase"] = progress.get("phase", "train")
    atomic_json(directory / "complete.json", marker)


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
