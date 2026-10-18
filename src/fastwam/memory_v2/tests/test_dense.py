"""Host-independent parts of the dense bridge (no dense delivery needed)."""
import pytest

torch = pytest.importorskip("torch")

from fastwam.memory_v2.dense import (ARM_COLUMNS, GRIPPER_COLUMNS, action_window, summarise,  # noqa: E402
                                     window_kind, window_metrics, window_noise)


class Identity:
    def denormalize(self, x):
        return x.float()


def test_action_window_holds_last_target_and_masks():
    actions = torch.arange(10, dtype=torch.float32)[:, None].repeat(1, 14)
    chunk, valid = action_window(actions, 4)
    assert chunk.shape == (32, 14) and int(valid.sum()) == 6
    assert torch.equal(chunk[:6, 0], torch.arange(4, 10, dtype=torch.float32))
    assert bool((chunk[6:, 0] == 9).all())
    with pytest.raises(ValueError):
        action_window(actions, 10)


def test_window_metrics_prefixes():
    target = torch.zeros(32, 14)
    sample = torch.zeros(32, 14)
    sample[:16, ARM_COLUMNS] = 1.0        # error only in the first 16 steps
    sample[:, GRIPPER_COLUMNS] = 2.0
    valid = torch.ones(32, dtype=torch.bool)
    m = window_metrics(sample, target, valid, Identity())
    assert m["prefix16_arm_rmse_rad"] == pytest.approx(1.0)
    assert m["prefix24_arm_rmse_rad"] == pytest.approx((16 / 24) ** 0.5)
    assert m["arm_rmse_rad"] == pytest.approx(0.5 ** 0.5)
    assert m["gripper_rmse"] == pytest.approx(2.0)
    valid[8:] = False
    m = window_metrics(sample, target, valid, Identity())
    assert m["arm_rmse_rad"] == pytest.approx(1.0) and m["prefix24_arm_rmse_rad"] == pytest.approx(1.0)


def test_window_noise_matches_dense_first_draw():
    row = {"action_seed": 1234}
    expected = torch.randn((32, 14), generator=torch.Generator().manual_seed(1234), dtype=torch.float32)
    assert torch.equal(window_noise(row, (32, 14), "cpu"), expected)


def test_window_kind_and_summary():
    rows = [{"labels": ["initial"]}, {"labels": ["left_close_at"]}, {"labels": ["residue_3"]}]
    assert [window_kind(r) for r in rows] == ["initial", "event", "ordinary"]
    cases = [{"task": "t", "split": "val", "kind": k, "x": float(i)} for i, k in enumerate(["initial", "event", "event"])]
    out = summarise(cases, ["x"])
    assert out[0]["windows"] == 3 and out[0]["x"] == pytest.approx(1.0)
    assert out[0]["by_window_kind"]["event"]["x"] == pytest.approx(1.5)
