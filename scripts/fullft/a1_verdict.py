"""Plan v19 A1 verdict (11-22, Opus). The reading was registered in the A1 cards' hypothesis text (queue5_tasks.yaml,
commit 5dcb216, 11-22 01:51, before any A1 episode); this script applies it unchanged. Read-only, CPU.
  battery_ar e30 executing 16 of the 32 predicted steps instead of 8, battery_try scenes 1-100 (official seed-42 bank),
  paired by scene with closed_loop/e6 battery_ar_e30 (execute 8).
  D = success(execute 16) - success(execute 8), paired bootstrap 95 % CI (10,000 resamples of the paired scenes, seed 0);
  SESOI -0.20:
    CI upper < 0 and D <= -0.20 -> EXECUTION LENGTH MATTERS
    CI lower > -0.20            -> NOT EXECUTION LENGTH
    otherwise                   -> UNCERTAIN (pre-set extension: both with MWAM_NOISE_SALT=r2)
  execute 32: descriptive only (dose).
Fewer than 100 paired scenes -> WAIT (no verdict). Prints the verdict line and writes outputs/fullft/A1_VERDICT.json.
  /opt/mwam/bin/python scripts/fullft/a1_verdict.py
"""
from __future__ import annotations

import importlib.util
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop")
F = Path("/workspace/FastWAM-memory2/outputs/fullft")
SESOI = -0.20


def e1():
    spec = importlib.util.spec_from_file_location("e1_verdict", HERE / "e1_verdict.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def results(folder: Path, label: str, seeds):
    out = {}
    for s in seeds:
        res = folder / label / "on" / "battery_try" / f"seed_{s}" / "result.json"
        if res.exists():
            out[s] = bool(json.loads(res.read_text()).get("success"))
    return out


def paired_ci(a, b, n=10_000, seed=0):
    """D = mean(a) - mean(b) over paired scenes; percentile CI of the paired bootstrap."""
    k = len(a)
    d = sum(a) / k - sum(b) / k
    rng = random.Random(seed)
    stats = []
    for _ in range(n):
        idx = [rng.randrange(k) for _ in range(k)]
        stats.append(sum(a[i] - b[i] for i in idx) / k)
    stats.sort()
    return d, stats[int(0.025 * n)], stats[int(0.975 * n) - 1]


def verdict(d, lo, hi):
    if hi < 0 and d <= SESOI:
        return "EXECUTION LENGTH MATTERS"
    if lo > SESOI:
        return "NOT EXECUTION LENGTH"
    return "UNCERTAIN"


def main():
    seeds = e1().seeds_of("battery_try", 100)
    base = results(O / "e6", "battery_ar_e30", seeds)
    x16 = results(O / "a1", "battery_ar_e30_x16", seeds)
    x32 = results(O / "a1", "battery_ar_e30_x32", seeds)
    out = {"registered": "5dcb216 (A1 card hypothesis)", "sesoi": SESOI,
           "finished": {"execute8": len(base), "execute16": len(x16), "execute32": len(x32)}}
    common = [s for s in seeds if s in base and s in x16]
    if len(common) < 100:
        out["verdict"] = f"WAIT ({len(common)} of 100 paired scenes)"
    else:
        a, b = [int(x16[s]) for s in common], [int(base[s]) for s in common]
        d, lo, hi = paired_ci(a, b)
        out.update(verdict=verdict(d, lo, hi), execute16=sum(a), execute8=sum(b), D=round(d, 4),
                   ci95=[round(lo, 4), round(hi, 4)], only16=sum(x and not y for x, y in zip(a, b)),
                   only8=sum(y and not x for x, y in zip(a, b)))
    c32 = [s for s in seeds if s in base and s in x32]
    if c32:
        a, b = [int(x32[s]) for s in c32], [int(base[s]) for s in c32]
        d, lo, hi = paired_ci(a, b)
        out["execute32_descriptive"] = {"scenes": len(c32), "execute32": sum(a), "execute8": sum(b), "D": round(d, 4),
                                        "ci95": [round(lo, 4), round(hi, 4)]}
    (F / "A1_VERDICT.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    print(f"A1 VERDICT: {out['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
