"""5090 diagnosis step D1 (11-12): how much does the FIRST decision differ between pipelines? CPU only, read-only.

At frame 0 every pipeline starts from the same scene (AL0: identical poses), the same physics (AL1) and the same
CPU-seeded noise; only the rendered images and the policy numerics can differ. Comparing decision 0's action chunk
between runs therefore splits the 5090 / A100 difference without any new GPU run:
  ref     vs rerun      floor (the A100 is deterministic: expect 0)
  ref     vs oidn233    the denoiser VERSION alone (same machine, same numerics)
  oidn233 vs 5090       what is left after matching the version: GPU ray-tracing residual + policy numerics
  ref     vs 5090       the total

  export --name NAME --folders F [F ...] --label L [--mode on]
      -> outputs/fullft/align/first/<NAME>.json: per episode (task/seed) decision 0's normalized action chunk,
         its noise seed, and the policy seconds of decision 0 and the median of the later decisions
  compare A.json B.json [--relay-get PREFIX]
      per task, paired episodes: arm RMSE / max |diff| (normalized units, arm joints = all dims but the two
      grippers), gripper max |diff|, whether the noise seeds agree; plus the timing of both sides.
Reading (written 11-12 before any comparison): V = median arm RMSE of ref vs oidn233, N = median of oidn233 vs 5090.
  N <= 0.25 V  -> the residual and the numerics are minor: fixing the denoiser version is the 5090 fix
  N >= V       -> the residual or the numerics dominate: next is the numerics probe (identical inputs on both GPUs)
  otherwise    -> both
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/first_actions.py export --name a100_x7_ref \
      --folders closed_loop/official/put_x7_s0 closed_loop/official/put_x7_s1 --label a2C6_e6
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
OUT = Path(__import__("os").environ.get("FIRST_OUT", "/workspace/FastWAM-memory2/outputs/fullft/align/first"))
GRIPPERS = (6, 13)


def resolve(p):
    return Path(p) if str(p).startswith("/") else O / p


def cmd_export(args):
    entries = {}
    for folder in args.folders:
        for dec in sorted(resolve(folder).glob(f"{args.label}/{args.mode}/*/seed_*/decisions.jsonl")):
            res = dec.parent / "result.json"
            task = dec.parent.parent.name
            seed = dec.parent.name.split("_", 1)[1]
            if not seed.isdigit():
                continue
            rows = [json.loads(s) for s in dec.read_text().splitlines() if s.strip()]
            if not rows:
                continue
            later = [float(r.get("seconds", 0.0)) for r in rows[1:]]
            entries[f"{task}/{int(seed)}"] = {
                "frame_id": rows[0].get("frame_id"), "noise_seed": rows[0].get("noise_seed"),
                "actions": rows[0]["normalized_actions"], "first_seconds": float(rows[0].get("seconds", 0.0)),
                "later_median_seconds": statistics.median(later) if later else None,
                "success": json.loads(res.read_text()).get("success") if res.exists() else None}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{args.name}.json"
    path.write_text(json.dumps({"name": args.name, "folders": args.folders, "label": args.label, "entries": entries}) + "\n")
    tasks = sorted({k.split("/")[0] for k in entries})
    print(f"FIRST ACTIONS {args.name}: {len(entries)} episodes ({', '.join(f'{t} {sum(k.startswith(t) for k in entries)}' for t in tasks)}) -> {path}")


def flat(chunk):
    return [row for row in (chunk[0] if isinstance(chunk[0][0], list) else chunk)]


def diff(a, b):
    a, b = flat(a), flat(b)
    arm, grip = [], []
    for ra, rb in zip(a, b):
        for j, (x, y) in enumerate(zip(ra, rb)):
            (grip if j in GRIPPERS else arm).append(x - y)
    rmse = math.sqrt(sum(d * d for d in arm) / max(1, len(arm)))
    return rmse, max(abs(d) for d in arm), max(abs(d) for d in grip) if grip else 0.0


def load(path):
    p = Path(path)
    if not p.exists():
        p = OUT / path
    return json.loads(p.read_text())


def cmd_compare(args):
    a, b = load(args.a), load(args.b)
    print(f"FIRST-DECISION COMPARE {a['name']} vs {b['name']}")
    for name, side in ((a["name"], a), (b["name"], b)):
        firsts = [e["first_seconds"] for e in side["entries"].values()]
        later = [e["later_median_seconds"] for e in side["entries"].values() if e["later_median_seconds"] is not None]
        if firsts:
            print(f"  timing {name}: decision 0 median {statistics.median(firsts):.1f} s; later decisions median "
                  f"{statistics.median(later) if later else float('nan'):.2f} s")
    tasks = sorted({k.split("/")[0] for k in a["entries"]} & {k.split("/")[0] for k in b["entries"]})
    for task in tasks:
        keys = sorted(k for k in a["entries"] if k.startswith(task + "/") and k in b["entries"])
        rows = []
        for k in keys:
            ea, eb = a["entries"][k], b["entries"][k]
            rmse, mx, gmx = diff(ea["actions"], eb["actions"])
            rows.append((k, rmse, mx, gmx, ea["noise_seed"] == eb["noise_seed"]))
        if not rows:
            continue
        r = sorted(x[1] for x in rows)
        print(f"  {task}: paired {len(rows)}; arm RMSE median {statistics.median(r):.4f} (min {r[0]:.4f}, max {r[-1]:.4f}); "
              f"arm max|diff| median {statistics.median(x[2] for x in rows):.4f}; gripper max|diff| median "
              f"{statistics.median(x[3] for x in rows):.4f}; identical {sum(x[1] == 0 for x in rows)}/{len(rows)}; "
              f"noise seeds agree {sum(x[4] for x in rows)}/{len(rows)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--name", required=True)
    e.add_argument("--folders", nargs="+", required=True)
    e.add_argument("--label", required=True)
    e.add_argument("--mode", default="on")
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    args = ap.parse_args()
    {"export": cmd_export, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    main()
