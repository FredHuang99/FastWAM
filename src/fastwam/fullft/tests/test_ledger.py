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


@pytest.mark.parametrize("variant", ["ar", "arprop", "arprop_ord", "arclk"])
def test_session_decide_end_to_end(tmp_path, variant):
    """FullSession.decide as the closed loop calls it (observation batches, identity checks, detection, ledger,
    selection, eviction, the decision log), with the image / text encoders stubbed: it equals decide_encoded on the
    same encodings and logs the ledger it used."""
    import json as _json
    import sys
    try:
        import h5py  # noqa: F401
    except ImportError:                                # the dev machine has no h5py; nothing here reads hdf5
        sys.modules["h5py"] = types.ModuleType("h5py")
    from fastwam.fullft.online import FrameCache, FullSession, decide_encoded
    from fastwam.memory_s1.common import seed_for
    from fastwam.memory_s1.sim_bridge import diagnostic_action_noise
    ordinal = 3 if variant == "arprop_ord" else 0                  # 11-17 plan v13 E4: the ordinal code end to end
    variant = "arprop" if ordinal else variant
    rule = HistoryRule(variant, event_max=4, lag=4, ordinal=ordinal)
    m = _model(variant, event_slots=rule.event_slots, ledger_features=rule.ledger_features)
    with torch.no_grad():
        m.hist_gate.fill_(0.5)
        if m.ledger is not None:
            m.ledger.weight.normal_(0, 0.3)
    g = torch.Generator().manual_seed(3)
    lat = {i: torch.randn(48, 1, 8, 6, generator=g) for i in range(80)}
    text = torch.cat((torch.randn(1, 2, TEXT, generator=g), torch.zeros(1, 4, TEXT)), 1)
    identity = types.SimpleNamespace(normalize=lambda x, kind: x, denormalize=lambda x: x)
    policy = types.SimpleNamespace(rule=rule, model=m, normaliser=identity, device=torch.device("cpu"),
                                   dense_cfg={"seed": 42}, encode_text=lambda s: (text, None))
    session = FullSession(policy, tmp_path, "on", 3, 1.0, False, tag="t", limit=80)

    def fake_encode(ids):
        for i in ids:
            r = session.raw[i]
            session.encoded[i] = (lat[i], torch.tensor(r["proprio"], dtype=torch.float32))
    session._encode = fake_encode
    grip = np.ones(80)
    grip[12:] = 0.0                                    # left arm closes at frame 12 -> one 'close' event
    pos = np.zeros((80, 2, 3))
    pos[:, 0, 0] = np.arange(80) * 0.01
    obs = []
    for i in range(80):
        p = [0.1 * (i % 7)] * 14
        p[6], p[13] = float(grip[i]), 1.0
        obs.append({"frame_id": i, "proprio": p, "endpose": {"left": list(pos[i, 0]) + [1, 0, 0, 0],
                                                            "right": list(pos[i, 1]) + [1, 0, 0, 0]}})
    ref_cache, ref_encoded = FrameCache(), {}
    last = -1
    for current in (0, 8, 16, 24, 40):
        req = {"current_id": current, "instruction": "x", "episode_seed": 5, "task": "put_back_block",
               "observations": obs[last + 1:current + 1]}
        last = current
        out = session.decide(req)
        noise = diagnostic_action_noise(seed_for(42, 5, current, "closed-loop-noise")).to(torch.bfloat16).float()
        for i in range(current + 1):
            ref_encoded.setdefault(i, (lat[i], torch.tensor(obs[i]["proprio"], dtype=torch.float32)))
        ledger = None
        if variant == "arclk":                                         # 11-17 plan v13 E5: clock tokens
            from fastwam.fullft.data import clock_tensor
            from fastwam.fullft.history import clock_frames
            ledger = clock_tensor(rule, clock_frames(rule, current), lambda f: ref_encoded[f][1])
        if variant == "arprop":
            evs = detect(np.stack([grip[:current + 1], np.ones(current + 1)], 1), pos[:current + 1])
            ledger = ledger_tensor(rule, ledger_entries(rule, current, evs), lambda f: ref_encoded[f][1])
        ref = decide_encoded(m, rule, ref_cache, ref_encoded, current, text, noise, 3, [], ledger)
        want = ref["normalised"].clone()
        want[:, [6, 13]] = want[:, [6, 13]].clamp(0, 1)            # the session clips the grippers after denormalising
        assert np.allclose(out, want.numpy(), atol=1e-5)
    rows = [_json.loads(x) for x in (tmp_path / "decisions.jsonl").read_text().splitlines()]
    assert len(rows) == 5 and rows[0]["ledger"] == []
    if variant == "arprop":
        assert rows[1]["frame_id"] == 8 and rows[1]["ledger"] == []                  # close at 12 not seen yet
        assert rows[2]["frame_id"] == 16 and rows[2]["ledger"] == [[12, 0, "close", 12] + ([1] if ordinal else [])]
        assert rows[2]["events_known"] == [12]


