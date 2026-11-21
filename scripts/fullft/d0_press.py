"""Plan v19 D0 (11-22, Opus): zero-compute analysis of the press_button episodes already on the 5090, and the fact checks
of Insight v2 6.3 that the episodes can answer. Read-only, CPU; writes outputs/fullft/D0_PRESS.json. Descriptive: no
reading word.
Runs (FOLDER:LABEL, closed_loop/<folder>/<label>/on/press_button/seed_*): default = press_count e30 on g1 (1-50), sel
(51-100), rep (51-100, noise r2), and press_fast e20 g1 / sel (the other writer), pooled per label.
Per episode (closed_loop_stages via press_pair.stages): card_1, card_2, e1 = button-1 presses - card_1 and e2 =
button-2 presses - card_2 at the first confirm press; per registered press the pressing arm (end effector nearest the
button in x, y at registration; press_ledger_audit.analyse_episode).
Tables:
  1 over rate (e >= +1) of each count by its card value ("does it drift as the count grows")
  2 second count against the first: right / over / under cross table (also e2 among episodes with e1 = 0)
  3 which arm pressed button 1 and button 2 (majority over that button's presses); e2 by same arm vs different arms
    (with one arm for both, the record's countable code keeps counting across the two buttons: code fact, history.py)
  4 e2 among same-arm episodes split by whether the arm's code at the start of button 2 already exceeds card_2
Also printed: the distinct instructions in the training cache (does the text carry the counts?).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/d0_press.py [FOLDER:LABEL ...]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2/closed_loop"


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pp = module("press_pair", "press_pair.py")
pla = module("press_ledger_audit", "press_ledger_audit.py")
DEFAULT = ["g1:press_count_e30", "sel:press_count_e30", "rep:press_count_e30", "g1:press_fast_e20", "sel:press_fast_e20"]


def cls(e):
    return None if not isinstance(e, int) else ("right" if e == 0 else "over" if e > 0 else "under")


def main():
    runs = sys.argv[1:] or DEFAULT
    by_label = defaultdict(list)
    for item in runs:
        folder, label = item.split(":", 1)
        try:
            st = pp.stages(folder, label)
        except Exception as e:                                     # noqa: BLE001
            print(f"{item}: no stages ({type(e).__name__})")
            continue
        root = O / folder / label / "on" / "press_button"
        for seed, v in st.items():
            by_label[label].append((dict(v, seed=seed, folder=folder), root / f"seed_{seed}"))
        print(f"{item}: {len(st)} episodes")
    out = {}
    for label, eps in by_label.items():
        rows = []
        for v, d in eps:
            arm = {1: None, 2: None}
            if (d / "executed_actions.jsonl").exists():
                presses = presses_with_arm(d)
                for b in (1, 2):
                    c = Counter(p["arm"] for p in presses if p["button"] == b and p["arm"])
                    arm[b] = c.most_common(1)[0][0] if c else None
            rows.append({"seed": v["seed"], "folder": v["folder"], "card1": v.get("card_1"), "card2": v.get("card_2"),
                         "e1": v.get("n1_error"), "e2": v.get("n2_error"), "arm1": arm[1], "arm2": arm[2]})
        res = {"episodes": len(rows)}
        t1 = {}
        for k, ck, ek in ((1, "card1", "e1"), (2, "card2", "e2")):
            g = defaultdict(list)
            for r in rows:
                if isinstance(r[ek], int) and r[ck] is not None:
                    g[int(r[ck])].append(r[ek] >= 1)
            t1[f"button{k}"] = {c: [sum(x), len(x)] for c, x in sorted(g.items())}
        res["over_by_card"] = t1
        ct = Counter((cls(r["e1"]), cls(r["e2"])) for r in rows)
        res["cross_e1_e2"] = {f"{a}|{b}": n for (a, b), n in sorted(ct.items(), key=lambda x: str(x))}
        res["e2_given_e1_right"] = dict(Counter(cls(r["e2"]) for r in rows if r["e1"] == 0))
        res["arms"] = {f"{a}->{b}": n for (a, b), n in Counter((r["arm1"], r["arm2"]) for r in rows).items()}
        same = [r for r in rows if r["arm1"] and r["arm1"] == r["arm2"]]
        diff = [r for r in rows if r["arm1"] and r["arm2"] and r["arm1"] != r["arm2"]]
        res["e2_same_arm"] = dict(Counter(cls(r["e2"]) for r in same))
        res["e2_different_arms"] = dict(Counter(cls(r["e2"]) for r in diff))
        res["e1_same_arm"] = dict(Counter(cls(r["e1"]) for r in same))
        res["e1_different_arms"] = dict(Counter(cls(r["e1"]) for r in diff))
        out[label] = res
        print(f"\n== {label}: {len(rows)} episodes")
        for key in ("over_by_card", "cross_e1_e2", "e2_given_e1_right", "arms", "e1_same_arm", "e2_same_arm",
                    "e1_different_arms", "e2_different_arms"):
            print(f"  {key}: {res[key]}")
    rec = R / "outputs/memory_v2/press/dense_press_button_v1/RECORDS.json"
    if rec.exists():
        value = json.loads(rec.read_text())
        items = value if isinstance(value, list) else value.get("records") or value.get("episodes") or list(value.values())
        texts = Counter()
        for x in items if isinstance(items, list) else []:
            if isinstance(x, dict):
                t = next((x[k] for k in x if "instr" in k.lower() or k.lower() in ("text", "task_text", "prompt")), None)
                if isinstance(t, str):
                    texts[t] += 1
        print(f"\ninstructions in the training cache ({sum(texts.values())} records, {len(texts)} distinct):")
        for t, n in texts.most_common(6):
            print(f"  {n:3d} x {t}")
        out["instructions"] = dict(texts.most_common(20))
    (R / "outputs/fullft/D0_PRESS.json").write_text(json.dumps(out, indent=1) + "\n")
    print("\nwrote outputs/fullft/D0_PRESS.json")
    return 0


def presses_with_arm(d: Path):
    """Registered presses of buttons 1 / 2 with the pressing arm (nearest end effector in x, y), as the audit does."""
    rows = pla.read_jsonl(d / "executed_actions.jsonl")
    first = (rows[0].get("objects_before") or {}) if rows else {}
    after = [r.get("objects_after") or {} for r in rows]
    ee = [(r.get("ee_after") or {}) for r in rows]
    out, prev = [], {c: int(first.get(c) or 0) for c, _, _ in pla.COUNTERS}
    for i, a in enumerate(after):
        for c, name, b in pla.COUNTERS:
            v = int(a.get(c) or 0)
            for _ in range(max(0, v - prev[c])):
                bp = ((a.get(name) or {}).get("p")) or ((first.get(name) or {}).get("p"))
                best = None
                for s in pla.SIDES:
                    e = (ee[i] or {}).get(s)
                    if bp and e:
                        dd = ((e[0] - bp[0]) ** 2 + (e[1] - bp[1]) ** 2) ** 0.5
                        if best is None or dd < best[0]:
                            best = (dd, s)
                out.append({"frame": i + 1, "button": b, "arm": best[1] if best else None})
            prev[c] = max(prev[c], v)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
