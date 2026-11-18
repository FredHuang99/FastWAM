"""Plan v13 E1 STRESS verdict (registered by Fable 11-17 in plan v13 section 3, approved by the user 15:40; this script
written 11-17 19:30 BJ before any E1 episode ran). Read-only.

Runs (A40, closed_loop/e1): for MODEL in {ar_2task_e30 (AR), ar2_prop_e30 (ledger)} x INJECT in {pause 64, fidget 64,
airgrasp 32} x ARM in {vis (history: the injected frames are shown), hid (hidden)}: label <MODEL>_e1<INJECT>_<ARM>,
scenes 1-50 of the task. One injection per episode, triggered by the robot's own events (fastwam/fullft/inject.py).
A pair = the same scene in the vis and hid arm of the same model and injection.
  valid pair: both episodes finished, both injected exactly once, and in both: object displacement < 1 cm, no task
              counter changed, the active arm back within 0.05 rad (implementation detail added 19:30: the card says
              "the arm returns to its pose before the injection" without a number)
  Delta = successes(vis) - successes(hid) over valid pairs; p = two-sided sign test on the discordant pairs
Registered reading (verbatim in meaning):
  structural  ledger model, pause and fidget, vis arm: no ledger entry from the injected frames in >= 95 % of the
              valid episodes -> "immune by construction" (reported for airgrasp too: its entries are the false events)
  behaviour   ledger model, pause and fidget: both Delta >= -5 -> IMMUNE; either Delta <= -8 with p < 0.05 ->
              WINDOW-FRAGILE; otherwise undetermined
  airgrasp    ledger model: Delta <= -8 with p < 0.05 -> FOOLED; Delta >= -5 -> NOT FOOLED; otherwise undetermined
  AR          reported only
  floors      >= 45 valid pairs; the ledger model's hid arm >= 45/50 successes; the AR's hid arm >= 20/50 (else a
              cell gets no verdict)
  conditional E1b (body-verified writes) after FOOLED; E1c (recent window by motion) after WINDOW-FRAGILE.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e1_verdict.py --task swap_blocks
Writes outputs/fullft/E1_VERDICT_<task>.json.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
MODELS = {"AR": "ar_2task_e30", "ledger": "ar2_prop_e30"}
INJECT = {"pause": 64, "fidget": 64, "airgrasp": 32}
DISP, RETURN = 0.01, 0.05


def sign_p(a: int, b: int) -> float:
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def episode(folder: Path, label: str, task: str, seed: int):
    d = folder / label / "on" / task / f"seed_{seed}"
    res = d / "result.json"
    if not res.exists():
        return None
    r = json.loads(res.read_text())
    st = [json.loads(x) for x in (d / "stress.jsonl").read_text().splitlines() if x.strip()] if (d / "stress.jsonl").exists() else []
    rows = [json.loads(x) for x in (d / "decisions.jsonl").read_text().splitlines() if x.strip()] if (d / "decisions.jsonl").exists() else []
    out = {"success": bool(r.get("success")), "injected": len(st), "stress": st[0] if st else None, "entries_injected": None}
    if st:
        s = st[0]
        out["valid"] = (len(st) == 1 and s.get("displacement_m", 1) < DISP and not s.get("counters_changed")
                        and s.get("arm_return_rad", 1) <= RETURN)
        if s.get("arm") == "history":         # policy timeline: injected frames F .. F + k - 1 (one injection)
            lo, hi = int(s["frame"]), int(s["frame"]) + int(s["k"]) - 1
            seen = {(int(e[0]), int(e[1]), e[2]) for x in rows for e in (x.get("ledger") or []) if lo <= int(e[0]) <= hi}
            out["entries_injected"] = len(seen)
    else:
        out["valid"] = False
    return out


def seeds_of(task: str, n: int):
    """The first n scenes of the registered bank, in the order memory_v2.online.load_scenes runs them (--limit n)."""
    bank = O / f"scenes_seed42_n100_{task}"
    rows = []
    for f in sorted(bank.glob("*.json")) if bank.is_dir() else []:
        value = json.loads(f.read_text())
        scenes = value.get("scenes") if isinstance(value, dict) else value
        rows += [s for s in scenes or [] if s.get("task") == task]
    if not rows:
        return None
    uniq = {int(s["seed"]): s for s in rows}
    order = sorted(uniq.values(), key=lambda s: (s.get("ordinal", 0), int(s["seed"])))
    return [int(s["seed"]) for s in order[:n]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", default="swap_blocks")
    ap.add_argument("--folder", default=str(O / "e1"))
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--out", default="", help="11-18: verdict JSON path (default outputs/fullft/E1_VERDICT_<task>.json)")
    args = ap.parse_args()
    folder = Path(args.folder)
    seeds = seeds_of(args.task, args.n)
    if seeds is None:                         # fall back to the seeds present in the folders
        found = set()
        for m in MODELS.values():
            for k in INJECT:
                for arm in ("vis", "hid"):
                    found |= {int(p.name[5:]) for p in (folder / f"{m}_e1{k}_{arm}" / "on" / args.task).glob("seed_*")
                              if p.name[5:].isdigit()}
        seeds = sorted(found)[:args.n]
    report, cells = {}, {}
    print(f"E1 {args.task}: {len(seeds)} scenes; folder {folder}")
    print("model   inject    | valid | vis succ | hid succ | Delta | vis-only hid-only | p      | entries in injected frames (vis)")
    for mname, model in MODELS.items():
        for inj in INJECT:
            vis = {s: episode(folder, f"{model}_e1{inj}_vis", args.task, s) for s in seeds}
            hid = {s: episode(folder, f"{model}_e1{inj}_hid", args.task, s) for s in seeds}
            pairs = [s for s in seeds if vis[s] and hid[s] and vis[s]["valid"] and hid[s]["valid"]]
            a = sum(vis[s]["success"] and not hid[s]["success"] for s in pairs)
            b = sum(hid[s]["success"] and not vis[s]["success"] for s in pairs)
            delta, p = a - b, sign_p(a, b)
            hid_succ = sum(bool(hid[s] and hid[s]["success"]) for s in seeds)
            ent = [vis[s]["entries_injected"] for s in pairs if vis[s]["entries_injected"] is not None]
            zero_share = (sum(e == 0 for e in ent) / len(ent)) if ent else float("nan")
            cells[(mname, inj)] = {"valid_pairs": len(pairs), "vis_success": sum(vis[s]["success"] for s in pairs),
                                   "hid_success_all": hid_succ, "delta": delta, "vis_only": a, "hid_only": b, "p": p,
                                   "zero_entry_share": zero_share, "mean_entries": (sum(ent) / len(ent)) if ent else None,
                                   "finished": [sum(1 for s in seeds if vis[s]), sum(1 for s in seeds if hid[s])]}
            c = cells[(mname, inj)]
            print(f"{mname:7s} {inj:9s} | {len(pairs):5d} | {c['vis_success']:8d} | {hid_succ:8d} | {delta:+5d} | "
                  f"{a:8d} {b:8d} | {p:.4f} | zero-entry share {zero_share:.2f}, mean {c['mean_entries']}")
    def floor(mname, inj):
        c = cells[(mname, inj)]
        need = 45 if mname == "ledger" else 20
        return c["valid_pairs"] >= 45 and c["hid_success_all"] >= need
    led = {k: cells[("ledger", k)] for k in INJECT}
    if floor("ledger", "pause") and floor("ledger", "fidget"):
        if all(led[k]["delta"] >= -5 for k in ("pause", "fidget")):
            behaviour = "IMMUNE"
        elif any(led[k]["delta"] <= -8 and led[k]["p"] < 0.05 for k in ("pause", "fidget")):
            behaviour = "WINDOW-FRAGILE"
        else:
            behaviour = "undetermined"
    else:
        behaviour = "NO VERDICT (floor)"
    if floor("ledger", "airgrasp"):
        g = led["airgrasp"]
        air = "FOOLED" if (g["delta"] <= -8 and g["p"] < 0.05) else ("NOT FOOLED" if g["delta"] >= -5 else "undetermined")
    else:
        air = "NO VERDICT (floor)"
    zs = [led[k]["zero_entry_share"] for k in ("pause", "fidget")]
    structural = ("IMMUNE BY CONSTRUCTION" if all(z == z and z >= 0.95 for z in zs) else
                  ("NO VERDICT" if any(z != z for z in zs) else "NOT IMMUNE BY CONSTRUCTION"))
    print(f"STRUCTURAL (ledger, pause + fidget, vis): {structural}")
    print(f"BEHAVIOUR (ledger, pause + fidget): {behaviour}")
    print(f"AIRGRASP (ledger): {air}")
    print("AR: reported only (rows above)")
    report = {"task": args.task, "scenes": len(seeds), "cells": {f"{m}|{k}": v for (m, k), v in cells.items()},
              "structural": structural, "behaviour": behaviour, "airgrasp": air}
    (Path(args.out) if args.out else F / f"E1_VERDICT_{args.task}.json").write_text(json.dumps(report, indent=1) + "\n")


if __name__ == "__main__":
    main()
