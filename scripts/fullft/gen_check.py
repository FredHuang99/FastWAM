"""Plan v20 card 8 render check (11-24, Opus): are the generated demos the same kind of picture as the official ones?
Compares frame 0 (all three cameras) of generated episode k with official episode k, generated from the SAME seeds
(the official seed.txt), through the delivery's own reader (build_dense.make_record + data_path.Raw, unmodified).
Gate (the 11-11 render check's, plan v20 card 8): per camera mean |difference| <= 1 grey level AND pixels differing by
more than 8 levels < 2 %; every compared episode must pass. Also prints the instruction and the frame counts.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/gen_check.py --gen <dir>/data --official <dir>/data --n 3
Prints GEN CHECK PASS / GEN CHECK FAIL; JSON -> outputs/fullft/gen_obs/GEN_CHECK.json
--gate background (11-24 19:30, used ONLY after the user agrees; default stays 'pixel'): the 11-24 run failed on the head
camera only, and gen_diff.py put the difference on the objects (RMBench picks object models from an unsorted file list, so
the same seed gives other object instances on another machine). Then the head camera is compared OUTSIDE the shelf box
and the table box (where no object can be) with the same numbers (mean <= 1 level, > 8 levels < 2 %); the wrist cameras
keep the full-image gate.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REF_BOX = (0.395, 0.06, 0.675, 0.34)
CUR_BOX = (0.0, 0.42, 1.0, 1.0)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts/memory_v2/press"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--official", required=True)
    ap.add_argument("--task", default="observe_and_pickup")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--out", default="/workspace/FastWAM-memory2/outputs/fullft/gen_obs/GEN_CHECK.json")
    ap.add_argument("--gate", choices=["pixel", "background"], default="pixel")
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
            keep = np.ones(d.shape[:2], bool)
            if args.gate == "background" and c == 0:
                h, w = keep.shape
                keep[int(CUR_BOX[1] * h):, :] = False
                keep[int(REF_BOX[1] * h):int(REF_BOX[3] * h), int(REF_BOX[0] * w):int(REF_BOX[2] * w)] = False
            m, big = float(d[keep].mean()), float((d.max(axis=-1)[keep] > 8).mean())
            cams.append({"camera": c, "mean_abs": round(m, 3), "over8": round(big, 5), "pass": m <= 1.0 and big < 0.02,
                         "region": "outside the shelf and table boxes" if (args.gate == "background" and c == 0) else "full"})
        row = {"episode": k, "cameras": cams, "length": [rg["length"], ro["length"]],
               "instruction_same": rg["instruction"] == ro["instruction"], "instruction": [rg["instruction"], ro["instruction"]]}
        row["pass"] = all(c["pass"] for c in cams)
        ok = ok and row["pass"]
        rows.append(row)
        print(f"[gencheck] episode {k}: {'PASS' if row['pass'] else 'FAIL'}; " + "; ".join(
            f"cam {c['camera']} mean {c.get('mean_abs')} >8 {c.get('over8')}" for c in cams)
            + f"; frames {row['length']}; instruction same {row['instruction_same']}", flush=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"pass": ok, "gate": args.gate, "episodes": rows}, indent=1) + "\n")
    print(f"GEN CHECK ({args.gate}) " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
