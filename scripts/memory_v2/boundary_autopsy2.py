"""Phase-boundary autopsy v2 (11-03 evening): what the v1 classes hide. CPU only, read-only, same episodes as v1.

v1 (boundary_autopsy.py, pre-registered, unchanged) put X7-on in branch B: 71% of the put_back episodes that reached the
centre without a press had an end effector come near the button. v1 cannot say whether those are aiming errors or
"left too early" errors, and its swap classes were 79-100% "other". v2 answers four questions:

P1  put_back, centre reached, no press: did the arm go to the button at all? (approached / skipped = regrasped the block
    without going to the button / stuck = neither); for "stuck", the arm speed after the centre (still vs dithering).
P2  of the approaches: press success per condition, history available (X7-on, A2C-on) vs not (X7-null, A2C-null, B0),
    with Wilson intervals and Fisher exact tests. If history raises press-given-approach, the miss is not only motor.
P3  approach geometry: nearer end-effector link relative to the button. Pressing episodes at the press frame vs missed
    approaches at their lowest frame inside the press zone: height above the button (dz), sideways offset (r).
    "stayed high" = dz above the pressing episodes' 90th percentile (it never went down far enough: left before
    pushing); "off to the side" = low enough but r above the pressing 90th percentile (aimed wrong); "low and centred"
    = both inside (pushed in the right place but the counter did not move). Then: was the block re-grasped after the
    approach (the policy moved on as if it had pressed)?
S   swap, the episodes that stopped at s1->s2 / s2->s3, by what happened to the block that had to move next:
    went_back = the block already placed was lifted again (repeats a finished step: a progress error);
    lifted_misplaced = the right block was lifted but never came to rest in the target tray (where it ended);
    reached_not_lifted = an end effector got to grasp distance of it, it was never lifted (grasp failure);
    never_reached = no end effector got to it (did not go for the next step), split by arm motion (still / moving).
    Grasp distance = nearer end-effector link to the block at lift-off in the episodes that did lift it (median + 3 cm).

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/boundary_autopsy2.py [--out report.md]
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
import boundary_autopsy as b1  # noqa: E402  (helpers: rows_of, ee, obj, grip, button_dist, swap_times, ...)

ot, q, cls = b1.ot, b1.q, b1.cls
PUT, SWAP = b1.PUT, b1.SWAP
WITH_HISTORY = {"X7-on", "A2C-on"}
WITHOUT_HISTORY = {"X7-null", "A2C-null", "B0-null"}
LIFT = 0.03                      # a block counts as lifted 3 cm above its resting height
EE_STILL_MM = 2.0                # nearer end effector moves less than this per frame -> "still" frame


# ============================================================================ small helpers
def pct(values, p):
    v = sorted(x for x in values if x is not None)
    if not v:
        return None
    k = (len(v) - 1) * p / 100
    lo, hi = math.floor(k), math.ceil(k)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def r3(x):
    return None if x is None else round(float(x), 3)


def wilson(k, n, z=1.96):
    if not n:
        return None, None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def fisher(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]] (sum of tables no more likely than the observed one)."""
    n1, n2, m = a + b, c + d, a + c
    n = n1 + n2

    def pr(x):
        return math.comb(n1, x) * math.comb(n2, m - x) / math.comb(n, m)
    lo, hi = max(0, m - n2), min(m, n1)
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(lo, hi + 1) if pr(x) <= p0 * (1 + 1e-9)))


def nearer(row, point):
    """(side, distance, (dx, dy, dz)) of the end-effector link nearer to `point`."""
    best = None
    for side in ("left", "right"):
        e = b1.ee(row, side)
        if e and point:
            d = math.dist(e, point)
            if best is None or d < best[1]:
                best = (side, d, (e[0] - point[0], e[1] - point[1], e[2] - point[2]))
    return best


