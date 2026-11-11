"""Full fine-tuning trainer (single GPU; plan v10 A.3 / nodes N5, N7, N9, N11).

    PYTHONPATH=src python -m fastwam.fullft.train train  --config configs/fullft/ar_2task.yaml [--set k=v ...]
    PYTHONPATH=src python -m fastwam.fullft.train smoke  --config ... [--updates 200]     (N5: 2 episodes, overfit)
    PYTHONPATH=src python -m fastwam.fullft.train probe  --config ... [--micro 4 8 16]   (memory / speed per batch)
    PYTHONPATH=src python -m fastwam.fullft.train export --config ... --resume <resume.pt> --out <weights.pt>

Weights fp32, compute bf16 (autocast), AdamW (fused), linear warmup + cosine to min_lr_ratio, gradient clipping;
each joint layer recomputed in backward (model.checkpoint_layers). Every frame of every train episode is an anchor;
one "frame-epoch" = every anchor once. Writes its own log: <run>/logs/train_<time>.txt, metrics to
<run>/metrics.jsonl, the single resume checkpoint <run>/resume.pt (overwritten), bf16 exports
<run>/export_e<epoch>.pt (what the closed loop loads) and <run>/SUMMARY.json at the end (queue verdicts read it).
<run>/STOP: save the resume checkpoint and exit at the next update.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch

from .config import RunConfig, load
from .data import DenseEpisodes, Samples, collate, load_events, train_items, val_items, video_polarity
from .model import FullModel

BJ = timezone(timedelta(hours=8))
ARM = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]


class Logger:
    def __init__(self, run_dir: Path, tag: str):
        (run_dir / "logs").mkdir(parents=True, exist_ok=True)
        self.path = run_dir / "logs" / f"{tag}_{datetime.now(BJ):%Y%m%d_%H%M}.txt"
        self.file = self.path.open("a", encoding="utf-8")

    def __call__(self, *parts):
        line = f"[fullft] {datetime.now(BJ):%m-%d %H:%M:%S} " + " ".join(str(p) for p in parts)
        print(line, flush=True)
        self.file.write(line + "\n")
        self.file.flush()


def atomic_save(obj, path: Path) -> None:
    tmp = path.with_name(path.name + ".partial")
    torch.save(obj, tmp)
    os.replace(tmp, path)


def write_json(path: Path, value) -> None:
    tmp = path.with_name(path.name + ".partial")
    tmp.write_text(json.dumps(value, indent=1, allow_nan=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)


# ----------------------------------------------------------------------------- setup
def build(cfg: RunConfig, device: str, log, limit_episodes: int = 0):
    rule = cfg.rule
    episodes = DenseEpisodes(cfg.data.roots, cfg.data.tasks, capacity=cfg.data.episode_cache)
    if limit_episodes:
        keep = []
        for task in cfg.data.tasks:
            keep += [r["episode_id"] for r in episodes.split("train") if r["task"] == task][:limit_episodes]
        items = [(e, a) for e, a in train_items(episodes) if e in set(keep)]
        vitems = items[:: max(1, len(items) // 64)][:64]                 # smoke: measure on the SAME anchors
    else:
        items, vitems = train_items(episodes), val_items(episodes, cfg.data.val_anchors_per_task)
    events = load_events(cfg.data.events) if cfg.data.events else {}
    polarity = video_polarity(episodes)
    train = Samples(episodes, items, rule, events, polarity, augment=True, seed=cfg.seed)
    val = Samples(episodes, vitems, rule, events, polarity, augment=False, seed=cfg.seed)
    log(f"data: {len(items)} train anchors ({len({e for e, _ in items})} episodes), {len(vitems)} val anchors; "
        f"tasks {cfg.data.tasks}; video_valid polarity '{polarity}'; history {rule}")
    model = FullModel.from_release(cfg.model.architecture, cfg.model.base, rule.variant, rule.event_slots,
                                   cfg.model.video_shift, cfg.model.action_shift)
    model.set_trainable(cfg.model.train_video, cfg.model.lora_rank)
    model.checkpoint_layers = cfg.model.checkpoint_layers
    model.compute_dtype = torch.bfloat16
    model.to(device=device, dtype=torch.float32)
    n_all = sum(p.numel() for p in model.parameters())
    n_train = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log(f"model: {n_all / 1e9:.3f} B parameters, {n_train / 1e9:.3f} B trainable (train_video={cfg.model.train_video}); "
        f"base {cfg.model.base}")
    return model, train, val


def optimizer_for(model: FullModel, cfg: RunConfig):
    decay, no_decay, gates = [], [], []
    for name, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if name == "hist_gate":
            gates.append(p)
        elif p.ndim < 2:
            no_decay.append(p)
        else:
            decay.append(p)
    o = cfg.optim
    groups = [{"params": decay, "weight_decay": o.weight_decay, "lr_scale": 1.0},
              {"params": no_decay, "weight_decay": 0.0, "lr_scale": 1.0},
              {"params": gates, "weight_decay": 0.0, "lr_scale": o.gate_lr_scale}]
    groups = [g for g in groups if g["params"]]
    try:
        return torch.optim.AdamW(groups, lr=o.lr, betas=tuple(o.betas), fused=True)
    except (RuntimeError, TypeError):
        return torch.optim.AdamW(groups, lr=o.lr, betas=tuple(o.betas))


def lr_at(update: int, total: int, cfg: RunConfig) -> float:
    o = cfg.optim
    if update < o.warmup_steps:
        return o.lr * (update + 1) / o.warmup_steps
    progress = min(1.0, (update - o.warmup_steps) / max(1, total - o.warmup_steps))
    return o.lr * (o.min_lr_ratio + (1 - o.min_lr_ratio) * 0.5 * (1 + math.cos(math.pi * progress)))


def to_device(batch: dict, device) -> dict:
    return {k: v.to(device, non_blocking=True) for k, v in batch.items()}


# ----------------------------------------------------------------------------- evaluation
def fixed_noise(i: int, shapes, model: FullModel, device) -> dict:
    g = torch.Generator().manual_seed(1_000_003 * (i + 1))
    out = {"video": torch.randn(shapes["video"], generator=g), "action": torch.randn(shapes["action"], generator=g)}
    for key, sched in (("t_video", model.video_scheduler), ("t_action", model.action_scheduler)):
        u = torch.rand((1,), generator=g)
        out[key] = sched._phi(u, sched.shift) * float(sched.num_train_timesteps)
    out["sample"] = torch.randn(shapes["action"], generator=g)
    return {k: v.to(device) for k, v in out.items()}


@torch.no_grad()
def evaluate(model: FullModel, val: Samples, device, micro: int, sample_windows: int = 32, steps: int = 10,
             normaliser=None) -> Dict[str, float]:
    model.eval()
    vids, acts, arm, arm8 = [], [], [], []
    for start in range(0, len(val), micro):
        rows = [val[i] for i in range(start, min(len(val), start + micro))]
        batch = to_device(collate(rows), device)
        noises = [fixed_noise(start + j, {"video": tuple(r["video_latent"].shape), "action": tuple(r["actions"].shape)},
                              model, device) for j, r in enumerate(rows)]
        noise = {k: torch.stack([n[k] for n in noises]).squeeze(1) if k.startswith("t_") else
                 torch.stack([n[k] for n in noises]) for k in noises[0]}
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=batch["actions"].is_cuda, cache_enabled=False):
            history = model.history(batch)
            v, a = model.loss(batch, noise, history)
            vids += v.float().tolist()
            acts += a.float().tolist()
            if start < sample_windows:
                sample_batch = dict(batch, latent=batch["video_latent"][:, :, 0:1])
                pred = model.sample(sample_batch, noise["sample"], steps, history)
        if start < sample_windows and normaliser is not None:
            for j in range(len(rows)):
                p = normaliser.denormalize(pred[j].float().cpu())
                t = normaliser.denormalize(batch["actions"][j].float().cpu())
                valid = batch["action_valid"][j].cpu()
                err = (p - t)[valid][:, ARM]
                arm.append(float(err.square().mean().sqrt()))
                arm8.append(float(err[:8].square().mean().sqrt()))
    model.train()
    out = {"val_video": float(np.mean(vids)), "val_action": float(np.mean(acts))}
    if arm:
        out.update(val_arm_rmse=float(np.mean(arm)), val_arm_rmse_8=float(np.mean(arm8)))
    return out


def normaliser_for(cfg: RunConfig):
    try:
        from fastwam.memory_s1.common import ReleaseNormalizer
        return ReleaseNormalizer(cfg.model.stats)
    except Exception:                                      # noqa: BLE001 (metrics only)
        return None


# ----------------------------------------------------------------------------- training
def train(cfg: RunConfig, args, smoke: bool = False) -> dict:
    device = "cuda"
    run = cfg.run_dir
    run.mkdir(parents=True, exist_ok=True)
    log = Logger(run, "smoke" if smoke else "train")
    log(f"run {run}; config: {json.dumps(cfg.to_dict())}")
    torch.manual_seed(cfg.seed)
    random.seed(cfg.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    model, train_set, val_set = build(cfg, device, log, limit_episodes=1 if smoke else 0)
    write_json(run / "run_config.json", cfg.to_dict())
    opt = optimizer_for(model, cfg)
    s = cfg.schedule
    per_update = s.micro_batch * s.accumulation
    total = s.max_updates or math.ceil(s.frame_epochs * len(train_set) / per_update)
    if smoke:
        total = args.updates
        cfg.optim.warmup_steps = min(cfg.optim.warmup_steps, max(1, total // 10))
    state = {"update": 0, "epoch": 0, "position": 0}
    resume = run / "resume.pt"
    if resume.is_file() and not smoke:
        ck = torch.load(resume, map_location="cpu", weights_only=False)
        model.load_state_dict(ck["model"], strict=True)
        opt.load_state_dict(ck["optimizer"])
        state = ck["state"]
        log(f"resumed from {resume}: update {state['update']}, epoch {state['epoch']}, position {state['position']}")
        del ck
    normaliser = normaliser_for(cfg)
    exports = sorted(float(e) for e in s.export_at_epochs)
    done_exports = {float(x) for x in state.get("exports", [])}
    metrics_path = run / ("metrics_smoke.jsonl" if smoke else "metrics.jsonl")
    if smoke:
        start_check = step0_check(model, val_set, device, log)
        base = evaluate(model, val_set, device, s.micro_batch, 16, cfg.model.sample_steps, normaliser)
        log("smoke step-0 fixed-noise losses:", json.dumps(base))
    log(f"updates: {total} (micro {s.micro_batch} x accumulation {s.accumulation} = {per_update} samples / update; "
        f"{len(train_set)} anchors per frame-epoch)")
    model.train()
    torch.cuda.reset_peak_memory_stats()
    t0 = time.monotonic()
    seen = 0
    running = []
    grad_parts: Dict[str, float] = {}
    while state["update"] < total:
        train_set.epoch = state["epoch"]
        perm = np.random.default_rng(cfg.seed * 1000 + state["epoch"]).permutation(len(train_set))[state["position"]:]
        loader = torch.utils.data.DataLoader(
            torch.utils.data.Subset(train_set, perm.tolist()), batch_size=s.micro_batch, shuffle=False,
            num_workers=cfg.data.num_workers, collate_fn=collate, pin_memory=True, drop_last=True,
            persistent_workers=False, prefetch_factor=4 if cfg.data.num_workers else None)
        micro = 0
        for batch in loader:
            batch = to_device(batch, device)
            with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                v, a = model.loss(batch)
                loss = (cfg.model.video_loss * v.mean() + cfg.model.action_loss * a.mean()) / s.accumulation
            loss.backward()
            running.append((float(v.mean()), float(a.mean())))
            micro += 1
            state["position"] += s.micro_batch
            seen += s.micro_batch
            if micro % s.accumulation:
                continue
            lr = lr_at(state["update"], total, cfg)
            for g in opt.param_groups:
                g["lr"] = lr * g["lr_scale"]
            if state["update"] == 0:
                grad_parts = grad_norms(model)
                log("first update gradient norms per part:", json.dumps(grad_parts))
            norm = torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], cfg.optim.grad_clip)
            opt.step()
            opt.zero_grad(set_to_none=True)
            state["update"] += 1
            u = state["update"]
            epoch_float = state["epoch"] + state["position"] / len(train_set)
            if u % s.log_every == 0 or u == 1:
                el = time.monotonic() - t0
                vm, am = np.mean([r[0] for r in running]), np.mean([r[1] for r in running])
                row = {"update": u, "epoch": round(epoch_float, 4), "lr": lr, "loss_video": vm, "loss_action": am,
                       "grad_norm": float(norm), "samples_per_s": seen / el,
                       "peak_gib": torch.cuda.max_memory_allocated() / 2 ** 30,
                       "gate_abs_mean": float(model.hist_gate.detach().abs().mean())}
                with metrics_path.open("a") as f:
                    f.write(json.dumps(row) + "\n")
                eta = (total - u) * per_update / max(1e-9, seen / el) / 3600
                log(f"u {u}/{total} ep {epoch_float:.3f} lr {lr:.2e} video {vm:.4f} action {am:.4f} gn {float(norm):.2f} "
                    f"{seen / el:.1f} samples/s peak {row['peak_gib']:.1f} GiB gate {row['gate_abs_mean']:.4f} "
                    f"ETA {eta:.1f} h")
                running = []
            if (u % s.eval_every == 0 and not smoke) or u == total:
                ev = evaluate(model, val_set, device, s.micro_batch, 32, cfg.model.sample_steps, normaliser)
                ev.update(update=u, epoch=round(epoch_float, 4))
                with metrics_path.open("a") as f:
                    f.write(json.dumps({"eval": ev}) + "\n")
                log("eval", json.dumps(ev))
            for e in exports:
                if e not in done_exports and epoch_float >= e and not smoke:
                    export(model, run / f"export_e{int(e) if e == int(e) else e}.pt", cfg, state, log)
                    done_exports.add(e)
                    state["exports"] = sorted(done_exports)
            stop = (run / "STOP").exists()
            if not smoke and (u % s.resume_every == 0 or stop or u == total):
                atomic_save({"model": model.state_dict(), "optimizer": opt.state_dict(), "state": dict(state)}, resume)
                log(f"resume checkpoint saved at update {u}")
            if stop:
                log("STOP found: exiting after saving")
                return {"status": "stopped", "update": u}
            if u >= total:
                break
        if state["update"] < total:
            state["epoch"] += 1
            state["position"] = 0
    summary = {"status": "complete", "updates": state["update"], "epochs": state["epoch"] + state["position"] / len(train_set),
               "samples_per_s": seen / (time.monotonic() - t0), "peak_gib": torch.cuda.max_memory_allocated() / 2 ** 30,
               "final_eval": evaluate(model, val_set, device, s.micro_batch, 32 if not smoke else 16,
                                      cfg.model.sample_steps, normaliser)}
    if smoke:
        summary["step0"] = start_check
        summary["step0_eval"] = base
        drop = 1 - summary["final_eval"]["val_action"] / max(1e-12, base["val_action"])
        summary["action_loss_drop"] = drop
        summary["first_grad_norms"] = grad_parts
        video_ok = cfg.model.train_video == "frozen" or grad_parts.get("video", 0.0) > 0
        ok = (start_check["max_abs_diff"] == 0.0 and summary["peak_gib"] <= 135 and drop >= 0.8 and video_ok
              and grad_parts.get("action", 0.0) > 0 and all(math.isfinite(x) for x in summary["final_eval"].values()))
        summary["pass"] = bool(ok)
        log(f"SMOKE {'PASS' if ok else 'FAIL'}: step-0 history == none: {start_check}; peak {summary['peak_gib']:.1f} GiB "
            f"(<= 135); {summary['samples_per_s']:.1f} samples/s; fixed-noise action loss drop {drop:.1%} (>= 80 %)")
    else:
        export(model, run / "export_final.pt", cfg, state, log)
    write_json(run / ("SMOKE.json" if smoke else "SUMMARY.json"), summary)
    log("summary", json.dumps(summary))
    return summary


@torch.no_grad()
def grad_norms(model: FullModel) -> Dict[str, float]:
    """L2 norm of the gradients per part (video / action / proprio / gate / extra): a part that should train must not be
    0 (11-11 smoke: autocast's weight-cast cache made the video expert's casts outside autograd)."""
    out: Dict[str, float] = {}
    for name, p in model.named_parameters():
        if p.grad is None:
            continue
        part = ("video" if name.startswith("mot.mixtures.video") else "action" if name.startswith("mot.mixtures.action")
                else name.split(".")[0])
        out[part] = out.get(part, 0.0) + float(p.grad.float().square().sum())
    return {k: v ** 0.5 for k, v in out.items()}


@torch.no_grad()
def step0_check(model: FullModel, val: Samples, device, log) -> dict:
    """Non-degenerate start: with every gate at 0 the history must not change the released model's output."""
    rows = [val[i] for i in range(min(4, len(val)))]
    batch = to_device(collate(rows), device)
    noise = [fixed_noise(i, {"video": tuple(r["video_latent"].shape), "action": tuple(r["actions"].shape)}, model, device)
             for i, r in enumerate(rows)]
    noise = {k: torch.stack([n[k] for n in noise]).squeeze(1) if k.startswith("t_") else torch.stack([n[k] for n in noise])
             for k in noise[0]}
    model.eval()
    with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
        h = model.history(batch)
        v1, a1 = model.loss(batch, noise, h)
        v0, a0 = model.loss(batch, noise, None)
    model.train()
    out = {"history_frames": int(batch["hist_valid"].sum()) if "hist_valid" in batch else 0,
           "max_abs_diff": float(max((v1 - v0).abs().max(), (a1 - a0).abs().max()))}
    log("step-0 check (gates 0): history vs none", json.dumps(out))
    return out


