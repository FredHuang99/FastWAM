"""Plan v14 E14 PRESS-tau verdict on the A40 (registered by Fable 11-18 in plan v14 section 3, approved by the user 18:33
together with E17, so E14 is evaluated on the A40; this script written 11-19 10:05 BJ, before press_v3c exists).
Read-only. A40, closed_loop/e17 (the A40's press bank), labels press_v3c_e10/e20/e30 and press_count_e10/e20/e30.
Each run's epoch by the P-SEL rule on scenes 1-50 (most successes; ties -> more first counts right; ties -> the later
epoch; an epoch needs >= 48 finished), the two picks paired on the held-out scenes 51-100 (same machine):
  new >= ref + 8 with paired sign p < 0.05 -> TIMELY WRITER HELPS; |new - ref| <= 4 -> NO EFFECT; otherwise PARTIAL.
  Floor: both picks >= 48/50 finished on 51-100, else NO READING. Also reported: new >= 25/50 ("back in the workable
  range", no verdict word). The 5090's press_series_verdict.py --card E14 is the same reading on the other machine
  group (the 5090 is not on the auto-pull, so it needs the user's pull before it can run press_v3c).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e14_verdict_a40.py
Writes outputs/fullft/E14_VERDICT_A40.json.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pp = module("press_pair", "press_pair.py")
e1 = module("e1_verdict", "e1_verdict.py")
F = pp.R / "outputs/fullft"


def pick(run, first):
    best = None
    for tag in ("e10", "e20", "e30"):
        try:
            st = pp.stages("e17", f"{run}_{tag}")
        except Exception:                                # noqa: BLE001
            continue
        d = {s: v for s, v in st.items() if str(s) in first}
        if len(d) < 48:
            continue
        key = (sum(bool(v.get("success")) for v in d.values()), sum(v.get("n1_error") == 0 for v in d.values()), int(tag[1:]))
        print(f"{run}_{tag} on 1-50: success {key[0]}/{len(d)}, first right {key[1]}")
        if best is None or key > best[0]:
            best = (key, tag, st)
    return best


def main():
    seeds = e1.seeds_of("press_button", 100) or []
    first, held = {str(s) for s in seeds[:50]}, {str(s) for s in seeds[50:]}
    new, ref = pick("press_v3c", first), pick("press_count", first)
    out = {"new": new and f"press_v3c_{new[1]}", "ref": ref and f"press_count_{ref[1]}"}
    if not new or not ref:
        out["reading"] = "NO READING (an epoch pick is missing: < 48 finished on 1-50)"
    else:
        A = {str(s): bool(v.get("success")) for s, v in new[2].items() if str(s) in held}
        B = {str(s): bool(v.get("success")) for s, v in ref[2].items() if str(s) in held}
        common = sorted(set(A) & set(B))
        if len(A) < 48 or len(B) < 48:
            out["reading"] = f"NO READING (finished on 51-100: {len(A)} / {len(B)} < 48)"
        else:
            sn, sr = sum(A[s] for s in common), sum(B[s] for s in common)
            a = sum(A[s] and not B[s] for s in common)
            b = sum(B[s] and not A[s] for s in common)
            p = pp.sign_p(a, b)
            out.update(n=len(common), success=sn, reference=sr, only_new=a, only_ref=b, sign_p=p, workable_range=sn >= 25,
                       reading="TIMELY WRITER HELPS" if (sn - sr >= 8 and p < 0.05) else "NO EFFECT" if abs(sn - sr) <= 4 else "PARTIAL")
            print(f"E14 (A40): {out['new']} vs {out['ref']} on 51-100, n={len(common)}: {sn} vs {sr}; only new {a}, only ref {b}, sign p {p:.4f}")
    print(f"E14 VERDICT (A40): {out['reading']}" + (f"; >= 25/50: {out.get('workable_range')}" if "workable_range" in out else ""))
    (F / "E14_VERDICT_A40.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
