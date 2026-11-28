#!/usr/bin/env python3
"""Plan v22 (Fable, rev. 1) decision tree as go tests (v22b part 3 section 3, written 11-28 16:20 by Opus before any of
these results exists). Exit 0 = the gate is open (the run may start), 1 = closed. Parses the A40 verdict JSONs with
json (never grep). Where they come from: on the A40 its own outputs/fullft; anywhere else the A40's results branch
(git fetch origin +results-a40, then `git show <ref>:snap/fullft/<file>`), refreshed at most every 10 minutes.

  c37     card 37 (swapT_joint3_ow): card 9b's swap_T verdict is CO-TRAINING HELPS (after the pre-set extension, if
          any) AND card 36's seed-17 run beat 39 by >= 10 or read RELEASE WEIGHTING HELPS (V22_C36 card37_condition_two)
  c35     card 35 (swapT_joint3_s18): card 9b CO-TRAINING HELPS AND V22_C36 has a final verdict with
          card37_condition_two false (card 37 does not open)
  c27s17  card 27's seed-17 continuation: V22_C27 early_stop says "train" (seed 18 gained >= +0.10 from e30 to e60)
  c27bs17 the same for card 27b (the H100-class pair; V22_C27B.json)
  c32     card 32 (rearr_joint3): card 9b CO-TRAINING HELPS AND diagnostic 7(a) says most of rearr_pw_s18's "never
          pressed" episodes stopped above the press depth (DIAG_V22_DIAG7A.json majority_above) AND card 27 has not read
          TRAINING-LIMITED (V22_C27, if it exists)
  python3 scripts/fullft/v22_gate.py <gate> [--why]
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

R = Path(__file__).resolve().parents[2]
LOCAL = R / "outputs/fullft"
REF = "refs/remotes/origin/results-a40"
STAMP = R / "outputs/fullft/.v22_gate_fetch"


def _git(*a):
    return subprocess.run(["git", "-c", "safe.directory=*", "-C", str(R), *a], capture_output=True, text=True,
                          timeout=300)


def a40_json(name):
    """The A40's verdict JSON `name`, or None. On the A40 itself the local file wins."""
    if (LOCAL / name).exists() and (LOCAL / name).stat().st_size > 0:      # on the A40 (only it writes these files)
        return json.loads((LOCAL / name).read_text())
    if not STAMP.exists() or time.time() - STAMP.stat().st_mtime > 600:
        _git("fetch", "-q", "origin", f"+results-a40:{REF}")
        STAMP.parent.mkdir(parents=True, exist_ok=True)
        STAMP.touch()
    r = _git("show", f"{REF}:snap/fullft/{name}")
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def final(word_text):
    """'UNCERTAIN at 100 pairs -> X at 200 pairs (pre-set extension)' -> 'X'; 'X' -> 'X'."""
    t = word_text.split("->")[-1].strip()
    return t.split(" at ")[0].strip()


def joint3_helps():
    j = a40_json("V20_JOINT3.json")
    if not j:
        return False, "V20_JOINT3.json not there"
    sw = [p for p in j.get("verdict", "").split("; ") if p.startswith("swap_T: ")]
    v = final(sw[0][len("swap_T: "):]) if sw else ""
    return v == "CO-TRAINING HELPS", f"card 9b swap_T: {v or j.get('verdict')}"


def c36_two():
    j = a40_json("V22_C36.json")
    if not j or "early_stop" not in j:
        return None, "V22_C36 not final"
    return bool(j.get("card37_condition_two")), f"card 36 condition two {j.get('card37_condition_two')} ({j.get('verdict')})"


def gate(name):
    if name == "c37":
        a, wa = joint3_helps()
        b, wb = c36_two()
        return bool(a and b), f"{wa}; {wb}"
    if name == "c35":
        a, wa = joint3_helps()
        b, wb = c36_two()
        return bool(a and b is False), f"{wa}; {wb}"
    if name in ("c27s17", "c27bs17"):        # 27b (11-28): the same early stop on the H100-class pair (V22_C27B)
        j = a40_json("V22_C27.json" if name == "c27s17" else "V22_C27B.json")
        es = (j or {}).get("early_stop") or {}
        return es.get("seed17") == "train", f"card {name[1:-3]} early stop: {es or 'not there'}"
    if name == "c32":
        a, wa = joint3_helps()
        d = a40_json("DIAG_V22_DIAG7A.json") or {}
        b = bool(d.get("majority_above"))
        c27 = a40_json("V22_C27.json") or {}
        c = final(c27.get("verdict", "")) != "TRAINING-LIMITED"
        return bool(a and b and c), f"{wa}; diag 7(a) majority_above {d.get('majority_above')}; card 27 {c27.get('verdict', 'not there')}"
    raise SystemExit(f"unknown gate {name}")


if __name__ == "__main__":
    ok, why = gate(sys.argv[1])
    if "--why" in sys.argv:
        print(f"v22 gate {sys.argv[1]}: {'OPEN' if ok else 'closed'} ({why})")
    sys.exit(0 if ok else 1)
