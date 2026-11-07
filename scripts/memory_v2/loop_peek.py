"""Read-only look at closed-loop episodes (11-07, after S4 on the 5090): no state, verdict, SUMMARY.json or autopsy is
written, so it is safe on a RUNNING task's folder.

  --folder F --label L          stage table of label L's finished episodes in F (all modes), plus per-episode means
                                from result.json (decisions, policy seconds, wall seconds, executed targets, termination)
                                and the open errors (true seed_<n> folders with ERROR.json and no result.json; the
                                renamed seed_<n>_interrupted_* folders of earlier attempts are counted apart)
  --ref-folder R ... --ref-label RL --ref-mode M
                                the same table for the reference on the seeds both have, and the paired progress
                                difference (this - reference) per task and pooled
  --first TASK:SEED             the first 8 executed targets (rad / gripper) of that episode in F, to compare the
                                same scene across machines (the per-decision noise is CPU-seeded, so the first
                                decision depends only on frame 0 and the numerics)
  --out FILE                    also write the text there (default: report/LOOP_PEEK_<label>_<time>.txt)

  PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/loop_peek.py --folder closed_loop/s2_steps2 --label x7_steps2_exec8
Folders are relative to outputs/memory_v2 unless absolute.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import statistics
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("queue5", HERE / "queue5.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
BJ = timezone(timedelta(hours=8))
LINES = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LINES.append(line)


def table(eps, title):
    say(f"\n== {title}")
    m = q.stage_table(eps)
    for key in sorted(m):
        cell = m[key]
        task = key.split("/")[0]
        stages = " ".join(f"{k}={cell.get(k, 0)}" for k in q.STAGES.get(task, ()))
        say(f"  {key:<28} n={cell['n']:<4} progress={cell['progress_mean']:.3f}  {stages}")
    return m


def result_means(folder, label):
    rows = []
    for res in sorted(q.resolve(folder).glob(f"{label}/*/*/seed_*/result.json")):
        if re.fullmatch(r"seed_\d+", res.parent.name):
            rows.append(q.read_json(res, {}))
    if not rows:
        say("  no result.json")
        return
    by = {}
    for r in rows:
        by.setdefault((r.get("mode"), r.get("task")), []).append(r)
    for (mode, task), rs in sorted(by.items()):
        def mean(key):
            xs = [r[key] for r in rs if isinstance(r.get(key), (int, float))]
            return f"{statistics.mean(xs):.1f}" if xs else "-"
        term = Counter(str(r.get("termination")) for r in rs).most_common(3)
        say(f"  {mode}/{task}: n={len(rs)} success={sum(bool(r.get('success')) for r in rs)} decisions={mean('decisions')} "
            f"targets={mean('executed_targets')} policy_s={mean('policy_seconds_mean')} wall_s={mean('wall_seconds')} "
            f"steps={sorted({r.get('steps') for r in rs})} termination={term}")


def errors(folder, label):
    root = q.resolve(folder)
    open_, renamed = [], 0
    for e in root.glob(f"{label}/*/*/seed_*/ERROR.json"):
        if (e.parent / "result.json").exists():
            continue
        if re.fullmatch(r"seed_\d+", e.parent.name):
            open_.append(e)
        else:
            renamed += 1
    kinds = Counter()
    for e in open_:
        text = (q.read_json(e, {}) or {}).get("error", "")
        kinds[re.sub(r"\d+", "N", text.strip().splitlines()[-1] if text.strip() else "?")[:160]] += 1
    say(f"\n== errors: {len(open_)} open (seed folders without result.json), {renamed} in renamed *_interrupted_* folders "
        f"of earlier attempts")
    for k, n in kinds.most_common(6):
        say(f"  {n:>4} x {k}")


def first_targets(folder, label, spec_):
    task, seed = spec_.split(":")
    hits = [p for p in q.resolve(folder).glob(f"{label}/*/{task}/seed_{seed}/executed_actions.jsonl")]
    if not hits:
        say(f"\n== first targets {task}:{seed}: no executed_actions.jsonl under {folder}/{label}")
        return
    for p in hits:
        say(f"\n== first targets {task}:{seed} ({p.parent.parent.parent.name}): {p}")
        with p.open() as f:
            for i, line in enumerate(f):
                if i >= 8:
                    break
                row = json.loads(line)
                say(f"  t{row.get('completed_target_id', i + 1):>2} " + " ".join(f"{float(v):+.4f}" for v in row["target"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--ref-folder", nargs="*", default=[])
    ap.add_argument("--ref-label", default="")
    ap.add_argument("--ref-mode", default="on")
    ap.add_argument("--mode", default="on")
    ap.add_argument("--first", nargs="*", default=[])
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    say(f"# loop_peek {datetime.now(BJ):%F %T}: {args.folder} label {args.label} (read-only)")
    eps = q.episodes([args.folder], args.label)
    table(eps, f"{args.label}: finished episodes with executed_actions.jsonl")
    result_means(args.folder, args.label)
    errors(args.folder, args.label)
    if args.ref_folder and args.ref_label:
        ref = q.episodes(args.ref_folder, args.ref_label)
        seeds = {(t, s) for (t, m, s) in eps if m == args.mode} & {(t, s) for (t, m, s) in ref if m == args.ref_mode}
        say(f"\n== reference {args.ref_label}/{args.ref_mode} in {args.ref_folder}: {len(ref)} episodes with "
            f"executed_actions.jsonl, {len(seeds)} seeds in common with {args.label}/{args.mode}")
        table({k: v for k, v in ref.items() if (k[0], k[2]) in seeds and k[1] == args.ref_mode}, "reference on the common seeds")
        table({k: v for k, v in eps.items() if (k[0], k[2]) in seeds and k[1] == args.mode}, "this on the common seeds")
        diffs = {}
        for t, s in sorted(seeds):
            diffs.setdefault(t, []).append(q.progress(t, eps[(t, args.mode, s)]) - q.progress(t, ref[(t, args.ref_mode, s)]))
        pooled = [d for v in diffs.values() for d in v]
        for t, v in diffs.items():
            say(f"  paired progress (this - reference) {t}: {statistics.mean(v):+.3f} (n={len(v)})")
        if pooled:
            say(f"  paired progress pooled: {statistics.mean(pooled):+.3f} (n={len(pooled)})")
    for f in args.first:
        first_targets(args.folder, args.label, f)
    out = Path(args.out) if args.out else q.O / "report" / f"LOOP_PEEK_{args.label}_{datetime.now(BJ):%Y%m%d_%H%M}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(LINES) + "\n")
    print(f"LOOP_PEEK: {out}")


if __name__ == "__main__":
    main()
