"""11-23 find-same parts (default off) on CPU: (1b) the pre-event window of the decision weighting and (2b) the
next-pose head (the body pose at the next gripper close, minus the pose now). Acceptance as plan v19 3.2: with the
parts off, samples, parameters, random draws and the training loss are exactly the earlier ones; each part has a test."""
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")

from fastwam.fullft.data import Samples, collate, decision_weight, next_pose_target, train_items  # noqa: E402
from fastwam.fullft.history import HistoryRule  # noqa: E402
from fastwam.fullft.tests.test_deed import ACTION, EVENTS, _dense, _model, _noise  # noqa: E402


def test_pre_window():
    # EVENTS: close arm 0 at 10; bottom at 20 (confirmed 24); open arm 1 at 30; top at 30 (confirmed 33)
    w = [decision_weight(EVENTS, a, 3.0, 0, ("open", "bottom"), 4, ("close",)) for a in range(0, 14)]
    assert w == [1.0] * 6 + [3.0] * 4 + [1.0] * 4                 # 6..9 = the 4 frames before the close at 10
    # the earlier windows still apply with pre > 0
    assert decision_weight(EVENTS, 25, 3.0, 16, ("open", "bottom"), 4, ("close",)) == 3.0
    assert decision_weight(EVENTS, 25, 3.0, 0, ("open", "bottom"), 4, ("close",)) == 1.0
    # pre = 0: exactly the earlier function
    for a in range(0, 50):
        assert decision_weight(EVENTS, a, 3.0, 16) == decision_weight(EVENTS, a, 3.0, 16, ("open", "bottom"), 0)
    assert decision_weight(EVENTS, 18, 2.0, 0, ("open",), 3, ("bottom",)) == 2.0     # other pre kinds


def test_next_pose_target():
    p = torch.arange(40 * 14, dtype=torch.float32).reshape(40, 14)
    t, ok = next_pose_target(EVENTS, 4, p)                         # next close at 10
    assert ok and torch.equal(t, p[10] - p[4])
    t, ok = next_pose_target(EVENTS, 10, p)                        # at the close itself: zero motion left
    assert ok and torch.equal(t, torch.zeros(14))
    t, ok = next_pose_target(EVENTS, 11, p)                        # no close left
    assert not ok and torch.equal(t, torch.zeros(14))
    t, ok = next_pose_target(EVENTS, 21, p, ("open", "top"))       # frame 30: open (arm 1) and top (arm 0) -> arm 0
    assert ok and torch.equal(t, p[30] - p[21])
    t, ok = next_pose_target([{"frame": 99, "arm": 0, "kind": "close"}], 5, p)   # past the end: clamped to the last
    assert ok and torch.equal(t, p[39] - p[5])


def test_samples_off_unchanged_on_add_fields(tmp_path):
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    for rule in (HistoryRule("ar"), HistoryRule("arprop", event_max=4, lag=4, ordinal=16)):
        base = Samples(eps, items, rule, events, "valid", augment=True, seed=3)
        old3 = Samples(eps, items, rule, events, "valid", augment=True, seed=3, decision=(3.0, 16, ("open", "bottom")))
        pre = Samples(eps, items, rule, events, "valid", augment=True, seed=3,
                      decision=(3.0, 16, ("open", "bottom"), 4, ("close",)), next_pose=("close",))
        off = Samples(eps, items, rule, events, "valid", augment=True, seed=3, next_pose=None)
        for i in range(0, len(items), 7):
            r0, r1, r3, rp = base[i], off[i], old3[i], pre[i]
            assert set(r0) == set(r1) and all(torch.equal(r0[k], r1[k]) for k in r0)
            assert set(rp) - set(r0) == {"loss_weight", "next_pose", "next_pose_valid"}
            assert all(torch.equal(r0[k], rp[k]) for k in r0)
            e, a = items[i]
            assert float(rp["loss_weight"]) == (3.0 if 6 <= a < 10 else float(r3["loss_weight"]))
            t, ok = next_pose_target(EVENTS, a, eps(e)["proprio"])
            assert bool(rp["next_pose_valid"]) == ok and torch.equal(rp["next_pose"], t)
        batch = collate([pre[i] for i in (0, 7, 12)])
        assert batch["next_pose"].shape == (3, 14) and batch["next_pose_valid"].tolist() == [True, True, False]
    with pytest.raises(ValueError):                              # the three-frame model needs the events file
        Samples(eps, items, HistoryRule("ar"), {}, "valid", next_pose=("close",))


