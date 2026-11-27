"""Card 25 (11-27 11:50, Opus): what the right-wrist difference of check 2 is. Read-only, CPU. For the first two seeds of
<base>, frame 0, target 0 against targets 1 and 3: the head camera and both wrist cameras as small PNGs, plus the |diff|
(max over RGB, x4, clipped) — base64 inside outputs/fullft/CARD25_PICS.json (the results push carries small JSON only).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/card25_pics.py --base outputs/fullft/gen_cf/check
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts/memory_v2/press"))
sys.path.insert(0, str(HERE))


def png(a, width=224):
    im = Image.fromarray(np.ascontiguousarray(a).astype(np.uint8))
    h = max(1, round(im.height * width / im.width))
    buf = io.BytesIO()
    im.resize((width, h), Image.BILINEAR).save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--out", default="/workspace/FastWAM-memory2/outputs/fullft/CARD25_PICS.json")
    a = ap.parse_args()
    import card25_check as cc
    import build_dense as bd
    common, data_path = bd.setup()
    cfg = json.loads((Path("/workspace/FastWAM-memory2/outputs/memory_v2/press") / "dense_observe_and_pickup_v1" /
                      "IDENTITY.json").read_text())["config"]
    maps = [cc.seed_to_episode(cc.tdir(a.base, k)) for k in range(5)]
    seeds = sorted(set(maps[0]).intersection(*[set(m) for m in maps[1:]]))[:2]
    out = {"note": "frame 0; cams 0 head, 1 / 2 wrists (order of data_path.Raw.images); diff = max |RGB| x4", "pairs": []}
    for s in seeds:
        frames = {}
        for k in (0, 1, 3):
            raw = data_path.Raw(cfg, bd.make_record(common, maps[k][s], "observe_and_pickup", "train"))
            try:
                frames[k] = [np.asarray(x) for x in raw.images(0)]
            finally:
                raw.close()
        for k in (1, 3):
            row = {"seed": s, "target": k, "cams": []}
            for c, (x, y) in enumerate(zip(frames[0], frames[k])):
                d = np.clip(np.abs(x.astype(np.int16) - y.astype(np.int16)).max(axis=-1) * 4, 0, 255)
                row["cams"].append({"cam": c, "shape": list(x.shape), "t0": png(x), "tk": png(y),
                                    "diff_x4": png(np.stack([d] * 3, -1))})
            out["pairs"].append(row)
    Path(a.out).write_text(json.dumps(out) + "\n")
    print(f"CARD25 PICS: {len(out['pairs'])} pairs -> {a.out} ({Path(a.out).stat().st_size} bytes)")


if __name__ == "__main__":
    main()
