"""Memory-aware one-step distillation (plan v8 D2, after RealtimeWAM's teacher-anchored term).

Teacher = a trained memory_v2 checkpoint (memory_v2 modules + ActionDiT); student = the same architecture, by
default started from the teacher. Per training sample, with the SAME batch, history, memory dropout and noise eps:

    a0_T  = teacher's K-step Euler rollout from eps (memory on, or the null branch for dropped samples)
    a_tau = (1 - tau) a0_T + tau eps,    target u = eps - a0_T          (the straight teacher-coupled path)
    L     = mean_b w(tau_b) ||v_S(a_tau, tau) - u||^2  +  endpoint_weight ||v_S(eps, 1) - u||^2

The tau = 1 term is the one-step decoder a0 = eps - v_S(eps, 1). The objective's tau sampling / weighting /
memory dropout are reused unchanged (ObjectiveConfig), so only the target differs from compute_loss.

The video branch is frozen and shared: the current-frame prefill (and, for kv_replay, the history prefill) is
computed once per micro-batch and given to both teacher and student. The teacher's weights are applied to the same
module tree by in-place swapping (`swapped`) and restored afterwards: bf16 ActionDiT parameters are restored from
their fp32 optimizer masters (bit-exact: the module copy is the master rounded), everything else from a clone. This
works whatever the backbone code holds references to, as long as it reads the same Parameter objects.

EMA (`EMA`): an fp32 CPU copy of the student's trainable weights; checkpoints store it as "memory" / "action" (what
evaluation and the closed loop load) and the raw weights under "raw" (what resume loads).
"""
from __future__ import annotations

import contextlib
from typing import Dict, Iterable, Optional, Tuple

import torch

from .config import GuidanceConfig, ObjectiveConfig
from .objectives import loss_weight, masked_mse, sample_tau


# ----------------------------------------------------------------------------- weight sets
def action_module_parameters(model) -> Dict[str, torch.nn.Parameter]:
    """ActionDiT parameters by the names checkpoints use (state["action"]), or {} for a backbone without one."""
    ab = getattr(model.backbone, "ab", None)
    if ab is None:
        return {}
    return dict(ab.backbone.mot.mixtures["action"].named_parameters())


def full_names(model) -> Dict[int, str]:
    return {id(p): n for n, p in model.named_parameters()}


def trainable_weight_names(model) -> Tuple[Dict[str, str], Dict[str, str]]:
    """(memory, action): checkpoint key -> full parameter name in model.named_parameters()."""
    names = full_names(model)
    memory = {n: names[id(p)] for n, p in model.memory.named_parameters()}
    action = {n: names[id(p)] for n, p in action_module_parameters(model).items() if id(p) in names}
    return memory, action


@contextlib.contextmanager
def swapped(model, weights: Dict[str, torch.Tensor], restore: Optional[Dict[str, torch.Tensor]] = None):
    """Temporarily copy `weights` (full parameter name -> tensor) into the model's parameters, in place.

    restore[name] (optional): the tensor the parameter is restored from afterwards (fp32 masters of bf16 weights;
    copy_ rounds them exactly as the optimizer step does). Parameters without one are cloned first."""
    params = dict(model.named_parameters())
    missing = [n for n in weights if n not in params]
    if missing:
        raise KeyError(f"swapped: unknown parameters {missing[:3]}")
    restore = restore or {}
    backup = {n: params[n].detach().clone() for n in weights if n not in restore}
    with torch.no_grad():
        for n, v in weights.items():
            params[n].copy_(v)
    try:
        yield
    finally:
        with torch.no_grad():
            for n in weights:
                params[n].copy_(restore[n] if n in restore else backup[n])


