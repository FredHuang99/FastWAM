"""Card 8 render check FAILED on the head camera (11-24 19:00: mean 5.3-6.3 levels, 9-11 % of pixels > 8; wrist cameras
0.34-1.13 / < 2 %). Where do the generated and official frame-0 head images differ? Read-only, CPU.
Per episode: the > 8 mask split into the reference box (shelf), the table box (candidates), the rest; the connected
difference regions (bbox, pixels); the mean |diff| outside all regions (a global rendering shift would show there);
and a sheet official | generated | difference (white = > 8) -> outputs/fullft/gen_obs/GEN_DIFF.png
Also: the order glob() gives the object model files here (RMBench envs/observe_and_pickup.py picks a model id with
np.random.choice over that UNSORTED list: a different file order on another machine gives other models for the same
seed). Prints GEN DIFF lines.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/gen_diff.py --gen <dir>/data --official <dir>/data --n 3
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts/memory_v2/press"))
REF_BOX = (0.395, 0.06, 0.675, 0.34)
CUR_BOX = (0.0, 0.42, 1.0, 1.0)


def box_mask(shape, box):
    h, w = shape
    m = np.zeros((h, w), bool)
    m[int(box[1] * h):int(box[3] * h), int(box[0] * w):int(box[2] * w)] = True
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--official", required=True)
    ap.add_argument("--task", default="observe_and_pickup")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--rmbench", default="/workspace/FastWAM/resources/RMBench")
    args = ap.parse_args()
    import build_dense as bd
    from PIL import Image
    from scipy import ndimage
    from fastwam.fullft.match import candidate_area
    common, data_path = bd.setup()
    area = candidate_area()
    print(f"[gendiff] the objects' projected area (x0, y0, x1, y1, fractions of the image) {[round(v, 3) for v in area]} (+0.03)")
    cfg = json.loads((Path("/workspace/FastWAM-memory2/outputs/memory_v2/press") / f"dense_{args.task}_v1" / "IDENTITY.json").read_text())["config"]
    tiles = []
    for k in range(args.n):
        name = f"episode_{k:07d}.hdf5"
        rg = bd.make_record(common, Path(args.gen) / name, args.task, "train")
        ro = bd.make_record(common, Path(args.official) / name, args.task, "train")
        a, b = data_path.Raw(cfg, rg), data_path.Raw(cfg, ro)
        try:
            g, o = np.asarray(a.images(0)[0]).astype(np.int16), np.asarray(b.images(0)[0]).astype(np.int16)
        finally:
            a.close()
            b.close()
        d = np.abs(g - o).max(axis=-1)
        big = d > 8
        rm, tm = box_mask(d.shape, REF_BOX), box_mask(d.shape, CUR_BOX)
        am = box_mask(d.shape, (area[0] - 0.03, area[1] - 0.03, area[2] + 0.03, area[3] + 0.03))
        rest = ~(rm | tm)
        other = ~(rm | am)
        lab, n = ndimage.label(ndimage.binary_dilation(big, iterations=2))
        regions = sorted(([int((lab == i).sum())] + [int(v) for v in (np.nonzero(lab == i)[1].min(), np.nonzero(lab == i)[0].min(),
                          np.nonzero(lab == i)[1].max(), np.nonzero(lab == i)[0].max())] for i in range(1, n + 1)), reverse=True)
        quiet = ~ndimage.binary_dilation(big, iterations=6)
        print(f"[gendiff] episode {k}: > 8 px {big.mean():.4f} of the image; in the reference box {big[rm].mean():.4f}, "
              f"table box {big[tm].mean():.4f}, rest {big[rest].mean():.4f}; OUTSIDE the shelf box and the objects' area: > 8 px "
              f"{big[other].mean():.4f}, mean |diff| {float(np.abs(g - o)[other].mean()):.3f}; regions (pixels, x0, y0, x1, y1) {regions[:8]}; "
              f"mean |diff| away from them {float(np.abs(g - o)[quiet].mean()):.3f} (n {int(quiet.sum())})", flush=True)
        vis = np.concatenate([o, g, np.repeat((big * 255)[..., None], 3, axis=-1)], axis=1).astype(np.uint8)
        tiles.append(Image.fromarray(vis).resize((vis.shape[1] * 2, vis.shape[0] * 2)))
    out = Path("/workspace/FastWAM-memory2/outputs/fullft/gen_obs/GEN_DIFF.png")
    sheet = Image.new("RGB", (tiles[0].width, sum(t.height for t in tiles)))
    y = 0
    for t in tiles:
        sheet.paste(t, (0, y))
        y += t.height
    sheet.save(out)
    print(f"[gendiff] sheet {out} (rows: official | generated | > 8 levels)")
    for m in ("009_toycar", "010_mouse", "011_stapler", "012_bell", "013_playingcards"):
        files = glob.glob(os.path.join(args.rmbench, "assets/objects", m, "model_data*.json"))
        names = [os.path.basename(f) for f in files]
        print(f"[gendiff] glob order {m}: {len(names)} files {names} ({'sorted' if names == sorted(names) else 'NOT sorted'})")
    print("GEN DIFF done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
