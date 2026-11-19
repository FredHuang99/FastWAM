"""Plan v15 E24 CLOCK-press verdict (registered by Fable 11-19 noon in plan v15 section 3, copied into
scripts/gaas/gaas_queue.txt at 13:40; this script written 11-19 19:45 BJ, before press_clock exists: it trains on the
new H200 from ~11-21 08:30). Read-only. A40, the E17 press bank (closed_loop/e17 for the no-stress runs).
  --select  P-SEL on scenes 1-50 for press_clock (e10 / e20 / e30) and press_count (e10 / e20 / e30), as E14
            (e14_verdict_a40.pick: most successes; ties -> more first counts right; ties -> later epoch; >= 48
            finished); held-out 51-100 paired (same machine):
              clock >= press_count + 8/50 with sign p < 0.05 -> TIME INDEX COUNTS BETTER;
              press_count >= clock + 8/50 with p < 0.05 -> EVENT INDEX COUNTS BETTER; |diff| <= 4 -> SAME;
              otherwise PARTIAL. Floor: both >= 48/50 finished on 51-100.
            Writes the picks as outputs/fullft/exports/press_clock_sel/export_sel.pt and
            .../press_count_sel/export_sel.pt (symlinks) for the stress cards.
  --stress  pause 64 frames, visible vs hidden, scenes 51-100, closed_loop/e24, labels press_clock_sel_p64_vis / _hid
            and press_count_sel_p64_vis / _hid. Trigger (inject.TRIGGERS, fixed 11-19 19:10 before any clock press
            result): once per episode, when the first press is confirmed (the pressing arm has risen 1.5 cm after it),
            so at least one press is still to do. E1's validity (no object moved > 1 cm, no counter changed).
              clock Delta <= -8/50 with p < 0.05 -> CLOCK READ ON PRESS; Delta >= -5/50 -> NOT READ AT 64;
              otherwise UNDECIDED. Floor: valid pairs >= 45, hidden >= 15/50 (else no verdict word; the first-count
              error distribution vis vs hid is reported). press_count's Delta beside it.
            Registered consequence: the clock not below any ledger version (P-SEL picks of press_arprop, press_fast,
            press_count, press_v3c on 51-100) AND NOT READ AT 64 -> SWITCH TO FABLE.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e24_verdict.py --select | --stress
Writes outputs/fullft/E24_VERDICT.json (--select) / E24_STRESS.json (--stress).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter

import v15_common as vc  # noqa: E402

e14 = vc.module("e14_verdict_a40", "e14_verdict_a40.py")
pp = e14.pp
EX = vc.F / "exports"
LEDGERS = ("press_arprop", "press_fast", "press_count", "press_v3c")


def held(st, held_seeds):
    return {str(s): bool(v.get("success")) for s, v in st.items() if str(s) in held_seeds}


def select():
    seeds = vc.e1.seeds_of("press_button", 100) or []
    first, hold = {str(s) for s in seeds[:50]}, {str(s) for s in seeds[50:]}
    clock, count = e14.pick("press_clock", first), e14.pick("press_count", first)
    out = {"clock": clock and f"press_clock_{clock[1]}", "count": count and f"press_count_{count[1]}"}
    if not clock or not count:
        out["verdict"] = "NO READING (an epoch pick is missing: < 48 finished on 1-50)"
    else:
        A, B = held(clock[2], hold), held(count[2], hold)
        common = sorted(set(A) & set(B))
        if len(A) < 48 or len(B) < 48:
            out["verdict"] = f"NO READING (finished on 51-100: {len(A)} / {len(B)} < 48)"
        else:
            sa, sb = sum(A[s] for s in common), sum(B[s] for s in common)
            oa = sum(A[s] and not B[s] for s in common)
            ob = sum(B[s] and not A[s] for s in common)
            p = pp.sign_p(oa, ob)
            word = ("TIME INDEX COUNTS BETTER" if sa - sb >= 8 and p < 0.05 else
                    "EVENT INDEX COUNTS BETTER" if sb - sa >= 8 and p < 0.05 else
                    "SAME" if abs(sa - sb) <= 4 else "PARTIAL")
            out.update(n=len(common), clock_success=sa, count_success=sb, only_clock=oa, only_count=ob, p=p, verdict=word)
        for run, pick in (("press_clock", clock), ("press_count", count)):
            src = EX / f"{run}_{pick[1]}" / f"export_{pick[1]}.pt"
            dst = EX / f"{run}_sel"
            dst.mkdir(parents=True, exist_ok=True)
            link = dst / "export_sel.pt"
            if link.is_symlink() or link.exists():
                link.unlink()
            link.symlink_to(src)
            out[f"{run}_sel"] = str(src)
    print(f"E24 (A40, no stress): {out}")
    vc.write("E24_VERDICT.json", out)


def first_errors(label, seed_strs):
    st = pp.stages("e24", label)
    return dict(Counter(v.get("n1_error") for s, v in st.items() if str(s) in seed_strs))


def stress():
    sel = json.loads((vc.F / "E24_VERDICT.json").read_text())
    seeds = vc.seeds("press_button", 100, start=50)
    e24 = vc.O / "e24"
    clock = vc.stress_cell(e24, "press_clock_sel_p64_vis", "press_clock_sel_p64_hid", "press_button", seeds, 15)
    count = vc.stress_cell(e24, "press_count_sel_p64_vis", "press_count_sel_p64_hid", "press_button", seeds, 15)
    word = {"HURT": "CLOCK READ ON PRESS", "NOT HURT": "NOT READ AT 64", "BETWEEN": "UNDECIDED"}.get(
        clock["state"], f"NO VERDICT ({clock['state']})")
    hs = {str(s) for s in seeds}
    errors = {lab: first_errors(lab, hs) for lab in ("press_clock_sel_p64_vis", "press_clock_sel_p64_hid")}
    first = {str(s) for s in (vc.e1.seeds_of("press_button", 100) or [])[:50]}
    ledgers = {}
    for run in LEDGERS:
        pk = e14.pick(run, first)
        if pk:
            ledgers[f"{run}_{pk[1]}"] = sum(held(pk[2], hs).values())
    cs = sel.get("clock_success")
    not_below = cs is not None and bool(ledgers) and all(cs >= v for v in ledgers.values())
    out = {"verdict": word, "clock": clock, "press_count": count, "first_count_errors": errors,
           "ledger_picks_51_100": ledgers, "clock_51_100": cs,
           "switch_to_fable": bool(not_below and word == "NOT READ AT 64")}
    print(f"E24 STRESS VERDICT: {word}; press_count Delta {count['delta']:+d}; ledger picks on 51-100 {ledgers}; "
          f"clock {cs}; switch to Fable: {out['switch_to_fable']}")
    vc.write("E24_STRESS.json", out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--select", action="store_true")
    g.add_argument("--stress", action="store_true")
    a = ap.parse_args()
    select() if a.select else stress()


if __name__ == "__main__":
    main()
