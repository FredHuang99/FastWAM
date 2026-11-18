"""Plan v13 E7 AR-long verdict (registered by Fable 11-17 in plan v13 section 3, approved by the user 15:50; copied
into scripts/gaas/gaas_queue.txt; this script written 11-18 18:00 BJ, before any ar2_long result exists). Read-only.

Model: the two-task AR (ar_2task) trained on from its 30-frame-epoch resume checkpoint to 60 frame-epochs on the new
H200 (GaaS run ar2_long; exports e45, e60). A40, closed_loop/e7: labels ar2_long_e45 / ar2_long_e60, swap_blocks and
put_back_block scenes 1-100, no stress.
Registered reading (plan v13 E7, verbatim in meaning):
  e60 swap >= 90/100 -> TRAINABLE; <= 70/100 -> STRUCTURAL; otherwise PARTIAL. Floor: put >= 95/100 (else no verdict).
  e45: evaluated, reported (no verdict).
  TRAINABLE -> contribution 1 is rewritten as in plan v13 1.3 (and Opus asks the user to switch to Fable).
Implementation details (written 11-18 before any result; not part of the registered reading):
  - With episodes missing (an error not yet re-run) a threshold is decided only when the missing ones cannot change it;
    otherwise WAIT.
  - Reported beside it: the A40 AR e30 (A40-EQ, closed_loop/g1, 56/100) paired with e45 / e60 on the same scenes
    (sign test), and the swap failure classes (press_gap.py: pressed before s3 / kept moving / idle after s3 /
    stopped before s3).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e7_verdict.py
Writes outputs/fullft/E7_VERDICT.json.
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
spec = importlib.util.spec_from_file_location("e5_verdict", HERE / "e5_verdict.py")
e5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e5)
e1 = e5.e1


def decided(n_success, n_done, n_all, need, at_least=True):
    """True / False if the threshold (>= need, or <= need) holds whatever the missing episodes do; None otherwise."""
    missing = n_all - n_done
    if at_least:
        return True if n_success >= need else (False if n_success + missing < need else None)
    return True if n_success + missing <= need else (False if n_success > need else None)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", default=str(O / "e7"))
    ap.add_argument("--base-folder", default=str(O / "g1"), help="A40 AR e30 (A40-EQ) and put e30")
    args = ap.parse_args()
    folder, base = Path(args.folder), Path(args.base_folder)
    seeds = {t: e1.seeds_of(t, 100) for t in ("swap_blocks", "put_back_block")}
    rows = {}
    ar30 = {t: e5.finished(base, "ar_2task_e30", t, seeds[t]) for t in seeds}
    for tag in ("e45", "e60"):
        for t in seeds:
            ep = e5.finished(folder, f"ar2_long_{tag}", t, seeds[t])
            fails = Counter(k or "unclassified" for ok, k in ep.values() if not ok)
            ref = ar30[t]
            common = sorted(set(ep) & set(ref))
            a = sum(ep[s][0] and not ref[s][0] for s in common)
            b = sum(ref[s][0] and not ep[s][0] for s in common)
            rows[f"{tag}|{t}"] = {"finished": len(ep), "of": len(seeds[t]), "success": sum(ok for ok, _ in ep.values()),
                                  "failures": dict(fails), "vs_ar_e30": {"scenes": len(common), "only_long": a,
                                                                         "only_e30": b, "p": e1.sign_p(a, b),
                                                                         "e30_success": sum(ref[s][0] for s in common)}}
            r = rows[f"{tag}|{t}"]
            print(f"ar2_long {tag} {t}: {r['success']}/{r['finished']} finished of {r['of']}"
                  + (f"; failures {dict(fails)}" if t == "swap_blocks" else "")
                  + f"; vs AR e30 on {len(common)} common scenes: {r['vs_ar_e30']['e30_success']} -> "
                    f"{sum(ep[s][0] for s in common)}, only-long {a}, only-e30 {b}, sign p {r['vs_ar_e30']['p']:.4f}")
    sw, pt = rows["e60|swap_blocks"], rows["e60|put_back_block"]
    floor = decided(pt["success"], pt["finished"], pt["of"], 95)
    trainable = decided(sw["success"], sw["finished"], sw["of"], 90)
    structural = decided(sw["success"], sw["finished"], sw["of"], 70, at_least=False)
    if floor is None:
        verdict = f"WAIT (floor undecided: put e60 {pt['success']}/{pt['finished']} of {pt['of']})"
    elif floor is False:
        verdict = "NO VERDICT (floor: e60 put < 95/100)"
    elif trainable is True:
        verdict = "TRAINABLE"
    elif structural is True:
        verdict = "STRUCTURAL"
    elif trainable is False and structural is False:
        verdict = "PARTIAL"
    else:
        verdict = f"WAIT (swap e60 {sw['success']}/{sw['finished']} of {sw['of']}: missing episodes could change it)"
    print(f"FLOOR (e60 put >= 95/100): {floor}")
    print(f"E7 VERDICT (e60 swap): {verdict}")
    if verdict == "TRAINABLE":
        print("-> registered consequence: contribution 1 rewritten as in plan v13 1.3; Opus asks the user to switch to Fable")
    (F / "E7_VERDICT.json").write_text(json.dumps({"verdict": verdict, "floor": floor, "rows": rows}, indent=1) + "\n")


if __name__ == "__main__":
    main()
