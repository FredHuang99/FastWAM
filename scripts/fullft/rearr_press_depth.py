"""Plan v20 section 8 item 1 (11-24, Opus): rearrange "never pressed" episodes -- did the left hand reach the button?
Read-only, CPU, zero GPU: the A40 episodes already there. Descriptive (decides whether card 6 opens).
What the logs hold (scripts/memory_s1/deploy_policy.py, per executed target): joint_details.left.ee_pose (world pose of
the configured end-effector link, not the fingertip centre), objects_after.button (the button's ROOT pose = its base;
the cap's travel, i.e. the press depth, is NOT logged; the env counts a press when the button joint is below -5 mm,
RMBench envs/rearrange_blocks.py check_button_pressed), press_cnt / press_flag, and object_contacts (finger-object
contact at that instant; for an articulation the alias may cover only the root link -> 'unknown' is printed as such).
Per episode, with the classes of rearr_split.py:
  never pressed   closest approach: min over targets of the left EE's horizontal distance to the button base, and at
                  that target the height of the EE above the base; the lowest EE height while within 4 cm
                  horizontally; any left-finger contact with the button; for body-record models the left-arm 'bottom'
                  entry of the last decision (frame) and the EE geometry at that frame
  pressed (ref.)  the same geometry at the first target where press_cnt reached 1 (the press the env counted)
Prints medians / quartiles per class; writes outputs/fullft/REARR_PRESS_DEPTH.json.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/rearr_press_depth.py [FOLDER:LABEL ...]
Default: e6:rearrange_arprop_e30 e6:rearrange_ar_e30 e16:rearrange_clock_e30.
"""
from __future__ import annotations

import importlib.util
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
TASK = "rearrange_blocks"
DEFAULT = ["e6:rearrange_arprop_e30", "e6:rearrange_ar_e30", "e16:rearrange_clock_e30"]
NEAR = 0.04


