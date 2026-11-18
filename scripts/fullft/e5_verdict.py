"""Plan v13 E5 CLOCK-arm verdict (registered by Fable 11-17 in plan v13 section 3, approved by the user 15:40; copied
into scripts/gaas/gaas_queue.txt; this script written 11-18 18:00 BJ, before any ar2_clock result exists). Read-only.

Model: ar2_clock e30 (AR + 32 proprio tokens sampled uniformly over the elapsed time, each with a sinusoidal timestamp;
same content, token path, data and recipe as the ledger model ar2_prop: only the index differs). A40, closed_loop/e5:
  no stress   label ar2_clock_e30, swap_blocks and put_back_block scenes 1-100
  stress      labels ar2_clock_e30_e1pause_vis / _hid, swap_blocks scenes 1-50, E1's injection (pause 64, one per
              episode, triggered by the robot's own events; vis = the frames are shown, hid = hidden)
Registered reading (plan v13 E5, verbatim in meaning):
  floor       the clock arm reaches swap >= 70/100 without stress, else no stress verdict; only the number
              "natively trained, the event index beats the time index" (clock vs ledger e30, no stress) is reported
  INDEX MATTERS   clock Delta (vis - hid) <= -8/50 with sign p < 0.05 AND the ledger model's E1 Delta >= -5/50
  NOT REPRODUCED  clock Delta >= -5/50
  PARTIAL         otherwise
  After INDEX MATTERS only: timestamps x1.5 and x0.5 (MWAM_CLOCK_SCALE), 50 episodes each; report only whether the
  failure direction flips (--scales).
Implementation details (written 11-18 before any result; not part of the registered reading):
  - Delta, p and the valid pairs exactly as scripts/fullft/e1_verdict.py (same injection, same validity: both finished,
    one injection each, object displacement < 1 cm, no counter changed, arm back within 0.05 rad); E1's floor of
    >= 45 valid pairs applies (same protocol); the ledger reference = E1's ledger pause cell on swap_blocks
    (outputs/fullft/E1_VERDICT_swap_blocks.json, same scenes 1-50, same machine).
  - The floor on 100 scenes with some episodes missing: decided when the missing ones cannot change it (>= 70 already,
    or successes + missing < 70); otherwise WAIT.
  - "Failure direction": per failed swap episode, pressed before the third move / kept moving or idle after it /
    stopped before it (press_gap.py classes). The x1.5 / x0.5 runs are without stress, scenes 1-50, labels
    ar2_clock_e30_ts1.5 / _ts0.5; compared with the clock's own no-stress scenes 1-50.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e5_verdict.py [--scales]
Writes outputs/fullft/E5_VERDICT.json (and E5_SCALES.json with --scales).
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
pg = module("press_gap", "press_gap.py")
cls = pg.cls
CLOCK = "ar2_clock_e30"


def finished(folder: Path, label: str, task: str, seeds):
    """{seed: (success, failure class or None)} of the finished episodes among seeds."""
    out = {}
    for s in seeds:
        d = folder / label / "on" / task / f"seed_{s}"
        if not (d / "result.json").exists():
            continue
        ok = bool(json.loads((d / "result.json").read_text()).get("success"))
        kind = None
        if not ok and task == "swap_blocks" and (d / "executed_actions.jsonl").exists():
            snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
            if len(snaps) >= 2 and snaps[0]:
                r = cls.analyse_swap(snaps, counters)
                kind = (pg.swap_case(snaps, counters)[0] if r["s3"]
                        else "pressed before s3" if r["pressed"] else "stopped before s3")
        out[s] = (ok, kind)
    return out


def floor_state(n_success, n_done, n_all, need):
    if n_success >= need:
        return True
    if n_success + (n_all - n_done) < need:
        return False
    return None


def scales(folder):
    seeds = e1.seeds_of("swap_blocks", 50)
    rows = {}
    for lab in (CLOCK, f"{CLOCK}_ts1.5", f"{CLOCK}_ts0.5"):
        ep = finished(folder, lab, "swap_blocks", seeds)
        fails = Counter(k or "unclassified" for ok, k in ep.values() if not ok)
        rows[lab] = {"finished": len(ep), "success": sum(ok for ok, _ in ep.values()), "failures": dict(fails)}
        print(f"{lab:24s} swap 1-50: {rows[lab]['success']}/{len(ep)}; failures {dict(fails)}")
    def direction(f):
        early, late = f.get("pressed before s3", 0), f.get("kept moving", 0) + f.get("idle after s3", 0)
        return "early" if early > late else "late" if late > early else "none"
    d = {lab: direction(v["failures"]) for lab, v in rows.items()}
    flips = d[f"{CLOCK}_ts1.5"] != d[f"{CLOCK}_ts0.5"] and "none" not in (d[f"{CLOCK}_ts1.5"], d[f"{CLOCK}_ts0.5"])
    print(f"failure direction (more 'pressed before s3' = early, more 'kept moving / idle after s3' = late): {d}")
    print(f"FAILURE DIRECTION FLIPS between x1.5 and x0.5: {'YES' if flips else 'NO'} (reported only)")
    (F / "E5_SCALES.json").write_text(json.dumps({"rows": rows, "direction": d, "flips": flips}, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=str(O / "e5"))
    ap.add_argument("--ledger-folder", default=str(O / "g1"), help="A40 no-stress ledger e30 (A40-EQ)")
    ap.add_argument("--scales", action="store_true")
    args = ap.parse_args()
    folder = Path(args.folder)
    if args.scales:
        return scales(folder)
    seeds100 = {t: e1.seeds_of(t, 100) for t in ("swap_blocks", "put_back_block")}
    base = {t: finished(folder, CLOCK, t, seeds100[t]) for t in seeds100}
    for t, ep in base.items():
        fails = Counter(k or "unclassified" for ok, k in ep.values() if not ok)
        print(f"clock no stress {t}: {sum(ok for ok, _ in ep.values())}/{len(ep)} finished of {len(seeds100[t])}"
              + (f"; swap failures {dict(fails)}" if t == "swap_blocks" else ""))
    sw = base["swap_blocks"]
    sw_succ = sum(ok for ok, _ in sw.values())
    floor = floor_state(sw_succ, len(sw), len(seeds100["swap_blocks"]), 70)
    led = finished(Path(args.ledger_folder), "ar2_prop_e30", "swap_blocks", seeds100["swap_blocks"])
    common = sorted(set(sw) & set(led))
    a = sum(led[s][0] and not sw[s][0] for s in common)
    b = sum(sw[s][0] and not led[s][0] for s in common)
    native = {"scenes": len(common), "ledger": sum(led[s][0] for s in common), "clock": sum(sw[s][0] for s in common),
              "ledger_only": a, "clock_only": b, "p": e1.sign_p(a, b)}
    print(f"no stress, swap, paired on {len(common)} scenes: ledger e30 (A40, {args.ledger_folder}) {native['ledger']} vs "
          f"clock {native['clock']}; ledger-only {a}, clock-only {b}, sign p {native['p']:.4f}")

    seeds50 = e1.seeds_of("swap_blocks", 50)
    vis = {s: e1.episode(folder, f"{CLOCK}_e1pause_vis", "swap_blocks", s) for s in seeds50}
    hid = {s: e1.episode(folder, f"{CLOCK}_e1pause_hid", "swap_blocks", s) for s in seeds50}
    pairs = [s for s in seeds50 if vis[s] and hid[s] and vis[s]["valid"] and hid[s]["valid"]]
    va = sum(vis[s]["success"] and not hid[s]["success"] for s in pairs)
    hb = sum(hid[s]["success"] and not vis[s]["success"] for s in pairs)
    delta, p = va - hb, e1.sign_p(va, hb)
    stressed = {arm: finished(folder, f"{CLOCK}_e1pause_{arm}", "swap_blocks", seeds50) for arm in ("vis", "hid")}
    for arm, ep in stressed.items():
        fails = Counter(k or "unclassified" for ok, k in ep.values() if not ok)
        print(f"clock pause {arm}: {sum(ok for ok, _ in ep.values())}/{len(ep)} finished; failures {dict(fails)}")
    print(f"clock pause: valid pairs {len(pairs)}; vis-only {va}, hid-only {hb}; Delta {delta:+d}; sign p {p:.4f} "
          f"(finished vis {sum(1 for s in seeds50 if vis[s])}, hid {sum(1 for s in seeds50 if hid[s])})")
    e1v = json.loads((F / "E1_VERDICT_swap_blocks.json").read_text()) if (F / "E1_VERDICT_swap_blocks.json").exists() else None
    led_delta = e1v["cells"]["ledger|pause"]["delta"] if e1v else None
    print(f"ledger model's E1 Delta (pause, swap 1-50, A40): {led_delta}; AR's: "
          f"{e1v['cells']['AR|pause']['delta'] if e1v else None} (reported)")

    if floor is None:
        verdict = f"WAIT (floor undecided: {sw_succ}/{len(sw)} no-stress swap episodes finished of 100)"
    elif floor is False:
        verdict = "NO STRESS VERDICT (floor: clock no-stress swap < 70/100)"
    elif led_delta is None:
        verdict = "WAIT (no E1_VERDICT_swap_blocks.json)"
    elif len(pairs) < 45:
        verdict = f"NO VERDICT (only {len(pairs)} valid pairs < 45)"
    elif delta <= -8 and p < 0.05 and led_delta >= -5:
        verdict = "INDEX MATTERS"
    elif delta >= -5:
        verdict = "NOT REPRODUCED"
    else:
        verdict = "PARTIAL"
    print(f"FLOOR (clock no-stress swap >= 70/100): {floor}")
    print(f"E5 VERDICT: {verdict}")
    out = {"verdict": verdict, "floor": floor, "no_stress": {t: {"finished": len(ep), "success": sum(ok for ok, _ in ep.values())}
                                                             for t, ep in base.items()},
           "native_vs_ledger": native, "stress": {"valid_pairs": len(pairs), "vis_only": va, "hid_only": hb,
                                                  "delta": delta, "p": p},
           "ledger_e1_delta": led_delta}
    (F / "E5_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
