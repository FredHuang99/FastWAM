"""Press ledger audit (11-16, descriptive, CPU only; episode files are read, never written).

Question: when the press model presses a button the wrong number of times, did the LEDGER it was given at that moment
hold the right count (the model misread a correct ledger), or not (the event detector missed or was late on a press)?
Facts behind it (5090, scenes 1-50): press_arprop e20 counts the first number right 28/50 (replicate 27/50), e30 only
10/50 (replicate 8/50), errors almost all over-presses by 1-4; with the ledger switched off the model never stops.

Per episode of a label (outputs/memory_v2/closed_loop/<folder>/<label>/on/press_button/seed_*):
  registered press  an increment of the simulator's counter press_cnt_1 / press_cnt_2 / press_cnt_check_button in
                    executed_actions.jsonl (objects_after; row i = frame i + 1). Only ground truth, never seen by the model.
  ledger            decisions.jsonl "ledger": the entries the model was given at each decision [frame, arm, kind,
                    confirmed]; a 'bottom' entry is the detector's press turning point (events.py, rule A).
  recorded          a registered press at frame t with a ledger 'bottom' (any arm) whose frame is within +-W (10) of t,
                    matched one-to-one in time order. missed = registered without a bottom. spurious = a bottom with no
                    registered press within W (an attempt that did not push the button far enough: done != achieved).
                    The confirm press ends the episode and never rises, so it is never recorded: reported apart.
  visible           a recorded press first appears in the ledger of the decision at frame v; delay = v - t.
  stroke            pressing arm = the arm whose end effector is nearest to that button (x, y) at t; drop = highest
                    point since its previous registered press - lowest point within +-5 frames of t; rise = highest
                    point before its next registered press (or the end) - that lowest point (the detector needs >= 0.015
                    m down and up, and 0.03 m of path since the arm's previous event).
  shallow           a button-joint dip below -0.001 that never crossed -0.005 (the press threshold): pushed, not pressed.
  phase k           k = 1: button 1 against card 1; k = 2: button 2 against card 2. In episodes that pressed button k at
                    least card_k times: T = frame of the card_k-th press; next registered press after T = 'over'
                    (button k again), 'moved on' (another button) or 'none'. For 'over': full = the frame of the first
                    decision whose ledger holds the bottoms of all card_k presses; "saw a full ledger" = full <= T_over - 16
                    (two decisions before the extra press registered); else 'missed' (one of the card_k presses never
                    recorded) or 'late' (all recorded, but visible only after T_over - 16).
                    Episodes that pressed button k fewer than card_k times and moved on: 'under' (with the spurious
                    bottoms between the first press of button k and the move, if any).
Pre-registered reading (written 11-16 14:00 BJ, before this script ran on any episode):
  per label, over-pressing phases (k = 1 and 2 pooled):
    >= 70 % saw a full ledger  -> MISREAD    (the ledger held the right count; the model pressed again anyway)
    <= 30 %                    -> RECORDING  (the ledger was short, missed or late, when the extra press began)
    otherwise                  -> BOTH
  floor: >= 10 over-pressing phases in the label, else NO READING.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_ledger_audit.py g1:press_arprop_e20 rep:press_arprop_e30_r1
  (each argument FOLDER:LABEL, FOLDER under outputs/memory_v2/closed_loop). --selftest runs the synthetic checks.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import tempfile
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"
OUT = R / "outputs/fullft/align"
TASK = "press_button"
COUNTERS = (("press_cnt_1", "button1", 1), ("press_cnt_2", "button2", 2), ("press_cnt_check_button", "check_button", 3))
SIDES = ("left", "right")
W = 10
SAW_MARGIN = 16


def read_jsonl(path: Path):
    with path.open() as f:
        return [json.loads(line) for line in f if line.strip()]


def pct(values, q):
    if not values:
        return None
    v = sorted(values)
    return v[min(len(v) - 1, max(0, int(math.ceil(q * len(v))) - 1))]


def analyse_episode(directory: Path) -> dict:
    rows = read_jsonl(directory / "executed_actions.jsonl")
    decisions = read_jsonl(directory / "decisions.jsonl")
    result = json.loads((directory / "result.json").read_text()) if (directory / "result.json").exists() else {}
    first = (rows[0].get("objects_before") or {}) if rows else {}
    after = [r.get("objects_after") or {} for r in rows]
    card = {}
    for k in (1, 2):
        name = f"card_id_{k}"
        card[k] = first.get(name) if first.get(name) is not None else next(
            (a[name] for a in after if a.get(name) is not None), None)
    # registered presses
    presses, prev = [], {c: int(first.get(c) or 0) for c, _, _ in COUNTERS}
    for i, a in enumerate(after):
        for c, _, b in COUNTERS:
            v = int(a.get(c) or 0)
            for _ in range(max(0, v - prev[c])):
                presses.append({"frame": i + 1, "button": b})
            prev[c] = max(prev[c], v)
    presses.sort(key=lambda p: (p["frame"], p["button"]))
    # end effector heights and button positions per frame (frame i + 1 = row i; frame 0 = before row 0)
    ee = [(r.get("ee_after") or {}) for r in rows]
    ee0 = rows[0].get("ee_before") if rows else None

    def ee_at(frame, side):
        src = ee0 if frame == 0 else (ee[frame - 1] if 0 < frame <= len(ee) else None)
        v = (src or {}).get(side)
        return v[:3] if v else None

    def button_p(b, frame):
        name = COUNTERS[b - 1][1]
        src = after[min(len(after) - 1, max(0, frame - 1))] if after else {}
        return ((src.get(name) or {}).get("p")) or ((first.get(name) or {}).get("p"))

    for p in presses:                                       # pressing arm: end effector nearest the button in x, y
        bp = button_p(p["button"], p["frame"])
        best = None
        for s in SIDES:
            e = ee_at(p["frame"], s)
            if bp and e:
                d = math.dist(e[:2], bp[:2])
                if best is None or d < best[0]:
                    best = (d, s)
        p["arm"] = best[1] if best else None
    for s in SIDES:                                         # strokes per arm
        mine = [p for p in presses if p["arm"] == s]
        for j, p in enumerate(mine):
            lo_f = max(0, p["frame"] - 5)
            hi_f = min(len(ee), p["frame"] + 5)
            zs = [ee_at(f, s)[2] for f in range(lo_f, hi_f + 1) if ee_at(f, s)]
            if not zs:
                continue
            zmin = min(zs)
            start = mine[j - 1]["frame"] if j else 0
            stop = mine[j + 1]["frame"] if j + 1 < len(mine) else len(ee)
            before = [ee_at(f, s)[2] for f in range(start, p["frame"] + 1) if ee_at(f, s)]
            later = [ee_at(f, s)[2] for f in range(p["frame"], stop + 1) if ee_at(f, s)]
            p["drop_m"] = round(max(before) - zmin, 4) if before else None
            p["rise_m"] = round(max(later) - zmin, 4) if later else None
    # shallow dips per button (joint below -0.001 without crossing -0.005)
    shallow = {1: 0, 2: 0, 3: 0}
    for _, name, b in COUNTERS:
        joints = [((a.get(name) or {}).get("joint")) for a in after]
        dipping, deep = False, False
        for j in joints:
            if j is None:
                continue
            if not dipping and j < -0.001:
                dipping, deep = True, j < -0.005
            elif dipping:
                deep = deep or j < -0.005
                if j > -0.001:
                    if not deep:
                        shallow[b] += 1
                    dipping = False
    # ledger: every bottom entry the model was ever given, and the first decision that showed it
    bottoms, shown = {}, []
    for d in decisions:
        keys = set()
        for e in d.get("ledger") or []:
            frame, arm, kind, confirmed = int(e[0]), int(e[1]), e[2], int(e[3])
            if kind != "bottom":
                continue
            key = (frame, arm)
            keys.add(key)
            if key not in bottoms:
                bottoms[key] = {"frame": frame, "arm": arm, "confirmed": confirmed, "visible": int(d["frame_id"])}
        shown.append((int(d["frame_id"]), keys))
    # one-to-one matching in time order (the terminal confirm press is never matched: it never rises)
    free = sorted(bottoms)
    for p in presses:
        p["bottom"] = None
        if p["button"] == 3:
            continue
        cand = [k for k in free if abs(k[0] - p["frame"]) <= W]
        if cand:
            k = min(cand, key=lambda k: (abs(k[0] - p["frame"]), k[0]))
            free.remove(k)
            p["bottom"] = list(k)
            p["delay"] = bottoms[k]["visible"] - p["frame"]
    spurious = [bottoms[k] for k in free]
    # phases
    phases = {}
    for k in (1, 2):
        mine = [p for p in presses if p["button"] == k]
        c = card.get(k)
        if c is None:
            continue
        if len(mine) >= c and c >= 1:
            T = mine[c - 1]["frame"]
            later = [p for p in presses if p["frame"] > T or (p["frame"] == T and p is not mine[c - 1] and p["button"] != k)]
            nxt = later[0] if later else None
            out = "over" if nxt is not None and nxt["button"] == k else ("moved on" if nxt is not None else "none")
            ph = {"card": c, "T": T, "outcome": out}
            if out == "over":
                need = [tuple(p["bottom"]) for p in mine[:c] if p["bottom"] is not None]
                ph["T_over"] = nxt["frame"]
                full = None
                if len(need) == c:
                    full = next((f for f, keys in shown if all(n in keys for n in need)), None)
                ph["full"] = full
                ph["saw_full"] = full is not None and full <= nxt["frame"] - SAW_MARGIN
                ph["why"] = ("saw full ledger" if ph["saw_full"] else
                             "missed" if len(need) < c else "late")
            phases[k] = ph
        elif mine or any(p["button"] != k for p in presses):
            first_k = mine[0]["frame"] if mine else None
            other = [p for p in presses if p["button"] != k and (first_k is None or p["frame"] > first_k)]
            moved = other[0]["frame"] if other else None
            sp = [s for s in spurious if first_k is not None and moved is not None and first_k - W <= s["frame"] <= moved]
            phases[k] = {"card": c, "outcome": "under" if moved is not None else "short (no move)",
                         "pressed": len(mine), "spurious_in_phase": len(sp)}
    regs = [p for p in presses if p["button"] in (1, 2)]
    return {"seed": directory.name.split("_", 1)[1], "success": result.get("success"), "card": card,
            "pressed": {k: sum(p["button"] == k for p in presses) for k in (1, 2, 3)},
            "registered": len(regs), "recorded": sum(p["bottom"] is not None for p in regs),
            "missed": [p for p in regs if p["bottom"] is None], "spurious": spurious,
            "delays": [p["delay"] for p in regs if p.get("delay") is not None],
            "strokes_recorded": [(p.get("drop_m"), p.get("rise_m")) for p in regs if p["bottom"] is not None],
            "strokes_missed": [(p.get("drop_m"), p.get("rise_m")) for p in regs if p["bottom"] is None],
            "shallow": shallow, "phases": phases, "decisions": len(decisions)}


def audit(folder: str, label: str, quiet=False) -> dict:
    root = (Path(folder) if folder.startswith("/") else O / "closed_loop" / folder) / label / "on" / TASK
    eps = []
    for d in sorted(root.glob("seed_*")):
        if d.name.split("_", 1)[1].isdigit() and (d / "result.json").exists() and (d / "decisions.jsonl").exists():
            eps.append(analyse_episode(d))
    reg = sum(e["registered"] for e in eps)
    rec = sum(e["recorded"] for e in eps)
    delays = [x for e in eps for x in e["delays"]]
    sm = [x for e in eps for x in e["strokes_missed"]]
    sr = [x for e in eps for x in e["strokes_recorded"]]
    over = [(e["seed"], k, ph) for e in eps for k, ph in e["phases"].items() if ph["outcome"] == "over"]
    saw = sum(ph["saw_full"] for _, _, ph in over)
    why = {w: sum(ph["why"] == w for _, _, ph in over) for w in ("saw full ledger", "missed", "late")}
    outcomes = {k: {} for k in (1, 2)}
    for e in eps:
        for k, ph in e["phases"].items():
            outcomes[k][ph["outcome"]] = outcomes[k].get(ph["outcome"], 0) + 1
    if len(over) < 10:
        reading = f"NO READING (floor: {len(over)} over-pressing phases < 10)"
    elif saw >= 0.70 * len(over):
        reading = "MISREAD (the ledger held the right count; the model pressed again anyway)"
    elif saw <= 0.30 * len(over):
        reading = "RECORDING (the ledger was short, missed or late, when the extra press began)"
    else:
        reading = "BOTH"

    def med(vals):
        vals = [v for v in vals if v is not None]
        return round(statistics.median(vals), 4) if vals else None
    summary = {"folder": folder, "label": label, "episodes": len(eps), "success": sum(bool(e["success"]) for e in eps),
               "registered": reg, "recorded": rec, "recall": round(rec / reg, 3) if reg else None,
               "missed": reg - rec, "spurious": sum(len(e["spurious"]) for e in eps),
               "confirm_presses": sum(e["pressed"][3] for e in eps),
               "shallow": {k: sum(e["shallow"][k] for e in eps) for k in (1, 2, 3)},
               "delay_median": med(delays), "delay_p90": pct(delays, 0.9),
               "stroke_recorded_median": [med([x[0] for x in sr]), med([x[1] for x in sr])],
               "stroke_missed_median": [med([x[0] for x in sm]), med([x[1] for x in sm])],
               "missed_rise_below_0.015": sum(1 for x in sm if x[1] is not None and x[1] < 0.015),
               "phase_outcomes": outcomes, "over": len(over), "saw_full": saw, "why": why, "reading": reading}
    if not quiet:
        print(f"== {folder}:{label}: {len(eps)} episodes, success {summary['success']}")
        print(f"   registered presses (buttons 1 + 2) {reg}, recorded in the ledger {rec} (recall {summary['recall']}), "
              f"missed {reg - rec}; spurious bottoms {summary['spurious']}; confirm presses {summary['confirm_presses']}")
        print(f"   visibility delay (frames, press -> first decision showing it) median {summary['delay_median']}, "
              f"p90 {summary['delay_p90']}; shallow dips (pushed, not pressed) per button {summary['shallow']}")
        print(f"   stroke drop / rise median (m): recorded {summary['stroke_recorded_median']}, missed "
              f"{summary['stroke_missed_median']}; missed with rise < 0.015 m: {summary['missed_rise_below_0.015']}")
        print(f"   phase outcomes: button 1 {outcomes[1]}; button 2 {outcomes[2]}")
        print(f"   over-pressing phases {len(over)}: saw a full ledger {saw}, missed {why['missed']}, late {why['late']}")
        print(f"   READING {label}: {reading}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"press_ledger_audit_{label}.json").write_text(json.dumps({"summary": summary, "episodes": eps}, indent=1))
    return summary


# ----------------------------------------------------------------------------------------------- synthetic self-test
def _write_episode(d: Path, card, plan, ledger_for):
    """plan: list of (frame, button) registered presses; ledger_for(frame) -> ledger entries at a decision."""
    d.mkdir(parents=True)
    n = max(f for f, _ in plan) + 40
    rows, cnt = [], {1: 0, 2: 0, 3: 0}
    for i in range(n):
        f = i + 1
        for pf, b in plan:
            if pf == f:
                cnt[b] += 1
        z = 0.20 - (0.03 if any(abs(f - pf) <= 2 for pf, _ in plan) else 0.0)
        after = {"press_cnt_1": cnt[1], "press_cnt_2": cnt[2], "press_cnt_check_button": cnt[3],
                 "card_id_1": card[0], "card_id_2": card[1],
                 "button1": {"p": [0.0, 0.0, 0.1], "joint": 0.0}, "button2": {"p": [0.3, 0.0, 0.1], "joint": 0.0},
                 "check_button": {"p": [0.6, 0.0, 0.1], "joint": 0.0}}
        rows.append({"objects_before": {"card_id_1": card[0], "card_id_2": card[1]} if i == 0 else {},
                     "objects_after": after, "ee_after": {"left": [0.0, 0.0, z], "right": [0.9, 0.0, 0.2]}})
    (d / "executed_actions.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    decs = [{"frame_id": f, "ledger": ledger_for(f)} for f in range(0, n, 8)]
    (d / "decisions.jsonl").write_text("\n".join(json.dumps(x) for x in decs) + "\n")
    (d / "result.json").write_text(json.dumps({"success": False}))


def selftest():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        # A: card 2; presses at 20, 40 recorded (visible 8 frames later); extra press at 80 -> saw a full ledger
        plan = [(20, 1), (40, 1), (80, 1), (120, 2), (160, 3)]
        led = lambda f: [[pf, 0, "bottom", pf + 4] for pf, b in plan if b != 3 and pf + 8 <= f]   # noqa: E731
        for s in range(10):
            _write_episode(root / "lab" / "A" / "on" / TASK / f"seed_{s}", (2, 1), plan, led)
        a = audit(str(root / "lab"), "A", quiet=True)
        assert a["registered"] == 40 and a["recorded"] == 40 and a["over"] == 10 and a["saw_full"] == 10, a
        assert a["reading"].startswith("MISREAD"), a["reading"]
        assert a["phase_outcomes"][2] == {"moved on": 10}, a["phase_outcomes"]
        # B: same presses, the second one never reaches the ledger -> missed -> RECORDING
        led_b = lambda f: [[pf, 0, "bottom", pf + 4] for pf, b in plan if b != 3 and pf != 40 and pf + 8 <= f]  # noqa
        for s in range(10):
            _write_episode(root / "lab" / "B" / "on" / TASK / f"seed_{s}", (2, 1), plan, led_b)
        b = audit(str(root / "lab"), "B", quiet=True)
        assert b["missed"] == 10 and b["why"]["missed"] == 10 and b["reading"].startswith("RECORDING"), b
        # C: recorded but visible only 30 frames late (after T_over - 16) -> late -> RECORDING
        led_c = lambda f: [[pf, 0, "bottom", pf + 4] for pf, b in plan if b != 3 and pf + 30 <= f]  # noqa: E731
        for s in range(10):
            _write_episode(root / "lab" / "C" / "on" / TASK / f"seed_{s}", (2, 1), plan, led_c)
        c = audit(str(root / "lab"), "C", quiet=True)
        assert c["why"]["late"] == 10 and c["reading"].startswith("RECORDING"), c
        # D: a spurious bottom (no registered press) at 60 and card 3 with only 2 presses before moving on -> under
        plan_d = [(20, 1), (40, 1), (120, 2), (160, 3)]
        led_d = lambda f: [[pf, 0, "bottom", pf + 4] for pf in (20, 40, 60) if pf + 8 <= f]  # noqa: E731
        for s in range(3):
            _write_episode(root / "lab" / "D" / "on" / TASK / f"seed_{s}", (3, 1), plan_d, led_d)
        d = audit(str(root / "lab"), "D", quiet=True)
        assert d["spurious"] == 3 and d["phase_outcomes"][1] == {"under": 3}, d
        assert d["reading"].startswith("NO READING"), d["reading"]
    print("SELFTEST OK")


def main():
    global OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("labels", nargs="*", help="FOLDER:LABEL, FOLDER under outputs/memory_v2/closed_loop")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        OUT = Path(tempfile.mkdtemp())
        selftest()
        return
    if not args.labels:
        ap.error("give FOLDER:LABEL arguments or --selftest")
    for item in args.labels:
        folder, label = item.split(":", 1)
        audit(folder, label)


if __name__ == "__main__":
    sys.exit(main())
