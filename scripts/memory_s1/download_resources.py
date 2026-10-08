"""Download only approved S1 resources and record immutable revisions/checksums."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

from huggingface_hub import HfApi, hf_hub_download, snapshot_download


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--models", action="store_true")
    parser.add_argument("--data", action="store_true")
    parser.add_argument("--assets", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    api = HfApi()
    resource_root = root / "resources"
    lock_path = resource_root / "download_lock.json"
    lock = json.loads(lock_path.read_text()) if lock_path.is_file() else {"repositories": {}, "files": {}}
    def revision(repo, kind):
        key = f"{kind}:{repo}"
        if key not in lock["repositories"]:
            lock["repositories"][key] = api.repo_info(repo, repo_type=kind).sha
            resource_root.mkdir(parents=True, exist_ok=True)
            lock_path.write_text(json.dumps(lock, indent=2))
        return lock["repositories"][key]
    if args.models:
        for repo, destination, filenames in (
            ("yuanty/fastwam", "base", ["robotwin_uncond_3cam_384.pt", "robotwin_uncond_3cam_384_dataset_stats.json"]),
            ("DiffSynth-Studio/Wan-Series-Converted-Safetensors", "encoders", ["Wan2.2_VAE.safetensors", "models_t5_umt5-xxl-enc-bf16.safetensors"])):
            for filename in filenames:
                hf_hub_download(repo, filename, revision=revision(repo, "model"), local_dir=resource_root / destination)
        snapshot_download("Wan-AI/Wan2.1-T2V-1.3B", revision=revision("Wan-AI/Wan2.1-T2V-1.3B", "model"),
                          allow_patterns=["google/umt5-xxl/**"], local_dir=resource_root / "tokenizer")
    repo = "TianxingChen/RMBench"
    if args.data:
        script = resource_root / "RMBench/data/_download.py"
        subprocess.run([str(Path(__import__("sys").executable)), str(script), "put_back_block", "swap_blocks",
                        "--revision", revision(repo, "dataset")], check=True)
    if args.assets:
        snapshot_download(repo, repo_type="dataset", revision=revision(repo, "dataset"),
                          allow_patterns=["embodiments/**", "objects/**"], local_dir=resource_root / "RMBench/assets")
    for folder in ("base", "encoders", "tokenizer", "RMBench/data/download_cache", "RMBench/assets"):
        directory = resource_root / folder
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_file() and ".cache" not in path.parts:
                relative = str(path.relative_to(root))
                lock["files"][relative] = {"bytes": path.stat().st_size, "sha256": digest(path)}
                print(f"[verified] {relative} {path.stat().st_size/2**30:.3f}GiB", flush=True)
    lock_path.write_text(json.dumps(lock, indent=2))


if __name__ == "__main__":
    main()
