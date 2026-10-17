"""Reproduce the memory_s1 query-collapse geometry at initialisation (NumPy only).

python scripts/memory_v2/slot_collapse.py --output outputs/memory_v2/analysis/slot_collapse.json
"""
import argparse
import json
from pathlib import Path

from fastwam.memory_v2.analysis import slot_collapse_simulation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=256)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    runs = [slot_collapse_simulation(width=args.width, seed=s) for s in range(args.seeds)]
    for name in runs[0]:
        rows = [[run[name][k]["centred_norm_percent"] for run in runs] for k in range(len(runs[0][name]))]
        means = [sum(r) / len(r) for r in rows]
        cos = [min(run[name][k]["min_cosine"] for run in runs) for k in range(len(runs[0][name]))]
        print(f"{name:18s} slot variation % per stage: " + "  ".join(f"{m:6.2f}" for m in means)
              + " | min cosine: " + "  ".join(f"{c:.4f}" for c in cos))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(runs, indent=2))


if __name__ == "__main__":
    main()
