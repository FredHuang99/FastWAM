"""Plan v19 3.3 (A3, observe_and_pickup; 11-22, Opus): the zoom frames' two tools. Both read the dense cache's own
records and the delivery's image pipeline (dense_joint_v1 data_path.Raw / mosaic, the functions the caches and the closed
loop use); nothing under the dense cache is written.

  frames  (CPU, read-only) the head-camera image of frame 0 and of frames at 1/3, 2/3 and the end of the first N
          episodes, each with a 0.1 grid in normalised coordinates, as PNGs + one contact sheet
          -> outputs/fullft/zoom_boxes/  (the user sends them; Opus picks the two fixed boxes from them)
  build   (GPU, VAE only) the zoom latents of every episode for the given boxes: "ref" = frame 0 cropped to --ref-box,
          "cur" = every frame cropped to --cur-box (fullft/zoom.py zoom_images -> mosaic -> single-frame VAE, one frame at
          a time, as the closed loop encodes) -> <out>/<episode>.pt, resumable; first a pipeline check: frame 0 with the
          full box (0, 0, 1, 1) must reproduce the cache's own latent[0] (the recipe's VAE tolerance), else stop.

  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/zoom_tools.py frames [--n 6]
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/zoom_tools.py build --ref-box X0 Y0 X1 Y1 --cur-box X0 Y0 X1 Y1
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
CODE = Path("/restore-tmp/dense_joint_v1")
ROOT = R / "outputs/memory_v2/press/dense_observe_and_pickup_v1"


def delivery():
    import os
    os.environ.setdefault("FW_ROOT", "/workspace/FastWAM")
    if str(CODE) not in sys.path:
        sys.path.insert(0, str(CODE))
    import common      # noqa: E402  (dense_joint_v1, unmodified)
    import data_path   # noqa: E402
    return common, data_path


def cmd_frames(args):
    import numpy as np
    from PIL import Image, ImageDraw
    common, data_path = delivery()
    root = Path(args.root)
    cfg = common.read(root / "IDENTITY.json")["config"]
    records = common.read(root / "RECORDS.json")[: args.n]
    out = R / "outputs/fullft/zoom_boxes"
    out.mkdir(parents=True, exist_ok=True)
    tiles = []
    for rec in records:
        raw = data_path.Raw(cfg, rec)
        try:
            n = int(rec["length"])
            for f in sorted({0, n // 3, (2 * n) // 3, n - 1}):
                head = np.asarray(raw.images(f)[0])
                img = Image.fromarray(head).convert("RGB")
                w, h = img.size
                d = ImageDraw.Draw(img)
                for k in range(1, 10):
                    x, y = int(w * k / 10), int(h * k / 10)
                    d.line([(x, 0), (x, h)], fill=(255, 255, 0), width=1)
                    d.line([(0, y), (w, y)], fill=(255, 255, 0), width=1)
                    d.text((x + 2, 2), f"{k / 10:.1f}", fill=(255, 255, 0))
                    d.text((2, y + 2), f"{k / 10:.1f}", fill=(255, 255, 0))
                d.text((4, h - 14), f"{rec['episode_id']} frame {f}/{n}", fill=(255, 0, 0))
                name = f"{rec['episode_id'].replace('/', '_')}_f{f:04d}.png"
                img.save(out / name)
                tiles.append(img)
                print(f"[zoom] wrote {out / name} ({w}x{h})", flush=True)
        finally:
            raw.close()
    if tiles:
        w, h = tiles[0].size
        cols = 4
        sheet = Image.new("RGB", (w * cols, h * ((len(tiles) + cols - 1) // cols)))
        for i, t in enumerate(tiles):
            sheet.paste(t.resize((w, h)), ((i % cols) * w, (i // cols) * h))
        sheet.save(out / "SHEET.png")
        print(f"[zoom] contact sheet {out / 'SHEET.png'} ({len(tiles)} images)", flush=True)
    return 0


def cmd_build(args):
    import numpy as np
    import torch
    sys.path.insert(0, str(R / "src"))
    from fastwam.fullft.history import HistoryRule
    from fastwam.fullft.zoom import box_tag, zoom_images
    from fastwam.memory_s1.model import load_observation_encoders
    common, data_path = delivery()
    root = Path(args.root)
    cfg = common.read(root / "IDENTITY.json")["config"]
    records = common.read(root / "RECORDS.json")
    if args.limit:
        records = records[: args.limit]
    rule = HistoryRule("ar", zoom=True, zoom_ref_box=tuple(args.ref_box), zoom_cur_box=tuple(args.cur_box),
                       zoom_camera=args.camera)
    tag = box_tag(rule)
    out = Path(args.out) if args.out else R / f"outputs/memory_v2/press/zoom_{root.name}_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    num = common.read(CODE / "recipe.json")["numerical"]
    vae, text, tokenizer = load_observation_encoders(cfg, torch.device("cuda:0"))
    del text, tokenizer
    torch.cuda.empty_cache()

    @torch.no_grad()
    def encode(images):
        image = data_path.mosaic(images)[None].to("cuda:0", torch.bfloat16)       # [1, 3, H, W], as the closed loop
        return vae.model.encode(image.unsqueeze(2), vae.scale).detach()[0].cpu()   # [48, 1, 24, 20]

    first = records[0]
    raw = data_path.Raw(cfg, first)
    try:
        mine = encode(zoom_images(raw.images(0), (0.0, 0.0, 1.0, 1.0), args.camera))
    finally:
        raw.close()
    cached = torch.load(root / "cache" / first["episode_id"].replace("/", "_") / "encodings.pt", map_location="cpu",
                        weights_only=True, mmap=True)["latent"][0]
    err = float((mine.float() - cached.float()).abs().max())
    ok = torch.allclose(mine.float(), cached.float(), atol=num["vae_atol"], rtol=num["vae_rtol"])
    print(f"[zoom] pipeline check {first['episode_id']} frame 0, full box vs cache latent[0]: max |diff| {err:.3g} "
          f"(atol {num['vae_atol']}, rtol {num['vae_rtol']}) -> {'OK' if ok else 'FAILED'}", flush=True)
    if not ok:
        return 1
    started, done = time.monotonic(), 0
    total = sum(int(r["length"]) for r in records)
    for rec in records:
        path = out / (rec["episode_id"].replace("/", "_") + ".pt")
        if path.exists():
            v = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
            if v.get("tag") == tag and int(v["cur"].shape[0]) == int(rec["length"]):
                done += int(rec["length"])
                continue
            raise SystemExit(f"{path} exists with another tag / length: use a new --out")
        raw = data_path.Raw(cfg, rec)
        try:
            ref = encode(zoom_images(raw.images(0), rule.zoom_ref_box, args.camera))
            cur = torch.stack([encode(zoom_images(raw.images(i), rule.zoom_cur_box, args.camera))
                               for i in range(int(rec["length"]))])
        finally:
            raw.close()
        if not (bool(ref.isfinite().all()) and bool(cur.isfinite().all())):
            raise SystemExit(f"non-finite zoom latent in {rec['episode_id']}")
        tmp = path.with_suffix(".tmp")
        torch.save({"ref": ref, "cur": cur, "tag": tag, "episode_id": rec["episode_id"], "length": int(rec["length"])}, tmp)
        tmp.rename(path)
        done += int(rec["length"])
        el = time.monotonic() - started
        print(f"[zoom] {rec['episode_id']}: {rec['length']} frames; {done}/{total}, {el / 60:.1f} min", flush=True)
    (out / "ZOOM.json").write_text(json.dumps({"tag": tag, "ref_box": list(rule.zoom_ref_box),
                                               "cur_box": list(rule.zoom_cur_box), "camera": args.camera,
                                               "root": str(root), "episodes": len(records), "frames": total,
                                               "pipeline_check_max_diff": err}, indent=1) + "\n")
    print(f"[zoom] done: {out} (tag {tag}); training: data.zoom_root={out} history.zoom=true "
          f"history.zoom_ref_box=[{','.join(map(str, args.ref_box))}] history.zoom_cur_box=[{','.join(map(str, args.cur_box))}]",
          flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("frames")
    f.add_argument("--root", default=str(ROOT))
    f.add_argument("--n", type=int, default=6)
    b = sub.add_parser("build")
    b.add_argument("--root", default=str(ROOT))
    b.add_argument("--ref-box", type=float, nargs=4, required=True)
    b.add_argument("--cur-box", type=float, nargs=4, required=True)
    b.add_argument("--camera", type=int, default=0)
    b.add_argument("--out", default="")
    b.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    return cmd_frames(args) if args.cmd == "frames" else cmd_build(args)


if __name__ == "__main__":
    raise SystemExit(main())
