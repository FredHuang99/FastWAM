"""Shared read-only helpers for the plan v15 verdict scripts written 11-19 19:30 BJ (e15 / e16 / e24 / e9e25). No
reading lives here: each verdict script states its registered rule in its own header."""
from __future__ import annotations

import importlib.util
import json
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


def seeds(task, n, start=0):
    s = e1.seeds_of(task, n) or []
    return s[start:n]


def results(folder, label, task, seed_list):
    """{seed: success} of the finished episodes."""
    out = {}
    for s in seed_list:
        r = Path(folder) / label / "on" / task / f"seed_{s}" / "result.json"
        if r.exists():
            out[s] = bool(json.loads(r.read_text()).get("success"))
    return out


def paired(a, b):
    """(n common, successes a, successes b, only a, only b, sign p) on the common scenes."""
    common = sorted(set(a) & set(b))
    oa = sum(a[s] and not b[s] for s in common)
    ob = sum(b[s] and not a[s] for s in common)
    return len(common), sum(a[s] for s in common), sum(b[s] for s in common), oa, ob, e1.sign_p(oa, ob)


def stress_cell(folder, vis, hid, task, seed_list, hid_floor, pairs_floor=45):
    """Paired visible / hidden cell of one injection (E1's validity). state: WAIT (< 48 finished per arm) /
    FLOOR NOT MET / HURT (Delta <= -8 with p < 0.05) / NOT HURT (Delta >= -5) / BETWEEN."""
    v = {s: e1.episode(Path(folder), vis, task, s) for s in seed_list}
    h = {s: e1.episode(Path(folder), hid, task, s) for s in seed_list}
    pairs = [s for s in seed_list if v[s] and h[s] and v[s]["valid"] and h[s]["valid"]]
    a = sum(v[s]["success"] and not h[s]["success"] for s in pairs)
    b = sum(h[s]["success"] and not v[s]["success"] for s in pairs)
    hs = sum(bool(h[s] and h[s]["success"]) for s in seed_list)
    c = {"vis": vis, "hid": hid, "finished_vis": sum(1 for s in seed_list if v[s]),
         "finished_hid": sum(1 for s in seed_list if h[s]), "valid_pairs": len(pairs), "vis_only": a, "hid_only": b,
         "delta": a - b, "p": e1.sign_p(a, b), "hidden_success": hs}
    need = min(48, len(seed_list))
    if c["finished_vis"] < need or c["finished_hid"] < need:
        c["state"] = "WAIT"
    elif len(pairs) < pairs_floor or hs < hid_floor:
        c["state"] = "FLOOR NOT MET"
    elif c["delta"] <= -8 and c["p"] < 0.05:
        c["state"] = "HURT"
    elif c["delta"] >= -5:
        c["state"] = "NOT HURT"
    else:
        c["state"] = "BETWEEN"
    print(f"  {vis[:-4]:34s} {task:15s} pairs {len(pairs)}, Delta {a - b:+d} (vis-only {a}, hid-only {b}), "
          f"p {c['p']:.4f}, hidden {hs}/{len(seed_list)} -> {c['state']}")
    return c


def write(name, obj):
    (F / name).write_text(json.dumps(obj, indent=1) + "\n")
