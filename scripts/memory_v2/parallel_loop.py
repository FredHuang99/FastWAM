"""Run k closed-loop shards of ONE task in parallel on the same GPU (plan v7 P0: evaluation throughput).

    python scripts/memory_v2/parallel_loop.py --k 3 -- <python -m fastwam.memory_v2.online run ... (no --shard)>

Starts k copies of the online command with `--shard j/k` (j = 0..k-1), all writing to the same --output folder
(scenes are disjoint, every episode has its own seed folder, run tags carry the shard). The copies stay in this
process's group, so the queue's SIGINT -> SIGTERM -> SIGKILL on the group reaches all of them; this wrapper ignores
SIGINT itself and waits until every copy has stopped its simulators. Exit code: 0 if all copies exit 0, else the
first non-zero code. A copy that fails does not stop the others (a re-run skips finished episodes).
"""
from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--" not in argv:
        raise SystemExit("usage: parallel_loop.py --k K -- <online command>")
    split = argv.index("--")
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--stagger", type=float, default=20.0, help="seconds between starts (model loading peaks)")
    args = ap.parse_args(argv[:split])
    cmd = argv[split + 1:]
    if args.k < 1:
        raise SystemExit("--k must be >= 1")
    if "--shard" in cmd:
        raise SystemExit("the online command must not carry --shard (parallel_loop sets it)")
    if not cmd:
        raise SystemExit("empty online command")
    signal.signal(signal.SIGINT, signal.SIG_IGN)          # the children get the group's SIGINT and stop cleanly
    children = []
    for j in range(args.k):
        shard_cmd = cmd + ["--shard", f"{j}/{args.k}"]
        print(f"[parallel_loop] start shard {j}/{args.k}: {' '.join(shard_cmd)}", flush=True)
        children.append(subprocess.Popen(shard_cmd, restore_signals=True,
                                         preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_DFL)))
        if j + 1 < args.k and args.stagger > 0:
            time.sleep(args.stagger)
    codes = [None] * args.k
    while any(c is None for c in codes):
        for j, child in enumerate(children):
            if codes[j] is None and child.poll() is not None:
                codes[j] = child.returncode
                print(f"[parallel_loop] shard {j}/{args.k} exited with {codes[j]}", flush=True)
        time.sleep(1)
    bad = [c for c in codes if c != 0]
    print(f"[parallel_loop] all shards done: exit codes {codes}", flush=True)
    return bad[0] if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
