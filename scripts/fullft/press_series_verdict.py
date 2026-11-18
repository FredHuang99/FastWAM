"""Press-series verdicts on the 5090 for plan v13 E4 (press_count) and plan v14 E14 (press_v3c); written 11-18 18:40 BJ,
before any press_count or press_v3c closed-loop result exists. Read-only. The epoch of each run is chosen with the
P-SEL rule (press_select.py, scenes 1-50, closed_loop/g1); the chosen export runs on the held-out scenes 51-100
(closed_loop/sel) and is paired there with the reference run's chosen export (same machine).

E4 PRESS-count (registered by Fable 11-17 in plan v13 section 3, approved 15:40), reference = press_fast at the epoch
E3 chose (outputs/fullft/PRESS_FAST_VERDICT.json "tag"):
  new >= ref + 8 (successes on 51-100) with paired sign p < 0.05 -> COUNT HELPS; |new - ref| <= 4 -> NO EFFECT;
  otherwise PARTIAL. Floor: both >= 48/50 finished on 51-100, else NO READING.
  Counterfactuals (scenes 1-50, the chosen export, same noise as its g1 run; closed_loop/abl): MWAM_LEDGER=ordplus1 (every
  press entry's count code + 1, entries unchanged) and duppress (the latest press entry copied, code unchanged).
  Counted on the episodes whose first count was right without the change: share with the first count under by one.
  ordplus1 >= 60 % and duppress <= 20 % -> READS THE CODE; duppress >= 60 % and ordplus1 <= 20 % -> READS THE ENTRY
  COUNT; otherwise MIXED. (Floor added here, before any run: >= 10 such episodes, else NO READING.)
E14 PRESS-tau (registered by Fable 11-18 in plan v14 section 3, approved by the user 18:33), reference = press_count at
the epoch E4 chose:
  new >= ref + 8 with p < 0.05 -> TIMELY WRITER HELPS; |new - ref| <= 4 -> NO EFFECT; otherwise PARTIAL. Floor as E4.
  Also reported (no verdict word): new >= 25/50 -> "back in the workable range".
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_series_verdict.py --card E4 --new press_count_e20 --ref press_fast_e20
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_series_verdict.py --card E4cf --base press_count_e20
Writes outputs/fullft/PRESS_<card>_VERDICT.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ps = module("press_select", "press_select.py")
pp = module("press_pair", "press_pair.py")
F = ps.R / "outputs/fullft"
WORDS = {"E4": ("COUNT HELPS", "NO EFFECT", "PARTIAL"), "E14": ("TIMELY WRITER HELPS", "NO EFFECT", "PARTIAL")}


def paired(card, new, ref):
    a, b = ps.results("sel", new), ps.results("sel", ref)
    common = sorted(set(a) & set(b))
    out = {"card": card, "new": new, "ref": ref, "finished": [len(a), len(b)]}
    if len(a) < 48 or len(b) < 48:
        out["reading"] = f"NO READING (finished {len(a)} / {len(b)} < 48 on 51-100)"
    else:
        s_new, s_ref = sum(a[s] for s in common), sum(b[s] for s in common)
        only_new = sum(a[s] and not b[s] for s in common)
        only_ref = sum(b[s] and not a[s] for s in common)
        p = ps.sign_p(only_new, only_ref)
        helps, none, partial = WORDS[card]
        reading = helps if (s_new - s_ref >= 8 and p < 0.05) else none if abs(s_new - s_ref) <= 4 else partial
        out.update(n=len(common), success=s_new, reference=s_ref, only_new=only_new, only_ref=only_ref, sign_p=p,
                   reading=reading)
        if card == "E14":
            out["workable_range"] = s_new >= 25
        print(f"{card}: {new} vs {ref}, scenes 51-100, paired n={len(common)}: success {s_new} vs {s_ref}; "
              f"only new {only_new}, only reference {only_ref}, sign p {p:.4f}")
    print(f"{card} VERDICT: {out['reading']}" + (f"; >= 25/50: {out.get('workable_range')}" if card == "E14" else ""))
    return out


def counterfactuals(base):
    g = pp.stages("g1", base)
    cf = {k: pp.stages("abl", f"{base}_{k}") for k in ("ordplus1", "duppress")}
    right = [s for s, v in g.items() if v.get("n1_error") == 0]
    out = {"card": "E4cf", "base": base, "first_right_without_change": len(right)}
    shares = {}
    for k, d in cf.items():
        seen = [s for s in right if s in d]
        under = sum(d[s].get("n1_error") == -1 for s in seen)
        shares[k] = under / len(seen) if seen else None
        out[k] = {"episodes": len(seen), "under_by_one": under, "share": shares[k], **pp.numbers(d)}
        print(f"E4 counterfactual {k}: first count under by one in {under}/{len(seen)} of the episodes right without "
              f"the change; all episodes: {pp.numbers(d)}")
    if len(right) < 10 or any(v is None or out[k]["episodes"] < 10 for k, v in shares.items()):
        reading = f"NO READING (episodes with the first count right: {len(right)}; finished per counterfactual " \
                  f"{[out[k]['episodes'] for k in shares]})"
    elif shares["ordplus1"] >= 0.6 and shares["duppress"] <= 0.2:
        reading = "READS THE CODE"
    elif shares["duppress"] >= 0.6 and shares["ordplus1"] <= 0.2:
        reading = "READS THE ENTRY COUNT"
    else:
        reading = "MIXED"
    out["reading"] = reading
    print(f"E4 COUNTERFACTUAL READING: {reading}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--card", required=True, choices=("E4", "E14", "E4cf"))
    ap.add_argument("--new")
    ap.add_argument("--ref")
    ap.add_argument("--base")
    args = ap.parse_args()
    out = counterfactuals(args.base) if args.card == "E4cf" else paired(args.card, args.new, args.ref)
    (F / f"PRESS_{args.card}_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
