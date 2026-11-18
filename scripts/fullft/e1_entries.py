"""11-18 (Opus), read-only and descriptive: what the ledger recorded inside the injected frames of E1 (A40,
closed_loop/e1). E1 swap: in 26 % of the ledger model's pause / fidget episodes (visible arm) at least one ledger entry
falls in the injected frames (the registered structural criterion wanted >= 95 % with none). This lists those entries:
kind, arm (the injection's active arm or the other), the event frame and the confirmation frame relative to the first
injected frame, and the trigger. Hypothesis to check (not registered): the entry is the trigger event itself (the apex
of the rise after the second release), dated at the first still frame because the motion stops there.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e1_entries.py [--task swap_blocks]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")


def rows(path: Path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", default="swap_blocks")
    ap.add_argument("--folder", default=str(O / "e1"))
    ap.add_argument("--examples", type=int, default=8)
    args = ap.parse_args()
    for inj in ("pause", "fidget", "airgrasp"):
        base = Path(args.folder) / f"ar2_prop_e30_e1{inj}_vis" / "on" / args.task
        n_ep, n_with, kinds, offs, conf, examples = 0, 0, Counter(), Counter(), Counter(), []
        for d in sorted(base.glob("seed_*")):
            st = rows(d / "stress.jsonl")
            if not st or not (d / "result.json").exists():
                continue
            s = st[0]
            lo, hi = int(s["frame"]), int(s["frame"]) + int(s["k"]) - 1
            n_ep += 1
            seen = {}
            for x in rows(d / "decisions.jsonl"):
                for e in x.get("ledger") or []:
                    if lo <= int(e[0]) <= hi:
                        seen[(int(e[0]), int(e[1]), e[2])] = int(e[3]) if len(e) > 3 else None
            if not seen:
                continue
            n_with += 1
            for (f, arm, kind), c in sorted(seen.items()):
                same = "active arm" if arm == int(s.get("active_arm", -9)) else "other arm"
                kinds[(kind, same)] += 1
                offs[min(f - lo, 99) if f - lo < 8 else ("8-31" if f - lo < 32 else ">=32")] += 1
                if c is not None:
                    conf[(c - lo) if c - lo < 8 else ("8-31" if c - lo < 32 else ">=32")] += 1
            if len(examples) < args.examples:
                examples.append(f"  {d.name}: injection frames {lo}-{hi} (active arm {s.get('active_arm')}, open_frame "
                                f"{s.get('open_frame')}, shown {s.get('shown')}); entries in it "
                                f"{[(k[2], k[1], k[0] - lo, None if v is None else v - lo) for k, v in sorted(seen.items())]}")
        print(f"{args.task} {inj}: {n_with}/{n_ep} visible-arm episodes with a ledger entry in the injected frames")
        print(f"  entries by (kind, arm): {dict(kinds)}")
        print(f"  event frame - first injected frame: {dict(offs)}; confirmation frame - first injected frame: {dict(conf)}")
        print("\n".join(examples))


if __name__ == "__main__":
    main()
