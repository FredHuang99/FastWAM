"""Training samples from the dense per-episode caches (the format of the two-task dense output and of
scripts/memory_v2/press/build_dense.py): <root>/RECORDS.json and <root>/cache/<task>_<episode>/encodings.pt with
  latent        [L, 48, 1, 24, 20]  single-frame VAE latent of every frame (= the clip's first latent frame)
  video_latent  [L, 48, 3, 24, 20]  the clip latent of every anchor: frames a, a+4, ..., a+32 (padded at the end)
  video_valid   [L, 9] or [L, 3]    which clip frames are real (or padding; the polarity is detected, see below)
  text, text_valid, proprio [L, 14] (normalised), actions [L, 14] (normalised next-record targets)
Nothing here writes to a cache. The memory_v2 identity binding (Codex's code under /restore-tmp) is not needed:
the files are only read; each listed episode must have its COMPLETE.json marker.
"""
from __future__ import annotations

import json
import random
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import torch

from .events import event_frames
from .history import (LEDGER_KINDS, HistoryRule, augment_ledger, clock_code, clock_dim, clock_frames, event_states,
                      ledger_dim, ledger_entries, ordinal_code, select, zoom_positions)

HORIZON = 32


def action_window(actions: torch.Tensor, anchor: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Same as memory_v2.dense.action_window: hold the last target past the episode end, mask it."""
    n = len(actions)
    index = torch.clamp(torch.arange(anchor, anchor + HORIZON), max=n - 1)
    valid = torch.arange(anchor, anchor + HORIZON) < n
    return actions[index], valid


def load_text_table(path: str, episode_ids: Sequence[str]) -> Dict[str, torch.Tensor]:
    """11-24 plan v20 card 5: {episode_id: text [L, D]} from a text table (scripts/fullft/press_told_text.py). Every
    episode of `episode_ids` must have an entry (else an error: no silent fall-back to the cache's own text)."""
    table = torch.load(path, map_location="cpu", weights_only=True)
    missing = [e for e in episode_ids if e not in table["episodes"]]
    if missing:
        raise ValueError(f"text table {path} lacks {len(missing)} episodes, e.g. {missing[:3]}")
    return {e: table["by_instruction"][table["episodes"][e]]["text"] for e in episode_ids}


class DenseEpisodes:
    def __init__(self, roots: Sequence[str], tasks: Sequence[str], capacity: int = 16, check: bool = True):
        self.records: List[dict] = []
        for root in roots:
            rows = json.loads((Path(root) / "RECORDS.json").read_text(encoding="utf-8"))
            for r in rows:
                if r["task"] in tasks:
                    self.records.append({**r, "_root": str(root)})
        missing = sorted(set(tasks) - {r["task"] for r in self.records})
        if missing:
            raise ValueError(f"No dense records for tasks {missing} under {list(roots)}")
        self.index = {r["episode_id"]: k for k, r in enumerate(self.records)}
        if len(self.index) != len(self.records):
            raise ValueError("The same episode id appears in two dense roots.")
        if check:
            for r in self.records:
                if not (self.folder(r) / "COMPLETE.json").is_file():
                    raise FileNotFoundError(f"{r['episode_id']}: no COMPLETE.json under {self.folder(r)}")
        self.capacity = capacity
        self._open: "OrderedDict[str, dict]" = OrderedDict()

    @staticmethod
    def folder(record: dict) -> Path:
        return Path(record["_root"]) / "cache" / record["episode_id"].replace("/", "_")

    def __call__(self, episode_id: str) -> dict:
        if episode_id not in self._open:
            path = self.folder(self.records[self.index[episode_id]]) / "encodings.pt"
            self._open[episode_id] = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
            while len(self._open) > self.capacity:
                self._open.popitem(last=False)
        self._open.move_to_end(episode_id)
        return self._open[episode_id]

    def split(self, name: str) -> List[dict]:
        return [r for r in self.records if r.get("split") == name]


def video_polarity(episodes: DenseEpisodes) -> str:
    """'valid' if video_valid marks real frames, 'pad' if it marks padding: frame 0 of a long episode is real."""
    for r in episodes.records:
        if int(r["length"]) > 40:
            m = episodes(r["episode_id"])["video_valid"][0].bool()
            if bool(m.all()):
                return "valid"
            if not bool(m.any()):
                return "pad"
            raise ValueError(f"video_valid of anchor 0 of {r['episode_id']} is mixed: {m.tolist()}")
    raise ValueError("No episode longer than 40 frames to read the video_valid polarity from.")


def latent_valid(mask: torch.Tensor, polarity: str) -> torch.Tensor:
    """[9] raw-frame or [3] latent-frame mask -> [3] bool: is this latent frame real (it is padding only when all
    its raw frames are padding, as FastWAM._compute_video_loss_per_sample does)."""
    real = mask.bool() if polarity == "valid" else ~mask.bool()
    if real.numel() == 3:
        return real
    if real.numel() != 9:
        raise ValueError(f"video_valid has {real.numel()} entries; expected 9 raw frames or 3 latent frames")
    return torch.stack([real[0], real[1:5].any(), real[5:9].any()])


def ledger_tensor(rule: HistoryRule, entries: Sequence[dict], proprio_of,
                  proprio_dim: int = 14) -> Tuple[torch.Tensor, torch.Tensor]:
    """(features [event_max, ledger_dim], valid [event_max]) of ledger entries (ascending); proprio_of(frame) ->
    normalised proprio [proprio_dim] (14 RoboTwin; 11-28: 8 for the LIBERO base / RoboMME, the other features shift by
    proprio_dim - 14; 14 = exactly as before). Slot j holds entry j; rank 0 = the most recent entry."""
    slots = rule.event_max
    dims = int(rule.ordinal)
    p = int(proprio_dim)
    feat = torch.zeros(slots, ledger_dim(slots, dims, p))
    valid = torch.zeros(slots, dtype=torch.bool)
    kind0, arm0, rank0 = p, p + len(LEDGER_KINDS), p + len(LEDGER_KINDS) + 2
    flag = rank0 + slots                                # the valid flag (= the last feature when dims == 0)
    n = len(entries)
    for j, e in enumerate(entries):
        feat[j, :p] = proprio_of(int(e["frame"])).float()
        feat[j, kind0 + LEDGER_KINDS.index(e["kind"])] = 1.0
        feat[j, arm0 + int(e["arm"])] = 1.0
        feat[j, rank0 + (n - 1 - j)] = 1.0
        feat[j, flag] = 1.0
        if dims:                                        # 11-17 E4: KeyError if an entry carries no ordinal
            feat[j, flag + 1:flag + 1 + dims] = torch.tensor(ordinal_code(int(e["ordinal"]), dims))
        valid[j] = True
    return feat, valid


NEXT_EVENT_CLASSES = 2 * len(LEDGER_KINDS) + 1          # plan v19 3.2 (2): 4 kinds x 2 arms + "no event left"


def decision_weight(events: Sequence[dict], anchor: int, weight: float, window: int,
                    kinds: Sequence[str] = ("open", "bottom"), pre: int = 0,
                    pre_kinds: Sequence[str] = ("close",)) -> float:
    """Plan v19 3.2 (1): `weight` if the anchor lies within `window` frames from the confirmation of a completion
    event (kind in `kinds`; confirmed <= anchor < confirmed + window), else 1.0. An event without 'confirmed' counts
    as confirmed at its frame (gripper events).
    11-23 (1b): with pre > 0 also `weight` when the anchor lies in the `pre` frames before an event of `pre_kinds`
    (frame - pre <= anchor < frame; the reach to the object the gripper then closes on)."""
    a = int(anchor)
    for e in events:
        if e.get("kind") in kinds:
            c = int(e.get("confirmed", e["frame"]))
            if c <= a < c + int(window):
                return float(weight)
        if int(pre) > 0 and e.get("kind") in pre_kinds:
            f = int(e["frame"])
            if f - int(pre) <= a < f:
                return float(weight)
    return 1.0


def next_event_label(events: Sequence[dict], anchor: int) -> int:
    """Plan v19 3.2 (2): class of the demo's first body event at or after the anchor (frame >= anchor; same frame:
    arm 0 first) = kind index (history.LEDGER_KINDS) * 2 + arm, or NEXT_EVENT_CLASSES - 1 when no event is left."""
    later = [e for e in events if int(e["frame"]) >= int(anchor)]
    if not later:
        return NEXT_EVENT_CLASSES - 1
    e = min(later, key=lambda x: (int(x["frame"]), int(x["arm"])))
    return LEDGER_KINDS.index(e["kind"]) * 2 + int(e["arm"])


def next_pose_target(events: Sequence[dict], anchor: int, proprio: torch.Tensor,
                     kinds: Sequence[str] = ("close",)) -> Tuple[torch.Tensor, bool]:
    """11-23 (2b): (target [14], valid). The demo's first event of `kinds` at or after the anchor (frame >= anchor;
    same frame: arm 0 first); target = proprio[that frame] - proprio[anchor] (normalised proprio, both arms). No such
    event left: zeros, False."""
    a = int(anchor)
    later = [e for e in events if e.get("kind") in kinds and int(e["frame"]) >= a]
    if not later:
        return torch.zeros(int(proprio.shape[-1])), False
    e = min(later, key=lambda x: (int(x["frame"]), int(x["arm"])))
    f = min(int(e["frame"]), int(proprio.shape[0]) - 1)
    return (proprio[f].float() - proprio[a].float()), True


CLOCK_MODES = ("", "off", "freeze", "flat")


def clock_tensor(rule: HistoryRule, frames: Sequence[int], proprio_of, scale: float = 1.0, mode: str = "",
                 current: Optional[int] = None, proprio_dim: int = 14) -> Tuple[torch.Tensor, torch.Tensor]:
    """arclk (plan v13 E5): (features [event_max, clock_dim], valid [event_max]) of the sampled frames (ascending);
    proprio_of(frame) -> normalised proprio [14]; scale multiplies the frame index inside the timestamp code only
    (test-time timestamp scaling, 1.0 = as trained).
    mode (11-19 plan v15 E21, test time only; "" = as trained):
      off     no clock token (all slots invalid, zero features): what the model sees at the episode start
      freeze  every token's joint state = the CURRENT frame's (`current`); the timestamps stay those of the samples
      flat    every token's timestamp code = the code of the middle sample; the joint states stay"""
    if mode not in CLOCK_MODES:
        raise ValueError(f"clock mode must be one of {CLOCK_MODES}, got {mode!r}")
    if mode == "freeze" and current is None:
        raise ValueError("clock mode 'freeze' needs the current frame")
    slots = rule.event_max
    p = int(proprio_dim)                                # 11-28: the base's proprio width (14 = as before)
    feat = torch.zeros(slots, clock_dim(p))
    valid = torch.zeros(slots, dtype=torch.bool)
    shown = [] if mode == "off" else [int(f) for f in list(frames)[-slots:]]
    middle = shown[len(shown) // 2] if shown else 0
    for j, f in enumerate(shown):
        feat[j, :p] = proprio_of(int(current) if mode == "freeze" else f).float()
        feat[j, p:-1] = torch.tensor(clock_code(float(middle if mode == "flat" else f) * scale))
        feat[j, -1] = 1.0
        valid[j] = True
    return feat, valid


def check_ledger_slots(text: torch.Tensor, slots: int, where: str = "") -> None:
    """The ledger writes into the last `slots` text positions: they must be padding (exact zeros)."""
    if text.shape[-2] < slots or bool(text[..., -slots:, :].abs().sum() != 0):
        raise ValueError(f"the last {slots} text positions are not padding {where}: the instruction is too long for "
                         "the ledger (shorten event_max)")


def match_events(episode_ids: Sequence[str], events: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
    """Event lists keyed by the dense episode ids. The event files key demos as <task>/<hdf5 stem>; a dense root that
    names episodes differently (e.g. <task>/episode_0000007 for episode7.hdf5) is matched by (task, episode number)
    when that mapping is one-to-one and covers every unmatched id; otherwise the unmatched ids stay absent."""
    import re
    out = {e: events[e] for e in episode_ids if e in events}
    missing = [e for e in episode_ids if e not in events]
    if not missing:
        return out

    def key(name):
        task, _, stem = name.partition("/")
        digits = re.findall(r"\d+", stem)
        return (task, int(digits[-1])) if digits else None
    index = {}
    for name in events:
        k = key(name)
        if k is not None:
            index.setdefault(k, []).append(name)
    mapped = {e: index.get(key(e), []) for e in missing}
    if all(len(v) == 1 for v in mapped.values()) and len({v[0] for v in mapped.values()}) == len(mapped):
        out.update({e: events[v[0]] for e, v in mapped.items()})
    return out


def load_events(paths: Sequence[str], rule: Optional[HistoryRule] = None) -> Dict[str, List[dict]]:
    """Merge events_<task>.json files. With `rule` (11-16): every file must have been written with the model's event
    thresholds (rule.event_delta / event_min_path; a file without a "rule" field counts as rule A)."""
    from .events import parse_rule
    out: Dict[str, List[dict]] = {}
    for p in paths:
        value = json.loads(Path(p).read_text(encoding="utf-8"))
        if rule is not None:
            got = parse_rule(value.get("rule", "") if isinstance(value, dict) else "")
            want = {"delta": float(rule.event_delta), "min_path": float(rule.event_min_path)}
            if any(abs(got[k] - want[k]) > 1e-9 for k in want):
                raise ValueError(f"events file {p} was written with {got}, the model's history rule says {want}")
        out.update(value["episodes"] if "episodes" in value else value)
    return out


class Samples(torch.utils.data.Dataset):
    """Item i -> one training sample (episode, anchor) of the given list; history per the rule."""

    def __init__(self, episodes: DenseEpisodes, items: Sequence[Tuple[str, int]], rule: HistoryRule,
                 events: Dict[str, List[dict]], polarity: str, augment: bool = False, seed: int = 0,
                 decision: Optional[tuple] = None, next_event: bool = False,
                 zoom_root: str = "", next_pose: Optional[Sequence[str]] = None, text_table: str = ""):
        """decision = (weight, window, kinds[, pre, pre_kinds]) adds 'loss_weight' to every sample (plan v19 3.2 (1);
        the pre-event window 11-23 (1b)); next_event adds the 'next_event' class (3.2 (2)); next_pose = event kinds
        adds 'next_pose' [14] and 'next_pose_valid' (11-23 (2b)). All off (default): the samples are exactly as
        before."""
        self.episodes, self.items, self.rule = episodes, list(items), rule
        self.events, self.polarity, self.augment, self.seed = events, polarity, augment, seed
        self.decision, self.next_event = decision, bool(next_event)
        self.next_pose = tuple(next_pose) if next_pose else None
        self.zoom_root = str(zoom_root or "")
        self._zoom: "OrderedDict[str, dict]" = OrderedDict()
        self.text_override = load_text_table(text_table, sorted({e for e, _ in items})) if text_table else {}
        if rule.zoom and not self.zoom_root:
            raise ValueError("history zoom needs data.zoom_root (the folder written by scripts/fullft/build_zoom.py)")
        self.epoch = 0
        self.checked_text: set = set()
        if (rule.variant in ("event", "prop", "arprop", "arev") or decision is not None or self.next_event
                or self.next_pose is not None):
            self.events = events = match_events(sorted({e for e, _ in self.items}), events)
            absent = sorted({e for e, _ in self.items if e not in events})
            if absent:
                what = (f"history '{rule.variant}'" if rule.variant in ("event", "prop", "arprop", "arev")
                        else "decision weighting / the next-event or next-pose head")
                raise ValueError(f"{what} needs events for {len(absent)} episodes, e.g. {absent[:3]}")

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int) -> dict:
        episode_id, a = self.items[i]
        e = self.episodes(episode_id)
        actions, action_valid = action_window(e["actions"], a)
        pdim = int(e["proprio"].shape[-1])              # 11-28: 14 RoboTwin, 8 LIBERO / RoboMME
        rng = random.Random(hash((self.seed, self.epoch, i)) & 0xFFFFFFFF) if self.augment else None
        known = event_frames(self.events.get(episode_id, []), before=a, known_by=a - int(self.rule.lag))
        ids, pos = select(self.rule, a, known, rng)
        k = self.rule.max_frames
        text = self.text_override.get(episode_id, e["text"])         # 11-24 card 5: per-episode instruction text
        sample = {
            "video_latent": e["video_latent"][a].clone(),
            "video_valid": latent_valid(e["video_valid"][a], self.polarity),
            "text": text.clone(),
            "proprio": e["proprio"][a].float(),
            "actions": actions.float(),
            "action_valid": action_valid,
            "anchor": torch.tensor(a, dtype=torch.long),
        }
        if self.decision is not None:
            sample["loss_weight"] = torch.tensor(
                decision_weight(self.events.get(episode_id, []), a, *self.decision), dtype=torch.float32)
        if self.next_event:
            sample["next_event"] = torch.tensor(next_event_label(self.events.get(episode_id, []), a), dtype=torch.long)
        if self.next_pose is not None:
            target, ok = next_pose_target(self.events.get(episode_id, []), a, e["proprio"], self.next_pose)
            sample.update(next_pose=target, next_pose_valid=torch.tensor(ok))
        if k:
            lat = e["latent"]
            hist_latent = torch.zeros((k,) + tuple(lat.shape[1:]), dtype=lat.dtype)
            hist_proprio = torch.zeros(k, pdim)
            hist_valid = torch.zeros(k, dtype=torch.bool)
            hist_pos = torch.zeros(k)
            hist_ids = torch.full((k,), -1, dtype=torch.long)
            for j, (f, p) in enumerate(zip(ids[-k:], pos[-k:])):
                hist_latent[j] = lat[f]
                hist_proprio[j] = e["proprio"][f].float()
                hist_valid[j] = True
                hist_pos[j] = p
                hist_ids[j] = f
            if self.rule.zoom:                         # plan v19 3.3: the two zoom frames after the ordinary ones
                z = self.zoom_of(episode_id, int(e["proprio"].shape[0]))
                n = len(ids[-k:])
                ref_pos, cur_pos = zoom_positions(self.rule, a, n)
                for j, (zl, pr, zp) in enumerate(((z["ref"], e["proprio"][0], ref_pos),
                                                  (z["cur"][a], e["proprio"][a], cur_pos))):
                    hist_latent[n + j] = zl
                    hist_proprio[n + j] = pr.float()
                    hist_valid[n + j] = True
                    hist_pos[n + j] = zp
                    hist_ids[n + j] = -1                 # not a frame id (zoom)
            sample.update(hist_latent=hist_latent, hist_proprio=hist_proprio, hist_valid=hist_valid,
                          hist_pos=hist_pos, hist_ids=hist_ids)
        if self.rule.variant == "prop":
            frames = event_states(self.rule, a, known)
            states = torch.zeros(self.rule.event_max, pdim)
            valid = torch.zeros(self.rule.event_max, dtype=torch.bool)
            for j, f in enumerate(frames):
                states[j] = e["proprio"][f].float()
                valid[j] = True
            sample.update(event_proprio=states, event_valid=valid)
        if self.rule.variant == "arclk":
            if episode_id not in self.checked_text:
                check_ledger_slots(text, self.rule.event_max, f"in {episode_id}")
                self.checked_text.add(episode_id)
            feat, valid = clock_tensor(self.rule, clock_frames(self.rule, a), lambda f: e["proprio"][f], proprio_dim=pdim)
            sample.update(ledger=feat, ledger_valid=valid)
        if self.rule.variant == "arprop":
            if episode_id not in self.checked_text:
                check_ledger_slots(text, self.rule.event_max, f"in {episode_id}")
                self.checked_text.add(episode_id)
            entries = ledger_entries(self.rule, a, self.events.get(episode_id, []), lambda f: e["proprio"][f])
            if rng is not None and (float(self.rule.ledger_drop_p) > 0 or float(self.rule.ledger_over_p) > 0):
                entries = augment_ledger(self.rule, a, self.events.get(episode_id, []), entries,
                                         lambda f: e["proprio"][f], rng)          # plan v19 3.2 (4), training only
            if rng is not None and float(self.rule.record_dropout) > 0 and rng.random() < float(self.rule.record_dropout):
                entries = []                     # plan v21 card 24b: the empty record (training only)
            feat, valid = ledger_tensor(self.rule, entries, lambda f: e["proprio"][f], proprio_dim=pdim)
            sample.update(ledger=feat, ledger_valid=valid)
        return sample


def _zoom_of(self, episode_id: str, length: int) -> dict:
    """Plan v19 3.3: the zoom latents of an episode (data.zoom_root), checked against the rule's boxes and the length."""
    from .zoom import box_tag
    if episode_id not in self._zoom:
        path = Path(self.zoom_root) / (episode_id.replace("/", "_") + ".pt")
        value = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
        if value.get("tag") != box_tag(self.rule):
            raise ValueError(f"{path}: zoom boxes {value.get('tag')} differ from the model's {box_tag(self.rule)}")
        if int(value["cur"].shape[0]) != int(length):
            raise ValueError(f"{path}: {value['cur'].shape[0]} zoom frames for an episode of {length}")
        self._zoom[episode_id] = value
        while len(self._zoom) > 16:
            self._zoom.popitem(last=False)
    self._zoom.move_to_end(episode_id)
    return self._zoom[episode_id]


Samples.zoom_of = _zoom_of


def train_items(episodes: DenseEpisodes) -> List[Tuple[str, int]]:
    return [(r["episode_id"], a) for r in episodes.split("train") for a in range(int(r["length"]))]


def val_items(episodes: DenseEpisodes, per_task: int) -> List[Tuple[str, int]]:
    """Evenly spaced anchors over the val episodes of each task (deterministic)."""
    out = []
    for task in sorted({r["task"] for r in episodes.records}):
        frames = [(r["episode_id"], a) for r in episodes.split("val") if r["task"] == task
                  for a in range(int(r["length"]))]
        if not frames:
            continue
        step = max(1, len(frames) // per_task)
        out.extend(frames[::step][:per_task])
    return out


def collate(rows: List[dict]) -> dict:
    return {k: torch.stack([r[k] for r in rows]) for k in rows[0]}
