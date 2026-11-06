"""Acceptance checks of kv_replay (plan v7 N1) on the real dense backbone (GPU; read only, nothing is trained).

1. Layer replica: for every action layer, L(o_A) rebuilt from the MoT primitives (replay.mot_replay_parts) vs
   ABModel's own 'action' call on the same input (probe batch, tau = 0.7): relative L2 per layer.
   Pass: max <= 2e-2 (both bf16; the delta g * (L(o_AH) - L(o_A)) cancels a common offset, so this is a sanity bound).
2. Zero start: on / null / off velocities bit-identical (torch.equal) at three noise levels.
3. Gates opened to 0.5 (test only): the velocity changes (relative L2 on vs off > 1e-3) and history keys get
   attention mass; per-layer history mass at tau 0.7 on layer 0 / 15 / 29.
4. Cost: conditions + one velocity per micro-batch, inject (the run's own config) vs kv_replay, and peak memory.

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/replay_check.py --run v2_press_cf [--micro 2]
Writes outputs/memory_v2/report/REPLAY_CHECK_<time>.md (+ .json); exit 1 if check 1 or 2 fails.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
BJ = timezone(timedelta(hours=8))


def build(run, sets, device):
    from fastwam.memory_v2.train_v2 import DenseBackend, load_config
    saved = json.loads((O / run / "CONFIG.json").read_text(encoding="utf-8"))
    path = O / "replay_check" / f"{run}_config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(saved["config"], indent=1), encoding="utf-8")
    cfg = load_config(path, sets)
    return DenseBackend(cfg, device, train_action=False), cfg


def timed(fn, torch):
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    out = fn()
    torch.cuda.synchronize()
    return out, time.perf_counter() - t0


def main():
    import torch
    from fastwam.memory_v2.replay import mot_replay_parts
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default="v2_press_cf", help="run whose saved config is the base (stage 1, no init_memory)")
    ap.add_argument("--micro", type=int, default=2)
    args = ap.parse_args()
    device = torch.device("cuda:0")
    lines, result, ok = [f"# kv_replay acceptance ({datetime.now(BJ):%F %T}; config of {args.run})", ""], {}, True

    # ---- 4a: inject cost on the run's own config
    backend, cfg = build(args.run, [f"schedule.micro_batch={args.micro}"], device)
    rows = backend.train_rows()[:: max(1, len(backend.train_rows()) // args.micro)][:args.micro]
    batch = backend.batch(rows)
    torch.cuda.reset_peak_memory_stats()
    with torch.no_grad():
        model = backend.model
        model.eval()
        x = torch.randn(batch["actions"].shape, device=device)
        t = torch.full((x.shape[0],), 700.0, device=device)
        c, enc = timed(lambda: model.conditions(batch), torch)
        _, vel = timed(lambda: model.velocity(x, t, c, "on"), torch)
    result["inject"] = {"conditions_s": enc, "velocity_s": vel, "peak_gb": torch.cuda.max_memory_allocated() / 2**30,
                        "history_frames": int(batch["history_valid"].sum())}
    del backend, model, c, batch
    torch.cuda.empty_cache()

    # ---- kv_replay model on the same rows
    backend, cfg = build(args.run, [f"schedule.micro_batch={args.micro}", "memory_v2.memory.read=kv_replay"], device)
    model = backend.model
    model.eval()
    batch = backend.batch(rows)
    torch.cuda.reset_peak_memory_stats()
    with torch.no_grad():
        c, enc = timed(lambda: model.conditions(batch), torch)
        _, vel = timed(lambda: model.velocity(x, t, c, "on"), torch)
    result["kv_replay"] = {"conditions_s": enc, "velocity_s_zero_gate": vel,
                           "peak_gb": torch.cuda.max_memory_allocated() / 2**30,
                           "history_frames": int(batch["history_valid"].sum())}

    # ---- 1: replica vs ABModel 'action', every layer
    adapter = model.backbone
    mot = adapter.ab.backbone.mot
    state = c.replay
    rel = []
    with torch.no_grad():
        h, aux = adapter.prepare(x, t, c.context)
        keys, values, _ = c.current_kv
        for index in range(adapter.num_action_layers):
            mod, ctx, ctx_mask, freqs = aux
            ref = adapter.ab.call("action", h, freqs, mod, ctx, ctx_mask, keys[index], values[index], index=index,
                                  checkpointed=False)
            slot = model.memory.replay.slot(index)
            hk, hv = model.memory.replay.layer_kv(state, slot)
            _, mine = mot_replay_parts(mot, index, h, aux, keys[index], values[index], hk, hv, state.token_valid)
            rel.append(float((mine.float() - ref.float()).norm() / ref.float().norm().clamp_min(1e-12)))
            h = ref
    result["replica_rel_l2"] = rel
    replica_ok = max(rel) <= 2e-2
    ok = ok and replica_ok
    lines += ["## 1. Layer replica vs ABModel 'action'", "",
              f"max relative L2 over {len(rel)} layers: {max(rel):.2e} (layer {rel.index(max(rel))}); "
              f"median {sorted(rel)[len(rel) // 2]:.2e} -> **{'PASS' if replica_ok else 'FAIL'}** (<= 2e-2)", ""]

    # ---- 2: zero start
    exact = True
    with torch.no_grad():
        for tau in (1.0, 0.7, 0.3):
            tt = torch.full((x.shape[0],), 1000.0 * tau, device=device)
            off = model.velocity(x, tt, c, "off")
            exact = exact and torch.equal(model.velocity(x, tt, c, "on"), off) and torch.equal(model.velocity(x, tt, c, "null"), off)
    result["zero_start_exact"] = exact
    ok = ok and exact
    lines += ["## 2. Zero start: on == null == off (bit-identical)", "", f"**{'PASS' if exact else 'FAIL'}**", ""]

    # ---- 3: gates opened (test only)
    with torch.no_grad():
        model.memory.replay.gate.net[2].bias.fill_(0.5)
        on, open_s = timed(lambda: model.velocity(x, t, c, "on"), torch)
        off = model.velocity(x, t, c, "off")
        change = float((on.float() - off.float()).norm() / off.float().norm().clamp_min(1e-12))
        mass = {}
        h, aux = adapter.prepare(x, t, c.context)
        last = adapter.num_action_layers - 1
        for index in range(adapter.num_action_layers):        # base trajectory; history mass of the joint softmax
            if index in (0, 15, last):
                mod, ctx, ctx_mask, freqs = aux
                expert = mot.mixtures["action"]
                block = expert.blocks[index]
                # 11-07: the dense ABModel keeps fp32 ActionDiT weights (A100 run of 11-06 crashed here with
                # "mat1 and mat2 must have the same dtype"); same bf16 autocast as replay.mot_replay_parts
                low = block.self_attn.q.weight.dtype == torch.bfloat16
                with torch.autocast(device_type=h.device.type, dtype=torch.bfloat16, enabled=not low):
                    q = mot._build_expert_attention_io(expert=expert, block=block, x=h, freqs=freqs, t_mod=mod)[0]
                hk, _ = model.memory.replay.layer_kv(state, model.memory.replay.slot(index))
                k_all = torch.cat((hk, keys[index]), 1).float()
                nh = mot.num_heads
                d = q.shape[-1] // nh
                qh = q.float().reshape(q.shape[0], q.shape[1], nh, d).transpose(1, 2)
                kh = k_all.reshape(k_all.shape[0], k_all.shape[1], nh, d).transpose(1, 2)
                logits = qh @ kh.transpose(-1, -2) / d ** 0.5
                valid = torch.cat((state.token_valid, torch.ones(keys[index].shape[:2], dtype=torch.bool, device=device)), 1)
                probs = logits.masked_fill(~valid[:, None, None, :], float("-inf")).softmax(-1)
                mass[index] = round(float(probs[..., :hk.shape[1]].sum(-1).mean()), 4)
            h = adapter.block(index, h, aux, c.current_kv)
    result["open"] = {"relative_change": change, "history_mass": mass, "velocity_s_open": open_s}
    lines += ["## 3. Gates at 0.5 (test only)", "", f"velocity relative change on vs off: {change:.3e}; "
              f"history attention mass (joint softmax over [history; current] keys, base trajectory): {mass}", ""]

    # ---- 4: cost
    i, r = result["inject"], result["kv_replay"]
    lines += ["## 4. Cost per micro-batch (no grad)", "",
              "| path | history frames | conditions s | velocity s | peak GB |", "|---|---|---|---|---|",
              f"| inject (run config) | {i['history_frames']} | {i['conditions_s']:.2f} | {i['velocity_s']:.2f} | {i['peak_gb']:.1f} |",
              f"| kv_replay, gate 0 | {r['history_frames']} | {r['conditions_s']:.2f} | {r['velocity_s_zero_gate']:.2f} | {r['peak_gb']:.1f} |",
              f"| kv_replay, gate 0.5 | {r['history_frames']} | - | {open_s:.2f} | - |", ""]
    lines.append(f"**overall: {'PASS' if ok else 'FAIL'}** (checks 1 and 2)")
    rep = O / "report" / f"REPLAY_CHECK_{datetime.now(BJ):%Y%m%d_%H%M}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rep.with_suffix(".json").write_text(json.dumps(result, indent=1, default=str), encoding="utf-8")
    print("\n".join(lines))
    print(f"REPLAY_CHECK: {rep}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
