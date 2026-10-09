"""Strict dense-data derivation and restartable distributed frozen-feature caching."""
from __future__ import annotations
import argparse
from datetime import timedelta
import os
from pathlib import Path
import shutil
import time
import h5py
import numpy as np
import torch
import torch.distributed as dist
from .common import (SCHEMA, atomic_json, atomic_torch, fingerprint, load_config,
                     make_cache_contract, read_json, sha256, ReleaseNormalizer, duration)
from .data import official_decoder, mosaic_rgb, observation_tensor, read_episode, choose_instruction


def migrate(cfg, parent_cfg):
    source, target = Path(parent_cfg["paths"]["prepared"]), Path(cfg["paths"]["prepared"])
    if source.resolve() == target.resolve():
        raise ValueError("Dense preparation must use a different directory.")
    original = read_json(source / "manifest.json")
    if (target / "manifest.json").exists():
        if read_json(target / "manifest.json").get("parent_manifest_sha") != fingerprint(original):
            raise ValueError("Existing dense preparation has a different parent; preserve it.")
    approval = read_json(source / "alignment_approved.json")
    flags = ("approved", "joint_order_confirmed", "gripper_units_confirmed", "next_record_targets_replay_confirmed",
             "whole_task_instructions_no_location_leak_confirmed", "rgb_preview_confirmed")
    if approval.get("manifest_sha") != fingerprint(original) or not all(approval.get(k) is True for k in flags):
        raise ValueError("The parent data needs an actual approved alignment record.")
    if not approval.get("reviewer") or not approval.get("notes"):
        raise ValueError("The parent approval lacks a reviewer or concrete evidence.")
    decoder_root = Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]
    if sha256(decoder_root / "data/decode_image_bit.py") != original["decoder_sha256"]:
        raise ValueError("Official decoder changed; a new review is required.")
    decoder = official_decoder(decoder_root)
    records = []
    for record in original["episodes"]:
        path = Path(cfg["root"]) / record["raw"]
        if sha256(path) != record["raw_sha256"]:
            raise ValueError(f"Original episode changed: {path}")
        old = torch.load(source / record["file"], map_location="cpu", weights_only=True)
        states, targets, cameras, kind, metadata, embedded = read_episode(path)
        instruction, instruction_source = choose_instruction(path, embedded)
        if (cameras != record["camera_paths"] or instruction != record["instruction"] or kind != record["source_kind"]
                or metadata != record["attributes"] or instruction_source != record["instruction_source"]
                or len(states) != record["length"] or not np.array_equal(states, old["states"].numpy())
                or not np.array_equal(targets, old["targets"].numpy())
                or old["anchors"].tolist() != list(range(0, len(states), 16))):
            raise ValueError(f"Data semantics differ from the reviewed parent: {record['episode_id']}")
        with h5py.File(path, "r") as file:
            for i in range(len(states)):
                # Newly included observations must decode successfully; none are silently removed.
                mosaic_rgb([decoder(file[key][i]) for key in cameras])
        value = dict(old)
        value["frame_ids"] = torch.arange(len(states))
        atomic_torch(target / record["file"], value)
        records.append(dict(record))
        print(f"[dense-audit] {record['episode_id']} frames={len(states)} split={record['split']}", flush=True)
    manifest = {**original, "episodes": records, "coverage": "all_native_observation_records",
                "parent_manifest_sha": fingerprint(original), "parent_approval_sha": sha256(source / "alignment_approved.json")}
    if (target / "manifest.json").exists() and read_json(target / "manifest.json") != manifest:
        raise ValueError("An incompatible dense preparation already exists; preserve it and use a new path.")
    atomic_json(target / "manifest.json", manifest)
    atomic_json(target / "alignment_approved.json", {**approval, "manifest_sha": fingerprint(manifest),
        "derivation": {"kind": "verified_identical_semantics_and_dense_rgb_decode",
                       "parent_prepared": str(source), "parent_manifest_sha": fingerprint(original),
                       "parent_approval": approval}})
    run = Path(cfg["paths"]["run"])
    run.mkdir(parents=True, exist_ok=True)
    admission_path = Path(parent_cfg["paths"]["run"]) / "base_admission.json"
    print("[integration-required] Data preparation does not inherit a manipulation-success gate. "
          "Create version-bound integration_admission.json after the integration checks.", flush=True)
    for name in ("provenance",):
        old_path = Path(parent_cfg["paths"]["run"]) / name
        if old_path.is_dir():
            destination = run / "parent_provenance"
            destination.mkdir(exist_ok=True)
            for entry in old_path.iterdir():
                if entry.is_file() and entry.suffix in (".txt", ".json"):
                    shutil.copy2(entry, destination / entry.name)
    scene_root = Path(parent_cfg["paths"]["run"]) / "scene_manifests"
    for entry in scene_root.rglob("*.json"):
        if entry.name.endswith(".owner.json"):
            continue
        destination = run / "scene_manifests" / entry.relative_to(scene_root)
        if destination.exists() and read_json(destination) != read_json(entry):
            raise ValueError("Inherited scene manifest conflicts with an existing new-run manifest.")
        atomic_json(destination, read_json(entry))
    if admission_path.exists():
        diagnostic = Path(read_json(admission_path).get("diagnostic_summary", ""))
        if diagnostic.is_file():
            shutil.copy2(diagnostic, run / "base_diagnostic_evidence.json")
    atomic_json(run / "dense_derivation.json", {"parent_manifest_sha": fingerprint(original),
        "manifest_sha": fingerprint(manifest), "split": {r["episode_id"]: r["split"] for r in records},
        "frames": sum(r["length"] for r in records), "configuration": cfg})


