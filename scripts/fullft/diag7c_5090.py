"""Plan v22 diagnostic 7(c) (appendix of claude/MemWAM_Plan_v22_20261128.md), written 11-28 17:13 (Opus) before any
of these numbers is measured. 5090, one GPU (~20 GB at --micro 2), read-only, DESCRIBED ONLY (no verdict word).
Question: without running the simulator, can one tell which rearrange checkpoint has not learned the press?
  Demos: the rearrange_blocks demos of the dense cache's 'val' split (the demos no training used; training reads the
    'train' split only, data.train_items), the same for every checkpoint.
  Anchors per demo: p = the frame of the demo's first 'bottom' event in events_rearrange_blocks_v3c.json (the same
    file and the same anchors for every checkpoint, whatever events file the checkpoint itself trained with);
    press window: 9 anchors evenly in [p - 24, p + 16]; rest: 9 anchors evenly over the frames outside [p - 48, p + 48].
  Per anchor: the action loss with the checkpoint's own history (its own events file builds its record), mean over
    --noises fixed draws (train.fixed_noise, the same draws for every checkpoint), as hist_probe / obs_probe.
  Per checkpoint: mean action loss in the press window, in the rest, and their ratio.
Checkpoints (DEFAULT_ITEMS): the weighted recipe's two seeds at e10 / e20 / e30, the two other arms of cards 20 / 21
  (three frames + weighting; old writer + weighting) at e10 / e20 / e30, and the unweighted timely writer rearr_v3c_h2
  e30. Each is taken from this machine (export folder, offload backup, relay mirror) or fetched from the relay when the
  relay has it; a checkpoint found nowhere is reported as missing (never waited for).
Beside each, at reading time (not here: the closed-loop episodes are on the A40): its closed-loop "never pressed" +
  "pressed twice" count (rearr_split.py classes, A40, rearrange_blocks 1-100) with the source of each number.
  Written before measuring: across the checkpoints that have both numbers, Spearman rho between the press-window loss
  and never + twice >= 0.7 -> Status says "the offline press-window error tracks the press failures"; rho < 0.4 ->
  "it does not"; otherwise "unclear". The same rho for the rest-window loss is reported beside it.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/diag7c_5090.py [--items run:tag,...]
Writes outputs/fullft/DIAG_V22_DIAG7C.json (rewritten after every checkpoint).
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path

import torch

R = Path("/workspace/FastWAM-memory2")
F = R / "outputs/fullft"
EV = F / "events/events_rearrange_blocks_v3c.json"
TASK = "rearrange_blocks"
CACHE = R / "outputs/memory_v2/press/dense_rearrange_blocks_v1"      # every listed run's data.roots (gaas / h100 queue lines)
DEFAULT_ITEMS = ([f"rearr_pw:e{k}" for k in (10, 20, 30)] + [f"rearr_pw_s18:e{k}" for k in (10, 20, 30)]
                 + [f"rearr_ar_pw:e{k}" for k in (10, 20, 30)] + [f"rearr_arprop_pw:e{k}" for k in (10, 20, 30)]
                 + ["rearr_v3c_h2:e30"])
HFPY = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else "/opt/mwam/bin/python"


def evenly(lo: int, hi: int, n: int):
    if hi < lo:
        return []
    if hi == lo or n == 1:
        return [lo]
    return sorted({round(lo + (hi - lo) * k / (n - 1)) for k in range(n)})


def locate(run: str, tag: str):
    name = f"{run}_{tag}"
    for d in (F / "exports" / name, F / "exports_hf_backup/exports" / name, Path("/mnt/hf/relay_mirror/memwam-fullft/exports") / name):
        if (d / f"export_{tag}.pt").exists():
            return d
    r = subprocess.run([HFPY, str(R / "scripts/memory_v2/migrate/relay.py"), "ls", "--prefix", f"exports/{name}",
                        "--repo", "hhyfred/memwam-fullft"], capture_output=True, text=True, cwd=str(R))
    if f"export_{tag}.pt.sha256 " not in r.stdout:
        return None
    subprocess.run(["bash", str(R / "scripts/fullft/export_fetch.sh")], cwd=str(R),
                   env={**os.environ, "RUN": run, "TAG": tag, "POLL": "60"})
    d = F / "exports" / name
    return d if (d / f"export_{tag}.pt").exists() else None


def measure(path: Path, noises: int, micro: int, anchors_of):
    from fastwam.fullft.data import DenseEpisodes, Samples, collate, load_events, video_polarity
    from fastwam.fullft.online import load_export
    from fastwam.fullft.train import fixed_noise, to_device
    device = "cuda"
    model, cfg, _ = load_export(str(path), device)
    episodes = DenseEpisodes(cfg.data.roots, cfg.data.tasks, capacity=cfg.data.episode_cache)
    recs = [r for r in episodes.records if r["task"] == TASK and r.get("split") == "val"]
    items, window = [], []
    for r in recs:
        for w, a in anchors_of(r["episode_id"], int(r["length"])):
            items.append((r["episode_id"], a))
            window.append(w)
    events = load_events(cfg.data.events) if cfg.data.events else {}
    samples = Samples(episodes, items, cfg.rule, events, video_polarity(episodes), augment=False, seed=cfg.seed)
    loss = [[] for _ in items]
    with torch.no_grad():
        for start in range(0, len(samples), micro):
            idx = list(range(start, min(len(samples), start + micro)))
            rows = [samples[i] for i in idx]
            batch = to_device(collate(rows), device)
            for k in range(noises):
                nz = [fixed_noise(1000 * k + i, {"video": tuple(r["video_latent"].shape), "action": tuple(r["actions"].shape)},
                                  model, device) for i, r in zip(idx, rows)]
                noise = {key: torch.stack([n[key] for n in nz]).squeeze(1) if key.startswith("t_") else
                         torch.stack([n[key] for n in nz]) for key in nz[0]}
                with torch.autocast("cuda", dtype=torch.bfloat16, cache_enabled=False):
                    _, act = model.loss(batch, noise, model.history(batch))
                for j, i in enumerate(idx):
                    loss[i].append(float(act[j].float()))
    del model
    torch.cuda.empty_cache()
    per = [statistics.mean(v) for v in loss]
    out = {"run": cfg.name, "history": str(cfg.rule), "val_demos": [r["episode_id"] for r in recs], "anchors": len(items)}
    for w in ("press", "rest"):
        sel = [per[i] for i in range(len(items)) if window[i] == w]
        out[f"{w}_anchors"] = len(sel)
        out[f"{w}_action_loss"] = statistics.mean(sel) if sel else None
    if out["press_action_loss"] and out["rest_action_loss"]:
        out["press_over_rest"] = out["press_action_loss"] / out["rest_action_loss"]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--items", default=",".join(DEFAULT_ITEMS))
    ap.add_argument("--noises", type=int, default=2)
    ap.add_argument("--micro", type=int, default=2)
    a = ap.parse_args()
    from fastwam.fullft.data import load_events
    if not EV.exists():
        print(f"[d7c] STOP: {EV} missing")
        return 1
    if not (CACHE / ".verified").exists():
        print(f"[d7c] {CACHE.name} not verified here: fetching it from the cache relay", flush=True)
        rc = subprocess.run([HFPY, str(R / "scripts/fullft/cache_relay.py"), "get", "--name", CACHE.name, "--dest",
                             str(CACHE.parent)], cwd=str(R)).returncode
        if rc != 0 or not (CACHE / "CACHE.json").exists():
            print(f"[d7c] STOP: {CACHE} not available (cache_relay get exit {rc})")
            return 1
    press = {}
    for eid, evs in load_events([str(EV)]).items():
        b = [int(e["frame"]) for e in evs if e.get("kind") == "bottom"]
        if b:
            press[eid] = min(b)

    def anchors_of(eid, n):
        if eid not in press:
            raise SystemExit(f"[d7c] STOP: {eid} has no 'bottom' event in {EV.name}")
        p = press[eid]
        out = [("press", x) for x in evenly(max(1, p - 24), min(n - 1, p + 16), 9)]
        rest = [x for x in range(1, n) if x < p - 48 or x > p + 48]
        if rest:
            out += [("rest", rest[round((len(rest) - 1) * k / 8)]) for k in range(9)]
        return out
    rep = {"run": "plan v22 diagnostic 7(c): rearrange press-window action loss on the held-out demos (described)",
           "anchors": "press [p-24, p+16] x 9, rest outside [p-48, p+48] x 9; p = first 'bottom' of events_rearrange_blocks_v3c",
           "noises": a.noises, "items": {}, "missing": []}
    outp = F / "DIAG_V22_DIAG7C.json"
    for it in [x for x in a.items.split(",") if x]:
        run, tag = it.split(":")
        d = locate(run, tag)
        if d is None:
            rep["missing"].append(it)
            print(f"[d7c] {it}: not on this machine and not on the relay: skipped", flush=True)
            continue
        sha = d / f"export_{tag}.pt.sha256"
        if sha.exists() and subprocess.run(["sha256sum", "-c", "--quiet", sha.name], cwd=str(d)).returncode != 0:
            rep["missing"].append(f"{it} (sha256 mismatch at {d})")
            continue
        r = measure(d / f"export_{tag}.pt", a.noises, a.micro, anchors_of)
        r["from"] = str(d)
        rep["items"][it] = r
        print(f"[d7c] {it}: press {r['press_action_loss']:.5f} rest {r['rest_action_loss']:.5f} "
              f"ratio {r.get('press_over_rest', float('nan')):.3f} ({r['anchors']} anchors, {len(r['val_demos'])} demos)", flush=True)
        outp.write_text(json.dumps(rep, indent=1) + "\n")
    rep["verdict"] = "DESCRIBED" if rep["items"] else "NOTHING MEASURED"
    outp.write_text(json.dumps(rep, indent=1) + "\n")
    print(f"DIAG 7C {rep['verdict']}: {len(rep['items'])} checkpoints, missing {rep['missing']} -> {outp}")
    return 0 if rep["items"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
