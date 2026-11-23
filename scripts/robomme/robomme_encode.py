"""RoboMME encoding (11-23 19:20, Opus; plan R0 section 3, the step after robomme_convert.py; the user's scheduled task
said: encode once the conversion is done and the LIBERO base is downloaded, both done 17:34). mwam5090, one GPU.
Reads the conversion (robomme_convert.py: <convert>/RECORDS.json, <Task>/episode_<k>.npz / .json, events_<Task>.json)
read-only; writes a dense-cache-like root (the layout fullft.data.DenseEpisodes reads):
  <out>/RECORDS.json                     episode_id, task, split, length, N, seed, robomme_split
  <out>/IDENTITY.json                    config (the VAE / T5 / tokenizer paths of --check-root's IDENTITY), the image
                                         pipeline, the clip padding rule, the pipeline check, the LIBERO base sha256
  <out>/events/events_<Task>.json        copied from the conversion (fullft events-file format)
  <out>/cache/<Task>_episode_<k>/encodings.pt + COMPLETE.json
      latent       [L, 48, 1, h, w]  every frame alone (the eager single-frame encoder, as memory_s1.encode_latent and
                                     the closed loop do: the history frames)
      video_latent [L, 48, 3, h, w]  the 9-frame clip of each anchor a: frames a, a + 4, ..., a + 32 (Fast-WAM's
                                     num_frames 33, action_video_freq_ratio 4), encoded together; past the end of the
                                     episode the last frame repeats (LeRobot's rule, which the LIBERO base was trained
                                     with: lerobot_dataset.py _get_query_indices clamps to the episode)
      video_valid  [L, 9]            True = a real frame (the "valid" polarity of the RoboTwin caches)
      text [128, D], text_valid [128]  T5 of TASK_PROMPT.format(task=goal) (memory_s1.encode_text; padding zeroed)
      proprio_raw [L, 8]  = eef_state (x y z roll pitch yaw) + gripper_state (2 widths)  (LIBERO's 8-number layout)
      actions_raw [L, 7]  = eef_action (pose + gripper -1 close / +1 open), absolute; action_valid [L]
      joint_state [L, 7], joint_action [L, 8]
    No "proprio" / "actions" keys: their normalisation (and LIBERO's delta pose actions) is a training-side choice
    still open, so nothing can read unnormalised values by mistake.
Image pipeline = the one Fast-WAM's LIBERO base was trained with (fastwam.datasets.lerobot.RobotVideoDataset with
configs/data/libero_2cam.yaml): per camera uint8 -> float / 255 -> torchvision Resize([224, 224]); front | wrist
concatenated horizontally (224 x 448); ResizeSmallestSideAspectPreserving + CenterCrop to [224, 448];
Normalize(0.5, 0.5) -> [-1, 1].
Pipeline check first (--check-root, a RoboTwin dense cache of the delivery on this machine): its episode 0 is
re-encoded from the delivery's own images (dense_joint_v1 data_path.Raw / mosaic, unmodified): latent[0]; the clip of
anchor 0 (no padding); and, for the record, a batch of two clips against two single clips and the clip of the LAST
anchor under two padding rules (repeat the last frame / zero image). Tolerances: the delivery's recipe.json (vae_atol,
vae_rtol). The RoboMME encoding starts only when latent[0] and clip 0 match (the VAE calls reproduce the caches the
RMBench models were trained on) and the image self-test passes; otherwise it stops. 11-23 19:51 (first run on the
5090): latent[0], clip 0 and the repeat-last padding matched exactly (max |diff| 0), the zero image did not (6.49), a
batch of 2 clips did NOT match single clips, so the encoding runs one clip / frame at a time (--batch 1).
Splits: RoboMME's 100 demos per task are all its train split; here every --val-every-th episode (by episode number,
k % 10 == 9 by default, spreading the counts N) is 'val', the rest 'train'. RECORDS.json can be rewritten without
re-encoding.
  PYTHONPATH=src /opt/mwam/bin/python scripts/robomme/robomme_encode.py --convert DIR --out DIR --check-root DIR
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

R = Path("/workspace/FastWAM-memory2")
CODE = Path("/restore-tmp/dense_joint_v1")
NUM_FRAMES, RATIO = 33, 4
OFFSETS = list(range(0, NUM_FRAMES, RATIO))                    # 0, 4, ..., 32: the 9 video frames of a clip


def clip_indices(anchor: int, length: int, rule: str):
    """[(frame or None)] * 9 and valid [9] for the clip of `anchor`: frames past the end follow `rule` ('repeat' = the
    last frame, 'zero' = None, a zero image)."""
    out, valid = [], []
    for o in OFFSETS:
        f = anchor + o
        valid.append(f < length)
        out.append(f if f < length else (length - 1 if rule == "repeat" else None))
    return out, valid


def libero_image(front: np.ndarray, wrist: np.ndarray) -> torch.Tensor:
    """[T, H, W, 3] uint8 x 2 -> [T, 3, 224, 448] float in [-1, 1], RobotVideoDataset's LIBERO path."""
    import torchvision.transforms as TF
    from fastwam.datasets.dataset_utils import CenterCrop, Normalize, ResizeSmallestSideAspectPreserving
    resize = TF.Resize([224, 224])
    cams = []
    for x in (front, wrist):
        t = torch.from_numpy(np.ascontiguousarray(x)).permute(0, 3, 1, 2)
        assert t.dtype == torch.uint8
        cams.append(resize(t.to(torch.float32) / 255.0))
    video = torch.cat(cams, dim=-1)                              # [T, 3, 224, 448]
    args = {"img_w": 448, "img_h": 224}
    video = CenterCrop(args=args)(ResizeSmallestSideAspectPreserving(args=args)(video))
    return Normalize(args={"mean": 0.5, "std": 0.5})(video)


