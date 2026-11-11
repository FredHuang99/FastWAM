"""K0 (plan v11 D.4 S-H, first step; Opus checklist 21), grasp part: in closed-loop episodes, how often does a grasp
attempt fail, and after a failed attempt does the policy retry or move on? Also: could the policy itself tell a failed
grasp from a successful one from its own proprio input, and could a detector tell them apart from the physical
finger opening? CPU only; reads executed_actions.jsonl of finished episodes (read-only).

Definitions (written 11-11 17:55, before this script read any episode):
  attempt     a commanded close of arm a: the gripper column of `target` (6 left / 13 right) falls below 0.35 after
              having been >= 0.65 (the rule-A gripper hysteresis), at completed target t
  achieved    within targets [t, t + 30] and before arm a is commanded open again, some block (block / block1 / block2)
              is in contact with arm a's fingers (object_contacts.by_side) AND its height rises >= 0.02 m above its
              height at t
  after a failed attempt:
              retry    arm a is commanded open and closed again within 60 targets of t
              move on  otherwise (no new close of arm a within 60 targets)
  first deviation (failed episodes only): the episode's first failed attempt is followed by "move on"
  separability (rule B's question, on these episodes): for every attempt, the settled reading 8 targets after t of
              (i) the policy-visible gripper (command_echo_before = what the policy is given) and (ii) the physical
              finger opening (physical_after, normalised like the command); AUC of achieved vs failed for each
Press attempts are not covered here (the logs carry no end-effector height); reported as "not measured".
Descriptive only for old models (X7, B0): the v11 K0 reading (>= 40 % "common") applies to the new base model.

  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/self_fail.py --folder closed_loop/eq5090b --label x7_eq5090b
  ... --search closed_loop/official --label a2C6_e6   (every sub-folder of the search folder that holds <label>/)
Rows are per task AND mode (11-11 19:00: the first A100 run pooled X7 "on" with X7 "masked" episodes of the same label).
Writes outputs/fullft/k0/SELF_FAIL_<label>_<time>.json and prints the table.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
BJ = timezone(timedelta(hours=8))
BLOCKS = ("block", "block1", "block2")
CLOSE, OPEN = 0.35, 0.65
WINDOW_ACHIEVE, WINDOW_RETRY, SETTLE = 30, 60, 8


def resolve(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else O / q


def episodes(folders, label):
    for folder in folders:
        for d in sorted(folder.glob(f"{label}/*/*/seed_*")):
            f = d / "executed_actions.jsonl"
            if (d / "result.json").exists() and f.exists():
                yield f"{d.parts[-2]} ({d.parts[-3]})", d.name, d      # "task (mode)": memory on / masked apart


def load_rows(path: Path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def commanded_closes(target_grip: np.ndarray):
    """Frames where a commanded gripper series closes (hysteresis), and where it opens."""
    closes, opens, is_open = [], [], None
    for t, g in enumerate(target_grip):
        if is_open is None:
            is_open = g >= 0.5
        elif is_open and g < CLOSE:
            is_open = False
            closes.append(t)
        elif not is_open and g > OPEN:
            is_open = True
            opens.append(t)
    return closes, opens


def block_z(row, key):
    out = {}
    for name in BLOCKS:
        cell = row.get(key, {}).get(name)
        if isinstance(cell, dict) and "p" in cell:
            out[name] = float(cell["p"][2])
    return out


def touching(row, name, side):
    cell = (row.get("object_contacts") or {}).get("objects", {}).get(name) or {}
    return bool((cell.get("by_side") or {}).get(side))


def analyse(rows, settle=SETTLE):
    if not rows:
        return []
    target = np.asarray([r["target"] for r in rows], dtype=float)
    echo = np.asarray([r.get("command_echo_before", r["target"]) for r in rows], dtype=float)
    phys = np.asarray([r.get("physical_after", r["target"]) for r in rows], dtype=float)
    attempts = []
    for arm, col, side in ((0, 6, "left"), (1, 13, "right")):
        closes, opens = commanded_closes(target[:, col])
        for t in closes:
            next_open = min([o for o in opens if o > t], default=len(rows))
            end = min(len(rows), t + WINDOW_ACHIEVE + 1, next_open)
            z0 = block_z(rows[t], "objects_before")
            achieved = False
            for u in range(t, end):
                zs = block_z(rows[u], "objects_after")
                for name, z in zs.items():
                    if name in z0 and z - z0[name] >= 0.02 and touching(rows[u], name, side):
                        achieved = True
            retry = any(t < c <= t + WINDOW_RETRY for c in closes)
            s = min(len(rows) - 1, t + settle)
            attempts.append({"arm": arm, "t": t, "achieved": achieved, "retry": retry,
                             "echo_settled": float(echo[s, col]), "phys_settled": float(phys[s, col])})
    return sorted(attempts, key=lambda a: a["t"])


def auc(pos, neg):
    """P(score of an achieved attempt > score of a failed one), ties count 1/2. None if a side is empty."""
    if not pos or not neg:
        return None
    pos, neg = np.asarray(pos), np.asarray(neg)
    gt = (pos[:, None] > neg[None, :]).mean()
    eq = (pos[:, None] == neg[None, :]).mean()
    return float(gt + 0.5 * eq)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True)
    ap.add_argument("--folder", nargs="*", default=[])
    ap.add_argument("--search", default="")
    ap.add_argument("--out", default="/workspace/FastWAM-memory2/outputs/fullft/k0")
    ap.add_argument("--settle", type=int, default=SETTLE,
                    help="targets after the close at which the readings are taken (11-11: 4 = the ledger write lag k)")
    args = ap.parse_args()
    folders = [resolve(f) for f in args.folder]
    if args.search:
        root = resolve(args.search)
        folders += sorted(d for d in root.iterdir() if (d / args.label).is_dir())
    per_task = {}
    for task, seed, d in episodes(folders, args.label):
        result = json.loads((d / "result.json").read_text())
        att = analyse(load_rows(d / "executed_actions.jsonl"), args.settle)
        per_task.setdefault(task, []).append({"seed": seed, "success": bool(result.get("success")), "attempts": att})
    report = {"label": args.label, "folders": [str(f) for f in folders], "tasks": {}}
    print(f"K0 grasp attempts, label {args.label} ({len(folders)} folders); readings {args.settle} targets after the close")
    print("| task | episodes (success) | attempts | failed | failed -> retry / move on | failed episodes whose first "
          "failed attempt moved on | AUC policy-visible gripper | AUC physical fingers |")
    print("|---|---|---|---|---|---|---|---|")
    for task, eps in sorted(per_task.items()):
        att = [a for e in eps for a in e["attempts"]]
        failed = [a for a in att if not a["achieved"]]
        retry = sum(a["retry"] for a in failed)
        failed_eps = [e for e in eps if not e["success"]]
        first_dev = 0
        with_failed = 0
        for e in failed_eps:
            f = [a for a in e["attempts"] if not a["achieved"]]
            if f:
                with_failed += 1
                first_dev += not f[0]["retry"]
        a_echo = auc([a["echo_settled"] for a in att if a["achieved"]], [a["echo_settled"] for a in failed])
        a_phys = auc([a["phys_settled"] for a in att if a["achieved"]], [a["phys_settled"] for a in failed])
        fmt = lambda x: "-" if x is None else f"{x:.3f}"
        row = {"episodes": len(eps), "success": sum(e["success"] for e in eps), "attempts": len(att),
               "failed": len(failed), "failed_retry": retry, "failed_move_on": len(failed) - retry,
               "failed_episodes": len(failed_eps), "failed_episodes_with_failed_attempt": with_failed,
               "first_deviation_move_on": first_dev, "auc_policy_visible": a_echo, "auc_physical": a_phys,
               "echo_settled_failed": sorted({round(a["echo_settled"], 3) for a in failed})[:10],
               "phys_settled_achieved_median": float(np.median([a["phys_settled"] for a in att if a["achieved"]]))
               if any(a["achieved"] for a in att) else None,
               "phys_settled_failed_median": float(np.median([a["phys_settled"] for a in failed])) if failed else None}
        report["tasks"][task] = row
        print(f"| {task} | {len(eps)} ({row['success']}) | {len(att)} | {len(failed)} ({len(failed) / max(1, len(att)):.0%}) "
              f"| {retry} / {len(failed) - retry} | {first_dev} / {len(failed_eps)} (with a failed attempt: {with_failed}) "
              f"| {fmt(a_echo)} | {fmt(a_phys)} |")
        print(f"    settled readings: policy-visible on failed attempts {row['echo_settled_failed']}; physical median "
              f"achieved {fmt(row['phys_settled_achieved_median'])} / failed {fmt(row['phys_settled_failed_median'])}")
    print("press attempts: not measured (no end-effector height in the logs)")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"SELF_FAIL_{args.label}_settle{args.settle}_{datetime.now(BJ):%Y%m%d_%H%M}.json"
    path.write_text(json.dumps(report, indent=1) + "\n")
    print(f"K0: {path}")


if __name__ == "__main__":
    main()
