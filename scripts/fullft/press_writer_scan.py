"""Plan v14 E14 PRESS-tau, step 1: choose the press writer from the demos alone (registered by Fable 11-18, plan v14
section 3, approved by the user 18:33; this script written 11-19 08:30 BJ, before it ran on any data and before any
press_v3c exists). CPU only; reads the 50 press_button demos, writes only its own outputs.

Candidate family (Opus, plan v14: at least press_fast's thresholds, a two-stage "provisional then confirm" write, and
gripper events without the debounce), in order of simplicity (ties go to the simpler one):
  T(delta, min_path)        the rule-A detector (fullft.events) with other thresholds, write lag 0. T(0.012, 0.015) is
                            press_fast / press_count's writer. delta in {0.012, 0.010, 0.008, 0.006, 0.005, 0.004},
                            min_path in {0.015, 0.010, 0.005}
  G(0.012, 0.015)           as press_fast, but gripper events are never debounced
  P(eps)                    press_fast's events (existence decided as before), but each reversal becomes visible as
                            soon as the height has come back by eps (the provisional write) instead of delta;
                            eps in {0.002, 0.003, 0.005}. Online this needs a provisional detector (retract when the
                            reversal is not confirmed); flagged NEEDS ENGINEERING if chosen
Measured on the demos, with the definitions of E2 (scripts/fullft/audit_demos.py) and of the 11-16 sweep
(press_event_sweep.py):
  recall     demo presses covered by a bottom of that arm within the press's bottom frames +-2
  spurious   bottoms matching no demo press (the terminal confirm press excluded) per demo press
  tau        share of events with a next event and L + 8 <= G (L = confirmed - frame at lag 0, G = gap to the next event)
Registered pick (plan v14 E14, verbatim in meaning): among candidates with recall >= 0.98 and spurious <= 0.02, the
largest tau; ties -> the simpler. Margin (for T7): the chosen candidate's thresholds all x0.8 and all x1.2 keep recall
>= 0.95, else the next one. Largest tau < 0.9 (or nothing eligible) -> NO TIMELY WRITER (no training; old H200 goes on).
Outputs: outputs/fullft/E14_WRITER_VERDICT.json (all numbers + the pick; the name matches the A40's results push);
when the pick is a T candidate (P / G need the online detector first): outputs/fullft/PRESS_V3C_RULE.json ({"delta", "min_path"}, the format
history.event_rule_from reads) and outputs/fullft/events/events_press_button_v3c.json (the demos' events under the pick)
and, with --relay, both to the relay diag/press_v3c (the old H200's v3c_ready.sh fetches them).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_writer_scan.py [--relay]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

R = Path("/workspace/FastWAM-memory2")
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from fastwam.fullft.events import EventDetector, EventRule, detect  # noqa: E402

TASK = "press_button"
F = R / "outputs/fullft"


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("/", "_"), REPO / f"scripts/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class GripNoDebounce(EventDetector):
    """press_fast's detector, gripper events never debounced (the path counter still restarts at every event)."""

    def _emit(self, arm, out, frame, side, kind):
        if kind in ("close", "open"):
            out.append({"frame": int(frame), "arm": side, "kind": kind})
            arm.path_since_event = 0.0
            return
        super()._emit(arm, out, frame, side, kind)


def detect_with(det_cls, grip, pos, rule):
    d = det_cls(rule)
    evs = []
    for t in range(len(grip)):
        for e in d.step(t, grip[t], pos[t]):
            e["confirmed"] = t
            evs.append(e)
    return sorted(evs, key=lambda e: (e["frame"], e["arm"]))


def provisional(evs, pos, eps):
    """Each reversal visible once the height has come back by eps from its turning point (never later than before)."""
    out = []
    for e in evs:
        e = dict(e)
        if e["kind"] in ("bottom", "top"):
            z = pos[:, e["arm"], 2]
            z0, sign = z[e["frame"]], (1.0 if e["kind"] == "bottom" else -1.0)
            t = next((t for t in range(e["frame"] + 1, int(e["confirmed"]) + 1) if sign * (z[t] - z0) >= eps),
                     int(e["confirmed"]))
            e["confirmed"] = int(t)
        out.append(e)
    return out


def candidates():
    out = [("T", 0.012, 0.015, None)]
    for d in (0.012, 0.010, 0.008, 0.006, 0.005, 0.004):
        for m in (0.015, 0.010, 0.005):
            if (d, m) != (0.012, 0.015):
                out.append(("T", d, m, None))
    out.append(("G", 0.012, 0.015, None))
    for eps in (0.002, 0.003, 0.005):
        out.append(("P", 0.012, 0.015, eps))
    return out


def name(c):
    k, d, m, eps = c
    return f"{k}({d}, {m})" if k != "P" else f"P(eps {eps}; delta {d}, min_path {m})"


def events_of(c, grip, pos):
    k, d, m, eps = c
    rule = EventRule(delta=d, min_path=m)
    if k == "T":
        return detect(grip, pos, rule)
    if k == "G":
        return detect_with(GripNoDebounce, grip, pos, rule)
    return provisional(detect(grip, pos, rule), pos, eps)


