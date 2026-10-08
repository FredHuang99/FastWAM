"""S1 DDP training with variable historical periods and durable validation phases."""
from __future__ import annotations
import argparse
from collections import Counter, deque
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
from .checkpoint import (save_checkpoint, upload_checkpoint, prune_local, save_weights,
                         random_state, restore_random_state, verified_load, save_continuation)
from .common import (SCHEMA, append_jsonl, atomic_json, code_version, duration, fingerprint,
                     load_config, read_json, sha256)
from .data import CachedEpisodes, collate
from .evaluate import deterministic_noise, validate, audit_cache
from .history import recipe
from .model import S1Model


def learning_rate_factor(step, cfg):
    if step < cfg["warmup"]:
        return (step + 1) / cfg["warmup"]
    progress = min(1, (step - cfg["warmup"]) / max(1, cfg["steps"] - cfg["warmup"] - 1))
    floor = cfg["min_learning_rate"] / cfg["learning_rate"]
    return floor + (1 - floor) * (1 + math.cos(math.pi * progress)) / 2


def archive_uncommitted_logs(run, step, phase):
    import shutil
    for folder in ("validation", "weights"):
        for path in (run / folder).glob("step_*"):
            try:
                artifact_step = int(path.stem.removeprefix("step_"))
            except ValueError:
                continue
            if artifact_step > step:
                destination = run / "interrupted_artifacts" / str(time.time_ns()) / folder / path.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), destination)
    for name in ("metrics.jsonl", "samples.jsonl"):
        path = run / name
        if not path.exists():
            continue
        import json
        kept, orphan = [], []
        for line in path.read_text().splitlines(True):
            row = json.loads(line)
            invalid = row.get("step", 0) > step or (row.get("step") == step and row.get("kind") == "validation" and phase == "validation")
            (orphan if invalid else kept).append(line)
        if orphan:
            directory = run / "interrupted_logs"
            directory.mkdir(exist_ok=True)
            (directory / f"{time.time_ns()}_{name}").write_text("".join(orphan), encoding="utf-8")
            path.write_text("".join(kept), encoding="utf-8")


