"""Plan v8 D5 (11-06): auxiliary task-progress head (label = frame / episode length), tiny CPU backend."""
import json

import pytest
import torch

from fastwam.memory_v2.config import MemoryV2Config, V2Config
from fastwam.memory_v2.model import MemoryV2Model
from fastwam.memory_v2.tests.helpers import TINY, TinyBackbone
from fastwam.memory_v2.tests.test_train_v2 import POLICY, TinyBackend, _cfg
from fastwam.memory_v2.train_v2 import Trainer, TrainConfig


class ProgressBackend(TinyBackend):
    def __init__(self, head=True):
        super().__init__()
        torch.manual_seed(0)
        self.model = MemoryV2Model(TinyBackbone(), MemoryV2Config(**TINY, progress_head=head)).float()

    def batch(self, rows):
        out = super().batch(rows)
        out["progress"] = torch.tensor([r["anchor"] / (self.length - 1) for r in rows], dtype=torch.float32)
        return out


def _progress_cfg(tmp_path, weight=0.5, epochs=1):
    cfg = _cfg(tmp_path, epochs=epochs)
    cfg.v2 = V2Config.from_dict({"memory": dict(TINY, progress_head=True), "history": POLICY.__dict__,
                                 "objective": {"progress_weight": weight}, "guidance": {"steps": 3}})
    return cfg


def test_config_off_by_default_and_validated():
    assert "progress_head" not in V2Config().to_dict()["memory"]
    assert "progress_weight" not in V2Config().to_dict()["objective"]
    with pytest.raises(ValueError):
        V2Config.from_dict({"objective": {"progress_weight": 0.1}})
    on = V2Config.from_dict({"memory": {"progress_head": True}, "objective": {"progress_weight": 0.1}})
    assert V2Config.from_dict(on.to_dict()).objective.progress_weight == 0.1


def test_head_starts_at_half_and_never_changes_the_actions():
    with_head, without = ProgressBackend(True), ProgressBackend(False)
    names = set(dict(without.model.memory.named_parameters()))
    assert set(dict(with_head.model.memory.named_parameters())) - names == {"progress.weight", "progress.bias"}
    with_head.model.memory.load_state_dict({**without.model.memory.state_dict(),
                                            **{k: v for k, v in with_head.model.memory.state_dict().items()
                                               if k.startswith("progress.")}})
    batch = with_head.batch(with_head.train_rows()[:4])
    x, t = torch.randn(4, 8, 5), torch.full((4,), 1000.0)
    with torch.no_grad():
        a, hidden = with_head.model.velocity(x, t, with_head.model.conditions(batch), return_hidden=True)
        b = without.model.velocity(x, t, without.model.conditions(batch))
        assert torch.equal(a, b)
        assert torch.allclose(torch.sigmoid(with_head.model.memory.progress_logit(hidden)), torch.full((4,), 0.5))


def test_progress_head_learns_and_is_evaluated(tmp_path):
    cfg = _progress_cfg(tmp_path, weight=1.0, epochs=6)
    cfg.schedule.eval_every = 24
    cfg.schedule.probe_every = 0
    trainer = Trainer(ProgressBackend(), cfg, tmp_path / "run", log=lambda m: None)
    assert trainer.run()["complete"]
    metrics = [json.loads(x) for x in (tmp_path / "run" / "metrics.jsonl").read_text().splitlines()]
    assert all("progress" in m and "progress_abs_err" in m for m in metrics)
    first = sum(m["progress"] for m in metrics[:4]) / 4
    last = sum(m["progress"] for m in metrics[-4:]) / 4
    assert last < first, (first, last)
    ev = json.loads((tmp_path / "run" / "eval" / "update_000048.json").read_text())["overall"]
    assert {"on/progress_abs_err", "null/progress_abs_err", "off/progress_abs_err"} <= set(ev)


def test_init_memory_without_the_head_starts_it_at_zero(tmp_path):
    plain = Trainer(TinyBackend(), _cfg(tmp_path / "a"), tmp_path / "a" / "run", log=lambda m: None)
    plain.step()
    ckpt = plain.save()
    cfg = _progress_cfg(tmp_path / "b")
    cfg.init_memory = str(ckpt)
    logs = []
    second = Trainer(ProgressBackend(), cfg, tmp_path / "b" / "run", log=logs.append)
    assert second.run(dry_run=1)["complete"]
    assert any("progress head not in" in m for m in logs)
    assert TrainConfig.from_dict(cfg.to_dict()).v2.memory.progress_head