def test_event_rule_travels_with_the_model(tmp_path, monkeypatch):
    """11-16: HistoryRule carries the detector thresholds (defaults = frozen rule A, so earlier exports are unchanged);
    the online session builds its detector from them; test-time env overrides change only the session's copy;
    the trainer refuses an events file written with other thresholds."""
    import json
    from fastwam.fullft.data import load_events
    from fastwam.fullft.events import EventRule, parse_rule, rule_for
    from fastwam.fullft.online import FullSession, effective_rule
    base = HistoryRule("arprop", event_max=8, lag=4)
    assert rule_for(base) == EventRule()                                      # rule A
    fast = HistoryRule("arprop", event_max=8, lag=0, event_delta=0.008, event_min_path=0.015)
    assert rule_for(fast).delta == 0.008 and rule_for(fast).min_path == 0.015
    with pytest.raises(ValueError):
        HistoryRule("arprop", event_delta=0.0)
    for k in ("MWAM_LEDGER_LAG", "MWAM_EVENT_DELTA", "MWAM_EVENT_MIN_PATH"):
        monkeypatch.delenv(k, raising=False)
    assert effective_rule(base) is base
    monkeypatch.setenv("MWAM_LEDGER_LAG", "0")
    monkeypatch.setenv("MWAM_EVENT_DELTA", "0.006")
    eff = effective_rule(base)
    assert (eff.lag, eff.event_delta, eff.event_min_path, eff.event_max) == (0, 0.006, 0.03, 8) and base.lag == 4
    session = FullSession(types.SimpleNamespace(rule=base), tmp_path, "on", 3, 1.0, False)
    assert session.detector.rule.delta == 0.006 and session.rule.lag == 0
    monkeypatch.delenv("MWAM_LEDGER_LAG"); monkeypatch.delenv("MWAM_EVENT_DELTA")
    session.reset()
    assert session.detector.rule == EventRule() and session.rule.lag == 4
    # a smaller delta confirms a press bottom earlier (less rise needed) -> the entry is usable sooner
    n = 60
    pos = np.zeros((n, 2, 3)); pos[:, :, 2] = 0.3
    pos[:, 0, 2] = 0.3 - 0.04 * np.clip(1 - np.abs(np.arange(n) - 20) / 10, 0, 1)   # one 4 cm press, bottom at 20
    grip = np.ones((n, 2))
    slow = [e for e in detect(grip, pos) if e["kind"] == "bottom"]
    quick = [e for e in detect(grip, pos, EventRule(delta=0.008, min_path=0.015)) if e["kind"] == "bottom"]
    assert slow[0]["frame"] == quick[0]["frame"] == 20 and quick[0]["confirmed"] < slow[0]["confirmed"]
    # events files: rule field parsed; mismatch refused; files without the field count as rule A
    assert parse_rule(str(EventRule(delta=0.008, min_path=0.015))) == {"delta": 0.008, "min_path": 0.015}
    assert parse_rule("") == {"delta": 0.015, "min_path": 0.03}
    a = tmp_path / "events_a.json"; a.write_text(json.dumps({"rule": str(EventRule()), "episodes": {"x": []}}))
    b = tmp_path / "events_b.json"; b.write_text(json.dumps({"rule": str(EventRule(delta=0.008, min_path=0.015)),
                                                            "episodes": {"y": []}}))
    c = tmp_path / "events_c.json"; c.write_text(json.dumps({"z": []}))
    assert set(load_events([str(a), str(c)], base)) == {"x", "z"}
    assert set(load_events([str(b)], fast)) == {"y"}
    with pytest.raises(ValueError):
        load_events([str(b)], base)
    with pytest.raises(ValueError):
        load_events([str(a)], fast)
    assert set(load_events([str(a), str(b)])) == {"x", "y"}                  # no rule given: no check (old callers)


