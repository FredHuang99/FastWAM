"""Find matched-present pairs in the dense data (CPU; reads the dense cache and the feature store).

    python scripts/memory_v2/find_pairs.py --output outputs/memory_v2/pairs/pairs_v1.json

Writes {"train": [...], "val": [...], "summary": ...}:
  train : query and donor both from train episodes  (counterfactual training)
  val   : query from a val episode, donor from any other episode  (PR evaluation; donor_split recorded)
Each pair: task, query/donor {episode_id, anchor}, present_rms, delta_norm, visual_distance.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=Path("outputs/memory_v2/pairs/pairs_v1.json"))
    parser.add_argument("--features", default="outputs/memory_v2/features_dense_v1",
                        help="feature store for the visual distance ('' to skip)")
    parser.add_argument("--root", default="/workspace/FastWAM")
    parser.add_argument("--code", default="/restore-tmp/dense_joint_v1")
    parser.add_argument("--dense-output", default="/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")
    parser.add_argument("--anchor-stride", type=int, default=8)
    parser.add_argument("--stage", type=float, nargs=2, default=(0.3, 1.0), help="episode fraction window")
    parser.add_argument("--state-eps", type=float, default=0.05, help="max RMS normalised present distance")
    parser.add_argument("--min-delta", type=float, default=2.0, help="min L2 between the two future chunks")
    parser.add_argument("--per-query", type=int, default=3)
    args = parser.parse_args()

    from fastwam.memory_v2 import dense
    from fastwam.memory_v2.pairs import build_pairs
    spec = dense.DenseSpec(root=Path(args.root), code=Path(args.code), output=Path(args.dense_output),
                           verify_identity=False)
    records = dense.records(spec)
    episodes = dense.EpisodeStore(spec, capacity=4, verify=False)
    features = dense.FeatureStore(Path(args.features), capacity=2) if args.features else None
    result = build_pairs(spec, records, episodes, features, anchor_stride=args.anchor_stride, stage=tuple(args.stage),
                         state_eps=args.state_eps, min_delta=args.min_delta, per_query=args.per_query,
                         log=lambda m: None)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({"anchors": result["anchors"], "settings": result["settings"], "summary": result["summary"]}, indent=1))
    print(f"[pairs] written {args.output.resolve()}")


if __name__ == "__main__":
    main()
