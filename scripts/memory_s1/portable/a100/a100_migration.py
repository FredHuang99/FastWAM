"""Explicit H100 export / A100 recovery. Never launch a diagnostic or change old evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from urllib.parse import urlsplit, parse_qs

REPO = "hhyfred/fastwam-memory-s1-backup"
RUN = "memory_s1_variable_t_h100_phase_seed17"
POINTER = "migration/a100_after_h100/LATEST.json"
SKIP = {".git", ".cache", "__pycache__", "build", "dist", ".pytest_cache", "node_modules", "packages"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def tool(root, name):
    path = root / "scripts/memory_s1" / name
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location("migration_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(argv, **kwargs):
    return subprocess.check_output([str(a) for a in argv], text=True, **kwargs)


def hub():
    os.environ.update(HF_HUB_OFFLINE="0", TRANSFORMERS_OFFLINE="0")
    from huggingface_hub import HfApi, hf_hub_download
    return HfApi(), hf_hub_download


def copy_tree(source, target, *, source_only=False):
    source, target = Path(source), Path(target)
    if not source.is_dir():
        raise FileNotFoundError(source)
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if path.is_symlink() or not path.is_file() or set(rel.parts) & SKIP:
            continue
        if any(p.endswith(".egg-info") for p in rel.parts) or path.suffix in (".so", ".pyc", ".o", ".a", ".pem", ".key"):
            continue
        if path.name.startswith(".env") or path.name in ("token", "stored_tokens", "credentials", ".netrc"):
            continue
        if source_only and path.suffix not in (".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".sh", ".cu", ".h", ".cuh", ".cpp", ".c", ".hpp", ".md", ".cfg", ".ini"):
            continue
        out = target / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out)


def export(args):
    root = args.root
    sim = Path("/opt/rmbench-fused-env/bin/python")
    # This is an export of actual installed state, not the pre-training ready environment.
    probe = run([sim, "-c", "import sys,torch; assert sys.version_info[:2]==(3,10); assert torch.__version__.split('+')[0]=='2.6.0'; assert torch.version.cuda=='12.6'; print(torch.__version__)"])
    print("[export] simulator", probe.strip(), flush=True)
    evidence = root / "outputs/s1_zero_success_followup_v2/HF_diagnosis.json"
    if not evidence.is_file() or read(evidence).get("readback_verified") is not True:
        raise ValueError("Finish this H100 diagnosis and its verified backup first; no diagnostic will be started here.")
    import fcntl
    diagnostic_lock = (evidence.parent / "diagnosis.lock").open("rb")
    fcntl.flock(diagnostic_lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
    for name in ("launch.json", "owner.json"):
        marker = evidence.parent / name
        owner = read(marker).get("owner") if marker.exists() else None
        current = process(owner["pid"]) if owner else None
        if current and current["state"] != "Z" and current["start_ticks"] == str(owner["start_ticks"]):
            raise ValueError("The H100 diagnosis is still active; wait for its exit receipt")
    final_report = evidence.parent / "DIAGNOSIS_STATUS.json"
    backup = evidence.parent / "backup.json"
    if (not final_report.is_file() or not backup.is_file() or read(backup).get("complete") is not True
            or read(backup).get("remote_readback") != read(evidence)
            or read(evidence).get("time", 0) < final_report.stat().st_mtime):
        raise ValueError("Generate the final H100 report and verified backup before migration; old/incomplete backup receipts are not accepted")
    output = root / "outputs/a100_migration_exports" / (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"_{time.time_ns()}")
    payload = output / "payload"
    payload.mkdir(parents=True)
    for name, python in (("training", "/opt/mwam/bin/python"), ("simulator", str(sim))):
        write(payload / f"{name}-pip.json", json.loads(run([python, "-m", "pip", "list", "--format=json"])))
    explicit = run(["/opt/miniforge/bin/conda", "list", "-p", "/opt/rmbench-fused-env", "--explicit"])
    for line in explicit.splitlines():
        if line.startswith(("https://", "http://")):
            url = urlsplit(line)
            if url.username or url.password or set(parse_qs(url.query)) & {"token", "access_token", "key", "auth"} or "/t/" in url.path:
                raise ValueError("Conda URL contains authentication; do not upload it")
    (payload / "simulator-conda-explicit.txt").write_text(explicit)
    native = {}
    for module in ("sapien", "mplib"):
        folder = Path(run([sim, "-c", f"import {module}; from pathlib import Path; print(Path({module}.__file__).parent)"]).strip().splitlines()[-1])
        for path in folder.rglob("*.py"):
            target = payload / "patches" / module / path.relative_to(folder)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        native[module] = {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob("*.so") if p.is_file()}
    write(payload / "simulator-native-hashes.json", native)
    build = root / "outputs/fused_environment_h100_v1"
    for name in ("curobo", "pytorch3d"):
        source = build / name
        if not (source / "setup.py").is_file():
            raise FileNotFoundError(f"Missing actual fused build source: {source}")
        copy_tree(source, payload / "build_sources" / name)
    copy_tree(root / "resources/RMBench", payload / "project/resources/RMBench", source_only=True)
    for name in ("src", "scripts/memory_s1", "configs", "requirements"):
        copy_tree(root / name, payload / "historical_code" / name, source_only=True)
    copy_tree(root / "resources/prepared_dense_h100_v1", payload / "project/resources/prepared_dense_h100_v1")
    for name in ("resources/download_lock.json", "outputs/memory_s1_variable_t_h100_phase_seed17/LATEST_READY_REMOTE.json"):
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(path)
        target = payload / "project" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    shutil.copy2(evidence, payload / "HF_diagnosis.json")
    api, download = hub()
    repository_revision = api.repo_info(args.repo).sha
    write(payload / "CHECKPOINT_REMOTE.json", read(download(args.repo, f"runs/{RUN}/LATEST_COMPLETE.json", revision=repository_revision)))
    # Save actual frozen banks without importing any completed evaluation into a new queue.
    banks = list((root / "outputs/posttrain_h100_phase_seed17_top2_v2").glob("frozen_scenes.json"))
    if len(banks) != 1 or len(read(banks[0]).get("scenes", [])) != 20:
        raise ValueError("Expected the existing 20-scene bank; no seed search is allowed")
    shutil.copy2(banks[0], payload / "frozen_scenes.json")
    write(payload / "ORIGIN.json", {"commit": run(["git", "-C", root, "rev-parse", "HEAD"]).strip(),
          "run": RUN, "diagnosis": read(evidence), "export_tool_sha256": sha(__file__), "phase": "post_diagnosis_migration_inputs",
          "does_not_include": ["models", "raw_hdf5", "asset_meshes", "dense_cache", "CUDA_binaries", "tokens"],
          "note": "Historical code is evidence only. It must not overwrite the new A100 entry points."})
    files = {p.relative_to(payload).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
             for p in sorted(payload.rglob("*")) if p.is_file()}
    write(payload / "FILES.json", files)
    archive = output / "migration.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for path in sorted(payload.rglob("*")):
            if path.is_file():
                tar.add(path, arcname=path.relative_to(payload).as_posix(), recursive=False)
    api, download = hub()
    utilities = tool(root, "hf_tools.py")
    budget = utilities.check_budget(api, archive.stat().st_size + 1024**2, 100_000_000_000 / 2**30, 10)
    if api.repo_info(args.repo).private is not True:
        raise ValueError("Migration backup must remain private")
    remote = f"migration/a100_after_h100/{output.name}/migration.tar.gz"
    commit = api.upload_file(repo_id=args.repo, path_or_fileobj=str(archive), path_in_repo=remote,
                             commit_message="Save actual post-diagnosis environment for A100 reconstruction")
    if sha(download(args.repo, remote, revision=commit.oid)) != sha(archive):
        raise ValueError("Migration archive remote readback mismatch; pointer not published")
    pointer = {"repo": args.repo, "revision": commit.oid, "package": remote, "sha256": sha(archive),
               "bytes": archive.stat().st_size, "readback_verified": True, "budget": budget}
    write(output / "LATEST.json", pointer)
    publication = api.upload_file(repo_id=args.repo, path_or_fileobj=str(output / "LATEST.json"), path_in_repo=POINTER)
    if read(download(args.repo, POINTER, revision=publication.oid)) != pointer:
        raise ValueError("Migration pointer readback mismatch")
    write(output / "UPLOAD_COMPLETE.json", {**pointer, "pointer_revision": publication.oid})
    print(json.dumps(pointer, indent=2), flush=True)


def fetch(args):
    api, download = hub()
    output = args.root / "outputs/recovery_aws_a100_v1"
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / "MIGRATION_REMOTE.json"
    if receipt.exists():
        pointer = read(receipt)  # A restart never silently selects a newer migration.
    else:
        revision = api.repo_info(args.repo).sha
        pointer = read(download(args.repo, POINTER, revision=revision))
        pointer["pointer_revision"] = revision
    if pointer["repo"] != args.repo or not pointer["readback_verified"]:
        raise ValueError("Unverified/mismatched migration pointer")
    archive = Path(download(args.repo, pointer["package"], revision=pointer["revision"]))
    if sha(archive) != pointer["sha256"] or archive.stat().st_size != pointer["bytes"]:
        raise ValueError("Migration archive checksum mismatch")
    recovery = tool(args.root, "portable/recovery.py")
    target = output / "migration"
    recovery.extract_archive(archive, target)
    for name, row in read(target / "FILES.json").items():
        path = (target / name).resolve()
        if not path.is_relative_to(target.resolve()) or sha(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
            raise ValueError(f"Migration member mismatch: {name}")
    write(receipt, pointer)
    print("[migration] verified", target, flush=True)


def restore(args):
    root = args.root
    package = root / "outputs/recovery_aws_a100_v1/migration"
    files = read(package / "FILES.json")
    # Never restore live leases, checkpoints or historical code over current code.
    for name, row in files.items():
        if not name.startswith("project/"):
            continue
        source = package / name
        if sha(source) != row["sha256"]:
            raise ValueError(f"Altered migration source: {name}")
        target = (root / name.removeprefix("project/")).resolve()
        if not target.is_relative_to(root):
            raise ValueError(name)
        if target.exists() and sha(target) != row["sha256"]:
            if args.overlay_sources and name.startswith("project/resources/RMBench/"):
                before = root / "outputs/recovery_aws_a100_v1/before_source_restore" / sha(target) / target.name
                before.parent.mkdir(parents=True, exist_ok=True)
                if not before.exists():
                    shutil.copy2(target, before)
                shutil.copy2(source, target)
                continue
            raise ValueError(f"Existing file differs; preserve it before restoring: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
    ready = root / "outputs/recovery_aws_a100_v1/restored"
    snapshots = list(ready.rglob("snapshot.json"))
    if len(snapshots) != 1:
        raise ValueError("Expected one verified ready snapshot before project restoration")
    snapshot = snapshots[0]
    for name, row in read(snapshot)["files"].items():
        # Recover original review references and historical reports at their original paths.
        if not name.startswith("outputs/") or Path(name).name.startswith(("STOP", "launcher")):
            continue
        source = (snapshot.parent / name).resolve()
        target = (root / name).resolve()
        if not target.is_relative_to(root / "outputs") or not source.is_relative_to(snapshot.parent.resolve()):
            raise ValueError(name)
        if sha(source) != row["sha256"]:
            raise ValueError(f"Historical evidence hash differs: {name}")
        if target.exists() and sha(target) != row["sha256"]:
            raise ValueError(f"Existing historical evidence differs: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
    print("[restored] actual prepared data/source/locks; historical admission is not new A100 approval")


def payloads(args):
    root = args.root
    output = root / "outputs/recovery_aws_a100_v1"
    package = output / "migration"
    api, download = hub()
    recovery = tool(root, "portable/recovery.py")
    pointers = (("ready", read(package / f"project/outputs/{RUN}/LATEST_READY_REMOTE.json"), output / "restored"),
                ("diagnosis", read(package / "HF_diagnosis.json"), output / "historical_diagnosis"))
    for label, pointer, target in pointers:
        if pointer.get("repo", args.repo) != args.repo:
            raise ValueError(f"Unexpected {label} repository")
        archive = Path(download(args.repo, pointer["package"], revision=pointer["revision"]))
        if sha(archive) != pointer["sha256"]:
            raise ValueError(f"{label} archive checksum mismatch")
        recovery.extract_archive(archive, target)
        print(f"[{label}] exact archived revision restored: {target}", flush=True)
    pointer = read(package / "CHECKPOINT_REMOTE.json")
    prefix = f"runs/{RUN}"
    manifest_path = f"{prefix}/checkpoints/{pointer['directory']}/backup_manifest.json"
    manifest = Path(download(args.repo, manifest_path, revision=pointer["checkpoint_revision"]))
    if sha(manifest) != pointer["backup_manifest_sha256"]:
        raise ValueError("Checkpoint manifest checksum mismatch")
    from concurrent.futures import ThreadPoolExecutor
    destination = root / "outputs" / RUN
    files = read(manifest)["files"]
    def one(item):
        name, expected = item
        target = (destination / name).resolve()
        if not target.is_relative_to(destination.resolve()):
            raise ValueError(f"Unsafe checkpoint member: {name}")
        if target.exists():
            if sha(target) != expected:
                raise ValueError(f"Existing checkpoint material differs: {target}")
            return
        source = Path(download(args.repo, f"{prefix}/{name}", revision=pointer["checkpoint_revision"]))
        if sha(source) != expected:
            raise ValueError(f"Checkpoint member mismatch: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + ".downloading")
        shutil.copy2(source, temporary)
        temporary.replace(target)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(one, files.items()))
    if sha(destination / "checkpoints" / pointer["directory"] / "resume.pt") != pointer["resume_sha256"]:
        raise ValueError("Full recovery point checksum mismatch")
    shutil.copy2(manifest, output / "checkpoint_manifest.json")
    write(output / "PAYLOADS_COMPLETE.json", {"checkpoint": pointer, "files": files,
          "historical_evidence_only": True, "gpu_admission_inherited": False})
    print(f"[checkpoint] verified update={pointer['step']}; training was not started")


def pins(args):
    base = args.root / "outputs/recovery_aws_a100_v1/migration"
    rows = read(base / f"{args.kind}-pip.json")
    skip = {"torch", "torchvision", "torchaudio", "pytorch3d", "nvidia-curobo", "curobo", "fastwam", "pip"}
    versions = {r["name"].lower().replace("_", "-"): r["version"] for r in rows}
    if args.kind == "training":
        # NVIDIA owns the base environment. Restore application packages through the existing recorded-pins logic.
        tool(args.root, "portable/recovery.py").pins(argparse.Namespace(ready=str(base), kind="training", output=str(args.output)))
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(f"{name}=={version}\n" for name, version in sorted(versions.items()) if name not in skip))
    write(args.output.with_suffix(".sources.json"), {name: versions[name] for name in ("nvidia-curobo", "pytorch3d")})


def patches(args):
    import importlib
    source = args.root / "outputs/recovery_aws_a100_v1/migration/patches"
    for name in ("sapien", "mplib"):
        target = Path(importlib.import_module(name).__file__).parent
        paths = list((source / name).rglob("*.py"))
        if not paths:
            raise FileNotFoundError(f"No actual {name} patches")
        for path in paths:
            out = target / path.relative_to(source / name)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, out)
    print("[patches] actual H100 Python patches restored; native wheels remain the new installation")


def device(args):
    import importlib
    import numpy as np
    import torch
    import sapien
    import pynvml
    from pytorch3d.ops import knn_points
    sys.path.insert(0, str(args.root / "src/fastwam/memory_s1"))
    from eval_state import cuda_gpu_uuid
    assert torch.cuda.device_count() == 1
    assert torch.cuda.get_device_capability(0) == (8, 0)
    assert "A100" in torch.cuda.get_device_name(0)
    assert torch.cuda.get_device_properties(0).total_memory >= 75 * 1024**3
    expected = os.environ["CUDA_VISIBLE_DEVICES"]
    assert cuda_gpu_uuid(0) == expected
    points = torch.arange(96, device="cuda", dtype=torch.float32).reshape(1, 32, 3)
    assert torch.isfinite(knn_points(points, points, K=1).dists).all()
    x = torch.ones(32, 32, device="cuda")
    stream = torch.cuda.Stream()
    stream.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(stream):
        for _ in range(3):
            y = x @ x
    torch.cuda.current_stream().wait_stream(stream)
    graph = torch.cuda.CUDAGraph()
    with torch.cuda.graph(graph):
        y = x @ x
    x.fill_(2)
    graph.replay()
    torch.cuda.synchronize()
    assert torch.equal(y, torch.full_like(y, 128))
    renderer = sapien.render.RenderSystem(device="cuda:0")
    pci = getattr(renderer.device, "pci_string", None)
    if not pci:
        raise ValueError("Cannot prove Vulkan physical GPU mapping; inspect renderer device before parallel evaluation")
    pynvml.nvmlInit()
    try:
        actual = pynvml.nvmlDeviceGetUUID(pynvml.nvmlDeviceGetHandleByPciBusId(str(pci).encode()))
        if isinstance(actual, bytes):
            actual = actual.decode()
        assert actual == expected, (actual, expected)
    finally:
        pynvml.nvmlShutdown()
    scene = sapien.Scene([sapien.physx.PhysxCpuSystem(), renderer])
    camera = scene.add_camera("migration", 64, 64, 1., .1, 10.)
    scene.step()
    scene.update_render()
    camera.take_picture()
    pixels = camera.get_picture("Color")
    assert pixels.shape == (64, 64, 4) and np.isfinite(pixels).all()
    extensions = {}
    for name in ("pytorch3d._C", "curobo.curobolib.lbfgs_step_cu", "curobo.curobolib.kinematics_fused_cu"):
        path = Path(importlib.import_module(name).__file__).resolve()
        assert path.is_relative_to(Path(sys.prefix).resolve()), path
        extensions[name] = {"path": str(path), "sha256": sha(path)}
    write(args.output, {"passed": True, "gpu_uuid": expected, "renderer_uuid": actual,
                       "torch": torch.__version__, "extensions": extensions,
                       "scope": "CUDA_graph_fresh_input_PyTorch3D_kernel_and_offscreen_render_not_task_admission"})


def devices(args):
    import signal
    rows = [r.split(", ") for r in run(["nvidia-smi", "--query-gpu=uuid,name,memory.total", "--format=csv,noheader,nounits"]).strip().splitlines()]
    if len(rows) != 8 or any("A100" not in row[1] or int(row[2]) < 75000 for row in rows):
        raise ValueError(f"Expected eight A100 80GB GPUs: {rows}")
    output = args.root / "outputs/recovery_aws_a100_v1/device_checks" / str(time.time_ns())
    output.mkdir(parents=True)
    children, streams = [], []
    try:
        for index, (uuid, _, _) in enumerate(rows):
            log = (output / f"gpu_{index}.log").open("w")
            streams.append(log)
            env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "CUDA_LAUNCH_BLOCKING", "VIRTUAL_ENV")}
            prefix = "/opt/rmbench-a100-env"
            env.update(CUDA_VISIBLE_DEVICES=uuid, CUDA_DEVICE_ORDER="PCI_BUS_ID", OMP_NUM_THREADS="2",
                       CUDA_HOME=prefix, TORCH_CUDA_ARCH_LIST="8.0",
                       LD_LIBRARY_PATH=f"{prefix}/lib:{prefix}/targets/x86_64-linux/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64")
            command = [f"{prefix}/bin/python", "-u", str(Path(__file__).resolve()), "device", "--root", str(args.root), "--output", str(output / f"gpu_{index}.json")]
            children.append(subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True))
        deadline = time.monotonic() + 600
        while any(p.poll() is None for p in children):
            failed = [i for i, p in enumerate(children) if p.poll() not in (None, 0)]
            if failed or time.monotonic() > deadline:
                raise RuntimeError(f"A100 device check failed/timed out; failed GPUs={failed}; logs={output}")
            time.sleep(1)
        if any(p.returncode != 0 for p in children):
            raise RuntimeError(f"Device check failed: inspect {output}")
        results = [read(output / f"gpu_{i}.json") for i in range(8)]
        write(args.root / "outputs/recovery_aws_a100_v1/DEVICES_COMPLETE.json", {"passed": True, "devices": results, "directory": str(output)})
        print("[devices] 8/8 CUDA/renderer/extension checks passed. Task/planner qualification is still separate.")
    finally:
        for child in children:
            if child.poll() is None:
                try:
                    os.killpg(child.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
        for child in children:
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        for stream in streams:
            stream.close()


def nccl(args):
    from datetime import timedelta
    import torch
    import torch.distributed as dist
    rank = int(os.environ["LOCAL_RANK"])
    assert int(os.environ["WORLD_SIZE"]) == 8
    torch.cuda.set_device(rank)
    assert torch.cuda.get_device_capability(rank) == (8, 0)
    dist.init_process_group("nccl", timeout=timedelta(seconds=180))
    try:
        value = torch.tensor(float(rank + 1), device=f"cuda:{rank}")
        dist.all_reduce(value)
        assert value.item() == 36., value
        dist.barrier()
        if rank == 0:
            write(args.root / "outputs/recovery_aws_a100_v1/NCCL_COMPLETE.json", {"passed": True, "world_size": 8, "sum": value.item(), "scope": "collective_only_no_optimizer_updates"})
    finally:
        dist.destroy_process_group()


def process(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return {"pid": pid, "start_ticks": fields[19], "state": fields[0]}
    except (OSError, IndexError):
        return None


def register(args):
    write(args.root / "outputs/recovery_aws_a100_v1/LAUNCH.json", {"owner": process(args.pid), "log": str(args.log)})


def status(args):
    marker = args.root / "outputs/recovery_aws_a100_v1/LAUNCH.json"
    if not marker.exists():
        print("A100 setup has not started")
        return
    value = read(marker)
    owner = value["owner"]
    current = process(owner["pid"]) if owner else None
    value["running"] = bool(current and current["state"] != "Z" and current["start_ticks"] == owner["start_ticks"])
    receipt = Path(value["log"]).with_suffix(".exit")
    value["exit"] = receipt.read_text().strip() if receipt.exists() else None
    print(json.dumps(value, indent=2))


def stop(args):
    marker = args.root / "outputs/recovery_aws_a100_v1/LAUNCH.json"
    value = read(marker)
    owner = value["owner"]
    current = process(owner["pid"]) if owner else None
    if not current or current["state"] == "Z" or current["start_ticks"] != owner["start_ticks"]:
        print("No matching live A100 setup process")
        return
    if os.getpgid(owner["pid"]) != owner["pid"]:
        raise RuntimeError("Refusing to stop an unrelated process group")
    os.killpg(owner["pid"], signal.SIGTERM)
    print("Stop requested for the recorded A100 setup only; retain partial files and inspect its exit receipt")


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("export", "fetch", "payloads", "restore", "pins", "patches", "device", "devices", "nccl", "register", "status", "stop"))
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"))
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--kind", choices=("training", "simulator"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pid", type=int)
    parser.add_argument("--log", type=Path)
    parser.add_argument("--overlay-sources", action="store_true", help="Restore recorded simulator patches after asset download; preserve conflicting downloaded files")
    args = parser.parse_args()
    args.root = args.root.resolve()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    globals()[args.command](args)


if __name__ == "__main__":
    main()
