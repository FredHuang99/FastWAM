"""Plan v20 section 8 item 5 (11-24, Opus): why does the three-frame ranking model fail (blocks_ranking_try, 77/100)?
Read-only, CPU, zero GPU: the A40 episodes already there. Descriptive (whether card 4 is worth it; plan v20 2.1).
The task (RMBench envs/blocks_ranking_try.py, read 11-24): three blocks on three slots x = 0.04 / 0.16 / 0.28
(y -0.1), a random non-sorted order; success = block1 < block2 < block3 in x (within 13 cm / 4 cm of each other),
right gripper open, and the button pressed while so. The expert presses the button first, then, until success,
swaps two blocks with the right arm and presses again, in the fixed order (middle,right) (left,right) (left,middle)
(middle,right) (left,right) -- it walks the six orders without repeating one; which order is next is not in the
current image (the blocks look alike apart from colour): the policy must keep track of how many it has tried.
Logged per executed target (objects_after): block1 / block2 poses (block3 is not in the adapter's snapshot; with all
three on slots it is on the remaining one), press_cnt. Per episode:
  order at each counted press (block1 / block2 slots, block3 the rest), the number of presses, distinct orders pressed
  classes, in this order: success | never pressed | repeated an order already pressed (a counting error) | a block off
  the slots at the end (manipulation) | the sorted order reached but not pressed | ran out of time without repeating
  | other
  Also: does the order sequence follow the expert's swap order (cumulative position k after k swaps)?
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/ranking_split.py [FOLDER:LABEL ...]   (default e6:ranking_ar_e30)
Writes outputs/fullft/RANKING_SPLIT.json.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
TASK = "blocks_ranking_try"
SLOTS = (0.04, 0.16, 0.28)
TOL, Y0, REST = 0.03, -0.1, 0.785          # on a slot: |dx|, |dy| < 3 cm and resting (block centre z 0.765 + margin)
EXPERT = [(1, 2), (0, 2), (0, 1), (1, 2), (0, 2)]   # position pairs swapped (left 0, middle 1, right 2)


def slot(p):
    if p is None or p[2] > REST or abs(p[1] - Y0) > TOL:
        return None
    k = min(range(3), key=lambda i: abs(p[0] - SLOTS[i]))
    return k if abs(p[0] - SLOTS[k]) < TOL else None


def order(snap):
    """(slot of block1, slot of block2, slot of block3) or None when not all resting on slots."""
    a = slot((snap.get("block1") or {}).get("p"))
    b = slot((snap.get("block2") or {}).get("p"))
    if a is None or b is None or a == b:
        return None
    return a, b, 3 - a - b


def expert_orders(start):
    """The six orders the expert visits from `start` (tuple of slots of block1..3), in its swap order."""
    out, cur = [start], list(start)
    for i, j in EXPERT:
        inv = {s: blk for blk, s in enumerate(cur)}          # which block sits on slot s
        bi, bj = inv[i], inv[j]
        cur[bi], cur[bj] = j, i
        out.append(tuple(cur))
    return out


def episode(d: Path):
    acts = [json.loads(x) for x in (d / "executed_actions.jsonl").read_text().splitlines() if x.strip()]
    ok = bool(json.loads((d / "result.json").read_text()).get("success"))
    snaps = [acts[0].get("objects_before") or {}] + [r.get("objects_after") or {} for r in acts]
    start = order(snaps[0])
    presses, last_order, prev = [], start, 0
    for t, s in enumerate(snaps):
        o = order(s)
        if o is not None:
            last_order = o
        c = s.get("press_cnt")
        if isinstance(c, (int, float)) and c > prev:
            presses.append({"t": t, "order": last_order})
            prev = int(c)
    seq = [p["order"] for p in presses]
    distinct = len(set(o for o in seq if o is not None))
    repeated = len(seq) != len(set(seq))
    final = order(snaps[-1])
    sorted_o = (0, 1, 2)
    reached_sorted = any(order(s) == sorted_o for s in snaps)
    exp = expert_orders(start) if start else []
    follows = all(o == exp[k] for k, o in enumerate(seq) if k < len(exp)) if seq and exp else None
    info = {"presses": len(seq), "distinct_orders_pressed": distinct, "start": start, "final": final,
            "orders_pressed": seq, "expert_position_of_sorted": exp.index(sorted_o) if sorted_o in exp else None,
            "follows_expert_order": follows, "reached_sorted": reached_sorted, "targets": len(acts)}
    if ok:
        return "success", info
    if not seq:
        return "never pressed", info
    if repeated:
        return "repeated an order already pressed (counting error)", info
    if final is None:
        return "a block off the slots at the end (manipulation)", info
    if reached_sorted:
        return "the sorted order reached but not confirmed by a press", info
    return "ran out of time without repeating an order", info


def main():
    items = sys.argv[1:] or ["e6:ranking_ar_e30"]
    out = {}
    for item in items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / TASK
        eps = sorted(d for d in root.glob("seed_*") if d.is_dir() and (d / "result.json").exists()
                     and (d / "executed_actions.jsonl").exists())
        if not eps:
            print(f"{item}: no episodes")
            continue
        counts, seeds, per = Counter(), defaultdict(list), {}
        follow = Counter()
        for d in eps:
            c, info = episode(d)
            counts[c] += 1
            seeds[c].append(int(d.name[5:]))
            follow[str(info["follows_expert_order"])] += 1
            per[d.name[5:]] = dict(info, cls=c)
        print(f"\n{item}: {len(eps)} episodes")
        for c, k in counts.most_common():
            print(f"  {k:3d}  {c}   e.g. seeds {seeds[c][:4]}")
        fails = [v for v in per.values() if v["cls"] != "success"]
        if fails:
            print(f"  failures: presses per episode {Counter(v['presses'] for v in fails)}; distinct orders pressed "
                  f"{Counter(v['distinct_orders_pressed'] for v in fails)}")
            print(f"  failures: where the sorted order sits in the expert's walk (0 = start) "
                  f"{Counter(v['expert_position_of_sorted'] for v in fails)}")
        succ = [v for v in per.values() if v["cls"] == "success"]
        if succ:
            print(f"  successes: where the sorted order sits in the expert's walk {Counter(v['expert_position_of_sorted'] for v in succ)}")
        print(f"  pressed orders follow the expert's swap order (True / False / None = no press): {dict(follow)}")
        out[item] = {"counts": dict(counts), "episodes": per}
    (F / "RANKING_SPLIT.json").write_text(json.dumps(out, indent=1) + "\n")
    print("\nRANKING SPLIT REPORT: written outputs/fullft/RANKING_SPLIT.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
