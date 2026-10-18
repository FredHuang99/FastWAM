"""CPU tests of the train_v2 loop on the tiny backbone (no dense host needed)."""
import json

import pytest

torch = pytest.importorskip("torch")

from fastwam.memory_v2.config import HistoryPolicyConfig, MemoryV2Config, V2Config  # noqa: E402
from fastwam.memory_v2.history import collate_history, select_history  # noqa: E402
from fastwam.memory_v2.model import MemoryV2Model  # noqa: E402
from fastwam.memory_v2.tests.helpers import TINY, TinyBackbone  # noqa: E402
from fastwam.memory_v2.train_v2 import (Backend, EvalConfig, GuardConfig, OptimConfig, ScheduleConfig,  # noqa: E402
                                        TrainConfig, Trainer, epoch_rows, evaluate, lr_at)

POLICY = HistoryPolicyConfig(anchor_frames=1, landmark_stride=8, recent_frames=1, recent_stride=4, max_frames=6)


class TinyBackend(Backend):
    def __init__(self, episodes=4, length=40):
        torch.manual_seed(0)
        self.device = torch.device("cpu")
        self.cfg_memory = MemoryV2Config(**TINY)
        self.model = MemoryV2Model(TinyBackbone(), self.cfg_memory).float()
        g = torch.Generator().manual_seed(0)
        tokens = TINY["grid"][0] * TINY["grid"][1]
        self.features = torch.randn(episodes, length, tokens, TINY["video_dim"], generator=g)
        self.latent = torch.randn(episodes, length, 6, 16, generator=g)
        self.context = torch.randn(episodes, 24, generator=g)
        self.actions = torch.randn(episodes, length, 5, generator=g)
        self.length = length
        self.episodes = episodes

    def train_rows(self):
        return [{"episode_id": e, "anchor": a} for e in range(self.episodes - 1) for a in range(self.length)]

    def batch(self, rows):
        selections, feats, latent, context, actions, valid = [], [], [], [], [], []
        for row in rows:
            e, a = row["episode_id"], row["anchor"]
            s = select_history(range(a + 1), a, POLICY)
            selections.append(s)
            feats.append([self.features[e, i] for i in s.ids])
            index = torch.clamp(torch.arange(a, a + 8), max=self.length - 1)
            actions.append(self.actions[e, index])
            valid.append(torch.arange(a, a + 8) < self.length)
            latent.append(self.latent[e, a])
            context.append(self.context[e])
        history = collate_history(feats, selections, TINY["grid"][0] * TINY["grid"][1], TINY["video_dim"], dtype=torch.float32)
        return {"latent": torch.stack(latent), "context": torch.stack(context), "actions": torch.stack(actions),
                "action_valid": torch.stack(valid), **history}

    def probe_rows(self):
        return [{"episode_id": self.episodes - 1, "anchor": 20}, {"episode_id": self.episodes - 1, "anchor": 30}]

    def eval_rows(self, limit):
        rows = [{"id": f"{self.episodes - 1}:{a}", "episode_id": self.episodes - 1, "anchor": a} for a in (0, 9, 18, 27, 36)]
        return rows[:limit] if limit else rows

    def window_case(self, row, sample, b, batch):
        err = (sample.float() - batch["actions"][b].float()).square()[batch["action_valid"][b]]
        return {"arm_rmse_rad": float(err.mean().sqrt())}

    def noise(self, row, shape):
        return torch.randn(shape, generator=torch.Generator().manual_seed(int(row["anchor"]) + 1))

    def describe(self):
        return {"kind": "tiny"}


def _cfg(tmp_path, **schedule):
    cfg = TrainConfig(output=str(tmp_path / "run"))
    cfg.v2 = V2Config.from_dict({"memory": TINY, "history": POLICY.__dict__,
                                 "guidance": {"steps": 3}})
    cfg.optim = OptimConfig(lr_memory=1e-3, warmup_fraction=0.2)
    cfg.schedule = ScheduleConfig(**{"epochs": 1, "global_batch": 16, "micro_batch": 4, "save_every": 3,
                                     "probe_every": 2, "eval_every": 4, "keep_last": 1, **schedule})
    cfg.eval = EvalConfig(windows=0, batch=2, modes=("on", "off", "null"), guidance_scales=(1.0, 2.0), fm_taus=(0.5, 1.0))
    cfg.guard = GuardConfig(start_update=10 ** 6)
    return cfg


def test_lr_schedule_and_permutation():
    assert lr_at(1, 100, 1e-4, 0.05, 0.01) == pytest.approx(2e-5)
    assert lr_at(5, 100, 1e-4, 0.05, 0.01) == pytest.approx(1e-4)
    assert lr_at(100, 100, 1e-4, 0.05, 0.01) == pytest.approx(1e-6)
    assert lr_at(10, 100, 0.0, 0.05, 0.01) == 0.0
    rows = [{"i": i} for i in range(50)]
    assert epoch_rows(rows, 1, 3) == epoch_rows(rows, 1, 3)
    assert epoch_rows(rows, 1, 3) != epoch_rows(rows, 2, 3)


def test_config_roundtrip_and_validation(tmp_path):
    cfg = _cfg(tmp_path)
    again = TrainConfig.from_dict(json.loads(json.dumps(cfg.to_dict())))
    assert again.to_dict() == cfg.to_dict()
    bad = cfg.to_dict()
    bad["schedule"]["micro_batch"] = 5
    with pytest.raises(ValueError):
        TrainConfig.from_dict(bad)
    with pytest.raises(ValueError):
        TrainConfig.from_dict({**cfg.to_dict(), "typo": 1})


