"""Inference-time chunk consistency for the closed loop (week plan v4, U1; NumPy only).

BID-lite (backward coherence of Bidirectional Decoding, Liu et al. 2024): at every decision sample N candidate
chunks; when a previous chunk exists, execute the candidate whose start agrees best with the part of the previous
chunk that was predicted but not executed. Distance over the overlapping targets: L2 with arm joints weight 1,
grippers `gripper_weight`, overlap step j weighted rho**j (the first overlapping targets count most).
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

GRIPPERS = (6, 13)


def overlap_distance(previous_frame: int, previous: np.ndarray, frame: int, candidate: np.ndarray, rho: float = 0.5,
                     gripper_weight: float = 0.5) -> Optional[float]:
    """Weighted RMS difference between previous[frame - previous_frame:] and candidate[:overlap].

    previous / candidate: [H, 14] raw targets predicted at previous_frame / frame. None when they do not overlap."""
    previous = np.asarray(previous, dtype=np.float64)
    candidate = np.asarray(candidate, dtype=np.float64)
    shift = int(frame) - int(previous_frame)
    if shift <= 0 or shift >= len(previous):
        return None
    a = previous[shift:]
    b = candidate[:len(a)]
    if len(b) < len(a):
        a = a[:len(b)]
    columns = np.ones(a.shape[1])
    for g in GRIPPERS:
        if g < len(columns):
            columns[g] = gripper_weight
    steps = rho ** np.arange(len(a))
    squared = ((a - b) * columns) ** 2
    return float(np.sqrt((steps[:, None] * squared).sum() / (steps.sum() * a.shape[1])))


def choose(previous_frame: Optional[int], previous: Optional[np.ndarray], frame: int,
           candidates: Sequence[np.ndarray], rho: float = 0.5, gripper_weight: float = 0.5) -> Tuple[int, list]:
    """Index of the most coherent candidate (0 when there is no previous chunk or no overlap) and all distances."""
    if previous is None or previous_frame is None or len(candidates) <= 1:
        return 0, []
    distances = [overlap_distance(previous_frame, previous, frame, c, rho, gripper_weight) for c in candidates]
    if any(d is None for d in distances):
        return 0, []
    return int(np.argmin(distances)), [round(d, 6) for d in distances]
