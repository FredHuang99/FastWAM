"""RoboMME step 2 (plan v22 6.6; Status 11-28 12.8), 11-28 17:20 Opus. CPU, mwam5090 (the RoboMME dense root is there).
Adds the normalised "proprio" [L, 8] / "actions" [L, 7] keys that fullft.data reads to every episode of the RoboMME
dense root (robomme_encode.py wrote only proprio_raw / actions_raw on purpose: the normalisation is a training choice).
Choices (R0 section 2 and Status 12.8; written before any statistic is computed):
  * actions stay ABSOLUTE end-effector pose + gripper (RoboMME's eef_action, what its own controller executes); the
    LIBERO base was trained on delta poses, so its statistics are not borrowed: ours come from this root's 'train' split.
  * the LIBERO base's normaliser: min/max -> [-1, 1] per dimension (configs/data/libero_2cam.yaml norm_default_mode;
    fastwam.datasets.lerobot.utils.normalizer.SingleFieldLinearNormalizer: a range below 1e-4 maps to the middle; the
    output clamped to [-5, 5]). Proprio and actions separately.
  * frames whose action is not valid (action_valid False) are left out of the statistics and hold the previous valid
    action (the first valid one before any); their number is reported.
  * angle wrap check: the three orientation numbers (roll pitch yaw) of proprio and actions; a step of more than pi
    between consecutive frames of an episode is a wrap. Any wrap -> nothing is written (STOP; the report lists them):
    min/max over wrapped angles would be meaningless, and how to unwrap (also online) is decided after seeing them.
Writes <root>/NORM_STATS.json (stats, counts, wraps, sha256 of the stats) and, unless --stats-only or a STOP, adds the
two keys to each encodings.pt; when every episode is done, <root>/CACHE.json (the dense-cache build marker that
cache_relay.py needs before it uploads a root) (written to a temporary file in the same folder, then renamed over the old one; every
existing key is kept unchanged; an episode that already has both keys from the same stats is skipped).
  PYTHONPATH=src /opt/mwam/bin/python scripts/robomme/robomme_norm.py [--root DIR] [--stats-only]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import torch

ROOT = Path("/workspace/FastWAM-memory2/outputs/robomme/dense_robomme_v1")
ANGLES = {"proprio_raw": (3, 4, 5), "actions_raw": (3, 4, 5)}
RANGE_TOL, OUT_MIN, OUT_MAX, CLAMP = 1e-4, -1.0, 1.0, 5.0


def folder(root: Path, eid: str) -> Path:
    return root / "cache" / eid.replace("/", "_")


def held(actions: torch.Tensor, valid: torch.Tensor) -> torch.Tensor:
    """Invalid frames hold the previous valid action (the first valid one before any)."""
    out = actions.clone()
    idx = valid.nonzero(as_tuple=False).flatten()
    if len(idx) == 0:
        raise ValueError("an episode without any valid action")
    last = int(idx[0])
    for t in range(len(out)):
        if bool(valid[t]):
            last = t
        else:
            out[t] = actions[last]
    return out


def scale_offset(lo: torch.Tensor, hi: torch.Tensor):
    rng = hi - lo
    ignore = rng < RANGE_TOL
    rng = torch.where(ignore, torch.full_like(rng, OUT_MAX - OUT_MIN), rng)
    scale = (OUT_MAX - OUT_MIN) / rng
    offset = OUT_MIN - scale * lo
    offset = torch.where(ignore, (OUT_MAX + OUT_MIN) / 2 - lo, offset)
    return scale, offset


def normalise(x: torch.Tensor, st: dict) -> torch.Tensor:
    return torch.clamp(x * torch.tensor(st["scale"]) + torch.tensor(st["offset"]), -CLAMP, CLAMP).float()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--stats-only", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    records = json.loads((root / "RECORDS.json").read_text())
    train = [r for r in records if r.get("split") == "train"]
    print(f"[norm] {root}: {len(records)} episodes, {len(train)} train", flush=True)
    data = {"proprio_raw": [], "actions_raw": []}
    invalid, wraps = 0, []
    for r in records:
        e = torch.load(folder(root, r["episode_id"]) / "encodings.pt", map_location="cpu", weights_only=True, mmap=True)
        v = e["action_valid"].bool()
        invalid += int((~v).sum())
        for key, cols in ANGLES.items():
            x = held(e[key].float(), v) if key == "actions_raw" else e[key].float()     # invalid frames held first
            d = (x[1:, list(cols)] - x[:-1, list(cols)]).abs()
            hit = (d > math.pi).nonzero(as_tuple=False)
            if len(hit):
                wraps.append({"episode": r["episode_id"], "key": key, "steps": len(hit),
                              "first": [int(hit[0, 0]) + 1, int(cols[int(hit[0, 1])])]})
        if r.get("split") == "train":
            data["proprio_raw"].append(e["proprio_raw"].float())
            data["actions_raw"].append(e["actions_raw"].float()[v])
    stats = {}
    for key, xs in data.items():
        x = torch.cat(xs)
        lo, hi = x.min(0).values, x.max(0).values
        scale, offset = scale_offset(lo, hi)
        stats[key] = {"min": lo.tolist(), "max": hi.tolist(), "mean": x.mean(0).tolist(), "std": x.std(0).tolist(),
                      "q01": torch.quantile(x, 0.01, dim=0).tolist(), "q99": torch.quantile(x, 0.99, dim=0).tolist(),
                      "frames": int(x.shape[0]), "scale": scale.tolist(), "offset": offset.tolist()}
    body = {"mode": "min/max -> [-1, 1] (LIBERO base normaliser), clamp +-5; train split only; actions absolute",
            "stats": {"proprio": stats["proprio_raw"], "actions": stats["actions_raw"]}}
    sha = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    rep = {**body, "sha256": sha, "episodes": len(records), "train_episodes": len(train),
           "invalid_action_frames": invalid, "angle_wraps": wraps[:50], "angle_wrap_episodes": len(wraps)}
    (root / "NORM_STATS.json").write_text(json.dumps(rep, indent=1) + "\n")
    for k in ("proprio", "actions"):
        s = body["stats"][k]
        print(f"[norm] {k}: min {[round(v, 3) for v in s['min']]} max {[round(v, 3) for v in s['max']]}", flush=True)
    print(f"[norm] invalid action frames {invalid}; angle wraps in {len(wraps)} episode-keys; stats sha256 {sha[:16]}",
          flush=True)
    if wraps:
        print(f"[norm] STOP: angle wraps (first: {wraps[:3]}); nothing written to the episodes")
        return 1
    if a.stats_only:
        print("[norm] --stats-only: done")
        return 0
    done = skipped = 0
    for r in records:
        d = folder(root, r["episode_id"])
        marker = d / "NORM.json"
        if marker.exists() and json.loads(marker.read_text()).get("sha256") == sha:
            skipped += 1
            continue
        e = dict(torch.load(d / "encodings.pt", map_location="cpu", weights_only=True))
        e["proprio"] = normalise(e["proprio_raw"].float(), body["stats"]["proprio"])
        e["actions"] = normalise(held(e["actions_raw"].float(), e["action_valid"].bool()), body["stats"]["actions"])
        tmp = d / "encodings.pt.norm_tmp"
        torch.save(e, tmp)
        check = torch.load(tmp, map_location="cpu", weights_only=True, mmap=True)
        if not (torch.equal(check["proprio"], e["proprio"]) and torch.equal(check["latent"], e["latent"])):
            print(f"[norm] STOP: {tmp} does not read back")
            return 1
        os.replace(tmp, d / "encodings.pt")
        marker.write_text(json.dumps({"sha256": sha}) + "\n")
        done += 1
        if done % 20 == 0:
            print(f"[norm] {done} written", flush=True)
    marked = sum((folder(root, r["episode_id"]) / "NORM.json").exists() for r in records)
    if marked == len(records):        # the dense-cache build marker (cache_relay.py refuses a root without it)
        (root / "CACHE.json").write_text(json.dumps({
            "built_by": "scripts/robomme/robomme_encode.py + scripts/robomme/robomme_norm.py", "episodes": len(records),
            "norm_sha256": sha, "keys": "latent video_latent video_valid text text_valid proprio actions (+ raw)"}, indent=1) + "\n")
    print(f"[norm] DONE: {done} written, {skipped} already done, {marked}/{len(records)} marked (stats sha256 {sha[:16]})")
    return 0 if marked == len(records) else 1


if __name__ == "__main__":
    raise SystemExit(main())
