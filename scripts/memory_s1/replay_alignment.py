"""Replay reviewed native targets with physical feedback and explicit execution cadence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from rootcause_sim import run_scene


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--task", choices=("put_back_block", "swap_blocks"), required=True)
    parser.add_argument("--episode", required=True)
    parser.add_argument("--scene-seed", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-targets", type=int, default=128)
    parser.add_argument("--executor", choices=("upstream_topp", "dense_native"), default="upstream_topp")
    parser.add_argument("--cadence")
    parser.add_argument("--gpu-uuid")
    parser.add_argument("--stop-root")
    args = parser.parse_args()
    if args.max_targets < 0:
        parser.error("max-targets must be nonnegative; zero replays the complete episode")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if (output / "alignment_replay.json").exists():
        raise ValueError("Preserve the existing alignment report and choose a new output directory.")
    job = {"scene": {"task": args.task, "seed": args.scene_seed, "ordinal": 0},
        "condition": args.executor, "episode": str(Path(args.episode).resolve()),
        "cadence": str(Path(args.cadence).resolve()) if args.cadence else None, "max_targets": args.max_targets}
    path = output / "job.json"
    path.write_text(json.dumps(job, indent=2), encoding="utf-8")
    args.job, args.operation, args.output = str(path), "replay", str(output)
    run_scene(args)


if __name__ == "__main__":
    main()
