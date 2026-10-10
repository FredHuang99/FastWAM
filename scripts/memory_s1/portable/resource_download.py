"""Recover S1 resources from public sources while preserving known checksums."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys

from common import digest, read, write


WAN_REPO = "Wan-AI/Wan2.2-TI2V-5B"
DATASET_REPO = "TianxingChen/RMBench"


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", required=True)
    for name in ("models", "data", "assets"):
        parser.add_argument(f"--{name}", action="store_true")
    args = parser.parse_args()
    if not any((args.models, args.data, args.assets)):
        parser.error("Choose at least one of --models --data --assets.")

    # Hub constants are evaluated at import time, so set these first.
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download

    root = Path(args.root).resolve()
    resource_root = root / "resources"
    lock_path = resource_root / "download_lock.json"
    lock = read(lock_path) if lock_path.is_file() else {"repositories": {}, "files": {}}
    lock.setdefault("repositories", {})
    lock.setdefault("files", {})
    expected = {name.replace("\\", "/"): row["sha256"]
                for name, row in lock["files"].items()}
    protection = root / "outputs/recovery_aws_v2/EXPECTED_DOWNLOADS.json"
    if protection.is_file():
        expected.update(read(protection)["files"])
    api = HfApi()

    def revision(repo, kind):
        # A commit from the obsolete DiffSynth repository cannot pin the Wan repo.
        key = f"{kind}:{repo}"
        value = lock["repositories"].get(key)
        if value is None:
            value = api.repo_info(repo, repo_type=kind).sha
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
            raise ValueError(f"Invalid immutable revision for {key}: {value!r}")
        if key not in lock["repositories"]:
            lock["repositories"][key] = value
            write(lock_path, lock)
        print(f"[source] {key} revision={value}", flush=True)
        return value

    def record(path):
        name = path.relative_to(root).as_posix()
        actual = digest(path)
        required = expected.get(name)
        if required is not None and actual != required:
            write(root / "outputs/recovery_aws_v2/DOWNLOAD_MISMATCH.json", {
                "file": name, "expected_sha256": required, "actual_sha256": actual,
            })
            raise ValueError(f"Original SHA256 mismatch: {name}. Files retained; not approved.")
        lock["files"][name] = {"bytes": path.stat().st_size, "sha256": actual}
        print(f"[verified] {name} {path.stat().st_size / 2**30:.3f}GiB", flush=True)

    def folder(directory):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and ".cache" not in path.parts:
                record(path)
        write(lock_path, lock)

    if args.models:
        for repo, destination, filenames in (
            ("yuanty/fastwam", "base", (
                "robotwin_uncond_3cam_384.pt",
                "robotwin_uncond_3cam_384_dataset_stats.json",
            )),
            (WAN_REPO, "encoders", (
                "Wan2.2_VAE.pth", "models_t5_umt5-xxl-enc-bf16.pth",
            )),
        ):
            for filename in filenames:
                target = resource_root / destination / filename
                name = target.relative_to(root).as_posix()
                if not (target.is_file() and expected.get(name) is not None
                        and digest(target) == expected[name]):
                    hf_hub_download(repo, filename, revision=revision(repo, "model"),
                                    local_dir=target.parent)
                else:
                    print(f"[reuse] {name}", flush=True)
                record(target)
                write(lock_path, lock)
        snapshot_download(WAN_REPO, revision=revision(WAN_REPO, "model"),
                          allow_patterns=["google/umt5-xxl/**"],
                          local_dir=resource_root / "tokenizer")
        folder(resource_root / "tokenizer")

    if args.data:
        script = resource_root / "RMBench/data/_download.py"
        if not script.is_file():
            raise FileNotFoundError(f"Restore the recorded RMBench source before downloading: {script}")
        subprocess.run([sys.executable, "-u", str(script), "put_back_block", "swap_blocks",
                        "--revision", revision(DATASET_REPO, "dataset")], cwd=root, check=True)
        folder(resource_root / "RMBench/data/download_cache")

    if args.assets:
        snapshot_download(DATASET_REPO, repo_type="dataset",
                          revision=revision(DATASET_REPO, "dataset"),
                          allow_patterns=["embodiments/**", "objects/**"],
                          local_dir=resource_root / "RMBench/assets")
        folder(resource_root / "RMBench/assets")

    write(lock_path, lock)
    print("[download] Requested resources verified; production source files were not edited.", flush=True)


if __name__ == "__main__":
    main()
