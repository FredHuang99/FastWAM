"""Plan v17 second task, evaluation only (Fable review of plan v16, part 2 item 1: "the cheapest second task: turn the
record delay on the swap task"; registered 11-20 22:50 BJ by Opus before any of these runs exists). Read-only.

Model ar2_prop_e30 (the swap / put ledger model; trained with its own lag), swap_blocks scenes 1-50, default noise,
A100 (group A100 + A40). Runs in closed_loop/swaplag: label ar2_prop_e30 (as trained) and ar2_prop_e30_lagL with
MWAM_LEDGER_LAG = L for L = 16, 32, 64 (every ledger entry visible L frames after its confirmation).
Prediction of the thesis (Fable): in swap the next decision that depends on the record comes only after the arm has
withdrawn (tens of frames), so the first two levels are harmless and only a delay longer than the withdrawal produces
"finished but kept moving blocks". Per level L, paired on the scene with the as-trained run:
  drop = successes(as trained) - successes(lag L)
  drop >= 8 with paired sign p < 0.05 -> HURT;  |drop| <= 4 -> TOLERATED;  otherwise UNDECIDED
  floor: both runs >= 48 of 50 finished, else NO READING.
Meaning: lag16 HURT -> the delay injection itself is destructive (or swap is not slow): T1's late side (LATE HURTS on the
press task) is discounted and cannot count alone. lag16 and lag32 TOLERATED -> the criterion's prediction holds on a
second task (gate G4d item 2, together with the press-task dose). Reported only: the levels' successes in dose order.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/swap_lag_verdict.py   Writes outputs/fullft/SWAP_LAG_VERDICT.json.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2/closed_loop/swaplag"
LEVELS = (16, 32, 64)


def sign_p(a: int, b: int) -> float:
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(math.comb(n, k) for k in range(min(a, b) + 1)) / 2 ** n)


def successes(label: str) -> dict:
    out = {}
    for p in sorted((O / label / "on" / "swap_blocks").glob("seed_*/result.json")):
        if p.parent.name.split("_", 1)[1].isdigit():
            out[p.parent.name] = bool(json.loads(p.read_text()).get("success"))
    return out


def main():
    base = successes("ar2_prop_e30")
    res = {"as_trained": {"n": len(base), "success": sum(base.values())}, "levels": {}}
    print(f"as trained: {res['as_trained']}")
    for L in LEVELS:
        s = successes(f"ar2_prop_e30_lag{L}")
        common = sorted(set(s) & set(base))
        only_base = sum(base[k] and not s[k] for k in common)
        only_lag = sum(s[k] and not base[k] for k in common)
        drop = sum(base[k] for k in common) - sum(s[k] for k in common)
        if len(base) < 48 or len(s) < 48:
            word = f"NO READING ({len(base)} / {len(s)} finished; floor 48)"
        else:
            p = sign_p(only_base, only_lag)
            word = "HURT" if drop >= 8 and p < 0.05 else "TOLERATED" if abs(drop) <= 4 else "UNDECIDED"
        res["levels"][L] = {"n": len(s), "success": sum(s.values()), "pairs": len(common), "drop": drop,
                            "only_as_trained": only_base, "only_lag": only_lag, "p": sign_p(only_base, only_lag),
                            "word": word}
        print(f"lag {L}: {res['levels'][L]}")
    (R / "outputs/fullft/SWAP_LAG_VERDICT.json").write_text(json.dumps(res, indent=1) + "\n")


if __name__ == "__main__":
    main()
