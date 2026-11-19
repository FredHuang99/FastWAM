"""Plan v14 E16 C-test (rearrange) and plan v15 E16b (swap_T) verdicts: the single-task clock arm under a pause.
Registered by Fable (plan v14 section 3 E16, 11-18, approved 18:33; plan v15 section 3 E16b, 11-19, user 13:21 / 13:45);
this script written 11-19 19:35 BJ, before any closed-loop result of rearrange_clock / swapT_clock (both training on the
H100). Read-only. A40.
  --task rearrange_blocks   clock rearrange_clock_e30; AR rearrange_ar_e30; ledger rearrange_arprop_e30
  --task swap_T             clock swapT_clock_e30;     AR swapT_ar_e30;     ledger swapT_arprop_e30
Cells: no stress 1-100 (closed_loop/e16 for the clock, closed_loop/e6 for AR / ledger); pause 64 frames visible /
hidden 1-50 (closed_loop/e16, labels <model>_p64_vis / _hid; E1's validity; trigger inject.TRIGGERS: rearrange after
the first release at the next apex, swap_T after the second release at the next apex).
Registered reading (the clock's 64-frame cell): Delta <= -8/50 with sign p < 0.05 -> C HIT; Delta >= -5/50 -> C MISS;
otherwise UNDECIDED. Floors: clock no stress >= 70/100; valid pairs >= 45; hidden arm >= 35/50.
  rearrange (E16): counts for rule C of the audit (E2: rearrange cur "clock EARLY UNDER PAUSE").
  swap_T (E16b): the same words, descriptive only (E2 gives no clock prediction for swap_T); not counted for the audit.
Reported only: rearrange 256-frame clock cell; AR and ledger at 64 frames (rearrange); no-stress clock vs ledger vs AR.
G3 (scripts/fullft/G3_GATE_REGISTERED.txt): C HIT with the ledger's 64-frame Delta >= -5/50 counts for the event index.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e16_verdict.py --task rearrange_blocks|swap_T
Writes outputs/fullft/E16_VERDICT_<task>.json.
"""
from __future__ import annotations

import argparse

import v15_common as vc  # noqa: E402  (same folder)

NAMES = {"rearrange_blocks": ("rearrange_clock_e30", "rearrange_ar_e30", "rearrange_arprop_e30"),
         "swap_T": ("swapT_clock_e30", "swapT_ar_e30", "swapT_arprop_e30")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", choices=sorted(NAMES), required=True)
    task = ap.parse_args().task
    clock, ar, ledger = NAMES[task]
    s100, s50 = vc.seeds(task, 100), vc.seeds(task, 50)
    e16, e6 = vc.O / "e16", vc.O / "e6"
    ns = {"clock": vc.results(e16, clock, task, s100), "AR": vc.results(e6, ar, task, s100),
          "ledger": vc.results(e6, ledger, task, s100)}
    out = {"task": task, "no_stress": {k: f"{sum(v.values())}/{len(v)}" for k, v in ns.items()}}
    for k in ("AR", "ledger"):
        n, a, b, oa, ob, p = vc.paired(ns["clock"], ns[k])
        out["no_stress"][f"clock_vs_{k}"] = {"n": n, "clock": a, k: b, "only_clock": oa, f"only_{k}": ob, "p": p}
    print(f"E16 {task} no stress 1-100: {out['no_stress']}")
    cells = {"clock_p64": vc.stress_cell(e16, f"{clock}_p64_vis", f"{clock}_p64_hid", task, s50, 35)}
    if task == "rearrange_blocks":
        cells["clock_p256"] = vc.stress_cell(e16, f"{clock}_p256_vis", f"{clock}_p256_hid", task, s50, 35)
        cells["AR_p64"] = vc.stress_cell(e16, f"{ar}_p64_vis", f"{ar}_p64_hid", task, s50, 0)
        cells["ledger_p64"] = vc.stress_cell(e16, f"{ledger}_p64_vis", f"{ledger}_p64_hid", task, s50, 0)
    out["cells"] = cells
    c = cells["clock_p64"]
    if len(ns["clock"]) < 95:
        word = "WAIT (clock no-stress run not finished)"
    elif sum(ns["clock"].values()) < 70:
        word = f"NO VERDICT (floor: clock no stress {sum(ns['clock'].values())}/100 < 70)"
    elif c["state"] in ("WAIT", "FLOOR NOT MET"):
        word = f"NO VERDICT ({c['state']})" if c["state"] != "WAIT" else "WAIT"
    elif c["state"] == "HURT":
        word = "C HIT"
    elif c["state"] == "NOT HURT":
        word = "C MISS"
    else:
        word = "UNDECIDED"
    out["verdict"] = word
    out["audit"] = "rule C (rearrange cur)" if task == "rearrange_blocks" else "descriptive only (no E2 prediction)"
    if task == "rearrange_blocks" and word == "C HIT":
        lg = cells["ledger_p64"]
        out["g3_event_index"] = lg["state"] not in ("WAIT",) and lg["delta"] >= -5
    print(f"E16 VERDICT ({task}): {word}; {out['audit']}")
    vc.write(f"E16_VERDICT_{task}.json", out)


if __name__ == "__main__":
    main()
