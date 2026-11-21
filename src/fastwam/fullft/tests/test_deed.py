"""Plan v19 3.2 (11-22, Deed Memory training parts) on CPU: (1) decision-point weighting and (2) the next-event head.
Acceptance (plan v19): with the parts off, samples, parameters, random draws and the training loss are exactly the
earlier ones; each part has a unit test."""
import json

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")

from torch import nn  # noqa: E402

from fastwam.fullft.data import (NEXT_EVENT_CLASSES, DenseEpisodes, Samples, collate, decision_weight,  # noqa: E402
                                 next_event_label, train_items)
from fastwam.fullft.history import HistoryRule  # noqa: E402
from fastwam.fullft.model import FullModel  # noqa: E402

LAYERS, HEADS, HEAD_DIM, VIDEO, ACTION, TEXT = 2, 4, 24, 96, 32, 16

EVENTS = [{"frame": 10, "arm": 0, "kind": "close", "confirmed": 10},
          {"frame": 20, "arm": 0, "kind": "bottom", "confirmed": 24},
          {"frame": 30, "arm": 1, "kind": "open", "confirmed": 30},
          {"frame": 30, "arm": 0, "kind": "top", "confirmed": 33}]


def _model(next_event=False, seed=0, variant="ar"):
    from fastwam.models.wan22.action_dit import ActionDiT
    from fastwam.models.wan22.mot import MoT
    from fastwam.models.wan22.wan_video_dit import WanVideoDiT
    torch.manual_seed(seed)
    video = WanVideoDiT(hidden_dim=VIDEO, in_dim=48, ffn_dim=64, out_dim=48, text_dim=TEXT, freq_dim=32, eps=1e-6,
                        patch_size=(1, 2, 2), num_heads=HEADS, attn_head_dim=HEAD_DIM, num_layers=LAYERS,
                        has_image_input=False, seperated_timestep=True, fuse_vae_embedding_in_latents=True,
                        action_dim=14, video_attention_mask_mode="first_frame_causal")
    action = ActionDiT(hidden_dim=ACTION, action_dim=14, ffn_dim=64, text_dim=TEXT, freq_dim=32, eps=1e-6,
                       num_heads=HEADS, attn_head_dim=HEAD_DIM, num_layers=LAYERS)
    mot = MoT({"video": video, "action": action}, mot_checkpoint_mixed_attn=False)
    m = FullModel(mot, nn.Linear(14, TEXT), variant=variant, next_event=next_event)
    rng_after_build = torch.get_rng_state()
    with torch.no_grad():                         # lift zero-initialised output layers (not the new head)
        for name, p in m.named_parameters():
            if p.abs().sum() == 0 and not name.startswith(("hist_gate", "extra", "ledger", "next_event_head")):
                p.normal_(0, 0.02)
    return m.float(), rng_after_build


def _dense(tmp_path, n=60, episodes=2):
    root = tmp_path / "dense"
    records = []
    for k in range(episodes):
        eid = f"swap_blocks/episode_{k:07d}"
        folder = root / "cache" / eid.replace("/", "_")
        folder.mkdir(parents=True)
        text = torch.cat((torch.randn(3, TEXT), torch.zeros(4, TEXT)))
        torch.save({"latent": torch.randn(n, 48, 1, 4, 4), "video_latent": torch.randn(n, 48, 3, 4, 4),
                    "video_valid": torch.ones(n, 9, dtype=torch.bool), "text": text,
                    "text_valid": torch.tensor([True] * 3 + [False] * 4), "proprio": torch.randn(n, 14),
                    "actions": torch.randn(n, 14)}, folder / "encodings.pt")
        (folder / "COMPLETE.json").write_text("{}")
        records.append({"episode_id": eid, "task": "swap_blocks", "split": "train", "length": n})
    (root / "RECORDS.json").write_text(json.dumps(records))
    eps = DenseEpisodes([str(root)], ["swap_blocks"])
    return eps, {r["episode_id"]: EVENTS for r in eps.records}


def _noise(batch, seed=1):
    g = torch.Generator().manual_seed(seed)
    b = batch["actions"].shape[0]
    return {"video": torch.randn(batch["video_latent"].shape, generator=g),
            "action": torch.randn(batch["actions"].shape, generator=g),
            "t_video": torch.rand(b, generator=g) * 1000, "t_action": torch.rand(b, generator=g) * 1000}


