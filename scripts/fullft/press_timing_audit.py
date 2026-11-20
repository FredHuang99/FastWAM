"""Plan v17 G4-0 (Fable review of plan v16, 2.1 / part 2 item 1: O1, O2, O3, O5): when was the robot's own press
readable, compared with what it did next? Read-only, CPU only; episode files are read, never written.
Written 11-20 21:30 BJ by Opus, BEFORE the O1 table or the O3 chain below was computed on any episode.

Why (Fable): "41 over-pressing phases, 32 of them late" (press_ledger_audit) has no denominator: the phases that did
NOT over-press were never classified. If records were just as often late there, lateness explains nothing.

Episodes as in press_ledger_audit.py (same press registration, same bottom matching within +-10 frames, same phases:
k = 1 / 2, T = frame of the card_k-th press of button k; outcome 'over' = the next registered press is button k again,
'moved on' = another button). New per phase (outcomes 'over' and 'moved on' only):
  full     first decision frame whose ledger holds the bottoms of all card_k presses of button k (None if one of
           them was never recorded = 'never')
  E        full - T (frames from the deciding press to the first decision that could read the full count)
  V_h      full is not None and full <= T + h, for h = 8 / 12 / 16 (one / one and a half / two decision periods)
  mirror   the press_ledger_audit 'late' rule applied to both outcomes: full is None or full > T_next - 16, T_next =
           the next registered press (any button); descriptive only (moved-on phases have longer T_next - T, so this
           rule is biased toward 'visible' there)
O5 (per recorded press of buttons 1 / 2, and separately for the deciding card_k-th presses): with t = registration,
  t_bot = the matched ledger bottom (turning point), t_conf = its 'confirmed' frame, t_vis = first decision showing it:
  a = t_bot - t, b = t_conf - t_bot (the detector waiting for the 12 mm rise), c = t_vis - t_conf (waiting for the
  next decision). Medians and p90 of a, b, c and of the total.
O3 chain (over phases): every press of button k after T before the robot first presses another button is an extra
  press x_j (j = 1, 2, ...). At the cutoff x_j - 16 (two decisions before it registered), how many of the presses of
  button k before x_j were in the ledger of the last decision <= cutoff? 'full' if >= card_k, else 'short'.
  A 'full' at j >= 2 means the model pressed again while its ledger already held the required number.
T2 boundary R (Fable 1(b); computed and committed BEFORE the T2 result is read): for every over-pressing phase of the
  press_ledger_audit class 'late', s = frames from the confirmation of the deciding press to the turning point ('top'
  ledger entry of the same arm) that starts the extra press's descent; R = mean of min(1, s / 4). timing_meaning.py
  reads T2 against R (g1 run, button 1, the T2 metric).
O2 (descriptive): over rate by E bin (<= 8, 9-12, 13-16, > 16, never).
O3 (descriptive): first-count error e1 (button 1 presses - card 1) by card number; share of e1 >= +2 among e1 >= +1.
  The 5090 log already printed e1 by card for g1:press_count_e30 before this script existed (+1: 11, +2: 8, +3: 4,
  +5: 1), so no reading is registered on these two O3 quantities.

Registered reading (O1; written before computing it). PRIMARY = the runs of the T1 / T2 model press_count e30 that
exist: g1 (scenes 1-50), sel (51-100), rep (51-100, noise r2), phases pooled over runs and both buttons.
  rows V_12 (readable within 12 frames of the deciding press) and not V_12 (later or never); over rate per row.
  over(not V_12) - over(V_12) >= 0.20 and one-sided Fisher p < 0.05  -> TIMING PREDICTS
  |difference| <= 0.10                                                 -> NOT DIAGNOSTIC
  otherwise                                                            -> UNCLEAR
  floor: each row >= 10 phases, else the same rule on V_16 (registered fallback); if that row is short too: NO READING.
  Reported with the same rule, not the reading: excluding 'never' phases (a shallow re-press can itself cause the
  miss: reverse causation); each run alone; every --describe run (press_v3c e30, press_arprop ...).
Expectation (subjective, before the run): TIMING PREDICTS 0.5, UNCLEAR 0.3, NOT DIAGNOSTIC 0.2.
O3 chain, registered: over phases with j >= 2 extra presses; 'full' at j >= 2 in >= 50 % of them -> CHAIN MISREAD
  (beyond the first extra press the model re-presses with the count already in its ledger); <= 20 % -> CHAIN LATE;
  otherwise CHAIN MIXED; floor >= 10 extra presses with j >= 2, else NO READING. Pooled over the PRIMARY runs.

  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_timing_audit.py \
      --primary g1:press_count_e30 sel:press_count_e30 rep:press_count_e30 \
      --describe g1:press_v3c_e30 sel:press_v3c_e30
  --selftest runs the synthetic checks. Writes outputs/fullft/PRESS_TIMING_AUDIT.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("press_ledger_audit", HERE / "press_ledger_audit.py")
pla = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pla)

R = pla.R
O = pla.O
OUT = R / "outputs/fullft"
HS = (8, 12, 16)
BINS = (("<=8", 0, 8), ("9-12", 9, 12), ("13-16", 13, 16), (">16", 17, 10 ** 9))


def fisher_one_sided(a: int, b: int, c: int, d: int) -> float:
    """P(X >= a) for the 2x2 table [[a, b], [c, d]] (row 1 = the row predicted to over-press more; a = its overs)."""
    r1, c1, n = a + b, a + c, a + b + c + d

    def h(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    return min(1.0, sum(h(x) for x in range(a, min(r1, c1) + 1)))


def q(values, f):
    v = sorted(x for x in values if x is not None)
    return None if not v else v[min(len(v) - 1, max(0, int(math.ceil(f * len(v))) - 1))]


def med(values):
    v = [x for x in values if x is not None]
    return None if not v else statistics.median(v)


def episode(directory: Path) -> dict:
    """press_ledger_audit's registration / matching, plus per-press confirmation and the per-phase timing."""
    base = pla.analyse_episode(directory)
    rows = pla.read_jsonl(directory / "executed_actions.jsonl")
    decisions = pla.read_jsonl(directory / "decisions.jsonl")
    first = (rows[0].get("objects_before") or {}) if rows else {}
    after = [r.get("objects_after") or {} for r in rows]
    presses, prev = [], {c: int(first.get(c) or 0) for c, _, _ in pla.COUNTERS}
    for i, a in enumerate(after):
        for c, _, b in pla.COUNTERS:
            v = int(a.get(c) or 0)
            for _ in range(max(0, v - prev[c])):
                presses.append({"frame": i + 1, "button": b})
            prev[c] = max(prev[c], v)
    presses.sort(key=lambda p: (p["frame"], p["button"]))
    bottoms, shown, tops = {}, [], set()
    for d in decisions:
        keys = set()
        for e in d.get("ledger") or []:
            frame, arm, kind, confirmed = int(e[0]), int(e[1]), e[2], int(e[3])
            if kind == "top":
                tops.add((frame, arm))
            if kind != "bottom":
                continue
            keys.add((frame, arm))
            bottoms.setdefault((frame, arm), {"confirmed": confirmed, "visible": int(d["frame_id"])})
        shown.append((int(d["frame_id"]), keys))
    shown.sort(key=lambda x: x[0])
    free = sorted(bottoms)
    for p in presses:                               # the same one-to-one matching as press_ledger_audit
        p["bottom"] = None
        if p["button"] == 3:
            continue
        cand = [k for k in free if abs(k[0] - p["frame"]) <= pla.W]
        if cand:
            k = min(cand, key=lambda k: (abs(k[0] - p["frame"]), k[0]))
            free.remove(k)
            p["bottom"] = k
            p["t_bot"], p["t_conf"], p["t_vis"] = k[0], bottoms[k]["confirmed"], bottoms[k]["visible"]

    def keys_at(cutoff):
        last = None
        for f, keys in shown:
            if f <= cutoff:
                last = keys
            else:
                break
        return last or set()

    def decomposition(p):
        return {"a": p["t_bot"] - p["frame"], "b": p["t_conf"] - p["t_bot"], "c": p["t_vis"] - p["t_conf"],
                "total": p["t_vis"] - p["frame"]}

    card = base["card"]
    phases = []
    for k, ph in base["phases"].items():
        if ph["outcome"] not in ("over", "moved on"):
            continue
        c = int(card[k])
        mine = [p for p in presses if p["button"] == k]
        T = mine[c - 1]["frame"]
        need = [p["bottom"] for p in mine[:c]]
        full = None
        if all(n is not None for n in need):
            full = next((f for f, keys in shown if all(n in keys for n in need)), None)
        later = [p for p in presses if p["frame"] > T or (p["frame"] == T and p is not mine[c - 1] and p["button"] != k)]
        t_next = later[0]["frame"] if later else None
        row = {"seed": base["seed"], "button": k, "card": c, "T": T, "outcome": ph["outcome"], "full": full,
               "E": None if full is None else full - T, "never": full is None, "T_next": t_next,
               "mirror_late": full is None or (t_next is not None and full > t_next - 16)}
        for h in HS:
            row[f"V{h}"] = full is not None and full <= T + h
        last = mine[c - 1]
        row["deciding"] = decomposition(last) if last["bottom"] is not None else None
        if ph["outcome"] == "over":
            # s (Fable 1(b)): from the confirmation of the deciding press to the turning point ('top' entry of the
            # same arm) that starts the extra press's descent; None if either was never recorded
            t_over = ph["T_over"]
            row["T_over"] = t_over
            row["audit_class"] = ph["why"]
            if last["bottom"] is not None:
                arm = last["bottom"][1]
                tt = sorted(f for f, a in tops if a == arm and last["t_bot"] < f < t_over)
                row["s"] = (tt[0] - last["t_conf"]) if tt else None
            else:
                row["s"] = None
            leave = next((p["frame"] for p in presses if p["frame"] > T and p["button"] != k), 10 ** 9)
            extra = [p for p in mine[c:] if p["frame"] < leave]
            chain = []
            for j, x in enumerate(extra, 1):
                before = [p for p in mine if p["frame"] < x["frame"] and p["bottom"] is not None]
                keys = keys_at(x["frame"] - 16)
                n_vis = sum(p["bottom"] in keys for p in before)
                chain.append({"j": j, "frame": x["frame"], "visible": n_vis, "status": "full" if n_vis >= c else "short"})
            row["chain"] = chain
        phases.append(row)
    e1 = None
    if card.get(1) is not None:
        e1 = sum(p["button"] == 1 for p in presses) - int(card[1])
    return {"seed": base["seed"], "card": card, "e1": e1, "phases": phases,
            "presses": [decomposition(p) for p in presses if p["button"] in (1, 2) and p["bottom"] is not None]}


