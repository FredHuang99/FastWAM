"""N1 "KV replay" (plan v7 Q1, 11-05): the action expert reads history in the format it already reads the current frame.

FastWAM's action expert attends, in EVERY layer, to the current frame's video K/V that the frozen video branch
computed when it prefilled that frame alone (mot.prefill_video_cache; memory_s1 FrozenBackbone.encode_observation).
KV replay gives each replayed layer the same per-layer K/V of the selected history frames, each also prefilled alone
(so it is exactly what the model computed when that frame was the current one):

    o_A  = attention(q, [K_cur; K_act], [V_cur; V_act])                     (the base model, unchanged)
    o_AH = attention(q, [K_hist'; K_cur; K_act], [V_hist'; V_cur; V_act])    (history + current, one softmax)
    out  = base_layer(x) + g_l(tau) * (L(o_AH) - L(o_A))                    (L = the layer after attention)

* Time order. The action rows have no causal mask over video keys and a softmax does not care how the keys are
  concatenated; "before" is the temporal RoPE index. The video branch is per-frame causal (a query sees frames with a
  smaller index), so history goes to t = -rank (rank 1 = most recent selected frame), the current frame stays at 0.
  A history frame was prefilled as a first frame (t = 0, temporal rotation = identity); `rerotate_temporal` multiplies
  only the temporal channels (the first (d - 2*(d//3)) / 2 complex pairs of every head, Wan's 3D RoPE layout) by
  exp(-i * rank * theta_f). Rotations compose, so this equals encoding the frame at t = -rank; spatial channels are
  untouched. History frames never attend to each other (each was prefilled alone), so no mask is needed between them.
* Start. g_l = TauGate - 1 is exactly 0 at initialisation, so on == null == off == the base model; the gradient of g_l
  is L(o_AH) - L(o_A), so the gate opens without a vanishing-gradient start.
* K_hist' = rerotated K + role embedding + log2-elapsed-time embedding (both zero at start) + low-rank adapter
  (zero at start); V_hist' = V + low-rank adapter. The action expert never saw a video key at t != 0; these are the
  only new parameters.
* null / off / memory dropout: no history at all (out = base_layer(x)).
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import List, Optional

import torch
from torch import nn
import torch.nn.functional as F

from .config import NUM_ROLES, MemoryV2Config


# ----------------------------------------------------------------------------- temporal RoPE
def temporal_pairs(head_dim: int) -> int:
    """Number of complex channel pairs per head that carry the temporal RoPE (Wan precompute_freqs_cis_3d)."""
    return (head_dim - 2 * (head_dim // 3)) // 2


def temporal_rotation(positions: torch.Tensor, head_dim: int, theta: float = 10000.0) -> torch.Tensor:
    """exp(i * position * theta_f) for the temporal pairs: [..., n_f] complex64 (same frequencies as
    wan_video_dit.precompute_freqs_cis(head_dim - 2 * (head_dim // 3)))."""
    n_f = temporal_pairs(head_dim)
    dim_f = 2 * n_f
    inv = 1.0 / (theta ** (torch.arange(0, dim_f, 2, device=positions.device)[:n_f].double() / dim_f))
    angles = positions.double()[..., None] * inv
    return torch.polar(torch.ones_like(angles), angles).to(torch.complex64)


def rerotate_temporal(keys: torch.Tensor, positions: torch.Tensor, num_heads: int) -> torch.Tensor:
    """keys [B, K, T, H*Dh] RoPE-encoded at temporal index 0 -> encoded at temporal index positions [B, K]."""
    b, k, t, width = keys.shape
    head_dim = width // num_heads
    n_f = temporal_pairs(head_dim)
    x = keys.reshape(b, k, t, num_heads, head_dim // 2, 2)
    temporal = torch.view_as_complex(x[..., :n_f, :].float().contiguous())             # [B, K, T, H, n_f]
    temporal = temporal * temporal_rotation(positions, head_dim)[:, :, None, None, :]
    out = torch.cat((torch.view_as_real(temporal).to(keys.dtype), x[..., n_f:, :]), dim=-2)
    return out.reshape(b, k, t, width)


# ----------------------------------------------------------------------------- history metadata
def recency_positions(frame_ids: torch.Tensor, valid: torch.Tensor) -> torch.Tensor:
    """[B, K] temporal RoPE index of each history slot: -1 for the most recent valid frame, -2 for the next, ...;
    0 for padding (masked anyway)."""
    ids = frame_ids.masked_fill(~valid, -1)
    order = ids.argsort(dim=1, descending=True, stable=True)
    ranks = torch.empty_like(order)
    ranks.scatter_(1, order, torch.arange(1, order.shape[1] + 1, device=order.device).expand_as(order).contiguous())
    return torch.where(valid, -ranks, torch.zeros_like(ranks))


def time_buckets(frame_ids: torch.Tensor, current_ids: torch.Tensor, valid: torch.Tensor, buckets: int,
                 unit: float) -> torch.Tensor:
    """[B, K] floor(log2(1 + elapsed / unit)), clamped to [0, buckets - 1]; 0 for padding."""
    elapsed = (current_ids[:, None] - frame_ids).clamp_min(0).float() / unit
    b = torch.floor(torch.log2(1.0 + elapsed)).long().clamp(0, buckets - 1)
    return torch.where(valid, b, torch.zeros_like(b))


@dataclass
class ReplayState:
    """Per-decision history for kv_replay (built once per decision / batch by MemoryV2Model.conditions)."""
    keys: List[torch.Tensor]        # per replayed layer [B, K*T, W], temporally re-rotated
    values: List[torch.Tensor]      # per replayed layer [B, K*T, W]
    token_valid: torch.Tensor       # [B, K*T] bool
    roles: torch.Tensor             # [B, K] long
    buckets: torch.Tensor           # [B, K] long
    active: torch.Tensor            # [B] bool: has history and not dropped
    tokens_per_frame: int

    def without_history(self) -> "ReplayState":
        return replace(self, active=torch.zeros_like(self.active))

    def drop(self, drop: torch.Tensor) -> "ReplayState":
        return replace(self, active=self.active & ~drop.to(self.active.device))


# ----------------------------------------------------------------------------- parameters
class KVReplay(nn.Module):
    """Trainable part of kv_replay: per-layer tau gates (zero at start), key embeddings, low-rank K / V adapters."""

    def __init__(self, cfg: MemoryV2Config):
        super().__init__()
        from .modules import TauGate
        self.cfg = cfg
        self.layers = tuple(cfg.replayed_layers)
        self._slot = {layer: j for j, layer in enumerate(self.layers)}
        n, width = len(self.layers), cfg.video_dim
        self.gate = TauGate(n, cfg.tau_gate_hidden)                      # g = gate(t) - 1: exactly 0 at start
        self.role_embedding = nn.Parameter(torch.zeros(n, NUM_ROLES, width))
        self.time_embedding = nn.Parameter(torch.zeros(n, cfg.replay_time_buckets, width))
        r = cfg.replay_rank
        if r:
            self.key_down = nn.Parameter(torch.randn(n, width, r) / width ** 0.5)
            self.key_up = nn.Parameter(torch.zeros(n, r, width))
            self.value_down = nn.Parameter(torch.randn(n, width, r) / width ** 0.5)
            self.value_up = nn.Parameter(torch.zeros(n, r, width))

    def slot(self, layer: int) -> Optional[int]:
        return self._slot.get(int(layer))

    def gates(self, timestep: torch.Tensor) -> torch.Tensor:
        """[B, n] memory strength per replayed layer; 0 at initialisation."""
        return self.gate(timestep) - 1.0

    def layer_kv(self, state: ReplayState, slot: int):
        """K', V' of one replayed layer: [B, K*T, W] in the backbone's dtype."""
        k, v = state.keys[slot], state.values[slot]
        dtype = k.dtype
        b, s, w = k.shape
        t = state.tokens_per_frame
        emb = self.role_embedding[slot][state.roles] + self.time_embedding[slot][state.buckets]      # [B, K, W]
        k = k + emb.to(dtype).repeat_interleave(t, dim=1)
        if self.cfg.replay_rank:
            k = k + ((k @ self.key_down[slot].to(dtype)) @ self.key_up[slot].to(dtype))
            v = v + ((v @ self.value_down[slot].to(dtype)) @ self.value_up[slot].to(dtype))
        return k, v


# ----------------------------------------------------------------------------- history prefill
@torch.no_grad()
def encode_history_frames(encode_fn, batch, layers, positions, chunk: int, num_heads: Optional[int]):
    """Per-layer K / V of every valid history frame, each prefilled alone.

    encode_fn(latent [n, ...], text [n, L, D], proprio [n, P]) -> (keys, values): lists over ALL action layers of
    [n, T, W] (what the backbone's encode returns for current frames). Returns (keys, values): lists over `layers` of
    [B, K*T, W]; padding slots are zero (masked by token_valid). num_heads=None skips the temporal re-rotation
    (test backbones without RoPE)."""
    valid = batch["history_valid"]
    b, k = valid.shape
    index = valid.nonzero(as_tuple=False)
    real = index.shape[0]
    if real == 0:                                     # shapes only: one padding slot, fully masked afterwards
        index = torch.zeros(1, 2, dtype=torch.long, device=valid.device)
    latent, proprio, text = batch["hist_latent"], batch["hist_proprio"], batch["text"]
    out_k = out_v = None
    for start in range(0, index.shape[0], chunk):
        sel = index[start:start + chunk]
        keys, values = encode_fn(latent[sel[:, 0], sel[:, 1]], text[sel[:, 0]], proprio[sel[:, 0], sel[:, 1]])
        if out_k is None:
            t, w = keys[0].shape[1], keys[0].shape[2]
            out_k = [keys[0].new_zeros(b, k, t, w) for _ in layers]
            out_v = [values[0].new_zeros(b, k, t, w) for _ in layers]
        if real == 0:
            break
        for j, layer in enumerate(layers):
            out_k[j][sel[:, 0], sel[:, 1]] = keys[layer].to(out_k[j].dtype)
            out_v[j][sel[:, 0], sel[:, 1]] = values[layer].to(out_v[j].dtype)
    t, w = out_k[0].shape[2], out_k[0].shape[3]
    if num_heads is not None:
        out_k = [rerotate_temporal(x, positions, num_heads) for x in out_k]
    return [x.reshape(b, k * t, w) for x in out_k], [x.reshape(b, k * t, w) for x in out_v]


# ----------------------------------------------------------------------------- the layer delta
def joint_attention(q, k_hist, v_hist, hist_valid, k_rest, v_rest, num_heads):
    """softmax over [history; rest] with history padding masked; q [B, Q, W], k/v [B, S, W] -> [B, Q, W]."""
    b, qn, w = q.shape
    d = w // num_heads

    def heads(x):
        return x.reshape(b, x.shape[1], num_heads, d).transpose(1, 2)

    keys = torch.cat((k_hist, k_rest), 1)
    values = torch.cat((v_hist, v_rest), 1)
    mask = torch.cat((hist_valid, torch.ones(b, k_rest.shape[1], dtype=torch.bool, device=q.device)), 1)
    out = F.scaled_dot_product_attention(heads(q), heads(keys), heads(values), attn_mask=mask[:, None, None, :])
    return out.transpose(1, 2).reshape(b, qn, w)


def mot_replay_delta(mot, index, x, aux, current_k, current_v, hist_k, hist_v, hist_valid):
    """L(o_AH) - L(o_A) for action layer `index` of a FastWAM MoT."""
    with_history, without = mot_replay_parts(mot, index, x, aux, current_k, current_v, hist_k, hist_v, hist_valid)
    return with_history - without


def mot_replay_parts(mot, index, x, aux, current_k, current_v, hist_k, hist_v, hist_valid):
    """(L(o_AH), L(o_A)) for action layer `index` of a FastWAM MoT (frozen layer, same calls as the released
    action path: _build_expert_attention_io -> flash_attention over [current; action] -> _apply_expert_post_block_tensor);
    L(o_A) is the layer without history (replay_check.py compares it with ABModel's own 'action' call)."""
    from fastwam.models.wan22.wan_video_dit import flash_attention
    mod, ctx, ctx_mask, freqs = aux
    expert = mot.mixtures["action"]
    block = expert.blocks[index]
    with torch.autocast(device_type=x.device.type, enabled=False):      # the released path runs without autocast
        q, k, v, residual, gate, shift, scale, ffn_gate, _ = mot._build_expert_attention_io(
            expert=expert, block=block, x=x, freqs=freqs, t_mod=mod)
        rest_k, rest_v = torch.cat((current_k, k), 1), torch.cat((current_v, v), 1)
        full = torch.ones((x.shape[1], rest_k.shape[1]), device=x.device, dtype=torch.bool)
        o_a = flash_attention(q=q, k=rest_k, v=rest_v, num_heads=mot.num_heads, ctx_mask=full)
        o_ah = joint_attention(q, hist_k.to(q.dtype), hist_v.to(q.dtype), hist_valid, rest_k, rest_v, mot.num_heads)

        def post(o):
            return mot._apply_expert_post_block_tensor(
                block=block, residual_x=residual, mixed_attn_out=o, gate_msa=gate,
                shift_mlp=shift, scale_mlp=scale, gate_mlp=ffn_gate, context=ctx, context_mask=ctx_mask)
        return post(o_ah), post(o_a)


def maybe_checkpoint(fn, *args):
    """Activation checkpointing in training (the delta keeps attention over up to K*T history keys per layer)."""
    if torch.is_grad_enabled() and any(isinstance(a, torch.Tensor) and a.requires_grad for a in args):
        from torch.utils.checkpoint import checkpoint
        return checkpoint(fn, *args, use_reentrant=False)
    return fn(*args)
