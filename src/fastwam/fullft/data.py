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
from .history import HistoryRule, event_states, select

HORIZON = 32


def action_window(actions: torch.Tensor, anchor: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Same as memory_v2.dense.action_window: hold the last target past the episode end, mask it."""
    n = len(actions)
    index = torch.clamp(torch.arange(anchor, anchor + HORIZON), max=n - 1)
    valid = torch.arange(anchor, anchor + HORIZON) < n
    return actions[index], valid


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


def load_events(paths: Sequence[str]) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    for p in paths:
        value = json.loads(Path(p).read_text(encoding="utf-8"))
        out.update(value["episodes"] if "episodes" in value else value)
    return out


class Samples(torch.utils.data.Dataset):
    """Item i -> one training sample (episode, anchor) of the given list; history per the rule."""

    def __init__(self, episodes: DenseEpisodes, items: Sequence[Tuple[str, int]], rule: HistoryRule,
                 events: Dict[str, List[dict]], polarity: str, augment: bool = False, seed: int = 0):
        self.episodes, self.items, self.rule = episodes, list(items), rule
        self.events, self.polarity, self.augment, self.seed = events, polarity, augment, seed
        self.epoch = 0
        if rule.variant in ("event", "prop"):
            absent = sorted({e for e, _ in self.items if e not in events})
            if absent:
                raise ValueError(f"history '{rule.variant}' needs events for {len(absent)} episodes, e.g. {absent[:3]}")

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, i: int) -> dict:
        episode_id, a = self.items[i]
        e = self.episodes(episode_id)
        actions, action_valid = action_window(e["actions"], a)
        rng = random.Random(hash((self.seed, self.epoch, i)) & 0xFFFFFFFF) if self.augment else None
        known = event_frames(self.events.get(episode_id, []), before=a, known_by=a)
        ids, pos = select(self.rule, a, known, rng)
        k = self.rule.max_frames
        sample = {
            "video_latent": e["video_latent"][a].clone(),
            "video_valid": latent_valid(e["video_valid"][a], self.polarity),
            "text": e["text"].clone(),
            "proprio": e["proprio"][a].float(),
            "actions": actions.float(),
            "action_valid": action_valid,
            "anchor": torch.tensor(a, dtype=torch.long),
        }
        if k:
            lat = e["latent"]
            hist_latent = torch.zeros((k,) + tuple(lat.shape[1:]), dtype=lat.dtype)
            hist_proprio = torch.zeros(k, 14)
            hist_valid = torch.zeros(k, dtype=torch.bool)
            hist_pos = torch.zeros(k)
            hist_ids = torch.full((k,), -1, dtype=torch.long)
            for j, (f, p) in enumerate(zip(ids[-k:], pos[-k:])):
                hist_latent[j] = lat[f]
                hist_proprio[j] = e["proprio"][f].float()
                hist_valid[j] = True
                hist_pos[j] = p
                hist_ids[j] = f
            sample.update(hist_latent=hist_latent, hist_proprio=hist_proprio, hist_valid=hist_valid,
                          hist_pos=hist_pos, hist_ids=hist_ids)
        if self.rule.variant == "prop":
            frames = event_states(self.rule, a, known)
            states = torch.zeros(self.rule.event_max, 14)
            valid = torch.zeros(self.rule.event_max, dtype=torch.bool)
            for j, f in enumerate(frames):
                states[j] = e["proprio"][f].float()
                valid[j] = True
            sample.update(event_proprio=states, event_valid=valid)
        return sample


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
