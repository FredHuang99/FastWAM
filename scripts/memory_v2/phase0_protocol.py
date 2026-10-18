"""Phase-0 protocol check on the dense-joint fixed offline windows.

For each checkpoint (C+256 source, A335, ...) and each fixed window of the dense
run (WINDOWS.json, 401 windows), with the SAME noise draw as the dense evaluation:

  * inference shift 1 vs 5          (released base was trained at action shift 5,
                                      the dense C/A recipe trains and infers at 1)
  * memory_s1 injection on vs off   (gate_scale 1 / 0: localises a regression to
                                      the ActionDiT or to the memory path)
  * executed prefix 16 vs 24 steps  (offline proxy of execute 16 / 24)
  * FM error of the velocity field at tau 0.1 / 0.5 / 0.9 / 0.95 / 1.0, per gate.

Everything reuses the dense delivery's ABModel, Dataset.at() and random_inputs(),
so `gate1_shift1` reproduces the dense EVALUATION.json numbers exactly.
Resumable: one JSON per (checkpoint, window). Shardable across GPUs.

    python scripts/memory_v2/phase0_protocol.py run \
        --checkpoint source \
        --checkpoint A335=/migration/runs/a327_gpu4_v1/checkpoints/update_000335/mp_rank_00_model_states.pt \
        --output outputs/memory_v2/phase0 [--shard 0/2] [--limit 40]
    python scripts/memory_v2/phase0_protocol.py summarize --output outputs/memory_v2/phase0
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

SHIFTS = (1.0, 5.0)
GATES = (1.0, 0.0)
FM_TAUS = (0.1, 0.5, 0.9, 0.95, 1.0)
METRICS = ("arm_rmse_rad", "gripper_rmse", "prefix16_arm_rmse_rad", "prefix24_arm_rmse_rad",
           "prefix16_gripper_rmse", "prefix24_gripper_rmse")


def parse_checkpoint(text):
    if text == "source":
        return "source", "source"
    label, _, path = text.partition("=")
    if not path:
        raise SystemExit(f"--checkpoint must be 'source' or LABEL=PATH, got {text!r}")
    return label, path


def dense_dataset(spec, identity, device):
    from data_path import Dataset  # dense_joint_v1/data_path.py
    from collections import OrderedDict

    class Bound(Dataset):                       # same as the migration tool's HistoricalDataset
        def __init__(self):
            self.out = spec.output
            self.device = device
            self.records = {r["episode_id"]: r for r in json.loads((spec.output / "RECORDS.json").read_text())}
            self.loaded = OrderedDict()
            self.ident = identity
    return Bound()


def ab_sample(ab, conditions, noise, shift, gate, steps=10):
    """ABModel.sample with an inference-shift override (identical to it at shift 1, gate 1)."""
    import torch
    actions = noise.to(torch.bfloat16)
    ts, ds = ab.action_scheduler.build_inference_schedule(steps, actions.device, actions.dtype, shift_override=shift)
    for t, d in zip(ts, ds):
        actions = ab.action_scheduler.step(ab.velocity(actions, t.expand(len(actions)), conditions, gate), d, actions)
    return actions.float()


def run(args):
    import torch
    from fastwam.memory_v2 import dense
    spec = dense.DenseSpec(root=Path(args.root), code=Path(args.code), output=Path(args.dense_output),
                           verify_identity=not args.no_verify)
    _, identity = dense.bind(spec)
    from fastwam.memory_s1.common import ReleaseNormalizer
    normaliser = ReleaseNormalizer(dense.dense_config(spec)["paths"]["stats"])
    rows = dense.windows(spec)
    if args.limit:
        rows = rows[:args.limit]
    index, count = (int(x) for x in args.shard.split("/"))
    mine = [(i, r) for i, r in enumerate(rows) if i % count == index]
    out = Path(args.output)
    device = "cuda:0"
    data = dense_dataset(spec, identity, device)
    for text in args.checkpoint:
        label, path = parse_checkpoint(text)
        model, info = dense.load_ab_model(spec, path, device, hash_checkpoint=not args.no_hash)
        folder = out / label
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"CHECKPOINT.shard{index}.json").write_text(json.dumps(info, indent=2))
        started = time.monotonic()
        done = 0
        for i, row in mine:
            file = folder / "cases" / f"{i:05d}.json"
            binding = {"window": row["id"], "checkpoint": info["sha256"], "dense": identity}
            if file.is_file() and json.loads(file.read_text()).get("binding") == binding:
                continue
            b = data.at(row)
            with torch.no_grad():
                an, _, _, _ = model.random_inputs(b, row)
                conditions = model.conditions(b)
                valid = b["action_valid"][0]
                case = {**row, "kind": dense.window_kind(row), "checkpoint": label, "binding": binding,
                        "variants": {}, "fm": {}}
                for gate in GATES:
                    for shift in SHIFTS:
                        t0 = time.monotonic()
                        sample = ab_sample(model, conditions, an, shift, gate, steps=args.steps)
                        metrics = dense.window_metrics(sample[0], b["actions"][0], valid, normaliser)
                        metrics["seconds"] = time.monotonic() - t0
                        case["variants"][f"gate{gate:g}_shift{shift:g}"] = metrics
                    fm = []
                    actions = b["actions"].to(torch.bfloat16)
                    for tau in FM_TAUS:
                        t = torch.tensor([1000 * tau], device=actions.device, dtype=torch.bfloat16)
                        noisy = model.action_scheduler.add_noise(actions, an, t)
                        pred = model.velocity(noisy, t, conditions, gate)
                        wanted = model.action_scheduler.training_target(actions, an, t)
                        fm.append(float((pred.float() - wanted.float()).square()[0, valid].mean()))
                    case["fm"][f"gate{gate:g}"] = dict(zip((f"tau{x:g}" for x in FM_TAUS), fm))
            file.parent.mkdir(parents=True, exist_ok=True)
            temp = file.with_name(file.name + ".partial")
            temp.write_text(json.dumps(case, indent=1))
            temp.replace(file)
            done += 1
            if done % 10 == 0:
                rate = (time.monotonic() - started) / done
                print(f"[phase0] {label} shard {index}/{count}: {done}/{len(mine)} windows, {rate:.1f}s/window", flush=True)
        model._eval_features.clear()
        del model
        torch.cuda.empty_cache()
    print("[phase0] shard complete", flush=True)


def summarize(args):
    out = Path(args.output)
    report = {"checkpoints": {}, "scope": "fixed dense offline windows; same noise as the dense evaluation; not task success"}
    lines = ["# Phase-0 offline protocol check", "",
             "Mean over windows. arm RMSE in rad (denormalised), gripper in action units. "
             "`gate0` = memory_s1 injection off, `shift5` = inference schedule shift 5.", ""]
    for folder in sorted(p for p in out.iterdir() if (p / "cases").is_dir()):
        cases = [json.loads(p.read_text()) for p in sorted((folder / "cases").glob("*.json"))]
        if not cases:
            continue
        variants = sorted(cases[0]["variants"])
        entry = {"windows": len(cases), "variants": {}, "fm": {}, "by_group": {}}
        for v in variants:
            entry["variants"][v] = {m: sum(c["variants"][v][m] for c in cases) / len(cases) for m in METRICS}
            groups = {}
            for c in cases:
                for key in (f"{c['task']}/{c['split']}", f"kind/{c['kind']}"):
                    groups.setdefault(key, []).append(c["variants"][v])
            entry["by_group"][v] = {k: {"windows": len(xs), **{m: sum(x[m] for x in xs) / len(xs) for m in METRICS}}
                                    for k, xs in sorted(groups.items())}
        for g in sorted(cases[0]["fm"]):
            entry["fm"][g] = {t: sum(c["fm"][g][t] for c in cases) / len(cases) for t in cases[0]["fm"][g]}
        report["checkpoints"][folder.name] = entry
        lines += [f"## {folder.name} ({len(cases)} windows)", "",
                  "| variant | arm RMSE | gripper RMSE | prefix16 arm | prefix24 arm | initial arm | event arm | ordinary arm |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for v in variants:
            e = entry["variants"][v]
            kinds = entry["by_group"][v]
            kind = lambda k, kinds=kinds: f"{kinds[f'kind/{k}']['arm_rmse_rad']:.4f}" if f"kind/{k}" in kinds else "-"
            lines.append(f"| {v} | {e['arm_rmse_rad']:.4f} | {e['gripper_rmse']:.4f} | {e['prefix16_arm_rmse_rad']:.4f} | "
                         f"{e['prefix24_arm_rmse_rad']:.4f} | {kind('initial')} | {kind('event')} | {kind('ordinary')} |")
        lines += ["", "| FM error | " + " | ".join(next(iter(entry["fm"].values())).keys()) + " |",
                  "|---|" + "---:|" * len(next(iter(entry["fm"].values()))) ]
        for g, values in entry["fm"].items():
            lines.append(f"| {g} | " + " | ".join(f"{x:.4f}" for x in values.values()) + " |")
        lines.append("")
    # Decision helpers.
    notes = []
    for name, e in report["checkpoints"].items():
        v = e["variants"]
        if "gate1_shift1" in v and "gate1_shift5" in v:
            d = v["gate1_shift5"]["arm_rmse_rad"] / max(v["gate1_shift1"]["arm_rmse_rad"], 1e-12) - 1
            notes.append(f"{name}: shift5 vs shift1 arm RMSE {d:+.1%}")
        if "gate1_shift1" in v and "gate0_shift1" in v:
            d = v["gate0_shift1"]["arm_rmse_rad"] / max(v["gate1_shift1"]["arm_rmse_rad"], 1e-12) - 1
            notes.append(f"{name}: memory_s1 off vs on arm RMSE {d:+.1%}")
    names = list(report["checkpoints"])
    if "source" in names:
        base = report["checkpoints"]["source"]["variants"]
        for name in names:
            if name == "source":
                continue
            for v in ("gate1_shift1", "gate0_shift1"):
                if v in base and v in report["checkpoints"][name]["variants"]:
                    r = report["checkpoints"][name]["variants"][v]["arm_rmse_rad"] / max(base[v]["arm_rmse_rad"], 1e-12)
                    notes.append(f"{name} / source arm RMSE ({v}): x{r:.2f}")
    report["notes"] = notes
    lines += ["## Reading", ""] + [f"- {n}" for n in notes] + [
        "", "Rules: if A335 is still far worse than source with gate0, the ActionDiT itself regressed "
        "(not the memory path). If shift5 beats shift1 by >5% on the source, re-open the shift question "
        "for the base; otherwise keep shift 1 (the dense/C training shift)."]
    (out / "PHASE0_SUMMARY.json").write_text(json.dumps(report, indent=2))
    (out / "PHASE0_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("run", "summarize"))
    parser.add_argument("--checkpoint", action="append", default=[], help="'source' or LABEL=PATH (repeatable)")
    parser.add_argument("--output", default="outputs/memory_v2/phase0")
    parser.add_argument("--root", default="/workspace/FastWAM")
    parser.add_argument("--code", default="/restore-tmp/dense_joint_v1")
    parser.add_argument("--dense-output", default="/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")
    parser.add_argument("--shard", default="0/1", help="i/n: this process handles windows with index %% n == i")
    parser.add_argument("--limit", type=int, default=0, help="first N windows only (quick check)")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--no-verify", action="store_true", help="skip dense identity re-hashing")
    parser.add_argument("--no-hash", action="store_true", help="skip hashing large checkpoint files")
    args = parser.parse_args()
    if args.command == "run":
        if not args.checkpoint:
            args.checkpoint = ["source"]
        run(args)
    else:
        summarize(args)


if __name__ == "__main__":
    main()
