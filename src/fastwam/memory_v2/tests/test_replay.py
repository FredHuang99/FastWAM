"""kv_replay (plan v7 N1): temporal RoPE re-rotation, metadata, zero start, gradients, dropout, config."""
import json

import pytest

torch = pytest.importorskip("torch")

from fastwam.memory_v2.config import HistoryPolicyConfig, MemoryV2Config, V2Config  # noqa: E402
from fastwam.memory_v2.history import collate_selection, select_history  # noqa: E402
from fastwam.memory_v2.model import MemoryV2Model  # noqa: E402
from fastwam.memory_v2.replay import (recency_positions, rerotate_temporal, temporal_pairs,  # noqa: E402
                                      time_buckets)
from fastwam.memory_v2.tests.helpers import TINY, TinyBackbone  # noqa: E402

REPLAY = dict(TINY, video_dim=24, read="kv_replay", replay_rank=4, replay_time_buckets=6, replay_chunk=3)
POLICY = HistoryPolicyConfig(anchor_frames=1, landmark_stride=8, recent_frames=2, recent_stride=4, max_frames=6)


# ----------------------------------------------------------------------------- RoPE
def _wan_freqs(head_dim, f_index, h, w):
    """Wan 3D RoPE of one frame at temporal index f_index (negative = conjugate of the positive row)."""
    from fastwam.models.wan22.wan_video_dit import precompute_freqs_cis_3d
    ff, fh, fw = precompute_freqs_cis_3d(head_dim)
    row = ff[abs(f_index)].conj() if f_index < 0 else ff[f_index]
    return torch.cat([row.view(1, 1, -1).expand(h, w, -1), fh[:h].view(h, 1, -1).expand(h, w, -1),
                      fw[:w].view(1, w, -1).expand(h, w, -1)], dim=-1).reshape(h * w, 1, -1)


@pytest.mark.parametrize("position", [-1, -3, -17, -48])
def test_rerotation_equals_encoding_at_the_negative_index(position):
    from fastwam.models.wan22.wan_video_dit import rope_apply
    heads, head_dim, h, w = 2, 128, 3, 4
    raw = torch.randn(1, h * w, heads * head_dim, generator=torch.Generator().manual_seed(0))
    at_zero = rope_apply(raw, _wan_freqs(head_dim, 0, h, w), heads)                     # what the cache holds
    direct = rope_apply(raw, _wan_freqs(head_dim, position, h, w), heads)                # encoded at t = position
    moved = rerotate_temporal(at_zero[:, None], torch.tensor([[position]]), heads)[:, 0]
    assert temporal_pairs(head_dim) == 22
    assert float((moved - direct).abs().max()) < 1e-5
    # spatial channels untouched, temporal channels moved
    x = moved.reshape(1, h * w, heads, head_dim)
    y = at_zero.reshape(1, h * w, heads, head_dim)
    assert torch.equal(x[..., 44:], y[..., 44:])
    assert not torch.allclose(x[..., :44], y[..., :44])


def test_positions_and_buckets():
    ids = torch.tensor([[0, 8, 16, 24, 0], [0, 40, 48, 0, 0]])
    valid = torch.tensor([[True, True, True, True, False], [True, True, True, False, False]])
    pos = recency_positions(ids, valid)
    assert pos.tolist() == [[-4, -3, -2, -1, 0], [-3, -2, -1, 0, 0]]
    current = torch.tensor([32, 56])
    b = time_buckets(ids, current, valid, buckets=6, unit=8.0)
    # elapsed / 8 = 4, 3, 2, 1 -> floor(log2(1 + u)) = 2, 2, 1, 1;  7, 2, 1 -> 3, 1, 1
    assert b.tolist() == [[2, 2, 1, 1, 0], [3, 1, 1, 0, 0]]


