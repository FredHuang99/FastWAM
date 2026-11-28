"""Plan v22 card 31 (press_cd), 11-28 Opus: the countdown events file. CPU, runs in mwam5090 (the press_button demos
are there). Written before any press_cd training.
  1 the events file press_told trained on (events_press_button_v3c.json; fetched from the relay diag/press_v3c if
    missing, as press_told_text.py)
  2 per training demo: every 'bottom' / 'top' entry gets the button whose x the pressing arm's end-effector is nearest
    at that frame (history.press_button_of: left -0.15 / middle 0.0 / check 0.15; > 5 cm from all = unclear -> stop),
    and history.annotate_remaining with the demo's own counts N1 / N2 (its 'bottom' presses of the left / middle button,
    as press_told_text.py; no annotation): 'remaining' = N_b - presses of b made so far (this one included)
  3 checks (all must hold, else stop, nothing written): counts equal TOLD_TEXT.json's (when present); per demo and
    button the first press reads N_b - 1 and the last 0; no 'remaining' on check-button or gripper entries
  4 outputs/fullft/events/events_press_button_v3d.json = the v3c file with the annotated entries (every other key
    unchanged: the event rule's thresholds stay those of v3c) + PRESS_CD_EVENTS.json (checks, sha256); --relay puts the
    events file to the relay as diag/press_button_v3d (the new H200's job fetches data.events=[..._v3d.json] there)
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_cd_events.py [--relay]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "src"))
R = Path("/workspace/FastWAM-memory2")
ROOT = R / "outputs/memory_v2/press/dense_press_button_v1"
EV_IN = R / "outputs/fullft/events/events_press_button_v3c.json"
EV_OUT = R / "outputs/fullft/events/events_press_button_v3d.json"
TOLD = R / "outputs/fullft/press_told/TOLD_TEXT.json"
UNCLEAR = 0.05


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--relay", action="store_true")
    a = ap.parse_args()
    import events_stats as es
    from fastwam.fullft.history import BUTTON_X, annotate_remaining, press_button_of
    hf = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else sys.executable
    if not EV_IN.exists():
        inbox = R / "outputs/fullft/relay_in/press_v3c"
        inbox.mkdir(parents=True, exist_ok=True)
        subprocess.run([hf, str(REPO / "scripts/memory_v2/migrate/relay.py"), "get", "--prefix", "diag/press_v3c",
                        "--out", str(inbox)])
        got = inbox / EV_IN.name
        if not got.exists():
            print(f"[cd] STOP: {EV_IN} missing here and not on the relay (diag/press_v3c)")
            return 1
        EV_IN.parent.mkdir(parents=True, exist_ok=True)
        EV_IN.write_bytes(got.read_bytes())
    doc = json.loads(EV_IN.read_text())
    eps = doc.get("episodes", doc)
    records = json.loads((ROOT / "RECORDS.json").read_text())
    demos = {f"press_button/{p.stem}": p for p in es.demo_files("press_button")}
    told = json.loads(TOLD.read_text()).get("counts", {}) if TOLD.exists() else {}
    problems, counts, out_eps = [], {}, dict(eps)
    for r in records:
        eid = r["episode_id"]
        path = demos.get(eid) or (Path(r["raw"]) if r.get("raw") and Path(r["raw"]).exists() else None)
        if path is None or eid not in eps:
            problems.append(f"{eid}: {'no demo file' if path is None else 'no events'}")
            continue
        _, pos = es.read_demo(path)

        def button_of(e, pos=pos, eid=eid):
            x = float(pos[min(int(e["frame"]), len(pos) - 1)][int(e["arm"])][0])
            b = press_button_of(x)
            if abs(x - BUTTON_X[b - 1]) > UNCLEAR:
                problems.append(f"{eid}: a press entry at x {x:.3f} is near no button")
            return b
        n = {1: 0, 2: 0}
        for e in eps[eid]:
            if e.get("kind") == "bottom":
                b = button_of(e)
                if b in n:
                    n[b] += 1
        counts[eid] = [n[1], n[2]]
        if told.get(eid) is not None and list(told[eid])[:2] != [n[1], n[2]]:
            problems.append(f"{eid}: counts {n} differ from TOLD_TEXT.json {told[eid]}")
        ann = annotate_remaining(eps[eid], n, button_of)
        for b in (1, 2):
            rs = [e["remaining"] for e in ann if e.get("kind") == "bottom" and e.get("button") == b]
            if rs and (rs[0] != n[b] - 1 or rs[-1] != 0):
                problems.append(f"{eid}: button {b} countdown {rs} (N {n[b]})")
        if any(e.get("remaining") is not None for e in ann if e.get("kind") in ("close", "open") or e.get("button") == 3):
            problems.append(f"{eid}: a countdown on a check-button or gripper entry")
        out_eps[eid] = ann
    print(f"[cd] {len(counts)} demos; pairs {sorted({tuple(v) for v in counts.values()})}")
    if problems:
        print("[cd] STOP:\n  " + "\n  ".join(problems[:20]))
        return 1
    out = dict(doc)
    if "episodes" in doc:
        out["episodes"] = out_eps
    else:
        out = out_eps
    EV_OUT.write_text(json.dumps(out) + "\n")
    rep = {"from": str(EV_IN), "from_sha256": sha(EV_IN), "events_sha256": sha(EV_OUT), "demos": len(counts),
           "counts": counts, "checks": "counts = TOLD_TEXT.json; first press N_b - 1, last 0; none on check / gripper"}
    (R / "outputs/fullft/press_told/PRESS_CD_EVENTS.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(f"[cd] written {EV_OUT} (sha256 {rep['events_sha256'][:16]})")
    if a.relay:
        rc = subprocess.run([hf, str(REPO / "scripts/memory_v2/migrate/relay.py"), "put", str(EV_OUT),
                             "--prefix", "diag/press_button_v3d"]).returncode
        print(f"[cd] relay put exit {rc}")
        return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
