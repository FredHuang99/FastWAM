"""History selection (pure Python) and the online append-only archive.

`select_history` is the single source of truth for which past observations a
decision may read. It is used unchanged by the offline dense-cache sampler and
by the online archive, so training and deployment see identical histories
whenever the set of available ids is identical.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .config import (HistoryPolicyConfig, ROLE_ANCHOR, ROLE_CURRENT, ROLE_LANDMARK,
                     ROLE_RECENT)


@dataclass(frozen=True)
class HistorySelection:
    ids: Tuple[int, ...]       # ascending observation ids, all <= current
    roles: Tuple[int, ...]     # ROLE_* per id (anchor > recent > landmark priority)
    current: int

    def __len__(self) -> int:
        return len(self.ids)


def _validate_available(available: Iterable[int], current: int) -> List[int]:
    ids = [int(i) for i in available]
    if any(i < 0 for i in ids) or ids != sorted(set(ids)):
        raise ValueError("Available ids must be unique, increasing and non-negative.")
    if not isinstance(current, int) or current < 0:
        raise ValueError("current must be a non-negative int.")
    if current not in ids:
        raise ValueError(f"The current observation {current} is not in the available ids.")
    return [i for i in ids if i <= current]


def _uniform_subset(values: Sequence[int], count: int) -> List[int]:
    """Deterministic, order-preserving uniform thinning that keeps both ends."""
    values = list(values)
    if count >= len(values):
        return values
    if count <= 0:
        return []
    if count == 1:
        return [values[-1]]
    step = (len(values) - 1) / (count - 1)
    chosen = sorted({values[round(k * step)] for k in range(count)})
    # Rounding collisions can only shrink the set; top it up deterministically from the end.
    rest = [v for v in reversed(values) if v not in chosen]
    while len(chosen) < count and rest:
        chosen.append(rest.pop(0))
    return sorted(chosen)


def select_history(available: Iterable[int], current: int, policy: HistoryPolicyConfig) -> HistorySelection:
    """Choose the observations visible at decision `current`.

    Never returns an id greater than `current`. Anchors and the recent window are
    always kept; fixed-stride landmarks are thinned uniformly to respect
    `max_frames`.
    """
    past = _validate_available(available, current)
    before = [i for i in past if i < current]
    roles: Dict[int, int] = {}
    for i in before[:policy.anchor_frames]:
        roles[i] = ROLE_ANCHOR
    for k in range(1, policy.recent_frames + 1):
        target = current - k * policy.recent_stride
        candidates = [i for i in before if i <= target]
        if candidates and candidates[-1] not in roles:
            roles[candidates[-1]] = ROLE_RECENT
    landmarks = [i for i in before if i % policy.landmark_stride == 0 and i not in roles]
    budget = policy.max_frames - len(roles) - int(policy.include_current)
    for i in _uniform_subset(landmarks, max(0, budget)):
        roles[i] = ROLE_LANDMARK
    if policy.include_current:
        roles[current] = ROLE_CURRENT
    ids = tuple(sorted(roles))
    return HistorySelection(ids=ids, roles=tuple(roles[i] for i in ids), current=current)


class EpisodeArchive:
    """Append-only per-environment-slot store of frozen observation features.

    Stores whatever feature object the caller provides (normally a CPU BF16
    tensor [P, C]). Writes are idempotent per frame id; a different payload for an
    existing id is rejected. Reads never mutate the store. A reset clears the slot.
    """

    def __init__(self, policy: HistoryPolicyConfig):
        self.policy = policy
        self._slots: Dict[Any, Dict[str, Any]] = {}

    def reset(self, slot: Any, episode_key: str, signature: str) -> None:
        self._slots[slot] = {"episode": str(episode_key), "signature": str(signature), "frames": {}}

    def _slot(self, slot: Any) -> Dict[str, Any]:
        if slot not in self._slots:
            raise KeyError(f"Archive slot {slot!r} was not reset for an episode.")
        return self._slots[slot]

    def append(self, slot: Any, frame_id: int, feature: Any, signature: str) -> bool:
        record = self._slot(slot)
        if signature != record["signature"]:
            raise ValueError("Feature encoder signature changed inside an episode.")
        frame_id = int(frame_id)
        frames = record["frames"]
        if frames and frame_id < max(frames) and frame_id not in frames:
            raise ValueError("Observations must be appended in non-decreasing order.")
        if frame_id in frames:
            if frames[frame_id] is not feature:
                same = _same_payload(frames[frame_id], feature)
                if not same:
                    raise ValueError(f"Frame {frame_id} re-written with a different payload.")
            return False
        frames[frame_id] = feature
        return True

    def ids(self, slot: Any) -> List[int]:
        return sorted(self._slot(slot)["frames"])

    def episode(self, slot: Any) -> str:
        return self._slot(slot)["episode"]

    def select(self, slot: Any, current: int) -> Tuple[HistorySelection, List[Any]]:
        frames = self._slot(slot)["frames"]
        selection = select_history(sorted(frames), current, self.policy)
        return selection, [frames[i] for i in selection.ids]

    def __len__(self) -> int:
        return len(self._slots)


def _same_payload(a: Any, b: Any) -> bool:
    try:
        import torch
        if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
            return a.shape == b.shape and a.dtype == b.dtype and bool(torch.equal(a, b))
    except ImportError:  # pragma: no cover - torch is always present in training environments
        pass
    return a == b


def collate_history(features: Sequence[Sequence[Any]], selections: Sequence[HistorySelection],
                    tokens_per_frame: int, width: int, dtype=None, device=None) -> Dict[str, Any]:
    """Pad per-sample feature lists to [B, Nmax, P, C] with validity masks.

    Samples with an empty selection keep one fully-masked padding frame so the
    tensor shapes stay rectangular; the null memory tokens keep attention defined.
    """
    import torch

    if len(features) != len(selections):
        raise ValueError("features and selections must align.")
    batch = len(selections)
    longest = max([len(s) for s in selections] + [1])
    dtype = dtype or torch.bfloat16
    history = torch.zeros(batch, longest, tokens_per_frame, width, dtype=dtype)
    frame_ids = torch.zeros(batch, longest, dtype=torch.long)
    roles = torch.zeros(batch, longest, dtype=torch.long)
    valid = torch.zeros(batch, longest, dtype=torch.bool)
    current = torch.zeros(batch, dtype=torch.long)
    for b, (feats, selection) in enumerate(zip(features, selections)):
        if len(feats) != len(selection):
            raise ValueError("A selection and its features have different lengths.")
        current[b] = selection.current
        for j, (feature, frame_id, role) in enumerate(zip(feats, selection.ids, selection.roles)):
            feature = torch.as_tensor(feature)
            if tuple(feature.shape) != (tokens_per_frame, width):
                raise ValueError(f"Feature shape {tuple(feature.shape)} != {(tokens_per_frame, width)}.")
            history[b, j] = feature.to(dtype)
            frame_ids[b, j] = frame_id
            roles[b, j] = role
            valid[b, j] = True
    out = {"history": history, "frame_ids": frame_ids, "roles": roles, "history_valid": valid,
           "current_ids": current}
    if device is not None:
        out = {k: v.to(device) for k, v in out.items()}
    return out
