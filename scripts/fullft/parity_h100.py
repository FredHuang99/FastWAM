"""H100 vs H200 training parity (11-17, Opus; read-only). Written 09:55 BJ, before the parity run started.

Question (user, 11-17): does a model trained on the H100 box (gpu24, micro 2 x accumulation 32) learn like one trained on
the H200 (micro 8 x 8)? Same software (restore test: no drift from the H200 pins), same architecture (sm_90), same
recipe, data order and LR schedule; 64 samples per update either way. Differences: the micro-batch split (other GEMM
shapes, other random draws for the diffusion noise), so the curves should agree in level, not bit for bit.

Inputs: the H100 parity run outputs/fullft/h100_parity/metrics.jsonl (press_ar recipe, stop_after 500) and the
H200 press_ar metrics (relay diag/parity_ref/metrics.jsonl, put by the H200 log command; fetched if missing).
Pre-registered reading:
  training curve  mean loss_video and mean loss_action over the logged rows with 100 < update <= 500:
                  |H100 / H200 - 1| <= 0.05 for both
  eval at 500     val_video: |ratio - 1| <= 0.05; val_action: |ratio - 1| <= 0.10 (fixed-noise validation)
  health          no skipped (non-finite) step; max grad norm over 100 < update <= 500 <= 3 x the H200's
  ALIGNED = all of the above; NOT ALIGNED otherwise (then: no new H100 training until explained; battery_ar flagged)
  floor: both files have rows up to update 500 and the eval at 500, else NO READING.
Also printed: means per 100-update window, side by side.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/parity_h100.py
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
F = R / "outputs/fullft"


def rows(path: Path):
    train, evals = [], {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        if "eval" in d:
            evals[int(d["eval"]["update"])] = d["eval"]
        else:
            train.append(d)
    return train, evals


def mean(v):
    v = [x for x in v if x is not None and math.isfinite(x)]
    return sum(v) / len(v) if v else float("nan")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--new", default=str(F / "h100_parity/metrics.jsonl"))
    ap.add_argument("--ref", default=str(F / "parity_ref/metrics.jsonl"))
    args = ap.parse_args()
    ref = Path(args.ref)
    if not ref.exists():
        ref.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["/opt/hf-tools/bin/python", str(R / "scripts/memory_v2/migrate/relay.py"), "get", "--prefix",
                        "diag/parity_ref", "--out", str(ref.parent)], check=False, capture_output=True)
    if not ref.exists():
        print("PARITY: NO READING - the H200 reference (press_ar metrics.jsonl) is not on the relay under diag/parity_ref;"
              " put it from the H200 first")
        raise SystemExit(2)
    tn, en = rows(Path(args.new))
    tr, er = rows(ref)
    w = lambda t, a, b, k: mean([x.get(k) for x in t if a < x["update"] <= b])          # noqa: E731
    print("updates      | H100 video  H200 video | H100 action H200 action | H100 gn max  H200 gn max")
    for a in range(0, 500, 100):
        print(f"{a + 1:4d}-{a + 100:4d}    | {w(tn, a, a + 100, 'loss_video'):.4f}      {w(tr, a, a + 100, 'loss_video'):.4f}     | "
              f"{w(tn, a, a + 100, 'loss_action'):.5f}     {w(tr, a, a + 100, 'loss_action'):.5f}     | "
              f"{max([x['grad_norm'] for x in tn if a < x['update'] <= a + 100] or [float('nan')]):.2f}        "
              f"{max([x['grad_norm'] for x in tr if a < x['update'] <= a + 100] or [float('nan')]):.2f}")
    if max([x["update"] for x in tn] or [0]) < 500 or max([x["update"] for x in tr] or [0]) < 500 or 500 not in en or 500 not in er:
        print("READING: NO READING (a run lacks rows up to update 500 or the eval at 500)")
        return
    checks = {}
    for k in ("loss_video", "loss_action"):
        checks[k] = w(tn, 100, 500, k) / w(tr, 100, 500, k) - 1
    for k, tol in (("val_video", 0.05), ("val_action", 0.10)):
        checks[k] = en[500][k] / er[500][k] - 1
    gn_new = max(x["grad_norm"] for x in tn if 100 < x["update"] <= 500)
    gn_ref = max(x["grad_norm"] for x in tr if 100 < x["update"] <= 500)
    summary = json.loads((Path(args.new).parent / "SUMMARY.json").read_text()) if (Path(args.new).parent / "SUMMARY.json").exists() else {}
    skipped = int(summary.get("skipped_steps", 0) or 0)
    ok = (abs(checks["loss_video"]) <= 0.05 and abs(checks["loss_action"]) <= 0.05 and abs(checks["val_video"]) <= 0.05
          and abs(checks["val_action"]) <= 0.10 and gn_new <= 3 * gn_ref and skipped == 0)
    print("relative differences H100 / H200 - 1: " + ", ".join(f"{k} {v:+.3f}" for k, v in checks.items()))
    print(f"max grad norm (101-500): H100 {gn_new:.2f}, H200 {gn_ref:.2f}; skipped steps on the H100: {skipped}; "
          f"H100 {summary.get('samples_per_s', float('nan')):.1f} samples/s")
    print(f"READING: {'ALIGNED' if ok else 'NOT ALIGNED'}")
    out = Path(args.new).parent.parent / "PARITY_H100.json"
    out.write_text(json.dumps({"checks": checks, "grad_norm": [gn_new, gn_ref], "skipped": skipped,
                                                    "reading": "ALIGNED" if ok else "NOT ALIGNED"}, indent=1) + "\n")


if __name__ == "__main__":
    main()
