"""Plan v17 T2b (REPLAN) verdict on the 5090 (registered 11-20 22:00 BJ by Opus, from the Fable review of plan v16,
section 2.2, taken over in full by the user at 20:47; written before any T2b episode exists). Read-only.

Question: does the over-pressing go away when the policy re-decides as soon as a press is confirmed, and is it the
READ of the new record that helps (not merely re-deciding more often)?
Model press_count e30 (the T1 / T2 model), press scenes 1-50, default noise, 5090 GPU1; baseline = the existing
closed_loop/g1 run press_count_e30 (same scenes, noise and machine). New runs (closed_loop/tim, memory_v2.online
--execute 8 --replan MODE; the simulator executes one target per RPC, the model decides every 8 targets and, in both
arms, also when the detector confirms a new press; the unexecuted rest of the chunk is dropped):
  press_count_e30_replan  the re-decision reads the ledger as usual (the triggering press is in it)
  press_count_e30_blind   the same re-decision, but entries confirmed after the previous decision are hidden from it
                          (visible again at the next regular decision)
Metric as T1: first count error e1 (export_stages n1_error); over: e1 >= +1; under: e1 <= -1; pairs = same scene;
sign test on the discordant pairs.
Registered reading (Fable 2.2, verbatim in substance):
  MAIN (replan against the baseline)
    over(replan) <= over(base) - 8 with p < 0.05, and under(replan) - under(base) <= 4  -> REPLAN HELPS
    |over(replan) - over(base)| <= 4                                                   -> REPLAN NO EFFECT
    over(replan) <= over(base) - 8 and under(replan) - under(base) > 4                 -> REPLAN FLIPS
    otherwise                                                                          -> PARTIAL
  ATTRIBUTION (replan against blind, same scenes)
    over(replan) <= over(blind) - 8 with p < 0.05  -> READ IS THE CAUSE
    |over(replan) - over(blind)| <= 4              -> REPLAN ITSELF
    otherwise                                      -> UNDECIDED
  Floor: each arm >= 48 of 50 finished, else NO READING. Manipulation check: the median frames from a press to the
  first decision whose ledger shows it (press_ledger_audit) must be LOWER in the replan arm than in the baseline,
  else MAIN and ATTRIBUTION are VOID (the re-decision did not make the record readable earlier).
  Meaning (Fable 2.2): HELPS + READ IS THE CAUSE -> the strongest test-time evidence for the thesis, and a training-
  free fix; NO EFFECT -> the thesis' explanation of the existing over-presses is refuted; HELPS + REPLAN ITSELF -> an
  execution problem, not memory freshness (thesis weakened); FLIPS -> the model carries a learned "one more press"
  (same meaning as T1's early side).
  Gate G4b (plan v17): REPLAN NO EFFECT with the manipulation check passed -> W1 is not trained and S1 not done (switch
  to the backup thesis); REPLAN HELPS -> W1 trains (its reference becomes T2b).
Reported only: successes; model decisions and re-decisions per episode; the joint jump at re-decisions (radians, from
replan.jsonl); the residual over-pressing phases by press_ledger_audit class; the press_timing_audit tables.
Written expectation (subjective, before any run): REPLAN HELPS 0.45 (of which READ IS THE CAUSE 0.6), NO EFFECT 0.3.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/replan_verdict.py   Writes outputs/fullft/REPLAN_VERDICT.json.
"""
from __future__ import annotations

import importlib.util
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pp = module("press_pair", "press_pair.py")
pla = module("press_ledger_audit", "press_ledger_audit.py")
F = pp.R / "outputs/fullft"
BASE = ("g1", "press_count_e30")
ARMS = {"replan": ("tim", "press_count_e30_replan"), "blind": ("tim", "press_count_e30_blind")}


def kind(e):
    return None if not isinstance(e, int) else "over" if e >= 1 else "under" if e <= -1 else "right"


def paired(a: dict, b: dict, side: str) -> dict:
    common = sorted(set(a) & set(b))
    only_a = sum(kind(a[s].get("n1_error")) == side and kind(b[s].get("n1_error")) != side for s in common)
    only_b = sum(kind(b[s].get("n1_error")) == side and kind(a[s].get("n1_error")) != side for s in common)
    na = sum(kind(a[s].get("n1_error")) == side for s in common)
    nb = sum(kind(b[s].get("n1_error")) == side for s in common)
    return {"pairs": len(common), "a": na, "b": nb, "diff": na - nb, "only_a": only_a, "only_b": only_b,
            "p": pp.sign_p(only_a, only_b)}


