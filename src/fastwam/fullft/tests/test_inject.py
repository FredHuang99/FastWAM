"""Plan v13 E1 null-event injections (fastwam/fullft/inject.py): the trigger fires once, after the n-th release at the
next apex of that arm; the three target sequences; the validity helpers; loading by file path (simulator side)."""
import importlib.util
import math
import sys
from pathlib import Path

import numpy as np

from fastwam.fullft.inject import Trigger, arm_return_error, counters_changed, object_displacement, targets_for


def _demo(n=260):
    grip = np.ones((n, 2)); pos = np.zeros((n, 2, 3)); pos[:, :, 2] = 0.30
    pos[:, 0, 0] = np.arange(n) * 0.002; pos[:, 1, 0] = 0.5
    grip[20:60, 0] = 0.0; grip[120:160, 0] = 0.0
    z = np.full(n, 0.30)
    for c in (60, 160):
        for f in range(c - 20, c + 20):
            z[f] = 0.30 - 0.06 * (1 - abs(f - c) / 20)
        for f in range(c + 20, c + 60):
            z[f] = 0.30 + 0.05 * math.sin(math.pi * (f - c - 20) / 40)
    pos[:, 0, 2] = z
    return grip, pos


def test_trigger_fires_once_after_the_nth_release_at_the_apex():
    grip, pos = _demo()
    for n_open, lo, hi in ((1, 100, 120), (2, 200, 220)):
        tr, fired = Trigger(n_open), []
        for t in range(len(grip)):
            if tr.step(t, grip[t], pos[t]):
                fired.append(t)
                tr.fire()
        assert len(fired) == 1 and lo <= fired[0] <= hi and tr.arm == 0


def test_target_sequences_and_validity():
    last = np.linspace(0, 1, 14).astype(np.float32); last[6] = 1.0
    assert all(np.array_equal(x, last) for x in targets_for("pause", 64, last, 0))
    f = targets_for("fidget", 64, last, 1)
    w = [x[12] - last[12] for x in f]
    assert abs(max(w) - 0.3) < 1e-3 and abs(min(w) + 0.3) < 1e-3 and abs(w[-1]) < 1e-6
    assert all(np.array_equal(np.delete(x, 12), np.delete(last, 12)) for x in f)
    g = [x[6] for x in targets_for("airgrasp", 32, last, 0)]
    assert min(g) == 0.0 and abs(g[-1] - 1.0) < 1e-6 and g[0] < 1.0
    assert object_displacement({"b": {"p": [0, 0, 0]}}, {"b": {"p": [0.003, 0.004, 0]}}) == 0.005
    assert counters_changed({"c": 1, "f": True}, {"c": 2, "f": False}) == ["c"]
    assert abs(arm_return_error(np.zeros(14), np.r_[np.zeros(5), 0.02, np.zeros(8)], 0) - 0.02) < 1e-9


def test_loads_by_file_path():
    path = Path(__file__).resolve().parents[1] / "inject.py"
    spec = importlib.util.spec_from_file_location("mwam_fullft_inject_test", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["mwam_fullft_inject_test"] = mod
    spec.loader.exec_module(mod)
    assert mod.N_OPEN == {"put_back_block": 1, "swap_blocks": 2} and mod.Trigger(2).n_open == 2


def test_press_trigger_fires_after_the_first_press_at_the_apex():
    """11-19 (plan v15 E24): press_button's trigger counts 'bottom' reversals (presses) instead of releases; put / swap
    keep ('open', 1 / 2) exactly as N_OPEN."""
    from fastwam.fullft.inject import N_OPEN, TRIGGERS
    assert {k: v for k, (kind, v) in TRIGGERS.items() if k in N_OPEN} == N_OPEN
    assert all(TRIGGERS[k][0] == "open" for k in N_OPEN) and TRIGGERS["press_button"] == ("bottom", 1)
    n = 300
    grip = np.ones((n, 2)); pos = np.zeros((n, 2, 3)); pos[:, :, 2] = 0.30
    pos[:, 0, 0] = 0.4; pos[:, 1, 0] = 0.0
    z = np.full(n, 0.30)
    for c in (80, 160, 240):                        # three presses: down 3 cm and back up over 40 frames
        for f in range(c - 20, c + 20):
            z[f] = 0.30 - 0.03 * (1 - abs(f - c) / 20)
    pos[:, 1, 2] = z
    tr, fired = Trigger(1, kind="bottom"), []
    for t in range(n):
        if tr.step(t, grip[t], pos[t]):
            fired.append(t)
            tr.fire()
    assert len(fired) == 1 and tr.arm == 1 and 85 <= fired[0] <= 100       # press 1 confirmed, before press 2
    try:
        Trigger(1, kind="sideways")
    except ValueError:
        pass
    else:
        raise AssertionError("an unknown trigger kind must be refused")
