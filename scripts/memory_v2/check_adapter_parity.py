"""GPU check: memory_v2 on the released frozen backbone reproduces the native action path.

Compares, on one cached RMBench sample and fixed noise/timesteps,
  (a) memory_s1.FrozenBackbone.action_velocity with the memory bypassed, and
  (b) MemoryV2Model(FastWAMActionAdapter) with zero-initialised injectors (modes on/null/off).
They must be bitwise equal (same kernels, same BF16 discipline). Then it perturbs
the injector outputs and verifies that the memory now changes the velocity.

python scripts/memory_v2/check_adapter_parity.py --config configs/memory_s1/s1_variable_t_h100.yaml \
    --output outputs/memory_v2/checks/adapter_parity.json
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import torch

from fastwam.memory_s1.common import load_config
from fastwam.memory_s1.data import CachedEpisodes, collate
from fastwam.memory_s1.model import FrozenBackbone
from fastwam.memory_v2.config import HistoryPolicyConfig, MemoryV2Config
from fastwam.memory_v2.history import collate_history, select_history
from fastwam.memory_v2.model import FastWAMActionAdapter, MemoryV2Model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--split", default="val")
    parser.add_argument("--anchor", type=int, default=96)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    device = torch.device("cuda:0")
    episodes = CachedEpisodes(cfg, args.split)
    record = episodes.by_task["put_back_block"][0]
    sample = episodes.at(record, args.anchor, period=8, phase=0)
    batch = collate([sample], device)
    episode = episodes.load(record)
    available = episode["frame_ids"].tolist()
    selection = select_history([i for i in available if i <= args.anchor], args.anchor, HistoryPolicyConfig())
    position = {int(i): k for k, i in enumerate(available)}
    features = [[episode["features"][position[i]] for i in selection.ids]]
    batch.update(collate_history(features, [selection], 120, 3072, dtype=torch.bfloat16, device=device))

    backbone = FrozenBackbone(cfg, device)
    model = MemoryV2Model(FastWAMActionAdapter(backbone), MemoryV2Config()).to(device)
    model.memory.float()
    generator = torch.Generator().manual_seed(0)
    noise = torch.randn(1, 32, 14, generator=generator).to(device)
    report = {"history_ids": list(selection.ids), "checks": []}
    with torch.no_grad():
        current, kv, context = backbone.encode_observation(batch["latent"], batch["text"], batch["proprio"])
        conditions = model.conditions(batch)
        for tau in (1.0, 0.9, 0.5, 0.1):
            t = torch.full((1,), 1000.0 * tau, device=device)
            noisy = ((1 - tau) * batch["actions"] + tau * noise)
            native = backbone.action_velocity(noisy, t, context, kv, SimpleNamespace(injectors={}), None, gate_scale=0)
            row = {"tau": tau}
            for mode in ("on", "null", "off"):
                ours = model.velocity(noisy, t, conditions, mode)
                row[f"{mode}_max_abs"] = float((ours.float() - native.float()).abs().max())
            report["checks"].append(row)
        for injector in model.memory.injectors.values():
            injector.out.weight.normal_(0, 1e-3)
        t = torch.full((1,), 1000.0, device=device)
        changed = model.velocity(noise, t, conditions, "on").float()
        native = backbone.action_velocity(noise, t, context, kv, SimpleNamespace(injectors={}), None, gate_scale=0).float()
        report["perturbed_on_max_abs"] = float((changed - native).abs().max())
    report["passed"] = all(v == 0.0 for row in report["checks"] for k, v in row.items() if k.endswith("max_abs")) \
        and report["perturbed_on_max_abs"] > 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
