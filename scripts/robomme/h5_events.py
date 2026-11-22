"""RoboMME counting tasks: how many body events does our rule find in each demonstration? (11-22, Opus; plan v19 R0;
user 18:23: the SwingXtimes event goes to Fable, with facts.) Read-only, CPU, numpy + h5py only, so it runs inside
RoboMME's own image. The rule is ours, unchanged: events.py (fastwam.fullft, copied next to this file) with its default
EventRule (gripper command crossing its midpoint with hysteresis; height reversal of >= 1.5 cm, turning point = event;
3 cm of end-effector path between events). Single arm: the Panda is arm 0, arm 1 is a still dummy.
  gripper command = the demo's joint_action[7] (-1 close, +1 open) mapped to [0, 1]   (our RMBench rule also uses the
  command, not the finger width); height = obs/eef_state[2] (world z, table at 0).
Video-demo steps (info/is_video_demo) are skipped, as RoboMME's own replay does.
Per task and per count N parsed from the goal (PickXtimes / SwingXtimes: \"... <word> times\", else 1; BinFill: the sum of
the cube numbers; StopCube: not parsed): episodes, steps, and min / median / max of close, open, bottom, top events and
of subgoal boundaries. Then, per task, how the bottom count grows with N (one line through the medians).
  python h5_events.py --data DIR_WITH_record_dataset_<Task>.h5 [--tasks ...] [--limit 100]
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import h5py
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("events", HERE / "events.py")
events = importlib.util.module_from_spec(spec)
sys.modules["events"] = events          # dataclasses need the module registered
spec.loader.exec_module(events)
WORDS = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}


def count_of(task, goal):
    g = goal.lower()
    if task == "BinFill":
        n = sum(WORDS.get(w, 0) for w in re.findall(r"\b(\w+) (?:red|blue|green) cubes?\b", g))
        return n or None
    if task in ("PickXtimes", "SwingXtimes"):
        m = re.search(r"\b(\w+) times\b", g)
        return WORDS.get(m.group(1)) if m else 1
    return None


def flag(ts, key):
    info = ts.get("info")
    return bool(np.reshape(np.asarray(info[key][()]), -1)[0]) if info is not None and key in info else False


def episode(ep):
    keys = sorted((k for k in ep.keys() if k.startswith("timestep_")), key=lambda k: int(k.split("_")[1]))
    grip, pos, bounds = [], [], 0
    for k in keys:
        ts = ep[k]
        if flag(ts, "is_video_demo"):
            continue
        a = np.asarray(ts["action"]["joint_action"][()], dtype=np.float64).reshape(-1)
        z = np.asarray(ts["obs"]["eef_state"][()], dtype=np.float64).reshape(-1)
        grip.append([(a[7] + 1.0) / 2.0, 1.0])
        pos.append([[z[0], z[1], z[2]], [0.0, 0.0, 0.0]])
        bounds += flag(ts, "is_subgoal_boundary")
    ev = events.detect(np.asarray(grip), np.asarray(pos), events.EventRule()) if grip else []
    c = {kind: sum(1 for e in ev if e["arm"] == 0 and e["kind"] == kind) for kind in ("close", "open", "bottom", "top")}
    return len(grip), c, bounds


def mmm(xs):
    return f"{min(xs)}/{statistics.median(xs):g}/{max(xs)}" if xs else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--tasks", nargs="+", default=["PickXtimes", "SwingXtimes", "BinFill", "StopCube"])
    ap.add_argument("--limit", type=int, default=100)
    args = ap.parse_args()
    for task in args.tasks:
        f = Path(args.data) / f"record_dataset_{task}.h5"
        if not f.exists():
            print(f"{task}: no {f.name}")
            continue
        rows = defaultdict(list)
        with h5py.File(f, "r") as h:
            eps = sorted((k for k in h.keys() if k.startswith("episode_")), key=lambda k: int(k.split("_")[1]))
            for k in eps[:args.limit]:
                goal = h[k]["setup"]["task_goal"][()]
                goal = goal[0] if np.ndim(goal) else goal
                goal = goal.decode() if isinstance(goal, (bytes, np.bytes_)) else str(goal)
                n, c, b = episode(h[k])
                rows[count_of(task, goal)].append((n, c, b, goal))
        total = sum(len(v) for v in rows.values())
        print(f"\n== {task}: {total} episodes; e.g. goal: {next(iter(rows.values()))[0][3]}")
        print(f"  {'N':>4} {'eps':>4} {'steps':>12} {'close':>9} {'open':>9} {'bottom':>10} {'top':>9} {'boundaries':>11}")
        med = []
        for N in sorted(rows, key=lambda x: (x is None, x)):
            r = rows[N]
            col = lambda kind: [x[1][kind] for x in r]                       # noqa: E731
            print(f"  {str(N):>4} {len(r):>4} {mmm([x[0] for x in r]):>12} {mmm(col('close')):>9} {mmm(col('open')):>9} "
                  f"{mmm(col('bottom')):>10} {mmm(col('top')):>9} {mmm([x[2] for x in r]):>11}")
            if isinstance(N, int):
                med.append((N, statistics.median(col("bottom")), statistics.median(col("close"))))
        if len(med) >= 2:
            ns, bs, cs = (np.array(v, dtype=float) for v in zip(*med))
            kb, cb = np.polyfit(ns, bs, 1)
            kc, cc = np.polyfit(ns, cs, 1)
            print(f"  medians vs N: bottom ~ {kb:.2f} N + {cb:.2f};  close ~ {kc:.2f} N + {cc:.2f}")
    print("\nH5 EVENTS done")


if __name__ == "__main__":
    main()