# ----------------------------------------------------------------------------- tiny model
def _batch(cfg, batch=3, seed=0, length=40):
    g = torch.Generator().manual_seed(seed)
    episodes = torch.randn(batch, length, 6, 16, generator=g)
    currents = [12 + 9 * b for b in range(batch)]
    selections = [select_history(range(c + 1), c, POLICY) for c in currents]
    meta = collate_selection(selections)
    k = meta["frame_ids"].shape[1]
    hist_latent = torch.zeros(batch, k, 6, 16)
    for b, s in enumerate(selections):
        for j, i in enumerate(s.ids):
            hist_latent[b, j] = episodes[b, i]
    return {"latent": torch.stack([episodes[b, c] for b, c in enumerate(currents)]),
            "context": torch.randn(batch, 24, generator=g), "text": torch.zeros(batch, 1, 1),
            "actions": torch.randn(batch, 8, 5, generator=g), "action_valid": torch.ones(batch, 8, dtype=torch.bool),
            "hist_latent": hist_latent, "hist_proprio": torch.zeros(batch, k, 1), **meta}


def _model():
    torch.manual_seed(0)
    return MemoryV2Model(TinyBackbone(), MemoryV2Config(**REPLAY)).float()


def _open_gates(model, value=0.5):
    with torch.no_grad():
        model.memory.replay.gate.net[2].bias.fill_(value)       # g = 1 + net - 1 = value everywhere


def test_zero_start_is_exactly_the_base_model():
    model = _model()
    batch = _batch(model.cfg)
    x = torch.randn(3, 8, 5)
    t = torch.full((3,), 700.0)
    for grad in (False, True):
        with torch.set_grad_enabled(grad):
            c = model.conditions(batch)
            off = model.velocity(x, t, c, "off")
            assert torch.equal(model.velocity(x, t, c, "on"), off)
            assert torch.equal(model.velocity(x, t, c, "null"), off)
    assert model.memory.tokenizer is None and len(model.memory.injectors) == 0
    names = set(model.memory_state_dict())
    assert names and all(n.startswith("replay.") for n in names)


def test_gate_gets_the_first_gradient_then_the_embeddings():
    model = _model()
    batch = _batch(model.cfg)
    x, t = torch.randn(3, 8, 5), torch.full((3,), 900.0)
    model.velocity(x, t, model.conditions(batch), "on").square().mean().backward()
    replay = model.memory.replay
    assert float(replay.gate.net[2].weight.grad.abs().sum()) > 0          # dL/dg = L(with) - L(without) != 0
    assert float(replay.role_embedding.grad.abs().sum()) == 0             # times g = 0
    model.zero_grad()
    _open_gates(model)
    model.velocity(x, t, model.conditions(batch), "on").square().mean().backward()
    for p in (replay.role_embedding, replay.time_embedding, replay.key_up, replay.value_up):
        assert float(p.grad.abs().sum()) > 0
    assert all(p.grad is None or float(p.grad.abs().sum()) == 0 for p in model.backbone.parameters())


def test_open_gate_uses_history_and_null_drop_stay_exact():
    model = _model()
    _open_gates(model)
    batch = _batch(model.cfg)
    x, t = torch.randn(3, 8, 5), torch.full((3,), 500.0)
    with torch.no_grad():
        c = model.conditions(batch)
        on, off, null = (model.velocity(x, t, c, m) for m in ("on", "null", "off"))
        assert not torch.allclose(on, off)
        assert torch.equal(null, off)
        drop = torch.tensor([True, False, True])
        dropped = model.velocity(x, t, model.conditions(batch, drop=drop), "on")
        assert torch.equal(dropped[drop], off[drop]) and torch.allclose(dropped[~drop], on[~drop])
        swapped = dict(batch)
        for key in ("hist_latent", "hist_proprio", "frame_ids", "roles", "history_valid"):
            swapped[key] = batch[key].roll(1, 0)
        assert not torch.allclose(model.velocity(x, t, model.conditions(swapped), "on"), on)


