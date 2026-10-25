"""Read-only health check of the A-v2 queue (scripts/memory_v2/jobs/a100_queue_4.sh) with a verdict.

    /opt/mwam/bin/python scripts/memory_v2/queue4_check.py

Prints, then ends with either "VERDICT: OK - nothing to do" or "VERDICT: ACTION NEEDED" + the reasons:
  lanes      : base / ablate / watch alive, finished ("lane done") or dead
  lr probe   : per lr final/start and peak/start loss ratios, the choice (FALLBACK flagged)
  training   : a2C / a2C_nopairs - process alive, update/total, epoch, s/update, ETA (Beijing time), loss trend
               (median fm of the last 30 updates / first 30), last offline eval vs the update-0 eval, guard,
               errors in stdout.log, minutes since the last update
  closed loop: bank summary written, noabs done, the episode running now, finished checkpoints
  GPUs, disk
Changes nothing.
"""
from __future__ import annotations

import json
import re
import statistics
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
Q = O / "queue4"
CL = O / "closed_loop"
CLOUT = CL / "a2"
BJ = timezone(timedelta(hours=8))
problems, warnings = [], []


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60).stdout
    except Exception as error:                      # noqa: BLE001
        return f"<{error}>"


def bj(ts=None):
    return datetime.fromtimestamp(ts or time.time(), BJ).strftime("%m-%d %H:%M")


def tail(path: Path, n=3):
    try:
        return path.read_text(errors="replace").splitlines()[-n:]
    except OSError:
        return []


def section(title):
    print(f"\n== {title}")


def processes():
    out = sh("pgrep -af 'a100_queue_4.sh|a100_final.sh|fastwam.memory_v2.train_v2|fastwam.memory_v2.online run'")
    return [line for line in out.splitlines() if "pgrep" not in line and "queue4_check" not in line]


