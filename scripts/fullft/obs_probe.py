"""Find-same root cause (11-23 15:00, Opus; user 14:53: why is the history useless on observe_and_pickup?). Does the
trained model use frame 0 (the only frame that shows the reference on the shelf) when it chooses which object to take?
Offline, read-only, one GPU (~20 GB at --micro 2). Descriptive; the 2 % line is the plan v12 N8b rule reused.
Data: the model's own observe_and_pickup demos (all 50, train and val), the same noise draws for every condition.
Anchors per demo, from the demo's own proprio (gripper command = columns 6 / 13; closed below 0.35 after open):
  choice  --choice anchors evenly in [g - 48, g - 1], g = the first gripper close (the reach to the chosen object)
  late    --late anchors evenly in [g + 16, end]  (after the grasp: nothing left to choose)
Conditions (action loss per anchor, mean over --noises fixed draws):
  true    the history as trained (frame 0 = this demo's frame 0)
  swap    frame 0 replaced by ANOTHER demo's frame 0 (other reference, other table) — everything else unchanged
  none    no history frames at all
  --window onset (11-23 15:40): instead of the choice window, anchors evenly in [m - 24, m + 8], m = the arm's motion
          onset (the first frame whose arm joints have moved 5 % of the way from frame 0 to the pose at g). The 32-step
          action chunk of these anchors holds the start of the reach while the recent frames do not show its direction
          yet: if the model picks the object anywhere, it is here ([g - 48, g - 1] is the final approach, where the
          recent frames already show the direction).
Reading: in the choice window, (swap - true) / true < 2 % -> "frame 0 is not used at the choice"; >= 2 % -> it is used.
The same for the late window as a contrast, and (none - true) / true for reference. Also: the share of training anchors
that fall in a 48-frame choice window (how much of the training signal is about the choice).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/obs_probe.py --export outputs/fullft/exports/obs_ar_e30/export_e30.pt
"""
from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import torch


def first_close(proprio: torch.Tensor):
    g = proprio[:, [6, 13]].float()
    opened = [False, False]
    for t in range(g.shape[0]):
        for a in (0, 1):
            v = float(g[t, a])
            if v > 0.65:
                opened[a] = True
            elif opened[a] and v < 0.35:
                return t
    return None


ARM_JOINTS = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]


def motion_onset(proprio: torch.Tensor, g: int, frac: float = 0.05):
    """The first frame whose arm joints have moved `frac` of the way (Euclidean, normalised proprio) from frame 0 to
    the pose at frame g; None if the pose at g equals frame 0's."""
    p = proprio[:, ARM_JOINTS].float()
    total = float((p[g] - p[0]).norm())
    if total == 0.0:
        return None
    for t in range(g + 1):
        if float((p[t] - p[0]).norm()) >= frac * total:
            return t
    return g


