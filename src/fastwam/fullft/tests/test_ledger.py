"""plan v12 C.2 / Opus checklist 11: the arprop ledger (anchor + recent frames + one small token per proprioceptive
event, written `lag` frames after confirmation, the last `event_max` kept) and the arev frames. Checks: frame selection
equals ar (arprop) / ar + known events (arev); lag and cap of the ledger; a zero ledger encoder gives EXACTLY the ar
model (and the ledger gets a gradient); the dense dataset builds the ledger as the online session does; the online
assembly (decide_encoded) equals offline sampling with the ledger; the session's streaming detection over observed
frames equals the batch detector used for the demos."""
import types

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")
np = pytest.importorskip("numpy")

from fastwam.fullft.data import check_ledger_slots, ledger_tensor  # noqa: E402
from fastwam.fullft.events import detect  # noqa: E402
from fastwam.fullft.history import HistoryRule, ledger_dim, ledger_entries, select  # noqa: E402
from fastwam.fullft.tests.test_fullft import TEXT, _batch, _model, _noise  # noqa: E402

EVENTS = [{"frame": 10, "arm": 0, "kind": "close", "confirmed": 10},
          {"frame": 20, "arm": 1, "kind": "bottom", "confirmed": 24},
          {"frame": 30, "arm": 0, "kind": "open", "confirmed": 30},
          {"frame": 40, "arm": 1, "kind": "top", "confirmed": 45}]


def test_rules_and_selection():
    ar, lp = HistoryRule("ar"), HistoryRule("arprop", event_max=4, lag=2)
    assert lp.max_frames == ar.max_frames == 3 and lp.event_slots == 4
    for t in (0, 5, 20, 50, 300):
        assert select(lp, t, [3, 9]) == select(ar, t)
    ev = HistoryRule("arev", event_max=2)
    assert ev.max_frames == 5 and ev.event_slots == 0
    ids, pos = select(ev, 50, [10, 20, 30])
    assert ids == [0, 18, 20, 30, 34] and pos == [-5.0, -4.0, -3.0, -2.0, -1.0]
    assert ledger_dim(32) == 53


def test_ledger_lag_cap_and_features():
    rule = HistoryRule("arprop", event_max=3, lag=4)
    assert [e["frame"] for e in ledger_entries(rule, 27, EVENTS)] == [10]           # 20 written at 24 + 4 = 28
    assert [e["frame"] for e in ledger_entries(rule, 28, EVENTS)] == [10, 20]
    assert [e["frame"] for e in ledger_entries(rule, 50, EVENTS)] == [20, 30, 40]    # cap: the last 3
    assert [e["frame"] for e in ledger_entries(rule, 48, EVENTS)] == [10, 20, 30]    # 40 written at 49
    proprio = {f: torch.full((14,), float(f)) for f in (10, 20, 30, 40)}
    feat, valid = ledger_tensor(rule, ledger_entries(rule, 50, EVENTS), lambda f: proprio[f])
    assert feat.shape == (3, ledger_dim(3)) and valid.tolist() == [True, True, True]
    assert feat[0, 0] == 20 and feat[2, 0] == 40                                    # ascending slots
    assert feat[0, 14 + 2] == 1 and feat[1, 14 + 1] == 1 and feat[2, 14 + 3] == 1    # bottom, open, top
    assert feat[0, 18 + 1] == 1 and feat[1, 18 + 0] == 1                              # arms
    assert feat[2, 20 + 0] == 1 and feat[0, 20 + 2] == 1                              # rank 0 = most recent
    feat, valid = ledger_tensor(rule, ledger_entries(rule, 27, EVENTS), lambda f: proprio[f])
    assert valid.tolist() == [True, False, False] and float(feat[1:].abs().sum()) == 0


def _ledger_batch(b=2, slots=4, seed=0):
    batch = _batch(b)
    g = torch.Generator().manual_seed(seed)
    batch["text"] = torch.cat((torch.randn(b, 2, TEXT, generator=g), torch.zeros(b, slots, TEXT)), 1)
    batch["ledger"] = torch.randn(b, slots, ledger_dim(slots), generator=g)
    batch["ledger_valid"] = torch.tensor([[True, True, False, False], [False, False, False, False]])[:b, :slots]
    return batch