def test_decision_weight_windows():
    w = [decision_weight(EVENTS, a, 3.0, 16) for a in (0, 10, 23, 24, 29, 39, 40, 45, 46)]
    # close never counts; bottom confirmed at 24 -> 24..39; open confirmed at 30 -> 30..45
    assert w == [1.0, 1.0, 1.0, 3.0, 3.0, 3.0, 3.0, 3.0, 1.0]
    assert decision_weight(EVENTS, 26, 3.0, 2) == 1.0          # window 2: 24, 25 only
    assert decision_weight(EVENTS, 11, 3.0, 16, ("close",)) == 3.0
    assert decision_weight([{"frame": 5, "arm": 0, "kind": "open"}], 5, 2.0, 1) == 2.0   # no 'confirmed' -> its frame
    assert decision_weight([], 5, 3.0, 16) == 1.0


def test_next_event_label():
    labels = [next_event_label(EVENTS, a) for a in (0, 10, 11, 20, 21, 30, 31)]
    # close arm 0 = 0; bottom arm 0 = 2 * 2 + 0 = 4; frame 30: arm 0 (top, 3 * 2 + 0 = 6) before arm 1; none = 8
    assert labels == [0, 0, 4, 4, 6, 6, NEXT_EVENT_CLASSES - 1]
    assert NEXT_EVENT_CLASSES == 9
    assert next_event_label([{"frame": 3, "arm": 1, "kind": "open"}], 0) == 1 * 2 + 1


def test_samples_off_unchanged_on_add_fields(tmp_path):
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    for rule in (HistoryRule("ar"), HistoryRule("arprop", event_max=4, lag=4, ordinal=16)):
        base = Samples(eps, items, rule, events, "valid", augment=True, seed=3)
        off = Samples(eps, items, rule, events, "valid", augment=True, seed=3, decision=None, next_event=False)
        on = Samples(eps, items, rule, events, "valid", augment=True, seed=3, decision=(3.0, 16, ("open", "bottom")),
                     next_event=True)
        for i in (0, 25, 31, 59, 75):
            r0, r1, r2 = base[i], off[i], on[i]
            assert set(r0) == set(r1) and all(torch.equal(r0[k], r1[k]) for k in r0)
            assert set(r2) - set(r0) == {"loss_weight", "next_event"}
            assert all(torch.equal(r0[k], r2[k]) for k in r0)
            e, a = items[i]
            assert float(r2["loss_weight"]) == decision_weight(EVENTS, a, 3.0, 16)
            assert int(r2["next_event"]) == next_event_label(EVENTS, a)
        batch = collate([on[i] for i in (0, 25, 31)])
        assert batch["loss_weight"].tolist() == [1.0, 3.0, 3.0] and batch["next_event"].tolist() == [0, 6, 8]
    with pytest.raises(ValueError):                 # the three-frame model needs the events file for the new parts
        Samples(eps, items, HistoryRule("ar"), {}, "valid", decision=(3.0, 16, ("open",)))
    Samples(eps, items, HistoryRule("ar"), {}, "valid")       # off: no events needed, as before


def test_config_parts(tmp_path):
    from fastwam.fullft.config import load
    cfg = load(None, [])
    assert cfg.decision is None and not cfg.next_event_head
    assert cfg.model.decision_weight == 1.0 and cfg.model.next_event_loss == 0.0
    with pytest.raises(ValueError):
        load(None, ["model.decision_weight=3"])                 # needs data.events
    with pytest.raises(ValueError):
        load(None, ["model.next_event_loss=0.1"])
    ev = ["data.events=[/x/events_swap_blocks.json]"]
    cfg = load(None, ev + ["model.decision_weight=3", "model.next_event_loss=0.1"])
    assert cfg.decision == (3.0, 16, ("open", "bottom")) and cfg.next_event_head
    for bad in ("model.decision_weight=0", "model.decision_window=0", "model.decision_kinds=[press]",
                "model.next_event_loss=-1"):
        with pytest.raises(ValueError):
            load(None, ev + [bad])
    # an export written before 11-22 (its config has none of the new keys) builds the same model as before
    from fastwam.fullft.config import _build, RunConfig
    old = cfg.to_dict()
    for k in ("decision_weight", "decision_window", "decision_kinds", "next_event_loss"):
        old["model"].pop(k)
    rebuilt = _build(RunConfig, old)
    assert rebuilt.decision is None and not rebuilt.next_event_head