def test_history_order_in_the_tensor_does_not_matter():
    """Permuting the history slots (keys of one softmax, positions follow the frame ids) changes nothing."""
    model = _model()
    _open_gates(model)
    batch = _batch(model.cfg)
    x, t = torch.randn(3, 8, 5), torch.full((3,), 500.0)
    perm = torch.tensor([2, 0, 1, 4, 3, 5])[:batch["frame_ids"].shape[1]]
    shuffled = dict(batch)
    for key in ("hist_latent", "hist_proprio", "frame_ids", "roles", "history_valid"):
        shuffled[key] = batch[key][:, perm]
    with torch.no_grad():
        a = model.velocity(x, t, model.conditions(batch), "on")
        b = model.velocity(x, t, model.conditions(shuffled), "on")
    assert torch.allclose(a, b, atol=1e-5)


def test_config_roundtrip_and_old_configs_unchanged():
    inject = V2Config()
    assert "read" not in inject.to_dict()["memory"] and "replay_rank" not in inject.to_dict()["memory"]
    replay = V2Config.from_dict({"memory": {"read": "kv_replay", "replay_layers": [3, 9]}})
    d = replay.to_dict()
    assert d["memory"]["read"] == "kv_replay" and V2Config.from_dict(json.loads(json.dumps(d))) == replay
    assert replay.memory.replayed_layers == (3, 9) and inject.memory.replayed_layers == ()
    assert V2Config.from_dict({"memory": {"read": "kv_replay"}}).memory.replayed_layers == tuple(range(30))
    with pytest.raises(ValueError):
        MemoryV2Config(read="cross")
    with pytest.raises(ValueError):
        MemoryV2Config(read="kv_replay", replay_layers=(5, 3))


def test_history_sensitivity_and_gate_profile_on_replay():
    from fastwam.memory_v2.metrics import gate_profile, history_sensitivity
    model = _model()
    _open_gates(model)
    batch = _batch(model.cfg)
    sens = history_sensitivity(model, batch, taus=(0.5, 1.0))
    assert sens["null"][0] > 0 and sens["swap"][0] > 0
    prof = gate_profile(model, taus=(0.0, 1.0))
    assert set(prof) == {"tau"} | {str(i) for i in model.memory.replay.layers}
    assert prof["0"][0] == pytest.approx(0.5)


def test_trainer_runs_kv_replay_with_pairs_probes_and_eval(tmp_path):
    """Integration on the tiny backend: zero-start parity, updates, pairs, probes (gate profile), evaluation."""
    from fastwam.memory_v2.tests.test_train_v2 import POLICY as TRAIN_POLICY, TinyBackend, _cfg
    from fastwam.memory_v2.train_v2 import PairsConfig, Trainer

    class ReplayBackend(TinyBackend):
        def __init__(self):
            super().__init__()
            torch.manual_seed(0)
            self.cfg_memory = MemoryV2Config(**REPLAY)
            self.model = MemoryV2Model(TinyBackbone(), self.cfg_memory).float()

        def batch(self, rows):
            selections, latent, context, actions, valid = [], [], [], [], []
            for row in rows:
                e, a = row["episode_id"], row["anchor"]
                selections.append(select_history(range(a + 1), a, TRAIN_POLICY))
                index = torch.clamp(torch.arange(a, a + 8), max=self.length - 1)
                actions.append(self.actions[e, index])
                valid.append(torch.arange(a, a + 8) < self.length)
                latent.append(self.latent[e, a])
                context.append(self.context[e])
            meta = collate_selection(selections)
            k = meta["frame_ids"].shape[1]
            hist = torch.zeros(len(rows), k, 6, 16)
            for b, (row, s) in enumerate(zip(rows, selections)):
                for j, i in enumerate(s.ids):
                    hist[b, j] = self.latent[row["episode_id"], i]
            return {"latent": torch.stack(latent), "context": torch.stack(context), "actions": torch.stack(actions),
                    "action_valid": torch.stack(valid), "text": torch.zeros(len(rows), 1, 1), "hist_latent": hist,
                    "hist_proprio": torch.zeros(len(rows), k, 1), **meta}

    pairs = [{"task": "t", "query": {"episode_id": 0, "anchor": 20}, "donor": {"episode_id": 1, "anchor": 24},
              "present_rms": 0.01, "delta_norm": 3.0, "visual_distance": 0.0}]
    path = tmp_path / "pairs.json"
    path.write_text(json.dumps({"train": pairs, "val": pairs}))
    cfg = _cfg(tmp_path)
    cfg.v2 = V2Config.from_dict({"memory": REPLAY, "history": TRAIN_POLICY.__dict__, "guidance": {"steps": 3}})
    cfg.pairs = PairsConfig(file=str(path), weight=1.0, per_update=1)
    backend = ReplayBackend()
    trainer = Trainer(backend, cfg, tmp_path / "run", log=lambda m: None)
    result = trainer.run()
    assert result.get("complete")
    parity = json.loads((tmp_path / "run" / "INIT_PARITY.json").read_text())
    assert parity["exact"]
    probes = [json.loads(line) for line in (tmp_path / "run" / "probes.jsonl").read_text().splitlines()]
    assert probes and set(probes[-1]["gate"]) >= {"tau", "0", "5"}
    gate = probes[-1]["gate"]["0"]
    assert any(abs(v) > 0 for v in gate)                       # the gates moved away from zero
    assert (tmp_path / "run" / "eval").exists()