def run_episodes(item: str):
    folder, label = item.split(":", 1)
    root = (Path(folder) if folder.startswith("/") else O / "closed_loop" / folder) / label / "on" / pla.TASK
    eps = []
    for d in sorted(root.glob("seed_*")):
        if d.name.split("_", 1)[1].isdigit() and (d / "result.json").exists() and (d / "decisions.jsonl").exists():
            eps.append(episode(d))
    return eps


def table(phases, key):
    """rows: key True / False; returns (overs, moved) per row."""
    t = {True: [0, 0], False: [0, 0]}
    for ph in phases:
        t[bool(ph[key])][0 if ph["outcome"] == "over" else 1] += 1
    return t


def o1_reading(phases) -> dict:
    out = {}
    for h in (12, 16):
        t = table(phases, f"V{h}")
        (ov, mv), (on, mn) = t[True], t[False]
        nv, nn = ov + mv, on + mn
        rv, rn = (ov / nv if nv else None), (on / nn if nn else None)
        cell = {"visible": {"over": ov, "moved_on": mv, "rate": rv}, "not_visible": {"over": on, "moved_on": mn, "rate": rn}}
        if nv < 10 or nn < 10:
            cell["word"] = f"NO READING (rows {nv} / {nn} < 10)"
        else:
            diff = rn - rv
            p = fisher_one_sided(on, mn, ov, mv)
            cell.update(diff=round(diff, 3), p=p)
            cell["word"] = ("TIMING PREDICTS" if diff >= 0.20 and p < 0.05 else
                            "NOT DIAGNOSTIC" if abs(diff) <= 0.10 else "UNCLEAR")
        out[f"V{h}"] = cell
    out["word"] = out["V12"]["word"] if not out["V12"]["word"].startswith("NO READING") else (
        out["V16"]["word"] + " (fallback V16)")
    return out


