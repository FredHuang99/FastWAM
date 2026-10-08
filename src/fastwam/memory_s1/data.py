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
from .history import select_ids, training_period


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
    return torch.from_numpy(mosaic.copy()).permute(2, 0, 1).float() / 127.5 - 1


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
        self.loaded = OrderedDict()
        self.normalizer = ReleaseNormalizer(cfg["paths"]["stats"])

    def load(self, record):
        key = record["episode_id"]
        if key not in self.loaded:
            path = self.root / record["file"]
            value = torch.load(path, map_location="cpu", weights_only=True)
            if value["signature"] != self.signature:
                raise ValueError(f"Stale cache: {path}.")
            if value.get("shards"):
                fields = {name: [] for name in ("features", "latents", "proprio", "frame_ids")}
                for shard in value["shards"]:
                    shard_path = self.root / shard["file"]
                    if sha256(shard_path) != shard["sha256"]:
                        raise ValueError(f"Corrupt cache shard: {shard_path}")
                    block = torch.load(shard_path, map_location="cpu", weights_only=True)
                    if block["signature"] != self.signature:
                        raise ValueError("Cache shard encoder identity mismatch.")
                    for name in fields:
                        fields[name].append(block[name])
                value.update({name: torch.cat(parts) for name, parts in fields.items()})
                if value["frame_ids"].tolist() != list(range(record["length"])):
                    raise ValueError("Dense cache must cover every original observation.")
            self.loaded[key] = value
            if len(self.loaded) > 8:
                self.loaded.popitem(last=False)
        self.loaded.move_to_end(key)
        return self.loaded[key]

    def sample(self, step, slot, validation=False):
        task = TASKS[(step + slot) % len(TASKS)]
        generator = np.random.default_rng(seed_for(self.cfg["seed"], step, slot, "validation" if validation else "sample"))
        records = self.by_task[task]
        record = records[int(generator.integers(len(records)))]
        episode = self.load(record)
        anchor = int(generator.choice(episode["anchors"].numpy()))
        period = 8 if validation else training_period(self.cfg, step, slot)
        return self.at(record, anchor, period=period)

    def at(self, record, anchor, period=8):
        episode = self.load(record)
        indices = episode["frame_ids"]
        chosen = select_ids(indices.tolist(), anchor, int(period))
        if chosen != select_ids(range(anchor + 1), anchor, int(period)):
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
                "episode_id": record["episode_id"], "task": record["task"], "history_period": int(period)}


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
