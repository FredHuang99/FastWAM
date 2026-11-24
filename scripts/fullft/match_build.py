"""Plan v20 card 7 (obs_match, 11-24, Opus): the match-frame zoom cache. GPU (VAE + the frozen encoder). Runs in
mwam5090 (the observe_and_pickup dense cache, the delivery's raw frames and the plain zoom cache zoom_obs_02102ba0 are
there). Nothing under the dense cache or the plain zoom cache is written.
Per episode of the dense cache: "ref" = the MATCH frame (fullft/match.py match_image on frame 0's head camera, the same
function the closed loop calls) through the delivery's mosaic and the single-frame VAE; "cur" = the plain zoom cache's
"cur" (the same boxes: the current table crop of every frame), copied; "tag" = zoom.box_tag of the rule with
zoom_match (a plain-zoom model refuses this cache and vice versa).
Checks first (stop on failure): (1) the plain cache's tag is the rule's boxes without the match; (2) pipeline: frame 0
cropped to the current box through this script's encoder equals the plain cache's cur[0] (the recipe's VAE tolerance);
(3) the encoder file's sha256 is the probe's (match.Scorer).
Writes <out>/<episode>.pt, ZOOM.json (as zoom_tools build) and MATCH.json (per episode: candidates, scores, the best).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/match_build.py [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
R = Path("/workspace/FastWAM-memory2")
ROOT = R / "outputs/memory_v2/press/dense_observe_and_pickup_v1"
# the plain zoom cache: zoom_build_5090.sh wrote it here (relay name zoom_obs_02102ba0); a relay download lands in the second
PLAINS = (R / "outputs/memory_v2/press/zoom_dense_observe_and_pickup_v1_02102ba0", R / "outputs/memory_v2/press/zoom_obs_02102ba0")
REF_BOX = (0.395, 0.06, 0.675, 0.34)
CUR_BOX = (0.0, 0.42, 1.0, 1.0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--plain", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    sys.path.insert(0, str(R / "src"))
    from fastwam.fullft.history import HistoryRule
    from fastwam.fullft.match import Scorer, candidate_area, match_image
    from fastwam.fullft.zoom import box_tag, zoom_images
    from fastwam.memory_s1.model import load_observation_encoders
    from zoom_tools import CODE, delivery
    common, data_path = delivery()
    found = [p for p in PLAINS if (p / "ZOOM.json").exists()]
    if not args.plain and not found:
        print(f"[match-build] STOP: no plain zoom cache (ZOOM.json) in {[str(p) for p in PLAINS]}")
        return 1
    root, plain = Path(args.root), Path(args.plain) if args.plain else found[0]
    print(f"[match-build] plain zoom cache {plain}", flush=True)
    cfg = common.read(root / "IDENTITY.json")["config"]
    records = common.read(root / "RECORDS.json")
    base = dict(variant="ar", zoom=True, zoom_ref_box=REF_BOX, zoom_cur_box=CUR_BOX, zoom_camera=0)
    tag_plain, tag = box_tag(HistoryRule(**base)), box_tag(HistoryRule(**base, zoom_match=True))
    zj = json.loads((plain / "ZOOM.json").read_text())
    if zj.get("tag") != tag_plain:
        print(f"[match-build] STOP: the plain cache's tag {zj.get('tag')} != the boxes' {tag_plain}")
        return 1
    out = Path(args.out) if args.out else R / f"outputs/memory_v2/press/zoom_obs_match_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    num = common.read(CODE / "recipe.json")["numerical"]
    vae, text, tokenizer = load_observation_encoders(cfg, torch.device("cuda:0"))
    del text, tokenizer
    torch.cuda.empty_cache()
    scorer = Scorer.get("cuda:0")
    area = candidate_area()
    print(f"[match-build] tags plain {tag_plain} match {tag}; candidate area {[round(v, 4) for v in area]}; out {out}", flush=True)

    @torch.no_grad()
    def encode(images):
        image = data_path.mosaic(images)[None].to("cuda:0", torch.bfloat16)
        return vae.model.encode(image.unsqueeze(2), vae.scale).detach()[0].cpu()

    first = records[0]
    raw = data_path.Raw(cfg, first)
    try:
        mine = encode(zoom_images(raw.images(0), CUR_BOX, 0))
    finally:
        raw.close()
    cached = torch.load(plain / (first["episode_id"].replace("/", "_") + ".pt"), map_location="cpu", weights_only=True)["cur"][0]
    err = float((mine.float() - cached.float()).abs().max())
    ok = torch.allclose(mine.float(), cached.float(), atol=num["vae_atol"], rtol=num["vae_rtol"])
    print(f"[match-build] pipeline check {first['episode_id']} frame 0, current box vs the plain cache's cur[0]: "
          f"max |diff| {err:.3g} -> {'OK' if ok else 'FAILED'}", flush=True)
    if not ok:
        return 1
    meta, started = {}, time.monotonic()
    for k, rec in enumerate(records):
        eid = rec["episode_id"]
        path = out / (eid.replace("/", "_") + ".pt")
        src = torch.load(plain / (eid.replace("/", "_") + ".pt"), map_location="cpu", weights_only=True)
        if int(src["cur"].shape[0]) != int(rec["length"]):
            print(f"[match-build] STOP: {eid} plain cur length {src['cur'].shape[0]} != {rec['length']}")
            return 1
        raw = data_path.Raw(cfg, rec)
        try:
            views = [np.ascontiguousarray(np.asarray(x)) for x in raw.images(0)]
        finally:
            raw.close()
        img, m = match_image(views[0].astype(np.uint8), REF_BOX, CUR_BOX, scorer, area)
        views[0] = img
        ref = encode(views)
        if not bool(ref.isfinite().all()):
            print(f"[match-build] STOP: non-finite match latent in {eid}")
            return 1
        tmp = path.with_suffix(".tmp")
        torch.save({"ref": ref, "cur": src["cur"], "tag": tag, "episode_id": eid, "length": int(rec["length"])}, tmp)
        tmp.rename(path)
        best = int(np.argmax(m["scores"])) if m["scores"] else None
        meta[eid] = dict(m, best=best)
        if k < 3 or k == len(records) - 1:
            from PIL import Image
            Image.fromarray(img).save(out / f"match_{eid.replace('/', '_')}.png")
        print(f"[match-build] {eid}: {len(m['candidates'])} candidates, scores {m['scores']}, best {best}; "
              f"{k + 1}/{len(records)}, {(time.monotonic() - started) / 60:.1f} min", flush=True)
    from fastwam.fullft import match as mt
    (out / "MATCH.json").write_text(json.dumps({"encoder": {"model": mt.MODEL, "revision": mt.REVISION, "sha256": mt.SHA256},
                                                "settings": {"fg": mt.FG, "min_area": mt.MIN_AREA, "merge_px": mt.MERGE_PX,
                                                             "keep": mt.KEEP, "margin": mt.MARGIN, "low": mt.LOW, "high": mt.HIGH},
                                                "candidate_area": area, "episodes": meta}, indent=1) + "\n")
    (out / "ZOOM.json").write_text(json.dumps({"tag": tag, "ref_box": list(REF_BOX), "cur_box": list(CUR_BOX), "camera": 0,
                                               "match": "dinov2-crop-v2", "root": str(root), "episodes": len(records),
                                               "cur_from": str(plain), "pipeline_check_max_diff": err}, indent=1) + "\n")
    print(f"[match-build] done: {out} (tag {tag}); training: data.zoom_root={out} history.zoom=true history.zoom_match=true",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
