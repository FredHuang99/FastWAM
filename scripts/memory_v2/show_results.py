"""Print every result of the memory_v2 round (PR, full evals, training curves, guards) in one go.

    /opt/mwam/bin/python /workspace/FastWAM-memory2/scripts/memory_v2/show_results.py \
        | tee /workspace/FastWAM-memory2/outputs/memory_v2/RESULTS_round3.txt

Read-only; missing files are reported, not fatal.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

RUNS = ("v2_A_memory_only", "v2_A_bfull", "v2_A_noabs", "v2_A_b0", "v2_A_cf")
LABEL = {"v2_A_memory_only": "Ours", "v2_A_bfull": "B-full", "v2_A_noabs": "noabs", "v2_A_b0": "B0(cap)",
         "v2_A_cf": "D(cf)"}
MODES = ("on", "null", "off")


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def jsonl(path: Path):
    out = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                out.append(json.loads(line))
    except (OSError, ValueError):
        pass
    return out


def fmt(x, w=7, p=4):
    return f"{x:>{w}.{p}f}" if isinstance(x, (int, float)) else f"{'-':>{w}}"


def section(title):
    print("\n" + "=" * 100 + f"\n{title}\n" + "=" * 100)


def status(root: Path):
    section("0. run status")
    for run in RUNS:
        d = root / run
        latest = load(d / "checkpoints" / "LATEST.json")
        guard = load(d / "GUARD.json")
        metrics = jsonl(d / "metrics.jsonl")
        evals = sorted(p.stem for p in (d / "eval").glob("update_*.json"))
        last = metrics[-1] if metrics else {}
        print(f"{LABEL[run]:<8} {d}")
        print(f"         latest={latest}  updates_logged={len(metrics)}  last_update={last.get('update')}  "
              f"evals={evals[-3:]}  GUARD={guard}")


def curves(root: Path, bucket: int):
    section(f"1. training curves (mean per {bucket} updates): fm | endpoint | pair_loss | grad_norm")
    for run in RUNS:
        m = jsonl(root / run / "metrics.jsonl")
        if not m:
            continue
        print(f"-- {LABEL[run]}  ({root / run / 'metrics.jsonl'})")
        for start in range(0, m[-1]["update"], bucket):
            xs = [r for r in m if start < r["update"] <= start + bucket]
            if not xs:
                continue
            mean = lambda k: (sum(r[k] for r in xs if k in r) / max(1, sum(1 for r in xs if k in r))) if any(k in r for r in xs) else None
            print(f"   {start + 1:>5}-{start + bucket:<5} fm {fmt(mean('fm'))}  endpoint {fmt(mean('endpoint'))}  "
                  f"pair {fmt(mean('pair_loss'))}  grad {fmt(mean('grad_norm'), 7, 3)}")


def training_evals(root: Path):
    section("2. in-training eval (96-window subset): arm RMSE on | null | off")
    for run in RUNS:
        files = sorted((root / run / "eval").glob("update_*.json"))
        if not files:
            continue
        print(f"-- {LABEL[run]}")
        for f in files:
            o = (load(f) or {}).get("overall", {})
            print(f"   {f.stem}  " + "  ".join(f"{m} {fmt(o.get(f'{m}/arm_rmse_rad'))}" for m in MODES))


def full_evals(root: Path):
    section("3. full 401-window eval (eval_full/update_001340.json)")
    keys = ("arm_rmse_rad", "prefix16_arm_rmse_rad", "gripper_rmse", "fm_tau1", "fm_tau0.5")
    print(f"{'run':<9}{'mode':<6}" + "".join(f"{k:>24}" for k in keys))
    tables = {}
    for run in RUNS:
        path = root / run / "eval_full" / "update_001340.json"
        value = load(path)
        if value is None:
            print(f"{LABEL[run]:<9}(missing {path})")
            continue
        tables[run] = value
        for m in MODES:
            o = value["overall"]
            print(f"{LABEL[run]:<9}{m:<6}" + "".join(f"{fmt(o.get(f'{m}/{k}'), 24)}" for k in keys))
    print("\nby task / split / window kind: arm RMSE on | null | off")
    for run, value in tables.items():
        print(f"-- {LABEL[run]}")
        for g in value.get("groups", []):
            cells = []
            for kind, row in g.get("by_window_kind", {}).items():
                cells.append(f"{kind[:7]:<7} n={row['windows']:>3} " + "|".join(fmt(row.get(f"{m}/arm_rmse_rad"), 6) for m in MODES))
            print(f"   {g['task']:<15}{g['split']:<6}" + "   ".join(cells))


def pr(root: Path):
    section("4. PR on matched-present val pairs (own_correct | switch | PR | median response)")
    files = sorted(glob.glob(str(root / "pr" / "*" / "pr_*_val.json")))
    if not files:
        print(f"(no files under {root / 'pr'})")
    for f in files:
        value = load(Path(f)) or {}
        s = value.get("summary", {})
        print(f"\n== {f}   pairs={value.get('pairs')}  checkpoint={value.get('checkpoint')}")
        for part in ("all", "put_back_block", "swap_blocks", "delta_low", "delta_mid", "delta_high", "donor_train", "donor_val"):
            if part not in s:
                continue
            row = s[part]
            cells = "  ".join(f"{m}: own {row[m]['own_correct']:.2f} sw {row[m]['switch']:.2f} PR {row[m]['pr']:.2f} "
                              f"resp {row[m]['response_median']:.2f}" for m in MODES if m in row)
            print(f"  {part:<15} n={row['n']:<4} {cells}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM-memory2/outputs/memory_v2"))
    parser.add_argument("--bucket", type=int, default=100)
    args = parser.parse_args()
    status(args.root)
    curves(args.root, args.bucket)
    training_evals(args.root)
    full_evals(args.root)
    pr(args.root)


if __name__ == "__main__":
    main()
