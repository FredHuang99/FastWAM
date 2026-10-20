"""Matched-present pair search (NumPy only)."""
import numpy as np
import pytest

from fastwam.memory_v2.pairs import chunk, match_pairs, summarise_pairs


def _item(ep, anchor, state, future, task="t", visual=None):
    c = np.repeat(np.asarray(future, dtype=float)[None], 32, 0)[:, None].repeat(2, 1)
    return {"episode_id": ep, "task": task, "anchor": anchor, "state": np.asarray(state, dtype=float),
            "chunk": c, "valid": np.ones(32, dtype=bool), "visual": visual}


def test_pairs_need_same_present_different_future_other_episode():
    items = [_item("a", 0, [0, 0], 0.0), _item("b", 5, [0.01, 0], 1.0),     # match: close state, delta = 8
             _item("c", 9, [0.01, 0], 0.0),                                  # close state but same future
             _item("a", 7, [0, 0], 1.0),                                     # same episode as query
             _item("d", 3, [1.0, 0], 1.0),                                   # far present
             _item("e", 1, [0, 0], 1.0, task="other")]                       # other task
    pairs = match_pairs(items, state_eps=0.05, min_delta=2.0, per_query=5,
                        query_filter=lambda it: it["episode_id"] == "a" and it["anchor"] == 0)
    assert [(p["donor"]["episode_id"], p["donor"]["anchor"]) for p in pairs] == [("b", 5)]
    assert pairs[0]["delta_norm"] == pytest.approx(8.0)


def test_visual_filter_and_per_query_order():
    v0, v1, v2 = np.array([1.0, 0]), np.array([1.0, 0.01]), np.array([0, 1.0])
    items = [_item("a", 0, [0, 0], 0.0, visual=v0), _item("b", 0, [0.02, 0], 1.0, visual=v1),
             _item("c", 0, [0.01, 0], 1.0, visual=v2), _item("d", 0, [0.03, 0], 1.0, visual=v1)]
    q = lambda it: it["episode_id"] == "a"
    all_pairs = match_pairs(items, per_query=2, query_filter=q)
    assert [p["donor"]["episode_id"] for p in all_pairs] == ["c", "b"]      # sorted by present distance
    close = match_pairs(items, per_query=5, query_filter=q, max_visual_distance=0.01)
    assert {p["donor"]["episode_id"] for p in close} == {"b", "d"}
    s = summarise_pairs(all_pairs, [])
    assert s["train"]["pairs"] == 2 and s["train"]["t"]["queries"] == 1


def test_chunk_masks_past_end():
    c, v = chunk(np.arange(10)[:, None].astype(float), 5)
    assert c.shape == (32, 1) and v.sum() == 5 and c[-1, 0] == 9