def test_zero_ledger_is_exactly_ar_and_ledger_learns():
    batch = _ledger_batch()
    noise = _noise(batch)
    m0, ml = _model("ar"), _model("arprop", event_slots=4)
    missing, unexpected = ml.load_state_dict(m0.state_dict(), strict=False)
    assert not unexpected and sorted(missing) == ["ledger.bias", "ledger.weight"]
    with torch.no_grad():
        m0.hist_gate.fill_(0.3)
        ml.hist_gate.fill_(0.3)
        v0, a0 = m0.loss(batch, noise)
        v1, a1 = ml.loss(batch, noise)
        assert torch.equal(v0, v1) and torch.equal(a0, a1)
        s0 = m0.sample(dict(batch, latent=batch["video_latent"][:, :, 0:1]), noise["action"], steps=3)
        s1 = ml.sample(dict(batch, latent=batch["video_latent"][:, :, 0:1]), noise["action"], steps=3)
        assert torch.equal(s0, s1)
    v, a = ml.loss(batch, noise)
    (a.mean() + v.mean()).backward()
    assert float(ml.ledger.weight.grad.abs().sum()) > 0
    with torch.no_grad():
        ml.ledger.weight.normal_(0, 0.5)
        _, a2 = ml.loss(batch, noise)
        assert not torch.allclose(a2[0], a0[0])                       # sample 0 has two ledger entries
        assert torch.allclose(a2[1], a0[1], atol=1e-6)                # sample 1: empty ledger, zero bias -> unchanged
    with pytest.raises(ValueError):
        check_ledger_slots(torch.randn(6, TEXT), 4)
    check_ledger_slots(batch["text"][0], 4)


def test_dense_samples_build_the_ledger(tmp_path):
    import json as _json
    from fastwam.fullft.data import DenseEpisodes, Samples, collate, train_items
    root = tmp_path / "dense"
    records = []
    for k in range(2):
        eid = f"put_back_block/episode_{k:07d}"
        n = 60
        folder = root / "cache" / eid.replace("/", "_")
        folder.mkdir(parents=True)
        text = torch.cat((torch.randn(3, TEXT), torch.zeros(4, TEXT)))
        torch.save({"latent": torch.randn(n, 48, 1, 4, 4), "video_latent": torch.randn(n, 48, 3, 4, 4),
                    "video_valid": torch.ones(n, 9, dtype=torch.bool), "text": text,
                    "text_valid": torch.tensor([True] * 3 + [False] * 4),
                    "proprio": torch.arange(n, dtype=torch.float32)[:, None].repeat(1, 14),
                    "actions": torch.randn(n, 14)}, folder / "encodings.pt")
        (folder / "COMPLETE.json").write_text("{}")
        records.append({"episode_id": eid, "task": "put_back_block", "split": "train", "length": n})
    (root / "RECORDS.json").write_text(_json.dumps(records))
    eps = DenseEpisodes([str(root)], ["put_back_block"])
    items = train_items(eps)
    events = {r["episode_id"]: EVENTS for r in eps.records}
    rule = HistoryRule("arprop", event_max=4, lag=4)
    ds = Samples(eps, items, rule, events, "valid")
    for a in (5, 27, 28, 50):
        row = ds[items.index(("put_back_block/episode_0000000", a))]
        want = ledger_entries(rule, a, EVENTS)
        feat, valid = ledger_tensor(rule, want, lambda f: torch.full((14,), float(f)))
        assert torch.equal(row["ledger"], feat) and torch.equal(row["ledger_valid"], valid)
        ids = row["hist_ids"][row["hist_valid"]].tolist()
        assert ids == select(HistoryRule("ar"), a)[0]
    batch = collate([ds[i] for i in (0, 30, 59)])
    assert batch["ledger"].shape == (3, 4, ledger_dim(4))
    ev = HistoryRule("arev", event_max=2, lag=4)
    row = Samples(eps, items, ev, events, "valid")[items.index(("put_back_block/episode_0000000", 28))]
    assert row["hist_ids"][row["hist_valid"]].tolist() == [0, 10, 12, 20]   # t-16 = 12; event 20 known at 24 + 4
    bad = tmp_path / "bad"
    (bad / "cache").mkdir(parents=True)
    folder = bad / "cache" / "put_back_block_episode_0000009"
    folder.mkdir()
    torch.save({"latent": torch.randn(40, 48, 1, 4, 4), "video_latent": torch.randn(40, 48, 3, 4, 4),
                "video_valid": torch.ones(40, 9, dtype=torch.bool), "text": torch.randn(7, TEXT),
                "text_valid": torch.ones(7, dtype=torch.bool), "proprio": torch.randn(40, 14),
                "actions": torch.randn(40, 14)}, folder / "encodings.pt")
    (folder / "COMPLETE.json").write_text("{}")
    (bad / "RECORDS.json").write_text(_json.dumps([{"episode_id": "put_back_block/episode_0000009",
                                                    "task": "put_back_block", "split": "train", "length": 40}]))
    beps = DenseEpisodes([str(bad)], ["put_back_block"])
    with pytest.raises(ValueError):
        Samples(beps, train_items(beps), rule, {"put_back_block/episode_0000009": EVENTS}, "valid")[0]


