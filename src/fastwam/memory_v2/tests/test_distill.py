"""Plan v8 D2 (11-06): memory-aware one-step distillation on the tiny CPU backend.

Acceptance (a): the teacher endpoint computed by swapping the teacher's weights into the student's module tree is
bit-identical to model.sample on a separate model holding the teacher's weights, and the student is restored
exactly. Acceptance (b): a student started from the teacher lowers the distillation loss within 50 updates; checks,
EMA checkpoints and resume.
"""
import json

import pytest
import torch

from fastwam.memory_v2.config import GuidanceConfig, V2Config
from fastwam.memory_v2.distill import Teacher, distill_loss, swapped, teacher_rollout
from fastwam.memory_v2.tests.test_train_v2 import TINY, POLICY, TinyBackend, TrainableTinyBackend, _cfg_action
from fastwam.memory_v2.train_v2 import DistillConfig, EvalConfig, Trainer, TrainConfig

GUIDE = GuidanceConfig(steps=10, shift=1.0, scale=1.0, min_sigma=0.7)


def _teacher_checkpoint(tmp_path, updates=6):
    """A 'trained' tiny memory_v2 model: FM training of memory + ActionDiT for a few updates."""
    cfg = _cfg_action(tmp_path / "teacher")
    trainer = Trainer(TrainableTinyBackend(torch.bfloat16), cfg, tmp_path / "teacher" / "run", log=lambda m: None)
    for _ in range(updates):
        trainer.step()
    return trainer.save(), trainer


def _distill_cfg(tmp_path, teacher, **distill):
    cfg = _cfg_action(tmp_path / "student")
    cfg.distill = DistillConfig(teacher=str(teacher), **distill)
    cfg.eval = EvalConfig(windows=0, batch=2, modes=("on", "null"), guidance_scales=(1.0,), fm_taus=(1.0,), steps=(1,))
    return cfg


def test_teacher_swap_equals_a_separate_teacher_model_and_restores_the_student(tmp_path):
    ckpt, trained = _teacher_checkpoint(tmp_path)
    state = torch.load(ckpt, map_location="cpu", weights_only=False)
    student = Trainer(TrainableTinyBackend(torch.bfloat16), _cfg_action(tmp_path / "s"), tmp_path / "s" / "run",
                      log=lambda m: None)
    model = student.model
    teacher = Teacher(model, state)
    assert teacher.has_action and teacher.numel() > 0
    batch = student.backend.batch(student.backend.probe_rows())
    noise = torch.randn(batch["actions"].shape, generator=torch.Generator().manual_seed(5))
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    swapped_endpoint = teacher_rollout(model, teacher, batch, noise, GUIDE, student.restore)
    for n, p in model.named_parameters():                                  # student restored bit-exactly
        assert torch.equal(p, before[n]), n
    # a separate model that simply holds the teacher's weights (load as the online policy / evaluate do)
    other = TrainableTinyBackend(torch.bfloat16)
    other.model.memory.load_state_dict(state["memory"], strict=True)
    named = dict(other.model.backbone.named_action_parameters())
    with torch.no_grad():
        for n, v in state["action"].items():
            named[n].copy_(v.to(named[n].dtype))
    other.model.eval()
    reference, _ = other.model.sample(other.model.conditions(batch), noise, GUIDE)
    assert torch.equal(swapped_endpoint, reference.float())
    # and it is not the student's own rollout (the swap matters)
    model.eval()
    own, _ = model.sample(model.conditions(batch), noise, GUIDE)
    assert not torch.allclose(own.float(), reference.float())


def test_distill_loss_uses_teacher_targets_and_leaves_weights_untouched(tmp_path):
    ckpt, _ = _teacher_checkpoint(tmp_path)
    student = Trainer(TrainableTinyBackend(torch.bfloat16), _cfg_action(tmp_path / "s"), tmp_path / "s" / "run",
                      log=lambda m: None)
    model = student.model
    teacher = Teacher(model, torch.load(ckpt, map_location="cpu", weights_only=False))
    batch = student.backend.batch(student.backend.train_rows()[:4])
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    cfg = V2Config.from_dict({}).objective
    out = distill_loss(model, teacher, batch, cfg, GUIDE, torch.Generator().manual_seed(0), restore=student.restore)
    for n, p in model.named_parameters():
        assert torch.equal(p, before[n]), n
    assert {"loss", "fm", "endpoint", "teacher_gt", "tau", "memory_dropped"} <= set(out)
    out["loss"].backward()
    grads = [p.grad for _, p in model.backbone.named_action_parameters()]
    assert any(g is not None and float(g.abs().sum()) > 0 for g in grads)
    # same generator -> same noise / tau / drop draws as compute_loss (same order)
    from fastwam.memory_v2.objectives import compute_loss
    plain = compute_loss(model, batch, cfg, torch.Generator().manual_seed(0))
    assert torch.equal(plain["tau"], out["tau"]) and torch.equal(plain["memory_dropped"], out["memory_dropped"])


