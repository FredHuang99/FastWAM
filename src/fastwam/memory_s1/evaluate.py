"""Fixed offline validation, frozen-cache audit, and intervention measurements."""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import torch

from .common import atomic_json, load_config, read_json, seed_for, sha256, fingerprint, make_cache_contract
from .data import CachedEpisodes, collate, history_variant, load_evidence


def deterministic_noise(seed, step, slots, device, purpose="noise"):
    noises, times = [], []
    for slot in slots:
        generator = torch.Generator(device="cpu").manual_seed(seed_for(seed, step, slot, purpose))
        noises.append(torch.randn(32, 14, generator=generator))
        times.append(torch.rand((), generator=generator))
    return torch.stack(noises).to(device), torch.stack(times).to(device)


@torch.no_grad()
def validate(model, dataset, cfg, device, interventions=False, evidence=None, period=8, progress_path=None, stop_root=None):
    model.eval()
    count = cfg["validation_anchors_per_task"] * 2
    results, bins = [], [[] for _ in range(5)]
    conditions = ["full", "gate_zero", "current_only"] if interventions else ["full"]
    if evidence is not None:
        conditions += ["delete_critical", "delete_irrelevant"]
    if progress_path and Path(progress_path).exists():
        saved = read_json(progress_path)
        if saved["period"] != period or saved["cache_signature"] != dataset.signature:
            raise ValueError("Offline validation cursor identity mismatch.")
        results = saved["episodes"]
        for row in results:
            bins[min(4, int(row["tau"] * 5))].append(row["conditions"]["full"]["fm_unweighted"])
    for slot in range(len(results), count):
        if stop_root and (Path(stop_root) / "STOP_REQUESTED").exists():
            from .eval_state import EvaluationInterrupted
            raise EvaluationInterrupted("Stopped at an offline-validation anchor boundary.")
        original = dataset.sample(0, slot, validation=True)
        record = next(r for r in dataset.by_task[original["task"]] if r["episode_id"] == original["episode_id"])
        sample = dataset.at(record, int(original["t"]), period=period)
        noise, tau = deterministic_noise(17, 0, [slot], device, "validation-noise")
        entry = {"episode_id": sample["episode_id"], "t": int(sample["t"]), "task": sample["task"], "period": period, "tau": float(tau[0]), "read_frame_ids": sample["frame_ids"].tolist(), "conditions": {}}
        for condition in conditions:
            annotation = None if evidence is None else evidence.get("offline", {}).get(sample["episode_id"])
            changed = history_variant(sample, condition, annotation)
            batch = collate([changed], device)
            loss, diagnostic = model(batch, noise, tau, gate_scale=0 if condition == "gate_zero" else 1)
            actions, _ = model.sample(batch, noise, gate_scale=0 if condition == "gate_zero" else 1)
            valid = batch["action_valid"]
            mse = ((actions - batch["actions"]).square() * valid[..., None]).sum() / (14 * valid.sum())
            error = float(diagnostic["unweighted_fm"].mean())
            entry["conditions"][condition] = {"fm": float(loss), "fm_unweighted": error,
                                               "sample_mse": float(mse), "finite_actions": bool(torch.isfinite(actions).all()),
                                               "deleted_frame_ids": sorted(set(sample["frame_ids"].tolist()) - set(changed["frame_ids"].tolist()))}
            if condition == "full":
                bins[min(4, int(float(tau[0]) * 5))].append(error)
        results.append(entry)
        if progress_path:
            atomic_json(progress_path, {"period": period, "cache_signature": dataset.signature, "episodes": results, "next_slot": slot + 1})
    summary = {"fm": sum(row["conditions"]["full"]["fm"] for row in results) / len(results),
               "sample_mse": sum(row["conditions"]["full"]["sample_mse"] for row in results) / len(results),
               "noise_bins": [{"low": i / 5, "high": (i + 1) / 5, "count": len(values),
                               "mse": sum(values) / len(values) if values else None} for i, values in enumerate(bins)],
               "episodes": results, "memory_claim": "Action changes and lower loss alone do not prove correct memory use."}
    summary["period"] = period
    summary["by_task"] = {task: {"fm": sum(r["conditions"]["full"]["fm"] for r in results if r["task"] == task) / sum(r["task"] == task for r in results),
                                  "sample_mse": sum(r["conditions"]["full"]["sample_mse"] for r in results if r["task"] == task) / sum(r["task"] == task for r in results)}
                          for task in dataset.by_task}
    model.train()
    return summary


@torch.no_grad()
def audit_cache(model, dataset, cfg, device):
    cache_manifest = dataset.manifest
    prepared = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    expected = make_cache_contract(cfg, prepared)
    if fingerprint(expected) != cache_manifest["signature"]:
        raise ValueError("Cache was produced by different resources, preprocessing, or feature code.")
    if sha256(cfg["paths"]["base"]) != cache_manifest["contract"]["base_sha256"] or sha256(cfg["paths"]["stats"]) != cache_manifest["contract"]["stats_sha256"]:
        raise ValueError("Base/statistics do not match the cache.")
    reports = []
    for task, records in dataset.by_task.items():
        record = records[0]
        sample = dataset.at(record, 0)
        batch = collate([sample], device)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            current, _, _ = model.backbone.encode_observation(batch["latent"], batch["text"], batch["proprio"])
        stored = batch["history"][:, 0]
        delta = (current.float() - stored.float()).abs()
        relative = float(delta.mean() / stored.float().abs().mean().clamp_min(1e-6))
        if relative > 0.02:
            raise ValueError(f"Online/cache relative MAE too large for {task}: {relative}.")
        reports.append({"task": task, "relative_mae": relative, "maximum_abs": float(delta.max())})
    return reports


