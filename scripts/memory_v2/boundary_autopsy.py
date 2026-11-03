"""Phase-boundary autopsy (week plan v6 2.4): why episodes stop at the two progress boundaries.

Conditions = the official-table rows (official_table.ROWS: X7 / A2C / B0-6ep x put_back / swap, execute 8, 100 official
scenes; H200 episodes read from closed_loop/h200/ after the sync). CPU only; reads executed_actions.jsonl.

put_back, episodes that reached the centre but never pressed the button, classified in this order (exclusive):
  (c) button_missed     an end effector came within the calibrated press distance of the button, press_cnt stayed 0
  (b) skipped_button    the block was lifted again / left the centre without a press
  (d) not_released      the block rests in the centre but the right gripper stays closed (>= 50% of the frames after)
  (a) idle              placed + released, then the arm targets stay still for >= half of the remaining frames
  (e) wandering         none of the above (moving, but neither near the button nor regrasping)
  The press distance is calibrated on the episodes that DID press: the distance of the nearer end-effector link to the
  button at the press frame (median + 3 cm). end-effector link = configured ee link, not the fingertip.
swap, two boundaries:
  S1 -> S2 (S1 done, S2 not): same_block_again / grasp_fail (a close with no lift) / idle / other
  S2 -> S3 (S2 done, S3 not): wrong_block (the other block moved again) / lifted_not_placed (the first block was
  lifted >= 5 cm but not put into the target tray) / grasp_fail / idle / other
Also: continuation rate at each boundary binned by the frame the boundary was reached (< 200 / 200-400 / > 400): a rate
that falls with the frame index points at pace drift (slow episodes leave the demonstrated distribution).
Branch rule for X7-on put_back (v6 2.4): (A) idle >= 60% -> X12a; (B) button_missed >= 40%; (C) not_released >= 40%;
otherwise mixed.

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/boundary_autopsy.py [--out report.md]
"""
import argparse
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import official_table as ot  # noqa: E402
import queue5 as q  # noqa: E402

cls = q._stages_module()
PUT, SWAP = ot.PUT, ot.SWAP
OPEN, CLOSED = 0.75, 0.62                 # gripper thresholds as in closed_loop_stages.gripper_closes_rows
GR = {"left": 6, "right": 13}


def rows_of(d):
    return [json.loads(x) for x in (Path(d) / "executed_actions.jsonl").read_text().splitlines() if x.strip()]


def idle_fraction(rows, start):
    """Fraction of the frames from `start` on that lie in still runs (targets within 0.01 rad, >= 24 frames)."""
    from fastwam.memory_v2.motion import still_runs
    t = np.asarray([r["target"] for r in rows[start:] if r.get("target") is not None], dtype=np.float64)
    if len(t) < 24:
        return 0.0, 0
    runs = still_runs(t, arm_eps=0.01, gripper_eps=0.05, min_length=24)
    still = sum(x["length"] for x in runs)
    return still / len(t), max((x["length"] for x in runs), default=0)


def ee(row, side):
    p = (((row.get("joint_details") or {}).get(side) or {}).get("ee_pose") or {}).get("p")
    return p[:3] if p else None


def obj(row, name):
    v = (row.get("objects_after") or {}).get(name)
    return v["p"][:3] if isinstance(v, dict) and "p" in v else None


def grip(row, side):
    p = row.get("physical_after") or []
    return p[GR[side]] if len(p) > GR[side] else None


def button_dist(row):
    b = obj(row, "button")
    if b is None:
        return None
    ds = [math.dist(e, b) for e in (ee(row, "left"), ee(row, "right")) if e]
    return min(ds) if ds else None


# ============================================================================ put_back
def put_centre_t(rows, snaps):
    ev, _ = cls.events(snaps, ["block"], cls.put_back_location)
    return next((e["t"] for e in ev if e["to"] == "centre"), None)


def put_press_distance(cases):
    """Calibrate: distance of the nearer ee link to the button at the first pressed frame, over pressing episodes."""
    d = []
    for rows in cases:
        t = next((i for i, r in enumerate(rows) if ((r.get("objects_after") or {}).get("press_cnt") or 0) >= 1), None)
        if t is not None:
            v = button_dist(rows[t])
            if v is not None:
                d.append(v)
    return (statistics.median(d) if d else None), len(d)


