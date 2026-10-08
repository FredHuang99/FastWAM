"""Convert, audit, approve alignment, and build version-bound frozen caches."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import h5py
import numpy as np
import torch
from PIL import Image

from .common import (SCHEMA, TASKS, ReleaseNormalizer, atomic_json, atomic_torch, fingerprint,
                     load_config, make_cache_contract, read_json, sha256, duration)
from .data import official_decoder, mosaic_rgb, read_episode, choose_instruction


def convert(cfg):
    output = Path(cfg["paths"]["prepared"])
    decoder_root = Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]
    decoder = official_decoder(decoder_root)
    records, rejected = [], []
    for task in TASKS:
        paths = sorted((Path(cfg["paths"]["raw"]) / task / "aloha_agilex/data").glob("*.hdf5"))
        if not paths:
            raise FileNotFoundError(f"No official demo_clean episodes for {task}.")
        for path in paths:
            try:
                states, targets, cameras, kind, metadata, embedded = read_episode(path)
                instruction, instruction_source = choose_instruction(path, embedded)
                if not instruction:
                    raise ValueError("Empty instruction.")
                episode_id = f"{task}/{path.stem}"
                frame_ids = list(range(0, len(states), 8))
                anchors = list(range(0, len(states), 16))
                rgb_preview = None
                with h5py.File(path, "r") as file:
                    # Decode every observation used by the cache before accepting the episode.
                    for index in frame_ids:
                        images = [decoder(file[key][index]) for key in cameras]
                        mosaic = mosaic_rgb(images)
                        if rgb_preview is None:
                            rgb_preview = ((mosaic.permute(1, 2, 0) + 1) * 127.5).byte().numpy()
                name = f"episodes/{task}_{path.stem}.pt"
                atomic_torch(output / name, {"states": torch.from_numpy(states), "targets": torch.from_numpy(targets),
                                            "frame_ids": torch.tensor(frame_ids), "anchors": torch.tensor(anchors)})
                preview = output / "audit_images" / f"{task}_{path.stem}.png"
                preview.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(rgb_preview).save(preview)
                record = {"episode_id": episode_id, "task": task, "raw": str(path.relative_to(cfg["root"])),
                          "raw_sha256": sha256(path), "file": name, "length": len(states), "camera_paths": cameras,
                          "instruction": instruction, "instruction_source": instruction_source,
                          "source_kind": kind, "attributes": metadata,
                          "joint_delta_abs_percentiles": np.percentile(np.abs(targets - states), [50, 95, 99], axis=0).tolist(),
                          "instruction_sha": fingerprint(instruction)}
                records.append(record)
                print(f"[convert] {episode_id}: records={len(states)} archive={len(frame_ids)} anchors={len(anchors)}", flush=True)
            except Exception as error:
                rejected.append({"path": str(path), "error": str(error)})
                print(f"[reject] {path}: {error}", flush=True)
    for task in TASKS:
        task_records = [record for record in records if record["task"] == task]
        if len(task_records) < 2:
            raise ValueError(f"Too few valid episodes for {task}; see conversion output.")
        ordered = sorted(task_records, key=lambda record: fingerprint([17, record["episode_id"]]))
        validation_count = max(1, round(0.1 * len(ordered)))
        for index, record in enumerate(ordered):
            record["split"] = "val" if index < validation_count else "train"
    manifest = {"schema": SCHEMA, "episodes": records, "rejected": rejected,
                "decoder_sha256": sha256(decoder_root / "data/decode_image_bit.py"),
                "timeline": "t is native observation record; target[t] is the next recorded state, not a proven fixed-Hz control command",
                "joint_order": "left6,left_gripper,right6,right_gripper", "action_offset": 1,
                "instruction_policy": "whole_task_seen_first_fixed_for_episode_no_subtask"}
    atomic_json(output / "manifest.json", manifest)
    atomic_json(output / "alignment_review_template.json", {
        "manifest_sha": fingerprint(manifest), "approved": False,
        "joint_order_confirmed": False, "gripper_units_confirmed": False,
        "next_record_targets_replay_confirmed": False, "whole_task_instructions_no_location_leak_confirmed": False,
        "rgb_preview_confirmed": False, "reviewer": "", "notes": "Fill after examining audit images, official source, and replay results."})
    print(f"[audit] Valid={len(records)} rejected={len(rejected)}; alignment remains unapproved.", flush=True)


def admit(cfg, review):
    manifest = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    value = read_json(review)
    required = ("approved", "joint_order_confirmed", "gripper_units_confirmed", "next_record_targets_replay_confirmed",
                "whole_task_instructions_no_location_leak_confirmed", "rgb_preview_confirmed")
    if value.get("manifest_sha") != fingerprint(manifest) or not all(value.get(key) is True for key in required):
        raise ValueError("Review must match this manifest and confirm every alignment check; do not guess missing evidence.")
    if not value.get("reviewer") or not value.get("notes"):
        raise ValueError("Record the reviewer and concrete replay/inspection evidence.")
    atomic_json(Path(cfg["paths"]["prepared"]) / "alignment_approved.json", value)


def build_cache(cfg, device):
    from .model import FrozenBackbone, load_observation_encoders, encode_text, encode_latent
    source = Path(cfg["paths"]["prepared"])
    manifest = read_json(source / "manifest.json")
    approval = read_json(source / "alignment_approved.json")
    if approval["manifest_sha"] != fingerprint(manifest) or approval["approved"] is not True:
        raise ValueError("A matching approved alignment review is required before caching.")
    root = Path(cfg["paths"]["cache"])
    contract = make_cache_contract(cfg, manifest)
    signature = fingerprint(contract)
    backbone = FrozenBackbone(cfg, device)
    vae, text_encoder, tokenizer = load_observation_encoders(cfg, device)
    decoder = official_decoder(Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"])
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    records = []
    started = time.monotonic()
    for number, record in enumerate(manifest["episodes"]):
        destination = root / record["file"]
        if destination.is_file() and destination.with_suffix(".complete.json").is_file():
            marker = read_json(destination.with_suffix(".complete.json"))
            if marker["signature"] != signature or marker["sha256"] != sha256(destination):
                raise ValueError(f"Cache signature/checksum mismatch: {destination}.")
        else:
            raw_path = Path(cfg["root"]) / record["raw"]
            if sha256(raw_path) != record["raw_sha256"]:
                raise ValueError(f"Raw episode changed: {raw_path}.")
            episode = torch.load(source / record["file"], map_location="cpu", weights_only=True)
            text, text_valid = encode_text(text_encoder, tokenizer, record["instruction"], device)
            features, latents, proprio = [], [], []
            with h5py.File(raw_path, "r") as file, torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                for index in episode["frame_ids"].tolist():
                    mosaic = mosaic_rgb([decoder(file[key][index]) for key in record["camera_paths"]])[None].to(device)
                    state = normalizer.normalize(episode["states"][index][None].to(device), "state")
                    latent = encode_latent(vae, mosaic)
                    feature, _, _ = backbone.encode_observation(latent, text, state, keep_kv=False)
                    features.append(feature[0].cpu())
                    latents.append(latent[0].cpu())
                    proprio.append(state[0].cpu())
            value = {"signature": signature, "features": torch.stack(features), "latents": torch.stack(latents),
                     "proprio": torch.stack(proprio), "frame_ids": episode["frame_ids"], "anchors": episode["anchors"],
                     "targets": episode["targets"], "text": text[0].cpu(), "text_valid": text_valid[0].cpu(),
                     "episode_id": record["episode_id"], "instruction": record["instruction"]}
            atomic_torch(destination, value)
            atomic_json(destination.with_suffix(".complete.json"), {"signature": signature, "sha256": sha256(destination)})
        records.append({**record, "cache_sha256": sha256(destination)})
        elapsed = time.monotonic() - started
        print(f"[cache] {number+1}/{len(manifest['episodes'])} elapsed={duration(elapsed)} ETA={duration(elapsed/(number+1)*(len(manifest['episodes'])-number-1))}", flush=True)
    atomic_json(root / "manifest.json", {"schema": SCHEMA, "signature": signature, "contract": contract,
                                       "alignment": approval, "episodes": records})


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("convert", "admit", "cache"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--review")
    parser.add_argument("--device", default="cuda:0")
    args = parser.parse_args()
    cfg = load_config(args.config)
    if args.command == "convert":
        convert(cfg)
    elif args.command == "admit":
        if not args.review:
            parser.error("admit requires --review")
        admit(cfg, args.review)
    else:
        build_cache(cfg, torch.device(args.device))


if __name__ == "__main__":
    main()
