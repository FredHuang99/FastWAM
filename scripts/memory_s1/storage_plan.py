"""Budget private Hub history before caching/training without assuming dedup savings."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
from fastwam.memory_s1.common import load_config, atomic_json, read_json, fingerprint, make_cache_contract, sha256
from fastwam.memory_s1.history import recipe
from fastwam.memory_s1.modules import MemoryModules


def resource_paths(cfg):
    root = Path(cfg["root"])
    paths = [Path(cfg["paths"][key]) for key in ("base", "stats", "vae", "t5", "tokenizer", "raw", "prepared", "cache")]
    paths += [root / cfg["closed_loop"]["simulator_root"] / "assets", root / "resources/download_lock.json"]
    unique = []
    for path in sorted(set(p.absolute() for p in paths), key=lambda p: len(p.parts)):
        if not any(parent == path or parent in path.parents for parent in unique):
            unique.append(path)
    return unique


def tree_bytes(path):
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file() and not {".cache", "__pycache__"}.intersection(p.parts))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--assets-local-only", action="store_true")
    args = parser.parse_args()
    cfg = load_config(args.config)
    prepared = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    cache_signature = fingerprint(make_cache_contract(cfg, prepared))
    frames = sum(record["length"] for record in prepared["episodes"])
    parameter_bytes = sum(p.numel() * 4 for p in MemoryModules().parameters())
    full = 3 * parameter_bytes + 16 * 2**20
    initial = parameter_bytes + 16 * 2**20
    updates = set(range(cfg["checkpoint_every"], cfg["steps"] + 1, cfg["checkpoint_every"]))
    updates.update(range(cfg["validate_every"], cfg["steps"] + 1, cfg["validate_every"]))
    updates.add(cfg["steps"])
    settings = cfg.get("backup_budget", {})
    run = Path(cfg["paths"]["run"])
    remote_step, remote_phase = -1, "train"
    for name in ("LATEST_REMOTE.json", "RESTORE_REMOTE.json"):
        path = run / name
        if not path.exists():
            continue
        pointer = read_json(path)
        checkpoint = run / "checkpoints" / pointer["directory"]
        marker = checkpoint / "complete.json"
        if (marker.exists() and (checkpoint / "resume.pt").exists()
                and read_json(marker)["completed_updates"] == pointer["step"]
                and sha256(checkpoint / "resume.pt") == pointer["resume_sha256"]):
            if pointer["step"] >= remote_step:
                remote_step = pointer["step"]
                remote_phase = read_json(marker).get("phase", "train")
    updates = {step for step in updates if step > remote_step}
    extra = settings.get("extra_stop_checkpoints", 1)
    weights = settings.get("weight_versions", 2 * cfg["steps"] // cfg["validate_every"])
    auxiliary = int(settings.get("auxiliary_history_gib", 4) * 2**30)
    remaining_validations = sum(step > remote_step for step in range(cfg["validate_every"], cfg["steps"] + 1, cfg["validate_every"]))
    if remote_phase == "validation":
        remaining_validations += 1
    weights = min(weights, 2 * remaining_validations)
    native = (initial if remote_step < 0 else 0) + (len(updates) + extra) * full + weights * parameter_bytes + auxiliary
    recovery = 2 * full + (cfg["steps"] // cfg["validate_every"] + 1) * parameter_bytes + 2 * 2**30
    # BF16 features/latent, FP32 proprio, int64 ID; allow metadata and serialization overhead.
    dense_estimate = int(frames * (120 * 3072 * 2 + 48 * 24 * 20 * 2 + 14 * 4 + 8) * 1.03) + 128 * 2**20
    inventory = {str(p): tree_bytes(p) for p in resource_paths(cfg)}
    actual_cache = tree_bytes(Path(cfg["paths"]["cache"]))
    resources = sum(inventory.values()) - actual_cache + max(actual_cache, dense_estimate)
    script = Path(cfg["root"]) / "scripts/memory_s1/hf_tools.py"
    def quota(planned):
        result = subprocess.run([cfg["hf"]["python"], str(script), "quota", "--planned-bytes", str(planned),
                                 "--quota-gib", str(cfg["hf"]["quota_gib"]), "--reserve-gib", str(cfg["hf"]["reserve_gib"])],
                                capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr.strip())
        return json.loads(result.stdout)
    training_budget = quota(native + recovery)
    assets_local_only, asset_error = args.assets_local_only, None
    combined_budget = None
    if not assets_local_only:
        try:
            combined_budget = quota(native + recovery + resources)
        except RuntimeError as error:
            assets_local_only, asset_error = True, str(error)
    value = {"checkpoint_every": cfg["checkpoint_every"], "recipe_sha": fingerprint(recipe(cfg)), "cache_signature": cache_signature,
             "parameter_bytes_fp32": parameter_bytes, "initial_checkpoint_estimate_bytes": initial,
             "full_checkpoint_estimate_bytes": full, "periodic_completed_updates": sorted(updates),
             "last_verified_remote_update": remote_step, "remote_phase": remote_phase, "extra_stop_checkpoints": extra, "weight_versions": weights, "auxiliary_history_bytes": auxiliary,
             "dense_frames": frames, "dense_cache_estimate_bytes": dense_estimate, "resource_inventory": inventory,
             "resources_uncompressed_upper_bound_bytes": resources, "native_training_history_estimate_bytes": native,
             "recovery_package_uncompressed_estimate_bytes": recovery, "assets_local_only": assets_local_only,
             "asset_budget_error": asset_error, "quota_check": combined_budget or training_budget,
             "training_quota_check": training_budget, "planned_new_bytes": native + recovery + (0 if assets_local_only else resources),
             "assumptions": "No compression or dedup savings; private historical blobs count. Initial checkpoint has no moments. Reserve includes one extra stop and all milestone/best weights. Re-run after additional stops, recorded evaluation frames or other account uploads."}
    atomic_json(args.output, value)
    print(json.dumps(value, indent=2))
    if assets_local_only:
        print("[assets-local-only] Training recovery fits; keep a SHA256-verified split resources package locally. No assets upload is authorized by this budget.")

if __name__ == "__main__":
    main()