class Teacher:
    """The teacher's trainable weights (memory_v2 + ActionDiT) as full-name tensors on the model's device."""

    def __init__(self, model, state: dict, source: str = ""):
        memory_names, action_names = trainable_weight_names(model)
        params = dict(model.named_parameters())
        self.source = source
        self.update = state.get("update")
        self.weights: Dict[str, torch.Tensor] = {}
        own = model.memory.state_dict()
        if set(state["memory"]) != set(own):
            raise ValueError(f"Teacher memory keys differ from the student's ({len(state['memory'])} vs {len(own)}); "
                             "the teacher must have the same memory_v2 architecture.")
        for key, value in state["memory"].items():
            if key in memory_names:
                p = params[memory_names[key]]
                self.weights[memory_names[key]] = value.detach().to(p.device, p.dtype).clone()
            elif not torch.equal(value.cpu(), own[key].cpu()):
                raise ValueError(f"Teacher buffer {key} differs from the student's; buffers are not swapped.")
        action = state.get("action")
        self.has_action = action is not None
        if action is not None:
            all_action = action_module_parameters(model)
            if set(action) != set(all_action):
                raise ValueError("Teacher ActionDiT keys differ from the student's.")
            names = full_names(model)
            for key, value in action.items():
                p = all_action[key]
                self.weights[names[id(p)]] = value.detach().to(p.device, p.dtype).clone()
        self.memory_names, self.action_names = memory_names, action_names

    def applied(self, model, restore: Optional[Dict[str, torch.Tensor]] = None):
        return swapped(model, self.weights, restore)

    def numel(self) -> int:
        return sum(v.numel() for v in self.weights.values())

    def load_into_student(self, model, masters: Dict[str, torch.Tensor]) -> int:
        """Start the student as the teacher: module parameters and their fp32 masters (keyed by checkpoint name)."""
        params = dict(model.named_parameters())
        inverse = {full: key for key, full in self.action_names.items()}
        with torch.no_grad():
            for full, value in self.weights.items():
                params[full].copy_(value)
                key = inverse.get(full)
                if key is not None and key in masters:
                    masters[key].copy_(value.float())
        return len(self.weights)


def load_teacher(model, path: str) -> Teacher:
    state = torch.load(path, map_location="cpu", weights_only=False)
    teacher = Teacher(model, state, source=str(path))
    del state
    return teacher


# ----------------------------------------------------------------------------- the loss
def distill_loss(model, teacher: Teacher, batch: Dict[str, torch.Tensor], cfg: ObjectiveConfig,
                 guidance: GuidanceConfig, generator: Optional[torch.Generator] = None,
                 restore: Optional[Dict[str, torch.Tensor]] = None, drop: Optional[torch.Tensor] = None,
                 gt_weight: float = 0.0) -> Dict[str, torch.Tensor]:
    """Teacher-anchored one-step distillation for one micro-batch (keys as compute_loss, plus teacher_gt)."""
    actions = batch["actions"].float()
    valid = batch["action_valid"].bool()
    b = actions.shape[0]
    device = actions.device
    noise = torch.randn(actions.shape, generator=generator, dtype=torch.float32).to(device)
    tau = sample_tau(b, cfg, generator).to(device=device, dtype=torch.float32)
    if drop is None:
        drop = torch.rand(b, generator=generator) < cfg.memory_dropout
    drop = drop.to(device)
    shared = model.shared_encoding(batch)                       # frozen video branch, once for both
    with torch.no_grad(), teacher.applied(model, restore):
        was_training = model.training
        model.eval()
        teacher_conditions = model.conditions(batch, drop=drop, shared=shared)
        endpoint, _ = model.sample(teacher_conditions, noise, guidance, memory_mode="on")
        model.train(was_training)
        del teacher_conditions
    endpoint = endpoint.detach().float()
    conditions = model.conditions(batch, drop=drop, shared=shared)
    noisy = (1.0 - tau)[:, None, None] * endpoint + tau[:, None, None] * noise
    target = noise - endpoint
    prediction = model.velocity(noisy, 1000.0 * tau, conditions)
    error = masked_mse(prediction, target, valid)
    weight = loss_weight(tau, cfg).to(device)
    fm = (weight * error).mean()
    teacher_gt = masked_mse(endpoint, actions, valid).detach()
    out = {"fm": fm, "fm_unweighted": error.detach(), "tau": tau.detach(), "memory_dropped": drop.detach(),
           "teacher_gt": teacher_gt.mean()}
    loss = fm
    if cfg.endpoint_weight > 0:
        one_step = model.velocity(noise, torch.full((b,), 1000.0, device=device), conditions)
        endpoint_error = masked_mse(one_step, target, valid).mean()
        out["endpoint"] = endpoint_error
        loss = loss + cfg.endpoint_weight * endpoint_error
    if gt_weight > 0:                                           # optional anchor to the demonstrations
        gt_noisy = (1.0 - tau)[:, None, None] * actions + tau[:, None, None] * noise
        gt = masked_mse(model.velocity(gt_noisy, 1000.0 * tau, conditions), noise - actions, valid)
        out["gt_fm"] = (weight * gt).mean()
        loss = loss + gt_weight * out["gt_fm"]
    out["loss"] = loss
    return out


