"""Plan v20 card 8, 11-24 19:30 (Opus; used ONLY with the background gate, after the user agrees): the generated scenes
are not seed-for-seed the official ones (object instances differ), so before their cache is built and uploaded (upload =
a training slot may pick it), compare overall statistics with the official demos. Gate, set before any generated scene
exists:
  (1) frames per episode: generated median within +-10 % of the official median;
  (2) expert success rate (kept seeds / seeds tried): within +-10 points of the official (official: 50 kept, seeds 0..max);
  (3) head camera frame 0 mean brightness: generated median inside the official [min, max].
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/gen_stats.py --gen <dir>/demo_clean/<task>/aloha_agilex \
      --official <dir>/demo_clean/<task>/aloha_agilex
Prints GEN STATS PASS / FAIL; JSON -> <gen>/GEN_STATS.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts/memory_v2/press"))


def side(folder: Path, bd, common, data_path, cfg, task):
    seeds = [int(x) for x in (folder / "seed.txt").read_text().split()]
    gen = folder / "GEN.json"
    start = min(seeds)
    if gen.exists() and json.loads(gen.read_text()).get("start_seed") is not None:
        start = int(json.loads(gen.read_text())["start_seed"])
    tries = max(seeds) - start + 1      # seeds are tried one after another from the start
    frames, bright = [], []
    for f in sorted((folder / "data").glob("episode_*.hdf5")):
        rec = bd.make_record(common, f, task, "train")
        raw = data_path.Raw(cfg, rec)
        try:
            img = np.asarray(raw.images(0)[0])
        finally:
            raw.close()
        frames.append(int(rec["length"]))
        bright.append(float(img.mean()))
    return {"episodes": len(frames), "seeds": len(seeds), "seed_min": min(seeds), "seed_max": max(seeds), "tries": tries,
            "frames": frames, "bright": bright}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True)
    ap.add_argument("--official", required=True)
    ap.add_argument("--task", default="observe_and_pickup")
    args = ap.parse_args()
    import build_dense as bd
    common, data_path = bd.setup()
    cfg = json.loads((Path("/workspace/FastWAM-memory2/outputs/memory_v2/press") / f"dense_{args.task}_v1" / "IDENTITY.json").read_text())["config"]
    g = side(Path(args.gen), bd, common, data_path, cfg, args.task)
    o = side(Path(args.official), bd, common, data_path, cfg, args.task)
    o_rate = o["seeds"] / (o["seed_max"] + 1)          # the official loop starts at seed 0
    g_rate = g["seeds"] / g["tries"]
    mf_o, mf_g = float(np.median(o["frames"])), float(np.median(g["frames"]))
    mb_g = float(np.median(g["bright"]))
    checks = {
        "frames": {"official_median": mf_o, "generated_median": mf_g, "pass": abs(mf_g - mf_o) <= 0.10 * mf_o},
        "success_rate": {"official": round(o_rate, 4), "generated": round(g_rate, 4), "pass": abs(g_rate - o_rate) <= 0.10},
        "head_brightness": {"official_min": round(min(o["bright"]), 2), "official_max": round(max(o["bright"]), 2),
                            "generated_median": round(mb_g, 2), "pass": min(o["bright"]) <= mb_g <= max(o["bright"])},
    }
    ok = all(c["pass"] for c in checks.values())
    for k, v in checks.items():
        print(f"[genstats] {k}: {v}")
    print(f"[genstats] frames official {min(o['frames'])}-{max(o['frames'])} (n {o['episodes']}), generated "
          f"{min(g['frames'])}-{max(g['frames'])} (n {g['episodes']}); head brightness official median "
          f"{np.median(o['bright']):.2f}")
    (Path(args.gen) / "GEN_STATS.json").write_text(json.dumps({"pass": ok, "checks": checks, "official": o, "generated": g},
                                                              indent=1) + "\n")
    print("GEN STATS " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
