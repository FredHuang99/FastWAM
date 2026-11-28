#!/usr/bin/env python3
"""Plan v22 (Fable, rev. 1) verdicts, written 11-28 17:40 (Opus) before any episode of these runs; the readings are
registered above the queue lines (gaas_queue.txt / h200_queue.txt / h100_queue.txt, commit c3787d8). A40, official
seed-42 banks, default noise; new runs' episodes in closed_loop/v22 (r2 noise in closed_loop/r2).
  c36   card 36: D = success(swapT_ow e30) - success(swapT_arprop_h2 e30, closed_loop/v20), swap_T 1-100; SESOI +0.15:
        CI lower > +0.15 -> RELEASE WEIGHTING HELPS; CI upper < +0.15 -> NO HELP; otherwise UNCERTAIN (pre-set
        extension: r2, 200 pairs, the same rule). Early stop (written before the run): success(swapT_ow e30) - 39 < 5 ->
        the seed-18 run is not trained. Described: swapT_ow_s18 e30 (main-table cell = mean of the two seeds); e10 / e20.
  c36_a100  card 36 on the A100 (fallback approved 11-29, only if the A40 is not repaired at 11-29 12:00): both arms
        on the A100, closed_loop/a100fb; see c36_a100() -> V22_C36_A100.json
  c36b  card 36b: D = success(swapT_ar_ow e30) - success(swapT_ar e30, closed_loop/e6), swap_T 1-100; SESOI +0.15:
        RELEASE WEIGHTING HELPS (NO RECORD) / NO HELP / UNCERTAIN (same extension). Described: swapT_ar_ow_s18 e30.
Each verdict is about these two checkpoints (plan v21 5.5).
  c31   card 31 (press_cd, 11-28 16:52, before any run): see c31() -- COMPARISON IS THE BOTTLENECK / NOT THE COMPARISON
  python3 scripts/fullft/v22_verdict.py c36 | c36b | c31   -> outputs/fullft/V22_C36.json / V22_C36B.json / V22_C31.json
  python3 scripts/fullft/v22_verdict.py gate c36 UNCERTAIN   -> exit 0 if V22_C36.json's verdict starts with UNCERTAIN
        (100 pairs), else exit 3: releases the pre-set r2 extension tasks on the A40 through requires_pass
"""
from __future__ import annotations

import importlib.util
from collections import Counter
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


def c36_a100():
    """Card 36 on the A100 (fallback; user 11-29 00:5x "中午 12 点没修好就挪"; written 11-29 01:06 before any A100
    episode of these runs). Runs only if scripts/fullft/c36fb_gate.py found the A40 not repaired at 11-29 12:00. Both
    arms on the A100 (A100 class), the A40's swap_T scene bank copied over, the same scenes, arguments and default
    noise; episodes in the A100's closed_loop/a100fb (the pre-set r2 extension in the A100's closed_loop/r2). The same
    rule and SESOI as c36. Every "39" of c36 (swapT_arprop_h2's A40 success) is swapT_arprop_h2's A100 success here.
    After a fallback this is card 36's verdict (v22_gate.py reads it); the A40's c36, if it runs later, is described."""
    task = "swap_T"
    out = {"run": "card 36 on the A100 (fallback, A100 class): swapT_ow against swapT_arprop_h2, both arms on the A100",
           "sesoi": 0.15, "machine": "A100"}
    out, order, new, ref = _main_rule(out, task, "swapT_ow_e30", "a100fb", "swapT_arprop_h2_e30", "a100fb", 0.15,
                                      "RELEASE WEIGHTING HELPS", "NO HELP")
    if len(new) >= 100 and len(ref) >= 100:
        base = sum(ref.values())
        gain = sum(new.values()) - base
        out["early_stop"] = {"rule": f"success(swapT_ow e30) - success(swapT_arprop_h2 e30) on the A100 ({base}) < 5 -> "
                                     "seed 18 not trained (seed 18 was already trained: reported only)",
                             "gain_over_reference": gain, "seed18": "NOT TRAINED (early stop)" if gain < 5 else "train"}
        out["card37_condition_two"] = bool(gain >= 10 or out.get("verdict", "").endswith("RELEASE WEIGHTING HELPS"))
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