def main():
    from .model import S1Model
    from .checkpoint import verified_load
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--period", type=int, default=8)
    parser.add_argument("--checkpoint")
    parser.add_argument("--output", required=True)
    parser.add_argument("--evidence")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.plot:
        plot_metrics(cfg["paths"]["run"], args.output)
        return
    device = torch.device("cuda:0")
    torch.manual_seed(17)
    model = S1Model(cfg, device)
    if args.checkpoint:
        path = Path(args.checkpoint)
        checkpoint = verified_load(path) if path.is_dir() or path.name == "resume.pt" else torch.load(path, map_location="cpu", weights_only=True)
        if checkpoint["identity"]["cache_signature"] != read_json(Path(cfg["paths"]["cache"]) / "manifest.json")["signature"]:
            raise ValueError("Checkpoint cache signature mismatch.")
        model.memory.load_state_dict(checkpoint["memory"], strict=True)
    dataset = CachedEpisodes(cfg, "val")
    audit = audit_cache(model, dataset, cfg, device)
    result = {"cache_audit": audit}
    if not args.audit_only:
        result["validation"] = validate(model, dataset, cfg, device, True, load_evidence(args.evidence) if args.evidence else None, period=args.period)
    atomic_json(args.output, result)


def plot_metrics(run, output):
    import csv
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    run, output = Path(run), Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(line) for line in (run / "metrics.jsonl").read_text().splitlines() if line]
    training = [row for row in rows if row.get("kind") == "train"]
    keys = ("step", "loss", "fm_unweighted", "learning_rate", "gradient_norm", "history_frames", "update_seconds", "eta_seconds", "data_seconds", "gpu_peak_gib")
    with output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in keys} for row in training)
    fig, axes = plt.subplots(3, 2, figsize=(12, 10))
    for ax, key in zip(axes.flat, ("loss", "fm_unweighted", "gradient_norm", "update_seconds", "history_frames", "learning_rate")):
        selected = [r for r in training if r.get(key) is not None]
        ax.plot([r["step"] for r in selected], [r[key] for r in selected], linewidth=.8)
        ax.set(xlabel="Completed optimizer updates", ylabel=key)
        ax.grid(alpha=.25)
    fig.tight_layout()
    for suffix in (".png", ".pdf"):
        fig.savefig(output.with_suffix(suffix), dpi=160)
    plt.close(fig)
    detail, axes = plt.subplots(1, 3, figsize=(16, 4))
    for layer in ("4", "9", "14", "19", "24", "29"):
        selected = [r for r in training if layer in r.get("gates", {})]
        axes[0].plot([r["step"] for r in selected], [r["gates"][layer] for r in selected], label=layer)
    axes[0].set_title("Injection gates (raw values)")
    axes[0].legend()
    validation = [r for r in rows if r.get("kind") == "validation"]
    validation_rows = []
    for period in (1, 4, 8, 16):
        selected = [r for r in validation if str(period) in r.get("periods", {})]
        axes[1].plot([r["step"] for r in selected], [r["periods"][str(period)]["fm"] for r in selected], marker="o", label=f"T={period}")
        for row in selected:
            for task, value in row["periods"][str(period)].get("by_task", {}).items():
                validation_rows.append({"step": row["step"], "period": period, "task": task, **value})
    axes[1].set_title("Validation FM")
    if validation:
        axes[1].legend()
    events = [r for r in rows if r.get("kind") == "timing"]
    for kind in ("checkpoint", "upload", "evaluation_upload", "offline_validation", "closed_validation"):
        selected = [r for r in events if r["component"] == kind]
        axes[2].plot([r["step"] for r in selected], [r["seconds"] for r in selected], marker=".", label=kind)
    axes[2].set_title("Measured component seconds")
    if events:
        axes[2].legend()
    for ax in axes:
        ax.set_xlabel("Completed optimizer updates")
        ax.grid(alpha=.25)
    detail.tight_layout()
    for suffix in (".png", ".pdf"):
        detail.savefig(output.with_name(output.stem + "_validation_gates_timing").with_suffix(suffix), dpi=160)
    plt.close(detail)
    with output.with_name(output.stem + "_validation.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=("step", "period", "task", "fm", "sample_mse"))
        writer.writeheader()
        writer.writerows(validation_rows)
    with output.with_name(output.stem + "_details.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("step", "kind", "values_json"))
        for row in rows:
            writer.writerow((row.get("step"), row.get("kind"), json.dumps(row, ensure_ascii=False)))


if __name__ == "__main__":
    main()
