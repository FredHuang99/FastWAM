"""Read-time-selection memory: tokenizer, per-layer injectors and the tau gate.

Design (contrast with memory_s1):
  * No learnable-query bottleneck. The 32 action tokens of every injected
    ActionDiT layer are themselves the queries, so what is read depends on the
    current noisy action, the denoising level and the layer.
  * Memory tokens keep per-patch detail of every selected frame (optionally
    pooled), with relative-age, absolute-index, spatial and role encodings.
  * Learned null tokens are always valid: they keep attention defined for an
    empty history and provide the "no memory" branch used by memory dropout and
    classifier-free memory guidance.
  * The output projection is zero-initialised, so the backbone is reproduced
    exactly at initialisation without shrinking gradients through a tiny gate.
  * An optional tau gate learns how strongly each layer uses memory as a function
    of the noise level; it is an interpretable mechanism read-out.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import torch
from torch import nn
from torch.nn import functional as F

from .config import MemoryV2Config, NUM_ROLES


def sinusoid(values: torch.Tensor, width: int, max_period: float = 10000.0) -> torch.Tensor:
    """[...] -> [..., width] float32 sinusoid features."""
    half = width // 2
    frequency = torch.exp(-math.log(max_period) * torch.arange(half, device=values.device, dtype=torch.float32) / half)
    phase = values.float().unsqueeze(-1) * frequency
    return torch.cat((phase.cos(), phase.sin()), dim=-1)


@dataclass
class MemoryTokens:
    tokens: torch.Tensor        # [B, T, D] (null tokens first)
    valid: torch.Tensor         # [B, T] bool, True = attend
    is_history: torch.Tensor    # [B, T] bool, False for null tokens
    frame_slot: torch.Tensor    # [B, T] long, index into the history frame axis (-1 for null)
    role: torch.Tensor          # [B, T] long, ROLE_* (-1 for null)

    def without_history(self) -> "MemoryTokens":
        return MemoryTokens(self.tokens, self.valid & ~self.is_history, self.is_history, self.frame_slot, self.role)

    def drop_history(self, drop: torch.Tensor) -> "MemoryTokens":
        """drop: [B] bool; dropped samples keep only the null tokens."""
        valid = self.valid & ~(drop.to(self.valid.device)[:, None] & self.is_history)
        return MemoryTokens(self.tokens, valid, self.is_history, self.frame_slot, self.role)


class MemoryTokenizer(nn.Module):
    """Cached frame features [B, N, P, C] -> memory tokens [B, K + N*P', D]."""

    def __init__(self, cfg: MemoryV2Config):
        super().__init__()
        self.cfg = cfg
        self.norm = nn.LayerNorm(cfg.video_dim, eps=cfg.layer_norm_eps)
        self.project = nn.Linear(cfg.video_dim, cfg.memory_dim)
        self.time = nn.Linear(2 * cfg.time_features, cfg.memory_dim)
        self.space = nn.Linear(2 * cfg.spatial_features, cfg.memory_dim)
        self.role = nn.Embedding(NUM_ROLES, cfg.memory_dim)
        self.null = nn.Parameter(torch.empty(cfg.null_tokens, cfg.memory_dim))
        for module in (self.project, self.time, self.space):
            nn.init.xavier_uniform_(module.weight)
            nn.init.zeros_(module.bias)
        nn.init.normal_(self.role.weight, std=0.02)
        nn.init.normal_(self.null, std=0.02)
        rows, cols = cfg.grid[0] // cfg.pool[0], cfg.grid[1] // cfg.pool[1]
        r = torch.arange(rows).repeat_interleave(cols)
        c = torch.arange(cols).repeat(rows)
        spatial = torch.cat((sinusoid(r, cfg.spatial_features, 100.0), sinusoid(c, cfg.spatial_features, 100.0)), -1)
        self.register_buffer("spatial_code", spatial, persistent=False)

    def _pool(self, x: torch.Tensor) -> torch.Tensor:
        cfg = self.cfg
        if cfg.pool == (1, 1):
            return x
        b, n, p, c = x.shape
        rows, cols = cfg.grid
        grid = x.reshape(b * n, rows, cols, c).permute(0, 3, 1, 2)
        pooled = F.avg_pool2d(grid, kernel_size=cfg.pool, stride=cfg.pool)
        return pooled.permute(0, 2, 3, 1).reshape(b, n, -1, c)

    def forward(self, history: torch.Tensor, frame_ids: torch.Tensor, roles: torch.Tensor,
                history_valid: torch.Tensor, current_ids: torch.Tensor) -> MemoryTokens:
        cfg = self.cfg
        b, n, p, c = history.shape
        if p != cfg.grid[0] * cfg.grid[1] or c != cfg.video_dim:
            raise ValueError(f"History features {tuple(history.shape)} do not match grid {cfg.grid} x {cfg.video_dim}.")
        if frame_ids.shape != (b, n) or roles.shape != (b, n) or history_valid.shape != (b, n):
            raise ValueError("frame_ids/roles/history_valid must be [B, N].")
        if current_ids.shape != (b,):
            raise ValueError("current_ids must be [B].")
        if bool(((frame_ids > current_ids[:, None]) & history_valid).any()):
            raise ValueError("Future observations are forbidden in memory.")
        x = self.project(self._pool(self.norm(history.to(self.project.weight.dtype))))   # [B, N, P', D]
        per_frame = x.shape[2]
        age = (current_ids[:, None] - frame_ids).clamp(min=0).float() / cfg.age_unit
        timing = torch.cat((sinusoid(age, cfg.time_features), sinusoid(frame_ids, cfg.time_features)), -1)
        frame_code = self.time(timing.to(x.dtype)) + self.role(roles.clamp(0, NUM_ROLES - 1))  # [B, N, D]
        space_code = self.space(self.spatial_code.to(device=x.device, dtype=x.dtype))          # [P', D]
        x = x + frame_code[:, :, None, :] + space_code[None, None]
        tokens = x.reshape(b, n * per_frame, cfg.memory_dim)
        valid = history_valid.repeat_interleave(per_frame, dim=1)
        slot = torch.arange(n, device=x.device).repeat_interleave(per_frame)[None].expand(b, -1)
        role = roles.repeat_interleave(per_frame, dim=1)
        null = self.null.to(x.dtype)[None].expand(b, -1, -1)
        k = cfg.null_tokens
        ones = torch.ones(b, k, dtype=torch.bool, device=x.device)
        minus = torch.full((b, k), -1, dtype=torch.long, device=x.device)
        return MemoryTokens(tokens=torch.cat((null, tokens), 1), valid=torch.cat((ones, valid), 1),
                            is_history=torch.cat((~ones, torch.ones_like(valid)), 1),
                            frame_slot=torch.cat((minus, slot), 1), role=torch.cat((minus, role), 1))


class ReadTimeInjector(nn.Module):
    """Action tokens of one ActionDiT layer cross-attend memory tokens (post-block residual)."""

    def __init__(self, cfg: MemoryV2Config):
        super().__init__()
        self.heads = cfg.heads
        self.q_norm = nn.LayerNorm(cfg.action_hidden, eps=cfg.layer_norm_eps)
        self.kv_norm = nn.LayerNorm(cfg.memory_dim, eps=cfg.layer_norm_eps)
        self.q = nn.Linear(cfg.action_hidden, cfg.memory_dim)
        self.k = nn.Linear(cfg.memory_dim, cfg.memory_dim)
        self.v = nn.Linear(cfg.memory_dim, cfg.memory_dim)
        self.out = nn.Linear(cfg.memory_dim, cfg.action_hidden)
        for module in (self.q, self.k, self.v, self.out):
            nn.init.xavier_uniform_(module.weight)
            nn.init.zeros_(module.bias)
        if cfg.zero_init_output:
            nn.init.zeros_(self.out.weight)

    def _split(self, x: torch.Tensor) -> torch.Tensor:
        return x.unflatten(-1, (self.heads, x.shape[-1] // self.heads)).transpose(1, 2)

    def memory_kv(self, memory: MemoryTokens) -> Tuple[torch.Tensor, torch.Tensor]:
        """Computed once per decision and reused across all denoising steps."""
        normed = self.kv_norm(memory.tokens)
        return self._split(self.k(normed)), self._split(self.v(normed))

    def query(self, hidden: torch.Tensor) -> torch.Tensor:
        return self._split(self.q(self.q_norm(hidden.to(self.q.weight.dtype))))

    def forward(self, hidden: torch.Tensor, kv: Tuple[torch.Tensor, torch.Tensor], valid: torch.Tensor,
                gate: Optional[torch.Tensor] = None) -> torch.Tensor:
        q = self.query(hidden)
        k, v = kv
        mask = valid[:, None, None, :]
        read = F.scaled_dot_product_attention(q, k.to(q.dtype), v.to(q.dtype), attn_mask=mask)
        delta = self.out(read.transpose(1, 2).flatten(2))
        if gate is not None:
            delta = delta * gate.to(delta.dtype).view(-1, 1, 1)
        return hidden + delta.to(hidden.dtype)

    @torch.no_grad()
    def attention(self, hidden: torch.Tensor, kv: Tuple[torch.Tensor, torch.Tensor],
                  valid: torch.Tensor) -> torch.Tensor:
        """Explicit attention probabilities [B, H, Q, T] for diagnostics."""
        q = self.query(hidden).float()
        k = kv[0].float()
        logits = q @ k.transpose(-1, -2) / math.sqrt(q.shape[-1])
        logits = logits.masked_fill(~valid[:, None, None, :], float("-inf"))
        return logits.softmax(-1)


class TauGate(nn.Module):
    """g_l(tau) = 1 + MLP(sinusoid(1000 tau)); zero-initialised last layer (starts at exactly 1)."""

    def __init__(self, layers: int, hidden: int = 64, features: int = 64):
        super().__init__()
        self.features = features
        self.net = nn.Sequential(nn.Linear(features, hidden), nn.SiLU(), nn.Linear(hidden, layers))
        nn.init.xavier_uniform_(self.net[0].weight)
        nn.init.zeros_(self.net[0].bias)
        nn.init.zeros_(self.net[2].weight)
        nn.init.zeros_(self.net[2].bias)

    def forward(self, timestep: torch.Tensor) -> torch.Tensor:
        """timestep: [B] in [0, 1000] -> [B, layers]."""
        code = sinusoid(timestep.float(), self.features, 10000.0).to(self.net[0].weight.dtype)
        return 1.0 + self.net(code)


class MemoryV2Modules(nn.Module):
    """All trainable memory parameters; the backbone is owned elsewhere."""

    def __init__(self, cfg: MemoryV2Config):
        super().__init__()
        self.cfg = cfg
        self.tokenizer = MemoryTokenizer(cfg)
        self.injectors = nn.ModuleDict({str(i): ReadTimeInjector(cfg) for i in cfg.injection_layers})
        self.tau_gate = TauGate(len(cfg.injection_layers), cfg.tau_gate_hidden) if cfg.tau_gate else None
        self._layer_index: Dict[int, int] = {layer: j for j, layer in enumerate(cfg.injection_layers)}

    def layer_slot(self, layer: int) -> Optional[int]:
        return self._layer_index.get(int(layer))

    def gates(self, timestep: torch.Tensor) -> Optional[torch.Tensor]:
        return None if self.tau_gate is None else self.tau_gate(timestep)

    def memory_kv(self, memory: MemoryTokens) -> Dict[int, Tuple[torch.Tensor, torch.Tensor]]:
        return {int(layer): injector.memory_kv(memory) for layer, injector in self.injectors.items()}

    def parameter_groups(self, weight_decay: float = 0.01):
        decay, no_decay = [], []
        for name, parameter in self.named_parameters():
            exclude = parameter.ndim < 2 or "norm" in name or name.endswith("null") or "role" in name
            (no_decay if exclude else decay).append(parameter)
        return [{"params": decay, "weight_decay": weight_decay}, {"params": no_decay, "weight_decay": 0.0}]
