"""Press error breakdown (11-15, read-only): per label, how the counts go wrong on press_button.
For each LABEL (closed_loop/<folder>/<label>/on/press_button) the stage export is made (export_stages.py, the same
parser as the loop_peek numbers) into outputs/fullft/align/press_<label>_stages.json, then printed:
  success, first / second count right, both right, confirmed; error of each count (pressed - shown) as a histogram;
  first-count error by the number shown; total presses; and, for every pair of labels, the paired first-count
  outcome on common scenes (right in A only / B only).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_errors.py --folder closed_loop/g1 press_arprop_e20 press_arprop_e30
"""
from __future__ import annotations

import argparse
import collections
import json
import subprocess
import sys
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"


def hist(values):
    c = collections.Counter(values)
    return " ".join(f"{k:+d}:{c[k]}" if isinstance(k, int) else f"{k}:{c[k]}" for k in
                    sorted(c, key=lambda x: (not isinstance(x, int), x if isinstance(x, int) else 0)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default="closed_loop/g1")
    ap.add_argument("labels", nargs="+")
    args = ap.parse_args()
    eps = {}
    for label in args.labels:
        out = R / "outputs/fullft/align" / f"press_{label}_stages.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, str(R / "scripts/memory_v2/migrate/export_stages.py"), "--label", label,
                        "--mode", "on", "--folders", str(O / args.folder), "--out", str(out)],
                       check=True, stdout=subprocess.DEVNULL, cwd=str(R))
        d = json.loads(out.read_text())["episodes"].get("press_button", {})
        eps[label] = d
        n = len(d)
        f = lambda k: sum(bool(e.get(k)) for e in d.values())              # noqa: E731
        print(f"== {label}: n={n} success {f('success')} first right {f('n1_correct')} second right {f('n2_correct')} "
              f"both {f('count_correct')} confirmed {f('confirmed')}")
        print(f"   first-count error  {hist([e.get('n1_error') for e in d.values()])}")
        print(f"   second-count error {hist([e.get('n2_error') for e in d.values()])}")
        by = collections.defaultdict(list)
        for e in d.values():
            if isinstance(e.get("n1_error"), int):
                by[e.get("card_1")].append(e["n1_error"])
        print("   first-count error by number shown  " + "  ".join(
            f"{k}: {sum(x == 0 for x in v)}/{len(v)} right, mean {sum(v) / len(v):+.1f}" for k, v in sorted(by.items())))
        print(f"   presses per episode {hist([e.get('presses') for e in d.values()])}")
    labels = list(eps)
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            common = sorted(set(eps[a]) & set(eps[b]))
            oa = sum(bool(eps[a][s].get("n1_correct")) and not eps[b][s].get("n1_correct") for s in common)
            ob = sum(bool(eps[b][s].get("n1_correct")) and not eps[a][s].get("n1_correct") for s in common)
            print(f"-- first count right, {a} only {oa} vs {b} only {ob} (common scenes {len(common)})")


if __name__ == "__main__":
    main()