@torch.no_grad()
def teacher_rollout(model, teacher: Teacher, batch, noise, guidance: GuidanceConfig,
                    restore: Optional[Dict[str, torch.Tensor]] = None) -> torch.Tensor:
    """The teacher's endpoint on a fixed batch / noise (memory on), for the isolation check."""
    shared = model.shared_encoding(batch)
    with teacher.applied(model, restore):
        was_training = model.training
        model.eval()
        conditions = model.conditions(batch, shared=shared)
        out, _ = model.sample(conditions, noise, guidance, memory_mode="on")
        model.train(was_training)
    return out.float()


# ----------------------------------------------------------------------------- EMA
class EMA:
    """fp32 CPU exponential moving average of the student's trainable weights, keyed like checkpoints:
    ("memory", key) and ("action", key)."""

    def __init__(self, decay: float, every: int = 1):
        if not 0.0 < decay < 1.0 or every < 1:
            raise ValueError("EMA decay must be in (0, 1) and every >= 1.")
        self.decay, self.every = float(decay), int(every)
        self.memory: Dict[str, torch.Tensor] = {}
        self.action: Dict[str, torch.Tensor] = {}

    @staticmethod
    def _cpu(t: torch.Tensor) -> torch.Tensor:
        return t.detach().to("cpu", torch.float32, copy=True)

    def reset(self, memory: Dict[str, torch.Tensor], action: Dict[str, torch.Tensor]) -> None:
        self.memory = {k: self._cpu(v) for k, v in memory.items()}
        self.action = {k: self._cpu(v) for k, v in action.items()}

    def update(self, memory: Dict[str, torch.Tensor], action: Dict[str, torch.Tensor], step: int) -> bool:
        if step % self.every:
            return False
        d = self.decay ** self.every
        for store, src in ((self.memory, memory), (self.action, action)):
            for k, v in src.items():
                store[k].mul_(d).add_(v.detach().to("cpu", torch.float32), alpha=1.0 - d)
        return True

    def weights(self, memory_names: Dict[str, str], action_names: Dict[str, str]) -> Dict[str, torch.Tensor]:
        """Full-name tensors for `swapped` (memory parameters only; buffers are not averaged)."""
        out = {memory_names[k]: v for k, v in self.memory.items() if k in memory_names}
        out.update({action_names[k]: v for k, v in self.action.items() if k in action_names})
        return out


def memory_parameters_by_key(model) -> Dict[str, torch.Tensor]:
    return {n: p for n, p in model.memory.named_parameters()}


def iter_pairs(a: Dict[str, torch.Tensor], b: Dict[str, torch.Tensor]) -> Iterable[Tuple[str, torch.Tensor, torch.Tensor]]:
    for k in a:
        yield k, a[k], b[k]
