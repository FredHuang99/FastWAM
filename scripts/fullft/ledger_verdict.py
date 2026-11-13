"""Registered AR+PROP vs AR verdict (rule agreed by the user 11-13 13:21; written as code 11-13 18:20, before any ar2_prop
result exists). Same machine, same official scenes (bank order, first N swap and put scenes both arms finished).
Read-only for the episodes.

  swap, paired on the same scenes:
    USEFUL   success(arm) >= success(control) + 8, exact two-sided sign test on the discordant scenes p < 0.05,
             and "kept moving after s3" (press_gap) of the arm <= 8
    NULL     |success(arm) - success(control)| <= 3
    EXTEND   otherwise: no verdict; both arms are extended to swap scenes 51-100 and the rule is applied to 1-100
  put:   arm success >= 48/50, else the line says HARMS PUT (reported next to the swap verdict)
  floor: both arms complete the three moves (s3) in >= 40/50 swap scenes, else NO VERDICT (an execution problem)
Judging machine: the 5090; since AL4 (e30, 11-13 18:08) is NOT EQUIVALENT, the A100 (registered fallback). The +8 is
relative to the control on the judging machine; the kept-moving bound (8) is absolute.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/ledger_verdict.py --folder closed_loop/g1 --arm ar2_prop_e30 \
      --control ar_2task_e30 [--n 50]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("press_gap", HERE / "press_gap.py")
pg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pg)
cls = pg.cls
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")


def bank_order(task):
    order = []
    for f in sorted((O / f"closed_loop/scenes_seed42_n100_{task}").glob("*.json")):
        v = json.loads(f.read_text())
        sc = v.get("scenes") if isinstance(v, dict) else v
        order += [str(s["seed"]) for s in (sc if isinstance(sc, list) else []) if s.get("task") == task]
    return order


def episodes(root, label, task):
    out = {}
    for d in sorted((root / label / "on" / task).glob("seed_*")):
        if not cls.SEED_DIR.fullmatch(d.name) or not (d / "result.json").exists():
            continue
        res = json.loads((d / "result.json").read_text())
        row = {"success": bool(res.get("success"))}
        if (d / "executed_actions.jsonl").exists():
            snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
            if len(snaps) >= 2 and snaps[0]:
                if task == "swap_blocks":
                    row["s3"] = bool(cls.analyse_swap(snaps, counters)["s3"])
                    row["case"] = pg.swap_case(snaps, counters)[0] if row["s3"] else None
        out[d.name.split("_", 1)[1]] = row
    return out


def sign_p(a, b):
    n, k = a + b, min(a, b)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--control", required=True)
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--progress", action="store_true", help="e10 / e20: the same numbers, no verdict")
    args = ap.parse_args()
    root = Path(args.folder) if args.folder.startswith("/") else O / args.folder
    lines, report = [], {"arm": args.arm, "control": args.control, "n": args.n}
    sw_a, sw_c = episodes(root, args.arm, "swap_blocks"), episodes(root, args.control, "swap_blocks")
    seeds = [s for s in bank_order("swap_blocks") if s in sw_a and s in sw_c][:args.n]
    sa = sum(sw_a[s]["success"] for s in seeds)
    sc = sum(sw_c[s]["success"] for s in seeds)
    only_a = sum(sw_a[s]["success"] and not sw_c[s]["success"] for s in seeds)
    only_c = sum(sw_c[s]["success"] and not sw_a[s]["success"] for s in seeds)
    p = sign_p(only_a, only_c)
    kept_a = sum(sw_a[s].get("case") == "kept moving" for s in seeds)
    kept_c = sum(sw_c[s].get("case") == "kept moving" for s in seeds)
    s3_a = sum(bool(sw_a[s].get("s3")) for s in seeds)
    s3_c = sum(bool(sw_c[s].get("s3")) for s in seeds)
    lines.append(f"swap: paired n={len(seeds)}; success {args.arm} {sa} vs {args.control} {sc} (only arm {only_a}, only "
                 f"control {only_c}, sign p {p:.4f}); kept moving after s3 {kept_a} vs {kept_c}; s3 {s3_a} vs {s3_c}")
    pu_a, pu_c = episodes(root, args.arm, "put_back_block"), episodes(root, args.control, "put_back_block")
    pseeds = [s for s in bank_order("put_back_block") if s in pu_a and s in pu_c][:args.n]
    pa = sum(pu_a[s]["success"] for s in pseeds)
    pc = sum(pu_c[s]["success"] for s in pseeds)
    lines.append(f"put: paired n={len(pseeds)}; success {args.arm} {pa} vs {args.control} {pc}")
    floor_n = math.ceil(0.8 * len(seeds))                       # 40 of 50
    if args.progress:
        verdict = "PROGRESS ONLY (no verdict before e30)"
    elif len(seeds) < args.n or len(pseeds) < args.n:
        verdict = f"NO VERDICT (only {len(seeds)} swap / {len(pseeds)} put paired scenes of {args.n})"
    elif s3_a < floor_n or s3_c < floor_n:
        verdict = f"NO VERDICT (floor: s3 {s3_a} / {s3_c} < {floor_n}: an execution problem, not memory)"
    elif sa >= sc + 8 and p < 0.05 and kept_a <= 8:
        verdict = "USEFUL"
    elif abs(sa - sc) <= 3:
        verdict = "NULL"
    else:
        verdict = "EXTEND (no verdict: both arms to swap scenes 51-100, rule on 1-100)"
    put_line = "put kept" if pa >= math.ceil(0.96 * len(pseeds)) else "HARMS PUT"
    report.update(swap={"seeds": seeds, "success_arm": sa, "success_control": sc, "only_arm": only_a,
                        "only_control": only_c, "sign_p": p, "kept_arm": kept_a, "kept_control": kept_c,
                        "s3_arm": s3_a, "s3_control": s3_c},
                  put={"n": len(pseeds), "success_arm": pa, "success_control": pc}, verdict=verdict, put_line=put_line)
    for s in lines:
        print(s)
    print(f"LEDGER VERDICT {args.arm} vs {args.control}: {verdict}; {put_line}")
    out = O / "report" / f"LEDGER_{'PROGRESS' if args.progress else 'VERDICT'}_{args.arm}_vs_{args.control}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