def export(model: FullModel, path: Path, cfg: RunConfig, state: dict, log) -> None:
    """bf16 inference weights (LoRA merged is not done: the online loader rebuilds the same structure)."""
    weights = {k: v.detach().to(torch.bfloat16).cpu() for k, v in model.state_dict().items()}
    atomic_save({"weights": weights, "config": cfg.to_dict(), "state": dict(state),
                 "variant": model.variant, "train_video": cfg.model.train_video}, path)
    log(f"exported {path} ({path.stat().st_size / 2 ** 30:.1f} GiB)")


# ----------------------------------------------------------------------------- probe (memory / speed)
def probe(cfg: RunConfig, args) -> None:
    device = "cuda"
    log = Logger(cfg.run_dir, "probe")
    model, train_set, _ = build(cfg, device, log, limit_episodes=1)
    opt = optimizer_for(model, cfg)
    model.train()
    report = []
    for micro in args.micro:
        try:
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            times = []
            for k in range(args.steps):
                rows = [train_set[(k * micro + j) % len(train_set)] for j in range(micro)]
                batch = to_device(collate(rows), device)
                torch.cuda.synchronize()
                t = time.monotonic()
                with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                    v, a = model.loss(batch)
                    (v.mean() + a.mean()).backward()
                opt.step()
                opt.zero_grad(set_to_none=True)
                torch.cuda.synchronize()
                times.append(time.monotonic() - t)
            sec = float(np.median(times[1:] or times))
            row = {"micro": micro, "seconds_per_micro": sec, "samples_per_s": micro / sec,
                   "peak_gib": torch.cuda.max_memory_allocated() / 2 ** 30}
        except torch.OutOfMemoryError:
            row = {"micro": micro, "oom": True}
            opt.zero_grad(set_to_none=True)
        report.append(row)
        log("probe", json.dumps(row))
    write_json(cfg.run_dir / "PROBE.json", {"history": str(cfg.rule), "rows": report})


def main(argv: Optional[List[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("train", "smoke", "probe", "export"))
    ap.add_argument("--config", required=True)
    ap.add_argument("--set", action="append", default=[], dest="overrides")
    ap.add_argument("--updates", type=int, default=200, help="smoke: number of updates")
    ap.add_argument("--micro", type=int, nargs="+", default=[4, 8, 16], help="probe: micro batches to try")
    ap.add_argument("--steps", type=int, default=4, help="probe: timed steps per micro batch")
    ap.add_argument("--resume", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args(argv)
    cfg = load(args.config, args.overrides)
    if args.command == "train":
        train(cfg, args)
    elif args.command == "smoke":
        s = train(cfg, args, smoke=True)
        sys.exit(0 if s.get("pass") else 1)
    elif args.command == "probe":
        probe(cfg, args)
    else:
        model = FullModel.from_release(cfg.model.architecture, cfg.model.base, cfg.rule.variant, cfg.rule.event_slots)
        model.set_trainable(cfg.model.train_video, cfg.model.lora_rank)
        ck = torch.load(args.resume, map_location="cpu", weights_only=False)
        model.load_state_dict(ck["model"], strict=True)
        export(model, Path(args.out), cfg, ck["state"], print)


if __name__ == "__main__":
    main()