def strat_ci(pairs_by_stratum, n=10_000, seed=0):
    """Stratified paired bootstrap (plan v21 5.5 item 6 / plan v22 cards 27, 28): D = mean over strata (seeds) of the
    within-stratum paired mean difference; each replicate resamples the scenes of every stratum with replacement."""
    import random
    rng = random.Random(seed)
    diffs = [[x - y for x, y in pr] for pr in pairs_by_stratum if pr]
    d = sum(sum(v) / len(v) for v in diffs) / len(diffs)
    stats = []
    for _ in range(n):
        stats.append(sum(sum(v[rng.randrange(len(v))] for _ in v) / len(v) for v in diffs) / len(diffs))
    stats.sort()
    return round(d, 4), [round(stats[int(0.025 * n)], 4), round(stats[int(0.975 * n) - 1], 4)]


# card 27 (H200 class: rearr_pw_long_s18 / rearr_pw_long from the new H200's resume checkpoints) and card 27b (the same
# reading with the H100-class pair of card 33: rearr_pw_h100_long_s18 / rearr_pw_h100_long). seed -> (e30, e45, e60)
C27 = {"c27": {18: (("v21", "rearr_pw_s18_e30"), ("v22", "rearr_pw_long_s18_e45"), ("v22", "rearr_pw_long_s18_e60")),
               17: (("v20", "rearr_pw_e30"), ("v22", "rearr_pw_long_e45"), ("v22", "rearr_pw_long_e60"))},
       "c27b": {18: (("v22", "rearr_pw_h100_s18_e30"), ("v22", "rearr_pw_h100_long_s18_e45"), ("v22", "rearr_pw_h100_long_s18_e60")),
                17: (("v22", "rearr_pw_h100_e30"), ("v22", "rearr_pw_h100_long_e45"), ("v22", "rearr_pw_h100_long_e60"))}}


def c27(which="c27"):
    """Card 27 / 27b, registered 11-28 in gaas_queue.txt / h100_queue.txt (verbatim from plan v22 2.4) before any run:
    MAIN, two seeds pooled: D = mean success(e60; s17, s18) - mean success(e30; s17, s18), stratified paired bootstrap;
    SESOI +0.10: TRAINING-LIMITED / NOT TRAINING-LIMITED / UNCERTAIN (pre-set extension: all four checkpoints with r2,
    200 pairs per seed). Early stop: success(e60, s18) - success(e30, s18) < +0.10 -> seed 17 not trained, the card reads
    NOT TRAINING-LIMITED (ONE SEED). Described: each seed at e30 / e45 / e60 with rearr_split classes; the seed gap at
    e60 beside the gap at e30; the expectation written before (s18 e60 >= 85, twice < 5, never < 8; s17 >= 88)."""
    task, cfg = "rearrange_blocks", C27[which]
    out = {"run": f"card {which[1:]} rearrange training length (two seeds pooled)", "sesoi": 0.10, "seeds": {}}
    got = {}
    for sd, cells in cfg.items():
        row = {}
        for tag, (folder, lab) in zip(("e30", "e45", "e60"), cells):
            order, x = success(folder, lab, task)
            got[(sd, tag)] = (order, x)
            if x:
                row[tag] = {"cell": f"{folder}:{lab}", "finished": len(x), "success": sum(x.values()),
                            "classes": dict(Counter(v20.rearr_classes(folder, lab).values()))}
        out["seeds"][sd] = row
    o18, e30_18 = got[(18, "e30")]
    _, e60_18 = got[(18, "e60")]
    if len(e30_18) >= 100 and len(e60_18) >= 100:
        gain = (sum(e60_18.values()) - sum(e30_18.values())) / 100.0
        out["early_stop"] = {"rule": "success(e60, s18) - success(e30, s18) < +0.10 -> seed 17 not trained",
                             "gain_s18": round(gain, 2), "seed17": "train" if gain >= 0.10 else "NOT TRAINED (early stop)"}
        if gain < 0.10:
            out["verdict"] = "NOT TRAINING-LIMITED (ONE SEED)"
    full = all(len(got[(sd, t)][1]) >= 100 for sd in cfg for t in ("e30", "e60"))
    if "verdict" not in out:
        if not full:
            out["verdict"] = "WAIT (" + ", ".join(f"s{sd} {t} {len(got[(sd, t)][1])}" for sd in cfg for t in ("e30", "e60")) + ")"
        else:
            def pairs(src):
                res = []
                for sd in cfg:
                    order, a = src(sd, "e60")
                    _, b = src(sd, "e30")
                    res.append([(a[k], b[k]) for k in order[:100] if k in a and k in b])
                return res
            d, ci = strat_ci(pairs(lambda sd, t: got[(sd, t)]))
            main = {"D": d, "ci95": ci, "scenes_per_seed": [len(x) for x in pairs(lambda sd, t: got[(sd, t)])]}
            rule = lambda c: three(c, 0.10, "TRAINING-LIMITED", "NOT TRAINING-LIMITED")   # noqa: E731
            out["main"], out["verdict"] = main, rule(main)
            if out["verdict"] == "UNCERTAIN":
                r2 = {(sd, t): success("r2", cfg[sd][i][1], task) for sd in cfg for i, t in ((0, "e30"), (2, "e60"))}
                out["extension"] = {"r2_finished": {f"s{sd} {t}": len(v[1]) for (sd, t), v in r2.items()}}
                if all(len(v[1]) >= 100 for v in r2.values()):
                    def both(sd, t):
                        order, x = got[(sd, t)]
                        _, y = r2[(sd, t)]
                        z = {("d", k): v for k, v in x.items()}
                        z.update({("r2", k): v for k, v in y.items()})
                        return [("d", k) for k in order[:100]] + [("r2", k) for k in order[:100]], z
                    d2, ci2 = strat_ci(pairs(both))
                    e = {"D": d2, "ci95": ci2}
                    out["extension"].update(pooled=e, verdict=rule(e))
                    out["verdict"] = f"UNCERTAIN at 100 pairs -> {rule(e)} at 200 pairs per seed (pre-set extension)"
                else:
                    out["extension"]["verdict"] = "WAIT (r2 evaluations: the pre-set extension)"
    gaps = {}
    for t in ("e30", "e60"):
        a, b = got[(17, t)][1], got[(18, t)][1]
        if len(a) >= 100 and len(b) >= 100:
            gaps[t] = sum(a.values()) - sum(b.values())
    out["seed_gap_s17_minus_s18"] = gaps
    s18 = out["seeds"][18].get("e60")
    if s18:
        cl = s18["classes"]
        out["expectation_written_before"] = {
            "s18_e60_success": s18["success"], "s18_twice": sum(v for k, v in cl.items() if k.startswith("pressed twice")),
            "s18_never": sum(v for k, v in cl.items() if k.startswith("never pressed")),
            "s17_e60_success": (out["seeds"][17].get("e60") or {}).get("success")}
    return out


