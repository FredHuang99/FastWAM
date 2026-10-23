"""Host-independent parts of the memory_v2 closed loop (no simulator, no dense delivery, CPU only)."""
import json

import pytest

torch = pytest.importorskip("torch")

from fastwam.memory_v2 import online  # noqa: E402
from fastwam.memory_v2.config import HistoryPolicyConfig  # noqa: E402
from fastwam.memory_v2.dense import S1Policy, make_batch  # noqa: E402
from fastwam.memory_v2.history import select_history  # noqa: E402


class Store:
    def __init__(self, value):
        self.value = value

    def __call__(self, episode_id):
        return self.value


@pytest.mark.parametrize("anchor", [0, 7, 49])
def test_assemble_matches_offline_make_batch(anchor):
    g = torch.Generator().manual_seed(anchor)
    n = 50
    episode = {"latent": torch.randn(n, 48, 1, 24, 20, generator=g).to(torch.bfloat16),
               "text": torch.randn(8, 16, generator=g), "text_valid": torch.ones(8, dtype=torch.bool),
               "proprio": torch.randn(n, 14, generator=g), "actions": torch.randn(n, 14, generator=g)}
    features = torch.randn(n, 120, 3072, generator=g).to(torch.bfloat16)
    policy = HistoryPolicyConfig()
    s1 = S1Policy(period=8)
    row = {"episode_id": "e", "anchor": anchor, "phase": 3, "T": 8}
    offline = make_batch([row], Store(episode), Store(features), policy, "cpu", s1=s1)
    selection = select_history(range(anchor + 1), anchor, policy)
    s1_ids = s1.ids(anchor, 3)[:-1]
    encoded = {i: (episode["latent"][i], episode["proprio"][i], features[i])
               for i in sorted(set(s1_ids) | set(selection.ids) | {anchor})}
    batch = online.assemble(encoded, episode["text"][None], episode["text_valid"][None], anchor, selection, s1_ids)
    assert set(batch) == set(offline)
    for key in offline:
        if key in ("actions", "action_valid"):        # targets: offline only
            continue
        assert offline[key].dtype == batch[key].dtype, key
        assert torch.equal(offline[key], batch[key]), key


def test_assemble_without_s1_base():
    selection = select_history(range(5), 4, HistoryPolicyConfig())
    encoded = {i: (torch.zeros(48, 1, 24, 20), torch.zeros(14), torch.zeros(120, 3072, dtype=torch.bfloat16)) for i in range(5)}
    batch = online.assemble(encoded, torch.zeros(1, 8, 16), torch.ones(1, 8, dtype=torch.bool), 4, selection, None)
    assert "s1_history" not in batch and batch["history"].shape[0] == 1 and int(batch["current_ids"][0]) == 4


def test_execution_count_and_caps():
    assert online.execution_count(0, 500) == 24
    assert online.execution_count(480, 500) == 20
    assert online.execution_count(984, 1000) == 16
    with pytest.raises(ValueError):
        online.execution_count(500, 500)
    assert online.LIMITS == {"put_back_block": 500, "swap_blocks": 1000}


def test_wilson_and_mcnemar():
    lo, hi = online.wilson(5, 10)
    assert 0.2 < lo < 0.5 < hi < 0.8
    assert online.wilson(0, 10)[0] == pytest.approx(0.0, abs=1e-12)
    assert online.wilson(10, 10)[1] == pytest.approx(1.0, abs=1e-12)
    assert online.wilson(0, 0) is None
    assert online.mcnemar_exact(0, 0) == 1.0
    assert online.mcnemar_exact(6, 0) == pytest.approx(2 / 64)
    assert online.mcnemar_exact(3, 3) == 1.0


def test_episode_metrics_lift_travel_counters():
    def snap(z, x=0.0, stage=0):
        return {"block1": {"p": [x, 0.0, z], "q": [1, 0, 0, 0]}, "block2": {"p": [0.5, 0.5, 0.1], "q": [1, 0, 0, 0]},
                "stage_id": stage, "press_flag": True}
    rows = [{"objects_before": snap(0.10), "objects_after": snap(0.12, 0.01)},
            {"objects_before": snap(0.12, 0.01), "objects_after": snap(0.19, 0.03, 1)},
            {"objects_before": snap(0.19, 0.03, 1), "objects_after": snap(0.11, 0.04, 1)}]
    m = online.episode_metrics(rows)
    assert m["max_block_lift_m"] == pytest.approx(0.09)
    assert m["lifted_5cm"] is True
    assert m["travel_m"]["block1"] == pytest.approx(0.04)
    assert m["counters"]["stage_id"] == {"first": 0, "last": 1, "max": 1}
    assert "press_flag" not in m["counters"]
    assert online.episode_metrics([])["lifted_5cm"] is None


def test_load_select_scenes(tmp_path):
    bank = {"contract": {}, "complete": True,
            "scenes": [{"task": "put_back_block", "seed": 10 + i, "ordinal": i, "instruction": f"p{i}"} for i in range(4)]}
    (tmp_path / "put_back_block.json").write_text(json.dumps(bank))
    (tmp_path / "swap_blocks.json").write_text(json.dumps(
        {"scenes": [{"task": "swap_blocks", "seed": 50 + i, "ordinal": i, "instruction": f"s{i}", "gpu": {}} for i in range(3)]}))
    (tmp_path / "contract.json").write_text(json.dumps({"seed": 17}))
    scenes = online.load_scenes([str(tmp_path), str(tmp_path / "put_back_block.json")], tmp_path, list(online.LIMITS))
    assert [s["seed"] for s in scenes] == [10, 11, 12, 13, 50, 51, 52]          # deduplicated, task order
    assert "gpu" not in scenes[-1]
    assert [s["seed"] for s in online.select_scenes(scenes, 2, "0/1")] == [10, 11, 50, 51]
    assert [s["seed"] for s in online.select_scenes(scenes, 0, "1/2")] == [11, 13, 51]
    with pytest.raises(ValueError):
        online.select_scenes(scenes, 0, "2/2")


def test_overrides_labels_and_collect(tmp_path):
    value = online.apply_overrides({"memory_v2": {"history": {"landmark_stride": 24}}},
                                   ["memory_v2.history.landmark_stride=12", "seed=19"])
    assert value == {"memory_v2": {"history": {"landmark_stride": 12}}, "seed": 19}
    assert online.run_label("/x/outputs/memory_v2/v2_A_cf/checkpoints/update_001340.pt") == "v2_A_cf"
    assert online.run_label("init") == "init"
    good = tmp_path / "D" / "on" / "swap_blocks" / "seed_5"
    stale = tmp_path / "D" / "on" / "swap_blocks" / "seed_5_interrupted_123"
    for d in (good, stale):
        d.mkdir(parents=True)
    (good / "result.json").write_text(json.dumps({"label": "D", "mode": "on", "task": "swap_blocks", "seed": 5, "success": True}))
    (stale / "result.json").write_text(json.dumps({"label": "D", "mode": "on", "task": "swap_blocks", "seed": 5, "success": False}))
    rows = online.collect(tmp_path)
    assert len(rows) == 1 and rows[0]["success"] is True
