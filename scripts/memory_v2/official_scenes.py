"""Official-seed scene banks (week plan v5 F1): prefix check and subsets of a planned scene manifest.

A bank folder holds <task>.json = {"scenes": [{task, seed, ordinal, instruction, episode_info}, ...], ...} written by
`online.py plan` (rule of the official eval_policy.py: st_seed = 100000 * (1 + seed), the first K expert-feasible
increasing seeds). Plain JSON, no project imports.

    official_scenes.py check-prefix <full_dir> <prefix_dir> <task>     exit 1 unless the first K scenes are identical
    official_scenes.py subset <full_dir> <out_dir> <task> --start K    scenes[K:] (ordinals kept) -> <out_dir>/<task>.json
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
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
