"""Plan v21 6.5 zero-training diagnostics, A40 reports (11-27 02:20, Opus; written before any episode of these runs).
Read-only, CPU, DESCRIBED ONLY (no verdict word): counts and paired counts beside the unmodified runs of the same scenes.
  diag2   ranking reading audit (closed_loop/diag2): per condition (body record: record off / first frame masked /
          near frames masked; three-frame: first / near masked) the successes on the 30 audit scenes, split by the
          position of the sorted order in the expert's walk (1-2 / 4-5), beside the unmodified e6 runs of the same
          scenes; ranking_split.episode classes and the orders pressed per episode.
  diag5a  swap_T masks (closed_loop/diag5): swapT_ar e30 first / near masked, swapT_arprop e30 first / near masked and
          record off, scenes 1-50, beside e6 on the same scenes; swapT_split.measure per episode (MWAM_OBJECT_LOG=1):
          for each failure whether a block ended at its own start (< 2.5 cm; card 11's "back at its own place").
  rearrrt rearrange re-tests: rearr_pw e30 with MWAM_NOISE_SALT=r2 (closed_loop/r2) beside the default draw (v20),
          rearr_split classes; pause 256 visible / hidden 1-50 (closed_loop/v21rt), paired counts and classes.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag_v21.py diag2|diag5a|rearrrt
Writes outputs/fullft/DIAG_V21_<NAME>.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


gen = _module("gen_v21_tasks", "gen_v21_tasks.py")
v20 = _module("v20_verdict", "v20_verdict.py")


def results(folder, label, task):
    """{seed: success} of the finished episodes (any scene subset)."""
    root = O / folder / label / "on" / task
    out = {}
    for d in root.glob("seed_*"):
        r = d / "result.json"
        if d.name[5:].isdigit() and r.exists():
            out[int(d.name[5:])] = int(bool(json.loads(r.read_text()).get("success")))
    return out


def paired(new, ref, seeds):
    common = [s for s in seeds if s in new and s in ref]
    return {"scenes": len(common), "new": sum(new[s] for s in common), "ref": sum(ref[s] for s in common),
            "only_new": sum(new[s] and not ref[s] for s in common), "only_ref": sum(ref[s] and not new[s] for s in common)}


def diag2():
    rs = _module("ranking_split", "ranking_split.py")
    task = "blocks_ranking_try"
    groups = {"position_1_2": gen.D2_P12, "position_4_5": gen.D2_P45}
    conds = {"ranking_arprop_e30": ["off", "mfirst", "mnear"], "ranking_ar_e30": ["mfirst", "mnear"]}
    out = {"run": "plan v21 diagnostic 2: ranking reading audit (described)", "scenes": groups, "models": {}}
    for model, cs in conds.items():
        base = results("e6", model, task)
        m = {"unmodified_e6": {g: sum(base.get(s, 0) for s in L) for g, L in groups.items()}}
        for c in cs:
            lab = f"{model}_{c}"
            r = results("diag2", lab, task)
            row = {"finished": len(r)}
            for g, L in groups.items():
                row[g] = paired(r, base, L)
            eps = {}
            for d in sorted((O / "diag2" / lab / "on" / task).glob("seed_*")):
                if (d / "result.json").exists() and (d / "executed_actions.jsonl").exists():
                    cls, info = rs.episode(d)
                    eps[d.name[5:]] = {"cls": cls, "orders_pressed": info["orders_pressed"],
                                       "expert_position_of_sorted": info["expert_position_of_sorted"]}
            row["classes"] = dict(Counter(v["cls"] for v in eps.values()))
            row["episodes"] = eps
            m[c] = row
        out["models"][model] = m
    done = all(m[c]["finished"] >= 30 for model, m in out["models"].items() for c in conds[model])
    out["verdict"] = "DESCRIBED" if done else "PARTIAL (not every condition has its 30 episodes)"
    return out


def diag5a():
    sp = _module("swapT_split", "swapT_split.py")
    task = "swap_T"
    seeds = v20.dv.seeds(task)[:50]
    conds = {"swapT_ar_e30": ["mfirst", "mnear"], "swapT_arprop_e30": ["mfirst", "mnear", "off"]}
    out = {"run": "plan v21 diagnostic 5(a): swap_T masks and record off, scenes 1-50 (described)", "models": {}}
    for model, cs in conds.items():
        base = results("e6", model, task)
        m = {"unmodified_e6_1_50": sum(base.get(s, 0) for s in seeds)}
        for c in cs:
            lab = f"{model}_{c}"
            r = results("diag5", lab, task)
            row = {"finished": len(r), "paired": paired(r, base, seeds)}
            own = Counter()
            for d in sorted((O / "diag5" / lab / "on" / task).glob("seed_*")):
                x = sp.measure(d)
                if not x or "why" in x or x["success"]:
                    continue
                back = [b for b in ("T_block1", "T_block2") if x[b]["to_own_start_cm"] < 2.5 and x[b]["lifted"]]
                own["a block back at its own start" if back else "no block back at its own start"] += 1
            row["failures"] = dict(own)
            m[c] = row
        out["models"][model] = m
    done = all(m[c]["finished"] >= 50 for model, m in out["models"].items() for c in conds[model])
    out["verdict"] = "DESCRIBED" if done else "PARTIAL"
    return out


def rearrrt():
    task = "rearrange_blocks"
    seeds = v20.dv.seeds(task)
    d = results("v20", "rearr_pw_e30", task)
    r2 = results("r2", "rearr_pw_e30", task)
    out = {"run": "plan v21 6.5 rearrange re-tests of rearr_pw e30 (described)",
           "second_noise_draw": {"finished": len(r2), "success": sum(r2.values()), "default_draw": sum(d.values()),
                                 "paired": paired(r2, d, seeds),
                                 "classes_r2": dict(Counter(v20.rearr_classes("r2", "rearr_pw_e30").values()))}}
    vis, hid = results("v21rt", "rearr_pw_e30_p256_vis", task), results("v21rt", "rearr_pw_e30_p256_hid", task)
    out["pause_256"] = {"finished": {"vis": len(vis), "hid": len(hid)}, "visible": sum(vis.values()),
                        "hidden": sum(hid.values()), "paired_hidden_vs_visible": paired(hid, vis, seeds[:50]),
                        "no_pause_same_scenes": sum(d.get(s, 0) for s in seeds[:50]),
                        "classes_vis": dict(Counter(v20.rearr_classes("v21rt", "rearr_pw_e30_p256_vis").values())),
                        "classes_hid": dict(Counter(v20.rearr_classes("v21rt", "rearr_pw_e30_p256_hid").values()))}
    done = len(r2) >= 100 and len(vis) >= 50 and len(hid) >= 50
    out["verdict"] = "DESCRIBED" if done else "PARTIAL"
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    fns = {"diag2": diag2, "diag5a": diag5a, "rearrrt": rearrrt}
    if name not in fns:
        print(__doc__)
        return 2
    out = fns[name]()
    print(json.dumps({k: v for k, v in out.items() if k != "models"}, default=str)[:4000])
    (F / f"DIAG_V21_{name.upper()}.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"DIAG V21 {name.upper()}: {out['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
