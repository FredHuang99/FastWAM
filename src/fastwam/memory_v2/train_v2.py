"""memory_v2 training / evaluation on the dense-joint data (branch-A layout).

    python -m fastwam.memory_v2.train_v2 features --config configs/memory_v2/train_v2_A.yaml
    python -m fastwam.memory_v2.train_v2 train    --config configs/memory_v2/train_v2_A.yaml [--dry-run 3] [--resume]
    python -m fastwam.memory_v2.train_v2 evaluate --config configs/memory_v2/train_v2_A.yaml --checkpoint <ckpt|init>

Multi-GPU: `torchrun --standalone --nproc_per_node=N -m fastwam.memory_v2.train_v2 train ...`.

Contract (see README "train_v2"):
  * Start weights: the C+256 source by default (NOT A335: A335 degraded the
    offline error 3x; its own training loss rose 3.8x with the LR warm-up,
    scripts/memory_v2/loss_vs_lr.py). Any A checkpoint can be given instead.
  * Default: ActionDiT, Video DiT and proprio frozen; only memory_v2 trains.
    The zero-initialised memory output makes the first forward identical to the
    start model, which is checked (INIT_PARITY.json) before the first update.
  * ActionDiT co-training is opt-in (`optim.lr_action > 0`) and refused above
    2e-5 unless `--allow-high-action-lr` is given.
  * Guards stop the run (GUARD.json) when the training FM loss rises above
    `guard.loss_factor` x its initial level, or when memory-on offline error is
    worse than memory-off by more than `guard.eval_regression`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import shutil
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import torch

from .config import GuidanceConfig, V2Config
from .metrics import attention_report, gate_profile, history_sensitivity, summarize_sensitivity
from .model import MemoryV2Model
from .objectives import compute_loss

TAU_BINS = (0.0, 0.2, 0.4, 0.6, 0.8, 0.95, 1.0 + 1e-9)
HIGH_ACTION_LR = 2e-5
BASE_TOLERANCE = 0.02   # relative L2 between memory-off velocity and ABModel's; gate 0 vs 1 differ by O(1)


# ============================================================================ config
@dataclass
class OptimConfig:
    lr_memory: float = 1e-4
    lr_action: float = 0.0            # 0 = ActionDiT frozen (default)
    betas: tuple = (0.9, 0.95)
    eps: float = 1e-8
    weight_decay: float = 0.01
    warmup_fraction: float = 0.05
    min_lr_ratio: float = 0.01
    clip: float = 1.0


@dataclass
class ScheduleConfig:
    epochs: int = 2
    global_batch: int = 64
    micro_batch: int = 8
    save_every: int = 50
    probe_every: int = 25
    eval_every: int = 100
    keep_last: int = 2


@dataclass
class EvalConfig:
    windows: int = 96                  # 0 = all fixed windows; otherwise a deterministic stratified subset
    batch: int = 8
    modes: tuple = ("on", "off", "null")
    guidance_scales: tuple = (1.0,)    # extra scales are evaluated with memory_mode="on"
    fm_taus: tuple = (0.1, 0.5, 0.9, 1.0)


@dataclass
class GuardConfig:
    loss_factor: float = 2.0           # stop if rolling median FM > factor x initial median
    loss_window: int = 16
    loss_baseline_updates: int = 8
    eval_regression: float = 0.10      # stop if on-mode val arm RMSE > (1 + x) * off-mode
    start_update: int = 50             # guards inactive before this update (except non-finite)


@dataclass
class PairsConfig:
    """Counterfactual history training on matched-present pairs (scripts/memory_v2/find_pairs.py)."""
    file: str = ""                     # pairs JSON; empty = off
    weight: float = 0.0                # loss weight of the swapped-history term (0 = off)
    per_update: int = 16               # pairs per optimizer update (each used in both directions)
    max_visual_distance: float = 1e9   # keep only pairs whose current frames also look alike
    min_delta: float = 0.0             # keep only pairs whose futures differ at least this much

    @property
    def enabled(self) -> bool:
        return bool(self.file) and self.weight > 0


@dataclass
class TrainConfig:
    name: str = "v2_A_memory_only"
    output: str = "outputs/memory_v2/v2_A_memory_only"
    seed: int = 17
    init_checkpoint: str = "source"
    base_memory: str = "s1"          # s1 = frozen memory_s1 stays in the base (C+256 needs it); none = gate-0 diagnostic
    s1_period: int = 8               # memory_s1 history period T (dense evaluation/online use 8)
    features: str = "outputs/memory_v2/features_dense_v1"
    feature_batch: int = 16
    dense: dict = field(default_factory=dict)
    v2: V2Config = field(default_factory=V2Config)
    optim: OptimConfig = field(default_factory=OptimConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    guard: GuardConfig = field(default_factory=GuardConfig)
    pairs: PairsConfig = field(default_factory=PairsConfig)

    @classmethod
    def from_dict(cls, value: dict) -> "TrainConfig":
        value = dict(value or {})
        known = {"name", "output", "seed", "init_checkpoint", "base_memory", "s1_period", "features", "feature_batch", "dense",
                 "memory_v2", "optim", "schedule", "eval", "guard", "pairs"}
        unknown = set(value) - known
        if unknown:
            raise ValueError(f"Unknown train_v2 keys: {sorted(unknown)}")

        def section(kind, key):
            data = dict(value.get(key) or {})
            allowed = set(kind.__dataclass_fields__)
            extra = set(data) - allowed
            if extra:
                raise ValueError(f"Unknown keys in {key}: {sorted(extra)}")
            for name, f in kind.__dataclass_fields__.items():
                if name in data and isinstance(f.default, tuple):
                    data[name] = tuple(data[name])
            return kind(**data)

        cfg = cls(**{k: value[k] for k in ("name", "output", "seed", "init_checkpoint", "base_memory", "s1_period",
                                          "features", "feature_batch", "dense")
                     if k in value})
        cfg.v2 = V2Config.from_dict(value.get("memory_v2"))
        cfg.optim = section(OptimConfig, "optim")
        cfg.schedule = section(ScheduleConfig, "schedule")
        cfg.eval = section(EvalConfig, "eval")
        cfg.eval.modes = normalise_modes(cfg.eval.modes)
        cfg.guard = section(GuardConfig, "guard")
        cfg.pairs = section(PairsConfig, "pairs")
        if cfg.schedule.global_batch % cfg.schedule.micro_batch:
            raise ValueError("global_batch must be a multiple of micro_batch.")
        return cfg

    def to_dict(self) -> dict:
        return {"name": self.name, "output": self.output, "seed": self.seed, "init_checkpoint": self.init_checkpoint,
                "base_memory": self.base_memory, "s1_period": self.s1_period,
                "features": self.features, "feature_batch": self.feature_batch, "dense": dict(self.dense),
                "memory_v2": self.v2.to_dict(), "optim": asdict(self.optim), "schedule": asdict(self.schedule),
                "eval": asdict(self.eval), "guard": asdict(self.guard),
                **({"pairs": asdict(self.pairs)} if asdict(self.pairs) != asdict(PairsConfig()) else {})}


YAML_MODE_ALIASES = {True: "on", False: "off", None: "null"}   # YAML 1.1 reads on/off/null as True/False/None


def normalise_modes(modes) -> tuple:
    out = tuple(YAML_MODE_ALIASES.get(m, m) if not isinstance(m, str) else m for m in modes)
    bad = [m for m in out if m not in ("on", "null", "off")]
    if bad:
        raise ValueError(f"eval.modes must be on/null/off, got {bad}")
    return out


def load_config(path: Path, overrides: Sequence[str] = ()) -> TrainConfig:
    import yaml
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    for item in overrides:                       # key.sub=value (YAML-parsed value)
        key, _, raw = item.partition("=")
        target = value
        parts = key.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = yaml.safe_load(raw)
    return TrainConfig.from_dict(value)


# ============================================================================ helpers
def stable_seed(*parts) -> int:
    return int.from_bytes(hashlib.sha256(json.dumps(parts, sort_keys=True).encode()).digest()[:8], "little") % (2 ** 63 - 1)


def lr_at(update: int, total: int, base: float, warmup_fraction: float, min_ratio: float) -> float:
    """Linear warm-up then cosine to min_ratio x base (same shape as the dense recipe)."""
    if base <= 0:
        return 0.0
    warm = max(1, math.ceil(total * warmup_fraction))
    if update <= warm:
        return base * update / warm
    f = min(1.0, (update - warm) / max(1, total - warm))
    return base * (min_ratio + (1 - min_ratio) * (1 + math.cos(math.pi * f)) / 2)


def epoch_rows(all_rows: Sequence[dict], epoch: int, seed: int) -> List[dict]:
    rows = list(all_rows)
    random.Random(stable_seed(seed, epoch, "memory_v2-epoch-permutation")).shuffle(rows)
    return rows


def rank_world():
    if torch.distributed.is_available() and torch.distributed.is_initialized():
        return torch.distributed.get_rank(), torch.distributed.get_world_size()
    return 0, 1


def barrier():
    if rank_world()[1] > 1:
        torch.distributed.barrier()


def broadcast_flag(flag: bool, device) -> bool:
    if rank_world()[1] == 1:
        return flag
    t = torch.tensor([1 if flag else 0], device=device)
    torch.distributed.broadcast(t, src=0)
    return bool(t.item())


def gather_objects(items: list) -> list:
    rank, world = rank_world()
    if world == 1:
        return items
    out = [None] * world
    torch.distributed.all_gather_object(out, items)
    return [x for part in out for x in part]


def write_json(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.partial")
    temp.write_text(json.dumps(value, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    temp.replace(path)


def append_jsonl(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(value, allow_nan=True) + "\n")


def tau_bin_stats(tau: torch.Tensor, error: torch.Tensor) -> Dict[str, List[float]]:
    sums, counts = [0.0] * (len(TAU_BINS) - 1), [0] * (len(TAU_BINS) - 1)
    for t, e in zip(tau.tolist(), error.tolist()):
        for j in range(len(TAU_BINS) - 1):
            if TAU_BINS[j] <= t < TAU_BINS[j + 1]:
                sums[j] += e
                counts[j] += 1
                break
    return {"sum": sums, "count": counts}


# ============================================================================ backend protocol
class Backend:
    """What the trainer needs from the data/model side (dense host or the tiny CPU test backend)."""

    model: MemoryV2Model
    device: torch.device

    def train_rows(self) -> List[dict]: ...
    def batch(self, rows: Sequence[dict]) -> Dict[str, torch.Tensor]: ...
    def probe_rows(self) -> List[dict]: ...
    def eval_rows(self, limit: int) -> List[dict]: ...
    def window_case(self, row: dict, normalised_sample: torch.Tensor, batch_index: int,
                    batch: Dict[str, torch.Tensor]) -> Dict[str, float]: ...
    def noise(self, row: dict, shape) -> torch.Tensor: ...
    def describe(self) -> dict: ...

    def pair_batches(self, pairs: Sequence[dict], reverse: bool = False, swap: str = "all"):
        """(own, swapped): own = query current + query history (query targets); swapped = query current +
        donor history (donor targets). reverse swaps the roles of query and donor."""
        from .pairs import swap_history
        q, d = ("donor", "query") if reverse else ("query", "donor")
        own = self.batch([p[q] for p in pairs])
        donor = self.batch([p[d] for p in pairs])
        return own, swap_history(own, donor, swap)

    def pair_noise(self, pair: dict, reverse: bool, shape) -> torch.Tensor:
        key = "|".join(f"{p['episode_id']}:{p['anchor']}" for p in ((pair["donor"], pair["query"]) if reverse
                                                                    else (pair["query"], pair["donor"])))
        g = torch.Generator().manual_seed(stable_seed("pair-noise", key))
        return torch.randn(shape, generator=g).to(torch.bfloat16).float().to(self.device)


# ============================================================================ evaluation
@torch.no_grad()
def evaluate(backend: Backend, rows: Sequence[dict], cfg: TrainConfig, log=print) -> Dict[str, object]:
    """Offline windows: sampled-chunk errors per memory mode / guidance scale + FM error per tau."""
    model = backend.model
    model.eval()
    rank, world = rank_world()
    mine = list(rows)[rank::world]
    variants = [(mode, 1.0) for mode in cfg.eval.modes] + [("on", s) for s in cfg.eval.guidance_scales if s != 1.0]
    cases = []
    for start in range(0, len(mine), cfg.eval.batch):
        chunk = mine[start:start + cfg.eval.batch]
        batch = backend.batch(chunk)
        conditions = model.conditions(batch)
        actions = batch["actions"].float()
        noise = torch.stack([backend.noise(row, actions.shape[1:]) for row in chunk]).to(actions.device)
        per_row = [dict(row) for row in chunk]
        for mode, scale in variants:
            guidance = GuidanceConfig(steps=cfg.v2.guidance.steps, shift=cfg.v2.guidance.shift, scale=scale,
                                      min_sigma=cfg.v2.guidance.min_sigma)
            sample, _ = model.sample(conditions, noise, guidance, memory_mode=mode)
            label = mode if scale == 1.0 else f"{mode}_cfg{scale:g}"
            for b, row in enumerate(per_row):
                metrics = backend.window_case(row, sample[b], b, batch)
                row.update({f"{label}/{k}": v for k, v in metrics.items()})
        valid = batch["action_valid"].float()
        for mode in cfg.eval.modes:                      # FM error of the velocity field, per noise level
            for tau in cfg.eval.fm_taus:
                t = torch.full((actions.shape[0],), 1000.0 * tau, device=actions.device)
                noisy = (1 - tau) * actions + tau * noise
                pred = model.velocity(noisy, t, conditions, mode).float()
                err = ((pred - (noise - actions)).square().mean(-1) * valid).sum(1) / valid.sum(1)
                for b, row in enumerate(per_row):
                    row[f"{mode}/fm_tau{tau:g}"] = float(err[b])
        cases.extend(per_row)
        if rank == 0 and (start // cfg.eval.batch) % 8 == 0:
            log(f"[eval] {min(len(mine), start + len(chunk))}/{len(mine)} windows on rank 0")
    cases = gather_objects(cases)
    keys = sorted({k for c in cases for k in c if "/" in k})
    from .dense import summarise
    summary = summarise(cases, keys) if cases and "task" in cases[0] else []
    overall = {k: sum(c[k] for c in cases) / len(cases) for k in keys}
    model.train()
    return {"windows": len(cases), "overall": overall, "groups": summary, "cases": cases}


@torch.no_grad()
def evaluate_pairs(backend: Backend, pairs: Sequence[dict], cfg: TrainConfig, modes=("on", "off", "null"),
                   batch_size: int = 8, log=print, swap: str = "all") -> Dict[str, object]:
    """History-swap response on matched-present pairs, both directions, same noise for own/swapped.

    own_correct : with its own history, the prediction is closer to its own future than to the partner's
    switch      : with the partner's history (same current frame), it is closer to the partner's future
    pr          : own_correct and switch                      (history-blind model: switch ~ 1 - own_correct)
    response    : ||pred(swapped) - pred(own)|| / ||target(partner) - target(own)||   (0 = ignores history)
    swap        : all | content (partner's history re-timed to the own clock) | clock (own history, partner's clock)
    """
    model = backend.model
    model.eval()
    rank, world = rank_world()
    mine = list(enumerate(pairs))[rank::world]
    guidance = GuidanceConfig(steps=cfg.v2.guidance.steps, shift=cfg.v2.guidance.shift, scale=1.0,
                              min_sigma=cfg.v2.guidance.min_sigma)
    cases = []
    for start in range(0, len(mine), batch_size):
        chunk = mine[start:start + batch_size]
        group = [p for _, p in chunk]
        for reverse in (False, True):
            own, swapped = backend.pair_batches(group, reverse, swap)
            dropped = swapped.get("history_dropped")
            c_own, c_swap = model.conditions(own), model.conditions(swapped)
            t_own, t_swap = own["actions"].float(), swapped["actions"].float()
            valid = (own["action_valid"] & swapped["action_valid"]).float()[..., None]
            noise = torch.stack([backend.pair_noise(p, reverse, t_own.shape[1:]) for p in group])
            gap = ((t_swap - t_own) * valid).flatten(1).norm(dim=1).clamp_min(1e-6)

            def dist(a, b):
                return ((a - b) * valid).flatten(1).norm(dim=1)

            rows = [{"pair": i, "reverse": reverse, "task": p["task"], "delta_norm": p["delta_norm"],
                     "visual_distance": p.get("visual_distance"), "present_rms": p["present_rms"],
                     "donor_split": p.get("donor_split"), "swap": swap,
                     "history_dropped": 0 if dropped is None else int(dropped[b])} for b, (i, p) in enumerate(chunk)]
            for mode in modes:
                p_own, _ = model.sample(c_own, noise, guidance, memory_mode=mode)
                p_swap, _ = model.sample(c_swap, noise, guidance, memory_mode=mode)
                own_ok = dist(p_own, t_own) < dist(p_own, t_swap)
                switch = dist(p_swap, t_swap) < dist(p_swap, t_own)
                response = dist(p_swap, p_own) / gap
                for b, row in enumerate(rows):
                    row[f"{mode}/own_correct"] = bool(own_ok[b])
                    row[f"{mode}/switch"] = bool(switch[b])
                    row[f"{mode}/pr"] = bool(own_ok[b] and switch[b])
                    row[f"{mode}/response"] = float(response[b])
            cases.extend(rows)
        if rank == 0 and (start // batch_size) % 10 == 0:
            log(f"[pr] {min(len(mine), start + len(chunk))}/{len(mine)} pairs on rank 0")
    cases = gather_objects(cases)
    model.train()
    return {"pairs": len(pairs), "swap": swap, "cases": cases, "summary": summarise_pairs_eval(cases, modes)}


def summarise_pairs_eval(cases: Sequence[dict], modes) -> dict:
    import statistics

    def agg(sub):
        out = {"n": len(sub)}
        for mode in modes:
            if not sub:
                continue
            out[mode] = {k: sum(c[f"{mode}/{k}"] for c in sub) / len(sub) for k in ("own_correct", "switch", "pr")}
            out[mode]["response_median"] = statistics.median(c[f"{mode}/response"] for c in sub)
        return out

    summary = {"all": agg(list(cases))}
    for task in sorted({c["task"] for c in cases}):
        summary[task] = agg([c for c in cases if c["task"] == task])
    deltas = sorted(c["delta_norm"] for c in cases)
    if deltas:
        cuts = [deltas[len(deltas) // 3], deltas[2 * len(deltas) // 3]]
        for name, lo, hi in (("delta_low", -1, cuts[0]), ("delta_mid", cuts[0], cuts[1]), ("delta_high", cuts[1], 1e18)):
            summary[name] = agg([c for c in cases if lo < c["delta_norm"] <= hi])
    for split in sorted({c.get("donor_split") for c in cases if c.get("donor_split")}):
        summary[f"donor_{split}"] = agg([c for c in cases if c.get("donor_split") == split])
    return summary


# ============================================================================ trainer
class Trainer:
    def __init__(self, backend: Backend, cfg: TrainConfig, output: Path, log=print):
        self.backend = backend
        self.cfg = cfg
        self.output = Path(output)
        self.log = log
        self.model = backend.model
        self.device = backend.device
        rank, world = rank_world()
        self.rank, self.world = rank, world
        groups = self.model.memory.parameter_groups(cfg.optim.weight_decay)
        for g in groups:
            g["lr_base"] = cfg.optim.lr_memory
            g["name"] = "memory"
        named_action = getattr(self.model.backbone, "named_action_parameters", lambda: [])()
        if named_action:
            decay = [p for n, p in named_action if p.ndim >= 2 and "norm" not in n.lower() and not n.endswith("bias")]
            keep = [p for n, p in named_action if not (p.ndim >= 2 and "norm" not in n.lower() and not n.endswith("bias"))]
            groups.append({"params": decay, "weight_decay": cfg.optim.weight_decay,
                           "lr_base": cfg.optim.lr_action, "name": "action"})
            groups.append({"params": keep, "weight_decay": 0.0, "lr_base": cfg.optim.lr_action, "name": "action_no_decay"})
        groups = [g for g in groups if g["params"]]
        self.parameters = [p for g in groups for p in g["params"]]
        self.optimizer = torch.optim.AdamW(groups, lr=cfg.optim.lr_memory, betas=tuple(cfg.optim.betas),
                                           eps=cfg.optim.eps, weight_decay=cfg.optim.weight_decay)
        self.rows = backend.train_rows()
        self.updates_per_epoch = math.ceil(len(self.rows) / cfg.schedule.global_batch)
        self.total = cfg.schedule.epochs * self.updates_per_epoch
        self.update = 0
        self.loss_history: List[float] = []
        self._probe = None
        self.pairs: List[dict] = []
        if cfg.pairs.enabled:
            from .pairs import load_pairs
            self.pairs = load_pairs(cfg.pairs.file, "train", cfg.pairs.max_visual_distance, cfg.pairs.min_delta)
            if not self.pairs:
                raise ValueError(f"No training pairs left in {cfg.pairs.file} after the filters.")
            log(f"[pairs] {len(self.pairs)} counterfactual training pairs, weight {cfg.pairs.weight}, "
                f"{cfg.pairs.per_update}/update")

    # ------------------------------------------------------------- checkpoints
    def checkpoint_dir(self) -> Path:
        return self.output / "checkpoints"

    def state(self) -> dict:
        action = None
        if self.cfg.optim.lr_action > 0:
            action = {n: p.detach().cpu() for n, p in self.model.backbone.ab.backbone.mot.mixtures["action"].named_parameters()}
        return {"update": self.update, "memory": self.model.memory.state_dict(), "action": action,
                "optimizer": self.optimizer.state_dict(), "loss_history": self.loss_history,
                "config": self.cfg.to_dict(), "backend": self.backend.describe(),
                "torch_rng": torch.get_rng_state()}

    def save(self, tag: Optional[str] = None) -> Optional[Path]:
        if self.rank != 0:
            barrier()
            return None
        folder = self.checkpoint_dir()
        folder.mkdir(parents=True, exist_ok=True)
        name = tag or f"update_{self.update:06d}"
        path = folder / f"{name}.pt"
        temp = path.with_name(path.name + ".partial")
        torch.save(self.state(), temp)
        temp.replace(path)
        write_json(folder / "LATEST.json", {"file": path.name, "update": self.update})
        self._prune(keep={path.name})
        self.log(f"[checkpoint] update={self.update} -> {path}")
        barrier()
        return path

    def _prune(self, keep):
        folder = self.checkpoint_dir()
        files = sorted(folder.glob("update_*.pt"))
        epoch_ends = {f"update_{e * self.updates_per_epoch:06d}.pt" for e in range(1, self.cfg.schedule.epochs + 1)}
        recent = {p.name for p in files[-self.cfg.schedule.keep_last:]}
        for p in files:
            if p.name not in keep | recent | epoch_ends:
                p.unlink()

    def resume(self) -> bool:
        latest = self.checkpoint_dir() / "LATEST.json"
        if not latest.is_file():
            return False
        pointer = json.loads(latest.read_text(encoding="utf-8"))
        state = torch.load(self.checkpoint_dir() / pointer["file"], map_location="cpu", weights_only=False)
        if state["config"] != self.cfg.to_dict():
            raise ValueError("Config differs from the checkpoint; start a new output instead of resuming.")
        self.model.memory.load_state_dict(state["memory"], strict=True)
        if state.get("action") is not None:
            named = dict(self.model.backbone.ab.backbone.mot.mixtures["action"].named_parameters())
            with torch.no_grad():
                for n, v in state["action"].items():
                    named[n].copy_(v.to(named[n].device, named[n].dtype))
        self.optimizer.load_state_dict(state["optimizer"])
        self.update = int(state["update"])
        self.loss_history = list(state.get("loss_history", []))
        self.log(f"[resume] update={self.update} from {pointer['file']}")
        return True

    # ------------------------------------------------------------- guards
    def loss_guard(self) -> Optional[dict]:
        g = self.cfg.guard
        h = self.loss_history
        if any(not math.isfinite(x) for x in h[-1:]):
            return {"reason": "non-finite training loss", "update": self.update}
        if self.update < g.start_update or len(h) < g.loss_baseline_updates + g.loss_window:
            return None
        base = sorted(h[:g.loss_baseline_updates])[g.loss_baseline_updates // 2]
        recent = sorted(h[-g.loss_window:])[g.loss_window // 2]
        if recent > g.loss_factor * base:
            return {"reason": "training FM loss rose above guard", "update": self.update,
                    "initial_median": base, "recent_median": recent, "factor": g.loss_factor}
        return None

    def eval_guard(self, result: dict) -> Optional[dict]:
        g = self.cfg.guard
        if self.update < g.start_update:
            return None
        o = result["overall"]
        on, off = o.get("on/arm_rmse_rad"), o.get("off/arm_rmse_rad")
        if on is None or off is None:
            return None
        if on > (1 + g.eval_regression) * off:
            return {"reason": "memory-on offline error worse than memory-off", "update": self.update,
                    "on_arm_rmse_rad": on, "off_arm_rmse_rad": off, "allowed_regression": g.eval_regression}
        return None

    def stop_requested(self) -> bool:
        return broadcast_flag(self.rank == 0 and (self.output / "STOP.json").exists(), self.device)

    # ------------------------------------------------------------- one update
    def step(self) -> dict:
        cfg = self.cfg
        u = self.update + 1
        epoch = (u - 1) // self.updates_per_epoch + 1
        index = (u - 1) % self.updates_per_epoch
        if getattr(self, "_epoch", (None,))[0] != epoch:
            self._epoch = (epoch, epoch_rows(self.rows, epoch, cfg.seed))
        rows = self._epoch[1][index * cfg.schedule.global_batch:(index + 1) * cfg.schedule.global_batch]
        total = len(rows)
        mine = rows[self.rank::self.world]
        lrs = {}
        for group in self.optimizer.param_groups:
            group["lr"] = lr_at(u, self.total, group["lr_base"], cfg.optim.warmup_fraction, cfg.optim.min_lr_ratio)
            lrs[group["name"]] = group["lr"]
        self.model.train()
        started = time.monotonic()
        stats = {"loss": 0.0, "fm": 0.0, "endpoint": 0.0, "dropped": 0, "samples": 0}
        bins = {"sum": [0.0] * (len(TAU_BINS) - 1), "count": [0] * (len(TAU_BINS) - 1)}
        for m in range(0, len(mine), cfg.schedule.micro_batch):
            micro = mine[m:m + cfg.schedule.micro_batch]
            batch = self.backend.batch(micro)
            generator = torch.Generator().manual_seed(stable_seed(cfg.seed, u, self.rank, m))
            out = compute_loss(self.model, batch, cfg.v2.objective, generator)
            if not bool(torch.isfinite(out["loss"])):
                raise FloatingPointError(f"Non-finite loss at update {u}.")
            (out["loss"] * (len(micro) / total)).backward()
            n = len(micro)
            stats["loss"] += float(out["loss"]) * n
            stats["fm"] += float(out["fm"]) * n
            stats["endpoint"] += float(out.get("endpoint", torch.zeros(()))) * n
            stats["dropped"] += int(out["memory_dropped"].sum())
            stats["samples"] += n
            b = tau_bin_stats(out["tau"].cpu(), out["fm_unweighted"].cpu())
            for j in range(len(bins["sum"])):
                bins["sum"][j] += b["sum"][j]
                bins["count"][j] += b["count"][j]
        pair_stats = {"loss": 0.0, "samples": 0}
        if self.pairs:
            chosen = random.Random(stable_seed(cfg.seed, "pairs", u)).sample(
                self.pairs, min(cfg.pairs.per_update, len(self.pairs)))
            mine_pairs = chosen[self.rank::self.world]
            pair_total = 2 * len(chosen)
            for m in range(0, len(mine_pairs), cfg.schedule.micro_batch):
                group = mine_pairs[m:m + cfg.schedule.micro_batch]
                for reverse in (False, True):
                    _, swapped = self.backend.pair_batches(group, reverse)
                    generator = torch.Generator().manual_seed(stable_seed(cfg.seed, "pair-step", u, self.rank, m, reverse))
                    out = compute_loss(self.model, swapped, cfg.v2.objective, generator,
                                       drop=torch.zeros(len(group), dtype=torch.bool))
                    if not bool(torch.isfinite(out["loss"])):
                        raise FloatingPointError(f"Non-finite pair loss at update {u}.")
                    (out["loss"] * cfg.pairs.weight * (len(group) / pair_total)).backward()
                    pair_stats["loss"] += float(out["loss"]) * len(group)
                    pair_stats["samples"] += len(group)
        if self.world > 1:
            for p in self.parameters:
                if p.grad is None:
                    p.grad = torch.zeros_like(p)
                torch.distributed.all_reduce(p.grad)
            packed = torch.tensor([stats["loss"], stats["fm"], stats["endpoint"], stats["dropped"], stats["samples"],
                                   *bins["sum"], *bins["count"], pair_stats["loss"], pair_stats["samples"]],
                                  device=self.device, dtype=torch.float64)
            torch.distributed.all_reduce(packed)
            values = packed.tolist()
            pair_stats = {"loss": values[-2], "samples": values[-1]}
            values = values[:-2]
            stats = dict(zip(("loss", "fm", "endpoint", "dropped", "samples"), values[:5]))
            k = len(bins["sum"])
            bins = {"sum": values[5:5 + k], "count": values[5 + k:5 + 2 * k]}
        norm = torch.nn.utils.clip_grad_norm_(self.parameters, cfg.optim.clip)
        if not bool(torch.isfinite(norm)):
            raise FloatingPointError(f"Non-finite gradient norm at update {u}.")
        self.optimizer.step()
        self.optimizer.zero_grad(set_to_none=True)
        self.update = u
        count = max(1, stats["samples"])
        fm = stats["fm"] / count
        self.loss_history.append(fm)
        record = {"update": u, "epoch": epoch, "lr": lrs, "loss": stats["loss"] / count, "fm": fm,
                  "endpoint": stats["endpoint"] / count, "memory_dropped_fraction": stats["dropped"] / count,
                  "samples": int(stats["samples"]), "grad_norm": float(norm),
                  "fm_by_tau": {f"{TAU_BINS[j]:.2f}-{min(1.0, TAU_BINS[j + 1]):.2f}":
                                (bins["sum"][j] / bins["count"][j] if bins["count"][j] else None)
                                for j in range(len(bins["sum"]))},
                  "seconds": time.monotonic() - started}
        if pair_stats["samples"]:
            record["pair_loss"] = pair_stats["loss"] / pair_stats["samples"]
            record["pair_samples"] = int(pair_stats["samples"])
        if torch.cuda.is_available() and self.device.type == "cuda":
            record["peak_gpu_bytes"] = torch.cuda.max_memory_allocated(self.device)
        return record

    # ------------------------------------------------------------- probes
    @torch.no_grad()
    def probe(self) -> dict:
        if self._probe is None:
            self._probe = self.backend.batch(self.backend.probe_rows())
        model = self.model
        model.eval()
        batch = self._probe
        out = {"update": self.update, "gate": gate_profile(model)}
        sens = history_sensitivity(model, batch, taus=(0.3, 0.6, 0.8, 0.9, 0.95, 1.0))
        out["sensitivity"] = sens
        out["sensitivity_summary"] = summarize_sensitivity(sens)
        conditions = model.conditions(batch)
        noise = torch.randn(batch["actions"].shape, generator=torch.Generator().manual_seed(0)).to(self.device)
        out["attention"] = {}
        for tau in (0.95, 0.5, 0.1):
            noisy = (1 - tau) * batch["actions"].float() + tau * noise
            out["attention"][str(tau)] = {str(k): v for k, v in attention_report(model, conditions, noisy, tau).items()}
        model.train()
        return out

    # ------------------------------------------------------------- loop
    def run(self, dry_run: int = 0, resume: bool = False) -> dict:
        cfg = self.cfg
        out = self.output
        if self.rank == 0:
            out.mkdir(parents=True, exist_ok=True)
        barrier()
        resumed = self.resume() if resume else False
        if not resumed and self.rank == 0 and not dry_run:
            if (self.checkpoint_dir() / "LATEST.json").exists():
                raise ValueError("Checkpoint exists; pass --resume or use a new output.")
            write_json(out / "CONFIG.json", {"config": cfg.to_dict(), "backend": self.backend.describe(),
                                             "updates_per_epoch": self.updates_per_epoch, "total_updates": self.total,
                                             "train_rows": len(self.rows), "world_size": self.world})
        if not resumed:
            parity = self.init_parity()
            if self.rank == 0 and not dry_run:
                write_json(out / "INIT_PARITY.json", parity)
            if not parity["exact"]:
                raise ValueError(f"Zero-initialised memory does not reproduce the start model: {parity}")
            if not dry_run and cfg.schedule.eval_every > 0:
                result = evaluate(self.backend, self.backend.eval_rows(cfg.eval.windows), cfg, self.log)
                if self.rank == 0:
                    write_json(out / "eval" / "update_000000.json", result)
        target = dry_run if dry_run else self.total
        while self.update < target:
            if self.stop_requested():
                if not dry_run:
                    self.save()
                self.log("[stop] STOP.json found; checkpoint saved")
                return {"stopped": True, "update": self.update}
            record = self.step()
            if self.rank == 0:
                self.log("[train] " + json.dumps({k: record[k] for k in ("update", "loss", "fm", "endpoint", "pair_loss",
                                                                        "grad_norm", "seconds") if k in record}))
                if not dry_run:
                    append_jsonl(out / "metrics.jsonl", record)
            trip = self.loss_guard()
            if dry_run:
                continue
            if cfg.schedule.probe_every and self.update % cfg.schedule.probe_every == 0 and self.rank == 0:
                append_jsonl(out / "probes.jsonl", self.probe())
            if cfg.schedule.eval_every and (self.update % cfg.schedule.eval_every == 0 or self.update == self.total):
                result = evaluate(self.backend, self.backend.eval_rows(cfg.eval.windows), cfg, self.log)
                if self.rank == 0:
                    write_json(out / "eval" / f"update_{self.update:06d}.json", result)
                trip = trip or self.eval_guard(result)
            if broadcast_flag(trip is not None, self.device):
                if self.rank == 0:
                    write_json(out / "GUARD.json", trip or {"reason": "guard tripped on rank 0"})
                self.save()
                self.log(f"[guard] {trip}")
                return {"guard": trip, "update": self.update}
            if self.update % cfg.schedule.save_every == 0 or self.update % self.updates_per_epoch == 0 or self.update == self.total:
                self.save()
        if self.rank == 0 and not dry_run:
            write_json(out / "COMPLETE.json", {"update": self.update, "epochs": cfg.schedule.epochs})
        return {"complete": True, "update": self.update}

    @torch.no_grad()
    def init_parity(self) -> dict:
        """With zero-initialised memory, memory on / null / off must give identical velocities."""
        model = self.model
        model.eval()
        batch = self.backend.batch(self.backend.probe_rows())
        conditions = model.conditions(batch)
        noise = torch.randn(batch["actions"].shape, generator=torch.Generator().manual_seed(1)).to(self.device)
        result = {"exact": True, "max_abs": {}}
        for tau in (1.0, 0.7, 0.3):
            t = torch.full((noise.shape[0],), 1000.0 * tau, device=self.device)
            x = (1 - tau) * batch["actions"].float() + tau * noise
            ref = model.velocity(x, t, conditions, "off")
            for mode in ("on", "null"):
                v = model.velocity(x, t, conditions, mode)
                diff = float((v.float() - ref.float()).abs().max())
                result["max_abs"][f"{mode}@{tau}"] = diff
                result["exact"] = result["exact"] and bool(torch.equal(v, ref))
        # The memory-off path must be the start model itself (dense ABModel with its own inputs).
        reference = getattr(self.backend, "base_reference", None)
        if reference is not None:
            result["base_relative_l2"] = {}
            for tau in (1.0, 0.7, 0.3):
                t = torch.full((noise.shape[0],), 1000.0 * tau, device=self.device)
                x = (1 - tau) * batch["actions"].float() + tau * noise
                ours = model.velocity(x, t, conditions, "off").float()
                theirs = reference(self.backend.probe_rows(), x, t).float()
                rel = float((ours - theirs).flatten(1).norm(dim=1).max() / theirs.flatten(1).norm(dim=1).min().clamp_min(1e-6))
                result["base_relative_l2"][str(tau)] = rel
                result["exact"] = result["exact"] and rel <= BASE_TOLERANCE
            result["base_tolerance"] = BASE_TOLERANCE
        model.train()
        return result


# ============================================================================ dense backend
class DenseBackend(Backend):
    def __init__(self, cfg: TrainConfig, device: torch.device, train_action: bool):
        from . import dense
        self.dense = dense
        self.cfg = cfg
        self.device = device
        self.spec = dense.DenseSpec.from_dict(cfg.dense)
        self.ab, self.info = dense.load_ab_model(self.spec, cfg.init_checkpoint, str(device))
        if cfg.base_memory == "none" and hasattr(self.ab, "memory"):
            del self.ab.memory                  # gate-0 diagnostic base only
        self.s1 = dense.S1Policy(period=cfg.s1_period) if cfg.base_memory == "s1" else None
        self.features = dense.FeatureStore(Path(cfg.features))
        self.features.require(self.info["video_digest"], self.info["dense_identity"])
        self.episodes = dense.EpisodeStore(self.spec)
        self.adapter = dense.DenseActionAdapter(self.ab, train_action=train_action, base_memory=cfg.base_memory)
        self.model = MemoryV2Model(self.adapter, cfg.v2.memory)
        self.model.memory.to(device=device, dtype=torch.float32)
        from fastwam.memory_s1.common import ReleaseNormalizer
        self.normaliser = ReleaseNormalizer(dense.dense_config(self.spec)["paths"]["stats"])
        self._records = dense.records(self.spec)

    def train_rows(self):
        return [{"episode_id": r["episode_id"], "anchor": a} for r in self._records if r["split"] == "train"
                for a in range(r["length"])]

    def batch(self, rows):
        return self.dense.make_batch(rows, self.episodes, self.features, self.cfg.v2.history, self.device,
                                     s1=self.s1, spec=self.spec)

    @torch.no_grad()
    def base_reference(self, rows, noisy, timestep):
        """ABModel.velocity on its own Dataset.at() inputs (scale 1 with s1, 0 without), row by row."""
        if not hasattr(self, "_ab_data"):
            self._ab_data = self.dense.ab_dataset(self.spec, self.info["dense_identity"], str(self.device))
        was_training = self.ab.training
        self.ab.eval()
        out = []
        for i, row in enumerate(rows):
            period = self.cfg.s1_period
            full = dict(row, T=period, phase=self.dense.s1_phase(self.spec, row, period))
            b = self._ab_data.at(full)
            conditions = self.ab.conditions(b)
            out.append(self.ab.velocity(noisy[i:i + 1], timestep[i:i + 1], conditions,
                                        1.0 if self.cfg.base_memory == "s1" else 0.0))
        self.ab._eval_features.clear()
        self.ab.train(was_training)
        return torch.cat(out)

    def probe_rows(self):
        val = [r for r in self._records if r["split"] == "val"]
        rows = []
        for r in val:
            for a in (min(r["length"] - 1, 120), min(r["length"] - 1, 240)):
                rows.append({"episode_id": r["episode_id"], "anchor": a})
        return rows[:max(2, self.cfg.schedule.micro_batch)]

    def eval_rows(self, limit):
        rows = self.dense.windows(self.spec)
        for row in rows:
            row["kind"] = self.dense.window_kind(row)
        if not limit or limit >= len(rows):
            return rows
        groups = {}
        for row in rows:                                   # stratify by task/split/kind, deterministic
            groups.setdefault((row["task"], row["split"], row["kind"]), []).append(row)
        ordered = []
        for key in sorted(groups):
            g = groups[key]
            random.Random(stable_seed(self.cfg.seed, "eval-subset", key)).shuffle(g)
            ordered.append(g)
        out = []
        while len(out) < limit and any(ordered):
            for g in ordered:
                if g and len(out) < limit:
                    out.append(g.pop())
        return sorted(out, key=lambda r: r["id"])

    def window_case(self, row, normalised_sample, b, batch):
        return self.dense.window_metrics(normalised_sample, batch["actions"][b], batch["action_valid"][b], self.normaliser)

    def noise(self, row, shape):
        return self.dense.window_noise(row, shape, self.device)

    def describe(self):
        return {"kind": "dense", "spec": {k: str(v) for k, v in asdict(self.spec).items()}, "init": self.info,
                "base_memory": self.cfg.base_memory, "s1_period": self.cfg.s1_period,
                "features": {k: self.features.manifest.get(k) for k in ("version", "video_digest", "dense_identity")}}


# ============================================================================ CLI
def setup_distributed():
    world = int(os.environ.get("WORLD_SIZE", "1"))
    local = int(os.environ.get("LOCAL_RANK", "0"))
    if torch.cuda.is_available():
        torch.cuda.set_device(local)
        device = torch.device("cuda", local)
    else:
        device = torch.device("cpu")
    if world > 1 and not torch.distributed.is_initialized():
        torch.distributed.init_process_group("nccl" if device.type == "cuda" else "gloo")
    return device


def logger(output: Optional[Path]):
    rank, _ = rank_world()

    def log(message: str):
        if rank != 0:
            return
        line = time.strftime("%Y-%m-%dT%H:%M:%S") + " " + message
        print(line, flush=True)
        if output is not None:
            output.mkdir(parents=True, exist_ok=True)
            with (output / "train.log").open("a", encoding="utf-8") as f:
                f.write(line + "\n")
    return log


def cmd_features(cfg: TrainConfig, args) -> None:
    from . import dense
    device = setup_distributed()
    if rank_world()[1] != 1:
        raise ValueError("Build features on one GPU.")
    spec = dense.DenseSpec.from_dict(cfg.dense)
    ab, info = dense.load_ab_model(spec, "source", str(device))
    episodes = [r["episode_id"] for r in dense.records(spec)]
    frames = sum(r["length"] for r in dense.records(spec))
    need = frames * 120 * 3072 * 2
    directory = Path(cfg.features)
    directory.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(directory).free
    log = logger(directory)
    log(f"[features] {len(episodes)} episodes, {frames} frames, ~{need / 2 ** 30:.1f} GiB, free {free / 2 ** 30:.1f} GiB")
    if free < need * 1.05:
        raise OSError("Not enough disk for the feature cache.")
    store = dense.FeatureStore(directory)
    store.build(ab, info, spec, episodes, batch=cfg.feature_batch, log=log)
    log("[features] complete")


def cmd_train(cfg: TrainConfig, args) -> None:
    if cfg.optim.lr_action > HIGH_ACTION_LR and not args.allow_high_action_lr:
        raise ValueError(f"optim.lr_action={cfg.optim.lr_action} > {HIGH_ACTION_LR}: dense A at 1e-4 raised its own "
                         "training loss 3.8x and the offline error 3x. Pass --allow-high-action-lr to override.")
    device = setup_distributed()
    output = Path(cfg.output)
    log = logger(output)
    torch.manual_seed(cfg.seed)
    backend = DenseBackend(cfg, device, train_action=cfg.optim.lr_action > 0)
    trainer = Trainer(backend, cfg, output, log)
    log(f"[train] rows={len(trainer.rows)} updates/epoch={trainer.updates_per_epoch} total={trainer.total} "
        f"world={trainer.world} trainable={sum(p.numel() for p in trainer.parameters)}")
    result = trainer.run(dry_run=args.dry_run, resume=args.resume)
    log("[train] " + json.dumps(result))


def cmd_evaluate(cfg: TrainConfig, args) -> None:
    device = setup_distributed()
    output = Path(args.output or (Path(cfg.output) / "eval_full"))
    log = logger(output)
    backend = DenseBackend(cfg, device, train_action=False)
    label = "init"
    if args.checkpoint and args.checkpoint != "init":
        state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
        backend.model.memory.load_state_dict(state["memory"], strict=True)
        if state.get("action") is not None:
            named = dict(backend.ab.backbone.mot.mixtures["action"].named_parameters())
            with torch.no_grad():
                for n, v in state["action"].items():
                    named[n].copy_(v.to(named[n].device, named[n].dtype))
        label = Path(args.checkpoint).stem
    if args.windows is not None:
        cfg.eval.windows = args.windows
    if args.guidance:
        cfg.eval.guidance_scales = tuple(args.guidance)
    result = evaluate(backend, backend.eval_rows(cfg.eval.windows), cfg, log)
    if rank_world()[0] == 0:
        write_json(output / f"{label}.json", {"checkpoint": args.checkpoint, "backend": backend.describe(), **result})
        log(json.dumps(result["overall"], indent=2))


def cmd_pr(cfg: TrainConfig, args) -> None:
    """PR evaluation of a memory_v2 checkpoint ('init' = the start model, v2 inert) on matched-present pairs."""
    from .pairs import load_pairs
    device = setup_distributed()
    path = args.pairs or cfg.pairs.file
    if not path:
        raise SystemExit("Give --pairs <pairs json> (scripts/memory_v2/find_pairs.py output).")
    pairs = load_pairs(path, args.pair_split, args.max_visual_distance, args.min_delta)
    if args.limit and args.limit < len(pairs):           # deterministic subset across tasks, not the first N
        pairs = sorted(random.Random(stable_seed("pr-subset", args.limit)).sample(pairs, args.limit),
                       key=lambda p: (p["task"], p["query"]["episode_id"], p["query"]["anchor"]))
    output = Path(args.output or (Path(cfg.output) / "pr"))
    log = logger(output)
    backend = DenseBackend(cfg, device, train_action=False)
    label = "init"
    if args.checkpoint and args.checkpoint != "init":
        state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
        backend.model.memory.load_state_dict(state["memory"], strict=True)
        label = Path(args.checkpoint).stem
    log(f"[pr] {len(pairs)} pairs ({args.pair_split}) from {path}; checkpoint {args.checkpoint or 'init'}")
    result = evaluate_pairs(backend, pairs, cfg, modes=tuple(cfg.eval.modes), batch_size=cfg.eval.batch, log=log,
                            swap=args.swap)
    suffix = "" if args.swap == "all" else f"_{args.swap}"
    if rank_world()[0] == 0:
        result.update(checkpoint=args.checkpoint, pairs_file=str(path), pair_split=args.pair_split,
                      backend=backend.describe())
        write_json(output / f"pr_{label}_{args.pair_split}{suffix}.json", result)
        log("[pr] summary " + json.dumps(result["summary"], indent=1))
        log(f"[pr] written {output / f'pr_{label}_{args.pair_split}{suffix}.json'}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("features", "train", "evaluate", "pr"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--set", action="append", default=[], help="override, e.g. --set optim.lr_memory=5e-5")
    parser.add_argument("--dry-run", type=int, default=0, help="train: run N updates, no saving/eval")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--allow-high-action-lr", action="store_true")
    parser.add_argument("--checkpoint", help="evaluate: memory_v2 checkpoint or 'init'")
    parser.add_argument("--windows", type=int, help="evaluate: number of windows (0 = all)")
    parser.add_argument("--guidance", type=float, nargs="*", help="evaluate: extra guidance scales")
    parser.add_argument("--output", help="evaluate/pr: output folder")
    parser.add_argument("--pairs", help="pr: pairs JSON (default: pairs.file of the config)")
    parser.add_argument("--pair-split", default="val", choices=("val", "train"), help="pr: which pair list")
    parser.add_argument("--max-visual-distance", type=float, default=None, help="pr: filter pairs")
    parser.add_argument("--min-delta", type=float, default=0.0, help="pr: filter pairs")
    parser.add_argument("--limit", type=int, default=0, help="pr: first N pairs only")
    parser.add_argument("--swap", default="all", choices=("all", "content", "clock"),
                        help="pr: what of the partner's history is swapped in (see evaluate_pairs)")
    args = parser.parse_args(argv)
    cfg = load_config(args.config, args.set)
    try:
        {"features": cmd_features, "train": cmd_train, "evaluate": cmd_evaluate, "pr": cmd_pr}[args.command](cfg, args)
    finally:
        if torch.distributed.is_available() and torch.distributed.is_initialized():
            torch.distributed.destroy_process_group()


if __name__ == "__main__":
    main()
