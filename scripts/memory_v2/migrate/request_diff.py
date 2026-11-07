"""Pixel comparison of two dumped decision requests of the same scene and frame (online.py run --dump-first),
e.g. the A100's and the 5090's frame 0 of put_back seed 4300030 (11-08, 5090 online diagnosis).

Per camera: mean / max absolute difference (0-255), the fraction of pixels differing by more than 8 levels, the mean
colour of each image; plus a difference picture (|a - b| x 4, clipped) per camera in --out. Proprio and the
instruction are compared too. Read-only for both requests.
  /opt/mwam/bin/python scripts/memory_v2/migrate/request_diff.py A.pkl B.pkl --out DIR
"""
from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np


def images(req):
    obs = sorted(req["observations"], key=lambda r: int(r["frame_id"]))[-1]
    return [np.frombuffer(b, dtype=np.uint8).reshape(s) for b, s in zip(obs["images"], obs["shapes"])], obs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--names", nargs=2, default=["A", "B"])
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    ra, rb = (pickle.loads(Path(p).read_bytes()) for p in (args.a, args.b))
    na, nb = args.names
    print(f"request {na}: {args.a}\nrequest {nb}: {args.b}")
    for k in ("task", "episode_seed", "current_id", "instruction"):
        print(f"  {k}: {'same' if ra.get(k) == rb.get(k) else f'DIFFERENT {ra.get(k)!r} vs {rb.get(k)!r}'}")
    ia, oa = images(ra)
    ib, ob = images(rb)
    pa, pb = np.asarray(oa.get("proprio") or [], float), np.asarray(ob.get("proprio") or [], float)
    print(f"  proprio max |diff|: {float(np.abs(pa - pb).max()) if pa.shape == pb.shape and pa.size else 'shape differs'}")
    out = Path(args.out) if args.out else None
    if out:
        out.mkdir(parents=True, exist_ok=True)
    print("| camera | shape | mean abs diff | max abs diff | pixels > 8 levels | mean RGB " + na + " | mean RGB " + nb + " |")
    print("|---|---|---|---|---|---|---|")
    for i, (a, b) in enumerate(zip(ia, ib)):
        if a.shape != b.shape:
            print(f"| {i} | {a.shape} vs {b.shape} | - | - | - | - | - |")
            continue
        d = np.abs(a.astype(np.int16) - b.astype(np.int16))
        print(f"| {i} | {a.shape} | {d.mean():.2f} | {int(d.max())} | {100 * float((d.max(-1) > 8).mean()):.1f} % | "
              f"{np.round(a.reshape(-1, 3).mean(0), 1).tolist()} | {np.round(b.reshape(-1, 3).mean(0), 1).tolist()} |")
        if out:
            from PIL import Image
            Image.fromarray(np.clip(d * 4, 0, 255).astype(np.uint8)).save(out / f"diff_cam{i}.png")
            Image.fromarray(a).save(out / f"{na}_cam{i}.png")
            Image.fromarray(b).save(out / f"{nb}_cam{i}.png")
    if out:
        print(f"pictures: {out}")


if __name__ == "__main__":
    main()
