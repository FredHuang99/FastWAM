"""Plan v18 Z1 verdict on the 5090 (registered 11-21 15:10 BJ by Opus; the user approved Z1 at 14:21; written before any
Z1 episode exists). Read-only. Reading method of plan v18 (effect size with a paired-bootstrap 95 % CI against the
smallest effect that matters; three outcomes plus a pre-set extension).

After Z0 (perfect, instant press record: TIMING EXPLAINS PART, over-press rate 0.49 -> 0.34) two explanations remain
for the rest: (a) COMMITMENT: the chunk being executed when the press lands already carries the next descent (open-loop
inertia; exec4 shortened chains 13 -> 5), so the record comes in time but no decision reads it before the arm moves;
(b) READING: the policy reads the complete, timely record and presses again anyway (Z0's chain: 96 of 97 later extra
presses with the full count in the ledger). Interventions, all with MWAM_LEDGER=oracle (true counters, zero delay):
  Z0   closed_loop/tim  press_count_e30_oracle          (exists; decisions every 8 targets)
  Z1   closed_loop/tim  press_count_e30_oracle_replan   --replan replan: the policy also re-decides AT the observation
                                                         whose counter first shows a press, the press in its ledger
  Z1b  closed_loop/tim  press_count_e30_oracle_blind    --replan blind: the same re-decision with that press hidden
                                                         (visible from the next regular decision)
Press scenes 1-100, default noise, paired by scene. Metric: first-button over-press o = 1 if e1 >= +1.
MAIN (Z1 against Z0): D1 = rate(Z1) - rate(Z0), 95 % CI (paired bootstrap, 10,000, seed 0); SESOI1 = -0.5 x rate(Z0).
  CI upper < 0 and D1 <= SESOI1 -> PRESS RE-DECISION >= HALF (of what Z0 left)
  CI upper < 0 and D1 >  SESOI1 -> PRESS RE-DECISION PART
  CI lower > SESOI1             -> PRESS RE-DECISION < HALF (the rest is mostly reading: (b))
  otherwise                     -> UNCERTAIN: pre-set extension = Z0 and Z1 again with MWAM_NOISE_SALT=r2 on 1-100
                                   (closed_loop/tim2), the same rule on 200 pairs (z1_verdict.py --extended)
ATTRIBUTION (Z1 against Z1b; read only when MAIN is >= HALF or PART): D2 = rate(Z1) - rate(Z1b); SESOI2 = 0.5 x D1.
  CI upper < 0 and D2 <= SESOI2 -> THE RECORD CARRIES IT (re-deciding helps because the fresh press is read: the
                                   decision wait, i.e. timing, not inertia)
  CI lower > SESOI2             -> RE-DECIDING CARRIES IT (breaking the old chunk helps, with or without the record:
                                   commitment / inertia, explanation (a))
  otherwise                     -> UNCERTAIN
Floor: >= 95 pairs per comparison. Manipulation check (Z1): >= 90 % of the registered presses of buttons 1 / 2 have a
decision at the very frame the counter shows them (decisions.jsonl), else VOID.
Reported with the same rule, not the reading: mean extra presses; success; Z1 / Z1b against the baseline (g1 + sel);
the O3 chain share of each run (press_timing_audit).
Meaning for the decomposition: write delay = Z0 vs baseline; the press re-decision = Z1 vs Z0, split by Z1b into
commitment (re-deciding alone) and decision wait (the record read at once); reading = what Z1 leaves.
Expectation (subjective, before any run): PRESS RE-DECISION < HALF 0.45, PART 0.4, >= HALF 0.15.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/z1_verdict.py [--extended]   Writes outputs/fullft/Z1_VERDICT.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("oracle_verdict", HERE / "oracle_verdict.py")
ov = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ov)
pla = ov.pla


def rate(ps, i):
    return sum(p[i] >= 1 for p in ps) / len(ps)


def compare(new, ref, sesoi_of, words, name):
    seeds, pairs = ov.paired(new, ref)
    out = {"pairs": len(pairs)}
    if len(pairs) < 95:
        out["word"] = f"WAIT / NO READING ({len(pairs)} pairs < 95)"
        return out
    dfun = lambda ps: rate(ps, 0) - rate(ps, 1)                                    # noqa: E731
    d, (lo, hi) = dfun(pairs), ov.boot_ci(pairs, dfun)
    sesoi = sesoi_of(rate(pairs, 1), d)
    if hi < 0 and d <= sesoi:
        w = words[0]
    elif hi < 0 and words[1]:
        w = words[1]
    elif lo > sesoi:
        w = words[2]
    else:
        w = "UNCERTAIN"
    ext = lambda ps, i: sum(max(p[i], 0) for p in ps) / len(ps)                    # noqa: E731
    out.update(rate_ref=round(rate(pairs, 1), 3), rate_new=round(rate(pairs, 0), 3), D=round(d, 3),
               ci=[round(lo, 3), round(hi, 3)], sesoi=round(sesoi, 3), word=w,
               extra_ref=round(ext(pairs, 1), 3), extra_new=round(ext(pairs, 0), 3))
    print(f"{name}: {out}")
    return out


def manipulation(folder, label):
    root = ov.pp.O / "closed_loop" / folder / label / "on" / "press_button"
    hit = tot = 0
    for d in sorted(root.glob("seed_*")):
        if not d.name.split("_", 1)[1].isdigit() or not (d / "result.json").exists():
            continue
        rows = [json.loads(x) for x in (d / "executed_actions.jsonl").read_text().splitlines() if x.strip()]
        dec = {json.loads(x)["frame_id"] for x in (d / "decisions.jsonl").read_text().splitlines() if x.strip()}
        for i, r in enumerate(rows):
            a, b = r.get("objects_after") or {}, r.get("objects_before") or {}
            for c in ("press_cnt_1", "press_cnt_2"):
                if int(a.get(c) or 0) > int(b.get(c) or 0):
                    tot += 1
                    hit += (i + 1) in dec
    return {"presses": tot, "decided_at_press": hit, "share": round(hit / tot, 3) if tot else None,
            "passed": bool(tot) and hit / tot >= 0.9}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extended", action="store_true")
    args = ap.parse_args()
    z0 = ov.merged(("tim", "press_count_e30_oracle"))
    z1 = ov.merged(("tim", "press_count_e30_oracle_replan"))
    z1b = ov.merged(("tim", "press_count_e30_oracle_blind"))
    base = ov.merged(("g1", "press_count_e30"), ("sel", "press_count_e30"))
    res = {}
    res["main"] = compare(z1, z0, lambda r, d: -0.5 * r,
                          ("PRESS RE-DECISION >= HALF", "PRESS RE-DECISION PART", "PRESS RE-DECISION < HALF"), "MAIN Z1 vs Z0")
    if args.extended:
        z0b = {**{f"a{k}": v for k, v in z0.items()}, **{f"b{k}": v for k, v in ov.merged(("tim2", "press_count_e30_oracle")).items()}}
        z1x = {**{f"a{k}": v for k, v in z1.items()}, **{f"b{k}": v for k, v in ov.merged(("tim2", "press_count_e30_oracle_replan")).items()}}
        res["main_extended"] = compare(z1x, z0b, lambda r, d: -0.5 * r,
                                       ("PRESS RE-DECISION >= HALF", "PRESS RE-DECISION PART", "PRESS RE-DECISION < HALF"), "MAIN extended")
    main_word = (res.get("main_extended") or res["main"])["word"]
    if main_word in ("PRESS RE-DECISION >= HALF", "PRESS RE-DECISION PART"):
        d1 = (res.get("main_extended") or res["main"])["D"]
        res["attribution"] = compare(z1, z1b, lambda r, d: 0.5 * d1,
                                     ("THE RECORD CARRIES IT", None, "RE-DECIDING CARRIES IT"), "ATTRIBUTION Z1 vs Z1b")
    else:
        res["attribution"] = {"word": f"not read (MAIN {main_word})"}
    for name, run in (("z1_vs_base", z1), ("z1b_vs_base", z1b), ("z0_vs_base", z0)):
        res[name] = compare(run, base, lambda r, d: -0.5 * r, ("REMOVES >= HALF", "REMOVES PART", "REMOVES < HALF"), name)
    res["success"] = {k: sum(bool(v.get("success")) for v in run.values()) for k, run in
                      (("base", base), ("z0", z0), ("z1", z1), ("z1b", z1b))}
    try:
        res["manipulation"] = manipulation("tim", "press_count_e30_oracle_replan")
    except Exception as e:                                  # noqa: BLE001
        res["manipulation"] = {"error": str(e), "passed": None}
    final = main_word
    if res["manipulation"].get("passed") is False:
        final = f"VOID (manipulation check {res['manipulation']}; word was {main_word})"
    res["Z1"] = final
    res["Z1_ATTRIBUTION"] = res["attribution"]["word"]
    print(f"manipulation check: {res['manipulation']}")
    print(f"success: {res['success']}")
    print(f"Z1 MAIN: {final}\nZ1 ATTRIBUTION: {res['Z1_ATTRIBUTION']}")
    (ov.F / "Z1_VERDICT.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
