"""Where does a training update spend its time? (plan v7, P0; read only: dry runs, nothing is saved but PROFILE.json)

For each case, a dry run of N updates with the run's OWN saved config (CONFIG.json) and MEMV2_PROFILE=1; the first
update is discarded (warm-up). Sections (nested names, parent includes children):
  update                         one optimizer update
  update/batch                   building the ordinary micro-batches on the CPU + host->GPU copy
    .../gather | collate_history | collate_s1 | to_device
  update/loss                    forward: current-frame video prefill (encode/current_frame), memory_s1 readout
                                 (encode/s1_readout), history tokenizer (tokenize), action expert (the rest of loss)
  update/backward
  update/pairs_batch, pairs_loss, pairs_backward   the counterfactual pair samples
  update/grad_sync_optim         grad cast, all-reduce (multi-GPU), clip, AdamW

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/profile_step.py [--updates 5] [--cases x7 x7_nopairs press_lm8]
Writes outputs/memory_v2/profile/<case>/PROFILE.json and report/PROFILE_<time>.md (+ .json).
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
# case -> (run whose saved config is used, extra --set overrides)
CASES = {
    "x7": ("a2C_6ep", []),                                         # stage 2, pairs 0.5 x 8 / update, stride 24
    "x7_nopairs": ("a2C_6ep", ["pairs.weight=0"]),                 # pairs off (PairsConfig.enabled needs weight > 0)
    "press_a": ("press_6ep", []),                                   # press stage 2, stride 24 (~45 s / update)
    "press_lm8": ("press_6ep_lm8", []),                             # press stage 2, stride 8 (~86 s / update)
    # plan v7 N1: stage 1 on press, the current 6-layer injection vs kv_replay, same micro-batch (2)
    "press_s1_m2": ("v2_press_cf", ["schedule.micro_batch=2"]),
    "press_n1_m2": ("v2_press_cf", ["schedule.micro_batch=2", "memory_v2.memory.read=kv_replay"]),
    # plan v8 D2 (11-06): X7 recipe without pairs, as one-step distillation from X7 itself (teacher 10-step rollout
    # + student FM / endpoint on the teacher's endpoints); compare with x7_nopairs
    "x7_nopairs_m2": ("a2C_6ep", ["pairs.weight=0", "schedule.micro_batch=2"]),
    "x7_distill": ("a2C_6ep", ["pairs.weight=0", "init_memory=", "schedule.micro_batch=2",
                               f"distill.teacher={O}/a2C_6ep/checkpoints/update_004020.pt", "distill.teacher_steps=10",
                               "distill.ema=0.995", "eval.steps=[1]"]),
    # plan v8 D5 (11-06): press stage 1 with the progress head (dry run: the head trains, nothing breaks)
    "press_prog_m2": ("v2_press_cf", ["schedule.micro_batch=2", "memory_v2.memory.progress_head=true",
                                      "memory_v2.objective.progress_weight=0.1"]),
}
P0_CASES = ["x7", "x7_nopairs", "press_a", "press_lm8", "press_s1_m2", "press_n1_m2"]   # plan v7 P0 (the default)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cases", nargs="+", default=P0_CASES, choices=list(CASES))
    ap.add_argument("--updates", type=int, default=5, help="dry-run updates per case (the first is warm-up)")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--tag", default="", help="report name PROFILE_<tag>_<time>.md (keeps it apart from other profiles)")
    args = ap.parse_args()
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), MEMV2_PROFILE="1", MEMV2_PROFILE_WARMUP="1")
    results = {}
    for case in args.cases:
        run, extra = CASES[case]
        saved_path = O / run / "CONFIG.json"
        if not saved_path.exists():
            print(f"[profile] {case}: {saved_path} missing, skipped", flush=True)
            continue
        saved = json.loads(saved_path.read_text(encoding="utf-8"))
        folder = O / "profile" / case
        folder.mkdir(parents=True, exist_ok=True)
        cfg = folder / "run_config.yaml"
        cfg.write_text(json.dumps(saved["config"], indent=1), encoding="utf-8")
        sets = [f"output={folder}", f"name=profile_{case}"] + extra
        for stale in ("PROFILE.json", "DISTILL_CHECK.json"):
            (folder / stale).unlink(missing_ok=True)
        cmd = [args.python, "-m", "fastwam.memory_v2.train_v2", "train", "--config", str(cfg),
               "--dry-run", str(args.updates)] + [x for s in sets for x in ("--set", s)]
        print(f"[profile] {datetime.now(BJ):%F %T} {case}: {' '.join(cmd)}", flush=True)
        rc = subprocess.call(cmd, cwd=str(REPO), env=env)
        prof = folder / "PROFILE.json"
        if rc != 0 or not prof.exists():
            print(f"[profile] {case}: failed (rc {rc})", flush=True)
            results[case] = {"error": rc}
            continue
        results[case] = json.loads(prof.read_text(encoding="utf-8"))
        results[case]["run"] = run
        results[case]["sets"] = extra
        check = folder / "DISTILL_CHECK.json"
        if check.exists():
            results[case]["distill_check"] = json.loads(check.read_text(encoding="utf-8"))
    now = datetime.now(BJ)
    lines = [f"# Training step profile ({now:%F %T}; dry runs of {args.updates} updates, first discarded)", ""]
    for case, r in results.items():
        if "sections" not in r:
            lines += [f"## {case}: FAILED (rc {r.get('error')}); see the job log", ""]
            continue
        sec = r["sections"]
        step = sec.get("update", {}).get("mean_s")
        lines += [f"## {case} (config of {r['run']}{' + ' + ', '.join(r['sets']) if r['sets'] else ''})", "",
                  f"global batch {r['global_batch']}, micro batch {r['micro_batch']}, pairs / update "
                  f"{r['pairs_per_update']}, GPUs {r['world']}; **{step:.2f} s / update**" if step else "", "",
                  "| section | s / update | share | calls / update |", "|---|---|---|---|"]
        for name, v in sec.items():
            share = f"{v['mean_s'] / step:.1%}" if step else "-"
            lines.append(f"| {name} | {v['mean_s']:.3f} | {share} | {v['calls_per_update']} |")
        lines.append("")
        if r.get("peak_gpu_gb") is not None:
            lines += [f"peak GPU memory {r['peak_gpu_gb']:.1f} GiB", ""]
        if r.get("distill_check"):
            for stage, v in r["distill_check"].items():
                lines.append(f"- distillation check, {stage}: " + ", ".join(f"{k} = {x}" for k, x in v.items()))
            lines.append("")
    base, dist = results.get("x7_nopairs_m2", {}), results.get("x7_distill", {})
    b = base.get("sections", {}).get("update", {}).get("mean_s")
    d = dist.get("sections", {}).get("update", {}).get("mean_s")
    if b and d:
        lines += [f"**x7_distill vs x7_nopairs (both micro batch 2): {d:.2f} / {b:.2f} s per update = {d / b:.2f}x** "
                  "(plan v8 D7 item 1 expects <= 1.2x)", ""]
    rep = O / "report" / f"PROFILE_{args.tag + '_' if args.tag else ''}{now:%Y%m%d_%H%M}.md"
    rep.parent.mkdir(parents=True, exist_ok=True)
    rep.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rep.with_suffix(".json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\n".join(lines))
    print(f"PROFILE: {rep}")
    return 0 if any("sections" in r for r in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