def run_training(args):
    cfg = load_config(args.config)
    cfg["training_python"] = sys.executable
    rank, world = int(os.environ.get("RANK", 0)), int(os.environ.get("WORLD_SIZE", 1))
    local = int(os.environ.get("LOCAL_RANK", 0))
    torch.cuda.set_device(local)
    device = torch.device("cuda", local)
    dist.init_process_group("nccl", timeout=timedelta(hours=8))
    run = Path(cfg["paths"]["run"])
    micro = args.micro_batch if args.micro_batch is not None else cfg["micro_batch"]
    if micro <= 0 or cfg["global_batch"] % (micro * world):
        raise ValueError("Positive micro_batch * world_size must divide global_batch=16.")
    accumulation = cfg["global_batch"] // (micro * world)
    def request_stop(signum, frame):
        run.mkdir(parents=True, exist_ok=True)
        (run / "STOP_REQUESTED").touch()
    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    random.seed(17 + rank)
    np.random.seed(17 + rank)
    torch.manual_seed(17)
    model = S1Model(cfg, device)
    train_data, val_data = CachedEpisodes(cfg, "train"), CachedEpisodes(cfg, "val")

    def leader(function):
        box = [None]
        if rank == 0:
            try:
                box[0] = {"ok": True, "value": function()}
            except Exception as error:
                box[0] = {"ok": False, "error": repr(error)}
        dist.broadcast_object_list(box, src=0, device=device)
        if not box[0]["ok"]:
            raise RuntimeError(box[0]["error"])
        return box[0]["value"]

    def admission():
        prepared = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
        approval = read_json(Path(cfg["paths"]["prepared"]) / "alignment_approved.json")
        base = read_json(run / "base_admission.json")
        budget = read_json(run / "storage_plan.json")
        if "quota_check" not in budget or budget.get("recipe_sha") != fingerprint(recipe(cfg)):
            raise ValueError("Run the configuration-bound storage planner before training.")
        if budget.get("cache_signature") != train_data.signature:
            raise ValueError("Storage budget refers to a different cache.")
        if budget.get("checkpoint_every") != cfg["checkpoint_every"]:
            raise ValueError("HF interval changed after storage budgeting.")
        if approval["manifest_sha"] != fingerprint(prepared) or train_data.manifest["contract"]["prepared_sha"] != fingerprint(prepared):
            raise ValueError("Data, alignment and cache identities differ.")
        if not (base.get("interface_correct") is True and base.get("basic_manipulation_adequate") is True and base.get("reviewer") and base.get("notes")):
            raise ValueError("Base admission is missing; do not infer it from memory-task success rates.")
        if base.get("base_sha256") != sha256(cfg["paths"]["base"]) or base.get("stats_sha256") != sha256(cfg["paths"]["stats"]):
            raise ValueError("Base admission identifies different weights/statistics.")
        for record in train_data.manifest["episodes"]:
            if sha256(Path(cfg["paths"]["cache"]) / record["file"]) != record["cache_sha256"]:
                raise ValueError(f"Corrupt cached episode: {record['episode_id']}")
            for shard in record.get("shards", []):
                if sha256(Path(cfg["paths"]["cache"]) / shard["file"]) != shard["sha256"]:
                    raise ValueError(f"Corrupt cache shard: {shard['file']}")
        atomic_json(run / "cache_audit.json", audit_cache(model, val_data, cfg, device))
        return {"schema": SCHEMA, "base_sha256": sha256(cfg["paths"]["base"]), "stats_sha256": sha256(cfg["paths"]["stats"]),
                "cache_signature": train_data.signature, "data_sha": fingerprint(prepared), "code": code_version(cfg["root"]),
                "recipe": fingerprint({**{key: cfg[key] for key in ("seed", "global_batch", "steps", "learning_rate", "min_learning_rate", "warmup")},
                                       "history": recipe(cfg), "validation_periods": cfg.get("history", {}).get("validation_periods", [8])})}
    identity = leader(admission)
    optimizer = torch.optim.AdamW(model.memory.parameter_groups(), lr=cfg["learning_rate"], betas=(.9, .95))
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda step: learning_rate_factor(step, cfg))
    allowed = {id(p) for p in model.memory.parameters()}
    if {id(p) for group in optimizer.param_groups for p in group["params"]} != allowed or {id(p) for p in model.parameters() if p.requires_grad} != allowed:
        raise ValueError("Optimizer, trainable parameters and approved memory parameters differ.")
    step, best = 0, {"success_rate": -1., "fm": None, "step": None}
    progress = {"phase": "train", "train_seconds": 0., "checkpoint_seconds": 0., "upload_seconds": 0.,
                "offline_validation_seconds": 0., "closed_validation_seconds": 0., "evaluation_upload_seconds": 0., "wall_seconds": 0.,
                "uploads": 0, "checkpoints": 0, "offline_validations": 0, "closed_validations": 0}
    if args.resume:
        saved = verified_load(args.resume)
        old = saved["identity"]
        for key in ("schema", "base_sha256", "stats_sha256", "cache_signature", "data_sha", "recipe"):
            if old[key] != identity[key]:
                raise ValueError(f"Resume identity mismatch: {key}")
        if old["code"]["implementation_sha"] != identity["code"]["implementation_sha"] or old["code"]["core_sha"] != identity["code"]["core_sha"] or old["code"].get("support_sha") != identity["code"].get("support_sha"):
            raise ValueError("Restore the backed-up source before continuing this run.")
        model.memory.load_state_dict(saved["memory"], strict=True)
        optimizer.load_state_dict(saved["optimizer"])
        scheduler.load_state_dict(saved["scheduler"])
        step = int(saved["completed_updates"])
        if saved["sampler_next_update"] != step or step > cfg["steps"]:
            raise ValueError("Invalid completed-update resume cursor.")
        progress.update(saved["progress"])
        best = saved["best"]
        if (run / "RESTORE_REMOTE.json").exists():
            remote = read_json(run / "RESTORE_REMOTE.json")
            if remote.get("step") == step:
                progress["upload_seconds"] += remote.get("upload_seconds", 0.)
                progress["wall_seconds"] += remote.get("upload_seconds", 0.)
        elif (run / "progress_live.json").exists():
            live = read_json(run / "progress_live.json")
            if live.get("step") == step and live["progress"].get("phase") == progress["phase"]:
                progress.update(live["progress"])
        if len(saved["rng_states"]) == world:
            restore_random_state(saved["rng_states"][rank])
        leader(lambda: archive_uncommitted_logs(run, step, progress["phase"]))
        def reconcile_best():
            import shutil
            best_path = run / "weights/best.pt"
            if best.get("step") is not None:
                source = run / "weights" / f"step_{best['step']:06d}.pt"
                if not source.exists():
                    raise ValueError("Resume lacks the best checkpoint's milestone weights.")
                best_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, best_path)
                atomic_json(run / "BEST.json", best)
            else:
                for path in (best_path, run / "BEST.json"):
                    if path.exists():
                        destination = run / "interrupted_artifacts" / str(time.time_ns()) / path.name
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(path), destination)
        leader(reconcile_best)
    elif (run / "LATEST_LOCAL.json").exists():
        raise ValueError("Existing run requires explicit --resume.")
    wrapped = DDP(model, device_ids=[local], broadcast_buffers=False, find_unused_parameters=False)
    frozen = [(p, p._version) for p in model.backbone.parameters()]
    model.train()
    if rank == 0:
        run.mkdir(parents=True, exist_ok=True)
        atomic_json(run / "config_resolved.json", cfg)
        atomic_json(run / "identity.json", identity)
        atomic_json(run / "parameters.json", {name: {"shape": list(p.shape), "dtype": str(p.dtype), "trainable": True} for name, p in model.memory.named_parameters()})
        atomic_json(run / "launch_runtime.json", {"world_size": world, "micro_batch": micro, "accumulation": accumulation,
                    "torch": torch.__version__, "cuda": torch.version.cuda, "python": sys.version, "start_update": step,
                    "pid": os.getpid(), "device": torch.cuda.get_device_name(local)})
        print(f"[start] update={step}/{cfg['steps']} phase={progress['phase']} world={world} micro={micro} accumulation={accumulation}", flush=True)
    wall_start, prior_wall = time.monotonic(), progress["wall_seconds"]
    rolling = deque(maxlen=30)

    def event(component, seconds):
        progress[component + "_seconds"] += seconds
        if rank == 0:
            append_jsonl(run / "metrics.jsonl", {"kind": "timing", "step": step, "component": component, "seconds": seconds})

    def persist(rewrite=True):
        states = [None] * world if rank == 0 else None
        dist.gather_object(random_state(), states, dst=0)
        def write_upload():
            progress["wall_seconds"] = prior_wall + time.monotonic() - wall_start
            started = time.monotonic()
            directory = run / "checkpoints" / f"step_{step:06d}"
            if rewrite or not (directory / "resume.pt").exists():
                directory = save_checkpoint(model, optimizer, scheduler, run, step, cfg, identity, states, progress, best)
                progress["checkpoints"] += 1
            else:
                save_continuation(directory, step, identity, progress, best)
            event("checkpoint", time.monotonic() - started)
            started = time.monotonic()
            try:
                upload_checkpoint(cfg, directory)
                progress["uploads"] += 1
                event("upload", time.monotonic() - started)
                progress["wall_seconds"] = prior_wall + time.monotonic() - wall_start
                atomic_json(run / "progress_live.json", {"step": step, "progress": progress, "best": best})
                prune_local(run)
                print(f"[saved] update={step} phase={progress['phase']} local+HF complete", flush=True)
            except Exception as error:
                atomic_json(run / "UPLOAD_FAILED.json", {"step": step, "checkpoint": str(directory), "error": repr(error)})
                raise RuntimeError(f"HF upload failed; local checkpoint preserved at {directory}. Retry hf_tools.py checkpoint before resuming: {error}") from error
            return dict(progress)
        progress.update(leader(write_upload))

    # Validate the actual serialized size, credentials and upload path before any parameter update.
    if not args.resume:
        persist()
    stopped = False
    while step < cfg["steps"] or progress["phase"] == "validation":
        if progress["phase"] == "validation":
            rng = random_state()
            directory = run / "validation" / f"step_{step:06d}"
            weights = run / "weights" / f"step_{step:06d}.pt"
            def offline():
                directory.mkdir(parents=True, exist_ok=True)
                if not weights.exists():
                    save_weights(model, weights, step, identity)
                summaries = {}
                started = time.monotonic()
                try:
                    for period in cfg.get("history", {}).get("validation_periods", [8]):
                        output = directory / f"offline_T{period}.json"
                        if not output.exists():
                            result = validate(model, val_data, cfg, device, period=period,
                                              progress_path=directory / f"offline_T{period}_cursor.json", stop_root=run)
                            atomic_json(output, result)
                        summaries[str(period)] = read_json(output)
                except Exception as error:
                    from .eval_state import EvaluationInterrupted
                    if isinstance(error, EvaluationInterrupted):
                        return {"stopped": True, "seconds": time.monotonic() - started}
                    raise
                return {"stopped": False, "periods": summaries, "seconds": time.monotonic() - started}
            try:
                result = leader(offline)
                event("offline_validation", result["seconds"])
                stopped = result["stopped"]
                closed = None
                if not stopped:
                    from .eval_parallel import distributed_validation
                    started = time.monotonic()
                    closed = distributed_validation(cfg, weights, directory / "closed_loop", model)
                    elapsed = time.monotonic() - started
                    uploaded = closed.get("hf_upload_seconds_this_launch", 0.)
                    event("closed_validation", max(0., elapsed - uploaded))
                    event("evaluation_upload", uploaded)
                    stopped = not closed["complete"]
                if not stopped:
                    progress["offline_validations"] += 1
                    progress["closed_validations"] += 1
                    def finish_validation():
                        nonlocal best
                        fm, success = result["periods"]["8"]["fm"], closed["success_rate"]
                        atomic_json(run / "validation" / f"step_{step:06d}.json", {"periods": result["periods"], "closed_loop": closed})
                        append_jsonl(run / "metrics.jsonl", {"kind": "validation", "step": step, "periods": result["periods"], "fm": fm, "success_rate": success})
                        if success > best["success_rate"] or (success == best["success_rate"] and (best["fm"] is None or fm < best["fm"])):
                            best = {"success_rate": success, "fm": fm, "step": step}
                            save_weights(model, run / "weights/best.pt", step, identity)
                            atomic_json(run / "BEST.json", best)
                        return best
                    best = leader(finish_validation)
                    progress["phase"] = "train"
            except Exception as error:
                stopped = True
                if rank == 0:
                    atomic_json(run / "VALIDATION_FAILED.json", {"step": step, "error": repr(error)})
                    print(f"[validation-failed] Resume will finish this validation before the next update: {error}", flush=True)
            finally:
                restore_random_state(rng)
                model.train()
            # Publish a checksummed continuation sidecar, not a second optimizer file.
            persist(rewrite=False)
            if stopped or (run / "STOP_REQUESTED").exists():
                break
            continue
        if (run / "STOP_REQUESTED").exists():
            persist(rewrite=False)
            stopped = True
            break
        started = time.monotonic()
        values = torch.zeros(5, device=device, dtype=torch.float64)
        data_seconds, local_samples = 0., []
        torch.cuda.reset_peak_memory_stats(device)
        optimizer.zero_grad(set_to_none=True)
        for index in range(accumulation):
            slots = [index * world * micro + rank * micro + j for j in range(micro)]
            before = time.monotonic()
            samples = [train_data.sample(step, slot) for slot in slots]
            batch = collate(samples, device)
            data_seconds += time.monotonic() - before
            for slot, sample in zip(slots, samples):
                ids = sample["frame_ids"].tolist()
                local_samples.append({"step": step + 1, "sampling_update": step, "global_slot": slot,
                    "episode_id": sample["episode_id"], "task": sample["task"], "anchor": int(sample["t"]),
                    "T": sample["history_period"], "read_frames": len(ids), "frame_ids_sha": fingerprint(ids),
                    "first_ids": ids[:8], "last_ids": ids[-8:]})
            noise, tau = deterministic_noise(17, step, slots, device)
            sync = nullcontext() if index == accumulation - 1 else wrapped.no_sync()
            with sync:
                loss, diagnostic = wrapped(batch, noise, tau)
                if not torch.isfinite(loss):
                    raise FloatingPointError(f"Non-finite loss update={step} rank={rank}")
                (loss / accumulation).backward()
            values += torch.stack((loss.detach().double(), diagnostic["readout_norm"].double(),
                batch["history_valid"].sum(1).double().mean(), batch["action_valid"].sum(1).double().mean(),
                diagnostic["unweighted_fm"].double().mean())) / accumulation
        norm = torch.nn.utils.clip_grad_norm_(model.memory.parameters(), 1., error_if_nonfinite=True)
        if step == 0 and any(p.grad is None for p in model.memory.parameters()):
            raise ValueError("A memory parameter did not receive a gradient.")
        update_learning_rate = optimizer.param_groups[0]["lr"]
        optimizer.step()
        scheduler.step()
        step += 1
        torch.cuda.synchronize(device)
        dist.all_reduce(values)
        values /= world
        maxima = torch.tensor([time.monotonic() - started, data_seconds, torch.cuda.max_memory_allocated(device) / 2**30], device=device, dtype=torch.float64)
        dist.all_reduce(maxima, op=dist.ReduceOp.MAX)
        seconds = float(maxima[0])
        rolling.append(seconds)
        progress["train_seconds"] += seconds
        gathered = [None] * world if rank == 0 else None
        dist.gather_object(local_samples, gathered, dst=0)
        if rank == 0:
            all_samples = sorted([sample for rows in gathered for sample in rows], key=lambda sample: sample["global_slot"])
            if [sample["global_slot"] for sample in all_samples] != list(range(cfg["global_batch"])):
                raise ValueError("The optimizer update did not cover exactly 16 global slots.")
            for sample in all_samples:
                append_jsonl(run / "samples.jsonl", sample)
            remaining = sum(rolling) / len(rolling) * (cfg["steps"] - step)
            for component, count_name, remaining_events in (("checkpoint", "checkpoints", (cfg["steps"]-step)//cfg["checkpoint_every"]),
                    ("upload", "uploads", (cfg["steps"]-step)//cfg["checkpoint_every"] + (cfg["steps"]-step)//cfg["validate_every"]),
                    ("offline_validation", "offline_validations", (cfg["steps"]-step)//cfg["validate_every"]),
                    ("closed_validation", "closed_validations", (cfg["steps"]-step)//cfg["validate_every"])):
                remaining += progress[component + "_seconds"] / max(1, progress[count_name]) * remaining_events
            remaining += progress["evaluation_upload_seconds"] / max(1, progress["closed_validations"]) * ((cfg["steps"] - step) // cfg["validate_every"])
            row = {"kind": "train", "step": step, "loss": float(values[0]), "fm_unweighted": float(values[4]),
                "readout_norm": float(values[1]), "history_frames": float(values[2]), "valid_actions": float(values[3]),
                "learning_rate": update_learning_rate, "next_learning_rate": optimizer.param_groups[0]["lr"], "update_seconds": seconds, "data_seconds": float(maxima[1]),
                "gpu_peak_gib": float(maxima[2]), "T_histogram": dict(Counter(str(sample["T"]) for sample in all_samples)),
                "eta_seconds": remaining, "eta_provisional": not progress["closed_validations"], "cumulative": dict(progress)}
            if step % cfg["log_every"] == 0 or step == 1:
                row.update(gradient_norm=float(norm), gates={name: float(module.gate.detach()) for name, module in model.memory.injectors.items()},
                    gradient_by_module={name: float(torch.sqrt(sum(p.grad.float().square().sum() for p in module.parameters() if p.grad is not None)))
                                        for name, module in (("reader", model.memory.reader), ("injectors", model.memory.injectors))})
                print(f"[train] {step}/{cfg['steps']} ({100*step/cfg['steps']:.1f}%) loss={row['loss']:.6f} lr={row['learning_rate']:.2e} ETA={duration(remaining)} provisional={row['eta_provisional']}", flush=True)
            append_jsonl(run / "metrics.jsonl", row)
        if any(p._version != version for p, version in frozen):
            raise RuntimeError("A frozen backbone parameter changed.")
        stop_flag = torch.tensor(int((run / "STOP_REQUESTED").exists()), device=device)
        dist.all_reduce(stop_flag, op=dist.ReduceOp.MAX)
        stopped = bool(stop_flag.item())
        if step % cfg["validate_every"] == 0:
            progress["phase"] = "validation"
        if step % cfg["checkpoint_every"] == 0 or progress["phase"] == "validation" or stopped or step == cfg["steps"]:
            persist()
        if stopped:
            break
    if rank == 0:
        (run / "STOP_REQUESTED").unlink(missing_ok=True)
        print(f"[finish] completed_updates={step} phase={progress['phase']} stopped={stopped}; latest complete HF pointer is LATEST_REMOTE.json", flush=True)
    return 2 if stopped else 0


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
