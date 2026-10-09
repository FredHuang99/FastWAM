"""Configuration, provenance, atomic writes, and deterministic sample seeds."""
from __future__ import annotations

import ast
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

import torch
import yaml

SCHEMA = "fastwam-memory-s1-v1"
TASKS = ("put_back_block", "swap_blocks")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with tmp.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def atomic_torch(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.tmp")
    with tmp.open("wb") as stream:
        torch.save(value, stream)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(tmp, path)


def append_jsonl(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + "\n")
        stream.flush()


def load_config(path):
    cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = Path(os.environ.get("FW_ROOT", cfg.get("root", "."))).expanduser().resolve()
    cfg["root"] = str(root)
    for key in ("base", "stats", "vae", "t5", "tokenizer", "raw", "prepared", "cache", "run"):
        p = Path(cfg["paths"][key]).expanduser()
        cfg["paths"][key] = str(p if p.is_absolute() else root / p)
    if cfg["global_batch"] != 16 or cfg["steps"] != 2000 or cfg["seed"] != 17:
        raise ValueError("This S1 recipe requires global_batch=16, steps=2000, seed=17.")
    history = cfg.get("history", {})
    if history:
        low, high = history.get("train_min", 8), history.get("train_max", 8)
        if not 1 <= low <= high <= 16 or history.get("archive_stride", 8) not in (1, 8):
            raise ValueError("Invalid historical periods or archive coverage.")
        if low != high and history.get("archive_stride") != 1:
            raise ValueError("Variable-period training requires a dense cache.")
        if history.get("cache_shard_frames", 64) != 64:
            raise ValueError("This dense cache version uses exactly 64-frame shards.")
    return cfg


def seed_for(seed, step, slot, purpose):
    raw = f"{SCHEMA}:{seed}:{step}:{slot}:{purpose}".encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "little") % (2**63 - 1)


def code_version(root):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
    files = sorted((Path(root) / "src/fastwam/memory_s1").glob("*.py"))
    core = sorted((Path(root) / "src/fastwam/models/wan22").rglob("*.py"))
    return {"commit": git("rev-parse", "HEAD"), "branch": git("branch", "--show-current"),
            "core_sha": fingerprint({str(p.relative_to(root)): sha256(p) for p in core}),
            "diff": git("diff", "HEAD", "--stat"),
            "implementation_sha": fingerprint({str(p.name): sha256(p) for p in files}),
            "support_sha": fingerprint({str(p.relative_to(root)): sha256(p) for p in sorted((Path(root) / "scripts/memory_s1").glob("*")) if p.is_file() and p.suffix in (".py", ".sh")})}


def make_cache_contract(cfg, prepared_manifest):
    from .protocol import prompt_contract, precision_contract
    contract = {"schema": SCHEMA, "base_sha256": sha256(cfg["paths"]["base"]),
            "stats_sha256": sha256(cfg["paths"]["stats"]), "vae_sha256": sha256(cfg["paths"]["vae"]),
            "t5_sha256": sha256(cfg["paths"]["t5"]),
            "tokenizer_sha256": fingerprint({str(p.relative_to(cfg["paths"]["tokenizer"])): sha256(p) for p in sorted(Path(cfg["paths"]["tokenizer"]).rglob("*")) if p.is_file() and ".cache" not in p.parts}),
            "prepared_sha": fingerprint(prepared_manifest), "feature": "video_post_block_29_pre_head",
            "feature_code_sha": fingerprint({name: sha256(Path(__file__).parent / name) for name in ("model.py", "data.py", "common.py")}),
            "architecture_sha": sha256(Path(cfg["root"]) / "configs/model/fastwam.yaml"),
            "core_sha": code_version(cfg["root"])["core_sha"],
            "encoding": "independent_T1_clean_time0_with_then_proprio_fixed_instruction",
            "mosaic": "RGB_PIL_bilinear_head256x320_wrists128x160_device_bf16_then_affine_v2",
            "stride": 8, "decision_stride": 16, "text": "128_zero_padded_base_all_true_reader_valid_mask",
            "prompt": prompt_contract(), "precision": precision_contract(),
            "prompt_code_sha": sha256(Path(__file__).parent / "protocol.py")}
    if cfg.get("integration"):
        from .integration_contract import numerics
        contract["numerics"] = numerics(cfg)
    if cfg.get("history", {}).get("archive_stride", 8) == 1:
        names = {"model.py": {"FrozenBackbone", "load_observation_encoders", "encode_text", "encode_latent"},
                 "data.py": {"official_decoder", "mosaic_rgb", "observation_tensor"}, "common.py": {"ReleaseNormalizer"}, "dense.py": {"cache_observation"}}
        sources = {}
        for filename, functions in names.items():
            tree = ast.parse((Path(__file__).parent / filename).read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in functions:
                    if node.name == "FrozenBackbone":
                        node.body = [item for item in node.body if not isinstance(item, ast.FunctionDef) or item.name in ("__init__", "context", "encode_observation")]
                    sources[f"{filename}:{node.name}"] = ast.dump(node, include_attributes=False)
        contract.update(feature_code_sha=fingerprint(sources), stride=1,
                        coverage="all_native_observation_records", cache_format="frame_shards_v1")
    return contract



def duration(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(max(0, seconds)))


class ReleaseNormalizer:
    """Match the released default-field, global z-score processor."""
    def __init__(self, path):
        stats = read_json(path)
        self.fields = {}
        for kind in ("state", "action"):
            values = stats[kind]["default"]
            mean = torch.tensor(values["global_mean"], dtype=torch.float32)
            std = torch.tensor(values["global_std"], dtype=torch.float32)
            if mean.shape != (14,) or std.shape != (14,) or not torch.isfinite(std).all() or (std <= 0).any():
                raise ValueError(f"Invalid released {kind} statistics.")
            self.fields[kind] = (mean, std + 1e-8)

    def normalize(self, x, kind):
        mean, scale = self.fields[kind]
        reciprocal = 1.0 / scale
        offset = -mean / scale
        # The official deployment processor normalizes CPU FP32 state vectors.
        value = (x.float().cpu() * reciprocal + offset).clamp(-5, 5)
        return value.to(x.device)

    def denormalize(self, x):
        mean, scale = self.fields["action"]
        reciprocal = 1.0 / scale
        offset = -mean / scale
        value = (x.float().cpu() - offset) / reciprocal
        return value.to(x.device)
