"""Plan v15 E21 CLOCK-read verdict (registered by Fable 11-19 noon in plan v15 section 3; the user said 13:21 "按照
fable 的计划去执行"; this script written 11-19 14:45 BJ, before any E21 closed-loop result exists). Read-only.

Hypothesis: the clock arm (ar2_clock e30) reads the joint states inside its tokens, not the timestamps.
A40. Untreated = the clock arm's no-stress swap episodes of E5 (closed_loop/e5, label ar2_clock_e30, scenes 1-50).
Test-time interventions (closed_loop/e21, swap_blocks scenes 1-50, no stress; same scenes and noise as untreated):
  (a) ar2_clock_e30_ts1.5   timestamps x1.5 (MWAM_CLOCK_SCALE=1.5)
  (b) ar2_clock_e30_ts0.5   timestamps x0.5
  (c) ar2_clock_e30_clkoff  all clock tokens off (MWAM_CLOCK=off); also on put_back_block 1-50
  (d) ar2_clock_e30_clkfreeze  every token's joint state = the current frame's, timestamps kept (MWAM_CLOCK=freeze)
  (e) ar2_clock_e30_clkflat    every timestamp = the middle sample's, joint states kept (MWAM_CLOCK=flat)
Registered reading (plan v15 E21, verbatim in meaning). Floor: untreated >= 45/50.
  time code: (a), (b), (e) all >= 45/50 -> TIME CODE NOT READ; (a) or (b) <= 35/50 AND x1.5's failures mostly
    "pressed before s3" (early) AND x0.5's mostly "kept moving / idle after s3" (late) -> TIME CODE READ; else PARTIAL.
  dependence: (c) <= 10/50 -> DEPENDS; >= 40/50 -> NOT DEPENDENT; else undecided.
  content: (d) <= 10/50 -> READS CONTENT; >= 40/50 -> DOES NOT READ CONTENT; else undecided.
  put (c): reported only (the written expectation: still >= 45/50, put reads the recent window).
  A cell with < 48/50 finished gives no word (WAIT).
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e21_verdict.py
Writes outputs/fullft/E21_VERDICT.json.
"""
from __future__ import annotations

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
e5 = module("e5_verdict", "e5_verdict.py")
CLOCK = "ar2_clock_e30"
ARMS = {"a": "ts1.5", "b": "ts0.5", "c": "clkoff", "d": "clkfreeze", "e": "clkflat"}


def cell(folder, label, task, seeds):
    ep = e5.finished(folder, label, task, seeds)
    fails = Counter(k or "unclassified" for ok, k in ep.values() if not ok)
    return {"finished": len(ep), "success": sum(ok for ok, _ in ep.values()), "failures": dict(fails),
            "ok": {s: ok for s, (ok, _) in ep.items()}}


def direction(f):
    early, late = f.get("pressed before s3", 0), f.get("kept moving", 0) + f.get("idle after s3", 0)
    return "early" if early > late else "late" if late > early else "none"


def main():
    seeds = e1.seeds_of("swap_blocks", 50)
    put = e1.seeds_of("put_back_block", 50)
    base = cell(O / "e5", CLOCK, "swap_blocks", seeds)
    rows = {"untreated": base}
    for k, tag in ARMS.items():
        rows[k] = cell(O / "e21", f"{CLOCK}_{tag}", "swap_blocks", seeds)
    rows["c_put"] = cell(O / "e21", f"{CLOCK}_clkoff", "put_back_block", put)
    for k, r in rows.items():
        common = sorted(set(r["ok"]) & set(base["ok"]))
        r["vs_untreated"] = {"n": len(common), "only_this": sum(r["ok"][s] and not base["ok"][s] for s in common),
                             "only_untreated": sum(base["ok"][s] and not r["ok"][s] for s in common)}
        print(f"{k:10s} {r['success']:3d}/{r['finished']:2d} finished; failures {r['failures']}; vs untreated "
              f"{r['vs_untreated']}")
    done = lambda k: rows[k]["finished"] >= 48                                         # noqa: E731
    s = lambda k: rows[k]["success"]                                                   # noqa: E731
    out = {"rows": {k: {x: v for x, v in r.items() if x != "ok"} for k, r in rows.items()}}
    if not done("untreated"):
        out["floor"] = "WAIT"
    else:
        out["floor"] = s("untreated") >= 45
    if out["floor"] is not True:
        out.update(time_code="NO READING (floor)", dependence="NO READING (floor)", content="NO READING (floor)")
    else:
        if not all(done(k) for k in "abe"):
            out["time_code"] = "WAIT"
        elif all(s(k) >= 45 for k in "abe"):
            out["time_code"] = "TIME CODE NOT READ"
        elif (min(s("a"), s("b")) <= 35 and direction(rows["a"]["failures"]) == "early"
              and direction(rows["b"]["failures"]) == "late"):
            out["time_code"] = "TIME CODE READ"
        else:
            out["time_code"] = "PARTIAL"
        out["dependence"] = ("WAIT" if not done("c") else "DEPENDS" if s("c") <= 10
                             else "NOT DEPENDENT" if s("c") >= 40 else "UNDECIDED")
        out["content"] = ("WAIT" if not done("d") else "READS CONTENT" if s("d") <= 10
                          else "DOES NOT READ CONTENT" if s("d") >= 40 else "UNDECIDED")
    out["directions"] = {k: direction(rows[k]["failures"]) for k in ("a", "b")}
    out["put_clock_off"] = f"{s('c_put')}/{rows['c_put']['finished']} (reported only; expectation >= 45/50)"
    print(f"E21 VERDICT: time code {out['time_code']}; dependence {out['dependence']}; content {out['content']}; "
          f"put with clock off {out['put_clock_off']}")
    (F / "E21_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
