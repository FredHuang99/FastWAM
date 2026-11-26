"""Card 25 (11-27 04:20, Opus): WHERE the 'same table' check failed (card25_check.py check 2, 11-27 02:03 on the 5090).
Read-only, CPU. For every seed and target pair of <base> (target 0 against target K, frame 0): per camera the largest
|difference|, the share of pixels differing at all and by more than 8 levels, and the bounding box (normalised x0 y0 x1 y1)
of the > 8 pixels; the head camera split into inside / outside the shelf box (REF_BOX) and the table box (CUR_BOX).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/card25_detail.py --base outputs/fullft/gen_cf/check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts/memory_v2/press"))
sys.path.insert(0, str(HERE))
REF_BOX = (0.395, 0.06, 0.675, 0.34)
CUR_BOX = (0.0, 0.42, 1.0, 1.0)


def box_mask(shape, b):
    h, w = shape
    m = np.zeros(shape, bool)
    m[int(b[1] * h):int(b[3] * h), int(b[0] * w):int(b[2] * w)] = True
    return m


def bbox(mask):
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None
    h, w = mask.shape
    return [round(xs.min() / w, 3), round(ys.min() / h, 3), round((xs.max() + 1) / w, 3), round((ys.max() + 1) / h, 3)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--targets", type=int, default=5)
    a = ap.parse_args()
    import card25_check as cc
    import build_dense as bd
    common, data_path = bd.setup()
    cfg = json.loads((Path("/workspace/FastWAM-memory2/outputs/memory_v2/press") / "dense_observe_and_pickup_v1" / "IDENTITY.json").read_text())["config"]
    maps = [cc.seed_to_episode(cc.tdir(a.base, k)) for k in range(a.targets)]
    seeds = sorted(set(maps[0]).intersection(*[set(m) for m in maps[1:]]))
    rows = []
    for s in seeds:
        frames = []
        for k in range(a.targets):
            raw = data_path.Raw(cfg, bd.make_record(common, maps[k][s], "observe_and_pickup", "train"))
            try:
                frames.append([np.asarray(x).astype(np.int16) for x in raw.images(0)])
            finally:
                raw.close()
        for k in range(1, a.targets):
            r = {"seed": s, "target": k}
            for c, (x, y) in enumerate(zip(frames[0], frames[k])):
                d = np.abs(x - y).max(axis=-1)
                cam = {"max": int(d.max()), "nonzero": round(float((d > 0).mean()), 5), "over8": round(float((d > 8).mean()), 5),
                       "bbox_over8": bbox(d > 8)}
                if c == 0:
                    shelf, table = box_mask(d.shape, REF_BOX), box_mask(d.shape, CUR_BOX)
                    rest = ~(shelf | table)
                    for name, m in (("shelf", shelf), ("table", table), ("rest", rest)):
                        cam[f"{name}_max"] = int(d[m].max())
                        cam[f"{name}_over8"] = round(float((d[m] > 8).mean()), 5)
                r[f"cam{c}"] = cam
            rows.append(r)
            print(json.dumps(r))
    print(f"CARD25 DETAIL: {len(rows)} pairs over {len(seeds)} seeds")


if __name__ == "__main__":
    main()
