"""Plan v13 E1 STRESS (11-17, Opus): null-event injections for the closed loop. Pure numpy (the simulator adapter,
which runs in the simulator's python, imports this file; fastwam/__init__ and fastwam/fullft/__init__ import nothing).

An injection happens ONCE per episode, at the first decision after a trigger defined by the robot's own state (so the
moment is the same in the visible and the hidden arm of a pair, which share everything up to it):
  trigger  after the n-th gripper 'open' event (any arm; put_back_block n = 1, swap_blocks n = 2), the first 'top'
           reversal of that arm confirmed after it (the end-effector has risen to its apex after the release)
  pause    k targets = the last commanded target (the robot holds still)
  fidget   k targets: the active arm's wrist joint (6th arm joint) + 0.3 sin(2 pi i / k) rad, one full cycle, back to 0
  airgrasp k targets on the active arm's gripper command: quarter 1 down to 0 (closed), quarter 2 closed, quarter 3
           back up to the value before, quarter 4 held (on empty fingers: the trigger comes after a release)
The adapter executes them budget-neutrally (the official cap counts policy targets only), shows them to the policy as
ordinary past frames in the 'history' (visible) arm and not at all in the 'hidden' arm (memory_v2.online stress).
Validity (logged per injection, judged by e1_verdict.py): max object displacement, the active arm's joint return
error, task counters unchanged.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import numpy as np

try:
    from .events import EventDetector, EventRule
except ImportError:          # loaded by file path (the simulator adapter: its `fastwam` may be another checkout's)
    import importlib.util as _util
    import sys as _sys
    _spec = _util.spec_from_file_location("mwam_fullft_events", Path(__file__).with_name("events.py"))
    _events = _util.module_from_spec(_spec)
    _sys.modules["mwam_fullft_events"] = _events
    _spec.loader.exec_module(_events)
    EventDetector, EventRule = _events.EventDetector, _events.EventRule

KINDS = ("pause", "fidget", "airgrasp")
N_OPEN = {"put_back_block": 1, "swap_blocks": 2}
WRIST = {0: 5, 1: 12}                     # 14-d joint vector: left arm 0-5, left gripper 6, right arm 7-12, gripper 13
GRIP = {0: 6, 1: 13}
ARM = {0: slice(0, 6), 1: slice(7, 13)}
FIDGET_RAD = 0.3


class Trigger:
    """Streams the trainer's event detector over the executed frames; `step` returns True once the injection is due
    (and keeps returning True until `fire` is called); `arm` is the active arm."""

    def __init__(self, n_open: int, rule: Optional[EventRule] = None):
        self.detector = EventDetector(rule or EventRule())
        self.n_open = int(n_open)
        self.opens = 0
        self.arm: Optional[int] = None
        self.open_frame: Optional[int] = None
        self.due = False
        self.fired = False

    def step(self, frame: int, gripper: Sequence[float], positions) -> bool:
        for e in sorted(self.detector.step(frame, gripper, np.asarray(positions, dtype=np.float64)),
                        key=lambda e: (e["frame"], e["arm"])):
            if self.fired or self.due:
                break
            if e["kind"] == "open" and self.arm is None:
                self.opens += 1
                if self.opens == self.n_open:
                    self.arm, self.open_frame = int(e["arm"]), int(e["frame"])
            elif (e["kind"] == "top" and self.arm is not None and int(e["arm"]) == self.arm
                  and int(e["frame"]) > int(self.open_frame)):
                self.due = True
        return self.due and not self.fired

    def fire(self) -> None:
        self.fired, self.due = True, False


def targets_for(kind: str, k: int, last: Sequence[float], arm: int) -> List[np.ndarray]:
    """The k injected joint targets (14-d) that start from the last commanded target."""
    if kind not in KINDS:
        raise ValueError(f"injection must be one of {KINDS}, got {kind!r}")
    k = int(k)
    if k < 4:
        raise ValueError("an injection needs k >= 4 targets")
    base = np.asarray(last, dtype=np.float32)
    out = []
    for i in range(k):
        t = base.copy()
        if kind == "fidget":
            t[WRIST[arm]] = base[WRIST[arm]] + FIDGET_RAD * math.sin(2 * math.pi * (i + 1) / k)
        elif kind == "airgrasp":
            q, g0 = k // 4, float(base[GRIP[arm]])
            if i < q:
                t[GRIP[arm]] = g0 * (1 - (i + 1) / q)
            elif i < 2 * q:
                t[GRIP[arm]] = 0.0
            elif i < 3 * q:
                t[GRIP[arm]] = g0 * ((i - 2 * q + 1) / q)
            else:
                t[GRIP[arm]] = g0
        out.append(t)
    return out


def object_displacement(before: Dict, after: Dict) -> float:
    """Max 3-d displacement (m) over the objects of two adapter snapshots ({name: {"p": [x, y, z, ...]}})."""
    worst = 0.0
    for name, value in (before or {}).items():
        other = (after or {}).get(name)
        if isinstance(value, dict) and "p" in value and isinstance(other, dict) and "p" in other:
            worst = max(worst, float(np.linalg.norm(np.asarray(other["p"][:3], float) - np.asarray(value["p"][:3], float))))
    return worst


def counters_changed(before: Dict, after: Dict) -> List[str]:
    """Names of numeric task counters (task_state) that differ between two snapshots."""
    return sorted(n for n, v in (before or {}).items()
                  if isinstance(v, (int, float)) and not isinstance(v, bool) and (after or {}).get(n) != v)


def arm_return_error(before: Sequence[float], after: Sequence[float], arm: int) -> float:
    """Max |joint after - before| (rad) over the active arm's six joints."""
    b, a = np.asarray(before, float), np.asarray(after, float)
    return float(np.max(np.abs(a[ARM[arm]] - b[ARM[arm]])))
