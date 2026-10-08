"""Prepare a review record from executed base diagnostics; never auto-approve it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--diagnostic", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root)
    diagnostic = json.loads(Path(args.diagnostic).read_text())
    if len(diagnostic["episodes"]) != 20 or any(row["condition"] != "gate_zero" for row in diagnostic["episodes"]):
        raise ValueError("Admission requires gate-zero base diagnostics for 10 scenarios per task.")
    value = {"base_sha256": digest(root / "resources/base/robotwin_uncond_3cam_384.pt"),
             "stats_sha256": digest(root / "resources/base/robotwin_uncond_3cam_384_dataset_stats.json"),
             "diagnostic_summary": str(Path(args.diagnostic).resolve()), "interface_correct": False,
             "basic_manipulation_adequate": False, "reviewer": "",
             "notes": "Review joint order, gripper ranges, grasp/transport/button prefixes and failures; full memory-task success is not the admission criterion."}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