def _split():
    spec = importlib.util.spec_from_file_location("rearr_split", HERE / "rearr_split.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rows(p: Path):
    out = []
    if p.exists():
        for x in p.read_text().splitlines():
            if x.strip():
                try:
                    out.append(json.loads(x))
                except json.JSONDecodeError:
                    pass
    return out


def geom(r):
    """(horizontal distance, height of the left EE above the button base) after this target, or None."""
    ee = ((r.get("joint_details") or {}).get("left") or {}).get("ee_pose")
    b = (r.get("objects_after") or {}).get("button")
    if not ee or not isinstance(b, dict) or "p" not in b:
        return None
    e, p = ee["p"], b["p"]
    return ((e[0] - p[0]) ** 2 + (e[1] - p[1]) ** 2) ** 0.5, e[2] - p[2]


def contact(r):
    c = (((r.get("object_contacts") or {}).get("objects") or {}).get("button") or {}).get("by_side") or {}
    return c.get("left")


def q(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return "n 0"
    k = len(xs)
    return (f"median {statistics.median(xs):.3f} (q1 {xs[k // 4]:.3f}, q3 {xs[(3 * k) // 4]:.3f}, min {xs[0]:.3f}, "
            f"max {xs[-1]:.3f}, n {k})")


def episode(d: Path, split):
    acts = rows(d / "executed_actions.jsonl")
    res = d / "result.json"
    if not acts or not res.exists():
        return None
    ok = bool(json.loads(res.read_text()).get("success"))
    cls, _ = split.classify(acts, ok)
    g = [geom(r) for r in acts]
    out = {"cls": cls, "targets": len(acts)}
    if not any(g):
        out["why"] = "no ee_pose / button pose in executed_actions.jsonl"
        return out
    t1 = next((i for i, r in enumerate(acts)
               if isinstance((r.get("objects_after") or {}).get("press_cnt"), (int, float))
               and r["objects_after"]["press_cnt"] >= 1), None)
    if t1 is not None:
        out["at_counted_press"] = {"target": t1, "dxy": g[t1][0] if g[t1] else None, "dz": g[t1][1] if g[t1] else None}
    i_min = min((i for i, x in enumerate(g) if x), key=lambda i: g[i][0])
    out["closest"] = {"target": i_min, "dxy": g[i_min][0], "dz": g[i_min][1]}
    near = [x[1] for x in g if x and x[0] < NEAR]
    out["lowest_dz_within_4cm"] = min(near) if near else None
    cs = [contact(r) for r in acts]
    out["left_contact_with_button"] = (True if any(c is True for c in cs) else
                                       False if any(c is False for c in cs) else "unknown")
    decs = rows(d / "decisions.jsonl")
    if decs and decs[-1].get("ledger") is not None:
        bottoms = [int(e[0]) for e in (decs[-1].get("ledger") or []) if int(e[1]) == 0 and e[2] == "bottom"]
        out["left_bottom_entries"] = bottoms
        if bottoms:
            f = min(max(bottoms[-1] - 1, 0), len(g) - 1)      # entry frame = executed target index (frame f -> row f-1)
            out["at_last_bottom_entry"] = {"frame": bottoms[-1], "dxy": g[f][0] if g[f] else None,
                                           "dz": g[f][1] if g[f] else None}
    return out


def main():
    split = _split()
    items = sys.argv[1:] or DEFAULT
    report = {}
    for item in items:
        folder, label = item.split(":", 1)
        root = O / folder / label / "on" / TASK
        per = {}
        for d in sorted(root.glob("seed_*")):
            if d.is_dir() and d.name[5:].isdigit():
                e = episode(d, split)
                if e:
                    per[d.name[5:]] = e
        if not per:
            print(f"\n== {item}: no episodes")
            continue
        groups = defaultdict(list)
        for s, e in per.items():
            groups["never pressed" if e["cls"].startswith("never pressed") else
                   "pressed (env counted >= 1 press)" if "at_counted_press" in e else e["cls"]].append(e)
        print(f"\n== {item}: {len(per)} episodes")
        for gname in ("never pressed", "pressed (env counted >= 1 press)"):
            es = groups.get(gname, [])
            print(f"  -- {gname}: {len(es)}")
            if not es:
                continue
            if gname.startswith("never"):
                print(f"     closest approach, horizontal EE-button distance (m): {q([e.get('closest', {}).get('dxy') for e in es])}")
                print(f"     EE height above the button base there (m):           {q([e.get('closest', {}).get('dz') for e in es])}")
                print(f"     lowest EE height while within 4 cm (m):              {q([e.get('lowest_dz_within_4cm') for e in es])}")
                print(f"     episodes never within 4 cm: {sum(e.get('lowest_dz_within_4cm') is None for e in es)}")
                cc = defaultdict(int)
                for e in es:
                    cc[str(e.get("left_contact_with_button"))] += 1
                print(f"     left finger touched the button (any target): {dict(cc)}")
                lb = [e for e in es if "left_bottom_entries" in e]
                if lb:
                    print(f"     body record: a left 'bottom' entry at the last decision in {sum(bool(e['left_bottom_entries']) for e in lb)}/{len(lb)}")
                    print(f"       at that entry: dxy {q([e.get('at_last_bottom_entry', {}).get('dxy') for e in lb])}")
                    print(f"                      dz  {q([e.get('at_last_bottom_entry', {}).get('dz') for e in lb])}")
            else:
                print(f"     at the counted press: dxy {q([e['at_counted_press']['dxy'] for e in es])}")
                print(f"                           dz  {q([e['at_counted_press']['dz'] for e in es])}")
            miss = sum("why" in e for e in es)
            if miss:
                print(f"     {miss} episodes without the poses in their logs")
        report[item] = per
    (F / "REARR_PRESS_DEPTH.json").write_text(json.dumps(report, indent=1) + "\n")
    print("\nREARR PRESS DEPTH REPORT: written outputs/fullft/REARR_PRESS_DEPTH.json (the cap's travel is not logged: "
          "geometry of the EE link against the button base only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