def chain_reading(phases) -> dict:
    late = [x for ph in phases if ph["outcome"] == "over" for x in ph.get("chain", []) if x["j"] >= 2]
    j1 = [x for ph in phases if ph["outcome"] == "over" for x in ph.get("chain", []) if x["j"] == 1]
    full = sum(x["status"] == "full" for x in late)
    word = (f"NO READING ({len(late)} extra presses with j >= 2 < 10)" if len(late) < 10 else
            "CHAIN MISREAD" if full >= 0.5 * len(late) else "CHAIN LATE" if full <= 0.2 * len(late) else "CHAIN MIXED")
    return {"j1": len(j1), "j1_full": sum(x["status"] == "full" for x in j1), "j2plus": len(late), "j2plus_full": full,
            "word": word}


def describe(eps) -> dict:
    phases = [ph for e in eps for ph in e["phases"]]
    pr = [x for e in eps for x in e["presses"]]
    dec = [ph["deciding"] for ph in phases if ph["deciding"]]
    o5 = {}
    for name, src in (("all_recorded", pr), ("deciding", dec)):
        o5[name] = {k: {"median": med([x[k] for x in src]), "p90": q([x[k] for x in src], 0.9)}
                    for k in ("a", "b", "c", "total")}
        o5[name]["n"] = len(src)
    bins = {}
    for name, lo, hi in BINS:
        sel = [ph for ph in phases if ph["E"] is not None and lo <= ph["E"] <= hi]
        bins[name] = [sum(ph["outcome"] == "over" for ph in sel), len(sel)]
    nev = [ph for ph in phases if ph["never"]]
    bins["never"] = [sum(ph["outcome"] == "over" for ph in nev), len(nev)]
    mirror = table(phases, "mirror_late")
    by_card = {}
    for e in eps:
        if e["e1"] is None or e["card"].get(1) is None:
            continue
        by_card.setdefault(int(e["card"][1]), []).append(e["e1"])
    over = [x for v in by_card.values() for x in v if x >= 1]
    late = [ph for ph in phases if ph["outcome"] == "over" and ph.get("audit_class") == "late"]
    late_b1 = [ph for ph in late if ph["button"] == 1]
    r_all = [min(1.0, max(0, ph["s"]) / 4) for ph in late if ph.get("s") is not None]
    r_b1 = [min(1.0, max(0, ph["s"]) / 4) for ph in late_b1 if ph.get("s") is not None]
    t2_r = {"R_late_all": round(sum(r_all) / len(r_all), 3) if r_all else None, "n_late_all": len(late),
            "n_with_s_all": len(r_all), "R_late_button1": round(sum(r_b1) / len(r_b1), 3) if r_b1 else None,
            "n_late_button1": len(late_b1), "n_with_s_button1": len(r_b1),
            "s_median_late": med([ph["s"] for ph in late if ph.get("s") is not None])}
    return {"episodes": len(eps), "phases": len(phases), "t2_R": t2_r,
            "outcomes": {o: sum(ph["outcome"] == o for ph in phases) for o in ("over", "moved on")},
            "o1": o1_reading(phases),
            "o1_without_never": o1_reading([ph for ph in phases if not ph["never"]]),
            "o2_over_by_E": bins, "o3_chain": chain_reading(phases),
            "o3_e1_by_card": {c: sorted(v) for c, v in sorted(by_card.items())},
            "o3_share_e1_2plus_among_over": [sum(x >= 2 for x in over), len(over)],
            "o5": o5, "mirror_late": {"late": mirror[True], "not_late": mirror[False]}}