def c30():
    """Card 30 (obs_cf800), registered 11-28 before any run: D = success(obs_cf800 e10) - success(obs_s800 e10,
    closed_loop/v20), observe_and_pickup 1-100; SESOI +0.15: COUNTERFACTUAL GROUPS HELP AT 800 / NO GAIN AT 800 /
    UNCERTAIN (pre-set extension: r2, 200 pairs). Described: e5; against 28 and 20; seed extension due when not UNCERTAIN
    and |D| < 0.30."""
    task = "observe_and_pickup"
    out = {"run": "card 30 obs_cf800 (800 counterfactual scenes) against obs_s800", "sesoi": 0.15}
    out, order, new, ref = _main_rule(out, task, "obs_cf800_e10", "v22", "obs_s800_e10", "v20", 0.15,
                                      "COUNTERFACTUAL GROUPS HELP AT 800", "NO GAIN AT 800")
    if len(new) >= 100:
        out["success_vs_bars"] = f"{sum(new.values())} vs 28 (pure-WAM best, self-reported, RoboTwin pre-training) and 20 (blind pick)"
    v21 = _module("v21_verdict", "v21_verdict.py")
    out["seed_extension"] = v21.seed_extension(out)
    _described(out, task, order, ref, [("obs_cf800_e5", "v22")])
    return out


def _non_inferior(out, key, task, new_label, new_folder, ref_label, ref_folder, margin=-0.05):
    order, ref = success(ref_folder, ref_label, task)
    _, new = success(new_folder, new_label, task)
    if len(new) < 100 or len(ref) < 100:
        out[key] = {"verdict": f"WAIT ({len(new)} / {len(ref)} of 100)"}
        return
    c = compare(new, ref, order)
    rule = lambda x: v20.non_inferior(x, margin)                # noqa: E731
    o = {}
    with_extension(o, c, rule(c), rule, task, new_label, new_folder, ref_label, ref_folder)
    out[key] = o