def ee_speed(rows, start):
    """Per frame from `start`: the larger of the two end-effector displacements (mm)."""
    out = []
    for i in range(max(1, start), len(rows)):
        steps = []
        for side in ("left", "right"):
            a, b = b1.ee(rows[i - 1], side), b1.ee(rows[i], side)
            if a and b:
                steps.append(1000 * math.dist(a, b))
        if steps:
            out.append(max(steps))
    return out


def motion(rows, start):
    """Arm motion after `start`: median end-effector speed (mm / frame), share of near-still frames, and the share of
    frames inside loose still runs (targets within 0.03 rad for >= 16 frames)."""
    sp = ee_speed(rows, start)
    from fastwam.memory_v2.motion import still_runs
    t = np.asarray([r["target"] for r in rows[start:] if r.get("target") is not None], dtype=np.float64)
    loose = 0.0
    if len(t) >= 16:
        runs = still_runs(t, arm_eps=0.03, gripper_eps=0.1, min_length=16)
        loose = sum(x["length"] for x in runs) / len(t)
    return {"ee_mm_per_frame": r3(statistics.median(sp)) if sp else None,
            "ee_still_frac": r3(sum(x < EE_STILL_MM for x in sp) / len(sp)) if sp else None,
            "loose_still_frac": r3(loose), "frames_after": len(rows) - start}


def press_row(rows):
    return next((i for i, r in enumerate(rows) if ((r.get("objects_after") or {}).get("press_cnt") or 0) >= 1), None)


def touched_button(rows, start, end=None):
    """True / False if the episode logs contacts with the button, None if it does not log them."""
    seen = False
    for r in rows[start:end]:
        objs = (r.get("object_contacts") or {}).get("objects")
        if objs is None:
            continue
        seen = True
        by = ((objs.get("button") or {}).get("by_side") or {})
        if any(by.values()):
            return True
    return False if seen else None


# ============================================================================ put_back
def put_episode(rows, snaps, centre_t, zone):
    """Everything P1-P3 need about one centre-reached episode (pressed or not)."""
    i0 = max(0, centre_t - 1)
    z0 = snaps[0]["block"]["p"][2]
    pr = press_row(rows)
    info = {"centre_frame": centre_t, "pressed": pr is not None, "press_frame": pr, "length": len(rows)}
    if pr is not None:
        n = nearer(rows[pr], b1.obj(rows[pr], "button"))
        if n:
            info.update(side=n[0], dist=r3(n[1]), dz=r3(n[2][2]), r=r3(math.hypot(n[2][0], n[2][1])))
        info["motion"] = motion(rows, i0)
        return info
    # not pressed: the approach = the frames after the centre with the nearer link inside the press zone
    track = []
    for i in range(i0, len(rows)):
        n = nearer(rows[i], b1.obj(rows[i], "button"))
        if n:
            track.append((i, n))
    if not track:
        info["kind"] = "no_data"
        return info
    closest = min(track, key=lambda x: x[1][1])
    info["min_dist"] = r3(closest[1][1])
    inside = [(i, n) for i, n in track if zone is not None and n[1] <= zone]
    approach_end = inside[-1][0] if inside else None
    lifted_after = lambda t: any(b1.obj(r, "block") and b1.obj(r, "block")[2] - z0 >= 0.05 for r in rows[t:])  # noqa: E731
    if inside:
        low = min(inside, key=lambda x: x[1][2][2])
        info.update(kind="approached", side=low[1][0], dist=r3(low[1][1]), dz=r3(low[1][2][2]),
                    r=r3(math.hypot(low[1][2][0], low[1][2][1])), zone_frames=len(inside),
                    entries=sum(1 for a, b in zip(inside, inside[1:]) if b[0] - a[0] > 1) + 1,
                    regrasp_after=lifted_after(approach_end), touched=touched_button(rows, i0))
    else:
        moved = lifted_after(i0) or any(
            (lambda p: p is not None and cls.put_back_location(p[0], p[1]) != "centre" and p[2] - z0 < 0.012)(b1.obj(r, "block"))
            for r in rows[i0 + 5:])
        info["kind"] = "skipped" if moved else "stuck"
    info["motion"] = motion(rows, i0)
    return info