def test_config_event_rule_from_copies_numbers(tmp_path):
    """11-16: history.event_rule_from=<PRESS_FAST_RULE.json> becomes event_delta / event_min_path numbers in the config
    (run_config.json and exports never hold the path); without it the defaults (rule A) stay."""
    import json
    from fastwam.fullft.config import load
    pick = tmp_path / "PRESS_FAST_RULE.json"
    pick.write_text(json.dumps({"delta": 0.008, "min_path": 0.015, "why": "test"}))
    cfg = load(None, ["history.variant=arprop", "history.event_max=32", "history.lag=0", f"history.event_rule_from={pick}"])
    assert "event_rule_from" not in cfg.history and cfg.rule.event_delta == 0.008 and cfg.rule.event_min_path == 0.015
    assert cfg.rule.lag == 0 and json.loads(json.dumps(cfg.to_dict()))["history"]["event_delta"] == 0.008
    plain = load(None, ["history.variant=arprop", "history.lag=4"])
    assert plain.rule.event_delta == 0.015 and plain.rule.event_min_path == 0.03


def test_press_counterfactual():
    """11-16: addpress enters the first completed press (bottom + its top) twice; droppress removes it; nothing changes
    before that press is complete; other arms and later presses are untouched."""
    from fastwam.fullft.online import press_counterfactual
    e = lambda f, a, k: {"frame": f, "arm": a, "kind": k, "confirmed": f + 3}          # noqa: E731
    only_bottom = [e(10, 0, "bottom")]
    assert press_counterfactual(only_bottom, "addpress") == only_bottom
    led = [e(5, 1, "close"), e(10, 0, "bottom"), e(12, 1, "top"), e(18, 0, "top"), e(30, 0, "bottom"), e(38, 0, "top")]
    add = press_counterfactual(led, "addpress")
    assert [x["kind"] for x in add].count("bottom") == 3 and len(add) == len(led) + 2
    assert add[4:6] == [led[1], led[3]] and add[4] is not led[1]                     # copies, right after its top
    drop = press_counterfactual(led, "droppress")
    assert drop == [led[0], led[2], led[4], led[5]]
    assert press_counterfactual([], "droppress") == []


# ----------------------------------------------------------------------------- 11-17 plan v13 E4 / E7
PRESSES = [{"frame": 10, "arm": 1, "kind": "bottom", "confirmed": 12},
           {"frame": 16, "arm": 1, "kind": "top", "confirmed": 18},
           {"frame": 20, "arm": 0, "kind": "close", "confirmed": 20},
           {"frame": 30, "arm": 1, "kind": "bottom", "confirmed": 32},
           {"frame": 36, "arm": 1, "kind": "top", "confirmed": 38},
           {"frame": 50, "arm": 1, "kind": "bottom", "confirmed": 52},
           {"frame": 56, "arm": 1, "kind": "top", "confirmed": 58},
           {"frame": 60, "arm": 1, "kind": "bottom", "confirmed": 62}]


