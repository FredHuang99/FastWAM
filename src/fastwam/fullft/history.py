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
  arclk  (11-17, plan v13 E5) ar frames + `event_max` CLOCK tokens: the proprio states of frames sampled uniformly over
         the elapsed time [0, t), each with a sinusoidal code of its frame index (a timestamp); same content as the
         ledger (joint states), same token path (text padding slots), only the index differs (time, not events)
Index:
  rank   position -1 for the most recent shown frame, -2 for the one before, ... (no time inside the model)
  time   position -(t - frame) / time_unit (time_unit = 16 raw frames = one latent step of the clip)
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field, replace
from typing import List, Optional, Sequence, Tuple

VARIANTS = ("none", "ar", "event", "tw", "clk", "prop", "arprop", "arev", "arclk")
FRAME_VARIANTS = ("ar", "event", "tw", "arprop", "arev", "arclk")
CLOCK_CODE = 16                                            # arclk: sinusoidal timestamp dims
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
    # 11-16 (Opus): the event rule's two distance thresholds travel with the model (events.EventRule; the defaults are
    # rule A as frozen in plan v11 N2, so every earlier export keeps exactly its rule). The online session builds its
    # detector from these; the trainer checks that the events file was written with the same values.
    event_delta: float = 0.015
    event_min_path: float = 0.03
    event_provisional: float = 0.0            # 11-19 plan v14 E14: provisional write (events.EventRule.provisional)
    # 11-17 plan v13 E4 (arprop only): each ledger entry also carries its ORDINAL = 1 + the number of earlier written
    # entries of the same arm and kind since the episode start (so the 3rd press of the right arm says 3 even when
    # older entries have left the event_max window), as a thermometer code of this many dims (feature k = 1 if
    # ordinal >= k). 0 = off: features, ledger_dim and every earlier export are exactly as before.
    ordinal: int = 0
    # 11-22 plan v19 3.2 (3) (arprop with ordinal only): the ordinal becomes the IN-PLACE REPEAT COUNT: an entry counts
    # previous + 1 when the arm's joints at its frame are closer than repeat_theta (L2 over that arm's six normalised
    # joints, ARM_JOINTS) to those at the previous entry of the same arm and kind, else 1 (a new place). Same
    # thermometer code, same features otherwise. 0 = off (the ordinal from the episode start, as before).
    repeat_theta: float = 0.0
    # 11-22 plan v19 3.2 (4) record augmentation, TRAINING ONLY (data.Samples with augment; never online; only the
    # ledger changes, never the frames or the target actions). 0 = off (no random number drawn).
    #   ledger_drop_p  per sample, with this probability drop the oldest k entries (k uniform in 1..all but the last
    #                  ledger_keep); the kept entries keep their counts
    #   ledger_over_p  per sample whose latest entry ENDS its in-place run in the demo (the next demo event of the same
    #                  arm and kind is at another place, or there is none), with this probability add 1..ledger_over_max
    #                  more copies of the latest in-place cycle (the arm's entries since its previous entry of the same
    #                  kind), each copy's count + j: "one or two more presses recorded"; needs repeat_theta
    ledger_drop_p: float = 0.0
    ledger_keep: int = 4
    ledger_over_p: float = 0.0
    ledger_over_max: int = 2
    # 11-22 plan v19 3.3 (A3, observe_and_pickup): two ZOOM history frames on top of the variant's frames: the head
    # camera of frame 0 cropped to zoom_ref_box (where the reference object is shown) and the head camera of the current
    # frame cropped to zoom_cur_box (the table's candidates), each resized back to the camera's size and encoded like
    # any frame (fullft/zoom.py; the same function offline and online). Boxes are fixed, normalised (x0, y0, x1, y1).
    # Positions (zoom_positions): the reference crop one step older than the oldest shown frame, the current crop at
    # 0. False = off: max_frames, selection and every earlier export are exactly as before.
    zoom: bool = False
    zoom_ref_box: Tuple[float, ...] = (0.0, 0.0, 1.0, 1.0)
    zoom_cur_box: Tuple[float, ...] = (0.0, 0.0, 1.0, 1.0)
    zoom_camera: int = 0
    zoom_match: bool = False                  # 11-24 plan v20 card 7: the reference zoom frame = the MATCH frame
                                              # (fullft/match.py: frame 0's table crop, candidates brightened by their
                                              # similarity to the reference); needs zoom; its own zoom cache

    def __post_init__(self):
        if self.variant not in VARIANTS:
            raise ValueError(f"history variant must be one of {VARIANTS}, got {self.variant!r}")
        if not 0 <= int(self.ordinal) <= 64:
            raise ValueError(f"history ordinal (thermometer dims) must be 0..64, got {self.ordinal}")
        if int(self.ordinal) and self.variant != "arprop":
            raise ValueError("history ordinal is a ledger feature: only with variant arprop")
        if float(self.repeat_theta) < 0.0:
            raise ValueError(f"history repeat_theta must be >= 0, got {self.repeat_theta}")
        if float(self.repeat_theta) > 0.0 and not int(self.ordinal):
            raise ValueError("history repeat_theta replaces the ordinal's count: it needs history.ordinal > 0")
        if not (0.0 <= float(self.ledger_drop_p) <= 1.0 and 0.0 <= float(self.ledger_over_p) <= 1.0):
            raise ValueError(f"ledger_drop_p / ledger_over_p must be in [0, 1], got {self.ledger_drop_p}, "
                             f"{self.ledger_over_p}")
        if int(self.ledger_keep) < 0 or int(self.ledger_over_max) < 1:
            raise ValueError(f"ledger_keep must be >= 0 and ledger_over_max >= 1, got {self.ledger_keep}, "
                             f"{self.ledger_over_max}")
        if (float(self.ledger_drop_p) > 0.0 or float(self.ledger_over_p) > 0.0) and self.variant != "arprop":
            raise ValueError("ledger augmentation needs variant arprop")
        if float(self.ledger_over_p) > 0.0 and not float(self.repeat_theta) > 0.0:
            raise ValueError("ledger_over_p marks the end of an in-place run: it needs history.repeat_theta > 0")
        if self.zoom:
            if self.variant not in FRAME_VARIANTS:
                raise ValueError(f"history zoom adds history frames: only with {FRAME_VARIANTS}, got {self.variant!r}")
            for box in (self.zoom_ref_box, self.zoom_cur_box):
                b = [float(x) for x in box]
                if len(b) != 4 or not (0.0 <= b[0] < b[2] <= 1.0 and 0.0 <= b[1] < b[3] <= 1.0):
                    raise ValueError(f"zoom box must be (x0, y0, x1, y1) with 0 <= x0 < x1 <= 1, 0 <= y0 < y1 <= 1: {box}")
            if int(self.zoom_camera) not in (0, 1, 2):
                raise ValueError(f"zoom_camera must be 0 (head), 1 or 2, got {self.zoom_camera}")
        if self.zoom_match and not self.zoom:
            raise ValueError("history.zoom_match replaces the reference zoom frame: it needs history.zoom=true")
        if not (0.0 <= float(self.event_provisional) < float(self.event_delta)):
            raise ValueError(f"event_provisional must be in [0, event_delta), got {self.event_provisional}")
        if not (0.0 < float(self.event_delta) <= 0.1 and 0.0 <= float(self.event_min_path) <= 0.2):
            raise ValueError(f"event thresholds out of range: delta {self.event_delta}, min_path {self.event_min_path}")
        if self.index not in ("rank", "time"):
            raise ValueError(f"history index must be rank | time, got {self.index!r}")

    @property
    def max_frames(self) -> int:
        """Fixed slot count K per variant (padding up to it); + 2 zoom frames when zoom is on."""
        return self._frames() + (2 if self.zoom else 0)

    def _frames(self) -> int:
        if self.variant in ("ar", "arprop", "arclk"):
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
        return self.event_max if self.variant in ("event", "prop", "arprop", "arclk") else 0

    @property
    def ledger_features(self) -> int:
        """Input width of the ledger encoder (0 when the variant has no ledger)."""
        if self.variant == "arclk":
            return clock_dim()
        return ledger_dim(self.event_max, self.ordinal) if self.variant == "arprop" else 0


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
    if rule.variant in ("ar", "tw", "arprop", "arev", "arclk"):
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


