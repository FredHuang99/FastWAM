"""Plan v15 E22 DOSE verdicts and Z6 (registered by Fable 11-19 noon in plan v15 section 3; user 13:21 "按照 fable 的
计划去执行"; this script written 11-19 14:50 BJ, before any E22 closed-loop result exists). Read-only. A40.

E22a pause length. Hypothesis: a time-indexed memory starts to err once the pause takes the share of its 32 slots that
hurt in Bo An's study (~0.3-0.4) or more; the event-indexed ledger does not.
  clock ar2_clock e30: swap 64 (E5, closed_loop/e5), 256, 1024; put 64 (E5b, closed_loop/e5), 256
  ledger ar2_prop e30: swap 64 (E1, closed_loop/e1), 1024; put 64 (E1), 256
  new cells: closed_loop/e22, labels <model>_p<L>_vis / _hid (E1's injection point and validity; vis / hid paired)
  Registered reading, per task and level (Delta = vis - hid on valid pairs):
    clock Delta <= -8/50 with p < 0.05 AND the task's ledger Delta at its largest level >= -5/50 -> INDEX MATTERS AT L
      (the smallest such L is reported);
    clock Delta >= -5/50 at every level of the task -> NO DOSE EFFECT;
    ledger Delta <= -8/50 with p < 0.05 -> LEDGER ALSO HURT (no INDEX MATTERS at that level); otherwise PARTIAL.
    Floors per cell: valid pairs >= 45; hidden arm >= 45/50 successes.
  Reported only: the clock's slot share in the pause at the first decision after it (vis), failure classes.
E22b token budget (swap 1-50, no stress; MWAM_BUDGET=K): clock K uniform samples, ledger the last K entries, K = 16, 8,
  4 (closed_loop/e22, labels <model>_b<K>); K = 32 = as trained (clock: closed_loop/e5 ar2_clock_e30; ledger:
  closed_loop/g1 ar2_prop_e30). B = the smallest budget from which every larger budget still has >= 45/50.
  Ledger B <= clock B / 2 (or the clock is < 45/50 at 16 and below while the ledger reaches 45 there) -> EVENT INDEX
  CHEAPER; equal B -> SAME; otherwise the curve only. Appendix only (both models see an untrained input).
Z6 (--occupancy): the clock's slot share in the pause for the existing 64-frame cells (swap from E5, put from E5b).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e22_verdict.py --part a|b|occupancy
Writes outputs/fullft/E22A_VERDICT.json / E22B_VERDICT.json / Z6_OCCUPANCY.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


e1 = module("e1_verdict", "e1_verdict.py")
e5 = module("e5_verdict", "e5_verdict.py")
e5b = module("e5b_verdict", "e5b_verdict.py")
CLOCK, LEDGER = "ar2_clock_e30", "ar2_prop_e30"
# 11-28 (Opus; the code audit): the A100's 25 hidden-arm cards of the 256 / 1024 cells ran with
# --stress event:pause:L:history (the VISIBLE arm) -- their "_hid" cells are a second visible run, not hidden. The hidden
# arm is re-run on the A100 as "_hid2" with :hidden (A100-E22h-*); --hid-suffix hid2 reads those, --out writes a new
# file. Default "hid" / E22A_VERDICT.json: unchanged (the registered reading itself is not changed).
HID = "hid"
OUT_A = "E22A_VERDICT.json"
TASKS = ("swap_blocks", "put_back_block")
LEVELS = {(CLOCK, "swap_blocks"): (64, 256, 1024), (CLOCK, "put_back_block"): (64, 256),
          (LEDGER, "swap_blocks"): (64, 1024), (LEDGER, "put_back_block"): (64, 256)}


def where(model, level):
    """(folder, vis label, hid label) of a pause cell."""
    if level == 64:
        folder = O / ("e5" if model == CLOCK else "e1")
        return folder, f"{model}_e1pause_vis", f"{model}_e1pause_hid"
    return O / "e22", f"{model}_p{level}_vis", f"{model}_p{level}_{HID}"


def classes(folder, label, task, seeds):
    if task == "swap_blocks":
        ep = e5.finished(folder, label, task, seeds)
        return dict(Counter(k or "unclassified" for ok, k in ep.values() if not ok))
    out = Counter()
    for s in seeds:
        d = folder / label / "on" / task / f"seed_{s}"
        if (d / "result.json").exists():
            c = e5b.put_class(d)
            if c != "success":
                out[c] += 1
    return dict(out)


def pause_cell(model, task, level, seeds):
    folder, lv, lh = where(model, level)
    vis = {s: e1.episode(folder, lv, task, s) for s in seeds}
    hid = {s: e1.episode(folder, lh, task, s) for s in seeds}
    pairs = [s for s in seeds if vis[s] and hid[s] and vis[s]["valid"] and hid[s]["valid"]]
    a = sum(vis[s]["success"] and not hid[s]["success"] for s in pairs)
    b = sum(hid[s]["success"] and not vis[s]["success"] for s in pairs)
    hid_succ = sum(bool(hid[s] and hid[s]["success"]) for s in seeds)
    shares = [x for x in (e5b.clock_share(folder / lv / "on" / task / f"seed_{s}") for s in seeds) if x is not None]
    cell = {"model": model, "task": task, "level": level, "finished_vis": sum(1 for s in seeds if vis[s]),
            "finished_hid": sum(1 for s in seeds if hid[s]), "valid_pairs": len(pairs), "vis_only": a, "hid_only": b,
            "delta": a - b, "p": e1.sign_p(a, b), "hidden_success": hid_succ,
            "share_mean": (sum(shares) / len(shares)) if shares else None,
            "classes_vis": classes(folder, lv, task, seeds), "classes_hid": classes(folder, lh, task, seeds)}
    if cell["finished_vis"] < 48 or cell["finished_hid"] < 48:
        cell["state"] = "WAIT"
    elif len(pairs) < 45 or hid_succ < 45:
        cell["state"] = "FLOOR NOT MET"
    elif cell["delta"] <= -8 and cell["p"] < 0.05:
        cell["state"] = "HURT"
    elif cell["delta"] >= -5:
        cell["state"] = "NOT HURT"
    else:
        cell["state"] = "BETWEEN"
    share = f"{cell['share_mean']:.2f}" if cell["share_mean"] is not None else "-"
    print(f"{model:14s} {task:15s} pause {level:4d}: valid pairs {len(pairs)}, vis-only {a}, hid-only {b}, "
          f"Delta {a - b:+d}, p {cell['p']:.4f}, hidden {hid_succ}/50, slot share {share} -> {cell['state']}")
    return cell


def part_a():
    out = {}
    for task in TASKS:
        seeds = e1.seeds_of(task, 50)
        clock = [pause_cell(CLOCK, task, L, seeds) for L in LEVELS[(CLOCK, task)]]
        ledger = [pause_cell(LEDGER, task, L, seeds) for L in LEVELS[(LEDGER, task)]]
        top = ledger[-1]
        if any(c["state"] == "WAIT" for c in clock + [top]):
            word = "WAIT"
        else:
            hurt = [c["level"] for c in clock if c["state"] == "HURT"]
            if top["state"] == "HURT":
                word = f"LEDGER ALSO HURT (at {top['level']}; clock hurt at {hurt or 'no level'}, descriptive)"
            elif hurt and top["state"] == "NOT HURT":
                word = f"INDEX MATTERS AT {min(hurt)}"
            elif all(c["state"] == "NOT HURT" for c in clock):
                word = "NO DOSE EFFECT"
            else:
                word = "PARTIAL"
        out[task] = {"verdict": word, "clock": clock, "ledger": ledger}
        print(f"E22a {task}: {word}")
    out["hidden_cells"] = f"closed_loop/e22 *_{HID} (256 / 1024 levels)"
    (F / OUT_A).write_text(json.dumps(out, indent=1) + "\n")


def budget_curve(model, seeds):
    curve = {}
    for k in (32, 16, 8, 4):
        if k == 32:
            folder, label = (O / "e5", CLOCK) if model == CLOCK else (O / "g1", LEDGER)
        else:
            folder, label = O / "e22", f"{model}_b{k}"
        ep = e5.finished(folder, label, "swap_blocks", seeds)
        curve[k] = {"finished": len(ep), "success": sum(ok for ok, _ in ep.values()),
                    "failures": dict(Counter(c or "unclassified" for ok, c in ep.values() if not ok))}
    return curve


def smallest_ok(curve):
    b = None
    for k in (32, 16, 8, 4):
        if curve[k]["success"] >= 45:
            b = k
        else:
            break
    return b


def part_b():
    seeds = e1.seeds_of("swap_blocks", 50)
    cc, lc = budget_curve(CLOCK, seeds), budget_curve(LEDGER, seeds)
    for name, c in (("clock", cc), ("ledger", lc)):
        print(f"{name:7s} " + "  ".join(f"K={k}: {v['success']}/{v['finished']}" for k, v in c.items()))
    if any(v["finished"] < 48 for c in (cc, lc) for v in c.values()):
        word, bc, bl = "WAIT", None, None
    else:
        bc, bl = smallest_ok(cc), smallest_ok(lc)
        clock_low = all(cc[k]["success"] < 45 for k in (16, 8, 4))
        if bl is not None and ((bc is not None and bl <= bc / 2) or (clock_low and bl <= 16)):
            word = "EVENT INDEX CHEAPER"
        elif bl == bc:
            word = "SAME"
        else:
            word = "CURVE ONLY"
    print(f"E22b: clock B {bc}, ledger B {bl} -> {word} (appendix only)")
    (F / "E22B_VERDICT.json").write_text(json.dumps({"verdict": word, "clock_B": bc, "ledger_B": bl, "clock": cc,
                                                     "ledger": lc}, indent=1) + "\n")


def occupancy():
    out = {}
    for task in TASKS:
        seeds = e1.seeds_of(task, 50)
        d = O / "e5" / f"{CLOCK}_e1pause_vis" / "on" / task
        rows = []
        for s in seeds:
            ep = d / f"seed_{s}"
            share = e5b.clock_share(ep)
            st = json.loads((ep / "stress.jsonl").read_text().splitlines()[0]) if (ep / "stress.jsonl").exists() else None
            if share is not None and st:
                rows.append((share, int(st["frame"])))
        if rows:
            sh = sorted(r[0] for r in rows)
            fr = sorted(r[1] for r in rows)
            out[task] = {"episodes": len(rows), "share_mean": sum(sh) / len(sh), "share_min": sh[0], "share_max": sh[-1],
                         "inject_frame_median": fr[len(fr) // 2], "inject_frame_min": fr[0], "inject_frame_max": fr[-1]}
            t0 = fr[len(fr) // 2]
            out[task]["share_at_L_from_median_frame"] = {L: round(L / (t0 + L), 3) for L in (64, 128, 256, 512, 768, 1024)}
        print(f"Z6 {task}: {out.get(task)}")
    (F / "Z6_OCCUPANCY.json").write_text(json.dumps(out, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--part", choices=("a", "b", "occupancy"), required=True)
    ap.add_argument("--hid-suffix", default="hid")
    ap.add_argument("--out", default="E22A_VERDICT.json")
    args = ap.parse_args()
    global HID, OUT_A
    HID, OUT_A = args.hid_suffix, args.out
    {"a": part_a, "b": part_b, "occupancy": occupancy}[args.part]()


if __name__ == "__main__":
    main()
