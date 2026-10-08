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
def validate(model, dataset, cfg, device, interventions=False, evidence=None):
    model.eval()
    count = cfg["validation_anchors_per_task"] * 2
    results, bins = [], [[] for _ in range(5)]
    conditions = ["full", "gate_zero", "current_only"] if interventions else ["full"]
    if evidence is not None:
        conditions += ["delete_critical", "delete_irrelevant"]
    for slot in range(count):
        sample = dataset.sample(0, slot, validation=True)
        noise, tau = deterministic_noise(17, 0, [slot], device, "validation-noise")
        entry = {"episode_id": sample["episode_id"], "t": int(sample["t"]), "task": sample["task"], "conditions": {}}
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
    summary = {"fm": sum(row["conditions"]["full"]["fm"] for row in results) / len(results),
               "sample_mse": sum(row["conditions"]["full"]["sample_mse"] for row in results) / len(results),
               "noise_bins": [{"low": i / 5, "high": (i + 1) / 5, "count": len(values),
                               "mse": sum(values) / len(values) if values else None} for i, values in enumerate(bins)],
               "episodes": results, "memory_claim": "Action changes and lower loss alone do not prove correct memory use."}
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
        result["validation"] = validate(model, dataset, cfg, device, True, load_evidence(args.evidence) if args.evidence else None)
    atomic_json(args.output, result)


def plot_metrics(run, output):
    import json
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [json.loads(line) for line in (Path(run) / "metrics.jsonl").read_text().splitlines() if line]
    rows = [row for row in rows if row.get("kind") == "train"]
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for ax, key in zip(axes.flat, ("loss", "learning_rate", "gradient_norm", "update_seconds")):
        ax.plot([row["step"] for row in rows], [row[key] for row in rows])
        ax.set(xlabel="Optimizer update", ylabel=key)
        ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()
