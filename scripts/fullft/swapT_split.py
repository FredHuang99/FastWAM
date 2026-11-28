"""Card 11 (plan v20 3.3): why swap_T fails -- measurements per episode, then classes. Read-only, CPU, descriptive.
The task (RMBench envs/swap_T.py, read 11-24): two T blocks at x -0.09 / +0.09, y in [-0.15, -0.10], random yaw up to
0.75 rad; success = T_block1 within 2.5 cm (xy) of T_block2's start AND within 15 degrees of T_block2's start
orientation, and the same for T_block2 at T_block1's start; both grippers open; both blocks down (z < 0.77). Where to
put each block (and how to turn it) is the OTHER block's start pose: only frame 0 shows it once both are lifted.
Logs (5090 closed loop with MWAM_OBJECT_LOG=1, sim_adapter.py): per executed target objects_after['_actors'] (positions)
and ['_quat'] (orientations, 11-24) of T_block1 / T_block2, ee_after (both end-effectors), physical_after (grippers).
Per episode and block: lifted (> 3 cm above its start), by which arm (the nearer end-effector when first lifted),
final position error and angle error against its target, distance to its OWN start (put back instead of swapped),
final height, both grippers open at the end; the frames of the first lift and of the final put-down.
Classes (plan v20 card 11): fixed by Opus after reading the first 10 episodes' measurements of each model and BEFORE
any full result is read; until CLASSES is filled in, --first 10 prints measurements only and the full run refuses.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/swapT_split.py --first 10 FOLDER:LABEL ...   (measurements only)
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/swapT_split.py FOLDER:LABEL ...              (after CLASSES is set)
Writes outputs/fullft/SWAPT_SPLIT.json.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
TASK = "swap_T"
BLOCKS = ("T_block1", "T_block2")
LIFT, DOWN, POS_TOL, ANG_TOL = 0.03, 0.77, 0.025, 15.0
HOME, FAR, RELEASED = 0.03, 0.05, 0.6


def classify(m):
    """Fixed 11-24 20:45 (Opus) from the first 10 episodes of each model (SWAPT_SPLIT_FIRST.json, CARD11_5090 11:19 UTC),
    BEFORE any of scenes 11-50 was read. What those 20 showed: both blocks are lifted together (left T1, right T2, target
    ~72); T1 goes down first (~173), T2 second (~280) in every success. 7 / 10 failures: T2 back within 1.2 cm of its OWN
    start, put down late (517-589), the right gripper still half closed (0.41), and T1 off the table (z 0.83-0.96,
    6-40 cm from its start); 2: both placed within 2.5 cm but one angle 24.5 / 43.9 deg; 1: both within tolerance, both
    grippers at 0.41-0.42. The logged gripper value is not the env's: successes end with the right one at 0.68-0.71.
    Rules in this order (first match). Families for plan v20 2.1 / cards 9, 9b (set now, before the full results):
      WHERE  = the block went to the wrong place (the other block's start, seen only in frame 0, not used): card 9 family
      POSE   = right place, position or angle off: card 9 family
      HANDLE = lifting / releasing / a block left off the table: card 9b family"""
    if m.get("success"):
        return "success"
    b = {k: m[k] for k in BLOCKS}
    if not all(v["lifted"] for v in b.values()):
        return "HANDLE: a block never lifted"
    for k, o in (("T_block1", "T_block2"), ("T_block2", "T_block1")):
        if b[k]["to_own_start_cm"] < 100 * HOME and b[k]["down"]:
            return ("WHERE: a block put back at its own start, the other off the table" if not b[o]["down"]
                    else "WHERE: a block put back at its own start, both on the table")
    if not all(v["down"] for v in b.values()):
        return "HANDLE: a block not on the table at the end (held / dropped on something)"
    if any(v["pos_err_cm"] > 100 * FAR for v in b.values()):
        return "WHERE: a block put down elsewhere (> 5 cm from its target)"
    if any(v["pos_err_cm"] >= 100 * POS_TOL for v in b.values()):
        return "POSE: both near the targets, a position 2.5-5 cm off"
    if any(not v["ang_ok"] for v in b.values()):
        return "POSE: both within 2.5 cm, an angle >= 15 deg off"
    g = m.get("grippers_open_end") or [0, 0]
    if min(g) < RELEASED:
        return "HANDLE: both placed within tolerance, a gripper not opened"
    return "other"


CLASSES = classify      # fixed 11-24 20:45 after the first 10 episodes per model (plan v20 card 11); see Status 11-24


def angle_deg(q, r):
    n1, n2 = math.sqrt(sum(x * x for x in q)) or 1.0, math.sqrt(sum(x * x for x in r)) or 1.0
    dot = abs(sum(a * b for a, b in zip(q, r))) / (n1 * n2)
    return math.degrees(2.0 * math.acos(min(1.0, dot)))


def rows(p: Path):
    out = []
    for x in p.read_text().splitlines() if p.exists() else []:
        if x.strip():
            try:
                out.append(json.loads(x))
            except json.JSONDecodeError:
                pass
    return out


def measure(d: Path):
    acts = rows(d / "executed_actions.jsonl")
    res = d / "result.json"
    if not acts or not res.exists():
        return None
    ok = bool(json.loads(res.read_text()).get("success"))
    pos = [(r.get("objects_after") or {}).get("_actors") or {} for r in acts]
    quat = [(r.get("objects_after") or {}).get("_quat") or {} for r in acts]
    if not all(b in pos[0] for b in BLOCKS):
        return {"success": ok, "why": "no T-block positions (MWAM_OBJECT_LOG off?)"}
    start = {b: pos[0][b] for b in BLOCKS}
    q0 = {b: quat[0].get(b) for b in BLOCKS}
    other = {"T_block1": "T_block2", "T_block2": "T_block1"}
    m = {"success": ok, "targets": len(acts)}
    for b in BLOCKS:
        zs = [p[b][2] for p in pos if b in p]
        lifted_at = next((i for i, p in enumerate(pos) if b in p and p[b][2] > start[b][2] + LIFT), None)
        by = None
        if lifted_at is not None:
            ee = acts[lifted_at].get("ee_after") or {}
            dist = {s: math.dist(ee[s][:3], pos[lifted_at][b]) for s in ("left", "right") if ee.get(s)}
            by = min(dist, key=dist.get) if dist else None
        down_at = None
        if lifted_at is not None:
            for i in range(lifted_at, len(pos)):
                if b in pos[i] and pos[i][b][2] < DOWN and (down_at is None or pos[i - 1][b][2] >= DOWN):
                    down_at = i
        fin, tgt = pos[-1][b], start[other[b]]
        pe = math.dist(fin[:2], tgt[:2])
        ae = angle_deg(quat[-1][b], q0[other[b]]) if quat[-1].get(b) and q0.get(other[b]) else None
        m[b] = {"lifted": lifted_at is not None, "lifted_at": lifted_at, "lifted_by": by,
                "max_lift_cm": round(100 * (max(zs) - start[b][2]), 1), "down_at": down_at,
                "final_z": round(fin[2], 3), "pos_err_cm": round(100 * pe, 1),
                "ang_err_deg": round(ae, 1) if ae is not None else None,
                "to_own_start_cm": round(100 * math.dist(fin[:2], start[b][:2]), 1),
                "pos_ok": pe < POS_TOL, "ang_ok": ae is not None and ae < ANG_TOL, "down": fin[2] < DOWN}
    g = acts[-1].get("physical_after") or []
    m["grippers_open_end"] = [round(g[6], 2), round(g[13], 2)] if len(g) >= 14 else None
    m["start_yaw_diff_deg"] = (round(angle_deg(q0["T_block1"], q0["T_block2"]), 1)
                               if q0.get("T_block1") and q0.get("T_block2") else None)
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="+")
    ap.add_argument("--first", type=int, default=0, help="measurements of the first N episodes (bank order) only")
    ap.add_argument("--out", default="", help="output file name in outputs/fullft (11-28, plan v22: card 9b / 36 / 36b "
                    "splits; default unchanged: SWAPT_SPLIT[_FIRST].json)")
    args = ap.parse_args()
    if not args.first and CLASSES is None:
        print("SWAPT SPLIT: the classes are not fixed yet (read --first 10 first, then fix CLASSES): nothing read")
        return 2
    out = {}
    for item in args.items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / TASK
        eps = sorted((d for d in root.glob("seed_*") if d.is_dir()), key=lambda d: int(d.name[5:]))
        # the seed-42 bank = the first feasible seeds from 42 upwards, so seed order = bank order
        per = {}
        for d in eps:
            m = measure(d)
            if m is None:
                continue
            per[d.name[5:]] = m
            if args.first and len(per) >= args.first:
                break
        print(f"\n== {item}: {len(per)} episodes{' (first ' + str(args.first) + ')' if args.first else ''}")
        for s, m in per.items():
            if "why" in m:
                print(f"  seed {s}: {m['why']}")
                continue
            b1, b2 = m["T_block1"], m["T_block2"]
            print(f"  seed {s}: success {int(m['success'])}; targets {m['targets']}; grippers {m['grippers_open_end']}; "
                  f"start yaw diff {m['start_yaw_diff_deg']}")
            for b, v in (("T1", b1), ("T2", b2)):
                print(f"     {b}: lifted {v['lifted']} at {v['lifted_at']} by {v['lifted_by']} (max {v['max_lift_cm']} cm), "
                      f"down at {v['down_at']} z {v['final_z']}; to target {v['pos_err_cm']} cm / {v['ang_err_deg']} deg; "
                      f"to own start {v['to_own_start_cm']} cm")
        if not args.first:
            counts, seeds = Counter(), defaultdict(list)
            for s, m in per.items():
                c = CLASSES(m) if callable(CLASSES) else "unclassified"
                counts[c] += 1
                seeds[c].append(s)
                m["cls"] = c
            for c, k in counts.most_common():
                print(f"  {k:3d}  {c}   e.g. seeds {seeds[c][:4]}")
        out[item] = per
    name = args.out or ("SWAPT_SPLIT_FIRST.json" if args.first else "SWAPT_SPLIT.json")
    (F / name).write_text(json.dumps(out, indent=1) + "\n")
    print(f"\nSWAPT SPLIT: written outputs/fullft/{name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
