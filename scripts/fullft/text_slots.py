"""How many record entries fit in a task's cached instruction text? (11-23 15:00, Opus; the old H200's ranking readiness
check said the last 80 text positions are not padding in all 50 ranking episodes.) The body record is written into the
LAST event_max positions of the cached text context, which must be exact zeros (data.check_ledger_slots). Prints, per
task: the text length, the trailing all-zero positions per episode (min / median / max) = the largest event_max that
fits, and how many demos have more events than that (from the task's events file when given). Read-only, CPU.
  PYTHONPATH=src CUDA_VISIBLE_DEVICES= /opt/mwam/bin/python scripts/fullft/text_slots.py \
      --root outputs/memory_v2/press/dense_blocks_ranking_try_v1 --task blocks_ranking_try \
      [--events outputs/fullft/events/events_blocks_ranking_try.json]
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def trailing_zeros(text) -> int:
    rows = (text.abs().sum(-1) == 0).tolist()
    n = 0
    for z in reversed(rows):
        if not z:
            break
        n += 1
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--task", required=True)
    ap.add_argument("--events", default="")
    args = ap.parse_args()
    from fastwam.fullft.data import DenseEpisodes
    eps = DenseEpisodes([args.root], [args.task])
    free, length = [], None
    for r in eps.records:
        t = eps(r["episode_id"])["text"]
        t = t.reshape(-1, t.shape[-1])
        length = t.shape[0]
        free.append(trailing_zeros(t))
    k = min(free)
    print(f"[slots] {args.task}: {len(free)} episodes; text length {length}; trailing zero positions min {k}, "
          f"median {statistics.median(free)}, max {max(free)} -> the largest record that fits: {k} entries")
    if args.events and Path(args.events).exists():
        v = json.loads(Path(args.events).read_text())
        ev = v["episodes"] if isinstance(v, dict) and "episodes" in v else v
        n = sorted(len(x) for x in ev.values())
        over = sum(x > k for x in n)
        print(f"[slots] events per demo min {n[0]}, median {statistics.median(n)}, max {n[-1]}; demos with more than "
              f"{k} events: {over}/{len(n)}")


if __name__ == "__main__":
    main()
