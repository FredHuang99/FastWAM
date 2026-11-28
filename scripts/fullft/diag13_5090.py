"""Plan v22 diagnostic 13 (appendix of claude/MemWAM_Plan_v22_20261128.md), 11-28 18:20 Opus, written before any of
these counts is read. CPU, the 5090 (the official demos are there). DESCRIBED ONLY.
Per task: how many times its KEY DECISION occurs in each of the 50 official demos, from the demos' own proprioceptive
events (events_stats.py / events.py rule A, recomputed here from the hdf5 with the detector the events files use), next to
our best / the pure-WAM best (self-reported) and the two-training spread where one exists (numbers copied below with
their sources). Key decision per task (fixed now):
  put_back_block, rearrange_blocks   button presses ('bottom' events)
  press_button                       button presses ('bottom')
  blocks_ranking_try                 button presses ('bottom') and block swaps (gripper openings 'open')
  swap_blocks, cover_blocks          gripper openings ('open', the put-downs)
  swap_T                             gripper openings per arm ('open' of each arm)
  observe_and_pickup                 the first gripper closing (the choice; one per demo by construction)
  battery_try                        gripper openings ('open')
For put_back_block and rearrange_blocks (the "press once" pair; put_back is solved by the three-frame model, rearrange
is not) also, at each press: the pressing arm's gripper reading (closed < 0.35 = still holding something), and the
approach over the 24 frames before the press (vertical vs horizontal travel of the pressing end-effector, cm).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag13_5090.py   -> outputs/fullft/DIAG_V22_DIAG13.json
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))
OUT = Path("/workspace/FastWAM-memory2/outputs/fullft")
KEY = {"put_back_block": [("bottom", None)], "rearrange_blocks": [("bottom", None)], "press_button": [("bottom", None)],
       "blocks_ranking_try": [("bottom", None), ("open", None)], "swap_blocks": [("open", None)],
       "cover_blocks": [("open", None)], "swap_T": [("open", 0), ("open", 1)], "battery_try": [("open", None)],
       "observe_and_pickup": [("close-first", None)]}
# copied from claude/MemWAM_LeaderboardData_20261127.md section 0 / 1 (11-28 16:30 version); spread = |two trainings|
CONTEXT = {"put_back_block": (100, 100, None), "swap_blocks": (100, 100, None), "battery_try": (96, 48, None),
           "cover_blocks": (99, 98, None), "rearrange_blocks": (93, 100, "93 / 61 (rearr_pw seeds 17 / 18), 33 / 47 (rearr_v3c H100 / H200)"),
           "blocks_ranking_try": (91, 100, None), "swap_T": (51, 97, "49 / 39 (swapT_arprop H100 / H200)"),
           "observe_and_pickup": (16, 28, None), "press_button": (26, 87, None)}


def main():
    import numpy as np
    import events_stats as es
    from fastwam.fullft.events import EventRule, detect
    rep = {"run": "plan v22 diagnostic 13: key decisions per demo (described)", "tasks": {}}
    for task, keys in KEY.items():
        files = es.demo_files(task)
        per, press = [], []
        for f in files:
            g, pos = es.read_demo(f)
            evs = detect(g, pos, EventRule())          # rule A, as events_stats.py writes the events files
            row = {}
            for kind, arm in keys:
                if kind == "close-first":
                    row["first close"] = int(any(e["kind"] == "close" for e in evs))
                else:
                    row[f"{kind}{'' if arm is None else ' arm ' + str(arm)}"] = sum(
                        1 for e in evs if e["kind"] == kind and (arm is None or int(e["arm"]) == arm))
            per.append(row)
            if task in ("put_back_block", "rearrange_blocks"):
                for e in evs:
                    if e["kind"] != "bottom":
                        continue
                    t, a = int(e["frame"]), int(e["arm"])
                    lo = max(0, t - 24)
                    d = pos[t, a] - pos[lo, a]
                    press.append({"gripper_at_press": round(float(g[t, a]), 3),
                                  "holding (gripper < 0.35)": bool(g[t, a] < 0.35),
                                  "approach_vertical_cm": round(100 * abs(float(d[2])), 1),
                                  "approach_horizontal_cm": round(100 * float(np.hypot(d[0], d[1])), 1)})
        summ = {}
        for k in (per[0].keys() if per else []):
            v = [r[k] for r in per]
            summ[k] = {"min": min(v), "median": statistics.median(v), "max": max(v)}
        ours, best, spread = CONTEXT[task]
        rep["tasks"][task] = {"demos": len(per), "key_decisions_per_demo": summ, "ours_best": ours,
                              "pure_wam_best_self_reported": best, "gap": ours - best, "two_training_spread": spread}
        if press:
            rep["tasks"][task]["presses"] = {
                "n": len(press), "holding_at_press": sum(p["holding (gripper < 0.35)"] for p in press),
                "approach_vertical_cm_median": statistics.median(p["approach_vertical_cm"] for p in press),
                "approach_horizontal_cm_median": statistics.median(p["approach_horizontal_cm"] for p in press)}
        print(f"{task:20s} demos {len(per):3d} {json.dumps(summ)} gap {ours - best:+d}"
              + (f" presses {json.dumps(rep['tasks'][task].get('presses'))}" if press else ""), flush=True)
    rep["verdict"] = "DESCRIBED"
    (OUT / "DIAG_V22_DIAG13.json").write_text(json.dumps(rep, indent=1) + "\n")
    print("DIAG 13 written outputs/fullft/DIAG_V22_DIAG13.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
