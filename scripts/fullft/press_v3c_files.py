"""Plan v14 E14 step 1b (11-19 10:00 BJ, Opus): the files of the writer press_writer_scan.py chose when it is the
provisional write ("先暂记、后确认", E14_WRITER_VERDICT.json kind P), now that the detector supports it
(fullft.events.EventRule.provisional, commit after 6b546c3; online.py shows undecided provisional entries).
Reads outputs/fullft/E14_WRITER_VERDICT.json; for kind P writes
  outputs/fullft/PRESS_V3C_RULE.json                 {"delta", "min_path", "provisional"} (history.event_rule_from)
  outputs/fullft/events/events_press_button_v3c.json the 50 demos' events under that rule (fullft.events.detect)
checks that every event's visible frame equals the scan's provisional() timing and that the events are press_fast's
(same frame / arm / kind), then (--relay) puts both on the relay diag/press_v3c for the old H200 (v3c_ready.sh).
Kind T: the scan wrote the files itself; nothing to do. NO TIMELY WRITER: nothing to do. CPU only.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_v3c_files.py --relay
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from fastwam.fullft.events import EventRule, detect  # noqa: E402

R = Path("/workspace/FastWAM-memory2")
F = R / "outputs/fullft"
TASK = "press_button"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relay", action="store_true")
    args = ap.parse_args()
    v = json.loads((F / "E14_WRITER_VERDICT.json").read_text())
    if v.get("verdict") != "CHOSEN" or v.get("kind") != "P":
        print(f"[v3c] writer verdict {v.get('verdict')} kind {v.get('kind')}: nothing to do here")
        return 0
    spec = importlib.util.spec_from_file_location("scan", REPO / "scripts/fullft/press_writer_scan.py")
    scan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan)
    es = scan.load("fullft/events_stats")
    std_rule = EventRule(delta=float(v["delta"]), min_path=float(v["min_path"]))
    rule = EventRule(delta=float(v["delta"]), min_path=float(v["min_path"]), provisional=float(v["eps"]))
    events, bad, n = {}, 0, 0
    for path in es.demo_files(TASK):
        grip, pos = es.read_demo(path)
        std = detect(grip, pos, std_rule)
        new = detect(grip, pos, rule)
        ref = scan.provisional(std, pos, float(v["eps"]))
        n += len(new)
        if [(e["frame"], e["arm"], e["kind"]) for e in new] != [(e["frame"], e["arm"], e["kind"]) for e in std] \
                or [e["confirmed"] for e in new] != [e["confirmed"] for e in ref]:
            bad += 1
        events[f"{TASK}/{path.stem}"] = new
    lat = [e["confirmed"] - e["frame"] for ev in events.values() for e in ev]
    print(f"[v3c] {len(events)} demos, {n} events; demos where the detector differs from the scan's timing: {bad}; "
          f"latency (visible - frame) median {float(np.median(lat)):.1f}, max {max(lat)}")
    if len(events) < 45 or bad:
        print("[v3c] FAILED: the provisional detector does not reproduce the scan; no files written")
        return 1
    rule_json = F / "PRESS_V3C_RULE.json"
    rule_json.write_text(json.dumps({"delta": rule.delta, "min_path": rule.min_path, "provisional": rule.provisional,
                                     "why": f"plan v14 E14 writer scan: {v['candidate']}"}) + "\n")
    (F / "events").mkdir(parents=True, exist_ok=True)
    ev = F / "events/events_press_button_v3c.json"
    ev.write_text(json.dumps({"rule": str(rule), "episodes": events}) + "\n")
    print(f"[v3c] -> {rule_json}, {ev}")
    if args.relay:
        hf = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else sys.executable
        rc = subprocess.run([hf, str(REPO / "scripts/memory_v2/migrate/relay.py"), "put", str(rule_json), str(ev),
                             "--prefix", "diag/press_v3c"]).returncode
        print(f"[v3c] relay put exit code {rc}")
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