def test_online_ledger_decision_equals_offline_sampling():
    from fastwam.fullft.online import FrameCache, decide_encoded
    m = _model("arprop", event_slots=4)
    with torch.no_grad():
        m.hist_gate.fill_(0.5)
        m.ledger.weight.normal_(0, 0.3)
    g = torch.Generator().manual_seed(7)
    encoded = {i: (torch.randn(48, 1, 8, 6, generator=g), torch.randn(14, generator=g)) for i in range(60)}
    text = torch.cat((torch.randn(1, 2, TEXT, generator=g), torch.zeros(1, 4, TEXT)), 1)
    rule = HistoryRule("arprop", event_max=4, lag=4)
    cache = FrameCache()
    for current in (28, 48, 56):
        noise = torch.randn(1, 32, 14, generator=g)
        ledger = ledger_tensor(rule, ledger_entries(rule, current, EVENTS), lambda f: encoded[f][1])
        out = decide_encoded(m, rule, cache, encoded, current, text, noise, 3, [], ledger)
        ids, pos = select(rule, current)
        batch = {"latent": encoded[current][0][None], "text": text, "proprio": encoded[current][1][None],
                 "anchor": torch.tensor([current]), "ledger": ledger[0][None], "ledger_valid": ledger[1][None],
                 "hist_latent": torch.stack([encoded[i][0] for i in ids])[None],
                 "hist_proprio": torch.stack([encoded[i][1] for i in ids])[None],
                 "hist_valid": torch.ones(1, len(ids), dtype=torch.bool), "hist_pos": torch.tensor([pos])}
        ref = m.sample(batch, noise, steps=3)
        assert out["ids"] == ids and torch.allclose(out["normalised"], ref[0], atol=1e-6)


def test_session_streaming_detection_equals_demo_detector(tmp_path):
    from fastwam.fullft.online import FullSession
    n = 160
    grip = np.ones((n, 2))
    grip[30:80, 0] = np.linspace(1, 0, 50).clip(0, 1)[::-1] * 0 + np.r_[np.linspace(1, 0, 6), np.zeros(44)]
    pos = np.zeros((n, 2, 3))
    pos[:, :, 2] = 0.3
    pos[:, 1, 2] = 0.3 - 0.04 * np.abs(np.sin(np.arange(n) / 12.0))        # right arm goes down and up (presses)
    pos[:, 0, 0] = np.arange(n) * 0.002                                     # left arm travels (debounce path)
    pos[:, 1, 0] = np.arange(n) * 0.002
    batch_events = detect(grip, pos)
    assert any(e["kind"] in ("bottom", "top") for e in batch_events) and any(e["kind"] == "close" for e in batch_events)
    policy = types.SimpleNamespace(rule=HistoryRule("arprop", event_max=8, lag=4))
    session = FullSession(policy, tmp_path, "on", 3, 1.0, False)
    for i in range(n):
        proprio = [0.0] * 14
        proprio[6], proprio[13] = float(grip[i, 0]), float(grip[i, 1])
        session.raw[i] = {"proprio": proprio, "endpose": {"left": list(pos[i, 0]) + [1, 0, 0, 0],
                                                         "right": list(pos[i, 1]) + [1, 0, 0, 0]}}
    session._detect(70)                                                      # two decisions' worth of frames
    session._detect(n - 1)
    key = lambda e: (e["frame"], e["arm"], e["kind"], e["confirmed"])
    assert sorted(map(key, session.events)) == sorted(map(key, batch_events))
    session.raw[n] = {"proprio": [0.0] * 14}
    with pytest.raises(ValueError):
        session._detect(n)