def put_classify(rows, snaps, centre_t, press_thr):
    i0 = max(0, centre_t - 1)                       # rows[i] -> snaps[i + 1]
    after = rows[i0:]
    z0 = snaps[0]["block"]["p"][2]
    flags = {}
    bd = [button_dist(r) for r in after]
    bd = [x for x in bd if x is not None]
    flags["button_min_m"] = round(min(bd), 3) if bd else None
    flags["near_button"] = bool(press_thr is not None and bd and min(bd) <= press_thr)
    pos = [obj(r, "block") for r in after]
    pos = [p for p in pos if p]
    lifted = any(p[2] - z0 >= 0.05 for p in pos)
    left_centre = any(cls.put_back_location(p[0], p[1]) not in ("centre",) and p[2] - z0 < 0.012 for p in pos[5:])
    flags["regrasped_or_moved"] = bool(lifted or left_centre)
    g = [grip(r, "right") for r in after]
    g = [x for x in g if x is not None]
    flags["right_closed_frac"] = round(sum(x < CLOSED for x in g) / len(g), 3) if g else None
    frac, longest = idle_fraction(rows, i0)
    flags["idle_frac"], flags["longest_idle"] = round(frac, 3), longest
    flags["centre_frame"] = centre_t
    if flags["near_button"]:
        kind = "button_missed"
    elif flags["regrasped_or_moved"]:
        kind = "skipped_button"
    elif flags["right_closed_frac"] is not None and flags["right_closed_frac"] >= 0.5:
        kind = "not_released"
    elif frac >= 0.5:
        kind = "idle"
    else:
        kind = "wandering"
    return kind, flags


# ============================================================================ swap
def swap_times(snaps):
    ev, lift = cls.events(snaps, ["block1", "block2"], cls.swap_location)
    start = {b: cls.swap_location(*snaps[0][b]["p"][:2]) for b in ("block1", "block2")}
    empty = next(iter(set(cls.TRAYS) - set(start.values())), None)
    moves = [e for e in ev if e["to"] != "table"]
    s1 = next((e for e in moves if e["to"] == empty), None)
    s2 = None
    if s1:
        other = "block2" if s1["block"] == "block1" else "block1"
        s2 = next((e for e in moves if e["t"] > s1["t"] and e["block"] == other and e["to"] == start[s1["block"]]), None)
    return ev, start, s1, s2


def grasp_fails_after(rows, t0):
    closes = cls.gripper_closes_rows(rows[max(0, t0 - 1):], SWAP)
    return sum(c["kind"] != "grasp" for c in closes), sum(c["kind"] == "grasp" for c in closes)


def swap_classify(rows, snaps, boundary):
    ev, start, s1, s2 = swap_times(snaps)
    z0 = {b: snaps[0][b]["p"][2] for b in ("block1", "block2")}
    if boundary == "s1->s2":
        t0, first = s1["t"], s1["block"]
        later = [e for e in ev if e["t"] > t0 and e["to"] != "table"]
        frac, longest = idle_fraction(rows, max(0, t0 - 1))
        fails, grasps = grasp_fails_after(rows, t0)
        if later and later[0]["block"] == first:
            kind = "same_block_again"
        elif fails and not grasps:
            kind = "grasp_fail"
        elif frac >= 0.5:
            kind = "idle"
        else:
            kind = "other"
        return kind, {"boundary_frame": t0, "idle_frac": round(frac, 3), "longest_idle": longest, "failed_closes": fails}
    t0, first = s2["t"], s1["block"]
    other = "block2" if first == "block1" else "block1"
    later = [e for e in ev if e["t"] > t0 and e["to"] != "table"]
    lifted_first = any(obj(r, first) and obj(r, first)[2] - z0[first] >= 0.05 for r in rows[max(0, t0 - 1):])
    frac, longest = idle_fraction(rows, max(0, t0 - 1))
    fails, grasps = grasp_fails_after(rows, t0)
    if any(e["block"] == other for e in later):
        kind = "wrong_block"
    elif lifted_first:
        kind = "lifted_not_placed"
    elif fails and not grasps:
        kind = "grasp_fail"
    elif frac >= 0.5:
        kind = "idle"
    else:
        kind = "other"
    return kind, {"boundary_frame": t0, "idle_frac": round(frac, 3), "longest_idle": longest, "failed_closes": fails,
                  "first_block_lifted": lifted_first}


