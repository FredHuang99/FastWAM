"""Press checkpoint selection, node P-SEL (11-16; registered before any press model ran on scenes 51-100).

Rule: for one press run (press_arprop, press_ar, later press_arev), among its exports e10 / e20 / e30 evaluated on
press_button scenes 1-50 (5090, fixed pipeline, closed_loop/g1, label <run>_<tag>), choose the one with the most
successes; ties -> more episodes with the first count right; ties -> the later epoch. The chosen export is then run on
scenes 51-100 (closed_loop/sel), which no press model has seen. Descriptive (not a verdict): success on 51-100 per
run and the paired comparison of two runs there. The registered S-C verdict (e30, scenes 1-50) is unchanged.
Prints one line "SELECTED <run> <tag> (success s/50, first right f/50)" or "NOT READY <reason>" (exit code 2), so a
shell script can read the tag:  tag=$(... press_select.py --run press_ar | awk '/^SELECTED/ {print $3}')
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_select.py --run press_arprop [--tags e10 e20 e30] [--n 50]
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_select.py --pair press_arprop_e20 press_ar_e10
      (paired table of two labels in closed_loop/sel: success, only-A / only-B, sign p)
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
TASK = "press_button"


def results(folder: str, label: str) -> dict:
    out = {}
    for d in sorted((O / "closed_loop" / folder / label / "on" / TASK).glob("seed_*")):
        r = d / "result.json"
        if d.name.split("_", 1)[1].isdigit() and r.exists():
            out[d.name.split("_", 1)[1]] = bool(json.loads(r.read_text()).get("success"))
    return out


def first_right(folder: str, label: str) -> int:
    out = R / "outputs/fullft/align" / f"press_{label}_stages.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(R / "scripts/memory_v2/migrate/export_stages.py"), "--label", label,
                    "--mode", "on", "--folders", str(O / "closed_loop" / folder), "--out", str(out)],
                   check=True, stdout=subprocess.DEVNULL, cwd=str(R))
    eps = json.loads(out.read_text())["episodes"].get(TASK, {})
    return sum(bool(e.get("n1_correct")) for e in eps.values())


def sign_p(a, b):
    n, k = a + b, min(a, b)
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run")
    ap.add_argument("--tags", nargs="+", default=["e10", "e20", "e30"])
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--folder", default="g1")
    ap.add_argument("--pair", nargs=2)
    args = ap.parse_args()
    if args.pair:
        a, b = (results("sel", x) for x in args.pair)
        common = sorted(set(a) & set(b))
        oa = sum(a[s] and not b[s] for s in common)
        ob = sum(b[s] and not a[s] for s in common)
        print(f"P-SEL scenes 51-100 (closed_loop/sel), paired n={len(common)}: {args.pair[0]} {sum(a[s] for s in common)}"
              f" vs {args.pair[1]} {sum(b[s] for s in common)}; only first {oa}, only second {ob}, sign p {sign_p(oa, ob):.4f}")
        return 0
    if not args.run:
        ap.error("--run or --pair")
    rows = []
    for i, tag in enumerate(args.tags):
        label = f"{args.run}_{tag}"
        res = results(args.folder, label)
        if len(res) < args.n:
            print(f"NOT READY {label}: {len(res)} of {args.n} episodes on scenes 1-{args.n}")
            return 2
        rows.append((sum(res.values()), first_right(args.folder, label), i, tag))
    for s, f, _, tag in rows:
        print(f"  {args.run}_{tag}: success {s}/{args.n}, first count right {f}/{args.n}")
    s, f, _, tag = max(rows)
    print(f"SELECTED {args.run} {tag} (success {s}/{args.n}, first right {f}/{args.n})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
