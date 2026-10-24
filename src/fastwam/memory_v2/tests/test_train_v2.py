"""CPU tests of the train_v2 loop on the tiny backbone (no dense host needed)."""
import json
import types

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


def test_eval_modes_survive_yaml(tmp_path):
    from pathlib import Path
    yaml = pytest.importorskip("yaml")
    from fastwam.memory_v2.train_v2 import load_config
    cfg = TrainConfig.from_dict({"eval": {"modes": [True, False, None]}})
    assert cfg.eval.modes == ("on", "off", "null")
    with pytest.raises(ValueError):
        TrainConfig.from_dict({"eval": {"modes": ["sometimes"]}})
    shipped = Path(__file__).resolve().parents[4] / "configs" / "memory_v2" / "train_v2_A.yaml"
    assert load_config(shipped).eval.modes == ("on", "off", "null")
    raw = tmp_path / "c.yaml"
    raw.write_text(yaml.safe_dump({"eval": {"modes": ["on"]}}).replace("'on'", "on"))
    assert load_config(raw).eval.modes == ("on",)


def test_counterfactual_pairs_train_and_pr(tmp_path):
    import json as _json
    pairs = [{"task": "t", "query": {"episode_id": 0, "anchor": 20}, "donor": {"episode_id": 1, "anchor": 24},
              "present_rms": 0.01, "delta_norm": 3.0, "visual_distance": 0.0},
             {"task": "t", "query": {"episode_id": 2, "anchor": 30}, "donor": {"episode_id": 0, "anchor": 28},
              "present_rms": 0.02, "delta_norm": 5.0, "visual_distance": 0.5}]
    path = tmp_path / "pairs.json"
    path.write_text(_json.dumps({"train": pairs, "val": pairs}))
    from fastwam.memory_v2.train_v2 import PairsConfig, evaluate_pairs
    cfg = _cfg(tmp_path)
    cfg.pairs = PairsConfig(file=str(path), weight=1.0, per_update=2, max_visual_distance=0.4)
    assert "pairs" in cfg.to_dict() and "pairs" not in _cfg(tmp_path).to_dict()
    backend = TinyBackend()
    trainer = Trainer(backend, cfg, tmp_path / "run", log=lambda m: None)
    assert len(trainer.pairs) == 1                              # visual filter
    record = trainer.step()
    assert record["pair_samples"] == 2 and record["pair_loss"] > 0
    own, swapped = backend.pair_batches(pairs, reverse=False)
    assert torch.equal(swapped["latent"], own["latent"])         # current frame of the query
    assert torch.equal(swapped["current_ids"], torch.tensor([24, 28]))
    result = evaluate_pairs(backend, pairs, cfg, modes=("on", "null"), batch_size=2, log=lambda m: None)
    assert result["summary"]["all"]["n"] == 4
    # The null branch never sees history: swapping it changes nothing.
    assert all(c["null/response"] < 1e-6 for c in result["cases"])


def test_pr_swap_content_and_clock(tmp_path):
    pairs = [{"task": "t", "query": {"episode_id": 0, "anchor": 20}, "donor": {"episode_id": 1, "anchor": 24},
              "present_rms": 0.01, "delta_norm": 3.0, "visual_distance": 0.0},
             {"task": "t", "query": {"episode_id": 2, "anchor": 30}, "donor": {"episode_id": 0, "anchor": 28},
              "present_rms": 0.02, "delta_norm": 5.0, "visual_distance": 0.0}]
    from fastwam.memory_v2.train_v2 import evaluate_pairs
    backend = TinyBackend()
    own, donor = backend.batch([p["query"] for p in pairs]), backend.batch([p["donor"] for p in pairs])

    def ages(b):
        return torch.where(b["history_valid"], b["current_ids"][:, None] - b["frame_ids"], torch.full_like(b["frame_ids"], -1))

    _, content = backend.pair_batches(pairs, swap="content")
    assert torch.equal(content["current_ids"], own["current_ids"])            # own clock
    assert torch.equal(content["history"], donor["history"])                   # donor content
    keep = content["history_valid"]
    assert torch.equal(ages(content)[keep], ages(donor)[keep])                 # donor ages kept
    assert torch.equal(content["actions"], donor["actions"])
    _, clock = backend.pair_batches(pairs, swap="clock")
    assert torch.equal(clock["current_ids"], donor["current_ids"])             # donor clock
    assert torch.equal(clock["history"], own["history"])                       # own content
    assert torch.equal(ages(clock)[clock["history_valid"]], ages(own)[clock["history_valid"]])
    assert not bool(((clock["frame_ids"] > clock["current_ids"][:, None]) & clock["history_valid"]).any())
    cfg = _cfg(tmp_path)
    for swap in ("content", "clock"):
        result = evaluate_pairs(backend, pairs, cfg, modes=("on", "null"), batch_size=2, log=lambda m: None, swap=swap)
        assert result["swap"] == swap and result["summary"]["all"]["n"] == 4
        assert all(c["null/response"] < 1e-6 and c["history_dropped"] >= 0 for c in result["cases"])


