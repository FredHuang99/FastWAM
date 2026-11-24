"""Plan v20 readings on the A40 (11-24, Opus; written before any episode of these runs exists). Each applies the reading
registered in scripts/gaas/gaas_queue.txt above the run's line (commit 5c5c660) unchanged. Read-only, CPU. Paired
bootstrap = a1_verdict.paired_ci (10,000 resamples, seed 0, percentile 95 % CI), via deed_verdict.compare / three.
Official seed-42 banks, scenes 1-100, default noise; the pre-set extensions pool the default-noise pairs with the
MWAM_NOISE_SALT=r2 pairs (closed_loop/r2) of the same scenes = 200 pairs, the same rule, when both r2 sides are complete.
  rv3ch2   card 1, described only: rearr_v3c_h2 e30 (closed_loop/rv3c) success 1-100; against rearr_v3c (H100) e30
           (closed_loop/rv3c) paired counts and two-sided sign p (training-level spread); against rearrange_arprop e30
           (closed_loop/e6) paired counts. The failure classes / write delay come from rearr_split.py / rearr_ledger.py.
  swapt    card 3: D = success(swapT_long e60) - success(swapT_arprop_h2 e30), swap_T 1-100 (closed_loop/v20); SESOI
           +0.15 -> TRAINING-LIMITED / NOT TRAINING-LIMITED / UNCERTAIN. Described: e45; swapT_arprop_h2 e30 against
           swapT_arprop (H100) e30 (closed_loop/e6).
  rankv3c  card 4: D = success(ranking_v3a e30, closed_loop/v20) - success(ranking_arprop e30, closed_loop/e6); SESOI
           +0.10 -> TIMELY WRITING HELPS / NO HELP / UNCERTAIN; ceiling: ranking_arprop e30 >= 95 -> non-inferiority,
           margin -0.05 -> NO HARM / HARM / UNCERTAIN. Described: success against 100.
  ar2v3c   card 2: non-inferiority, margin -0.05, swap_blocks 1-100 e30 (closed_loop/v20 against ar2_prop e30,
           closed_loop/g1): CI lower > -0.05 -> NO HARM; CI upper < -0.05 -> HARM; otherwise UNCERTAIN; put_back_block
           the same rule beside it. Described: e10 swap against ar2_prop e10 (closed_loop/lc).
  swapth100 the same question on the H100 class: swapT_long_h100 e60 (closed_loop/v20) - swapT_arprop e30 (H100,
           closed_loop/e6); SESOI +0.15, the same outcomes; reported beside card 3, never pooled with it
  batclk   battery_clock e30 (H100 filler, main-table clock cell, closed_loop/e6), described against battery_ar /
           battery_arprop e30
  presstold card 5: D = success(press_told e30, closed_loop/v20, MWAM_TOLD_COUNTS=1) - success(press_v3c e30,
           closed_loop/e17); SESOI +0.30 -> READING THE TARGET IS THE BOTTLENECK / NOT THE MAIN BOTTLENECK / UNCERTAIN.
           Described: each button's over / right / under (deed_verdict.per_button, D2's definitions); success by N1 + N2
  rankarp  ranking_arprop e30 (main-table cell, closed_loop/e6), described: success; paired counts against ranking_ar e30.
  covnone  cover_none e30 (main-table cell, closed_loop/e6), described: paired counts against cover_ar / cover_arprop e30.
  battmask A2 follow-up (plan v20 2.4c, SHORT MEMORY NEEDED): battery_ar e30, battery_try 1-50, frame 0 masked / the two
           near frames masked (MWAM_HIST_MASK first / near, closed_loop/a2m), against the same 50 scenes unmasked
           (closed_loop/e6). Described only.
A verdict needs all its MAIN scenes finished on both sides (else WAIT). Writes outputs/fullft/V20_<NAME>.json.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v20_verdict.py rv3ch2|swapt|swapth100|rankv3c|ar2v3c|rankarp|covnone|batclk|battmask|presstold
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = Path("/workspace/FastWAM-memory2/outputs/fullft")


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


dv = _module("deed_verdict", "deed_verdict.py")
success, compare, three = dv.success, dv.compare, dv.three


def sign_p(c):
    """Two-sided exact sign test on the discordant pairs of a compare() result."""
    n, k = c["only_new"] + c["only_ref"], min(c["only_new"], c["only_ref"])
    if n == 0:
        return 1.0
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return round(min(1.0, 2 * p), 4)


def pooled(new, ref, order, new_r2, ref_r2):
    """The pre-set extension: default-noise pairs + r2 pairs of the same scenes (200 pairs)."""
    a = {("d", x): v for x, v in new.items()}
    a.update({("r2", x): v for x, v in new_r2.items()})
    b = {("d", x): v for x, v in ref.items()}
    b.update({("r2", x): v for x, v in ref_r2.items()})
    return compare(a, b, [("d", x) for x in order] + [("r2", x) for x in order])


def non_inferior(c, margin=-0.05):
    lo, hi = c["ci95"]
    return "NO HARM" if lo > margin else "HARM" if hi < margin else "UNCERTAIN"


def with_extension(out, c, verdict, rule, task, new_label, new_folder, ref_label, ref_folder, n=100):
    """Applies the registered rule; when it says UNCERTAIN and both r2 sides are complete, the pooled 200 pairs decide."""
    out.update(main=c, verdict=verdict)
    if verdict != "UNCERTAIN":
        return out
    order, ref = success(ref_folder, ref_label, task)
    _, new = success(new_folder, new_label, task)
    _, nr2 = success("r2", new_label, task)
    _, rr2 = success("r2", ref_label, task)
    out["extension"] = {"r2_finished": {new_label: len(nr2), ref_label: len(rr2)}}
    if len(nr2) >= n and len(rr2) >= n:
        e = pooled(new, ref, order, nr2, rr2)
        out["extension"].update(pooled=e, verdict=rule(e))
        out["verdict"] = f"UNCERTAIN at 100 pairs -> {rule(e)} at {e['scenes']} pairs (pre-set extension)"
    else:
        out["extension"]["verdict"] = "WAIT (r2 evaluations: the pre-set extension)"
    return out


def rv3ch2():
    task = "rearrange_blocks"
    order, new = success("rv3c", "rearr_v3c_h2_e30", task)
    _, h100 = success("rv3c", "rearr_v3c_e30", task)
    _, arp = success("e6", "rearrange_arprop_e30", task)
    out = {"run": "card 1 rearr_v3c_h2 (described only)", "finished": {"rearr_v3c_h2_e30": len(new),
           "rearr_v3c_e30": len(h100), "rearrange_arprop_e30": len(arp)}, "success_1_100": sum(new.values())}
    if len(h100) == 100 and len(new) == 100:
        c = compare(new, h100, order)
        out["against_rearr_v3c_h100"] = dict(c, sign_p=sign_p(c))
    if len(arp) == 100 and len(new) == 100:
        out["against_rearrange_arprop"] = compare(new, arp, order)
    out["verdict"] = "DESCRIBED" if len(new) == 100 else f"WAIT ({len(new)} of 100)"
    return out


def swapt():
    task = "swap_T"
    order, ref = success("v20", "swapT_arprop_h2_e30", task)
    _, new = success("v20", "swapT_long_e60", task)
    out = {"run": "card 3 swap_T training length", "sesoi": 0.15,
           "finished": {"swapT_long_e60": len(new), "swapT_arprop_h2_e30": len(ref)}}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
    else:
        c = compare(new, ref, order)
        rule = lambda x: three(x, 0.15, "TRAINING-LIMITED", "NOT TRAINING-LIMITED")   # noqa: E731
        with_extension(out, c, rule(c), rule, task, "swapT_long_e60", "v20", "swapT_arprop_h2_e30", "v20")
    _, e45 = success("v20", "swapT_long_e45", task)
    if e45 and ref:
        out["described_e45"] = compare(e45, ref, order)
    _, h100 = success("e6", "swapT_arprop_e30", task)
    if len(ref) == 100 and len(h100) == 100:
        c = compare(ref, h100, order)
        out["described_h2_vs_h100_e30"] = dict(c, sign_p=sign_p(c))
    return out


def swapth100():
    task = "swap_T"
    order, ref = success("e6", "swapT_arprop_e30", task)
    _, new = success("v20", "swapT_long_h100_e60", task)
    out = {"run": "card 3 on the H100 class (swapT_long_h100)", "sesoi": 0.15,
           "finished": {"swapT_long_h100_e60": len(new), "swapT_arprop_e30": len(ref)}}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
    else:
        c = compare(new, ref, order)
        rule = lambda x: three(x, 0.15, "TRAINING-LIMITED", "NOT TRAINING-LIMITED")   # noqa: E731
        with_extension(out, c, rule(c), rule, task, "swapT_long_h100_e60", "v20", "swapT_arprop_e30", "e6")
    _, e45 = success("v20", "swapT_long_h100_e45", task)
    if e45 and ref:
        out["described_e45"] = compare(e45, ref, order)
    return out


def batclk():
    task = "battery_try"
    order, new = success("e6", "battery_clock_e30", task)
    out = {"run": "main-table cell battery clock (described)", "finished": {"battery_clock_e30": len(new)},
           "success_1_100": sum(new.values())}
    for ref in ("battery_ar_e30", "battery_arprop_e30"):
        _, r = success("e6", ref, task)
        if len(new) == 100 and len(r) == 100:
            out[f"against_{ref}"] = compare(new, r, order)
    out["verdict"] = "DESCRIBED" if len(new) == 100 else f"WAIT ({len(new)} of 100)"
    return out


def presstold():
    task = "press_button"
    order, ref = success("e17", "press_v3c_e30", task)
    _, new = success("v20", "press_told_e30", task)
    out = {"run": "card 5 press_told (diagnostic; never a main-table entry)", "sesoi": 0.30,
           "finished": {"press_told_e30": len(new), "press_v3c_e30": len(ref)}}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
    else:
        c = compare(new, ref, order)
        rule = lambda x: three(x, 0.30, "READING THE TARGET IS THE BOTTLENECK", "NOT THE MAIN BOTTLENECK")   # noqa: E731
        with_extension(out, c, rule(c), rule, task, "press_told_e30", "v20", "press_v3c_e30", "e17")
    try:
        rows_new, rows_ref = dv.press_rows("v20", "press_told_e30"), dv.press_rows("e17", "press_v3c_e30")
        out["described"] = {"press_told_e30": dv.per_button(rows_new), "press_v3c_e30": dv.per_button(rows_ref)}
        by = {}
        for s_, v in rows_new.items():
            c1, c2 = v.get("card_1"), v.get("card_2")
            if c1 is not None and c2 is not None:
                k = int(c1) + int(c2)
                by.setdefault(k, [0, 0])
                by[k][0] += int(bool(new.get(s_)))
                by[k][1] += 1
        out["described"]["success_by_N1_plus_N2"] = {k: f"{a}/{b}" for k, (a, b) in sorted(by.items())}
    except Exception as e:                                                     # noqa: BLE001
        out["described_error"] = f"{type(e).__name__}: {e}"
    for tag in ("e10", "e20"):
        _, x = success("v20", f"press_told_{tag}", task)
        if x:
            out[f"described_{tag}"] = compare(x, ref, order)
    return out


def rankv3c():
    task = "blocks_ranking_try"
    order, ref = success("e6", "ranking_arprop_e30", task)
    _, new = success("v20", "ranking_v3a_e30", task)
    out = {"run": "card 4 ranking timely writer (ranking_v3a, user 18:32 option b)", "finished": {"ranking_v3a_e30": len(new), "ranking_arprop_e30": len(ref)}}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
        return out
    c = compare(new, ref, order)
    if c["ref"] >= 95:
        out["ceiling"] = f"ranking_arprop e30 {c['ref']}/100 >= 95: no verdict on HELPS; non-inferiority, margin -0.05"
        with_extension(out, c, non_inferior(c), non_inferior, task, "ranking_v3a_e30", "v20", "ranking_arprop_e30", "e6")
    else:
        out["sesoi"] = 0.10
        rule = lambda x: three(x, 0.10, "TIMELY WRITING HELPS", "NO HELP")              # noqa: E731
        with_extension(out, c, rule(c), rule, task, "ranking_v3a_e30", "v20", "ranking_arprop_e30", "e6")
    out["success_vs_100"] = f"{c['new']} vs 100 (pure-WAM best, self-reported)"
    return out


def ar2v3c():
    out = {"run": "card 2 two-task timely writer (non-inferiority, margin -0.05)", "finished": {}}
    verdicts = []
    for task in ("swap_blocks", "put_back_block"):
        order, ref = success("g1", "ar2_prop_e30", task)
        _, new = success("v20", "ar2_v3c_e30", task)
        r = {"finished": {"ar2_v3c_e30": len(new), "ar2_prop_e30": len(ref)}}
        if len(new) < 100 or len(ref) < 100:
            r["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
        else:
            c = compare(new, ref, order)
            with_extension(r, c, non_inferior(c), non_inferior, task, "ar2_v3c_e30", "v20", "ar2_prop_e30", "g1")
        out[task] = r
        verdicts.append(f"{task}: {r['verdict']}")
    order, ref10 = success("lc", "ar2_prop_e10", "swap_blocks")
    _, new10 = success("v20", "ar2_v3c_e10", "swap_blocks")
    if new10 and ref10:
        out["described_e10_swap"] = compare(new10, ref10, order)
    out["verdict"] = "; ".join(verdicts)
    return out


def rankarp():
    task = "blocks_ranking_try"
    order, new = success("e6", "ranking_arprop_e30", task)
    _, ar = success("e6", "ranking_ar_e30", task)
    out = {"run": "main-table cell ranking body record (described)", "finished": {"ranking_arprop_e30": len(new),
           "ranking_ar_e30": len(ar)}, "success_1_100": sum(new.values())}
    if len(new) == 100 and len(ar) == 100:
        c = compare(new, ar, order)
        out["against_ranking_ar"] = dict(c, sign_p=sign_p(c))
        if c["new"] < c["ref"]:
            out["plan_v20_6_back_to_fable"] = f"body record {c['new']} below three-frame {c['ref']} (plan v20 section 6)"
    out["verdict"] = "DESCRIBED" if len(new) == 100 else f"WAIT ({len(new)} of 100)"
    return out


def covnone():
    task = "cover_blocks"
    order, new = success("e6", "cover_none_e30", task)
    out = {"run": "main-table cell cover without history (described)", "finished": {"cover_none_e30": len(new)},
           "success_1_100": sum(new.values())}
    for ref in ("cover_ar_e30", "cover_arprop_e30"):
        _, r = success("e6", ref, task)
        if len(new) == 100 and len(r) == 100:
            out[f"against_{ref}"] = compare(new, r, order)
    out["verdict"] = "DESCRIBED" if len(new) == 100 else f"WAIT ({len(new)} of 100)"
    return out


def battmask():
    task = "battery_try"
    order, ref = success("e6", "battery_ar_e30", task)
    order = order[:50]
    ref = {x: v for x, v in ref.items() if x in order}
    out = {"run": "A2 follow-up: which history frame battery_ar uses (described)", "unmasked_1_50": sum(ref.values())}
    for mask in ("first", "near"):
        _, m = success("a2m", f"battery_ar_e30_mask{mask}", task)
        m = {x: v for x, v in m.items() if x in order}
        out[f"mask_{mask}"] = {"finished": len(m), **(compare(m, ref, order) if len(m) == 50 else {})}
    out["verdict"] = "DESCRIBED" if all(out[f"mask_{k}"]["finished"] == 50 for k in ("first", "near")) else "WAIT"
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    fns = {"rv3ch2": rv3ch2, "swapt": swapt, "swapth100": swapth100, "batclk": batclk, "rankv3c": rankv3c, "ar2v3c": ar2v3c, "rankarp": rankarp,
           "covnone": covnone, "presstold": presstold, "battmask": battmask}
    if name not in fns:
        print(__doc__)
        return 2
    out = fns[name]()
    print(json.dumps(out))
    (F / f"V20_{name.upper()}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"V20 {name.upper()}: {out['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
