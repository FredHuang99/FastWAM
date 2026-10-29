"""Official-seed scene banks (week plan v5 F1): prefix check and subsets of a planned scene manifest.

A bank folder holds <task>.json = {"scenes": [{task, seed, ordinal, instruction, episode_info}, ...], ...} written by
`online.py plan` (rule of the official eval_policy.py: st_seed = 100000 * (1 + seed), the first K expert-feasible
increasing seeds). Plain JSON, no project imports.

    official_scenes.py check-prefix <full_dir> <prefix_dir> <task>     exit 1 unless the first K scenes are identical
    official_scenes.py subset <full_dir> <out_dir> <task> --start K    scenes[K:] (ordinals kept) -> <out_dir>/<task>.json
    official_scenes.py complete <dir> <task> <n>                       exit 0 iff the planner marked the bank complete
                                                                       with >= n scenes (a partial bank resumes on re-plan)
    official_scenes.py skip-expert-error <dir> <task>                  the official rule for a seed whose EXPERT raised
        (eval_policy.py: expert_check, `except Exception: now_seed += 1`): our planner stops on any exception and keeps
        the seed (<task>.error.json); when the exception came from the expert demo (play_once), mark that seed rejected
        and advance next_seed, so a re-plan continues like the official evaluation. Exit 0 if a seed was skipped, 2 if
        there was nothing to skip, 1 if the error is not an expert error (left for a human).
"""
import argparse
import json
import sys
from pathlib import Path

KEYS = ("task", "seed", "ordinal", "instruction")


def scenes(folder, task):
    value = json.loads((Path(folder) / f"{task}.json").read_text())
    rows = value.get("scenes") if isinstance(value, dict) else value
    return sorted((r for r in rows if r.get("task") == task), key=lambda r: (r.get("ordinal", 0), int(r["seed"])))


def check_prefix(args):
    full, prefix = scenes(args.full, args.task), scenes(args.prefix, args.task)
    bad = [(i, a, b) for i, (a, b) in enumerate(zip(full, prefix)) if any(a.get(k) != b.get(k) for k in KEYS)]
    print(f"{args.task}: full {len(full)} scenes, prefix {len(prefix)}; first seeds full {[r['seed'] for r in full[:5]]} "
          f"prefix {[r['seed'] for r in prefix[:5]]}")
    if len(full) < len(prefix) or bad:
        for i, a, b in bad[:5]:
            print(f"  MISMATCH at {i}: full {[a.get(k) for k in KEYS]} vs prefix {[b.get(k) for k in KEYS]}")
        print(f"PREFIX CHECK FAILED: {len(bad)} mismatching scenes" + (f"; full bank shorter ({len(full)}) than the prefix "
              f"({len(prefix)})" if len(full) < len(prefix) else ""))
        sys.exit(1)
    print(f"PREFIX CHECK OK: the first {len(prefix)} scenes are identical")


def subset(args):
    rows = scenes(args.full, args.task)[args.start:]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{args.task}.json").write_text(json.dumps({"scenes": rows, "complete": True,
                                                       "subset_of": str(Path(args.full).resolve()),
                                                       "start": args.start}, indent=1))
    print(f"{args.task}: wrote {len(rows)} scenes (from index {args.start}, seeds {rows[0]['seed']}..{rows[-1]['seed']}) "
          f"-> {out}")


def complete(args):
    path = Path(args.dir) / f"{args.task}.json"
    value = json.loads(path.read_text()) if path.exists() else {}
    n = len(value.get("scenes") or [])
    ok = bool(value.get("complete")) and n >= args.n
    print(f"{args.task}: {path} {'complete' if ok else 'NOT complete'} ({n} scenes, next seed {value.get('next_seed')})")
    sys.exit(0 if ok else 1)


def skip_expert_error(args):
    path = Path(args.dir) / f"{args.task}.json"
    err_path = path.with_suffix(".error.json")
    if not err_path.exists():
        print(f"{args.task}: no {err_path.name}: nothing to skip")
        sys.exit(2)
    err = json.loads(err_path.read_text())
    saved = json.loads(path.read_text())
    seed, text = int(err["seed"]), str(err.get("error", ""))
    if saved.get("next_seed") != seed:
        print(f"{args.task}: error seed {seed} != next_seed {saved.get('next_seed')}: already handled, nothing to skip")
        err_path.rename(err_path.with_name(f"{args.task}.error.{seed}.handled.json"))
        sys.exit(2)
    if "in play_once" not in text:
        print(f"{args.task}: seed {seed} failed outside the expert demo (not skipped):\n{text[-800:]}")
        sys.exit(1)
    last = [x for x in text.strip().splitlines() if x.strip()][-1]
    saved.setdefault("candidates", []).append({"seed": seed, "accepted": False, "expert_exception": last[:300],
                                              "rule": "official eval_policy.py expert_check: exception -> next seed"})
    saved.setdefault("expert_exception_seeds", []).append(seed)
    saved["next_seed"] = seed + 1
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(saved, indent=1))
    tmp.replace(path)
    err_path.rename(err_path.with_name(f"{args.task}.error.{seed}.json"))
    print(f"{args.task}: seed {seed} rejected (expert exception: {last[:160]}); next_seed -> {seed + 1}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("check-prefix")
    a.add_argument("full")
    a.add_argument("prefix")
    a.add_argument("task")
    a.set_defaults(fn=check_prefix)
    b = sub.add_parser("subset")
    b.add_argument("full")
    b.add_argument("out")
    b.add_argument("task")
    b.add_argument("--start", type=int, required=True)
    b.set_defaults(fn=subset)
    c = sub.add_parser("complete")
    c.add_argument("dir")
    c.add_argument("task")
    c.add_argument("n", type=int)
    c.set_defaults(fn=complete)
    e = sub.add_parser("skip-expert-error")
    e.add_argument("dir")
    e.add_argument("task")
    e.set_defaults(fn=skip_expert_error)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
