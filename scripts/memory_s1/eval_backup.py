"""Package environment, fixed resources, or stopped evaluation state without secrets."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

# Import the standalone state module, then restore the search path.
_state_directory = str(Path(__file__).resolve().parents[2] / "src/fastwam/memory_s1")
sys.path.insert(0, _state_directory)
try:
    from eval_state import digest, durable_json, is_alive, read
finally:
    sys.path.remove(_state_directory)


def capture(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=90)
    return {"command": command, "exit": result.returncode, "output": result.stdout}


def assert_stopped(root):
    outputs = Path(root) / "outputs"
    for path in outputs.rglob("launcher.json"):
        value = read(path)
        if is_alive(value.get("owner")):
            raise RuntimeError(f"Evaluation launcher still active: {path}")
    for path in outputs.rglob("queue.json"):
        for job in read(path)["jobs"]:
            if job["state"] == "running" and is_alive(job.get("owner")):
                raise RuntimeError(f"Evaluation episode still active: {job['id']}")
    for path in outputs.rglob("*.owner.json"):
        if is_alive(read(path)):
            raise RuntimeError(f"Scene planner still active: {path}")
    for path in outputs.rglob("simulator_owner.json"):
        if is_alive(read(path)):
            raise RuntimeError(f"Simulator still active: {path}")
    # Match processes by their actual working tree and entry point, not stale PID files.
    expected = Path(root).resolve()
    for directory in Path("/proc").iterdir():
        if not directory.name.isdigit() or int(directory.name) == os.getpid():
            continue
        try:
            command = (directory / "cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
            if any(name in command for name in ("fastwam.memory_s1.train", "fastwam.memory_s1.sim_bridge", "fastwam.memory_s1.eval_parallel run", "fastwam.memory_s1.eval_parallel worker")) and (directory / "cwd").resolve() == expected:
                raise RuntimeError(f"Training/evaluation still active: PID={directory.name}")
        except FileNotFoundError:
            pass


def environment_inventory(root, output):
    value = {"format": 1, "created": time.time(), "root": str(root), "commands": [], "environments": [],
             "restore_requirement": "Same NVIDIA image digest, original absolute paths, NVIDIA Container Toolkit and compatible host driver."}
    for command in (["nvidia-smi"], ["uname", "-a"], ["git", "-C", str(root), "rev-parse", "HEAD"],
                    ["git", "-C", str(root), "diff", "--binary"], ["ldconfig", "-p"]):
        value["commands"].append(capture(command))
    paths = []
    for prefix in (Path("/opt/mwam"), Path("/opt/rmbench-env"), Path("/opt/hf-tools")):
        python = prefix / "bin/python"
        if not python.exists():
            raise FileNotFoundError(f"Environment missing: {python}")
        value["environments"].append({"prefix": str(prefix), "python_target": str(python.resolve()),
                                      "pip": capture([str(python), "-m", "pip", "list", "--format=freeze"])})
        paths.append(prefix)
        # Include external paths used by editable package metadata.
        script = "import importlib.util,json; names=('curobo','pytorch3d','fastwam'); print(json.dumps({n:(s.origin if (s:=importlib.util.find_spec(n)) else None) for n in names}))"
        origins = capture([str(python), "-c", script])
        value["environments"][-1]["editable_origins"] = origins
        for metadata in prefix.glob("lib/python*/site-packages/*.pth"):
            for line in metadata.read_text(errors="replace").splitlines():
                if line.startswith("/") and Path(line).is_dir() and Path(line).resolve() != root:
                    paths.append(Path(line))
        if origins["exit"] == 0:
            for name, origin in json.loads(origins["output"].splitlines()[-1]).items():
                if origin and name != "fastwam" and not Path(origin).is_relative_to(prefix):
                    parents = Path(origin).parents
                    checkout = next((parent for parent in parents if (parent / ".git").exists() or (parent / "pyproject.toml").exists() or (parent / "setup.py").exists()), Path(origin).parent)
                    paths.append(checkout)
    for path in (Path("/root/.cache/torch_extensions"), Path("/root/.cache/warp"), Path("/root/.nv"),
                 Path("/etc/vulkan"), Path("/usr/share/vulkan/icd.d")):
        if path.exists():
            paths.append(path)
    # Collapse nested trees, preserving symlinked environment prefixes themselves.
    selected = []
    for path in sorted(set(paths), key=lambda p: len(p.parts)):
        if not any(path.is_relative_to(parent) for parent in selected):
            if path == Path("/") or len(path.parts) < 3:
                raise ValueError(f"Refusing an overly broad archive root: {path}")
            selected.append(path)
    value["archive_paths"] = [str(path) for path in selected]
    value["runtime_environment"] = {name: os.environ.get(name) for name in ("VK_ICD_FILENAMES", "NVIDIA_DRIVER_CAPABILITIES", "LD_LIBRARY_PATH", "CUDA_HOME", "CUDA_DEVICE_ORDER")}
    durable_json(output, value)
    return selected


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--kind", choices=("environment", "resources", "evaluation"), required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--directory", required=True)
    parser.add_argument("--split-gib", type=int, default=0)
    args = parser.parse_args()
    root, destination = Path(args.root).resolve(), Path(args.directory).resolve()
    if destination.is_relative_to(root):
        raise ValueError("Package directory must be outside the FastWAM checkout.")
    destination.mkdir(parents=True, exist_ok=False)
    assert_stopped(root)
    if args.kind == "environment":
        selected = environment_inventory(root, destination / "environment.json")
    elif args.kind == "resources":
        selected = [root / "resources"]
        if (root / "resources").resolve() != root / "resources":
            selected.append((root / "resources").resolve())
    else:
        selected = [root]
        outputs = root / "outputs"
        if outputs.resolve() != outputs and not outputs.resolve().is_relative_to(root):
            selected.append(outputs.resolve())
        provenance = outputs / "memory_s1_seed17/provenance"
        provenance.mkdir(parents=True, exist_ok=True)
        bundle = provenance / "eval_source.bundle"
        temporary_bundle = provenance / "eval_source.bundle.tmp"
        subprocess.run(["git", "-C", str(root), "bundle", "create", str(temporary_bundle), "HEAD", "refs/heads/memory"], check=True)
        temporary_bundle.replace(bundle)
    archive = destination / f"mwam_{args.kind}.tar.zst"
    command = ["tar", "--use-compress-program=zstd -T4 -3", "-cf", str(archive), "-C", "/",
               "--exclude=.git", "--exclude=__pycache__", "--exclude=*.sock", "--exclude=*.tmp", "--exclude=*.pid",
               "--exclude=.ssh", "--exclude=.aws", "--exclude=.netrc", "--exclude=.git-credentials", "--exclude=.cache/huggingface", "--exclude=token", "--exclude=stored_tokens"]
    if args.kind == "evaluation":
        command += [f"--exclude={str(root / 'resources').lstrip('/')}"]
    if args.kind == "resources":
        command += ["--exclude=download_cache", "--exclude=eval_result", "--exclude=.cache", "--exclude=*.zip"]
    command += [str(path).lstrip("/") for path in selected]
    print(f"[pack] kind={args.kind} paths={selected}; compression may take time", flush=True)
    subprocess.run(command, check=True)
    metadata = {"kind": args.kind, "root": str(root), "original_paths": [str(p) for p in selected],
                "archive_sha256": digest(archive), "archive_bytes": archive.stat().st_size,
                "note": "Evaluation snapshots exclude resources; restore the fixed resource package separately."}
    if args.split_gib:
        subprocess.run(["split", "-b", f"{args.split_gib}G", "-d", "-a", "3", str(archive), str(archive) + ".part-"], check=True)
        archive.unlink()
    durable_json(destination / "package.json", metadata)
    files = sorted(path for path in destination.iterdir() if path.is_file() and path.name != "SHA256.sha256")
    with (destination / "SHA256.sha256").open("w") as stream:
        for path in files:
            stream.write(f"{digest(path)}  {path.name}\n")
    print(f"[packed] bytes={sum(p.stat().st_size for p in files)} directory={destination}", flush=True)


if __name__ == "__main__":
    main()
