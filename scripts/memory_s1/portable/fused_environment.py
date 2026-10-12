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
import time


CUDA_CHANNEL = "nvidia/label/cuda-12.6.3"
CUDA_DEVELOPMENT = {
    # Explicit compiler/header/library roots avoid the release's broken aggregate
    # libraries-dev dependency on an unpublished libnvjpeg-dev version.
    "cuda-minimal-build": "12.6.3", "cuda-nvcc": "12.6.85",
    "cuda-nvrtc-dev": "12.6.85",
    "cuda-nvtx": "12.6.77", "cuda-cupti": "12.6.80",
    "libcublas-dev": "12.6.4.1", "libcusolver-dev": "11.7.1.2",
    "libcusparse-dev": "12.5.4.2", "libcurand-dev": "10.3.7.77",
    "libcufft-dev": "11.3.0.4",
}


def cuda_package(name):
    return name in ("cuda", "cudatoolkit", "nvidia-gds", "_cuda_mutex", "_cuda_compiler_mutex") or name.startswith((
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
    build = record.get("build_string", record.get("build"))
    if build is None:
        raise ValueError(f"Conda record has no build string: {record['name']}")
    return str(record["version"]), str(build)


def protected_packages(before, after):
    changed = [name for name, record in before.items() if not cuda_package(name) and (
        name not in after or package_identity(record) != package_identity(after[name]))]
    if changed:
        raise ValueError(f"Transaction changes protected non-CUDA packages: {changed}")


def solved_records(path, prefix, initial):
    plan = json.loads(Path(path).read_text())
    if plan.get("success") is not True:
        raise ValueError(f"Conda did not produce a successful solve: {path}")
    actions = plan.get("actions", {})
    if actions.get("PREFIX", str(prefix)) != str(prefix):
        raise ValueError("Conda planned a transaction against a different environment")
    final = dict(initial)
    for record in actions.get("UNLINK", []):
        final.pop(record["name"], None)
    for record in actions.get("LINK", []):
        if record.get("subdir", record.get("platform", "linux-64")) not in ("linux-64", "noarch", "linux"):
            raise ValueError(f"Non-Linux artifact in CUDA plan: {record['name']}")
        if any(dep.split()[0] == "__win" for dep in record.get("depends", [])):
            raise ValueError(f"Windows-only metapackage in CUDA plan: {record['name']}")
        final[record["name"]] = record
    return final


def check_development(records):
    for name, version in CUDA_DEVELOPMENT.items():
        if records.get(name, {}).get("version") != version:
            raise ValueError(f"Expected development package {name}={version}")
    forbidden = {"cuda-documentation", "cuda-toolkit", "cuda-libraries-dev", "cuda-tools", "cuda-visual-tools", "nsight-compute"} & records.keys()
    if forbidden:
        raise ValueError(f"Legacy/full CUDA toolkit packages remain: {sorted(forbidden)}")


def cuda_migration(args, output):
    """Solve a clean development set before removing the clone's old CUDA requests."""
    prefix = Path(args.prefix).resolve()
    records = conda_records(prefix)
    if args.command == "cuda-specs":
        output.mkdir(parents=True, exist_ok=False)
        metadata_dir = output / "conda-meta-before"
        metadata_dir.mkdir()
        for path in (prefix / "conda-meta").iterdir():
            if path.is_file() and (path.suffix == ".json" or path.name in ("history", "pinned")):
                shutil.copy2(path, metadata_dir / path.name)
        specs, remove = [], []
        for name, record in sorted(records.items()):
            if cuda_package(name):
                remove.append(name)
            else:
                version, build = package_identity(record)
                specs.append(f"{name}={version}={build}")
        specs += [f"{CUDA_CHANNEL}::{name}={version}" for name, version in CUDA_DEVELOPMENT.items()]
        # New nvcc packages depend on these wrappers; avoid selecting GCC 14/15.
        for name in ("gcc_linux-64", "gxx_linux-64"):
            if name not in records:
                specs.append(f"{name}=12")
        (output / "requested-specs.txt").write_text("\n".join(specs) + "\n")
        (output / "remove-names.txt").write_text("\n".join(remove) + ("\n" if remove else ""))
        (output / "before.json").write_text(json.dumps({"prefix": str(prefix), "records": records}, indent=2))
        print(f"[cuda] saved {len(records)} records; old CUDA set={len(remove)}; new roots={CUDA_DEVELOPMENT}", flush=True)
        return
    before = json.loads(Path(args.before).read_text())
    if before["prefix"] != str(prefix):
        raise ValueError("CUDA migration prefix differs from the saved inventory")
    if args.command == "cuda-remove-plan":
        final = solved_records(args.plan, prefix, before["records"])
        protected_packages(before["records"], final)
        if any(cuda_package(name) for name in final):
            raise ValueError("Removal plan did not remove the complete old CUDA set")
    elif args.command == "cuda-plan":
        # A dry-run create has no cloned history or retired package requests.
        plan_prefix = Path(args.before).parent / "solve-prefix"
        final = solved_records(args.plan, plan_prefix, {})
        protected_packages(before["records"], final)
        check_development(final)
        specs = [f"{name}={package_identity(record)[0]}={package_identity(record)[1]}"
                 for name, record in sorted(final.items())]
        output.with_suffix(".specs.txt").write_text("\n".join(specs) + "\n")
        for name in sorted(set(before["records"]) | set(final)):
            old, new = before["records"].get(name), final.get(name)
            if (package_identity(old) if old else None) != (package_identity(new) if new else None):
                print(f"[cuda plan] {name}: {package_identity(old) if old else 'absent'} -> {package_identity(new) if new else 'removed'}", flush=True)
    else:
        final = records
        protected_packages(before["records"], final)
        expected = json.loads(Path(args.plan).read_text())["records"]
        if {n: package_identity(r) for n, r in records.items()} != {n: package_identity(r) for n, r in expected.items()}:
            raise ValueError("Installed Conda records differ from the reviewed solve; stop before extension builds")
        if args.command == "cuda-removed":
            if any(cuda_package(name) for name in records):
                raise ValueError("Old CUDA removal is incomplete")
        else:
            check_development(records)
    if args.command == "cuda-check":
        compiler = subprocess.check_output([str(prefix / "bin/nvcc"), "--version"], text=True)
        if "release 12.6," not in compiler:
            raise ValueError(f"Unexpected CUDA compiler: {compiler}")
        include_roots = (prefix / "include", prefix / "targets/x86_64-linux/include")
        for header in ("cuda_runtime.h", "nvrtc.h", "cub/cub.cuh"):
            if not any((base / header).is_file() for base in include_roots):
                raise ValueError(f"Missing CUDA development header: {header}")
        if not any(list(base.glob("libcudart.so*")) for base in (prefix / "lib", prefix / "targets/x86_64-linux/lib")):
            raise ValueError("Missing CUDA runtime library in the isolated prefix")
        print(compiler, flush=True)
    write_json(output, {"prefix": str(prefix), "records": final})
    print(f"[{args.command}] verified; protected non-CUDA versions unchanged; report={output}", flush=True)


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".partial_{os.getpid()}_{time.time_ns()}")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def preflight(root):
    errors = []
    if sys.version_info[:2] != (3, 10):
        errors.append(f"Expected Python 3.10, found {sys.version}")
    for name in ("gcc-12", "g++-12", "ninja", "git"):
        if not shutil.which(name):
            errors.append(f"Missing command: {name}")
    for relative in ("resources/RMBench/envs/curobo/setup.py", "resources/PyTorch3D/setup.py"):
        if not (root / relative).is_file():
            errors.append(f"Missing saved source: {root / relative}")
    for name in ("setuptools", "setuptools-scm", "wheel", "packaging", "numpy", "sapien", "mplib", "nvidia-curobo"):
        try:
            metadata.version(name)
        except metadata.PackageNotFoundError:
            errors.append(f"Missing build/runtime distribution: {name}")
    import torch
    if not torch.cuda.is_available() or torch.cuda.get_device_capability(0) != (9, 0):
        errors.append("Expected a visible SM90 H100 GPU")
    if errors:
        raise ValueError("Preparation prerequisites:\n- " + "\n- ".join(errors))
    return {"passed": True, "python": sys.executable, "gpu": torch.cuda.get_device_name(0),
            "source_root": str(root), "gcc": subprocess.check_output(["gcc-12", "-dumpfullversion"], text=True).strip()}


def build_wheel(source, output, version):
    """Key compiled wheels by source and ABI; resume without reusing old .so files."""
    import torch
    from packaging.utils import canonicalize_name, parse_wheel_filename
    from packaging.version import Version
    marker = source.with_suffix(".source.json")
    identity = {"source_sha256": sha(marker), "python": sys.version,
                "torch": torch.__version__, "cuda": torch.version.cuda,
                "cxx11_abi": torch._C._GLIBCXX_USE_CXX11_ABI,
                "nvcc": subprocess.check_output([str(Path(sys.prefix) / "bin/nvcc"), "--version"], text=True),
                "gcc": subprocess.check_output(["gcc-12", "-dumpfullversion"], text=True).strip(),
                "architecture": os.environ.get("TORCH_CUDA_ARCH_LIST"), "version": version}
    if torch.__version__.split("+")[0] != "2.6.0" or torch.version.cuda != "12.6":
        raise ValueError("Refusing to build extensions for a different Torch/CUDA ABI")
    if identity["architecture"] != "9.0":
        raise ValueError("Extension builds must target SM90")
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]
    cache = output.parent / "wheels" / source.name / key
    receipt = cache / "COMPLETE.json"
    if receipt.exists():
        saved = json.loads(receipt.read_text())
        wheel = Path(saved["wheel"])
        if saved["identity"] != identity or not wheel.is_file() or sha(wheel) != saved["sha256"]:
            raise ValueError(f"Cached wheel identity/checksum differs: {receipt}")
        print(f"[wheel] reuse verified {wheel}", flush=True)
    else:
        attempt = cache / f"build_{time.time_ns()}"
        work = attempt / "source"
        # Each compile starts from saved sources, not a failed build directory.
        shutil.copytree(source, work, ignore=shutil.ignore_patterns("build", "dist", "*.egg-info", "*.so", "*.pyc", "__pycache__"))
        wheels = attempt / "wheels"
        wheels.mkdir()
        subprocess.run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--no-cache-dir",
                        "--wheel-dir", str(wheels), str(work)], check=True)
        candidates = list(wheels.glob("*.whl"))
        if len(candidates) != 1:
            raise ValueError(f"Expected one compiled wheel: {wheels}")
        wheel = candidates[0]
        name, built_version, _, _ = parse_wheel_filename(wheel.name)
        expected_name = "nvidia-curobo" if source.name == "curobo" else "pytorch3d"
        if canonicalize_name(name) != expected_name or built_version != Version(version):
            raise ValueError(f"Compiled wheel distribution/version differs from saved source: {wheel.name}")
        saved = {"identity": identity, "wheel": str(wheel), "sha256": sha(wheel)}
        write_json(receipt, saved)
    write_json(output, saved)


