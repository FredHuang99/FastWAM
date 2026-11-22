"""Where does the gripper close in observe_and_pickup? (11-22 23:15, Opus; follow-up of obs_split.py on the 5090 a3diag
episodes: 29 / 50 of obs_arprop \"lifted nothing\", and the objects it did lift were the target 3 times in 21.) Read-only,
CPU, zero GPU: the episodes already recorded with MWAM_OBJECT_LOG=1. Descriptive.
Per executed target: the commanded grippers (target[6] left, target[13] right; our event rule's gripper part, events.py
EventRule defaults: closed below 0.35, open above 0.65), the end-effector positions (ee_after, robot.get_*_ee_pose) and
the five candidates' positions (objects_after['_actors'] object[i]).
Per gripper CLOSE: the arm, and the nearest candidate in x-y (index, distance in cm, target or not, same category).
Per episode, in this order:
  never closed                                no close at all
  closed near the target                      some close within --near (default 5 cm, x-y) of the target
  closed near another object only             closes near candidates, never near the target
  closed in the air only                      every close farther than --near from every candidate
Calibration line first: the x-y distance to the target at the close that preceded a success (should be small; if not,
the end-effector and object frames differ and the rest is not readable).
Also: the first close's nearest candidate is the target in how many episodes (chance with 5 candidates ~ 20 %).
  /opt/mwam/bin/python scripts/fullft/obs_grasp.py a3diag:obs_ar_e30 a3diag:obs_arprop_e30 [--near 0.05]
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
LOW, HIGH = 0.35, 0.65


def rows(path: Path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def xy(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def episode(d: Path, near: float) -> dict:
    meta = json.loads((d / "OBJECTS_META.json").read_text())
    target = (meta.get("scalars") or {}).get("target_object_idx")
    target = None if target is None else int(target)
    names = (meta.get("lists") or {}).get("object_modelnames") or []
    ok = bool(json.loads((d / "result.json").read_text()).get("success")) if (d / "result.json").exists() else False
    state = {6: None, 13: None}
    closes = []
    for r in rows(d / "executed_actions.jsonl"):
        tgt = r.get("target") or []
        ee = r.get("ee_after") or {}
        objs = {int(m.group(1)): p for k, p in ((r.get("objects_after") or {}).get("_actors") or {}).items()
                if (m := re.fullmatch(r"object\[(\d+)\]", k)) and p}
        for col, side in ((6, "left"), (13, "right")):
            if len(tgt) <= col:
                continue
            g = float(tgt[col])
            s = state[col]
            if s is None:
                state[col] = g >= 0.5
                continue
            if s and g < LOW:
                state[col] = False
                p = ee.get(side)
                if p and objs:
                    dist = {i: xy(p, q) for i, q in objs.items()}
                    i = min(dist, key=dist.get)
                    closes.append({"t": r.get("completed_target_id"), "arm": side, "nearest": i,
                                   "cm": round(100 * dist[i], 1), "target_cm": None if target not in dist
                                   else round(100 * dist[target], 1), "is_target": i == target,
                                   "same_category": bool(names) and target is not None and i != target
                                   and names[i] == names[target]})
            elif not s and g > HIGH:
                state[col] = True
    if not closes:
        cls = "never closed"
    elif any(c["target_cm"] is not None and c["target_cm"] <= 100 * near for c in closes):
        cls = "closed near the target"
    elif any(c["cm"] <= 100 * near for c in closes):
        cls = "closed near another object only"
    else:
        cls = "closed in the air only"
    return {"seed": d.name, "success": ok, "target": target, "class": cls, "closes": closes}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="FOLDER:LABEL under closed_loop")
    ap.add_argument("--near", type=float, default=0.05)
    args = ap.parse_args()
    for item in args.runs:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / "observe_and_pickup"
        eps = [episode(d, args.near) for d in sorted(root.glob("seed_*")) if (d / "OBJECTS_META.json").exists()]
        print(f"== {item}: {len(eps)} episodes")
        cal = [e["closes"][-1]["target_cm"] for e in eps if e["success"] and e["closes"]
               and e["closes"][-1]["target_cm"] is not None]
        print(f"  calibration: x-y distance to the target at the last close of the {len(cal)} successes (cm): {cal}")
        print("  classes (all episodes):", dict(Counter(e["class"] for e in eps)))
        print("  classes (failed episodes):", dict(Counter(e["class"] for e in eps if not e["success"])))
        first = [e["closes"][0] for e in eps if e["closes"]]
        if first:
            print(f"  first close: nearest candidate is the target in {sum(c['is_target'] for c in first)} / {len(first)}"
                  f" (same category, other instance: {sum(c['same_category'] for c in first)}); distance to the"
                  f" nearest candidate median {statistics.median(c['cm'] for c in first):.1f} cm")
            print(f"  closes per episode: {dict(sorted(Counter(len(e['closes']) for e in eps).items()))}")
            print(f"  arms at the first close: {dict(Counter(c['arm'] for c in first))}")
        for e in eps:
            print("   ", json.dumps({k: e[k] for k in ("seed", "success", "target", "class")})[:120],
                  json.dumps(e["closes"][:3])[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
