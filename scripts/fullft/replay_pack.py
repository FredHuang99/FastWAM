"""Plan v12 AL1 (Opus checklist 2-3): pack reference episodes for a target replay, and compare a replay with them.

  pack --name NAME --folders F [F ...] --label L [--mode on] --task T [--bank BANK --from-scene K --limit N | --seeds S ...]
      -> outputs/fullft/align/replay/<NAME>.json.gz: per episode (key "<task>/<seed>") the executed targets, and per
         executed target the joint state after it (physical_after) and the object positions after it, plus success
         and progress (queue5 stage analysis). Several --task runs into the same NAME merge (--merge).
  compare --pack PATH --folder F --label L --name NAME [--self-check]
      the replay episodes (online.py run --checkpoint replay:PATH, label L, in folder F) against the pack:
      per episode: outcome equal (same progress and success), max object position deviation over the steps both
      have (mm), max joint deviation, first target whose object deviation > 1 mm.
      Reading (plan v12 F.1 AL1, written before any replay): CONSISTENT = outcome equal in >= 95 % of the episodes
      (38/40) and the median of the per-episode max object deviation <= 2 mm; INCONSISTENT = outcome equal in <= 85 %
      (34/40) or that median > 10 mm; otherwise PARTIAL. --self-check (the tool's own acceptance: a machine replaying
      its own episodes): every outcome equal and every max object deviation <= 2 mm.
CPU only. Episode files are read, never written.
"""
from __future__ import annotations

import argparse
import gzip
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(os.environ.get("MWAM_REPO", "/workspace/FastWAM-memory2"))
O = REPO / "outputs/memory_v2"
OUT = REPO / "outputs/fullft/align/replay"
BJ = timezone(timedelta(hours=8))
spec = importlib.util.spec_from_file_location("queue5", REPO / "scripts/memory_v2/queue5.py")
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)


def resolve(p):
    p = Path(p)
    return p if p.is_absolute() else O / p


def bank_seeds(bank, task, start, limit):
    rows = []
    for f in sorted(resolve(bank).glob("*.json")):
        v = json.loads(f.read_text())
        sc = v.get("scenes") if isinstance(v, dict) else v
        rows += [s for s in (sc if isinstance(sc, list) else []) if s["task"] == task]
    seen, out = set(), []
    for s in sorted(rows, key=lambda s: (s.get("ordinal", 0), int(s["seed"]))):
        if int(s["seed"]) not in seen:
            seen.add(int(s["seed"]))
            out.append(int(s["seed"]))
    out = out[start - 1:]
    return out[:limit] if limit else out