def test_head_draws_no_random_numbers_and_changes_nothing_at_start(tmp_path):
    m0, rng0 = _model(next_event=False)
    m1, rng1 = _model(next_event=True)
    assert torch.equal(rng0, rng1)                             # the head drew no random number
    s0, s1 = m0.state_dict(), m1.state_dict()
    assert set(s1) - set(s0) == {"next_event_head.weight", "next_event_head.bias"}
    assert all(torch.equal(s0[k], s1[k]) for k in s0)
    assert m1.next_event_head.weight.shape == (NEXT_EVENT_CLASSES, ACTION)
    eps, events = _dense(tmp_path)
    items = train_items(eps)
    ds = Samples(eps, items, HistoryRule("ar"), events, "valid", next_event=True)
    batch = collate([ds[i] for i in (5, 25, 40)])
    noise = _noise(batch)
    v0, a0 = m0.loss(batch, noise)
    aux = {}
    v1, a1 = m1.loss(batch, noise, aux=aux)
    assert torch.equal(v0, v1) and torch.equal(a0, a1)         # the returned losses do not depend on the head
    assert torch.allclose(aux["next_event"], torch.full((3,), float(torch.log(torch.tensor(9.0)))))
    v2, a2 = m1.loss(batch, noise)                             # no aux: head not run
    assert torch.equal(v1, v2) and torch.equal(a1, a2)
    # step 0: the zero head sends no gradient into the trunk; the head itself gets one
    aux = {}
    m1.loss(batch, noise, aux=aux)
    aux["next_event"].mean().backward()
    trunk = [p.grad for n, p in m1.named_parameters() if not n.startswith("next_event_head") and p.grad is not None]
    assert all(float(g.abs().sum()) == 0.0 for g in trunk)
    assert float(m1.next_event_head.weight.grad.abs().sum()) > 0
    # after one step on the head, the cross entropy reaches the action branch
    with torch.no_grad():
        m1.next_event_head.weight -= 0.5 * m1.next_event_head.weight.grad
    m1.zero_grad()
    aux = {}
    m1.loss(batch, noise, aux=aux)
    aux["next_event"].mean().backward()
    g = sum(float(p.grad.abs().sum()) for n, p in m1.named_parameters()
            if n.startswith("mot.mixtures.action") and p.grad is not None)
    assert g > 0


def test_objective_off_is_the_earlier_expression_and_on_weights():
    from fastwam.fullft.config import load
    from fastwam.fullft.train import objective
    cfg = load(None, ["model.video_loss=0.7"])
    g = torch.Generator().manual_seed(0)
    v, a = torch.rand(4, generator=g), torch.rand(4, generator=g)
    earlier = (cfg.model.video_loss * v.mean() + cfg.model.action_loss * a.mean()) / 8
    assert torch.equal(objective(cfg, v, a, {}, None, 8), earlier)
    assert torch.equal(objective(cfg, v, a, {}, {}, 8), earlier)            # an empty aux adds nothing
    w = torch.tensor([3.0, 1.0, 1.0, 3.0])
    want = (0.7 * (w * v).mean() + 1.0 * (w * a).mean()) / 8
    assert torch.allclose(objective(cfg, v, a, {"loss_weight": w}, None, 8), want)
    cfg2 = load(None, ["data.events=[/x.json]", "model.next_event_loss=0.1"])
    ce = torch.tensor([2.0, 1.0, 0.5, 0.5])
    got = objective(cfg2, v, a, {}, {"next_event": ce}, 8)
    assert torch.allclose(got, (v.mean() + a.mean()) / 8 + 0.1 * ce.mean() / 8)


def test_export_with_head_loads_strict(tmp_path):
    """online.load_export builds the head from the export's config (strict load); exports without it are unchanged."""
    m1, _ = _model(next_event=True)
    m0, _ = _model(next_event=False)
    with pytest.raises(RuntimeError):
        m0.load_state_dict(m1.state_dict(), strict=True)
    m1b, _ = _model(next_event=True, seed=5)
    m1b.load_state_dict(m1.state_dict(), strict=True)
