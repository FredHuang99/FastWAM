"""Export the per-scene stage analysis of a closed-loop label (A100 side, 11-11, plan v10 N1) so another machine can
make a PAIRED comparison on the same official scenes without copying the episodes (executed_actions.jsonl are
~14 MB each). Read-only for the episodes; writes one JSON and, with --relay, puts it on the private HF relay.

  PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/migrate/export_stages.py --label a2C6_e6 --mode on \
      --search closed_loop/official --out closed_loop/check_a100/x7_official_stages.json --relay diag/a100_x7_stages
JSON: {"label", "mode", "folders", "episodes": {task: {seed: {stage flags..., "success", "progress"}}}}
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("queue5", HERE.parent / "queue5.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--label", required=True)
    ap.add_argument("--mode", default="on")
    ap.add_argument("--folders", nargs="*", default=[])
    ap.add_argument("--search", default="", help="also every sub-folder of this folder that holds <label>/")
    ap.add_argument("--out", required=True)
    ap.add_argument("--relay", default="", help="HF relay prefix, e.g. diag/a100_x7_stages")
    ap.add_argument("--merge", action="store_true", help="add these tasks to an existing --out file (other tasks kept)")
    args = ap.parse_args()
    folders = list(args.folders)
    if args.search:
        root = q.resolve(args.search)
        folders += sorted(str(d) for d in root.iterdir() if (d / args.label).is_dir())
    eps = q.episodes(folders, args.label, modes=[args.mode])
    out = {"label": args.label, "mode": args.mode, "folders": folders, "episodes": {}}
    for (task, mode, seed), a in sorted(eps.items()):
        row = {k: v for k, v in a.items() if k != "dir" and isinstance(v, (bool, int, float, str))}
        row["progress"] = q.progress(task, a)
        out["episodes"].setdefault(task, {})[str(seed)] = row
    path = q.resolve(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    if args.merge and path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        for task, rows in old.get("episodes", {}).items():
            out["episodes"].setdefault(task, rows)
        out["merged_from"] = {"label": old.get("label"), "folders": old.get("folders")}
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    for task, rows in out["episodes"].items():
        print(f"{task}: {len(rows)} episodes, mean progress {q.mean(r['progress'] for r in rows.values()):.3f}, "
              f"success {sum(bool(r.get('success')) for r in rows.values())}")
    print(f"folders: {folders}\nEXPORT: {path}")
    if args.relay:
        rc = subprocess.run(["/opt/hf-tools/bin/python", str(HERE / "relay.py"), "put", str(path), "--prefix", args.relay]).returncode
        sys.exit(rc)


if __name__ == "__main__":
    main()