def c32():
    """Card 32 (rearr_joint3, conditional), registered 11-28 before any run: D = success(rearr_joint3 e30) -
    success(rearr_v3c_h2 e30, closed_loop/rv3c), rearrange 1-100; SESOI +0.15: CO-TRAINING HELPS REARRANGE / NO HELP /
    UNCERTAIN (pre-set extension). Beside: put_back / swap 1-100 against ar2_v3c e30 (v20), non-inferiority -0.05.
    Described: classes; against rearr_pw's two seeds (93 / 61); e10 / e20; the expectation (never < 8, twice < 10)."""
    task = "rearrange_blocks"
    out = {"run": "card 32 rearr_joint3 (rearrange co-trained with put_back / swap) against rearr_v3c_h2", "sesoi": 0.15}
    out, order, new, ref = _main_rule(out, task, "rearr_joint3_e30", "v22", "rearr_v3c_h2_e30", "rv3c", 0.15,
                                      "CO-TRAINING HELPS REARRANGE", "NO HELP")
    for t in ("put_back_block", "swap_blocks"):
        _non_inferior(out, f"beside_{t}", t, "rearr_joint3_e30", "v22", "ar2_v3c_e30", "v20")
    cl = dict(Counter(v20.rearr_classes("v22", "rearr_joint3_e30").values()))
    out["classes"] = cl
    out["expectation_written_before"] = {
        "never_pressed": sum(v for k, v in cl.items() if k.startswith("never pressed")),
        "pressed_twice": sum(v for k, v in cl.items() if k.startswith("pressed twice"))}
    _described(out, task, order, ref, [("rearr_pw_e30", "v20"), ("rearr_pw_s18_e30", "v21"),
                                       ("rearr_joint3_e10", "v22"), ("rearr_joint3_e20", "v22")])
    v21 = _module("v21_verdict", "v21_verdict.py")
    out["seed_extension"] = v21.seed_extension(out)
    return out


def c37():
    """Card 37 (swapT_joint3_ow, conditional), registered 11-28 before any run: D = success(swapT_joint3_ow e30) -
    success(swapT_joint3 e30, closed_loop/v20), swap_T 1-100; SESOI +0.10: ADDS UP / NO FURTHER GAIN / UNCERTAIN
    (pre-set extension). Beside: put_back / swap 1-100 against swapT_joint3 e30 (non-inferiority -0.05). Described:
    against 94-97; e10 / e20."""
    task = "swap_T"
    out = {"run": "card 37 swapT_joint3_ow (co-training + release weighting) against swapT_joint3", "sesoi": 0.10}
    out, order, new, ref = _main_rule(out, task, "swapT_joint3_ow_e30", "v22", "swapT_joint3_e30", "v20", 0.10,
                                      "ADDS UP", "NO FURTHER GAIN")
    for t in ("put_back_block", "swap_blocks"):
        _non_inferior(out, f"beside_{t}", t, "swapT_joint3_ow_e30", "v22", "swapT_joint3_e30", "v20")
    _described(out, task, order, ref, [("swapT_joint3_ow_e10", "v22"), ("swapT_joint3_ow_e20", "v22")])
    v21 = _module("v21_verdict", "v21_verdict.py")
    out["seed_extension"] = v21.seed_extension(out)
    return out


def desc(task, items):
    """Described-only cards (28, 29, 33, 35, fillers): success 1-100 of each FOLDER:LABEL, beside the first item
    (the reference), with the task's split classes for rearrange."""
    rf, rl = items[0].split(":", 1)
    order, ref = success(rf, rl, task)
    out = {"run": f"plan v22 described: {' / '.join(items[1:])} beside {items[0]} ({task})", "reference": items[0],
           "reference_success": sum(ref.values()), "items": {}}
    for it in items[1:]:
        f, l = it.split(":", 1)
        _, x = success(f, l, task)
        row = {"finished": len(x), "success": sum(x.values())}
        if x and ref:
            row["against_reference"] = compare(x, ref, order)
        if task == "rearrange_blocks" and x:
            row["classes"] = dict(Counter(v20.rearr_classes(f, l).values()))
        out["items"][it] = row
    out["verdict"] = "DESCRIBED" if all(v["finished"] >= 100 for v in out["items"].values()) else "PARTIAL"
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
    fns = {"c36": c36, "c36_a100": c36_a100, "c36b": c36b, "c31": c31, "c27": lambda: c27("c27"), "c27b": lambda: c27("c27b"),
           "c30": c30, "c32": c32, "c37": c37}
    if name == "desc":                       # desc <task> <ref folder:label> <folder:label> ... [--name X]
        args = [a for a in sys.argv[2:] if not a.startswith("--name")]
        nm = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--name=")), args[2].split(":", 1)[1])
        out = desc(args[0], args[1:])
        (F / f"V22_DESC_{nm.upper()}.json").write_text(json.dumps(out, indent=1) + "\n")
        print(json.dumps(out)[:3000])
        print(f"V22 DESC {nm}: {out['verdict']}")
        return 0
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
