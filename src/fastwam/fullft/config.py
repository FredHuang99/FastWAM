"""Configuration of a full fine-tuning run (YAML + dotted --set overrides)."""
from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .history import HistoryRule


@dataclass
class DataConfig:
    roots: List[str] = field(default_factory=lambda: ["/workspace/FastWAM/outputs/s1_dense_joint_h100_v1"])
    tasks: List[str] = field(default_factory=lambda: ["put_back_block", "swap_blocks"])
    events: List[str] = field(default_factory=list)      # events_<task>.json files (fullft/events_stats.py)
    val_anchors_per_task: int = 96                       # fixed validation anchors from the val episodes
    num_workers: int = 6
    episode_cache: int = 16                              # episodes kept open per worker


@dataclass
class OptimConfig:
    lr: float = 1.0e-4
    weight_decay: float = 1.0e-2
    betas: Tuple[float, float] = (0.9, 0.999)
    warmup_steps: int = 500
    min_lr_ratio: float = 0.1
    grad_clip: float = 1.0
    gate_lr_scale: float = 10.0                          # history gates start at 0 and are scalars


@dataclass
class ScheduleConfig:
    frame_epochs: float = 30.0
    micro_batch: int = 8
    accumulation: int = 8
    max_updates: int = 0                                 # 0 = from frame_epochs
    log_every: int = 10
    eval_every: int = 500
    resume_every: int = 1000                             # overwrite the single resume checkpoint
    export_at_epochs: List[float] = field(default_factory=lambda: [10.0, 20.0, 30.0])   # bf16 inference exports


@dataclass
class ModelConfig:
    base: str = "/workspace/FastWAM/resources/base/robotwin_uncond_3cam_384.pt"
    architecture: str = "/workspace/FastWAM/configs/model/fastwam.yaml"
    stats: str = "/workspace/FastWAM/resources/base/robotwin_uncond_3cam_384_dataset_stats.json"
    train_video: str = "full"                            # full | lora | frozen
    lora_rank: int = 64
    checkpoint_layers: bool = True
    video_loss: float = 1.0
    action_loss: float = 1.0
    video_shift: float = 5.0
    action_shift: float = 1.0
    sample_steps: int = 10


@dataclass
class RunConfig:
    name: str = "fullft"
    output: str = "/workspace/FastWAM-memory2/outputs/fullft"
    seed: int = 17
    data: DataConfig = field(default_factory=DataConfig)
    history: Dict[str, Any] = field(default_factory=lambda: {"variant": "ar"})
    optim: OptimConfig = field(default_factory=OptimConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    model: ModelConfig = field(default_factory=ModelConfig)

    @property
    def rule(self) -> HistoryRule:
        h = dict(self.history)
        for key in ("recent",):
            if key in h:
                h[key] = tuple(h[key])
        if h.get("variant") == "tw" and "index" not in h:
            h["index"] = "time"
        return HistoryRule(**h)

    @property
    def run_dir(self) -> Path:
        return Path(self.output) / self.name

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _build(cls, value):
    if not dataclasses.is_dataclass(cls):
        return value
    value = dict(value or {})
    known = {f.name: f for f in dataclasses.fields(cls)}
    unknown = set(value) - set(known)
    if unknown:
        raise ValueError(f"Unknown {cls.__name__} keys: {sorted(unknown)}")
    kwargs = {}
    for name, f in known.items():
        if name not in value:
            continue
        if f.default is not dataclasses.MISSING:
            default = f.default
        elif f.default_factory is not dataclasses.MISSING:
            default = f.default_factory()
        else:
            default = None
        if dataclasses.is_dataclass(default):
            kwargs[name] = _build(type(default), value[name])
        elif isinstance(default, tuple):
            kwargs[name] = tuple(value[name])
        else:
            kwargs[name] = value[name]
    return cls(**kwargs)


def set_dotted(tree: dict, key: str, raw: str) -> None:
    parts = key.split(".")
    node = tree
    for p in parts[:-1]:
        node = node.setdefault(p, {})
    node[parts[-1]] = yaml.safe_load(raw)


def load(path: Optional[str], overrides: List[str] = ()) -> RunConfig:
    tree = yaml.safe_load(Path(path).read_text()) if path else {}
    tree = tree or {}
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"--set expects key=value, got {item!r}")
        k, v = item.split("=", 1)
        set_dotted(tree, k.strip(), v.strip())
    cfg = _build(RunConfig, tree)
    cfg.rule                                              # validate the history rule early
    if cfg.model.train_video not in ("full", "lora", "frozen"):
        raise ValueError(f"model.train_video must be full | lora | frozen, got {cfg.model.train_video!r}")
    return cfg
