"""Press event-rule sweep (11-16 night, Opus; CPU only; episodes and demos are read, never written).

Why. The press ledger audit (press_ledger_audit.py, 11-16) found that most extra presses of the ledger model start
about 16 frames after the last correct press, while a press reaches the ledger about 19 frames after it registers
(rule A: the bottom is confirmed only after the hand has risen delta = 1.5 cm, then the write lag of 4 frames, then
the next decision). At e30 a second loss adds up: shallower strokes (< 3 cm) fall under the debounce path (3 cm) and
are not recorded at all (recall 0.84). This script measures, without any GPU, what other thresholds of the SAME
detector (events.py; only delta and min_path change) would record and when.

What. For every rule of the grid delta x min_path:
  closed loop  replay the detector on the frames the models actually executed (executed_actions.jsonl: end-effector
               poses ee_before = the observation's endpose; gripper = the observation's joint vector, columns 6 / 13,
               exactly what FullSession._detect streams) of the given labels; registered presses = increments of the
               simulator's press counters (ground truth, as in the audit). Per label: recall (buttons 1 + 2: a bottom
               of either arm within +-10 frames, one-to-one in time order), spurious bottoms per registered press
               (bottoms matching no registered press of any button), confirmation latency (confirmed - press frame),
               visible delay at lag 4 and lag 0 (first logged decision frame v with v >= confirmed + lag and
               v > the event frame, minus the press frame), and the share of presses visible at the FIRST decision
               after the press (the decision that plans the next stroke).
  demos        the 50 press_button demos (events_stats.read_demo): coverage of the demo presses (a bottom of that arm
               within the press's bottom frames +-2; scripts/memory_v2/press/events.py), spurious bottoms per demo
               press, confirmation latency, events per demo (ledger cap 32).
  check        rule A replayed must equal what the models were given: bottoms visible by the last decision vs the
               bottoms logged in decisions.jsonl (Jaccard per label), and the demos' rule-A events vs the training
               file events_press_button.json (equal demos / all).

Pre-registered pick (written 11-16 19:50 BJ, before this script ran on any data):
  eligible   (relative to rule A on the same demos, so a property rule A already has cannot exclude everything)
             demo coverage >= rule A's - 0.005; demo spurious bottoms per demo press <= max(0.05, rule A's + 0.02);
             demos with <= 32 events (the ledger cap) >= rule A's count - 5; closed-loop spurious bottoms <= 0.15 per
             registered press (pooled over the ledger labels given; rule A in the audit: 0.09-0.11)
  objective  highest pooled closed-loop recall; within 0.005 of the best: the larger share visible at the first
             decision (lag 0), then the larger delta, then the larger min_path (the more conservative rule)
  default    the pick must beat rule A by recall >= +0.02 OR by the visible-at-first-decision share (both at lag 0)
             >= +0.20; otherwise SELECTED = rule A (then the test-time arm T1 of lat_5090.sh repeats T0)
  floor      replay check Jaccard >= 0.98 on every ledger label and demo equality >= 48/50; else NO PICK (rule A)
Outputs: outputs/fullft/align/press_event_sweep.json (all numbers), PRESS_FAST_RULE.json (the pick), and, when the
pick is not rule A, outputs/fullft/events/events_press_button_fast.json (the demos' events under the pick, the
format of events_stats.py, its "rule" field = the pick) for a possible retrain (needs the user's approval: plan v11
froze rule A before W2).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_event_sweep.py g1:press_arprop_e20 g1:press_arprop_e30 \
      rep:press_arprop_e20_r1 rep:press_arprop_e30_r1 sel:press_arprop_e20
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

R = Path("/workspace/FastWAM-memory2")
REPO = Path(__file__).resolve().parents[2]            # = R on the machines
sys.path.insert(0, str(REPO / "src"))
from fastwam.fullft.events import EventRule, detect  # noqa: E402

O = R / "outputs/memory_v2"
ALIGN = R / "outputs/fullft/align"
EVENTS = R / "outputs/fullft/events"
TASK = "press_button"
COUNTERS = (("press_cnt_1", 1), ("press_cnt_2", 2), ("press_cnt_check_button", 3))
W = 10
DELTAS = (0.015, 0.012, 0.010, 0.008, 0.006, 0.005)
PATHS = (0.03, 0.025, 0.02, 0.015, 0.012, 0.01)
RULE_A = (0.015, 0.03)


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("/", "_"), REPO / f"scripts/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_jsonl(path: Path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def episode_inputs(directory: Path):
    rows = read_jsonl(directory / "executed_actions.jsonl")
    if not rows or any(not r.get("ee_before") for r in rows):
        return None
    grip = np.asarray([[r["command_echo_before"][6], r["command_echo_before"][13]] for r in rows], dtype=np.float64)
    pos = np.asarray([[r["ee_before"]["left"][:3], r["ee_before"]["right"][:3]] for r in rows], dtype=np.float64)
    first = rows[0].get("objects_before") or {}
    prev = {c: int(first.get(c) or 0) for c, _ in COUNTERS}
    presses = []
    for i, r in enumerate(rows):
        a = r.get("objects_after") or {}
        for c, b in COUNTERS:
            v = int(a.get(c) or 0)
            presses += [{"frame": i + 1, "button": b}] * max(0, v - prev[c])
            prev[c] = max(prev[c], v)
    presses.sort(key=lambda p: (p["frame"], p["button"]))
    decisions = read_jsonl(directory / "decisions.jsonl")
    frames = sorted(int(d["frame_id"]) for d in decisions)
    logged = {(int(e[0]), int(e[1])) for d in decisions for e in (d.get("ledger") or []) if e[2] == "bottom"}
    return {"grip": grip, "pos": pos, "presses": presses, "decisions": frames, "logged": logged}


def match(presses, bottoms):
    """One-to-one in time order: each press takes the nearest free bottom within +-W. Returns {press index: bottom}."""
    free = sorted(bottoms, key=lambda e: (e["frame"], e["arm"]))
    out = {}
    for i, p in enumerate(presses):
        cand = [b for b in free if abs(b["frame"] - p["frame"]) <= W]
        if cand:
            b = min(cand, key=lambda b: (abs(b["frame"] - p["frame"]), b["frame"]))
            free.remove(b)
            out[i] = b
    return out, free


def visible(decisions, b, lag):
    for v in decisions:
        if v > b["frame"] and v >= b["confirmed"] + lag:
            return v
    return None


def closed_loop(ep, rule):
    evs = detect(ep["grip"], ep["pos"], rule)
    bottoms = [e for e in evs if e["kind"] == "bottom"]
    m, free = match(ep["presses"], bottoms)
    out = {"registered": 0, "recorded": 0, "spurious": len(free), "events": len(evs), "confirm": [], "vis4": [],
           "vis0": [], "first4": 0, "first0": 0, "nvis": 0}
    for i, p in enumerate(ep["presses"]):
        if p["button"] == 3:
            continue
        out["registered"] += 1
        b = m.get(i)
        if b is None:
            continue
        out["recorded"] += 1
        out["confirm"].append(b["confirmed"] - p["frame"])
        nxt = next((v for v in ep["decisions"] if v > p["frame"]), None)
        v4, v0 = visible(ep["decisions"], b, 4), visible(ep["decisions"], b, 0)
        if nxt is None or v0 is None:
            continue
        out["nvis"] += 1
        out["vis4"].append(None if v4 is None else v4 - p["frame"])
        out["vis0"].append(v0 - p["frame"])
        out["first4"] += v4 == nxt
        out["first0"] += v0 == nxt
    return out, bottoms


def demo_stats(grip, pos, rule, pm):
    evs = detect(grip, pos, rule)
    covered = total = spurious = 0
    lat = []
    for arm in (0, 1):
        z, xy = pos[:, arm, 2], pos[:, arm, :2]
        ps = pm.presses(z, xy)
        mine = [e for e in evs if e["arm"] == arm and e["kind"] == "bottom"]
        used = set()
        for p in ps:
            total += 1
            a, b = p["bottom"]
            hit = [j for j, e in enumerate(mine) if a - 2 <= e["frame"] <= b + 2]
            if hit:
                covered += 1
                used.update(hit)
                lat.append(mine[hit[0]]["confirmed"] - p["t"])
        term = pm.terminal_press(z, xy)
        for j, e in enumerate(mine):
            if j in used:
                continue
            if term is not None and abs(e["frame"] - (term["t"] if isinstance(term, dict) else int(term))) <= 5:
                continue
            spurious += 1
    return {"covered": covered, "total": total, "spurious": spurious, "latency": lat, "events": len(evs)}, evs


def med(v):
    v = [x for x in v if x is not None]
    return float(statistics.median(v)) if v else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labels", nargs="+", help="FOLDER:LABEL of press ledger runs (closed_loop/<FOLDER>/<LABEL>)")
    ap.add_argument("--no-write", action="store_true", help="numbers only (no pick file, no events file)")
    args = ap.parse_args()
    t0 = time.time()
    rules = [(d, m) for d in DELTAS for m in PATHS]
    es = load("fullft/events_stats")
    pm = es.press_module()
    # ---- closed loop
    labels = {}
    for spec in args.labels:
        folder, label = spec.split(":", 1)
        base = O / "closed_loop" / folder / label / "on" / TASK
        eps = []
        for d in sorted(base.glob("seed_*")):
            if (d / "result.json").exists() and (d / "executed_actions.jsonl").exists():
                e = episode_inputs(d)
                if e is not None:
                    eps.append(e)
        labels[spec] = eps
        print(f"[sweep] {spec}: {len(eps)} episodes read ({time.time() - t0:.0f} s)", flush=True)
    # ---- demos
    demos = []
    for f in es.demo_files(TASK):
        try:
            demos.append((f, *es.read_demo(f)))
        except Exception as exc:                                    # noqa: BLE001
            print(f"[sweep] demo {f.name}: {type(exc).__name__}: {exc}")
    train_file = EVENTS / f"events_{TASK}.json"
    train_events = json.loads(train_file.read_text())["episodes"] if train_file.exists() else {}
    print(f"[sweep] {len(demos)} demos read; training events file {'found' if train_events else 'MISSING'}", flush=True)
    # ---- sweep
    rows, check = [], {}
    for d, m in rules:
        rule = EventRule(delta=d, min_path=m)
        row = {"delta": d, "min_path": m, "labels": {}}
        pool = {"registered": 0, "recorded": 0, "spurious": 0, "nvis": 0, "first0": 0, "first4": 0,
                "confirm": [], "vis0": [], "vis4": []}
        for spec, eps in labels.items():
            agg = {k: (0 if not isinstance(v, list) else []) for k, v in pool.items()}
            agg["events"] = 0
            jac = []
            for ep in eps:
                o, bottoms = closed_loop(ep, rule)
                for k in agg:
                    agg[k] = agg[k] + o[k] if isinstance(agg[k], list) else agg[k] + o[k]
                if (d, m) == RULE_A and ep["logged"]:
                    last = ep["decisions"][-1]
                    mine = {(b["frame"], b["arm"]) for b in bottoms if b["confirmed"] + 4 <= last and b["frame"] < last}
                    jac.append(len(mine & ep["logged"]) / max(1, len(mine | ep["logged"])))
            if (d, m) == RULE_A:
                check[spec] = round(float(np.mean(jac)), 4) if jac else None
            for k in pool:
                pool[k] = pool[k] + agg[k]
            row["labels"][spec] = {
                "episodes": len(eps), "registered": agg["registered"], "recall": round(agg["recorded"] / max(1, agg["registered"]), 3),
                "spurious_per_press": round(agg["spurious"] / max(1, agg["registered"]), 3),
                "confirm_median": med(agg["confirm"]), "visible_median_lag4": med(agg["vis4"]),
                "visible_median_lag0": med(agg["vis0"]), "first_decision_lag4": round(agg["first4"] / max(1, agg["nvis"]), 3),
                "first_decision_lag0": round(agg["first0"] / max(1, agg["nvis"]), 3),
                "events_per_episode": round(agg["events"] / max(1, len(eps)), 1)}
        row["pool"] = {"recall": round(pool["recorded"] / max(1, pool["registered"]), 4),
                       "spurious_per_press": round(pool["spurious"] / max(1, pool["registered"]), 4),
                       "confirm_median": med(pool["confirm"]), "visible_median_lag4": med(pool["vis4"]),
                       "visible_median_lag0": med(pool["vis0"]),
                       "first_decision_lag4": round(pool["first4"] / max(1, pool["nvis"]), 4),
                       "first_decision_lag0": round(pool["first0"] / max(1, pool["nvis"]), 4)}
        cov = tot = spu = within = 0
        lat, equal = [], 0
        for f, grip, pos in demos:
            s, evs = demo_stats(grip, pos, rule, pm)
            cov += s["covered"]; tot += s["total"]; spu += s["spurious"]; lat += s["latency"]
            within += s["events"] <= 32
            if (d, m) == RULE_A:
                ref = train_events.get(f"{TASK}/{f.stem}")
                key = lambda e: (int(e["frame"]), int(e["arm"]), e["kind"], int(e["confirmed"]))   # noqa: E731
                equal += ref is not None and sorted(map(key, ref)) == sorted(map(key, evs))
        row["demos"] = {"n": len(demos), "coverage": round(cov / max(1, tot), 4), "presses": tot,
                        "spurious_per_press": round(spu / max(1, tot), 4), "confirm_median": med(lat),
                        "within_cap": within}
        if (d, m) == RULE_A:
            check["demos_equal_training_file"] = f"{equal}/{len(demos)}"
        rows.append(row)
        p, q = row["pool"], row["demos"]
        print(f"[sweep] delta {d:.3f} min_path {m:.3f}: closed loop recall {p['recall']:.3f} spurious/press "
              f"{p['spurious_per_press']:.3f} confirm {p['confirm_median']} visible lag4 {p['visible_median_lag4']} "
              f"lag0 {p['visible_median_lag0']} first-decision lag4 {p['first_decision_lag4']:.2f} lag0 "
              f"{p['first_decision_lag0']:.2f} | demos coverage {q['coverage']:.3f} spurious/press "
              f"{q['spurious_per_press']:.3f} confirm {q['confirm_median']} <=32 events {q['within_cap']}/{q['n']}",
              flush=True)
    # ---- pick
    ledger_labels = [s for s in labels if labels[s] and any(ep["logged"] for ep in labels[s])]
    floor = all((check.get(s) or 0) >= 0.98 for s in ledger_labels) and \
        int(str(check.get("demos_equal_training_file", "0/0")).split("/")[0]) >= 48
    base = next(r for r in rows if (r["delta"], r["min_path"]) == RULE_A)
    bd = base["demos"]
    elig = [r for r in rows if r["demos"]["coverage"] >= bd["coverage"] - 0.005
            and r["demos"]["spurious_per_press"] <= max(0.05, bd["spurious_per_press"] + 0.02)
            and r["demos"]["within_cap"] >= bd["within_cap"] - 5 and r["pool"]["spurious_per_press"] <= 0.15]
    pick, why = RULE_A, ""
    if not floor:
        why = f"NO PICK (floor: replay check {check}); rule A kept"
    elif not elig:
        why = "no eligible rule; rule A kept"
    else:
        best = max(r["pool"]["recall"] for r in elig)
        top = [r for r in elig if r["pool"]["recall"] >= best - 0.005]
        top.sort(key=lambda r: (r["pool"]["first_decision_lag0"], r["delta"], r["min_path"]), reverse=True)
        c = top[0]
        gain_r = c["pool"]["recall"] - base["pool"]["recall"]
        gain_v = c["pool"]["first_decision_lag0"] - base["pool"]["first_decision_lag0"]
        if (c["delta"], c["min_path"]) != RULE_A and (gain_r >= 0.02 or gain_v >= 0.20):
            pick = (c["delta"], c["min_path"])
            why = f"recall {base['pool']['recall']:.3f} -> {c['pool']['recall']:.3f}; first-decision share (lag 0) " \
                  f"{base['pool']['first_decision_lag0']:.2f} -> {c['pool']['first_decision_lag0']:.2f}"
        else:
            why = f"best eligible ({c['delta']}, {c['min_path']}) does not beat rule A enough (recall {gain_r:+.3f}, " \
                  f"first-decision share {gain_v:+.2f}); rule A kept"
    print(f"[sweep] replay check (rule A replay vs what the model was given): {check}")
    print(f"SELECTED delta {pick[0]} min_path {pick[1]} ({why})")
    ALIGN.mkdir(parents=True, exist_ok=True)
    report = {"labels": list(labels), "rules": rows, "check": check, "floor": floor, "eligible": len(elig),
              "selected": {"delta": pick[0], "min_path": pick[1], "why": why}, "seconds": round(time.time() - t0)}
    (ALIGN / "press_event_sweep.json").write_text(json.dumps(report, indent=1) + "\n")
    if args.no_write:
        return
    (R / "outputs/fullft").mkdir(parents=True, exist_ok=True)
    (R / "outputs/fullft/PRESS_FAST_RULE.json").write_text(json.dumps(report["selected"]) + "\n")
    if pick != RULE_A:
        rule = EventRule(delta=pick[0], min_path=pick[1])
        events = {f"{TASK}/{f.stem}": detect(grip, pos, rule) for f, grip, pos in demos}
        out = EVENTS / f"events_{TASK}_fast.json"
        EVENTS.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"rule": str(rule), "episodes": events}) + "\n")
        print(f"[sweep] events under the pick -> {out} ({len(events)} demos)")
    print(f"[sweep] -> {ALIGN / 'press_event_sweep.json'} ({time.time() - t0:.0f} s)")


if __name__ == "__main__":
    main()
