"""LAT-T reading (11-16 night, Opus; read-only): does the press ledger model count better when the ledger shows a
press sooner? Test-time only: the trained models are unchanged; only the session's copy of the ledger timing / event
thresholds is (online.effective_rule: MWAM_LEDGER_LAG, MWAM_EVENT_DELTA, MWAM_EVENT_MIN_PATH). Same scenes (1-50),
same diffusion noise seeds as the reference runs in closed_loop/g1, so every difference comes from the ledger timing.

Background (audit 11-16): over-presses of e20 start about 16 frames after the last correct press, and a press shows
up in the ledger about 19 frames after it registers (rule A confirmation + write lag 4 + next decision). Reference
first-count errors on scenes 1-50: e20 right 28, under by one 1, over 21 (replicate: 27, 0, 23); e30 right 10
(replicate 8), with 34 of 73 over-press phases missing a shallow stroke the detector did not record.

Pre-registered readings (written 11-16 19:55 BJ, before any of these runs):
  e20 arms (T0 = lag 0 only; T1 = lag 0 + the sweep's thresholds), against g1:press_arprop_e20:
    IMPLICIT  first count under by one >= 8/50: the model learned to add the press the ledger does not show yet,
              so a timely ledger makes it stop one press early (a retrain with a timely ledger would remove the guess)
    WAITS     first count right >= 35/50 and under by one <= 4/50: it presses until the press shows; the delay
              itself causes the over-presses (a timely ledger fixes them even without retraining)
    NEITHER   otherwise
  e30 arm (T1 thresholds, or lag 0 only when the sweep kept rule A), against g1:press_arprop_e30:
    RECORDING EXPLAINS E30   first count right >= 20/50 (recording the shallow strokes restores counting)
    NOT RECORDING            first count right <= 13/50
    PARTIAL                  in between
  floor: >= 48 finished episodes in both runs of a pair, else NO READING. All other numbers are descriptive.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/lat_verdict.py \
      e20:press_arprop_e20_lag0 e20:press_arprop_e20_fast e30:press_arprop_e30_fast
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"
ALIGN = R / "outputs/fullft/align"
REF = {"e20": "press_arprop_e20", "e30": "press_arprop_e30"}


def stages(folder: str, label: str) -> dict:
    out = ALIGN / f"press_{folder}_{label}_stages.json"
    ALIGN.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(R / "scripts/memory_v2/migrate/export_stages.py"), "--label", label, "--mode",
                    "on", "--folders", str(O / "closed_loop" / folder), "--out", str(out)],
                   check=True, stdout=subprocess.DEVNULL, cwd=str(R))
    return json.loads(out.read_text())["episodes"].get("press_button", {})


def sign_p(a: int, b: int) -> float:
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, k) for k in range(min(a, b) + 1)) / 2 ** n)


def numbers(d: dict) -> dict:
    e1 = [v.get("n1_error") for v in d.values()]
    return {"n": len(d), "success": sum(bool(v.get("success")) for v in d.values()),
            "first_right": sum(x == 0 for x in e1), "first_under1": sum(x == -1 for x in e1),
            "first_under": sum(isinstance(x, int) and x < 0 for x in e1),
            "first_over1": sum(x == 1 for x in e1), "first_over2plus": sum(isinstance(x, int) and x >= 2 for x in e1),
            "second_right": sum(bool(v.get("n2_correct")) for v in d.values())}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("arms", nargs="+", help="EPOCH:LABEL (label in closed_loop/lat; EPOCH e20 | e30 = the reference)")
    ap.add_argument("--folder", default="lat")
    args = ap.parse_args()
    report = {}
    for arm in args.arms:
        epoch, label = arm.split(":", 1)
        ref, new = stages("g1", REF[epoch]), stages(args.folder, label)
        a, b = numbers(new), numbers(ref)
        common = sorted(set(new) & set(ref))
        only_new = sum(bool(new[s].get("n1_correct")) and not ref[s].get("n1_correct") for s in common)
        only_ref = sum(bool(ref[s].get("n1_correct")) and not new[s].get("n1_correct") for s in common)
        if a["n"] < 48 or b["n"] < 48:
            reading = f"NO READING (finished {a['n']} / {b['n']} < 48)"
        elif epoch == "e20":
            if a["first_under1"] >= 8:
                reading = "IMPLICIT"
            elif a["first_right"] >= 35 and a["first_under1"] <= 4:
                reading = "WAITS"
            else:
                reading = "NEITHER"
        else:
            reading = ("RECORDING EXPLAINS E30" if a["first_right"] >= 20 else
                       "NOT RECORDING" if a["first_right"] <= 13 else "PARTIAL")
        report[label] = {"reference": REF[epoch], "new": a, "ref": b, "paired_first": [only_new, only_ref],
                         "sign_p": round(sign_p(only_new, only_ref), 4), "reading": reading}
        print(f"== {label} vs g1:{REF[epoch]}: success {a['success']} vs {b['success']}; first right {a['first_right']} vs "
              f"{b['first_right']} (only new {only_new}, only reference {only_ref}, sign p {sign_p(only_new, only_ref):.3f}); "
              f"first under by one {a['first_under1']} vs {b['first_under1']}; over by one {a['first_over1']} vs "
              f"{b['first_over1']}; over by >= 2 {a['first_over2plus']} vs {b['first_over2plus']}; second right "
              f"{a['second_right']} vs {b['second_right']}")
        print(f"   READING {label}: {reading}")
    out = R / "outputs/fullft/LAT_VERDICT.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
