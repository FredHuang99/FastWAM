"""fullft on a tiny REAL FastWAM MoT (Wan video DiT + ActionDiT, random weights, CPU): the joint forward equals the
released MoT core, the gated history start is exact, training and inference read the current frame identically,
the history re-rotation equals replay.py's, LoRA / clk / prop start exactly, the event detector is invariant to
pauses and slow replay, and the history selection never looks ahead."""
import random

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")
np = pytest.importorskip("numpy")

from torch import nn  # noqa: E402

from fastwam.fullft.events import EventDetector, EventRule, detect, event_frames  # noqa: E402
from fastwam.fullft.history import HistoryRule, select  # noqa: E402
from fastwam.fullft.data import action_window, latent_valid  # noqa: E402
from fastwam.fullft.model import FullModel, rerotate  # noqa: E402

LAYERS, HEADS, HEAD_DIM, VIDEO, ACTION, TEXT = 2, 4, 24, 96, 32, 16


def _model(variant="ar", event_slots=0, seed=0):
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
    m = FullModel(mot, nn.Linear(14, TEXT), variant=variant, event_slots=event_slots)
    with torch.no_grad():                         # lift zero-initialised output layers so every path does something
        for name, p in m.named_parameters():
            if p.abs().sum() == 0 and not name.startswith(("hist_gate", "extra", "ledger")):
                p.normal_(0, 0.02)
    return m.float()


def _batch(b=2, k=3, seed=0, length=4):
    g = torch.Generator().manual_seed(seed)
    valid = torch.tensor([[True, True, True], [True, False, False]])[:b, :k]
    return {"video_latent": torch.randn(b, 48, 3, 8, 6, generator=g), "video_valid": torch.ones(b, 3, dtype=torch.bool),
            "text": torch.randn(b, 5, TEXT, generator=g), "proprio": torch.randn(b, 14, generator=g),
            "actions": torch.randn(b, 32, 14, generator=g), "action_valid": torch.ones(b, 32, dtype=torch.bool),
            "anchor": torch.tensor([40, 7])[:b],
            "hist_latent": torch.randn(b, k, 48, 1, 8, 6, generator=g), "hist_proprio": torch.randn(b, k, 14, generator=g),
            "hist_valid": valid, "hist_pos": torch.tensor([[-3.0, -2.0, -1.0], [-1.0, 0.0, 0.0]])[:b, :k]}


def _noise(batch, seed=1):
    g = torch.Generator().manual_seed(seed)
    b = batch["actions"].shape[0]
    return {"video": torch.randn(batch["video_latent"].shape, generator=g),
            "action": torch.randn(batch["actions"].shape, generator=g),
            "t_video": torch.rand(b, generator=g) * 1000, "t_action": torch.rand(b, generator=g) * 1000}


def _released_core(m, batch, noise):
    """The same inputs through the released MoT.forward_joint_core with FastWAM's joint mask."""
    clean = batch["video_latent"]
    latents = m.video_scheduler.add_noise(clean, noise["video"], noise["t_video"])
    latents[:, :, 0:1] = clean[:, :, 0:1]
    noisy = m.action_scheduler.add_noise(batch["actions"], noise["action"], noise["t_action"])
    context, cmask = m.context(batch["text"], batch["proprio"])
    xv, t_v, mv, cv, cmv, fv, f, h, w, tpf = m.video.prepare(x=latents, timestep=noise["t_video"], context=context,
                                                             context_mask=cmask, fuse_vae_embedding_in_latents=True)
    xa, _, ma, ca, cma, fa = m.action.prepare(action_tokens=noisy, timestep=noise["t_action"], context=context,
                                              context_mask=cmask)
    total = xv.shape[1] + xa.shape[1]
    mask = torch.zeros((total, total), dtype=torch.bool)
    mask[:xv.shape[1], :xv.shape[1]] = m.video.build_video_to_video_mask(xv.shape[1], tpf, xv.device)
    mask[xv.shape[1]:, xv.shape[1]:] = True
    mask[xv.shape[1]:, :tpf] = True
    ov, oa = m.mot.forward_joint_core(video_tokens=xv, action_tokens=xa, video_freqs=fv, action_freqs=fa,
                                      video_t_mod=mv, action_t_mod=ma, video_context=cv, video_context_mask=cmv,
                                      action_context=ca, action_context_mask=cma, attention_mask=mask)
    return m.video.post(ov, t_v, f, h, w), m.action.post(oa), mask


