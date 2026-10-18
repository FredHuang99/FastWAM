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

    def __post_init__(self):
        if self.anchor_frames < 0 or self.recent_frames < 0:
            raise ValueError("anchor_frames and recent_frames must be non-negative.")
        if self.landmark_stride < 1 or self.recent_stride < 1:
            raise ValueError("Strides must be positive.")
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
        if not 0.0 <= self.memory_dropout < 1.0:
            raise ValueError("memory_dropout must be in [0, 1).")
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
            built[name] = kind(**section)
        return cls(**built)

    def to_dict(self) -> dict:
        return {name: asdict(getattr(self, name)) for name in ("history", "memory", "objective", "guidance")}
