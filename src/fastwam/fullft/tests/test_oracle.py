"""Plan v18 Z0 (11-21, Opus): the oracle ledger (MWAM_LEDGER=oracle). Checks: oracle_presses turns the simulator's
counters into 'bottom' entries readable from the observation that first shows the press (frame f - 1, confirmed f),
with the arm nearest the button and the confirm button left out; without counters it refuses; a FullSession decision
in oracle mode logs those entries (and no detector bottom), other modes are unchanged."""
import json

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("einops")
np = pytest.importorskip("numpy")


def _raw(n, presses):
    """presses: {frame: button} -> raw observations with cumulative counters; button 1 at x=0.3 (right arm there)."""
    raw, cnt = {}, {1: 0, 2: 0, 3: 0}
    for f in range(n):
        if f in presses:
            cnt[presses[f]] += 1
        raw[f] = {"frame_id": f, "task_counts": {"press_cnt_1": cnt[1], "press_cnt_2": cnt[2], "press_cnt_check_button": cnt[3]},
                  "task_buttons": {"button1": [0.3, 0.0, 0.1], "button2": [-0.3, 0.0, 0.1]},
                  "endpose": {"left": [-0.3, 0.0, 0.2, 1, 0, 0, 0], "right": [0.3, 0.0, 0.2, 1, 0, 0, 0]}}
    return raw


def test_oracle_presses_frames_arm_and_confirm_button():
    from fastwam.fullft.online import oracle_presses
    raw = _raw(40, {10: 1, 20: 1, 25: 2, 30: 3})
    out = oracle_presses(raw, 39)
    assert [(e["frame"], e["confirmed"], e["arm"], e["oracle"]) for e in out] == [(9, 10, 1, 1), (19, 20, 1, 1), (24, 25, 0, 2)]
    assert oracle_presses(raw, 15) == out[:1]
    from fastwam.fullft.history import HistoryRule, ledger_entries
    rule = HistoryRule("arprop", event_max=8, lag=0)
    assert ledger_entries(rule, 10, out) == [out[0]]               # readable at the very observation that shows it
    assert ledger_entries(rule, 9, out) == []
    del raw[5]["task_counts"]
    with pytest.raises(ValueError):
        oracle_presses(raw, 39)


def test_session_oracle_mode_logs_true_presses(tmp_path, monkeypatch):
    from fastwam.fullft.tests.test_replan import _observations, _session
    obs = _observations()
    for f, r in enumerate(obs):                                      # one true press of button 1 shown at frame 12
        r["task_counts"] = {"press_cnt_1": int(f >= 12), "press_cnt_2": 0, "press_cnt_check_button": 0}
        r["task_buttons"] = {"button1": [0.01 * f, 0.0, 0.1], "button2": [-1.0, 0.0, 0.1]}
        r["endpose"]["left"] = [0.01 * f, 0.5, 0.3, 1, 0, 0, 0]    # left arm away from the button: right presses
    monkeypatch.setenv("MWAM_LEDGER", "oracle")
    s = _session(tmp_path, "o")
    last = -1
    for cur in (0, 8, 16, 24):
        s.decide({"current_id": cur, "instruction": "x", "episode_seed": 5, "task": "press_button",
                  "observations": obs[last + 1:cur + 1]})
        last = cur
    rows = [json.loads(x) for x in (tmp_path / "o" / "decisions.jsonl").read_text().splitlines()]
    bottoms = [[e for e in r["ledger"] if e[2] == "bottom"] for r in rows]
    assert bottoms[0] == [] and bottoms[1] == []                     # decisions at 0 and 8: not pressed yet
    assert bottoms[2] == [[11, 1, "bottom", 12]] and bottoms[3] == [[11, 1, "bottom", 12]]
    monkeypatch.delenv("MWAM_LEDGER")
    d = _session(tmp_path, "d")                                     # the detector's own bottom (synthetic dip at 8)
    last = -1
    for cur in (0, 8, 16, 24):
        d.decide({"current_id": cur, "instruction": "x", "episode_seed": 5, "task": "press_button",
                  "observations": obs[last + 1:cur + 1]})
        last = cur
    rows_d = [json.loads(x) for x in (tmp_path / "d" / "decisions.jsonl").read_text().splitlines()]
    assert any(e[2] == "bottom" and e[0] != 11 for e in rows_d[-1]["ledger"])


def test_replan_driver_oracle_trigger(tmp_path):
    """Z1: with trigger='oracle' the driver re-decides at the observation whose counters first show a press (button 1 /
    2 only), not at detector bottoms; blind hides with the previous decision's frame as the cap."""
    from fastwam.fullft.tests.test_replan import FakeSession
    from fastwam.memory_v2.online import ReplanDriver
    for mode in ("replan", "blind"):
        s = FakeSession(presses=[5])                        # a detector bottom at 5: ignored under the oracle trigger
        (tmp_path / mode).mkdir()
        d = ReplanDriver(s, 8, mode, tmp_path / mode, trigger="oracle")
        cnt = {1: 0, 2: 0, 3: 0}
        for f in range(30):
            if f == 11:
                cnt[1] += 1
            if f == 21:
                cnt[3] += 1                                 # the confirm button: no re-decision
            obs = {"frame_id": f, "task_counts": {"press_cnt_1": cnt[1], "press_cnt_2": cnt[2],
                                                  "press_cnt_check_button": cnt[3]}}
            d.decide({"current_id": f, "observations": [obs]})
        assert [c[0] for c in s.calls] == [0, 8, 11, 19, 27], (mode, s.calls)
        assert dict(s.calls)[11] == (8 if mode == "blind" else None)
        rows = [json.loads(x) for x in (tmp_path / mode / "replan.jsonl").read_text().splitlines()]
        assert [r["frame"] for r in rows] == [11] and rows[0]["events"] == [[10, -1, "bottom", 11]]
    import pytest as _pytest
    with _pytest.raises(ValueError):
        ReplanDriver(FakeSession([]), 8, "replan", tmp_path, trigger="sometimes")


def test_session_oracle_blind_hides_the_press(tmp_path, monkeypatch):
    from fastwam.fullft.tests.test_replan import _observations, _session
    obs = _observations()
    for f, r in enumerate(obs):
        r["task_counts"] = {"press_cnt_1": int(f >= 12), "press_cnt_2": 0, "press_cnt_check_button": 0}
        r["task_buttons"] = {"button1": [0.01 * f, 0.0, 0.1], "button2": [-1.0, 0.0, 0.1]}
    monkeypatch.setenv("MWAM_LEDGER", "oracle")
    s = _session(tmp_path, "b")
    for f in range(13):
        s.observe({"current_id": f, "instruction": "x", "episode_seed": 5, "task": "press_button", "observations": [obs[f]]})
    req = {"current_id": 12, "instruction": "x", "episode_seed": 5, "task": "press_button", "observations": []}
    s.hide_after = 8
    s.decide(req)
    s.hide_after = None
    s.decide(req)
    rows = [json.loads(x) for x in (tmp_path / "b" / "decisions.jsonl").read_text().splitlines()]
    assert not any(e[2] == "bottom" for e in rows[0]["ledger"]) and rows[0]["hide_after"] == 8
    assert [[e[0], e[2], e[3]] for e in rows[1]["ledger"] if e[2] == "bottom"] == [[11, "bottom", 12]]
