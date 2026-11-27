"""11-27 plan v21 card 24b: history.record_dropout (training only). 0 = bit-identical; 1 = always the empty record;
online / validation (no augment) never drop."""
import json

import pytest
import torch

from fastwam.fullft.data import DenseEpisodes, Samples, ledger_tensor, train_items
from fastwam.fullft.history import HistoryRule, ledger_entries
from fastwam.fullft.tests.test_fullft import TEXT
from fastwam.fullft.tests.test_ledger import EVENTS


def _episodes(tmp_path):
    root = tmp_path / "dense"
    records = []
    for k in range(2):
        eid = f"put_back_block/episode_{k:07d}"
        n = 60
        folder = root / "cache" / eid.replace("/", "_")
        folder.mkdir(parents=True)
        g = torch.Generator().manual_seed(k)
        torch.save({"latent": torch.randn(n, 48, 1, 4, 4, generator=g), "video_latent": torch.randn(n, 48, 3, 4, 4, generator=g),
                    "video_valid": torch.ones(n, 9, dtype=torch.bool),
                    "text": torch.cat((torch.randn(3, TEXT, generator=g), torch.zeros(4, TEXT))),
                    "text_valid": torch.tensor([True] * 3 + [False] * 4),
                    "proprio": torch.arange(n, dtype=torch.float32)[:, None].repeat(1, 14),
                    "actions": torch.randn(n, 14, generator=g)}, folder / "encodings.pt")
        (folder / "COMPLETE.json").write_text("{}")
        records.append({"episode_id": eid, "task": "put_back_block", "split": "train", "length": n})
    (root / "RECORDS.json").write_text(json.dumps(records))
    eps = DenseEpisodes([str(root)], ["put_back_block"])
    return eps, train_items(eps), {r["episode_id"]: EVENTS for r in eps.records}


def _same(a, b):
    assert a.keys() == b.keys()
    for k in a:
        if torch.is_tensor(a[k]):
            assert torch.equal(a[k], b[k]), k
        else:
            assert a[k] == b[k], k


def test_zero_is_bit_identical(tmp_path):
    eps, items, events = _episodes(tmp_path)
    old = Samples(eps, items, HistoryRule("arprop", event_max=4, lag=4), events, "valid", augment=True, seed=17)
    new = Samples(eps, items, HistoryRule("arprop", event_max=4, lag=4, record_dropout=0.0), events, "valid",
                  augment=True, seed=17)
    for i in (0, 27, 50, 90):
        _same(old[i], new[i])


def test_one_always_empty_and_validation_never_drops(tmp_path):
    eps, items, events = _episodes(tmp_path)
    rule = HistoryRule("arprop", event_max=4, lag=4, record_dropout=1.0)
    empty_feat, empty_valid = ledger_tensor(rule, [], lambda f: torch.zeros(14))
    base = Samples(eps, items, HistoryRule("arprop", event_max=4, lag=4), events, "valid", augment=True, seed=17)
    drop = Samples(eps, items, rule, events, "valid", augment=True, seed=17)
    for i in (27, 50):
        r, b = drop[i], base[i]
        assert torch.equal(r["ledger"], empty_feat) and not r["ledger_valid"].any()
        for k in r:                                   # only the record changes
            if k not in ("ledger", "ledger_valid") and torch.is_tensor(r[k]):
                assert torch.equal(r[k], b[k]), k
    val = Samples(eps, items, rule, events, "valid", augment=False, seed=17)
    a = items[50][1]
    want = ledger_tensor(rule, ledger_entries(rule, a, EVENTS), lambda f: torch.full((14,), float(f)))
    assert torch.equal(val[50]["ledger"], want[0])


def test_rule_checks():
    with pytest.raises(ValueError):
        HistoryRule("ar", record_dropout=0.3)
    with pytest.raises(ValueError):
        HistoryRule("arprop", record_dropout=1.5)
    assert HistoryRule("arprop", record_dropout=0.3).record_dropout == 0.3
