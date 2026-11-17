"""11-17 21:10 (Opus), read-only diagnosis of ledger_ready.py check 3 on the H100 (rearrange_blocks 89/100,
cover_blocks 73/100 episode-arms with equal 'close' frames; swap_T, blocks_ranking_try, battery_try 100/100).

Check 3 compares the 'close' events of the task's event file (events.py: gripper hysteresis 0.35 / 0.65 AND the
min_path debounce: an event < 3 cm of end-effector path after the previous event of the same arm is dropped) with the
commanded gripper crossings of the training cache (same hysteresis, no debounce). For every episode-arm that differs,
each difference is put in one class:
  MISSING   a crossing with no event at the same frame (what the debounce does) -> also: the previous event of the
            same arm in the event file (kind, frames before the crossing)
  EXTRA     an event 'close' with no crossing at the same frame (the debounce never adds events: a different gripper
            signal or a misalignment)
  SHIFTED   an EXTRA within +-3 frames of a MISSING (frames off: alignment)
Prints counts per task and the first examples. CPU only.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/ready_diag.py --tasks rearrange_blocks cover_blocks
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

import torch

R = Path("/workspace/FastWAM-memory2")
spec = importlib.util.spec_from_file_location("mwam_ledger_ready", R / "scripts/fullft/ledger_ready.py")
lr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", required=True)
    ap.add_argument("--examples", type=int, default=6)
    args = ap.parse_args()
    from fastwam.fullft.data import DenseEpisodes, load_events, match_events
    stats = json.loads(Path(lr.STATS).read_text())["state"]["default"]
    mean, std = torch.tensor(stats["global_mean"]), torch.tensor(stats["global_std"]) + 1e-8
    for task in args.tasks:
        root = lr.ROOTS.get(task, str(R / f"outputs/memory_v2/press/dense_{task}_v1"))
        eps = DenseEpisodes([root], [task])
        events = load_events([str(R / f"outputs/fullft/events/events_{task}.json")])
        matched = match_events([r["episode_id"] for r in eps.records], events)
        cls, prev_kind, gaps, examples, n_arms, n_diff = Counter(), Counter(), [], [], 0, 0
        for r in eps.records:
            eid = r["episode_id"]
            if eid not in matched:
                continue
            raw = eps(eid)["proprio"].float() * std + mean
            evs = sorted(matched[eid], key=lambda x: int(x["frame"]))
            for arm, col in ((0, 6), (1, 13)):
                n_arms += 1
                want = sorted({int(x["frame"]) for x in evs if x["arm"] == arm and x["kind"] == "close"})
                got = lr.closes(raw[:, col].tolist())
                if want == got:
                    continue
                n_diff += 1
                missing = [f for f in got if f not in want]
                extra = [f for f in want if f not in got]
                shifted = {(m, e) for m in missing for e in extra if abs(m - e) <= 3}
                for m in missing:
                    if any(m == s[0] for s in shifted):
                        continue
                    cls["MISSING"] += 1
                    before = [x for x in evs if x["arm"] == arm and int(x["frame"]) < m]
                    if before:
                        prev_kind[before[-1]["kind"]] += 1
                        gaps.append(m - int(before[-1]["frame"]))
                    else:
                        prev_kind["(none)"] += 1
                for e in extra:
                    if not any(e == s[1] for s in shifted):
                        cls["EXTRA"] += 1
                cls["SHIFTED"] += len(shifted)
                if len(examples) < args.examples:
                    g = raw[:, col].tolist()
                    examples.append(f"  {eid} arm {arm}: crossings {got} / event closes {want}; missing {missing} "
                                    f"extra {extra}; gripper at missing frames "
                                    f"{[round(min(g[max(0, m - 3):m + 4]), 2) for m in missing][:4]}; "
                                    f"same-arm events before: "
                                    f"{[(x['kind'], int(x['frame'])) for x in evs if x['arm'] == arm and missing and int(x['frame']) < missing[0]][-2:]}")
        gp = sorted(gaps)
        print(f"[diag] {task}: {n_diff}/{n_arms} episode-arms differ; classes {dict(cls)}; previous same-arm event "
              f"of a MISSING close: {dict(prev_kind)}; frames since it: "
              f"{'median %d, max %d' % (gp[len(gp) // 2], gp[-1]) if gp else '-'}")
        print("\n".join(examples))


if __name__ == "__main__":
    main()
