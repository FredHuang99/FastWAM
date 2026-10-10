"""Reconstruct dense tensors from byte-verified episodes; never invent alignment approval."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import h5py
import numpy as np
from PIL import Image
import torch

from recovery import admission, unique_file, verify_source_hashes
from fastwam.memory_s1.common import atomic_json, atomic_torch, fingerprint, load_config, sha256
from fastwam.memory_s1.data import choose_instruction, mosaic_rgb, official_decoder, read_episode
from fastwam.memory_s1.integration import source_semantics


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--ready", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    ready = Path(args.ready)
    prior_path, prior, reports = admission(ready)
    verify_source_hashes(ready, cfg["root"], assets=True)
    if source_semantics(cfg) != reports["data"]["source"]:
        raise ValueError("Collection/conversion sources differ from the verified prior semantics.")
    expected = {row["episode_id"]: row for row in reports["data"]["episodes"]}
    counts = Counter((key.split("/")[0], row["split"]) for key, row in expected.items())
    if len(expected) != 100 or sorted(counts.values()) != [5, 5, 45, 45]:
        raise ValueError(f"Unexpected saved data population/splits: {counts}")
    saved_manifest = None
    for path in ready.rglob("manifest.json"):
        value = json.loads(path.read_text(encoding="utf-8"))
        if fingerprint(value) == prior["binding"]["prepared_sha"]:
            if saved_manifest is not None and saved_manifest != value:
                raise ValueError("Conflicting prior prepared manifests.")
            saved_manifest = value
    saved_rows = {row["episode_id"]: row for row in saved_manifest["episodes"]} if saved_manifest else {}
    output = Path(cfg["paths"]["prepared"])
    if (output / "manifest.json").exists():
        existing = json.loads((output / "manifest.json").read_text())
        if not saved_manifest or existing != saved_manifest:
            state = output / "recovery_verification.json"
            if not state.is_file() or json.loads(state.read_text())["prior_admission_sha256"] != sha256(prior_path):
                raise ValueError("Existing preparation has another origin; preserve it and use a new directory.")
    decoder_root = Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]
    decoder = official_decoder(decoder_root)
    discovered = {}
    for task in ("put_back_block", "swap_blocks"):
        for path in sorted((Path(cfg["paths"]["raw"]) / task / "aloha_agilex/data").glob("*.hdf5")):
            discovered[f"{task}/{path.stem}"] = path
    if set(discovered) != set(expected):
        raise ValueError(f"Episode set differs; missing={set(expected)-set(discovered)}, extra={set(discovered)-set(expected)}")
    records, checks, frame_total = [], [], 0
    for episode_id, path in sorted(discovered.items()):
        old = expected[episode_id]
        if sha256(path) != old["raw_sha256"]:
            raise ValueError(f"Original episode checksum differs: {episode_id}")
        states, actions, cameras, kind, metadata, embedded = read_episode(path)
        instruction, instruction_source = choose_instruction(path, embedded)
        duplicates = (np.nonzero(np.all(np.diff(states, axis=0) == 0, axis=1))[0]+1).tolist()
        events = {str(j): (np.nonzero(np.abs(np.diff(actions[:, j])) > 0.05)[0]+1).tolist() for j in (6, 13)}
        tail = list(range(0, len(states), 16))[-1]
        observed = {"length": len(states), "last_anchor": tail, "last_valid_actions": min(32, len(actions)-tail),
                    "frequency_field": metadata.get("stored_frequency"), "duplicate_command_record_ids": duplicates,
                    "gripper_target_event_ids": events}
        for key, value in observed.items():
            if value != old[key]:
                raise ValueError(f"Saved label/timeline check differs: {episode_id}/{key}")
        task = episode_id.split("/")[0]
        record = {"episode_id": episode_id, "task": task, "raw": str(path.relative_to(cfg["root"])),
                  "raw_sha256": old["raw_sha256"], "file": f"episodes/{task}_{path.stem}.pt", "length": len(states),
                  "camera_paths": cameras, "instruction": instruction, "instruction_source": instruction_source,
                  "source_kind": kind, "attributes": metadata, "split": old["split"],
                  "joint_delta_abs_percentiles": np.percentile(np.abs(actions-states), [50, 95, 99], axis=0).tolist(),
                  "instruction_sha": fingerprint(instruction)}
        if saved_manifest:
            original = saved_rows[episode_id]
            if any(record[key] != original[key] for key in record):
                raise ValueError(f"Original manifest semantics differ: {episode_id}")
            record = original
        preview = None
        with h5py.File(path, "r") as file:
            for index in range(len(states)):
                image = mosaic_rgb([decoder(file[key][index]) for key in cameras])
                if preview is None:
                    preview = image.permute(1, 2, 0).numpy()
        # Targets are unchanged; validity and repeated tail padding are constructed by the actual sampler.
        tensors = {"states": torch.from_numpy(states), "targets": torch.from_numpy(actions),
                   "frame_ids": torch.arange(len(states)), "anchors": torch.arange(0, len(states), 16)}
        atomic_torch(output / record["file"], tensors)
        picture = output / "audit_images" / f"{task}_{path.stem}.png"
        picture.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(preview).save(picture)
        records.append(record)
        checks.append({"episode_id": episode_id, "raw_sha256": old["raw_sha256"], "split": old["split"], **observed})
        frame_total += len(states)
        print(f"[rebuild] {len(records)}/100 {episode_id} frames={len(states)} split={old['split']}", flush=True)
    if frame_total != 47579:
        raise ValueError(f"Full observation coverage changed: {frame_total}, expected 47579.")
    if saved_manifest:
        manifest = saved_manifest
    else:
        manifest = {"schema": "fastwam-memory-s1-v1", "episodes": records, "rejected": [],
                    "decoder_sha256": sha256(decoder_root / "data/decode_image_bit.py"),
                    "timeline": "t is native observation record; target[t] is the next recorded state, not a proven fixed-Hz control command",
                    "joint_order": "left6,left_gripper,right6,right_gripper", "action_offset": 1,
                    "instruction_policy": "whole_task_seen_first_fixed_for_episode_no_subtask",
                    "coverage": "all_native_observation_records",
                    "recovery": {"prior_admission_sha256": sha256(prior_path), "old_prepared_sha": prior["binding"]["prepared_sha"]}}
    atomic_json(output / "manifest.json", manifest)
    approved = None
    for path in ready.rglob("alignment_approved.json"):
        value = json.loads(path.read_text(encoding="utf-8"))
        if (saved_manifest and sha256(path) == reports["data"]["prior_review_sha"]
                and value.get("manifest_sha") == fingerprint(manifest) and value.get("approved") is True):
            approved = value
    approved_path = output / "alignment_approved.json"
    if approved:
        atomic_json(approved_path, approved)
    elif approved_path.exists():
        # A separately reviewed reconstruction is retained only while its manifest is unchanged.
        value = json.loads(approved_path.read_text())
        if value.get("manifest_sha") != fingerprint(manifest) or value.get("approved") is not True:
            raise ValueError("Existing review no longer matches this reconstruction.")
        approved = value
    else:
        atomic_json(output / "alignment_review_template.json", {"manifest_sha": fingerprint(manifest), "approved": False,
            "joint_order_confirmed": False, "gripper_units_confirmed": False,
            "next_record_targets_replay_confirmed": False, "whole_task_instructions_no_location_leak_confirmed": False,
            "rgb_preview_confirmed": False, "reviewer": "", "notes": "Review recovered source checks, instructions, RGB previews and physical replay evidence. Prior review file is missing."})
    result = {"prior_admission_sha256": sha256(prior_path), "source_semantics_identical": True,
              "raw_files_identical": True, "dense_frames": frame_total, "episodes": checks,
              "manifest_sha": fingerprint(manifest), "original_manifest_restored": saved_manifest is not None,
              "alignment_review_available": approved is not None, "phase": "ready_for_checks" if approved else "pending_alignment_review"}
    atomic_json(output / "recovery_verification.json", result)
    if not approved:
        print(f"[pending-review] {output / 'alignment_review_template.json'}; no approval was fabricated.", flush=True)
        raise SystemExit(2)
    print("[prepared] 100 byte-verified episodes, original splits, all 47579 observations; real review retained.")


if __name__ == "__main__":
    main()
