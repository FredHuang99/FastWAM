"""11-28 (RoboMME, plan v22 6.6 step 1): the per-entry proprio width follows the base (14 RoboTwin = bit-identical to the
code before; 8 for the LIBERO base). The old functions are copied here verbatim to pin the 14 path."""
import torch
from torch import nn

from fastwam.fullft.data import clock_tensor, ledger_tensor
from fastwam.fullft.history import CLOCK_CODE, LEDGER_KINDS, HistoryRule, clock_code, ledger_dim, ordinal_code


def old_ledger_tensor(rule, entries, proprio_of):
    slots = rule.event_max
    dims = int(rule.ordinal)
    feat = torch.zeros(slots, 14 + len(LEDGER_KINDS) + 2 + slots + 1 + dims)
    valid = torch.zeros(slots, dtype=torch.bool)
    flag = 20 + slots
    n = len(entries)
    for j, e in enumerate(entries):
        feat[j, :14] = proprio_of(int(e["frame"])).float()
        feat[j, 14 + LEDGER_KINDS.index(e["kind"])] = 1.0
        feat[j, 18 + int(e["arm"])] = 1.0
        feat[j, 20 + (n - 1 - j)] = 1.0
        feat[j, flag] = 1.0
        if dims:
            feat[j, flag + 1:flag + 1 + dims] = torch.tensor(ordinal_code(int(e["ordinal"]), dims))
        valid[j] = True
    return feat, valid


def old_clock_tensor(rule, frames, proprio_of, scale=1.0):
    slots = rule.event_max
    feat = torch.zeros(slots, 14 + CLOCK_CODE + 1)
    valid = torch.zeros(slots, dtype=torch.bool)
    shown = [int(f) for f in list(frames)[-slots:]]
    for j, f in enumerate(shown):
        feat[j, :14] = proprio_of(f).float()
        feat[j, 14:-1] = torch.tensor(clock_code(float(f) * scale))
        feat[j, -1] = 1.0
        valid[j] = True
    return feat, valid


ENTRIES = [{"frame": 5, "arm": 0, "kind": "close", "ordinal": 1}, {"frame": 9, "arm": 1, "kind": "bottom", "ordinal": 2},
           {"frame": 12, "arm": 0, "kind": "open", "ordinal": 3}]


def p14(f):
    return torch.arange(14, dtype=torch.float32) / 10 + f


def test_ledger_14_is_bit_identical():
    for ordinal in (0, 16):
        rule = HistoryRule(variant="arprop", event_max=32, ordinal=ordinal)
        a, va = ledger_tensor(rule, ENTRIES, p14)
        b, vb = old_ledger_tensor(rule, ENTRIES, p14)
        assert torch.equal(a, b) and torch.equal(va, vb)
        assert a.shape[1] == rule.ledger_features


def test_ledger_width_8():
    rule = HistoryRule(variant="arprop", event_max=32, ordinal=16)
    p8 = lambda f: torch.full((8,), float(f))
    feat, valid = ledger_tensor(rule, ENTRIES, p8, proprio_dim=8)
    assert feat.shape == (32, ledger_dim(32, 16, 8)) and feat.shape[1] == rule.ledger_features - 6
    assert torch.equal(feat[1, :8], torch.full((8,), 9.0))
    assert feat[1, 8 + LEDGER_KINDS.index("bottom")] == 1 and feat[1, 8 + 4 + 1] == 1   # kind, arm 1
    assert feat[1, 8 + 6 + 1] == 1                                                          # rank 1 (one newer entry)
    flag = 8 + 6 + 32
    assert feat[:3, flag].tolist() == [1, 1, 1] and feat[3:, flag].sum() == 0
    assert feat[2, flag + 1:flag + 17].tolist() == ordinal_code(3, 16)
    assert valid.tolist()[:4] == [True, True, True, False]


def test_clock_14_is_bit_identical_and_8():
    rule = HistoryRule(variant="arclk", event_max=32)
    a, va = clock_tensor(rule, [3, 7, 20], p14, 1.5)
    b, vb = old_clock_tensor(rule, [3, 7, 20], p14, 1.5)
    assert torch.equal(a, b) and torch.equal(va, vb)
    c, _ = clock_tensor(rule, [3, 7, 20], lambda f: torch.full((8,), float(f)), 1.5, proprio_dim=8)
    assert c.shape[1] == a.shape[1] - 6 and torch.equal(c[:, 8:], a[:, 14:])


def test_model_widths_follow_the_proprio_encoder():
    from types import SimpleNamespace
    from fastwam.fullft.model import FullModel

    class Mot(nn.Module):
        num_layers, num_heads = 2, 2
        mixtures = {"action": SimpleNamespace(hidden_dim=16)}
    rule = HistoryRule(variant="arprop", event_max=32, ordinal=16)
    m14 = FullModel(Mot(), nn.Linear(14, 24), "arprop", 32, ledger_features=rule.ledger_features, next_pose=True)
    m8 = FullModel(Mot(), nn.Linear(8, 24), "arprop", 32, ledger_features=rule.ledger_features, next_pose=True)
    assert m14.ledger.in_features == rule.ledger_features and m8.ledger.in_features == rule.ledger_features - 6
    assert m14.next_pose_head.weight.shape[0] == 14 and m8.next_pose_head.weight.shape[0] == 8
    p8 = FullModel(Mot(), nn.Linear(8, 24), "prop", 4)
    assert p8.extra.in_features == 4 * 9 and FullModel(Mot(), nn.Linear(14, 24), "prop", 4).extra.in_features == 60
