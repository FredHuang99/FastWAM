"""Plan v13 E2 AUDIT (11-17 19:00 BJ, Opus; card registered by Fable 11-17, approved by the user 15:40; this file was
written before it was run on any demo). CPU only; reads the RMBench demos, writes nothing but its own outputs.

Question: from the demos alone, before any training, can we predict on which tasks the body ledger helps and which
"table" a model will learn? Per task (all ten with demos) and per write setting:
  cur   = rule A (delta 0.015 m, min_path 0.03 m), write lag 4   (the ledger models trained so far)
  fast  = press_fast's thresholds (delta 0.012 m, min_path 0.015 m), lag 0   (E3 / E4)
the events of every demo are recomputed with fullft.events.detect (the trainer's detector) and measured:
  events / demo; G = gap to the next event (frames); L = write latency = confirmed + lag - frame;
  tau  = share of events that have a next event and satisfy L + 8 <= G (8 = frames executed per decision)
  r    = in-place repeat share: events whose arm joint state (6 joint angles, rad, L2) is within theta of the previous
         event of the same arm and kind. theta is set ONLY from press_button and swap_blocks (cur setting):
         theta = sqrt(q90(press 'bottom' distances) * q10(swap 'close' distances)) if q90 < q10, else the press median
  cue sufficiency, leave one demo out. Decision points: before each event k+1 (k = 0 .. n-1, events 1..k known).
    Target y = (kind, arm, where) of event k+1, where = the back-index (1 = most recent) among the earlier events of
    the same arm of the most recent one whose end-effector is within 3 cm, capped at 4, else "new" (layout-free).
    Plus one decision point after the last event with y = ("end",): knowing when to stop (e.g. go to the confirm
    button once the count is reached) is the decision most tasks fail on (added 18:50, before any real demo).
    s_time  key = the decision frame (frame of event k+1 minus 8; for "end": the demo's last frame minus 8),
            1-nearest neighbour among the other demos
    s_last  key = (kind, arm, where) of event k (or "empty")
    s_count key = number of events so far per (arm, kind)
    s_full  key = the whole sequence of (kind, arm, where) so far
    s_full_goal (context only, not used by any rule; added 18:55): s_full's key plus the demo's own final count per
            (arm, kind) = what a policy knows when the goal is visible (e.g. the press counts printed on the card)
    (the last three: majority y among the other demos' decision points with the same key; an unseen key -> the
    majority y of the other demos at the same decision index k; ties -> the smallest y)
Prediction rules (plan v13 E2, verbatim in meaning), per task and setting:
  rule 0  s_full < 0.7                         -> ledger gives NO GAIN (the answer is not in the body record)
  rule T  tau >= 0.9                           -> GAIN;  tau < 0.5 -> SMALL under this setting (larger when timely)
  rule R  s_last >= 0.9 * s_full               -> the current read suffices;
          s_last < 0.7 * s_full and s_count >= 0.9 * s_full -> NEEDS COUNTABLE CODE
  rule C  s_time >= 0.8                        -> the E5 clock arm presses early under a pause on this task
  ledger prediction = NONE if rule 0 fires, else GAIN / SMALL from rule T, else (0.5 <= tau < 0.9) none.
Measured later (not here): normalised gain = (ledger - AR) / (100 - AR), same machine and scenes; GAIN = >= 0.5,
SMALL = < 0.3, NONE = < 0.2; AR > 90 -> saturated, that prediction is void. Fits, not predictions: put, swap and
press (cur). Predictions: battery, rearrange, swap_T, cover, ranking (cur); press (fast) for E3; rule R on press for
E4; rule C for E5. LAW HOLDS if >= 4 non-void predictions and >= 80 % hit; LAW FAILS if <= 50 %; else partial.
Floor: >= 45 demos read and every counted demo has >= 2 events, else that task gets no prediction.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/audit_demos.py [--tasks ...]
Writes outputs/fullft/audit/E2_AUDIT_<time>.json and prints the table + the PREDICTIONS block (paste it back; Opus
commits it as scripts/fullft/E2_PREDICTIONS_REGISTERED.txt before any battery closed-loop result is read).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from fastwam.fullft.events import EventRule, detect  # noqa: E402

BJ = timezone(timedelta(hours=8))
TASKS = ["put_back_block", "swap_blocks", "press_button", "battery_try", "rearrange_blocks", "swap_T", "cover_blocks",
         "blocks_ranking_try", "observe_and_pickup", "place_block_mat"]
SETTINGS = {"cur": (EventRule(delta=0.015, min_path=0.03), 4), "fast": (EventRule(delta=0.012, min_path=0.015), 0)}
EXEC = 8
WHERE_RADIUS = 0.03
WHERE_CAP = 4
ARM_JOINTS = {0: slice(0, 6), 1: slice(7, 13)}


# ----------------------------------------------------------------------------- per demo
def where_refs(events, pos):
    """where of each event: back-index (1 = most recent) among earlier events of the same arm of the most recent one
    within WHERE_RADIUS of its end-effector position, capped at WHERE_CAP; 'new' if none."""
    out = []
    for i, e in enumerate(events):
        p = pos[e["frame"], e["arm"]]
        same = [j for j in range(i) if events[j]["arm"] == e["arm"]]
        ref = "new"
        for back, j in enumerate(reversed(same), 1):
            if np.linalg.norm(pos[events[j]["frame"], e["arm"]] - p) <= WHERE_RADIUS:
                ref = str(min(back, WHERE_CAP))
                break
        out.append(ref)
    return out


def demo_record(events, pos, joints, lag, n_frames=None):
    """Per-demo measurements and the decision points of the cue tests."""
    ev = sorted(events, key=lambda e: (e["frame"], e["arm"]))
    where = where_refs(ev, pos)
    tok = [(e["kind"], int(e["arm"]), w) for e, w in zip(ev, where)]
    gaps, lat, timely = [], [], []
    for k, e in enumerate(ev):
        L = int(e.get("confirmed", e["frame"])) + lag - int(e["frame"])
        lat.append(L)
        if k + 1 < len(ev):
            G = int(ev[k + 1]["frame"]) - int(e["frame"])
            gaps.append(G)
            timely.append(L + EXEC <= G)
    rep = []                                     # joint distance to the previous event of the same arm and kind
    for k, e in enumerate(ev):
        prev = next((ev[j] for j in range(k - 1, -1, -1) if ev[j]["arm"] == e["arm"] and ev[j]["kind"] == e["kind"]), None)
        if prev is not None:
            js = ARM_JOINTS[int(e["arm"])]
            rep.append((e["kind"], float(np.linalg.norm(joints[e["frame"], js] - joints[prev["frame"], js]))))
    points = []
    goal = tuple(sorted(Counter((a, kd) for kd, a, _ in tok).items()))
    n_frames = int(n_frames if n_frames is not None else len(pos))
    for k in range(len(ev) + 1):                 # before event k+1 (index k), events 0..k-1 known; k = n: the end
        known = tok[:k]
        counts = Counter((a, kd) for kd, a, _ in known)
        y = tok[k] if k < len(ev) else ("end",)
        t = int(ev[k]["frame"]) - EXEC if k < len(ev) else n_frames - EXEC
        points.append({"k": k, "y": y, "t": max(0, t), "last": known[-1] if known else ("empty",),
                       "count": tuple(sorted(counts.items())), "full": tuple(known), "fullg": (tuple(known), goal)})
    return {"n": len(ev), "gaps": gaps, "lat": lat, "timely": timely, "rep": rep, "points": points}


# ----------------------------------------------------------------------------- cue tests (leave one demo out)
def _majority(ys):
    c = Counter(ys)
    best = max(c.values())
    return min(y for y, n in c.items() if n == best)


def cue_accuracy(demos, key):
    """Leave one demo out accuracy of predicting y from points[key] (majority over the others; unseen key -> majority
    of the others at the same decision index; time -> 1-nearest neighbour on the decision frame)."""
    hit = tot = 0
    for i, d in enumerate(demos):
        others = [p for j, o in enumerate(demos) if j != i for p in o["points"]]
        if not others:
            continue
        if key == "t":
            ts = np.array([p["t"] for p in others])
            for p in d["points"]:
                dist = np.abs(ts - p["t"])
                near = [others[j]["y"] for j in np.flatnonzero(dist == dist.min())]
                hit += _majority(near) == p["y"]
                tot += 1
            continue
        table, by_k = defaultdict(list), defaultdict(list)
        for p in others:
            table[p[key]].append(p["y"])
            by_k[p["k"]].append(p["y"])
        allys = [p["y"] for p in others]
        for p in d["points"]:
            ys = table.get(p[key]) or by_k.get(p["k"]) or allys
            hit += _majority(ys) == p["y"]
            tot += 1
    return hit / tot if tot else float("nan")


def theta_from(press_dists, swap_dists):
    """In-place threshold from press 'bottom' and swap 'close' joint distances (rule in the docstring)."""
    if not press_dists or not swap_dists:
        return float("nan"), "no data"
    q90, q10 = float(np.quantile(press_dists, 0.9)), float(np.quantile(swap_dists, 0.1))
    if q90 < q10:
        return math.sqrt(max(q90, 1e-6) * q10), f"press q90 {q90:.4f} < swap q10 {q10:.4f}"
    return float(np.median(press_dists)), f"NOT separable (press q90 {q90:.4f} >= swap q10 {q10:.4f}): press median"


def summarise(demos, theta):
    q = lambda v, a: float(np.quantile(v, a)) if v else float("nan")          # noqa: E731
    gaps = [g for d in demos for g in d["gaps"]]
    lat = [x for d in demos for x in d["lat"]]
    timely = [x for d in demos for x in d["timely"]]
    reps = [x for d in demos for _, x in d["rep"]]
    n_events = sum(d["n"] for d in demos)
    s = {"demos": len(demos), "events_median": float(np.median([d["n"] for d in demos])) if demos else float("nan"),
         "events_max": max([d["n"] for d in demos] or [0]), "G_median": q(gaps, 0.5), "G_q10": q(gaps, 0.1),
         "L_median": q(lat, 0.5), "tau": float(np.mean(timely)) if timely else float("nan"),
         "r": (sum(x <= theta for x in reps) / n_events) if n_events and math.isfinite(theta) else float("nan")}
    for key, name in (("t", "s_time"), ("last", "s_last"), ("count", "s_count"), ("full", "s_full"),
                      ("fullg", "s_full_goal")):
        s[name] = cue_accuracy(demos, key)
    return s


def predict(s, floor_ok):
    if not floor_ok:
        return {"ledger": "NO PREDICTION (floor)", "read": "-", "clock": "-"}
    if s["s_full"] < 0.7:
        ledger = "NONE"
    elif s["tau"] >= 0.9:
        ledger = "GAIN"
    elif s["tau"] < 0.5:
        ledger = "SMALL"
    else:
        ledger = "none (0.5 <= tau < 0.9)"
    if s["s_last"] >= 0.9 * s["s_full"]:
        read = "CURRENT READ SUFFICES"
    elif s["s_last"] < 0.7 * s["s_full"] and s["s_count"] >= 0.9 * s["s_full"]:
        read = "NEEDS COUNTABLE CODE"
    else:
        read = "none"
    clock = "EARLY UNDER PAUSE" if s["s_time"] >= 0.8 else "none"
    return {"ledger": ledger, "read": read, "clock": clock}


# ----------------------------------------------------------------------------- IO
def load_task(task):
    sys.path.insert(0, str(REPO / "scripts/fullft"))
    from events_stats import demo_files, read_demo                         # noqa: E402
    from fastwam.memory_s1.data import read_episode                       # noqa: E402
    out = []
    for path in demo_files(task):
        try:
            grip, pos = read_demo(path)
            states = np.asarray(read_episode(path)[0], dtype=np.float64)[:len(grip)]
            out.append((grip, pos, states))
        except Exception as exc:                                          # noqa: BLE001
            print(f"  {task} {path.name}: unreadable ({exc})")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=TASKS)
    ap.add_argument("--out", default=str(REPO / "outputs/fullft/audit"))
    args = ap.parse_args()
    raw = {t: load_task(t) for t in args.tasks}
    recs = {s: {} for s in SETTINGS}
    for sname, (rule, lag) in SETTINGS.items():
        for t, demos in raw.items():
            recs[sname][t] = [demo_record(detect(g, p, rule), p, j, lag, len(g)) for g, p, j in demos]
    press = [x for d in recs["cur"].get("press_button", []) for k, x in d["rep"] if k == "bottom"]
    swap = [x for d in recs["cur"].get("swap_blocks", []) for k, x in d["rep"] if k == "close"]
    theta, why = theta_from(press, swap)
    print(f"in-place threshold theta = {theta:.4f} rad ({why})")
    table, preds = {}, {}
    for sname in SETTINGS:
        for t in args.tasks:
            demos = recs[sname][t]
            counted = [d for d in demos if d["n"] >= 2]
            floor_ok = len(demos) >= 45 and len(counted) == len(demos)
            s = summarise(demos, theta) if demos else {}
            table[(t, sname)] = s
            preds[(t, sname)] = predict(s, floor_ok) if demos else {"ledger": "NO DEMOS", "read": "-", "clock": "-"}
    cols = ("demos", "events_median", "events_max", "G_median", "G_q10", "L_median", "tau", "r",
            "s_time", "s_last", "s_count", "s_full", "s_full_goal")
    print("task                set  | " + " ".join(f"{c:>9s}" for c in cols))
    for (t, sname), s in table.items():
        print(f"{t:19s} {sname:4s} | " + " ".join(f"{s.get(c, float('nan')):9.3f}" for c in cols))
    print("\n===== PREDICTIONS (register before any battery closed-loop result is read) =====")
    print(f"theta {theta:.4f} rad; fits (known results): put_back_block, swap_blocks, press_button cur")
    for (t, sname), p in preds.items():
        print(f"{t:19s} {sname:4s} | ledger {p['ledger']:24s} | read {p['read']:22s} | clock {p['clock']}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BJ).strftime("%Y%m%d_%H%M")
    (out / f"E2_AUDIT_{stamp}.json").write_text(json.dumps(
        {"theta": theta, "theta_why": why, "table": {f"{t}|{s}": v for (t, s), v in table.items()},
         "predictions": {f"{t}|{s}": v for (t, s), v in preds.items()}}, indent=1) + "\n")
    print(f"\nwritten {out / f'E2_AUDIT_{stamp}.json'}")


if __name__ == "__main__":
    main()