def main():
    deadline = datetime(2026, 10, 27, 0, 0, tzinfo=BJ).timestamp()
    left = (deadline - time.time()) / 3600
    print(f"queue4 check  {bj()} (Beijing)   GPU guard / queue deadline Tue 10-27 00:00 ({left:.1f} h left)")
    procs = processes()

    # ------------------------------------------------------------------ lanes
    section("lanes")
    for lane in ("base", "ablate", "watch", "final"):
        log = Q / f"{lane}.log"
        if (Q / f"RETIRED_{lane}").exists():
            print(f"  {lane:<7} retired (replaced by a100_final.sh)")
            continue
        if lane == "final" and not log.exists():
            continue
        script = "a100_final\\.sh" if lane == "final" else rf"a100_queue_4\.sh {lane}\b"
        alive = any(re.search(script, p) for p in procs)
        last = tail(log, 2)
        done = any("lane done" in line or "final done" in line for line in tail(log, 50))
        failed = [line for line in tail(log, 50) if "PROBE FAILED" in line or "GUARD tripped" in line or "lane stops" in line]
        state = "alive" if alive else ("finished" if done else "NOT RUNNING")
        print(f"  {lane:<7} {state}")
        for line in last:
            print(f"          {line[:170]}")
        if not alive and not done:
            if (Q / "STOP").exists():
                warnings.append(f"lane {lane} stopped by {Q / 'STOP'}")
            else:
                problems.append(f"lane {lane} is not running and did not finish ({log})")
        for line in failed:
            problems.append(f"lane {lane}: {line.strip()[:160]}")

    # ------------------------------------------------------------------ probe
    section("lr probe")
    choice_file = O / "a2probe" / "CHOICE.json"
    lr = None
    if choice_file.exists():
        c = json.loads(choice_file.read_text())
        for r in c["probes"]:
            print(f"  lr {r['lr']:.0e}: {r['updates']:>3} updates  final/start {r.get('final_ratio', float('nan')):.2f}  "
                  f"peak/start {r.get('peak_ratio', float('nan')):.2f}  {r['status']} {r.get('reason', '')}")
        lr = c["choice"]
        print(f"  choice: lr_action = {lr}" + ("   (FALLBACK: no lr met the strict rule)" if c.get("fallback") else ""))
        if lr is None:
            problems.append("lr probe: no lr qualified (A2C did not start)")
        elif c.get("fallback"):
            warnings.append("lr chosen by the fallback rule: watch the A2C loss trend")
    else:
        for d in sorted((O / "a2probe").glob("lr*")):
            n = sum('"fm"' in line for line in (d / "train.log").read_text(errors="replace").splitlines()) if (d / "train.log").exists() else 0
            print(f"  {d.name}: {n} updates so far")
        print("  (no CHOICE.json yet: probe still running)")

    # ------------------------------------------------------------------ training
    section("training")
    for run in ("a2C", "a2C_nopairs"):
        d = O / run
        alive = any(re.search(rf"output=\S*/{run}(\s|$)", p) for p in procs if "train_v2" in p)
        if not (d / "CONFIG.json").exists():
            print(f"  {run}: not started" + (" (process loading)" if alive else ""))
            continue
        cfg = json.loads((d / "CONFIG.json").read_text())
        total, upe = cfg["total_updates"], cfg["updates_per_epoch"]
        rows = [json.loads(line) for line in (d / "metrics.jsonl").read_text().splitlines() if line.strip()] \
            if (d / "metrics.jsonl").exists() else []
        complete, guard = (d / "COMPLETE.json").exists(), (d / "GUARD.json").exists()
        state = "COMPLETE" if complete else "GUARD" if guard else ("running" if alive else "PROCESS NOT RUNNING")
        print(f"  {run}: [{state}]  lr_action {cfg['config']['optim']['lr_action']}  pairs "
              f"{'on' if cfg['config'].get('pairs') else 'off'}")
        if guard:
            problems.append(f"{run}: training guard tripped: {(d / 'GUARD.json').read_text().strip()[:200]}")
        if rows:
            r = rows[-1]
            sec = statistics.mean(x["seconds"] for x in rows[-20:])
            eta = time.time() + (total - r["update"]) * sec
            age = (time.time() - (d / "metrics.jsonl").stat().st_mtime) / 60
            print(f"    update {r['update']}/{total}  epoch {r['epoch']}/{cfg['config']['schedule']['epochs']}  "
                  f"{sec:.0f} s/update  ETA {bj(eta)}  last update {age:.0f} min ago  peak {r.get('peak_gpu_bytes', 0) / 2**30:.1f} GB")
            fm = [x["fm"] for x in rows]
            k = min(30, max(1, len(fm) // 3))
            first, last = statistics.median(fm[:k]), statistics.median(fm[-k:])
            ratio = last / first if first else float("nan")
            pair = [x["pair_loss"] for x in rows if "pair_loss" in x]
            print(f"    fm median first {k}: {first:.4f}  last {k}: {last:.4f}  (x{ratio:.2f})"
                  + (f"   pair loss last {statistics.median(pair[-k:]):.4f}" if pair else "")
                  + f"   grad norm {statistics.median(x['grad_norm'] for x in rows[-k:]):.3f}")
            if ratio > 2.0:
                problems.append(f"{run}: training loss rose x{ratio:.2f} (first vs last {k} updates)")
            elif ratio > 1.3:
                warnings.append(f"{run}: training loss up x{ratio:.2f}; the guard stops it at 2.5x")
            if not complete and not guard and age > 75:
                problems.append(f"{run}: no update for {age:.0f} min")
            if r["update"] >= upe and not any(d.glob("checkpoints/update_*.pt")):
                problems.append(f"{run}: past epoch 1 but no checkpoint on disk")
        elif alive:
            print("    loading / initial evaluation (no update yet)")
        evals = sorted((d / "eval").glob("update_*.json"))
        if evals:
            def overall(p):
                return json.loads(p.read_text())["overall"]
            e0, e1 = overall(evals[0]), overall(evals[-1])
            cells = []
            for mode in ("on", "off", "null"):
                a, b = e0.get(f"{mode}/arm_rmse_rad"), e1.get(f"{mode}/arm_rmse_rad")
                if a is not None and b is not None:
                    cells.append(f"{mode} {a:.4f} -> {b:.4f}")
            print(f"    offline arm RMSE ({evals[0].stem} -> {evals[-1].stem}): " + "   ".join(cells))
            on0, on1 = e0.get("on/arm_rmse_rad"), e1.get("on/arm_rmse_rad")
            if on0 and on1 and len(evals) > 1 and on1 > 1.10 * on0:
                warnings.append(f"{run}: offline on-error rose {on0:.4f} -> {on1:.4f}")
        log = d / "stdout.log"
        if log.exists():
            text = log.read_text(errors="replace").splitlines()
            errors = [line for line in text[-400:] if re.search(r"Traceback|Error|out of memory|Killed", line)
                      and "WARNING" not in line]
            if errors:
                print("    stdout.log errors (last 400 lines):")
                for line in errors[-5:]:
                    print(f"      {line[:170]}")
                if not alive and not complete:
                    problems.append(f"{run}: errors in {log} and no training process")
                else:
                    warnings.append(f"{run}: error lines in {log} (process alive: {alive}; the lane retries up to 3x)")
        if not alive and not complete and not guard and rows:
            base_alive = any(re.search(r"a100_queue_4\.sh (base|ablate)\b", p) for p in procs)
            if not base_alive:
                problems.append(f"{run}: not complete, no training process and its lane is gone")

    # ------------------------------------------------------------------ closed loop
    section("closed loop (watch lane)")
    print(f"  bank summary: {'written ' + str(CL / 'bank' / 'bank_summary.txt') if (CL / 'bank' / 'bank_summary.txt').exists() else 'not yet'}")
    done = sorted(p.name[5:] for p in CLOUT.glob("DONE_*")) if CLOUT.exists() else []
    print(f"  finished: {done or 'none yet'}")
    for p in procs:
        if "online run" in p:
            m = re.search(r"--label (\S+)", p)
            label = m.group(1) if m else "?"
            shard = re.search(r"--shard (\S+)", p)
            label_shown = label + (f" shard {shard.group(1)}" if shard else "")
            n = len(list((CLOUT / label).glob("*/*/seed_*/result.json"))) if (CLOUT / label).exists() else 0
            print(f"  running now: {label_shown}  ({n} episodes of {label} finished, all modes/shards)")
    if (CLOUT / "stages.txt").exists():
        lines = (CLOUT / "stages.txt").read_text(errors="replace").splitlines()
        start = next((i for i, l in enumerate(lines) if "stage reach" in l), None)
        if start is not None:
            for line in lines[start + 1:start + 13]:
                print("  " + line)

    # ------------------------------------------------------------------ GPUs, disk
    section("GPUs (container index: used / free MiB, util)")
    print("  " + sh("nvidia-smi --query-gpu=index,memory.used,memory.free,utilization.gpu --format=csv,noheader").strip().replace("\n", "\n  "))
    section("disk")
    df = sh(f"df -BG --output=avail {O} | tail -n 1").strip().rstrip("G")
    print(f"  free under {O}: {df} GB   (each A2C checkpoint ~12 GB)")
    try:
        if int(df) < 80:
            problems.append(f"only {df} GB free on the output disk")
    except ValueError:
        pass

    print()
    for w in warnings:
        print(f"  note: {w}")
    if problems:
        print("VERDICT: ACTION NEEDED")
        for p in problems:
            print(f"  - {p}")
    else:
        print("VERDICT: OK - nothing to do")


if __name__ == "__main__":
    main()
