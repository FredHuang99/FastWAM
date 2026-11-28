#!/usr/bin/env python3
"""Plan v22 (Fable, rev. 1) verdicts, written 11-28 17:40 (Opus) before any episode of these runs; the readings are
registered above the queue lines (gaas_queue.txt / h200_queue.txt / h100_queue.txt, commit c3787d8). A40, official
seed-42 banks, default noise; new runs' episodes in closed_loop/v22 (r2 noise in closed_loop/r2).
  c36   card 36: D = success(swapT_ow e30) - success(swapT_arprop_h2 e30, closed_loop/v20), swap_T 1-100; SESOI +0.15:
        CI lower > +0.15 -> RELEASE WEIGHTING HELPS; CI upper < +0.15 -> NO HELP; otherwise UNCERTAIN (pre-set
        extension: r2, 200 pairs, the same rule). Early stop (written before the run): success(swapT_ow e30) - 39 < 5 ->
        the seed-18 run is not trained. Described: swapT_ow_s18 e30 (main-table cell = mean of the two seeds); e10 / e20.
  c36b  card 36b: D = success(swapT_ar_ow e30) - success(swapT_ar e30, closed_loop/e6), swap_T 1-100; SESOI +0.15:
        RELEASE WEIGHTING HELPS (NO RECORD) / NO HELP / UNCERTAIN (same extension). Described: swapT_ar_ow_s18 e30.
Each verdict is about these two checkpoints (plan v21 5.5).
  c31   card 31 (press_cd, 11-28 18:40, before any run): see c31() -- COMPARISON IS THE BOTTLENECK / NOT THE COMPARISON
  python3 scripts/fullft/v22_verdict.py c36 | c36b | c31   -> outputs/fullft/V22_C36.json / V22_C36B.json / V22_C31.json
  python3 scripts/fullft/v22_verdict.py gate c36 UNCERTAIN   -> exit 0 if V22_C36.json's verdict starts with UNCERTAIN
        (100 pairs), else exit 3: releases the pre-set r2 extension tasks on the A40 through requires_pass
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = Path("/workspace/FastWAM-memory2/outputs/fullft")


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v20 = _module("v20_verdict", "v20_verdict.py")
success, compare, three, with_extension = v20.success, v20.compare, v20.three, v20.with_extension


def _main_rule(out, task, new_label, new_folder, ref_label, ref_folder, sesoi, yes, no):
    order, ref = success(ref_folder, ref_label, task)
    _, new = success(new_folder, new_label, task)
    out["finished"] = {new_label: len(new), ref_label: len(ref)}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
        return out, order, new, ref
    c = compare(new, ref, order)
    rule = lambda x: three(x, sesoi, yes, no)   # noqa: E731
    with_extension(out, c, rule(c), rule, task, new_label, new_folder, ref_label, ref_folder)
    return out, order, new, ref


def _described(out, task, order, ref, labels):
    for lab, folder in labels:
        _, s = success(folder, lab, task)
        if s:
            out.setdefault("described", {})[lab] = dict(compare(s, ref, order), success=sum(s.values()), finished=len(s))


def c36():
    task = "swap_T"
    out = {"run": "card 36 swapT_ow (body record + release weighting) against swapT_arprop_h2", "sesoi": 0.15}
    out, order, new, ref = _main_rule(out, task, "swapT_ow_e30", "v22", "swapT_arprop_h2_e30", "v20", 0.15,
                                      "RELEASE WEIGHTING HELPS", "NO HELP")
    if len(new) >= 100:
        gain = sum(new.values()) - 39
        out["early_stop"] = {"rule": "success(swapT_ow e30) - 39 < 5 -> seed 18 not trained", "gain_over_39": gain,
                             "seed18": "NOT TRAINED (early stop)" if gain < 5 else "train"}
        out["card37_condition_two"] = bool(gain >= 10 or out.get("verdict", "").endswith("RELEASE WEIGHTING HELPS"))
    _described(out, task, order, ref, [("swapT_ow_s18_e30", "v22"), ("swapT_ow_e10", "v22"), ("swapT_ow_e20", "v22")])
    return out


def c36b():
    task = "swap_T"
    out = {"run": "card 36b swapT_ar_ow (three frames + release weighting) against swapT_ar (H100 class)", "sesoi": 0.15}
    out, order, new, ref = _main_rule(out, task, "swapT_ar_ow_e30", "v22", "swapT_ar_e30", "e6", 0.15,
                                      "RELEASE WEIGHTING HELPS (NO RECORD)", "NO HELP")
    _described(out, task, order, ref, [("swapT_ar_ow_s18_e30", "v22")])
    return out


def c31():
    """Card 31 (press_cd, countdown; a diagnostic, never a main-table entry), registered 11-28 in gaas_queue.txt above
    press_cd before any run: D = success(press_cd e30) - success(press_told e30, closed_loop/v20), press_button 1-100;
    SESOI +0.30: COMPARISON IS THE BOTTLENECK / NOT THE COMPARISON / UNCERTAIN (pre-set extension: r2, 200 pairs).
    press_cd runs with the scene's counts in the instruction and the simulator's true presses in the record
    (MWAM_TOLD_COUNTS=1, MWAM_LEDGER=oracle). Described: each button's over / right / under; presses beyond the card
    (made after the countdown read 0) per button; success by N1 + N2; e10 / e20; diagnostic 4(a)'s table."""
    task = "press_button"
    out = {"run": "card 31 press_cd (countdown; diagnostic, never a main-table entry) against press_told", "sesoi": 0.30}
    out, order, new, ref = _main_rule(out, task, "press_cd_e30", "v22", "press_told_e30", "v20", 0.30,
                                      "COMPARISON IS THE BOTTLENECK", "NOT THE COMPARISON")
    dv = v20.dv
    try:
        rn, rr = dv.press_rows("v22", "press_cd_e30"), dv.press_rows("v20", "press_told_e30")
        out["described"] = {"press_cd_e30": dv.per_button(rn), "press_told_e30": dv.per_button(rr)}
        for lab, rows in (("press_cd_e30", rn), ("press_told_e30", rr)):
            out["described"][lab]["presses_beyond_card"] = {
                k: sum(max(0, v[k]) for v in rows.values() if isinstance(v.get(k), int)) for k in ("n1_error", "n2_error")}
        by = {}
        for s_, v in rn.items():
            c1, c2 = v.get("card_1"), v.get("card_2")
            if c1 is not None and c2 is not None:
                k = int(c1) + int(c2)
                by.setdefault(k, [0, 0])
                by[k][0] += int(bool(new.get(s_)))
                by[k][1] += 1
        out["described"]["success_by_N1_plus_N2"] = {k: f"{a}/{b}" for k, (a, b) in sorted(by.items())}
        d4 = _module("diag_cpu_v21", "diag_cpu_v21.py")
        out["described"]["pressed_x_card"] = d4.diag4a(["v22:press_cd_e30"]).get("items", {}).get("v22:press_cd_e30")
    except Exception as e:                                                     # noqa: BLE001
        out["described_error"] = f"{type(e).__name__}: {e}"
    for tag in ("e10", "e20"):
        _, x = success("v22", f"press_cd_{tag}", task)
        if x:
            out[f"described_{tag}"] = compare(x, ref, order)
    return out


def gate(name, word, anywhere=False):
    """name = c36 / c36b (V22_<NAME>.json) or a verdict file stem such as V21_C23 (11-28 audit: card 23's extension)."""
    f = F / (f"{name}.json" if name.startswith("V2") else f"V22_{name.upper()}.json")
    v = json.loads(f.read_text()).get("verdict", "") if f.exists() else ""
    if anywhere:     # "task (MAIN): X; task (beside): Y" -> release if any part is still unresolved UNCERTAIN
        parts = [p.split(": ", 1)[-1] for p in v.split("; ")]
        ok = any(p.startswith(word) and "->" not in p for p in parts)
    else:
        ok = v.startswith(word) and "->" not in v
    print(f"V22 GATE {name} {word}: verdict '{v}' -> {'release' if ok else 'hold'}")
    return 0 if ok else 3


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name == "gate":
        return gate(sys.argv[2], sys.argv[3], "--anywhere" in sys.argv)
    fns = {"c36": c36, "c36b": c36b, "c31": c31}
    if name not in fns:
        print(__doc__)
        return 2
    out = fns[name]()
    print(json.dumps(out))
    (F / f"V22_{name.upper()}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"V22 {name.upper()}: {out['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
