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
    """11-24 19:30 fix: clipped to the image (the first run's objects-area box ran past the left edge, a negative start
    index wrapped around, so its 'OUTSIDE ...' line was wrong; that statistic is dropped)."""
    h, w = shape
    m = np.zeros((h, w), bool)
    y0, y1 = max(0, int(box[1] * h)), min(h, int(box[3] * h))
    x0, x1 = max(0, int(box[0] * w)), min(w, int(box[2] * w))
    m[y0:y1, x0:x1] = True
    return m


def pair_up(a, b):
    """Greedy nearest pairing of two candidate lists (match.candidates) by bbox centre -> [(dist px, area a, area b)]."""
    ca = [((c["bbox"][0] + c["bbox"][2]) / 2, (c["bbox"][1] + c["bbox"][3]) / 2, c["area"]) for c in a]
    cb = [((c["bbox"][0] + c["bbox"][2]) / 2, (c["bbox"][1] + c["bbox"][3]) / 2, c["area"]) for c in b]
    out, used = [], set()
    pairs = sorted((float(np.hypot(x[0] - y[0], x[1] - y[1])), i, j) for i, x in enumerate(ca) for j, y in enumerate(cb))
    done_a = set()
    for d, i, j in pairs:
        if i in done_a or j in used:
            continue
        done_a.add(i)
        used.add(j)
        out.append((round(d, 1), ca[i][2], cb[j][2]))
    return sorted(out)


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
    from fastwam.fullft import match as mt
    common, data_path = bd.setup()
    area = mt.candidate_area()
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
        rest = ~(rm | tm)
        lab, n = ndimage.label(ndimage.binary_dilation(big, iterations=2))
        regions = sorted(([int((lab == i).sum())] + [int(v) for v in (np.nonzero(lab == i)[1].min(), np.nonzero(lab == i)[0].min(),
                          np.nonzero(lab == i)[1].max(), np.nonzero(lab == i)[0].max())] for i in range(1, n + 1)), reverse=True)
        quiet = ~ndimage.binary_dilation(big, iterations=6)
        print(f"[gendiff] episode {k}: > 8 px {big.mean():.4f} of the image; in the reference box {big[rm].mean():.4f}, "
              f"table box {big[tm].mean():.4f}, rest (outside both boxes) {big[rest].mean():.4f} with mean |diff| "
              f"{float(np.abs(g - o)[rest].mean()):.3f}; regions (pixels, x0, y0, x1, y1) {regions[:8]}; "
              f"mean |diff| away from them {float(np.abs(g - o)[quiet].mean()):.3f} (n {int(quiet.sum())})", flush=True)
        co = mt.candidates(o.astype(np.uint8), CUR_BOX, area)
        cg = mt.candidates(g.astype(np.uint8), CUR_BOX, area)
        pr = pair_up(co, cg)
        print(f"[gendiff] episode {k} objects on the table (card 7's candidate finder): official {len(co)}, generated {len(cg)}; "
              f"paired by centre (distance px, area official, area generated) {pr}; within 5 px {sum(p[0] <= 5 for p in pr)}",
              flush=True)
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
