"""RTX 5090 (11-07 23:30, after S4): the online observation path against the dense cache, component by component.

S4 on the 5090 (X7, 4 steps) lifted the block in 21/50 put_back scenes (X7 at 10 steps on the A100 / H200: 98/100)
although offline 4 steps equal 10 steps. The offline parity (parity5090.sh) read cached latents and text, so the
5090's ONLINE encoders were never compared with anything. Here, on one put_back and one swap demo episode (train
split, first of each task in RECORDS.json):

  1 text   the instruction's T5 features (a) on the CPU in bf16 = the 5090 closed loop since f4e8d50, (b) on this GPU in
           bf16 = the A100 / H100 path, each vs the cache's 'text' (built on the H100, GPU bf16); valid tokens only
  2 image  the online latent of frames 0 / middle / last: Codex's Raw.images (official decoder) -> data_path.mosaic ->
           memory_s1 encode_latent (the closed loop's call) on this GPU, vs the cache's 'latent' of the same frame
  3 the dense cache's own receipt (max_first_latent_difference) for scale

Relative L2 = ||online - cache|| / ||cache||. PASS when every text value <= 2e-2 and every latent <= 3e-2 (bf16 on a
different GPU / kernel: expected 1e-3 to 1e-2). Read-only: loads weights and the cache, writes only
report/ONLINE5090_<time>.md. Run alone on a free GPU (VAE + T5 on the GPU ~13 GB):
  CUDA_VISIBLE_DEVICES=0 PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/migrate/online_check5090.py
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
CKPT = O / "a2C_6ep/checkpoints/update_004020.pt"
BJ = timezone(timedelta(hours=8))
LINES = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LINES.append(line)


def rel(a, b):
    a, b = a.float().flatten(), b.float().flatten()
    return float((a - b).norm() / b.norm().clamp_min(1e-12))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", default=str(CKPT), help="only its config is read (dense spec)")
    ap.add_argument("--text-tol", type=float, default=2e-2)
    ap.add_argument("--latent-tol", type=float, default=3e-2)
    args = ap.parse_args()
    import torch
    from fastwam.memory_v2 import dense
    from fastwam.memory_v2.online import policy_config
    from fastwam.memory_s1.model import encode_latent, encode_text
    from fastwam.models.wan22.helpers.loader import _load_registered_model
    from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer

    say(f"# ONLINE5090 {datetime.now(BJ):%F %T}: online encoders vs the dense cache")
    say(f"torch {torch.__version__}, GPU {torch.cuda.get_device_name(0)}, checkpoint config {args.checkpoint}")
    cfg, _ = policy_config(Path("unused"), args.checkpoint, [])
    spec = dense.DenseSpec.from_dict(cfg.dense)
    dcfg = dense.dense_config(spec)                      # binds the dense delivery code (sys.path)
    import data_path                                     # noqa: E402  (Codex: Raw, mosaic)

    def path(key):
        v = Path(dcfg["paths"][key])
        return str(v if v.is_absolute() else Path(spec.root) / v)

    records = dense.records(spec)
    picks = []
    for task in ("put_back_block", "swap_blocks"):
        rows = [r for r in records if r.get("task") == task and r.get("split", "train") == "train"] or \
               [r for r in records if r.get("task") == task]
        if rows:
            picks.append(rows[0])
    say(f"episodes: {[r['episode_id'] for r in picks]}")
    store = dense.EpisodeStore(spec, verify=False)
    fail = []

    # ---- 1 text
    tok = HuggingfaceTokenizer(path("tokenizer"), seq_len=128, clean="whitespace", local_files_only=True)
    t0 = time.time()
    t5 = _load_registered_model(path("t5"), "wan_video_text_encoder", torch.bfloat16, "cpu").eval().requires_grad_(False)
    say(f"\n## 1 text (T5 bf16 loaded on the CPU in {time.time() - t0:.0f} s)")
    say("| episode | CPU vs cache | GPU vs cache | CPU vs GPU | valid tokens |")
    say("|---|---|---|---|---|")
    cpu_feats = {}
    for r in picks:
        enc = store(r["episode_id"])
        cache, valid = enc["text"].float(), enc["text_valid"].bool()
        with torch.no_grad():
            f, v = encode_text(t5, tok, r["instruction"], torch.device("cpu"))
        if not torch.equal(v[0].cpu(), valid):
            say(f"  {r['episode_id']}: token mask differs from the cache (instruction text / tokenizer differ)")
            fail.append("text mask")
        cpu_feats[r["episode_id"]] = f[0].float()
    t5.to("cuda:0")
    for r in picks:
        enc = store(r["episode_id"])
        cache, valid = enc["text"].float(), enc["text_valid"].bool()
        with torch.no_grad():
            g, _ = encode_text(t5, tok, r["instruction"], torch.device("cuda:0"))
        g = g[0].float().cpu()
        c = cpu_feats[r["episode_id"]]
        a, b, ab = rel(c[valid], cache[valid]), rel(g[valid], cache[valid]), rel(c[valid], g[valid])
        say(f"| {r['episode_id']} | {a:.2e} | {b:.2e} | {ab:.2e} | {int(valid.sum())} |")
        if a > args.text_tol:
            fail.append(f"text CPU {r['episode_id']} {a:.2e}")
        if b > args.text_tol:
            fail.append(f"text GPU {r['episode_id']} {b:.2e}")
    del t5
    torch.cuda.empty_cache()

    # ---- 2 image
    vae = _load_registered_model(path("vae"), "wan_video_vae", torch.bfloat16, "cuda:0").eval().requires_grad_(False)
    say("\n## 2 image (Raw.images -> mosaic -> encode_latent on this GPU vs the cached latent)")
    say("| episode | frame | rel L2 | max abs | cache receipt max_first_latent_difference |")
    say("|---|---|---|---|---|")
    for r in picks:
        enc = store(r["episode_id"])
        receipt = "-"
        try:
            import json
            receipt = json.loads((dense.cache_dir(spec, r["episode_id"]) / "COMPLETE.json").read_text()).get(
                "max_first_latent_difference", "-")
        except (OSError, ValueError):
            pass
        raw = data_path.Raw(dcfg, r)
        try:
            n = int(r["length"])
            for i in sorted({0, n // 2, n - 1}):
                image = data_path.mosaic(raw.images(i))[None].to("cuda:0", torch.bfloat16)
                with torch.no_grad():
                    z = encode_latent(vae, image)[0].float().cpu()
                c = enc["latent"][i].float()
                e = rel(z, c)
                say(f"| {r['episode_id']} | {i} | {e:.2e} | {float((z - c).abs().max()):.3f} | {receipt} |")
                if e > args.latent_tol:
                    fail.append(f"latent {r['episode_id']}:{i} {e:.2e}")
        finally:
            raw.close()
    say(f"\n{'PASS' if not fail else 'FAIL'}: text tol {args.text_tol}, latent tol {args.latent_tol}"
        + ("" if not fail else "; " + "; ".join(fail)))
    out = O / "report" / f"ONLINE5090_{datetime.now(BJ):%Y%m%d_%H%M}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(LINES) + "\n")
    print(f"ONLINE5090: {out}")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
