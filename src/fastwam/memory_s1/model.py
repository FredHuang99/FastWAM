"""Eager frozen FastWAM bridge with explicit feature and KV lifecycles."""
from __future__ import annotations

from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F
import yaml

from fastwam.models.wan22.action_dit import ActionDiT
from fastwam.models.wan22.mot import MoT
from fastwam.models.wan22.wan_video_dit import WanVideoDiT, flash_attention
from fastwam.models.wan22.helpers.loader import _load_registered_model
from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
from fastwam.models.wan22.schedulers.scheduler_continuous import WanContinuousFlowMatchScheduler
from .modules import MemoryModules
from .protocol import format_task_prompt


class FrozenBackbone(nn.Module):
    def __init__(self, cfg, device):
        super().__init__()
        architecture = yaml.safe_load((Path(cfg["root"]) / "configs/model/fastwam.yaml").read_text())
        video_cfg = dict(architecture["video_dit_config"])
        action_cfg = dict(architecture["action_dit_config"])
        video_cfg.update(use_gradient_checkpointing=False, action_dim=14)
        action_cfg.update(use_gradient_checkpointing=False, action_dim=14)
        video = WanVideoDiT(**video_cfg)
        action = ActionDiT(**action_cfg)
        self.mot = MoT({"video": video, "action": action}, mot_checkpoint_mixed_attn=False)
        self.proprio_encoder = nn.Linear(14, 4096)
        payload = torch.load(cfg["paths"]["base"], map_location="cpu", weights_only=True, mmap=True)
        if "mot" not in payload or "proprio_encoder" not in payload:
            raise ValueError("Released base must contain complete mot and proprio_encoder; legacy video-only weights are rejected.")
        self.mot.load_state_dict(payload["mot"], strict=True)
        self.proprio_encoder.load_state_dict(payload["proprio_encoder"], strict=True)
        del payload
        self.to(device=device, dtype=torch.bfloat16).eval().requires_grad_(False)

    def context(self, text, proprio):
        text = text.to(torch.bfloat16)
        state = self.proprio_encoder(proprio.to(torch.bfloat16))[:, None]
        context = torch.cat((text, state), 1)
        # Retain the released encoder's zero-padded text/all-true backbone mask.
        return context, torch.ones(context.shape[:2], device=context.device, dtype=torch.bool)

    @torch.no_grad()
    def encode_observation(self, latent, text, proprio, keep_kv=True):
        if tuple(latent.shape[1:]) != (48, 1, 24, 20):
            raise ValueError(f"Expected independent single-frame latent, got {latent.shape}.")
        context, context_mask = self.context(text, proprio)
        expert = self.mot.mixtures["video"]
        x, _, mod, ctx, ctx_mask, freqs, _, _, _, _ = expert.prepare(
            x=latent.to(torch.bfloat16), timestep=torch.zeros(latent.shape[0], device=latent.device, dtype=torch.bfloat16),
            context=context, context_mask=context_mask, fuse_vae_embedding_in_latents=True)
        keys, values = [], []
        attention_mask = torch.ones((x.shape[1], x.shape[1]), device=x.device, dtype=torch.bool)
        for block in expert.blocks:
            q, k, v, residual, gate, shift, scale, ffn_gate, _ = self.mot._build_expert_attention_io(
                expert=expert, block=block, x=x, freqs=freqs, t_mod=mod)
            mixed = flash_attention(q=q, k=k, v=v, num_heads=24, ctx_mask=attention_mask)
            x = self.mot._apply_expert_post_block_tensor(
                block=block, residual_x=residual, mixed_attn_out=mixed, gate_msa=gate,
                shift_mlp=shift, scale_mlp=scale, gate_mlp=ffn_gate, context=ctx, context_mask=ctx_mask)
            if keep_kv:
                keys.append(k.detach())
                values.append(v.detach())
        return x.detach(), (keys, values), (context, context_mask)

    def action_velocity(self, actions, timestep, shared_context, kv, memory, readout, gate_scale=1.0):
        context, mask = shared_context
        expert = self.mot.mixtures["action"]
        x, _, mod, ctx, ctx_mask, freqs = expert.prepare(
            action_tokens=actions.to(torch.bfloat16), timestep=timestep, context=context, context_mask=mask)
        attention_mask = torch.ones((x.shape[1], kv[0][0].shape[1] + x.shape[1]), device=x.device, dtype=torch.bool)
        for layer, block in enumerate(expert.blocks):
            q, k, v, residual, gate, shift, scale, ffn_gate, _ = self.mot._build_expert_attention_io(
                expert=expert, block=block, x=x, freqs=freqs, t_mod=mod)
            mixed = flash_attention(q=q, k=torch.cat((kv[0][layer], k), 1),
                                    v=torch.cat((kv[1][layer], v), 1), num_heads=24, ctx_mask=attention_mask)
            x = self.mot._apply_expert_post_block_tensor(
                block=block, residual_x=residual, mixed_attn_out=mixed, gate_msa=gate,
                shift_mlp=shift, scale_mlp=scale, gate_mlp=ffn_gate, context=ctx, context_mask=ctx_mask)
            if str(layer) in memory.injectors:
                x = memory.injectors[str(layer)](x, readout, gate_scale)
        return expert.post(x)


