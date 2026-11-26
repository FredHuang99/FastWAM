"""Plan v21 6.5 zero-training diagnostics on episodes already on the A40 (11-27 02:50, Opus). Read-only, CPU, DESCRIBED
ONLY (no verdict word). Writes outputs/fullft/DIAG_V21_<NAME>.json.

diag1  RANKING, per episode (blocks_ranking_try). Task rules (RMBench envs/blocks_ranking_try.py at 7d1cdfc): three
       blocks on three slots x = 0.04 / 0.16 / 0.28 (l.13-23), a random NON-sorted permutation (l.41-49); success =
       block1 < block2 < block3 in x within (0.13, 0.04) of each other, right gripper open and the button pressed while so
       (check_success l.179-193; press_cnt counts a press when the button is down and press_flag is clear, l.174-177).
       The expert (play_once l.77-102) presses the button with the LEFT arm first (press_button l.123-127), then until
       success swaps two blocks with the RIGHT arm (swap_blocks l.104-121) and presses again, in the fixed swap order
       (middle,right) (left,right) (left,middle) (middle,right) (left,right): it walks the six orders without repeating
       one. Step limit 3500 targets (env_cfg/task_config/_eval_step_limit.yml l.10).
       Per episode: the start order; the expert's walk; the orders at each counted press; each swap (which two blocks
       changed slots, from / to); whether the model's first swap is the expert's; presses on the start order before the
       first swap; the FIRST REPEAT (a press on an order already pressed): its press number and type. Types (fixed
       11-27 02:45 after reading the first 10 episodes of each model - RANKING_SPLIT.json seeds 4300000-4300009 - and
       before any other episode; Status 11-27):
         A  the same order pressed again with no swap in between (seq[i] == seq[i-1])
         B  swapped away and straight back (seq[i] == seq[i-2] != seq[i-1])
         C  back to an earlier order (seq[i] == seq[j], j < i-2), not A / B
         D  other
       Reported TWICE, because in the first 10 episodes 17 of 20 (both models, successes included) pressed the start
       order 2-9 times before the first swap: (1) the first repeat overall (the plan's definition) and (2) the first
       repeat AFTER the first swap. Body-record models also: at the last decision before that press, the number of record
       entries, whether the previous press (a left-arm 'bottom' within +-15 targets) and the last swap (a right-arm
       'open' within +-15 targets of the order change) were in the record. Success tables by the position of the sorted
       order in the expert's walk (1-5) and in the model's own walk (rank among the distinct orders it pressed; 'never').
       Default items: e6:ranking_ar_e30 e6:ranking_arprop_e30 v20:ranking_v3a_e30 (when evaluated).
diag3  REARRANGE press timing (rearrange_blocks), every 'pressed twice' episode (rearr_split class): targets between
       the two counted presses; the second press immediately (no block lifted in between) or after later steps; at the
       decision that STARTED the second press - the last decision at or before the start of the final descent, i.e. the
       last target before the second press with the left EE >= 4 cm above its height at that press - whether the first
       press was in the record (a left-arm 'bottom' within +-15 targets of it); also over all decisions between the two
       presses (always / sometimes / never, as rearr_ledger.py); the lowest left-EE height above the button base within
       +-8 targets of the first press (counted presses are at 0.186-0.191 m, REARR_PRESS_DEPTH 11-24). Write delay of
       every first press (targets until the first decision whose record holds it). Default items: rv3c:rearr_v3c_e30,
       rv3c:rearr_v3c_h2_e30, v20:rearr_pw_e30, e6:rearrange_arprop_e30, e6:rearrange_ar_e30.
diag4a PRESS BUTTON: per button, pressed count (at the first confirm, else the end; closed_loop_stages.py) x the card
       count, cross table and least-squares slope of pressed on card, for e17:press_v3c_e30 (timely writer),
       v20:press_told_e30 (count in the instruction), e17:press_fast_e30 (fast writer), d2:d2_press_e30 (merged).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag_cpu_v21.py diag1 [--first 10] [FOLDER:LABEL ...]
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag_cpu_v21.py diag3 | diag4a
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
WIN = 15


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rows(p: Path):
    out = []
    if p.exists():
        for x in p.read_text().splitlines():
            if x.strip():
                try:
                    out.append(json.loads(x))
                except json.JSONDecodeError:
                    pass
    return out


def tid(acts, k):
    """target id of executed row k (completed_target_id, else its index + 1)."""
    v = acts[k].get("completed_target_id")
    return int(v) if isinstance(v, (int, float)) else k + 1


def ledger_at(decs, t):
    """record entries of the last decision with frame_id < t (None if no such decision / no record logged)."""
    best = None
    for d in decs:
        f = d.get("frame_id")
        if isinstance(f, (int, float)) and f < t:
            best = d
    return None if best is None else (best.get("ledger") if "ledger" in best else None)


def has(ledger, arm, kind, t):
    return any(int(e[1]) == arm and e[2] == kind and abs(int(e[0]) - int(t)) <= WIN for e in (ledger or []))


def rep_type(seq, i):
    if seq[i] == seq[i - 1]:
        return "A same order pressed again, no swap between"
    if i >= 2 and seq[i] == seq[i - 2]:
        return "B swapped away and straight back"
    if seq[i] in seq[:max(0, i - 2)]:
        return "C back to an earlier order"
    return "D other"


# ------------------------------------------------------------------------------------------------------------- diag1
def diag1_episode(rs, d: Path):
    acts, decs = rows(d / "executed_actions.jsonl"), rows(d / "decisions.jsonl")
    res = d / "result.json"
    if not acts or not res.exists():
        return None
    ok = bool(json.loads(res.read_text()).get("success"))
    snaps = [acts[0].get("objects_before") or {}] + [r.get("objects_after") or {} for r in acts]
    start = rs.order(snaps[0])
    exp = [tuple(x) for x in rs.expert_orders(start)] if start else []
    presses, swaps, last, prev = [], [], start, 0
    for k, s in enumerate(snaps):
        o = rs.order(s)
        t = tid(acts, k - 1) if k >= 1 else 0
        if o is not None and last is not None and o != last:
            moved = [b for b in range(3) if o[b] != last[b]]
            swaps.append({"t": t, "from": last, "to": o, "blocks": [b + 1 for b in moved]})
        if o is not None:
            last = o
        c = s.get("press_cnt")
        if isinstance(c, (int, float)) and c > prev:
            presses.append({"t": t, "order": last})
            prev = int(c)
    seq = [p["order"] for p in presses]
    t_sw1 = swaps[0]["t"] if swaps else None
    start_presses = sum(1 for p in presses if t_sw1 is None or p["t"] < t_sw1)

    def first_repeat(lo):
        for i in range(max(1, lo), len(seq)):
            if seq[i] is not None and seq[i] in seq[:i]:
                return i
        return None
    i_all = first_repeat(1)
    i_after = first_repeat(start_presses) if t_sw1 is not None else None
    if i_after is not None and i_after < start_presses:
        i_after = None
    distinct = []
    for o in seq:
        if o is not None and o not in distinct:
            distinct.append(o)
    srt = (0, 1, 2)
    info = {"success": ok, "targets": len(acts), "start": start, "expert_walk": exp,
            "expert_position_of_sorted": exp.index(srt) if srt in exp else None,
            "model_position_of_sorted": distinct.index(srt) if srt in distinct else "never",
            "orders_pressed": seq, "press_targets": [p["t"] for p in presses], "swaps": swaps,
            "first_swap_is_experts": (swaps[0]["to"] == exp[1]) if swaps and len(exp) > 1 else None,
            "start_presses_before_first_swap": start_presses, "record_logged": any("ledger" in x for x in decs)}
    for name, i in (("first_repeat", i_all), ("first_repeat_after_first_swap", i_after)):
        if i is None:
            info[name] = None
            continue
        r = {"press_number": i + 1, "type": rep_type(seq, i), "target": presses[i]["t"]}
        if info["record_logged"]:
            led = ledger_at(decs, presses[i]["t"])
            sw = [s["t"] for s in swaps if s["t"] < presses[i]["t"]]
            r["record_entries"] = len(led) if led is not None else None
            r["previous_press_in_record"] = has(led, 0, "bottom", presses[i - 1]["t"]) if led is not None else None
            r["last_swap_in_record"] = (has(led, 1, "open", sw[-1]) if sw else None) if led is not None else None
        info[name] = r
    return info


def diag1(items, first=0):
    rs = _module("ranking_split", "ranking_split.py")
    task = "blocks_ranking_try"
    out = {"run": "plan v21 diagnostic 1: ranking per episode (described)", "items": {}}
    for item in items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / task
        eps = sorted((d for d in root.glob("seed_*") if d.name[5:].isdigit()), key=lambda d: int(d.name[5:]))
        per = {}
        for d in eps:
            x = diag1_episode(rs, d)
            if x is not None:
                per[d.name[5:]] = x
            if first and len(per) >= first:
                break
        if not per:
            print(f"{item}: no episodes")
            continue
        print(f"\n== {item}: {len(per)} episodes{' (first ' + str(first) + ')' if first else ''}")
        if first:
            for s, x in per.items():
                print(f"  {s} ok {int(x['success'])} start {x['start']} expert {x['expert_walk']}")
                print(f"      pressed {x['orders_pressed']}  swaps {[(w['from'], w['to']) for w in x['swaps']]}")
                print(f"      first repeat {x['first_repeat']}; after first swap {x['first_repeat_after_first_swap']}")
            out["items"][item] = per
            continue
        summ = {}
        for key in ("first_repeat", "first_repeat_after_first_swap"):
            by = defaultdict(Counter)
            for x in per.values():
                r = x[key]
                by["success" if x["success"] else "failure"][r["type"] if r else "no repeat"] += 1
            summ[key] = {k: dict(v) for k, v in by.items()}
            if any(x[key] and "previous_press_in_record" in x[key] for x in per.values()):
                rec = Counter()
                for x in per.values():
                    r = x[key]
                    if r and r.get("record_entries") is not None:
                        rec[(r["type"][0], f"prev press in record {r['previous_press_in_record']}",
                             f"last swap in record {r['last_swap_in_record']}")] += 1
                summ[key + "_record"] = {" / ".join(k): v for k, v in rec.items()}
                n = [x[key]["record_entries"] for x in per.values() if x[key] and x[key].get("record_entries") is not None]
                if n:
                    summ[key + "_record_entries"] = {"median": statistics.median(n), "max": max(n), "n": len(n)}
        tab_e, tab_m = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        for x in per.values():
            tab_e[x["expert_position_of_sorted"]][0] += x["success"]
            tab_e[x["expert_position_of_sorted"]][1] += 1
            tab_m[x["model_position_of_sorted"]][0] += x["success"]
            tab_m[x["model_position_of_sorted"]][1] += 1
        summ["success_by_expert_position"] = {str(k): f"{v[0]}/{v[1]}" for k, v in sorted(tab_e.items(), key=lambda z: str(z[0]))}
        summ["success_by_model_position"] = {str(k): f"{v[0]}/{v[1]}" for k, v in sorted(tab_m.items(), key=lambda z: str(z[0]))}
        summ["first_swap_is_experts"] = dict(Counter(str(x["first_swap_is_experts"]) for x in per.values()))
        summ["start_presses_before_first_swap"] = dict(Counter(x["start_presses_before_first_swap"] for x in per.values()))
        for k, v in summ.items():
            print(f"  {k}: {v}")
        out["items"][item] = {"summary": summ, "episodes": per}
    out["verdict"] = "FIRST 10 ONLY (classes check)" if first else "DESCRIBED"
    return out


# ------------------------------------------------------------------------------------------------------------- diag3
def first_at(acts, n):
    for k, r in enumerate(acts):
        c = (r.get("objects_after") or {}).get("press_cnt")
        if isinstance(c, (int, float)) and c >= n:
            return k
    return None


def diag3(items):
    split = _module("rearr_split", "rearr_split.py")
    depth = _module("rearr_press_depth", "rearr_press_depth.py")
    task = "rearrange_blocks"
    out = {"run": "plan v21 diagnostic 3: rearrange press timing (described)", "items": {}}
    for item in items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / task
        per, delays = {}, []
        for d in sorted((d for d in root.glob("seed_*") if d.name[5:].isdigit()), key=lambda d: int(d.name[5:])):
            acts, decs = rows(d / "executed_actions.jsonl"), rows(d / "decisions.jsonl")
            res = d / "result.json"
            if not acts or not res.exists():
                continue
            ok = bool(json.loads(res.read_text()).get("success"))
            cls, _ = split.classify(acts, ok)
            k1 = first_at(acts, 1)
            logged = any("ledger" in x for x in decs)
            if k1 is not None and logged:
                t1 = tid(acts, k1)
                w = next((int(x["frame_id"]) - t1 for x in decs if isinstance(x.get("frame_id"), (int, float))
                          and x["frame_id"] > t1 and has(x.get("ledger"), 0, "bottom", t1)), None)
                if w is not None:
                    delays.append(w)
            if not cls.startswith("pressed twice"):
                continue
            k2 = first_at(acts, 2)
            if k1 is None or k2 is None:
                continue
            t1, t2 = tid(acts, k1), tid(acts, k2)
            snaps = [acts[0].get("objects_before") or {}] + [r.get("objects_after") or {} for r in acts]
            z0 = {b: (split.pos(snaps[0], b) or [0, 0, 0])[2] for b in ("block1", "block2")}
            lifted = any((split.pos(snaps[k + 1], b) or [0, 0, 0])[2] > z0[b] + split.LIFT
                         for k in range(k1 + 1, k2) for b in ("block1", "block2"))
            h = [depth.geom(r) for r in acts]
            hz = [g[1] if g else None for g in h]
            low1 = min((hz[k] for k in range(max(0, k1 - 8), min(len(hz), k1 + 9)) if hz[k] is not None), default=None)
            start = None
            if hz[k2] is not None:
                for k in range(k2 - 1, k1, -1):
                    if hz[k] is not None and hz[k] >= hz[k2] + 0.04:
                        start = tid(acts, k)
                        break
            r = {"targets_between": t2 - t1, "second_press": "after later steps (a block lifted in between)" if lifted
                 else "immediately (no block lifted in between)", "lowest_ee_at_first_press_m": low1,
                 "descent_start_target": start}
            if logged:
                between = [x for x in decs if isinstance(x.get("frame_id"), (int, float)) and t1 < x["frame_id"] <= t2]
                flags = [has(x.get("ledger"), 0, "bottom", t1) for x in between]
                r["first_press_in_record_between"] = ("always" if flags and all(flags) else "never" if not any(flags)
                                                      else "sometimes")
                if start is not None:
                    led = None
                    for x in decs:
                        if isinstance(x.get("frame_id"), (int, float)) and x["frame_id"] <= start:
                            led = x.get("ledger")
                    r["first_press_in_record_at_the_starting_decision"] = has(led, 0, "bottom", t1) if led is not None else None
            per[d.name[5:]] = r
        summ = {"pressed_twice": len(per),
                "second_press": dict(Counter(v["second_press"] for v in per.values())),
                "targets_between": {"median": statistics.median([v["targets_between"] for v in per.values()])} if per else None,
                "lowest_ee_at_first_press_m": sorted(round(v["lowest_ee_at_first_press_m"], 3) for v in per.values()
                                                     if v["lowest_ee_at_first_press_m"] is not None)}
        if any("first_press_in_record_between" in v for v in per.values()):
            summ["first_press_in_record_between"] = dict(Counter(v.get("first_press_in_record_between") for v in per.values()))
            summ["first_press_in_record_at_the_starting_decision"] = dict(Counter(
                str(v.get("first_press_in_record_at_the_starting_decision")) for v in per.values()))
        if delays:
            summ["write_delay_targets"] = {"median": statistics.median(delays), "min": min(delays), "max": max(delays),
                                           "n": len(delays)}
        print(f"\n== {item}: {summ}")
        out["items"][item] = {"summary": summ, "episodes": per}
    out["verdict"] = "DESCRIBED"
    return out


# ------------------------------------------------------------------------------------------------------------ diag4a
def diag4a(items):
    pp = _module("press_pair", "press_pair.py")
    out = {"run": "plan v21 diagnostic 4(a): pressed count x card count per button (described)", "items": {}}
    for item in items:
        folder, label = item.split(":", 1)
        try:
            st = pp.stages(folder, label)
        except Exception as e:                    # noqa: BLE001
            print(f"{item}: no stages ({type(e).__name__})")
            continue
        r = {}
        for b, (nk, ck) in (("button1", ("n1", "card_1")), ("button2", ("n2", "card_2"))):
            pairs = [(v[ck], v[nk]) for v in st.values() if isinstance(v.get(ck), int) and isinstance(v.get(nk), int)]
            tab = defaultdict(Counter)
            for c, n in pairs:
                tab[c][n] += 1
            slope = None
            if len(pairs) >= 3:
                mc = sum(c for c, _ in pairs) / len(pairs)
                mn = sum(n for _, n in pairs) / len(pairs)
                sxx = sum((c - mc) ** 2 for c, _ in pairs)
                slope = round(sum((c - mc) * (n - mn) for c, n in pairs) / sxx, 3) if sxx else None
            r[b] = {"episodes": len(pairs), "slope_pressed_on_card": slope,
                    "table_card_to_pressed": {str(c): dict(sorted(v.items())) for c, v in sorted(tab.items())}}
        r["success"] = sum(bool(v.get("success")) for v in st.values())
        print(f"\n== {item}: success {r['success']}; slopes {r.get('button1', {}).get('slope_pressed_on_card')} / "
              f"{r.get('button2', {}).get('slope_pressed_on_card')}")
        out["items"][item] = r
    out["verdict"] = "DESCRIBED"
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", choices=("diag1", "diag3", "diag4a"))
    ap.add_argument("items", nargs="*")
    ap.add_argument("--first", type=int, default=0)
    a = ap.parse_args()
    if a.name == "diag1":
        items = a.items or ["e6:ranking_ar_e30", "e6:ranking_arprop_e30", "v20:ranking_v3a_e30"]
        out = diag1(items, a.first)
        name = "DIAG1_FIRST10" if a.first else "DIAG1"
    elif a.name == "diag3":
        out = diag3(a.items or ["rv3c:rearr_v3c_e30", "rv3c:rearr_v3c_h2_e30", "v20:rearr_pw_e30",
                                "e6:rearrange_arprop_e30", "e6:rearrange_ar_e30"])
        name = "DIAG3"
    else:
        out = diag4a(a.items or ["e17:press_v3c_e30", "v20:press_told_e30", "e17:press_fast_e30", "d2:d2_press_e30"])
        name = "DIAG4A"
    (F / f"DIAG_V21_{name}.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"\nDIAG V21 {name}: {out['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
