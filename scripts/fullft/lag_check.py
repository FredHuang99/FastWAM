"""Plan v12 C.2 / Opus checklist 12: the ledger's write lag k (frames between an event and its entry in the ledger,
the same in training and online; the verifier works inside it). Rule written in v12 before this ran: in the
press_button demos (rule-A event file of N2), the median number of frames from a press "bottom" event to the next
"top" event of the same arm >= 12 -> k = 8, else k = 4. k is fixed afterwards. CPU only, reads the event file.
  /opt/mwam/bin/python scripts/fullft/lag_check.py      (5090: outputs/fullft/events/events_press_button.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

EVENTS = Path("/workspace/FastWAM-memory2/outputs/fullft/events")


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else EVENTS / "events_press_button.json"
    data = json.loads(path.read_text())
    gaps, all_gaps, n_bottom = [], [], 0
    for _name, evs in data["episodes"].items():
        evs = sorted(evs, key=lambda e: e["frame"])
        for i, e in enumerate(evs):
            later = [x for x in evs[i + 1:] if x["arm"] == e["arm"]]
            if later:
                all_gaps.append(later[0]["frame"] - e["frame"])
            if e["kind"] == "bottom":
                n_bottom += 1
                top = next((x for x in later if x["kind"] == "top"), None)
                if top is not None:
                    gaps.append(top["frame"] - e["frame"])
    if not gaps:
        print(f"no bottom -> top pairs in {path}: no reading"); raise SystemExit(1)
    med = float(np.median(gaps))
    k = 8 if med >= 12 else 4
    print(f"{path.name}: {len(data['episodes'])} demos, {n_bottom} press bottoms, {len(gaps)} bottom -> next top gaps: "
          f"median {med:.1f} frames, 10th percentile {np.percentile(gaps, 10):.1f}, min {min(gaps)}; "
          f"any event -> next event of the same arm: median {np.median(all_gaps):.1f}")
    print(f"WRITE LAG k = {k} (rule: median bottom -> top >= 12 frames -> 8, else 4)")


if __name__ == "__main__":
    main()