def zoom_positions(rule: HistoryRule, t: int, n_shown: int) -> Tuple[float, float]:
    """Plan v19 3.3: temporal positions of the two zoom frames when n_shown ordinary frames are shown at frame t.
    rank: the reference crop (of frame 0) one step older than the oldest shown frame, -(n + 1); time: frame 0's own
    position, -t / time_unit. The current crop: 0 (the current frame's temporal index) in both."""
    if rule.index == "time":
        return -float(t) / rule.time_unit, 0.0
    return -float(n_shown + 1), 0.0


def event_states(rule: HistoryRule, t: int, events: Sequence[int]) -> List[int]:
    """prop variant: the frames whose proprio states are shown (last event_max events before t)."""
    return sorted({int(e) for e in events if 0 < int(e) < t})[-rule.event_max:]


def ledger_dim(slots: int, ordinal: int = 0) -> int:
    """Features of one ledger token: proprio (14) + kind one-hot (4) + arm one-hot (2) + rank one-hot (slots) + 1
    (valid flag) [+ ordinal thermometer (ordinal dims), 11-17 E4]. Rank 0 = the most recent entry."""
    return 14 + len(LEDGER_KINDS) + 2 + int(slots) + 1 + int(ordinal)


def clock_dim() -> int:
    """Features of one arclk token: proprio (14) + timestamp code (CLOCK_CODE) + 1 (valid flag)."""
    return 14 + CLOCK_CODE + 1


