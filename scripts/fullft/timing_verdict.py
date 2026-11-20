"""Plan v16 T1 (TIMING) and T2 (CHUNK) verdicts on the 5090 (written 11-20 20:00 BJ by Opus, who writes plan v16 with the
user's approval of 19:12; before any T1 / T2 episode exists). Read-only. Thesis under test (MemWAM Insight v1, line 5,
"read your own writes"): a chunked policy over-presses because a press reaches its memory later than the next decision.

Model: press_count e30 (the E4 pick; trained with the fast writer, lag 0, no provisional write). Scenes 1-50 of the press
bank, default diffusion noise, all on the 5090 GPU1 (the machine of E3 / E4 / G2'). Baseline = the existing run
closed_loop/g1 label press_count_e30 (same scenes, same noise, same machine; first count over 24/50, under 0/50).
New runs (closed_loop/tim):
  press_count_e30_lag16   MWAM_LEDGER_LAG=16: every entry becomes visible 16 frames after its confirmation (later)
  press_count_e30_prov    MWAM_EVENT_PROVISIONAL=0.002: entries visible at a 2 mm reversal, before the trained 1.2 cm
                          confirmation (earlier; the v3c writer at test time)
  press_count_e30_lag8    MWAM_LEDGER_LAG=8 (the middle of the dose; descriptive)
  press_count_e30_exec4   --execute 4 instead of 8 (decisions twice as often; trained timing)
Metric: first count error e1 = presses of button 1 - the required number (export_stages n1_error); over: e1 >= +1;
under: e1 <= -1. Pairs = the same scene in the new run and the baseline; sign test on the discordant pairs.
Registered reading (T1, the two sides):
  LATE   over(lag16) - over(base) >= 8 with paired sign p < 0.05 -> LATE HURTS; |diff| <= 4 -> LATE NO EFFECT; else
         LATE UNDECIDED.
  EARLY  under(prov) - under(base) >= 8 with p < 0.05 -> EARLY FLIPS; |diff| <= 4 -> EARLY NO EFFECT; else EARLY UNDECIDED.
  T1 word: LATE HURTS and EARLY FLIPS -> TIMING CAUSAL; only LATE HURTS -> LATE SIDE ONLY; only EARLY FLIPS -> EARLY SIDE
  ONLY; LATE NO EFFECT and EARLY NO EFFECT -> TIMING NOT CAUSAL; otherwise PARTIAL.
Registered reading (T2): over(exec4) <= over(base) - 8 with p < 0.05 -> SHORTER CHUNK HELPS; |diff| <= 4 -> CHUNK NO
  EFFECT; otherwise PARTIAL.
Floor (each run): >= 48 of 50 finished, else NO READING for the words that need it.
Reported only: successes per run; over / under at lag 0 / 8 / 16 (dose order); prov's over count; the press ledger audit
(share of over-pressing phases that began while the last press was not yet in the ledger) per run.
Written expectations (subjective, before any run): T1 TIMING CAUSAL 0.45, LATE SIDE ONLY 0.25; T2 PARTIAL or HELPS 0.6.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/timing_verdict.py        Writes outputs/fullft/TIMING_VERDICT.json.
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
F = pp.R / "outputs/fullft"
BASE = ("g1", "press_count_e30")
RUNS = {"lag16": ("tim", "press_count_e30_lag16"), "prov": ("tim", "press_count_e30_prov"),
        "lag8": ("tim", "press_count_e30_lag8"), "exec4": ("tim", "press_count_e30_exec4")}


def kind(e):
    return None if not isinstance(e, int) else "over" if e >= 1 else "under" if e <= -1 else "right"


def cell(st, base, side):
    common = sorted(set(st) & set(base))
    a = sum(kind(st[s].get("n1_error")) == side and kind(base[s].get("n1_error")) != side for s in common)
    b = sum(kind(base[s].get("n1_error")) == side and kind(st[s].get("n1_error")) != side for s in common)
    n_new = sum(kind(st[s].get("n1_error")) == side for s in common)
    n_base = sum(kind(base[s].get("n1_error")) == side for s in common)
    return {"pairs": len(common), "new": n_new, "base": n_base, "diff": n_new - n_base, "only_new": a, "only_base": b,
            "p": pp.sign_p(a, b)}


def side_word(c, name_hit, name_null, name_else):
    if c is None:
        return "WAIT"
    if c["pairs"] < 48:
        return f"NO READING ({c['pairs']} pairs < 48)"
    if c["diff"] >= 8 and c["p"] < 0.05:
        return name_hit
    if abs(c["diff"]) <= 4:
        return name_null
    return name_else


def main():
    base = pp.stages(*BASE)
    st, out = {}, {"baseline": f"{BASE[0]}:{BASE[1]}", "runs": {}}
    for k, (folder, label) in RUNS.items():
        try:
            st[k] = pp.stages(folder, label)
        except Exception:                                  # noqa: BLE001  (run not there yet)
            st[k] = {}
        n = pp.numbers(st[k]) if st[k] else {"n": 0}
        out["runs"][k] = n
        print(f"{k:6s} {label}: {n}")
    print(f"base   {BASE[1]}: {pp.numbers(base)}")
    late = cell(st["lag16"], base, "over") if len(st["lag16"]) >= 48 else None
    early = cell(st["prov"], base, "under") if len(st["prov"]) >= 48 else None
    chunk = cell(st["exec4"], base, "over") if len(st["exec4"]) >= 48 else None
    lw = side_word(late, "LATE HURTS", "LATE NO EFFECT", "LATE UNDECIDED")
    ew = side_word(early, "EARLY FLIPS", "EARLY NO EFFECT", "EARLY UNDECIDED")
    if "WAIT" in (lw, ew) or "NO READING" in lw or "NO READING" in ew:
        t1 = "WAIT" if "WAIT" in (lw, ew) else "NO READING"
    elif lw == "LATE HURTS" and ew == "EARLY FLIPS":
        t1 = "TIMING CAUSAL"
    elif lw == "LATE HURTS":
        t1 = "LATE SIDE ONLY"
    elif ew == "EARLY FLIPS":
        t1 = "EARLY SIDE ONLY"
    elif lw == "LATE NO EFFECT" and ew == "EARLY NO EFFECT":
        t1 = "TIMING NOT CAUSAL"
    else:
        t1 = "PARTIAL"
    if chunk is None:
        t2 = "WAIT"
    elif chunk["pairs"] < 48:
        t2 = "NO READING"
    else:
        d = -chunk["diff"]                                  # fewer over-presses = positive
        p = pp.sign_p(chunk["only_new"], chunk["only_base"])
        t2 = "SHORTER CHUNK HELPS" if d >= 8 and p < 0.05 else "CHUNK NO EFFECT" if abs(d) <= 4 else "PARTIAL"
    dose = {k: (out["runs"][k].get("first_over1", 0) + out["runs"][k].get("first_over2plus", 0)) if out["runs"][k].get("n")
            else None for k in ("lag8", "lag16")}
    nb = pp.numbers(base)
    dose["lag0"] = nb["first_over1"] + nb["first_over2plus"]
    out.update(late=late, early=early, chunk=chunk, late_word=lw, early_word=ew, T1=t1, T2=t2, over_by_lag=dose,
               base_numbers=nb)
    print(f"T1 LATE: {late}\n   -> {lw}\nT1 EARLY: {early}\n   -> {ew}\nT1 VERDICT: {t1}")
    print(f"T2 CHUNK: {chunk}\nT2 VERDICT: {t2}\nover-pressed first counts by lag (0 / 8 / 16): {dose}")
    (F / "TIMING_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
