"""Production training preflight: real histories and gradients, zero optimizer updates."""
from __future__ import annotations

from contextlib import nullcontext
import os
from pathlib import Path
import time

import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

from .common import atomic_json, fingerprint, load_config, read_json
from .data import collate
from .evaluate import deterministic_noise
from .history import select_ids, training_period, training_phase


def global_slots(index, world, micro, rank):
    return [index * world * micro + rank * micro + offset for offset in range(micro)]


def wrap_training_model(model, device, world):
    """Share the production/preflight wrapper choice; one worker needs no collectives."""
    if world == 1:
        if dist.is_initialized():
            raise ValueError("Single-worker training must not initialize a process group.")
        return model
    if world < 1 or not dist.is_initialized() or dist.get_world_size() != world:
        raise ValueError("Multi-worker training requires a matching initialized process group.")
    return DDP(model, device_ids=[device.index], broadcast_buffers=False, find_unused_parameters=False)


def accumulation_context(model, last_micro_batch):
    if last_micro_batch or not isinstance(model, DDP):
        return nullcontext()
    return model.no_sync()


def loader_comparison(dataset, record, sample):
    """Compare the LRU loader with direct, independently indexed shard reads."""
    wanted = sample["frame_ids"]
    features, ids, latent, proprio = [], [], None, None
    for shard in record["shards"]:
        selected = wanted[(wanted >= shard["first"]) & (wanted <= shard["last"])]
        if not len(selected):
            continue
        block = torch.load(dataset.root / shard["file"], map_location="cpu", weights_only=True)
        offsets = selected - shard["first"]
        features.append(block["features"][offsets])
        ids.append(block["frame_ids"][offsets])
        anchor = int(sample["t"])
        if shard["first"] <= anchor <= shard["last"]:
            latent = block["latents"][anchor - shard["first"]]
            proprio = block["proprio"][anchor - shard["first"]]
    comparisons = {"history": torch.cat(features), "frame_ids": torch.cat(ids), "latent": latent, "proprio": proprio}
    if any(value is None or not torch.equal(value, sample[key]) for key, value in comparisons.items()):
        raise ValueError(f"Cached loader differs from direct shard indexing: {record['episode_id']}")
    return {"passed": True, "episode_id": record["episode_id"], "anchor": int(sample["t"])}


def verify_full_inventory(cfg):
    from .data import CachedEpisodes
    dataset = CachedEpisodes(cfg, "train")
    count, started = 0, time.monotonic()
    for index, record in enumerate(dataset.manifest["episodes"], 1):
        dataset.verify_record(record)
        ids = []
        for shard in record["shards"]:
            marker = read_json((dataset.root / shard["file"]).with_suffix(".complete.json"))
            planned = list(range(shard["first"], shard["last"] + 1))
            if marker["sha256"] != shard["sha256"] or marker["signature"] != dataset.signature or marker["frame_ids"] != planned:
                raise ValueError(f"Invalid cache completion marker: {shard['file']}")
            ids.extend(planned)
            count += 1
        if ids != list(range(record["length"])):
            raise ValueError(f"Incomplete cache coverage: {record['episode_id']}")
        print(f"[cache-integrity] {index}/{len(dataset.manifest['episodes'])} episodes", flush=True)
    return {"passed": True, "shards": count, "seconds": time.monotonic() - started}