def test_train_eval_checkpoint_resume(tmp_path):
    backend = TinyBackend()
    cfg = _cfg(tmp_path)
    trainer = Trainer(backend, cfg, tmp_path / "run", log=lambda m: None)
    before = {k: v.clone() for k, v in backend.model.memory.state_dict().items()}
    backbone_before = {k: v.clone() for k, v in backend.model.backbone.state_dict().items()}
    result = trainer.run()
    assert result["complete"] and trainer.update == trainer.total == 8   # 3 episodes x 40 / 16 = 7.5 -> 8
    run = tmp_path / "run"
    parity = json.loads((run / "INIT_PARITY.json").read_text())
    assert parity["exact"]
    metrics = [json.loads(line) for line in (run / "metrics.jsonl").read_text().splitlines()]
    assert [m["update"] for m in metrics] == list(range(1, 9))
    assert metrics[-1]["samples"] == 3 * 40 - 7 * 16                      # partial last update
    assert all(m["fm"] > 0 for m in metrics)
    assert (run / "probes.jsonl").exists() and (run / "eval" / "update_000004.json").exists()
    ev = json.loads((run / "eval" / "update_000008.json").read_text())
    assert {"on/arm_rmse_rad", "off/arm_rmse_rad", "null/arm_rmse_rad", "on_cfg2/arm_rmse_rad",
            "on/fm_tau1", "off/fm_tau0.5"} <= set(ev["overall"])
    # Memory changed; the frozen backbone did not.
    after = backend.model.memory.state_dict()
    assert any(not torch.equal(before[k], after[k]) for k in before)
    assert all(torch.equal(backbone_before[k], v) for k, v in backend.model.backbone.state_dict().items())
    # Off-mode outputs are the frozen backbone, so they did not move with training.
    ev0 = json.loads((run / "eval" / "update_000000.json").read_text())
    assert ev0["overall"]["off/arm_rmse_rad"] == pytest.approx(ev["overall"]["off/arm_rmse_rad"], abs=1e-6)
    assert ev0["overall"]["on/arm_rmse_rad"] == pytest.approx(ev0["overall"]["off/arm_rmse_rad"], abs=1e-6)
    # Resume: a new trainer on the same output restores the last checkpoint exactly.
    backend2 = TinyBackend()
    trainer2 = Trainer(backend2, cfg, run, log=lambda m: None)
    assert trainer2.resume() and trainer2.update == 8
    for k, v in backend.model.memory.state_dict().items():
        assert torch.equal(v, backend2.model.memory.state_dict()[k])
    assert (run / "COMPLETE.json").exists()


def test_resume_continues_identically(tmp_path):
    cfg_a = _cfg(tmp_path / "a")
    full = Trainer(TinyBackend(), cfg_a, tmp_path / "a" / "run", log=lambda m: None)
    full.run()
    cfg_b = _cfg(tmp_path / "b")
    part = Trainer(TinyBackend(), cfg_b, tmp_path / "b" / "run", log=lambda m: None)
    (tmp_path / "b" / "run").mkdir(parents=True)
    # Run 3 updates, save, then continue in a fresh trainer.
    for _ in range(3):
        part.step()
    part.save()
    resumed = Trainer(TinyBackend(), cfg_b, tmp_path / "b" / "run", log=lambda m: None)
    assert resumed.resume() and resumed.update == 3
    while resumed.update < 8:
        resumed.step()
    for k, v in full.model.memory.state_dict().items():
        assert torch.allclose(v, resumed.model.memory.state_dict()[k], atol=1e-6), k


def test_loss_guard_trips(tmp_path):
    cfg = _cfg(tmp_path)
    cfg.guard = GuardConfig(loss_factor=2.0, loss_window=4, loss_baseline_updates=4, start_update=0)
    trainer = Trainer(TinyBackend(), cfg, tmp_path / "run", log=lambda m: None)
    trainer.loss_history = [0.01] * 4 + [0.05] * 4
    trainer.update = 8
    trip = trainer.loss_guard()
    assert trip and trip["recent_median"] == pytest.approx(0.05)
    trainer.loss_history = [0.01] * 8
    assert trainer.loss_guard() is None
    trainer.loss_history.append(float("nan"))
    assert trainer.loss_guard()["reason"].startswith("non-finite")


def test_eval_guard(tmp_path):
    cfg = _cfg(tmp_path)
    cfg.guard = GuardConfig(eval_regression=0.1, start_update=0)
    trainer = Trainer(TinyBackend(), cfg, tmp_path / "run", log=lambda m: None)
    assert trainer.eval_guard({"overall": {"on/arm_rmse_rad": 1.2, "off/arm_rmse_rad": 1.0}})
    assert trainer.eval_guard({"overall": {"on/arm_rmse_rad": 1.05, "off/arm_rmse_rad": 1.0}}) is None


def test_evaluate_is_deterministic(tmp_path):
    backend = TinyBackend()
    cfg = _cfg(tmp_path)
    a = evaluate(backend, backend.eval_rows(0), cfg, log=lambda m: None)
    b = evaluate(backend, backend.eval_rows(0), cfg, log=lambda m: None)
    assert a["overall"] == b["overall"] and a["windows"] == 5