def clock_frames(rule: HistoryRule, t: int) -> List[int]:
    """arclk: min(event_max, t) frames spread uniformly over the elapsed time [0, t) (0 and t - 1 included); [] at t <= 0.
    They move as t grows (the memory is indexed by time), unlike ledger entries."""
    t = int(t)
    if t <= 0:
        return []
    n = min(int(rule.event_max), t)
    if n == 1:
        return [0]
    return sorted({int(round(i * (t - 1) / (n - 1))) for i in range(n)})


def clock_code(frame: float, dims: int = CLOCK_CODE) -> List[float]:
    """Sinusoidal timestamp of a frame index: [sin(f w_k), cos(f w_k)], w_k = 10000^(-k / (dims / 2))."""
    import math
    half = dims // 2
    out = []
    for k in range(half):
        w = 10000.0 ** (-k / half)
        out += [math.sin(float(frame) * w), math.cos(float(frame) * w)]
    return out


def ordinal_code(n: int, dims: int) -> List[float]:
    """Thermometer code of an ordinal n >= 1: feature k (k = 1..dims) is 1 if n >= k (saturates at dims)."""
    return [1.0 if int(n) >= k else 0.0 for k in range(1, int(dims) + 1)]


def with_ordinals(entries: Sequence[dict]) -> List[dict]:
    """Copies of the (ascending) entries, each with 'ordinal' = 1 + the number of earlier entries of the same arm and
    kind in this list. Called on the full written list since the episode start (before the event_max cut)."""
    seen: dict = {}
    out = []
    for e in entries:
        key = (int(e["arm"]), e["kind"])
        seen[key] = seen.get(key, 0) + 1
        out.append(dict(e, ordinal=seen[key]))
    return out


ARM_JOINTS = ((0, 1, 2, 3, 4, 5), (7, 8, 9, 10, 11, 12))   # the six joints of each arm in the 14-d proprio (6, 13 = grippers)


def arm_joints(proprio, arm: int) -> List[float]:
    return [float(proprio[i]) for i in ARM_JOINTS[int(arm)]]


def joint_distance(a: Sequence[float], b: Sequence[float]) -> float:
    return math.sqrt(sum((float(x) - float(y)) ** 2 for x, y in zip(a, b)))


def with_repeats(entries: Sequence[dict], proprio_of, theta: float) -> List[dict]:
    """Plan v19 3.2 (3): copies of the (ascending) entries, each with 'ordinal' = its IN-PLACE REPEAT COUNT: previous
    count + 1 if the arm's joints at its frame (proprio_of(frame), normalised) are within theta of those at the
    previous entry of the same arm and kind, else 1. Called on the full written list (before the event_max cut)."""
    last: dict = {}
    out = []
    for e in entries:
        key = (int(e["arm"]), e["kind"])
        q = arm_joints(proprio_of(int(e["frame"])), int(e["arm"]))
        prev = last.get(key)
        n = prev[1] + 1 if prev is not None and joint_distance(q, prev[0]) < float(theta) else 1
        last[key] = (q, n)
        out.append(dict(e, ordinal=n))
    return out


def ledger_entries(rule: HistoryRule, t: int, events: Sequence[dict], proprio_of=None) -> List[dict]:
    """arprop: the ledger at current frame t = events with frame < t whose entry has been written (confirmed + lag
    <= t), ordered by (frame, arm), the last `event_max` kept. The same function offline and online.
    With rule.ordinal the entries are copies carrying their ordinal, counted over ALL written entries: from the
    episode start, or (rule.repeat_theta > 0, plan v19 3.2 (3)) the in-place repeat count, which needs proprio_of
    (frame -> normalised 14-d proprio; ignored otherwise)."""
    known = [e for e in events
             if int(e["frame"]) < t and int(e.get("confirmed", e["frame"])) + int(rule.lag) <= t]
    known.sort(key=lambda e: (int(e["frame"]), int(e["arm"])))
    if int(rule.ordinal):
        if float(rule.repeat_theta) > 0.0:
            if proprio_of is None:
                raise ValueError("history repeat_theta: ledger_entries needs proprio_of")
            known = with_repeats(known, proprio_of, rule.repeat_theta)
        else:
            known = with_ordinals(known)
    return known[-rule.event_max:]


