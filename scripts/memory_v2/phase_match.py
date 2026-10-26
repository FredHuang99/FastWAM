"""Where in the expert's task is the closed-loop robot? (CPU; dense cache + closed-loop logs)

For put_back_block the policy presses the button and then never re-grasps the block. Two explanations:
  * phase regression: after the press its state matches the expert BEFORE the press (it "forgets" it pressed and
    goes back), so the next action is the expert's pre-press action;
  * off-distribution state: its state is far from every expert state after the press, so nothing it learned applies.
This matches every closed-loop commanded target (14 joints incl. grippers, the same space as the expert action
targets) to the nearest expert target over all train demonstrations of the task, and reports the expert phase and
time of that nearest frame and the joint distance. Held-out (val) demonstrations give the in-distribution distance.

Expert phases (put_back_block, from the gripper events of each demonstration + the press found as the left arm's
largest excursion between the left-gripper close and the second right-gripper close):
  P0 reach+grasp | P1 carry to centre | P2 release, retreat | P3 left to button | P4 after press: left back,
  right reaches the block | P5 carry back to the mat
For swap_blocks the phase is the number of gripper events so far.

    /opt/mwam/bin/python scripts/memory_v2/phase_match.py outputs/memory_v2/closed_loop/a2 --label a2C_e3 --modes on null
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

LEFT_ARM, RIGHT_ARM, GRIP = [0, 1, 2, 3, 4, 5], [7, 8, 9, 10, 11, 12], [6, 13]
PUT_BACK_PHASES = ["P0 grasp", "P1 carry->centre", "P2 release/retreat", "P3 left->button", "P4 after press",
                   "P5 carry back"]


def put_back_phases(actions: np.ndarray, events) -> np.ndarray:
    """Phase per frame (0..5) of one put_back demonstration; -1 when the event pattern is not the usual one."""
    n = len(actions)
    seq = [(e["side"], e["kind"], e["t"]) for e in events]
    right_close = [t for s, k, t in seq if s == "right" and k == "close"]
    right_open = [t for s, k, t in seq if s == "right" and k == "open"]
    left_close = [t for s, k, t in seq if s == "left" and k == "close"]
    if len(right_close) < 2 or not right_open or not left_close:
        return np.full(n, -1)
    g1, r1, lc, g2 = right_close[0], right_open[0], left_close[0], right_close[1]
    seg = actions[lc:g2, LEFT_ARM]
    press = lc + int(np.argmax(np.abs(seg - actions[lc, LEFT_ARM]).max(1))) if g2 > lc else lc
    bounds = [g1, r1, lc, press, g2]
    phase = np.zeros(n, dtype=int)
    for b in bounds:
        phase[b:] += 1
    return phase


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", type=Path, help="closed-loop output folder (contains <label>/<mode>/<task>/seed_*)")
    ap.add_argument("--label", required=True)
    ap.add_argument("--modes", nargs="+", default=["on"])
    ap.add_argument("--task", default="put_back_block")
    ap.add_argument("--every", type=int, default=24)
    ap.add_argument("--root", default="/workspace/FastWAM")
    ap.add_argument("--code", default="/restore-tmp/dense_joint_v1")
    ap.add_argument("--dense-output", default="/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")
    args = ap.parse_args()

    from fastwam.memory_s1.common import ReleaseNormalizer
    from fastwam.memory_v2 import dense
    from fastwam.memory_v2.motion import gripper_events, phase_index

    spec = dense.DenseSpec(root=Path(args.root), code=Path(args.code), output=Path(args.dense_output),
                           verify_identity=False)
    episodes = dense.EpisodeStore(spec, capacity=4, verify=False)
    normaliser = ReleaseNormalizer(dense.dense_config(spec)["paths"]["stats"])
    records = [r for r in dense.records(spec) if r["task"] == args.task]

    def expert(r):
        raw = normaliser.denormalize(episodes(r["episode_id"])["actions"].float()).numpy().astype(np.float64)
        ev = gripper_events(raw)
        ph = put_back_phases(raw, ev) if args.task == "put_back_block" else phase_index(len(raw), ev)
        return raw, ph

    bank_x, bank_phase, bank_t, bank_len = [], [], [], []
    val = []
    for r in records:
        raw, ph = expert(r)
        if r["split"] == "train":
            bank_x.append(raw); bank_phase.append(ph); bank_t.append(np.arange(len(raw))); bank_len.append(np.full(len(raw), len(raw)))
        else:
            val.append(raw)
    X = np.concatenate(bank_x); P = np.concatenate(bank_phase); T = np.concatenate(bank_t); L = np.concatenate(bank_len)
    arms = LEFT_ARM + RIGHT_ARM
    scale = np.ones(14); scale[GRIP] = 0.5          # gripper command 0..1 counts like 0.5 rad of joint distance

    def nearest(x):
        d = np.sqrt((((X - x) * scale) ** 2).sum(1))
        i = int(np.argmin(d))
        return i, float(d[i])

    ref = [nearest(x)[1] for raw in val for x in raw[::8]]
    q50, q90, q99 = np.quantile(ref, [0.5, 0.9, 0.99])
    print(f"expert bank: {len(records)} {args.task} demos ({len(bank_x)} train, {len(val)} val), {len(X)} frames")
    print(f"in-distribution distance (val demos vs train bank): median {q50:.3f}  q90 {q90:.3f}  q99 {q99:.3f}")
    names = PUT_BACK_PHASES if args.task == "put_back_block" else None

    def pname(p):
        return "?" if p < 0 else (names[p] if names else f"phase {p}")

    for mode in args.modes:
        totals = Counter()
        for res in sorted(args.folder.glob(f"{args.label}*/{mode}/{args.task}/seed_*/result.json")):
            d = res.parent
            if not re.fullmatch(r"seed_\d+", d.name):
                continue
            rows = [json.loads(l) for l in (d / "executed_actions.jsonl").read_text().splitlines() if l.strip()]
            if not rows:
                continue
            press_t = next((i + 1 for i, r in enumerate(rows) if ((r.get("objects_after") or {}).get("press_cnt") or 0) >= 1), None)
            print(f"\n== {res.parent.parent.parent.parent.name}/{mode} {args.task} {d.name}  "
                  f"targets={len(rows)}  first press at {press_t}")
            after_press = Counter()
            for i in range(0, len(rows), args.every):
                x = np.asarray(rows[i]["target"], dtype=np.float64)
                j, dist = nearest(x)
                tag = "FAR" if dist > q99 else ""
                print(f"   t={i + 1:<4} -> expert {pname(int(P[j])):<20} t={int(T[j]):>4}/{int(L[j])}  dist {dist:.3f} {tag}")
                if press_t is not None and i + 1 > press_t + 24:
                    after_press[pname(int(P[j]))] += 1
                    totals[pname(int(P[j]))] += 1
                    totals["FAR"] += dist > q99
                    totals["n"] += 1
            if after_press:
                print(f"   after the press: {dict(after_press)}")
        if totals["n"]:
            n = totals.pop("n"); far = totals.pop("FAR")
            print(f"\n## {args.label}/{mode}: decisions after the press ({n}): "
                  + "  ".join(f"{k} {v / n:.0%}" for k, v in sorted(totals.items())) + f"   |  beyond expert q99: {far / n:.0%}")


if __name__ == "__main__":
    main()
