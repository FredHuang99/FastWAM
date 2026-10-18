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

    # background, one shard per GPU; GPU ids are those visible INSIDE this container (nvidia-smi -L here),
    # 'auto:N' picks N free ones; logs are written by the script under <output>/logs/
    python scripts/memory_v2/phase0_protocol.py launch --gpus auto:2 \
        --checkpoint source \
        --checkpoint A335=/migration/runs/a327_gpu4_v1/checkpoints/update_000335/mp_rank_00_model_states.pt \
        --output outputs/memory_v2/phase0
    python scripts/memory_v2/phase0_protocol.py status    --output outputs/memory_v2/phase0
    python scripts/memory_v2/phase0_protocol.py summarize --output outputs/memory_v2/phase0

    # foreground, one process (same flags; --shard i/n to split by hand, --limit N for a quick check)
    python scripts/memory_v2/phase0_protocol.py run --checkpoint source --output outputs/memory_v2/phase0
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
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


def ab_sample(ab, conditions, noise, shift, gate, steps=10):
    """ABModel.sample with an inference-shift override (identical to it at shift 1, gate 1)."""
    import torch
    actions = noise.to(torch.bfloat16)
    ts, ds = ab.action_scheduler.build_inference_schedule(steps, actions.device, actions.dtype, shift_override=shift)
    for t, d in zip(ts, ds):
        actions = ab.action_scheduler.step(ab.velocity(actions, t.expand(len(actions)), conditions, gate), d, actions)
    return actions.float()


class _Tee:
    """Mirror a stream into a log file owned by this script (no shell redirection needed)."""

    def __init__(self, stream, handle):
        self.stream, self.handle = stream, handle

    def write(self, text):
        self.handle.write(text)
        self.handle.flush()
        if self.stream is not None:
            try:
                self.stream.write(text)
                self.stream.flush()
            except (OSError, ValueError):
                self.stream = None
        return len(text)

    def flush(self):
        self.handle.flush()

    def isatty(self):
        return False


def open_log(out: Path, name: str) -> Path:
    folder = out / "logs"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    handle = path.open("a", encoding="utf-8", buffering=1)
    handle.write(f"\n===== {time.strftime('%Y-%m-%d %H:%M:%S')} pid={os.getpid()} "
                 f"CUDA_VISIBLE_DEVICES={os.environ.get('CUDA_VISIBLE_DEVICES')} argv={sys.argv[1:]}\n")
    sys.stdout = _Tee(sys.stdout, handle)
    sys.stderr = _Tee(sys.stderr, handle)
    return path


def parse_shard(text):
    try:
        index, count = (int(x) for x in text.split("/"))
    except ValueError:
        raise SystemExit(f"--shard must be i/n, got {text!r}") from None
    if count < 1 or not 0 <= index < count:
        raise SystemExit(f"--shard {text}: need 0 <= i < n (e.g. 0/2 and 1/2), the GPU id is set by CUDA_VISIBLE_DEVICES")
    return index, count


def run(args):
    index, count = parse_shard(args.shard)
    out = Path(args.output)
    log = open_log(out, f"run_{args.suite}_shard{index}of{count}.log")
    print(f"[phase0] log: {log}", flush=True)
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
    mine = [(i, r) for i, r in enumerate(rows) if i % count == index]
    device = "cuda:0"
    data = dense.ab_dataset(spec, identity, device)
    if args.suite == "s1":
        return run_s1(args, spec, identity, normaliser, rows, mine, data, index, count, out, device)
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


S1_VARIANTS = ("real", "gate0", "gate0.5", "current_only", "swap", "mean")
S1_FM_TAUS = (0.5, 0.9, 1.0)


def readout_stats(r):
    """Collapse geometry of one memory_s1 readout [32, D]."""
    x = r.float()
    n = x.norm(dim=1).clamp_min(1e-12)
    cosine = (x @ x.T) / (n[:, None] * n[None, :])
    return {"min_slot_cosine": float(cosine.min()),
            "centred_norm_percent": float(100 * (x - x.mean(0)).norm() / x.norm().clamp_min(1e-12))}


