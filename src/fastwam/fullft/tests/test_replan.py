"""Plan v17 T2b (11-20, Opus): event-triggered re-decision at test time.
Checks: (1) visible_events is the identity unless the blind arm sets a cap; (2) ReplanDriver's schedule with a fake
session: 'off' decides at 0, 8, 16, ... exactly like the baseline, 'replan' re-decides at the frame a press is
confirmed and restarts the period there, 'blind' does the same with the previous decision's frame as the cap, the
simulator always gets a [32, 14] chunk whose first row is the next unexecuted target; (3) the real FullSession driven
through observe() frame by frame decides exactly as when the closed loop hands it 8-frame batches, and a cap hides the
entries confirmed after it from the ledger it logs."""
import json
import types

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")
np = pytest.importorskip("numpy")


def test_visible_events_identity_and_cap():
    from fastwam.fullft.online import visible_events
    evs = [{"frame": 5, "arm": 0, "kind": "bottom", "confirmed": 9}, {"frame": 12, "arm": 1, "kind": "top"}]
    assert visible_events(evs, None) is evs
    assert visible_events(evs, 8) == []
    assert visible_events(evs, 9) == [evs[0]]
    assert visible_events(evs, 12) == evs                      # no 'confirmed' -> its frame


class FakeSession:
    """observe() reports a 'bottom' confirmed at the frames in `presses`; decide() returns a chunk whose row j holds
    the value (frame + j) so the executed target identifies the decision and the offset."""

    def __init__(self, presses):
        self.presses, self.hide_after = set(presses), None
        self.calls, self.observed = [], []

    def reset(self):
        self.calls, self.observed = [], []

    def observe(self, request):
        f = int(request["current_id"])
        self.observed.append(f)
        return [{"frame": f - 3, "arm": 1, "kind": "bottom", "confirmed": f}] if f in self.presses else []

    def decide(self, request):
        f = int(request["current_id"])
        self.calls.append((f, self.hide_after))
        return np.tile((f + np.arange(32, dtype=np.float32))[:, None], (1, 14))


@pytest.mark.parametrize("mode", ["off", "replan", "blind"])
def test_driver_schedule(tmp_path, mode):
    from fastwam.memory_v2.online import ReplanDriver
    s = FakeSession(presses=[11, 30])
    d = ReplanDriver(s, 8, mode, tmp_path)
    executed = []
    for f in range(40):
        out = d.decide({"current_id": f, "observations": [{"frame_id": f}]})
        assert out.shape == (32, 14)
        executed.append(float(out[0, 0]))
    frames = [c[0] for c in s.calls]
    if mode == "off":
        assert frames == [0, 8, 16, 24, 32] and all(h is None for _, h in s.calls)
        assert executed == [float(f) for f in range(40)]       # target f comes from decision 8*(f//8), offset f%8
        assert not (tmp_path / "replan.jsonl").exists()
    else:
        assert frames == [0, 8, 11, 19, 27, 30, 38]           # re-decisions at 11 and 30 restart the period
        hides = dict(s.calls)
        if mode == "blind":
            assert hides[11] == 8 and hides[30] == 27 and hides[19] is None and hides[0] is None
        else:
            assert all(h is None for _, h in s.calls)
        assert executed == [float(f) for f in range(40)]
        rows = [json.loads(x) for x in (tmp_path / "replan.jsonl").read_text().splitlines()]
        assert [r["frame"] for r in rows] == [11, 30] and rows[0]["used_of_previous"] == 3
        assert rows[0]["previous_decision"] == 8 and rows[0]["events"] == [[8, 1, "bottom", 11]]
        assert rows[0]["joint_jump_rad"] == 0.0                  # the fake chunks agree on the shared frame
    assert s.observed == list(range(40))
    d.reset()
    assert d.chunk is None and s.calls == []


def test_driver_rejects_sessions_without_observe(tmp_path):
    from fastwam.memory_v2.online import ReplanDriver
    with pytest.raises(ValueError):
        ReplanDriver(types.SimpleNamespace(decide=lambda r: None), 8, "replan", tmp_path)
    with pytest.raises(ValueError):
        ReplanDriver(FakeSession([]), 8, "sometimes", tmp_path)


