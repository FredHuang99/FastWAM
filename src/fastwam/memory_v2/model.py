"""memory_v2 model: any action backbone + read-time-selection memory.

The backbone is reached through a small adapter protocol so the same memory
code runs on
  * FastWAMActionAdapter  - the released frozen MoT (memory_s1.FrozenBackbone),
  * a trainable-ActionDiT adapter (to be supplied by train_v2 for the
    dense-joint A continuation), and
  * the tiny CPU backbone used in the unit tests.

Adapter protocol
    num_action_layers: int
    encode(batch) -> (current_kv, shared_context)       # once per decision
    prepare(actions, timestep, shared_context) -> (x, aux)
    block(index, x, aux, current_kv) -> x               # one original action block
    post(x, aux) -> velocity [B, H, action_dim]
"""
from __future__ import annotations

import contextlib
from dataclasses import dataclass, replace
from typing import Any, Dict, Optional, Tuple

import torch
from torch import nn

from .config import GuidanceConfig, MemoryV2Config
from .modules import MemoryTokens, MemoryV2Modules
from .objectives import phi


def _autocast(device: torch.device):
    if device.type == "cuda":
        return torch.autocast("cuda", dtype=torch.bfloat16)
    return contextlib.nullcontext()


@dataclass
class Conditions:
    current_kv: Any                                  # backbone-specific current-frame KV
    context: Any                                     # backbone-specific shared context
    memory: MemoryTokens
    memory_kv: Dict[int, Tuple[torch.Tensor, torch.Tensor]]

    def null(self) -> "Conditions":
        """Same tensors, history tokens masked: the learned no-memory branch."""
        return replace(self, memory=self.memory.without_history())


class MemoryV2Model(nn.Module):
    def __init__(self, backbone, cfg: MemoryV2Config):
        super().__init__()
        if backbone.num_action_layers != cfg.num_action_layers:
            raise ValueError(f"Backbone has {backbone.num_action_layers} action layers, config says {cfg.num_action_layers}.")
        self.backbone = backbone
        self.cfg = cfg
        self.memory = MemoryV2Modules(cfg)

    # ------------------------------------------------------------------ conditions
    def conditions(self, batch: Dict[str, torch.Tensor], drop: Optional[torch.Tensor] = None) -> Conditions:
        """Encode the current observation and tokenise the selected history once per decision."""
        current_kv, context = self.backbone.encode(batch)
        device = batch["history"].device
        with _autocast(device):
            memory = self.memory.tokenizer(batch["history"], batch["frame_ids"], batch["roles"],
                                           batch["history_valid"], batch["current_ids"])
            if drop is not None:
                memory = memory.drop_history(drop)
            memory_kv = self.memory.memory_kv(memory)
        return Conditions(current_kv=current_kv, context=context, memory=memory, memory_kv=memory_kv)

    # ------------------------------------------------------------------ velocity
    def velocity(self, actions: torch.Tensor, timestep: torch.Tensor, conditions: Conditions,
                 memory_mode: str = "on") -> torch.Tensor:
        """memory_mode: on | null (history masked, learned null tokens only) | off (bypass injectors)."""
        if memory_mode not in ("on", "null", "off"):
            raise ValueError(f"Unknown memory_mode={memory_mode}.")
        if memory_mode == "null":
            conditions = conditions.null()
        timestep = timestep.reshape(-1)
        if timestep.numel() == 1 and actions.shape[0] > 1:
            timestep = timestep.expand(actions.shape[0])
        x, aux = self.backbone.prepare(actions, timestep, conditions.context)
        gates = None
        if memory_mode != "off":
            with _autocast(actions.device):
                gates = self.memory.gates(timestep.float())
        for index in range(self.backbone.num_action_layers):
            x = self.backbone.block(index, x, aux, conditions.current_kv)
            slot = self.memory.layer_slot(index)
            if slot is None or memory_mode == "off":
                continue
            injector = self.memory.injectors[str(index)]
            gate = None if gates is None else gates[:, slot]
            with _autocast(actions.device):
                x = injector(x, conditions.memory_kv[index], conditions.memory.valid, gate)
        return self.backbone.post(x, aux)

    # ------------------------------------------------------------------ sampling
    @torch.no_grad()
    def sample(self, conditions: Conditions, noise: torch.Tensor, guidance: GuidanceConfig = GuidanceConfig(),
               memory_mode: str = "on", trace: bool = False):
        """Euler integration from tau = 1; memory CFG only on steps with sigma >= guidance.min_sigma.

        Returns (actions, steps) where steps (if trace) lists per-step sigma and the
        clean-action estimate x0 = x - sigma * u, used for branch-commitment analysis.
        """
        actions = noise.clone()
        u = torch.linspace(1.0, 0.0, guidance.steps + 1, dtype=torch.float32)
        sigmas = phi(u, guidance.shift)
        records = []
        for k in range(guidance.steps):
            sigma, delta = float(sigmas[k]), float(sigmas[k + 1] - sigmas[k])
            timestep = torch.full((actions.shape[0],), 1000.0 * sigma, device=actions.device)
            velocity = self.velocity(actions, timestep, conditions, memory_mode).to(actions.dtype)
            guided = memory_mode == "on" and guidance.scale != 1.0 and sigma >= guidance.min_sigma
            if guided:
                unconditional = self.velocity(actions, timestep, conditions, "null").to(actions.dtype)
                velocity = unconditional + guidance.scale * (velocity - unconditional)
            if trace:
                records.append({"sigma": sigma, "guided": guided,
                                "x0": (actions.float() - sigma * velocity.float()).detach().cpu()})
            actions = actions + velocity * delta
        return actions.float(), records

    def memory_state_dict(self) -> Dict[str, torch.Tensor]:
        return self.memory.state_dict()

    def load_memory_state_dict(self, state: Dict[str, torch.Tensor]) -> None:
        self.memory.load_state_dict(state, strict=True)


