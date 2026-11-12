"""5090 fix F2 (11-12): can both machines take the instruction's text features from the dense TRAINING cache?
Every official scene bank has one instruction per task. Per task: the bank's instruction, how many training episodes in
the dense cache carry exactly that string, and (--t5) the relative L2 between this machine's own T5 encoding (as the
closed loop does it: CPU bf16 on < 60 GB cards) and the cached features. CPU only. Read-only.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/text_check.py [--t5] [--tasks put_back_block swap_blocks]
"""
from __future__ import annotations

import argparse
import glob
import json
import time
from pathlib import Path

O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")


def bank_instruction(task):
    found = set()
    for f in glob.glob(str(O / f"closed_loop/scenes_seed42_n100_{task}/*.json")):
        v = json.load(open(f))
        v = (v.get("scenes") if isinstance(v, dict) else v) or []
        found |= {x["instruction"] for x in v if isinstance(x, dict) and "instruction" in x}
    return sorted(found)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", default=["put_back_block", "swap_blocks", "observe_and_pickup", "press_button",
                                                   "battery_try", "blocks_ranking_try", "cover_blocks",
                                                   "rearrange_blocks", "swap_T"])
    ap.add_argument("--t5", action="store_true")
    args = ap.parse_args()
    import torch
    from fastwam.memory_v2 import dense
    spec = dense.DenseSpec()
    recs = list(dense.records(spec))
    print(f"dense cache {spec.root}: {len(recs)} training episodes, tasks {sorted({r.get('task') for r in recs})}")
    t5 = tok = None
    if args.t5:
        from fastwam.models.wan22.helpers.loader import _load_registered_model
        from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
        cfg = dense.dense_config(spec)
        path = lambda k: str(Path(cfg["paths"][k]) if Path(cfg["paths"][k]).is_absolute() else Path(spec.root) / cfg["paths"][k])
        tok = HuggingfaceTokenizer(path("tokenizer"), seq_len=128, clean="whitespace", local_files_only=True)
        t5 = _load_registered_model(path("t5"), "wan_video_text_encoder", torch.bfloat16, "cpu").eval()
        torch.set_num_threads(8)                                   # as the closed loop
    store = dense.EpisodeStore(spec, verify=False)
    for task in args.tasks:
        for instr in bank_instruction(task):
            same = [r for r in recs if r.get("instruction") == instr]
            line = f"{task}: bank instruction {instr!r}; training episodes with exactly this string: {len(same)}"
            if same and t5 is not None:
                from fastwam.memory_s1.model import encode_text
                enc = store(same[0]["episode_id"])
                start = time.monotonic()
                with torch.no_grad():
                    f, v = encode_text(t5, tok, instr, torch.device("cpu"))
                m = v[0].bool()
                x, y = f[0][m].float(), enc["text"][m].float()
                line += f"; this machine's CPU T5 vs cache: relative L2 {float((x - y).norm() / y.norm()):.3e} ({time.monotonic() - start:.0f} s)"
            print(line, flush=True)


if __name__ == "__main__":
    main()
