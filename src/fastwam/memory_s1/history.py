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

ONLINE_VERSION = "history-decision-v1"


def online_contract(cfg):
    history = cfg.get("history", {})
    cycle = history.get("online_cycle", [])
    mode = history.get("online_mode", "cycle" if cycle else "fixed")
    if mode not in ("fixed", "cycle", "seeded_per_decision"):
        raise ValueError("Unknown online history mode.")
    if mode != "cycle" and cycle:
        raise ValueError("A history cycle cannot be combined with another sampling mode.")
    low, high = history.get("online_min", 1), history.get("online_max", 16)
    if not all(type(i) is int for i in (low, high)) or not 1 <= low <= high <= 16:
        raise ValueError("Online random T bounds must be integers within [1,16].")
    if mode == "seeded_per_decision" and history.get("online_phase") == "fixed":
        raise ValueError("Random per-decision sampling draws its own phase; remove fixed phase.")
    values = cycle if mode == "cycle" else [history.get("online_period", 8)]
    if not values or any(type(i) is not int or not 1 <= i <= 16 for i in values):
        raise ValueError("Online periods must be integers within [1,16].")
    return {"version": ONLINE_VERSION, "mode": mode, "period": history.get("online_period", 8),
            "cycle": list(cycle), "minimum": low, "maximum": high,
            "phase_rule": "uniform_per_decision" if mode == "seeded_per_decision" else history.get("online_phase", "zero"),
            "phase": history.get("phase", 0), "seed": cfg["seed"],
            "seed_rule": "seed_for(seed,task:scene,current_frame,purpose); separate T/phase; weights excluded",
            "decision_stride": 16, "manifest_sha256": history.get("diagnostic_manifest_sha256")}


def resolve_online(cfg, task, episode_seed, current):
    """Stateless, retry-stable sampling. Call once and retain this record with the input."""
    if type(current) is not int or current < 0:
        raise ValueError("A nonnegative current frame is required.")
    rule = online_contract(cfg)
    episode = f"{task}:{int(episode_seed)}"
    if rule["mode"] == "seeded_per_decision":
        period = random.Random(seed_for(cfg["seed"], episode, current, "online-history-period-v1")).randint(rule["minimum"], rule["maximum"])
        phase = random.Random(seed_for(cfg["seed"], episode, current, "online-history-phase-v1")).randrange(period)
    else:
        period = online_period(cfg, current)
        phase = evaluation_phase(cfg, period, episode, "online")
    return {"version": ONLINE_VERSION, "mode": rule["mode"], "period": period, "phase": phase,
            "decision_id": f"{episode}:{current}", "current_frame": current}


def online_arguments(cfg):
    """One shared parent/child CLI representation; never force T=8 over random mode."""
    rule = online_contract(cfg)
    result = ["--history-mode", rule["mode"]]
    if rule["mode"] == "cycle":
        result += ["--history-cycle", ",".join(map(str, rule["cycle"]))]
    elif rule["mode"] == "fixed":
        result += ["--history-period", str(rule["period"])]
    if rule["phase_rule"] == "fixed":
        result += ["--history-phase", str(rule["phase"])]
    return result


def online_period(cfg, current):
    history = cfg.get("history", {})
    cycle = history.get("online_cycle", [])
    if history.get("online_mode") == "seeded_per_decision":
        raise ValueError("Random online history requires resolve_online with task and scene identity.")
    value = int(cycle[(current // 16) % len(cycle)]) if cycle else int(history.get("online_period", 8))
    if not 1 <= value <= 16:
        raise ValueError("Online history periods must be within [1,16].")
    return value

def override_online(cfg, period=None, cycle=None, phase=None, mode=None):
    if mode == "seeded_per_decision" and any(v is not None for v in (period, cycle, phase)):
        raise ValueError("Random per-decision history cannot have fixed T/phase or a cycle override.")
    if mode == "fixed" and cycle is not None or mode == "cycle" and period is not None:
        raise ValueError("Conflicting history mode and period/cycle override.")
    if mode is not None:
        cfg.setdefault("history", {})["online_mode"] = mode
    if period is not None and cycle is not None:
        raise ValueError("Choose a fixed period OR a decision-period cycle.")
    if period is not None or cycle is not None:
        cfg.setdefault("history", {})
        cfg["history"]["online_cycle"] = [] if cycle is None else [int(i) for i in cycle.split(",")]
        cfg["history"]["online_mode"] = "fixed" if cycle is None else "cycle"
        if period is not None:
            cfg["history"]["online_period"] = period
    values = cfg.get("history", {}).get("online_cycle", []) or [cfg.get("history", {}).get("online_period", 8)]
    if any(not 1 <= int(i) <= 16 for i in values):
        raise ValueError("Online periods must be within [1,16].")
    if phase is not None:
        if not 0 <= phase < min(values):
            raise ValueError("Fixed phase must be valid for every requested period.")
        cfg.setdefault("history", {}).update(online_phase="fixed", phase=phase)
    online_contract(cfg)
    return cfg
