"""Motion audit of the dense expert data + within-episode transition pairs (CPU only).

    /opt/mwam/bin/python scripts/memory_v2/audit_motion.py --output-dir outputs/memory_v2/motion

Writes into --output-dir:
  motion_audit.json  per task: share of "hold still" targets, P(still future | still recent past),
                     still-run lengths and where they sit (after which gripper event), gripper events
                     per episode; per-episode details.
  pairs_within.json  within-episode pairs (same layout as find_pairs.py output; kind="within"):
                     train = train episodes, val = val episodes (use with `train_v2.py pr --pairs`).
  pairs_v1_within.json (with --merge) the cross-episode train/val pairs of --merge plus these.
Prints a short table.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/memory_v2/motion"))
    parser.add_argument("--features", default="outputs/memory_v2/features_dense_v1",
                        help="feature store for the visual distance of pairs ('' to skip)")
    parser.add_argument("--root", default="/workspace/FastWAM")
    parser.add_argument("--code", default="/restore-tmp/dense_joint_v1")
    parser.add_argument("--dense-output", default="/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")
    parser.add_argument("--arm-eps", type=float, nargs="+", default=(0.005, 0.01, 0.02),
                        help="rad: a window is still if every arm joint target spans less than this")
    parser.add_argument("--gripper-eps", type=float, default=0.05)
    parser.add_argument("--recent", type=int, default=16, help="steps of recent past for P(still | still)")
    parser.add_argument("--min-run", type=int, default=8, help="shortest still run reported")
    parser.add_argument("--anchor-stride", type=int, default=8)
    parser.add_argument("--min-gap", type=int, default=16, help="within pairs: min anchor distance")
    parser.add_argument("--state-eps", type=float, default=0.05)
    parser.add_argument("--min-delta", type=float, default=2.0)
    parser.add_argument("--per-query", type=int, default=3)
    parser.add_argument("--require-event", action="store_true", help="within pairs: a gripper event between")
    parser.add_argument("--merge", default="outputs/memory_v2/pairs/pairs_v1.json",
                        help="cross-episode pairs to merge with ('' to skip)")
    args = parser.parse_args()

    import torch
    from fastwam.memory_s1.common import ReleaseNormalizer
    from fastwam.memory_v2 import dense
    from fastwam.memory_v2.motion import (describe_within, gripper_events, match_within, phase_index, still_runs,
                                          stillness, summarise_stillness)
    from fastwam.memory_v2.pairs import chunk

    spec = dense.DenseSpec(root=Path(args.root), code=Path(args.code), output=Path(args.dense_output),
                           verify_identity=False)
    records = dense.records(spec)
    episodes = dense.EpisodeStore(spec, capacity=4, verify=False)
    features = dense.FeatureStore(Path(args.features), capacity=2) if args.features else None
    normaliser = ReleaseNormalizer(dense.dense_config(spec)["paths"]["stats"])
    split = {r["episode_id"]: r["split"] for r in records}

    still_rows = {eps: {} for eps in args.arm_eps}     # eps -> task -> [rows]
    runs_by_task, events_by_task, details = {}, {}, []
    items, phases = [], {}
    main_eps = sorted(args.arm_eps)[len(args.arm_eps) // 2]
    for k, r in enumerate(records):
        e = episodes(r["episode_id"])
        raw = normaliser.denormalize(e["actions"].float()).numpy()
        n = len(raw)
        ev = gripper_events(raw)
        phases[r["episode_id"]] = phase_index(n, ev)
        events_by_task.setdefault(r["task"], []).append(len(ev))
        for eps in args.arm_eps:
            s = stillness(raw, recent=args.recent, arm_eps=eps, gripper_eps=args.gripper_eps)
            still_rows[eps].setdefault(r["task"], []).append(s)
        runs = still_runs(raw, main_eps, args.gripper_eps, args.min_run)
        for run in runs:
            before = [x for x in ev if x["t"] <= run["start"]]
            after = [x for x in ev if x["t"] >= run["start"] + run["length"]]
            run.update(position=run["start"] / max(1, n - 1),
                       after_event=None if not before else f"{before[-1]['side']}-{before[-1]['kind']}",
                       since_event=None if not before else run["start"] - before[-1]["t"],
                       next_event=None if not after else f"{after[0]['side']}-{after[0]['kind']}",
                       at_end=run["start"] + run["length"] >= n - 1)
        runs_by_task.setdefault(r["task"], []).extend(runs)
        details.append({"episode_id": r["episode_id"], "task": r["task"], "split": r["split"], "length": n,
                        "events": ev, "still_runs": runs})
        # within-episode pair anchors (whole episode)
        proprio = e["proprio"].float().numpy()
        actions = e["actions"].float().numpy()
        anchors = list(range(0, n, args.anchor_stride))
        visual = features(r["episode_id"])[anchors].float().mean(1).numpy() if features is not None else None
        for j, a in enumerate(anchors):
            c, v = chunk(actions, a)
            items.append({"episode_id": r["episode_id"], "task": r["task"], "anchor": a, "state": proprio[a],
                          "chunk": c, "valid": v, "visual": None if visual is None else visual[j]})
        if (k + 1) % 20 == 0:
            print(f"[motion] {k + 1}/{len(records)} episodes", flush=True)

    # ------------------------------------------------------------------ audit summary
    summary = {}
    for task in sorted(runs_by_task):
        runs = [x for x in runs_by_task[task] if not x["at_end"]]
        lengths = np.array([x["length"] for x in runs]) if runs else np.zeros(0)
        n_ep = len(events_by_task[task])
        after = {}
        for x in runs:
            after.setdefault(x["after_event"] or "start", []).append(x["length"])
        summary[task] = {
            "episodes": n_ep,
            "gripper_events_per_episode_median": float(np.median(events_by_task[task])),
            "stillness": {str(eps): summarise_stillness(still_rows[eps][task]) for eps in args.arm_eps},
            f"still_runs@{main_eps}": {
                "per_episode": len(runs) / max(1, n_ep),
                "length_q50_q90_max": [float(np.quantile(lengths, 0.5)), float(np.quantile(lengths, 0.9)),
                                       float(lengths.max())] if len(lengths) else None,
                "steps_share": float(lengths.sum()) / max(1, sum(d["length"] for d in details if d["task"] == task)),
                "after_event": {key: {"runs": len(v), "median_length": float(np.median(v)), "max": int(max(v))}
                                for key, v in sorted(after.items())},
                "trailing_runs_per_episode": sum(x["at_end"] for x in runs_by_task[task]) / max(1, n_ep)},
        }

    # ------------------------------------------------------------------ within-episode pairs
    common = dict(min_gap=args.min_gap, state_eps=args.state_eps, min_delta=args.min_delta, per_query=args.per_query,
                  require_event=args.require_event)
    train = match_within(items, phases, query_filter=lambda it: split[it["episode_id"]] == "train", **common)
    val = match_within(items, phases, query_filter=lambda it: split[it["episode_id"]] == "val", **common)
    for p in val:
        p["donor_split"] = "val"
    pairs = {"settings": {"kind": "within", "anchor_stride": args.anchor_stride, **common,
                          "visual": "1 - cos(token-mean post-Video-DiT feature)" if features is not None else None},
             "anchors": len(items), "train": train, "val": val,
             "summary": {"train": describe_within(train), "val": describe_within(val)}}

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    settings = {k: (list(v) if isinstance(v, tuple) else v) for k, v in vars(args).items() if k != "output_dir"}
    settings["output_dir"] = str(out)
    (out / "motion_audit.json").write_text(json.dumps({"settings": settings, "summary": summary,
                                                       "episodes": details}, indent=1), encoding="utf-8")
    (out / "pairs_within.json").write_text(json.dumps(pairs, indent=1), encoding="utf-8")
    if args.merge and not Path(args.merge).exists():
        print(f"[motion] WARNING: --merge {args.merge} not found; the merged pairs file is not written")
        args.merge = ""
    if args.merge:
        cross = json.loads(Path(args.merge).read_text(encoding="utf-8"))
        merged = {"settings": {"cross": cross.get("settings"), "within": pairs["settings"]},
                  "train": [dict(p, kind=p.get("kind", "cross")) for p in cross["train"]] + train,
                  "val": [dict(p, kind=p.get("kind", "cross")) for p in cross["val"]] + val}
        merged["summary"] = {"cross_train": len(cross["train"]), "within_train": len(train),
                             "cross_val": len(cross["val"]), "within_val": len(val)}
        (out / "pairs_v1_within.json").write_text(json.dumps(merged, indent=1), encoding="utf-8")

    # ------------------------------------------------------------------ table
    print("\n== stillness of the expert targets (anchor = every frame) ==")
    print(f"{'task':<16}{'eps':>6}{'still fut':>11}{'still rec':>11}{'P(still|still)':>16}{'P(still|moving)':>17}")
    for task, s in summary.items():
        for eps, v in s["stillness"].items():
            print(f"{task:<16}{eps:>6}{v['still_future']:>11.3f}{v['still_recent']:>11.3f}"
                  f"{v['p_still_given_still']:>16.3f}{v['p_still_given_moving']:>17.3f}")
    print(f"\n== still runs >= {args.min_run} steps (arm eps {main_eps} rad), excluding the trailing hold ==")
    for task, s in summary.items():
        r = s[f"still_runs@{main_eps}"]
        print(f"{task:<16} runs/ep {r['per_episode']:.2f}  len q50/q90/max {r['length_q50_q90_max']}  "
              f"share of steps {r['steps_share']:.3f}  trailing/ep {r['trailing_runs_per_episode']:.2f}  "
              f"gripper events/ep {s['gripper_events_per_episode_median']:.0f}")
        for key, v in r["after_event"].items():
            print(f"{'':<18}after {key:<14} runs {v['runs']:>4}  median {v['median_length']:>6.1f}  max {v['max']}")
    print("\n== within-episode pairs ==")
    print(json.dumps(pairs["summary"], indent=1))
    print(f"\n[motion] written {(out / 'motion_audit.json').resolve()}")
    print(f"[motion] written {(out / 'pairs_within.json').resolve()}")
    if args.merge:
        print(f"[motion] written {(out / 'pairs_v1_within.json').resolve()}")


if __name__ == "__main__":
    main()
