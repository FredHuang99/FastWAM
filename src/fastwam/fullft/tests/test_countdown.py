"""11-28 plan v22 card 31: history.count_mode=remaining (the countdown). Off = bit-identical; on = the countdown values."""
import dataclasses

import pytest
import torch

from fastwam.fullft.data import ledger_tensor
from fastwam.fullft.history import (HistoryRule, annotate_remaining, ledger_entries, press_button_of, told_targets)

# a press_button-like demo: arm 0 presses the left button twice, the middle button three times, the check button once
X = {0: -0.15, 1: 0.0, 2: 0.15}


def ev(frame, kind, where, arm=0):
    return {"frame": frame, "arm": arm, "kind": kind, "confirmed": frame + 2, "x": X[where]}


EVENTS = [ev(10, "bottom", 0), ev(14, "top", 0), ev(30, "bottom", 0), ev(34, "top", 0),
          ev(50, "bottom", 1), ev(54, "top", 1), ev(70, "bottom", 1), ev(74, "top", 1),
          ev(90, "bottom", 1), ev(94, "top", 1), ev(110, "bottom", 2), ev(114, "top", 2),
          {"frame": 5, "arm": 1, "kind": "close", "confirmed": 6}]


def button_of(e):
    return press_button_of(e.get("x", 0.15))


def proprio(f):
    return torch.full((14,), float(f) / 100.0)


def test_off_is_bit_identical():
    """count_mode '' must give exactly the ordinal path (entries and the ledger tensor)."""
    rule = HistoryRule(variant="arprop", event_max=32, ordinal=16)
    assert rule.count_mode == ""
    ann = annotate_remaining(EVENTS, {1: 2, 2: 3}, button_of)        # extra keys present must not change the off path
    for t in (0, 40, 120):
        a = ledger_entries(rule, t, EVENTS)
        b = ledger_entries(rule, t, ann)
        assert [e["ordinal"] for e in a] == [e["ordinal"] for e in b]
        fa, va = ledger_tensor(rule, a, proprio)
        fb, vb = ledger_tensor(rule, b, proprio)
        assert torch.equal(fa, fb) and torch.equal(va, vb)


def test_countdown_values():
    ann = annotate_remaining(EVENTS, {1: 2, 2: 3}, button_of)
    rem = [(e["frame"], e["kind"], e.get("button"), e["remaining"]) for e in ann]
    assert (10, "bottom", 1, 1) in rem and (14, "top", 1, 1) in rem
    assert (30, "bottom", 1, 0) in rem and (34, "top", 1, 0) in rem
    assert [r for f, k, b, r in rem if b == 2 and k == "bottom"] == [2, 1, 0]
    assert all(r is None for f, k, b, r in rem if b == 3 or k == "close")


def test_countdown_entries_and_code():
    rule = HistoryRule(variant="arprop", event_max=32, ordinal=16, count_mode="remaining")
    ann = annotate_remaining(EVENTS, {1: 2, 2: 3}, button_of)
    ents = ledger_entries(rule, 120, ann)
    by = {(e["frame"], e["kind"]): e["ordinal"] for e in ents}
    assert by[(30, "bottom")] == 1          # 0 still to do -> thermometer of 1 (first feature on)
    assert by[(10, "bottom")] == 2
    assert by[(110, "bottom")] == 0         # check button: all features off
    assert by[(5, "close")] == 0
    feat, valid = ledger_tensor(rule, ents, proprio)
    flag = 20 + 32
    j = [i for i, e in enumerate(ents) if (e["frame"], e["kind"]) == (30, "bottom")][0]
    assert feat[j, flag + 1].item() == 1.0 and feat[j, flag + 2].item() == 0.0
    k = [i for i, e in enumerate(ents) if (e["frame"], e["kind"]) == (110, "bottom")][0]
    assert feat[k, flag + 1:flag + 17].sum().item() == 0.0 and valid[k]


def test_overpress_clamps_and_told_parse():
    extra = EVENTS + [ev(130, "bottom", 0), ev(134, "top", 0)]
    ann = annotate_remaining(extra, {1: 2, 2: 3}, button_of)
    assert [e["remaining"] for e in ann if e.get("button") == 1 and e["kind"] == "bottom"] == [1, 0, 0]
    assert told_targets("Press the button. Press the left button two times and the middle button three times.") == {1: 2, 2: 3}
    assert told_targets("Press the button.") == {}


def test_validation():
    with pytest.raises(ValueError):
        HistoryRule(variant="arprop", event_max=32, ordinal=0, count_mode="remaining")
    with pytest.raises(ValueError):
        HistoryRule(variant="ar", count_mode="remaining")
    with pytest.raises(ValueError):
        HistoryRule(variant="arprop", event_max=32, ordinal=16, count_mode="left")
    r = HistoryRule(variant="arprop", event_max=32, ordinal=16, count_mode="remaining")
    assert dataclasses.replace(r, count_mode="").count_mode == ""


def test_online_countdown_annotation():
    """The online session's _countdown: told counts from the instruction, the button from the observation's endpose."""
    from types import SimpleNamespace
    from fastwam.fullft.online import FullSession
    raw = {f: {"endpose": {"left": [X[0] if f < 40 else X[1], 0.0, 0.8], "right": [0.3, 0.0, 0.8]}} for f in range(120)}
    fake = SimpleNamespace(raw=raw, instruction="Press. Press the left button two times and the middle button one times.")
    evs = [{"frame": 10, "arm": 0, "kind": "bottom", "confirmed": 12}, {"frame": 30, "arm": 0, "kind": "bottom", "confirmed": 32},
           {"frame": 50, "arm": 0, "kind": "bottom", "confirmed": 52}, {"frame": 55, "arm": 0, "kind": "top", "confirmed": 57}]
    ann = FullSession._countdown(fake, evs)
    assert [e["remaining"] for e in ann] == [1, 0, 0, 0]
    assert [e["button"] for e in ann] == [1, 1, 2, 2]
    with pytest.raises(ValueError):
        FullSession._countdown(SimpleNamespace(raw=raw, instruction="Press."), evs)
