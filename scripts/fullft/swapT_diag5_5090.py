"""Plan v21 6.5 diagnostic 5 (b) and (d) on the 5090 (11-27 02:00, Opus; written before either is run). Read-only, CPU,
DESCRIBED ONLY. swap_T (RMBench envs/swap_T.py): two T blocks; each arm must put its block where the OTHER block started.

(b) python scripts/fullft/swapT_diag5_5090.py b [--first 10]
    Card 11's closed-loop episodes on this machine (closed_loop/swaptdiag, swapT_ar_e30 and swapT_arprop_e30, scenes
    1-50, MWAM_OBJECT_LOG=1: T-block poses and both end-effectors per executed target). Episodes where a block ended at its
    own start (lifted, < 2.5 cm from its start: card 11's "a block back at its own place"), successes as the reference.
    Per episode: which block / arm was put down first; the FIRST placer's end-effector: closest horizontal distance to the
    OTHER block's start while carrying (and when), and at its put-down; the closest distance between the two
    end-effectors (and when); the LATER placer: when it turned back (the target of its farthest horizontal distance from
    its own block's start while carrying), how far it got, and its closest horizontal distance to the other block's
    start. --first 10: the first 10 such episodes of each model (bank order) and the first 5 successes, measurements only
    (the classes are fixed from these, Status 11-27, before the full run). Without --first: the same for all episodes
    plus the classes in CLASSES_5B (None until fixed: the full run refuses).
(d) python scripts/fullft/swapT_diag5_5090.py d
    The 50 swap_T demos (official hdf5). Per demo and arm: the arm's release pose (end-effector position + orientation at
    its first gripper opening after its grasp) and the OTHER arm's readings at its own grasp (first gripper close). Can
    the release pose be read linearly from the other arm's readings? Inputs: (i) the other arm's six joint readings,
    (ii) its end-effector pose in the robot base frame (the hdf5's end-effector poses: the simulator's own forward
    kinematics). Linear least squares with an intercept (ridge 1e-6), leave-one-demo-out: position error (cm) and angle
    error (deg; quaternions sign-aligned, the prediction normalised). Also the "copy" baseline: release position = the
    other arm's grasp position. Card 26 opens (plan v21 6.4) when (ii)'s position error < 2.5 cm and (i)'s is at least
    twice that, AND (b) shows that in the back-at-own-place episodes the first placer never went over the other block's
    start.
Writes outputs/fullft/SWAPT_DIAG5B[_FIRST].json / SWAPT_DIAG5D.json.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2/closed_loop"
F = R / "outputs/fullft"
BLOCKS = ("T_block1", "T_block2")
OVER_CM = 5.0              # "over the other start": hand within 5 cm horizontally (twice the benchmark's 2.5 cm block tolerance)


def CLASSES_5B(x):
    """Fixed 11-27 04:30 from the first 10 back-at-own-start failures per model (SWAPT_DIAG5B_FIRST.json, Status 11-27),
    before the full run. A is card 26's condition (b): the first placer never went over the other block's start."""
    f, l = x.get("first") or {}, x.get("later") or {}
    fc, lc, lp = f.get("closest_to_other_start_cm"), l.get("closest_to_other_start_cm"), l.get("at_putdown_to_other_start_cm")
    if None in (fc, lc, lp):
        return "E other (a reading missing)"
    if fc >= OVER_CM:
        return "A first hand never over the other start"
    if lc >= OVER_CM:
        return "B later hand never over the other start"
    if l.get("block") in x["back_at_own_start"]:
        if lp >= OVER_CM:
            return "C both hands went over the other start; the later hand put its block down elsewhere"
        return "D the later hand put its block down over the other start; that block ended at its own start"
    return "E other"


def _module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def hdist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def measure_b(sp, d: Path):
    m = sp.measure(d)
    if not m or "why" in m:
        return None
    acts = sp.rows(d / "executed_actions.jsonl")
    pos = [(r.get("objects_after") or {}).get("_actors") or {} for r in acts]
    ee = [r.get("ee_after") or {} for r in acts]
    start = {b: pos[0][b] for b in BLOCKS}
    other = {"T_block1": "T_block2", "T_block2": "T_block1"}
    back = [b for b in BLOCKS if m[b]["lifted"] and m[b]["to_own_start_cm"] < 2.5]
    downs = [(m[b]["down_at"], b) for b in BLOCKS if m[b]["down_at"] is not None]
    out = {"success": m["success"], "back_at_own_start": back, "targets": len(acts)}
    if not downs:
        out["why"] = "no block put down"
        return out
    downs.sort()
    first_b, later_b = downs[0][1], other[downs[0][1]]
    for role, b in (("first", first_b), ("later", later_b)):
        arm = m[b]["lifted_by"]
        lo, hi = m[b]["lifted_at"], m[b]["down_at"] if m[b]["down_at"] is not None else len(acts) - 1
        r = {"block": b, "arm": arm, "lifted_at": lo, "down_at": m[b]["down_at"],
             "to_target_cm": m[b]["pos_err_cm"], "to_own_start_cm": m[b]["to_own_start_cm"]}
        if arm and lo is not None:
            tr = [(t, ee[t][arm][:3]) for t in range(lo, hi + 1) if ee[t].get(arm)]
            if tr:
                d_other = [(hdist(p, start[other[b]]), t) for t, p in tr]
                d_own = [(hdist(p, start[b]), t) for t, p in tr]
                r["closest_to_other_start_cm"], r["closest_to_other_start_at"] = round(100 * min(d_other)[0], 1), min(d_other)[1]
                r["at_putdown_to_other_start_cm"] = round(100 * d_other[-1][0], 1)
                far = max(d_own)
                r["farthest_from_own_start_cm"], r["turned_back_at"] = round(100 * far[0], 1), far[1]
        out[role] = r
    both = [(math.dist(e["left"][:3], e["right"][:3]), t) for t, e in enumerate(ee) if e.get("left") and e.get("right")]
    if both:
        mn = min(both)
        out["closest_hands_cm"], out["closest_hands_at"] = round(100 * mn[0], 1), mn[1]
    return out


def part_b(first: int):
    sp = _module("swapT_split", "swapT_split.py")
    if not first and CLASSES_5B is None:
        print("DIAG 5B: the classes are not fixed yet (run --first 10, fix CLASSES_5B): nothing read")
        return 2
    rep = {"run": "plan v21 diagnostic 5(b) (described)", "models": {}}
    for label in ("swapT_ar_e30", "swapT_arprop_e30"):
        root = O / "swaptdiag" / label / "on" / "swap_T"
        eps = sorted((d for d in root.glob("seed_*") if d.name[5:].isdigit()), key=lambda d: int(d.name[5:]))
        back, succ = {}, {}
        for d in eps:
            x = measure_b(sp, d)
            if x is None:
                continue
            if x["back_at_own_start"] and not x["success"]:
                if not first or len(back) < first:
                    back[d.name[5:]] = x
            elif x["success"]:
                if not first or len(succ) < 5:
                    succ[d.name[5:]] = x
        print(f"\n== {label}: back-at-own-start failures {len(back)}, successes {len(succ)}"
              f"{' (first ' + str(first) + ' / 5)' if first else ''}")
        for tag, group in (("BACK", back), ("SUCCESS", succ)):
            for s, x in group.items():
                f, l = x.get("first", {}), x.get("later", {})
                print(f"  {tag} {s}: back {x['back_at_own_start']}; hands closest {x.get('closest_hands_cm')} cm at "
                      f"{x.get('closest_hands_at')}")
                for role, r in (("first", f), ("later", l)):
                    if r:
                        print(f"     {role:5s} {r['block']} by {r['arm']}: lifted {r['lifted_at']} down {r['down_at']}; "
                              f"closest to OTHER start {r.get('closest_to_other_start_cm')} cm at "
                              f"{r.get('closest_to_other_start_at')} (at put-down {r.get('at_putdown_to_other_start_cm')}); "
                              f"farthest from own start {r.get('farthest_from_own_start_cm')} cm, turned back at "
                              f"{r.get('turned_back_at')}; final to target {r['to_target_cm']} / own start "
                              f"{r['to_own_start_cm']} cm")
        if not first:
            from collections import Counter
            for x in back.values():
                x["cls"] = CLASSES_5B(x)
            print(f"  classes: {dict(Counter(x['cls'] for x in back.values()))}")
        rep["models"][label] = {"back": back, "success": succ}
    name = "SWAPT_DIAG5B_FIRST.json" if first else "SWAPT_DIAG5B.json"
    (F / name).write_text(json.dumps(rep, indent=1) + "\n")
    print(f"\nDIAG 5B -> {F / name}")
    return 0


# ---------------------------------------------------------------------------------------------------------------- (d)
DEMO_ROOTS = [Path("/workspace/FastWAM/resources/RMBench/data/demo_clean/swap_T/aloha_agilex/data"),
              R / "outputs/memory_v2/press/demo_clean/swap_T/aloha_agilex/data"]


def gripper_events(g):
    """(first close, first open after it) of one gripper series: closed < 0.35 after open > 0.65; open again > 0.65."""
    opened, c = False, None
    for t, v in enumerate(g):
        if c is None:
            if v > 0.65:
                opened = True
            elif opened and v < 0.35:
                c = t
        elif v > 0.65:
            return c, t
    return c, None


def lstsq_loo(X, Y, ridge=1e-6):
    import numpy as np
    X = np.asarray(X, float)
    Y = np.asarray(Y, float)
    Xa = np.hstack([X, np.ones((len(X), 1))])
    preds = np.zeros_like(Y)
    for i in range(len(X)):
        k = np.ones(len(X), bool)
        k[i] = False
        A = Xa[k]
        W = np.linalg.solve(A.T @ A + ridge * np.eye(A.shape[1]), A.T @ Y[k])
        preds[i] = Xa[i] @ W
    return preds


def part_d():
    import h5py
    import numpy as np
    from fastwam.memory_s1.data import read_episode
    root = next((p for p in DEMO_ROOTS if p.is_dir() and any(p.glob("*.hdf5"))), None)
    if root is None:
        print("DIAG 5D: no swap_T demo hdf5 folder")
        return 2
    rows = []
    for path in sorted(root.glob("*.hdf5")):
        states = np.asarray(read_episode(path)[0], float)
        with h5py.File(path, "r") as f:
            keys = next((p for p in (("state/left_ee_poses", "state/right_ee_poses"),
                                     ("endpose/left_endpose", "endpose/right_endpose")) if all(k in f for k in p)), None)
            if keys is None:
                print(f"{path.name}: no end-effector poses; keys {list(f.keys())}")
                continue
            ee = [np.asarray(f[k], float) for k in keys]
        n = min(len(states), len(ee[0]), len(ee[1]))
        ev = [gripper_events(states[:n, 6]), gripper_events(states[:n, 13])]
        if any(c is None or r is None for c, r in ev):
            print(f"{path.name}: gripper events {ev}: skipped")
            continue
        rows.append({"demo": path.stem, "ev": ev, "states": states[:n], "ee": [ee[0][:n], ee[1][:n]]})
    rep = {"run": "plan v21 diagnostic 5(d): release pose from the other arm's grasp readings (described)",
           "demos": len(rows), "ee_keys_dims": int(rows[0]["ee"][0].shape[1]) if rows else None, "arms": {}}
    print(f"DIAG 5D: {len(rows)} demos from {root}; end-effector pose dims {rep['ee_keys_dims']}")
    for a, name in ((0, "left"), (1, "right")):
        b = 1 - a
        Y_pos = [r["ee"][a][r["ev"][a][1], :3] for r in rows]
        Y_q = np.asarray([r["ee"][a][r["ev"][a][1], 3:7] for r in rows])
        ref = Y_q[0]
        Y_q = np.asarray([q if float(np.dot(q, ref)) >= 0 else -q for q in Y_q])
        X_joint = [r["states"][r["ev"][b][0], 7 * b: 7 * b + 6] for r in rows]
        X_ee = []
        for r in rows:
            p = np.asarray(r["ee"][b][r["ev"][b][0], :7], float)
            q = p[3:7] if float(np.dot(p[3:7], ref)) >= 0 else -p[3:7]
            X_ee.append(np.concatenate([p[:3], q]))
        res = {}
        for tag, X in (("joints_of_other_arm", X_joint), ("ee_pose_of_other_arm_base_frame", X_ee)):
            pp = lstsq_loo(X, Y_pos)
            pq = lstsq_loo(X, Y_q)
            pe = [100 * float(np.linalg.norm(p - y)) for p, y in zip(pp, Y_pos)]
            ae = []
            for p, y in zip(pq, Y_q):
                p = p / (np.linalg.norm(p) or 1.0)
                ae.append(math.degrees(2 * math.acos(min(1.0, abs(float(np.dot(p, y)))))))
            res[tag] = {"position_cm": {"median": round(statistics.median(pe), 2), "mean": round(statistics.mean(pe), 2),
                                        "max": round(max(pe), 2)},
                        "angle_deg": {"median": round(statistics.median(ae), 1), "mean": round(statistics.mean(ae), 1),
                                      "max": round(max(ae), 1)}}
        copy = [100 * float(np.linalg.norm(x[:3] - y)) for x, y in zip(X_ee, Y_pos)]
        res["copy_other_grasp_position_cm"] = {"median": round(statistics.median(copy), 2), "mean": round(statistics.mean(copy), 2)}
        rep["arms"][f"{name}_release_from_{('left', 'right')[b]}_grasp"] = res
        print(f"  {name} release from {('left', 'right')[b]} grasp: {json.dumps(res)}")
    ee_pos = [rep["arms"][k]["ee_pose_of_other_arm_base_frame"]["position_cm"]["mean"] for k in rep["arms"]]
    jt_pos = [rep["arms"][k]["joints_of_other_arm"]["position_cm"]["mean"] for k in rep["arms"]]
    rep["card26_condition_d (mean position error, both arms)"] = {
        "ee_below_2.5cm": all(x < 2.5 for x in ee_pos), "joints_at_least_twice_ee": all(j >= 2 * e for j, e in zip(jt_pos, ee_pos))}
    (F / "SWAPT_DIAG5D.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(f"DIAG 5D -> {F / 'SWAPT_DIAG5D.json'}; card 26 part (d): {rep['card26_condition_d (mean position error, both arms)']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("part", choices=("b", "d"))
    ap.add_argument("--first", type=int, default=0)
    a = ap.parse_args()
    return part_b(a.first) if a.part == "b" else part_d()


if __name__ == "__main__":
    raise SystemExit(main())
