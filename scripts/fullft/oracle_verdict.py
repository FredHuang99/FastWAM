"""Plan v18 Z0 ORACLE verdict on the 5090 (registered 11-21 01:20 BJ by Opus; the user approved replacing T2b at 00:58;
written before any oracle episode exists). Read-only. First card under the reading method of plan v18 (effect size with
a confidence interval against the smallest effect that matters; three outcomes; a pre-set extension when uncertain).

Question (the crucial test between the two explanations left after G4-0 / T1): are the over-presses there because the
robot's own press reaches its memory too late ("late write"), or does the policy not count even with a timely, complete
record ("does not count")? Intervention: MWAM_LEDGER=oracle. The ledger's press entries come from the simulator's true
counters, readable from the very observation that shows the press (zero writing delay; the detector's 12-frame delay,
its misses and its spurious bottoms are gone); everything else as trained. Model press_count e30 (the T1 / T2 model).
  oracle  closed_loop/tim, label press_count_e30_oracle, press scenes 1-100, default noise
  base    closed_loop/g1 (scenes 1-50) + closed_loop/sel (51-100), label press_count_e30 (same noise, same machine)
Predictions: late write -> over-pressing falls by at least half; does not count -> it stays.
Metric: first-button over-press o = 1 if e1 >= +1 (export_stages n1_error); paired by scene.
  D = rate_o(oracle) - rate_o(base); 95 % CI by paired bootstrap over scenes (10,000 resamples, seed 0);
  SESOI = -0.5 x rate_o(base) (the timing explanation must remove at least half of the over-presses).
Registered reading:
  CI upper bound < 0 and D <= SESOI   -> TIMING EXPLAINS >= HALF
  CI upper bound < 0 and D >  SESOI   -> TIMING EXPLAINS PART
  CI lower bound > SESOI              -> TIMING DOES NOT EXPLAIN (confident that less than half is removed)
  otherwise                           -> UNCERTAIN: pre-set extension = the oracle on scenes 1-100 again with
                                         MWAM_NOISE_SALT=r2 against the r2 baselines (nz2 1-50 + rep 51-100), the same
                                         rule on all 200 pairs; still UNCERTAIN after that is reported as such.
Floor: >= 95 pairs. Manipulation check: the oracle run's median frames from a press to the first decision showing it
(press_ledger_audit) <= 7, else VOID.
Reported with the same rule, not the reading: mean extra presses max(e1, 0); success. Reported only: the oracle run's
O3 chain share (press_timing_audit: extra presses made with the full count already in the ledger).
Meaning: >= HALF -> the late write is the mechanism (the detector's physical delay; a faster writer is the fix, the
thesis stands); PART -> timing contributes, counting is the larger part; DOES NOT EXPLAIN -> the over-presses are a
reading / counting problem: the main thesis is dropped as their explanation and the next round (Fable) starts there.
Expectation (subjective, before the run): DOES NOT EXPLAIN 0.55, PART 0.3, >= HALF 0.15.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/oracle_verdict.py [--extended]   Writes outputs/fullft/ORACLE_VERDICT.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pp = module("press_pair", "press_pair.py")
pla = module("press_ledger_audit", "press_ledger_audit.py")
F = pp.R / "outputs/fullft"


def merged(*items):
    out = {}
    for folder, label in items:
        try:
            out.update({str(k): v for k, v in pp.stages(folder, label).items()})
        except Exception:                                   # noqa: BLE001 (run not there yet)
            pass
    return out


def e1(v):
    x = v.get("n1_error")
    return x if isinstance(x, int) else None


def paired(new: dict, base: dict):
    seeds = sorted(s for s in set(new) & set(base) if e1(new[s]) is not None and e1(base[s]) is not None)
    return seeds, [(e1(new[s]), e1(base[s])) for s in seeds]


def boot_ci(pairs, f, n=10000, seed=0):
    rng = random.Random(seed)
    k = len(pairs)
    vals = []
    for _ in range(n):
        smp = [pairs[rng.randrange(k)] for _ in range(k)]
        vals.append(f(smp))
    vals.sort()
    return vals[int(0.025 * n)], vals[int(0.975 * n) - 1]


def word(d, lo, hi, sesoi):
    if hi < 0:
        return "TIMING EXPLAINS >= HALF" if d <= sesoi else "TIMING EXPLAINS PART"
    if lo > sesoi:
        return "TIMING DOES NOT EXPLAIN"
    return "UNCERTAIN"


def reading(new, base, name):
    seeds, pairs = paired(new, base)
    out = {"pairs": len(pairs)}
    if len(pairs) < 95:
        out["word"] = f"WAIT / NO READING ({len(pairs)} pairs < 95)"
        return out
    rate = lambda ps, i: sum(p[i] >= 1 for p in ps) / len(ps)                          # noqa: E731
    dfun = lambda ps: rate(ps, 0) - rate(ps, 1)                                         # noqa: E731
    d, (lo, hi) = dfun(pairs), boot_ci(pairs, dfun)
    rb = rate(pairs, 1)
    sesoi = -0.5 * rb
    out.update(rate_base=round(rb, 3), rate_new=round(rate(pairs, 0), 3), D=round(d, 3), ci=[round(lo, 3), round(hi, 3)],
               sesoi=round(sesoi, 3), word=word(d, lo, hi, sesoi))
    ext = lambda ps, i: sum(max(p[i], 0) for p in ps) / len(ps)                        # noqa: E731
    xfun = lambda ps: ext(ps, 0) - ext(ps, 1)                                           # noqa: E731
    xd, (xlo, xhi) = xfun(pairs), boot_ci(pairs, xfun)
    xb = ext(pairs, 1)
    out["extra_presses"] = {"base_mean": round(xb, 3), "new_mean": round(ext(pairs, 0), 3), "D": round(xd, 3),
                            "ci": [round(xlo, 3), round(xhi, 3)], "sesoi": round(-0.5 * xb, 3),
                            "word_same_rule": word(xd, xlo, xhi, -0.5 * xb)}
    print(f"{name}: {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extended", action="store_true", help="also pool the pre-set r2 extension (200 pairs)")
    args = ap.parse_args()
    base = merged(("g1", "press_count_e30"), ("sel", "press_count_e30"))
    new = merged(("tim", "press_count_e30_oracle"))
    res = {"main": reading(new, base, "MAIN (default noise, scenes 1-100)")}
    res["success"] = {"base": sum(bool(v.get("success")) for v in base.values()),
                      "oracle": sum(bool(v.get("success")) for v in new.values()), "n_oracle": len(new)}
    try:
        a = pla.audit("tim", "press_count_e30_oracle", quiet=True)
        res["manipulation"] = {"delay_median": a.get("delay_median"), "delay_p90": a.get("delay_p90"),
                               "passed": a.get("delay_median") is not None and a["delay_median"] <= 7,
                               "over_phases": a.get("over"), "why": a.get("why")}
    except Exception as e:                                  # noqa: BLE001
        res["manipulation"] = {"error": str(e), "passed": None}
    final = res["main"]["word"]
    if args.extended:
        base2 = merged(("nz2", "press_count_e30"), ("rep", "press_count_e30"))
        new2 = merged(("tim2", "press_count_e30_oracle"))
        b = {**{f"a{k}": v for k, v in base.items()}, **{f"b{k}": v for k, v in base2.items()}}
        n = {**{f"a{k}": v for k, v in new.items()}, **{f"b{k}": v for k, v in new2.items()}}
        res["extended"] = reading(n, b, "EXTENDED (both noises, 200 pairs)")
        final = res["extended"]["word"]
    if res["manipulation"].get("passed") is False:
        final = f"VOID (manipulation check: delay {res['manipulation'].get('delay_median')} > 7; word was {final})"
    res["ORACLE"] = final
    print(f"manipulation check: {res['manipulation']}")
    print(f"success: {res['success']}")
    print(f"Z0 ORACLE: {final}")
    (F / "ORACLE_VERDICT.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
