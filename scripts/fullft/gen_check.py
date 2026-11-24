"""Plan v20 card 8 render check (11-24, Opus): are the generated demos the same kind of picture as the official ones?
Compares frame 0 (all three cameras) of generated episode k with official episode k, generated from the SAME seeds
(the official seed.txt), through the delivery's own reader (build_dense.make_record + data_path.Raw, unmodified).
Gate (the 11-11 render check's, plan v20 card 8): per camera mean |difference| <= 1 grey level AND pixels differing by
more than 8 levels < 2 %; every compared episode must pass. Also prints the instruction and the frame counts.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/gen_check.py --gen <dir>/data --official <dir>/data --n 3
Prints GEN CHECK PASS / GEN CHECK FAIL; JSON -> outputs/fullft/gen_obs/GEN_CHECK.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts/memory_v2/press"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--official", required=True)
    ap.add_argument("--task", default="observe_and_pickup")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--out", default="/workspace/FastWAM-memory2/outputs/fullft/gen_obs/GEN_CHECK.json")
    args = ap.parse_args()
    import build_dense as bd
    common, data_path = bd.setup()
    cfg = json.loads((Path("/workspace/FastWAM-memory2/outputs/memory_v2/press") / f"dense_{args.task}_v1" / "IDENTITY.json").read_text())["config"]
    rows, ok = [], True
    for k in range(args.n):
        name = f"episode_{k:07d}.hdf5"
        g, o = Path(args.gen) / name, Path(args.official) / name
        if not g.exists() or not o.exists():
            rows.append({"episode": k, "why": f"missing {'generated' if not g.exists() else 'official'} file"})
            ok = False
            continue
        rg, ro = bd.make_record(common, g, args.task, "train"), bd.make_record(common, o, args.task, "train")
        a, b = data_path.Raw(cfg, rg), data_path.Raw(cfg, ro)
        try:
            ia, ib = a.images(0), b.images(0)
        finally:
            a.close()
            b.close()
        cams = []
        for c, (x, y) in enumerate(zip(ia, ib)):
            x, y = np.asarray(x).astype(np.int16), np.asarray(y).astype(np.int16)
            if x.shape != y.shape:
                cams.append({"camera": c, "shape": [list(x.shape), list(y.shape)], "pass": False})
                continue
            d = np.abs(x - y)
            m, big = float(d.mean()), float((d.max(axis=-1) > 8).mean())
            cams.append({"camera": c, "mean_abs": round(m, 3), "over8": round(big, 5), "pass": m <= 1.0 and big < 0.02})
        row = {"episode": k, "cameras": cams, "length": [rg["length"], ro["length"]],
               "instruction_same": rg["instruction"] == ro["instruction"], "instruction": [rg["instruction"], ro["instruction"]]}
        row["pass"] = all(c["pass"] for c in cams)
        ok = ok and row["pass"]
        rows.append(row)
        print(f"[gencheck] episode {k}: {'PASS' if row['pass'] else 'FAIL'}; " + "; ".join(
            f"cam {c['camera']} mean {c.get('mean_abs')} >8 {c.get('over8')}" for c in cams)
            + f"; frames {row['length']}; instruction same {row['instruction_same']}", flush=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"pass": ok, "episodes": rows}, indent=1) + "\n")
    print("GEN CHECK " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
