"""Audited episode conversion and stateless, task-balanced cache sampling."""
from __future__ import annotations

from collections import OrderedDict
import importlib.util
import json
from pathlib import Path

import h5py
import numpy as np
from PIL import Image
import torch

from .common import TASKS, ReleaseNormalizer, read_json, seed_for, sha256
from .history import select_ids, training_period, training_phase


def official_decoder(root):
    path = Path(root) / "data/decode_image_bit.py"
    spec = importlib.util.spec_from_file_location("rmbench_image_codec", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.decode_image_bit


def mosaic_rgb(images):
    parts = []
    for rgb, size in zip(images, ((320, 256), (160, 128), (160, 128))):
        if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[-1] != 3:
            raise ValueError("Official RGB decode must return uint8 HWC with three channels.")
        parts.append(np.asarray(Image.fromarray(rgb).resize(size, Image.Resampling.BILINEAR)))
    mosaic = np.concatenate((parts[0], np.concatenate(parts[1:], axis=1)), axis=0)
    return torch.from_numpy(mosaic.copy()).permute(2, 0, 1)


def observation_tensor(images, device):
    """Apply the released uint8 -> device BF16 -> affine image contract."""
    image = mosaic_rgb(images)[None].to(device=device, dtype=torch.bfloat16)
    return image * (2.0 / 255.0) - 1.0


def camera_columns(file):
    native = [f"observation/{cam}/rgb" for cam in ("head_camera", "left_camera", "right_camera")]
    converted = [f"vision/{cam}/colors" for cam in ("cam_head", "cam_left_wrist", "cam_right_wrist")]
    for paths in (native, converted):
        if all(path in file for path in paths):
            return paths
    raise ValueError(f"Missing one of the three RGB cameras; HDF5 keys={list(file.keys())}.")


def joint_columns(group):
    names = ("left_arm_joint_states", "left_ee_joint_states", "right_arm_joint_states", "right_ee_joint_states")
    fields = []
    for name, width in zip(names, (6, 1, 6, 1)):
        value = np.asarray(group[name], dtype=np.float32)
        if value.ndim == 1:
            value = value[:, None]
        if value.shape[1:] != (width,):
            raise ValueError(f"Unexpected {name} shape={value.shape}.")
        fields.append(value)
    return np.concatenate(fields, axis=1)


def read_episode(path):
    with h5py.File(path, "r") as file:
        cameras = camera_columns(file)
        if "joint_action/vector" in file:
            q = np.asarray(file["joint_action/vector"], dtype=np.float32)
            state, targets = q[:-1], q[1:]
            source_kind = "native_state_next_record_target"
        elif "state" in file and "action" in file:
            state, targets = joint_columns(file["state"]), joint_columns(file["action"])
            source_kind = "official_shifted_state_action"
            if len(state) > 1 and not np.allclose(targets[:-1], state[1:], atol=1e-5, rtol=1e-5):
                raise ValueError("Official state/action shift does not equal one record; manual alignment is required.")
        else:
            raise ValueError("No reliable state/action timeline was found.")
        if state.shape != targets.shape or state.ndim != 2 or state.shape[1] != 14 or len(state) < 2:
            raise ValueError(f"Invalid state/action shapes={state.shape}/{targets.shape}.")
        if not np.isfinite(state).all() or not np.isfinite(targets).all():
            raise ValueError("Non-finite state/action data.")
        if min(len(file[key]) for key in cameras) < len(state):
            raise ValueError("A camera is shorter than the state/action timeline.")
        if any(((value[:, [6, 13]] < -0.01) | (value[:, [6, 13]] > 1.01)).any() for value in (state, targets)):
            raise ValueError("Gripper values are not in the released [0,1] convention.")
        metadata = {key: str(value) for key, value in file.attrs.items()}
        if "additional_info/frequency" in file:
            metadata["stored_frequency"] = np.asarray(file["additional_info/frequency"]).tolist()
        instruction_value = None
        if "instructions" in file:
            value = file["instructions"][()]
            instruction_value = json.loads(value.decode() if isinstance(value, bytes) else str(value))
    return state, targets, cameras, source_kind, metadata, instruction_value


def choose_instruction(path, embedded):
    instruction_path = Path(path).parent.parent / "instruction" / (Path(path).stem + ".json")
    if instruction_path.is_file():
        value = read_json(instruction_path)
        seen = value.get("seen") if isinstance(value, dict) else None
        if not isinstance(seen, list) or not seen or not isinstance(seen[0], str):
            raise ValueError("Instruction JSON lacks a whole-task seen list; subtask labels are never substituted.")
        return seen[0].strip(), str(instruction_path)
    if isinstance(embedded, list) and embedded and isinstance(embedded[0], str):
        return embedded[0].strip(), "HDF5:instructions"
    raise ValueError("Missing fixed whole-task instruction.")


# Shared by train/validation datasets in one process. No tensors are modified here.
_HOST_CACHE = OrderedDict()
_HOST_BYTES = 0
_VERIFIED_FILES = {}


def _file_stamp(path):
    stat = path.stat()
    return (stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_ino)


def verify_cache_file(path, expected):
    path = Path(path).resolve()
    stamp = _file_stamp(path)
    old = _VERIFIED_FILES.get(str(path))
    if old is not None:
        if old != (stamp, expected):
            raise ValueError(f"Cache file changed during this process: {path}")
        return
    if sha256(path) != expected:
        raise ValueError(f"Corrupt cache file: {path}")
    _VERIFIED_FILES[str(path)] = (stamp, expected)


def _tensor_bytes(value):
    if isinstance(value, torch.Tensor):
        return value.numel() * value.element_size()
    if isinstance(value, dict):
        return sum(_tensor_bytes(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return sum(_tensor_bytes(item) for item in value)
    return 0


class CachedEpisodes:
    def __init__(self, cfg, split):
        self.cfg = cfg
        self.root = Path(cfg["paths"]["cache"])
        self.manifest = read_json(self.root / "manifest.json")
        self.signature = self.manifest["signature"]
        self.by_task = {task: [] for task in TASKS}
        for episode in self.manifest["episodes"]:
            if episode["split"] == split:
                self.by_task[episode["task"]].append(episode)
        if any(not episodes for episodes in self.by_task.values()):
            raise ValueError(f"Each task needs at least one {split} episode.")
        self.cache_limit = int(cfg.get("startup", {}).get("cpu_cache_gib", 64) * 2**30)
        if self.cache_limit <= 0:
            raise ValueError("cpu_cache_gib must be positive.")
        self.cache_hits = self.cache_misses = 0
        self.normalizer = ReleaseNormalizer(cfg["paths"]["stats"])

    def verify_record(self, record):
        verify_cache_file(self.root / record["file"], record["cache_sha256"])
        for shard in record.get("shards", []):
            verify_cache_file(self.root / shard["file"], shard["sha256"])

    def load(self, record):
        global _HOST_BYTES
        self.verify_record(record)
        key = (str(self.root.resolve()), self.signature, record["episode_id"])
        if key in _HOST_CACHE:
            self.cache_hits += 1
            _HOST_CACHE.move_to_end(key)
            return _HOST_CACHE[key][0]
        self.cache_misses += 1
        # Evict before allocation; reserve space for concatenation and other host work.
        estimated = int(record["length"]) * (120 * 3072 * 2 + 48 * 24 * 20 * 2 + 128)
        while _HOST_CACHE and _HOST_BYTES + 2 * estimated > self.cache_limit:
            _, (old_value, size) = _HOST_CACHE.popitem(last=False)
            del old_value
            _HOST_BYTES -= size
        if Path("/proc/meminfo").exists():
            available = int(next(line.split()[1] for line in Path("/proc/meminfo").read_text().splitlines()
                                 if line.startswith("MemAvailable:"))) * 1024
            while _HOST_CACHE and available < 2 * estimated + 16 * 2**30:
                _, (old_value, size) = _HOST_CACHE.popitem(last=False)
                del old_value
                _HOST_BYTES -= size
                available += size
        path = self.root / record["file"]
        value = torch.load(path, map_location="cpu", weights_only=True)
        if value["signature"] != self.signature:
            raise ValueError(f"Stale cache: {path}.")
        if value.get("shards"):
            if value["shards"] != record.get("shards"):
                raise ValueError("Episode descriptor and manifest shard lists differ.")
            fields = {name: [] for name in ("features", "latents", "proprio", "frame_ids")}
            for shard in value["shards"]:
                block = torch.load(self.root / shard["file"], map_location="cpu", weights_only=True)
                if block["signature"] != self.signature:
                    raise ValueError("Cache shard encoder identity mismatch.")
                for name in fields:
                    fields[name].append(block[name])
            value.update({name: torch.cat(parts) for name, parts in fields.items()})
            if value["frame_ids"].tolist() != list(range(record["length"])):
                raise ValueError("Dense cache must cover every original observation.")
        size = _tensor_bytes(value)
        while _HOST_CACHE and _HOST_BYTES + size > self.cache_limit:
            _, (old_value, old_size) = _HOST_CACHE.popitem(last=False)
            del old_value
            _HOST_BYTES -= old_size
        if size <= self.cache_limit:
            _HOST_CACHE[key] = (value, size)
            _HOST_BYTES += size
        return value

    def sample(self, step, slot, validation=False):
        task = TASKS[(step + slot) % len(TASKS)]
        generator = np.random.default_rng(seed_for(self.cfg["seed"], step, slot, "validation" if validation else "sample"))
        records = self.by_task[task]
        record = records[int(generator.integers(len(records)))]
        episode = self.load(record)
        anchor = int(generator.choice(episode["anchors"].numpy()))
        period = 8 if validation else training_period(self.cfg, step, slot)
        return self.at(record, anchor, period=period, phase=0 if validation else training_phase(self.cfg, step, slot, period))

    def at(self, record, anchor, period=8, phase=0):
        episode = self.load(record)
        indices = episode["frame_ids"]
        chosen = select_ids(indices.tolist(), anchor, int(period), phase=phase)
        if chosen != select_ids(range(anchor + 1), anchor, int(period), phase=phase):
            raise ValueError("The cache lacks observations required by this historical period.")
        selected = torch.isin(indices, torch.tensor(chosen))
        position = torch.nonzero(indices == anchor, as_tuple=False).flatten()
        if position.numel() != 1:
            raise ValueError("Decision observation must be cached exactly once.")
        actions = torch.zeros(32, 14)
        valid = torch.zeros(32, dtype=torch.bool)
        count = min(32, len(episode["targets"]) - anchor)
        if count <= 0:
            raise ValueError("All-invalid anchor.")
        actions[:count] = self.normalizer.normalize(episode["targets"][anchor:anchor + count], "action")
        if count < 32:
            actions[count:] = actions[count - 1]
        valid[:count] = True
        return {"latent": episode["latents"][position.item()], "proprio": episode["proprio"][position.item()],
                "text": episode["text"], "text_valid": episode["text_valid"], "history": episode["features"][selected],
                "frame_ids": indices[selected], "history_valid": torch.ones(int(selected.sum()), dtype=torch.bool),
                "actions": actions, "action_valid": valid, "t": torch.tensor(anchor),
                "episode_id": record["episode_id"], "task": record["task"], "history_period": int(period), "history_phase": phase}


def collate(samples, device):
    maximum = max(len(sample["frame_ids"]) for sample in samples)
    history = torch.zeros(len(samples), maximum, 120, 3072, dtype=torch.bfloat16)
    frame_ids = torch.zeros(len(samples), maximum, dtype=torch.long)
    valid = torch.zeros(len(samples), maximum, dtype=torch.bool)
    for index, sample in enumerate(samples):
        length = len(sample["frame_ids"])
        history[index, :length] = sample["history"]
        frame_ids[index, :length] = sample["frame_ids"]
        valid[index, :length] = sample["history_valid"]
    batch = {key: torch.stack([sample[key] for sample in samples]) for key in
             ("latent", "proprio", "text", "text_valid", "actions", "action_valid", "t")}
    batch.update(history=history, frame_ids=frame_ids, history_valid=valid)
    return {key: value.to(device, non_blocking=False) for key, value in batch.items()}


def history_variant(sample, condition, evidence=None):
    sample = dict(sample)
    ids = sample["frame_ids"]
    current = ids == sample["t"]
    keep = torch.ones_like(ids, dtype=torch.bool)
    if condition == "current_only":
        keep = current
    elif condition in ("delete_critical", "delete_irrelevant"):
        if evidence is None:
            raise ValueError("Evidence deletion requires reviewed visible intervals; random deletions are not substituted.")
        if int(sample["t"]) < evidence["apply_from"]:
            return sample
        ranges = evidence["critical"]
        critical = torch.zeros_like(keep)
        for start, end in ranges:
            critical |= (ids >= start) & (ids <= end)
        critical &= ~current
        if condition == "delete_critical":
            keep &= ~critical
        else:
            irrelevant = torch.zeros_like(keep)
            for start, end in evidence["irrelevant"]:
                irrelevant |= (ids >= start) & (ids <= end)
            candidates = torch.nonzero(irrelevant & ~critical & ~current).flatten()
            count = int(critical.sum())
            if len(candidates) < count:
                raise ValueError("Not enough reviewed irrelevant observations for count-matched deletion.")
            keep[candidates[:count]] = False
    elif condition not in ("full", "gate_zero"):
        raise ValueError(f"Unknown condition={condition}.")
    keep |= current
    for key in ("history", "frame_ids", "history_valid"):
        sample[key] = sample[key][keep]
    return sample


def load_evidence(path):
    value = read_json(path)
    if value.get("reviewed") is not True or not value.get("provenance"):
        raise ValueError("Evidence intervals require reviewed=true and a concrete visibility/provenance record.")
    if value.get("offline_index") != "native_observation_record" or value.get("online_index") != "completed_action_target":
        raise ValueError("Offline and online evidence indices must be explicitly distinguished.")
    for annotation in list(value.get("offline", {}).values()) + [entry for task in value.get("online", {}).values() for entry in task.values()]:
        if not isinstance(annotation.get("apply_from"), int) or annotation["apply_from"] < 0:
            raise ValueError("Each intervention needs a reviewed apply_from decision index after evidence disappears and controls exist.")
        for kind in ("critical", "irrelevant"):
            if kind not in annotation:
                raise ValueError(f"Missing {kind} visibility intervals.")
            for start, end in annotation[kind]:
                if not isinstance(start, int) or not isinstance(end, int) or start < 0 or end < start:
                    raise ValueError("Visibility intervals must be nonnegative inclusive integer ranges.")
    return value
