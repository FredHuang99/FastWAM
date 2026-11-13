"""Plan v12 N8b diagnosis (pre-registered 11-11): is the AR history used by a fullft export? Offline, on the run's own
validation anchors (data.val_anchors_per_task per task, as training's evaluate), the SAME noise and timesteps
(train.fixed_noise) with the history and with no history (model.loss(..., history=None)).
Reading (plan v12, unchanged): relative action-loss gain 1 - L_hist / L_none < 2 % -> "the history is not used"
(N8b = gate learning rate x 10, retrain 30 frame-epochs); otherwise N8b = continue from epoch 30 to 60 (lr 5e-5, cosine).
Also per task, and the video loss, for reference. GPU: one card (~20 GB at --micro 2). Read-only.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/hist_probe.py --export outputs/fullft/exports/ar_2task_e30/export_e30.pt
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import torch


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", required=True)
    ap.add_argument("--micro", type=int, default=2)
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    from fastwam.fullft.data import DenseEpisodes, Samples, collate, load_events, val_items, video_polarity
    from fastwam.fullft.online import load_export
    from fastwam.fullft.train import fixed_noise, to_device
    device = "cuda"
    model, cfg, _ = load_export(args.export, device)
    episodes = DenseEpisodes(cfg.data.roots, cfg.data.tasks, capacity=cfg.data.episode_cache)
    vitems = val_items(episodes, cfg.data.val_anchors_per_task)
    events = load_events(cfg.data.events) if cfg.data.events else {}
    val = Samples(episodes, vitems, cfg.rule, events, video_polarity(episodes), augment=False, seed=cfg.seed)
    task_of = {r["episode_id"]: r["task"] for r in episodes.records}
    rows_out = defaultdict(lambda: {"act_hist": [], "act_none": [], "vid_hist": [], "vid_none": []})
    with torch.no_grad():
        for start in range(0, len(val), args.micro):
            idx = list(range(start, min(len(val), start + args.micro)))
            rows = [val[i] for i in idx]
            batch = to_device(collate(rows), device)
            noises = [fixed_noise(start + j, {"video": tuple(r["video_latent"].shape), "action": tuple(r["actions"].shape)},
                                  model, device) for j, r in enumerate(rows)]
            noise = {k: torch.stack([n[k] for n in noises]).squeeze(1) if k.startswith("t_") else
                     torch.stack([n[k] for n in noises]) for k in noises[0]}
            with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                history = model.history(batch)
                vh, ah = model.loss(batch, noise, history)
                vn, an = model.loss(batch, noise, None)
            for j, i in enumerate(idx):
                t = task_of[vitems[i][0]]
                for key, val_ in (("act_hist", ah), ("act_none", an), ("vid_hist", vh), ("vid_none", vn)):
                    rows_out[t][key].append(float(val_[j].float()))
            if start % 64 == 0:
                print(f"  {start}/{len(val)}", flush=True)
    report = {"export": args.export, "run": cfg.name, "history": str(cfg.rule), "anchors": len(vitems), "tasks": {}}
    pooled_h, pooled_n = [], []
    for t, d in sorted(rows_out.items()):
        lh, ln = statistics.mean(d["act_hist"]), statistics.mean(d["act_none"])
        wins = sum(a < b for a, b in zip(d["act_hist"], d["act_none"]))
        report["tasks"][t] = {"n": len(d["act_hist"]), "action_hist": lh, "action_none": ln, "gain": 1 - lh / ln,
                              "anchors_lower_with_history": wins, "video_hist": statistics.mean(d["vid_hist"]),
                              "video_none": statistics.mean(d["vid_none"])}
        pooled_h += d["act_hist"]
        pooled_n += d["act_none"]
        print(f"{t}: n={len(d['act_hist'])} action loss with history {lh:.5f}, none {ln:.5f}, gain {100 * (1 - lh / ln):+.1f} %; "
              f"lower with history at {wins}/{len(d['act_hist'])} anchors; video {statistics.mean(d['vid_hist']):.4f} / "
              f"{statistics.mean(d['vid_none']):.4f}")
    gain = 1 - statistics.mean(pooled_h) / statistics.mean(pooled_n)
    report["pooled_gain"] = gain
    reading = "the history is NOT used (< 2 %)" if gain < 0.02 else "the history is used (>= 2 %)"
    print(f"HIST PROBE {cfg.name}: pooled action-loss gain {100 * gain:+.1f} % -> {reading}")
    out = Path(args.out or f"/workspace/FastWAM-memory2/outputs/fullft/align/HIST_PROBE_{cfg.name}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
