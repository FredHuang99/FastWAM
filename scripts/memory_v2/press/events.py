"""press_button demos: where the presses are, and whether our history selection can see them (v6 2.5 step 2, Plan v2 E7).

CPU only, reads the downloaded hdf5 (state/left_ee_poses, state/right_ee_poses). A press = a dip of an end effector:
a local minimum of its height that it reached by going down >= 2 cm and leaves by going up >= 2 cm (the expert presses,
then moves up 4 cm). The dip's "bottom" = the frames within 1 cm of that minimum. Presses are grouped into buttons by
where they happen in time and space. Task: press the left button n1 times, the middle n2 times, then the right button
once. v1 (11-03 20:52) looked at the left arm only and found two buttons in every demo, so 0/50 matched "3 buttons,
the last pressed once"; v2 also reads the right arm: plausible = the left arm gives two buttons (n1, n2 >= 1,
n1 + n2 <= 10) and the right arm presses once, after the last left press (the confirm); the v1 form (three left-arm
buttons) still counts.

Coverage, at every decision of an online episode (every 8 frames from frame 0), for every press that ended before it:
is any frame of the dip bottom among the frames the history policy shows (memory_v2 select_history)?
  rule A  the training config (anchor frame 0 + every 24th frame + 2 recent frames 8 apart, at most 48)
  rule B  landmarks every 8th frame instead of every 24th (same cap)
  rule C  rule A + the bottom frame of every past press (an event-anchored history; the upper bound)
"count recoverable" = every past press of that decision is visible. Writes report/PRESS_EVENTS_<time>.md (+ .json).

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/press/events.py [--raw <data dir>]
"""
import argparse
import json
import os
import statistics
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
BJ = timezone(timedelta(hours=8))
DROP, RISE, BOTTOM, JUMP = 0.02, 0.02, 0.01, 0.05


def presses(z, xy, window=40):
    """Dips of the end-effector height: (frame of the minimum, bottom frames, xy at the minimum)."""
    out = []
    n = len(z)
    t = 1
    while t < n - 1:
        lo, hi = max(0, t - window), min(n, t + window + 1)
        if z[t] == z[lo:hi].min() and z[lo:t].max(initial=z[t]) - z[t] >= DROP and z[t:hi].max(initial=z[t]) - z[t] >= RISE:
            a = t
            while a > 0 and z[a - 1] <= z[t] + BOTTOM:
                a -= 1
            b = t
            while b < n - 1 and z[b + 1] <= z[t] + BOTTOM:
                b += 1
            out.append({"t": int(t), "bottom": [int(a), int(b)], "xy": [float(xy[t][0]), float(xy[t][1])]})
            t = b + 1
        else:
            t += 1
    return out


def group(ps):
    """Consecutive presses at the same place (xy within 5 cm) form one button."""
    groups = []
    for p in ps:
        if groups and np.hypot(*(np.asarray(p["xy"]) - np.asarray(groups[-1][-1]["xy"]))) < JUMP:
            groups[-1].append(p)
        else:
            groups.append([p])
    return groups