def bin_of(t):
    return "<200" if t < 200 else "200-400" if t <= 400 else ">400"


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    args = ap.parse_args()
    out = {"time": q.now_bj(), "put": {}, "swap": {}}
    lines = [f"# Phase-boundary autopsy ({q.now_bj()}; official 100 scenes, execute 8)", ""]
    eps = {}
    for (task, model), (folders, label, where) in ot.ROWS.items():
        found = [f for f in folders if q.resolve(f).exists()]
        e = q.episodes(found, label, None, [task])
        for (t, mode, seed), a in e.items():
            eps.setdefault((task, model, mode), []).append((seed, a))
    # put_back: calibrate the press distance on every pressing episode of every condition
    pressing = []
    for (task, model, mode), items in eps.items():
        if task == PUT:
            pressing += [rows_of(a["dir"]) for _, a in items if a.get("pressed")]
    med, n_cal = put_press_distance(pressing)
    thr = None if med is None else med + 0.03
    lines += [f"Press distance calibration: nearer ee link to button at the press frame, median {med if med is None else round(med, 3)} m "
              f"over {n_cal} pressing episodes -> 'near the button' = <= {thr if thr is None else round(thr, 3)} m.", ""]
    lines += ["## put_back: reached the centre, never pressed", "",
              "| condition | centre | pressed | not pressed | idle (a) | skipped (b) | button missed (c) | not released (d) | wandering (e) | "
              "press rate by centre frame <200 / 200-400 / >400 |", "|---|---|---|---|---|---|---|---|---|---|"]
    branch = None
    for (task, model, mode), items in sorted(eps.items()):
        if task != PUT:
            continue
        kinds, examples, bins = Counter(), defaultdict(list), defaultdict(lambda: [0, 0])
        n_centre = n_press = 0
        for seed, a in items:
            if not a.get("centre"):
                continue
            rows = rows_of(a["dir"])
            snaps, _ = cls.read_rows(Path(a["dir"]) / "executed_actions.jsonl")
            ct = put_centre_t(rows, snaps)
            if ct is None:
                continue
            n_centre += 1
            b = bins[bin_of(ct)]
            b[1] += 1
            if a.get("pressed"):
                n_press += 1
                b[0] += 1
                continue
            kind, flags = put_classify(rows, snaps, ct, thr)
            kinds[kind] += 1
            if len(examples[kind]) < 4:
                examples[kind].append({"seed": seed, **flags})
        n_not = n_centre - n_press
        pct = lambda k: f"{kinds[k]} ({100 * kinds[k] / n_not:.0f}%)" if n_not else "-"   # noqa: E731
        rate = " / ".join(f"{b[0]}/{b[1]}" for b in (bins["<200"], bins["200-400"], bins[">400"]))
        lines.append(f"| {model}-{mode} | {n_centre} | {n_press} | {n_not} | {pct('idle')} | {pct('skipped_button')} | "
                     f"{pct('button_missed')} | {pct('not_released')} | {pct('wandering')} | {rate} |")
        out["put"][f"{model}-{mode}"] = {"centre": n_centre, "pressed": n_press, "classes": dict(kinds),
                                         "examples": examples, "bins": dict(bins)}
        if model == "X7" and mode == "on" and n_not:
            share = {k: kinds[k] / n_not for k in kinds}
            branch = ("A (idle >= 60%: X12a goes ahead)" if share.get("idle", 0) >= 0.6 else
                      "B (button missed >= 40%: press precision; no X12a)" if share.get("button_missed", 0) >= 0.4 else
                      "C (not released >= 40%: placement precision; no X12a)" if share.get("not_released", 0) >= 0.4 else
                      "mixed (send the table to Fable)")
    lines += ["", f"**Branch for X7-on (v6 2.4): {branch}**", "", "Examples (first 4 per class, X7-on):", "```"]
    for kind, ex in (out["put"].get("X7-on", {}).get("examples") or {}).items():
        lines.append(f"{kind}: {json.dumps(ex)}")
    lines += ["```", ""]
    for boundary, need, stop in (("s1->s2", "s1", "s2"), ("s2->s3", "s2", "s3")):
        lines += [f"## swap {boundary}: {need} done, {stop} not", "",
                  "| condition | reached | continued | stopped | classes | continuation by boundary frame <200 / 200-400 / >400 |",
                  "|---|---|---|---|---|---|"]
        for (task, model, mode), items in sorted(eps.items()):
            if task != SWAP:
                continue
            kinds, bins, examples = Counter(), defaultdict(lambda: [0, 0]), defaultdict(list)
            reached = cont = 0
            for seed, a in items:
                if not a.get(need):
                    continue
                snaps, _ = cls.read_rows(Path(a["dir"]) / "executed_actions.jsonl")
                ev, start, s1, s2 = swap_times(snaps)
                boundary_event = s1 if need == "s1" else s2
                t0 = boundary_event["t"] if boundary_event else None
                if t0 is None:
                    continue
                reached += 1
                b = bins[bin_of(t0)]
                b[1] += 1
                if a.get(stop):
                    cont += 1
                    b[0] += 1
                    continue
                kind, flags = swap_classify(rows_of(a["dir"]), snaps, boundary)
                kinds[kind] += 1
                if len(examples[kind]) < 3:
                    examples[kind].append({"seed": seed, **flags})
            stopped = reached - cont
            classes = ", ".join(f"{k} {v} ({100 * v / stopped:.0f}%)" for k, v in kinds.most_common()) if stopped else "-"
            rate = " / ".join(f"{b[0]}/{b[1]}" for b in (bins["<200"], bins["200-400"], bins[">400"]))
            lines.append(f"| {model}-{mode} | {reached} | {cont} | {stopped} | {classes} | {rate} |")
            out["swap"][f"{boundary}/{model}-{mode}"] = {"reached": reached, "continued": cont, "classes": dict(kinds),
                                                        "bins": dict(bins), "examples": examples}
        lines.append("")
    R = q.O / "report"
    R.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(q.BJ).strftime("%Y%m%d_%H%M")
    md = Path(args.out) if args.out else R / f"BOUNDARY_{stamp}.md"
    md.write_text("\n".join(lines) + "\n")
    md.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str))
    print("\n".join(lines))
    print(f"\nBOUNDARY: {md}")


if __name__ == "__main__":
    main()
