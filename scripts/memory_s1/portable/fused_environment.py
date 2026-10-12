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


CUDA_CHANNEL = "nvidia/label/cuda-12.6.3"


def cuda_package(name):
    return name == "cuda" or name.startswith((
        "cuda-", "libcublas", "libcufft", "libcufile", "libcurand",
        "libcusolver", "libcusparse", "libnpp", "libnvjpeg", "libnvjitlink",
        "libnvfatbin", "libnvvm", "nsight-", "gds-tools",
    ))


def conda_records(prefix):
    prefix = Path(prefix).resolve()
    if prefix != Path("/opt/rmbench-fused-env"):
        raise ValueError(f"CUDA migration is restricted to the isolated simulator: {prefix}")
    records = {}
    for path in sorted((prefix / "conda-meta").glob("*.json")):
        record = json.loads(path.read_text())
        records[record["name"]] = record
    if not records or not records.get("python", {}).get("version", "").startswith("3.10."):
        raise ValueError("Expected an existing Python 3.10 Conda clone")
    return records


def package_identity(record):
    return str(record["version"]), str(record.get("build_string", record.get("build")))


def cuda_migration(args, output):
    """Replace cloned CUDA requests together; never mutate Conda history by hand."""
    prefix = Path(args.prefix).resolve()
    records = conda_records(prefix)
    if args.command == "cuda-specs":
        output.mkdir(parents=True, exist_ok=False)
        metadata_dir = output / "conda-meta-before"
        metadata_dir.mkdir()
        for path in (prefix / "conda-meta").iterdir():
            if path.is_file() and (path.suffix == ".json" or path.name in ("history", "pinned")):
                shutil.copy2(path, metadata_dir / path.name)
        specs = []
        for name, record in sorted(records.items()):
            if name == "cuda-version":
                specs.append("cuda-version=12.6")
            elif cuda_package(name):
                # Unversioned component requests replace the clone's 12.4 exact requests.
                version = "=12.6.3" if name in ("cuda", "cuda-toolkit") else ""
                specs.append(f"{CUDA_CHANNEL}::{name}{version}")
            else:
                version, build = package_identity(record)
                specs.append(f"{name}={version}={build}")
        if "cuda-toolkit" not in records:
            specs.append(f"{CUDA_CHANNEL}::cuda-toolkit=12.6.3")
        (output / "requested-specs.txt").write_text("\n".join(specs) + "\n")
        (output / "before.json").write_text(json.dumps({"prefix": str(prefix), "records": records}, indent=2))
        print(f"[cuda] saved {len(records)} package records; replacing all CUDA component requests together", flush=True)
        return
    before = json.loads(Path(args.before).read_text())
    if before["prefix"] != str(prefix):
        raise ValueError("CUDA migration prefix differs from the saved inventory")
    if args.command == "cuda-plan":
        plan = json.loads(Path(args.plan).read_text())
        if plan.get("success") is not True:
            raise ValueError("Conda did not produce a successful solve; inspect the saved solver JSON")
        actions = plan.get("actions", {})
        if actions.get("PREFIX", str(prefix)) != str(prefix):
            raise ValueError("Conda planned a transaction against a different environment")
        final = dict(before["records"])
        for record in actions.get("UNLINK", []):
            final.pop(record["name"], None)
        for record in actions.get("LINK", []):
            if record.get("subdir", record.get("platform", "linux-64")) not in ("linux-64", "noarch", "linux"):
                raise ValueError(f"Non-Linux artifact in CUDA plan: {record['name']}")
            final[record["name"]] = record
    else:
        final = records
    for name, record in before["records"].items():
        if not cuda_package(name) and (
            name not in final or package_identity(record) != package_identity(final[name])
        ):
            raise ValueError(f"CUDA transaction would change a protected non-CUDA package: {name}")
    if final.get("cuda-toolkit", {}).get("version") != "12.6.3":
        raise ValueError("Expected the fixed CUDA Toolkit 12.6.3 release")
    if args.command == "cuda-plan":
        specs = [f"{name}={package_identity(record)[0]}={package_identity(record)[1]}"
                 for name, record in sorted(final.items())]
        output.with_suffix(".specs.txt").write_text("\n".join(specs) + "\n")
        for name in sorted(set(before["records"]) | set(final)):
            old = before["records"].get(name)
            new = final.get(name)
            if (package_identity(old) if old else None) != (package_identity(new) if new else None):
                print(f"[cuda plan] {name}: {package_identity(old) if old else 'absent'} -> {package_identity(new) if new else 'removed'}", flush=True)
    else:
        expected = json.loads(Path(args.plan).read_text())["records"]
        if {n: package_identity(r) for n, r in records.items()} != {n: package_identity(r) for n, r in expected.items()}:
            raise ValueError("Installed Conda records differ from the reviewed solve; stop before extension builds")
        compiler = subprocess.check_output([str(prefix / "bin/nvcc"), "--version"], text=True)
        if "release 12.6," not in compiler:
            raise ValueError(f"Unexpected CUDA compiler: {compiler}")
        print(compiler, flush=True)
    output.write_text(json.dumps({"prefix": str(prefix), "records": final}, indent=2))
    print(f"[{args.command}] verified; protected non-CUDA versions unchanged; report={output}", flush=True)


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
    parser.add_argument("command", choices=("snapshot", "copy-source", "verify", "cuda-specs", "cuda-plan", "cuda-check"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--source")
    parser.add_argument("--before")
    parser.add_argument("--prefix")
    parser.add_argument("--plan")
    args = parser.parse_args()
    output = Path(args.output)
    if args.command.startswith("cuda-"):
        cuda_migration(args, output)
        return
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