def geometry_class(e, dz_hi, r_hi):
    if e["dz"] is None or dz_hi is None:
        return "unknown"
    if e["dz"] > dz_hi:
        return "stayed_high"
    if r_hi is not None and e["r"] is not None and e["r"] > r_hi:
        return "off_to_side"
    return "low_and_centred"


# ============================================================================ swap
def first_lift(rows, block, z0, start):
    for i in range(max(0, start), len(rows)):
        p = b1.obj(rows[i], block)
        if p and p[2] - z0 >= LIFT:
            return i
    return None


def swap_boundary(rows, snaps, boundary):
    """(target block, destination tray, block that must stay, row index of the boundary) or None."""
    ev, start, s1, s2 = b1.swap_times(snaps)
    if boundary == "s1->s2":
        if not s1:
            return None
        first = s1["block"]
        other = "block2" if first == "block1" else "block1"
        return other, start[first], first, s1["t"], start
    if not (s1 and s2):
        return None
    first = s1["block"]
    other = "block2" if first == "block1" else "block1"
    return first, start[other], other, s2["t"], start


def swap_episode(rows, snaps, boundary, grasp_zone):
    got = swap_boundary(rows, snaps, boundary)
    if got is None:
        return None
    target, dest, keep, t0, start = got
    i0 = max(0, t0 - 1)
    z0 = {bk: snaps[0][bk]["p"][2] for bk in ("block1", "block2")}
    info = {"boundary_frame": t0, "target": target, "destination": dest, "length": len(rows)}
    went_back = first_lift(rows, keep, z0[keep], i0 + 1)
    lift = first_lift(rows, target, z0[target], i0 + 1)
    dists = [n[1] for n in (nearer(r, b1.obj(r, target)) for r in rows[i0:]) if n]
    info["target_min_dist"] = r3(min(dists)) if dists else None
    info["motion"] = motion(rows, i0)
    if went_back is not None and (lift is None or went_back < lift):
        info["kind"] = "went_back"
        info["went_back_frame"] = went_back
    elif lift is not None:
        last = b1.obj(rows[-1], target)
        held = last is not None and last[2] - z0[target] >= LIFT
        where = "held_at_end" if held else (cls.swap_location(last[0], last[1]) if last else "?")
        info.update(kind="lifted_misplaced", lift_frame=lift, ended=("table" if where == "table" else where))
    elif dists and grasp_zone is not None and min(dists) <= grasp_zone:
        info["kind"] = "reached_not_lifted"
        closes = cls.gripper_closes_rows(rows[i0:], SWAP)
        info["closes"] = len(closes)
    else:
        info["kind"] = "never_reached"
    return info


def grasp_distance(cases):
    """Nearer end-effector link to the block at lift-off, over the episodes that lifted the block that moves next."""
    d = []
    for rows, snaps, boundary in cases:
        got = swap_boundary(rows, snaps, boundary)
        if got is None:
            continue
        target, _, _, t0, _ = got
        lift = first_lift(rows, target, snaps[0][target]["p"][2], max(0, t0 - 1) + 1)
        if lift is not None:
            n = nearer(rows[lift], b1.obj(rows[lift], target))
            if n:
                d.append(n[1])
    return (statistics.median(d) if d else None), len(d)


# ============================================================================ main
def collect():
    eps = {}
    for (task, model), (folders, label, where) in ot.ROWS.items():
        found = [f for f in folders if q.resolve(f).exists()]
        for (t, mode, seed), a in q.episodes(found, label, None, [task]).items():
            eps.setdefault((task, f"{model}-{mode}"), []).append((seed, a))
    return eps


