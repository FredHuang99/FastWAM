"""Training noise floor for the H100 parity reading (11-17 14:45 BJ, Opus; written before the run; read-only).

Why: h100_parity (11-17) read NOT ALIGNED on one item only: val_action at update 500 was 12 % above the H200 press_ar
(threshold 10 %); training losses agreed within 3 %. The two machines differ only in the micro-batch split, i.e. in
the random draws of the diffusion noise / timesteps (same data order, same initialisation). This run measures how far
val_action at update 500 moves when ONLY those draws change on one machine: the H200 press_ar recipe again with
schedule.noise_seed=18 (data order, augmentation, init unchanged), stop_after 500, on the H200 (micro 8 x 8, same as
press_ar). User 14:35: do A (same-machine pairs, deviation 39) and B (this test) together.

Pre-registered reading, d = |val_action(noise run) / val_action(press_ar) - 1| at update 500:
  d >= 0.08  -> EXPLAINED: the H100 gap (0.120) is the size of a noise-draw change; the H100 is used like the H200
                (battery_ar no longer flagged)
  d <= 0.04  -> NOT EXPLAINED: the machine gap is larger than the noise floor; the H100 keeps rule A (both arms of a
                comparison on the same machine) and its runs stay flagged for cross-machine tables
  otherwise  -> NOT EXPLAINED (same consequence)
  floor: both files have the eval at update 500, else NO READING.
Also printed (context only): the same ratios for val_video and the 100-update training-loss windows.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/noise_floor.py
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
        if line.strip():
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
    ap.add_argument("--new", default=str(F / "press_noise500/metrics.jsonl"))
    ap.add_argument("--ref", default=str(F / "press_ar/metrics.jsonl"))
    args = ap.parse_args()
    if not (Path(args.new).exists() and Path(args.ref).exists()):
        print(f"NOISE FLOOR: NO READING - missing {args.new if not Path(args.new).exists() else args.ref}")
        raise SystemExit(2)
    tn, en = rows(Path(args.new))
    tr, er = rows(Path(args.ref))
    w = lambda t, a, b, k: mean([x.get(k) for x in t if a < x["update"] <= b])          # noqa: E731
    print("updates      | noise video  ref video | noise action ref action")
    for a in range(0, 500, 100):
        print(f"{a + 1:4d}-{a + 100:4d}    | {w(tn, a, a + 100, 'loss_video'):.4f}       {w(tr, a, a + 100, 'loss_video'):.4f}    | "
              f"{w(tn, a, a + 100, 'loss_action'):.5f}      {w(tr, a, a + 100, 'loss_action'):.5f}")
    if 500 not in en or 500 not in er:
        print("NOISE FLOOR: NO READING - eval at update 500 missing")
        raise SystemExit(2)
    dv = en[500]["val_video"] / er[500]["val_video"] - 1
    da = en[500]["val_action"] / er[500]["val_action"] - 1
    print(f"eval at 500: val_video {dv:+.3f}, val_action {da:+.3f} (noise run / press_ar - 1); H100 gap was +0.120")
    d = abs(da)
    reading = "EXPLAINED" if d >= 0.08 else "NOT EXPLAINED"
    print(f"READING: {reading} (d = {d:.3f}; >= 0.08 explained, otherwise not)")
    (F / "NOISE_FLOOR.json").write_text(json.dumps({"d_val_action": da, "d_val_video": dv, "reading": reading}, indent=1))


if __name__ == "__main__":
    main()