def test_ordinal_entries_and_features():
    from fastwam.fullft.history import ordinal_code
    with pytest.raises(ValueError):
        HistoryRule("ar", ordinal=4)                                             # ledger feature only
    base = HistoryRule("arprop", event_max=3, lag=0)
    assert base.ledger_features == ledger_dim(3) == 3 + 21 and ledger_dim(32) == 53         # unchanged without it
    assert all("ordinal" not in e for e in ledger_entries(base, 100, PRESSES))
    rule = HistoryRule("arprop", event_max=3, lag=0, ordinal=4)
    assert rule.ledger_features == ledger_dim(3, 4) == ledger_dim(3) + 4 and HistoryRule("ar").ledger_features == 0
    got = ledger_entries(rule, 100, PRESSES)                                    # capped at 3, counted from the start
    assert [(e["frame"], e["ordinal"]) for e in got] == [(50, 3), (56, 3), (60, 4)]
    assert "ordinal" not in PRESSES[0]                                           # copies, the event list untouched
    assert ordinal_code(1, 4) == [1, 0, 0, 0] and ordinal_code(4, 4) == [1, 1, 1, 1] and ordinal_code(9, 4) == [1] * 4
    proprio = {f: torch.full((14,), float(f)) for f in range(100)}
    f0, v0 = ledger_tensor(base, ledger_entries(base, 100, PRESSES), lambda f: proprio[f])
    f1, v1 = ledger_tensor(rule, got, lambda f: proprio[f])
    assert f1.shape == (3, ledger_dim(3, 4)) and torch.equal(v0, v1)
    assert torch.equal(f1[:, :ledger_dim(3)], f0)                               # the old features, same places
    assert f1[0, -4:].tolist() == [1, 1, 1, 0] and f1[2, -4:].tolist() == [1, 1, 1, 1]
    f2, v2 = ledger_tensor(rule, ledger_entries(rule, 21, PRESSES), lambda f: proprio[f])
    assert v2.tolist() == [True, True, True] and f2[0, -4:].tolist() == [1, 0, 0, 0]    # 1st bottom, 1st top, 1st close
    with pytest.raises(KeyError):
        ledger_tensor(rule, ledger_entries(base, 100, PRESSES), lambda f: proprio[f])     # entries without ordinals


def test_ordinal_counterfactuals():
    from fastwam.fullft.history import ordinal_counterfactual
    rule = HistoryRule("arprop", event_max=10 ** 6, lag=0, ordinal=16)
    full = ledger_entries(rule, 100, PRESSES)
    plus = ordinal_counterfactual(full, "ordplus1")
    assert len(plus) == len(full)
    assert [e["ordinal"] for e in plus] == [2, 2, 1, 3, 3, 4, 4, 5]               # the close keeps 1
    assert [e["ordinal"] for e in full] == [1, 1, 1, 2, 2, 3, 3, 4]               # input untouched
    dup = ordinal_counterfactual(full, "duppress")                                # last COMPLETED press: 50 / 56
    assert [(e["frame"], e["ordinal"]) for e in dup] == [(10, 1), (16, 1), (20, 1), (30, 2), (36, 2), (50, 3),
                                                         (56, 3), (50, 3), (56, 3), (60, 4)]
    early = ledger_entries(rule, 13, PRESSES)                                     # only the 1st bottom written
    assert ordinal_counterfactual(early, "duppress") == early
    with pytest.raises(ValueError):
        ordinal_counterfactual(ledger_entries(HistoryRule("arprop", event_max=99), 100, PRESSES), "ordplus1")
    with pytest.raises(ValueError):
        ordinal_counterfactual(full, "nope")


def test_zero_ledger_with_ordinal_is_exactly_ar():
    rule = HistoryRule("arprop", event_max=4, lag=0, ordinal=16)
    batch = _ledger_batch()
    batch["ledger"] = torch.randn(2, 4, rule.ledger_features, generator=torch.Generator().manual_seed(5))
    noise = _noise(batch)
    m0, ml = _model("ar"), _model("arprop", event_slots=4, ledger_features=rule.ledger_features)
    assert ml.ledger.in_features == ledger_dim(4, 16)
    missing, unexpected = ml.load_state_dict(m0.state_dict(), strict=False)
    assert not unexpected and sorted(missing) == ["ledger.bias", "ledger.weight"]
    with torch.no_grad():
        m0.hist_gate.fill_(0.3)
        ml.hist_gate.fill_(0.3)
        v0, a0 = m0.loss(batch, noise)
        v1, a1 = ml.loss(batch, noise)
        assert torch.equal(v0, v1) and torch.equal(a0, a1)
    v, a = ml.loss(batch, noise)
    (a.mean() + v.mean()).backward()
    assert float(ml.ledger.weight.grad[:, -16:].abs().sum()) > 0                 # the code columns learn