def image_selftest() -> bool:
    """A white front and a black wrist image must come out [1, 3, 224, 448] with +1 on the left, -1 on the right."""
    white = libero_image(np.full((1, 256, 256, 3), 255, np.uint8), np.zeros((1, 256, 256, 3), np.uint8))
    left, right = white[..., :224], white[..., 224:]
    dev = max(float((left - 1).abs().max()), float((right + 1).abs().max()))
    ok = tuple(white.shape) == (1, 3, 224, 448) and dev < 1e-4      # 11-23 19:51: float rounding, not exact
    print(f"[check] image pipeline: white front | black wrist -> {tuple(white.shape)}, left {float(left.min()):.7f}.."
          f"{float(left.max()):.7f}, right {float(right.min()):.7f}..{float(right.max()):.7f} (max deviation {dev:.2g}): "
          f"{'+1 | -1 as expected' if ok else 'NOT +1 | -1'}", flush=True)
    return ok


class Encoders:
    def __init__(self, cfg, device):
        from fastwam.memory_s1.model import load_observation_encoders
        self.vae, self.text, self.tokenizer = load_observation_encoders(cfg, device)
        self.device = device

    @torch.no_grad()
    def frames(self, images: torch.Tensor) -> torch.Tensor:          # [B, 3, H, W] -> [B, 48, 1, h, w]
        from fastwam.memory_s1.model import encode_latent
        with torch.autocast("cuda", enabled=False):
            return encode_latent(self.vae, images.to(self.device)).cpu()

    @torch.no_grad()
    def clips(self, clips: torch.Tensor) -> torch.Tensor:            # [B, 3, 9, H, W] -> [B, 48, 3, h, w]
        with torch.autocast("cuda", enabled=False):
            return self.vae.model.encode(clips.to(self.device, torch.bfloat16), self.vae.scale).detach().cpu()

    def prompt(self, goal: str):
        from fastwam.memory_s1.model import encode_text
        f, v = encode_text(self.text, self.tokenizer, goal, self.device)
        return f[0].cpu(), v[0].cpu()


def close(a, b, num) -> tuple:
    a, b = a.float(), b.float()
    return bool(torch.allclose(a, b, atol=num["vae_atol"], rtol=num["vae_rtol"])), float((a - b).abs().max())


