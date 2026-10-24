"""Motion audit + within-episode pairs (NumPy only)."""
import numpy as np
import pytest

from fastwam.memory_v2.motion import (describe_within, gripper_events, match_within, phase_index, still_runs,
                                      stillness, summarise_stillness)


def _episode(n=100):
    a = np.zeros((n, 14))
    a[:, 6] = 1.0                 # left gripper open
    a[:, 13] = 1.0                # right gripper open
    return a


def test_gripper_events_with_hysteresis():
    a = _episode()
    a[20:50, 13] = 0.0            # right closes at 20, opens at 50
    a[60:62, 6] = 0.6             # left wiggle: inside the hysteresis band -> no event
    a[70:, 6] = 0.0               # left closes at 70 (range 1 -> counts)
    ev = gripper_events(a)
    assert [(e["t"], e["side"], e["kind"]) for e in ev] == [(20, "right", "close"), (50, "right", "open"),
                                                            (70, "left", "close")]
    ph = phase_index(len(a), ev)
    assert ph[19] == 0 and ph[20] == 1 and ph[50] == 2 and ph[99] == 3


def test_flat_gripper_has_no_events():
    a = _episode()
    a[:, 13] = np.linspace(0.9, 1.0, len(a))
    assert gripper_events(a) == []


def test_still_runs_and_stillness():
    a = _episode(160)
    a[:40, 0] = np.linspace(0, 1, 40)          # moving
    a[40:100, 0] = 1.0                         # still 60 steps
    a[100:, 0] = 1.0 + np.linspace(0, 1, 60)   # moving again
    runs = still_runs(a, arm_eps=0.01, min_length=8)
    assert len(runs) == 1 and runs[0]["start"] in (39, 40) and 60 <= runs[0]["length"] <= 62
    s = stillness(a, horizon=32, recent=16, arm_eps=0.01)
    assert s["future"][41] and not s["future"][80]          # 80 + 32 reaches the moving part
    assert s["recent"][60] and s["recent"][80] and not s["recent"][30]
    pooled = summarise_stillness([s])
    assert 0 < pooled["p_still_given_still"] < 1
    assert pooled["restart_given_still"] == pytest.approx(1 - pooled["p_still_given_still"])


def _item(ep, anchor, state, future, visual=None):
    c = np.full((32, 2), float(future))
    return {"episode_id": ep, "task": "t", "anchor": anchor, "state": np.asarray(state, float),
            "chunk": c, "valid": np.ones(32, bool), "visual": visual}


def test_within_pairs_same_episode_gap_and_event():
    items = [_item("a", 0, [0, 0], 0.0), _item("a", 8, [0, 0], 1.0),      # gap 8 < min_gap
             _item("a", 32, [0.01, 0], 1.0),                              # match (gap 32, delta 8)
             _item("a", 40, [0.01, 0], 0.0),                              # same future as anchor 0
             _item("b", 32, [0, 0], 1.0)]                                 # other episode: never a within pair
    phases = {"a": np.r_[np.zeros(20, int), np.ones(80, int)], "b": np.zeros(100, int)}
    pairs = match_within(items, phases, min_gap=16, per_query=5, query_filter=lambda it: it["anchor"] == 0)
    assert [(p["query"]["anchor"], p["donor"]["anchor"]) for p in pairs] == [(0, 32)]
    p = pairs[0]
    assert p["kind"] == "within" and p["gap"] == 32 and p["events_between"] == 1
    assert p["delta_norm"] == pytest.approx(8.0)
    none = match_within(items, {"a": np.zeros(100, int)}, min_gap=16, require_event=True,
                        query_filter=lambda it: it["anchor"] == 0)
    assert none == []
    d = describe_within(pairs)
    assert d["pairs"] == 1 and d["t"]["with_event"] == 1.0