def test_resume_source(tmp_path):
    from fastwam.fullft.train import resume_source
    run, other = tmp_path / "run", tmp_path / "other"
    run.mkdir(); other.mkdir()
    assert resume_source(run, "") is None
    with pytest.raises(FileNotFoundError):
        resume_source(run, str(other / "resume.pt"))                              # never a silent fresh start
    (other / "resume.pt").write_text("x")
    assert resume_source(run, str(other / "resume.pt")) == other / "resume.pt"
    assert resume_source(run, str(other / "resume.pt"), smoke=True) is None
    (run / "resume.pt").write_text("y")
    assert resume_source(run, str(other / "resume.pt")) == run / "resume.pt"      # its own checkpoint wins


def test_arclk_zero_encoder_is_exactly_ar_and_dataset_builds_clock_tokens(tmp_path):
    """11-17 plan v13 E5: time-indexed proprio tokens through the ledger path; zero encoder = exactly AR; the dense
    dataset builds the same tokens as clock_tensor(clock_frames(t)); the frames move with t (time-indexed)."""
    import json as _json
    from fastwam.fullft.data import DenseEpisodes, Samples, clock_tensor, collate, train_items
    from fastwam.fullft.history import clock_dim, clock_frames
    rule = HistoryRule("arclk", event_max=4)
    assert rule.ledger_features == clock_dim() and rule.max_frames == HistoryRule("ar").max_frames
    assert clock_frames(rule, 40) == [0, 13, 26, 39] and clock_frames(rule, 41) == [0, 13, 27, 40]
    batch = _ledger_batch()
    batch["ledger"] = torch.randn(2, 4, clock_dim(), generator=torch.Generator().manual_seed(3))
    noise = _noise(batch)
    m0, mc = _model("ar"), _model("arclk", event_slots=4, ledger_features=rule.ledger_features)
    missing, unexpected = mc.load_state_dict(m0.state_dict(), strict=False)
    assert not unexpected and sorted(missing) == ["ledger.bias", "ledger.weight"]
    with torch.no_grad():
        m0.hist_gate.fill_(0.3)
        mc.hist_gate.fill_(0.3)
        v0, a0 = m0.loss(batch, noise)
        v1, a1 = mc.loss(batch, noise)
        assert torch.equal(v0, v1) and torch.equal(a0, a1)
    v, a = mc.loss(batch, noise)
    (a.mean() + v.mean()).backward()
    assert float(mc.ledger.weight.grad.abs().sum()) > 0
    with pytest.raises(ValueError):
        _model("arclk", event_slots=4)                                 # the width must come from the rule
    root = tmp_path / "dense"
    eid = "put_back_block/episode_0000000"
    folder = root / "cache" / eid.replace("/", "_")
    folder.mkdir(parents=True)
    n = 60
    torch.save({"latent": torch.randn(n, 48, 1, 4, 4), "video_latent": torch.randn(n, 48, 3, 4, 4),
                "video_valid": torch.ones(n, 9, dtype=torch.bool), "text": torch.cat((torch.randn(3, TEXT), torch.zeros(4, TEXT))),
                "text_valid": torch.tensor([True] * 3 + [False] * 4),
                "proprio": torch.arange(n, dtype=torch.float32)[:, None].repeat(1, 14), "actions": torch.randn(n, 14)},
               folder / "encodings.pt")
    (folder / "COMPLETE.json").write_text("{}")
    (root / "RECORDS.json").write_text(_json.dumps([{"episode_id": eid, "task": "put_back_block", "split": "train",
                                                      "length": n}]))
    eps = DenseEpisodes([str(root)], ["put_back_block"])
    items = train_items(eps)
    ds = Samples(eps, items, rule, {}, "valid")
    for a in (0, 1, 5, 40, 59):
        row = ds[items.index((eid, a))]
        feat, valid = clock_tensor(rule, clock_frames(rule, a), lambda f: torch.full((14,), float(f)))
        assert torch.equal(row["ledger"], feat) and torch.equal(row["ledger_valid"], valid)
        assert row["hist_ids"][row["hist_valid"]].tolist() == select(HistoryRule("ar"), a)[0]
    assert collate([ds[i] for i in (0, 30)])["ledger"].shape == (2, 4, clock_dim())
    f2, _ = clock_tensor(rule, [10], lambda f: torch.zeros(14), scale=1.5)
    f1, _ = clock_tensor(rule, [15], lambda f: torch.zeros(14))
    assert torch.allclose(f1, f2)                                        # timestamp scaling = another frame index


