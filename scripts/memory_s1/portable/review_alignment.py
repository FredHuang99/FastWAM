"""Record an explicit evidence-backed review when the original approval file was lost."""
from __future__ import annotations

import argparse
from pathlib import Path

from fastwam.memory_s1.common import load_config, read_json, fingerprint, sha256, atomic_json
from fastwam.memory_s1.prepare import admit


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--evidence", required=True, help="Directory containing task/alignment_replay.json")
    args = parser.parse_args()
    cfg = load_config(args.config)
    prepared = Path(cfg["paths"]["prepared"])
    manifest = read_json(prepared / "manifest.json")
    reconstruction = read_json(prepared / "recovery_verification.json")
    if reconstruction["manifest_sha"] != fingerprint(manifest) or not reconstruction["raw_files_identical"]:
        raise ValueError("Reconstruction evidence is stale or unverified.")
    evidence = {}
    for task in ("put_back_block", "swap_blocks"):
        path = Path(args.evidence) / task / "alignment_replay.json"
        value = read_json(path)
        if value.get("feedback_source") != "physical_qpos_unclipped_gripper" or not value.get("targets"):
            raise ValueError(f"Review requires actual physical feedback, not command echo: {path}")
        evidence[task] = {"path": str(path.resolve()), "sha256": sha256(path)}
    print("Review source/timeline checks:", prepared / "recovery_verification.json")
    print("Review RGB previews:", prepared / "audit_images")
    print("Review replay feedback and object images:", args.evidence)
    print("Whole-task instructions:")
    for text in sorted({row["instruction"] for row in manifest["episodes"]}):
        print(text)
    keys = ("joint_order_confirmed", "gripper_units_confirmed", "next_record_targets_replay_confirmed",
            "whole_task_instructions_no_location_leak_confirmed", "rgb_preview_confirmed")
    review = {"manifest_sha": fingerprint(manifest), "approved": False, "recovery_evidence": evidence,
              "reconstruction_sha256": sha256(prepared / "recovery_verification.json")}
    for key in keys:
        if input(f"After reviewing the evidence, confirm {key} [type yes; default no]: ").strip().lower() != "yes":
            raise SystemExit("Review remains unapproved; no training admission was changed.")
        review[key] = True
    review["reviewer"] = input("Reviewer: ").strip()
    review["notes"] = input("Concrete evidence and remaining limitations: ").strip()
    if not review["reviewer"] or not review["notes"]:
        raise SystemExit("A reviewer and concrete notes are required.")
    review["approved"] = True
    output = Path(cfg["paths"]["run"]) / "alignment_recovery_review.json"
    atomic_json(output, review)
    admit(cfg, output)
    print("Explicit reconstruction review recorded:", output)


if __name__ == "__main__":
    main()
