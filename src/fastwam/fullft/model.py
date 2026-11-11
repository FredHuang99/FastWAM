"""FullModel: the released FastWAM MoT made fully trainable, with history frames as gated extra keys.

Joint layer l (video tokens of the clip + action tokens, the released masks):
    o_base = attention(q, [K_clip; K_act], [V_clip; V_act], released mask)
    o_hist = attention(q, [K_hist; K_clip; K_act], [V_hist; ...], released mask + every query may see history)
    o      = o_base + g_l,h * (o_hist - o_base)            g = 0 at start (per layer, per head)
so at start the model IS the released one (tested), and the gradient of g is o_hist - o_base.
K_hist / V_hist: every history frame prefilled ALONE through the video expert (clean, t = 0, its own proprio),
exactly as a current frame is prefilled at inference, no gradient (the weights are the current ones); its keys are
re-rotated from temporal index 0 to its position (history.py: -rank or -elapsed / 16).
clk / prop: the elapsed step count / the event proprio states enter through the proprio token: proprio_token +
extra(feature), extra zero-initialised (exact start).
arprop (plan v12): the ledger, one token per event = ledger(features) (zero-initialised), ADDED to the last
event_slots positions of the text context, which are padding zeros (checked): a zero ledger is exactly ar.
Training loss = the released FastWAM.training_loss (video flow matching on the two noisy latent frames + action flow
matching), computed on cached clip latents instead of re-encoding the video.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import torch
from torch import nn
import torch.nn.functional as F

from fastwam.models.wan22.schedulers.scheduler_continuous import WanContinuousFlowMatchScheduler
from fastwam.models.wan22.wan_video_dit import sinusoidal_embedding_1d

CLK_DIM = 256


# ----------------------------------------------------------------------------- temporal re-rotation (as replay.py)
def temporal_pairs(head_dim: int) -> int:
    return (head_dim - 2 * (head_dim // 3)) // 2


def rerotate(keys: torch.Tensor, positions: torch.Tensor, num_heads: int) -> torch.Tensor:
    """keys [B, K, T, H*D] encoded at temporal index 0 -> at temporal index positions [B, K] (float)."""
    b, k, t, width = keys.shape
    head_dim = width // num_heads
    n_f = temporal_pairs(head_dim)
    dim_f = 2 * n_f
    inv = 1.0 / (10000.0 ** (torch.arange(0, dim_f, 2, device=keys.device)[:n_f].double() / dim_f))
    angles = positions.double()[..., None] * inv                                 # [B, K, n_f]
    rot = torch.polar(torch.ones_like(angles), angles).to(torch.complex64)
    x = keys.reshape(b, k, t, num_heads, head_dim // 2, 2)
    temporal = torch.view_as_complex(x[..., :n_f, :].float().contiguous()) * rot[:, :, None, None, :]
    out = torch.cat((torch.view_as_real(temporal).to(keys.dtype), x[..., n_f:, :]), dim=-2)
    return out.reshape(b, k, t, width)


@dataclass
class History:
    keys: List[torch.Tensor]          # per layer [B, K*T, W]
    values: List[torch.Tensor]
    valid: torch.Tensor               # [B, K*T] bool


# ----------------------------------------------------------------------------- LoRA (train_video = lora)
class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, rank: int):
        super().__init__()
        self.base = base
        self.base.requires_grad_(False)
        self.down = nn.Parameter(torch.randn(rank, base.in_features) / math.sqrt(base.in_features))
        self.up = nn.Parameter(torch.zeros(base.out_features, rank))

    @property
    def weight(self):                 # code that reads .weight.dtype (e.g. memory_s1 numerics) keeps working
        return self.base.weight

    def forward(self, x):
        return self.base(x) + F.linear(F.linear(x, self.down.to(x.dtype)), self.up.to(x.dtype))


def add_lora(module: nn.Module, rank: int) -> int:
    """Wrap every nn.Linear inside the attention (q, k, v, o) and FFN of each block. Returns the count."""
    count = 0
    for block in module.blocks:
        for parent in (block.self_attn, block.ffn):
            for name, child in list(parent.named_children()):
                if isinstance(child, nn.Linear):
                    setattr(parent, name, LoRALinear(child, rank))
                    count += 1
    return count


# ----------------------------------------------------------------------------- the model
class FullModel(nn.Module):
    def __init__(self, mot, proprio_encoder: nn.Linear, variant: str = "none", event_slots: int = 0,
                 video_shift: float = 5.0, action_shift: float = 1.0):
        super().__init__()
        self.mot = mot
        self.proprio_encoder = proprio_encoder
        self.variant = variant
        self.num_layers = mot.num_layers
        self.num_heads = mot.num_heads
        self.hist_gate = nn.Parameter(torch.zeros(self.num_layers, self.num_heads))
        text_dim = proprio_encoder.out_features
        self.extra = None
        if variant == "clk":
            self.extra = nn.Linear(CLK_DIM, text_dim)
        elif variant == "prop":
            self.extra = nn.Linear(event_slots * 15, text_dim)
        if self.extra is not None:
            nn.init.zeros_(self.extra.weight)
            nn.init.zeros_(self.extra.bias)
        self.ledger = None
        if variant == "arprop":
            from .history import ledger_dim
            self.ledger = nn.Linear(ledger_dim(event_slots), text_dim)
            nn.init.zeros_(self.ledger.weight)
            nn.init.zeros_(self.ledger.bias)
        self.video_scheduler = WanContinuousFlowMatchScheduler(shift=video_shift)
        self.action_scheduler = WanContinuousFlowMatchScheduler(shift=action_shift)
        self.checkpoint_layers = False
        self.compute_dtype: Optional[torch.dtype] = None     # bf16 when the trainer runs fp32 weights under autocast

    def _dtype(self) -> torch.dtype:
        return self.compute_dtype or next(self.proprio_encoder.parameters()).dtype

    # ------------------------------------------------------------------ construction
    @classmethod
    def from_release(cls, architecture: str, base: str, variant: str = "none", event_slots: int = 0,
                     video_shift: float = 5.0, action_shift: float = 1.0) -> "FullModel":
        import yaml
        from fastwam.models.wan22.action_dit import ActionDiT
        from fastwam.models.wan22.mot import MoT
        from fastwam.models.wan22.wan_video_dit import WanVideoDiT
        arch = yaml.safe_load(Path(architecture).read_text())
        video_cfg = dict(arch["video_dit_config"])
        action_cfg = dict(arch["action_dit_config"])
        video_cfg.update(use_gradient_checkpointing=False, action_dim=14)
        action_cfg.update(use_gradient_checkpointing=False, action_dim=14)
        if video_cfg.get("video_attention_mask_mode") != "first_frame_causal":
            raise ValueError("FullModel reproduces the released first_frame_causal video mask only.")
        mot = MoT({"video": WanVideoDiT(**video_cfg), "action": ActionDiT(**action_cfg)}, mot_checkpoint_mixed_attn=False)
        proprio = nn.Linear(14, int(video_cfg["text_dim"]))
        payload = torch.load(base, map_location="cpu", weights_only=True, mmap=True)
        mot.load_state_dict(payload["mot"], strict=True)
        proprio.load_state_dict(payload["proprio_encoder"], strict=True)
        del payload
        return cls(mot, proprio, variant, event_slots, video_shift, action_shift)

    @property
    def video(self):
        return self.mot.mixtures["video"]

    @property
    def action(self):
        return self.mot.mixtures["action"]

    def set_trainable(self, train_video: str, lora_rank: int = 64) -> None:
        self.requires_grad_(True)
        if train_video == "frozen":
            self.video.requires_grad_(False)
        elif train_video == "lora":
            self.video.requires_grad_(False)
            add_lora(self.video, lora_rank)          # new LoRA parameters are trainable

    # ------------------------------------------------------------------ inputs
    def context(self, text: torch.Tensor, proprio: torch.Tensor, extra: Optional[torch.Tensor] = None,
                ledger: Optional[torch.Tensor] = None):
        """Released convention (FrozenBackbone.context / FastWAM._append_proprio_to_context): zero-padded text with
        an all-true mask, plus one proprio token. arprop: ledger [B, S, ledger_dim] features -> tokens added to the
        last S text positions (padding zeros)."""
        if ledger is not None and self.ledger is not None:
            tokens = self.ledger(ledger.to(text.dtype))
            n = tokens.shape[1]
            text = torch.cat((text[:, :-n], text[:, -n:] + tokens.to(text.dtype)), 1)
        token = self.proprio_encoder(proprio.to(text.dtype).unsqueeze(1))
        if extra is not None and self.extra is not None:
            token = token + self.extra(extra.to(token.dtype)).unsqueeze(1)
        context = torch.cat((text, token.to(text.dtype)), 1)
        return context, torch.ones(context.shape[:2], dtype=torch.bool, device=context.device)

    def extra_feature(self, batch: dict) -> Optional[torch.Tensor]:
        if self.variant == "clk":
            return sinusoidal_embedding_1d(CLK_DIM, batch["anchor"].float())
        if self.variant == "prop":
            v = batch["event_valid"].float()
            return torch.cat((batch["event_proprio"] * v[..., None], v[..., None]), -1).flatten(1)
        return None

    def ledger_input(self, batch: dict) -> Optional[torch.Tensor]:
        if self.ledger is None or "ledger" not in batch:
            return None
        return batch["ledger"] * batch["ledger_valid"][..., None].to(batch["ledger"].dtype)

    @staticmethod
    def base_mask(video_len: int, action_len: int, tokens_per_frame: int, device) -> torch.Tensor:
        """The released joint mask (FastWAM._build_mot_attention_mask with first_frame_causal video)."""
        total = video_len + action_len
        mask = torch.zeros((total, total), dtype=torch.bool, device=device)
        mask[:video_len, :video_len] = True
        mask[:tokens_per_frame, tokens_per_frame:video_len] = False
        mask[video_len:, video_len:] = True
        mask[video_len:, :tokens_per_frame] = True
        return mask

    # ------------------------------------------------------------------ history
    @torch.no_grad()
    def prefill_frames(self, latent: torch.Tensor, text: torch.Tensor, proprio: torch.Tensor, chunk: int = 16):
        """Per-layer K / V of single frames, each alone (= FrozenBackbone.encode_observation): latent [n, 48, 1, 24,
        20], text [n, L, D], proprio [n, 14] -> keys, values: lists over layers of [n, T, W]."""
        keys = [[] for _ in range(self.num_layers)]
        values = [[] for _ in range(self.num_layers)]
        for s in range(0, latent.shape[0], chunk):
            k, v = self._prefill(latent[s:s + chunk], text[s:s + chunk], proprio[s:s + chunk])
            for l in range(self.num_layers):
                keys[l].append(k[l])
                values[l].append(v[l])
        return [torch.cat(x) for x in keys], [torch.cat(x) for x in values]

    def _prefill(self, latent, text, proprio, history: Optional[History] = None, return_tokens: bool = False):
        context, mask = self.context(text.to(self._dtype()), proprio)
        expert = self.video
        dtype = self._dtype()
        x, _, mod, ctx, ctx_mask, freqs, _, _, _, _ = expert.prepare(
            x=latent.to(dtype), timestep=torch.zeros(latent.shape[0], device=latent.device, dtype=dtype),
            context=context.to(dtype), context_mask=mask, fuse_vae_embedding_in_latents=True)
        full = torch.ones((x.shape[1], x.shape[1]), dtype=torch.bool, device=x.device)
        keys, values = [], []
        for l, block in enumerate(expert.blocks):
            q, k, v, residual, gate, shift, scale, ffn_gate, _ = self.mot._build_expert_attention_io(
                expert=expert, block=block, x=x, freqs=freqs, t_mod=mod)
            o = self._attend(q, k, v, full, history, l)
            x = self.mot._apply_expert_post_block_tensor(
                block=block, residual_x=residual, mixed_attn_out=o, gate_msa=gate, shift_mlp=shift,
                scale_mlp=scale, gate_mlp=ffn_gate, context=ctx, context_mask=ctx_mask)
            keys.append(k)
            values.append(v)
        return (keys, values, x) if return_tokens else (keys, values)

    @torch.no_grad()
    def history(self, batch: dict) -> Optional[History]:
        """History K / V of a batch with hist_latent [B, K, ...], hist_proprio, hist_valid, hist_pos; None if the
        variant shows no frames or no sample has any."""
        if "hist_valid" not in batch or not bool(batch["hist_valid"].any()):
            return None
        valid = batch["hist_valid"]
        b, k = valid.shape
        idx = valid.nonzero(as_tuple=False)
        keys, values = self.prefill_frames(batch["hist_latent"][idx[:, 0], idx[:, 1]], batch["text"][idx[:, 0]],
                                           batch["hist_proprio"][idx[:, 0], idx[:, 1]])
        t, w = keys[0].shape[1], keys[0].shape[2]
        out_k, out_v = [], []
        for kl, vl in zip(keys, values):
            fk = kl.new_zeros(b, k, t, w)
            fv = vl.new_zeros(b, k, t, w)
            fk[idx[:, 0], idx[:, 1]] = kl
            fv[idx[:, 0], idx[:, 1]] = vl
            fk = rerotate(fk, batch["hist_pos"].to(fk.device), self.num_heads)
            out_k.append(fk.reshape(b, k * t, w))
            out_v.append(fv.reshape(b, k * t, w))
        return History(out_k, out_v, valid.repeat_interleave(t, dim=1))

    # ------------------------------------------------------------------ attention
    def _attend(self, q, k, v, mask, history: Optional[History], layer: int):
        """q [B, S, W], k / v [B, S', W], mask [S, S'] bool -> [B, S, W]; with history: the gated mixture."""
        b, s, w = q.shape
        h = self.num_heads

        def heads(x):
            return x.reshape(b, x.shape[1], h, w // h).transpose(1, 2)

        qh = heads(q)
        base = F.scaled_dot_product_attention(qh, heads(k), heads(v), attn_mask=mask)
        if history is not None:
            hk = history.keys[layer].to(k.dtype)
            hv = history.values[layer].to(v.dtype)
            # additive, materialised (no stride-0 broadcast) mask with a finite floor: 11-11 H200 smoke gave NaN
            # gradients with the expanded boolean mask
            allowed = torch.cat((history.valid[:, None, None, :].expand(b, 1, s, hk.shape[1]),
                                 mask[None, None].expand(b, 1, s, mask.shape[1])), -1)
            bias = torch.zeros(allowed.shape, dtype=qh.dtype, device=qh.device)
            bias.masked_fill_(~allowed, torch.finfo(qh.dtype).min)
            mixed = F.scaled_dot_product_attention(qh, heads(torch.cat((hk, k), 1)), heads(torch.cat((hv, v), 1)),
                                                   attn_mask=bias)
            g = self.hist_gate[layer].to(base.dtype).view(1, h, 1, 1)
            base = base + g * (mixed - base)
        return base.transpose(1, 2).reshape(b, s, w)

    def _joint_layer(self, layer, xv, xa, fv, fa, mv, ma, cv, cmv, ca, cma, mask, history):
        vb = self.video.blocks[layer]
        ab = self.action.blocks[layer]
        qv, kv, vv, rv, gv, sv, scv, fgv, _ = self.mot._build_expert_attention_io(
            expert=self.video, block=vb, x=xv, freqs=fv, t_mod=mv)
        qa, ka, va, ra, ga, sa, sca, fga, _ = self.mot._build_expert_attention_io(
            expert=self.action, block=ab, x=xa, freqs=fa, t_mod=ma)
        o = self._attend(torch.cat((qv, qa), 1), torch.cat((kv, ka), 1), torch.cat((vv, va), 1), mask, history, layer)
        n = xv.shape[1]
        xv = self.mot._apply_expert_post_block_tensor(block=vb, residual_x=rv, mixed_attn_out=o[:, :n], gate_msa=gv,
                                                      shift_mlp=sv, scale_mlp=scv, gate_mlp=fgv, context=cv,
                                                      context_mask=cmv)
        xa = self.mot._apply_expert_post_block_tensor(block=ab, residual_x=ra, mixed_attn_out=o[:, n:], gate_msa=ga,
                                                      shift_mlp=sa, scale_mlp=sca, gate_mlp=fga, context=ca,
                                                      context_mask=cma)
        return xv, xa

    # ------------------------------------------------------------------ training
    def loss(self, batch: dict, noise: Optional[dict] = None, history: Optional[History] = "auto"):
        """The released FastWAM.training_loss on a cached clip. noise (validation): {"video", "action",
        "t_video", "t_action"} to fix the draws. Returns (total, {"video", "action"} per-sample tensors)."""
        dtype = self._dtype()
        clean = batch["video_latent"].to(dtype)
        b = clean.shape[0]
        if history == "auto":
            history = self.history(batch)
        nv = torch.randn_like(clean) if noise is None else noise["video"].to(clean)
        tv = (self.video_scheduler.sample_training_t(b, clean.device, dtype) if noise is None
              else noise["t_video"].to(clean.device, dtype))
        latents = self.video_scheduler.add_noise(clean, nv, tv)
        target_video = self.video_scheduler.training_target(clean, nv, tv)
        latents[:, :, 0:1] = clean[:, :, 0:1]
        actions = batch["actions"].to(dtype)
        na = torch.randn_like(actions) if noise is None else noise["action"].to(actions)
        ta = (self.action_scheduler.sample_training_t(b, actions.device, dtype) if noise is None
              else noise["t_action"].to(actions.device, dtype))
        noisy = self.action_scheduler.add_noise(actions, na, ta)
        target_action = self.action_scheduler.training_target(actions, na, ta)
        context, cmask = self.context(batch["text"].to(dtype), batch["proprio"], self.extra_feature(batch),
                                      self.ledger_input(batch))
        xv, t_v, mv, cv, cmv, fv, f, hh, ww, tpf = self.video.prepare(
            x=latents, timestep=tv, context=context, context_mask=cmask, fuse_vae_embedding_in_latents=True)
        xa, _, ma, ca, cma, fa = self.action.prepare(action_tokens=noisy, timestep=ta, context=context,
                                                     context_mask=cmask)
        mask = self.base_mask(xv.shape[1], xa.shape[1], tpf, xv.device)
        for layer in range(self.num_layers):
            args = (layer, xv, xa, fv, fa, mv, ma, cv, cmv, ca, cma, mask, history)
            if self.checkpoint_layers and torch.is_grad_enabled():
                xv, xa = torch.utils.checkpoint.checkpoint(self._joint_layer, *args, use_reentrant=False)
            else:
                xv, xa = self._joint_layer(*args)
        pred_video = self.video.post(xv, t_v, f, hh, ww)[:, :, 1:]
        pred_action = self.action.post(xa)
        per_frame = F.mse_loss(pred_video.float(), target_video[:, :, 1:].float(), reduction="none").mean(dim=(1, 3, 4))
        valid = batch["video_valid"][:, 1:].to(per_frame)
        video = (per_frame * valid).sum(1) / valid.sum(1).clamp(min=1.0)
        video = video * self.video_scheduler.training_weight(tv).to(video)
        per_step = F.mse_loss(pred_action.float(), target_action.float(), reduction="none").mean(dim=2)
        av = batch["action_valid"].to(per_step)
        action = (per_step * av).sum(1) / av.sum(1).clamp(min=1.0)
        action = action * self.action_scheduler.training_weight(ta).to(action)
        return video, action

    # ------------------------------------------------------------------ inference (online and offline sampling)
    @torch.no_grad()
    def prefill_current(self, batch: dict, history: Optional[History]):
        """Frame 0 of the clip (the current frame) prefilled with history (its queries see history as in training;
        it never sees future frames): per-layer K / V for the action expert, and the context."""
        context, cmask = self.context(batch["text"].to(self._dtype()), batch["proprio"], self.extra_feature(batch),
                                      self.ledger_input(batch))
        keys, values = self._prefill_with_context(batch["latent"], context, cmask, history)
        return keys, values, (context, cmask)

    def _prefill_with_context(self, latent, context, cmask, history):
        expert = self.video
        dtype = context.dtype
        x, _, mod, ctx, ctx_mask, freqs, _, _, _, _ = expert.prepare(
            x=latent.to(dtype), timestep=torch.zeros(latent.shape[0], device=latent.device, dtype=dtype),
            context=context, context_mask=cmask, fuse_vae_embedding_in_latents=True)
        full = torch.ones((x.shape[1], x.shape[1]), dtype=torch.bool, device=x.device)
        keys, values = [], []
        for l, block in enumerate(expert.blocks):
            q, k, v, residual, gate, shift, scale, ffn_gate, _ = self.mot._build_expert_attention_io(
                expert=expert, block=block, x=x, freqs=freqs, t_mod=mod)
            o = self._attend(q, k, v, full, history, l)
            x = self.mot._apply_expert_post_block_tensor(
                block=block, residual_x=residual, mixed_attn_out=o, gate_msa=gate, shift_mlp=shift,
                scale_mlp=scale, gate_mlp=ffn_gate, context=ctx, context_mask=ctx_mask)
            keys.append(k)
            values.append(v)
        return keys, values

    @torch.no_grad()
    def velocity(self, actions, timestep, current_kv, shared_context, history: Optional[History]):
        """Action-expert velocity with the current frame's cached K / V (+ history), all layers."""
        context, cmask = shared_context
        xa, _, ma, ca, cma, fa = self.action.prepare(action_tokens=actions, timestep=timestep, context=context,
                                                     context_mask=cmask)
        keys, values = current_kv
        t = keys[0].shape[1]
        mask = torch.ones((xa.shape[1], t + xa.shape[1]), dtype=torch.bool, device=xa.device)
        for layer, block in enumerate(self.action.blocks):
            q, k, v, residual, gate, shift, scale, ffn_gate, _ = self.mot._build_expert_attention_io(
                expert=self.action, block=block, x=xa, freqs=fa, t_mod=ma)
            o = self._attend(q, torch.cat((keys[layer], k), 1), torch.cat((values[layer], v), 1), mask, history, layer)
            xa = self.mot._apply_expert_post_block_tensor(
                block=block, residual_x=residual, mixed_attn_out=o, gate_msa=gate, shift_mlp=shift,
                scale_mlp=scale, gate_mlp=ffn_gate, context=ca, context_mask=cma)
        return self.action.post(xa)

    @torch.no_grad()
    def sample(self, batch: dict, noise: torch.Tensor, steps: int = 10, history: Optional[History] = "auto"):
        """Euler sampling of a 32-step chunk (released schedule, action shift); batch needs latent [B, 48, 1, 24,
        20] (the current frame), text, proprio, (+ history fields)."""
        if history == "auto":
            history = self.history(batch)
        keys, values, shared = self.prefill_current(batch, history)
        actions = noise.to(shared[0].dtype).clone()
        timesteps, deltas = self.action_scheduler.build_inference_schedule(steps, noise.device, actions.dtype)
        for timestep, delta in zip(timesteps, deltas):
            v = self.velocity(actions, timestep.expand(len(actions)), (keys, values), shared, history)
            actions = self.action_scheduler.step(v.to(actions.dtype), delta, actions)
        return actions.float()
