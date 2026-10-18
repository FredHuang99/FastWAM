"""Estimate branch distances ||Delta|| from demonstrations and the implied tau_c.

Reads memory_s1 prepared episodes (states/targets in raw joint units) and the
released normaliser statistics, finds cross-episode anchors with nearly the same
normalised present, and reports how much of each training objective lands above
the noise level where the noisy action stops revealing the branch.

python scripts/memory_v2/tau_crossover.py --config configs/memory_s1/s1_variable_t_h100.yaml \
    --stage 0.35 1.0 --state-eps 0.05 --output outputs/memory_v2/analysis/tau_crossover.json

# or take the config recorded by the dense-joint run (CPU only, no torch model):
python scripts/memory_v2/tau_crossover.py --dense-output /workspace/FastWAM/outputs/s1_dense_joint_h100_v1 \
    --root /workspace/FastWAM --output outputs/memory_v2/analysis/tau_crossover.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fastwam.memory_v2.analysis import (mass_above, near_present_branch_distances, normalise,
                                        summarize_crossover)


def load_stats(path):
    stats = json.loads(Path(path).read_text())
    out = {}
    for kind in ("state", "action"):
        values = stats[kind]["default"]
        out[kind] = (np.asarray(values["global_mean"], dtype=np.float64), np.asarray(values["global_std"], dtype=np.float64))
    return out


def main():
    import torch

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="memory_s1 YAML config")
    parser.add_argument("--dense-output", type=Path, help="dense run folder; uses its IDENTITY.json config instead")
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"), help="base for relative paths")
    parser.add_argument("--split", default="train")
    parser.add_argument("--stage", type=float, nargs=2, default=(0.0, 1.0), help="episode fraction window")
    parser.add_argument("--state-eps", type=float, default=0.05, help="RMS normalised present distance")
    parser.add_argument("--anchor-stride", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if bool(args.config) == bool(args.dense_output):
        sys.exit("Give exactly one of --config or --dense-output.")
    if args.dense_output:
        cfg = json.loads((args.dense_output / "IDENTITY.json").read_text())["config"]
    else:
        from fastwam.memory_s1.common import load_config
        cfg = load_config(args.config)

    def resolve(path):
        path = Path(path)
        return path if path.is_absolute() else args.root / path

    prepared = resolve(cfg["paths"]["prepared"])
    manifest = json.loads((prepared / "manifest.json").read_text())
    stats = load_stats(resolve(cfg["paths"]["stats"]))
    report = {"config": args.config or str(args.dense_output), "stage": list(args.stage), "state_eps": args.state_eps,
              "reference_mass_above_0.8": {n: mass_above(0.8, n) for n in
                                           ("released_shift5", "memory_s1_uniform", "memory_v2_no_endpoint", "memory_v2")},
              "tasks": {}}
    for task in sorted({e["task"] for e in manifest["episodes"]}):
        episodes = []
        for record in manifest["episodes"]:
            if record["task"] != task or record["split"] != args.split:
                continue
            value = torch.load(prepared / record["file"], map_location="cpu", weights_only=True)
            episodes.append({"state": normalise(value["states"].double().numpy(), *stats["state"]),
                             "target": normalise(value["targets"].double().numpy(), *stats["action"])})
        found = near_present_branch_distances(episodes, args.state_eps, anchor_stride=args.anchor_stride,
                                              min_fraction=args.stage[0], max_fraction=args.stage[1])
        summary = summarize_crossover(found["delta_norm"])
        summary["episodes"] = len(episodes)
        report["tasks"][task] = summary
        print(task, json.dumps(summary, indent=1)[:2000])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
