"""Free disk on a training host: replace the INTERMEDIATE checkpoints of FINISHED runs by their weights-only copy.

What is dropped: optimizer state, loss history and RNG (only needed to resume training from that exact point).
What is kept bit-exact: update, memory, action, config, backend (everything evaluation, closed loop, init_memory and
a distillation teacher read), so every checkpoint can still be evaluated. 12.6 GB -> ~4.3 GB for an X7-size run.

Never touched:
  * runs without COMPLETE.json (still training, stopped, or crashed);
  * the file LATEST.json points to in each run (kept full, so a finished run can still be extended);
  * files smaller than --min-gb (memory-only runs, already slim files);
  * any checkpoint holding a 'raw' entry (distillation with EMA: raw training weights).

Dry run by default (reads only tensor metadata). --execute: for each file, write <file>.slim.partial, reload it and
check memory / action / update / config are equal to the source, then replace the source in place. One file at a
time; stops before writing if the free space is below the slim size + 5 GB. Everything is logged to
<out>/slim/SLIM_LOG.txt (and SLIM_LOG.jsonl, one record per replaced file).

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/slim_runs.py [--execute] [--runs a2C a2B0 ...]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
BJ = timezone(timedelta(hours=8))
KEEP = ("update", "memory", "action", "config", "backend")
GB = 1e9


def tensor_bytes(tree) -> int:
    import torch
    if isinstance(tree, torch.Tensor):
        return tree.numel() * tree.element_size()
    if isinstance(tree, dict):
        return sum(tensor_bytes(v) for v in tree.values())
    if isinstance(tree, (list, tuple)):
        return sum(tensor_bytes(v) for v in tree)
    return 0


def candidates(runs, min_gb, log):
    out = []
    for run in sorted(runs):
        d = O / run
        ck = d / "checkpoints"
        if not ck.is_dir():
            continue
        files = sorted(ck.glob("update_*.pt"))
        big = [f for f in files if f.stat().st_size >= min_gb * GB]
        if not big:
            continue
        if not (d / "COMPLETE.json").exists():
            log(f"  skip {run}: no COMPLETE.json (unfinished run), {len(big)} large files left as they are")
            continue
        try:
            latest = json.loads((ck / "LATEST.json").read_text())["file"]
        except (OSError, ValueError, KeyError):
            log(f"  skip {run}: LATEST.json unreadable")
            continue
        for f in big:
            if f.name != latest:
                out.append((run, f, latest))
    return out


def same(a, b) -> bool:
    import torch
    if a is None or b is None:
        return a is None and b is None
    return a.keys() == b.keys() and all(torch.equal(a[k], b[k]) for k in a)


def main():
    import torch
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="replace the files (default: dry run)")
    ap.add_argument("--runs", nargs="*", help="only these run folders (default: every run under the output root)")
    ap.add_argument("--min-gb", type=float, default=6.0)
    args = ap.parse_args()
    logdir = O / "slim"
    logdir.mkdir(parents=True, exist_ok=True)
    text = (logdir / "SLIM_LOG.txt").open("a", encoding="utf-8")

    def log(msg):
        line = f"[slim] {datetime.now(BJ):%F %T} {msg}"
        print(line, flush=True)
        text.write(line + "\n")
        text.flush()

    runs = args.runs or [p.name for p in O.iterdir() if p.is_dir()]
    log(f"{'EXECUTE' if args.execute else 'DRY RUN'} under {O}; runs: {'given' if args.runs else 'all'}")
    todo = candidates(runs, args.min_gb, log)
    plan, total_free = [], 0
    for run, f, latest in todo:
        state = torch.load(f, map_location="cpu", weights_only=False, mmap=True)
        if "raw" in state:
            log(f"  skip {run}/{f.name}: holds 'raw' (distillation) weights")
            continue
        if "memory" not in state:
            log(f"  skip {run}/{f.name}: no 'memory' entry")
            continue
        keep = sum(tensor_bytes(state.get(k)) for k in KEEP)
        size = f.stat().st_size
        dropped = sorted(k for k in state if k not in KEEP)
        if not dropped:
            log(f"  skip {run}/{f.name}: already slim")
            continue
        plan.append((run, f, latest, size, keep, dropped))
        total_free += size - keep
        del state
    log(f"{len(plan)} files to slim; frees about {total_free / GB:.0f} GB; the LATEST file of each run stays full")
    for run, f, latest, size, keep, dropped in plan:
        log(f"  {run}/checkpoints/{f.name}: {size / GB:.1f} GB -> about {keep / GB:.1f} GB "
            f"(drops {', '.join(dropped)}; kept full: {latest})")
    if not args.execute:
        log("dry run only: nothing was changed (rerun with --execute after confirming)")
        return 0
    done = 0
    for run, f, latest, size, keep, dropped in plan:
        free = shutil.disk_usage(f.parent).free
        if free < keep + 5 * GB:
            log(f"STOP: {free / GB:.0f} GB free < {(keep + 5 * GB) / GB:.0f} GB needed for {run}/{f.name}")
            return 1
        t0 = time.time()
        state = torch.load(f, map_location="cpu", weights_only=False, mmap=True)
        slim = {k: state[k] for k in KEEP if k in state}
        slim["slimmed_from"] = {"file": str(f), "bytes": size, "dropped": dropped,
                                "time": datetime.now(BJ).isoformat(timespec="seconds")}
        tmp = f.with_name(f.name + ".slim.partial")
        torch.save(slim, tmp)
        back = torch.load(tmp, map_location="cpu", weights_only=False)
        ok = (same(state.get("memory"), back.get("memory")) and same(state.get("action"), back.get("action"))
              and state.get("update") == back.get("update") and state.get("config") == back.get("config"))
        if not ok:
            tmp.unlink(missing_ok=True)
            log(f"STOP: {run}/{f.name}: the slim copy does not match the source; source left untouched")
            return 1
        del state, back, slim
        os.replace(tmp, f)
        new = f.stat().st_size
        done += 1
        rec = {"run": run, "file": f.name, "bytes_before": size, "bytes_after": new, "dropped": dropped,
               "seconds": round(time.time() - t0, 1), "time": datetime.now(BJ).isoformat(timespec="seconds")}
        with (logdir / "SLIM_LOG.jsonl").open("a", encoding="utf-8") as j:
            j.write(json.dumps(rec) + "\n")
        log(f"  [{done}/{len(plan)}] {run}/{f.name}: {size / GB:.1f} -> {new / GB:.1f} GB, verified, "
            f"{rec['seconds']:.0f} s; free now {shutil.disk_usage(f.parent).free / GB:.0f} GB")
    log(f"finished: {done} files slimmed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