def steps(path):
    targets, joints, objects = [], [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            targets.append([float(x) for x in r["target"]])        # EXACT (11-11: rounding to 7 decimals changed
            #                                                         the float32 targets by an ulp; the replay drifted mm)
            joints.append([round(float(x), 7) for x in (r.get("physical_after") or [])])
            objects.append({k: [round(float(x), 7) for x in v["p"][:3]] for k, v in (r.get("objects_after") or {}).items()
                            if isinstance(v, dict) and isinstance(v.get("p"), list)})
    return targets, joints, objects


def cmd_pack(args):
    folders = [str(resolve(f)) for f in args.folders]
    eps = q.episodes(folders, args.label, modes=[args.mode], tasks=[args.task])
    want = set(bank_seeds(args.bank, args.task, args.from_scene, args.limit)) if args.bank else \
        {int(s.split(":")[-1]) for s in args.seeds}
    path = OUT / f"{args.name}.json.gz"
    pack = {"meta": {"name": args.name, "folders": folders, "label": args.label, "mode": args.mode,
                     "created": f"{datetime.now(BJ):%F %T}"}, "episodes": {}}
    if args.merge and path.exists():
        with gzip.open(path, "rt", encoding="utf-8") as f:
            pack = json.load(f)
    n = 0
    for (task, mode, seed), a in sorted(eps.items()):
        if want and int(seed) not in want:
            continue
        d = Path(a["dir"])
        t, j, o = steps(d / "executed_actions.jsonl")
        pack["episodes"][f"{task}/{int(seed)}"] = {"targets": t, "joints": j, "objects": o,
                                                   "success": bool(a.get("success")), "progress": q.progress(task, a),
                                                   "source": str(d)}
        n += 1
    missing = sorted(want - {int(k.split("/")[1]) for k in pack["episodes"] if k.startswith(args.task + "/")})
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(pack, f)
    print(f"PACK {path}: +{n} {args.task} episodes ({len(pack['episodes'])} in total, {path.stat().st_size / 1e6:.1f} MB); "
          f"wanted but missing: {missing}")


def cmd_compare(args):
    with gzip.open(args.pack, "rt", encoding="utf-8") as f:
        pack = json.load(f)
    eps = q.episodes([str(resolve(args.folder))], args.label, modes=["on"])
    rows = []
    for (task, mode, seed), a in sorted(eps.items()):
        ref = pack["episodes"].get(f"{task}/{int(seed)}")
        if ref is None:
            continue
        t, j, o = steps(Path(a["dir"]) / "executed_actions.jsonl")
        n = min(len(o), len(ref["objects"]))
        worst, first, jworst = 0.0, None, 0.0
        for i in range(n):
            d = 0.0
            for name in set(o[i]) & set(ref["objects"][i]):
                d = max(d, max(abs(x - y) for x, y in zip(o[i][name], ref["objects"][i][name])) * 1000)
            worst = max(worst, d)
            if first is None and d > 1.0:
                first = i
            if j[i] and ref["joints"][i]:
                jworst = max(jworst, max(abs(x - y) for x, y in zip(j[i], ref["joints"][i])))
        same = abs(q.progress(task, a) - ref["progress"]) < 1e-9 and bool(a.get("success")) == ref["success"]
        rows.append({"task": task, "seed": int(seed), "outcome_equal": same, "max_object_mm": worst,
                     "first_over_1mm": first, "max_joint": jworst, "steps": [len(o), len(ref["objects"])],
                     "progress": [q.progress(task, a), ref["progress"]], "success": [bool(a.get("success")), ref["success"]]})
    print(f"REPLAY COMPARE {args.name}: replay {args.folder} {args.label} vs pack {args.pack}")
    print("| task | seed | outcome equal | max object dev (mm) | first target > 1 mm | max joint dev | targets replay / ref "
          "| progress replay / ref |")
    for r in rows:
        print(f"| {r['task']} | {r['seed']} | {r['outcome_equal']} | {r['max_object_mm']:.3f} | {r['first_over_1mm']} | "
              f"{r['max_joint']:.2e} | {r['steps'][0]} / {r['steps'][1]} | {r['progress'][0]:.3f} / {r['progress'][1]:.3f} |")
    n = len(rows)
    if not n:
        print("REPLAY READING: no replayed episode matches the pack"); raise SystemExit(1)
    equal = sum(r["outcome_equal"] for r in rows)
    med = sorted(r["max_object_mm"] for r in rows)[n // 2]
    if args.self_check:
        ok = equal == n and all(r["max_object_mm"] <= 2.0 for r in rows)
        reading = "SELF-CHECK PASS" if ok else "SELF-CHECK FAIL"
    elif equal >= 0.95 * n and med <= 2.0:
        reading = "CONSISTENT"
    elif equal <= 0.85 * n or med > 10.0:
        reading = "INCONSISTENT"
    else:
        reading = "PARTIAL"
    out = OUT / f"COMPARE_{args.name}_{datetime.now(BJ):%Y%m%d_%H%M}.json"
    OUT.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"name": args.name, "reading": reading, "episodes": n, "outcome_equal": equal,
                               "median_max_object_mm": med, "rows": rows}, indent=1) + "\n")
    print(f"episodes {n}; outcome equal {equal}; median of the max object deviation {med:.3f} mm; report {out}")
    print(f"REPLAY READING {args.name}: {reading}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pack")
    p.add_argument("--name", required=True)
    p.add_argument("--folders", nargs="+", required=True)
    p.add_argument("--label", required=True)
    p.add_argument("--mode", default="on")
    p.add_argument("--task", required=True)
    p.add_argument("--bank", default="")
    p.add_argument("--from-scene", type=int, default=1)
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--seeds", nargs="*", default=[])
    p.add_argument("--merge", action="store_true")
    c = sub.add_parser("compare")
    c.add_argument("--pack", required=True)
    c.add_argument("--folder", required=True)
    c.add_argument("--label", required=True)
    c.add_argument("--name", required=True)
    c.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    {"pack": cmd_pack, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    main()
