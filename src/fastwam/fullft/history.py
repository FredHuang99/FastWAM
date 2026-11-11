"""Which past frames the model sees, and at which temporal index (plan v10 D.4 / D.5). Pure Python; the trainer and
the online session call the same `select`.

Variants (frames strictly before the current frame t; the current frame itself is the clip's first frame):
  none   no history (= the released FastWAM fine-tuned, "FastWAM-ft" row)
  ar     anchor (frame 0) + recent frames t - 16, t - 32                                  (G1 base)
  event  anchor + the last `event_max` proprioceptive event frames (events.py)            (the method)
  tw     anchor + every `tw_stride`-th frame (last `tw_max`) + t - 16, t - 32, time index  (time-organised memory)
  clk    no frames; the elapsed step count enters through the proprio token (model.py)    (clock only)
  prop   no frames; the proprio states at the event frames enter through the proprio token (non-visual memory)
  arprop ar frames + the proprioceptive LEDGER (plan v12 C.2): one small token per event (its proprio state, kind,
         arm, rank), the last `event_max` events, written `lag` frames after the event is confirmed; the tokens
         occupy the last `event_max` (zero) padding slots of the text context (model.py), so a zero ledger encoder
         is exactly the ar model
  arev   ar frames + the last `event_max` event FRAMES (known `lag` frames after confirmation)
Index:
  rank   position -1 for the most recent shown frame, -2 for the one before, ... (no time inside the model)
  time   position -(t - frame) / time_unit (time_unit = 16 raw frames = one latent step of the clip)
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

VARIANTS = ("none", "ar", "event", "tw", "clk", "prop", "arprop", "arev")
FRAME_VARIANTS = ("ar", "event", "tw", "arprop", "arev")
LEDGER_KINDS = ("close", "open", "bottom", "top")          # events.py kinds


@dataclass(frozen=True)
class HistoryRule:
    variant: str = "ar"
    index: str = "rank"                       # rank | time
    recent: Tuple[int, ...] = (16, 32)
    event_max: int = 8
    tw_stride: int = 32
    tw_max: int = 12
    time_unit: float = 16.0
    anchor: bool = True
    drop_event_p: float = 0.0                 # training-only augmentation (missed / spurious detections)
    spurious_event_p: float = 0.0
    lag: int = 0                              # frames between an event's confirmation and its use (arprop / arev)

    def __post_init__(self):
        if self.variant not in VARIANTS:
            raise ValueError(f"history variant must be one of {VARIANTS}, got {self.variant!r}")
        if self.index not in ("rank", "time"):
            raise ValueError(f"history index must be rank | time, got {self.index!r}")

    @property
    def max_frames(self) -> int:
        """Fixed slot count K per variant (padding up to it)."""
        if self.variant in ("ar", "arprop"):
            return int(self.anchor) + len(self.recent)
        if self.variant == "arev":
            return int(self.anchor) + len(self.recent) + self.event_max
        if self.variant == "event":
            return int(self.anchor) + self.event_max
        if self.variant == "tw":
            return int(self.anchor) + self.tw_max + len(self.recent)
        return 0

    @property
    def event_slots(self) -> int:
        return self.event_max if self.variant in ("event", "prop", "arprop") else 0


def select(rule: HistoryRule, t: int, events: Sequence[int] = (), rng: Optional[random.Random] = None
           ) -> Tuple[List[int], List[float]]:
    """(frame ids ascending, temporal positions) of the history shown at current frame t.

    events: event frames of this episode known at t (ascending; frames >= t are ignored).
    rng: training augmentation of event detections (None = deterministic, as online)."""
    t = int(t)
    if rule.variant in ("none", "clk", "prop") or t <= 0:
        return [], []
    ids = set()
    if rule.anchor:
        ids.add(0)
    if rule.variant in ("ar", "tw", "arprop", "arev"):
        ids.update(t - r for r in rule.recent if t - r > 0)
    if rule.variant == "tw":
        grid = [f for f in range(rule.tw_stride, t, rule.tw_stride)]
        ids.update(grid[-rule.tw_max:])
    if rule.variant in ("event", "arev"):
        ids.update(augmented_events(rule, t, events, rng)[-rule.event_max:])
    ids = sorted(i for i in ids if 0 <= i < t)
    return ids, positions(rule, t, ids)


def augmented_events(rule: HistoryRule, t: int, events: Sequence[int], rng: Optional[random.Random]) -> List[int]:
    past = sorted({int(e) for e in events if 0 < int(e) < t})
    if rng is None:
        return past
    kept = [e for e in past if rng.random() >= rule.drop_event_p]
    if t > 1 and rng.random() < rule.spurious_event_p:
        kept.append(rng.randrange(1, t))
    return sorted(set(kept))


def positions(rule: HistoryRule, t: int, ids: Sequence[int]) -> List[float]:
    if rule.index == "time":
        return [-(t - i) / rule.time_unit for i in ids]
    n = len(ids)
    return [-(n - j) * 1.0 for j in range(n)]            # ascending ids -> most recent gets -1


def event_states(rule: HistoryRule, t: int, events: Sequence[int]) -> List[int]:
    """prop variant: the frames whose proprio states are shown (last event_max events before t)."""
    return sorted({int(e) for e in events if 0 < int(e) < t})[-rule.event_max:]


def ledger_dim(slots: int) -> int:
    """Features of one ledger token: proprio (14) + kind one-hot (4) + arm one-hot (2) + rank one-hot (slots) + 1."""
    return 14 + len(LEDGER_KINDS) + 2 + int(slots) + 1


def ledger_entries(rule: HistoryRule, t: int, events: Sequence[dict]) -> List[dict]:
    """arprop: the ledger at current frame t = events with frame < t whose entry has been written (confirmed + lag
    <= t), ordered by (frame, arm), the last `event_max` kept. The same function offline and online."""
    known = [e for e in events
             if int(e["frame"]) < t and int(e.get("confirmed", e["frame"])) + int(rule.lag) <= t]
    known.sort(key=lambda e: (int(e["frame"]), int(e["arm"])))
    return known[-rule.event_max:]
