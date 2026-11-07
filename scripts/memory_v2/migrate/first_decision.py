"""Replay one closed-loop decision request offline with chosen text features (11-08, 5090 diagnosis).

Same scene 4300030 (official put_back), same weights, same CPU-seeded noise: the 5090's first executed chunk equals
the A100's delayed by two targets (arm RMSE 0.0054 at lag 2, 0.040 at lag 0). The 5090's online T5 (CPU, and also
GPU) differs from the H100 dense cache by 2.3-3.1 % relative; its VAE by 0.4 %. This replays frame 0's request
(online.py run --dump-first) through the closed loop's own Session.decide with the instruction encoded:
  cpu    on the CPU in bf16 (the 5090 closed loop since f4e8d50); must reproduce that episode's executed targets
  gpu    on this GPU in bf16 (T5 alone on the GPU, before the policy is loaded)
  cache  the dense cache's text of a training episode with the SAME instruction string (built on the H100, GPU bf16),
         if one exists
and prints, per variant, the first 8 executed targets, the arm RMSE against a reference chunk (--ref: the A100's
first 8 executed targets of the same scene) at lags 0-3, and against the cpu variant.
Read-only apart from its report: report/FIRST_DECISION_<time>.md (and decisions.jsonl rows in a temp folder).

  CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/migrate/first_decision.py \
      --request <episode>/request_000000.pkl --ref scripts/memory_v2/migrate/ref_a100_put_4300030.json \
      --replayed <episode>/executed_actions.jsonl
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
CKPT = O / "a2C_6ep/checkpoints/update_004020.pt"
ARM = list(range(6)) + list(range(7, 13))
BJ = timezone(timedelta(hours=8))
LINES = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LINES.append(line)


def lag_rmse(ref, x, lags=(0, 1, 2, 3)):
    """arm RMSE of x[s:] against ref[:8-s] (x lags ref by s targets)."""
    out = {}
    for s in lags:
        n = min(len(ref), len(x)) - s
        d = (np.asarray(ref[:n]) - np.asarray(x[s:s + n]))[:, ARM]
        out[s] = float(np.sqrt((d ** 2).mean()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--request", required=True)
    ap.add_argument("--checkpoint", default=str(CKPT))
    ap.add_argument("--variants", nargs="+", default=["cpu", "gpu", "cache"], choices=("cpu", "gpu", "cache"))
    ap.add_argument("--ref", default="", help="JSON {'targets': [[14] x 8], ...}: the reference machine's first targets")
    ap.add_argument("--replayed", default="", help="executed_actions.jsonl of the episode the request came from")
    ap.add_argument("--steps", type=int, default=0, help="Euler steps (0 = the checkpoint's)")
    args = ap.parse_args()
    import torch
    from fastwam.memory_v2 import dense
    from fastwam.memory_v2.online import LIMITS, Policy, Session, policy_config
    from fastwam.memory_s1.model import encode_text
    from fastwam.models.wan22.helpers.loader import _load_registered_model
    from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer

    req = pickle.loads(Path(args.request).read_bytes())
    say(f"# FIRST_DECISION {datetime.now(BJ):%F %T}")
    say(f"torch {torch.__version__}, GPU {torch.cuda.get_device_name(0)}; request {args.request}")
    say(f"task {req['task']} seed {req['episode_seed']} frame {req['current_id']}; instruction: {req['instruction']!r}")
    for r in req["observations"]:
        shapes = r.get("shapes")
        stats = []
        for b, s in zip(r.get("images", []), shapes or []):
            a = np.frombuffer(b, dtype=np.uint8).reshape(s).astype(np.float32)
            stats.append(f"{tuple(s)} mean {a.mean():.2f} std {a.std():.2f}")
        say(f"  observation frame {r.get('frame_id')}: images {stats}; proprio "
            f"{[round(float(v), 4) for v in (r.get('proprio') or [])]}")

    cfg, state = policy_config(Path("unused"), args.checkpoint, [])
    spec = dense.DenseSpec.from_dict(cfg.dense)
    dcfg = dense.dense_config(spec)

    def path(key):
        v = Path(dcfg["paths"][key])
        return str(v if v.is_absolute() else Path(spec.root) / v)

    texts = {}
    if "gpu" in args.variants:                      # T5 alone on the GPU first (policy + T5 do not fit 32 GB together)
        tok = HuggingfaceTokenizer(path("tokenizer"), seq_len=128, clean="whitespace", local_files_only=True)
        t5 = _load_registered_model(path("t5"), "wan_video_text_encoder", torch.bfloat16, "cuda:0").eval()
        with torch.no_grad():
            f, v = encode_text(t5, tok, req["instruction"], torch.device("cuda:0"))
        texts["gpu"] = (f.cpu(), v.cpu())
        del t5
        torch.cuda.empty_cache()
    if "cache" in args.variants:
        recs = [r for r in dense.records(spec) if r.get("instruction") == req["instruction"]]
        if recs:
            enc = dense.EpisodeStore(spec, verify=False)(recs[0]["episode_id"])
            texts["cache"] = (enc["text"][None], enc["text_valid"][None].bool())
            say(f"cache text: {len(recs)} training episodes have this exact instruction; using {recs[0]['episode_id']}")
        else:
            near = sorted({r.get("instruction") for r in dense.records(spec) if r.get("task") == req["task"]})[:3]
            say(f"cache text: no training episode has this exact instruction (e.g. {near!r}): variant skipped")

    policy = Policy(cfg, state, args.checkpoint, "cuda:0", encoders=True, t5_on_gpu=False)
    del state
    say(f"policy: {json.dumps({k: v for k, v in policy.describe().items() if k.startswith('t5') or k == 'checkpoint'})}")
    if "cpu" in args.variants:
        if policy.t5_on_gpu or not policy.t5_cpu_encode:
            say("note: this card is >= 36 GB, so 'cpu' here is the GPU-visit path of 40 GB cards")
        f, v = policy.encode_text(req["instruction"])
        texts["cpu"] = (f.cpu(), v.cpu())
    order = [k for k in ("cpu", "gpu", "cache") if k in texts]
    for a in order:
        for b in order:
            if a < b and torch.equal(texts[a][1], texts[b][1]):
                m = texts[a][1][0]
                x, y = texts[a][0][0][m].float(), texts[b][0][0][m].float()
                say(f"text {a} vs {b}: relative L2 {float((x - y).norm() / y.norm()):.3e}")

    ref = json.loads(Path(args.ref).read_text())["targets"] if args.ref else None
    replayed = None
    if args.replayed and Path(args.replayed).exists():
        replayed = [json.loads(l)["target"] for l in Path(args.replayed).read_text().splitlines()[:8] if l.strip()]
    results = {}
    task = req["task"]
    with tempfile.TemporaryDirectory() as tmp:
        for name in order:
            (Path(tmp) / name).mkdir()
            session = Session(policy, Path(tmp) / name, "on", args.steps, 1.0, False, tag=f"first/{name}",
                              limit=LIMITS[task])
            session.instruction, session.seed, session.task = req["instruction"], req["episode_seed"], task
            session.text, session.text_valid = (t.to(policy.device) for t in texts[name])
            actions = session.decide(req)
            results[name] = actions[:8].tolist()
    say("\n## first 8 targets per variant (arm RMSE vs the reference at lag s: this lags the reference by s targets)")
    for name in order:
        x = results[name]
        say(f"\n### {name}")
        for i, row in enumerate(x):
            say(f"  t{i + 1} " + " ".join(f"{v:+.4f}" for v in row))
        if ref:
            say(f"  vs reference: " + "  ".join(f"lag {s}: {v:.4f}" for s, v in lag_rmse(ref, x).items()))
        if replayed:
            say(f"  vs the episode's own executed targets (lag 0): {lag_rmse(replayed, x, (0,))[0]:.5f}")
        if name != "cpu" and "cpu" in results:
            say(f"  vs cpu variant (lag 0): {lag_rmse(results['cpu'], x, (0,))[0]:.4f}")
    out = O / "report" / f"FIRST_DECISION_{datetime.now(BJ):%Y%m%d_%H%M}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(LINES) + "\n")
    print(f"FIRST_DECISION: {out}")


if __name__ == "__main__":
    main()
