"""Plan v17 G4a: what the registered T1 / T2 words mean (Fable review of plan v16, 1(c) and 2.1; taken over in full by
the user 11-20 20:47; written 22:10 BJ by Opus before any T1 / T2 run finished). Read-only, descriptive: it never
changes the words of timing_verdict.py, it adds the checks that decide how a word is READ:
  manipulation check   median frames from a press to the first decision showing it (press_ledger_audit): lag16 and
                       lag8 must be ABOVE the baseline, prov BELOW; an arm that did not move is not evidence
  prov over-presses    over(prov) - over(base) <= -8: writing earlier helped directly (supports the thesis even when
                       the registered word is EARLY NO EFFECT)
  lag16 e1             mean first-count error and episodes with e1 >= +2 against the baseline (the episode-level word
                       can saturate: 24/50 already over-press)
  non-specific damage  under-presses or failures to press at all rising with lag16 (the timing mechanism only allows
                       more over-presses)
  fake records (prov)  under-pressing phases of button 1 in which a spurious ledger bottom (no registered press) was
                       written before the robot moved on: early writing created false records, not early knowledge
  dose                 over-presses and mean e1 at lag 0 / 8 / 16 (monotone?)
T2 typing (Fable 1(b); thresholds registered here 11-20 22:20 BJ, before the T2 result): over-pressing phases of button
1 in the baseline g1 run, by press_ledger_audit class: 'late' vs the rest ('saw full ledger' + 'missed'); fixed = the
same scene has e1 <= 0 in exec4. R = press_timing_audit's R_late_button1 of g1:press_count_e30 (computed before T2).
  late fix <= R + 0.15 and other fix <= 0.25  -> READ-YOUR-WRITES TYPE (what T2 fixed is the record that came too late)
  other fix > 0.50 or late fix > R + 0.25     -> EXECUTION TOO LONG (shorter open-loop execution helps by itself)
  otherwise -> MIXED; floor: >= 8 late and >= 5 other phases, else NO READING.
Reading of TIMING NOT CAUSAL (registered by Fable, 2.1): it refutes the mechanism only if (1) the manipulation check
passed for lag16 and prov, (2) prov did not lower over-presses by >= 8, and (3) lag16's mean e1 did not rise (> +0.2);
otherwise it is recorded as "word NOT CAUSAL, the descriptive quantities do not support a refutation" and T2b decides.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/timing_meaning.py     Writes outputs/fullft/TIMING_MEANING.json.
"""
from __future__ import annotations

import importlib.util
import json
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
RUNS = {"base": ("g1", "press_count_e30"), "lag8": ("tim", "press_count_e30_lag8"),
        "lag16": ("tim", "press_count_e30_lag16"), "prov": ("tim", "press_count_e30_prov"),
        "exec4": ("tim", "press_count_e30_exec4")}


def e1s(st):
    return [v.get("n1_error") for v in st.values() if isinstance(v.get("n1_error"), int)]


