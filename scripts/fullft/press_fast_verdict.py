"""press_fast verdict (rule registered 11-16 19:55 BJ, Status 1116 sections IX.3 / X, before press_fast was trained;
this code written 11-17 15:10 BJ, before any press_fast export exists; read-only).

press_fast = press_arprop's recipe and data with the ledger write lag 0 and the event thresholds of the CPU sweep
(deviation 36). Its epoch is chosen with the P-SEL rule (press_select.py --run press_fast, scenes 1-50, closed_loop/g1);
the chosen export runs on the held-out scenes 51-100 (closed_loop/sel) and is paired with sel:press_arprop_e20
(the ledger model P-SEL chose: 8/50 there). Reading:
  success >= 18/50 and paired sign test p < 0.05  -> BETTER (the timely ledger is better)
  success <= 10/50                                 -> NO IMPROVEMENT
  otherwise                                        -> PARTIAL
  floor: both arms have >= 48 finished episodes on scenes 51-100, else NO READING.
Any claim from press_fast uses scenes 51-100 only. Descriptive extras are printed by press_ledger_audit.py / press_errors.py.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_fast_verdict.py --tag e20
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("press_select", HERE / "press_select.py")
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True, help="the epoch press_select.py chose for press_fast")
    ap.add_argument("--ref", default="press_arprop_e20")
    args = ap.parse_args()
    new_label = f"press_fast_{args.tag}"
    a, b = ps.results("sel", new_label), ps.results("sel", args.ref)
    common = sorted(set(a) & set(b))
    if len(a) < 48 or len(b) < 48:
        print(f"PRESS_FAST VERDICT: NO READING ({new_label} {len(a)}, {args.ref} {len(b)} finished episodes on 51-100)")
        return 2
    s_new, s_ref = sum(a[s] for s in common), sum(b[s] for s in common)
    only_new = sum(a[s] and not b[s] for s in common)
    only_ref = sum(b[s] and not a[s] for s in common)
    p = ps.sign_p(only_new, only_ref)
    reading = ("BETTER" if s_new >= 18 and p < 0.05 else "NO IMPROVEMENT" if s_new <= 10 else "PARTIAL")
    print(f"press_fast {args.tag} vs {args.ref}, scenes 51-100, paired n={len(common)}: success {s_new} vs {s_ref};"
          f" only press_fast {only_new}, only reference {only_ref}, sign p {p:.4f}")
    print(f"PRESS_FAST VERDICT: {reading}")
    out = ps.R / "outputs/fullft/PRESS_FAST_VERDICT.json"
    out.write_text(json.dumps({"tag": args.tag, "n": len(common), "success": s_new, "reference": s_ref,
                               "only_new": only_new, "only_ref": only_ref, "sign_p": p, "reading": reading}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
