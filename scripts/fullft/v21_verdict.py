"""Plan v21 readings on the A40 (11-27 01:50, Opus; written before any episode of these runs exists). Each applies the
reading registered in scripts/gaas/gaas_queue.txt above the run's line (plan v21 6.1, copied verbatim) unchanged.
Read-only, CPU. Helpers from v20_verdict.py / deed_verdict.py (paired bootstrap = a1_verdict.paired_ci, 10,000
resamples, seed 0, percentile 95 % CI). Official seed-42 bank, rearrange_blocks 1-100, default noise, execute 8. The
pre-set extensions pool the default-noise pairs with the MWAM_NOISE_SALT=r2 pairs (closed_loop/r2) of the same scenes =
200 pairs, the same rule, when both r2 sides are complete.
  c20  card 20 rearr_ar_pw (three frames + rearr_pw's pre-event weighting; no record):
       D = success(rearr_pw e30, closed_loop/v20) - success(rearr_ar_pw e30, closed_loop/v21); SESOI +0.15:
       CI lower > +0.15 -> RECORD NEEDED; CI upper < +0.15 -> WEIGHTING ALONE SUFFICES; otherwise UNCERTAIN.
       Described: rearr_split.py classes of rearr_ar_pw beside rearrange_ar (closed_loop/e6, H100); e10 / e20; the
       pre-written expectation (never pressed < 10 and pressed twice >= 20 if the record matters; both < 10 if the press
       was the whole problem) is reported as met / not met, never as a verdict.
  c21  card 21 rearr_arprop_pw (old writer + weighting), non-inferiority of the old writer:
       D = success(rearr_arprop_pw e30, v21) - success(rearr_pw e30, v20); margin -0.10: CI lower > -0.10 -> OLD WRITER
       SUFFICES; CI upper < -0.10 -> TIMELY WRITER NEEDED; otherwise UNCERTAIN. Described: classes beside
       rearrange_arprop (e6, H100); e10 / e20; pre-written expectation "pressed twice >= 10 if late writing causes
       repeats". The write delay and the record at the decision that started each second press come from
       rearr_ledger.py (separate task).
  c22  card 22 rearr_pw_s18 (seed 18), described only: success 1-100 and classes beside rearr_pw (seed 17); the mean of
       the two seeds (plan v19 rule R1).
Both c20 and c21 also report whether the seed extension of plan v21 5.5 item 6 is due (verdict not UNCERTAIN and
|D| < 0.30 -> both arms get a seed-18 training; the pooled interval is computed when those exist; the single-seed
verdict word stands). A verdict needs all 100 MAIN scenes on both sides (else WAIT). Writes outputs/fullft/V21_<NAME>.json.
  c24b card 24b ranking_drop (11-27 11:40, user chose it 11:12): see c24b's docstring.
  c25  card 25 obs_cf200 (11-27 12:45): see c25's docstring.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/v21_verdict.py c20|c21|c22|c24b|c25
"""
from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
TASK = "rearrange_blocks"


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


v20 = _module("v20_verdict", "v20_verdict.py")
success, compare, three, with_extension, rearr_classes = v20.success, v20.compare, v20.three, v20.with_extension, \
    v20.rearr_classes


def seed_extension(out):
    """Plan v21 5.5 item 6: due when the verdict is not UNCERTAIN and |D| < 0.30 (single-seed verdict word stands)."""
    main = out.get("main")
    if not main or str(out.get("verdict", "")).startswith(("WAIT", "UNCERTAIN")):
        return "not due"
    return "DUE (both arms seed 18; pooled interval when they exist)" if abs(main["D"]) < 0.30 else "not due (|D| >= 0.30)"


def described(folder, label):
    _, ok = success(folder, label, TASK)
    if not ok:
        return None
    return {"success": f"{sum(ok.values())}/{len(ok)}", "classes": dict(Counter(rearr_classes(folder, label).values()))}


def count(classes, prefix):
    return sum(v for k, v in classes.items() if k.startswith(prefix))


