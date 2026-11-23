"""Find-same label and frame check (11-23 15:40, Opus; user 14:53: find the root cause and fix it). CPU only, read-only.
Runs in mwam5090 (the observe_and_pickup dense cache, its events file, the closed-loop frames of diag_1123_5090.sh step 2
and the delivery's raw demo frames are there).

  labels  per demo, from the dense cache's proprio and the events file:
          g = first gripper close from the proprio (obs_probe.first_close) vs the first 'close' event of the file;
          m = arm motion onset (obs_probe.motion_onset: 5 % of the way to the pose at g); also the 20 % / 50 % frames;
          the next-pose label (data.next_pose_target, kinds close): share of training anchors that have a close ahead,
          and the mean square of the label (= the loss of predicting "no further motion") before m, in [m, g);
          the grasp poses (the closing arm's joints at the first close): pairwise and nearest-neighbour distances and
          how many groups they form (single linkage at 25 % of the median pairwise distance) - the label only helps
          if the grasp pose tells the five candidates apart;
          the share of training anchors a 48-frame pre-close window would weight (model.decision_pre_window=48).
  frames  F0CHECK's wall heuristic gave 30 % in the closed loop's first frame and 0 % in its last, the reverse of the
          expectation, so the heuristic is not trusted. Instead the reference box (x 0.395-0.675, y 0.06-0.34) is
          compared directly: mean colour and mean |difference to frame 0| per frame, in the closed loop (scene 1) and
          in 4 training demos (raw frames through the delivery's data_path.Raw, unmodified). In the training demos
          frame 0 shows the reference (the frame sheet of 11-22); the closed loop's frame 0 should look like them.
  PYTHONPATH=src CUDA_VISIBLE_DEVICES= /opt/mwam/bin/python scripts/fullft/findsame_labels.py
Output lines start with "[labels]" / "[frames]"; JSON -> outputs/fullft/align/FINDSAME_LABELS.json
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

import numpy as np
import torch

from obs_probe import ARM_JOINTS, first_close, motion_onset

R = Path("/workspace/FastWAM-memory2")
ROOT = R / "outputs/memory_v2/press/dense_observe_and_pickup_v1"
EVENTS = R / "outputs/fullft/events/events_observe_and_pickup.json"
FRAMES = R / "outputs/memory_v2/closed_loop/f0check"
BOX = (0.395, 0.06, 0.675, 0.34)


def stats(xs):
    xs = list(xs)
    return f"median {statistics.median(xs):.3g} (min {min(xs):.3g}, max {max(xs):.3g}, n {len(xs)})" if xs else "none"


def first_frame_at(p: torch.Tensor, g: int, frac: float) -> int:
    total = float((p[g] - p[0]).norm())
    for t in range(g + 1):
        if float((p[t] - p[0]).norm()) >= frac * total:
            return t
    return g


def labels(args, report):
    from fastwam.fullft.data import (DenseEpisodes, decision_weight, load_events, match_events, next_pose_target,
                                     train_items)
    eps = DenseEpisodes([args.root], ["observe_and_pickup"])
    ids = [r["episode_id"] for r in eps.records]
    events = match_events(ids, load_events([args.events]))
    gs, cs, diff, arms, ms, m20, m50, poses, rows = [], [], [], [], [], [], [], [], []
    for r in eps.records:
        eid = r["episode_id"]
        p = eps(eid)["proprio"].float()
        g = first_close(p)
        closes = sorted((e for e in events.get(eid, []) if e["kind"] == "close"), key=lambda e: (e["frame"], e["arm"]))
        if g is None or not closes:
            rows.append({"episode": eid, "g": g, "close_events": len(closes)})
            continue
        c = closes[0]
        q = p[:, ARM_JOINTS]
        m = motion_onset(p, g)
        gs.append(g); cs.append(int(c["frame"])); diff.append(int(c["frame"]) - g); arms.append(int(c["arm"]))
        ms.append(m); m20.append(first_frame_at(q, g, 0.2)); m50.append(first_frame_at(q, g, 0.5))
        arm = list(range(0, 6)) if int(c["arm"]) == 0 else list(range(7, 13))
        poses.append(p[int(c["frame"]), arm])
        rows.append({"episode": eid, "g": g, "close_event": int(c["frame"]), "arm": int(c["arm"]), "onset": m,
                     "length": int(r["length"])})
    print(f"[labels] {len(eps.records)} demos, {len(gs)} with a close; first close from proprio g {stats(gs)}; "
          f"first close event {stats(cs)}; event - g {stats(diff)}; |event - g| > 2 in {sum(abs(d) > 2 for d in diff)}")
    print(f"[labels] closing arm: arm 0 {arms.count(0)}, arm 1 {arms.count(1)}")
    print(f"[labels] arm motion: 5 % of the way to the grasp pose at frame {stats(ms)}; 20 % {stats(m20)}; "
          f"50 % {stats(m50)}")
    items = train_items(eps)
    onset = {row["episode"]: row.get("onset") for row in rows}
    gof = {row["episode"]: row.get("close_event") for row in rows}
    ok, before, during, after = 0, [], [], []
    pre = 0
    for eid, a in items:
        p = eps(eid)["proprio"]
        t, valid = next_pose_target(events.get(eid, []), a, p, ("close",))
        ms_ = float(t.float().square().mean())
        if valid:
            ok += 1
            m, c = onset.get(eid), gof.get(eid)
            if m is not None and a < m:
                before.append(ms_)
            elif c is not None and a < c:
                during.append(ms_)
            else:
                after.append(ms_)
        if decision_weight(events.get(eid, []), a, 3.0, 0, ("open", "bottom"), 48, ("close",)) != 1.0:
            pre += 1
    zero = {"before_onset": float(np.mean(before)) if before else None,
            "onset_to_close": float(np.mean(during)) if during else None,
            "later_close": float(np.mean(after)) if after else None}
    print(f"[labels] training anchors {len(items)}: a close ahead (next-pose label valid) at {100 * ok / len(items):.1f} %; "
          f"label mean square (= loss of predicting no motion): before the onset {zero['before_onset']}, "
          f"onset to close {zero['onset_to_close']}, before a later close {zero['later_close']}")
    print(f"[labels] a 48-frame pre-close window weights {100 * pre / len(items):.1f} % of the training anchors")
    P = torch.stack(poses)
    d = torch.cdist(P, P)
    off = d[~torch.eye(len(P), dtype=torch.bool)]
    nn_ = (d + torch.eye(len(P)) * 1e9).min(1).values
    thr = 0.25 * float(off.median())
    parent = list(range(len(P)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            if float(d[i, j]) < thr:
                parent[root(i)] = root(j)
    groups = {}
    for i in range(len(P)):
        groups.setdefault(root(i), []).append(i)
    sizes = sorted((len(v) for v in groups.values()), reverse=True)
    print(f"[labels] grasp poses (closing arm's 6 joints, normalised): pairwise distance {stats(off.tolist())}; "
          f"nearest other demo {stats(nn_.tolist())}; groups at {thr:.3g}: {len(groups)} (sizes {sizes[:12]})")
    report["labels"] = {"g": gs, "close_event": cs, "arm": arms, "onset": ms, "onset20": m20, "onset50": m50,
                        "valid_share": ok / len(items), "label_mean_square": zero, "pre48_share": pre / len(items),
                        "pose_pairwise_median": float(off.median()), "pose_nn_median": float(nn_.median()),
                        "pose_groups": sizes, "rows": rows}


def box_of(img: np.ndarray) -> np.ndarray:
    from PIL import Image
    h, w = img.shape[:2]
    crop = img[int(BOX[1] * h):int(BOX[3] * h), int(BOX[0] * w):int(BOX[2] * w)]
    return np.asarray(Image.fromarray(crop).resize((64, 48))).astype(np.float32)


def describe(name, imgs, report):
    """imgs: [(label, HxWx3 uint8)]; frame 0 first."""
    b0 = box_of(imgs[0][1])
    out = []
    for lab, im in imgs:
        b = box_of(im)
        col = b.reshape(-1, 3).mean(0)
        out.append({"frame": lab, "box_rgb": [round(float(x), 1) for x in col],
                    "box_diff_to_frame0": round(float(np.abs(b - b0).mean()), 2)})
    print(f"[frames] {name}: " + "; ".join(f"{o['frame']} rgb {o['box_rgb']} diff {o['box_diff_to_frame0']}"
                                         for o in out))
    report.setdefault("frames", {})[name] = out
    return b0


def frames(args, report):
    from PIL import Image
    heads = sorted(Path(args.frames).rglob("head_*.png"))
    if not heads:
        print(f"[frames] no closed-loop head frames under {args.frames}")
    else:
        pick = [k for k in (0, 1, 2, 3, 5, 10, 20) if k < len(heads)] + [len(heads) - 1]
        imgs = [(heads[k].stem, np.asarray(Image.open(heads[k]).convert("RGB"))) for k in sorted(set(pick))]
        cl0 = describe("closed loop scene 1", imgs, report)
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from zoom_tools import delivery
    common, data_path = delivery()
    cfg = common.read(Path(args.root) / "IDENTITY.json")["config"]
    recs = common.read(Path(args.root) / "RECORDS.json")[:4]
    train0 = []
    for rec in recs:
        raw = data_path.Raw(cfg, rec)
        try:
            n = int(rec["length"])
            imgs = [(f"f{f}", np.asarray(raw.images(f)[0]).astype(np.uint8)) for f in (0, 1, 2, 5, n // 3, n - 1)]
        finally:
            raw.close()
        train0.append(describe(rec["episode_id"], imgs, report))
        last = box_of(imgs[-1][1])
        if heads:
            report.setdefault("closed_vs_train", []).append(
                {"episode": rec["episode_id"], "cl0_vs_train0": round(float(np.abs(cl0 - train0[-1]).mean()), 2),
                 "cl0_vs_train_last": round(float(np.abs(cl0 - last).mean()), 2)})
    if heads:
        for row in report["closed_vs_train"]:
            print(f"[frames] closed-loop frame 0 box vs {row['episode']}: frame 0 {row['cl0_vs_train0']}, "
                  f"last frame {row['cl0_vs_train_last']} (smaller = more alike)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--events", default=str(EVENTS))
    ap.add_argument("--frames", default=str(FRAMES))
    ap.add_argument("--out", default=str(R / "outputs/fullft/align/FINDSAME_LABELS.json"))
    args = ap.parse_args()
    report = {}
    labels(args, report)
    try:
        frames(args, report)
    except Exception as error:                                # noqa: BLE001 (the label part is still reported)
        print(f"[frames] FAILED: {type(error).__name__}: {error}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
