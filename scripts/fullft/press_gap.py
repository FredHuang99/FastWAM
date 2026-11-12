"""Where do the button presses go missing? (11-12, descriptive, CPU only; episode files are read, never written.)

The new base (N7 e10) lifts the block in 50/50 put episodes but presses the button in only 36/50, and in swap it
completes the three moves in 29/50 episodes but succeeds in 2. For each episode of one label this classifies what
happened around the button decision, from the logged block positions and the simulator's press counter:

put_back_block (episodes that reached the centre):
  pressed              the counter rose after the block reached the centre
  skipped -> returned  never pressed; the block was carried back to a mat (the press was skipped)
  skipped -> stuck     never pressed and the block stayed at the centre until the end
swap_blocks (episodes that completed the three moves, s3):
  pressed after s3     the counter rose after the third move (success if the simulator agrees)
  pressed before s3    the counter rose before the third move only (premature press)
  kept moving          no press after s3 and at least one more block move after s3 (did not know the swap was done)
  idle after s3        no press after s3 and no further block move (hovering until the target limit)
plus, per class, the median number of executed targets between the decisive event and the end of the episode.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_gap.py --folder closed_loop/g1 --label ar_2task_e10
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cls", HERE.parent / "memory_v2" / "closed_loop_stages.py")
cls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cls)
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")


def first_press(counters, after=0):
    base = max([c.get("press_cnt", 0) or 0 for c in counters[:after]] + [0])
    return next((i + 1 for i, c in enumerate(counters) if i + 1 > after and (c.get("press_cnt") or 0) > base), None)


def put_case(snaps, counters):
    ev, _ = cls.events(snaps, ["block"], cls.put_back_location)
    centre = next((e["t"] for e in ev if e["to"] == "centre"), None)
    if centre is None:
        return None, None
    press = first_press(counters, centre)
    if press is not None:
        return "pressed", press
    back = next((e["t"] for e in ev if e["t"] > centre and e["to"] not in ("table", "centre")), None)
    return ("skipped -> returned", back) if back is not None else ("skipped -> stuck", centre)


def swap_case(snaps, counters):
    r = cls.analyse_swap(snaps, counters)
    if not r["s3"]:
        return None, None
    ev, _ = cls.events(snaps, ["block1", "block2"], cls.swap_location)
    moves = [e for e in ev if e["to"] != "table"]
    # the third move = the first move of the first-moved block into the other block's start tray after s2 (as analyse_swap)
    start = {b: cls.swap_location(*snaps[0][b]["p"][:2]) for b in ("block1", "block2")}
    empty = next(iter(set(cls.TRAYS) - set(start.values())), None)
    s1 = next(e for e in moves if e["to"] == empty)
    first, other = s1["block"], ("block2" if s1["block"] == "block1" else "block1")
    s2 = next(e for e in moves if e["t"] > s1["t"] and e["block"] == other and e["to"] == start[first])
    s3 = next(e for e in moves if e["t"] > s2["t"] and e["block"] == first and e["to"] == start[other])
    after = first_press(counters, s3["t"])
    if after is not None:
        return "pressed after s3", after
    if first_press(counters, 0) is not None:
        return "pressed before s3", s3["t"]
    later = [e for e in moves if e["t"] > s3["t"]]
    return ("kept moving", s3["t"]) if later else ("idle after s3", s3["t"])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--mode", default="on")
    args = ap.parse_args()
    root = Path(args.folder) if args.folder.startswith("/") else O / args.folder
    for task, fn in (("put_back_block", put_case), ("swap_blocks", swap_case)):
        cases, tail, succ = Counter(), defaultdict(list), Counter()
        n = 0
        for result in sorted((root / args.label / args.mode / task).glob("seed_*/result.json")):
            d = result.parent
            if not cls.SEED_DIR.fullmatch(d.name) or not (d / "executed_actions.jsonl").exists():
                continue
            n += 1
            res = json.loads(result.read_text())
            snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
            if len(snaps) < 2 or not snaps[0]:
                continue
            case, t = fn(snaps, counters)
            if case is None:
                continue
            cases[case] += 1
            succ[case] += bool(res.get("success"))
            tail[case].append(len(counters) - (t or 0))
        print(f"{task} ({args.label}/{args.mode}, {n} episodes; reached the decision: {sum(cases.values())})")
        for case, k in cases.most_common():
            print(f"  {case:<22} {k:>3}   success {succ[case]:>3}   targets left after the event (median) "
                  f"{statistics.median(tail[case]):.0f}")


if __name__ == "__main__":
    main()
