"""NumPy-only analysis used by the paper figures and Phase-0 checks (no torch needed).

* tau-weight budget: what share of the FM objective lands above a noise level,
  for the released training (shift-5 sampling), memory_s1 (uniform tau) and
  memory_v2 (mixture + bell_floor + endpoint).
* near-present branch distances from demonstrations: pairs of anchors from
  different episodes whose normalised present state is almost identical, and the
  distance between their future 32-step chunks -> ||Delta|| and tau_c.
* query-collapse geometry of the memory_s1 reader at initialisation.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


def phi(u, shift):
    u = np.asarray(u, dtype=np.float64)
    return shift * u / (1.0 + (shift - 1.0) * u)


def bell(tau, shift=1.0, steps=1000):
    u = np.linspace(1.0, 0.0, steps + 1)[:-1]
    y_grid = np.exp(-2.0 * (phi(u, shift) - 0.5) ** 2)
    y_min = y_grid.min()
    norm = (y_grid - y_min).mean()
    return (np.exp(-2.0 * (np.asarray(tau, dtype=np.float64) - 0.5) ** 2) - y_min) / (norm + 1e-10)


def objective_profile(name: str, samples: int = 400000, seed: int = 0) -> Tuple[np.ndarray, np.ndarray]:
    """(tau samples, per-sample weight) for a named recipe. Endpoint terms are point masses at tau = 1."""
    rng = np.random.default_rng(seed)
    u = rng.random(samples)
    if name == "released_shift5":
        tau = phi(u, 5.0)
        weight = bell(tau, 5.0)
    elif name == "memory_s1_uniform":
        tau = u
        weight = bell(tau, 1.0)
    elif name.startswith("memory_v2"):
        tau = u.copy()
        pick = rng.random(samples) < 0.3
        tau[pick] = 0.8 + 0.2 * rng.random(pick.sum())
        weight = np.maximum(bell(tau, 1.0), 0.25)
        if name == "memory_v2":  # + unit-weight endpoint term, one per sample
            tau = np.concatenate((tau, np.ones(samples)))
            weight = np.concatenate((weight, np.ones(samples)))
    else:
        raise ValueError(f"Unknown objective {name}.")
    return tau, weight


def mass_above(threshold: float, name: str, **kwargs) -> float:
    tau, weight = objective_profile(name, **kwargs)
    return float((weight * (tau >= threshold)).sum() / weight.sum())


def crossover_tau(delta_norm, separation=2.0):
    delta_norm = np.asarray(delta_norm, dtype=np.float64)
    return delta_norm / (delta_norm + separation)


def normalise(x: np.ndarray, mean: np.ndarray, std: np.ndarray, clip: float = 5.0) -> np.ndarray:
    """Released FastWAM z-score (std + 1e-8, clamp +-5)."""
    return np.clip((x - mean) / (std + 1e-8), -clip, clip)


def future_chunk(targets: np.ndarray, anchor: int, horizon: int = 32) -> Tuple[np.ndarray, np.ndarray]:
    count = min(horizon, len(targets) - anchor)
    if count <= 0:
        raise ValueError("Anchor beyond the end of the episode.")
    chunk = np.repeat(targets[anchor + count - 1][None], horizon, axis=0).astype(np.float64)
    chunk[:count] = targets[anchor:anchor + count]
    valid = np.zeros(horizon, dtype=bool)
    valid[:count] = True
    return chunk, valid


def near_present_branch_distances(episodes: Sequence[Dict[str, np.ndarray]], state_eps: float = 0.05,
                                  horizon: int = 32, anchor_stride: int = 16,
                                  min_fraction: float = 0.0, max_fraction: float = 1.0) -> Dict[str, np.ndarray]:
    """Cross-episode anchor pairs with nearly the same normalised present.

    episodes: list of {"state": [T,14] normalised, "target": [T,14] normalised}.
    Returns the future-chunk distances ||Delta|| (L2 over valid steps x dims) and
    the RMS present distance of every accepted pair. Restricting
    [min_fraction, max_fraction] of the episode isolates a task stage.
    """
    anchors = []
    for e, episode in enumerate(episodes):
        length = len(episode["state"])
        for t in range(0, length, anchor_stride):
            fraction = t / max(1, length - 1)
            if min_fraction <= fraction <= max_fraction:
                chunk, valid = future_chunk(episode["target"], t, horizon)
                anchors.append((e, episode["state"][t].astype(np.float64), chunk, valid))
    deltas, presents = [], []
    for i in range(len(anchors)):
        ei, si, ci, vi = anchors[i]
        for j in range(i + 1, len(anchors)):
            ej, sj, cj, vj = anchors[j]
            if ei == ej:
                continue
            present = float(np.sqrt(np.mean((si - sj) ** 2)))
            if present > state_eps:
                continue
            valid = vi & vj
            deltas.append(float(np.linalg.norm((ci - cj)[valid])))
            presents.append(present)
    return {"delta_norm": np.asarray(deltas), "present_rms": np.asarray(presents)}


def summarize_crossover(deltas: np.ndarray, quantiles: Iterable[float] = (0.25, 0.5, 0.75, 0.9),
                        recipes: Sequence[str] = ("released_shift5", "memory_s1_uniform", "memory_v2_no_endpoint", "memory_v2")) -> Dict:
    if len(deltas) == 0:
        return {"pairs": 0}
    out = {"pairs": int(len(deltas)), "quantiles": {}}
    for q in quantiles:
        d = float(np.quantile(deltas, q))
        tau_c = float(crossover_tau(d))
        out["quantiles"][str(q)] = {"delta_norm": d, "tau_c": tau_c,
                                    "objective_mass_above_tau_c": {name: mass_above(tau_c, name) for name in recipes}}
    return out


# ---------------------------------------------------------------------- collapse geometry
def _ln(x, eps=1e-6):
    return (x - x.mean(-1, keepdims=True)) / np.sqrt(x.var(-1, keepdims=True) + eps)


def _softmax(x, axis=-1):
    x = x - x.max(axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis, keepdims=True)


def slot_collapse_simulation(width: int = 256, slots: int = 32, heads: int = 8, history_tokens: int = 360,
                             blocks: int = 4, query_std: float = 0.02, context_rms: float = 0.96,
                             seed: int = 0) -> Dict[str, List[Dict[str, float]]]:
    """Init-time replica of memory_s1's reader (Q = U + broadcast c; cross -> self -> FFN, pre-LN, residual).

    Returns per-stage slot statistics for several query constructions:
      baseline (memory_s1), multiplicative (Q = U1 + U2*c), no_self_attention, rescaled_queries.
    """
    rng = np.random.default_rng(seed)

    def xavier(i, o):
        a = np.sqrt(6.0 / (i + o))
        return rng.uniform(-a, a, (i, o))

    def attention(q, src, w):
        def split(x):
            return x.reshape(x.shape[0], heads, width // heads).transpose(1, 0, 2)
        qh, kh, vh = split(q @ w[0]), split(src @ w[1]), split(src @ w[2])
        probs = _softmax(qh @ kh.transpose(0, 2, 1) / np.sqrt(width // heads))
        return (probs @ vh).transpose(1, 0, 2).reshape(q.shape[0], width) @ w[3]

    layers = [{"cross": [xavier(width, width) for _ in range(4)], "self": [xavier(width, width) for _ in range(4)],
               "w1": xavier(width, 4 * width), "w2": xavier(4 * width, width)} for _ in range(blocks)]

    def run(q0, use_self=True):
        q, stages = q0, [q0]
        for layer in layers:
            q = q + attention(_ln(q), _ln(z), layer["cross"])
            if use_self:
                n = _ln(q)
                q = q + attention(n, n, layer["self"])
            h = _ln(q) @ layer["w1"]
            h = 0.5 * h * (1 + np.tanh(0.7978845608 * (h + 0.044715 * h ** 3)))
            q = q + h @ layer["w2"]
            stages.append(q)
        return stages

    def stats(x):
        n = np.linalg.norm(x, axis=1)
        cosine = x @ x.T / np.outer(n, n)
        return {"min_cosine": float(cosine.min()),
                "centred_norm_percent": float(100 * np.linalg.norm(x - x.mean(0)) / np.linalg.norm(x))}

    z = rng.normal(0, 1, (history_tokens, width))
    u = rng.normal(0, query_std, (slots, width))
    c = rng.normal(0, context_rms, width)
    variants = {
        "baseline": (u + c[None], True),
        "multiplicative": (u + rng.normal(1.0, 0.5, (slots, width)) * c[None], True),
        "no_self_attention": (u + c[None], False),
        "rescaled_queries": (_ln(c)[None] + u * (1.0 / query_std), True),
    }
    return {name: [stats(s) for s in run(q0, use_self)] for name, (q0, use_self) in variants.items()}
