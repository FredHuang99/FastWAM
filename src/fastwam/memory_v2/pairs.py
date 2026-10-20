"""Matched-present pairs: where only history can tell the correct future.

A pair is two anchors (query, donor) from different episodes of the same task whose
normalised present (proprio state) is nearly identical but whose 32-step future
chunks differ by ||Delta||. Optionally the current camera features must also be
close (visual distance = 1 - cosine of the token-mean post-Video-DiT feature).

Uses:
  * PR evaluation (history-swap response): with the query's current observation,
    does the model follow the query's history -> query future, and the donor's
    history -> donor future?
  * Counterfactual history training: (query current, donor history) -> donor future,
    only where the presents are indistinguishable (state AND visual close).

`match_pairs` is NumPy-only (unit-tested without torch); `build_pairs` reads the
dense cache and the feature store on the host.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

HISTORY_KEYS = ("history", "frame_ids", "roles", "history_valid", "current_ids",
                "s1_history", "s1_frame_ids", "s1_valid")


def chunk(actions: np.ndarray, anchor: int, horizon: int = 32):
    n = len(actions)
    index = np.minimum(np.arange(anchor, anchor + horizon), n - 1)
    return actions[index], np.arange(anchor, anchor + horizon) < n


def match_pairs(items: Sequence[dict], state_eps: float = 0.05, min_delta: float = 2.0, per_query: int = 3,
                query_filter=None, donor_filter=None, max_visual_distance: float = math.inf) -> List[dict]:
    """items: dicts with episode_id, task, anchor, state [S], chunk [H, D], valid [H], optional visual [F].

    For every query item, keep the `per_query` donors (other episode, same task) with the smallest
    present RMS <= state_eps and future distance >= min_delta (L2 over commonly valid steps).
    """
    out = []
    by_task: Dict[str, List[int]] = {}
    for i, it in enumerate(items):
        by_task.setdefault(it["task"], []).append(i)
    for task, index in by_task.items():
        states = np.stack([items[i]["state"] for i in index]).astype(np.float64)
        chunks = np.stack([items[i]["chunk"] for i in index]).astype(np.float64)
        valid = np.stack([items[i]["valid"] for i in index])
        episodes = np.array([items[i]["episode_id"] for i in index])
        has_visual = all(items[i].get("visual") is not None for i in index)
        if has_visual:
            vis = np.stack([items[i]["visual"] for i in index]).astype(np.float64)
            vis /= np.linalg.norm(vis, axis=1, keepdims=True).clip(1e-12)
        queries = [k for k, i in enumerate(index) if query_filter is None or query_filter(items[i])]
        donors = np.array([donor_filter is None or donor_filter(items[i]) for i in index])
        for q in queries:
            rms = np.sqrt(((states - states[q]) ** 2).mean(1))
            ok = (rms <= state_eps) & donors & (episodes != episodes[q])
            cand = np.nonzero(ok)[0]
            if not len(cand):
                continue
            common = valid[cand] & valid[q]
            diff = ((chunks[cand] - chunks[q]) ** 2).sum(-1) * common
            delta = np.sqrt(diff.sum(1))
            visual = 1.0 - vis[cand] @ vis[q] if has_visual else np.full(len(cand), np.nan)
            keep = delta >= min_delta
            if has_visual:
                keep &= visual <= max_visual_distance
            cand, delta, visual = cand[keep], delta[keep], visual[keep]
            for j in np.argsort(rms[cand], kind="stable")[:per_query]:
                d = cand[j]
                out.append({"task": task,
                            "query": {"episode_id": items[index[q]]["episode_id"], "anchor": int(items[index[q]]["anchor"])},
                            "donor": {"episode_id": items[index[d]]["episode_id"], "anchor": int(items[index[d]]["anchor"])},
                            "present_rms": float(rms[d]), "delta_norm": float(delta[j]),
                            "visual_distance": None if not has_visual else float(visual[j])})
    return out


def build_pairs(spec, records: Sequence[dict], episodes, features=None, anchor_stride: int = 8,
                stage=(0.3, 1.0), state_eps: float = 0.05, min_delta: float = 2.0, per_query: int = 3,
                log=print) -> Dict[str, object]:
    """Host side: anchors from the dense cache (normalised proprio/actions) + token-mean visual features."""
    split = {r["episode_id"]: r["split"] for r in records}
    items = []
    for r in records:
        e = episodes(r["episode_id"])
        n = len(e["actions"])
        proprio = e["proprio"].float().numpy()
        actions = e["actions"].float().numpy()
        anchors = [a for a in range(0, n, anchor_stride) if stage[0] <= a / max(1, n - 1) <= stage[1]]
        visual = None
        if features is not None and anchors:
            f = features(r["episode_id"])
            visual = f[anchors].float().mean(1).numpy()
        for k, a in enumerate(anchors):
            c, v = chunk(actions, a)
            items.append({"episode_id": r["episode_id"], "task": r["task"], "anchor": a, "state": proprio[a],
                          "chunk": c, "valid": v, "visual": None if visual is None else visual[k]})
        log(f"[pairs] {r['episode_id']}: {len(anchors)} anchors")
    common = dict(state_eps=state_eps, min_delta=min_delta, per_query=per_query)
    train = match_pairs(items, query_filter=lambda it: split[it["episode_id"]] == "train",
                        donor_filter=lambda it: split[it["episode_id"]] == "train", **common)
    val = match_pairs(items, query_filter=lambda it: split[it["episode_id"]] == "val", donor_filter=None, **common)
    for p in val:
        p["donor_split"] = split[p["donor"]["episode_id"]]
    return {"settings": {"anchor_stride": anchor_stride, "stage": list(stage), **common,
                         "visual": "1 - cos(token-mean post-Video-DiT feature)" if features is not None else None},
            "anchors": len(items), "train": train, "val": val, "summary": summarise_pairs(train, val)}


def summarise_pairs(train: Sequence[dict], val: Sequence[dict]) -> dict:
    def stats(pairs):
        out = {"pairs": len(pairs)}
        for task in sorted({p["task"] for p in pairs}):
            sub = [p for p in pairs if p["task"] == task]
            d = np.array([p["delta_norm"] for p in sub])
            vis = np.array([p["visual_distance"] for p in sub if p["visual_distance"] is not None])
            out[task] = {"pairs": len(sub), "queries": len({(p["query"]["episode_id"], p["query"]["anchor"]) for p in sub}),
                         "delta_q25_50_75": [float(np.quantile(d, q)) for q in (0.25, 0.5, 0.75)],
                         "visual_q25_50_75": [float(np.quantile(vis, q)) for q in (0.25, 0.5, 0.75)] if len(vis) else None}
        return out
    return {"train": stats(train), "val": stats(val)}


def load_pairs(path, split: str, max_visual_distance: Optional[float] = None, min_delta: float = 0.0,
               donor_split: Optional[str] = None) -> List[dict]:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    pairs = value[split]
    out = []
    for p in pairs:
        if p["delta_norm"] < min_delta:
            continue
        if max_visual_distance is not None and p.get("visual_distance") is not None and p["visual_distance"] > max_visual_distance:
            continue
        if donor_split is not None and p.get("donor_split", "train") != donor_split:
            continue
        out.append(p)
    return out


def swap_history(current: dict, donor: dict) -> dict:
    """Batch with `current`'s observation and `donor`'s history (and donor targets)."""
    out = dict(current)
    for key in HISTORY_KEYS:
        if key in donor:
            out[key] = donor[key]
    out["actions"] = donor["actions"]
    out["action_valid"] = donor["action_valid"]
    return out