def test_student_from_teacher_lowers_the_distillation_loss_with_checks_ema_and_resume(tmp_path):
    ckpt, _ = _teacher_checkpoint(tmp_path)
    cfg = _distill_cfg(tmp_path, ckpt, ema=0.9, ema_every=1)
    cfg.schedule.epochs = 7                                   # 8 updates / epoch -> 56 updates
    cfg.schedule.eval_every = 28
    cfg.schedule.save_every = 28
    cfg.schedule.probe_every = 0
    logs = []
    trainer = Trainer(TrainableTinyBackend(torch.bfloat16), cfg, tmp_path / "student" / "run", log=logs.append)
    result = trainer.run()
    assert result["complete"] and trainer.update == 56
    run = tmp_path / "student" / "run"
    check = json.loads((run / "DISTILL_CHECK.json").read_text())
    assert check["start"]["ok"] and check["start"]["student_equals_teacher"]
    assert check["start"]["teacher_under_perturbed_student_exact"]
    assert check["after_first_update"]["ok"] and check["after_first_update"]["masters_consistent"]
    metrics = [json.loads(x) for x in (run / "metrics.jsonl").read_text().splitlines()]
    first = sum(m["fm"] for m in metrics[:5]) / 5
    last = sum(m["fm"] for m in metrics[-5:]) / 5
    assert last < first, (first, last)
    assert all("teacher_gt" in m for m in metrics)
    # evaluation reports the extra one-step decode; update 0 = the teacher (student started from it, EMA = student)
    ev0 = json.loads((run / "eval" / "update_000000.json").read_text())["overall"]
    assert {"on/arm_rmse_rad", "on_s1/arm_rmse_rad", "null_s1/arm_rmse_rad"} <= set(ev0)
    # checkpoint: memory / action = EMA (what eval and the closed loop load); raw = training weights (resume)
    state = torch.load(run / "checkpoints" / "update_000056.pt", map_location="cpu", weights_only=False)
    assert "raw" in state and state["ema"]["decay"] == 0.9
    key = next(iter(state["action"]))
    assert not torch.equal(state["action"][key], state["raw"]["action"][key])
    assert torch.equal(state["raw"]["action"][key], trainer.master_names[key].cpu())
    mkey = next(k for k in state["memory"] if k in dict(trainer.model.memory.named_parameters()))
    assert torch.equal(state["memory"][mkey], trainer.ema.memory[mkey])
    # resume restores the raw weights and the EMA
    again = Trainer(TrainableTinyBackend(torch.bfloat16), cfg, run, log=lambda m: None)
    assert again.resume()
    assert torch.equal(again.master_names[key], trainer.master_names[key])
    assert torch.equal(again.ema.action[key], trainer.ema.action[key])
    # config round trip; distill / eval.steps absent from ordinary configs
    assert TrainConfig.from_dict(cfg.to_dict()).distill.teacher == str(ckpt)
    plain = TrainConfig()
    assert "distill" not in plain.to_dict() and "steps" not in plain.to_dict()["eval"]
    assert any("[distill] student <- teacher" in m for m in logs)


def test_distill_config_validation():
    with pytest.raises(ValueError):
        TrainConfig.from_dict({"distill": {"teacher": "x.pt", "lambda_cd": 1.0}})
    with pytest.raises(ValueError):
        TrainConfig.from_dict({"distill": {"teacher": "x.pt", "ema": 1.5}})
    with pytest.raises(ValueError):
        TrainConfig.from_dict({"eval": {"steps": [0]}})
    cfg = TrainConfig.from_dict({"distill": {"teacher": "x.pt"}, "eval": {"steps": [1, 2]}})
    assert cfg.distill.enabled and cfg.eval.steps == (1, 2) and cfg.to_dict()["eval"]["steps"] == (1, 2)


def test_teacher_without_action_is_refused_when_the_student_trains_it(tmp_path):
    from fastwam.memory_v2.tests.test_train_v2 import _cfg
    cfg1 = _cfg(tmp_path / "m")                                  # memory-only teacher (action None in the checkpoint)
    first = Trainer(TinyBackend(), cfg1, tmp_path / "m" / "run", log=lambda m: None)
    first.step()
    ckpt = first.save()
    cfg = _distill_cfg(tmp_path, ckpt)
    with pytest.raises(ValueError):
        Trainer(TrainableTinyBackend(torch.bfloat16), cfg, tmp_path / "student" / "run", log=lambda m: None)


def test_swapped_restores_from_masters_and_clones(tmp_path):
    trainer = Trainer(TrainableTinyBackend(torch.bfloat16), _cfg_action(tmp_path), tmp_path / "run", log=lambda m: None)
    model = trainer.model
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    weights = {n: torch.zeros_like(p) for n, p in model.named_parameters() if n.startswith(("memory.", "backbone.head"))}
    with swapped(model, weights, trainer.restore):
        assert all(float(dict(model.named_parameters())[n].abs().sum()) == 0 for n in weights)
    for n, p in model.named_parameters():
        assert torch.equal(p, before[n]), n


def test_shared_encoding_reproduces_conditions_for_inject_and_kv_replay():
    from fastwam.memory_v2.tests.test_replay import _batch, _model, _open_gates
    model = _model()
    _open_gates(model)
    batch = _batch(model.cfg)
    x, t = torch.randn(3, 8, 5), torch.full((3,), 600.0)
    drop = torch.tensor([False, True, False])
    with torch.no_grad():
        shared = model.shared_encoding(batch)
        for d in (None, drop):
            a = model.velocity(x, t, model.conditions(batch, drop=d), "on")
            b = model.velocity(x, t, model.conditions(batch, drop=d, shared=shared), "on")
            assert torch.equal(a, b)
    inject = TinyBackend()
    batch = inject.batch(inject.train_rows()[:3])
    m = inject.model
    with torch.no_grad():
        shared = m.shared_encoding(batch)
        assert shared["replay"] is None
        a = m.velocity(x, t, m.conditions(batch, drop=drop), "on")
        b = m.velocity(x, t, m.conditions(batch, drop=drop, shared=shared), "on")
        assert torch.equal(a, b)