def test_joint_forward_is_the_released_core_and_mask():
    m = _model("none")
    batch = _batch()
    noise = _noise(batch)
    with torch.no_grad():
        ref_v, ref_a, ref_mask = _released_core(m, batch, noise)
        ours = FullModel.base_mask(ref_mask.shape[0] - 32, 32, (8 // 2) * (6 // 2), "cpu")
        assert torch.equal(ours, ref_mask)
        # our loss path, recomputing predictions the same way
        captured = {}
        post = m.action.post

        def grab(x):
            captured["a"] = post(x)
            return captured["a"]
        m.action.post = grab
        m.loss(batch, noise, history=None)
        m.action.post = post
    assert torch.allclose(captured["a"], ref_a, atol=1e-6, rtol=1e-5)


def test_gate_zero_start_is_exact_and_gate_gets_gradient():
    m = _model("ar")
    batch = _batch()
    noise = _noise(batch)
    with torch.no_grad():
        h = m.history(batch)
        assert h is not None and h.keys[0].shape[1] == 3 * 12
        v1, a1 = m.loss(batch, noise, h)
        v0, a0 = m.loss(batch, noise, None)
    assert torch.equal(v1, v0) and torch.equal(a1, a0)
    v, a = m.loss(batch, noise)
    (v.mean() + a.mean()).backward()
    assert float(m.hist_gate.grad.abs().sum()) > 0
    with torch.no_grad():
        m.hist_gate.fill_(0.5)
        v2, a2 = m.loss(batch, noise)
    assert not torch.allclose(a2, a0)


def test_checkpointed_layers_match():
    m = _model("ar")
    batch = _batch()
    noise = _noise(batch)
    with torch.no_grad():
        m.hist_gate.fill_(0.3)
    v, a = m.loss(batch, noise)
    (v.mean() + a.mean()).backward()
    g1 = m.mot.mixtures["action"].blocks[0].self_attn.q.weight.grad.clone()
    m.zero_grad()
    m.checkpoint_layers = True
    v2, a2 = m.loss(batch, noise)
    (v2.mean() + a2.mean()).backward()
    assert torch.allclose(a, a2) and torch.allclose(g1, m.mot.mixtures["action"].blocks[0].self_attn.q.weight.grad,
                                                    atol=1e-6, rtol=1e-4)


def test_inference_reads_the_current_frame_as_training_does():
    """velocity() with the prefilled current frame (+ history) == the action branch of the joint training forward,
    whatever the future frames are (the action never sees them)."""
    m = _model("ar")
    batch = _batch()
    noise = _noise(batch)
    with torch.no_grad():
        m.hist_gate.fill_(0.4)
        captured = {}
        post = m.action.post

        def grab(x):
            captured["a"] = post(x)
            return captured["a"]
        m.action.post = grab
        m.loss(batch, noise)
        m.action.post = post
        h = m.history(batch)
        b2 = dict(batch, latent=batch["video_latent"][:, :, 0:1])
        keys, values, shared = m.prefill_current(b2, h)
        noisy = m.action_scheduler.add_noise(batch["actions"], noise["action"], noise["t_action"])
        v = m.velocity(noisy, noise["t_action"], (keys, values), shared, h)
        other = dict(batch, video_latent=batch["video_latent"].clone())
        other["video_latent"][:, :, 1:] = torch.randn_like(other["video_latent"][:, :, 1:])
        m.action.post = grab
        m.loss(other, noise)
        m.action.post = post
    assert torch.allclose(v, captured["a"], atol=1e-5, rtol=1e-4)
    out = m.sample(b2, torch.randn(2, 32, 14), steps=3)
    assert out.shape == (2, 32, 14) and torch.isfinite(out).all()


def test_rerotate_equals_replay():
    from fastwam.memory_v2.replay import rerotate_temporal
    keys = torch.randn(2, 3, 5, HEADS * HEAD_DIM)
    pos = torch.tensor([[-3, -2, -1], [-1, 0, 0]])
    assert torch.allclose(rerotate(keys, pos.float(), HEADS), rerotate_temporal(keys, pos, HEADS), atol=1e-6)


def test_lora_clk_prop_start_exact():
    batch = _batch()
    noise = _noise(batch)
    m = _model("none")
    with torch.no_grad():
        v0, a0 = m.loss(batch, noise, None)
    m.set_trainable("lora", 4)
    with torch.no_grad():
        v1, a1 = m.loss(batch, noise, None)
    assert torch.allclose(a0, a1, atol=1e-6) and torch.allclose(v0, v1, atol=1e-6)
    trainable = {n for n, p in m.named_parameters() if p.requires_grad}
    assert any(".down" in n for n in trainable) and not any(n.startswith("mot.mixtures.video") and ".base." in n
                                                              for n in trainable)
    for variant, extra in (("clk", {}), ("prop", {"event_proprio": torch.randn(2, 4, 14),
                                                  "event_valid": torch.tensor([[1, 1, 0, 0], [0, 0, 0, 0]]).bool()})):
        m0 = _model("none")
        mv = _model(variant, event_slots=4)
        missing, unexpected = mv.load_state_dict(m0.state_dict(), strict=False)
        assert not unexpected and all(k.startswith("extra.") for k in missing)
        b = dict(batch, **extra)
        with torch.no_grad():
            assert torch.equal(m0.loss(b, noise, None)[1], mv.loss(b, noise, None)[1])
        v, a = mv.loss(b, noise, None)
        a.mean().backward()
        assert float(mv.extra.weight.grad.abs().sum()) > 0


def test_history_select_rules():
    ar = HistoryRule("ar")
    ids, pos = select(ar, 100)
    assert ids == [0, 68, 84] and pos == [-3.0, -2.0, -1.0]
    assert select(ar, 0) == ([], [])
    ids, _ = select(ar, 20)
    assert ids == [0, 4]
    tw = HistoryRule("tw", index="time")
    ids, pos = select(tw, 200)
    assert ids[0] == 0 and all(i < 200 for i in ids) and len(ids) <= tw.max_frames
    assert pos[-1] == -(200 - ids[-1]) / 16.0
    ev = HistoryRule("event", event_max=3)
    ids, pos = select(ev, 300, [10, 50, 120, 200, 299, 300, 400])
    assert ids == [0, 120, 200, 299] and pos == [-4.0, -3.0, -2.0, -1.0]
    aug = HistoryRule("event", drop_event_p=0.5, spurious_event_p=1.0)
    for s in range(20):
        ids, _ = select(aug, 300, [10, 50, 120], random.Random(s))
        assert all(i < 300 for i in ids)
    assert select(HistoryRule("clk"), 50) == ([], [])


def _trajectory():
    """A synthetic two-arm episode: left arm presses twice (down 3 cm, up 3 cm), right gripper closes and opens."""
    z = [0.20] * 10 + list(np.linspace(0.20, 0.17, 6)) + list(np.linspace(0.17, 0.20, 6)) + [0.20] * 8 \
        + list(np.linspace(0.20, 0.17, 6)) + list(np.linspace(0.17, 0.20, 6)) + [0.20] * 10
    n = len(z)
    pos = np.zeros((n, 2, 3))
    pos[:, 0, 2] = z
    pos[:, 0, 0] = np.linspace(0, 0.2, n)          # moving sideways so the debounce path grows
    pos[:, 1, 2] = 0.25
    pos[:, 1, 1] = np.linspace(0, 0.3, n)
    grip = np.ones((n, 2))
    grip[20:35, 1] = 0.0
    return grip, pos


def test_events_stream_equals_batch_and_are_tempo_invariant():
    grip, pos = _trajectory()
    events = detect(grip, pos)
    kinds = [(e["arm"], e["kind"]) for e in events]
    assert kinds.count((0, "bottom")) == 2 and (1, "close") in kinds and (1, "open") in kinds
    det = EventDetector(EventRule())
    stream = [e for t in range(len(grip)) for e in det.step(t, grip[t], pos[t])]
    assert [e["frame"] for e in stream] == sorted(e["frame"] for e in events) or \
        sorted((e["frame"], e["arm"]) for e in stream) == [(e["frame"], e["arm"]) for e in events]
    # a pause of 30 frames at frame 25: same events, frames after the pause shifted by 30
    k = 25
    g2 = np.concatenate([grip[:k], np.repeat(grip[k:k + 1], 30, 0), grip[k:]])
    p2 = np.concatenate([pos[:k], np.repeat(pos[k:k + 1], 30, 0), pos[k:]])
    e2 = detect(g2, p2)
    shift = [e["frame"] - (30 if e["frame"] >= k + 30 else 0) for e in e2]
    assert [(f, e["arm"], e["kind"]) for f, e in zip(shift, e2)] == [(e["frame"], e["arm"], e["kind"]) for e in events]
    # slowed replay x2 (every state repeated): same event kinds in the same order, frames ~ doubled
    g3, p3 = np.repeat(grip, 2, 0), np.repeat(pos, 2, 0)
    e3 = detect(g3, p3)
    assert [(e["arm"], e["kind"]) for e in e3] == [(e["arm"], e["kind"]) for e in events]
    assert all(abs(a["frame"] - 2 * b["frame"]) <= 1 for a, b in zip(e3, events))
    # known-at semantics: an event confirmed after t is not shown at t
    bottom = next(e for e in events if e["kind"] == "bottom")
    assert bottom["confirmed"] > bottom["frame"]
    assert bottom["frame"] not in event_frames(events, before=bottom["confirmed"], known_by=bottom["confirmed"] - 1)
    assert bottom["frame"] in event_frames(events, before=bottom["confirmed"] + 1, known_by=bottom["confirmed"])


def test_action_window_and_latent_valid():
    a = torch.arange(40).float()[:, None].repeat(1, 14)
    chunk, valid = action_window(a, 30)
    assert chunk.shape == (32, 14) and int(valid.sum()) == 10 and float(chunk[-1, 0]) == 39
    assert latent_valid(torch.tensor([1, 1, 1, 1, 1, 0, 0, 0, 0]).bool(), "valid").tolist() == [True, True, False]
    assert latent_valid(torch.tensor([0, 0, 0, 0, 0, 1, 1, 1, 1]).bool(), "pad").tolist() == [True, True, False]


def test_dense_samples_and_config(tmp_path):
    import json as _json
    from fastwam.fullft.config import load
    from fastwam.fullft.data import DenseEpisodes, Samples, collate, train_items, val_items, video_polarity
    root = tmp_path / "dense"
    records = []
    for task in ("put_back_block", "swap_blocks"):
        for k, split in enumerate(("train", "train", "val")):
            eid = f"{task}/episode_{k:07d}"
            n = 50 + 10 * k
            folder = root / "cache" / eid.replace("/", "_")
            folder.mkdir(parents=True)
            vv = torch.ones(n, 9, dtype=torch.bool)
            vv[-5:, 5:] = False
            torch.save({"latent": torch.randn(n, 48, 1, 4, 4), "video_latent": torch.randn(n, 48, 3, 4, 4),
                        "video_valid": vv, "text": torch.randn(7, TEXT), "text_valid": torch.ones(7, dtype=torch.bool),
                        "proprio": torch.randn(n, 14), "actions": torch.randn(n, 14)}, folder / "encodings.pt")
            (folder / "COMPLETE.json").write_text("{}")
            records.append({"episode_id": eid, "task": task, "split": split, "length": n})
    (root / "RECORDS.json").write_text(_json.dumps(records))
    eps = DenseEpisodes([str(root)], ["put_back_block", "swap_blocks"])
    assert video_polarity(eps) == "valid"
    items = train_items(eps)
    assert len(items) == 2 * (50 + 60)
    events = {r["episode_id"]: [{"frame": 20, "confirmed": 25}, {"frame": 40, "confirmed": 41}] for r in eps.records}
    for variant in ("none", "ar", "event", "tw", "clk", "prop"):
        rule = HistoryRule(variant, index="time" if variant == "tw" else "rank")
        ds = Samples(eps, items, rule, events, "valid", augment=True, seed=3)
        batch = collate([ds[i] for i in (0, 45, 100)])
        assert batch["video_latent"].shape == (3, 48, 3, 4, 4) and batch["actions"].shape == (3, 32, 14)
        if rule.max_frames:
            assert batch["hist_valid"].shape == (3, rule.max_frames)
            ids = batch["hist_ids"]
            assert bool(((ids < batch["anchor"][:, None]) | ~batch["hist_valid"]).all())   # never the future
        if variant == "event":
            row = ds[items.index(("put_back_block/episode_0000000", 30))]
            assert row["hist_ids"][row["hist_valid"]].tolist() == [0, 20]                   # 40 not yet, 20 known at 25
        if variant == "prop":
            assert batch["event_proprio"].shape == (3, rule.event_max, 14)
    assert len(val_items(eps, 8)) == 16
    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text("name: t\nhistory: {variant: tw}\noptim: {betas: [0.9, 0.95]}\n")
    cfg = load(str(cfg_path), ["schedule.micro_batch=4", "data.tasks=[put_back_block]"])
    assert cfg.rule.index == "time" and cfg.optim.betas == (0.9, 0.95) and cfg.schedule.micro_batch == 4
    assert cfg.data.tasks == ["put_back_block"]


def test_online_decision_equals_offline_sampling():
    """The closed-loop assembly (per-frame K/V cache, selection, re-rotation, eviction) gives exactly the chunk that
    FullModel.sample gives on the training-style batch of the same inputs."""
    from fastwam.fullft.online import FrameCache, decide_encoded
    m = _model("ar")
    with torch.no_grad():
        m.hist_gate.fill_(0.5)
    g = torch.Generator().manual_seed(5)
    encoded = {i: (torch.randn(48, 1, 8, 6, generator=g), torch.randn(14, generator=g)) for i in range(60)}
    text = torch.randn(1, 5, TEXT, generator=g)
    rule = HistoryRule("ar")
    cache = FrameCache()
    for current in (40, 48, 56):
        noise = torch.randn(1, 32, 14, generator=g)
        out = decide_encoded(m, rule, cache, encoded, current, text, noise, steps=3)
        ids, pos = select(rule, current)
        batch = {"latent": encoded[current][0][None], "text": text, "proprio": encoded[current][1][None],
                 "anchor": torch.tensor([current]),
                 "hist_latent": torch.stack([encoded[i][0] for i in ids])[None],
                 "hist_proprio": torch.stack([encoded[i][1] for i in ids])[None],
                 "hist_valid": torch.ones(1, len(ids), dtype=torch.bool), "hist_pos": torch.tensor([pos])}
        ref = m.sample(batch, noise, steps=3)
        assert out["ids"] == ids and torch.allclose(out["normalised"], ref[0], atol=1e-6)
        assert set(cache.kv) <= {0} | set(range(current - 32, current + 1))
