"""Plan v19 3.3 step 1 (A3 摸底, 11-22, Opus): split observe_and_pickup failures into "picked the wrong object" and
"picked nothing", from episodes run with the object record on (MWAM_OBJECT_LOG=1: sim_adapter.py writes
OBJECTS_META.json and objects_after['_actors'] per executed target). Read-only, CPU. Descriptive: no reading word.
Per episode: every scene entity's largest lift above its start height over the episode; lifted = >= --lift (default
3 cm). The correct object = the environment's actor attribute named by --target (default: the one attribute whose name
contains 'target', if exactly one); unknown -> the episode is only split into "lifted something" / "lifted nothing".
Classes: success; lifted the correct object (then failed); lifted another object (picked wrong); lifted nothing.
Also prints the first episode's OBJECTS_META.json (scalars and actor attributes) so the attribute naming the correct
object can be chosen.
  /opt/mwam/bin/python scripts/fullft/obs_split.py FOLDER:LABEL [...] [--target ATTR] [--lift 0.03]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
SKIP = ("ground", "table", "wall", "camera", "light")


def rows(path: Path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def episode(d: Path, target_attr: str, lift_min: float):
    meta = json.loads((d / "OBJECTS_META.json").read_text())
    start = meta.get("entities_at_start") or {}
    lift = {}
    for r in rows(d / "executed_actions.jsonl"):
        for name, p in ((r.get("objects_after") or {}).get("_actors") or {}).items():
            if name in start and p:
                lift[name] = max(lift.get(name, 0.0), float(p[2]) - float(start[name][2]))
    lifted = sorted(n for n, v in lift.items() if v >= lift_min and not any(s in n.lower() for s in SKIP))
    actors = meta.get("actors") or {}
    cands = [k for k in actors if "target" in k.lower()]
    attr = target_attr or (cands[0] if len(cands) == 1 else "")
    target = actors.get(attr, {}).get("entity") if isinstance(actors.get(attr), dict) else None
    result = json.loads((d / "result.json").read_text()) if (d / "result.json").exists() else {}
    ok = bool(result.get("success"))
    if ok:
        cls = "success"
    elif not lifted:
        cls = "lifted nothing"
    elif target is None:
        cls = "lifted something (correct object unknown)"
    elif any(n == target or n.startswith(target + "#") for n in lifted):
        cls = "lifted the correct object, failed later"
    else:
        cls = "lifted another object (picked wrong)"
    return {"seed": d.name, "class": cls, "lifted": lifted, "target_attr": attr, "target": target,
            "max_lift": {k: round(v, 3) for k, v in sorted(lift.items(), key=lambda x: -x[1])[:5]}}, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="FOLDER:LABEL under closed_loop")
    ap.add_argument("--target", default="")
    ap.add_argument("--lift", type=float, default=0.03)
    args = ap.parse_args()
    shown = False
    for item in args.runs:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / "observe_and_pickup"
        eps = sorted(d for d in root.glob("seed_*") if (d / "OBJECTS_META.json").exists())
        print(f"== {item}: {len(eps)} episodes with the object record")
        out = []
        for d in eps:
            row, meta = episode(d, args.target, args.lift)
            out.append(row)
            if not shown:
                print("first episode OBJECTS_META.json: scalars", json.dumps(meta.get("scalars"))[:1500])
                print("  actor attributes", json.dumps(meta.get("actors"))[:1500])
                shown = True
        print("  classes:", dict(Counter(r["class"] for r in out)))
        for r in out[:12]:
            print("   ", json.dumps(r)[:300])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
