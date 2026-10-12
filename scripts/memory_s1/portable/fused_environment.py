"""Explicit environment inventory/copy checks for the isolated H100 simulator."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata as metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inventory():
    result = {"python": sys.version, "executable": sys.executable, "packages": {}}
    for name, dist in (("torch", "torch"), ("sapien", "sapien"), ("mplib", "mplib"),
                       ("curobo", "nvidia-curobo"), ("pytorch3d", "pytorch3d"), ("warp", "warp-lang")):
        module = importlib.import_module(name)
        root = Path(module.__file__).resolve().parent
        result["packages"][name] = {"version": metadata.version(dist), "root": str(root)}
        if name in ("sapien", "mplib"):
            result["packages"][name]["files"] = {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob("*"))
                                                 if p.is_file() and p.suffix in (".py", ".so", ".json")}
    import torch
    result.update(cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0), architecture=list(torch.cuda.get_device_capability(0)))
    result["pip_list"] = json.loads(subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"], text=True))
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("snapshot", "copy-source", "verify"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--source")
    parser.add_argument("--before")
    args = parser.parse_args()
    output = Path(args.output)
    if args.command == "copy-source":
        source = Path(args.source).resolve()
        if not (source / "setup.py").is_file():
            raise ValueError(f"Missing saved extension source: {source}")
        exclude = {"build", "dist", ".git", "__pycache__", ".pytest_cache"}
        def ignore(directory, names):
            return [n for n in names if n in exclude or n.endswith((".so", ".pyc", ".egg-info"))]
        files = {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob("*")) if p.is_file()
                 and not set(p.relative_to(source).parts) & exclude
                 and not any(s.endswith(".egg-info") for s in p.relative_to(source).parts)
                 and p.suffix not in (".so", ".pyc")}
        marker = output.with_suffix(".source.json")
        if output.exists():
            if not marker.exists() or json.loads(marker.read_text())["files"] != files:
                raise ValueError("Existing build source differs; preserve it and use a fresh build directory")
        else:
            shutil.copytree(source, output, ignore=ignore, symlinks=False)
            marker.write_text(json.dumps({"source": str(source), "files": files}, indent=2))
        print(f"[source copy] {source} -> {output}; original build tree unchanged", flush=True)
        return
    value = inventory()
    if args.command == "verify":
        before = json.loads(Path(args.before).read_text())
        for name in ("sapien", "mplib"):
            a, b = before["packages"][name], value["packages"][name]
            if a["version"] != b["version"] or a["files"] != b["files"]:
                raise ValueError(f"{name} version/patches changed during environment creation")
        if not value["packages"]["torch"]["version"].startswith("2.6.0") or value["cuda"] != "12.6":
            raise ValueError("Expected PyTorch 2.6.0 / CUDA 12.6")
        if value["architecture"] != [9, 0] or sys.version_info[:2] != (3, 10):
            raise ValueError("Expected Python 3.10 on SM90")
        if value["packages"]["curobo"]["version"] != before["packages"]["curobo"]["version"]:
            raise ValueError("CuRobo source version changed")
        for module in ("curobo.curobolib.lbfgs_step_cu", "pytorch3d._C"):
            path = Path(importlib.import_module(module).__file__).resolve()
            if not path.is_relative_to(Path(sys.prefix).resolve()):
                raise ValueError(f"Extension still imports from old environment/source: {path}")
            value.setdefault("extensions", {})[module] = {"path": str(path), "sha256": sha(path)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(value, indent=2), encoding="utf-8")
    print(f"[{args.command}] {output}", flush=True)


if __name__ == "__main__":
    main()