def _session(tmp_path, sub):
    import sys
    try:
        import h5py  # noqa: F401
    except ImportError:
        sys.modules["h5py"] = types.ModuleType("h5py")
    from fastwam.fullft.history import HistoryRule
    from fastwam.fullft.online import FullSession
    from fastwam.fullft.tests.test_fullft import TEXT, _model
    rule = HistoryRule("arprop", event_max=4, lag=0)
    m = _model("arprop", event_slots=rule.event_slots, ledger_features=rule.ledger_features)
    with torch.no_grad():
        m.hist_gate.fill_(0.5)
        m.ledger.weight.normal_(0, 0.3)
    g = torch.Generator().manual_seed(3)
    lat = {i: torch.randn(48, 1, 8, 6, generator=g) for i in range(48)}
    text = torch.cat((torch.randn(1, 2, TEXT, generator=g), torch.zeros(1, 4, TEXT)), 1)
    identity = types.SimpleNamespace(normalize=lambda x, kind: x, denormalize=lambda x: x)
    policy = types.SimpleNamespace(rule=rule, model=m, normaliser=identity, device=torch.device("cpu"),
                                   dense_cfg={"seed": 42}, encode_text=lambda s: (text, None))
    (tmp_path / sub).mkdir()
    session = FullSession(policy, tmp_path / sub, "on", 3, 1.0, False, tag="t", limit=48)

    def fake_encode(ids):
        for i in ids:
            session.encoded[i] = (lat[i], torch.tensor(session.raw[i]["proprio"], dtype=torch.float32))
    session._encode = fake_encode
    return session


def _observations():
    obs = []
    for i in range(48):
        p = [0.1 * (i % 7)] * 14
        p[6], p[13] = 1.0, 1.0
        z = 0.3 - (0.04 if 6 <= i <= 10 else 0.0) * (1 - abs(i - 8) / 3)     # right arm: one press, bottom at 8
        obs.append({"frame_id": i, "proprio": p, "endpose": {"left": [0.01 * i, 0, 0.3, 1, 0, 0, 0],
                                                            "right": [0.01 * i, 0, z, 1, 0, 0, 0]}})
    return obs


def test_session_observe_path_equals_batches_and_cap_hides(tmp_path):
    obs = _observations()
    a, b = _session(tmp_path, "a"), _session(tmp_path, "b")
    last, outs_a = -1, []
    for cur in (0, 8, 16, 24, 32, 40):
        outs_a.append(a.decide({"current_id": cur, "instruction": "x", "episode_seed": 5, "task": "press_button",
                                "observations": obs[last + 1:cur + 1]}))
        last = cur
    outs_b, confirmed = [], []
    for f in range(41):
        req = {"current_id": f, "instruction": "x", "episode_seed": 5, "task": "press_button", "observations": [obs[f]]}
        confirmed += [e for e in b.observe(req)]
        if f % 8 == 0:
            outs_b.append(b.decide(req))
    for x, y in zip(outs_a, outs_b):
        assert np.array_equal(x, y)
    rows_a = [json.loads(x) for x in (tmp_path / "a" / "decisions.jsonl").read_text().splitlines()]
    rows_b = [json.loads(x) for x in (tmp_path / "b" / "decisions.jsonl").read_text().splitlines()]
    assert [r["ledger"] for r in rows_a] == [r["ledger"] for r in rows_b]
    bottoms = [e for e in confirmed if e["kind"] == "bottom"]
    assert bottoms, "the synthetic press must be confirmed"
    conf = int(bottoms[0]["confirmed"])
    shown = [r for r in rows_b if any(e[2] == "bottom" for e in r["ledger"])]
    assert shown and shown[0]["frame_id"] >= conf
    # a cap before the confirmation hides it (blind arm); the next uncapped decision shows it again
    c = _session(tmp_path, "c")
    for f in range(conf + 1):
        c.observe({"current_id": f, "instruction": "x", "episode_seed": 5, "task": "press_button",
                   "observations": [obs[f]]})
    req = {"current_id": conf, "instruction": "x", "episode_seed": 5, "task": "press_button", "observations": []}
    c.hide_after = conf - 1
    c.decide(req)
    c.hide_after = None
    c.decide(req)
    rows_c = [json.loads(x) for x in (tmp_path / "c" / "decisions.jsonl").read_text().splitlines()]
    assert rows_c[0]["hide_after"] == conf - 1 and not any(e[2] == "bottom" for e in rows_c[0]["ledger"])
    assert "hide_after" not in rows_c[1] and any(e[2] == "bottom" for e in rows_c[1]["ledger"])
