"""Stage-level (M1) and memory-decision analysis of memory_v2 closed-loop episodes.

RMBench's reward is 1 only at full success, so 0/40 says nothing about where episodes fail or whether memory
changes the decisive choice. From the per-target object snapshots the simulator adapter logs
(executed_actions.jsonl: objects_before/objects_after, press_cnt, stage_id) this script reconstructs the block
relocation events of every episode and scores the official stages (geometry as in RMBench envs/*.py):

put_back_block  mats left (0,-.1) right (.2,-.1) front (.1,-.2) back (.1,0); centre (.1,-.1)
  lifted (>=5 cm) -> centre (|dx|,|dy|<.04, resting) -> button pressed -> stage_id>=1 (pressed while centred)
  -> MEMORY DECISION: the mat the block is put on after the centre (correct = its original mat; chance 1/4)
swap_blocks     trays left (-.14) middle (0) right (.14), y -.15; one tray starts empty
  S1 a block into the empty tray -> S2 the OTHER block into the vacated tray -> S3 the first block into the
  other's original tray -> button pressed. MEMORY DECISION: after S1 the scene looks like a fresh start; moving
  the other block (correct) vs. the same block again (loop) needs the episode's history.

    /opt/mwam/bin/python scripts/memory_v2/closed_loop_stages.py [results folder ...]
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

SEED_DIR = re.compile(r"seed_\d+")
MATS = {"left": (0.0, -0.1), "right": (0.2, -0.1), "front": (0.1, -0.2), "back": (0.1, 0.0), "centre": (0.1, -0.1)}
TRAYS = {"left": -0.14, "middle": 0.0, "right": 0.14}


def put_back_location(x, y):
    for name, (mx, my) in MATS.items():
        if abs(x - mx) < 0.04 and abs(y - my) < 0.04:
            return name
    return "table"


def swap_location(x, y):
    for name, tx in TRAYS.items():
        if abs(x - tx) < 0.04 and abs(y + 0.15) < 0.06:
            return name
    return "table"


def read_rows(path: Path):
    """Initial snapshot + one snapshot after every executed target (only the fields we need)."""
    snaps, counters = [], []
    with path.open() as f:
        for i, line in enumerate(f):
            row = json.loads(line)
            if i == 0:
                snaps.append(row.get("objects_before") or {})
            after = row.get("objects_after") or {}
            snaps.append(after)
            counters.append({k: v for k, v in after.items() if not isinstance(v, dict)})
    return snaps, counters


def events(snaps, blocks, locate, rest_margin=0.012, min_move=0.05):
    """Per block: resting-position changes (from location -> to location), in time order, plus max lift."""
    out, lift = [], {}
    for b in blocks:
        if b not in snaps[0]:
            continue
        x0, y0, z0 = snaps[0][b]["p"][:3]
        last = (x0, y0)
        lift[b] = 0.0
        for t, s in enumerate(snaps):
            if b not in s:
                continue
            x, y, z = s[b]["p"][:3]
            lift[b] = max(lift[b], z - z0)
            if z < z0 + rest_margin and math.hypot(x - last[0], y - last[1]) > min_move:
                out.append({"t": t, "block": b, "from": locate(*last), "to": locate(x, y), "xy": (round(x, 3), round(y, 3))})
                last = (x, y)
    return sorted(out, key=lambda e: e["t"]), lift


def analyse_put_back(snaps, counters):
    ev, lift = events(snaps, ["block"], put_back_location)
    x0, y0 = snaps[0]["block"]["p"][:2]
    original = put_back_location(x0, y0)
    press = max([c.get("press_cnt", 0) or 0 for c in counters] + [0])
    stage = max([c.get("stage_id", 0) or 0 for c in counters] + [0])
    centre_t = next((e["t"] for e in ev if e["to"] == "centre"), None)
    after = [e for e in ev if centre_t is not None and e["t"] > centre_t]
    choice = after[-1]["to"] if after else None                     # where the block ends up after the centre
    r = {"original": original, "events": [f"{e['from']}->{e['to']}@{e['t']}" for e in ev],
         "lifted": lift["block"] >= 0.05, "centre": centre_t is not None, "pressed": press >= 1, "stage1": stage >= 1,
         "choice_after_centre": choice, "choice_correct": None if choice in (None, "table", "centre") else choice == original,
         "max_lift_m": round(lift["block"], 4)}
    r["furthest"] = ("success" if stage >= 2 else "stage1" if r["stage1"] else "pressed" if r["pressed"]
                     else "centre" if r["centre"] else "lifted" if r["lifted"] else "none")
    return r


def analyse_swap(snaps, counters):
    ev, lift = events(snaps, ["block1", "block2"], swap_location)
    start = {b: swap_location(*snaps[0][b]["p"][:2]) for b in ("block1", "block2")}
    empty = next(iter(set(TRAYS) - set(start.values())), None)
    press = max([c.get("press_cnt", 0) or 0 for c in counters] + [0])
    moves = [e for e in ev if e["to"] != "table"]
    s1 = next((e for e in moves if e["to"] == empty), None)
    s2 = s3 = None
    second = None
    if s1:
        first, other = s1["block"], ("block2" if s1["block"] == "block1" else "block1")
        later = [e for e in moves if e["t"] > s1["t"]]
        second = later[0] if later else None
        s2 = next((e for e in later if e["block"] == other and e["to"] == start[first]), None)
        if s2:
            s3 = next((e for e in moves if e["t"] > s2["t"] and e["block"] == first and e["to"] == start[other]), None)
    r = {"start": start, "empty": empty, "events": [f"{e['block']}:{e['from']}->{e['to']}@{e['t']}" for e in ev],
         "lifted": max(lift.values()) >= 0.05, "s1": s1 is not None, "s2": s2 is not None, "s3": s3 is not None,
         "pressed": press >= 1,
         "second_move": None if second is None else ("other block" if second["block"] != s1["block"] else "same block again"),
         "max_lift_m": round(max(lift.values()), 4)}
    r["choice_correct"] = None if second is None else second["block"] != s1["block"]
    r["furthest"] = ("s3" if r["s3"] else "s2" if r["s2"] else "s1" if r["s1"] else "lifted" if r["lifted"] else "none")
    return r


def trace_episode(path: Path, task: str, start: int, every: int = 24):
    """What the robot does from target `start` on: per `every` targets, block / end-effector / gripper / contacts."""
    blocks = ["block"] if task == "put_back_block" else ["block1", "block2"]
    out = []
    with path.open() as f:
        for i, line in enumerate(f):
            t = i + 1
            if t < start or (t - start) % every:
                continue
            row = json.loads(line)
            obj = row.get("objects_after") or {}
            joints = row.get("joint_details") or {}
            phys = row.get("physical_after") or [None] * 14
            contacts = ((row.get("object_contacts") or {}).get("objects") or {})
            cells = [f"t={t:<4}"]
            for b in blocks:
                if b not in obj:
                    continue
                bx, by, bz = obj[b]["p"][:3]
                loc = put_back_location(bx, by) if task == "put_back_block" else swap_location(bx, by)
                cells.append(f"{b}=({bx:+.3f},{by:+.3f},{bz:.3f}) {loc}")
                for side in ("left", "right"):
                    ee = (joints.get(side) or {}).get("ee_pose")
                    if ee:
                        d = math.dist(ee["p"][:3], (bx, by, bz))
                        cells.append(f"{side[0]}EE-{b[-1] if b != 'block' else 'b'}={d:.3f}")
            for name, c in contacts.items():
                sides = [s for s, v in (c.get("by_side") or {}).items() if v]
                if sides:
                    cells.append(f"touch[{name}]={'+'.join(sides)}")
            grip = [phys[6], phys[13]] if len(phys) >= 14 and phys[6] is not None else None
            if grip:
                cells.append(f"grip L={grip[0]:.2f} R={grip[1]:.2f}")
            cells.append(f"press={obj.get('press_cnt')} stage={obj.get('stage_id')}")
            out.append("  ".join(cells))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*", default=["/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/bank"])
    ap.add_argument("--quiet", action="store_true", help="no per-episode lines")
    ap.add_argument("--trace", default="", help="label/mode (e.g. v2_A_cf/on): timeline of episodes that reached "
                                                "the memory decision (put_back: block in the centre; swap: S1)")
    ap.add_argument("--trace-every", type=int, default=24)
    args = ap.parse_args()
    if args.trace:
        label, mode = args.trace.split("/")
        for folder in args.folders:
            for result in sorted(Path(folder).glob(f"{label}/{mode}/*/seed_*/result.json")):
                d = result.parent
                if not SEED_DIR.fullmatch(d.name):
                    continue
                res = json.loads(result.read_text())
                snaps, counters = read_rows(d / "executed_actions.jsonl")
                if res["task"] == "put_back_block":
                    r = analyse_put_back(snaps, counters)
                    if not r["centre"]:
                        continue
                    start = max(1, int(r["events"][0].split("@")[1]) - 24)
                else:
                    r = analyse_swap(snaps, counters)
                    if not r["s1"]:
                        continue
                    start = max(1, int(r["events"][0].split("@")[1]) - 24)
                print(f"\n== {args.trace} {res['task']} seed={res['seed']} furthest={r['furthest']} events={r['events']}")
                for line in trace_episode(d / "executed_actions.jsonl", res["task"], start, args.trace_every):
                    print("   " + line)
        return
    table = defaultdict(list)
    for folder in args.folders:
        for result in sorted(Path(folder).glob("*/*/*/seed_*/result.json")):
            d = result.parent
            if not SEED_DIR.fullmatch(d.name) or not (d / "executed_actions.jsonl").exists():
                continue
            res = json.loads(result.read_text())
            snaps, counters = read_rows(d / "executed_actions.jsonl")
            task = res["task"]
            r = analyse_put_back(snaps, counters) if task == "put_back_block" else analyse_swap(snaps, counters)
            r.update(seed=res["seed"], success=res["success"], cond=f"{res['label']}/{res['mode']}", task=task,
                     folder=Path(folder).name, targets=res["executed_targets"])
            table[(Path(folder).name, task, r["cond"])].append(r)
            if not args.quiet:
                extra = (f"orig={r['original']} choice={r['choice_after_centre']}" if task == "put_back_block"
                         else f"start={r['start']} empty={r['empty']} second={r['second_move']}")
                print(f"{Path(folder).name:<7}{r['cond']:<22}{task:<15} seed={r['seed']} furthest={r['furthest']:<8} "
                      f"lift={r['max_lift_m']:.3f} pressed={r['pressed']} {extra}  events={r['events'][:8]}")
    print("\n== stage reach per condition (fraction of episodes) and the memory decision")
    for (folder, task, cond), rs in sorted(table.items()):
        n = len(rs)
        frac = lambda k: sum(bool(r[k]) for r in rs) / n
        decided = [r["choice_correct"] for r in rs if r["choice_correct"] is not None]
        if task == "put_back_block":
            stages = f"lifted {frac('lifted'):.2f}  centre {frac('centre'):.2f}  pressed {frac('pressed'):.2f}  stage1 {frac('stage1'):.2f}"
            choices = Counter(r["choice_after_centre"] for r in rs if r["centre"])
            decision = f"return mat correct {sum(decided)}/{len(decided)} (chance 1/4)  choices after centre {dict(choices)}"
        else:
            stages = f"lifted {frac('lifted'):.2f}  S1 {frac('s1'):.2f}  S2 {frac('s2'):.2f}  S3 {frac('s3'):.2f}  pressed {frac('pressed'):.2f}"
            decision = f"second move = other block {sum(decided)}/{len(decided)}"
        print(f"  {folder:<7}{cond:<22}{task:<15} n={n:<3} success {frac('success'):.2f} | {stages} | {decision}")
        print(f"  {'':<7}{'':<22}{'':<15} furthest stage: {dict(Counter(r['furthest'] for r in rs))}")
    print("\n== paired on common scenes: episodes reaching each stage only under A / only under B")
    keys = {"put_back_block": ("lifted", "centre", "pressed", "stage1"), "swap_blocks": ("lifted", "s1", "s2", "s3", "pressed")}
    by = defaultdict(dict)
    for (folder, task, cond), rs in table.items():
        for r in rs:
            by[(folder, task, r["seed"])][cond] = r
    conds = sorted({c for (_, _, c) in table})
    for task, ks in keys.items():
        for i, a in enumerate(conds):
            for b in conds[i + 1:]:
                common = [v for (f, t, _), v in by.items() if t == task and a in v and b in v]
                if not common:
                    continue
                cells = "  ".join(f"{k}: {sum(v[a][k] and not v[b][k] for v in common)}/{sum(v[b][k] and not v[a][k] for v in common)}" for k in ks)
                print(f"  {task:<15} A={a:<22} B={b:<22} n={len(common):<3} {cells}")


if __name__ == "__main__":
    main()