def coverage(length, ps, policy, extra=()):
    from fastwam.memory_v2.history import select_history
    pairs = seen = decisions = full = 0
    for d in range(0, length, 8):
        past = [p for p in ps if p["bottom"][1] < d]
        if not past:
            continue
        ids = set(select_history(range(d + 1), d, policy).ids)
        if extra:
            ids |= {p["t"] for p in past}
        vis = [any(i in ids for i in range(p["bottom"][0], p["bottom"][1] + 1)) for p in past]
        pairs += len(vis)
        seen += sum(vis)
        decisions += 1
        full += all(vis)
    return pairs, seen, decisions, full


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", default=str(O / "press/demo_clean/press_button/aloha_agilex/data"))
    ap.add_argument("--min-plausible", type=float, default=0.0,
                    help="exit 1 unless at least this share of the demos gives a plausible count pattern")
    args = ap.parse_args()
    import h5py
    from fastwam.memory_v2.config import HistoryPolicyConfig
    rule_a = HistoryPolicyConfig(anchor_frames=1, landmark_stride=24, recent_frames=2, recent_stride=8, max_frames=48)
    rule_b = HistoryPolicyConfig(anchor_frames=1, landmark_stride=8, recent_frames=2, recent_stride=8, max_frames=48)
    files = sorted(Path(args.raw).glob("*.hdf5"))
    eps, totals = [], {k: [0, 0, 0, 0] for k in "ABC"}
    for f in files:
        with h5py.File(f, "r") as h:
            pose = np.asarray(h["state/left_ee_poses"], dtype=np.float64)
            rpose = np.asarray(h["state/right_ee_poses"], dtype=np.float64) if "state/right_ee_poses" in h else None
        z, xy = pose[:, 2], pose[:, :2]
        ps = presses(z, xy)
        gs = group(ps)
        counts = [len(g) for g in gs]
        rps = presses(rpose[:, 2], rpose[:, :2]) if rpose is not None else []
        last_left = ps[-1]["t"] if ps else -1
        confirm = [p["t"] for p in rps if p["t"] > last_left]
        ok_v2 = len(gs) == 2 and min(counts) >= 1 and sum(counts) <= 10 and len(rps) == 1 and len(confirm) == 1
        ok_v1 = len(gs) == 3 and counts[2] == 1 and counts[0] + counts[1] <= 10
        ok = ok_v2 or ok_v1
        row = {"episode": f.stem, "length": len(z), "presses": len(ps), "buttons": counts, "plausible": ok,
               "form": "v2 (left n1, n2 + right confirm)" if ok_v2 else ("v1 (three left buttons)" if ok_v1 else None),
               "right_arm_presses": [p["t"] for p in rps], "confirm_frame": confirm[0] if confirm else None,
               "frames_after_confirm": (len(z) - 1 - confirm[0]) if confirm else None,
               "press_frames": [p["t"] for p in ps], "bottom_frames": [p["bottom"][1] - p["bottom"][0] + 1 for p in ps],
               "gap_frames": [b["t"] - a["t"] for a, b in zip(ps, ps[1:])]}
        for k, pol, extra in (("A", rule_a, ()), ("B", rule_b, ()), ("C", rule_a, (1,))):
            c = coverage(len(z), ps, pol, extra)
            row[f"cov_{k}"] = c
            totals[k] = [x + y for x, y in zip(totals[k], c)]
        eps.append(row)
    good = [e for e in eps if e["plausible"]]
    lines = [f"# press_button demos: presses and history coverage ({datetime.now(BJ):%F %T})", "",
             f"{len(eps)} demos from {args.raw}; {len(good)} give a plausible count pattern "
             f"({sum(e['form'] == 'v2 (left n1, n2 + right confirm)' for e in eps)} as left-arm n1, n2 + one right-arm "
             f"confirm press; {sum(e['form'] == 'v1 (three left buttons)' for e in eps)} as three left-arm buttons).", ""]
    if eps:
        n1 = Counter(e["buttons"][0] for e in good)
        n2 = Counter(e["buttons"][1] for e in good)
        bot = [x for e in eps for x in e["bottom_frames"]]
        gap = [x for e in eps for x in e["gap_frames"]]
        lines += [f"- presses per demo: median {statistics.median([e['presses'] for e in eps])}, "
                  f"range {min(e['presses'] for e in eps)}-{max(e['presses'] for e in eps)}",
                  f"- left-button count n1: {dict(sorted(n1.items()))}; middle-button count n2: {dict(sorted(n2.items()))}",
                  f"- (n1, n2) pairs: {dict(sorted(Counter(tuple(e['buttons'][:2]) for e in good).items()))}",
                  f"- right-arm presses per demo: {dict(sorted(Counter(len(e['right_arm_presses']) for e in eps).items()))}; "
                  f"frames after the confirm press: median "
                  f"{statistics.median([e['frames_after_confirm'] for e in eps if e['frames_after_confirm'] is not None] or [0])}",
                  f"- dip bottom lasts median {statistics.median(bot) if bot else '-'} frames (range {min(bot) if bot else '-'}-"
                  f"{max(bot) if bot else '-'}); frames between presses median {statistics.median(gap) if gap else '-'} "
                  f"(range {min(gap) if gap else '-'}-{max(gap) if gap else '-'})", "",
                  "| history rule | past presses visible | decisions where every past press is visible (count recoverable) |",
                  "|---|---|---|"]
        names = {"A": "A: training config (anchor + every 24th + 2 recent)", "B": "B: landmarks every 8th frame",
                 "C": "C: A + an anchor frame at every past press (upper bound)"}
        for k in "ABC":
            pairs, seen, dec, full = totals[k]
            lines.append(f"| {names[k]} | {seen}/{pairs} = {100 * seen / max(1, pairs):.0f}% | "
                         f"{full}/{dec} = {100 * full / max(1, dec):.0f}% |")
        bad = [e for e in eps if not e["plausible"]]
        if bad:
            lines += ["", "Demos without a plausible pattern (press detection to check; left buttons, right-arm press "
                      "frames): " + ", ".join(f"{e['episode']} {e['buttons']} R{e['right_arm_presses']}" for e in bad[:12])]
    rep = O / "report" / f"PRESS_EVENTS_{datetime.now(BJ):%Y%m%d_%H%M}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n")
    rep.with_suffix(".json").write_text(json.dumps({"episodes": eps, "totals": totals}, indent=1))
    print("\n".join(lines))
    share = len(good) / max(1, len(eps))
    print(f"\nPRESS_EVENTS: {rep}  (plausible {len(good)}/{len(eps)} = {share:.0%}, required {args.min_plausible:.0%})")
    return 0 if eps and share >= args.min_plausible else 1


if __name__ == "__main__":
    sys.exit(main())
