"""Mechanism metrics (M4): does the action expert actually use history, and when?

* history_sensitivity: relative change of the predicted velocity when the
  history is replaced (null / time-shuffled / swapped across the batch), per
  noise level. The paper's central curve is sensitivity vs tau.
* attention_report: per injected layer, attention mass on null tokens and on
  each history role (anchor / landmark / recent / current) and its entropy.
* token_geometry: collapse diagnostics for any set of vectors (memory_s1 slots
  or memory_v2 read-outs): min pairwise cosine, centred-norm %, effective rank.
* branch_commitment: from a traced sample, the step at which the clean-action
  estimate x0 is already within `tolerance` of its final value.
"""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence

import torch

from .config import NUM_ROLES


def token_geometry(x: torch.Tensor) -> Dict[str, float]:
    """x: [N, D]."""
    x = x.detach().double()
    norms = x.norm(dim=1).clamp_min(1e-12)
    cosine = (x @ x.T) / (norms[:, None] * norms[None, :])
    centred = x - x.mean(0, keepdim=True)
    singular = torch.linalg.svdvals(x)
    p = singular / singular.sum().clamp_min(1e-12)
    entropy = -(p * p.clamp_min(1e-12).log()).sum()
    energy = singular.square()
    return {"min_cosine": float(cosine.min()),
            "centred_norm_percent": float(100 * centred.norm() / x.norm().clamp_min(1e-12)),
            "effective_rank": float(entropy.exp()),
            "rank_one_energy": float(energy[0] / energy.sum().clamp_min(1e-12))}


def _with_history(batch: Dict[str, torch.Tensor], variant: str, generator: Optional[torch.Generator]):
    batch = dict(batch)
    if variant == "shuffle_time":
        ids, valid = batch["frame_ids"].clone(), batch["history_valid"]
        for b in range(ids.shape[0]):
            index = torch.nonzero(valid[b], as_tuple=False).flatten()
            if len(index) > 1:
                order = index[torch.randperm(len(index), generator=generator).to(index.device)]
                ids[b, index] = batch["frame_ids"][b, order]
        batch["frame_ids"] = ids
    elif variant == "swap":
        if batch["history"].shape[0] < 2:
            raise ValueError("Swapping histories needs a batch of at least two samples.")
        for key in ("history", "frame_ids", "roles", "history_valid"):
            batch[key] = batch[key].roll(1, dims=0)
        # Keep causality for the receiving sample: drop frames from its future.
        batch["history_valid"] = batch["history_valid"] & (batch["frame_ids"] <= batch["current_ids"][:, None])
    elif variant == "swap_content":
        # Keep the receiving sample's clock (frame ids, roles, current id); take the
        # observation content from another sample. Separates content from timing.
        if batch["history"].shape[0] < 2:
            raise ValueError("Swapping content needs a batch of at least two samples.")
        donor_valid = batch["history_valid"].roll(1, dims=0)
        batch["history"] = batch["history"].roll(1, dims=0)
        batch["history_valid"] = batch["history_valid"] & donor_valid
    elif variant != "null":
        raise ValueError(f"Unknown history variant {variant}.")
    return batch


@torch.no_grad()
def history_sensitivity(model, batch: Dict[str, torch.Tensor], taus: Sequence[float] = (0.1, 0.3, 0.5, 0.7, 0.8, 0.9, 0.95, 1.0),
                        variants: Iterable[str] = ("null", "shuffle_time", "swap", "swap_content"),
                        seed: int = 0) -> Dict[str, List[float]]:
    """Relative L2 change of the velocity, mean over the batch, for each tau and variant."""
    generator = torch.Generator().manual_seed(seed)
    actions = batch["actions"].float()
    noise = torch.randn(actions.shape, generator=generator).to(actions.device)
    base = model.conditions(batch)
    others = {}
    for variant in variants:
        if variant == "null":
            others[variant] = base.null()
        elif variant in ("swap", "swap_content") and actions.shape[0] < 2:
            continue
        else:
            others[variant] = model.conditions(_with_history(batch, variant, generator))
    result = {"tau": [float(t) for t in taus]}
    for variant in others:
        result[variant] = []
    for tau in taus:
        timestep = torch.full((actions.shape[0],), 1000.0 * tau, device=actions.device)
        noisy = (1 - tau) * actions + tau * noise
        reference = model.velocity(noisy, timestep, base).float()
        scale = reference.flatten(1).norm(dim=1).clamp_min(1e-6)
        for variant, conditions in others.items():
            changed = model.velocity(noisy, timestep, conditions).float()
            result[variant].append(float(((changed - reference).flatten(1).norm(dim=1) / scale).mean()))
    return result


