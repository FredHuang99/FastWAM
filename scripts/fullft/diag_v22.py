#!/usr/bin/env python3
"""Plan v22 (Fable, rev. 1) diagnostics 9, 10 and 11, A40 reports (appendix of claude/MemWAM_Plan_v22_20261128.md).
Written 11-28 16:44 (Opus) before any episode of these runs. Read-only, CPU, DESCRIBED ONLY (no verdict word).
  diag9   rearrange, the two seeds of rearr_pw e30 (seed 17 v20:rearr_pw_e30, 93; seed 18 v21:rearr_pw_s18_e30, 61) with
          the record switched off at test time (MWAM_LEDGER=off), scenes 1-50 (closed_loop/d9): success and rearr_split
          classes beside the unmodified episodes of the same scenes. Written before (plan v22 2.3): if the record is read,
          seed 17's "pressed twice" rises from 0 to 15 or more; if seed 18 does not read it, its success changes by < 5.
  diag10  ranking, ranking_v3a e30 (91) on diagnostic 2's 30 audit scenes (positions 1-2 / 4-5 of the sorted order in
          the expert's walk) with the record off / the first frame masked / the near frames masked (closed_loop/d10),
          beside its unmodified v20 episodes, by position group; ranking_split classes. CPU part: its 9 failures at
          the first repeat after the first swap -- record entries (cap 69), previous press / last swap in the record,
          the repeat type and the two blocks of the last swap -- read from DIAG_V21_DIAG1.json (diag_cpu_v21.py diag1
          on v20:ranking_v3a_e30, 11-27 12:20).
  diag11  put_back_block, ar2_v3c e30's 23 failures over its two evaluations (v20 default noise, r2): the stage reached
          (b4_stages-style furthest stage, deed_verdict's split) per failure; and ar2_prop_s18 (seed 18 of the 100 / 100
          two-task body record): e30 put_back_block / swap_blocks 1-100 and e10 swap_blocks 1-100 (closed_loop/d11)
          beside seed 17 (g1:ar2_prop_e30 100 / 100; ar2_prop e10 swap 78).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag_v22.py diag9|diag10|diag11
Writes outputs/fullft/DIAG_V22_DIAG9.json / _DIAG10.json / _DIAG11.json.
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


d21 = _module("diag_v21", "diag_v21.py")
results, paired, v20, gen = d21.results, d21.paired, d21.v20, d21.gen


def diag9():
    task = "rearrange_blocks"
    seeds = v20.dv.seeds(task)[:50]
    out = {"run": "plan v22 diagnostic 9: rearrange record off at test time, both seeds of rearr_pw e30 (described)",
           "models": {}}
    done = True
    for tag, folder, label in (("seed17", "v20", "rearr_pw_e30"), ("seed18", "v21", "rearr_pw_s18_e30")):
        base = results(folder, label, task)
        off = results("d9", f"{label}_off", task)
        cb = v20.rearr_classes(folder, label)
        co = v20.rearr_classes("d9", f"{label}_off")
        out["models"][tag] = {
            "unmodified": f"{folder}:{label}", "off": f"d9:{label}_off", "finished_off": len(off),
            "paired_off_vs_unmodified": paired(off, base, seeds),
            "classes_unmodified_1_50": dict(Counter(cb[s] for s in seeds if s in cb)),
            "classes_off": dict(Counter(co[s] for s in seeds if s in co))}
        done = done and len(off) >= 50
    out["verdict"] = "DESCRIBED" if done else "PARTIAL"
    return out


def diag10():
    rs = _module("ranking_split", "ranking_split.py")
    task = "blocks_ranking_try"
    groups = {"position_1_2": gen.D2_P12, "position_4_5": gen.D2_P45}
    model = "ranking_v3a_e30"
    base = results("v20", model, task)
    out = {"run": "plan v22 diagnostic 10: ranking_v3a reading audit and its failures (described)", "scenes": groups,
           "unmodified_v20": {g: sum(base.get(s, 0) for s in L) for g, L in groups.items()}, "conditions": {}}
    done = True
    for c in ("off", "mfirst", "mnear"):
        lab = f"{model}_{c}"
        r = results("d10", lab, task)
        row = {"finished": len(r)}
        for g, L in groups.items():
            row[g] = paired(r, base, L)
        cls = Counter()
        for d in sorted((O / "d10" / lab / "on" / task).glob("seed_*")):
            if (d / "result.json").exists() and (d / "executed_actions.jsonl").exists():
                cls[rs.episode(d)[0]] += 1
        row["classes"] = dict(cls)
        out["conditions"][c] = row
        done = done and len(r) >= 30
    d1 = F / "DIAG_V21_DIAG1.json"
    fails = {}
    if d1.exists():
        eps = (json.loads(d1.read_text()).get("items", {}).get(f"v20:{model}") or {}).get("episodes", {})
        for s, x in eps.items():
            if x.get("success") is False:
                fr = x.get("first_repeat_after_first_swap") or {}
                sw = [w for w in x.get("swaps", []) if fr and w["t"] < fr.get("target", 10 ** 9)]
                fails[s] = {"expert_position_of_sorted": x.get("expert_position_of_sorted"),
                            "first_repeat_after_first_swap": fr or None,
                            "last_swap_blocks": sw[-1]["blocks"] if sw else None,
                            "orders_pressed": x.get("orders_pressed")}
    out["failures_from_diag1"] = fails
    out["failures_record_full"] = sum(1 for f in fails.values()
                                      if (f["first_repeat_after_first_swap"] or {}).get("record_entries") == 69)
    out["verdict"] = "DESCRIBED" if done and fails else "PARTIAL"
    return out


def diag11():
    out = {"run": "plan v22 diagnostic 11: put_back failures of ar2_v3c; seed 18 of ar2_prop (described)"}
    cls = _module("b4_stages", "b4_stages.py").module()      # scripts/memory_v2/closed_loop_stages.py (B4's stages)
    st = {}
    for folder in ("v20", "r2"):
        root = O / folder / "ar2_v3c_e30" / "on" / "put_back_block"
        for d in sorted(root.glob("seed_*")):
            r = d / "result.json"
            if not (d.name[5:].isdigit() and r.exists()) or json.loads(r.read_text()).get("success"):
                continue
            snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
            if not snaps:
                st[f"{folder}:{d.name[5:]}"] = {"furthest": "no log"}
                continue
            a = cls.analyse_put_back(snaps, counters)
            st[f"{folder}:{d.name[5:]}"] = {"furthest": a.get("furthest"), "choice_correct": a.get("choice_correct")}
    out["ar2_v3c_put_failures"] = {"n": len(st), "furthest": dict(Counter(str(v["furthest"]) for v in st.values())),
                                   "choice_after_centre": dict(Counter(str(v.get("choice_correct")) for v in st.values())),
                                   "episodes": st}
    seeds = {t: v20.dv.seeds(t) for t in ("put_back_block", "swap_blocks")}
    s18 = {}
    for lab, t, ref_folder, ref_label in (("ar2_prop_s18_e30", "put_back_block", "g1", "ar2_prop_e30"),
                                          ("ar2_prop_s18_e30", "swap_blocks", "g1", "ar2_prop_e30"),
                                          ("ar2_prop_s18_e10", "swap_blocks", "lc", "ar2_prop_e10")):
        new, ref = results("d11", lab, t), results(ref_folder, ref_label, t)
        s18[f"{lab} {t}"] = {"finished": len(new), "success": sum(new.values()),
                             "against_seed17": paired(new, ref, seeds[t]), "seed17": f"{ref_folder}:{ref_label}"}
    out["ar2_prop_seed18"] = s18
    out["verdict"] = "DESCRIBED" if all(v["finished"] >= 100 for v in s18.values()) else "PARTIAL"
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    fns = {"diag9": diag9, "diag10": diag10, "diag11": diag11}
    if name not in fns:
        print(__doc__)
        return 2
    out = fns[name]()
    (F / f"DIAG_V22_{name.upper()}.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("failures_from_diag1",)}, default=str)[:4000])
    print(f"DIAG V22 {name}: {out['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
