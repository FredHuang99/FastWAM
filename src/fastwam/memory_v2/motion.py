"""Motion audit of the expert data and within-episode transition pairs (NumPy only).

Why: in closed loop (10-24 trace) memory_v2 D reaches the memory-dependent states
(put_back: block centred / button pressed; swap: after the second move) and then
stops moving for hundreds of targets. Two explanations, with different fixes:

  * inertia ("copycat"): the expert data holds still for long stretches, and a
    policy that sees recent frames learns "still -> still"; once it stops, its
    own history keeps it stopped.  Measured here by how often a still recent
    past is followed by a still future, and how often by a restart.
  * phase ambiguity: two moments of one episode look alike now (same pose, same
    scene) but need different futures; only the history tells them apart.  The
    cross-episode pairs (pairs.py) never contain these, because the donor must
    come from another episode.  `match_within` mines them inside an episode.

All functions take raw (denormalised) action targets [n, 14]: arm joints in
radians at ARM_COLUMNS, grippers at GRIPPER_COLUMNS (low = closed).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np

ARM_COLUMNS = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]
GRIPPER_COLUMNS = [6, 13]
SIDES = {6: "left", 13: "right"}


# ----------------------------------------------------------------------------- events
def gripper_events(actions: np.ndarray, min_range: float = 0.2, hysteresis: float = 0.15) -> List[dict]:
    """Close/open transitions of each gripper target, with hysteresis around the episode's own midpoint.

    A gripper whose target spans less than `min_range` in the episode never changes state.
    Returns [{"t", "side", "kind"}] sorted by t; t is the first step past the threshold.
    """
    out = []
    for col in GRIPPER_COLUMNS:
        g = np.asarray(actions[:, col], dtype=np.float64)
        lo, hi = float(g.min()), float(g.max())
        if hi - lo < min_range:
            continue
        x = (g - lo) / (hi - lo)
        closed = x[0] < 0.5
        for t in range(1, len(x)):
            if not closed and x[t] < 0.5 - hysteresis:
                closed = True
                out.append({"t": t, "side": SIDES[col], "kind": "close"})
            elif closed and x[t] > 0.5 + hysteresis:
                closed = False
                out.append({"t": t, "side": SIDES[col], "kind": "open"})
    return sorted(out, key=lambda e: (e["t"], e["side"]))


def phase_index(n: int, events: Sequence[dict]) -> np.ndarray:
    """Number of gripper events at or before each step [n]."""
    count = np.zeros(n, dtype=np.int64)
    for e in events:
        count[e["t"]:] += 1
    return count


# ----------------------------------------------------------------------------- stillness
def step_speed(actions: np.ndarray) -> np.ndarray:
    """Per-step max |change| of the arm joints and of the grippers: [n-1, 2] (arm rad/step, gripper/step)."""
    d = np.abs(np.diff(np.asarray(actions, dtype=np.float64), axis=0))
    return np.stack([d[:, ARM_COLUMNS].max(1), d[:, GRIPPER_COLUMNS].max(1)], 1)


def window_range(actions: np.ndarray, start: int, stop: int) -> np.ndarray:
    """Per-column max - min over steps [start, stop) clipped to the episode: [14]."""
    a = np.asarray(actions, dtype=np.float64)
    lo, hi = max(0, start), min(len(a), stop)
    if hi - lo < 1:
        return np.zeros(a.shape[1])
    w = a[lo:hi]
    return w.max(0) - w.min(0)


def is_still(span: np.ndarray, arm_eps: float, gripper_eps: float) -> bool:
    return bool(span[ARM_COLUMNS].max() < arm_eps and span[GRIPPER_COLUMNS].max() < gripper_eps)


def still_runs(actions: np.ndarray, arm_eps: float, gripper_eps: float = 0.05, min_length: int = 8) -> List[dict]:
    """Maximal stretches where the targets stay within arm_eps (rad) / gripper_eps of the stretch's first target.

    Greedy from left: a run continues while every column stays within eps of where it started. Runs shorter
    than `min_length` steps are dropped. Returns [{"start", "length"}].
    """
    a = np.asarray(actions, dtype=np.float64)
    n = len(a)
    runs, s = [], 0
    while s < n:
        e = s + 1
        while e < n:
            span = np.abs(a[s:e + 1] - a[s]).max(0)
            if not is_still(span, arm_eps, gripper_eps):
                break
            e += 1
        if e - s >= min_length:
            runs.append({"start": s, "length": e - s})
            s = e
        else:
            s += 1
    return runs


def stillness(actions: np.ndarray, horizon: int = 32, recent: int = 16, arm_eps: float = 0.01,
              gripper_eps: float = 0.05) -> Dict[str, np.ndarray]:
    """Per anchor: is the future chunk [a, a+horizon) still; was the recent past [a-recent, a) still.

    Anchors whose recent window would start before frame 0 are marked recent=False (not still).
    Returns {"future": bool[n], "recent": bool[n]}.
    """
    n = len(actions)
    future = np.array([is_still(window_range(actions, a, a + horizon), arm_eps, gripper_eps) for a in range(n)])
    recent_ok = np.array([a >= recent and is_still(window_range(actions, a - recent, a + 1), arm_eps, gripper_eps)
                          for a in range(n)])
    return {"future": future, "recent": recent_ok}


def summarise_stillness(rows: Sequence[dict]) -> dict:
    """rows: {"future": bool[n], "recent": bool[n], "position": float[n]} per episode -> pooled rates.

    still_future      : share of training anchors whose target chunk is "hold still"
    still_recent      : share of anchors whose recent past was still
    p_still_given_still: P(future still | recent still)   -- the inertia the data teaches
    restart_given_still: 1 - the above                       -- how often the expert moves off after holding
    """
    fut = np.concatenate([r["future"] for r in rows]) if rows else np.zeros(0, bool)
    rec = np.concatenate([r["recent"] for r in rows]) if rows else np.zeros(0, bool)
    n = len(fut)
    both = int((fut & rec).sum())
    out = {"anchors": n, "still_future": float(fut.mean()) if n else float("nan"),
           "still_recent": float(rec.mean()) if n else float("nan"),
           "p_still_given_still": both / max(1, int(rec.sum())) if rec.any() else float("nan"),
           "p_still_given_moving": int((fut & ~rec).sum()) / max(1, int((~rec).sum())) if (~rec).any() else float("nan")}
    out["restart_given_still"] = 1.0 - out["p_still_given_still"] if rec.any() else float("nan")
    return out


# ----------------------------------------------------------------------------- within-episode pairs
def match_within(items: Sequence[dict], phases: Dict[str, np.ndarray], min_gap: int = 16, state_eps: float = 0.05,
                 min_delta: float = 2.0, per_query: int = 3, max_visual_distance: float = np.inf,
                 require_event: bool = False, query_filter=None) -> List[dict]:
    """Pairs of anchors of the SAME episode with nearly the same present and different futures.

    items: dicts with episode_id, task, anchor, state [S], chunk [H, D], valid [H], optional visual [F]
           (same layout as pairs.match_pairs).
    phases: episode_id -> phase_index array (gripper events so far), to annotate/require an event between.

    Each unordered anchor pair is reported once (query = earlier anchor). Per query, the `per_query`
    later donors with the smallest present RMS are kept. Training uses both directions anyway.
    """
    out = []
    by_episode: Dict[str, List[int]] = {}
    for i, it in enumerate(items):
        by_episode.setdefault(it["episode_id"], []).append(i)
    for episode, index in by_episode.items():
        index = sorted(index, key=lambda i: items[i]["anchor"])
        anchors = np.array([items[i]["anchor"] for i in index])
        states = np.stack([items[i]["state"] for i in index]).astype(np.float64)
        chunks = np.stack([items[i]["chunk"] for i in index]).astype(np.float64)
        valid = np.stack([items[i]["valid"] for i in index])
        has_visual = all(items[i].get("visual") is not None for i in index)
        if has_visual:
            vis = np.stack([items[i]["visual"] for i in index]).astype(np.float64)
            vis /= np.linalg.norm(vis, axis=1, keepdims=True).clip(1e-12)
        phase = phases.get(episode)
        for q in range(len(index)):
            if query_filter is not None and not query_filter(items[index[q]]):
                continue
            later = np.nonzero(anchors - anchors[q] >= min_gap)[0]
            if not len(later):
                continue
            rms = np.sqrt(((states[later] - states[q]) ** 2).mean(1))
            common = valid[later] & valid[q]
            delta = np.sqrt((((chunks[later] - chunks[q]) ** 2).sum(-1) * common).sum(1))
            keep = (rms <= state_eps) & (delta >= min_delta)
            visual = 1.0 - vis[later] @ vis[q] if has_visual else np.full(len(later), np.nan)
            if has_visual:
                keep &= visual <= max_visual_distance
            events = (phase[anchors[later]] - phase[anchors[q]]) if phase is not None else np.zeros(len(later), int)
            if require_event:
                keep &= events >= 1
            cand = np.nonzero(keep)[0]
            for j in cand[np.argsort(rms[cand], kind="stable")][:per_query]:
                d = later[j]
                out.append({"task": items[index[q]]["task"], "kind": "within",
                            "query": {"episode_id": episode, "anchor": int(anchors[q])},
                            "donor": {"episode_id": episode, "anchor": int(anchors[d])},
                            "gap": int(anchors[d] - anchors[q]), "events_between": int(events[j]),
                            "present_rms": float(rms[j]), "delta_norm": float(delta[j]),
                            "visual_distance": None if not has_visual else float(visual[j])})
    return out


def describe_within(pairs: Sequence[dict]) -> dict:
    out = {"pairs": len(pairs)}
    for task in sorted({p["task"] for p in pairs}):
        sub = [p for p in pairs if p["task"] == task]
        gap = np.array([p["gap"] for p in sub])
        ev = np.array([p["events_between"] for p in sub])
        out[task] = {"pairs": len(sub), "episodes": len({p["query"]["episode_id"] for p in sub}),
                     "gap_q25_50_75": [float(np.quantile(gap, q)) for q in (0.25, 0.5, 0.75)],
                     "with_event": float((ev >= 1).mean()),
                     "delta_median": float(np.median([p["delta_norm"] for p in sub]))}
    return out
