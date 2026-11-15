"""Registered Press verdict, plan v11/v12 D.4 S-C(a) and (c). Judging machine chosen by the user 11-15 15:33 (option A,
before any press_ar result existed): the 5090, both arms on the same pipeline and the same official scenes (bank order,
the first N press_button scenes every compared model finished). The A100 re-checks the deciding pair when it has time
(descriptive). Code written 11-15 16:10, before any press_ar result. Read-only for the episodes.

  (a) ledger useful on Press: the better of the two ledger designs (AR+PROP = press_arprop, AR+EV = press_arev) has
      success >= AR + 20 points, exact two-sided sign test on the discordant scenes p < 0.05
  floor: at least one of the three models >= 30% success, else NO VERDICT (all on the floor; go to the failure funnel)
  (c) choice of the ledger: PROP and EV within 5 points -> PROP (cheaper), else the higher one
  With only PROP finished: PROP passing (a) is final (the better one is at least PROP); PROP failing -> WAIT FOR AREV.

  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_verdict.py --folder closed_loop/g1 \
      --prop press_arprop_e30 --control press_ar_e30 [--ev press_arev_e30] [--n 50]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
TASK = "press_button"


def bank_order():
    order = []
    for f in sorted((O / f"closed_loop/scenes_seed42_n100_{TASK}").glob("*.json")):
        v = json.loads(f.read_text())
        sc = v.get("scenes") if isinstance(v, dict) else v
        order += [str(s["seed"]) for s in (sc if isinstance(sc, list) else []) if s.get("task") == TASK]
    return order


def results(root, label):
    out = {}
    for d in sorted((root / label / "on" / TASK).glob("seed_*")):
        r = d / "result.json"
        if d.name.split("_", 1)[1].isdigit() and r.exists():
            out[d.name.split("_", 1)[1]] = bool(json.loads(r.read_text()).get("success"))
    return out


def sign_p(a, b):
    n, k = a + b, min(a, b)
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True)
    ap.add_argument("--prop", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--ev", default="")
    ap.add_argument("--n", type=int, default=50)
    args = ap.parse_args()
    root = Path(args.folder) if args.folder.startswith("/") else O / args.folder
    arms = {"PROP": args.prop} | ({"EV": args.ev} if args.ev else {})
    res = {k: results(root, v) for k, v in arms.items()}
    ctrl = results(root, args.control)
    present = {k: v for k, v in res.items() if v}
    seeds = [s for s in bank_order() if s in ctrl and all(s in v for v in present.values())][:args.n]
    report = {"control": args.control, "arms": arms, "n": len(seeds), "required_n": args.n, "seeds": seeds}
    if len(seeds) < args.n or "PROP" not in present:
        report["verdict"] = f"NOT READY ({len(seeds)} common finished scenes of {args.n})"
        print(report["verdict"])
    else:
        n = len(seeds)
        sc = sum(ctrl[s] for s in seeds)
        rows = {}
        for k in present:
            sa = sum(res[k][s] for s in seeds)
            oa = sum(res[k][s] and not ctrl[s] for s in seeds)
            oc = sum(ctrl[s] and not res[k][s] for s in seeds)
            rows[k] = {"label": arms[k], "success": sa, "only_arm": oa, "only_control": oc, "sign_p": sign_p(oa, oc),
                       "passes_a": sa >= sc + 0.20 * n and sign_p(oa, oc) < 0.05}
            print(f"{k} {arms[k]}: success {sa}/{n} vs AR {args.control} {sc}/{n}; only arm {oa}, only AR {oc}, "
                  f"sign p {sign_p(oa, oc):.4f}; (a) {'met' if rows[k]['passes_a'] else 'not met'}")
        best = max(rows, key=lambda k: (rows[k]["success"], k == "PROP"))
        floor = max([sc] + [r["success"] for r in rows.values()]) >= 0.30 * n
        if "EV" in rows:
            choice = "PROP" if abs(rows["PROP"]["success"] - rows["EV"]["success"]) <= 0.05 * n else best
        else:
            choice = None
        if not floor:
            verdict = "NO VERDICT (floor: no model >= 30%; go to the failure funnel)"
        elif rows[best]["passes_a"]:
            verdict = f"LEDGER USEFUL ON PRESS (better design {best})"
        elif "EV" not in rows:
            verdict = "WAIT FOR AREV (PROP alone does not meet (a))"
        else:
            verdict = "LEDGER NOT USEFUL ON PRESS"
        report.update({"control_success": sc, "arms_result": rows, "better": best, "floor_met": floor,
                       "choice_c": choice, "verdict": verdict})
        print(f"PRESS VERDICT: {verdict}" + (f"; (c) choice {choice}" if choice else ""))
    out = O / "report" / f"PRESS_VERDICT_{args.prop}_vs_{args.control}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
