"""Z1 description (11-21 23:50 BJ, Opus; written after Z1_VERDICT = PRESS RE-DECISION < HALF, so DESCRIPTIVE ONLY:
no word, nothing here changes or adds to the registered reading in z1_verdict.py). Read-only.
Paired by scene (press scenes 1-100, first-button over-press o = e1 >= +1; paired bootstrap 95 % CI, 10,000, seed 0):
  Z1 vs Z1b, Z1b vs Z0 (the comparisons the registered attribution step did not read), and for every run against Z0:
  over rate, mean extra presses (e1 > 0), under rate (e1 <= -1), exact first count (e1 = 0), and e1's distribution.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/z1_describe.py
"""
from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("oracle_verdict", HERE / "oracle_verdict.py")
ov = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ov)


def stat(pairs, i, f):
    return sum(f(p[i]) for p in pairs) / len(pairs)


METRICS = (("over rate", lambda e: e >= 1), ("extra presses", lambda e: max(e, 0)),
           ("under rate", lambda e: e <= -1), ("exact", lambda e: e == 0))


def show(name, new, ref):
    seeds, pairs = ov.paired(new, ref)
    if not pairs:
        print(f"{name}: no pairs")
        return
    print(f"{name}: {len(pairs)} pairs")
    for m, f in METRICS:
        d = lambda ps: stat(ps, 0, f) - stat(ps, 1, f)                         # noqa: E731
        lo, hi = ov.boot_ci(pairs, d)
        print(f"    {m:14s} {stat(pairs, 1, f):.2f} -> {stat(pairs, 0, f):.2f}  D {d(pairs):+.2f}  95% CI [{lo:+.2f}, {hi:+.2f}]")


def main():
    z0 = ov.merged(("tim", "press_count_e30_oracle"))
    z1 = ov.merged(("tim", "press_count_e30_oracle_replan"))
    z1b = ov.merged(("tim", "press_count_e30_oracle_blind"))
    base = ov.merged(("g1", "press_count_e30"), ("sel", "press_count_e30"))
    show("Z1 (re-decide, press read) vs Z1b (re-decide, press hidden)", z1, z1b)
    show("Z1b vs Z0", z1b, z0)
    show("Z1 vs Z0", z1, z0)
    show("Z0 vs base", z0, base)
    for name, run in (("base", base), ("Z0", z0), ("Z1", z1), ("Z1b", z1b)):
        c = Counter(ov.e1(v) for v in run.values() if ov.e1(v) is not None)
        print(f"e1 distribution {name:4s} (n {sum(c.values())}): " + ", ".join(f"{k:+d}: {c[k]}" for k in sorted(c)))


if __name__ == "__main__":
    main()
