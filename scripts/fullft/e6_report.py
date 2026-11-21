"""Plan v13 E6 ROW-1 on the A40 (Fable 11-17, approved 15:40; this script written 11-18 17:40 BJ, before any closed-loop
result of these models exists). Read-only. A40, closed_loop/e6, official scenes 1-100 (bank order), no stress.

Battery (battery_try): the registered reading is plan v11 D.4 S-C (b), executed by Opus as plan v13 E6 says:
  (b) the ledger is useful on Battery: ledger - AR >= 15 points with an exact two-sided paired sign test p < 0.05,
      on scenes 1-50 (S-C: "各评 1-50 号场景"); 15 points of 50 scenes = 7.5 -> >= 8 more successes
  floor: at least one of the models >= 30 % on those scenes (>= 15/50), else no verdict (S-C: "都在地板上，转看漏斗")
  Models: battery_ar e30 (AR) and battery_arprop e30 (ledger, rule A, lag 4), both trained on the H100 (deviation 39:
  the two arms of a task on the same machine). S-C was written for the 30-frame-epoch models; e10 / e20 are not part of
  it. Scenes 51-100 and 1-100 are reported beside it (plan v13 E6: "A40 评官方场景 100 个"), no verdict.
  (S-C (c), the design choice, is replaced by G2' in plan v13 and not read here.)
Other tasks (rearrange_blocks, swap_T, later cover_blocks, blocks_ranking_try): numbers only (plan v13 E6), each to be
compared line by line with the E2 predictions (scripts/fullft/E2_PREDICTIONS_REGISTERED.txt) by Opus.
Implementation detail (11-18, before any result): with episodes missing on 1-50 the S-C (b) verdict waits until the
missing ones cannot change it.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e6_report.py [--labels battery_try:battery_ar_e30 ...]
Writes outputs/fullft/E6_REPORT.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
spec = importlib.util.spec_from_file_location("e1_verdict", HERE / "e1_verdict.py")
e1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e1)
DEFAULT = ["battery_try:battery_ar_e30", "battery_try:battery_arprop_e30", "rearrange_blocks:rearrange_ar_e30",
           "swap_T:swapT_ar_e30"]


def results(folder: Path, label: str, task: str, seeds):
    out = {}
    for s in seeds:
        res = folder / label / "on" / task / f"seed_{s}" / "result.json"
        if res.exists():
            out[s] = bool(json.loads(res.read_text()).get("success"))
    return out


def battery(folder):
    seeds = e1.seeds_of("battery_try", 100)
    if not seeds:
        print("battery_try: no scene bank here")
        return {"verdict": "NO BANK"}
    first = seeds[:50]
    ar, led = results(folder, "battery_ar_e30", "battery_try", first), results(folder, "battery_arprop_e30", "battery_try", first)
    common = sorted(set(ar) & set(led))
    a = sum(led[s] and not ar[s] for s in common)
    b = sum(ar[s] and not led[s] for s in common)
    p = e1.sign_p(a, b)
    s_ar, s_led = sum(ar[s] for s in common), sum(led[s] for s in common)
    missing = 50 - len(common)
    print(f"S-C (b) battery_try scenes 1-50: AR {s_ar}, ledger {s_led} on {len(common)} paired scenes "
          f"(finished AR {len(ar)}, ledger {len(led)}); ledger-only {a}, AR-only {b}, sign p {p:.4f}")
    if missing:
        best = max(s_ar, s_led) + missing
        verdict = ("NO VERDICT (floor: both < 15/50)" if best < 15
                   else f"WAIT ({missing} of scenes 1-50 not finished in both arms)")
    elif max(s_ar, s_led) < 15:
        verdict = "NO VERDICT (floor: both < 15/50 = 30 %)"
    elif s_led - s_ar >= 8 and p < 0.05:
        verdict = "LEDGER USEFUL ON BATTERY"
    else:
        verdict = "NOT SHOWN (S-C (b) not met)"
    print(f"S-C (b) VERDICT: {verdict}")
    desc = {}
    for name, part in (("51-100", seeds[50:]), ("1-100", seeds)):
        x, y = results(folder, "battery_ar_e30", "battery_try", part), results(folder, "battery_arprop_e30", "battery_try", part)
        c = sorted(set(x) & set(y))
        aa, bb = sum(y[s] and not x[s] for s in c), sum(x[s] and not y[s] for s in c)
        desc[name] = {"scenes": len(c), "ar": sum(x[s] for s in c), "ledger": sum(y[s] for s in c),
                      "ledger_only": aa, "ar_only": bb, "p": e1.sign_p(aa, bb)}
        print(f"  battery_try {name} (descriptive): AR {desc[name]['ar']}, ledger {desc[name]['ledger']} on {len(c)} "
              f"paired scenes; ledger-only {aa}, AR-only {bb}, sign p {desc[name]['p']:.4f}")
    return {"verdict": verdict, "scenes_1_50": {"scenes": len(common), "ar": s_ar, "ledger": s_led, "ledger_only": a,
                                                "ar_only": b, "p": p}, "descriptive": desc}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=str(O / "e6"))
    ap.add_argument("--labels", nargs="*", default=DEFAULT, help="task:label pairs to report (1-50, 51-100, 1-100)")
    ap.add_argument("--pairs", nargs="*", default=[],
                    help="11-22: task:labelA:labelB, descriptive paired counts on 1-100 (A-only, B-only, sign p); no word")
    args = ap.parse_args()
    folder = Path(args.folder)
    rows = {}
    for item in args.labels:
        task, label = item.split(":", 1)
        seeds = e1.seeds_of(task, 100) or []
        line = {}
        for name, part in (("1-50", seeds[:50]), ("51-100", seeds[50:]), ("1-100", seeds)):
            r = results(folder, label, task, part)
            line[name] = [sum(r.values()), len(r)]
        rows[item] = line
        print(f"{task:18s} {label:22s} " + "  ".join(f"{k}: {v[0]}/{v[1]}" for k, v in line.items())
              + ("" if seeds else "  (no scene bank)"))
    pairs = {}
    for item in args.pairs:
        task, la, lb = item.split(":")
        seeds = e1.seeds_of(task, 100) or []
        x, y = results(folder, la, task, seeds), results(folder, lb, task, seeds)
        c = sorted(set(x) & set(y))
        aa, bb = sum(x[s] and not y[s] for s in c), sum(y[s] and not x[s] for s in c)
        pairs[item] = {"scenes": len(c), la: sum(x[s] for s in c), lb: sum(y[s] for s in c), "a_only": aa, "b_only": bb,
                       "p": e1.sign_p(aa, bb) if c else None}
        print(f"pair {item} (descriptive, 1-100): {pairs[item]}")
    bat = battery(folder)
    (F / "E6_REPORT.json").write_text(json.dumps({"rows": rows, "pairs": pairs, "battery_sc_b": bat}, indent=1) + "\n")


if __name__ == "__main__":
    main()
