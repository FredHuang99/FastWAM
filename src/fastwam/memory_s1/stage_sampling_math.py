"""CPU rules for genuine command transitions, sampling, and masked action errors."""
from __future__ import annotations

import numpy as np

BRANCHES = ("uniform", "transition_balanced")
TASKS = ("put_back_block", "swap_blocks")
ARMS = (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)
GRIPPERS = (6, 13)


def event_partition(states, targets, anchors, threshold=.5, horizon=32):
    """A future label may guide sampling, but never becomes a model input."""
    states, targets = np.asarray(states), np.asarray(targets)
    anchors = [int(a) for a in anchors]
    if (states.shape != targets.shape or states.ndim != 2 or states.shape[1] != 14
            or not np.isfinite(states).all() or not np.isfinite(targets).all()
            or anchors != list(range(0, len(targets), 16)) or threshold != .5 or horizon != 32):
        raise ValueError("Expected original 14-D sequences, 16-stride anchors and 32-target horizon")
    previous = np.concatenate((states[:1, GRIPPERS], targets[:-1, GRIPPERS]), axis=0)
    grip = targets[:, GRIPPERS]
    closing = np.flatnonzero(((previous >= threshold) & (grip < threshold)).any(axis=1)).tolist()
    opening = np.flatnonzero(((previous < threshold) & (grip >= threshold)).any(axis=1)).tolist()
    bins = {key: [] for key in ("closing", "approach", "opening", "other")}
    for a in anchors:
        end = min(a + horizon, len(targets))
        if any(a <= e < end for e in closing):
            kind = "closing"
        elif any(end <= e < min(end + horizon, len(targets)) for e in closing):
            kind = "approach"
        elif any(a <= e < end for e in opening):
            kind = "opening"
        else:
            kind = "other"
        bins[kind].append(a)
    flattened = [a for values in bins.values() for a in values]
    if sorted(flattened) != anchors or len(flattened) != len(set(flattened)):
        raise ValueError("Transition bins must partition every original anchor exactly once")
    nonempty = sum(bool(v) for v in bins.values())
    probabilities = {str(a): 1 / (nonempty * len(values)) for values in bins.values() for a in values}
    return {"bins": bins, "closing_targets": closing, "opening_targets": opening,
            "conditional_balanced_probability": probabilities, "anchors": anchors,
            "semantics": "command half-close/open crossings; not contact or successful-grasp labels"}


def draw(record, sampling_update, slot, branch, seed, seed_for):
    """Episode choice is upstream and identical; only anchor choice changes."""
    if branch not in BRANCHES:
        raise ValueError("Unknown sampling branch")
    # Preserve the original RNG consumption: first draw was the episode index.
    rng = np.random.default_rng(seed_for(seed, sampling_update, slot, "sample"))
    rng.integers(record["episodes_in_task"])
    original = int(rng.choice(record["anchors"]))
    nonempty = [key for key, values in record["bins"].items() if values]
    if branch == "uniform":
        anchor = original
    else:
        phases = np.random.default_rng(seed_for(seed, sampling_update, slot, "stage-pilot-anchor-v1"))
        kind = nonempty[int(phases.integers(len(nonempty)))]
        anchor = int(phases.choice(record["bins"][kind]))
    kind = next(key for key, values in record["bins"].items() if anchor in values)
    return anchor, kind, original


def validation_anchors(record):
    """At most four per episode: initial, approach, closing, and after closing."""
    anchors = record["anchors"]
    result = [(0, "initial")]
    events = record["closing_targets"]
    if events:
        crossing = events[0]
        before = [a for a in anchors if a + 16 <= crossing]
        if before:
            result.append((before[-1], "reference_approach"))
        result.append((min((crossing // 16) * 16, anchors[-1]), "reference_closing"))
        later = [a for a in anchors if a >= crossing + 32]
        if later:
            result.append((later[0], "reference_postclosing"))
    seen, unique = set(), []
    for a, kind in result:
        if a not in seen:
            unique.append((a, kind)); seen.add(a)
    return unique


def action_errors(predicted, targets, valid, current):
    """Physical-unit command errors; valid tail labels only, both horizons."""
    predicted, targets = np.asarray(predicted, np.float64), np.asarray(targets, np.float64)
    valid = np.asarray(valid, bool)
    current = np.asarray(current, np.float64)
    if (predicted.shape != (32, 14) or targets.shape != predicted.shape or valid.shape != (32,)
            or current.shape != (14,) or not valid.any()
            or not np.isfinite(predicted).all() or not np.isfinite(targets).all()):
        raise ValueError("Expected finite 32x14 actions and a real tail mask")
    clipped = predicted.copy(); clipped[:, GRIPPERS] = np.clip(clipped[:, GRIPPERS], 0, 1)
    result = {}
    for name, sl in (("executed16", slice(0, 16)), ("future16", slice(16, 32))):
        mask = valid[sl]
        if not mask.any():
            result[name] = {"valid_targets": 0, "arm_rmse_rad": None, "gripper_mae": None}
            continue
        error = clipped[sl][mask] - targets[sl][mask]
        truth = targets[sl][mask] - current
        estimate = clipped[sl][mask] - current
        moving = np.abs(truth[:, ARMS]) > .01
        wrong = moving & (np.sign(truth[:, ARMS]) != np.sign(estimate[:, ARMS]))
        result[name] = {"valid_targets": int(mask.sum()),
            "arm_rmse_rad": float(np.sqrt(np.mean(error[:, ARMS] ** 2))),
            "left_arm_rmse_rad": float(np.sqrt(np.mean(error[:, :6] ** 2))),
            "right_arm_rmse_rad": float(np.sqrt(np.mean(error[:, 7:13] ** 2))),
            "gripper_mae": float(np.mean(np.abs(error[:, GRIPPERS]))),
            "per_joint_mae": np.abs(error).mean(0).tolist(),
            "moving_arm_elements": int(moving.sum()), "wrong_motion_sign_elements": int(wrong.sum())}
    result["half_close_offset"] = {}
    for g, side in zip(GRIPPERS, ("left", "right")):
        if current[g] < .5:
            result["half_close_offset"][side] = {"eligible": False, "reason": "already_closed"}
            continue
        truth = np.flatnonzero(valid & (targets[:, g] < .5))
        guess = np.flatnonzero(valid & (clipped[:, g] < .5))
        result["half_close_offset"][side] = {"eligible": bool(len(truth)),
            "reference_index": int(truth[0]) if len(truth) else None,
            "predicted_index": int(guess[0]) if len(guess) else None,
            "offset_targets": int(guess[0] - truth[0]) if len(truth) and len(guess) else None,
            "missed_within_window": bool(len(truth) and not len(guess))}
    return result