def test_cross_decision_cache_matches_fresh_prefill_and_prefills_each_frame_once():
    """Deployment (11-06): with model.replay_cache set, every history frame is prefilled once per episode; the replay
    state equals the uncached one at every decision (re-rotation to -rank happens after the cache)."""
    model = _model().eval()
    _open_gates(model)
    g = torch.Generator().manual_seed(3)
    episode = torch.randn(80, 6, 16, generator=g)
    context = torch.randn(1, 24, generator=g)
    policy = HistoryPolicyConfig(mode="periodic", period=8, recent_frames=2, max_frames=6)
    calls = []
    model.backbone.encoder.register_forward_hook(lambda module, args, out: calls.append(args[0].shape[0]))
    cache, seen = {}, set()
    x, t = torch.randn(1, 8, 5, generator=g), torch.full((1,), 600.0)
    for current in range(8, 80, 8):
        s = select_history(range(current + 1), current, policy)
        meta = collate_selection([s])
        k = meta["frame_ids"].shape[1]
        hist = torch.stack([episode[i] for i in s.ids])[None]
        batch = {"latent": episode[current][None], "context": context, "text": torch.zeros(1, 1, 1),
                 "actions": torch.zeros(1, 8, 5), "action_valid": torch.ones(1, 8, dtype=torch.bool),
                 "hist_latent": hist, "hist_proprio": torch.zeros(1, k, 1), **meta}
        with torch.no_grad():
            fresh = model.conditions(batch)
            model.replay_cache = cache
            before = len(calls)
            cached = model.conditions(batch)
            model.replay_cache = None
            new_frames = sum(calls[before:]) - 1                     # minus the current frame's own encode
            assert new_frames == len([i for i in s.ids if i not in seen])
            seen = set(cache)
            for a, b in zip(fresh.replay.keys + fresh.replay.values, cached.replay.keys + cached.replay.values):
                assert torch.allclose(a, b, atol=1e-6, rtol=1e-5)
            assert torch.allclose(model.velocity(x, t, fresh, "on"), model.velocity(x, t, cached, "on"), atol=1e-6)
    assert set(cache) - {-1} == set(range(0, 72, 8)) and len(select_history(range(73), 72, policy).ids) == 6
    with pytest.raises(ValueError):
        model.replay_cache = {}
        try:
            model.conditions(_batch(model.cfg))                          # batch 3: the cache serves one episode
        finally:
            model.replay_cache = None