class TrainableTinyBackend(TinyBackend):
    """TinyBackbone whose 'action' part (head + mlps) is trainable, stored in bfloat16 like the released MoT."""

    def __init__(self, dtype=torch.bfloat16):
        super().__init__()
        bb = self.model.backbone
        self.action_modules = [bb.head] + list(bb.mlp)
        for m in self.action_modules:
            m.to(dtype)
            m.requires_grad_(True)
            m.register_forward_pre_hook(lambda mod, args: (args[0].to(mod.weight.dtype),))
            m.register_forward_hook(lambda mod, args, out: out.float())
        bb.named_action_parameters = lambda: [(f"m{i}.{n}", p) for i, m in enumerate(self.action_modules)
                                              for n, p in m.named_parameters()]
        self.model.backbone.ab = types.SimpleNamespace(backbone=types.SimpleNamespace(mot=types.SimpleNamespace(
            mixtures={"action": types.SimpleNamespace(named_parameters=bb.named_action_parameters)})))


def _cfg_action(tmp_path, lr_action=1e-3, **extra):
    cfg = _cfg(tmp_path, **extra)
    cfg.optim = OptimConfig(lr_memory=1e-3, lr_action=lr_action, warmup_fraction=0.2)
    return cfg


def test_action_training_uses_fp32_masters_and_moves_bf16_weights(tmp_path):
    backend = TrainableTinyBackend(torch.bfloat16)
    cfg = _cfg_action(tmp_path)
    logs = []
    trainer = Trainer(backend, cfg, tmp_path / "run", log=logs.append)
    assert len(trainer.master) == len(backend.model.backbone.named_action_parameters()) > 0
    assert any("fp32 masters" in m for m in logs)
    head_before = backend.model.backbone.head.weight.detach().clone()
    for _ in range(3):
        trainer.step()
    head = backend.model.backbone.head.weight
    assert head.dtype == torch.bfloat16 and not torch.equal(head, head_before)
    master = trainer.master_names["m0.weight"]
    assert master.dtype == torch.float32 and torch.equal(master.to(torch.bfloat16), head)   # module = rounded master
    # Checkpoint holds the fp32 masters; a fresh trainer resumes them exactly.
    trainer.save()
    state = torch.load(trainer.checkpoint_dir() / "update_000003.pt", map_location="cpu", weights_only=False)
    assert state["action"]["m0.weight"].dtype == torch.float32
    again = Trainer(TrainableTinyBackend(torch.bfloat16), cfg, tmp_path / "run", log=lambda m: None)
    assert again.resume() and torch.equal(again.master_names["m0.weight"], master)
    assert torch.equal(again.model.backbone.head.weight, head)


def test_fp32_action_params_need_no_masters(tmp_path):
    backend = TrainableTinyBackend(torch.float32)
    trainer = Trainer(backend, _cfg_action(tmp_path), tmp_path / "run", log=lambda m: None)
    assert trainer.master == []
    before = backend.model.backbone.head.weight.detach().clone()
    trainer.step()
    assert not torch.equal(before, backend.model.backbone.head.weight)


def test_init_memory_stage_two(tmp_path):
    # Stage 1: memory only. Stage 2: a new run starts from that memory (parity no longer zero-init).
    cfg1 = _cfg(tmp_path / "s1")
    first = Trainer(TinyBackend(), cfg1, tmp_path / "s1" / "run", log=lambda m: None)
    first.run()
    ckpt = sorted((tmp_path / "s1" / "run" / "checkpoints").glob("update_*.pt"))[-1]
    cfg2 = _cfg_action(tmp_path / "s2")
    cfg2.init_memory = str(ckpt)
    assert TrainConfig.from_dict(cfg2.to_dict()).init_memory == str(ckpt)
    backend = TrainableTinyBackend(torch.bfloat16)
    logs = []
    second = Trainer(backend, cfg2, tmp_path / "s2" / "run", log=logs.append)
    result = second.run()
    assert result["complete"] and any("memory-first stage 2" in m for m in logs)
    parity = json.loads((tmp_path / "s2" / "run" / "INIT_PARITY.json").read_text())
    assert parity["exact"] and parity["zero_init_required"] is False
    assert parity["max_abs"]["on@0.3"] > 0                                   # memory was not zero-initialised
    loaded = torch.load(ckpt, map_location="cpu", weights_only=False)["memory"]
    first_record = json.loads((tmp_path / "s2" / "run" / "metrics.jsonl").read_text().splitlines()[0])
    assert first_record["update"] == 1
    assert set(loaded) == set(second.model.memory.state_dict())


def test_set_override_parses_scientific_notation(tmp_path):
    from fastwam.memory_v2.train_v2 import load_config, parse_override
    assert parse_override("1e-5") == 1e-5 and parse_override("3e-05") == 3e-5 and parse_override("0.5") == 0.5
    assert parse_override("16") == 16 and parse_override("outputs/x.pt") == "outputs/x.pt" and parse_override("null") is None
    assert parse_override('["on","off"]') == ["on", "off"]
    yaml = pytest.importorskip("yaml")
    path = tmp_path / "c.yaml"
    path.write_text(yaml.safe_dump({"optim": {"lr_memory": "1e-4"}}))
    cfg = load_config(path, ["optim.lr_action=2e-5", "schedule.epochs=3", "init_memory=a/b.pt"])
    assert cfg.optim.lr_action == 2e-5 and cfg.optim.lr_memory == 1e-4 and cfg.schedule.epochs == 3
    assert cfg.init_memory == "a/b.pt"