def accumulation_check(model, dataset, cfg, device, micro, check_masks=True):
    if int(os.environ.get("WORLD_SIZE", "1")) != 1 or dist.is_initialized():
        raise ValueError("Use torchrun --nproc_per_node=1 -m fastwam.memory_s1.train --functional-preflight.")
    if micro not in (1, 2):
        raise ValueError("H100 preflight supports micro-batch 1 or 2.")
    if cfg["global_batch"] != 16 or cfg["global_batch"] % micro:
        raise ValueError("Preflight requires exactly 16 global slots per complete update.")
    started = time.monotonic()
    print(f"[preflight] phase masks start; micro={micro} check_masks={check_masks}", flush=True)
    mask_cases = 0
    for task, records in (dataset.by_task.items() if check_masks else []):
        longest = max(records, key=lambda row: row["length"])
        anchor = int(dataset.load(longest)["anchors"][-1])
        for period in range(1, 17):
            for phase in range(period):
                sample = dataset.at(longest, anchor, period=period, phase=phase)
                ids = sample["frame_ids"].tolist()
                expected = [i for i in range(anchor + 1) if i % period == phase or i % 16 == 0 or i == anchor]
                if ids != expected or not {0, anchor}.issubset(ids):
                    raise ValueError("Production phase selection dropped mandatory frames or admitted future frames.")
                mask_cases += 1
    print(f"[preflight] phase masks complete; cases={mask_cases}", flush=True)
    # Worst available history for both tasks, plus the actual padded action tails.
    longest_samples = []
    for records in dataset.by_task.values():
        record = max(records, key=lambda row: row["length"])
        anchor = int(dataset.load(record)["anchors"][-1])
        longest_samples.append(dataset.at(record, anchor, period=1, phase=0))
    model.train()
    torch.cuda.reset_peak_memory_stats(device)
    for start in range(0, len(longest_samples), micro):
        model.zero_grad(set_to_none=True)
        batch = collate(longest_samples[start:start + micro], device)
        noise, tau = deterministic_noise(cfg["seed"], 0, list(range(start, start + len(batch["t"]))), device)
        print(f"[preflight] longest-history forward; micro={micro} frames={batch['history_valid'].sum(1).tolist()}", flush=True)
        loss, _ = model(batch, noise, tau)
        print(f"[preflight] longest-history backward; micro={micro}", flush=True)
        loss.backward()
        torch.cuda.synchronize(device)
        print(f"[preflight] longest-history complete; micro={micro}", flush=True)
        if not torch.isfinite(loss):
            raise ValueError("Longest-history loss is non-finite.")
        del batch, noise, tau, loss
    model.zero_grad(set_to_none=True)
    wrapped = wrap_training_model(model, device, world=1)
    slots_seen, samples = [], []
    accumulation = cfg["global_batch"] // micro
    before = [(p, p._version) for p in model.parameters()]
    print(f"[preflight] accumulation start; execution=single_process world=1 micro={micro} accumulation={accumulation}", flush=True)
    for index in range(accumulation):
        slots = global_slots(index, 1, micro, 0)
        values = [dataset.sample(0, slot) for slot in slots]
        batch = collate(values, device)
        noise, tau = deterministic_noise(cfg["seed"], 0, slots, device)
        with accumulation_context(wrapped, index == accumulation - 1):
            loss, _ = wrapped(batch, noise, tau)
            if not torch.isfinite(loss):
                raise ValueError("Accumulation preflight loss is non-finite.")
            (loss / accumulation).backward()
        for slot, sample in zip(slots, values):
            samples.append({"global_slot": slot, "episode_id": sample["episode_id"], "anchor": int(sample["t"]),
                "T": sample["history_period"], "phase": sample["history_phase"], "frame_ids": sample["frame_ids"].tolist()})
        slots_seen.extend(slots)
        torch.cuda.synchronize(device)
        print(f"[preflight] accumulation {index+1}/{accumulation}; micro={micro} optimizer_updates=0", flush=True)
    if slots_seen != list(range(16)):
        raise ValueError("Accumulation does not cover exactly 16 global slots.")
    if any(p._version != version for p, version in before):
        raise ValueError("A parameter changed during the no-update preflight.")
    if any(p.grad is None or not torch.isfinite(p.grad).all() for p in model.memory.parameters()):
        raise ValueError("Missing/non-finite memory gradients.")
    if any(p.requires_grad or p.grad is not None for p in model.backbone.parameters()):
        raise ValueError("Frozen backbone received parameter gradients.")
    torch.cuda.synchronize(device)
    result = {"passed": True, "micro_batch": micro, "accumulation": accumulation, "world_size": 1,
              "optimizer_updates": 0, "execution": "single_process", "process_group_initialized": dist.is_initialized(),
              "legal_phase_cases": mask_cases, "samples": samples,
              "longest_histories": [{"episode_id": s["episode_id"], "anchor": int(s["t"]),
                                     "frames": len(s["frame_ids"])} for s in longest_samples],
              "peak_gpu_gib": torch.cuda.max_memory_allocated(device) / 2**30,
              "seconds": time.monotonic() - started, "evidence_coverage": "unknown"}
    model.zero_grad(set_to_none=True)
    del wrapped
    import gc
    gc.collect()
    return result


def run(args):
    from .integration import training_check, admit
    from .integration_contract import output_root
    from .eval_state import cuda_gpu_uuid
    cfg = load_config(args.config)
    run_root = Path(cfg["paths"]["run"])
    if (run_root / "LATEST_LOCAL.json").exists():
        raise ValueError("Training already started; do not overwrite its pre-training admission.")
    if int(os.environ.get("WORLD_SIZE", "1")) != 1:
        raise ValueError("This preflight requires exactly one H100 worker.")
    torch.cuda.set_device(0)
    if dist.is_initialized():
        raise ValueError("Preflight must start without a distributed process group.")
    print("[preflight] execution=single_process world=1; no NCCL/DDP initialization; optimizer_updates=0", flush=True)
    root = output_root(cfg)
    if (root / "STOP_REQUESTED").exists():
        raise ValueError("Preflight stop marker exists; inspect it before retrying.")
    cfg["preflight_micro_batch"] = args.micro_batch or cfg["micro_batch"]
    # This runtime override is deliberately excluded from the final training configuration.
    try:
        atomic_json(root / "cache_integrity_phase.json", verify_full_inventory(cfg))
        training_check(cfg, root, cuda_gpu_uuid(0))
    finally:
        cfg.pop("preflight_micro_batch", None)
    admit(cfg)
    print("[preflight] fresh training evidence and derived six-stage admission complete; optimizer_updates=0", flush=True)
