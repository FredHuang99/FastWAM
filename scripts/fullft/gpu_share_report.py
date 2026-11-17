"""Other users' share of a shared machine's GPUs over the last N hours (default 24), from gpu_share.sh's samples.
Read-only; standard library only.

Per look and GPU (gpu_share.sh, every ~10 min):
  ours    one of our queue trainers runs on it
  others  not ours and >= 1000 MiB in use (the queue's own "busy" test: someone else holds it)
  free    not ours and < 1000 MiB
On a GPU of ours, someone else also on it shows only as >= 2 compute processes (when the container can see them).
Printed: per GPU the share of looks ours / others / free and the others' mean utilisation while they hold it; overall
the mean and max number of GPUs held by others, their compute in GPU-equivalents (sum of utilisation / 100 over the
GPUs they hold), and the share of looks in which >= 2 GPUs were held by nobody (what a 4-GPU plan would need).
No rule is applied: the user decides whether we may use all GPUs again (11-17 16:50).
  /opt/mwam/bin/python scripts/fullft/gpu_share_report.py [--hours 24] [--short]
"""
from __future__ import annotations

import argparse
import statistics
import time
from collections import defaultdict
from pathlib import Path

BUSY_MIB = 1000


def load(path: Path):
    rows = []
    for line in path.read_text().splitlines()[1:]:
        f = line.split("\t")
        if len(f) < 7:
            continue
        try:
            rows.append({"t": int(f[0]), "iso": f[1], "gpu": int(f[2]), "util": float(f[3]), "mem": float(f[4]),
                         "apps": int(f[5]), "ours": f[6].strip() == "1"})
        except ValueError:
            continue
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tsv", default="/workspace/FastWAM-memory2/outputs/fullft/GPU_SHARE_h100.tsv")
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--short", action="store_true", help="one line (for the queue heartbeat)")
    args = ap.parse_args()
    path = Path(args.tsv)
    if not path.exists():
        raise SystemExit(f"no samples yet: {path} (start: bash scripts/fullft/gpu_share.sh start)")
    now = time.time()
    rows = [r for r in load(path) if r["t"] >= now - args.hours * 3600]
    if not rows:
        raise SystemExit(f"no samples in the last {args.hours:g} h in {path}")
    looks = defaultdict(list)
    for r in rows:
        looks[r["t"]].append(r)
    times = sorted(looks)
    gaps = [b - a for a, b in zip(times, times[1:])]
    step = statistics.median(gaps) if gaps else 600
    covered = min(1.0, len(times) * step / (args.hours * 3600))
    gpus = sorted({r["gpu"] for r in rows})
    per = {g: {"n": 0, "ours": 0, "others": 0, "free": 0, "util": [], "shared": 0} for g in gpus}
    held, equiv, nobody = [], [], []
    for t in times:
        h = e = free = 0
        for r in looks[t]:
            p = per[r["gpu"]]
            p["n"] += 1
            if r["ours"]:
                p["ours"] += 1
                p["shared"] += r["apps"] >= 2
            elif r["mem"] >= BUSY_MIB:
                p["others"] += 1
                p["util"].append(r["util"])
                h += 1
                e += r["util"] / 100
            else:
                p["free"] += 1
                free += 1
        held.append(h)
        equiv.append(e)
        nobody.append(free)
    apps_seen = any(r["apps"] > 0 for r in rows)
    span = f"{looks[times[0]][0]['iso']} .. {looks[times[-1]][0]['iso']}"
    mean_held, mean_eq = statistics.mean(held), statistics.mean(equiv)
    two_free = sum(f >= 2 for f in nobody) / len(nobody)
    if args.short:
        print(f"GPU share last {args.hours:g} h ({len(times)} looks, {covered:.0%} covered): others hold "
              f"{mean_held:.1f} GPUs on average (max {max(held)}), compute {mean_eq:.1f} GPU-equivalents; "
              f">= 2 GPUs held by nobody in {two_free:.0%} of looks")
        return
    print(f"GPU share, last {args.hours:g} h: {len(times)} looks every ~{step / 60:.0f} min ({span}; "
          f"{covered:.0%} of the window covered)")
    print("GPU | ours  | others | free  | others' mean util while they hold it" + (" | ours shared" if apps_seen else ""))
    for g in gpus:
        p = per[g]
        n = max(p["n"], 1)
        u = f"{statistics.mean(p['util']):.0f} %" if p["util"] else "-"
        sh = f" | {p['shared']}/{p['ours']}" if apps_seen else ""
        print(f" {g}  | {p['ours'] / n:5.0%} | {p['others'] / n:6.0%} | {p['free'] / n:5.0%} | {u}{sh}")
    print(f"GPUs held by others: mean {mean_held:.2f}, max {max(held)}, min {min(held)}; their compute: mean "
          f"{mean_eq:.2f} GPU-equivalents (sum of utilisation over the GPUs they hold)")
    print(f"GPUs held by nobody: mean {statistics.mean(nobody):.2f}; >= 2 of them in {two_free:.0%} of the looks")
    if not apps_seen:
        print("(the container lists no compute processes: someone else on one of OUR GPUs cannot be seen; "
              "our trainers use ~91 of 94 GiB, so little else fits there)")


if __name__ == "__main__":
    main()