def evenly(lo: int, hi: int, n: int):
    if hi < lo:
        return []
    if n <= 1 or hi == lo:
        return [lo]
    return sorted({round(lo + (hi - lo) * i / (n - 1)) for i in range(n)})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", required=True)
    ap.add_argument("--micro", type=int, default=2)
    ap.add_argument("--noises", type=int, default=2)
    ap.add_argument("--choice", type=int, default=6)
    ap.add_argument("--late", type=int, default=3)
    ap.add_argument("--window", choices=("choice", "onset"), default="choice")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    from fastwam.fullft.data import DenseEpisodes, Samples, collate, load_events, video_polarity
    from fastwam.fullft.online import load_export
    from fastwam.fullft.train import fixed_noise, to_device
    device = "cuda"
    model, cfg, _ = load_export(args.export, device)
    episodes = DenseEpisodes(cfg.data.roots, cfg.data.tasks, capacity=cfg.data.episode_cache)
    recs = [r for r in episodes.records if r["task"] == "observe_and_pickup"]
    ids = [r["episode_id"] for r in recs]
    items, window, gs, lens, ms = [], {}, [], [], []
    for r in recs:
        e = episodes(r["episode_id"])
        n = int(r["length"])
        g = first_close(e["proprio"])
        if g is None or g < 8:
            continue
        gs.append(g)
        lens.append(n)
        if args.window == "onset":
            m = motion_onset(e["proprio"], g)
            if m is None:
                continue
            ms.append(m)
            lo, hi = max(1, m - 24), min(g - 1, m + 8)
        else:
            lo, hi = max(1, g - 48), g - 1
        for a in evenly(lo, hi, args.choice):
            items.append((r["episode_id"], a)); window[len(items) - 1] = args.window
        for a in evenly(min(g + 16, n - 1), n - 1, args.late):
            items.append((r["episode_id"], a)); window[len(items) - 1] = "late"
    print(f"[probe] {cfg.name} ({cfg.rule}); {len(gs)} demos with a grasp; first close at frame median "
          f"{statistics.median(gs)} (min {min(gs)}, max {max(gs)}) of length median {statistics.median(lens)}; "
          f"a 48-frame choice window = {100 * 48 * len(gs) / sum(lens):.1f} % of the training anchors")
    if ms:
        print(f"[probe] motion onset (5 % of the way to the grasp pose) at frame median {statistics.median(ms)} "
              f"(min {min(ms)}, max {max(ms)}); window [m - 24, m + 8]")
    events = load_events(cfg.data.events) if cfg.data.events else {}      # the body-record model needs its record
    samples = Samples(episodes, items, cfg.rule, events, video_polarity(episodes), augment=False, seed=cfg.seed)
    donor = {eid: ids[(k + 1) % len(ids)] for k, eid in enumerate(ids)}
    frame0 = {}
    loss = defaultdict(lambda: defaultdict(list))
    with torch.no_grad():
        for start in range(0, len(samples), args.micro):
            idx = list(range(start, min(len(samples), start + args.micro)))
            rows = [samples[i] for i in idx]
            batch = to_device(collate(rows), device)
            if "hist_ids" not in batch:
                raise SystemExit("this export shows no history frames: nothing to probe")
            swapped = dict(batch)
            hl = batch["hist_latent"].clone()
            for j, i in enumerate(idx):
                eid = items[i][0]
                d = donor[eid]
                if d not in frame0:
                    frame0[d] = episodes(d)["latent"][0]
                hit = (batch["hist_ids"][j] == 0).nonzero(as_tuple=False).flatten()
                for h in hit.tolist():
                    hl[j, h] = frame0[d].to(hl)
            swapped["hist_latent"] = hl
            for k in range(args.noises):
                noises = [fixed_noise(1000 * k + i, {"video": tuple(r["video_latent"].shape),
                                                     "action": tuple(r["actions"].shape)}, model, device)
                          for i, r in zip(idx, rows)]
                noise = {key: torch.stack([n[key] for n in noises]).squeeze(1) if key.startswith("t_") else
                         torch.stack([n[key] for n in noises]) for key in noises[0]}
                with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                    _, at = model.loss(batch, noise, model.history(batch))
                    _, asw = model.loss(swapped, noise, model.history(swapped))
                    _, an = model.loss(batch, noise, None)
                for j, i in enumerate(idx):
                    for cond, v in (("true", at), ("swap", asw), ("none", an)):
                        loss[i][cond].append(float(v[j].float()))
            if start % 40 == 0:
                print(f"  {start}/{len(samples)}", flush=True)
    report = {"export": args.export, "run": cfg.name, "rule": str(cfg.rule), "windows": {}}
    for w in (args.window, "late"):
        sel = [i for i in loss if window[i] == w]
        m = {c: statistics.mean(statistics.mean(loss[i][c]) for i in sel) for c in ("true", "swap", "none")}
        up = sum(statistics.mean(loss[i]["swap"]) > statistics.mean(loss[i]["true"]) for i in sel)
        rel_swap, rel_none = m["swap"] / m["true"] - 1, m["none"] / m["true"] - 1
        report["windows"][w] = {"anchors": len(sel), **{f"action_{c}": v for c, v in m.items()},
                                "swap_vs_true": rel_swap, "none_vs_true": rel_none, "swap_higher_at": up}
        print(f"{w:6s}: {len(sel)} anchors; action loss true {m['true']:.5f}, frame-0 swapped {m['swap']:.5f} "
              f"({100 * rel_swap:+.1f} %, higher at {up}/{len(sel)}), no history {m['none']:.5f} ({100 * rel_none:+.1f} %)")
    c = report["windows"][args.window]["swap_vs_true"]
    where = "at the choice" if args.window == "choice" else "at the motion onset"
    verdict = f"frame 0 is NOT used {where} (< 2 %)" if c < 0.02 else f"frame 0 IS used {where} (>= 2 %)"
    report["reading"] = verdict
    print(f"OBS PROBE {cfg.name}: {verdict}")
    tail = "" if args.window == "choice" else "_onset"
    out = Path(args.out or f"/workspace/FastWAM-memory2/outputs/fullft/align/OBS_PROBE_{cfg.name}{tail}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
