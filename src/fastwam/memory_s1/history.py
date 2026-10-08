"""Shared historical selection with original IDs and an independent period RNG."""
from __future__ import annotations
import random
from .common import seed_for
VERSION = "modulo-with-decisions-v1"

def recipe(cfg):
    value = cfg.get("history", {})
    low, high = value.get("train_min", 8), value.get("train_max", 8)
    if not isinstance(low, int) or not isinstance(high, int) or not 1 <= low <= high <= 16:
        raise ValueError("Training periods must be integers within [1,16].")
    return {"version": VERSION, "minimum": low, "maximum": high, "decision_stride": 16,
            "phase": 0, "keep_current": True, "rng_purpose": "history-period", "distribution": "uniform_integer"}

def training_period(cfg, step, slot):
    rule = recipe(cfg)
    return random.Random(seed_for(cfg["seed"], step, slot, rule["rng_purpose"])).randint(rule["minimum"], rule["maximum"])

def select_ids(available, current, period, decision_stride=16):
    if not isinstance(period, int) or not 1 <= period <= 16:
        raise ValueError("History period must be an integer within [1,16].")
    ids = [int(i) for i in available]
    if ids != sorted(set(ids)) or any(i < 0 for i in ids):
        raise ValueError("Frame IDs must be unique, increasing nonnegative integers.")
    if current not in ids:
        raise ValueError("The current observation is missing.")
    return [i for i in ids if i <= current and (i % period == 0 or i % decision_stride == 0 or i == current)]

def online_period(cfg, current):
    history = cfg.get("history", {})
    cycle = history.get("online_cycle", [])
    value = int(cycle[(current // 16) % len(cycle)]) if cycle else int(history.get("online_period", 8))
    if not 1 <= value <= 16:
        raise ValueError("Online history periods must be within [1,16].")
    return value

def override_online(cfg, period=None, cycle=None):
    if period is not None and cycle is not None:
        raise ValueError("Choose a fixed period OR a decision-period cycle.")
    if period is not None or cycle is not None:
        cfg.setdefault("history", {})
        cfg["history"]["online_cycle"] = [] if cycle is None else [int(i) for i in cycle.split(",")]
        if period is not None:
            cfg["history"]["online_period"] = period
    values = cfg.get("history", {}).get("online_cycle", []) or [cfg.get("history", {}).get("online_period", 8)]
    if any(not 1 <= int(i) <= 16 for i in values):
        raise ValueError("Online periods must be within [1,16].")
    return cfg