def c20():
    order, pw = success("v20", "rearr_pw_e30", TASK)
    _, ar = success("v21", "rearr_ar_pw_e30", TASK)
    out = {"run": "card 20 rearr_ar_pw (three frames + pre-event weighting) against rearr_pw", "sesoi": 0.15,
           "finished": {"rearr_pw_e30": len(pw), "rearr_ar_pw_e30": len(ar)}}
    if len(pw) < 100 or len(ar) < 100:
        out["verdict"] = f"WAIT ({len(pw)} / {len(ar)} of 100)"
        return out
    c = compare(pw, ar, order)                    # D = success(rearr_pw) - success(rearr_ar_pw)
    rule = lambda x: three(x, 0.15, "RECORD NEEDED", "WEIGHTING ALONE SUFFICES")   # noqa: E731
    with_extension(out, c, rule(c), rule, TASK, "rearr_pw_e30", "v20", "rearr_ar_pw_e30", "v21")
    cl = dict(Counter(rearr_classes("v21", "rearr_ar_pw_e30").values()))
    ref = dict(Counter(rearr_classes("e6", "rearrange_ar_e30").values()))
    out["described"] = {"rearr_ar_pw_e30": cl, "rearrange_ar_e30_h100": ref,
                        "rearr_pw_e30": dict(Counter(rearr_classes("v20", "rearr_pw_e30").values()))}
    nv, tw = count(cl, "never pressed"), count(cl, "pressed twice")
    out["expectation_written_before"] = {
        "never_pressed": nv, "pressed_twice": tw,
        "record_matters (never < 10 and twice >= 20)": nv < 10 and tw >= 20,
        "press_was_the_whole_problem (both < 10)": nv < 10 and tw < 10}
    for tag in ("e10", "e20"):
        d = described("v21", f"rearr_ar_pw_{tag}")
        if d:
            out[f"described_{tag}"] = d
    out["seed_extension_v21_5_5_6"] = seed_extension(out)
    return out


def c21():
    order, pw = success("v20", "rearr_pw_e30", TASK)
    _, old = success("v21", "rearr_arprop_pw_e30", TASK)
    out = {"run": "card 21 rearr_arprop_pw (old writer + pre-event weighting), non-inferiority against rearr_pw",
           "margin": -0.10, "finished": {"rearr_arprop_pw_e30": len(old), "rearr_pw_e30": len(pw)}}
    if len(pw) < 100 or len(old) < 100:
        out["verdict"] = f"WAIT ({len(old)} / {len(pw)} of 100)"
        return out

    def rule(x):
        lo, hi = x["ci95"]
        return "OLD WRITER SUFFICES" if lo > -0.10 else "TIMELY WRITER NEEDED" if hi < -0.10 else "UNCERTAIN"
    c = compare(old, pw, order)                   # D = success(rearr_arprop_pw) - success(rearr_pw)
    with_extension(out, c, rule(c), rule, TASK, "rearr_arprop_pw_e30", "v21", "rearr_pw_e30", "v20")
    cl = dict(Counter(rearr_classes("v21", "rearr_arprop_pw_e30").values()))
    out["described"] = {"rearr_arprop_pw_e30": cl,
                        "rearrange_arprop_e30_h100": dict(Counter(rearr_classes("e6", "rearrange_arprop_e30").values())),
                        "rearr_pw_e30": dict(Counter(rearr_classes("v20", "rearr_pw_e30").values()))}
    tw = count(cl, "pressed twice")
    out["expectation_written_before"] = {"pressed_twice": tw, "late writing causes repeats (twice >= 10)": tw >= 10}
    for tag in ("e10", "e20"):
        d = described("v21", f"rearr_arprop_pw_{tag}")
        if d:
            out[f"described_{tag}"] = d
    out["seed_extension_v21_5_5_6"] = seed_extension(out)
    return out