def show(name, s):
    o1 = s["o1"]
    print(f"== {name}: {s['episodes']} episodes, {s['phases']} phases {s['outcomes']}")
    for h in ("V12", "V16"):
        c = o1[h]
        print(f"   O1 {h}: readable in time over/moved {c['visible']['over']}/{c['visible']['moved_on']}; "
              f"not readable {c['not_visible']['over']}/{c['not_visible']['moved_on']}; diff {c.get('diff')} "
              f"p {c.get('p')} -> {c['word']}")
    print(f"   O1 READING {name}: {o1['word']}   (without 'never' phases: {s['o1_without_never']['word']})")
    print(f"   O2 over / phases by E: {s['o2_over_by_E']}")
    print(f"   O3 chain: {s['o3_chain']}")
    print(f"   O3 e1 >= +2 among e1 >= +1: {s['o3_share_e1_2plus_among_over']}; e1 by card: {s['o3_e1_by_card']}")
    a, d = s["o5"]["all_recorded"], s["o5"]["deciding"]
    print(f"   O5 all recorded presses (n {a['n']}): press->bottom {a['a']}, bottom->confirmed {a['b']}, "
          f"confirmed->decision {a['c']}, total {a['total']}")
    print(f"   O5 deciding presses (n {d['n']}): press->bottom {d['a']}, bottom->confirmed {d['b']}, "
          f"confirmed->decision {d['c']}, total {d['total']}")
    print(f"   T2 boundary R (Fable 1(b); mean min(1, s/4) over 'late' over-pressing phases): {s['t2_R']}")
    print(f"   mirror rule (press_ledger_audit 'late' on both outcomes; biased, descriptive): late over/moved "
          f"{s['mirror_late']['late']}, not late {s['mirror_late']['not_late']}")


