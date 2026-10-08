"""Estimate the entire S1 backup footprint before the first optimizer update."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from fastwam.memory_s1.common import load_config, atomic_json
from fastwam.memory_s1.modules import MemoryModules


def tree_bytes(path):
    path = Path(path)
    if path.is_file():
        return path.stat().st_size
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file() and ".cache" not in file.parts and "__pycache__" not in file.parts)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--assets-local-only", action="store_true")
    args = parser.parse_args()
    cfg = load_config(args.config)
    model = MemoryModules()
    parameter_bytes = sum(parameter.numel() * 4 for parameter in model.parameters())
    root = Path(cfg["root"])
    resources = sum(tree_bytes(root / relative) for relative in (
        "resources/base", "resources/encoders", "resources/tokenizer", "resources/RMBench/data/download_cache",
        "resources/RMBench/assets", "resources/cache_s1", "resources/prepared", "resources/download_lock.json"))
    # FP32 parameters plus two FP32 AdamW moments; include file/RNG overhead separately.
    checkpoint_estimate = 3 * parameter_bytes + 16 * 2**20
    full_points = cfg["steps"] // cfg["checkpoint_every"] + 1
    weight_versions = cfg["steps"] // cfg["validate_every"] * 2
    recovery_package = 2 * checkpoint_estimate + 5 * parameter_bytes + 2 * 2**30
    native_run = full_points * checkpoint_estimate + weight_versions * parameter_bytes + 2 * 2**30
    planned = native_run + recovery_package + (0 if args.assets_local_only else resources)
    value = {"parameter_bytes_fp32": parameter_bytes, "full_checkpoint_estimate_bytes": checkpoint_estimate,
             "full_checkpoint_versions_budgeted": full_points, "resources_uncompressed_upper_bound_bytes": resources,
             "native_training_history_estimate_bytes": native_run, "recovery_package_uncompressed_estimate_bytes": recovery_package,
             "planned_new_bytes": planned, "assets_local_only": args.assets_local_only,
             "assumptions": "No compression/dedup savings. One extra stop checkpoint, all best versions, two local resume files; 2GiB each for logs/code/evaluation. Recompute if stops/recorded frames exceed this budget."}
    atomic_json(args.output, value)
    result = subprocess.run([cfg["hf"]["python"], str(root / "scripts/memory_s1/hf_tools.py"), "quota",
                             "--planned-bytes", str(planned), "--quota-gib", str(cfg["hf"]["quota_gib"]),
                             "--reserve-gib", str(cfg["hf"]["reserve_gib"])], check=True, capture_output=True, text=True)
    value["quota_check"] = json.loads(result.stdout)
    atomic_json(args.output, value)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
