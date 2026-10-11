"""Separate parameter updates, durable weight exports, and evaluation scheduling."""
from __future__ import annotations


def validation_policy(cfg):
    mode = cfg.get("validation", {}).get("schedule", "inline")
    if mode not in ("inline", "deferred"):
        raise ValueError("validation.schedule must be inline or deferred.")
    interval = int(cfg.get("milestone_every", cfg["validate_every"]))
    if interval <= 0 or int(cfg["validate_every"]) <= 0:
        raise ValueError("Milestone and validation intervals must be positive.")
    return {"schedule": mode, "validate_every": int(cfg["validate_every"]),
            "milestone_every": interval,
            "periods": cfg.get("history", {}).get("validation_periods", [8]),
            "anchors_per_task": cfg["validation_anchors_per_task"]}


def milestone_steps(cfg):
    interval = validation_policy(cfg)["milestone_every"]
    return sorted(set(range(interval, cfg["steps"] + 1, interval)) | {cfg["steps"]})


def checkpoint_steps(cfg):
    steps = set(range(cfg["checkpoint_every"], cfg["steps"] + 1, cfg["checkpoint_every"]))
    steps.update(milestone_steps(cfg))
    if validation_policy(cfg)["schedule"] == "inline":
        steps.update(range(cfg["validate_every"], cfg["steps"] + 1, cfg["validate_every"]))
    return sorted(steps | {cfg["steps"]})
