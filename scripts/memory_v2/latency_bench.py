"""Deployment latency of one memory_v2 policy WITHOUT the simulator (latency track, 11-06).

In a real deployment there is no simulator: per decision the cost is observation encoding + the policy (+ the
network). This script feeds a recorded RMBench demo to the online Session exactly as the closed loop does
(contiguous observations, one decision every --execute frames), so every decision runs the deployed path:
VAE encode of the new frames -> current-frame prefill + history (inject readout, or kv_replay prefill / episode
cache) -> denoising. No simulator and no diagnostic re-sampling. Timings are CUDA-synchronised per decision
(the decisions.jsonl fields written by online.Session).

Variants (each a fresh Session on the same demo, same noise seeds):
  steps<K>    memory on, K Euler steps (--steps, default 10 4 2 1)
  nohist<K>   the same model with an EMPTY history (periodic rule, T = 1e9, no anchor/recent): the cost of the
              policy without reading memory, at the smallest and largest K
  nocache<K>  kv_replay only: the history re-prefilled at every decision (the online path before 11-06), at K = 10
Report: outputs/memory_v2/report/LATENCY_<run>_<time>.md (+ .json): per variant mean / p50 / p90 (ms) of encode,
conditions, sample and total, history frames, frames prefilled per decision, peak GPU memory. The first --warmup
decisions (text encoding, allocator, kernels) are excluded.

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/latency_bench.py --checkpoint <ckpt.pt> \
        --demo <RMBench .../data/episode_0000000.hdf5> [--decisions 40] [--steps 10 4 2 1] [--set k=v ...]
Run it on an otherwise idle GPU: the report records nvidia-smi utilisation before the first variant.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
BJ = timezone(timedelta(hours=8))
FIELDS = ("encode_seconds", "conditions_seconds", "sample_seconds", "seconds")


def load_demo(path: Path, frames: int, decode_root: Path):
    import h5py
    import numpy as np
    from fastwam.memory_s1.data import choose_instruction, official_decoder, read_episode
    state, _, cameras, _, _, embedded = read_episode(path)
    instruction, _ = choose_instruction(path, embedded)
    decode = official_decoder(decode_root)
    n = min(frames, len(state))
    observations = []
    with h5py.File(path, "r") as f:
        for i in range(n):
            arrays = [np.ascontiguousarray(np.asarray(decode(f[c][i])), dtype=np.uint8) for c in cameras]
            observations.append({"frame_id": i, "images": [a.tobytes() for a in arrays],
                                 "shapes": [list(a.shape) for a in arrays], "proprio": state[i].tolist()})
    return instruction, observations


def gpu_snapshot() -> str:
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=index,name,utilization.gpu,memory.used,memory.total",
                              "--format=csv,noheader"], capture_output=True, text=True, timeout=20)
        return out.stdout.strip()
    except Exception as error:  # pragma: no cover - informational only
        return f"nvidia-smi unavailable: {error}"


def run_variant(policy, name, steps, cache, instruction, observations, execute, task, out_dir):
    import torch
    from fastwam.memory_v2.online import Session
    directory = out_dir / name
    directory.mkdir(parents=True, exist_ok=True)
    log = directory / "decisions.jsonl"
    if log.exists():
        log.unlink()
    session = Session(policy, directory, "on", steps, 1.0, False, tag=f"latency/{name}", limit=len(observations),
                      replay_cache=cache)
    torch.cuda.reset_peak_memory_stats(policy.device)
    last = -1
    for d in range(0, len(observations), execute):
        request = {"current_id": d, "instruction": instruction, "episode_seed": 0, "task": task,
                   "observations": observations[last + 1:d + 1]}
        session.decide(request)
        last = d
    rows = [json.loads(s) for s in log.read_text().splitlines() if s.strip()]
    return rows, torch.cuda.max_memory_allocated(policy.device) / 2 ** 30


def summarise(rows, warmup):
    used = rows[warmup:] or rows
    out = {"decisions": len(used)}
    for key in FIELDS:
        values = sorted(1000.0 * float(r.get(key, 0.0)) for r in used)
        out[key] = {"mean": statistics.fmean(values), "p50": values[len(values) // 2],
                    "p90": values[min(len(values) - 1, int(0.9 * len(values)))]}
    out["history_frames_mean"] = statistics.fmean(r.get("history_frames", len(r.get("v2_frame_ids", []))) for r in used)
    out["history_frames_last"] = used[-1].get("history_frames", len(used[-1].get("v2_frame_ids", [])))
    out["prefilled_mean"] = statistics.fmean(r.get("history_prefilled", 0) for r in used)
    out["s1_frames_mean"] = statistics.fmean(len(r.get("s1_frame_ids") or []) for r in used)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", default="", help="memory_v2 checkpoint (.pt)")
    ap.add_argument("--run", default="", help="instead of --checkpoint: the UNTRAINED model built from this run's saved "
                                              "config (+ --set), e.g. kv_replay latency before any N1 training "
                                              "(zero-start gates: the same compute as a trained model)")
    ap.add_argument("--config", type=Path, default=Path("configs/memory_v2/train_v2_A.yaml"), help="only for 'init'")
    ap.add_argument("--set", nargs="*", default=[], help="config overrides (k=v), e.g. memory_v2.history.mode=periodic")
    ap.add_argument("--demo", required=True,
                    help="one RMBench demo: an hdf5 path, or task:<name>[:<k>] = the k-th demo (default 0) of that task "
                         "under the dense config's raw root (its task's instruction is used)")
    ap.add_argument("--task", default="", help="task name for the request (default: the demo's task folder)")
    ap.add_argument("--decisions", type=int, default=40)
    ap.add_argument("--execute", type=int, default=8)
    ap.add_argument("--steps", type=int, nargs="+", default=[10, 4, 2, 1])
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--no-nohist", action="store_true", help="skip the empty-history variants")
    ap.add_argument("--label", default="")
    ap.add_argument("--open-gates", action="store_true",
                    help="kv_replay, untrained model (--run): set every replay gate to 0.5 so sampling really computes "
                         "the history attention (zero gates are skipped under no_grad and would understate the cost)")
    args = ap.parse_args(argv)

    import torch
    from fastwam.memory_v2.config import HistoryPolicyConfig
    from fastwam.memory_v2.online import Policy, policy_config, run_label
    if args.run:
        saved = json.loads((O / args.run / "CONFIG.json").read_text(encoding="utf-8"))
        args.config = O / "latency" / f"{args.run}_config.yaml"
        args.config.parent.mkdir(parents=True, exist_ok=True)
        args.config.write_text(json.dumps(saved["config"], indent=1), encoding="utf-8")
        args.checkpoint = "init"
        args.label = args.label or f"{args.run}_init_{'_'.join(x.split('=')[0].split('.')[-1] for x in args.set) or 'saved'}"
    if not args.checkpoint:
        raise SystemExit("give --checkpoint or --run")
    cfg, state = policy_config(args.config, args.checkpoint, args.set)
    policy = Policy(cfg, state, args.checkpoint, "cuda:0", encoders=True)
    del state
    if args.open_gates:
        if cfg.v2.memory.read != "kv_replay":
            raise SystemExit("--open-gates is for kv_replay models")
        with torch.no_grad():
            policy.model.memory.replay.gate.net[2].bias.fill_(0.5)       # g = TauGate - 1 = 0.5 at every tau
    label = args.label or run_label(args.checkpoint)
    if args.demo.startswith("task:"):
        parts = args.demo.split(":")
        demos = sorted((Path(policy.path("raw")) / parts[1] / "aloha_agilex/data").glob("*.hdf5"))
        if not demos:
            raise FileNotFoundError(f"No demos for {parts[1]} under {policy.path('raw')}")
        args.demo = demos[int(parts[2]) if len(parts) > 2 else 0]
    args.demo = Path(args.demo)
    task = args.task or args.demo.parent.parent.parent.name
    decode_root = Path(policy.spec.root) / policy.dense_cfg["closed_loop"]["simulator_root"]
    frames = (args.decisions - 1) * args.execute + 1
    started = time.monotonic()
    instruction, observations = load_demo(args.demo, frames, decode_root)
    print(f"[latency] {label}: {len(observations)} frames of {args.demo.name} decoded in {time.monotonic() - started:.0f}s; "
          f"task={task} read={cfg.v2.memory.read} history={cfg.v2.history.mode}", flush=True)
    snapshot = gpu_snapshot()
    replay = cfg.v2.memory.read == "kv_replay"
    variants = [(f"steps{k}", k, True, None) for k in args.steps]
    if not args.no_nohist:
        empty = HistoryPolicyConfig(mode="periodic", period=10 ** 9, anchor_frames=0, recent_frames=0, max_frames=1)
        variants += [(f"nohist{k}", k, True, empty) for k in sorted({max(args.steps), min(args.steps)}, reverse=True)]
    if replay:
        variants.append((f"nocache{max(args.steps)}", max(args.steps), False, None))
    out_dir = O / "latency" / label
    results = {}
    original = policy.cfg
    for name, steps, cache, history in variants:
        if history is not None:
            policy.cfg = dataclasses.replace(original, v2=dataclasses.replace(original.v2, history=history))
        try:
            rows, peak = run_variant(policy, name, steps, cache, instruction, observations, args.execute, task, out_dir)
        finally:
            policy.cfg = original
        results[name] = dict(summarise(rows, args.warmup), steps=steps, cache=cache and replay, peak_gib=peak,
                             empty_history=history is not None)
        r = results[name]
        print(f"[latency] {name:<10} total {r['seconds']['mean']:8.1f} ms (p90 {r['seconds']['p90']:.1f})  encode "
              f"{r['encode_seconds']['mean']:.1f}  conditions {r['conditions_seconds']['mean']:.1f}  sample "
              f"{r['sample_seconds']['mean']:.1f}  hist {r['history_frames_mean']:.1f}  prefilled {r['prefilled_mean']:.1f}",
              flush=True)

    base = results.get(f"steps{max(args.steps)}", {}).get("seconds", {}).get("mean")
    lines = [f"# Deployment latency without the simulator: {label} ({datetime.now(BJ):%F %T})", "",
             f"- checkpoint `{args.checkpoint}`; read = {cfg.v2.memory.read}; history = {cfg.v2.history.mode} "
             f"(period {cfg.v2.history.period}, cap {cfg.v2.history.max_frames}); overrides {args.set or '-'}",
             f"- demo `{args.demo}` ({task}), {len(observations)} frames, one decision every {args.execute} frames, "
             f"{len(observations[::args.execute])} decisions per variant, first {args.warmup} excluded",
             f"- GPU before the run: `{snapshot}`", "",
             "| variant | steps | memory | total ms (mean / p50 / p90) | encode | conditions | sample | speed-up vs "
             f"steps{max(args.steps)} | history frames (mean / last) | prefilled per decision | peak GiB |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, r in results.items():
        mem = "empty history" if r["empty_history"] else ("on, cache" if r["cache"] else ("on, no cache" if replay else "on"))
        t = r["seconds"]
        speed = f"{base / t['mean']:.2f}x" if base else "-"
        lines.append(f"| {name} | {r['steps']} | {mem} | {t['mean']:.1f} / {t['p50']:.1f} / {t['p90']:.1f} | "
                     f"{r['encode_seconds']['mean']:.1f} | {r['conditions_seconds']['mean']:.1f} | "
                     f"{r['sample_seconds']['mean']:.1f} | {speed} | {r['history_frames_mean']:.1f} / "
                     f"{r['history_frames_last']} | {r['prefilled_mean']:.1f} | {r['peak_gib']:.1f} |")
    lines += ["", "Reading: encode = VAE (+ readout prefill for inject / memory_s1) of the frames new at this decision; "
              "conditions = current-frame prefill + history (kv_replay: only frames not yet in the episode cache are "
              "prefilled); sample = all denoising steps. total also includes batch assembly and host transfers. "
              "Memory overhead = steps<K> minus nohist<K>; step-distillation headroom = steps10 / steps1. nohist empties "
              "only the memory_v2 history: a memory_s1 base keeps reading its own frames "
              f"(memory_s1 frames per decision: {', '.join(f'{n} {r['s1_frames_mean']:.0f}' for n, r in results.items())})."]
    stamp = f"{datetime.now(BJ):%Y%m%d_%H%M}"
    report = O / "report" / f"LATENCY_{label}_{stamp}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report.with_suffix(".json").write_text(json.dumps({"label": label, "checkpoint": args.checkpoint, "demo": str(args.demo),
                                                       "gpu": snapshot, "results": results}, indent=1), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nLATENCY: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
