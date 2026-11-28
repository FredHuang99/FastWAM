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
  --window wait (11-24): anchors evenly in [8, m - 25], before the arm moves (the action is "stay still"; only frame 0
          says which candidate is the target).
  Models with the next-pose head (obs_pose, 11-23 part (2b)): per window also the head's squared error (true history /
  frame 0 swapped) next to the error of predicting "no further motion" (descriptive, the registered obs_pose reading:
  is the target position known before the reach, and does it come from frame 0?).
Reading: in the choice window, (swap - true) / true < 2 % -> "frame 0 is not used at the choice"; >= 2 % -> it is used.
  --swap matchref (11-26, plan v20 card 7 described: "obs_probe with the match frame swapped for another demo's
          (>= 2 % at the onset = the cue is read)"): for a zoom / match model, the REFERENCE zoom slot (the match
          frame of obs_match; the first hist_ids == -1 slot, data.py) gets ANOTHER demo's, frame 0 untouched.
          The samples are built with the run's data.zoom_root / data.text_table, as in training. Default
          --swap frame0: exactly as before.
  --task swap_T --window carry (11-27, plan v21 diagnostic 5(c)): swap_T demos; anchors evenly in [g + 16, r - 1],
          g = the first gripper close (both arms grasp together), r = the first gripper opening after it (the first
          put-down): while both blocks are carried, where to put them is shown only by frame 0. The contrast window
          'late' is then [r2 + 8, end], r2 = the second opening (both blocks down). Default --task observe_and_pickup:
          exactly as before.
  --roots (11-28, plan v21 card 25 described: "the frame-0 swap at the onset on held-out generated demos"): the
          demos come from these dense caches instead of the run's data.roots (default: unchanged).
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


