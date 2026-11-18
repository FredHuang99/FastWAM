"""Plan v14 E5b CLOCK-put verdict (registered by Fable 11-18 in plan v14 section 3, approved by the user 18:33; this
script written 11-18 19:00 BJ, before any closed-loop result of the clock model ar2_clock e30 exists). Read-only.

Hypothesis (plan v14 1.2 (b)): E2's rule C says time alone predicts progress in the put demonstrations, not in swap.
So the clock model under a pause errs on put and not on swap. A40, closed_loop/e5: labels ar2_clock_e30_e1pause_vis /
_hid, put_back_block scenes 1-50, E1's put injection and validity (scripts/fullft/e1_verdict.py).
Registered reading (plan v14 E5b, verbatim in meaning):
  Delta (vis - hid, valid pairs) <= -8/50 with sign p < 0.05 -> CLOCK READ ON PUT; Delta >= -5/50 -> NOT ON PUT;
  otherwise undetermined. Floors: >= 45 valid pairs; hidden arm >= 40/50 successes.
  Audit: rule C's prediction on put = "errs"; CLOCK READ ON PUT = hit, NOT ON PUT = miss (how a hit counts in E2's
  law verdict follows scripts/fullft/E2_PREDICTIONS_REGISTERED.txt).
  Read together with E5 (swap; outputs/fullft/E5_VERDICT.json) by the table of plan v14 E5b (printed below).
  After CLOCK READ ON PUT only: timestamps x1.5 and x0.5, put 1-50, no stress; report only whether the failure
  direction flips (--scales).
Descriptive (new reporting used by every stress card from plan v14 on): the share of the clock tokens that point into
the injected frames at the first decision after the injection (visible arm), i.e. how much of the clock memory the
pause occupies.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e5b_verdict.py [--scales]
Writes outputs/fullft/E5B_VERDICT.json (E5B_SCALES.json with --scales).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e1 = module("e1_verdict", "e1_verdict.py")
pg = module("press_gap", "press_gap.py")
cls = pg.cls
CLOCK = "ar2_clock_e30"
TASK = "put_back_block"
TABLE = {
    ("NOT REPRODUCED", "CLOCK READ ON PUT"): "best case: the clock is read only where the audit says time suffices "
                                             "(plan v14 E5b row 1)",
    ("INDEX MATTERS", "CLOCK READ ON PUT"): "the clock is read on both tasks; the audit was conservative on swap "
                                            "(no prediction there, not a miss) (row 2)",
    ("INDEX MATTERS", "NOT ON PUT"): "against the audit: rule C misses; the time table stays, no 'predictable where' "
                                     "(row 3)",
    ("NOT REPRODUCED", "NOT ON PUT"): "the clock model does not read the clock: if its no-stress swap is also >= 95/100 "
                                      "the weight moves to content (E9) and counting -> SWITCH TO FABLE (row 4)",
}


def put_class(d: Path):
    """success / the put failure class of press_gap.py (pressed, skipped -> returned, skipped -> stuck) / never centred."""
    res = json.loads((d / "result.json").read_text())
    if res.get("success"):
        return "success"
    if not (d / "executed_actions.jsonl").exists():
        return "unclassified"
    snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
    if len(snaps) < 2 or not snaps[0]:
        return "unclassified"
    case, _ = pg.put_case(snaps, counters)
    return case or "never centred"


def clock_share(d: Path):
    """Share of the clock tokens inside the injected frames at the first decision after the injection (visible arm)."""
    st = [json.loads(x) for x in (d / "stress.jsonl").read_text().splitlines() if x.strip()] if (d / "stress.jsonl").exists() else []
    if not st or st[0].get("arm") != "history":
        return None
    lo, hi = int(st[0]["frame"]), int(st[0]["frame"]) + int(st[0]["k"]) - 1
    for line in (d / "decisions.jsonl").read_text().splitlines() if (d / "decisions.jsonl").exists() else []:
        if not line.strip():
            continue
        x = json.loads(line)
        if int(x.get("frame_id", -1)) <= hi:
            continue
        frames = [int(e[0]) for e in x.get("ledger") or []]
        return sum(lo <= f <= hi for f in frames) / len(frames) if frames else None
    return None


def scales(folder):
    seeds = e1.seeds_of(TASK, 50)
    rows = {}
    for lab in (CLOCK, f"{CLOCK}_ts1.5", f"{CLOCK}_ts0.5"):
        kinds = Counter()
        for s in seeds:
            d = folder / lab / "on" / TASK / f"seed_{s}"
            if (d / "result.json").exists():
                kinds[put_class(d)] += 1
        rows[lab] = dict(kinds)
        print(f"{lab:24s} put 1-50: {dict(kinds)}")
    def dominant(k):
        f = {a: b for a, b in k.items() if a != "success"}
        return max(f, key=f.get) if f else "none"
    d = {lab: dominant(v) for lab, v in rows.items()}
    flips = d[f"{CLOCK}_ts1.5"] != d[f"{CLOCK}_ts0.5"] and "none" not in (d[f"{CLOCK}_ts1.5"], d[f"{CLOCK}_ts0.5"])
    print(f"dominant failure class: {d}")
    print(f"FAILURE DIRECTION FLIPS between x1.5 and x0.5 on put: {'YES' if flips else 'NO'} (reported only)")
    (F / "E5B_SCALES.json").write_text(json.dumps({"rows": rows, "dominant": d, "flips": flips}, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=str(O / "e5"))
    ap.add_argument("--scales", action="store_true")
    args = ap.parse_args()
    folder = Path(args.folder)
    if args.scales:
        return scales(folder)
    seeds = e1.seeds_of(TASK, 50)
    vis = {s: e1.episode(folder, f"{CLOCK}_e1pause_vis", TASK, s) for s in seeds}
    hid = {s: e1.episode(folder, f"{CLOCK}_e1pause_hid", TASK, s) for s in seeds}
    pairs = [s for s in seeds if vis[s] and hid[s] and vis[s]["valid"] and hid[s]["valid"]]
    a = sum(vis[s]["success"] and not hid[s]["success"] for s in pairs)
    b = sum(hid[s]["success"] and not vis[s]["success"] for s in pairs)
    delta, p = a - b, e1.sign_p(a, b)
    hid_succ = sum(bool(hid[s] and hid[s]["success"]) for s in seeds)
    kinds = {arm: Counter(put_class(folder / f"{CLOCK}_e1pause_{arm}" / "on" / TASK / f"seed_{s}") for s in seeds
                          if (folder / f"{CLOCK}_e1pause_{arm}" / "on" / TASK / f"seed_{s}" / "result.json").exists())
             for arm in ("vis", "hid")}
    shares = [x for x in (clock_share(folder / f"{CLOCK}_e1pause_vis" / "on" / TASK / f"seed_{s}") for s in seeds) if x is not None]
    print(f"E5b put 1-50: finished vis {sum(1 for s in seeds if vis[s])}, hid {sum(1 for s in seeds if hid[s])}; "
          f"valid pairs {len(pairs)}; vis-only {a}, hid-only {b}; Delta {delta:+d}; sign p {p:.4f}; hidden successes {hid_succ}/50")
    for arm, k in kinds.items():
        print(f"  {arm}: {dict(k)}")
    if shares:
        print(f"  clock tokens inside the injected frames at the first decision after the pause (vis): mean "
              f"{sum(shares) / len(shares):.2f} over {len(shares)} episodes (descriptive)")
    if len(pairs) < 45:
        verdict = f"NO VERDICT (only {len(pairs)} valid pairs < 45)"
    elif hid_succ < 40:
        verdict = f"NO VERDICT (hidden arm {hid_succ}/50 < 40)"
    elif delta <= -8 and p < 0.05:
        verdict = "CLOCK READ ON PUT"
    elif delta >= -5:
        verdict = "NOT ON PUT"
    else:
        verdict = "UNDETERMINED"
    audit = {"CLOCK READ ON PUT": "rule C on put: HIT", "NOT ON PUT": "rule C on put: MISS"}.get(verdict, "rule C on put: no reading")
    print(f"E5b VERDICT: {verdict}; {audit}")
    e5 = json.loads((F / "E5_VERDICT.json").read_text())["verdict"] if (F / "E5_VERDICT.json").exists() else None
    row = TABLE.get((e5, verdict))
    print(f"with E5 (swap) = {e5}: {row or 'not a row of the plan v14 E5b table (one of them undetermined / no verdict)'}")
    (F / "E5B_VERDICT.json").write_text(json.dumps({
        "verdict": verdict, "audit": audit, "e5": e5, "row": row, "valid_pairs": len(pairs), "vis_only": a,
        "hid_only": b, "delta": delta, "p": p, "hidden_success": hid_succ,
        "classes": {k: dict(v) for k, v in kinds.items()},
        "clock_share_mean": (sum(shares) / len(shares)) if shares else None}, indent=1) + "\n")


if __name__ == "__main__":
    main()
