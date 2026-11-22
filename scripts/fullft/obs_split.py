"""Plan v19 3.3 step 1 (A3 摸底, 11-22, Opus; redone 12:50 after reading RMBench envs/observe_and_pickup.py): split
observe_and_pickup failures, from episodes run with the object record on (MWAM_OBJECT_LOG=1: sim_adapter.py writes
OBJECTS_META.json and, per executed target, objects_after['_actors'] / ['_flags']). Read-only, CPU. Descriptive only.
The task (envs/observe_and_pickup.py): five candidates on the table (object[0..4], start z 0.741); the reference, a copy
of object[target_object_idx], stands on the shelf until a wall hides it after 20 physics steps; an arm moving > 3 cm
before that sets fail_flag (the episode can no longer succeed); success = object[target_object_idx] above z 0.8.
Per episode, in this order:
  success                                   result.json success
  moved before the wall                     _flags.fail_flag became true
  lifted another object (picked wrong)      some object[i], i != target, rose >= --lift (default 3 cm) above its start
  lifted the correct object, then failed    object[target] rose >= --lift (not above 0.8 long enough, or dropped)
  lifted nothing                            no candidate rose >= --lift
(an episode that lifted the target AND another one counts as picked wrong; both lifts are listed). Per run: the counts,
the wrong picks' categories (same model name as the target = same category, other instance; else another category).
  /opt/mwam/bin/python scripts/fullft/obs_split.py FOLDER:LABEL [...] [--lift 0.03]
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")


def rows(path: Path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def episode(d: Path, lift_min: float) -> dict:
    meta = json.loads((d / "OBJECTS_META.json").read_text())
    target = (meta.get("scalars") or {}).get("target_object_idx")
    names = (meta.get("lists") or {}).get("object_modelnames") or []
    start, rise, fail = {}, {}, False
    for r in rows(d / "executed_actions.jsonl"):
        oa = r.get("objects_after") or {}
        fail = fail or bool((oa.get("_flags") or {}).get("fail_flag"))
        for name, p in (oa.get("_actors") or {}).items():
            m = re.fullmatch(r"object\[(\d+)\]", name)
            if not m or not p:
                continue
            i = int(m.group(1))
            start.setdefault(i, float(p[2]))
            rise[i] = max(rise.get(i, 0.0), float(p[2]) - start[i])
    lifted = sorted(i for i, v in rise.items() if v >= lift_min)
    ok = bool(json.loads((d / "result.json").read_text()).get("success")) if (d / "result.json").exists() else False
    wrong = [i for i in lifted if target is not None and i != int(target)]
    if ok:
        cls = "success"
    elif fail:
        cls = "moved before the wall"
    elif wrong:
        cls = "lifted another object (picked wrong)"
    elif target is not None and int(target) in lifted:
        cls = "lifted the correct object, then failed"
    elif target is None and lifted:
        cls = "lifted something (target index unknown)"
    else:
        cls = "lifted nothing"
    same = [i for i in wrong if names and target is not None and names[i] == names[int(target)]]
    return {"seed": d.name, "class": cls, "target": target, "lifted": lifted, "wrong_same_category": same,
            "names": names, "rise_cm": {i: round(100 * v, 1) for i, v in sorted(rise.items())}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="FOLDER:LABEL under closed_loop")
    ap.add_argument("--lift", type=float, default=0.03)
    args = ap.parse_args()
    for item in args.runs:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / "observe_and_pickup"
        eps = sorted(d for d in root.glob("seed_*") if (d / "OBJECTS_META.json").exists())
        print(f"== {item}: {len(eps)} episodes with the object record")
        out = [episode(d, args.lift) for d in eps]
        print("  classes:", dict(Counter(r["class"] for r in out)))
        wrong = [r for r in out if r["class"].startswith("lifted another")]
        if wrong:
            print(f"  wrong picks: same category as the target {sum(bool(r['wrong_same_category']) for r in wrong)}"
                  f" / {len(wrong)}")
        for r in out[:20]:
            print("   ", json.dumps(r)[:320])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