def main():
    out, st, au = {"runs": {}}, {}, {}
    for k, (folder, label) in RUNS.items():
        try:
            st[k] = pp.stages(folder, label)
        except Exception:                                   # noqa: BLE001
            st[k] = {}
        try:
            au[k] = pla.audit(folder, label, quiet=True) if st[k] else {}
        except Exception as e:                              # noqa: BLE001
            au[k] = {"error": str(e)}
        e = e1s(st[k])
        out["runs"][k] = {"n": len(st[k]), "over": sum(x >= 1 for x in e), "under": sum(x <= -1 for x in e),
                          "e1_mean": round(sum(e) / len(e), 3) if e else None, "e1_2plus": sum(x >= 2 for x in e),
                          "success": sum(bool(v.get("success")) for v in st[k].values()),
                          "delay_median": au[k].get("delay_median"), "delay_p90": au[k].get("delay_p90"),
                          "why": au[k].get("why"), "recall": au[k].get("recall")}
        if k == "prov" and st[k]:
            eps = []
            root = pp.O / "closed_loop" / folder / label / "on" / "press_button"
            for d in sorted(root.glob("seed_*")):
                if d.name.split("_", 1)[1].isdigit() and (d / "result.json").exists():
                    eps.append(pla.analyse_episode(d))
            under = [e["phases"][1] for e in eps if e["phases"].get(1, {}).get("outcome") == "under"]
            out["runs"][k]["under_phases_b1"] = len(under)
            out["runs"][k]["under_phases_b1_with_fake_record"] = sum(ph.get("spurious_in_phase", 0) > 0 for ph in under)
        print(f"{k:6s} {label}: {out['runs'][k]}")
    r = out["runs"]
    ok = lambda k: r[k]["n"] >= 48                                     # noqa: E731
    checks = {}
    if ok("base") and ok("lag16") and ok("prov"):
        db = r["base"]["delay_median"]
        checks["manipulation_lag16"] = None if db is None or r["lag16"]["delay_median"] is None else r["lag16"]["delay_median"] > db
        checks["manipulation_prov"] = None if db is None or r["prov"]["delay_median"] is None else r["prov"]["delay_median"] < db
        checks["prov_over_drop_ge8"] = r["prov"]["over"] - r["base"]["over"] <= -8
        checks["lag16_e1_mean_rise"] = (r["lag16"]["e1_mean"] - r["base"]["e1_mean"]) if r["lag16"]["e1_mean"] is not None else None
        checks["lag16_nonspecific_under_rise"] = r["lag16"]["under"] - r["base"]["under"]
        refute = (checks["manipulation_lag16"] is True and checks["manipulation_prov"] is True
                  and not checks["prov_over_drop_ge8"]
                  and checks["lag16_e1_mean_rise"] is not None and checks["lag16_e1_mean_rise"] <= 0.2)
        checks["NOT_CAUSAL_would_refute"] = refute
    if ok("base") and ok("lag8") and ok("lag16"):
        o = [r[k]["over"] for k in ("base", "lag8", "lag16")]
        m = [r[k]["e1_mean"] for k in ("base", "lag8", "lag16")]
        checks["dose_over_0_8_16"] = o
        checks["dose_e1_mean_0_8_16"] = m
        checks["dose_monotone"] = o[0] <= o[1] <= o[2] and m[0] <= m[1] <= m[2]
    if ok("base") and ok("exec4"):
        root = pp.O / "closed_loop" / RUNS["base"][0] / RUNS["base"][1] / "on" / "press_button"
        cls = {}
        for d in sorted(root.glob("seed_*")):
            if d.name.split("_", 1)[1].isdigit() and (d / "result.json").exists():
                ph = pla.analyse_episode(d)["phases"].get(1, {})
                if ph.get("outcome") == "over":
                    cls[d.name.split("_", 1)[1]] = ph["why"]
        ex = {str(k): v for k, v in st["exec4"].items()}
        def fixed(seed):
            e = (ex.get(str(seed)) or {}).get("n1_error")
            return isinstance(e, int) and e <= 0
        late = [sd for sd, w in cls.items() if w == "late" and str(sd) in ex]
        other = [sd for sd, w in cls.items() if w != "late" and str(sd) in ex]
        lf = sum(map(fixed, late)) / len(late) if late else None
        of = sum(map(fixed, other)) / len(other) if other else None
        try:
            R = json.loads((F / "PRESS_TIMING_AUDIT.json").read_text())["runs"]["g1:press_count_e30"]["t2_R"]["R_late_button1"]
        except Exception:                                    # noqa: BLE001
            R = None
        if len(late) < 8 or len(other) < 5 or R is None:
            word = f"NO READING (late {len(late)}, other {len(other)}, R {R})"
        elif lf <= R + 0.15 and of <= 0.25:
            word = "READ-YOUR-WRITES TYPE"
        elif of > 0.50 or lf > R + 0.25:
            word = "EXECUTION TOO LONG"
        else:
            word = "MIXED"
        checks["t2_typing"] = {"late": len(late), "late_fixed_rate": lf, "other": len(other), "other_fixed_rate": of,
                               "R": R, "word": word}
    try:
        tv = json.loads((F / "TIMING_VERDICT.json").read_text())
        out["registered_words"] = {"T1": tv.get("T1"), "T2": tv.get("T2"), "late": tv.get("late_word"),
                                   "early": tv.get("early_word")}
    except Exception:                                        # noqa: BLE001
        out["registered_words"] = None
    out["checks"] = checks
    print(f"registered words: {out['registered_words']}")
    print(f"checks: {checks}")
    if out["registered_words"] and out["registered_words"].get("T1") == "TIMING NOT CAUSAL":
        print("READING OF NOT CAUSAL: " + ("refutes the mechanism (all three checks hold)" if checks.get("NOT_CAUSAL_would_refute")
                                           else "word NOT CAUSAL, the descriptive quantities do not support a refutation; T2b decides"))
    (F / "TIMING_MEANING.json").write_text(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
