"""Encode the official banks' instructions once and save them for MWAM_TEXT_FILE (11-12, 5090 fix T-test).

Why: the X7 policy (memory_v2 Policy) encodes the instruction with T5 on the GPU on the A100 (40 GB card: T5 visits the
GPU per episode) but on the CPU on the 5090 (32 GB: no room next to the policy and the simulator). The two encodings
differ by a few percent (A100 GPU vs training cache 2.9 %, 5090 CPU vs cache 2.5 %), the largest input difference left
after the render fix. Encoding on THIS machine's GPU once, before any closed loop, gives the 5090 the A100's path.

  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/text_dump.py --device cuda --out outputs/fullft/align/text/x7_t5gpu_5090.pt
Prints per instruction the fingerprint, the relative L2 vs the dense training cache (the A100's GPU path measured 2.92e-2)
and, with --cpu-too, vs this machine's CPU encoding (what the 5090's closed loop used so far).
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from text_check import bank_instruction  # noqa: E402


def fingerprint(t, v):
    import torch
    t = t.to(torch.bfloat16).contiguous().cpu()
    return hashlib.sha256(t.view(torch.int16).numpy().tobytes() + v.bool().contiguous().cpu().numpy().tobytes()).hexdigest()[:12]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", nargs="+", default=["put_back_block", "swap_blocks"])
    ap.add_argument("--cpu-too", action="store_true")
    args = ap.parse_args()
    import torch
    from fastwam.memory_s1.model import encode_text
    from fastwam.memory_v2 import dense
    from fastwam.models.wan22.helpers.loader import _load_registered_model
    from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
    spec = dense.DenseSpec()
    cfg = dense.dense_config(spec)
    path = lambda k: str(Path(cfg["paths"][k]) if Path(cfg["paths"][k]).is_absolute() else Path(spec.root) / cfg["paths"][k])
    tok = HuggingfaceTokenizer(path("tokenizer"), seq_len=128, clean="whitespace", local_files_only=True)
    dev = torch.device(args.device)
    t5 = _load_registered_model(path("t5"), "wan_video_text_encoder", torch.bfloat16, str(dev)).eval().requires_grad_(False)
    recs = list(dense.records(spec))
    store = dense.EpisodeStore(spec, verify=False)
    torch.set_num_threads(8)
    out = {}
    for task in args.tasks:
        for instr in bank_instruction(task):
            with torch.no_grad():
                f, v = encode_text(t5, tok, instr, dev)
            f, v = f.detach().cpu(), v.detach().cpu()
            out[instr] = {"text": f, "valid": v, "device": torch.cuda.get_device_name(dev) if dev.type == "cuda" else "cpu"}
            line = f"{task}: {args.device} fingerprint {fingerprint(f[0], v[0])}"
            m = v[0].bool()
            same = [r for r in recs if r.get("instruction") == instr]
            if same:
                y = store(same[0]["episode_id"])["text"][m].float()
                line += f"; vs training cache rel L2 {float((f[0][m].float() - y).norm() / y.norm()):.3e}"
            if args.cpu_too and dev.type != "cpu":
                start = time.monotonic()
                with torch.no_grad():
                    fc, _ = encode_text(t5.to("cpu"), tok, instr, torch.device("cpu"))
                t5.to(dev)
                x = f[0][m].float()
                line += f"; vs this machine's CPU T5 rel L2 {float((fc[0][m].float() - x).norm() / x.norm()):.3e} ({time.monotonic() - start:.0f} s)"
            print(line, flush=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    torch.save(out, args.out)
    print(f"TEXT DUMP {len(out)} instructions -> {args.out}")


if __name__ == "__main__":
    main()