def fmt_ci(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {100 * k / n:.0f}% [{100 * lo:.0f}, {100 * hi:.0f}]" if n else "-"


def put_section(eps, lines, out):
    # zone: v1 calibration (median press distance + 3 cm), recomputed here on the same episodes
    pressing = [b1.rows_of(a["dir"]) for (task, _), items in eps.items() if task == PUT for _, a in items if a.get("pressed")]
    med, n_cal = b1.put_press_distance(pressing)
    zone = None if med is None else med + 0.03
    per = {}
    for (task, cond), items in sorted(eps.items()):
        if task != PUT:
            continue
        per[cond] = []
        for seed, a in items:
            if not a.get("centre"):
                continue
            rows = b1.rows_of(a["dir"])
            snaps, _ = cls.read_rows(Path(a["dir"]) / "executed_actions.jsonl")
            ct = b1.put_centre_t(rows, snaps)
            if ct is None:
                continue
            per[cond].append({"seed": seed, **put_episode(rows, snaps, ct, zone)})
    pressed_all = [e for c in per.values() for e in c if e["pressed"] and e.get("dz") is not None]
    dz_hi, r_hi = pct([e["dz"] for e in pressed_all], 90), pct([e["r"] for e in pressed_all], 90)
    lines += [f"Press zone (v1 calibration): nearer end-effector link within {r3(zone)} m of the button "
              f"(median at the press frame {r3(med)} m over {n_cal} pressing episodes).", ""]

    lines += ["## P1 put_back: reached the centre, no press - did the arm go to the button?", "",
              "| condition | centre | pressed | not pressed | approached the button | skipped it (re-grasped the block) | "
              "stuck (neither) | stuck: median ee mm/frame, still-frame share |", "|---|---|---|---|---|---|---|---|"]
    for cond, es in per.items():
        n = [e for e in es if not e["pressed"]]
        k = Counter(e.get("kind") for e in n)
        stuck = [e for e in n if e.get("kind") == "stuck"]
        sm = [e["motion"]["ee_mm_per_frame"] for e in stuck if e.get("motion")]
        sf = [e["motion"]["ee_still_frac"] for e in stuck if e.get("motion")]
        share = lambda x: f"{k[x]} ({100 * k[x] / len(n):.0f}%)" if n else "-"   # noqa: E731
        lines.append(f"| {cond} | {len(es)} | {sum(e['pressed'] for e in es)} | {len(n)} | {share('approached')} | "
                     f"{share('skipped')} | {share('stuck')} | "
                     f"{r3(statistics.median(sm)) if sm else '-'}, {r3(statistics.median(sf)) if sf else '-'} |")
    ref = [e["motion"]["ee_mm_per_frame"] for es in per.values() for e in es if e["pressed"] and e.get("motion")]
    lines += ["", f"Reference: pressing episodes after the centre move their end effector a median "
                  f"{r3(statistics.median(ref)) if ref else '-'} mm/frame.", ""]

    lines += ["## P2 put_back: press success once the arm is at the button", "",
              "approach = pressed, or came inside the press zone without a press. [95% Wilson interval]", "",
              "| condition | history | approached / centre | pressed / approached |", "|---|---|---|---|"]
    counts = {}
    for cond, es in per.items():
        appr = [e for e in es if e["pressed"] or e.get("kind") == "approached"]
        k = sum(e["pressed"] for e in appr)
        counts[cond] = (k, len(appr))
        hist = "yes" if cond in WITH_HISTORY else "no" if cond in WITHOUT_HISTORY else "?"
        lines.append(f"| {cond} | {hist} | {fmt_ci(len(appr), len(es))} | {fmt_ci(k, len(appr))} |")
    tests = []
    for a_, b_ in (("X7-on", "B0-null"), ("X7-on", "X7-null"), ("A2C-on", "A2C-null"), ("X7-on", "A2C-on")):
        if a_ in counts and b_ in counts and counts[a_][1] and counts[b_][1]:
            (ka, na), (kb, nb) = counts[a_], counts[b_]
            p = fisher(ka, na - ka, kb, nb - kb)
            tests.append({"a": a_, "b": b_, "a_rate": r3(ka / na), "b_rate": r3(kb / nb), "fisher_p": float(f"{p:.2g}")})
            lines.append(f"- {a_} vs {b_}: {100 * ka / na:.0f}% vs {100 * kb / nb:.0f}%, Fisher p = {p:.2g}")
    pool = {g: [sum(counts[c][i] for c in counts if c in s) for i in (0, 1)] for g, s in
            (("with", WITH_HISTORY), ("without", WITHOUT_HISTORY))}
    if pool["with"][1] and pool["without"][1]:
        (ka, na), (kb, nb) = pool["with"], pool["without"]
        p = fisher(ka, na - ka, kb, nb - kb)
        lines.append(f"- pooled: with history {fmt_ci(ka, na)} vs without {fmt_ci(kb, nb)}, Fisher p = {p:.2g}")
        tests.append({"a": "with history", "b": "without", "a_rate": r3(ka / na), "b_rate": r3(kb / nb),
                      "fisher_p": float(f"{p:.2g}")})
    lines.append("")

    lines += ["## P3 put_back: where the end effector was (relative to the button)", "",
              f"dz = height of the nearer end-effector link above the button, r = sideways offset (m). Pressing episodes at "
              f"the press frame; missed approaches at their lowest frame inside the zone. Cut-offs = 90th percentile of the "
              f"pressing episodes: dz {r3(dz_hi)}, r {r3(r_hi)}.", "",
              "| condition | pressed: n, dz median, r median, side L/R | missed: n, dz median, r median, side L/R | "
              "stayed high | off to the side | low and centred | re-grasped after the miss | touched button (if logged) |",
              "|---|---|---|---|---|---|---|---|---|"]
    geo = {}
    for cond, es in list(per.items()) + [("all", [e for es in per.values() for e in es])]:
        pr = [e for e in es if e["pressed"] and e.get("dz") is not None]
        ms = [e for e in es if e.get("kind") == "approached"]
        g = Counter(geometry_class(e, dz_hi, r_hi) for e in ms)
        side = lambda xs: f"{sum(e.get('side') == 'left' for e in xs)}/{sum(e.get('side') == 'right' for e in xs)}"  # noqa: E731
        med_ = lambda xs, k: r3(statistics.median([e[k] for e in xs if e.get(k) is not None])) if xs else "-"   # noqa: E731
        share = lambda x: f"{g[x]} ({100 * g[x] / len(ms):.0f}%)" if ms else "-"   # noqa: E731
        rg = sum(bool(e.get("regrasp_after")) for e in ms)
        tb = [e.get("touched") for e in ms if e.get("touched") is not None]
        lines.append(f"| {cond} | {len(pr)}, {med_(pr, 'dz')}, {med_(pr, 'r')}, {side(pr)} | {len(ms)}, {med_(ms, 'dz')}, "
                     f"{med_(ms, 'r')}, {side(ms)} | {share('stayed_high')} | {share('off_to_side')} | "
                     f"{share('low_and_centred')} | {rg}/{len(ms)} | {(str(sum(tb)) + '/' + str(len(tb))) if tb else 'not logged'} |")
        geo[cond] = dict(g)
    lines.append("")
    hist = defaultdict(Counter)
    edges = (0.20, 0.22, 0.25, 0.28)
    for cond, es in per.items():
        for e in es:
            if not e["pressed"] and e.get("min_dist") is not None:
                hist[cond][next((f"<={x}" for x in edges if e["min_dist"] <= x), ">0.28")] += 1
    lines += ["Closest approach of the not-pressed episodes (m; a gap between the bins means near / not near is not a "
              "threshold artefact):", "", "| condition | " + " | ".join([f"<={x}" for x in edges] + [">0.28"]) + " |",
              "|---|" + "---|" * (len(edges) + 1)]
    for cond in per:
        lines.append(f"| {cond} | " + " | ".join(str(hist[cond][f"<={x}"]) for x in edges) + f" | {hist[cond]['>0.28']} |")
    lines.append("")
    out["put"] = {"zone_m": r3(zone), "dz_cut": r3(dz_hi), "r_cut": r3(r_hi), "tests": tests, "geometry": geo,
                  "episodes": per}


def swap_section(eps, lines, out):
    cases, loaded = [], {}
    for (task, cond), items in eps.items():
        if task != SWAP:
            continue
        for seed, a in items:
            if not a.get("s1"):
                continue
            rows = b1.rows_of(a["dir"])
            snaps, _ = cls.read_rows(Path(a["dir"]) / "executed_actions.jsonl")
            loaded[(cond, seed)] = (rows, snaps, a)
            cases.append((rows, snaps, "s1->s2"))
            if a.get("s2"):
                cases.append((rows, snaps, "s2->s3"))
    gz_med, n_g = grasp_distance(cases)
    gz = None if gz_med is None else gz_med + 0.03
    lines += [f"Grasp distance: nearer end-effector link to the block at lift-off, median {r3(gz_med)} m over {n_g} "
              f"lifts -> 'reached' = <= {r3(gz)} m.", ""]
    out["swap"] = {"grasp_zone_m": r3(gz), "boundaries": {}}
    for boundary, need, stop in (("s1->s2", "s1", "s2"), ("s2->s3", "s2", "s3")):
        lines += [f"## S swap {boundary}: {need} done, {stop} not - what happened to the block that had to move next", "",
                  "| condition | stopped | went back to the placed block | lifted, misplaced (ended: table / tray / held) | "
                  "reached, not lifted | never reached: still / moving |", "|---|---|---|---|---|---|"]
        res = {}
        for cond in sorted({c for c, _ in loaded}):
            es = []
            for (c, seed), (rows, snaps, a) in loaded.items():
                if c != cond or not a.get(need) or a.get(stop):
                    continue
                e = swap_episode(rows, snaps, boundary, gz)
                if e:
                    es.append({"seed": seed, **e})
            k = Counter(e["kind"] for e in es)
            ended = Counter(e.get("ended") for e in es if e["kind"] == "lifted_misplaced")
            nr = [e for e in es if e["kind"] == "never_reached"]
            still = sum((e["motion"].get("ee_still_frac") or 0) >= 0.5 for e in nr)
            share = lambda x: f"{k[x]} ({100 * k[x] / len(es):.0f}%)" if es else "-"   # noqa: E731
            lines.append(f"| {cond} | {len(es)} | {share('went_back')} | {share('lifted_misplaced')} "
                         f"({ended.get('table', 0)} / {sum(v for w, v in ended.items() if w in cls.TRAYS)} / "
                         f"{ended.get('held_at_end', 0)}) | {share('reached_not_lifted')} | "
                         f"{share('never_reached')}: {still} / {len(nr) - still} |")
            res[cond] = es
        lines.append("")
        out["swap"]["boundaries"][boundary] = res
    lines += ["never reached: still = the end effector moved < 2 mm on at least half of the frames after the boundary.", ""]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out")
    args = ap.parse_args()
    eps = collect()
    out = {"time": q.now_bj()}
    lines = [f"# Phase-boundary autopsy v2 ({q.now_bj()}; official 100 scenes, execute 8)", "",
             "Same episodes as BOUNDARY (v1). v1's classes and branch stay as they are; this report splits them.", ""]
    put_section(eps, lines, out)
    swap_section(eps, lines, out)
    R = q.O / "report"
    R.mkdir(parents=True, exist_ok=True)
    md = Path(args.out) if args.out else R / f"BOUNDARY2_{datetime.now(q.BJ):%Y%m%d_%H%M}.md"
    md.write_text("\n".join(lines) + "\n")
    md.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str))
    print("\n".join(lines))
    print(f"\nBOUNDARY2: {md}  (+ .json with every episode)")


if __name__ == "__main__":
    main()