def measure(c, demos, pm, au):
    covered = total = spurious = 0
    timely = []
    for grip, pos, states in demos:
        evs = events_of(c, grip, pos)
        rec = au.demo_record(evs, pos, states, 0, len(grip))
        timely += rec["timely"]
        for arm in (0, 1):
            z, xy = pos[:, arm, 2], pos[:, arm, :2]
            mine = [e for e in evs if e["arm"] == arm and e["kind"] == "bottom"]
            used = set()
            for p in pm.presses(z, xy):
                total += 1
                a, b = p["bottom"]
                hit = [j for j, e in enumerate(mine) if a - 2 <= e["frame"] <= b + 2]
                if hit:
                    covered += 1
                    used.update(hit)
            term = pm.terminal_press(z, xy)
            for j, e in enumerate(mine):
                if j in used:
                    continue
                if term is not None and abs(e["frame"] - (term["t"] if isinstance(term, dict) else int(term))) <= 5:
                    continue
                spurious += 1
    return {"candidate": name(c), "recall": covered / max(1, total), "spurious_per_press": spurious / max(1, total),
            "tau": float(np.mean(timely)) if timely else float("nan"), "presses": total}


def scaled(c, f):
    k, d, m, eps = c
    return (k, round(d * f, 5), round(m * f, 5), None if eps is None else round(eps * f, 5))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relay", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    es, au = load("fullft/events_stats"), load("fullft/audit_demos")
    pm = es.press_module()
    from fastwam.memory_s1.data import read_episode
    files, demos = [], []
    for path in es.demo_files(TASK):                       # as audit_demos.load_task, keeping each demo's file
        try:
            grip, pos = es.read_demo(path)
            states = np.asarray(read_episode(path)[0], dtype=np.float64)[:len(grip)]
            files.append(path)
            demos.append((grip, pos, states))
        except Exception as exc:                          # noqa: BLE001
            print(f"[scan] {path.name}: unreadable ({exc})")
    print(f"[scan] {len(demos)} press demos read", flush=True)
    if len(demos) < 45:
        print("E14 WRITER: NO READING (< 45 demos)")
        (F / "E14_WRITER_VERDICT.json").write_text(json.dumps({"verdict": "NO READING", "demos": len(demos)}) + "\n")
        return 1
    rows = []
    for c in candidates():
        r = measure(c, demos, pm, au)
        r["eligible"] = r["recall"] >= 0.98 and r["spurious_per_press"] <= 0.02
        rows.append((c, r))
        print(f"[scan] {r['candidate']:40s} recall {r['recall']:.3f}  spurious/press {r['spurious_per_press']:.3f}  "
              f"tau {r['tau']:.3f}  {'eligible' if r['eligible'] else ''}", flush=True)
    order = sorted([x for x in rows if x[1]["eligible"]], key=lambda x: -x[1]["tau"])   # stable: ties keep simplicity
    pick, margin_log = None, []
    for c, r in order:
        if r["tau"] < 0.9:
            break
        lo, hi = measure(scaled(c, 0.8), demos, pm, au), measure(scaled(c, 1.2), demos, pm, au)
        ok = lo["recall"] >= 0.95 and hi["recall"] >= 0.95
        margin_log.append({"candidate": r["candidate"], "x0.8": lo, "x1.2": hi, "ok": ok})
        print(f"[scan] margin {r['candidate']}: recall x0.8 {lo['recall']:.3f}, x1.2 {hi['recall']:.3f} -> {'OK' if ok else 'fails'}")
        if ok:
            pick = (c, r)
            break
    if pick is None:
        best = order[0][1]["tau"] if order else float("nan")
        verdict = f"NO TIMELY WRITER (largest eligible tau {best:.3f} < 0.9, or margins failed)"
        print(f"E14 WRITER: {verdict}")
        out = {"verdict": "NO TIMELY WRITER", "why": verdict, "rows": [r for _, r in rows], "margins": margin_log}
    else:
        c, r = pick
        kind = c[0]
        out = {"verdict": "CHOSEN", "candidate": r["candidate"], "kind": kind, "delta": c[1], "min_path": c[2],
               "eps": c[3], "needs_engineering": kind in ("P", "G"), "tau": r["tau"], "recall": r["recall"],
               "spurious_per_press": r["spurious_per_press"], "rows": [x for _, x in rows], "margins": margin_log}
        print(f"E14 WRITER: CHOSEN {r['candidate']} (tau {r['tau']:.3f}, recall {r['recall']:.3f}, spurious/press "
              f"{r['spurious_per_press']:.3f}){' -- NEEDS ENGINEERING (the online detector)' if kind in ('P', 'G') else ''}")
        if kind == "T":
            (F / "PRESS_V3C_RULE.json").write_text(json.dumps({"delta": c[1], "min_path": c[2], "why": "plan v14 E14 writer scan"}) + "\n")
            events = {}
            for f, (grip, pos, _s) in zip(files, demos):
                events[f"{TASK}/{f.stem}"] = events_of(c, grip, pos)
            (F / "events").mkdir(parents=True, exist_ok=True)
            ev = F / "events/events_press_button_v3c.json"
            ev.write_text(json.dumps({"rule": str(EventRule(delta=c[1], min_path=c[2])), "episodes": events}) + "\n")
            print(f"[scan] events under the pick -> {ev} ({len(events)} demos)")
            if args.relay:
                hf = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else sys.executable
                subprocess.run([hf, str(REPO / "scripts/memory_v2/migrate/relay.py"), "put", str(F / "PRESS_V3C_RULE.json"),
                                str(ev), "--prefix", "diag/press_v3c"], check=False)
    out["seconds"] = round(time.time() - t0)
    (F / "E14_WRITER_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
