"""Objective math against the released scheduler."""
import math

import pytest

torch = pytest.importorskip("torch")

from fastwam.memory_v2.config import ObjectiveConfig  # noqa: E402
from fastwam.memory_v2.objectives import (bell_weight, crossover_tau, identifiability, loss_weight,  # noqa: E402
                                          masked_mse, sample_tau, tau_mass_above)
from fastwam.models.wan22.schedulers.scheduler_continuous import WanContinuousFlowMatchScheduler  # noqa: E402


@pytest.mark.parametrize("shift", [1.0, 5.0])
def test_bell_weight_matches_released_scheduler(shift):
    scheduler = WanContinuousFlowMatchScheduler(shift=shift)
    tau = torch.linspace(0, 1, 101)
    assert torch.allclose(bell_weight(tau, shift), scheduler.training_weight(1000 * tau), atol=1e-5)


def test_released_weight_vanishes_at_pure_noise_but_floor_does_not():
    assert float(bell_weight(torch.tensor([1.0]), 1.0)) < 1e-6
    cfg = ObjectiveConfig(weight_mode="bell_floor", weight_floor=0.25)
    assert float(loss_weight(torch.tensor([1.0]), cfg)) == pytest.approx(0.25)


def test_tau_sampler_ranges_and_determinism():
    cfg = ObjectiveConfig(tau_mode="mixture", high_noise_prob=0.5, high_noise_low=0.8)
    a = sample_tau(1000, cfg, torch.Generator().manual_seed(0))
    b = sample_tau(1000, cfg, torch.Generator().manual_seed(0))
    assert torch.equal(a, b) and float(a.min()) >= 0 and float(a.max()) < 1
    assert 0.45 < float((a >= 0.8).float().mean()) < 0.7


def test_high_noise_mass_increases():
    released_like = ObjectiveConfig(tau_mode="shift", tau_shift=5.0, weight_mode="bell", weight_shift=5.0)
    s1_like = ObjectiveConfig(tau_mode="uniform", weight_mode="bell", weight_shift=1.0)
    v2 = ObjectiveConfig()
    s1 = tau_mass_above(0.8, s1_like)
    assert s1 < 0.12
    assert tau_mass_above(0.8, released_like) > 2 * s1
    assert tau_mass_above(0.8, v2) > 2 * s1


def test_masked_mse_and_identifiability():
    prediction = torch.zeros(2, 4, 3)
    target = torch.ones(2, 4, 3)
    valid = torch.tensor([[True, True, False, False], [True, True, True, True]])
    target[0, 2:] = 100.0
    assert torch.allclose(masked_mse(prediction, target, valid), torch.ones(2))
    with pytest.raises(ValueError):
        masked_mse(prediction, target, torch.zeros(2, 4, dtype=torch.bool))
    assert identifiability(0.5, 4.0) == pytest.approx(4.0)
    assert crossover_tau(6.0) == pytest.approx(0.75)
    assert math.isinf(identifiability(0.0, 1.0))
