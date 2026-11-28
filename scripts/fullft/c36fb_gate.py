#!/usr/bin/env python3
"""Card 36 A100 fallback gate. User 11-29 00:5x (A40 GPUs 4-7 'GPU requires reset', no sudo there, GPUs 0-3 taken by
other users): "中午 12 点没修好就挪" -- if the A40 is still not repaired at 11-29 12:00 (+0800), card 36's verdict
(swapT_ow e30 against swapT_arprop_h2 e30, swap_T 1-100) is evaluated on the A100 with BOTH arms on the A100
(A100 class; v22_verdict.py c36_a100). Written 11-29 01:06 (Opus) before any A100 episode of these runs.
Runs on the A100 (pool5 cpu lane). Sleeps until 11-29 12:00 +0800 (a line every 10 minutes, so the pool does not take
it for stalled), then reads the A40's latest results snapshot (git fetch origin results-a40):
  repaired      the snapshot is at most 90 minutes old and every GPU line of snap/report/gpus.txt has a readable
                utilization (no [N/A] / 'requires reset')  -> exit 3: the A100 tasks stay blocked (requires_pass);
                card 36 is judged on the A40 as registered
  not repaired  otherwise (also: no snapshot readable within 30 minutes of trying) -> exit 0: the fallback runs
Writes outputs/fullft/C36FB_GATE.json (fallback true/false, why, the snapshot time and GPU lines); v22_gate.py reads
it: after a fallback, card 36's verdict is the A100 one (the A40's, if it runs later, is described only).
  python3 scripts/fullft/c36fb_gate.py [--now]     (--now: skip the wait; for a check by hand)
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

R = Path(__file__).resolve().parents[2]
OUT = R / "outputs/fullft/C36FB_GATE.json"
REF = "refs/remotes/origin/results-a40"
BJ = timezone(timedelta(hours=8))
AT = datetime(2026, 11, 29, 12, 0, tzinfo=BJ)
FRESH_S = 90 * 60


def say(msg):
    print(f"[c36fb-gate] {datetime.now(BJ):%F %T} {msg}", flush=True)


def git(*a):
    return subprocess.run(["git", "-c", "safe.directory=*", "-C", str(R), *a], capture_output=True, text=True,
                          timeout=300)


def a40_state():
    """(repaired: bool, why, snapshot time, gpu lines) or None when no snapshot can be read."""
    if git("fetch", "-q", "origin", f"+results-a40:{REF}").returncode != 0:
        return None
    t = git("log", "-1", "--format=%ct", REF)
    g = git("show", f"{REF}:snap/report/gpus.txt")
    if t.returncode != 0 or g.returncode != 0 or not t.stdout.strip():
        return None
    when = int(t.stdout.strip())
    rows = []
    for line in g.stdout.splitlines():
        p = [x.strip() for x in line.split(",")]
        if len(p) >= 5 and p[0].isdigit():
            rows.append(p)
    age = time.time() - when
    sick = [p[0] for p in rows if not p[4].replace("%", "").strip().isdigit()]
    stamp = datetime.fromtimestamp(when, BJ).strftime("%F %T")
    if age > FRESH_S:
        return False, f"the A40's latest snapshot is {age / 60:.0f} min old (> 90)", stamp, [", ".join(p) for p in rows]
    if not rows:
        return False, "no GPU line in the A40's gpus.txt", stamp, []
    if sick:
        return False, f"A40 GPUs {sick} still have no readable utilization", stamp, [", ".join(p) for p in rows]
    return True, "every A40 GPU reports a readable utilization", stamp, [", ".join(p) for p in rows]


def main():
    if "--now" not in sys.argv:
        last = 0.0
        while datetime.now(BJ) < AT:
            if time.time() - last >= 600:
                say(f"waiting until {AT:%F %H:%M} +0800 ({(AT - datetime.now(BJ)).total_seconds() / 3600:.1f} h left)")
                last = time.time()
            time.sleep(30)
    state, t0 = None, time.time()
    while state is None and time.time() - t0 < 1800:
        state = a40_state()
        if state is None:
            say("the A40's results snapshot cannot be read yet; retry in 2 min")
            time.sleep(120)
    if state is None:
        repaired, why, stamp, rows = False, "no A40 snapshot readable in 30 minutes", None, []
    else:
        repaired, why, stamp, rows = state
    rep = {"card": 36, "rule": "user 11-29: if the A40 is not repaired at 11-29 12:00, card 36 on the A100 (both arms)",
           "checked": datetime.now(BJ).strftime("%F %T"), "fallback": not repaired, "why": why,
           "a40_snapshot": stamp, "a40_gpus": rows}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, indent=1, ensure_ascii=False) + "\n")
    say(f"{why} -> {'A40 repaired: no fallback (exit 3)' if repaired else 'FALLBACK: card 36 on the A100 (exit 0)'}")
    return 3 if repaired else 0


if __name__ == "__main__":
    sys.exit(main())