def pipeline_check(enc: Encoders, root: Path, report: dict) -> bool:
    """Re-encode episode 0 of a RoboTwin dense cache from the delivery's images; True when the VAE calls reproduce it."""
    if str(CODE) not in sys.path:
        sys.path.insert(0, str(CODE))
    import common      # noqa: E402  (dense_joint_v1, unmodified)
    import data_path   # noqa: E402
    num = common.read(CODE / "recipe.json")["numerical"]
    cfg = common.read(root / "IDENTITY.json")["config"]
    rec = common.read(root / "RECORDS.json")[0]
    cached = torch.load(root / "cache" / rec["episode_id"].replace("/", "_") / "encodings.pt", map_location="cpu",
                        weights_only=True, mmap=True)
    report["cache_keys"] = {k: [list(v.shape), str(v.dtype)] for k, v in cached.items() if torch.is_tensor(v)}
    print(f"[check] {rec['episode_id']} cache: " + "; ".join(f"{k} {s} {d}" for k, (s, d) in report["cache_keys"].items()),
          flush=True)
    n = int(rec["length"])
    raw = data_path.Raw(cfg, rec)
    mosaics = {}

    def m(f):
        if f is None:
            return torch.zeros_like(m(0))
        if f not in mosaics:
            mosaics[f] = data_path.mosaic(raw.images(f)).float()
        return mosaics[f]

    def clip(anchor, rule):
        idx, _ = clip_indices(anchor, n, rule)
        return torch.stack([m(f) for f in idx], dim=1)            # [3, 9, H, W]
    try:
        ok0, d0 = close(enc.frames(m(0)[None])[0], cached["latent"][0], num)
        c0 = clip(0, "repeat")
        okc, dc = close(enc.clips(c0[None])[0], cached["video_latent"][0], num)
        last = n - 1
        rules = {}
        for rule in ("repeat", "zero"):
            rules[rule] = close(enc.clips(clip(last, rule)[None])[0], cached["video_latent"][last], num)
        c1 = clip(min(8, n - 1), "repeat")
        pair = enc.clips(torch.stack([c0, c1]))
        b0, b1 = close(pair[0], enc.clips(c0[None])[0], num), close(pair[1], enc.clips(c1[None])[0], num)
        okb, db = b0[0] and b1[0], max(b0[1], b1[1])
        vv = cached["video_valid"][last].bool().tolist() if "video_valid" in cached else None
    finally:
        raw.close()
    report.update(latent0=[ok0, d0], clip0=[okc, dc], last_anchor=last, last_clip=rules, batch_equals_single=[okb, db],
                  cached_video_valid_last=vv, tolerance=num)
    print(f"[check] latent[0] {'OK' if ok0 else 'DIFFERENT'} (max |diff| {d0:.3g}); clip of anchor 0 "
          f"{'OK' if okc else 'DIFFERENT'} ({dc:.3g}); last anchor {last}: repeat-last "
          f"{'OK' if rules['repeat'][0] else 'DIFFERENT'} ({rules['repeat'][1]:.3g}), zero image "
          f"{'OK' if rules['zero'][0] else 'DIFFERENT'} ({rules['zero'][1]:.3g}); batch of 2 = single "
          f"{'OK' if okb else 'DIFFERENT'} ({db:.3g}; the encoding runs one at a time); cached video_valid of the last anchor {vv} "
          f"(tolerance atol {num['vae_atol']}, rtol {num['vae_rtol']})", flush=True)
    return bool(ok0 and okc)                 # batches are not used (--batch 1), so they need not match


