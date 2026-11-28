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
  python3 scripts/fullft/v22_verdict.py c36 | c36b   -> outputs/fullft/V22_C36.json / V22_C36B.json
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


def gate(name, word):
    f = F / f"V22_{name.upper()}.json"
    v = json.loads(f.read_text()).get("verdict", "") if f.exists() else ""
    ok = v.startswith(word)
    print(f"V22 GATE {name} {word}: verdict '{v}' -> {'release' if ok else 'hold'}")
    return 0 if ok else 3


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name == "gate":
        return gate(sys.argv[2], sys.argv[3])
    fns = {"c36": c36, "c36b": c36b}
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
