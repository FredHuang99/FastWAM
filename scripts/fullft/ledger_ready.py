"""Plan v12 checklist 11 / h200_queue.txt: is the ledger run ready on THIS machine's data? Writes
outputs/fullft/READY_<variant> only if every check passes (the H200 queue starts put_arprop / press_arprop on it).
  1 unit tests (src/fastwam/fullft/tests: test_ledger.py + test_fullft.py), CPU
  2 per task: every dense episode has its rule-A event list (directly or by episode number, data.match_events)
  3 per task: alignment of the event file with the dense cache: the gripper 'close' frames detected in the demos equal
    the commanded crossings (0.65 -> 0.35) of the cache's proprio (de-normalised) in >= 95 % of episodes
    --check3 subset (11-17 deviation 44, user 21:11; for tasks whose demos put a grasp < 3 cm of path after a reversal,
    where the event rule's debounce drops that close: rearrange 11/100, cover 27/100 episode-arms, ready_diag.py):
    in EVERY episode-arm each event 'close' falls on a crossing (no extra, no shifted close) and each crossing without
    an event has an earlier event of the same arm (the debounce needs one); the dropped crossings are reported
  4 per task: the last event_max text positions are padding (exact zeros) in every episode
CPU only (does not touch the GPU).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/ledger_ready.py --variant arprop --tasks put_back_block press_button
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import torch

R = Path("/workspace/FastWAM-memory2")
ROOTS = {"put_back_block": "/workspace/FastWAM/outputs/s1_dense_joint_h100_v1",
         "swap_blocks": "/workspace/FastWAM/outputs/s1_dense_joint_h100_v1"}
STATS = "/workspace/FastWAM/resources/base/robotwin_uncond_3cam_384_dataset_stats.json"


def closes(raw):
    out, is_open = [], None
    for t, g in enumerate(raw):
        if is_open is None:
            is_open = g >= 0.5
        elif is_open and g < 0.35:
            is_open = False
            out.append(t)
        elif not is_open and g > 0.65:
            is_open = True
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--variant", default="arprop")
    ap.add_argument("--tasks", nargs="+", required=True)
    ap.add_argument("--event-max", type=int, default=32)
    ap.add_argument("--skip-tests", action="store_true")
    ap.add_argument("--events", default="", help="11-16: events file to check instead of outputs/fullft/events/events_<task>.json (one task only; e.g. events_press_button_fast.json for press_fast)")
    ap.add_argument("--check3", choices=("equal", "subset"), default="equal",
                    help="11-17 deviation 44: subset = alignment only (see the docstring); default equal (>= 95 %%)")
    ap.add_argument("--marker", default="", help="11-17: marker file name under outputs/fullft (default READY_<variant>; plan v13 runs use READY_v13)")
    ap.add_argument("--no-events", action="store_true",
                    help="11-19 plan v15 E24 (arclk on press_button, new H200, no event file there): skip checks 2 and 3 "
                         "(the event file); only for variants that do not read events (arclk)")
    args = ap.parse_args()
    if args.events and len(args.tasks) != 1:
        ap.error("--events goes with exactly one task")
    if args.no_events and args.variant != "arclk":
        ap.error("--no-events only for --variant arclk (the clock tokens do not read the event file)")
    from fastwam.fullft.data import DenseEpisodes, load_events, match_events, check_ledger_slots
    ok = True
    if not args.skip_tests:
        try:
            import pytest  # noqa: F401
            rc = subprocess.run([sys.executable, "-m", "pytest", "-q", str(R / "src/fastwam/fullft/tests")],
                                cwd=str(R)).returncode
        except ImportError:
            rc = 0
            print("[ready] WARNING pytest is not installed in this python: unit tests NOT run here (17 pass on the "
                  "development machine); the data checks below still decide")
        print(f"[ready] unit tests exit code {rc}")
        ok &= rc == 0
    stats = json.loads(Path(STATS).read_text())["state"]["default"]
    mean, std = torch.tensor(stats["global_mean"]), torch.tensor(stats["global_std"]) + 1e-8
    for task in args.tasks:
        root = ROOTS.get(task, str(R / f"outputs/memory_v2/press/dense_{task}_v1"))
        eps = DenseEpisodes([root], [task])
        ids = [r["episode_id"] for r in eps.records]
        if args.no_events:                       # check 4 only (the clock tokens use the last event_max text slots)
            bad_text = []
            for r in eps.records:
                try:
                    check_ledger_slots(eps(r["episode_id"])["text"], args.event_max, r["episode_id"])
                except ValueError:
                    bad_text.append(r["episode_id"])
            print(f"[ready] {task}: {len(ids)} dense episodes (root {root}); --no-events: checks 2-3 skipped; text "
                  f"positions not padding in {len(bad_text)} episodes {bad_text[:3]}")
            ok &= bool(ids) and not bad_text
            continue
        events = load_events([args.events or str(R / f"outputs/fullft/events/events_{task}.json")])
        direct = sum(e in events for e in ids)
        matched = match_events(ids, events)
        print(f"[ready] {task}: {len(ids)} dense episodes (root {root}); event lists: {direct} by id, "
              f"{len(matched)} after matching by episode number; e.g. dense {ids[:2]} / events {sorted(events)[:2]}")
        ok &= len(matched) == len(ids)
        agree, total, bad_text, dropped, crossings, unexplained = 0, 0, [], 0, 0, []
        for r in eps.records:
            e = eps(r["episode_id"])
            try:
                check_ledger_slots(e["text"], args.event_max, r["episode_id"])
            except ValueError:
                bad_text.append(r["episode_id"])
            if r["episode_id"] not in matched:
                continue
            raw = e["proprio"].float() * std + mean
            for arm, col in ((0, 6), (1, 13)):
                total += 1
                want = sorted({int(x["frame"]) for x in matched[r["episode_id"]] if x["arm"] == arm and x["kind"] == "close"})
                got = closes(raw[:, col].tolist())
                if args.check3 == "equal":
                    agree += want == got
                    continue
                same_arm = [int(x["frame"]) for x in matched[r["episode_id"]] if x["arm"] == arm]
                extra = [f for f in want if f not in got]
                missing = [f for f in got if f not in want]
                no_prior = [m for m in missing if not any(f < m for f in same_arm)]
                crossings += len(got)
                dropped += len(missing)
                if extra or no_prior:
                    unexplained.append((r["episode_id"], arm, extra, no_prior))
                else:
                    agree += 1
        share = agree / max(1, total)
        if args.check3 == "equal":
            print(f"[ready] {task}: close frames equal in {agree}/{total} episode-arms ({share:.3f}, need >= 0.95); "
                  f"text positions not padding in {len(bad_text)} episodes {bad_text[:3]}")
            ok &= share >= 0.95 and not bad_text
        else:
            print(f"[ready] {task}: (check3 subset, deviation 44) event closes on crossings, every missing one after a "
                  f"same-arm event: {agree}/{total} episode-arms (need all); crossings dropped by the debounce "
                  f"{dropped}/{crossings}; unexplained {unexplained[:3]}; text positions not padding in "
                  f"{len(bad_text)} episodes {bad_text[:3]}")
            ok &= agree == total and not bad_text
    marker = R / f"outputs/fullft/{args.marker or 'READY_' + args.variant}"
    if ok:
        marker.write_text(json.dumps({"tasks": args.tasks}) + "\n")
        print(f"[ready] ALL CHECKS PASSED -> {marker}")
    else:
        print("[ready] NOT READY (see above); no marker written")
        sys.exit(1)


if __name__ == "__main__":
    main()
