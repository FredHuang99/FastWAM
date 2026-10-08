"""Capture rebuild metadata without environment secrets or model downloads."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from fastwam.memory_s1.common import load_config, atomic_json

def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    cfg = load_config(args.config)
    output = Path(cfg["paths"]["run"]) / "provenance"
    output.mkdir(parents=True, exist_ok=True)
    commands = {"driver": ["nvidia-smi"], "disk": ["df", "-h"], "memory": ["free", "-h"],
        "training-pip-list": [sys.executable, "-m", "pip", "list", "--format=freeze"],
        "simulator-pip-list": [cfg["closed_loop"]["simulator_python"], "-m", "pip", "list", "--format=freeze"],
        "hf-pip-list": [cfg["hf"]["python"], "-m", "pip", "list", "--format=freeze"]}
    results = {}
    for name, command in commands.items():
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        (output / f"{name}.txt").write_text(result.stdout, encoding="utf-8")
        results[name] = command
    simulator_root = Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]
    subprocess.run(["git", "-C", str(simulator_root), "bundle", "create", str(output / "rmbench.source.bundle"), "--all"], check=True)
    patch = subprocess.check_output(["git", "-C", str(simulator_root), "diff", "HEAD", "--binary"], text=True)
    (output / "rmbench.git.diff").write_text(patch, encoding="utf-8")
    revision = subprocess.check_output(["git", "-C", str(simulator_root), "rev-parse", "HEAD"], text=True).strip()
    for name in ("wrapper/urdf_loader.py", "_vulkan_tricks.py"):
        path = Path(cfg["closed_loop"]["simulator_python"]).parent.parent / "lib/python3.10/site-packages/sapien" / name
        if path.exists():
            destination = output / "simulator_patches/sapien" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    atomic_json(output / "environment.json", {"python": sys.version, "platform": platform.platform(),
        "rmbench_commit": revision, "driver_capabilities": os.environ.get("NVIDIA_DRIVER_CAPABILITIES"),
        "training_python": sys.executable, "simulator_python": cfg["closed_loop"]["simulator_python"],
        "hf_python": cfg["hf"]["python"], "container_image_digest": os.environ.get("MWAM_IMAGE_DIGEST"),
        "commands": results, "config": cfg})
    print(f"[environment] Saved {output}")

if __name__ == "__main__":
    main()
