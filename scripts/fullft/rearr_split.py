"""Why rearrange_blocks fails (11-22, Opus; user 18:23: find out why rearrange and observe_and_pickup do badly). Read-only,
CPU, zero GPU: reads the episodes already on the A40. Descriptive only.
The task (RMBench envs/rearrange_blocks.py, read 11-22): three slots in a row; block1 in the middle, block2 on one of two
mats (the other mat empty); a button on the left. Steps: (1) the right arm moves block1 onto the EMPTY mat; (2) the left
arm presses the button ONCE; (3) the right arm moves block2 (the one that was on a mat from the start) to the middle.
env.check_success (every physics step): press_cnt > 1 -> failed for good; the press counts as stage 1 only if at that
moment block1 is on the empty mat and block2 still on its mat (3 cm, z < 0.77); stage 2 (success) = block2 in the
middle (0.13, y) within 3 cm with the right gripper open, block1 still on its mat. After step 2 the scene looks the same
as before the press (both mats taken, the middle empty, the button back up), and the two blocks look alike: whether
the press happened, and which block was moved first, are not in the current image.
The adapter logs, after every executed target, block1 / block2 / button poses and stage_id / press_cnt / press_flag
(scripts/memory_s1/sim_feedback.object_snapshot), so no new run is needed.
Classes per episode, in this order:
  success                         result.json success
  pressed twice or more           final press_cnt >= 2 (sub: before / after step 1 was complete)
  pressed too early               press_cnt 1 but stage 0: at the press, block1 was not yet on the empty mat (or block2
                                  had left its mat)
  never pressed: block1 placed    block1 reached the empty mat, no press
  never pressed: block1 not placed  block1 lifted but never on the empty mat (dropped / elsewhere)
  moved block2 first              block2 lifted before block1 was ever on the empty mat (wrong block first)
  never moved a block
  stage 1, then moved block1 again   the just-placed block left its mat after the press (\"which block\" error)
  stage 1, block2 not in the middle  block2 lifted after the press but not placed within 3 cm of the middle
  stage 1, block2 in the middle, not finished (gripper not opened / episode ended)
  stage 1, second step never started (block2 never lifted after the press)
  other
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/rearr_split.py [FOLDER:LABEL ...]
Default: e6:rearrange_ar_e30 e6:rearrange_arprop_e30 e16:rearrange_clock_e30 r2:rearrange_ar_e30.
Writes outputs/fullft/REARR_SPLIT.json.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
TASK = "rearrange_blocks"
DEFAULT = ["e6:rearrange_ar_e30", "e6:rearrange_arprop_e30", "e16:rearrange_clock_e30", "r2:rearrange_ar_e30"]
TOL, LIFT, LOW = 0.03, 0.03, 0.77


def xy(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def pos(snap, name):
    v = snap.get(name)
    return v.get("p") if isinstance(v, dict) else None


def classify(rows, success):
    first = rows[0].get("objects_before") or {}
    snaps = [r.get("objects_after") or {} for r in rows]
    b1_0, b2_0 = pos(first, "block1"), pos(first, "block2")
    if b1_0 is None or b2_0 is None:
        return "other", {"why": "no block poses"}
    empty_mat = (0.28 - b2_0[0], b2_0[1])        # mats at x 0.02 / 0.26 (env), block2 starts on one of them
    middle = (0.13, b1_0[1])                     # env: empty_region_center = [0.13, block_y_lim]
    z0 = b1_0[2]

    def series(name):
        return [pos(s, name) for s in snaps]
    b1, b2 = series("block1"), series("block2")
    press = [s.get("press_cnt") for s in snaps]
    stage = [s.get("stage_id") for s in snaps]
    on_empty = [p is not None and xy(p, empty_mat) < TOL and p[2] < LOW for p in b1]
    b2_home = [p is not None and xy(p, b2_0) < TOL and p[2] < LOW for p in b2]
    b1_lift = [p is not None and p[2] > z0 + LIFT for p in b1]
    b2_lift = [p is not None and p[2] > z0 + LIFT for p in b2]
    b2_mid = [p is not None and xy(p, middle) < TOL and p[2] < LOW for p in b2]
    final_press = max([x for x in press if isinstance(x, (int, float))] or [0])
    max_stage = max([x for x in stage if isinstance(x, (int, float))] or [0])
    t_press = next((i for i, x in enumerate(press) if isinstance(x, (int, float)) and x >= 1), None)
    t_stage1 = next((i for i, x in enumerate(stage) if isinstance(x, (int, float)) and x >= 1), None)
    t_place1 = next((i for i, v in enumerate(on_empty) if v), None)
    info = {"targets": len(rows), "press_cnt": final_press, "max_stage": max_stage, "t_press": t_press,
            "t_block1_on_mat": t_place1, "t_stage1": t_stage1}
    if success:
        return "success", info
    if final_press >= 2:
        return ("pressed twice or more (after step 1 was complete)" if t_stage1 is not None
                else "pressed twice or more (step 1 never complete)"), info
    if max_stage < 1:
        if final_press == 1:
            return "pressed too early (block1 not on the empty mat at the press)", info
        t_b2 = next((i for i, v in enumerate(b2_lift) if v), None)
        if t_b2 is not None and (t_place1 is None or t_b2 < t_place1):
            return "moved block2 first (wrong block first)", info
        if t_place1 is not None:
            return "never pressed: block1 placed on the empty mat", info
        if any(b1_lift):
            return "never pressed: block1 lifted, never on the empty mat", info
        return "never moved a block", info
    after = range(t_stage1, len(snaps))
    if any(not on_empty[i] for i in after):
        info["t_block1_left"] = next(i for i in after if not on_empty[i])
        return "stage 1, then moved block1 again (which-block error)", info
    if not any(b2_lift[i] for i in after):
        return "stage 1, second step never started (block2 never lifted)", info
    if any(b2_mid[i] for i in after):
        return "stage 1, block2 in the middle, not finished (gripper / time)", info
    return "stage 1, block2 not placed in the middle", info


def main():
    items = sys.argv[1:] or DEFAULT
    out = {}
    for item in items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / TASK
        eps = sorted(d for d in root.glob("seed_*") if d.is_dir() and d.name[5:].isdigit())
        if not eps:
            print(f"{item}: no episodes")
            continue
        counts, seeds, per = Counter(), defaultdict(list), {}
        for d in eps:
            res, act = d / "result.json", d / "executed_actions.jsonl"
            if not res.exists() or not act.exists():
                counts["unfinished"] += 1
                continue
            rows = [json.loads(x) for x in act.read_text().splitlines() if x.strip()]
            if not rows:
                counts["no targets"] += 1
                continue
            c, info = classify(rows, bool(json.loads(res.read_text()).get("success")))
            counts[c] += 1
            seeds[c].append(int(d.name[5:]))
            per[d.name[5:]] = dict(info, cls=c)
        n = sum(counts.values())
        print(f"\n{item}: {n} episodes")
        for c, k in counts.most_common():
            print(f"  {k:3d}  {c}   e.g. seeds {seeds[c][:4]}")
        out[item] = {"counts": dict(counts), "episodes": per}
    (F / "REARR_SPLIT.json").write_text(json.dumps(out, indent=1) + "\n")
    print("\nREARR SPLIT REPORT: written outputs/fullft/REARR_SPLIT.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