def c22():
    order, pw = success("v20", "rearr_pw_e30", TASK)
    _, s18 = success("v21", "rearr_pw_s18_e30", TASK)
    out = {"run": "card 22 rearr_pw_s18 (seed 18), described only",
           "finished": {"rearr_pw_s18_e30": len(s18), "rearr_pw_e30": len(pw)}}
    if len(s18) < 100:
        out["verdict"] = f"WAIT ({len(s18)} of 100)"
        return out
    out["success_1_100"] = {"seed18": sum(s18.values()), "seed17": sum(pw.values()),
                            "mean_of_two_seeds": (sum(s18.values()) + sum(pw.values())) / 2}
    out["paired_counts"] = compare(s18, pw, order)
    out["classes"] = {"rearr_pw_s18_e30": dict(Counter(rearr_classes("v21", "rearr_pw_s18_e30").values())),
                      "rearr_pw_e30": dict(Counter(rearr_classes("v20", "rearr_pw_e30").values()))}
    out["verdict"] = "DESCRIBED"
    return out


RT = "blocks_ranking_try"
D2_P12 = [4300001, 4300003, 4300006, 4300007, 4300008, 4300012, 4300014, 4300016, 4300017, 4300024, 4300026, 4300027,
          4300028, 4300030, 4300031]
D2_P45 = [4300000, 4300002, 4300004, 4300005, 4300009, 4300011, 4300013, 4300015, 4300018, 4300019, 4300020, 4300021,
          4300022, 4300035, 4300037]


def by_position(folder, label):
    """Success by the position of the sorted order in the expert's walk (diagnostic 1's reading of each episode):
    {'1-2': 'k/n', '3': .., '4-5': ..} and the per-position counts."""
    dg = _module("diag_cpu_v21", "diag_cpu_v21.py")
    rs = dg._module("ranking_split", "ranking_split.py")
    root = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop") / folder / label / "on" / RT
    tab = {}
    for d in sorted(root.glob("seed_*")):
        x = dg.diag1_episode(rs, d)
        if x is None or x["expert_position_of_sorted"] is None:
            continue
        p = x["expert_position_of_sorted"]
        g = "1-2" if p in (1, 2) else "3" if p == 3 else "4-5" if p in (4, 5) else str(p)
        ok, n = tab.get(g, (0, 0))
        tab[g] = (ok + int(x["success"]), n + 1)
    return {g: f"{ok}/{n}" for g, (ok, n) in sorted(tab.items())}


def c24b():
    """Card 24b ranking_drop (body record + record dropout 0.3), registered 11-27 (plan v21 6.2, verbatim):
    D = success(ranking_drop e30, v21) - success(ranking_arprop e30, e6); SESOI +0.15: CI lower > +0.15 -> RECORD
    DROPOUT HELPS; CI upper < +0.15 -> NO HELP; otherwise UNCERTAIN (pre-set r2 extension, 200 pairs). Described: against
    ranking_ar e30 (77) and 100; success by position (1-2 / 3 / 4-5); diagnostic 2's audit on ranking_drop (closed_loop/
    diag2, the same 30 scenes) when it exists; the pre-written expectation (positions 1-2 >= 38/45 while 4-5 >= 35/41)."""
    order, ref = success("e6", "ranking_arprop_e30", RT)
    _, new = success("v21", "ranking_drop_e30", RT)
    out = {"run": "card 24b ranking_drop (body record + record dropout 0.3) against ranking_arprop", "sesoi": 0.15,
           "finished": {"ranking_drop_e30": len(new), "ranking_arprop_e30": len(ref)}}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
        return out
    c = compare(new, ref, order)                  # D = success(ranking_drop) - success(ranking_arprop)
    rule = lambda x: three(x, 0.15, "RECORD DROPOUT HELPS", "NO HELP")   # noqa: E731
    with_extension(out, c, rule(c), rule, RT, "ranking_drop_e30", "v21", "ranking_arprop_e30", "e6")
    order_ar, ar = success("e6", "ranking_ar_e30", RT)
    out["described"] = {"against_ranking_ar_e30": compare(new, ar, order_ar),
                        "success_against_100": f"{sum(new.values())}/100",
                        "by_position": {"ranking_drop_e30": by_position("v21", "ranking_drop_e30"),
                                        "ranking_arprop_e30": by_position("e6", "ranking_arprop_e30"),
                                        "ranking_ar_e30": by_position("e6", "ranking_ar_e30")}}
    pos = out["described"]["by_position"]["ranking_drop_e30"]
    k12 = int(pos.get("1-2", "0/0").split("/")[0])
    k45 = int(pos.get("4-5", "0/0").split("/")[0])
    out["expectation_written_before"] = {"positions_1_2": pos.get("1-2"), "positions_4_5": pos.get("4-5"),
                                         "1-2 >= 38 and 4-5 >= 35": k12 >= 38 and k45 >= 35}
    audit = {}
    for cond in ("off", "mfirst", "mnear"):
        _, ok = success("diag2", f"ranking_drop_e30_{cond}", RT)
        if ok:
            audit[cond] = {"finished": len(ok), "position_1_2": sum(int(ok.get(s, 0)) for s in D2_P12),
                           "position_4_5": sum(int(ok.get(s, 0)) for s in D2_P45)}
    if audit:
        audit["unmodified_same_scenes"] = {"position_1_2": sum(int(new.get(s, 0)) for s in D2_P12),
                                           "position_4_5": sum(int(new.get(s, 0)) for s in D2_P45)}
        out["described"]["audit_diag2"] = audit
    out["seed_extension_v21_5_5_6"] = seed_extension(out)
    return out