def test_config_parts():
    from fastwam.fullft.config import RunConfig, _build, load
    cfg = load(None, [])
    assert cfg.decision is None and cfg.next_pose is None
    ev = ["data.events=[/x/events_observe_and_pickup.json]"]
    with pytest.raises(ValueError):
        load(None, ["model.next_pose_loss=0.1"])                 # needs data.events
    with pytest.raises(ValueError):
        load(None, ev + ["model.decision_pre_window=48"])        # needs a weight
    cfg = load(None, ev + ["model.decision_weight=3", "model.decision_window=0", "model.decision_pre_window=48",
                           "model.next_pose_loss=0.5"])
    assert cfg.decision == (3.0, 0, ("open", "bottom"), 48, ("close",)) and cfg.next_pose == ("close",)
    cfg = load(None, ev + ["model.decision_weight=3"])          # pre off: the earlier 3-tuple
    assert cfg.decision == (3.0, 16, ("open", "bottom"))
    for bad in ("model.decision_window=0", "model.next_pose_loss=-1", "model.next_pose_kinds=[press]",
                "model.decision_pre_kinds=[]"):
        with pytest.raises(ValueError):
            load(None, ev + ["model.decision_weight=3", bad])
    old = cfg.to_dict()                                         # an export written before 11-23
    for k in ("decision_pre_window", "decision_pre_kinds", "next_pose_loss", "next_pose_kinds"):
        old["model"].pop(k)
    rebuilt = _build(RunConfig, old)
    assert rebuilt.decision == (3.0, 16, ("open", "bottom")) and rebuilt.next_pose is None


def test_pose_head_draws_no_random_numbers_and_changes_nothing_at_start(tmp_path):
    m0, rng0 = _model()
    m1, rng1 = _model(next_pose=True)
    assert torch.equal(rng0, rng1)
    s0, s1 = m0.state_dict(), m1.state_dict()
    assert set(s1) - set(s0) == {"next_pose_head.weight", "next_pose_head.bias"}
    assert all(torch.equal(s0[k], s1[k]) for k in s0)
    assert m1.next_pose_head.weight.shape == (14, ACTION) and m1.aux_heads and not m0.aux_heads
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    ds = Samples(eps, items, HistoryRule("ar"), events, "valid", next_pose=("close",))
    rows = [ds[i] for i in (2, 5, 40)]                           # anchors before the close at 10, and one after
    assert [bool(r["next_pose_valid"]) for r in rows] == [True, True, False]
    batch = collate(rows)
    noise = _noise(batch)
    v0, a0 = m0.loss(batch, noise)
    aux = {}
    v1, a1 = m1.loss(batch, noise, aux=aux)
    assert torch.equal(v0, v1) and torch.equal(a0, a1)
    zero = batch["next_pose"].square().mean(-1) * batch["next_pose_valid"].float()
    assert torch.allclose(aux["next_pose"], zero) and torch.allclose(aux["next_pose_zero"], zero)
    assert float(aux["next_pose"][2]) == 0.0                     # no close left: no loss
    aux["next_pose"].mean().backward()
    trunk = [p.grad for n, p in m1.named_parameters() if not n.startswith("next_pose_head") and p.grad is not None]
    assert all(float(g.abs().sum()) == 0.0 for g in trunk)
    assert float(m1.next_pose_head.weight.grad.abs().sum()) > 0
    with torch.no_grad():
        m1.next_pose_head.weight -= 0.5 * m1.next_pose_head.weight.grad
    m1.zero_grad()
    aux = {}
    m1.loss(batch, noise, aux=aux)
    aux["next_pose"].mean().backward()
    g = sum(float(p.grad.abs().sum()) for n, p in m1.named_parameters()
            if n.startswith("mot.mixtures.action") and p.grad is not None)
    assert g > 0


def test_objective_with_pose_head():
    from fastwam.fullft.config import load
    from fastwam.fullft.train import objective
    g = torch.Generator().manual_seed(0)
    v, a = torch.rand(4, generator=g), torch.rand(4, generator=g)
    se = torch.tensor([0.4, 0.0, 0.2, 0.1])
    cfg = load(None, ["data.events=[/x.json]", "model.next_pose_loss=0.5"])
    got = objective(cfg, v, a, {}, {"next_pose": se, "next_pose_zero": se, "next_pose_valid": torch.ones(4)}, 8)
    assert torch.allclose(got, (v.mean() + a.mean()) / 8 + 0.5 * se.mean() / 8)
    cfg2 = load(None, ["data.events=[/x.json]", "model.next_pose_loss=0.5", "model.next_event_loss=0.1"])
    ce = torch.tensor([2.0, 1.0, 0.5, 0.5])
    got = objective(cfg2, v, a, {}, {"next_event": ce, "next_pose": se}, 8)
    assert torch.allclose(got, (v.mean() + a.mean()) / 8 + 0.1 * ce.mean() / 8 + 0.5 * se.mean() / 8)


def test_export_with_pose_head_loads_strict():
    m1, _ = _model(next_pose=True)
    m0, _ = _model()
    with pytest.raises(RuntimeError):
        m0.load_state_dict(m1.state_dict(), strict=True)
    m1b, _ = _model(next_pose=True, seed=5)
    m1b.load_state_dict(m1.state_dict(), strict=True)
