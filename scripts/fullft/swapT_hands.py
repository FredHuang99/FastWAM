"""Plan v20 supplement 6 (11-25, Opus): swap_T demos -- which hand grasps and which hand releases what. Read-only, CPU.
Input: the events file the swap_T models trained on (events_swap_T.json: relay diag/events_b1; fetched if missing).
Per demo: the body events in time order (arm, kind, frame); per arm the number of closes / opens; the order in which
the two arms close and open. Card 9's second condition (plan v20): the block a hand picks up and the place where the
OTHER block must go are handled by the same hand? In swap_T block 1's target is block 2's start and vice versa; if each
arm closes once and opens once, each arm carries one block from its own start to the other's, so the hand that grasped
block 1 (and whose joint reading at that close marks block 1's start) is NOT the hand that puts block 2 there.
Prints SWAPT HANDS lines; JSON -> outputs/fullft/SWAPT_HANDS.json
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/swapT_hands.py [--events FILE]
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
EV = R / "outputs/fullft/relay_in/events_b1/events_swap_T.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default=str(EV))
    args = ap.parse_args()
    ev = Path(args.events)
    if not ev.exists():
        ev.parent.mkdir(parents=True, exist_ok=True)
        hf = "/opt/hf-tools/bin/python"
        subprocess.run([hf, str(R / "scripts/memory_v2/migrate/relay.py"), "get", "--prefix", "diag/events_b1",
                        "--out", str(ev.parent)], check=False)
    value = json.loads(ev.read_text())
    eps = value["episodes"] if "episodes" in value else value
    pattern, per_arm, rows = Counter(), Counter(), {}
    for eid, es in sorted(eps.items()):
        es = sorted(es, key=lambda e: (int(e["frame"]), int(e["arm"])))
        seq = [(("L" if int(e["arm"]) == 0 else "R"), e["kind"]) for e in es if e["kind"] in ("close", "open")]
        c = Counter((a, k) for a, k in seq)
        per_arm[(c[("L", "close")], c[("L", "open")], c[("R", "close")], c[("R", "open")])] += 1
        pattern[" ".join(f"{a}{k[0]}" for a, k in seq)] += 1
        rows[eid] = {"seq": seq, "frames": [int(e["frame"]) for e in es if e["kind"] in ("close", "open")]}
    print(f"[hands] {len(rows)} demos; (left closes, left opens, right closes, right opens): {dict(per_arm)}")
    for p, n in pattern.most_common(8):
        print(f"[hands]   {n:3d}  {p}   (Lc = left close, Ro = right open, ...)")
    one_each = per_arm.get((1, 1, 1, 1), 0)
    print(f"SWAPT HANDS: {one_each} / {len(rows)} demos have exactly one close and one open per arm (each hand carries "
          f"one block; the hand that grasps a block is not the one that puts the other block on its start)")
    (R / "outputs/fullft/SWAPT_HANDS.json").write_text(json.dumps({"per_arm": {str(k): v for k, v in per_arm.items()},
                                                                   "patterns": dict(pattern), "episodes": rows}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
