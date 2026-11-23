"""The timely writer's event file for another task (11-23 15:00, Opus; user 14:53 approved the rearrange body record with
the timely writer on the H100). The writer is D2's / press_v3c's: delta 0.012 m, min_path 0.015 m, provisional 0.002 m
(fullft.events.EventRule; an event becomes visible as soon as the height has come back 0.2 cm from the turning point,
and the record shows it with lag 0). Runs on the machine with the RMBench demos (the 5090; events_stats.ROOTS), CPU.
Writes outputs/fullft/events/events_<task>_v3c.json {"rule", "episodes"} (episode keys <task>/<hdf5 stem>, as every
events file) and prints, against rule A (delta 0.015, min_path 0.03) on the same demos: events per demo and the write
latency (visible frame - event frame; rule A + the old lag 4). With --relay: puts the file on the relay as
diag/<task>_v3c for the H100 (rearr_v3c_ready.sh).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/task_v3c_events.py --task rearrange_blocks --relay
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from fastwam.fullft.events import EventRule, detect  # noqa: E402

F = Path("/workspace/FastWAM-memory2/outputs/fullft")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--relay", action="store_true")
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location("events_stats", REPO / "scripts/fullft/events_stats.py")
    es = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(es)
    rule = EventRule(delta=0.012, min_path=0.015, provisional=0.002)
    old = EventRule()
    events, n_new, n_old, lat_new, lat_old = {}, [], [], [], []
    for path in es.demo_files(args.task):
        grip, pos = es.read_demo(path)
        new = detect(grip, pos, rule)
        a = detect(grip, pos, old)
        events[f"{args.task}/{path.stem}"] = new
        n_new.append(len(new))
        n_old.append(len(a))
        lat_new += [e["confirmed"] - e["frame"] for e in new]
        lat_old += [e["confirmed"] - e["frame"] + 4 for e in a]
    if len(events) < 45:
        print(f"[v3c] {args.task}: only {len(events)} demos found: nothing written")
        return 1
    print(f"[v3c] {args.task}: {len(events)} demos; events per demo timely {min(n_new)}/{statistics.median(n_new)}/"
          f"{max(n_new)} (rule A {min(n_old)}/{statistics.median(n_old)}/{max(n_old)}); write latency in frames: timely "
          f"median {statistics.median(lat_new)}, max {max(lat_new)}; rule A + lag 4 median {statistics.median(lat_old)}, "
          f"max {max(lat_old)}")
    (F / "events").mkdir(parents=True, exist_ok=True)
    out = F / f"events/events_{args.task}_v3c.json"
    out.write_text(json.dumps({"rule": str(rule), "episodes": events}) + "\n")
    print(f"[v3c] -> {out}")
    if args.relay:
        hf = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else sys.executable
        rc = subprocess.run([hf, str(REPO / "scripts/memory_v2/migrate/relay.py"), "put", str(out),
                             "--prefix", f"diag/{args.task}_v3c"]).returncode
        print(f"[v3c] relay put exit code {rc}")
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
