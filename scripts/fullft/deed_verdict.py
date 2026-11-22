"""Plan v19 A3 / D1 / D2 verdicts on the A40 (11-22, Opus; written before any obs_zoom, d1 or d2 episode exists). Each
applies the reading registered in scripts/gaas/gaas_queue.txt above the run's line (committed 98bfded / f5a8114 /
fafaf13) unchanged. Read-only, CPU. Paired bootstrap = a1_verdict.paired_ci (10,000 resamples of the paired scenes,
seed 0, percentile 95 % CI). Official seed-42 banks, scenes 1-100, default noise unless said.
  a3  observe_and_pickup: D = success(obs_zoom e30, closed_loop/a3) - success(obs_ar e30, closed_loop/e6); SESOI +0.10:
      CI lower > +0.10 -> ZOOM HELPS; CI upper < +0.10 -> NO HELP; otherwise UNCERTAIN. Described: e10 / e20 when there;
      success against the bar 28 (plan 3.3: below 28 after two rounds -> back to Fable).
  d1  swap_blocks, per arm (d1_w, d1_wn e30, closed_loop/d1): D = success(arm) - success(ar_2task e30, closed_loop/g1);
      SESOI +0.15: CI lower > +0.15 -> DECISION TRAINING HELPS; CI upper < +0.15 -> NO HELP; otherwise UNCERTAIN. The
      arm difference d1_wn - d1_w is described, unless a MAIN is HELPS: then SESOI 0.10, the same three outcomes.
      put_back_block described. Plan 6.2: an arm at >= 95 or NO HELP -> back to Fable.
  d2  press_button: episode over-press = button-1 count > card_1 or button-2 count > card_2 at the first confirm press
      (at the end when none; closed_loop_stages.analyse_press n1_error / n2_error); under-press likewise with <.
      D = over rate(d2_press e30, closed_loop/d2) - over rate(press_v3c e30, closed_loop/e17); SESOI = -0.5 x the
      control's over rate on the paired scenes. In order: CI upper < 0 and D <= SESOI -> OVER-PRESS HALVED; CI upper < 0
      -> PART; CI lower > SESOI -> NOT HALVED; otherwise UNCERTAIN. Guard: D_under CI lower > +0.10 -> OVERCORRECTED
      (added to the outcome). Plan 6.2: CI containing 0 or D >= 0 -> back to Fable. Described: per-button over / right /
      under, success, and the same against press_count e30 (closed_loop/g1 1-50 + sel 51-100).
      Pairs: scenes where both episodes have known cards (n1_error not None); the count of excluded scenes is printed.
A verdict needs all 100 scenes finished on both sides (else WAIT). Writes outputs/fullft/<A3|D1|D2>_VERDICT.json.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/deed_verdict.py a3|d1|d2
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2/closed_loop"
F = R / "outputs/fullft"


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


a1 = module("a1_verdict", "a1_verdict.py")


def seeds(task):
    return a1.e1().seeds_of(task, 100)


def success(folder, label, task):
    s = seeds(task)
    out = {}
    for x in s:
        f = O / folder / label / "on" / task / f"seed_{x}" / "result.json"
        if f.exists():
            out[x] = int(bool(json.loads(f.read_text()).get("success")))
    return s, out


def compare(new, ref, order):
    common = [x for x in order if x in new and x in ref]
    a, b = [new[x] for x in common], [ref[x] for x in common]
    d, lo, hi = a1.paired_ci(a, b)
    return {"scenes": len(common), "new": sum(a), "ref": sum(b), "D": round(d, 4), "ci95": [round(lo, 4), round(hi, 4)],
            "only_new": sum(x and not y for x, y in zip(a, b)), "only_ref": sum(y and not x for x, y in zip(a, b))}


def three(c, sesoi, yes, no):
    if c["ci95"][0] > sesoi:
        return yes
    if c["ci95"][1] < sesoi:
        return no
    return "UNCERTAIN"


def a3():
    task = "observe_and_pickup"
    order, ref = success("e6", "obs_ar_e30", task)
    out = {"run": "A3 obs_zoom", "sesoi": 0.10, "finished": {}}
    _, new = success("a3", "obs_zoom_e30", task)
    out["finished"] = {"obs_zoom_e30": len(new), "obs_ar_e30": len(ref)}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT (obs_zoom {len(new)}, obs_ar {len(ref)} of 100)"
    else:
        c = compare(new, ref, order)
        out.update(main=c, verdict=three(c, 0.10, "ZOOM HELPS", "NO HELP"), success_vs_bar28=f"{c['new']} vs 28")
    for tag in ("e10", "e20"):
        _, x = success("a3", f"obs_zoom_{tag}", task)
        if x:
            out[f"described_{tag}"] = compare(x, ref, order)
    return out


def d1():
    out = {"run": "D1 decision training", "sesoi": 0.15}
    order, ref = success("g1", "ar_2task_e30", "swap_blocks")
    porder, pref = success("g1", "ar_2task_e30", "put_back_block")
    arms, fable = {}, []
    for arm in ("d1_w", "d1_wn"):
        _, new = success("d1", f"{arm}_e30", "swap_blocks")
        _, put = success("d1", f"{arm}_e30", "put_back_block")
        r = {"finished_swap": len(new), "finished_put": len(put)}
        if len(new) < 100 or len(ref) < 100:
            r["verdict"] = f"WAIT ({arm} {len(new)}, ar_2task {len(ref)} of 100)"
        else:
            r["main"] = compare(new, ref, order)
            r["verdict"] = three(r["main"], 0.15, "DECISION TRAINING HELPS", "NO HELP")
            if r["verdict"] == "NO HELP" or r["main"]["new"] >= 95:
                fable.append(f"{arm}: {r['verdict']}, {r['main']['new']}/100")
        if put:
            r["described_put_back"] = compare(put, pref, porder)
        arms[arm] = (r, new)
    out["arms"] = {k: v[0] for k, v in arms.items()}
    (rw, nw), (rn, nn) = arms["d1_w"], arms["d1_wn"]
    if len(nw) == 100 and len(nn) == 100:
        c = compare(nn, nw, order)
        if "HELPS" in str(rw.get("verdict")) or "HELPS" in str(rn.get("verdict")):
            out["arm_difference"] = dict(c, sesoi=0.10, verdict=three(c, 0.10, "HEAD HELPS", "NO HEAD EFFECT"))
        else:
            out["arm_difference_described"] = c
    out["plan_6_2_back_to_fable"] = fable
    out["verdict"] = "; ".join(f"{k}: {v[0]['verdict']}" for k, v in arms.items())
    return out


def press_rows(folder, label):
    pp = module("press_pair", "press_pair.py")
    try:
        st = pp.stages(folder, label)
    except Exception as e:                                         # noqa: BLE001
        print(f"{folder}:{label}: no stages ({type(e).__name__})")
        return {}
    return {int(s): v for s, v in st.items()}


def over(v):
    return int((v["n1_error"] or 0) > 0 or (v["n2_error"] or 0) > 0)


def under(v):
    return int((v["n1_error"] or 0) < 0 or (v["n2_error"] or 0) < 0)


def per_button(rows):
    out = {}
    for k in ("n1_error", "n2_error"):
        e = [v[k] for v in rows.values() if isinstance(v.get(k), int)]
        out[k] = {"over": sum(x > 0 for x in e), "right": sum(x == 0 for x in e), "under": sum(x < 0 for x in e)}
    out["success"] = sum(bool(v.get("success")) for v in rows.values())
    return out


def d2():
    out = {"run": "D2 press merged"}
    new, ref = press_rows("d2", "d2_press_e30"), press_rows("e17", "press_v3c_e30")
    order = [int(x) for x in seeds("press_button")]
    new = {s: v for s, v in new.items() if s in order}
    ref = {s: v for s, v in ref.items() if s in order}
    out["finished"] = {"d2_press_e30": len(new), "press_v3c_e30": len(ref)}
    if len(new) < 100 or len(ref) < 100:
        out["verdict"] = f"WAIT (d2 {len(new)}, press_v3c {len(ref)} of 100)"
        return out
    known = [s for s in order if new[s].get("n1_error") is not None and ref[s].get("n1_error") is not None]
    out["excluded_unknown_cards"] = 100 - len(known)
    on, orf = {s: over(new[s]) for s in known}, {s: over(ref[s]) for s in known}
    un, urf = {s: under(new[s]) for s in known}, {s: under(ref[s]) for s in known}
    c = compare(on, orf, known)
    sesoi = round(-0.5 * c["ref"] / len(known), 4)
    lo, hi = c["ci95"]
    if hi < 0 and c["D"] <= sesoi:
        v = "OVER-PRESS HALVED"
    elif hi < 0:
        v = "PART"
    elif lo > sesoi:
        v = "NOT HALVED"
    else:
        v = "UNCERTAIN"
    cu = compare(un, urf, known)
    if cu["ci95"][0] > 0.10:
        v += " + OVERCORRECTED"
    out.update(sesoi=sesoi, over=c, under=cu, verdict=v,
               plan_6_2_back_to_fable=bool(lo <= 0 <= hi or c["D"] >= 0),
               described={"d2_press_e30": per_button(new), "press_v3c_e30": per_button(ref)})
    pc = {**press_rows("g1", "press_count_e30"), **press_rows("sel", "press_count_e30")}
    pc = {s: v for s, v in pc.items() if s in order}
    if pc:
        k2 = [s for s in known if s in pc and pc[s].get("n1_error") is not None]
        out["described"]["press_count_e30"] = per_button(pc)
        out["described"]["over_vs_press_count"] = compare({s: on[s] for s in k2}, {s: over(pc[s]) for s in k2}, k2)
    return out


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = {"a3": a3, "d1": d1, "d2": d2}.get(which)
    if fn is None:
        print(__doc__)
        return 2
    out = fn()
    (F / f"{which.upper()}_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    print(f"{which.upper()} VERDICT: {out['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