class FastWAMActionAdapter(nn.Module):
    """Adapter over memory_s1.model.FrozenBackbone (frozen Video DiT + Action DiT + proprio).

    `block` reproduces FrozenBackbone.action_velocity layer by layer (same calls,
    same BF16/no-autocast discipline), so with the memory bypassed the velocity is
    identical to the released single-frame path; see tests_gpu in the README.
    """

    def __init__(self, frozen_backbone):
        super().__init__()
        self.inner = frozen_backbone
        self.num_action_layers = len(frozen_backbone.mot.mixtures["action"].blocks)

    def encode(self, batch):
        _, kv, context = self.inner.encode_observation(batch["latent"], batch["text"], batch["proprio"])
        return kv, context

    @torch.autocast("cuda", enabled=False)
    def prepare(self, actions, timestep, shared_context):
        context, mask = shared_context
        expert = self.inner.mot.mixtures["action"]
        timestep = timestep.to(device=actions.device, dtype=torch.bfloat16)
        x, _, mod, ctx, ctx_mask, freqs = expert.prepare(
            action_tokens=actions.to(torch.bfloat16), timestep=timestep, context=context, context_mask=mask)
        return x, (mod, ctx, ctx_mask, freqs)

    @torch.autocast("cuda", enabled=False)
    def block(self, index, x, aux, current_kv):
        from fastwam.models.wan22.wan_video_dit import flash_attention
        mod, ctx, ctx_mask, freqs = aux
        mot = self.inner.mot
        expert = mot.mixtures["action"]
        block = expert.blocks[index]
        keys, values = current_kv
        q, k, v, residual, gate, shift, scale, ffn_gate, _ = mot._build_expert_attention_io(
            expert=expert, block=block, x=x, freqs=freqs, t_mod=mod)
        attention_mask = torch.ones((x.shape[1], keys[index].shape[1] + x.shape[1]), device=x.device, dtype=torch.bool)
        mixed = flash_attention(q=q, k=torch.cat((keys[index], k), 1), v=torch.cat((values[index], v), 1),
                                num_heads=mot.num_heads, ctx_mask=attention_mask)
        return mot._apply_expert_post_block_tensor(
            block=block, residual_x=residual, mixed_attn_out=mixed, gate_msa=gate,
            shift_mlp=shift, scale_mlp=scale, gate_mlp=ffn_gate, context=ctx, context_mask=ctx_mask)

    @torch.autocast("cuda", enabled=False)
    def post(self, x, aux):
        return self.inner.mot.mixtures["action"].post(x.to(torch.bfloat16))
