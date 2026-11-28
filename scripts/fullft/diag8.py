#!/usr/bin/env python3
"""Plan v22 diagnostic 8 (Fable, rev. 1; registered in claude/MemWAM_Plan_v22_20261128.md, appendix): re-evaluate the
main-table checkpoints of three lagging tasks with a different execution protocol (the strongest pure WAMs predict 16
and execute 16 targets per decision and denoise with 50 steps; we predict 32, execute 8, 10 Euler steps). Described
only; no verdict. Written 11-28 17:20 (Opus), before any episode of these settings.

Settings (A40, official seed-42 banks, default noise; new episodes in closed_loop/d8):
  swapT_x16 / swapT_x32 / swapT_s50   swapT_ar_e30 (the swap_T main-table cell, 51/100, H100 class) with --execute 16 /
                                       --execute 32 / --steps 50; original = closed_loop/e6 swapT_ar_e30 (execute 8, 10 steps)
  press_x16 / press_x32 / press_s50    press_fast_e30 (26/100); original = closed_loop/e17 press_fast_e30
  rearr18_x16                          rearr_pw_s18_e30 (61/100); original = closed_loop/v21 rearr_pw_s18_e30
Rule of the plan (v22b part 3 section 3): a setting is chosen on scenes 1-50 only; if it succeeds 8 or more times more
than the original on the same 50 scenes, the same setting is re-evaluated on 51-100 automatically (the gate below) and
reported on 1-100 with 51-100 listed apart; the user then decides which protocol the main table uses.

  python3 scripts/fullft/diag8.py report          -> outputs/fullft/DIAG_V22_DIAG8.json (+ printed)
  python3 scripts/fullft/diag8.py gate <setting>  -> exit 0 if the setting gained >= 8 on 1-50 (all 50 of both sides
                                                    finished), exit 3 otherwise (pool5 then keeps its 51-100 tasks
                                                    blocked through requires_pass)
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = Path("/workspace/FastWAM-memory2/outputs/fullft")


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dv = _module("deed_verdict", "deed_verdict.py")
success, compare = dv.success, dv.compare

# setting -> (task, new label, original label, original folder)
SETTINGS = {
    "swapT_x16": ("swap_T", "swapT_ar_e30_x16", "swapT_ar_e30", "e6"),
    "swapT_x32": ("swap_T", "swapT_ar_e30_x32", "swapT_ar_e30", "e6"),
    "swapT_s50": ("swap_T", "swapT_ar_e30_s50", "swapT_ar_e30", "e6"),
    "press_x16": ("press_button", "press_fast_e30_x16", "press_fast_e30", "e17"),
    "press_x32": ("press_button", "press_fast_e30_x32", "press_fast_e30", "e17"),
    "press_s50": ("press_button", "press_fast_e30_s50", "press_fast_e30", "e17"),
    "rearr18_x16": ("rearrange_blocks", "rearr_pw_s18_e30_x16", "rearr_pw_s18_e30", "v21"),
}
LINE = 8          # "8 or more successes more than the original on scenes 1-50"


def one(name):
    task, new_l, ref_l, ref_f = SETTINGS[name]
    order, ref = success(ref_f, ref_l, task)
    _, new = success("d8", new_l, task)
    first, second = order[:50], order[50:100]
    out = {"task": task, "new": f"d8:{new_l}", "original": f"{ref_f}:{ref_l}",
           "finished_1_50": {"new": sum(x in new for x in first), "original": sum(x in ref for x in first)}}
    if not any(x in new and x in ref for x in first):     # 11-28 20:32: settings not run yet (the report crashed
        out.update(scenes_1_50=None, gain_1_50=None, reaches_line=False, status="no paired episodes yet")
        return out                                        # on press / rearrange with zero pairs at 19:33)
    c50 = compare(new, ref, first)
    out["scenes_1_50"] = c50
    out["gain_1_50"] = c50["new"] - c50["ref"]
    out["reaches_line"] = bool(c50["scenes"] == 50 and out["gain_1_50"] >= LINE)
    if sum(x in new for x in second) > 0:
        out["scenes_51_100"] = compare(new, ref, second)
        out["scenes_1_100"] = compare(new, ref, order[:100])
    return out


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "gate":
        r = one(sys.argv[2])
        print(f"DIAG8 GATE {sys.argv[2]}: gain on 1-50 = {r['gain_1_50']} ({r['scenes_1_50']}), "
              f"{'re-evaluate 51-100' if r['reaches_line'] else 'below the line: no re-evaluation'}")
        sys.exit(0 if r["reaches_line"] else 3)
    res = {"run": "plan v22 diagnostic 8: execution protocol re-evaluation (described)", "line": LINE,
           "settings": {k: one(k) for k in SETTINGS}, "verdict": "DESCRIBED"}
    (F / "DIAG_V22_DIAG8.json").write_text(json.dumps(res, indent=1) + "\n")
    for k, v in res["settings"].items():
        if v["scenes_1_50"] is None:
            print(f"{k:12s} {v['status']}")
            continue
        print(f"{k:12s} 1-50: {v['scenes_1_50']['new']} vs {v['scenes_1_50']['ref']} of {v['scenes_1_50']['scenes']} "
              f"(gain {v['gain_1_50']}; line reached {v['reaches_line']})"
              + (f"; 1-100 {v['scenes_1_100']['new']} vs {v['scenes_1_100']['ref']}" if "scenes_1_100" in v else ""))
    print("DIAG8 REPORT written", F / "DIAG_V22_DIAG8.json")


if __name__ == "__main__":
    main()
