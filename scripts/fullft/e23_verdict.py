"""Plan v15 E23 CLOCK-curve verdict (registered by Fable 11-19 noon in plan v15 section 3; user 13:21 "按照 fable 的
计划去执行"; this script written 11-19 15:20 BJ, before any closed-loop result of the clock arm's e10 exists). Read-only.
Hypothesis to separate: the ledger reaches swap 77/99 at e10 while AR has 6/99 (A40 learning curve); is that speed from
the body-state content or from the event index? A40, swap_blocks scenes 1-100: clock e10 (closed_loop/e23, label
ar2_clock_e10) paired with the ledger e10 (closed_loop/lc, label ar2_prop_e10) on common scenes.
Registered reading: ledger >= clock + 15/100 with sign p < 0.05 -> EVENT LEARNS FASTER; |diff| <= 8/100 -> SAME SPEED;
otherwise PARTIAL. Floor: both >= 95 finished.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/e23_verdict.py      Writes outputs/fullft/E23_VERDICT.json.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
spec = importlib.util.spec_from_file_location("e1_verdict", HERE / "e1_verdict.py")
e1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e1)


def results(folder, label, seeds):
    out = {}
    for s in seeds:
        r = folder / label / "on" / "swap_blocks" / f"seed_{s}" / "result.json"
        if r.exists():
            out[s] = bool(json.loads(r.read_text()).get("success"))
    return out


def main():
    seeds = e1.seeds_of("swap_blocks", 100)
    clock, ledger = results(O / "e23", "ar2_clock_e10", seeds), results(O / "lc", "ar2_prop_e10", seeds)
    common = sorted(set(clock) & set(ledger))
    sc, sl = sum(clock[s] for s in common), sum(ledger[s] for s in common)
    a = sum(ledger[s] and not clock[s] for s in common)
    b = sum(clock[s] and not ledger[s] for s in common)
    p = e1.sign_p(a, b)
    if len(clock) < 95 or len(ledger) < 95:
        word = f"WAIT / NO READING (finished: clock {len(clock)}, ledger {len(ledger)}; need >= 95)"
    elif sl - sc >= 15 and p < 0.05:
        word = "EVENT LEARNS FASTER"
    elif abs(sl - sc) <= 8:
        word = "SAME SPEED"
    else:
        word = "PARTIAL"
    print(f"E23 swap e10 on {len(common)} common scenes: ledger {sl}, clock {sc}; only ledger {a}, only clock {b}, "
          f"sign p {p:.4f} -> {word}")
    (F / "E23_VERDICT.json").write_text(json.dumps({"verdict": word, "n": len(common), "ledger": sl, "clock": sc,
                                                    "only_ledger": a, "only_clock": b, "p": p}, indent=1) + "\n")


if __name__ == "__main__":
    main()
