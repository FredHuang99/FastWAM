"""Noise-level sampling, loss weights and the memory_v2 training objective.

Conventions follow fastwam.models.wan22.schedulers.scheduler_continuous:
    A_tau = (1 - tau) A* + tau eps,  target u* = eps - A*,  model timestep = 1000 tau,
inference integrates from tau = 1 (pure noise) to 0 with negative Euler steps.

Why the extra terms (see README, "Memory must speak first"):
  * For a history-dependent branch with chunk difference ||Delta||, the noisy
    action alone identifies the branch whenever (1 - tau)/tau * ||Delta|| is
    large; memory is only *necessary* above tau_c = ||Delta|| / (||Delta|| + d*).
  * The released bell weight is 0 at tau = 1 and ~0.05 at tau = 0.99, and uniform
    tau puts < 10% of the weight mass above 0.8, yet inference commits to a
    branch in the first one or two steps from tau = 1.
  * `mixture` sampling + `bell_floor` weighting + a unit-weight tau = 1 endpoint
    term move supervision to where memory is needed. Memory dropout trains the
    null-memory branch used by classifier-free memory guidance.
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Dict, Optional

import torch

from .config import ObjectiveConfig


def phi(u: torch.Tensor, shift: float) -> torch.Tensor:
    return shift * u / (1.0 + (shift - 1.0) * u)


@lru_cache(maxsize=None)
def bell_constants(shift: float, steps: int = 1000):
    """(y_min, normaliser) exactly as WanContinuousFlowMatchScheduler precomputes them."""
    u = torch.linspace(1.0, 0.0, steps + 1, dtype=torch.float64)[:-1]
    t = phi(u, shift) * float(steps)
    y = torch.exp(-2.0 * ((t - steps / 2.0) / steps) ** 2)
    y_min = float(y.min().item())
    return y_min, float((y - y_min).mean().item())


def bell_weight(tau: torch.Tensor, shift: float, eps: float = 1e-10) -> torch.Tensor:
    """Released FastWAM training weight as a function of tau in [0, 1]."""
    y_min, norm = bell_constants(float(shift))
    y = torch.exp(-2.0 * (tau.float() - 0.5) ** 2)
    return (y - y_min) / (norm + eps)


def loss_weight(tau: torch.Tensor, cfg: ObjectiveConfig) -> torch.Tensor:
    if cfg.weight_mode == "uniform":
        return torch.ones_like(tau, dtype=torch.float32)
    weight = bell_weight(tau, cfg.weight_shift)
    if cfg.weight_mode == "bell_floor":
        weight = weight.clamp(min=cfg.weight_floor)
    return weight


def sample_tau(batch: int, cfg: ObjectiveConfig, generator: Optional[torch.Generator] = None,
               device=None) -> torch.Tensor:
    """Float32 noise levels in [0, 1) drawn on CPU (deterministic under a generator)."""
    u = torch.rand(batch, generator=generator, dtype=torch.float32)
    if cfg.tau_mode == "uniform":
        tau = u
    else:
        tau = phi(u, cfg.tau_shift)
        if cfg.tau_mode == "mixture" and cfg.high_noise_prob > 0:
            pick = torch.rand(batch, generator=generator) < cfg.high_noise_prob
            high = cfg.high_noise_low + (1.0 - cfg.high_noise_low) * torch.rand(batch, generator=generator)
            tau = torch.where(pick, high, tau)
    tau = tau.clamp(0.0, 1.0 - 1e-6)
    return tau if device is None else tau.to(device)


def masked_mse(prediction: torch.Tensor, target: torch.Tensor, valid: torch.Tensor) -> torch.Tensor:
    """Per-sample mean over valid action steps and all action dims. valid: [B, H] bool."""
    if prediction.shape != target.shape or valid.shape != prediction.shape[:2]:
        raise ValueError("prediction/target [B,H,D] and valid [B,H] must align.")
    mask = valid.to(torch.float32)
    count = mask.sum(1)
    if bool((count <= 0).any()):
        raise ValueError("A sample with no valid action reached the objective.")
    error = (prediction.float() - target.float()).square().mean(-1)
    return (error * mask).sum(1) / count


def tau_mass_above(threshold: float, cfg: ObjectiveConfig, samples: int = 200000, seed: int = 0) -> float:
    """Monte-Carlo share of the (weighted) FM objective with tau >= threshold."""
    generator = torch.Generator().manual_seed(seed)
    tau = sample_tau(samples, cfg, generator)
    weight = loss_weight(tau, cfg)
    return float((weight * (tau >= threshold)).sum() / weight.sum().clamp_min(1e-12))


def compute_loss(model, batch: Dict[str, torch.Tensor], cfg: ObjectiveConfig,
                 generator: Optional[torch.Generator] = None,
                 noise: Optional[torch.Tensor] = None, tau: Optional[torch.Tensor] = None,
                 drop: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
    """FM + endpoint objective for one micro-batch.

    `model` must provide conditions(batch, drop) and velocity(actions, timestep, conditions).
    Randomness is drawn on CPU from `generator` unless explicit tensors are given,
    so gradient accumulation and resumption are reproducible.
    """
    actions = batch["actions"].float()
    valid = batch["action_valid"].bool()
    b = actions.shape[0]
    device = actions.device
    if noise is None:
        noise = torch.randn(actions.shape, generator=generator, dtype=torch.float32)
    noise = noise.to(device=device, dtype=torch.float32)
    if tau is None:
        tau = sample_tau(b, cfg, generator)
    tau = tau.to(device=device, dtype=torch.float32)
    if drop is None:
        drop = torch.rand(b, generator=generator) < cfg.memory_dropout
    drop = drop.to(device)
    conditions = model.conditions(batch, drop=drop)
    noisy = (1.0 - tau)[:, None, None] * actions + tau[:, None, None] * noise
    target = noise - actions
    prediction = model.velocity(noisy, 1000.0 * tau, conditions)
    error = masked_mse(prediction, target, valid)
    weight = loss_weight(tau, cfg).to(device)
    fm = (weight * error).mean()
    out = {"fm": fm, "fm_unweighted": error.detach(), "tau": tau.detach(), "memory_dropped": drop.detach()}
    loss = fm
    if cfg.endpoint_weight > 0:
        endpoint_prediction = model.velocity(noise, torch.full((b,), 1000.0, device=device), conditions)
        endpoint = masked_mse(endpoint_prediction, target, valid).mean()
        out["endpoint"] = endpoint
        loss = loss + cfg.endpoint_weight * endpoint
    out["loss"] = loss
    return out


def paired_endpoint_loss(model, current_batch: Dict[str, torch.Tensor],
                         history_a: Dict[str, torch.Tensor], actions_a: torch.Tensor, valid_a: torch.Tensor,
                         history_b: Dict[str, torch.Tensor], actions_b: torch.Tensor, valid_b: torch.Tensor,
                         noise: torch.Tensor) -> torch.Tensor:
    """Same present + same pure noise, two lawful histories with different correct chunks.

    A history-blind model incurs the irreducible error ||A_a - A_b||^2 / (4 n);
    only the memory can remove it. Used once paired data (blueprint S2) exists.
    """
    losses = []
    for history, actions, valid in ((history_a, actions_a, valid_a), (history_b, actions_b, valid_b)):
        batch = dict(current_batch)
        batch.update(history)
        conditions = model.conditions(batch, drop=None)
        b = actions.shape[0]
        prediction = model.velocity(noise, torch.full((b,), 1000.0, device=noise.device), conditions)
        losses.append(masked_mse(prediction, noise - actions.float(), valid).mean())
    return 0.5 * (losses[0] + losses[1])


def identifiability(tau: float, delta_norm: float) -> float:
    """Gaussian mean separation d(tau) = (1 - tau)/tau * ||Delta|| of two branches seen through A_tau."""
    if tau <= 0:
        return math.inf
    return (1.0 - tau) / tau * delta_norm


def crossover_tau(delta_norm: float, separation: float = 2.0) -> float:
    """Largest tau at which the noisy action alone still separates branches by `separation` sigmas."""
    return delta_norm / (delta_norm + separation)
