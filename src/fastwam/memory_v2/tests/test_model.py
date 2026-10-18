"""CPU tests of the read-time-selection memory on a tiny backbone."""
import pytest

torch = pytest.importorskip("torch")

from fastwam.memory_v2.config import GuidanceConfig, MemoryV2Config, ObjectiveConfig  # noqa: E402
from fastwam.memory_v2.metrics import (attention_report, branch_commitment, gate_profile,  # noqa: E402
                                       history_sensitivity, token_geometry)
from fastwam.memory_v2.model import MemoryV2Model  # noqa: E402
from fastwam.memory_v2.objectives import compute_loss  # noqa: E402
from fastwam.memory_v2.tests.helpers import TINY, TinyBackbone, make_batch  # noqa: E402


def _model(**overrides):
    torch.manual_seed(1)
    cfg = MemoryV2Config(**{**TINY, **overrides})
    return MemoryV2Model(TinyBackbone(), cfg).float()


def _bare_velocity(model, batch, noisy, timestep):
    kv, context = model.backbone.encode(batch)
    x, aux = model.backbone.prepare(noisy, timestep, context)
    for i in range(model.backbone.num_action_layers):
        x = model.backbone.block(i, x, aux, kv)
    return model.backbone.post(x, aux)


def _make_output_nonzero(model, std=0.05):
    with torch.no_grad():
        for injector in model.memory.injectors.values():
            injector.out.weight.normal_(0, std)


def test_zero_init_reproduces_backbone_exactly():
    model = _model()
    batch = make_batch()
    timestep = torch.full((3,), 700.0)
    noisy = torch.randn_like(batch["actions"])
    conditions = model.conditions(batch)
    reference = _bare_velocity(model, batch, noisy, timestep)
    for mode in ("on", "null", "off"):
        assert torch.equal(model.velocity(noisy, timestep, conditions, mode), reference)


def test_memory_changes_output_only_through_history_when_on():
    model = _model()
    _make_output_nonzero(model)
    batch = make_batch()
    timestep = torch.full((3,), 900.0)
    noisy = torch.randn_like(batch["actions"])
    conditions = model.conditions(batch)
    on = model.velocity(noisy, timestep, conditions, "on")
    off = model.velocity(noisy, timestep, conditions, "off")
    null = model.velocity(noisy, timestep, conditions, "null")
    assert not torch.allclose(on, off)
    # Null branch must not depend on history content.
    altered = dict(batch)
    altered["history"] = batch["history"] + 3.0 * torch.randn_like(batch["history"])
    null_altered = model.velocity(noisy, timestep, model.conditions(altered), "null")
    assert torch.allclose(null, null_altered, atol=1e-6)
    on_altered = model.velocity(noisy, timestep, model.conditions(altered), "on")
    assert not torch.allclose(on, on_altered)


def test_padding_frames_are_ignored():
    model = _model()
    _make_output_nonzero(model)
    batch = make_batch()
    timestep = torch.full((3,), 500.0)
    noisy = torch.randn_like(batch["actions"])
    reference = model.velocity(noisy, timestep, model.conditions(batch))
    altered = dict(batch)
    history = batch["history"].clone()
    history[~batch["history_valid"]] = 1e3
    altered["history"] = history
    assert torch.allclose(reference, model.velocity(noisy, timestep, model.conditions(altered)), atol=1e-5)


def test_future_frames_rejected():
    model = _model()
    batch = make_batch()
    bad = dict(batch)
    ids = batch["frame_ids"].clone()
    ids[0, 0] = int(batch["current_ids"][0]) + 1
    bad["frame_ids"] = ids
    with pytest.raises(ValueError):
        model.conditions(bad)


def test_empty_history_is_well_defined():
    model = _model()
    _make_output_nonzero(model)
    batch = make_batch()
    empty = dict(batch)
    empty["history_valid"] = torch.zeros_like(batch["history_valid"])
    out = model.velocity(torch.randn_like(batch["actions"]), torch.full((3,), 1000.0), model.conditions(empty))
    assert torch.isfinite(out).all()


def test_action_tokens_read_different_content():
    """No query bottleneck: different action tokens can attend to different memory tokens."""
    model = _model()
    batch = make_batch()
    conditions = model.conditions(batch)
    injector = model.memory.injectors["3"]
    hidden = torch.randn(3, 8, TINY["action_hidden"])
    probs = injector.attention(hidden, conditions.memory_kv[3], conditions.memory.valid)
    per_token = probs.mean(1)                     # [B, Q, T]
    spread = (per_token - per_token.mean(1, keepdim=True)).abs().amax()
    assert float(spread) > 1e-3


def test_objective_backpropagates_into_all_memory_parameters():
    model = _model()
    batch = make_batch()
    cfg = ObjectiveConfig(memory_dropout=0.0)
    generator = torch.Generator().manual_seed(0)
    # Step 1: zero-init output -> only the output projections receive gradient.
    out = compute_loss(model, batch, cfg, generator)
    out["loss"].backward()
    for name, parameter in model.memory.named_parameters():
        if ".out." in name:
            assert parameter.grad is not None and parameter.grad.abs().sum() > 0, name
    # After the output is non-zero, queries/keys/values/tokenizer all receive gradient.
    model.zero_grad(set_to_none=True)
    _make_output_nonzero(model)
    with torch.no_grad():
        model.memory.tau_gate.net[2].weight.normal_(0, 0.05)
    out = compute_loss(model, batch, cfg, torch.Generator().manual_seed(1))
    out["loss"].backward()
    missing = [n for n, p in model.memory.named_parameters()
               if p.grad is None or float(p.grad.abs().sum()) == 0.0]
    assert not missing, missing
    assert all(p.grad is None for p in model.backbone.parameters())