def c25():
    """Card 25 obs_cf200 (counterfactual groups: the same table with every target), registered 11-27 12:45 (plan v21 6.3,
    verbatim): D = success(obs_cf200 e30, v21) - success(obs_s200 e30, v20); SESOI +0.15: CI lower > +0.15 -> BREAKING
    THE SHORTCUT HELPS; CI upper < +0.15 -> NO HELP; otherwise UNCERTAIN (pre-set r2 extension, 200 pairs). Described:
    against obs_ar e30 (13), 20 (blind pick), 28 (pure-WAM best, self-reported); e10 / e20; obs_s800 e10 beside it."""
    t = "observe_and_pickup"
    order, ref = success("v20", "obs_s200_e30", t)
    _, new = success("v21", "obs_cf200_e30", t)
    out = {"run": "card 25 obs_cf200 (same table, every target) against obs_s200", "sesoi": 0.15,
           "finished": {"obs_cf200_e30": len(new), "obs_s200_e30": len(ref)}}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT ({len(new)} / {len(ref)} of 100)"
        return out
    c = compare(new, ref, order)                  # D = success(obs_cf200) - success(obs_s200)
    rule = lambda x: three(x, 0.15, "BREAKING THE SHORTCUT HELPS", "NO HELP")   # noqa: E731
    with_extension(out, c, rule(c), rule, t, "obs_cf200_e30", "v21", "obs_s200_e30", "v20")
    o_ar, ar = success("e6", "obs_ar_e30", t)
    out["described"] = {"against_obs_ar_e30": compare(new, ar, o_ar),
                        "success_vs_bars": f"{c['new']} vs 13 (obs_ar e30), 20 (blind pick), 28 (pure-WAM best, self-reported)"}
    _, s800 = success("v20", "obs_s800_e10", t)
    if s800:
        out["described"]["against_obs_s800_e10"] = compare(new, s800, order)
    for tag in ("e10", "e20"):
        _, x = success("v21", f"obs_cf200_{tag}", t)
        if x:
            out["described"][f"obs_cf200_{tag}"] = compare(x, ref, order)
    out["seed_extension_v21_5_5_6"] = seed_extension(out)
    return out


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    fns = {"c20": c20, "c21": c21, "c22": c22, "c24b": c24b, "c25": c25}
    if name not in fns:
        print(__doc__)
        return 2
    out = fns[name]()
    print(json.dumps(out))
    (F / f"V21_{name.upper()}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"V21 {name.upper()}: {out['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
