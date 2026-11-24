"""Plan v20 section 8 item 4 (11-24, Opus): B4 (ar2_prop_novid = the two-task body-record model trained without the
video-prediction loss) -- does it fail to USE the record, or fail at basic manipulation? Read-only, CPU, zero GPU.
Descriptive (decides whether B4 goes to the main text or the appendix; plan v20 2.4 last row).
Per model and task, from the per-target object snapshots (scripts/memory_v2/closed_loop_stages.py analyse_swap /
analyse_put_back, RMBench geometry): how far each episode got and the failure type.
  swap_blocks: furthest stage none / lifted / s1 (a block into the empty tray) / s2 (the other block into the vacated
               tray) / s3 / success; the MEMORY decision after s1: other block (right) vs same block again (loop)
  put_back_block: none / lifted / centre / pressed / stage1 / regrasp / returned / success; the choice after the centre
               (its original mat = right, chance 1/4)
Models: ar2_prop_novid e10 (closed_loop/b4) and e30 (closed_loop/b4), against ar2_prop e10 (closed_loop/lc) and e30
(closed_loop/g1). put_back_block at e10 for ar2_prop_novid exists only if the 1-50 cards A40-B4put10 ran.
Writes outputs/fullft/B4_STAGES.json.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/b4_stages.py
"""
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
CLS = Path("/workspace/FastWAM-memory2/scripts/memory_v2/closed_loop_stages.py")
ITEMS = [("b4", "ar2_prop_novid_e10"), ("lc", "ar2_prop_e10"), ("b4", "ar2_prop_novid_e30"), ("g1", "ar2_prop_e30")]


def module():
    spec = importlib.util.spec_from_file_location("closed_loop_stages", CLS)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    cls = module()
    out = {}
    for folder, label in ITEMS:
        for task in ("swap_blocks", "put_back_block"):
            root = O / folder / label / "on" / task
            eps = sorted(d for d in root.glob("seed_*") if d.is_dir() and (d / "result.json").exists())
            if not eps:
                continue
            furthest, choice, ok = Counter(), Counter(), 0
            for d in eps:
                snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
                ok += int(bool(json.loads((d / "result.json").read_text()).get("success")))
                if not snaps:
                    furthest["no log"] += 1
                    continue
                r = cls.analyse_swap(snaps, counters) if task == "swap_blocks" else cls.analyse_put_back(snaps, counters)
                furthest[r["furthest"]] += 1
                key = "second_move" if task == "swap_blocks" else "choice_correct"
                choice[str(r.get(key))] += 1
            k = f"{folder}:{label}:{task}"
            out[k] = {"episodes": len(eps), "success": ok, "furthest": dict(furthest), "memory_decision": dict(choice)}
            print(f"{k}: {len(eps)} episodes, success {ok}")
            print(f"   furthest stage: {dict(furthest.most_common())}")
            print(f"   {'second move after s1' if task == 'swap_blocks' else 'choice after the centre (True = original mat)'}: "
                  f"{dict(choice.most_common())}")
    (F / "B4_STAGES.json").write_text(json.dumps(out, indent=1) + "\n")
    print("B4 STAGES REPORT: written outputs/fullft/B4_STAGES.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