class S1Model(nn.Module):
    def __init__(self, cfg, device):
        super().__init__()
        self.backbone = FrozenBackbone(cfg, device)
        self.memory = MemoryModules().to(device=device, dtype=torch.float32)
        self.memory.activation_checkpointing = cfg.get("history", {}).get("reader_checkpointing", False)
        self.scheduler = WanContinuousFlowMatchScheduler(shift=1.0)

    def train(self, mode=True):
        super().train(mode)
        self.backbone.eval()
        return self

    def conditions(self, batch):
        current, kv, context = self.backbone.encode_observation(batch["latent"], batch["text"], batch["proprio"])
        history_valid = batch["history_valid"]
        if ((batch["frame_ids"] > batch["t"][:, None]) & history_valid).any():
            raise ValueError("Future history is forbidden.")
        readout = self.memory.read(current, batch["text"], batch["text_valid"], batch["proprio"],
                                   batch["history"], batch["frame_ids"], history_valid)
        return kv, context, readout

    def forward(self, batch, noise, tau, gate_scale=1.0):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            kv, context, readout = self.conditions(batch)
            noisy = (1 - tau[:, None, None]) * batch["actions"] + tau[:, None, None] * noise
            prediction = self.backbone.action_velocity(noisy, 1000 * tau, context, kv, self.memory, readout, gate_scale)
        prediction = prediction.float()
        target = noise.float() - batch["actions"].float()
        count = batch["action_valid"].sum(1)
        if (count == 0).any():
            raise ValueError("An all-invalid anchor reached the trainer.")
        error = ((prediction - target).square() * batch["action_valid"][..., None]).sum((1, 2)) / (14 * count)
        loss = (self.scheduler.training_weight(1000 * tau) * error).mean()
        return loss, {"unweighted_fm": error.detach(), "tau": tau.detach(),
                      "readout_norm": readout.detach().float().norm(dim=-1).mean()}

    @torch.no_grad()
    def sample(self, batch, noise, gate_scale=1.0, prepared_conditions=None):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            kv, context, readout = self.conditions(batch) if prepared_conditions is None else prepared_conditions
            actions = noise.to(torch.bfloat16).clone()
            timesteps, deltas = self.scheduler.build_inference_schedule(10, noise.device, actions.dtype)
            for timestep, delta in zip(timesteps, deltas):
                velocity = self.backbone.action_velocity(actions, timestep.expand(len(actions)), context,
                                                         kv, self.memory, readout, gate_scale)
                actions = self.scheduler.step(velocity.to(actions.dtype), delta, actions)
        return actions.float(), readout


def load_observation_encoders(cfg, device):
    vae = _load_registered_model(cfg["paths"]["vae"], "wan_video_vae", torch.bfloat16, str(device))
    text = _load_registered_model(cfg["paths"]["t5"], "wan_video_text_encoder", torch.bfloat16, str(device))
    vae.eval().requires_grad_(False)
    text.eval().requires_grad_(False)
    tokenizer = HuggingfaceTokenizer(cfg["paths"]["tokenizer"], seq_len=128, clean="whitespace", local_files_only=True)
    return vae, text, tokenizer


@torch.no_grad()
def encode_text(encoder, tokenizer, instruction, device):
    ids, valid = tokenizer(format_task_prompt(instruction), return_mask=True, add_special_tokens=True)
    ids, valid = ids.to(device), valid.to(device).bool()
    features = encoder(ids, valid)
    features = features.masked_fill(~valid[..., None], 0)
    return features.detach(), valid


@torch.no_grad()
def encode_latent(vae, mosaics):
    # Use the eager single-frame encoder, without sharing VAE temporal state.
    return vae.model.encode(mosaics.unsqueeze(2).to(torch.bfloat16), [vae.mean, vae.inv_std]).detach()
