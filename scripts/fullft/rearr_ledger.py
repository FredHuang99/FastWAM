"""Rearrange, body-record model: when the arm presses the button a second time, was the first press already in its
record? (11-22 23:20, Opus; follow-up of rearr_split.py: rearrange_arprop e30 still fails 35 / 100 on the press, 18
pressed twice and 17 never pressed.) Read-only, CPU, zero GPU: the A40 episodes already there. Descriptive.
Sources per episode: executed_actions.jsonl (completed_target_id, objects_after.press_cnt = the env's press counter)
and decisions.jsonl (frame_id, ledger = [frame, arm, kind, confirmed, ...] entries the model saw at that decision).
t1 / t2 = the first executed target where press_cnt reached 1 / 2. The first press's record entry = a 'bottom' of the
left arm (arm 0) within +-15 targets of t1.
  pressed twice: at the decisions between t1 and t2 (the ones that led to the second press), was the entry in the
                 record? always -> the record had it, the model pressed again anyway (a USE failure); never -> the record
                 did not have it (a WRITE / READ failure); sometimes -> mixed
  success:       the same for the decisions after t1 (calibration: the entry should be there), and how many targets after
                 t1 it first appears (the write delay)
  never pressed: the left arm's entries in the last decision's record (did a press-like event appear at all?)
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/rearr_ledger.py [FOLDER:LABEL ...]   (default e6:rearrange_arprop_e30)
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
TASK = "rearrange_blocks"
WIN = 15


def rows(p: Path):
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []


def first_at(acts, n):
    for r in acts:
        c = (r.get("objects_after") or {}).get("press_cnt")
        if isinstance(c, (int, float)) and c >= n:
            return int(r.get("completed_target_id") or 0)
    return None


def has_entry(ledger, t1):
    return any(int(e[1]) == 0 and e[2] == "bottom" and abs(int(e[0]) - t1) <= WIN for e in ledger)


def main():
    items = sys.argv[1:] or ["e6:rearrange_arprop_e30"]
    for item in items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / TASK
        out = Counter()
        delays, examples = [], {}
        for d in sorted(root.glob("seed_*")):
            acts, decs = rows(d / "executed_actions.jsonl"), rows(d / "decisions.jsonl")
            res = d / "result.json"
            if not acts or not decs or not res.exists():
                continue
            ok = bool(json.loads(res.read_text()).get("success"))
            t1, t2 = first_at(acts, 1), first_at(acts, 2)
            if t1 is None:
                last = decs[-1].get("ledger") or []
                left = [e for e in last if int(e[1]) == 0]
                key = "never pressed: left-arm entries at the last decision " + ("none" if not left else
                      ",".join(sorted({e[2] for e in left})))
                out[key] += 1
                continue
            end = t2 if t2 is not None else 10 ** 9
            between = [has_entry(x.get("ledger") or [], t1) for x in decs if t1 < int(x["frame_id"]) < end]
            seen = next((int(x["frame_id"]) for x in decs if int(x["frame_id"]) > t1 and has_entry(x.get("ledger") or [], t1)), None)
            if seen is not None:
                delays.append(seen - t1)
            tag = "pressed twice" if t2 is not None else ("success" if ok else "pressed once, failed later")
            state = ("no decision in between" if not between else "always in the record" if all(between)
                     else "never in the record" if not any(between) else "sometimes in the record")
            out[f"{tag}: first press {state}"] += 1
            examples.setdefault(f"{tag}: first press {state}", []).append(d.name[5:])
        print(f"\n== {item}")
        for k, v in sorted(out.items()):
            print(f"  {v:3d}  {k}   e.g. {examples.get(k, [])[:4]}")
        if delays:
            print(f"  write delay (targets from the press to the first decision whose record has it): median "
                  f"{statistics.median(delays)}, min {min(delays)}, max {max(delays)}, n {len(delays)}")
    print("\nREARR LEDGER REPORT done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
