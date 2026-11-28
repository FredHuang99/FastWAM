#!/usr/bin/env python3
"""Plan v22 diagnostic 7(a) (Fable, rev. 1; appendix of claude/MemWAM_Plan_v22_20261128.md). Read-only, CPU, the A40's
existing episodes; DESCRIBED ONLY. Written 11-28 17:40 (Opus) before any of these numbers is read.
rearrange, the pre-event-weighted timely writer (rearr_pw), seed 18 (v21:rearr_pw_s18_e30, 61/100) beside seed 17
(v20:rearr_pw_e30, 93/100):
  pressed twice (22 in seed 18): at the decisions between the first and the second press, was the first press in the
    record (rearr_ledger.py's rule: a left-arm 'bottom' entry within +-15 targets of the press)? always / sometimes /
    never; the write delay (targets from the press to the first decision whose record has it).
  never pressed (17 in seed 18): how low the left hand got while within 4 cm (horizontally) of the button
    (rearr_press_depth.py's geometry: EE link height above the button base). Classes fixed now, before reading:
      ABOVE    within 4 cm, lowest height > 0.195 m (every counted press so far happened at 0.183-0.191 m; earlier
               never-pressed episodes stopped near 0.22 m; 4 mm margin over the deepest counted press height)
      AT DEPTH within 4 cm, lowest height <= 0.195 m (reached the depth, the press was not counted)
      FAR      never within 4 cm of the button horizontally
  majority_above (the decision tree's input for card 32, condition (b)): ABOVE > half of seed 18's never-pressed
    episodes.
  python3 scripts/fullft/diag7a.py   -> outputs/fullft/DIAG_V22_DIAG7A.json (+ printed)
"""
from __future__ import annotations

import importlib.util
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
TASK = "rearrange_blocks"
ABOVE_M = 0.195
ITEMS = [("seed18", "v21", "rearr_pw_s18_e30"), ("seed17", "v20", "rearr_pw_e30")]


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def depth_class(e):
    low = e.get("lowest_dz_within_4cm")
    if low is None:
        return "FAR"
    return "ABOVE" if low > ABOVE_M else "AT DEPTH"


def one(folder, label, pdepth, ledger, split):
    root = O / folder / label / "on" / TASK
    out = {"episodes": 0, "classes": Counter(), "pressed_twice": Counter(), "never_pressed": Counter(),
           "never_pressed_lowest_dz": [], "write_delay": [], "examples": {}}
    for d in sorted(root.glob("seed_*")):
        if not (d.is_dir() and d.name[5:].isdigit()):
            continue
        e = pdepth.episode(d, split)
        if not e or "why" in e:
            continue
        out["episodes"] += 1
        out["classes"][e["cls"]] += 1
        acts, decs = ledger.rows(d / "executed_actions.jsonl"), ledger.rows(d / "decisions.jsonl")
        t1, t2 = ledger.first_at(acts, 1), ledger.first_at(acts, 2)
        if t1 is not None and decs:
            seen = next((int(x["frame_id"]) for x in decs
                         if int(x["frame_id"]) > t1 and ledger.has_entry(x.get("ledger") or [], t1)), None)
            if seen is not None:
                out["write_delay"].append(seen - t1)
        if e["cls"].startswith("pressed twice") and t1 is not None and t2 is not None:
            between = [ledger.has_entry(x.get("ledger") or [], t1) for x in decs if t1 < int(x["frame_id"]) < t2]
            st = ("no decision in between" if not between else "always in the record" if all(between)
                  else "never in the record" if not any(between) else "sometimes in the record")
            out["pressed_twice"][st] += 1
            out["examples"].setdefault("twice: " + st, []).append(d.name[5:])
        if e["cls"].startswith("never pressed"):
            c = depth_class(e)
            out["never_pressed"][c] += 1
            out["examples"].setdefault("never: " + c, []).append(d.name[5:])
            if e.get("lowest_dz_within_4cm") is not None:
                out["never_pressed_lowest_dz"].append(round(e["lowest_dz_within_4cm"], 4))
    wd = out["write_delay"]
    res = {"episodes": out["episodes"], "classes": dict(out["classes"]),
           "pressed_twice_first_press_in_record": dict(out["pressed_twice"]),
           "never_pressed_depth": dict(out["never_pressed"]),
           "never_pressed_lowest_dz_m": sorted(out["never_pressed_lowest_dz"]),
           "write_delay_targets": ({"median": statistics.median(wd), "min": min(wd), "max": max(wd), "n": len(wd)}
                                   if wd else None),
           "examples": {k: v[:5] for k, v in out["examples"].items()}}
    return res


def main():
    pdepth = _module("rearr_press_depth", "rearr_press_depth.py")
    ledger = _module("rearr_ledger", "rearr_ledger.py")
    split = pdepth._split()
    rep = {"run": "plan v22 diagnostic 7(a): rearrange seed 18 vs 17, repeated presses and missed presses (described)",
           "above_threshold_m": ABOVE_M, "models": {}}
    for tag, folder, label in ITEMS:
        rep["models"][f"{tag} {folder}:{label}"] = r = one(folder, label, pdepth, ledger, split)
        print(f"\n== {tag} {folder}:{label}: {r['episodes']} episodes; classes {r['classes']}")
        print(f"   pressed twice, first press in the record between the presses: {r['pressed_twice_first_press_in_record']}")
        print(f"   never pressed, depth: {r['never_pressed_depth']}; lowest heights {r['never_pressed_lowest_dz_m']}")
        print(f"   write delay: {r['write_delay_targets']}")
    s18 = rep["models"][f"seed18 v21:rearr_pw_s18_e30"]
    n = sum(s18["never_pressed_depth"].values())
    above = s18["never_pressed_depth"].get("ABOVE", 0)
    rep["majority_above"] = bool(n > 0 and above > n / 2)
    rep["majority_rule"] = f"ABOVE {above} of {n} never-pressed episodes of seed 18 (> half -> true)"
    rep["verdict"] = "DESCRIBED"
    if s18["episodes"] < 100:
        rep["note"] = f"seed 18 has {s18['episodes']} episodes with poses (100 expected)"
    (F / "DIAG_V22_DIAG7A.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(f"\nDIAG 7A: majority_above {rep['majority_above']} ({rep['majority_rule']}); written outputs/fullft/DIAG_V22_DIAG7A.json")
    return 0 if s18["episodes"] >= 90 else 3      # too few episodes read: the task fails (the gate stays closed)


if __name__ == "__main__":
    sys.exit(main())