def encode_episode(enc, convert: Path, rec: dict, rule: str, batch: int, text_cache: dict) -> dict:
    z = np.load(convert / rec["file"])
    meta = json.loads((convert / rec["file"]).with_suffix(".json").read_text())
    images = libero_image(z["front_rgb"], z["wrist_rgb"])          # [L, 3, 224, 448]
    n = int(images.shape[0])
    latent = torch.cat([enc.frames(images[i:i + batch]) for i in range(0, n, batch)])
    zero = torch.zeros_like(images[0])
    video, valid = [], []
    for start in range(0, n, batch):
        clips = []
        for a in range(start, min(n, start + batch)):
            idx, ok = clip_indices(a, n, rule)
            clips.append(torch.stack([images[f] if f is not None else zero for f in idx], dim=1))
            valid.append(ok)
        video.append(enc.clips(torch.stack(clips)))
    goal = meta["goal"]
    if goal not in text_cache:
        text_cache[goal] = enc.prompt(goal)
    text, text_valid = text_cache[goal]
    out = {"latent": latent, "video_latent": torch.cat(video), "video_valid": torch.tensor(valid, dtype=torch.bool),
           "text": text, "text_valid": text_valid.bool(),
           "proprio_raw": torch.from_numpy(np.concatenate([z["eef_state"], z["gripper_state"]], axis=1)).float(),
           "actions_raw": torch.from_numpy(z["eef_action"]).float(),
           "action_valid": torch.from_numpy(z["action_valid"]).bool(),
           "joint_state": torch.from_numpy(z["joint_state"]).float(),
           "joint_action": torch.from_numpy(z["joint_action"]).float()}
    for k in ("latent", "video_latent"):
        if not bool(out[k].isfinite().all()):
            raise SystemExit(f"non-finite {k} in {rec['episode_id']}")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--convert", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check-root", default=str(R / "outputs/memory_v2/press/dense_observe_and_pickup_v1"))
    ap.add_argument("--base", default="/workspace/FastWAM/resources/base/libero_optional_idm_2cam224.pt")
    ap.add_argument("--tasks", nargs="+", default=["PickXtimes", "BinFill"])
    ap.add_argument("--limit", type=int, default=0, help="first N episodes per task (0 = all)")
    ap.add_argument("--batch", type=int, default=1, help="1 = one clip / frame at a time, as the delivery (19:51: a "
                                                       "batch of 2 clips did not reproduce single clips)")
    ap.add_argument("--val-every", type=int, default=10)
    args = ap.parse_args(argv)
    convert, out, root = Path(args.convert), Path(args.out), Path(args.check_root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "events").mkdir(exist_ok=True)
    cfg = json.loads((root / "IDENTITY.json").read_text())["config"]
    device = torch.device("cuda:0")
    enc = Encoders(cfg, device)
    report = {}
    passed = pipeline_check(enc, root, report)
    rule = "repeat"
    img_ok = image_selftest()
    report["image_pipeline_selftest"] = img_ok
    passed = passed and img_ok
    ident_path = out / "IDENTITY.json"
    identity = {"config": cfg, "convert": str(convert), "convert_identity": json.loads((convert / "IDENTITY.json").read_text()),
                "image_pipeline": "RobotVideoDataset LIBERO: uint8/255 -> Resize([224,224]) per camera -> front|wrist -> "
                                  "ResizeSmallestSide+CenterCrop [224,448] -> Normalize(0.5,0.5)",
                "clip": {"num_frames": NUM_FRAMES, "ratio": RATIO, "offsets": OFFSETS, "padding": rule},
                "check": report, "val_every": args.val_every}
    sha = Path(args.base + ".sha256")
    identity["base"] = {"path": args.base, "sha256": sha.read_text().split()[0] if sha.exists() else None}
    if not passed:
        ident_path.write_text(json.dumps(identity, indent=1, default=str) + "\n")
        print("[encode] FAILED: the pipeline check did not pass (see [check]); nothing encoded", flush=True)
        return 1
    agree = report["last_clip"]["repeat"][0]
    print(f"[encode] pipeline check passed; clips past the end repeat the last frame (LeRobot's rule); the delivery's "
          f"RMBench caches {'do the same' if agree else 'do NOT (recorded in IDENTITY.json)'}", flush=True)
    rows = [r for r in json.loads((convert / "RECORDS.json").read_text()) if r["task"] in args.tasks]
    if args.limit:
        keep = []
        for t in args.tasks:
            keep += [r for r in rows if r["task"] == t][:args.limit]
        rows = keep
    for t in args.tasks:
        src = convert / f"events_{t}.json"
        if src.exists():
            (out / "events" / src.name).write_text(src.read_text())
    records, text_cache, t0, frames = [], {}, time.time(), 0
    for i, r in enumerate(rows):
        folder = out / "cache" / r["episode_id"].replace("/", "_")
        k = int(r["episode_id"].rsplit("_", 1)[1])
        split = "val" if args.val_every and k % args.val_every == args.val_every - 1 else "train"
        records.append({"episode_id": r["episode_id"], "task": r["task"], "split": split, "length": r["length"],
                        "N": r["N"], "seed": r["seed"], "robomme_split": r["robomme_split"]})
        if (folder / "COMPLETE.json").exists():
            continue
        folder.mkdir(parents=True, exist_ok=True)
        e = encode_episode(enc, convert, r, rule, args.batch, text_cache)
        if int(e["latent"].shape[0]) != int(r["length"]):
            raise SystemExit(f"{r['episode_id']}: {e['latent'].shape[0]} frames, RECORDS says {r['length']}")
        tmp = folder / "encodings.tmp"
        torch.save(e, tmp)
        tmp.rename(folder / "encodings.pt")
        (folder / "COMPLETE.json").write_text(json.dumps({"frames": int(r["length"]), "padding": rule}) + "\n")
        frames += int(r["length"])
        el = time.time() - t0
        print(f"[encode] {r['episode_id']}: {r['length']} frames; {i + 1}/{len(rows)} episodes; "
              f"{frames / max(el, 1e-9):.1f} frames/s; {el / 60:.1f} min", flush=True)
    (out / "RECORDS.json").write_text(json.dumps(records, indent=0) + "\n")
    identity["episodes"] = len(records)
    ident_path.write_text(json.dumps(identity, indent=1, default=str) + "\n")
    print(f"[encode] DONE: {len(records)} episodes -> {out} (val {sum(r['split'] == 'val' for r in records)})", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
