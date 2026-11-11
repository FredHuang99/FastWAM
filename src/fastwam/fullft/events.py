"""Proprioceptive events (plan v10 D.4): label-free, no learnable parameters, the same rule offline and online.

An event is a moment where the robot's own state changes regime:
  * gripper: a gripper command crosses its midpoint (close <-> open), with hysteresis;
  * reversal: an end-effector's height goes down (or up) by >= delta and then comes back by >= delta (a press / a
    place-and-lift); the event is at the turning point;
  * debounce: an event closer than `min_path` (metres of end-effector PATH, not time) to the previous event of the
    same arm is dropped.
All thresholds are on distances and gripper values, never on time, so holding still (a pause) or moving slower
(a slowed replay) yields the same events at the corresponding frames: tests/test_fullft.py checks both.

Inputs per frame: gripper values [n, 2] in [0, 1] (columns 6 and 13 of the 14-d joint vector) and end-effector
positions [n, 2, 3] (left, right; metres). Offline they come from the demo hdf5 (endpose / ee poses), online from
the simulator's observation; `EventDetector` is the streaming form used online, `detect` the batch form, and they
give identical events (tested).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

import numpy as np


@dataclass(frozen=True)
class EventRule:
    gripper_high: float = 0.65        # open above, closed below gripper_low (hysteresis band in between)
    gripper_low: float = 0.35
    delta: float = 0.015              # metres of height change before and after a turning point
    min_path: float = 0.03            # metres of end-effector path between two events of the same arm
    use_gripper: bool = True
    use_reversal: bool = True


@dataclass
class _ArmState:
    gripper_open: Optional[bool] = None
    direction: int = 0                # +1 going up, -1 going down, 0 unknown
    extreme_z: Optional[float] = None
    extreme_frame: int = 0
    anchor_z: Optional[float] = None  # height where the current direction was confirmed
    path_since_event: float = float("inf")
    last_position: Optional[np.ndarray] = None


@dataclass
class EventDetector:
    """Streaming detector: call step(frame, gripper[2], positions[2, 3]) once per frame, in order.

    Returns the list of events confirmed at this call: {"frame", "arm", "kind"}. A reversal is confirmed only once
    the height has come back by `delta`, so its frame (the turning point) is in the past; online selection uses
    only confirmed events (no look-ahead)."""
    rule: EventRule = field(default_factory=EventRule)
    arms: List[_ArmState] = field(default_factory=lambda: [_ArmState(), _ArmState()])

    def reset(self) -> None:
        self.arms = [_ArmState(), _ArmState()]

    def _emit(self, arm: _ArmState, out: list, frame: int, side: int, kind: str) -> None:
        if arm.path_since_event >= self.rule.min_path:
            out.append({"frame": int(frame), "arm": side, "kind": kind})
            arm.path_since_event = 0.0

    def step(self, frame: int, gripper: Sequence[float], positions) -> List[dict]:
        r = self.rule
        positions = np.asarray(positions, dtype=np.float64).reshape(2, 3)
        out: List[dict] = []
        for side in (0, 1):
            arm = self.arms[side]
            p = positions[side]
            if arm.last_position is not None:
                arm.path_since_event += float(np.linalg.norm(p - arm.last_position))
            arm.last_position = p.copy()
            g = float(gripper[side])
            if r.use_gripper:
                state = arm.gripper_open
                if state is None:
                    arm.gripper_open = g >= 0.5
                elif state and g < r.gripper_low:
                    arm.gripper_open = False
                    self._emit(arm, out, frame, side, "close")
                elif not state and g > r.gripper_high:
                    arm.gripper_open = True
                    self._emit(arm, out, frame, side, "open")
            if r.use_reversal:
                z = float(p[2])
                if arm.extreme_z is None:
                    arm.extreme_z, arm.extreme_frame, arm.anchor_z = z, frame, z
                    continue
                if arm.direction == 0:
                    if z <= arm.anchor_z - r.delta:
                        arm.direction, arm.extreme_z, arm.extreme_frame = -1, z, frame
                    elif z >= arm.anchor_z + r.delta:
                        arm.direction, arm.extreme_z, arm.extreme_frame = 1, z, frame
                    continue
                if arm.direction < 0:
                    if z < arm.extreme_z:
                        arm.extreme_z, arm.extreme_frame = z, frame
                    elif z >= arm.extreme_z + r.delta:
                        self._emit(arm, out, arm.extreme_frame, side, "bottom")
                        arm.direction, arm.extreme_z, arm.extreme_frame = 1, z, frame
                else:
                    if z > arm.extreme_z:
                        arm.extreme_z, arm.extreme_frame = z, frame
                    elif z <= arm.extreme_z - r.delta:
                        self._emit(arm, out, arm.extreme_frame, side, "top")
                        arm.direction, arm.extreme_z, arm.extreme_frame = -1, z, frame
        return out


def detect(gripper: np.ndarray, positions: np.ndarray, rule: Optional[EventRule] = None) -> List[dict]:
    """Batch form over a whole episode: gripper [n, 2], positions [n, 2, 3]. Each event also carries `confirmed`,
    the frame at which the streaming detector knows it (== frame for gripper events)."""
    detector = EventDetector(rule or EventRule())
    events = []
    for t in range(len(gripper)):
        for e in detector.step(t, gripper[t], positions[t]):
            e["confirmed"] = t
            events.append(e)
    events.sort(key=lambda e: (e["frame"], e["arm"]))
    return events


def event_frames(events: Sequence[dict], before: int, known_by: Optional[int] = None) -> List[int]:
    """Distinct event frames < before (and confirmed <= known_by, default before - 1), ascending."""
    known_by = before - 1 if known_by is None else known_by
    return sorted({int(e["frame"]) for e in events
                   if int(e["frame"]) < before and int(e.get("confirmed", e["frame"])) <= known_by})


def gripper_columns(joint_vector: np.ndarray) -> np.ndarray:
    """[n, 14] joint vectors (or targets) -> [n, 2] gripper values (columns 6, 13)."""
    joint_vector = np.asarray(joint_vector)
    return joint_vector[:, [6, 13]]


def summarize(events_by_episode: Dict[str, List[dict]]) -> Dict[str, float]:
    counts = [len(v) for v in events_by_episode.values()]
    return {"episodes": len(counts), "events_mean": float(np.mean(counts)) if counts else 0.0,
            "events_min": int(min(counts)) if counts else 0, "events_max": int(max(counts)) if counts else 0}
