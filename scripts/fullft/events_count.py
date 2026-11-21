"""Body events per demonstration, per task (11-22, Opus; plan v19 B5: before the ranking body-record run, count the
events of every demo of the nine tasks and see whether any has more than the record's 32 entries; plan v19 fact
check 3: does the rearrange demo's button press appear in the record). Read-only, CPU.
For each events_<...>.json found (files or folders given; a task's file seen twice is read once, by name):
  demos, events per demo (min / median / p90 / max), demos with > 32 events (the record keeps the last 32), events by
  kind, demos with at least one 'bottom' (a press turning point), and the largest per-(arm, kind) count in one demo
  (the countable code saturates at 16).
  /opt/mwam/bin/python scripts/fullft/events_count.py DIR_OR_FILE ...   (prints; writes nothing)
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path


def files(args):
    seen = {}
    for a in args:
        p = Path(a)
        for f in ([p] if p.is_file() else sorted(p.rglob("events_*.json")) if p.is_dir() else []):
            seen.setdefault(f.name, f)
    return seen


def main():
    found = files(sys.argv[1:])
    if not found:
        print("no events_*.json found")
        return 1
    print(f"{'file':42s} demos  min  med  p90  max  >32  with-bottom  max-per-arm-kind  kinds")
    for name, f in sorted(found.items()):
        value = json.loads(f.read_text())
        eps = value["episodes"] if isinstance(value, dict) and "episodes" in value else value
        counts = [len(v) for v in eps.values()]
        if not counts:
            print(f"{name:42s} empty")
            continue
        s = sorted(counts)
        p90 = s[min(len(s) - 1, int(round(0.9 * (len(s) - 1))))]
        kinds = Counter(e.get("kind") for v in eps.values() for e in v)
        bottom = sum(any(e.get("kind") == "bottom" for e in v) for v in eps.values())
        per = max((max(Counter((e.get("arm"), e.get("kind")) for e in v).values()) if v else 0) for v in eps.values())
        rule = value.get("rule", "A (no field)") if isinstance(value, dict) else "A (no field)"
        print(f"{name:42s} {len(counts):5d} {s[0]:4d} {statistics.median(s):4.0f} {p90:4d} {s[-1]:4d} {sum(c > 32 for c in counts):4d}"
              f"  {bottom:5d}/{len(counts):<5d}  {per:16d}  {dict(kinds)}  rule {rule}  ({f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