def test_endpoint_and_dropout_terms():
    model = _model()
    batch = make_batch()
    out = compute_loss(model, batch, ObjectiveConfig(endpoint_weight=1.0, memory_dropout=0.5),
                       torch.Generator().manual_seed(3))
    assert "endpoint" in out and torch.isfinite(out["loss"])
    assert out["memory_dropped"].dtype == torch.bool


def test_guided_sampling_and_trace():
    model = _model()
    _make_output_nonzero(model)
    batch = make_batch()
    conditions = model.conditions(batch)
    noise = torch.randn_like(batch["actions"])
    plain, _ = model.sample(conditions, noise, GuidanceConfig(steps=5, scale=1.0))
    guided, records = model.sample(conditions, noise, GuidanceConfig(steps=5, scale=2.0, min_sigma=0.7), trace=True)
    assert len(records) == 5 and records[0]["sigma"] == 1.0 and records[0]["guided"]
    assert not records[-1]["guided"]
    assert not torch.allclose(plain, guided)
    # The last x0 estimate equals the final chunk exactly (x0 = x - sigma u, final = x + u * (0 - sigma)).
    steps = branch_commitment(records, guided, tolerance=1e-4)
    assert all(s is not None and s <= 4 for s in steps)


def test_conditions_reused_across_steps_do_not_change():
    model = _model()
    _make_output_nonzero(model)
    batch = make_batch()
    conditions = model.conditions(batch)
    before = {k: (a.clone(), b.clone()) for k, (a, b) in conditions.memory_kv.items()}
    model.sample(conditions, torch.randn_like(batch["actions"]), GuidanceConfig(steps=3, scale=1.5))
    for k, (a, b) in conditions.memory_kv.items():
        assert torch.equal(a, before[k][0]) and torch.equal(b, before[k][1])


def test_metrics_run():
    model = _model()
    _make_output_nonzero(model)
    batch = make_batch()
    result = history_sensitivity(model, batch, taus=(0.2, 0.9))
    assert set(result) == {"tau", "null", "shuffle_time", "swap", "swap_content"}
    assert all(v >= 0 for v in result["null"])
    conditions = model.conditions(batch)
    report = attention_report(model, conditions, torch.randn_like(batch["actions"]), 0.9)
    assert set(report) == {1, 3, 5}
    for row in report.values():
        total = row["null_mass"] + sum(row[f"role{r}_mass"] for r in range(4))
        assert abs(total - 1.0) < 1e-4
    geometry = token_geometry(torch.randn(32, 16))
    assert geometry["effective_rank"] > 5
    profile = gate_profile(model)
    assert profile["tau"][0] == 0.0 and abs(profile["1"][0] - 1.0) < 1e-6


def test_pooling_reduces_tokens():
    model = _model(pool=(2, 3))
    batch = make_batch()
    conditions = model.conditions(batch)
    frames = batch["history"].shape[1]
    assert conditions.memory.tokens.shape[1] == TINY["null_tokens"] + frames * 2


def test_memory_state_roundtrip():
    model = _model()
    _make_output_nonzero(model)
    state = model.memory_state_dict()
    other = _model()
    other.load_memory_state_dict(state)
    batch = make_batch()
    noisy = torch.randn_like(batch["actions"])
    t = torch.full((3,), 400.0)
    assert torch.equal(model.velocity(noisy, t, model.conditions(batch)),
                       other.velocity(noisy, t, other.conditions(batch)))


def test_swap_content_keeps_clock():
    from fastwam.memory_v2.metrics import _with_history
    batch = make_batch()
    swapped = _with_history(batch, "swap_content", None)
    assert torch.equal(swapped["frame_ids"], batch["frame_ids"])
    assert torch.equal(swapped["current_ids"], batch["current_ids"])
    assert torch.equal(swapped["history"], batch["history"].roll(1, dims=0))
    assert not bool((swapped["history_valid"] & ~batch["history_valid"]).any())


def test_relative_time_only_is_shift_invariant():
    torch.manual_seed(0)
    from fastwam.memory_v2.modules import MemoryTokenizer
    cfg = MemoryV2Config(**{**TINY, "absolute_time": False})
    tokenizer = MemoryTokenizer(cfg)
    batch = make_batch()
    args = (batch["history"], batch["frame_ids"], batch["roles"], batch["history_valid"], batch["current_ids"])
    shifted = (batch["history"], batch["frame_ids"] + 64, batch["roles"], batch["history_valid"], batch["current_ids"] + 64)
    a, b = tokenizer(*args), tokenizer(*shifted)
    assert torch.allclose(a.tokens, b.tokens, atol=1e-5)
    absolute = MemoryTokenizer(MemoryV2Config(**TINY))
    absolute.load_state_dict(tokenizer.state_dict())
    assert not torch.allclose(absolute(*args).tokens, absolute(*shifted).tokens, atol=1e-5)