def checked_shard(path, signature, ids):
    marker_path = path.with_suffix(".complete.json")
    if not path.exists() or not marker_path.exists():
        return None
    marker = read_json(marker_path)
    if marker["signature"] != signature or marker["frame_ids"] != ids or marker["sha256"] != sha256(path):
        raise ValueError(f"Incomplete identity or checksum for cache shard: {path}")
    return marker


@torch.no_grad()
@torch.autocast("cuda", enabled=False)
def cache_observation(backbone, vae, text, normalizer, raw_state, images, device):
    """Encode one raw observation through the same dense-cache production path."""
    from .model import encode_latent
    image = observation_tensor(images, device)
    state = normalizer.normalize(raw_state[None], "state").to(device)
    latent = encode_latent(vae, image)
    feature, _, _ = backbone.encode_observation(latent, text, state, keep_kv=False)
    return {"mosaic": image, "proprio": state, "latent": latent, "feature": feature}


def cache(cfg):
    from .model import FrozenBackbone, load_observation_encoders, encode_text, encode_latent
    rank, world = int(os.environ.get("RANK", 0)), int(os.environ.get("WORLD_SIZE", 1))
    local = int(os.environ.get("LOCAL_RANK", 0))
    torch.cuda.set_device(local)
    device = torch.device("cuda", local)
    if world > 1:
        dist.init_process_group("gloo", timeout=timedelta(hours=8))
    root, prepared = Path(cfg["paths"]["cache"]), Path(cfg["paths"]["prepared"])
    root.mkdir(parents=True, exist_ok=True)
    manifest, approval = read_json(prepared / "manifest.json"), read_json(prepared / "alignment_approved.json")
    if manifest.get("coverage") != "all_native_observation_records" or approval["manifest_sha"] != fingerprint(manifest):
        raise ValueError("A verified dense preparation is required.")
    box = [None]
    if rank == 0:
        try:
            if cfg.get("integration"):
                from .integration import require_report
                require_report(cfg, "pilot")
            box[0] = {"contract": make_cache_contract(cfg, manifest)}
        except Exception as error:
            box[0] = {"error": f"{type(error).__name__}: {error}"}

    if world > 1:
        dist.broadcast_object_list(box, src=0)
    if "error" in box[0]:
        raise ValueError(box[0]["error"])
    contract, signature = box[0]["contract"], fingerprint(box[0]["contract"])
    identity_file = root / "identity.json"
    if identity_file.exists() and read_json(identity_file)["signature"] != signature:
        raise ValueError("This cache directory belongs to different encoder resources.")
    if rank == 0:
        atomic_json(identity_file, {"contract": contract, "signature": signature})
    decoder = official_decoder(Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"])
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    records = manifest["episodes"][rank::world]
    backbone = FrozenBackbone(cfg, device)
    vae, text_encoder, tokenizer = load_observation_encoders(cfg, device)
    total, completed, newly_encoded = sum(r["length"] for r in records), 0, 0
    started = time.monotonic()
    interrupted = False
    output_records = []
    for record in records:
        raw_path = Path(cfg["root"]) / record["raw"]
        if sha256(raw_path) != record["raw_sha256"]:
            raise ValueError(f"Raw data changed: {raw_path}")
        episode = torch.load(prepared / record["file"], map_location="cpu", weights_only=True)
        if episode["frame_ids"].tolist() != list(range(record["length"])):
            raise ValueError("Prepared dense IDs are incomplete.")
        text, text_valid = encode_text(text_encoder, tokenizer, record["instruction"], device)
        shards = []
        with h5py.File(raw_path, "r") as file, torch.no_grad():
            for start in range(0, record["length"], 64):
                ids = list(range(start, min(start + 64, record["length"])))
                relative = f"shards/{record['task']}_{Path(record['file']).stem}/{start:06d}.pt"
                path = root / relative
                marker = checked_shard(path, signature, ids)
                if marker is None:
                    fields = {name: [] for name in ("features", "latents", "proprio")}
                    for i in ids:
                        encoded = cache_observation(backbone, vae, text, normalizer, episode["states"][i],
                                                    [decoder(file[key][i]) for key in record["camera_paths"]], device)
                        state, latent, feature = encoded["proprio"], encoded["latent"], encoded["feature"]
                        if not torch.isfinite(feature).all() or not torch.isfinite(latent).all():
                            raise ValueError(f"Non-finite cache at {record['episode_id']}:{i}")
                        for name, tensor in (("features", feature), ("latents", latent), ("proprio", state)):
                            fields[name].append(tensor[0].detach().cpu())
                        newly_encoded += 1
                        if newly_encoded % 8 == 0:
                            elapsed = time.monotonic() - started
                            print(f"[frame] rank={rank} episode={record['episode_id']} id={i} encoded={newly_encoded} elapsed={duration(elapsed)}", flush=True)
                    atomic_torch(path, {"signature": signature, "frame_ids": torch.tensor(ids),
                                       **{name: torch.stack(values) for name, values in fields.items()}})
                    marker = {"signature": signature, "frame_ids": ids, "sha256": sha256(path)}
                    atomic_json(path.with_suffix(".complete.json"), marker)
                shards.append({"file": relative, "sha256": marker["sha256"], "first": ids[0], "last": ids[-1]})
                completed += len(ids)
                elapsed = time.monotonic() - started
                eta = elapsed / max(1, newly_encoded) * (total - completed)
                atomic_json(root / f"progress_rank_{rank}.json", {"rank": rank, "world": world, "completed_frames": completed,
                    "total_frames": total, "encoded_this_launch": newly_encoded, "seconds": elapsed, "eta_seconds": eta,
                    "signature": signature, "complete": False})
                print(f"[shard] rank={rank} {completed}/{total} ETA={duration(eta)}", flush=True)
                if (root / "STOP_REQUESTED").exists():
                    interrupted = True
                    break
        if interrupted:
            break
        destination = root / record["file"]
        value = {"signature": signature, "shards": shards, "anchors": episode["anchors"], "targets": episode["targets"],
                 "text": text[0].cpu(), "text_valid": text_valid[0].cpu(), "episode_id": record["episode_id"], "instruction": record["instruction"]}
        atomic_torch(destination, value)
        atomic_json(destination.with_suffix(".complete.json"), {"signature": signature, "sha256": sha256(destination)})
        output_records.append({**record, "cache_sha256": sha256(destination), "shards": shards})
    atomic_json(root / f"progress_rank_{rank}.json", {"rank": rank, "world": world, "completed_frames": completed,
        "total_frames": total, "encoded_this_launch": newly_encoded, "seconds": time.monotonic() - started,
        "eta_seconds": 0 if not interrupted else None, "signature": signature, "complete": not interrupted})
    atomic_json(root / f"rank_{rank}_manifest.json", {"signature": signature, "episodes": output_records, "interrupted": interrupted})
    if world > 1:
        dist.barrier()
    if rank == 0:
        partials = [read_json(root / f"rank_{i}_manifest.json") for i in range(world)]
        if not any(p["interrupted"] for p in partials):
            all_records = {r["episode_id"]: r for part in partials for r in part["episodes"]}
            if set(all_records) != {r["episode_id"] for r in manifest["episodes"]}:
                raise ValueError("Distributed cache lost or duplicated episodes.")
            atomic_json(root / "manifest.json", {"schema": SCHEMA, "signature": signature, "contract": contract,
                        "alignment": approval, "episodes": [all_records[r["episode_id"]] for r in manifest["episodes"]]})
            print("[complete] Dense cache manifest published.", flush=True)
        else:
            print("[stopped] Complete shards retained. Clear STOP_REQUESTED and rerun the same command.", flush=True)
    if world > 1:
        dist.destroy_process_group()
    return 2 if interrupted else 0


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("migrate", "cache"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--parent-config", default="configs/memory_s1/s1.yaml")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.command == "migrate":
        migrate(cfg, load_config(args.parent_config))
    else:
        raise SystemExit(cache(cfg))

if __name__ == "__main__":
    main()