def run_s1(args, spec, identity, normaliser, rows, mine, data, index, count, out, device):
    """Does memory_s1 read history? Same base, its readout replaced in five ways (shift 1)."""
    import torch
    from fastwam.memory_v2 import dense

    def partner(i):
        row = rows[i]
        for step in range(1, len(rows)):
            other = rows[(i + step) % len(rows)]
            if other["episode_id"] != row["episode_id"] and other["task"] == row["task"]:
                return other
        return rows[(i + 1) % len(rows)]

    for text in args.checkpoint:
        label, path = parse_checkpoint(text)
        model, info = dense.load_ab_model(spec, path, device, hash_checkpoint=not args.no_hash)
        folder = out / label
        folder.mkdir(parents=True, exist_ok=True)
        with torch.no_grad():
            calibration = [r for r in rows if r["split"] == "train"][:args.calibration]
            raw = [model.conditions(data.at(r))[2] for r in calibration]
            model._eval_features.clear()
            readouts = [r.float() for r in raw]
            mean_float = torch.stack(readouts).mean(0)
            spread = float(torch.stack([(r - mean_float).norm() / r.norm() for r in readouts]).mean())
            mean_readout = mean_float.to(raw[0].dtype)
        (folder / f"S1_CHECKPOINT.shard{index}.json").write_text(json.dumps(
            {**info, "calibration_windows": len(calibration), "calibration_mean_relative_spread": spread}, indent=2))
        started, done = time.monotonic(), 0
        for i, row in mine:
            file = folder / "s1_cases" / f"{i:05d}.json"
            binding = {"window": row["id"], "checkpoint": info["sha256"], "dense": identity, "suite": "s1-v1",
                       "calibration": args.calibration}
            if file.is_file() and json.loads(file.read_text()).get("binding") == binding:
                continue
            b = data.at(row)
            with torch.no_grad():
                an, _, _, _ = model.random_inputs(b, row)
                kv, ctx, real = model.conditions(b)
                current_only = dict(b, history_latents=b["latent"], history_proprio=b["proprio"],
                                    frame_ids=b["t"][None].to(b["frame_ids"].dtype),
                                    history_valid=torch.ones(1, 1, dtype=torch.bool, device=b["latent"].device))
                model._eval_features.clear()
                single = model.conditions(current_only)[2]
                swapped = model.conditions(data.at(partner(i)))[2]
                options = {"real": (real, 1.0), "gate0": (real, 0.0), "gate0.5": (real, 0.5),
                           "current_only": (single, 1.0), "swap": (swapped, 1.0), "mean": (mean_readout, 1.0)}
                valid = b["action_valid"][0]
                actions = b["actions"].to(torch.bfloat16)
                case = {**row, "kind": dense.window_kind(row), "checkpoint": label, "binding": binding,
                        "variants": {}, "readout": readout_stats(real[0])}
                for name, (readout, scale) in options.items():
                    conditions = (kv, ctx, readout)
                    sample = ab_sample(model, conditions, an, 1.0, scale, steps=args.steps)
                    metrics = dense.window_metrics(sample[0], b["actions"][0], valid, normaliser)
                    for tau in S1_FM_TAUS:
                        t = torch.tensor([1000 * tau], device=actions.device, dtype=torch.bfloat16)
                        noisy = model.action_scheduler.add_noise(actions, an, t)
                        pred = model.velocity(noisy, t, conditions, scale)
                        wanted = model.action_scheduler.training_target(actions, an, t)
                        metrics[f"fm_tau{tau:g}"] = float((pred.float() - wanted.float()).square()[0, valid].mean())
                    metrics["readout_relative_change"] = float((readout.float() - real.float()).norm() / real.float().norm())
                    case["variants"][name] = metrics
                model._eval_features.clear()
            file.parent.mkdir(parents=True, exist_ok=True)
            temp = file.with_name(file.name + ".partial")
            temp.write_text(json.dumps(case, indent=1))
            temp.replace(file)
            done += 1
            if done % 10 == 0:
                rate = (time.monotonic() - started) / done
                print(f"[phase0-s1] {label} shard {index}/{count}: {done}/{len(mine)} windows, {rate:.1f}s/window", flush=True)
        del model
        torch.cuda.empty_cache()
    print("[phase0-s1] shard complete", flush=True)


