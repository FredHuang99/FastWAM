"""Training-loss trajectory of a dense-joint run against its learning rate (NumPy only).

Reads the per-update receipts written by dense_joint_v1/training.py
(`updates/u000123.rank0.json` or the migrated `history/u000123.rank0.json`):
    {"update", "lr", "losses": [[action_loss, video_loss], ...], "gradient_norm", ...}

and answers: did the training objective itself get worse while the run was
training on it, and if so, when did that start relative to the LR warm-up?
A loss that rises on its own training distribution in lock-step with the LR is
an optimisation failure (step size / optimizer state), not over-fitting.

Usage
    python scripts/memory_v2/loss_vs_lr.py --updates <dir with u*.json> --output loss_vs_lr.json [--plot loss_vs_lr.png]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np


def load(directory: Path):
    rows = []
    for path in sorted(directory.glob("u*.rank*.json")):
        match = re.match(r"u(\d+)\.rank(\d+)\.json$", path.name)
        if not match:
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        action = np.asarray([pair[0] for pair in value["losses"]], dtype=np.float64)
        rows.append({"update": int(value["update"]), "rank": int(match.group(2)), "lr": float(value["lr"]),
                     "action_loss": action, "gradient_norm": value.get("gradient_norm"),
                     "seconds": value.get("seconds")})
    if not rows:
        raise SystemExit(f"No update receipts under {directory}")
    merged = {}
    for row in rows:                      # merge ranks of the same update
        item = merged.setdefault(row["update"], {"update": row["update"], "lr": row["lr"], "losses": [],
                                                  "gradient_norm": row["gradient_norm"], "seconds": row["seconds"]})
        item["losses"].append(row["action_loss"])
    out = []
    for update in sorted(merged):
        item = merged[update]
        losses = np.concatenate(item["losses"])
        out.append({"update": update, "lr": item["lr"], "mean": float(losses.mean()), "median": float(np.median(losses)),
                    "p90": float(np.quantile(losses, 0.9)), "samples": int(len(losses)),
                    "gradient_norm": item["gradient_norm"], "seconds": item["seconds"]})
    return out


def onset(curve, baseline_updates=5, factor=1.5, window=3):
    """First update after which the rolling median stays above factor x the initial median."""
    medians = np.asarray([c["median"] for c in curve])
    base = float(np.median(medians[:baseline_updates]))
    rolling = np.convolve(medians, np.ones(window) / window, mode="valid")
    for i in range(len(rolling)):
        if np.all(rolling[i:] > factor * base):
            return {"update": curve[i + window - 1]["update"], "lr": curve[i + window - 1]["lr"],
                    "baseline_median": base, "factor": factor}
    return None


def summarise(curve):
    lr = np.asarray([c["lr"] for c in curve])
    med = np.asarray([c["median"] for c in curve])
    warm = lr < lr.max() * 0.999
    first, last = curve[0], curve[-1]
    spearman = None
    if warm.sum() > 3:
        a = np.argsort(np.argsort(lr[warm]))
        b = np.argsort(np.argsort(med[warm]))
        spearman = float(np.corrcoef(a, b)[0, 1])
    peak = int(np.argmax(med))
    return {
        "updates": len(curve), "first_update": first["update"], "last_update": last["update"],
        "first_median": first["median"], "last_median": last["median"],
        "peak_median": float(med[peak]), "peak_update": curve[peak]["update"],
        "last_over_first_median": last["median"] / max(first["median"], 1e-12),
        "first_mean": first["mean"], "last_mean": last["mean"],
        "warmup_spearman_lr_vs_median_loss": spearman,
        "onset": onset(curve),
        "mean_median_by_lr_band": {
            band: float(med[(lr >= lo) & (lr < hi)].mean()) if np.any((lr >= lo) & (lr < hi)) else None
            for band, (lo, hi) in {"lr<1e-5": (0, 1e-5), "1e-5..3e-5": (1e-5, 3e-5), "3e-5..6e-5": (3e-5, 6e-5),
                                   "6e-5..9e-5": (6e-5, 9e-5), ">=9e-5": (9e-5, 1)}.items()},
        "reading": ("Training loss on the run's own sample stream rises with the LR; this is an optimisation "
                    "failure (step size / fresh optimizer state on a converged expert), not over-fitting."
                    if spearman is not None and spearman > 0.5 and last["median"] > 1.5 * first["median"] else
                    "No monotone loss-vs-LR degradation detected."),
    }


def plot(curve, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    u = [c["update"] for c in curve]
    fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=150)
    ax.plot(u, [c["median"] for c in curve], color="#2a6fdb", lw=1.6, label="median action FM loss (128 samples)")
    ax.plot(u, [c["mean"] for c in curve], color="#2a6fdb", lw=0.8, alpha=0.45, label="mean")
    ax.set_xlabel("optimizer update")
    ax.set_ylabel("training loss")
    ax.grid(alpha=0.25)
    twin = ax.twinx()
    twin.plot(u, [c["lr"] for c in curve], color="#d9822b", lw=1.2, ls="--", label="learning rate")
    twin.set_ylabel("learning rate", color="#d9822b")
    lines = ax.get_legend_handles_labels()
    more = twin.get_legend_handles_labels()
    ax.legend(lines[0] + more[0], lines[1] + more[1], loc="lower right", fontsize=8, frameon=False)
    ax.set_title("Dense-joint A: training loss vs learning rate", fontsize=10)
    fig.tight_layout()
    fig.savefig(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--updates", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--plot", type=Path)
    args = parser.parse_args()
    curve = load(args.updates)
    result = {"source": str(args.updates), "summary": summarise(curve), "curve": curve}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if args.plot:
        plot(curve, args.plot)
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
