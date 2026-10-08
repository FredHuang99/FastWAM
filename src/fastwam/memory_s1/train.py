"""Standalone synchronous DDP S1 trainer, with completed-update resume semantics."""
from __future__ import annotations

import argparse
from collections import deque
from contextlib import nullcontext
from datetime import timedelta
import math
import os
from pathlib import Path
import random
import signal
import sys
import time

import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

from .checkpoint import (save_checkpoint, upload_checkpoint, prune_local, save_weights, random_state,
                         restore_random_state, verified_load)
from .common import (SCHEMA, append_jsonl, atomic_json, code_version, duration, fingerprint, load_config, read_json, sha256)
from .data import CachedEpisodes, collate
from .evaluate import deterministic_noise, validate, audit_cache
from .model import S1Model


def learning_rate_factor(step, cfg):
    if step < cfg["warmup"]:
        return (step + 1) / cfg["warmup"]
    progress = min(1, (step - cfg["warmup"]) / max(1, cfg["steps"] - cfg["warmup"] - 1))
    floor = cfg["min_learning_rate"] / cfg["learning_rate"]
    return floor + (1 - floor) * (1 + math.cos(math.pi * progress)) / 2


def run_training(args):
    cfg = load_config(args.config)
    cfg["training_python"] = sys.executable
    rank, world = int(os.environ.get("RANK", 0)), int(os.environ.get("WORLD_SIZE", 1))
    local = int(os.environ.get("LOCAL_RANK", 0))
    torch.cuda.set_device(local)
    device = torch.device("cuda", local)
    dist.init_process_group("nccl", timeout=timedelta(hours=4))
    run = Path(cfg["paths"]["run"])
    micro = args.micro_batch or cfg["micro_batch"]
    if micro <= 0 or (args.micro_batch is not None and args.micro_batch <= 0):
        raise ValueError("micro_batch must be positive.")
    if cfg["global_batch"] % (micro * world):
        raise ValueError("micro_batch * world_size must divide global_batch=16.")
    accumulation = cfg["global_batch"] // (micro * world)
    stop_requested = [False]
    def request_stop(signum, frame):
        stop_requested[0] = True
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    random.seed(17 + rank)
    np.random.seed(17 + rank)
    torch.manual_seed(17)
    model = S1Model(cfg, device)
    train_data, val_data = CachedEpisodes(cfg, "train"), CachedEpisodes(cfg, "val")
    identity_box = [None]
    if rank == 0:
        prepared = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
        approval = read_json(Path(cfg["paths"]["prepared"]) / "alignment_approved.json")
        admission = read_json(run / "base_admission.json")
        budget = read_json(run / "storage_plan.json")
        if "quota_check" not in budget:
            raise ValueError("Run scripts/memory_s1/storage_plan.py before training; the complete backup budget must fit private storage.")
        cache = train_data.manifest
        if approval["manifest_sha"] != fingerprint(prepared) or cache["contract"]["prepared_sha"] != fingerprint(prepared):
            raise ValueError("Data/cache/approval do not refer to the same split and episodes.")
        if not admission.get("interface_correct") or not admission.get("basic_manipulation_adequate") or not admission.get("reviewer"):
            raise ValueError("Base admission is incomplete; inspect prefix diagnostics or prepare P2 separately.")
        if admission.get("base_sha256") != sha256(cfg["paths"]["base"]) or admission.get("stats_sha256") != sha256(cfg["paths"]["stats"]) or not admission.get("notes"):
            raise ValueError("Base admission must identify the exact weights/statistics and diagnostic evidence.")
        for record in cache["episodes"]:
            if sha256(Path(cfg["paths"]["cache"]) / record["file"]) != record["cache_sha256"]:
                raise ValueError(f"Corrupt cached episode: {record['episode_id']}.")
        audit = audit_cache(model, val_data, cfg, device)
        identity_box[0] = {"schema": SCHEMA, "base_sha256": sha256(cfg["paths"]["base"]),
                           "stats_sha256": sha256(cfg["paths"]["stats"]), "cache_signature": train_data.signature,
                           "data_sha": fingerprint(prepared), "code": code_version(cfg["root"]),
                           "recipe": fingerprint({key: cfg[key] for key in ("seed", "global_batch", "steps", "learning_rate", "min_learning_rate", "warmup")})}
        atomic_json(run / "cache_audit.json", audit)
    dist.broadcast_object_list(identity_box, src=0, device=device)
    identity = identity_box[0]
    optimizer = torch.optim.AdamW(model.memory.parameter_groups(), lr=cfg["learning_rate"], betas=(0.9, 0.95))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda step: learning_rate_factor(step, cfg))
    allowed = {id(parameter) for parameter in model.memory.parameters()}
    optimized = {id(parameter) for group in optimizer.param_groups for parameter in group["params"]}
    trainable = {id(parameter) for parameter in model.parameters() if parameter.requires_grad}
    if optimized != allowed or trainable != allowed:
        raise ValueError("Optimizer/trainable/approved parameter sets differ.")
    step, best = 0, {"success_rate": -1.0, "fm": None, "step": None}
    progress = {"train_seconds": 0.0, "validation_seconds": 0.0, "upload_seconds": 0.0, "wall_seconds": 0.0}
    if args.resume:
        checkpoint = verified_load(args.resume)
        old = checkpoint["identity"]
        for key in ("schema", "base_sha256", "stats_sha256", "cache_signature", "data_sha", "recipe"):
            if old[key] != identity[key]:
                raise ValueError(f"Resume identity mismatch: {key}.")
        if old["code"]["implementation_sha"] != identity["code"]["implementation_sha"] or old["code"]["core_sha"] != identity["code"]["core_sha"]:
            raise ValueError("Implementation changed since checkpoint; use the backed-up code for exact S1 continuation.")
        model.memory.load_state_dict(checkpoint["memory"], strict=True)
        optimizer.load_state_dict(checkpoint["optimizer"])
        scheduler.load_state_dict(checkpoint["scheduler"])
        step = int(checkpoint["completed_updates"])
        if checkpoint["sampler_next_update"] != step or step > cfg["steps"]:
            raise ValueError("Invalid completed-update resume cursor.")
        progress, best = checkpoint["progress"], checkpoint["best"]
        if (run / "progress_live.json").is_file():
            live = read_json(run / "progress_live.json")
            if live.get("step") == step:
                progress = live["progress"]
        elif (run / "RESTORE_REMOTE.json").is_file():
            remote = read_json(run / "RESTORE_REMOTE.json")
            if remote.get("step") == step:
                progress["upload_seconds"] += remote.get("upload_seconds", 0)
                progress["wall_seconds"] += remote.get("upload_seconds", 0)
        states = checkpoint["rng_states"]
        if len(states) == world:
            restore_random_state(states[rank])
        # Sampling and FM noise are keyed by global update/slot, independent of worker RNG.
    elif (run / "LATEST_LOCAL.json").exists():
        raise ValueError("This run already contains checkpoints. Resume explicitly; do not silently restart.")
    wrapped = DDP(model, device_ids=[local], broadcast_buffers=False, find_unused_parameters=False)
    frozen_versions = [(parameter, parameter._version) for parameter in model.backbone.parameters()]
    model.train()
    if rank == 0:
        run.mkdir(parents=True, exist_ok=True)
        atomic_json(run / "config_resolved.json", cfg)
        atomic_json(run / "identity.json", identity)
        atomic_json(run / "parameters.json", {name: {"shape": list(parameter.shape), "dtype": str(parameter.dtype), "trainable": parameter.requires_grad}
                                             for name, parameter in model.named_parameters() if parameter.requires_grad})
        atomic_json(run / "launch_runtime.json", {"world_size": world, "micro_batch": micro, "accumulation": accumulation,
                                                  "torch": torch.__version__, "cuda": torch.version.cuda, "start_update": step,
                                                  "pid": os.getpid(), "device": torch.cuda.get_device_name(local)})
        print(f"[start] update={step}/{cfg['steps']} world={world} micro={micro} accumulation={accumulation}", flush=True)
    rolling = deque(maxlen=30)
    start_wall = time.monotonic()
    prior_wall = progress["wall_seconds"]
    while step < cfg["steps"]:
        started = time.monotonic()
        data_seconds = 0.0
        values = torch.zeros(5, device=device, dtype=torch.float64)
        optimizer.zero_grad(set_to_none=True)
        for accumulation_index in range(accumulation):
            slots = [accumulation_index * world * micro + rank * micro + index for index in range(micro)]
            data_start = time.monotonic()
            samples = [train_data.sample(step, slot) for slot in slots]
            batch = collate(samples, device)
            data_seconds += time.monotonic() - data_start
            noise, tau = deterministic_noise(17, step, slots, device)
            sync = nullcontext() if accumulation_index == accumulation - 1 else wrapped.no_sync()
            with sync:
                loss, diagnostic = wrapped(batch, noise, tau)
                if not torch.isfinite(loss):
                    raise FloatingPointError(f"Non-finite loss at update={step} rank={rank}.")
                (loss / accumulation).backward()
            values += torch.stack((loss.detach().double(), diagnostic["readout_norm"].double(),
                                    batch["history_valid"].sum(1).float().mean().double(),
                                    batch["action_valid"].sum(1).float().mean().double(),
                                    diagnostic["unweighted_fm"].mean().double())) / accumulation
        gradient_norm = torch.nn.utils.clip_grad_norm_(model.memory.parameters(), 1.0, error_if_nonfinite=True)
        if step == 0:
            missing = [name for name, parameter in model.memory.named_parameters() if parameter.grad is None]
            if missing:
                raise RuntimeError(f"Missing new-module gradients: {missing}.")
        optimizer.step()
        scheduler.step()
        step += 1
        torch.cuda.synchronize(device)
        dist.all_reduce(values, op=dist.ReduceOp.SUM)
        values /= world
        seconds = time.monotonic() - started
        rolling.append(seconds)
        progress["train_seconds"] += seconds
        stop_flag = torch.tensor(int(stop_requested[0] or (run / "STOP_REQUESTED").exists()), device=device)
        dist.all_reduce(stop_flag, op=dist.ReduceOp.MAX)
        stop = bool(stop_flag.item())
        if rank == 0 and (step % cfg["log_every"] == 0 or step == 1):
            remaining = sum(rolling) / len(rolling) * (cfg["steps"] - step)
            remaining += (cfg["steps"] - step) // cfg["checkpoint_every"] * progress["upload_seconds"] / max(1, step // cfg["checkpoint_every"])
            remaining += (cfg["steps"] - step) // cfg["validate_every"] * progress["validation_seconds"] / max(1, step // cfg["validate_every"])
            row = {"kind": "train", "step": step, "loss": float(values[0]), "fm_unweighted": float(values[4]),
                   "readout_norm": float(values[1]), "history_frames": float(values[2]), "valid_actions": float(values[3]),
                   "learning_rate": optimizer.param_groups[0]["lr"], "gradient_norm": float(gradient_norm),
                   "gates": {name: float(module.gate.detach()) for name, module in model.memory.injectors.items()},
                   "gradient_by_module": {name: float(torch.sqrt(sum(parameter.grad.float().square().sum() for parameter in module.parameters() if parameter.grad is not None)))
                                          for name, module in [("reader", model.memory.reader), ("injectors", model.memory.injectors)]},
                   "data_seconds": data_seconds, "update_seconds": seconds, "eta_seconds": remaining,
                   "gpu_peak_gib": torch.cuda.max_memory_allocated(device) / 2**30, "cumulative": dict(progress)}
            append_jsonl(run / "metrics.jsonl", row)
            print(f"[train] {step}/{cfg['steps']} loss={row['loss']:.6f} lr={row['learning_rate']:.2e} grad={row['gradient_norm']:.3f} ETA={duration(remaining)}", flush=True)
        if step % cfg["validate_every"] == 0 and not stop:
            validation_start = time.monotonic()
            if rank == 0:
                from .sim_bridge import run_closed_loop
                result = validate(model, val_data, cfg, device)
                weights = run / "weights" / f"step_{step:06d}.pt"
                save_weights(model, weights, step, identity)
                closed = run_closed_loop(cfg, weights, "internal", ["full"], run / "validation" / f"step_{step:06d}", resident_model=model)
                success_rate = closed["success_rate"]
                atomic_json(run / "validation" / f"step_{step:06d}.json", {"offline": result, "closed_loop": closed})
                append_jsonl(run / "metrics.jsonl", {"kind": "validation", "step": step, "fm": result["fm"], "success_rate": success_rate})
                if success_rate > best["success_rate"] or (success_rate == best["success_rate"] and (best["fm"] is None or result["fm"] < best["fm"])):
                    best = {"success_rate": success_rate, "fm": result["fm"], "step": step}
                    save_weights(model, run / "weights/best.pt", step, identity)
                    atomic_json(run / "BEST.json", best)
            dist.barrier()
            progress["validation_seconds"] += time.monotonic() - validation_start
        if any(parameter._version != version for parameter, version in frozen_versions):
            raise RuntimeError("A frozen backbone parameter was modified.")
        if step % cfg["checkpoint_every"] == 0 or stop or step == cfg["steps"]:
            rng_states = [None] * world if rank == 0 else None
            dist.gather_object(random_state(), rng_states, dst=0)
            status = [None]
            if rank == 0:
                progress["wall_seconds"] = prior_wall + time.monotonic() - start_wall
                directory = save_checkpoint(model, optimizer, scheduler, run, step, cfg, identity, rng_states, progress, best)
                upload_start = time.monotonic()
                try:
                    upload_checkpoint(cfg, directory)
                    progress["upload_seconds"] += time.monotonic() - upload_start
                    progress["wall_seconds"] = prior_wall + time.monotonic() - start_wall
                    atomic_json(run / "progress_live.json", {"step": step, "progress": progress})
                    prune_local(run)
                    status[0] = {"ok": True}
                    print(f"[saved] update={step} local+HF complete", flush=True)
                except Exception as error:
                    status[0] = {"ok": False, "error": str(error)}
                    atomic_json(run / "UPLOAD_FAILED.json", {"step": step, "checkpoint": str(directory), "error": str(error)})
                    print(f"[safe-stop] HF upload failed; local checkpoint preserved: {directory}. Retry with scripts/memory_s1/hf_tools.py checkpoint.", flush=True)
            dist.broadcast_object_list(status, src=0, device=device)
            if not status[0]["ok"]:
                return 2
        if stop:
            if rank == 0:
                (run / "STOP_REQUESTED").unlink(missing_ok=True)
                print(f"[safe-stop] All workers exit after completed update={step} and HF backup.", flush=True)
            break
    if rank == 0:
        print(f"[finish] completed_updates={step}; full evaluation is a separate explicit command.", flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--resume")
    parser.add_argument("--micro-batch", type=int)
    args = parser.parse_args()
    try:
        result = run_training(args)
    finally:
        if dist.is_initialized():
            dist.destroy_process_group()
    raise SystemExit(result)


if __name__ == "__main__":
    main()
