"""RoboMME card 10, training side step 1 (11-27 02:55, Opus; plan v21 6.6: P0, engineering starts today). Read-only, CPU.
What does Fast-WAM's LIBERO base (libero_optional_idm_2cam224.pt, sha256 26b4efff...) hold, compared with the RoboTwin
base the fullft trainer loads (robotwin_uncond_3cam_384.pt: a payload {"mot", "proprio_encoder"}, FullModel.from_release)?
Prints: top-level keys; for each dict-valued key the number of tensors and the first / last names; the shapes of every
tensor whose name says proprio / action / patch / head / idm; the same for the RoboTwin base; and the stats json's keys.
Nothing is converted or written except the report.
  PYTHONPATH=src /opt/mwam/bin/python scripts/robomme/inspect_base.py
Report: outputs/fullft/ROBOMME_BASE_INSPECT.json
"""
from __future__ import annotations

import json
from pathlib import Path

import torch

BASES = {"libero": Path("/workspace/FastWAM/resources/base/libero_optional_idm_2cam224.pt"),
         "robotwin": Path("/workspace/FastWAM/resources/base/robotwin_uncond_3cam_384.pt")}
STATS = Path("/workspace/FastWAM/resources/base/libero_optional_idm_2cam224_dataset_stats.json")
KEYS = ("proprio", "action", "patch", "head", "idm", "embedding", "time")


def describe(obj, depth=0):
    if isinstance(obj, torch.Tensor):
        return {"tensor": list(obj.shape), "dtype": str(obj.dtype)}
    if isinstance(obj, dict):
        tens = {k: v for k, v in obj.items() if isinstance(v, torch.Tensor)}
        out = {"n_keys": len(obj), "n_tensors": len(tens)}
        if tens:
            names = list(tens)
            out["first"], out["last"] = names[:5], names[-5:]
            out["interesting"] = {k: list(v.shape) for k, v in tens.items() if any(w in k.lower() for w in KEYS)}
            out["prefixes"] = sorted({k.split(".")[0] for k in names})
            out["params_M"] = round(sum(v.numel() for v in tens.values()) / 1e6, 1)
        if depth < 2:
            out["sub"] = {k: describe(v, depth + 1) for k, v in obj.items() if not isinstance(v, torch.Tensor)}
        return out
    return {"type": type(obj).__name__, "value": str(obj)[:200]}


def main():
    rep = {}
    for name, p in BASES.items():
        if not p.exists():
            rep[name] = {"missing": str(p)}
            continue
        payload = torch.load(p, map_location="cpu", weights_only=False, mmap=True)
        rep[name] = {"path": str(p), "bytes": p.stat().st_size, "top": describe(payload)}
        print(f"== {name}: {p} top-level {list(payload.keys()) if isinstance(payload, dict) else type(payload)}")
        del payload
    if STATS.exists():
        s = json.loads(STATS.read_text())
        rep["stats_keys"] = {k: (list(v.keys()) if isinstance(v, dict) else str(v)[:120]) for k, v in s.items()}
    out = Path("/workspace/FastWAM-memory2/outputs/fullft/ROBOMME_BASE_INSPECT.json")
    out.write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1)[:20000])
    print(f"ROBOMME BASE INSPECT -> {out}")


if __name__ == "__main__":
    main()
