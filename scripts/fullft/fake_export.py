"""Smoke-test input (11-11, before the first real N7 export reaches the evaluation machines): an export in the trainer's
format built from the RELEASED FastWAM weights (history gates 0 = the released model), so the fullft closed loop can be
run end to end now (model files, VAE / T5 / tokenizer paths, encoders, sessions, the simulator) instead of failing at
02:30 on the first real export. Not a model of ours: label it *_smoke and never compare its numbers.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/fake_export.py --out outputs/fullft/exports/release_smoke/export_e0.pt
  ... --check-cpu   also load it back with the online loader on the CPU and sample one chunk from random inputs
                    (the A100's torch 2.6 runs the fullft code; no GPU needed)
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import torch

R = Path("/workspace/FastWAM-memory2")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=str(R / "configs/fullft/base_2task.yaml"))
    ap.add_argument("--check-cpu", action="store_true")
    args = ap.parse_args()
    from fastwam.fullft.config import load
    from fastwam.fullft.model import FullModel
    cfg = load(args.config, ["name=release_smoke"])
    for name in ("base", "architecture", "stats"):
        path = Path(getattr(cfg.model, name))
        print(f"model.{name}: {'OK     ' if path.exists() else 'MISSING'} {path}", flush=True)
        if not path.exists():
            sys.exit(1)
    out = Path(args.out) if Path(args.out).is_absolute() else R / args.out
    if not out.exists():
        t = time.monotonic()
        model = FullModel.from_release(cfg.model.architecture, cfg.model.base, cfg.rule.variant, cfg.rule.event_slots)
        model.set_trainable(cfg.model.train_video, cfg.model.lora_rank)
        weights = {k: v.detach().to(torch.bfloat16).cpu() for k, v in model.state_dict().items()}
        out.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"weights": weights, "config": cfg.to_dict(), "state": {"update": 0, "smoke": "released weights"},
                    "variant": model.variant, "train_video": cfg.model.train_video}, out)
        print(f"export {out} ({out.stat().st_size / 2 ** 30:.1f} GiB, {time.monotonic() - t:.0f} s)", flush=True)
        del model, weights
    if args.check_cpu:
        from fastwam.fullft.online import is_fullft_export, load_export
        t = time.monotonic()
        assert is_fullft_export(str(out))
        model, run_cfg, _ = load_export(str(out), device="cpu")
        g = torch.Generator().manual_seed(0)
        batch = {"latent": torch.randn(1, 48, 1, 24, 20, generator=g, dtype=torch.bfloat16),
                 "text": torch.zeros(1, 128, model.proprio_encoder.out_features, dtype=torch.bfloat16),
                 "proprio": torch.zeros(1, 14, dtype=torch.bfloat16), "anchor": torch.tensor([0])}
        with torch.no_grad():
            a = model.sample(batch, torch.randn(1, 32, 14, generator=g), steps=1, history=None)
        print(f"CPU load + one 1-step chunk: {tuple(a.shape)}, finite {bool(torch.isfinite(a).all())}, "
              f"torch {torch.__version__}, {time.monotonic() - t:.0f} s", flush=True)
    print("FAKE EXPORT OK", flush=True)


if __name__ == "__main__":
    main()