def openings_after(proprio: torch.Tensor, g: int):
    """11-27: frames after g where a gripper that was closed opens again (> 0.65), in time order (either arm)."""
    gr = proprio[:, [6, 13]].float()
    closed = [float(gr[g, a]) < 0.35 for a in (0, 1)]
    out = []
    for t in range(g + 1, gr.shape[0]):
        for a in (0, 1):
            v = float(gr[t, a])
            if v < 0.35:
                closed[a] = True
            elif closed[a] and v > 0.65:
                out.append(t)
                closed[a] = False
    return out


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
    ap.add_argument("--window", choices=("choice", "onset", "wait", "carry"), default="choice")
    ap.add_argument("--task", default="observe_and_pickup", help="11-27: swap_T with --window carry (diagnostic 5(c))")
    ap.add_argument("--split", choices=("all", "train", "val"), default="all",
                    help="11-24: demos of one split only (the dense records' split; the model trained on 'train')")
    ap.add_argument("--swap", choices=("frame0", "matchref"), default="frame0")
    ap.add_argument("--out", default="")
    ap.add_argument("--roots", default="", help="11-28 (plan v21 card 25 described): comma-separated dense caches that replace the run's data.roots, e.g. the held-out generated probe groups (dense_observe_and_pickup_cf10probe_v1); default: the run's own roots, exactly as before")
    args = ap.parse_args()
    from fastwam.fullft.data import DenseEpisodes, Samples, collate, load_events, video_polarity
    from fastwam.fullft.online import load_export
    from fastwam.fullft.train import fixed_noise, to_device
    device = "cuda"
    model, cfg, _ = load_export(args.export, device)
    if args.roots:                               # 11-28: probe on other demos (held-out generated groups)
        cfg.data.roots = [x for x in args.roots.split(",") if x]
    episodes = DenseEpisodes(cfg.data.roots, cfg.data.tasks, capacity=cfg.data.episode_cache)
    if (args.window == "carry") != (args.task == "swap_T"):
        raise SystemExit("--window carry goes with --task swap_T (and swap_T only with carry)")
    recs = [r for r in episodes.records if r["task"] == args.task
            and (args.split == "all" or r.get("split") == args.split)]
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
        if args.window == "carry":                # 11-27 plan v21 diagnostic 5(c)
            ops = openings_after(e["proprio"], g)
            if len(ops) < 1 or ops[0] - 1 < g + 16:
                continue
            for a in evenly(g + 16, ops[0] - 1, args.choice):
                items.append((r["episode_id"], a)); window[len(items) - 1] = "carry"
            if len(ops) >= 2:
                for a in evenly(min(ops[1] + 8, n - 1), n - 1, args.late):
                    items.append((r["episode_id"], a)); window[len(items) - 1] = "late"
            continue
        if args.window in ("onset", "wait"):
            m = motion_onset(e["proprio"], g)
            if m is None:
                continue
            ms.append(m)
            lo, hi = (max(1, m - 24), min(g - 1, m + 8)) if args.window == "onset" else (8, m - 25)
        else:
            lo, hi = max(1, g - 48), g - 1
        for a in evenly(lo, hi, args.choice):
            items.append((r["episode_id"], a)); window[len(items) - 1] = args.window
        for a in evenly(min(g + 16, n - 1), n - 1, args.late):
            items.append((r["episode_id"], a)); window[len(items) - 1] = "late"
    print(f"[probe] {cfg.name} split {args.split}; {len(gs)} demos with a grasp; first close at frame median "
          f"{statistics.median(gs)} (min {min(gs)}, max {max(gs)}) of length median {statistics.median(lens)}; "
          f"a 48-frame choice window = {100 * 48 * len(gs) / sum(lens):.1f} % of the training anchors")
    if ms:
        print(f"[probe] motion onset (5 % of the way to the grasp pose) at frame median {statistics.median(ms)} "
              f"(min {min(ms)}, max {max(ms)}); window " + ("[m - 24, m + 8]" if args.window == "onset" else "[8, m - 25]"))
    events = load_events(cfg.data.events) if cfg.data.events else {}      # the body-record model needs its record
    pose = getattr(model, "next_pose_head", None) is not None
    zoom_kw = {}
    if getattr(cfg.rule, "zoom", False):        # 11-26: zoom / match models need their zoom cache (as in training)
        zoom_kw = {"zoom_root": getattr(cfg.data, "zoom_root", "") or "", "text_table": getattr(cfg.data, "text_table", "") or ""}
    elif args.swap == "matchref":
        raise SystemExit("--swap matchref needs a zoom / match model")
    samples = Samples(episodes, items, cfg.rule, events, video_polarity(episodes), augment=False, seed=cfg.seed,
                      next_pose=cfg.next_pose if pose else None, **zoom_kw)
    length = {r["episode_id"]: int(r["length"]) for r in recs}
    pose_err = defaultdict(lambda: defaultdict(list))
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
                if args.swap == "matchref":            # the reference zoom slot only (the first -1 slot)
                    if d not in frame0:
                        frame0[d] = samples.zoom_of(d, length[d])["ref"]
                    hit = (batch["hist_ids"][j] == -1).nonzero(as_tuple=False).flatten()[:1]
                else:
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
                    aux_t, aux_s = ({}, {}) if pose else (None, None)
                    _, at = model.loss(batch, noise, model.history(batch), aux=aux_t)
                    _, asw = model.loss(swapped, noise, model.history(swapped), aux=aux_s)
                    _, an = model.loss(batch, noise, None)
                for j, i in enumerate(idx):
                    for cond, v in (("true", at), ("swap", asw), ("none", an)):
                        loss[i][cond].append(float(v[j].float()))
                    if pose and float(aux_t["next_pose_valid"][j]) > 0:
                        pose_err[i]["true"].append(float(aux_t["next_pose"][j]))
                        pose_err[i]["swap"].append(float(aux_s["next_pose"][j]))
                        pose_err[i]["zero"].append(float(aux_t["next_pose_zero"][j]))
            if start % 40 == 0:
                print(f"  {start}/{len(samples)}", flush=True)
    what = "match frame" if args.swap == "matchref" else "frame-0"
    report = {"export": args.export, "run": cfg.name, "rule": str(cfg.rule), "swap": args.swap, "windows": {}}
    for w in (args.window, "late"):
        sel = [i for i in loss if window[i] == w]
        m = {c: statistics.mean(statistics.mean(loss[i][c]) for i in sel) for c in ("true", "swap", "none")}
        up = sum(statistics.mean(loss[i]["swap"]) > statistics.mean(loss[i]["true"]) for i in sel)
        rel_swap, rel_none = m["swap"] / m["true"] - 1, m["none"] / m["true"] - 1
        report["windows"][w] = {"anchors": len(sel), **{f"action_{c}": v for c, v in m.items()},
                                "swap_vs_true": rel_swap, "none_vs_true": rel_none, "swap_higher_at": up}
        print(f"{w:6s}: {len(sel)} anchors; action loss true {m['true']:.5f}, {what} swapped {m['swap']:.5f} "
              f"({100 * rel_swap:+.1f} %, higher at {up}/{len(sel)}), no history {m['none']:.5f} ({100 * rel_none:+.1f} %)")
        psel = [i for i in sel if pose_err[i]["true"]]
        if psel:
            pm = {c: statistics.mean(statistics.mean(pose_err[i][c]) for i in psel) for c in ("true", "swap", "zero")}
            report["windows"][w]["next_pose"] = {"anchors": len(psel), **pm}
            print(f"{w:6s}  next-pose head on {len(psel)} anchors: squared error {pm['true']:.4f}, frame-0 swapped "
                  f"{pm['swap']:.4f}, predicting no motion {pm['zero']:.4f}")
    c = report["windows"][args.window]["swap_vs_true"]
    where = {"choice": "at the choice", "onset": "at the motion onset", "wait": "before the arm moves",
             "carry": "while both blocks are carried"}[args.window]
    cue = "the match frame" if args.swap == "matchref" else "frame 0"
    verdict = f"{cue} is NOT used {where} (< 2 %)" if c < 0.02 else f"{cue} IS used {where} (>= 2 %)"
    report["reading"] = verdict
    print(f"OBS PROBE {cfg.name}: {verdict}")
    tail = ("" if args.window == "choice" else f"_{args.window}") + ("" if args.split == "all" else f"_{args.split}")
    tail += "" if args.task == "observe_and_pickup" else f"_{args.task}"
    tail += "" if args.swap == "frame0" else f"_{args.swap}"
    out = Path(args.out or f"/workspace/FastWAM-memory2/outputs/fullft/align/OBS_PROBE_{cfg.name}{tail}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
