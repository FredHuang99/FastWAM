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
    zoom_root: str = ""                                  # 11-22 plan v19 3.3: folder of the zoom latents
                                                         # (scripts/fullft/build_zoom.py); needed with history.zoom
    text_table: str = ""                                 # 11-24 plan v20 card 5 (press_told): a .pt file
                                                         # {"episodes": {episode_id: instruction}, "by_instruction":
                                                         # {instruction: {"text": [L, D]}}} (scripts/fullft/
                                                         # press_told_text.py); "" = the cache's own text (unchanged)


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
    stop_after: int = 0                                  # 11-17: stop after this many updates (0 = never); the LR
                                                         # schedule keeps the full length (parity runs)
    noise_seed: int = 0                                  # 11-17: reseed the training random draws (diffusion noise,
                                                         # timesteps, dropout) after the model is built; data order,
                                                         # augmentation and initialisation still follow seed (0 = off)
    resume_from: str = ""                                # 11-17 plan v13 E7: a NEW run starts from another run's
                                                         # resume.pt (weights, optimizer, data position, done exports);
                                                         # the LR follows THIS run's schedule. Ignored once the run has
                                                         # its own resume.pt; a missing file is an error ("" = off)
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
    # 11-22 plan v19 3.2 (Deed Memory training parts). Defaults = off: every earlier run and export is exactly as
    # before (no new sample field, no new parameter, the same loss expression).
    # (1) decision-point weighting: the video and action losses of a training sample are multiplied by decision_weight
    #     when its anchor lies within decision_window frames from the confirmation of a completion event of the demo
    #     (confirmed <= anchor < confirmed + window; kinds decision_kinds: gripper opened = put down, press bottom =
    #     pressed). 1.0 = off. Validation losses stay unweighted.
    decision_weight: float = 1.0
    decision_window: int = 16
    decision_kinds: List[str] = field(default_factory=lambda: ["open", "bottom"])
    # (2) next-event head: the mean of the action branch's last-layer tokens -> 9 classes (4 event kinds x 2 arms +
    #     "no event left"); label = the demo's first body event at or after the anchor (events file, no annotation);
    #     cross entropy times next_event_loss added to the training loss. Not used at inference. 0 = no head.
    next_event_loss: float = 0.0
    # 11-23 find-same root cause (obs_probe: frame 0 is not used at the choice; user 14:53 "find the root cause and fix
    # it"). Two more parts, default off, for Fable to choose from (11-24):
    # (1b) pre-event window of the decision weighting: with decision_weight != 1 and decision_pre_window > 0, an anchor
    #     also gets decision_weight when it lies in the decision_pre_window frames BEFORE an event of kinds
    #     decision_pre_kinds (frame - pre <= anchor < frame; 'close' = the gripper closes on the chosen object).
    #     decision_window may then be 0 (no window after the confirmations). 0 = off.
    decision_pre_window: int = 0
    decision_pre_kinds: List[str] = field(default_factory=lambda: ["close"])
    # (2b) next-pose head: the same token mean -> 14 numbers = the body pose (normalised proprio) at the demo's first
    #     event of kinds next_pose_kinds at or after the anchor, minus the pose at the anchor (where the arm will be
    #     when it next closes the gripper = where the chosen object is; no annotation). Masked squared error times
    #     next_pose_loss added to the training loss (no such event left: no loss). Not used at inference. 0 = no head.
    next_pose_loss: float = 0.0
    next_pose_kinds: List[str] = field(default_factory=lambda: ["close"])


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
        for key in ("recent", "zoom_ref_box", "zoom_cur_box"):
            if key in h:
                h[key] = tuple(h[key])
        if h.get("variant") == "tw" and "index" not in h:
            h["index"] = "time"
        return HistoryRule(**h)

    @property
    def decision(self) -> Optional[Tuple[float, int, Tuple[str, ...]]]:
        """(weight, window, kinds) of the decision-point weighting, None when off (plan v19 3.2 (1))."""
        m = self.model
        if float(m.decision_weight) == 1.0:
            return None
        base = (float(m.decision_weight), int(m.decision_window), tuple(m.decision_kinds))
        if int(m.decision_pre_window) > 0:               # 11-23 (1b): (weight, window, kinds, pre, pre_kinds)
            return base + (int(m.decision_pre_window), tuple(m.decision_pre_kinds))
        return base

    @property
    def next_event_head(self) -> bool:
        return float(self.model.next_event_loss) > 0.0

    @property
    def next_pose(self) -> Optional[Tuple[str, ...]]:
        """The event kinds of the next-pose head (11-23 (2b)), None when off."""
        return tuple(self.model.next_pose_kinds) if float(self.model.next_pose_loss) > 0.0 else None

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
    history = tree.get("history")
    if isinstance(history, dict) and history.get("event_rule_from"):
        # 11-16: the event thresholds picked by press_event_sweep.py (PRESS_FAST_RULE.json {"delta", "min_path"}) are
        # copied in as numbers, so run_config.json and every export carry the values, never the path
        import json
        pick = json.loads(Path(str(history.pop("event_rule_from"))).read_text())
        history["event_delta"], history["event_min_path"] = float(pick["delta"]), float(pick["min_path"])
        if float(pick.get("provisional", 0.0) or 0.0) > 0:          # 11-19 plan v14 E14 (provisional write)
            history["event_provisional"] = float(pick["provisional"])
    elif isinstance(history, dict):
        history.pop("event_rule_from", None)
    cfg = _build(RunConfig, tree)
    cfg.rule                                              # validate the history rule early
    if cfg.model.train_video not in ("full", "lora", "frozen"):
        raise ValueError(f"model.train_video must be full | lora | frozen, got {cfg.model.train_video!r}")
    check_deed_parts(cfg)
    return cfg


