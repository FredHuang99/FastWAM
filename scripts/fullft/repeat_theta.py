"""Plan v19 3.2 (3) (11-22, Opus): pick theta of the in-place repeat count on the press_button demos, and check that it
classifies EVERY pair of consecutive presses of the same arm correctly ("same button" vs "another button"). Plan: if
it does not separate all 50 demos, report and do not train. CPU, read-only.
Inputs (defaults = the 5090 layout):
  --dense   the dense cache the model trains on (encodings.pt: normalised 14-d proprio = what the ledger reads)
  --events  the events file the model trains on (default: the provisional-write file of press_v3c)
  --demos   the demo hdf5 folder (ground truth only: end-effector x at each press)
Ground truth: a press (a 'bottom' entry) belongs to the button whose x the end effector is nearest at that frame (the env
puts button1 / button2 / check at x -0.15 / 0.0 / 0.15; scripts/memory_v2/press/events.py); a press farther than 5 cm
from every button is reported as unclear. Joint distance = L2 over the arm's six normalised joints
(history.ARM_JOINTS), exactly what history.with_repeats computes.
theta = the midpoint of the gap between the largest same-button distance and the smallest change-button distance.
Also reported (descriptive): the same split for 'top' entries, labelled by the press each follows.
Writes outputs/fullft/REPEAT_THETA.json; prints THETA OK (all pairs of all demos right) or THETA NOT SEPARABLE.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/repeat_theta.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

R = Path("/workspace/FastWAM-memory2")
BUTTON_X = (-0.15, 0.0, 0.15)
UNCLEAR = 0.05


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dense", default=str(R / "outputs/memory_v2/press/dense_press_button_v1"))
    ap.add_argument("--events", default="")
    ap.add_argument("--demos", default="")
    ap.add_argument("--out", default=str(R / "outputs/fullft/REPEAT_THETA.json"))
    args = ap.parse_args()
    sys.path.insert(0, str(R / "src"))
    from fastwam.fullft.data import DenseEpisodes, match_events
    from fastwam.fullft.history import arm_joints, joint_distance
    events_path = Path(args.events) if args.events else next(
        (p for p in (R / "outputs/fullft/events/events_press_button_v3c.json",
                     Path("/mnt/hf/relay_mirror/memwam-diag-v1/diag/press_v3c/events_press_button_v3c.json"))
         if p.is_file()), None)
    if events_path is None or not events_path.is_file():
        raise SystemExit("no events file (give --events)")
    demos = Path(args.demos) if args.demos else next(
        (p for p in (Path("/workspace/FastWAM/resources/RMBench/data/demo_clean/press_button/aloha_agilex/data"),
                     R / "outputs/memory_v2/press/demo_clean/press_button/aloha_agilex/data")
         if any(p.glob("*.hdf5"))), None)
    if demos is None:
        raise SystemExit("no demo hdf5 folder (give --demos)")
    value = json.loads(events_path.read_text())
    events = value["episodes"] if "episodes" in value else value
    eps = DenseEpisodes([args.dense], ["press_button"])
    ids = [r["episode_id"] for r in eps.records]
    matched = match_events(ids, events)
    by_stem = {}
    for key in events:
        by_stem.setdefault(id(events[key]), key)
    print(f"events {events_path} ({value.get('rule', 'no rule field') if isinstance(value, dict) else ''})")
    print(f"dense {args.dense}: {len(ids)} episodes, {len(matched)} matched to events; demos {demos}")

    import h5py
    pairs = {"bottom": [], "top": []}          # (episode, arm, frame_a, frame_b, same_gt, joint_distance)
    unclear, per_episode = [], {}
    for eid in ids:
        evs = matched.get(eid)
        if evs is None:
            unclear.append((eid, "no events"))
            continue
        key = by_stem[id(evs)]
        stem = key.split("/", 1)[1]
        path = demos / f"{stem}.hdf5"
        if not path.is_file():
            unclear.append((eid, f"no demo {path.name}"))
            continue
        with h5py.File(path, "r") as f:
            keys = next((p for p in (("state/left_ee_poses", "state/right_ee_poses"),
                                     ("endpose/left_endpose", "endpose/right_endpose")) if all(k in f for k in p)))
            pos = [np.asarray(f[k], dtype=np.float64)[:, :3] for k in keys]
        proprio = eps(eid)["proprio"]
        n = min(len(proprio), len(pos[0]))
        runs = {}
        for arm in (0, 1):
            mine = sorted((e for e in evs if int(e["arm"]) == arm and int(e["frame"]) < n), key=lambda e: int(e["frame"]))
            button_of_press = {}
            for e in mine:
                if e["kind"] == "bottom":
                    x = float(pos[arm][int(e["frame"]), 0])
                    d = [abs(x - b) for b in BUTTON_X]
                    k = int(np.argmin(d))
                    if d[k] > UNCLEAR:
                        unclear.append((eid, f"arm {arm} press at frame {e['frame']}: x {x:.3f}"))
                    button_of_press[int(e["frame"])] = k
            # a top is labelled by the press it follows (the last bottom of the arm before it); none -> not labelled
            for kind in ("bottom", "top"):
                prev = None
                for e in (x for x in mine if x["kind"] == kind):
                    f = int(e["frame"])
                    if kind == "bottom":
                        lab = button_of_press[f]
                    else:
                        before = [b for b in button_of_press if b < f]
                        lab = button_of_press[max(before)] if before else None
                    if prev is not None and lab is not None and prev[1] is not None:
                        dist = joint_distance(arm_joints(proprio[f], arm), arm_joints(proprio[prev[0]], arm))
                        pairs[kind].append((eid, arm, prev[0], f, lab == prev[1], dist))
                    prev = (f, lab)
            seq = [button_of_press[int(e["frame"])] for e in mine if e["kind"] == "bottom"]
            if seq:
                rl = []
                for b in seq:
                    if rl and rl[-1][0] == b:
                        rl[-1][1] += 1
                    else:
                        rl.append([b, 1])
                runs[arm] = rl
        per_episode[eid] = runs
    report = {"events": str(events_path), "dense": args.dense, "demos": str(demos), "unclear": unclear[:40],
              "unclear_count": len(unclear)}
    theta = None
    for kind in ("bottom", "top"):
        same = [p[5] for p in pairs[kind] if p[4]]
        change = [p[5] for p in pairs[kind] if not p[4]]
        row = {"pairs": len(pairs[kind]), "same": len(same), "change": len(change)}
        if same and change:
            row.update(same_max=max(same), same_p99=float(np.percentile(same, 99)), change_min=min(change),
                       change_p1=float(np.percentile(change, 1)), gap=min(change) - max(same))
        report[kind] = row
        print(f"{kind}: {row}")
    b = report["bottom"]
    if b.get("gap", -1) > 0:
        theta = (b["same_max"] + b["change_min"]) / 2
    if theta is not None:
        wrong = {k: [p for p in pairs[k] if (p[5] < theta) != p[4]] for k in ("bottom", "top")}
        bad_eps = sorted({p[0] for p in wrong["bottom"]})
        report.update(theta=theta, wrong_bottom=len(wrong["bottom"]), wrong_top=len(wrong["top"]),
                      wrong_top_examples=[p[:5] + (round(p[5], 4),) for p in wrong["top"][:10]],
                      episodes_all_presses_right=len(ids) - len(bad_eps) - len({u[0] for u in unclear}))
    shapes = {}
    for eid, runs in per_episode.items():
        s = " ".join(f"{arm}:" + ",".join(f"b{b}x{c}" for b, c in rl) for arm, rl in sorted(runs.items()))
        shapes[s] = shapes.get(s, 0) + 1
    report["run_shapes_top"] = sorted(shapes.items(), key=lambda x: -x[1])[:12]
    ok = theta is not None and report["wrong_bottom"] == 0 and not unclear and len(per_episode) == len(ids)
    report["pass"] = bool(ok)
    Path(args.out).write_text(json.dumps(report, indent=1) + "\n")
    print("run shapes (arm: button x presses, most common):")
    for s, c in report["run_shapes_top"]:
        print(f"  {c:3d}  {s}")
    if unclear:
        print(f"unclear ({len(unclear)}): {unclear[:5]}")
    if ok:
        print(f"THETA OK: theta {theta:.4f} (same-button max {b['same_max']:.4f}, change-button min {b['change_min']:.4f}); "
              f"all {b['pairs']} press pairs of all {len(ids)} demos right; tops wrong {report['wrong_top']} "
              f"of {report['top']['pairs']} (descriptive); wrote {args.out}")
        return 0
    print(f"THETA NOT SEPARABLE (or incomplete): {json.dumps({k: report.get(k) for k in ('bottom', 'theta', 'wrong_bottom', 'unclear_count')})}; "
          f"wrote {args.out}. Plan v19 3.2 (3): report, do not train.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
