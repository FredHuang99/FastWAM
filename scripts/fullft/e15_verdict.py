"""Plan v14 E15 R-test verdict (registered by Fable 11-18 in plan v14 section 3, approved by the user 18:33; this script
written 11-19 19:40 BJ, before any closed-loop result of battery_count, which trains on the H100). Read-only. A40.
battery_count = battery_arprop's setting + the countable code of E4 (history.ordinal=16); only this changes.
battery_try scenes 1-100, closed_loop/e6: battery_count_e30 paired with battery_arprop_e30 (same machine and scenes).
E2_PREDICTIONS_REGISTERED.txt states no hit rule for rule R (checked 11-19), so plan v14's reading applies:
  count >= ledger + 10/100 with sign p < 0.05 -> R HIT; |count - ledger| <= 5/100 -> R MISS; otherwise UNDECIDED.
  Floors: battery_arprop <= 90/100 (not saturated) and at least one of the two >= 30/100; both >= 95 finished.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e15_verdict.py      Writes outputs/fullft/E15_VERDICT.json.
"""
from __future__ import annotations

import v15_common as vc  # noqa: E402


def main():
    task = "battery_try"
    s100 = vc.seeds(task, 100)
    count = vc.results(vc.O / "e6", "battery_count_e30", task, s100)
    ledger = vc.results(vc.O / "e6", "battery_arprop_e30", task, s100)
    n, c, l, oc, ol, p = vc.paired(count, ledger)
    print(f"E15 battery 1-100 on {n} common scenes: count {c}, ledger {l}; only count {oc}, only ledger {ol}, p {p:.4f}")
    if len(count) < 95 or len(ledger) < 95:
        word = f"WAIT (finished: count {len(count)}, ledger {len(ledger)})"
    elif l > 90:
        word = f"NO VERDICT (floor: ledger {l}/100 > 90, saturated)"
    elif max(c, l) < 30:
        word = "NO VERDICT (floor: both < 30/100)"
    elif c - l >= 10 and p < 0.05:
        word = "R HIT"
    elif abs(c - l) <= 5:
        word = "R MISS"
    else:
        word = "UNDECIDED"
    print(f"E15 VERDICT: {word}")
    vc.write("E15_VERDICT.json", {"verdict": word, "n": n, "count": c, "ledger": l, "only_count": oc,
                                  "only_ledger": ol, "p": p})


if __name__ == "__main__":
    main()
