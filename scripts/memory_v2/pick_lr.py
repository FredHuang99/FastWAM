"""Choose the ActionDiT learning rate from short probe runs (train_v2 --dry-run N, one folder per lr).

    python scripts/memory_v2/pick_lr.py outputs/memory_v2/a2probe --out outputs/memory_v2/a2probe/CHOICE.json

Each probe folder is named lr<value> and holds train.log with one "[train] {...}" JSON line per update
(fm = unweighted flow-matching loss of the update). All probes start from the same weights, so the median
fm of the first `--baseline` updates is the common starting loss.

A probe qualifies when (a) its final median (last `--tail` updates) is at most `--max-final` x the start
loss and (b) no running median of `--window` updates ever exceeded `--max-peak` x the start loss (the A335
failure: the loss rose 3.8x in lock-step with the warm-up). Among qualifying probes the lowest final median
wins; ties (within `--tie`) go to the larger lr. Exit code 1 when nothing qualifies (CHOICE.json says why).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

LINE = re.compile(r"\[train\] (\{.*\})$")


def read_fm(log: Path):
    out = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = LINE.search(line)
        if m:
            try:
                rec = json.loads(m.group(1))
            except json.JSONDecodeError:
                continue
            if "fm" in rec:
                out.append(float(rec["fm"]))
    return out


def running_median_max(values, window):
    if len(values) < window:
        return max(values) if values else float("nan")
    return max(statistics.median(values[i:i + window]) for i in range(0, len(values) - window + 1))


def choose(folders, baseline=5, tail=30, window=10, max_final=1.15, max_peak=1.5, tie=0.01, min_updates=40,
           fallback_max_final=1.6):
    rows = []
    for folder in folders:
        name = folder.name
        try:
            lr = float(name[2:]) if name.startswith("lr") else float(name)
        except ValueError:
            continue
        log = folder / "train.log"
        fm = read_fm(log) if log.exists() else []
        row = {"lr": lr, "folder": str(folder), "updates": len(fm)}
        if len(fm) < min_updates:
            row.update(status="too few updates", reason=f"{len(fm)} < {min_updates}")
            if log.exists() and "out of memory" in log.read_text(errors="replace").lower():
                row["status"] = "OOM"
            rows.append(row)
            continue
        start = statistics.median(fm[:baseline])
        final = statistics.median(fm[-tail:])
        peak = running_median_max(fm, window)
        row.update(start=start, final=final, final_ratio=final / start, peak_ratio=peak / start,
                   oom="out of memory" in log.read_text(errors="replace").lower())
        ok = row["final_ratio"] <= max_final and row["peak_ratio"] <= max_peak and not row["oom"]
        row["status"] = "ok" if ok else "rejected"
        row["reason"] = ("" if ok else
                         f"final {row['final_ratio']:.2f}x > {max_final}" if row["final_ratio"] > max_final else
                         f"peak {row['peak_ratio']:.2f}x > {max_peak}" if row["peak_ratio"] > max_peak else "OOM")
        rows.append(row)
    ok = [r for r in rows if r["status"] == "ok"]
    choice, fallback = None, False
    if ok:
        best = min(r["final"] for r in ok)
        near = [r for r in ok if r["final"] <= best * (1 + tie)]
        choice = max(near, key=lambda r: r["lr"])
    elif fallback_max_final:
        # Nothing met the strict rule (e.g. every lr bumps the loss early and 100 updates are too few to recover):
        # take the lowest final loss among probes that at least stayed below fallback_max_final x start. The
        # training run's own loss guard (2x the initial median) still stops a real divergence.
        soft = [r for r in rows if r.get("final_ratio") is not None and r["final_ratio"] <= fallback_max_final
                and r["peak_ratio"] <= fallback_max_final + 0.6 and not r["oom"]]
        if soft:
            choice, fallback = min(soft, key=lambda r: r["final"]), True
            choice["status"] = "fallback"
    return {"choice": None if choice is None else choice["lr"], "fallback": fallback,
            "probes": sorted(rows, key=lambda r: r["lr"]),
            "rule": {"baseline": baseline, "tail": tail, "window": window, "max_final": max_final, "max_peak": max_peak,
                     "tie": tie, "min_updates": min_updates, "fallback_max_final": fallback_max_final}}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--baseline", type=int, default=5)
    ap.add_argument("--tail", type=int, default=30)
    ap.add_argument("--window", type=int, default=10)
    ap.add_argument("--max-final", type=float, default=1.15)
    ap.add_argument("--max-peak", type=float, default=1.5)
    ap.add_argument("--min-updates", type=int, default=40)
    ap.add_argument("--fallback-max-final", type=float, default=1.6, help="0 = no fallback choice")
    args = ap.parse_args()
    folders = sorted(p for p in args.root.iterdir() if p.is_dir())
    result = choose(folders, args.baseline, args.tail, args.window, args.max_final, args.max_peak,
                    min_updates=args.min_updates, fallback_max_final=args.fallback_max_final)
    print(f"{'lr':>8}{'updates':>9}{'start':>9}{'final':>9}{'final/x':>9}{'peak/x':>8}  status")
    for r in result["probes"]:
        print(f"{r['lr']:>8.0e}{r['updates']:>9}{r.get('start', float('nan')):>9.4f}{r.get('final', float('nan')):>9.4f}"
              f"{r.get('final_ratio', float('nan')):>9.2f}{r.get('peak_ratio', float('nan')):>8.2f}  {r['status']} {r.get('reason', '')}")
    print(f"choice: {result['choice']}" + ("  (FALLBACK: no probe met the strict rule)" if result["fallback"] else ""))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return 0 if result["choice"] is not None else 1


if __name__ == "__main__":
    sys.exit(main())
