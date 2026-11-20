"""Plan v18 N0 noise calibration (11-21 01:25 BJ, Opus; user approved 00:58). Read-only, descriptive: how much do the
press metrics move when ONLY the diffusion noise changes (same model press_count e30, same scenes, same machine)?
The result sets the zero-effect band that later readings use (plan v18, reading method step 2).
Pairs (same scenes, different noise):
  g1 (default noise, scenes 1-50)  vs nz2 (MWAM_NOISE_SALT=r2, 1-50) and nz3 (r3, 1-50); nz2 vs nz3
  sel (default, 51-100)            vs rep (r2, 51-100)   (both already exist)
Per pair: first-button over-press rate difference with a paired-bootstrap 95 % CI, discordant pairs, mean e1 and
mean extra presses max(e1, 0) differences, success difference. Summary: the largest |difference| seen per metric.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/noise_band.py      Writes outputs/fullft/NOISE_BAND.json.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("oracle_verdict", HERE / "oracle_verdict.py")
ov = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ov)

PAIRS = [(("g1", "press_count_e30"), ("nz2", "press_count_e30")), (("g1", "press_count_e30"), ("nz3", "press_count_e30")),
         (("nz2", "press_count_e30"), ("nz3", "press_count_e30")), (("sel", "press_count_e30"), ("rep", "press_count_e30"))]


def main():
    out, worst = {"pairs": {}}, {}
    for a, b in PAIRS:
        A, B = ov.merged(a), ov.merged(b)
        seeds, pairs = ov.paired(B, A)
        name = f"{a[0]} vs {b[0]}"
        if len(pairs) < 45:
            out["pairs"][name] = {"pairs": len(pairs), "note": "not enough pairs yet"}
            print(f"{name}: {len(pairs)} pairs (waiting)")
            continue
        rate = lambda ps, i: sum(p[i] >= 1 for p in ps) / len(ps)                      # noqa: E731
        dfun = lambda ps: rate(ps, 0) - rate(ps, 1)                                     # noqa: E731
        lo, hi = ov.boot_ci(pairs, dfun)
        mean = lambda ps, i, f: sum(f(p[i]) for p in ps) / len(ps)                     # noqa: E731
        row = {"pairs": len(pairs), "over_a": sum(p[1] >= 1 for p in pairs), "over_b": sum(p[0] >= 1 for p in pairs),
               "over_rate_D": round(dfun(pairs), 3), "over_rate_ci": [round(lo, 3), round(hi, 3)],
               "discordant": [sum(p[1] >= 1 > p[0] for p in pairs), sum(p[0] >= 1 > p[1] for p in pairs)],
               "e1_mean_D": round(mean(pairs, 0, lambda x: x) - mean(pairs, 1, lambda x: x), 3),
               "extra_mean_D": round(mean(pairs, 0, lambda x: max(x, 0)) - mean(pairs, 1, lambda x: max(x, 0)), 3),
               "success_D": sum(bool(B[s].get("success")) for s in seeds) - sum(bool(A[s].get("success")) for s in seeds)}
        out["pairs"][name] = row
        for k in ("over_rate_D", "e1_mean_D", "extra_mean_D", "success_D"):
            worst[k] = max(worst.get(k, 0), abs(row[k]))
        print(f"{name}: {row}")
    out["largest_abs_difference"] = worst
    print(f"largest |difference| under noise only: {worst}")
    (ov.F / "NOISE_BAND.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
