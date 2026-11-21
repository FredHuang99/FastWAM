"""Plan v19 3.2 acceptance (11-22, Opus): with the new parts off, one training update of the CURRENT code is bit-for-bit
the update of an EARLIER commit (default 5dcb216, before the parts existed). CPU, tiny random FastWAM MoT, fake dense
episodes; no GPU, no real weights. For each history rule (ar; arprop with ordinal 16) it runs, in a fresh interpreter
per code tree: Samples -> collate -> FullModel.loss with fixed noise -> the trainer's micro-batch loss -> backward ->
AdamW step, and hashes every sample tensor, both loss vectors, every gradient and every updated parameter.
The trainer's loss: train.objective when the tree has it, else the earlier inline expression (verbatim).
  python3 scripts/fullft/deed_parity_cpu.py [--old 5dcb216]      (from the repo root; prints PARITY OK / FAIL)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

WORKER = r'''
import hashlib, json, sys, tempfile
from pathlib import Path
import torch
from torch import nn
from fastwam.fullft.data import DenseEpisodes, Samples, collate, train_items
from fastwam.fullft.history import HistoryRule
from fastwam.fullft.model import FullModel
from fastwam.fullft.config import load
import fastwam.fullft.train as T

TEXT = 16
def h(t):
    return hashlib.sha256(t.detach().float().contiguous().numpy().tobytes()).hexdigest()[:16]

def model(variant, slots, feats):
    from fastwam.models.wan22.action_dit import ActionDiT
    from fastwam.models.wan22.mot import MoT
    from fastwam.models.wan22.wan_video_dit import WanVideoDiT
    torch.manual_seed(0)
    video = WanVideoDiT(hidden_dim=96, in_dim=48, ffn_dim=64, out_dim=48, text_dim=TEXT, freq_dim=32, eps=1e-6,
                        patch_size=(1, 2, 2), num_heads=4, attn_head_dim=24, num_layers=2, has_image_input=False,
                        seperated_timestep=True, fuse_vae_embedding_in_latents=True, action_dim=14,
                        video_attention_mask_mode="first_frame_causal")
    action = ActionDiT(hidden_dim=32, action_dim=14, ffn_dim=64, text_dim=TEXT, freq_dim=32, eps=1e-6, num_heads=4,
                       attn_head_dim=24, num_layers=2)
    mot = MoT({"video": video, "action": action}, mot_checkpoint_mixed_attn=False)
    m = FullModel(mot, nn.Linear(14, TEXT), variant=variant, event_slots=slots, ledger_features=feats)
    with torch.no_grad():
        for name, p in m.named_parameters():
            if p.abs().sum() == 0:
                p.normal_(0, 0.02)
    return m.float()

out = {}
tmp = Path(tempfile.mkdtemp())
torch.manual_seed(123)
root = tmp / "dense"
records = []
for k in range(2):
    eid = f"swap_blocks/episode_{k:07d}"
    folder = root / "cache" / eid.replace("/", "_")
    folder.mkdir(parents=True)
    text = torch.cat((torch.randn(3, TEXT), torch.zeros(40, TEXT)))
    torch.save({"latent": torch.randn(70, 48, 1, 4, 4), "video_latent": torch.randn(70, 48, 3, 4, 4),
                "video_valid": torch.ones(70, 9, dtype=torch.bool), "text": text,
                "text_valid": torch.tensor([True] * 3 + [False] * 40), "proprio": torch.randn(70, 14),
                "actions": torch.randn(70, 14)}, folder / "encodings.pt")
    (folder / "COMPLETE.json").write_text("{}")
    records.append({"episode_id": eid, "task": "swap_blocks", "split": "train", "length": 70})
(root / "RECORDS.json").write_text(json.dumps(records))
EV = [{"frame": 10, "arm": 0, "kind": "close", "confirmed": 10}, {"frame": 20, "arm": 0, "kind": "bottom", "confirmed": 24},
      {"frame": 30, "arm": 1, "kind": "open", "confirmed": 30}, {"frame": 36, "arm": 0, "kind": "bottom", "confirmed": 40}]
eps = DenseEpisodes([str(root)], ["swap_blocks"])
events = {r["episode_id"]: EV for r in eps.records}
items = train_items(eps)
cfg = load(None, [])
for name, rule in (("ar", HistoryRule("ar")), ("arprop_ord16", HistoryRule("arprop", event_max=32, lag=4, ordinal=16))):
    ds = Samples(eps, items, rule, events, "valid", augment=True, seed=17)
    rows = [ds[i] for i in (3, 27, 44, 61, 100, 131)]
    batch = collate(rows)
    out[name + "/sample"] = {k: h(v) for k, v in sorted(batch.items())}
    m = model(rule.variant, rule.event_slots, rule.ledger_features)
    opt = torch.optim.AdamW([p for p in m.parameters() if p.requires_grad], lr=1e-3)
    torch.manual_seed(7)
    v, a = m.loss(batch)                                  # training draws (noise, timesteps) from the global RNG
    if hasattr(T, "objective"):
        loss = T.objective(cfg, v, a, batch, None, 8)
    else:
        loss = (cfg.model.video_loss * v.mean() + cfg.model.action_loss * a.mean()) / 8
    loss.backward()
    out[name + "/loss"] = [h(v), h(a), h(loss)]
    out[name + "/grad"] = {n: h(p.grad) for n, p in m.named_parameters() if p.grad is not None}
    opt.step()
    out[name + "/param"] = {n: h(p) for n, p in m.named_parameters()}
print(json.dumps(out, sort_keys=True))
'''


def run(tree: Path) -> dict:
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), CUDA_VISIBLE_DEVICES="")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(WORKER)
    res = subprocess.run([sys.executable, f.name], env=env, capture_output=True, text=True, cwd=tempfile.gettempdir())
    os.unlink(f.name)
    if res.returncode:
        raise SystemExit(f"worker failed on {tree}:\n{res.stderr[-3000:]}")
    return json.loads(res.stdout.strip().splitlines()[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", default="5dcb216")
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as d:
        old = Path(d) / "old"
        old.mkdir()
        arc = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(REPO), "archive", args.old, "src"], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(old)], input=arc, check=True)
        a, b = run(old), run(REPO)
    bad = []
    for key in sorted(set(a) | set(b)):
        if a.get(key) != b.get(key):
            bad.append(key)
    n = sum(len(v) if isinstance(v, (dict, list)) else 1 for v in a.values())
    digest = hashlib.sha256(json.dumps(b, sort_keys=True).encode()).hexdigest()[:16]
    if bad:
        print(f"PARITY FAIL against {args.old}: {bad}")
        return 1
    print(f"PARITY OK against {args.old}: {n} hashes equal (samples, losses, gradients, updated parameters; ar and "
          f"arprop + ordinal 16); digest {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
