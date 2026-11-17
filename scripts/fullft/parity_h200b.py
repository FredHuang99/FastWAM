"""New H200 (NTU GaaS) vs old H200 training parity (11-17 17:35 BJ, Opus; read-only). Written before the run.

Question (user 16:57): is the new H200 numerically aligned with the old one, so the H200s are interchangeable?
  old: conti-h200-0, container mwam2, NVIDIA H200 NVL (driver 580.159.04, max SM clock 1785 MHz)
  new: NTU GaaS gpu_as node, NVIDIA H200 SXM (132 SMs, driver 580.126.20, max SM clock 1980 MHz), apptainer SIF of the
       SAME image digest (nvcr.io/nvidia/pytorch@sha256:417cbf33...; versions line identical), the old H200's /opt/mwam
       venv copied byte for byte (pip freeze sha256 checked by setup_parity.pbs before this run)
Run: h200b_parity = the press_ar recipe (same data, seed 17, micro 8 x accumulation 8 as on the old H200, the LR
schedule of the full 30-epoch run), stop_after 500. Reference: the old H200's press_ar metrics (relay diag/parity_ref).
Same micro-batch split as the reference, so (unlike the H100 test) the data, the noise draws and the weights of the
first update are identical: only the GPU, the driver and the hardware's kernel choices can differ.

Pre-registered reading:
  (1) first update: the update-1 row (loss_video, loss_action, grad_norm): |new / ref - 1| <= 0.001 for all three
  (2) as the H100 test (11-17 09:55): mean loss_video and loss_action over 100 < update <= 500 within 5 %; eval at 500:
      val_video within 5 %, val_action within 10 %; no skipped (non-finite) step; max grad norm (101-500) <= 3 x the ref
  Context, not a threshold: the old H200's own noise floor (only the noise draws changed) moved val_action at 500 by
  +0.055 (11-17 17:10).
  IDENTICAL    (1) and (2): the H200s are interchangeable - a run may move between them, and the two arms of a
               comparison may be on different H200s
  ALIGNED      (2) but not (1): interchangeable for whole runs (the arms of a comparison may be on different H200s);
               a run is not moved between them mid-way
  NOT ALIGNED  (2) fails: the new H200 follows deviation 39 (both arms of a task on the same machine)
  floor: both files have rows up to update 500 and the eval at 500, and both have the update-1 row; else NO READING.
Writes outputs/fullft/PARITY_H200B.json.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/parity_h200b.py
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

F = Path("/workspace/FastWAM-memory2/outputs/fullft")


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
    ap.add_argument("--new", default=str(F / "h200b_parity/metrics.jsonl"))
    ap.add_argument("--ref", default=str(F / "parity_ref/metrics.jsonl"))
    args = ap.parse_args()
    if not Path(args.ref).exists() or not Path(args.new).exists():
        print(f"READING: NO READING (missing {args.ref if not Path(args.ref).exists() else args.new})")
        raise SystemExit(2)
    tn, en = rows(Path(args.new))
    tr, er = rows(Path(args.ref))
    w = lambda t, a, b, k: mean([x.get(k) for x in t if a < x["update"] <= b])          # noqa: E731
    print("updates      | new video   old video  | new action  old action | new gn max  old gn max")
    for a in range(0, 500, 100):
        print(f"{a + 1:4d}-{a + 100:4d}    | {w(tn, a, a + 100, 'loss_video'):.4f}      {w(tr, a, a + 100, 'loss_video'):.4f}     | "
              f"{w(tn, a, a + 100, 'loss_action'):.5f}     {w(tr, a, a + 100, 'loss_action'):.5f}     | "
              f"{max([x['grad_norm'] for x in tn if a < x['update'] <= a + 100] or [float('nan')]):.2f}        "
              f"{max([x['grad_norm'] for x in tr if a < x['update'] <= a + 100] or [float('nan')]):.2f}")
    first_n = next((x for x in tn if x["update"] == 1), None)
    first_r = next((x for x in tr if x["update"] == 1), None)
    if (max([x["update"] for x in tn] or [0]) < 500 or max([x["update"] for x in tr] or [0]) < 500 or 500 not in en
            or 500 not in er or first_n is None or first_r is None):
        print("READING: NO READING (a run lacks rows up to update 500, the eval at 500 or the update-1 row)")
        raise SystemExit(2)
    first = {k: first_n[k] / first_r[k] - 1 for k in ("loss_video", "loss_action", "grad_norm")}
    print("update 1 (new / old - 1): " + ", ".join(f"{k} {v:+.2e} ({first_n[k]:.6g} vs {first_r[k]:.6g})"
                                                    for k, v in first.items()))
    same_start = all(abs(v) <= 0.001 for v in first.values())
    checks = {k: w(tn, 100, 500, k) / w(tr, 100, 500, k) - 1 for k in ("loss_video", "loss_action")}
    for k in ("val_video", "val_action"):
        checks[k] = en[500][k] / er[500][k] - 1
    gn_new = max(x["grad_norm"] for x in tn if 100 < x["update"] <= 500)
    gn_ref = max(x["grad_norm"] for x in tr if 100 < x["update"] <= 500)
    sp = Path(args.new).parent / "SUMMARY.json"
    summary = json.loads(sp.read_text()) if sp.exists() else {}
    skipped = int(summary.get("skipped_steps", 0) or 0)
    level = (abs(checks["loss_video"]) <= 0.05 and abs(checks["loss_action"]) <= 0.05 and abs(checks["val_video"]) <= 0.05
             and abs(checks["val_action"]) <= 0.10 and gn_new <= 3 * gn_ref and skipped == 0)
    reading = "IDENTICAL" if level and same_start else ("ALIGNED" if level else "NOT ALIGNED")
    print("101-500 and eval at 500 (new / old - 1): " + ", ".join(f"{k} {v:+.3f}" for k, v in checks.items()))
    print(f"max grad norm (101-500): new {gn_new:.2f}, old {gn_ref:.2f}; skipped steps (new): {skipped}; "
          f"new {summary.get('samples_per_s', float('nan')):.1f} samples/s, peak {summary.get('peak_gib', float('nan')):.1f} GiB")
    print(f"READING: {reading}")
    (F / "PARITY_H200B.json").write_text(json.dumps({"first_update": first, "checks": checks, "grad_norm": [gn_new, gn_ref],
                                                     "skipped": skipped, "reading": reading}, indent=1) + "\n")


if __name__ == "__main__":
    main()