def test_clock_test_time_modes():
    """11-19 plan v15 E21: the test-time clock modes. '' = as trained; off = no valid token; freeze = every token's
    joint state is the current frame's, timestamps unchanged; flat = every timestamp is the middle sample's, joint
    states unchanged; an unknown mode or freeze without the current frame is refused."""
    from fastwam.fullft.data import clock_tensor
    from fastwam.fullft.history import clock_code, clock_frames
    rule = HistoryRule("arclk", event_max=4)
    frames = clock_frames(rule, 40)                                   # [0, 13, 26, 39]
    state = {f: torch.full((14,), float(f)) for f in range(41)}
    of = lambda f: state[int(f)]                                      # noqa: E731
    base, bv = clock_tensor(rule, frames, of)
    assert bv.all() and torch.equal(base[:, 0], torch.tensor([0.0, 13.0, 26.0, 39.0]))
    off, ov = clock_tensor(rule, frames, of, mode="off")
    assert not ov.any() and float(off.abs().sum()) == 0.0
    frz, fv = clock_tensor(rule, frames, of, mode="freeze", current=40)
    assert torch.equal(fv, bv) and bool((frz[:, :14] == 40.0).all())
    assert torch.equal(frz[:, 14:], base[:, 14:])                     # timestamps and valid flag unchanged
    flat, lv = clock_tensor(rule, frames, of, mode="flat")
    assert torch.equal(lv, bv) and torch.equal(flat[:, :14], base[:, :14])
    middle = torch.tensor(clock_code(26.0))                           # frames[len // 2] = 26
    assert all(torch.allclose(flat[j, 14:-1], middle) for j in range(4))
    sc, _ = clock_tensor(rule, frames, of, scale=1.5, mode="flat")
    assert torch.allclose(sc[0, 14:-1], torch.tensor(clock_code(26.0 * 1.5)))
    with pytest.raises(ValueError):
        clock_tensor(rule, frames, of, mode="sideways")
    with pytest.raises(ValueError):
        clock_tensor(rule, frames, of, mode="freeze")


def test_token_budget_env(monkeypatch):
    """11-19 plan v15 E22b: MWAM_BUDGET parses to K (unset = 0 = as trained); K clock samples still span [0, t)."""
    import dataclasses
    from fastwam.fullft.online import token_budget
    from fastwam.fullft.history import clock_frames
    monkeypatch.delenv("MWAM_BUDGET", raising=False)
    assert token_budget() == 0
    monkeypatch.setenv("MWAM_BUDGET", "8")
    assert token_budget() == 8
    rule = HistoryRule("arclk", event_max=32)
    f8 = clock_frames(dataclasses.replace(rule, event_max=8), 300)
    assert len(f8) == 8 and f8[0] == 0 and f8[-1] == 299
    monkeypatch.setenv("MWAM_BUDGET", "-1")
    with pytest.raises(ValueError):
        token_budget()
