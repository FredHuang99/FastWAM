"""5090 diagnosis D2 (11-12): this machine's policy on the very same frame-0 requests (dumped by dump_first.sh on
either machine). Output in first_actions.py format, so `first_actions.py compare` puts it next to the logged decisions:
  probe on this machine's own requests   vs  its logged decision 0   -> must be identical (the probe = the closed loop)
  probe on the OTHER machine's requests  vs  that machine's logged    -> policy numerics only (images, text, noise and
                                                                         proprio identical; VAE + T5 + DiT differ)
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/numerics_probe.py --name probe_5090_on_a100_x7 --policy x7 \
      --requests "closed_loop/dumpfirst_in/dumpfirst_a100/on/*/seed_*/request_000000.pkl"
--policy x7 = the X7 checkpoint (memory_v2 Session); any other value = a fullft export path (FullSession).
--t5 as online.py (auto = what this machine's closed loop does). GPU: CUDA_VISIBLE_DEVICES (one card, ~30 GB for e10).
"""
from __future__ import annotations

import argparse
import glob
import json
import pickle
import tempfile
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
OUT = Path("/workspace/FastWAM-memory2/outputs/fullft/align/first")
X7 = O / "a2C_6ep/checkpoints/update_004020.pt"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", required=True)
    ap.add_argument("--policy", required=True)
    ap.add_argument("--requests", nargs="+", required=True)
    ap.add_argument("--t5", default="auto", choices=("auto", "gpu", "cpu"))
    args = ap.parse_args()
    import torch
    from fastwam.memory_v2.online import LIMITS
    files = []
    for g in args.requests:
        files += sorted(glob.glob(g if g.startswith("/") else str(O / g)))
    if not files:
        raise SystemExit(f"no request matches {args.requests}")
    t5 = {"auto": None, "gpu": True, "cpu": False}[args.t5]
    if args.policy == "x7":
        from fastwam.memory_v2.online import Policy, Session, policy_config
        cfg, state = policy_config(Path("unused"), str(X7), [])
        policy = Policy(cfg, state, str(X7), "cuda:0", encoders=True, t5_on_gpu=t5)
        del state
        make = lambda d, task: Session(policy, d, "on", 0, 1.0, False, tag="probe", limit=LIMITS[task])
    else:
        from fastwam.fullft.online import FullPolicy, FullSession
        policy = FullPolicy(args.policy, "cuda:0", t5_on_gpu=t5)
        make = lambda d, task: FullSession(policy, d, "on", 10, 1.0, False, tag="probe", limit=LIMITS[task])
    entries = {}
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(files):
            req = pickle.loads(Path(f).read_bytes())
            key = f"{req['task']}/{int(req['episode_seed'])}"
            d = Path(tmp) / f"r{i}"
            d.mkdir()
            session = make(d, req["task"])
            session.reset()
            session.decide(req)
            row = json.loads((d / "decisions.jsonl").read_text().splitlines()[0])
            entries[key] = {"frame_id": row.get("frame_id"), "noise_seed": row.get("noise_seed"),
                            "actions": row["normalized_actions"], "first_seconds": float(row.get("seconds", 0.0)),
                            "later_median_seconds": None, "success": None, "request": f}
            print(f"  {key}: decided in {row.get('seconds', 0.0):.1f} s", flush=True)
            del session
            torch.cuda.empty_cache()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{args.name}.json"
    path.write_text(json.dumps({"name": args.name, "folders": args.requests, "label": args.policy,
                                "torch": torch.__version__, "gpu": torch.cuda.get_device_name(0),
                                "entries": entries}) + "\n")
    print(f"NUMERICS PROBE {args.name}: {len(entries)} requests on {torch.cuda.get_device_name(0)} -> {path}")


if __name__ == "__main__":
    main()
