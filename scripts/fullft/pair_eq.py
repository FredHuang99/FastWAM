"""Paired same-scene comparison of two closed-loop runs, with the plan v12 readings (Opus checklist 6; AL1-AL7).

Side A = the run being tested (e.g. the 5090, or the A100 with another denoiser); side B = the reference (the A100's
standard pipeline). Each side is either episode folders on this machine or a stage JSON exported on another machine
(scripts/memory_v2/migrate/export_stages.py; relayed through hhyfred/memwam-diag-v1):
  --a-folders F [F ...] --a-label L [--a-mode on]     |  --a-json PATH
  --b-folders ...                                     |  --b-json PATH
Per task (scenes present on both sides): paired progress difference A - B (mean, 95 % bootstrap CI), the task's key
stage (put_back_block: lifted; swap_blocks: s1), success counts and the discordant split (exact sign test).

Readings (--rule; written in plan v12 F.1 before any of these runs):
  n1   (N1 / AL3 / AL4'): per task |mean| <= 0.05 and CI contains 0, and A's key stage >= 18/20 (scaled: >= 0.9 n);
       floor: B's key stage >= the same count. EQUIVALENT only if every task passes.
  al4  (AL4, new base model, 50 + 50): per task (1) |mean| <= 0.05 and CI contains 0; (2) key stage >= 45/50 on BOTH
       sides (>= 0.9 n); (3) |success A - success B| <= 5/50 (<= 0.1 n). Floor: B success >= 10/50 (>= 0.2 n), else that
       task gives no verdict.
  al5  (AL5, A100 with OIDN 2.3.3 vs the A100 standard): per task CAUSE = mean <= -0.05 and CI upper < 0; NOT CAUSE =
       |mean| <= 0.05 and CI contains 0; else UNDETERMINED. Floor: B's key stage >= 18/20 (>= 0.9 n).
  al7  (AL7, weak tasks): tasks with a progress measure: (1) of al4 and |success diff| <= max(3, round(0.1 n)); tasks
       without one: discordant sign test p >= 0.05 and the same success bound. Floor: B finished >= 0.96 n and B success
       between 0.1 n and 0.9 n.
  report  numbers only.
Writes outputs/fullft/align/PAIR_<name>_<time>.json; the last line starts with "PAIR VERDICT".
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/pair_eq.py --name al5 --rule al5 \
     --a-folders closed_loop/al5 --a-label x7_al5_oidn233 \
     --b-folders closed_loop/official/put_x7_s0 closed_loop/official/put_x7_s1 --b-label a2C6_e6 --tasks put_back_block
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("queue5", HERE.parent / "memory_v2" / "queue5.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)

BJ = timezone(timedelta(hours=8))
KEY = {"put_back_block": "lifted", "swap_blocks": "s1"}
OUT = Path(os.environ.get("ALIGN_OUT", "/workspace/FastWAM-memory2/outputs/fullft/align"))


def side(folders, label, mode, path, tasks):
    """{task: {seed: {"progress", "success", <stage flags>}}} of one side."""
    rows = {}
    if path:
        data = json.loads(Path(q.resolve(path)).read_text(encoding="utf-8"))
        for task, eps in data["episodes"].items():
            rows[task] = {str(s): dict(r) for s, r in eps.items()}
    else:
        eps = q.episodes([str(q.resolve(f)) for f in folders], label, modes=[mode])
        for (task, _mode, seed), a in eps.items():
            row = {k: v for k, v in a.items() if k != "dir" and isinstance(v, (bool, int, float, str))}
            row["progress"] = q.progress(task, a)
            rows.setdefault(task, {})[str(seed)] = row
    return {t: r for t, r in rows.items() if not tasks or t in tasks}


def compare(task, a, b):
    seeds = sorted(set(a) & set(b), key=int)
    n = len(seeds)
    out = {"task": task, "n": n, "a_scenes": len(a), "b_scenes": len(b),
           "a_unpaired": len(set(a) - set(b)), "b_unpaired": len(set(b) - set(a))}
    if not n:
        return out
    diffs = [float(a[s]["progress"]) - float(b[s]["progress"]) for s in seeds]
    ci = q.bootstrap_ci(diffs)
    sa = sum(bool(a[s].get("success")) for s in seeds)
    sb = sum(bool(b[s].get("success")) for s in seeds)
    only_a = sum(bool(a[s].get("success")) and not b[s].get("success") for s in seeds)
    only_b = sum(bool(b[s].get("success")) and not a[s].get("success") for s in seeds)
    out.update(mean_a=q.mean(float(a[s]["progress"]) for s in seeds), mean_b=q.mean(float(b[s]["progress"]) for s in seeds),
               delta=q.mean(diffs), ci=[float(ci[0]), float(ci[1])], success_a=sa, success_b=sb,
               only_a=only_a, only_b=only_b, sign_p=q.sign_p(only_a, only_b), seeds=seeds)
    key = KEY.get(task)
    if key:
        out.update(key=key, key_a=sum(bool(a[s].get(key)) for s in seeds), key_b=sum(bool(b[s].get(key)) for s in seeds))
    return out


def reading(rule, c):
    """(label, ok_or_None, note) for one task; ok None = no verdict for this task."""
    n = c["n"]
    if not n:
        return "NO PAIRS", None, "no scene on both sides"
    within = abs(c["delta"]) <= 0.05 and c["ci"][0] <= 0 <= c["ci"][1]
    key_need = math.ceil(0.9 * n)
    if rule == "n1":
        if "key_b" in c and c["key_b"] < key_need:
            return "FLOOR NOT MET", None, f"B {c['key']} {c['key_b']}/{n} < {key_need}"
        ok = within and (c.get("key_a", n) >= key_need)
        return ("equivalent" if ok else "NOT equivalent"), ok, ""
    if rule == "al4":
        if c["success_b"] < math.ceil(0.2 * n):
            return "FLOOR NOT MET", None, f"B success {c['success_b']}/{n} < {math.ceil(0.2 * n)}"
        ok2 = "key_a" not in c or (c["key_a"] >= key_need and c["key_b"] >= key_need)
        ok3 = abs(c["success_a"] - c["success_b"]) <= round(0.1 * n)
        ok = within and ok2 and ok3
        return ("equivalent" if ok else "NOT equivalent"), ok, f"(1) {within} (2) {ok2} (3) {ok3}"
    if rule == "al5":
        if "key_b" in c and c["key_b"] < key_need:
            return "FLOOR NOT MET", None, f"B {c['key']} {c['key_b']}/{n} < {key_need}"
        if c["delta"] <= -0.05 and c["ci"][1] < 0:
            return "CAUSE (the denoiser version lowers the A100's own closed loop)", True, ""
        if within:
            return "NOT CAUSE", False, ""
        return "UNDETERMINED", None, ""
    if rule == "al7":
        fin_b = c["b_scenes"]
        if fin_b < math.ceil(0.96 * n) or not (0.1 * n <= c["success_b"] <= 0.9 * n):
            return "FLOOR NOT MET", None, f"B success {c['success_b']}/{n}"
        bound = max(3, round(0.1 * n))
        ok_s = abs(c["success_a"] - c["success_b"]) <= bound
        ok = (within and ok_s) if "delta" in c else (c["sign_p"] >= 0.05 and ok_s)
        return ("equivalent" if ok else "NOT equivalent"), ok, ""
    return "report", None, ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for s in ("a", "b"):
        ap.add_argument(f"--{s}-folders", nargs="*", default=[])
        ap.add_argument(f"--{s}-label", default="")
        ap.add_argument(f"--{s}-mode", default="on")
        ap.add_argument(f"--{s}-json", default="")
    ap.add_argument("--tasks", nargs="*", default=[])
    ap.add_argument("--rule", default="report", choices=("n1", "al4", "al5", "al7", "report"))
    ap.add_argument("--name", required=True)
    args = ap.parse_args()
    a = side(args.a_folders, args.a_label, args.a_mode, args.a_json, args.tasks)
    b = side(args.b_folders, args.b_label, args.b_mode, args.b_json, args.tasks)
    tasks = sorted(set(a) | set(b))
    report = {"name": args.name, "rule": args.rule, "a": vars(args), "tasks": {}, "time": f"{datetime.now(BJ):%F %T}"}
    oks = []
    print(f"PAIR {args.name}: rule {args.rule}; A = {args.a_json or args.a_folders} {args.a_label}; "
          f"B = {args.b_json or args.b_folders} {args.b_label}")
    for task in tasks:
        c = compare(task, a.get(task, {}), b.get(task, {}))
        label, ok, note = reading(args.rule, c)
        c.update(reading=label, ok=ok, note=note)
        report["tasks"][task] = {k: v for k, v in c.items() if k != "seeds"} | {"seeds": c.get("seeds", [])}
        oks.append(ok)
        if not c["n"]:
            print(f"  {task}: A {c['a_scenes']} scenes, B {c['b_scenes']}, paired 0 -> {label}")
            continue
        keys = f"; {c['key']} A {c['key_a']}/{c['n']} B {c['key_b']}/{c['n']}" if "key" in c else ""
        print(f"  {task}: paired n={c['n']} (unpaired A {c['a_unpaired']}, B {c['b_unpaired']}); progress A "
              f"{c['mean_a']:.3f} B {c['mean_b']:.3f}; delta {c['delta']:+.3f} CI [{c['ci'][0]:+.3f}, {c['ci'][1]:+.3f}]"
              f"{keys}; success A {c['success_a']} B {c['success_b']} (only A {c['only_a']}, only B {c['only_b']}, "
              f"sign p {c['sign_p']:.3f}) -> {label} {note}")
    if args.rule == "report":
        verdict = "REPORT ONLY"
    elif args.rule == "al5":
        verdict = "; ".join(f"{t}: {report['tasks'][t]['reading']}" for t in tasks) or "NO PAIRS"
    elif not oks or any(o is None for o in oks):
        verdict = "NO VERDICT (" + ", ".join(f"{t}: {report['tasks'][t]['reading']}" for t in tasks
                                              if report["tasks"][t]["ok"] is None) + ")"
    else:
        verdict = "EQUIVALENT" if all(oks) else "NOT EQUIVALENT"
    report["verdict"] = verdict
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"PAIR_{args.name}_{datetime.now(BJ):%Y%m%d_%H%M}.json"
    path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"report: {path}")
    print(f"PAIR VERDICT {args.name}: {verdict}")


if __name__ == "__main__":
    main()