def check_deed_parts(cfg: RunConfig) -> None:
    """Plan v19 3.2 (1) / (2) and the 11-23 parts (1b) / (2b): value ranges; all read the demos' events, so they need
    data.events."""
    from .history import LEDGER_KINDS
    m = cfg.model
    if not float(m.decision_weight) > 0.0:
        raise ValueError(f"model.decision_weight must be > 0, got {m.decision_weight}")
    if int(m.decision_pre_window) < 0:
        raise ValueError(f"model.decision_pre_window must be >= 0, got {m.decision_pre_window}")
    if int(m.decision_window) < (0 if int(m.decision_pre_window) > 0 else 1):
        raise ValueError(f"model.decision_window must be >= 1 (>= 0 with a pre-event window), got {m.decision_window}")
    if not m.decision_pre_kinds or not set(m.decision_pre_kinds) <= set(LEDGER_KINDS):
        raise ValueError(f"model.decision_pre_kinds must be a non-empty subset of {LEDGER_KINDS}, "
                         f"got {m.decision_pre_kinds}")
    if int(m.decision_pre_window) > 0 and float(m.decision_weight) == 1.0:
        raise ValueError("model.decision_pre_window needs model.decision_weight != 1 (the weight it applies)")
    if float(m.next_pose_loss) < 0.0:
        raise ValueError(f"model.next_pose_loss must be >= 0, got {m.next_pose_loss}")
    if not m.next_pose_kinds or not set(m.next_pose_kinds) <= set(LEDGER_KINDS):
        raise ValueError(f"model.next_pose_kinds must be a non-empty subset of {LEDGER_KINDS}, got {m.next_pose_kinds}")
    if not m.decision_kinds or not set(m.decision_kinds) <= set(LEDGER_KINDS):
        raise ValueError(f"model.decision_kinds must be a non-empty subset of {LEDGER_KINDS}, got {m.decision_kinds}")
    if float(m.next_event_loss) < 0.0:
        raise ValueError(f"model.next_event_loss must be >= 0, got {m.next_event_loss}")
    if (cfg.decision is not None or cfg.next_event_head or cfg.next_pose is not None) and not cfg.data.events:
        raise ValueError("decision weighting / the next-event and next-pose heads read the demos' events: "
                         "set data.events")
