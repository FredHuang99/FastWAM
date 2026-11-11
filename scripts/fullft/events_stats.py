"""Plan v10 node N2 (figure 1): how regular is the tempo of the RMBench expert demos, and can the stage of a task be
read off the clock alone? Also writes the proprioceptive events of every demo (fullft/events.py, the detector the
"event" history uses) as events_<task>.json for training. CPU only; read-only for the demos.

Per task, per demo: events = gripper crossings + end-effector height reversals (events.py). stage(t) = number of
events at frames <= t. Statistics:
  * events per demo; for the k-th event (k = 1, 2, ...): its frame across demos, IQR / median gap to the next event
    ("dispersion": small = the k-th event always happens at about the same time)
  * clock-only stage prediction, leave one demo out: stage_hat(t) = the most common stage of the OTHER demos at the
    same frame t; accuracy on all frames and on decision windows (frames within +-16 of an event of that demo)
Pre-registered reading (plan v10 F.1 N2, amended 11-11 BEFORE any real demo was read): a task is
"clock-identifiable" if clock-only accuracy on ALL frames >= 0.90 AND median dispersion over k <= 0.25. Reason for
the amendment: on synthetic demos with 4 gripper events whose gaps jitter by +-j frames (random walk), the plan's
"decision-window accuracy >= 0.90" passes only j <= 3 (j = 3 / 7 / 15 / 30: window 0.92 / 0.83 / 0.71 / 0.61; all
frames 0.98 / 0.96 / 0.92 / 0.84; dispersion 0.03 / 0.06 / 0.13 / 0.26), i.e. it would call even put_back's measured
<= 15-frame spread "not identifiable". The amended rule passes up to j ~ 15. The plan's strict rule is still
reported ("strict" column). Non-degenerate floor: >= 45 demos parsed and every counted demo has >= 2 events;
a task below the floor gets no verdict. Tally: >= 5 identifiable tasks -> the tempo shortcut is benchmark-wide;
3-4 -> the claim is limited to those tasks; <= 2 -> tempo is one section and P1 rests on the weak-task gains.

  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/events_stats.py [--tasks ...] [--out outputs/fullft/events]
Writes <out>/events_<task>.json, <out>/CLOCK_STATS_<time>.md / .json and <out>/clock_stats_<time>.png.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from fastwam.fullft.events import EventRule, detect, summarize  # noqa: E402

BJ = timezone(timedelta(hours=8))
TASKS = ["put_back_block", "swap_blocks", "press_button", "observe_and_pickup", "rearrange_blocks", "swap_T",
         "battery_try", "blocks_ranking_try", "cover_blocks", "place_block_mat"]
ROOTS = [Path("/workspace/FastWAM/resources/RMBench/data/demo_clean"),
         Path("/workspace/FastWAM-memory2/outputs/memory_v2/press/demo_clean")]
WINDOW = 16


def demo_files(task):
    for root in ROOTS:
        files = sorted((root / task / "aloha_agilex/data").glob("*.hdf5"))
        if files:
            return files
    return []


def read_demo(path):
    """(gripper [n, 2], positions [n, 2, 3]) aligned on the state timeline."""
    import h5py
    from fastwam.memory_s1.data import read_episode
    states, _, _, _, _, _ = read_episode(path)
    with h5py.File(path, "r") as f:
        pairs = (("state/left_ee_poses", "state/right_ee_poses"), ("endpose/left_endpose", "endpose/right_endpose"))
        keys = next((p for p in pairs if all(k in f for k in p)), None)
        if keys is None:
            raise KeyError(f"no end-effector poses in {path.name}; top level {list(f.keys())}")
        left, right = (np.asarray(f[k], dtype=np.float64)[:, :3] for k in keys)
    n = min(len(states), len(left), len(right))
    return np.asarray(states[:n])[:, [6, 13]], np.stack([left[:n], right[:n]], 1)


def stage_curve(events, n):
    s = np.zeros(n, dtype=np.int64)
    for e in events:
        if e["frame"] < n:
            s[e["frame"]:] += 1
    return s


def clock_accuracy(curves, events_by_demo):
    """Leave one demo out: majority stage of the others at the same frame."""
    longest = max(len(c) for c in curves)
    acc_all, acc_win = [], []
    for i, c in enumerate(curves):
        others = [o for j, o in enumerate(curves) if j != i]
        hits_all = hits_win = n_win = 0
        windows = np.zeros(len(c), dtype=bool)
        for e in events_by_demo[i]:
            windows[max(0, e["frame"] - WINDOW):e["frame"] + WINDOW + 1] = True
        for t in range(len(c)):
            votes = Counter(int(o[t]) if t < len(o) else int(o[-1]) for o in others)
            guess = votes.most_common(1)[0][0]
            hit = guess == int(c[t])
            hits_all += hit
            if windows[t]:
                hits_win += hit
                n_win += 1
        acc_all.append(hits_all / len(c))
        if n_win:
            acc_win.append(hits_win / n_win)
    return float(np.mean(acc_all)), float(np.mean(acc_win)) if acc_win else float("nan")


def dispersion(events_by_demo):
    """Per event index k: IQR of its frame across demos / median gap to event k+1."""
    by_k = {}
    for evs in events_by_demo:
        frames = sorted(e["frame"] for e in evs)
        for k, f in enumerate(frames):
            by_k.setdefault(k, []).append((f, frames[k + 1] - f if k + 1 < len(frames) else None))
    rows = []
    for k in sorted(by_k):
        frames = [f for f, _ in by_k[k]]
        gaps = [g for _, g in by_k[k] if g is not None]
        if len(frames) < 10 or not gaps:
            continue
        q1, q3 = np.percentile(frames, [25, 75])
        rows.append({"k": k + 1, "demos": len(frames), "median_frame": float(np.median(frames)),
                     "iqr": float(q3 - q1), "median_gap": float(np.median(gaps)),
                     "dispersion": float((q3 - q1) / max(1.0, np.median(gaps)))})
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=TASKS)
    ap.add_argument("--out", default="/workspace/FastWAM-memory2/outputs/fullft/events")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(BJ).strftime("%Y%m%d_%H%M")
    rule = EventRule()
    lines = [f"# CLOCK_STATS {datetime.now(BJ):%Y-%m-%d %H:%M} (plan v10 N2)", "",
             f"event rule: {rule}; decision window +-{WINDOW} frames", "",
             "| task | demos | events / demo (median, range) | clock-only accuracy all / decision windows | "
             "median dispersion (k = 1..) | verdict | strict (plan text) |", "|---|---|---|---|---|---|---|"]
    report = {"rule": str(rule), "tasks": {}}
    tally = 0
    for task in args.tasks:
        files = demo_files(task)
        if not files:
            lines.append(f"| {task} | 0 | no demos under {[str(r) for r in ROOTS]} |  |  | no verdict |  |")
            continue
        events, curves, errors = {}, [], []
        for f in files:
            try:
                grip, pos = read_demo(f)
            except Exception as e:                                  # noqa: BLE001 (counted against the floor)
                errors.append(f"{f.name}: {type(e).__name__}: {e}")
                continue
            evs = detect(grip, pos, rule)
            events[f"{task}/{f.stem}"] = evs
            curves.append(stage_curve(evs, len(grip)))
        (out / f"events_{task}.json").write_text(json.dumps({"rule": str(rule), "episodes": events}) + "\n")
        counted = [k for k, v in events.items() if len(v) >= 2]
        evs_list = [events[k] for k in events]
        floor = len(counted) >= 45                     # parsed AND >= 2 events (plan: >= 45 / 50 demos)
        acc_all, acc_win = clock_accuracy(curves, evs_list) if len(curves) >= 2 else (float("nan"), float("nan"))
        disp = dispersion(evs_list)
        med_disp = float(np.median([d["dispersion"] for d in disp])) if disp else float("nan")
        identifiable = floor and acc_all >= 0.90 and med_disp <= 0.25
        strict = floor and acc_win >= 0.90 and med_disp <= 0.25
        tally += identifiable
        counts = [len(v) for v in evs_list]
        verdict = ("no verdict (floor: " + f"{len(events)} demos, {len(events) - len(counted)} with < 2 events)") \
            if not floor else ("clock-identifiable" if identifiable else "not clock-identifiable")
        lines.append(f"| {task} | {len(events)} | {statistics.median(counts) if counts else 0} "
                     f"({min(counts) if counts else 0}-{max(counts) if counts else 0}) | {acc_all:.3f} / {acc_win:.3f} | "
                     f"{med_disp:.3f} | {verdict} | {'yes' if strict else 'no'} |")
        report["tasks"][task] = {"demos": len(events), "errors": errors[:5], "events": summarize(events),
                                 "clock_accuracy_all": acc_all, "clock_accuracy_windows": acc_win,
                                 "dispersion": disp, "median_dispersion": med_disp, "floor": floor,
                                 "identifiable": identifiable, "strict": strict, "lengths": [len(c) for c in curves]}
        print(lines[-1], flush=True)
    lines += ["", f"clock-identifiable tasks: {tally} -> " +
              ("the tempo shortcut is benchmark-wide (>= 5)" if tally >= 5 else
               "the claim is limited to these tasks (3-4)" if tally >= 3 else
               "tempo is one section; P1 rests on the weak-task gains (<= 2)"), ""]
    for task, r in report["tasks"].items():
        if r["dispersion"]:
            lines.append(f"- {task}: " + "; ".join(f"k{d['k']} frame {d['median_frame']:.0f} IQR {d['iqr']:.0f} "
                                                   f"gap {d['median_gap']:.0f} ({d['dispersion']:.2f})"
                                                   for d in r["dispersion"][:8]))
        if r["errors"]:
            lines.append(f"  - {task} unreadable demos: {r['errors']}")
    md = out / f"CLOCK_STATS_{stamp}.md"
    md.write_text("\n".join(lines) + "\n")
    (out / f"CLOCK_STATS_{stamp}.json").write_text(json.dumps(report, indent=1) + "\n")
    try:
        figure(report, out / f"clock_stats_{stamp}.png")
    except Exception as e:                                          # noqa: BLE001 (the table is the result)
        print(f"figure skipped: {e}")
    print("\n".join(lines[-(len(report['tasks']) + 3):]))
    print(f"CLOCK_STATS: {md}")


def figure(report, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    tasks = [t for t, r in report["tasks"].items() if r["dispersion"]]
    fig, axes = plt.subplots(1, 2, figsize=(12, 0.5 + 0.45 * len(tasks)), gridspec_kw={"width_ratios": [3, 1]})
    ax, bx = axes
    for i, t in enumerate(tasks):
        for d in report["tasks"][t]["dispersion"][:10]:
            ax.errorbar(d["median_frame"], i, xerr=d["iqr"] / 2, fmt="o", ms=3, color="#3b6ea5", elinewidth=2)
        bx.barh(i, report["tasks"][t]["clock_accuracy_all"], color="#c0504d" if report["tasks"][t]["identifiable"]
                else "#999999")
    ax.set_yticks(range(len(tasks)), tasks)
    ax.set_xlabel("frame of the k-th proprioceptive event (median, bar = IQR across demos)")
    bx.set_yticks(range(len(tasks)), [""] * len(tasks))
    bx.set_xlim(0, 1)
    bx.axvline(0.9, ls="--", color="k", lw=0.8)
    bx.set_xlabel("clock-only stage accuracy\n(all frames, leave one demo out)")
    fig.tight_layout()
    fig.savefig(path, dpi=160)


if __name__ == "__main__":
    main()