def source_files(source):
    exclude = {"build", "dist", ".git", "__pycache__", ".pytest_cache"}
    return {str(p.relative_to(source)): sha(p) for p in sorted(source.rglob("*")) if p.is_file()
            and not set(p.relative_to(source).parts) & exclude
            and not any(s.endswith(".egg-info") for s in p.relative_to(source).parts)
            and p.suffix not in (".so", ".pyc")}


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
    parser.add_argument("command", choices=("snapshot", "copy-source", "verify", "preflight", "build-wheel", "cuda-specs", "cuda-plan", "cuda-remove-plan", "cuda-removed", "cuda-check"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--source")
    parser.add_argument("--before")
    parser.add_argument("--prefix")
    parser.add_argument("--plan")
    parser.add_argument("--root")
    parser.add_argument("--version")
    args = parser.parse_args()
    output = Path(args.output)
    if args.command.startswith("cuda-"):
        cuda_migration(args, output)
        return
    if args.command == "preflight":
        write_json(output, preflight(Path(args.root).resolve()))
        print(f"[preflight] source/build prerequisites verified: {output}", flush=True)
        return
    if args.command == "build-wheel":
        build_wheel(Path(args.source).resolve(), output, args.version)
        return
    if args.command == "copy-source":
        source = Path(args.source).resolve()
        if not (source / "setup.py").is_file():
            raise ValueError(f"Missing saved extension source: {source}")
        exclude = {"build", "dist", ".git", "__pycache__", ".pytest_cache"}
        def ignore(directory, names):
            return [n for n in names if n in exclude or n.endswith((".so", ".pyc", ".egg-info"))]
        files = source_files(source)
        marker = output.with_suffix(".source.json")
        if output.exists():
            if not marker.exists() or json.loads(marker.read_text())["files"] != files:
                raise ValueError("Existing build source differs; preserve it and use a fresh build directory")
            if source_files(output) != files:
                raise ValueError(f"Saved build source files were modified: {output}")
        else:
            temporary = output.with_name(output.name + f".partial_{time.time_ns()}")
            shutil.copytree(source, temporary, ignore=ignore, symlinks=False)
            write_json(marker, {"source": str(source), "files": files})
            temporary.rename(output)
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
        for module in ("curobo.curobolib.lbfgs_step_cu", "curobo.curobolib.line_search_cu",
                       "curobo.curobolib.kinematics_fused_cu", "curobo.curobolib.tensor_step_cu",
                       "curobo.curobolib.geom_cu", "pytorch3d._C"):
            path = Path(importlib.import_module(module).__file__).resolve()
            if not path.is_relative_to(Path(sys.prefix).resolve()):
                raise ValueError(f"Extension still imports from old environment/source: {path}")
            value.setdefault("extensions", {})[module] = {"path": str(path), "sha256": sha(path)}
        import torch
        torch.ones(1, device="cuda").add_(1)
        torch.cuda.synchronize()
        value["preparation_recipe"] = "cuda126-development-v2"
    write_json(output, value)
    print(f"[{args.command}] {output}", flush=True)


if __name__ == "__main__":
    main()