def main_run(primary, extra, out_path: Path):
    result = {"primary": primary, "describe": extra, "runs": {}}
    pooled = []
    for item in primary + extra:
        eps = run_episodes(item)
        s = describe(eps)
        result["runs"][item] = s
        show(item, s)
        if item in primary:
            pooled += eps
    if primary:
        s = describe(pooled)
        result["pooled_primary"] = s
        show("POOLED PRIMARY", s)
        print(f"O1 REGISTERED READING (pooled primary): {s['o1']['word']}")
        print(f"O3 CHAIN REGISTERED READING (pooled primary): {s['o3_chain']['word']}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1, default=str) + "\n")
    return result


# ----------------------------------------------------------------------------------------------- synthetic self-test
def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # 'fast': records visible 8 frames after the press -> V12 True; plan 'over' for half, 'moved on' for half
        # 'slow': records visible 30 frames after the press -> V12 False; all over.
        over_plan = [(20, 1), (40, 1), (60, 1), (120, 2), (160, 3)]          # card 2: extra press at 60
        move_plan = [(20, 1), (40, 1), (120, 2), (160, 3)]                  # card 2: moved on
        fast = lambda plan: (lambda f: [[pf, 0, "bottom", pf + 4] for pf, b in plan if b != 3 and pf + 8 <= f])  # noqa
        slow = lambda plan: (lambda f: [[pf, 0, "bottom", pf + 4] for pf, b in plan if b != 3 and pf + 30 <= f])  # noqa
        for s in range(12):
            pla._write_episode(root / "lab" / "F" / "on" / pla.TASK / f"seed_{s}", (2, 1),
                               move_plan if s % 4 else over_plan, fast(move_plan if s % 4 else over_plan))
            pla._write_episode(root / "lab" / "S" / "on" / pla.TASK / f"seed_{s}", (2, 1), over_plan, slow(over_plan))
        f = describe(run_episodes(f"{root / 'lab'}:F"))
        s = describe(run_episodes(f"{root / 'lab'}:S"))
        # button 2 (card 1, then the confirm button) adds one 'moved on' phase per episode
        assert f["o1"]["V12"]["visible"] == {"over": 3, "moved_on": 21, "rate": 0.125}, f["o1"]
        assert s["o1"]["V12"]["not_visible"] == {"over": 12, "moved_on": 12, "rate": 0.5}, s["o1"]
        both = describe(run_episodes(f"{root / 'lab'}:F") + run_episodes(f"{root / 'lab'}:S"))
        assert both["o1"]["word"] == "TIMING PREDICTS", both["o1"]
        # deciding press 40: bottom 40 (a 0), confirmed 44 (b 4), visible at decision 48 (c 4)
        assert both["o5"]["deciding"]["a"]["median"] == 0 and both["o5"]["deciding"]["b"]["median"] == 4, both["o5"]
        assert f["o5"]["deciding"]["c"]["median"] == 4, f["o5"]
        # chain: extra presses at 60 and 80 with the full count visible before the second one -> 'full' at j = 2
        chain_plan = [(20, 1), (40, 1), (60, 1), (80, 1), (120, 2), (160, 3)]
        for s_ in range(10):
            pla._write_episode(root / "lab" / "C" / "on" / pla.TASK / f"seed_{s_}", (2, 1), chain_plan, fast(chain_plan))
        c = describe(run_episodes(f"{root / 'lab'}:C"))
        assert c["o3_chain"]["j2plus"] == 10 and c["o3_chain"]["j2plus_full"] == 10, c["o3_chain"]
        assert c["o3_chain"]["word"] == "CHAIN MISREAD", c["o3_chain"]
        assert c["o3_share_e1_2plus_among_over"] == [10, 10], c["o3_share_e1_2plus_among_over"]
        # s / R: a 'top' 6 frames after each bottom (confirmed 8 after): deciding press 40 confirmed 44, top 46 -> s 2
        topped = lambda plan: (lambda f: [[pf, 0, "bottom", pf + 4] for pf, b in plan if b != 3 and pf + 8 <= f]  # noqa
                               + [[pf + 6, 0, "top", pf + 8] for pf, b in plan if b != 3 and pf + 10 <= f])
        for s_ in range(4):
            pla._write_episode(root / "lab" / "T" / "on" / pla.TASK / f"seed_{s_}", (2, 1), over_plan, topped(over_plan))
        t = describe(run_episodes(f"{root / 'lab'}:T"))
        assert t["t2_R"]["n_late_all"] == 4 and t["t2_R"]["R_late_all"] == 0.5 and t["t2_R"]["s_median_late"] == 2, t["t2_R"]
        flat = describe(run_episodes(f"{root / 'lab'}:S"))       # one row empty -> no reading
        assert flat["o1"]["word"].startswith("NO READING"), flat["o1"]
        assert abs(fisher_one_sided(5, 5, 5, 5) - 0.6719) < 1e-3
    print("SELFTEST OK")


def main():
    global OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--primary", nargs="*", default=[], help="FOLDER:LABEL runs of the registered reading")
    ap.add_argument("--describe", nargs="*", default=[], help="FOLDER:LABEL runs reported with the same rules")
    ap.add_argument("--out", default=str(OUT / "PRESS_TIMING_AUDIT.json"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    if not args.primary and not args.describe:
        ap.error("give --primary / --describe FOLDER:LABEL runs, or --selftest")
    main_run(args.primary, args.describe, Path(args.out))


if __name__ == "__main__":
    sys.exit(main())
