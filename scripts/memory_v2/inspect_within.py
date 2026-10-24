"""Where do the within-episode pairs sit? (CPU; reads pairs_within.json + the dense cache)

    /opt/mwam/bin/python scripts/memory_v2/inspect_within.py outputs/memory_v2/motion/pairs_within.json

Per task: how many gripper events happened before the query / donor anchor (the expert's phase), the
position in the episode, and how far each arm travelled between the two anchors (max joint excursion from
the query pose, rad). A put_back pair with the left arm travelling out and back between the two anchors and
no gripper event in between is a press (pre-press vs post-press). Prints the phase histogram and a few rows.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

LEFT, RIGHT = [0, 1, 2, 3, 4, 5], [7, 8, 9, 10, 11, 12]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pairs", type=Path)
    parser.add_argument("--root", default="/workspace/FastWAM")
    parser.add_argument("--code", default="/restore-tmp/dense_joint_v1")
    parser.add_argument("--dense-output", default="/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")
    parser.add_argument("--rows", type=int, default=8, help="example rows per task")
    args = parser.parse_args()

    from fastwam.memory_s1.common import ReleaseNormalizer
    from fastwam.memory_v2 import dense
    from fastwam.memory_v2.motion import gripper_events, phase_index

    spec = dense.DenseSpec(root=Path(args.root), code=Path(args.code), output=Path(args.dense_output),
                           verify_identity=False)
    episodes = dense.EpisodeStore(spec, capacity=4, verify=False)
    normaliser = ReleaseNormalizer(dense.dense_config(spec)["paths"]["stats"])
    value = json.loads(args.pairs.read_text(encoding="utf-8"))
    cache = {}

    def episode(eid):
        if eid not in cache:
            raw = normaliser.denormalize(episodes(eid)["actions"].float()).numpy()
            ev = gripper_events(raw)
            cache[eid] = (raw, ev, phase_index(len(raw), ev))
        return cache[eid]

    for split in ("train", "val"):
        pairs = value[split]
        for task in sorted({p["task"] for p in pairs}):
            sub = [p for p in pairs if p["task"] == task]
            phases, rows = Counter(), []
            for p in sub:
                raw, ev, ph = episode(p["query"]["episode_id"])
                q, d = p["query"]["anchor"], p["donor"]["anchor"]
                seg = raw[q:d + 1]
                left = float(np.abs(seg[:, LEFT] - raw[q, LEFT]).max())
                right = float(np.abs(seg[:, RIGHT] - raw[q, RIGHT]).max())
                last = [e for e in ev if e["t"] <= q]
                phases[(int(ph[q]), int(ph[d]))] += 1
                rows.append((p["query"]["episode_id"], q, d, len(raw), int(ph[q]), int(ph[d]),
                             f"{last[-1]['side']}-{last[-1]['kind']}" if last else "start", left, right,
                             p["delta_norm"], p.get("visual_distance")))
            lefts = np.array([r[7] for r in rows])
            rights = np.array([r[8] for r in rows])
            print(f"\n== {split} {task}: {len(sub)} pairs ==")
            print("  (events before query, before donor): count  ", dict(sorted(phases.items())))
            print(f"  left-arm excursion between q and d  q50 {np.median(lefts):.3f}  q90 {np.quantile(lefts, 0.9):.3f} rad")
            print(f"  right-arm excursion between q and d q50 {np.median(rights):.3f}  q90 {np.quantile(rights, 0.9):.3f} rad")
            print(f"  {'episode':<34}{'q':>5}{'d':>5}{'len':>5}{'ph_q':>5}{'ph_d':>5}  {'after':<12}{'L_exc':>7}{'R_exc':>7}"
                  f"{'delta':>7}{'vis':>7}")
            for r in rows[:args.rows]:
                vis = "" if r[10] is None else f"{r[10]:.3f}"
                print(f"  {r[0][-34:]:<34}{r[1]:>5}{r[2]:>5}{r[3]:>5}{r[4]:>5}{r[5]:>5}  {r[6]:<12}{r[7]:>7.3f}{r[8]:>7.3f}"
                      f"{r[9]:>7.1f}{vis:>7}")


if __name__ == "__main__":
    main()