@torch.no_grad()
def attention_report(model, conditions, actions: torch.Tensor, tau: float) -> Dict[int, Dict[str, float]]:
    """Attention statistics of every injector at one noise level (runs one velocity pass)."""
    report = {}
    hooks = []

    def make_hook(layer):
        def hook(module, inputs, output):
            hidden, kv, valid = inputs[0], inputs[1], inputs[2]
            probs = module.attention(hidden, kv, valid)          # [B, H, Q, T]
            mass = probs.mean(dim=(1, 2))                        # [B, T]
            memory = conditions.memory
            row = {"null_mass": float((mass * (~memory.is_history)).sum(1).mean())}
            for role in range(NUM_ROLES):
                selected = memory.is_history & (memory.role == role)
                row[f"role{role}_mass"] = float((mass * selected).sum(1).mean())
            entropy = -(probs * probs.clamp_min(1e-12).log()).sum(-1).mean()
            row["entropy_nats"] = float(entropy)
            row["log_valid_tokens"] = float(valid.float().sum(1).clamp_min(1).log().mean())
            report[layer] = row
        return hook

    for layer, injector in model.memory.injectors.items():
        hooks.append(injector.register_forward_hook(make_hook(int(layer))))
    try:
        timestep = torch.full((actions.shape[0],), 1000.0 * tau, device=actions.device)
        model.velocity(actions, timestep, conditions)
    finally:
        for hook in hooks:
            hook.remove()
    return report


def branch_commitment(records: Sequence[Dict], final: torch.Tensor, tolerance: float = 0.1) -> List[Optional[int]]:
    """Per sample: first step index whose x0 estimate has relative error <= tolerance to the final chunk."""
    final = final.detach().float().cpu()
    scale = final.flatten(1).norm(dim=1).clamp_min(1e-6)
    result: List[Optional[int]] = [None] * final.shape[0]
    for step, record in enumerate(records):
        error = (record["x0"].float() - final).flatten(1).norm(dim=1) / scale
        for b in range(final.shape[0]):
            if result[b] is None and float(error[b]) <= tolerance:
                result[b] = step
    return result


@torch.no_grad()
def gate_profile(model, taus: Sequence[float] = tuple(i / 20 for i in range(21))) -> Dict[str, List[float]]:
    """Learned memory strength g_l(tau) for every injected layer."""
    if model.memory.tau_gate is None:
        return {}
    device = next(model.memory.parameters()).device
    timestep = torch.tensor([1000.0 * t for t in taus], device=device)
    gates = model.memory.gates(timestep).float().cpu()
    out = {"tau": [float(t) for t in taus]}
    for j, layer in enumerate(model.cfg.injection_layers):
        out[str(layer)] = gates[:, j].tolist()
    return out


def summarize_sensitivity(result: Dict[str, List[float]], high: float = 0.8) -> Dict[str, float]:
    """Scalar summaries: mean sensitivity at tau >= high vs tau < high, per variant."""
    taus = result["tau"]
    out = {}
    for key, values in result.items():
        if key == "tau":
            continue
        hi = [v for t, v in zip(taus, values) if t >= high]
        lo = [v for t, v in zip(taus, values) if t < high]
        out[f"{key}_high"] = sum(hi) / len(hi) if hi else math.nan
        out[f"{key}_low"] = sum(lo) / len(lo) if lo else math.nan
    return out
