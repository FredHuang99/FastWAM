"""Paired press_button comparison of two runs on the same scenes (11-16 night, Opus; read-only): success, first /
second count right, first-count error classes, paired first-count right only-in-A / only-in-B with a sign test; and,
for the two press counterfactuals, the reading registered here before any run (11-16 21:20 BJ).

Counterfactual readings (press_arprop e20, scenes 1-50, same noise as g1:press_arprop_e20: first count right 28,
under by one 1, over by one 16, over by >= 2 5; replicate 27 / 0 / 12 / 11). MWAM_LEDGER=addpress enters the first
completed press twice, droppress removes it (online.press_counterfactual):
  addpress   COUNTS ENTRIES      first count under by one >= 15/50 (one fake press -> it stops one press early)
             DOES NOT COUNT      first count under by one <= 5/50
             PARTIAL             otherwise
  droppress  COUNTS ENTRIES      first count right <= 12/50 and over by >= 2 >= 20/50 (one press hidden -> one more)
             DOES NOT COUNT      first count right >= 24/50
             PARTIAL             otherwise
  floor: >= 48 finished episodes in both runs, else NO READING. The second count (button 2) is reported: unchanged ->
  the model counts the presses since it moved to the button; shifted too -> it counts all presses.
Other pairs: descriptive only.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_pair.py abl:press_arprop_e20_addpress~g1:press_arprop_e20~addpress \
      latsel:press_arprop_e20_fast~sel:press_arprop_e20
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"
ALIGN = R / "outputs/fullft/align"


def stages(folder: str, label: str) -> dict:
    out = ALIGN / f"press_{folder}_{label}_stages.json"
    ALIGN.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(R / "scripts/memory_v2/migrate/export_stages.py"), "--label", label, "--mode",
                    "on", "--folders", str(O / "closed_loop" / folder), "--out", str(out)],
                   check=True, stdout=subprocess.DEVNULL, cwd=str(R))
    return json.loads(out.read_text())["episodes"].get("press_button", {})


def numbers(d: dict) -> dict:
    e1 = [v.get("n1_error") for v in d.values()]
    e2 = [v.get("n2_error") for v in d.values()]
    return {"n": len(d), "success": sum(bool(v.get("success")) for v in d.values()),
            "first_right": sum(x == 0 for x in e1), "first_under1": sum(x == -1 for x in e1),
            "first_under2plus": sum(isinstance(x, int) and x <= -2 for x in e1),
            "first_over1": sum(x == 1 for x in e1), "first_over2plus": sum(isinstance(x, int) and x >= 2 for x in e1),
            "second_right": sum(x == 0 for x in e2), "second_under1": sum(x == -1 for x in e2),
            "second_over1plus": sum(isinstance(x, int) and x >= 1 for x in e2)}


def sign_p(a: int, b: int) -> float:
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, k) for k in range(min(a, b) + 1)) / 2 ** n)


def reading(kind: str, a: dict, b: dict) -> str:
    if a["n"] < 48 or b["n"] < 48:
        return f"NO READING (finished {a['n']} / {b['n']} < 48)"
    if kind == "addpress":
        return "COUNTS ENTRIES" if a["first_under1"] >= 15 else "DOES NOT COUNT" if a["first_under1"] <= 5 else "PARTIAL"
    if kind == "droppress":
        if a["first_right"] <= 12 and a["first_over2plus"] >= 20:
            return "COUNTS ENTRIES"
        return "DOES NOT COUNT" if a["first_right"] >= 24 else "PARTIAL"
    return "descriptive"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pairs", nargs="+", help="NEWFOLDER:NEWLABEL~REFFOLDER:REFLABEL[~addpress|droppress]")
    args = ap.parse_args()
    report = {}
    for spec in args.pairs:
        parts = spec.split("~")
        (fa, la), (fb, lb) = parts[0].split(":", 1), parts[1].split(":", 1)
        kind = parts[2] if len(parts) > 2 else ""
        A, B = stages(fa, la), stages(fb, lb)
        a, b = numbers(A), numbers(B)
        common = sorted(set(A) & set(B))
        oa = sum(bool(A[s].get("n1_correct")) and not B[s].get("n1_correct") for s in common)
        ob = sum(bool(B[s].get("n1_correct")) and not A[s].get("n1_correct") for s in common)
        sa = sum(bool(A[s].get("success")) and not B[s].get("success") for s in common)
        sb = sum(bool(B[s].get("success")) and not A[s].get("success") for s in common)
        r = reading(kind, a, b)
        report[f"{fa}:{la}"] = {"reference": f"{fb}:{lb}", "new": a, "ref": b, "paired_n": len(common),
                                "paired_first": [oa, ob], "paired_success": [sa, sb], "reading": r}
        print(f"== {fa}:{la} vs {fb}:{lb} (paired {len(common)}): success {a['success']} vs {b['success']} "
              f"(only new {sa}, only ref {sb}, p {sign_p(sa, sb):.3f}); first right {a['first_right']} vs {b['first_right']} "
              f"(only new {oa}, only ref {ob}, p {sign_p(oa, ob):.3f})")
        print(f"   first: under >= 2 {a['first_under2plus']} vs {b['first_under2plus']}, under 1 {a['first_under1']} vs "
              f"{b['first_under1']}, over 1 {a['first_over1']} vs {b['first_over1']}, over >= 2 {a['first_over2plus']} vs "
              f"{b['first_over2plus']}; second right {a['second_right']} vs {b['second_right']}, under 1 "
              f"{a['second_under1']} vs {b['second_under1']}, over {a['second_over1plus']} vs {b['second_over1plus']}")
        print(f"   READING {fa}:{la}: {r}")
    out = R / "outputs/fullft/PRESS_PAIR.json"
    old = json.loads(out.read_text()) if out.exists() else {}
    old.update(report)
    out.write_text(json.dumps(old, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