def episodes_info(folder, label):
    root = pp.O / "closed_loop" / folder / label / "on" / "press_button"
    dec, rep, jumps = [], [], []
    for d in sorted(root.glob("seed_*")):
        if not d.name.split("_", 1)[1].isdigit() or not (d / "result.json").exists():
            continue
        r = json.loads((d / "result.json").read_text())
        dec.append(r.get("decisions"))
        rep.append(r.get("replans", 0))
        if (d / "replan.jsonl").exists():
            jumps += [json.loads(x).get("joint_jump_rad") for x in (d / "replan.jsonl").read_text().splitlines() if x.strip()]
    jumps = [j for j in jumps if j is not None]
    mean = lambda v: round(sum(v) / len(v), 2) if v else None                               # noqa: E731
    return {"decisions_mean": mean([x for x in dec if x is not None]), "replans_mean": mean(rep),
            "joint_jump_median": round(statistics.median(jumps), 4) if jumps else None,
            "joint_jump_p90": pla.pct(jumps, 0.9)}


def main():
    base = pp.stages(*BASE)
    st, out = {}, {"baseline": f"{BASE[0]}:{BASE[1]}", "arms": {}}
    for k, (folder, label) in ARMS.items():
        try:
            st[k] = pp.stages(folder, label)
        except Exception:                                       # noqa: BLE001  (arm not there yet)
            st[k] = {}
        out["arms"][k] = {"numbers": pp.numbers(st[k]) if st[k] else {"n": 0},
                          **(episodes_info(folder, label) if st[k] else {})}
        print(f"{k:7s} {label}: {out['arms'][k]}")
    out["base_numbers"] = pp.numbers(base)
    print(f"base    {BASE[1]}: {out['base_numbers']}")
    audits = {}
    for name, (folder, label) in [("base", BASE)] + [(k, v) for k, v in ARMS.items() if st[k]]:
        try:
            audits[name] = pla.audit(folder, label, quiet=True)
        except Exception as e:                                   # noqa: BLE001
            audits[name] = {"error": str(e)}
    out["audits"] = {k: {x: v.get(x) for x in ("delay_median", "delay_p90", "over", "why", "recall", "success", "error")}
                     for k, v in audits.items()}
    ready = {k: len(st[k]) >= 48 for k in ARMS}
    if not ready["replan"]:                 # fewer than 48: still running, or (after the chain) below the floor
        main_word = f"WAIT / NO READING ({len(st['replan'])} of 50 finished; floor 48)"
    else:
        o, u = paired(st["replan"], base, "over"), paired(st["replan"], base, "under")
        out["main_over"], out["main_under"] = o, u
        if o["diff"] <= -8 and o["p"] < 0.05 and u["diff"] <= 4:
            main_word = "REPLAN HELPS"
        elif abs(o["diff"]) <= 4:
            main_word = "REPLAN NO EFFECT"
        elif o["diff"] <= -8 and u["diff"] > 4:
            main_word = "REPLAN FLIPS"
        else:
            main_word = "PARTIAL"
    if not (ready["replan"] and ready["blind"]):
        attr_word = f"WAIT / NO READING (replan {len(st['replan'])}, blind {len(st['blind'])} of 50; floor 48)"
    else:
        a = paired(st["replan"], st["blind"], "over")
        out["attribution_over"] = a
        attr_word = ("READ IS THE CAUSE" if a["diff"] <= -8 and a["p"] < 0.05 else
                     "REPLAN ITSELF" if abs(a["diff"]) <= 4 else "UNDECIDED")
    check = None
    db, dr = audits.get("base", {}).get("delay_median"), audits.get("replan", {}).get("delay_median")
    if db is not None and dr is not None:
        check = dr < db
        out["manipulation_check"] = {"base_delay_median": db, "replan_delay_median": dr, "passed": check}
        if not check:
            main_word = f"VOID (manipulation check: delay {dr} not below {db}; registered word was {main_word})"
            attr_word = f"VOID ({attr_word})"
    out.update(MAIN=main_word, ATTRIBUTION=attr_word)
    print(f"MAIN over / under: {out.get('main_over')} / {out.get('main_under')}")
    print(f"ATTRIBUTION over: {out.get('attribution_over')}")
    print(f"manipulation check: {out.get('manipulation_check')}")
    print(f"T2b MAIN: {main_word}\nT2b ATTRIBUTION: {attr_word}")
    (F / "REPLAN_VERDICT.json").write_text(json.dumps(out, indent=1, default=str) + "\n")


if __name__ == "__main__":
    main()
