"""Typed configuration for the read-time-selection memory (memory_v2).

Every width is configurable so the unit tests can run on CPU with tiny shapes;
the defaults match the released FastWAM RoboTwin/RMBench backbone
(Wan2.2-TI2V-5B video expert 3072, 1B action expert 1024, 120 tokens/frame on a
12x10 patch grid, 30 action blocks).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields
from typing import Any, Mapping


ROLE_ANCHOR = 0      # earliest observations of the episode (initial scene)
ROLE_LANDMARK = 1    # fixed-stride landmarks from the start of the episode
ROLE_RECENT = 2      # short dense window before the current observation
ROLE_CURRENT = 3     # the current observation (normally excluded; it is already in the action KV)
NUM_ROLES = 4


def _tuple(value, length=None, name="value"):
    result = tuple(int(v) for v in value)
    if length is not None and len(result) != length:
        raise ValueError(f"{name} must have {length} integers, got {value!r}.")
    return result


@dataclass(frozen=True)
class HistoryPolicyConfig:
    """Which past observations are visible to the action expert at a decision.

    The SAME pure function is used offline (dense record cache) and online
    (append-only archive of executed-target observations), so a training sample
    and a deployment decision with the same available ids see the same history.
    """

    anchor_frames: int = 1          # keep the first `anchor_frames` available ids (0 = initial scene)
    landmark_stride: int = 24       # keep ids that are multiples of this (decision cadence in dense-joint)
    recent_frames: int = 2          # keep the nearest ids at current - k*recent_stride, k=1..recent_frames
    recent_stride: int = 8
    max_frames: int = 48            # hard cap; landmarks are thinned uniformly, anchors/recent always kept
    include_current: bool = False   # the current frame already reaches the action expert through its KV
    # Training only (mixed-stride arm, 11-04): when non-empty, every TRAINING sample (and every counterfactual
    # pair, one stride for both of its rows) draws its landmark stride from this set, deterministically from the
    # seed, epoch and row. Evaluation windows and the online archive always use `landmark_stride`, which can be
    # set freely at inference (online --set memory_v2.history.landmark_stride=K). () = fixed stride, as before.
    landmark_strides: tuple = ()
    # ---- 11-06 periodic mode (the "every decision frame" rule, after memory_s1's modulo-with-decisions rule).
    #   mode = "landmark": the rule above (anchors + recent window + fixed-stride landmarks), unchanged.
    #   mode = "periodic": anchors plus EVERY earlier frame a whole number of periods before the current one
    #       (current - T, current - 2T, ...). With T = the executed steps per decision (8 in the official protocol)
    #       that is every past decision frame. The `recent_frames` nearest of them carry the recent role;
    #       landmark_stride / recent_stride / landmark_strides are not used. Above max_frames the older periodic
    #       frames are thinned uniformly (anchors and the recent ones are always kept).
    #   period:    T for evaluation windows and the online archive (free at inference: --set memory_v2.history.period=K).
    #   periods:   training only: every training sample (and every counterfactual pair, one draw for both rows)
    #              draws its own T from this set, so training has seen every period. () = always `period`.
    #   irregular: training only: probability that a sample walks back with a fresh gap per step (each drawn from
    #              `periods`): the history of an irregular / adaptive-execution schedule.
    mode: str = "landmark"
    period: int = 8
    periods: tuple = ()
    irregular: float = 0.0

    def __post_init__(self):
        object.__setattr__(self, "landmark_strides", tuple(int(v) for v in (self.landmark_strides or ())))
        object.__setattr__(self, "periods", tuple(int(v) for v in (self.periods or ())))
        if self.anchor_frames < 0 or self.recent_frames < 0:
            raise ValueError("anchor_frames and recent_frames must be non-negative.")
        if self.landmark_stride < 1 or self.recent_stride < 1 or any(v < 1 for v in self.landmark_strides):
            raise ValueError("Strides must be positive.")
        if self.mode not in ("landmark", "periodic"):
            raise ValueError(f"history.mode must be landmark or periodic, got {self.mode!r}.")
        if self.period < 1 or any(v < 1 for v in self.periods):
            raise ValueError("Periods must be positive.")
        if not 0.0 <= float(self.irregular) <= 1.0:
            raise ValueError("history.irregular is a probability in [0, 1].")
        if self.mode == "landmark" and (self.periods or self.irregular):
            raise ValueError("history.periods / history.irregular need history.mode=periodic.")
        if self.mode == "periodic" and self.landmark_strides:
            raise ValueError("history.landmark_strides is the landmark-mode training draw; use history.periods.")
        if self.irregular and not self.periods:
            raise ValueError("history.irregular draws its gaps from history.periods; set them.")
        minimum = self.anchor_frames + self.recent_frames + int(self.include_current)
        if self.max_frames < max(1, minimum):
            raise ValueError(f"max_frames={self.max_frames} cannot hold anchors+recent+current={minimum}.")


@dataclass(frozen=True)
class MemoryV2Config:
    """Memory tokenizer + per-layer read-time injectors."""

    video_dim: int = 3072           # width of the cached final-layer video features
    action_hidden: int = 1024       # ActionDiT hidden width
    memory_dim: int = 1024          # width of memory tokens / injector attention
    heads: int = 8
    grid: tuple = (12, 10)          # patch grid of one cached frame (rows, cols)
    pool: tuple = (1, 1)            # spatial average pooling of the grid before projection
    injection_layers: tuple = (4, 9, 14, 19, 24, 29)
    num_action_layers: int = 30
    null_tokens: int = 4            # always-valid learned tokens: attention sink + "no memory" branch
    time_features: int = 128        # sinusoid width for each of (age, absolute index)
    spatial_features: int = 64      # sinusoid width for each of (row, col)
    age_unit: float = 1.0           # frames per unit in the age sinusoid
    absolute_time: bool = True      # also encode the absolute frame index (False: relative age only;
                                    # ablation against an episode-clock shortcut, see Phase 0c)
    tau_gate: bool = True           # learned per-layer memory strength as a function of the noise level
    tau_gate_hidden: int = 64
    zero_init_output: bool = True   # memory residual starts exactly at zero (base behaviour preserved)
    layer_norm_eps: float = 1e-6
    # ---- plan v7 N1 (11-05): how the action expert reads history.
    #   inject    : the tokenizer + read-time injectors above (cached final-layer features, `injection_layers`)
    #   kv_replay : every replayed action layer's video attention also sees the history frames' OWN per-layer video
    #               K/V (each history frame prefilled alone, exactly like a current frame), at temporal RoPE
    #               position -rank (rank 1 = most recent), plus zero-initialised role / elapsed-time key embeddings and
    #               low-rank K/V adapters; out = base + g_l(tau) * (L(attention over history+current) - L(current only)),
    #               g_l zero at start (exact base model). See replay.py.
    read: str = "inject"
    replay_layers: tuple = ()       # () = every action layer
    replay_rank: int = 16           # low-rank K / V adapters on history keys (0 = none)
    replay_time_buckets: int = 12   # log2 buckets of the elapsed time in replay_time_unit frames
    replay_time_unit: float = 8.0   # one decision (execute 8)
    replay_chunk: int = 32          # history frames per video prefill call (memory bound)

    def __post_init__(self):
        object.__setattr__(self, "grid", _tuple(self.grid, 2, "grid"))
        object.__setattr__(self, "pool", _tuple(self.pool, 2, "pool"))
        object.__setattr__(self, "injection_layers", _tuple(self.injection_layers, None, "injection_layers"))
        if self.memory_dim % self.heads:
            raise ValueError("memory_dim must be divisible by heads.")
        if (self.memory_dim // self.heads) % 2:
            raise ValueError("Head width must be even.")
        rows, cols = self.grid
        pr, pc = self.pool
        if pr < 1 or pc < 1 or rows % pr or cols % pc:
            raise ValueError(f"pool={self.pool} must divide grid={self.grid}.")
        layers = self.injection_layers
        if not layers or len(set(layers)) != len(layers) or list(layers) != sorted(layers):
            raise ValueError("injection_layers must be unique and increasing.")
        if layers[0] < 0 or layers[-1] >= self.num_action_layers:
            raise ValueError("injection_layers must index existing action blocks.")
        if self.null_tokens < 1:
            raise ValueError("At least one null token is required (keeps attention defined for empty history).")
        if self.time_features % 2 or self.spatial_features % 2:
            raise ValueError("Sinusoid widths must be even.")
        object.__setattr__(self, "replay_layers", _tuple(self.replay_layers, None, "replay_layers"))
        if self.read not in ("inject", "kv_replay"):
            raise ValueError(f"Unknown read={self.read} (inject | kv_replay).")
        rl = self.replay_layers
        if rl and (len(set(rl)) != len(rl) or list(rl) != sorted(rl) or rl[0] < 0 or rl[-1] >= self.num_action_layers):
            raise ValueError("replay_layers must be unique, increasing and index existing action blocks.")
        if self.replay_rank < 0 or self.replay_time_buckets < 1 or self.replay_time_unit <= 0 or self.replay_chunk < 1:
            raise ValueError("Invalid replay settings.")

    @property
    def replayed_layers(self) -> tuple:
        if self.read != "kv_replay":
            return ()
        return self.replay_layers or tuple(range(self.num_action_layers))

    @property
    def tokens_per_frame(self) -> int:
        return (self.grid[0] // self.pool[0]) * (self.grid[1] // self.pool[1])


@dataclass(frozen=True)
class ObjectiveConfig:
    """Training objective: flow matching + endpoint anchor + memory dropout."""

    tau_mode: str = "mixture"       # uniform | shift | mixture
    tau_shift: float = 1.0          # sigma = phi(u, shift) for mode shift / the base of mixture
    high_noise_prob: float = 0.3    # mixture: probability of drawing tau ~ U[high_noise_low, 1)
    high_noise_low: float = 0.8
    weight_mode: str = "bell_floor" # bell | bell_floor | uniform
    weight_shift: float = 1.0       # shift used for the bell normalisation constant (released code: training shift)
    weight_floor: float = 0.25      # bell_floor: max(bell, floor) keeps tau ~ 1 supervised
    endpoint_weight: float = 1.0    # extra tau = 1 (pure noise) term, unit weight; 0 disables
    memory_dropout: float = 0.15    # probability a sample sees only the null memory tokens (enables guidance)

    def __post_init__(self):
        if self.tau_mode not in ("uniform", "shift", "mixture"):
            raise ValueError(f"Unknown tau_mode={self.tau_mode}.")
        if self.weight_mode not in ("bell", "bell_floor", "uniform"):
            raise ValueError(f"Unknown weight_mode={self.weight_mode}.")
        if not 0.0 <= self.high_noise_prob <= 1.0 or not 0.0 <= self.high_noise_low < 1.0:
            raise ValueError("Invalid high-noise mixture.")
        if not 0.0 <= self.memory_dropout <= 1.0:
            raise ValueError("memory_dropout must be in [0, 1] (1 = history never seen: capacity-only control).")
        if self.tau_shift <= 0 or self.weight_shift <= 0:
            raise ValueError("Shifts must be positive.")
        if self.endpoint_weight < 0 or self.weight_floor < 0:
            raise ValueError("Weights must be non-negative.")


@dataclass(frozen=True)
class GuidanceConfig:
    """Inference: memory classifier-free guidance applied only at high noise."""

    steps: int = 10
    shift: float = 1.0
    scale: float = 1.0              # 1.0 = no guidance
    min_sigma: float = 0.7          # guidance only on steps whose sigma >= min_sigma

    def __post_init__(self):
        if self.steps < 1 or self.shift <= 0 or not 0.0 <= self.min_sigma <= 1.0:
            raise ValueError("Invalid guidance configuration.")


@dataclass(frozen=True)
class V2Config:
    history: HistoryPolicyConfig = field(default_factory=HistoryPolicyConfig)
    memory: MemoryV2Config = field(default_factory=MemoryV2Config)
    objective: ObjectiveConfig = field(default_factory=ObjectiveConfig)
    guidance: GuidanceConfig = field(default_factory=GuidanceConfig)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any] | None) -> "V2Config":
        value = dict(value or {})
        parts = {"history": HistoryPolicyConfig, "memory": MemoryV2Config,
                 "objective": ObjectiveConfig, "guidance": GuidanceConfig}
        unknown = set(value) - set(parts)
        if unknown:
            raise ValueError(f"Unknown memory_v2 sections: {sorted(unknown)}.")
        built = {}
        for name, kind in parts.items():
            section = dict(value.get(name) or {})
            allowed = {f.name for f in fields(kind)}
            extra = set(section) - allowed
            if extra:
                raise ValueError(f"Unknown keys in memory_v2.{name}: {sorted(extra)}.")
            for f in fields(kind):                # YAML 1.1 reads 1e-06 as a string: coerce numeric fields
                v = section.get(f.name)
                if isinstance(v, str) and type(f.default) in (float, int) and not isinstance(f.default, bool):
                    try:
                        section[f.name] = float(v) if isinstance(f.default, float) else int(float(v))
                    except ValueError:
                        raise ValueError(f"memory_v2.{name}.{f.name} must be a number, got {v!r}.") from None
            built[name] = kind(**section)
        return cls(**built)

    def to_dict(self) -> dict:
        out = {name: asdict(getattr(self, name)) for name in ("history", "memory", "objective", "guidance")}
        # landmark_strides (11-04) is left out while empty, so configs and checkpoints written before it existed
        # still compare equal (Trainer.resume requires state["config"] == cfg.to_dict()).
        if not out["history"].get("landmark_strides"):
            out["history"].pop("landmark_strides", None)
        # The periodic-mode fields (11-06) are left out in landmark mode for the same reason.
        if out["history"].get("mode", "landmark") == "landmark":
            for key in ("mode", "period", "periods", "irregular"):
                out["history"].pop(key, None)
        # The kv_replay fields (11-05) are left out for read == "inject" for the same reason.
        if out["memory"].get("read", "inject") == "inject":
            for key in ("read", "replay_layers", "replay_rank", "replay_time_buckets", "replay_time_unit", "replay_chunk"):
                out["memory"].pop(key, None)
        return out