def summarize_s1(out: Path):
    keys = ("arm_rmse_rad", "gripper_rmse", "prefix24_arm_rmse_rad", "fm_tau0.5", "fm_tau0.9", "fm_tau1",
            "readout_relative_change")
    lines = ["# Phase-0b: does memory_s1 read history?", "",
             "Same base; only the memory_s1 readout fed to its injectors changes. shift 1, same noise as the dense evaluation.",
             "`current_only` = history of the current frame only; `swap` = readout of a window from another episode "
             "(same task); `mean` = one constant readout (mean over calibration windows).", ""]
    report = {}
    for folder in sorted(p for p in out.iterdir() if (p / "s1_cases").is_dir()):
        cases = [json.loads(p.read_text()) for p in sorted((folder / "s1_cases").glob("*.json"))]
        if not cases:
            continue
        entry = {"windows": len(cases), "variants": {}}
        for v in S1_VARIANTS:
            entry["variants"][v] = {k: sum(c["variants"][v][k] for c in cases) / len(cases) for k in keys}
            kinds = {}
            for c in cases:
                kinds.setdefault(c["kind"], []).append(c["variants"][v]["arm_rmse_rad"])
            entry["variants"][v]["arm_by_kind"] = {k: sum(x) / len(x) for k, x in kinds.items()}
        entry["readout"] = {k: sum(c["readout"][k] for c in cases) / len(cases) for k in cases[0]["readout"]}
        report[folder.name] = entry
        lines += [f"## {folder.name} ({len(cases)} windows)", "",
                  "| variant | arm RMSE | gripper | prefix24 arm | FM t0.5 | FM t0.9 | FM t1 | readout change | initial arm |",
                  "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for v in S1_VARIANTS:
            e = entry["variants"][v]
            lines.append(f"| {v} | {e['arm_rmse_rad']:.4f} | {e['gripper_rmse']:.4f} | {e['prefix24_arm_rmse_rad']:.4f} | "
                         f"{e['fm_tau0.5']:.4f} | {e['fm_tau0.9']:.4f} | {e['fm_tau1']:.4f} | {e['readout_relative_change']:.3f} | "
                         f"{e['arm_by_kind'].get('initial', float('nan')):.4f} |")
        r = entry["readout"]
        real = entry["variants"]["real"]["arm_rmse_rad"]
        notes = [f"readout geometry: min slot cosine {r['min_slot_cosine']:.5f}, centred norm {r['centred_norm_percent']:.2f}%"]
        for v in ("current_only", "swap", "mean"):
            d = entry["variants"][v]["arm_rmse_rad"] / max(real, 1e-12) - 1
            notes.append(f"{v} vs real arm RMSE {d:+.1%}")
        blind = all(abs(entry["variants"][v]["arm_rmse_rad"] / max(real, 1e-12) - 1) < 0.05 for v in ("current_only", "swap", "mean"))
        notes.append("VERDICT: memory_s1 is history-blind (a constant adapter); keep it frozen as part of the base."
                     if blind else
                     "VERDICT: memory_s1 output depends on its inputs; treat the frozen s1 base as a memory baseline too.")
        entry["notes"] = notes
        lines += ["", *[f"- {n}" for n in notes], ""]
    (out / "S1_SUMMARY.json").write_text(json.dumps(report, indent=2))
    (out / "S1_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def summarize(args):
    if args.suite == "s1":
        return summarize_s1(Path(args.output))
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


def common_flags(args):
    flags = ["--output", args.output, "--root", args.root, "--code", args.code, "--dense-output", args.dense_output,
             "--steps", str(args.steps), "--suite", args.suite, "--calibration", str(args.calibration)]
    for c in args.checkpoint:
        flags += ["--checkpoint", c]
    if args.limit:
        flags += ["--limit", str(args.limit)]
    if args.no_verify:
        flags.append("--no-verify")
    if args.no_hash:
        flags.append("--no-hash")
    return flags


def visible_gpus():
    """GPUs visible in THIS container, in PCI order: [{index, uuid, name, used_mib, total_mib}].

    nvidia-smi on the host numbers all host GPUs; inside a container only the
    passed-through ones exist and are renumbered from 0, so host ids do not apply.
    """
    try:
        text = subprocess.run(["nvidia-smi", "--query-gpu=index,uuid,name,memory.used,memory.total",
                               "--format=csv,noheader,nounits"], capture_output=True, text=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"nvidia-smi failed inside this environment: {error}") from None
    gpus = []
    for line in text.strip().splitlines():
        index, uuid, name, used, total = (x.strip() for x in line.split(","))
        gpus.append({"index": index, "uuid": uuid, "name": name, "used_mib": int(used), "total_mib": int(total)})
    return gpus


def choose_gpus(spec: str, count: int, free_mib: int):
    gpus = visible_gpus()
    table = "\n".join(f"  index={g['index']} {g['name']} used={g['used_mib']}/{g['total_mib']} MiB {g['uuid']}" for g in gpus)
    usable = [g for g in gpus if "A100" in g["name"] or "H100" in g["name"] or "H200" in g["name"]]
    if spec.startswith("auto"):
        free = [g for g in usable if g["used_mib"] <= free_mib]
        want = int(spec.split(":")[1]) if ":" in spec else (count or len(free))
        if want < 1 or len(free) < want:
            raise SystemExit(f"Need {want} free GPUs (<= {free_mib} MiB used); visible in this container:\n{table}")
        return free[:want], table
    chosen = []
    for item in (x.strip() for x in spec.split(",") if x.strip()):
        match = [g for g in gpus if item in (g["index"], g["uuid"])]
        if not match:
            raise SystemExit(f"GPU {item!r} is not visible in this container (host nvidia-smi ids do not apply). "
                             f"Visible:\n{table}\nUse these indices/UUIDs, or --gpus auto.")
        g = match[0]
        if g["used_mib"] > free_mib:
            raise SystemExit(f"GPU {item} already uses {g['used_mib']} MiB; pick a free one or raise --free-mib.\n{table}")
        chosen.append(g)
    return chosen, table


def launch(args):
    """Start one detached `run` per GPU; each writes <output>/logs/run_shard{k}of{n}.log itself."""
    shard_ids = [int(x) for x in args.shard_ids.split(",")] if args.shard_ids else None
    gpus, table = choose_gpus(args.gpus, len(shard_ids) if shard_ids else 0, args.free_mib)
    shard_ids = shard_ids or list(range(len(gpus)))
    total = args.num_shards or len(shard_ids)
    if len(shard_ids) != len(gpus) or any(not 0 <= k < total for k in shard_ids):
        raise SystemExit(f"{len(gpus)} GPU(s) for shard ids {shard_ids} of {total}: need one GPU per shard id, ids < num-shards")
    print("[launch] GPUs visible in this container:\n" + table)
    out = Path(args.output)
    (out / "logs").mkdir(parents=True, exist_ok=True)
    processes = []
    for k, gpu in zip(shard_ids, gpus):
        # Select by UUID: immune to CUDA vs nvidia-smi ordering differences.
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu["uuid"], CUDA_DEVICE_ORDER="PCI_BUS_ID")
        cmd = [sys.executable, "-u", str(Path(__file__).resolve()), "run", "--shard", f"{k}/{total}", *common_flags(args)]
        proc = subprocess.Popen(cmd, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True, cwd=os.getcwd())
        processes.append({"pid": proc.pid, "gpu": gpu["index"], "uuid": gpu["uuid"], "shard": f"{k}/{total}",
                          "log": str(out / "logs" / f"run_{args.suite}_shard{k}of{total}.log"), "cmd": cmd, "proc": proc,
                          "suite": args.suite})
    launch_file = out / "LAUNCH.json"
    history = json.loads(launch_file.read_text()) if launch_file.is_file() else {"processes": []}
    history.setdefault("processes", [])
    started = {(q["suite"], q["shard"]) for q in processes}
    history["processes"] = [p for p in history["processes"] if (p.get("suite", "protocol"), p["shard"]) not in started]
    history["processes"] += [{k: v for k, v in p.items() if k != "proc"} for p in processes]
    history["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    launch_file.write_text(json.dumps(history, indent=2))
    time.sleep(args.check_seconds)
    failed = False
    for p in processes:
        code = p["proc"].poll()
        state = "running" if code is None else f"EXITED code={code}"
        failed |= code not in (None, 0)
        print(f"[launch] gpu={p['gpu']} shard={p['shard']} pid={p['pid']} {state}  log={p['log']}")
    if failed:
        print("[launch] a shard stopped early; read its log, or rerun that shard with `run` in the foreground.")
    print(f"[launch] progress: python {Path(__file__).name} status --output {out}")


def process_alive(pid) -> bool:
    """True only for a live process (a zombie keeps /proc/<pid> until reaped)."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return False
    return stat.rsplit(")", 1)[-1].split()[0] not in ("Z", "X")


def status(args):
    out = Path(args.output)
    launch_file = out / "LAUNCH.json"
    if launch_file.is_file():
        for p in json.loads(launch_file.read_text())["processes"]:
            alive = process_alive(p["pid"])
            tail = ""
            log = Path(p["log"])
            if log.is_file():
                lines = [x for x in log.read_text(errors="replace").splitlines() if x.strip()]
                tail = lines[-1] if lines else ""
            print(f"gpu={p['gpu']} shard={p['shard']} pid={p['pid']} {'running' if alive else 'stopped'} | {tail}")
    total = None
    try:
        from fastwam.memory_v2 import dense
        spec = dense.DenseSpec(root=Path(args.root), code=Path(args.code), output=Path(args.dense_output),
                               verify_identity=False)
        total = len(dense.windows(spec))
        if args.limit:
            total = min(total, args.limit)
    except Exception:  # noqa: BLE001 - status must work without the dense host
        pass
    sub = "s1_cases" if args.suite == "s1" else "cases"
    for folder in sorted(p for p in out.iterdir() if (p / sub).is_dir()) if out.is_dir() else []:
        done = len(list((folder / sub).glob("*.json")))
        print(f"{folder.name} [{args.suite}]: {done}/{total if total is not None else '?'} windows")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("launch", "run", "status", "summarize"))
    parser.add_argument("--gpus", default="auto", help="launch: 'auto' / 'auto:N' (free GPUs in this container) "
                        "or comma-separated container indices/UUIDs, one shard each")
    parser.add_argument("--shard-ids", default="", help="launch: which shard ids to start (default 0..len(gpus)-1)")
    parser.add_argument("--num-shards", type=int, default=0, help="launch: total shards n (default: number started)")
    parser.add_argument("--free-mib", type=int, default=2000, help="launch: a GPU counts as free below this usage")
    parser.add_argument("--check-seconds", type=int, default=30, help="launch: wait before checking the shards")
    parser.add_argument("--checkpoint", action="append", default=[], help="'source' or LABEL=PATH (repeatable)")
    parser.add_argument("--output", default="outputs/memory_v2/phase0")
    parser.add_argument("--root", default="/workspace/FastWAM")
    parser.add_argument("--code", default="/restore-tmp/dense_joint_v1")
    parser.add_argument("--dense-output", default="/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")
    parser.add_argument("--shard", default="0/1", help="i/n: this process handles windows with index %% n == i")
    parser.add_argument("--limit", type=int, default=0, help="first N windows only (quick check)")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--suite", choices=("protocol", "s1"), default="protocol",
                        help="protocol: shift x gate x prefix; s1: does memory_s1 read history (readout swaps)")
    parser.add_argument("--calibration", type=int, default=32, help="s1: train windows averaged for the constant readout")
    parser.add_argument("--no-verify", action="store_true", help="skip dense identity re-hashing")
    parser.add_argument("--no-hash", action="store_true", help="skip hashing large checkpoint files")
    args = parser.parse_args()
    if args.command in ("run", "launch") and not args.checkpoint:
        args.checkpoint = ["source"]
    {"launch": launch, "run": run, "status": status, "summarize": summarize}[args.command](args)


if __name__ == "__main__":
    main()
