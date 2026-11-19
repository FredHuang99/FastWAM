"""Plan v14 E17 PRESS-A40: the press series re-evaluated on the A40 (registered by Fable 11-18, approved by the user
18:33; this script written 11-19 08:50 BJ, before any press model ran on the A40). Read-only, descriptive only.

A40, closed_loop/e17, press_button scenes 1-100 of the A40's own official bank (planned on the A40; its first 50 equal
the 5090 copy in scripts/fullft/banks, checked by A40-BANK-press_button). Per label: successes and first-count right on
1-50 and 51-100. Per run, the P-SEL rule on 1-50 (most successes; ties -> more first counts right; ties -> the later
epoch) and the pick's 51-100. Consistency with the 5090 (reported, no verdict): the SIGN of (press_fast pick - press_arprop
e20) and of (press_count pick - press_fast pick) on 51-100. The registered E3 / E4 verdicts stay the 5090's.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e17_report.py
Writes outputs/fullft/E17_REPORT.json (and outputs/fullft/E17_VERDICT_table.json, a copy whose name the A40's
results push picks up).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("press_pair", HERE / "press_pair.py")
pp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pp)
spec = importlib.util.spec_from_file_location("e1_verdict", HERE / "e1_verdict.py")
e1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e1)
F = pp.R / "outputs/fullft"
RUNS = {"press_arprop": ("e10", "e20", "e30"), "press_ar": ("e30",), "press_fast": ("e10", "e20", "e30"),
        "press_count": ("e10", "e20", "e30")}


def main():
    seeds = e1.seeds_of("press_button", 100) or []
    first, second = set(str(s) for s in seeds[:50]), set(str(s) for s in seeds[50:])
    table, picks = {}, {}
    for run, tags in RUNS.items():
        for tag in tags:
            label = f"{run}_{tag}"
            try:
                st = pp.stages("e17", label)
            except Exception as error:                # noqa: BLE001
                print(f"{label}: no stages ({error})")
                continue
            row = {}
            for part, keep in (("1-50", first), ("51-100", second)):
                d = {s: v for s, v in st.items() if str(s) in keep}
                row[part] = {"n": len(d), "success": sum(bool(v.get("success")) for v in d.values()),
                             "first_right": sum(v.get("n1_error") == 0 for v in d.values())}
            row["_by_seed"] = {str(s): bool(v.get("success")) for s, v in st.items()}
            table[label] = row
            print(f"{label:18s} 1-50: {row['1-50']['success']:2d}/{row['1-50']['n']:2d} (first right {row['1-50']['first_right']:2d})"
                  f"   51-100: {row['51-100']['success']:2d}/{row['51-100']['n']:2d} (first right {row['51-100']['first_right']:2d})")
        cands = [(table[f"{run}_{t}"]["1-50"]["success"], table[f"{run}_{t}"]["1-50"]["first_right"], int(t[1:]), t)
                 for t in tags if f"{run}_{t}" in table and table[f"{run}_{t}"]["1-50"]["n"] >= 48]
        if cands:
            picks[run] = max(cands)[3]
    print(f"P-SEL picks (1-50): {picks}")

    def diff(a, b):
        A, B = table.get(a, {}).get("_by_seed", {}), table.get(b, {}).get("_by_seed", {})
        common = [s for s in second if s in A and s in B]
        if len(common) < 48:
            return None
        x, y = sum(A[s] for s in common), sum(B[s] for s in common)
        only_a, only_b = sum(A[s] and not B[s] for s in common), sum(B[s] and not A[s] for s in common)
        return {"a": a, "b": b, "n": len(common), "a_success": x, "b_success": y, "diff": x - y,
                "only_a": only_a, "only_b": only_b, "p": pp.sign_p(only_a, only_b)}
    comps = {}
    if "press_fast" in picks:
        comps["E3 analogue"] = diff(f"press_fast_{picks['press_fast']}", "press_arprop_e20")
    if "press_count" in picks and "press_fast" in picks:
        comps["E4 analogue"] = diff(f"press_count_{picks['press_count']}", f"press_fast_{picks['press_fast']}")
    for k, v in comps.items():
        print(f"{k} on 51-100 (A40, descriptive): {v}")
    for v in table.values():
        v.pop("_by_seed", None)
    out = {"table": table, "picks": picks, "comparisons": comps}
    (F / "E17_REPORT.json").write_text(json.dumps(out, indent=1) + "\n")
    (F / "E17_VERDICT_table.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
