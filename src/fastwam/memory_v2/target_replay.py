"""Plan v12 AL1 (Opus checklist 2): replay another run's executed targets in the closed loop, no model.

`online.py run --checkpoint replay:<pack.json.gz>` uses ReplayPolicy instead of a model: at every decision of scene
(task, seed) the session answers with the reference episode's executed targets from that frame on (32 of them; past
the reference's end the last target is held), so the simulator executes exactly the reference's target sequence. The
simulator, the adapter, the logs and every check of run_episode are the ordinary closed loop's (the command-to-
execution check still holds: what the policy returns is what is executed). Packs come from
scripts/fullft/replay_pack.py (targets + per-step joints / object positions of each reference episode).
"""
from __future__ import annotations

import copy
import gzip
import json
import time
from pathlib import Path
from typing import Dict

PREFIX = "replay:"


def is_replay(checkpoint: str) -> bool:
    return isinstance(checkpoint, str) and checkpoint.startswith(PREFIX)


def load_pack(path: str) -> dict:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


class ReplayPolicy:
    """Duck-typed stand-in for online.Policy / fullft FullPolicy (what cmd_run and run_episode use)."""

    def __init__(self, checkpoint: str):
        from . import dense
        from .online import dense_config_light
        self.checkpoint = checkpoint
        self.pack_path = checkpoint[len(PREFIX):]
        self.pack = load_pack(self.pack_path)
        self.spec = dense.DenseSpec()
        self.dense_cfg = copy.deepcopy(dense_config_light(self.spec))
        self.t5_on_gpu = False

    def base_label(self, label: str) -> str:
        return f"{label}_off"

    def describe(self) -> dict:
        return {"checkpoint": self.checkpoint, "kind": "target_replay", "pack": self.pack_path,
                "reference": self.pack.get("meta", {})}


class ReplaySession:
    def __init__(self, policy: ReplayPolicy, directory: Path, mode: str, steps: int, guidance_scale: float,
                 dependence: bool, tag: str = "", limit: int = 0, candidates: int = 1, coherence: str = "none",
                 noise: str = "per_decision", replay_cache: bool = True):
        self.p, self.directory, self.mode, self.tag = policy, Path(directory), mode, tag
        self.reset()

    def reset(self):
        self.targets = None
        self.decisions = 0

    def decide(self, request: dict):
        import numpy as np
        from .online import append
        key = f"{request['task']}/{int(request['episode_seed'])}"
        if self.targets is None:
            episode = self.p.pack["episodes"].get(key)
            if episode is None:
                raise ValueError(f"replay pack has no episode {key}")
            self.targets = np.asarray(episode["targets"], dtype=np.float32)
        current = int(request["current_id"])
        start = time.monotonic()
        idx = np.minimum(np.arange(current, current + 32), len(self.targets) - 1)
        actions = self.targets[idx]
        append(self.directory / "decisions.jsonl", {
            "frame_id": current, "mode": self.mode, "replay": key, "beyond_reference": int(current + 32 > len(self.targets)),
            "seconds": time.monotonic() - start, "actions_after_gripper_clip": actions.tolist()})
        self.decisions += 1
        return actions


ReplayPolicy.session_cls = ReplaySession