def run_ended(latest: dict, events: Sequence[dict], proprio_of, theta: float) -> bool:
    """Plan v19 3.2 (4b): does the entry end its in-place run in the demo? True if the demo's next event of the same
    arm and kind after it is at another place (joints >= theta apart) or there is none. `events` = all the demo's
    events (future ones included: a mechanical mark from the demo, training only)."""
    arm, kind, frame = int(latest["arm"]), latest["kind"], int(latest["frame"])
    later = [e for e in events if int(e["arm"]) == arm and e["kind"] == kind and int(e["frame"]) > frame]
    if not later:
        return True
    nxt = min(later, key=lambda e: int(e["frame"]))
    return joint_distance(arm_joints(proprio_of(frame), arm), arm_joints(proprio_of(int(nxt["frame"])), arm)) >= float(theta)


def last_cycle(full: Sequence[dict]) -> List[dict]:
    """The latest entry's in-place cycle: the entries of its arm after the arm's previous entry of the same kind
    (all of the arm's entries when there is none), ending with it. Press: [bottom, top] of the last press."""
    latest = full[-1]
    arm, kind = int(latest["arm"]), latest["kind"]
    mine = [e for e in full[:-1] if int(e["arm"]) == arm]
    prev = max((j for j, e in enumerate(mine) if e["kind"] == kind), default=-1)
    return mine[prev + 1:] + [latest]


def augment_ledger(rule: HistoryRule, t: int, events: Sequence[dict], entries: List[dict], proprio_of,
                   rng: random.Random) -> List[dict]:
    """Plan v19 3.2 (4), training only: the ledger `entries` (= ledger_entries(rule, t, events, proprio_of)) after
    (b) over-count then (a) drop-old; a random number is drawn only for a part whose probability is > 0."""
    out = list(entries)
    if float(rule.ledger_over_p) > 0.0 and out:
        if rng.random() < float(rule.ledger_over_p):
            full = ledger_entries(replace(rule, event_max=10 ** 6), t, events, proprio_of)
            k = rng.randint(1, int(rule.ledger_over_max))
            if run_ended(full[-1], events, proprio_of, rule.repeat_theta):
                cycle = last_cycle(full)
                extra = [dict(e, ordinal=int(e["ordinal"]) + j, augmented=True) for j in range(1, k + 1) for e in cycle]
                out = (full + extra)[-int(rule.event_max):]
    if float(rule.ledger_drop_p) > 0.0 and len(out) > int(rule.ledger_keep):
        if rng.random() < float(rule.ledger_drop_p):
            k = rng.randint(1, len(out) - int(rule.ledger_keep))
            out = out[k:]
    return out


PRESS_KINDS = ("bottom", "top")


def ordinal_counterfactual(entries: List[dict], mode: str) -> List[dict]:
    """11-17 plan v13 E4 test-time counterfactuals for a model trained with history.ordinal, applied to the full list
    of written entries (ledger_entries with no cap), before the event_max cut:
      ordplus1  the ordinal of every press entry ('bottom' / 'top') + 1; the NUMBER of entries is unchanged
      duppress  the most recent completed press (a 'bottom' and the next 'top' of the same arm) is entered twice, the
                copies keeping their ordinals; one press more by the number of entries, the code unchanged
    Before the first press completes, duppress changes nothing."""
    if mode == "ordplus1":
        if any("ordinal" not in e for e in entries):
            raise ValueError("ordplus1 needs a model trained with history.ordinal (entries carry no ordinal)")
        return [dict(e, ordinal=int(e["ordinal"]) + 1) if e["kind"] in PRESS_KINDS else e for e in entries]
    if mode == "duppress":
        for t in range(len(entries) - 1, -1, -1):
            if entries[t]["kind"] != "top":
                continue
            arm = int(entries[t]["arm"])
            b = next((i for i in range(t - 1, -1, -1)
                      if int(entries[i]["arm"]) == arm and entries[i]["kind"] in PRESS_KINDS), None)
            if b is not None and entries[b]["kind"] == "bottom":
                out = list(entries)
                out[t + 1:t + 1] = [dict(entries[b]), dict(entries[t])]
                return out
        return entries
    raise ValueError(f"unknown ordinal counterfactual {mode!r} (ordplus1 | duppress)")
