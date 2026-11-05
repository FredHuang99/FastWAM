"""Offline sampling error vs number of Euler steps, memory on vs null (plan v7 Q2 / S1, descriptive).

For one run, evaluates its final checkpoint on all val windows with the run's OWN saved config (CONFIG.json), once per
step count, only modes on / null, the same per-window noise every time (backend.noise is seeded per window). The FM
errors per tau do not depend on the step count and are not reported again (V7_EVIDENCE has them).

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/steps_sweep.py --run a2C_6ep --steps 10 4 2 1
Writes outputs/memory_v2/<run>/eval_steps/steps_<k>/<checkpoint>.json and report/STEPS_SWEEP_<run>_<time>.md (+ .json).
A step count whose JSON already exists is not re-run (resumable).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
REPO = Path(__file__).resolve().parents[2]
BJ = timezone(timedelta(hours=8))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--steps", type=int, nargs="+", default=[10, 4, 2, 1])
    ap.add_argument("--checkpoint", default="", help="default: update_<total_updates>.pt of the run")
    ap.add_argument("--windows", type=int, default=0, help="0 = all val windows")
    ap.add_argument("--python", default=sys.executable)
    args = ap.parse_args()

    run = O / args.run
    saved = json.loads((run / "CONFIG.json").read_text(encoding="utf-8"))
    ck = Path(args.checkpoint) if args.checkpoint else run / "checkpoints" / f"update_{int(saved['total_updates']):06d}.pt"
    if not ck.exists():
        raise SystemExit(f"checkpoint {ck} missing")
    out = run / "eval_steps"
    out.mkdir(parents=True, exist_ok=True)
    cfg_path = out / "run_config.yaml"
    cfg_path.write_text(json.dumps(saved["config"], indent=1), encoding="utf-8")   # JSON is valid YAML
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    results = {}
    for k in args.steps:
        folder = out / f"steps_{k}"
        target = folder / f"{ck.stem}.json"
        if not target.exists():
            cmd = [args.python, "-m", "fastwam.memory_v2.train_v2", "evaluate", "--config", str(cfg_path),
                   "--checkpoint", str(ck), "--windows", str(args.windows), "--output", str(folder),
                   "--set", f"memory_v2.guidance.steps={k}", "--set", 'eval.modes=["on","null"]',
                   "--set", "eval.guidance_scales=[]"]
            print(f"[steps_sweep] {datetime.now(BJ):%F %T} steps={k}: {' '.join(cmd)}", flush=True)
            rc = subprocess.call(cmd, cwd=str(REPO), env=env)
            if rc != 0 or not target.exists():
                raise SystemExit(f"steps={k}: evaluate failed (rc {rc})")
        overall = json.loads(target.read_text(encoding="utf-8")).get("overall", {})
        results[k] = {key: v for key, v in overall.items() if "/fm_tau" not in key}
    keys = sorted({key.split("/", 1)[1] for r in results.values() for key in r})
    now = datetime.now(BJ)
    lines = [f"# Steps sweep: {args.run} ({ck.name}; {now:%F %T})", "",
             f"Offline sampled-chunk errors on val windows (windows={args.windows or 'all'}), same noise per window; "
             "on = memory on, null = history masked. Lower is better.", ""]
    for key in keys:
        lines += [f"## {key}", "", "| steps | on | null | null - on | (null - on) / null |", "|---|---|---|---|---|"]
        for k in args.steps:
            on, nu = results[k].get(f"on/{key}"), results[k].get(f"null/{key}")
            if isinstance(on, (int, float)) and isinstance(nu, (int, float)):
                rel = f"{(nu - on) / nu:+.1%}" if nu else "-"
                lines.append(f"| {k} | {on:.5f} | {nu:.5f} | {nu - on:+.5f} | {rel} |")
        lines.append("")
    rep = O / "report" / f"STEPS_SWEEP_{args.run}_{now:%Y%m%d_%H%M}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rep.with_suffix(".json").write_text(json.dumps({"run": args.run, "checkpoint": str(ck), "results": results},
                                                   indent=1), encoding="utf-8")
    print("\n".join(lines))
    print(f"STEPS_SWEEP: {rep}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
