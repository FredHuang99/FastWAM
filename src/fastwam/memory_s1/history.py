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
    result = {"version": VERSION, "minimum": low, "maximum": high, "decision_stride": 16,
            "phase": 0, "keep_current": True, "rng_purpose": "history-period", "distribution": "uniform_integer"}
    mode = value.get("train_phase", "zero")
    if mode not in ("zero", "uniform"):
        raise ValueError("train_phase must be zero or uniform.")
    if mode == "uniform":
        result.update(version="modulo-phase-with-decisions-v2", phase="uniform_given_T",
                      phase_rng_purpose="history-phase", keep_initial=True)
    return result

def training_period(cfg, step, slot):
    rule = recipe(cfg)
    return random.Random(seed_for(cfg["seed"], step, slot, rule["rng_purpose"])).randint(rule["minimum"], rule["maximum"])

def training_phase(cfg, step, slot, period):
    rule = recipe(cfg)
    if rule["phase"] == 0:
        return 0
    return random.Random(seed_for(cfg["seed"], step, slot, rule["phase_rng_purpose"])).randrange(period)


def evaluation_phase(cfg, period, episode, purpose="validation"):
    history = cfg.get("history", {})
    mode = history.get("online_phase", "zero")
    if mode == "zero":
        return 0
    if mode == "fixed":
        phase = history.get("phase", 0)
        if not isinstance(phase, int) or not 0 <= phase < period:
            raise ValueError("Fixed phase must satisfy 0 <= phase < every selected period.")
        return phase
    if mode != "episode_seeded":
        raise ValueError("online_phase must be zero, fixed or episode_seeded.")
    return random.Random(seed_for(cfg["seed"], episode, period, "history-phase-" + purpose)).randrange(period)


def select_ids(available, current, period, decision_stride=16, phase=0):
    if not isinstance(period, int) or not 1 <= period <= 16:
        raise ValueError("History period must be an integer within [1,16].")
    if not isinstance(phase, int) or not 0 <= phase < period:
        raise ValueError("History phase must be an integer in [0,T).")
    ids = [int(i) for i in available]
    if ids != sorted(set(ids)) or any(i < 0 for i in ids):
        raise ValueError("Frame IDs must be unique, increasing nonnegative integers.")
    if current not in ids:
        raise ValueError("The current observation is missing.")
    return [i for i in ids if i <= current and (i % period == phase or i % decision_stride == 0 or i == current or i == 0)]

def online_period(cfg, current):
    history = cfg.get("history", {})
    cycle = history.get("online_cycle", [])
    value = int(cycle[(current // 16) % len(cycle)]) if cycle else int(history.get("online_period", 8))
    if not 1 <= value <= 16:
        raise ValueError("Online history periods must be within [1,16].")
    return value

def override_online(cfg, period=None, cycle=None, phase=None):
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
    if phase is not None:
        if not 0 <= phase < min(values):
            raise ValueError("Fixed phase must be valid for every requested period.")
        cfg.setdefault("history", {}).update(online_phase="fixed", phase=phase)
    return cfg
