"""Recover verified ready snapshots without importing training dependencies."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import time

from common import digest, eligible, inventory, read, safe_relative, verify_files, write, add_verified


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def config(path):
    import yaml
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    root = Path(os.environ.get("FW_ROOT", value.get("root", "."))).resolve()
    value["root"] = str(root)
    value["paths"] = {key: str((root / p).resolve()) for key, p in value["paths"].items()}
    return value


def pins(args):
    """Use recorded package versions without importing the old CUDA stack into training."""
    kind = args.kind
    indicators = ("training", "mwam") if kind == "training" else ("simulator", "rmbench")
    candidates = []
    for path in Path(args.ready).rglob("*"):
        if not path.is_file() or "pip" not in path.name.lower() or not any(word in path.relative_to(args.ready).as_posix().lower() for word in indicators):
            continue
        packages = {}
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, list):
                packages = {p["name"].lower().replace("_", "-"): p["version"] for p in value
                            if isinstance(p, dict) and "name" in p and "version" in p}
        except (ValueError, UnicodeDecodeError):
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                match = re.fullmatch(r"([A-Za-z0-9_.-]+)(?:==|\s+)([0-9][A-Za-z0-9.+_-]*)", line.strip())
                if match:
                    packages[match[1].lower().replace("_", "-")] = match[2]
        if packages:
            candidates.append((path, packages))
    if not candidates:
        raise FileNotFoundError(f"No saved {kind} pip list was found; inspect the ready package before installing.")
    _, packages = max(candidates, key=lambda item: len(item[1]))
    # The application dependencies are restored; the NVIDIA image owns the new training stack.
    application = {"einops", "omegaconf", "hydra-core", "safetensors", "transformers", "huggingface-hub",
                   "sentencepiece", "ftfy", "regex", "pillow", "h5py", "pyyaml", "opencv-python-headless",
                   "matplotlib", "gitpython", "rich", "imageio", "imageio-ffmpeg", "nvidia-ml-py"}
    # CuRobo imports as `curobo`, but its distribution is named `nvidia_curobo`.
    # Both names must be excluded: the simulator installer builds saved source
    # for the current GPU instead of resolving its version from a package index.
    source_installed = {"pytorch3d", "curobo", "nvidia-curobo", "fastwam"}
    ignored = {"torch", "torchvision", "torchaudio", "pip", "setuptools", "wheel"} | source_installed
    values = {name: version for name, version in packages.items() if name not in ignored
              and (kind != "training" or name in application)
              and re.fullmatch(r"[A-Za-z0-9.+_-]+", version)}
    if kind == "training":
        requirements = Path(__file__).resolve().parents[3] / "requirements/memory_s1.txt"
        for line in requirements.read_text(encoding="utf-8").splitlines():
            match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9.+_-]+)", line.strip())
            if match:
                name = match[1].lower().replace("_", "-")
                values.setdefault(name, match[2])
    if not values:
        raise ValueError("Saved dependency list contains no installable application packages.")
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(f"{name}=={version}\n" for name, version in sorted(values.items())), encoding="utf-8")
    write(target.with_suffix(".sources.json"), {"kind": kind, "records": [{"file": str(p), "sha256": digest(p)} for p, _ in candidates],
          "intentionally_rebuilt": sorted(ignored),
          "source_installed": {name: packages[name] for name in sorted(source_installed) if name in packages},
          "selected": values})
    for name in sorted(source_installed & packages.keys()):
        print(f"[pins] {name}=={packages[name]} excluded from index install; restored from source", flush=True)
    print(f"[pins] {kind}: {len(values)} recorded packages -> {target}", flush=True)


def conda_spec(args):
    candidates = []
    for path in Path(args.ready).rglob("*.txt"):
        if "conda" not in path.name.lower():
            continue
        text = path.read_text(encoding="utf-8")
        if "@EXPLICIT" in text:
            candidates.append((path, text))
    if not candidates:
        print("[conda] No saved explicit list; rebuild the fixed Python 3.10/CUDA 12.4.1 environment.")
        return
    if len({text for _, text in candidates}) != 1:
        raise ValueError("Conflicting saved Conda explicit lists; inspect them before creating the environment.")
    text = candidates[0][1]
    for line in text.splitlines():
        if line.startswith("http") and (not line.startswith(("https://conda.anaconda.org/", "https://repo.anaconda.com/"))
                                         or "@" in line.split("//", 1)[1].split("/", 1)[0]):
            raise ValueError("Saved Conda specification uses an unapproved or credential-bearing channel.")
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"[conda] Saved explicit reconstruction list -> {target}")


def unique_file(directory, name, required=True):
    candidates = sorted(p for p in Path(directory).rglob(name) if ".cache" not in p.parts)
    if not candidates:
        if required:
            raise FileNotFoundError(f"Snapshot has no {name}; do not invent missing provenance.")
        return None
    if len({digest(p) for p in candidates}) != 1:
        raise ValueError(f"Conflicting snapshot copies of {name}: {candidates}")
    return candidates[0]


def admission(directory):
    path = unique_file(directory, "integration_admission.json")
    value = read(path)
    if value.get("passed") is not True or set(value.get("reports", {})) != {
            "model", "execution", "data", "pilot", "cache", "training"}:
        raise ValueError("The recovered admission does not contain all six passed checks.")
    reports = {}
    for name, item in value["reports"].items():
        matches = [p for p in Path(directory).rglob(item["file"]) if digest(p) == item["sha256"]]
        if not matches:
            raise ValueError(f"Missing admission-bound report: {name}")
        report = read(matches[0])
        if report.get("passed") is not True or report.get("binding") != value["binding"]:
            raise ValueError(f"Inconsistent prior evidence: {name}")
        reports[name] = report
    return path, value, reports


def extract_archive(path, destination):
    """Reject traversal, special files and links before copying regular payloads."""
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    process = None
    if str(path).endswith(".zst"):
        process = subprocess.Popen(["zstd", "-dc", str(path)], stdout=subprocess.PIPE)
        archive = tarfile.open(fileobj=process.stdout, mode="r|")
    else:
        archive = tarfile.open(path, "r:*")
    try:
        with archive:
            seen = set()
            for member in archive:
                raw = member.name
                while raw.startswith("./"):
                    raw = raw[2:]
                if raw in ("", ".") and member.isdir():
                    continue
                name = str(safe_relative(raw))
                if member.isdir():
                    continue
                if member.issym():
                    # Source trees can contain policy links; restore only contained links.
                    if PurePosixPath(member.linkname).is_absolute() or "\\" in member.linkname:
                        print(f"[source-link-skipped] {name} -> {member.linkname}", flush=True)
                        continue
                    target = destination / name
                    linked = (target.parent / member.linkname).resolve()
                    if not linked.is_relative_to(destination):
                        print(f"[source-link-skipped] {name} -> {member.linkname}", flush=True)
                        continue
                    # Copy source links only if the later source overlay needs them.
                    continue
                if not member.isfile() or name in seen:
                    raise ValueError(f"Unexpected/duplicate archive member: {name}")
                seen.add(name)
                target = destination / name
                if not target.resolve().is_relative_to(destination):
                    raise ValueError(f"Archive path escaped its destination: {name}")
                if target.exists():
                    with archive.extractfile(member) as stream:
                        data = stream.read()
                    if target.read_bytes() != data:
                        raise ValueError(f"Existing recovery file differs: {target}; preserve it first.")
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary = target.with_name(target.name + ".restoring")
                with archive.extractfile(member) as source, temporary.open("wb") as output:
                    shutil.copyfileobj(source, output, 8 * 1024**2)
                os.chmod(temporary, member.mode & 0o777)
                temporary.replace(target)
    finally:
        if process:
            process.stdout.close()
            if process.wait() != 0:
                raise ValueError("Zstandard decompression failed; no snapshot is accepted.")


def hub():
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    from huggingface_hub import HfApi, hf_hub_download
    return HfApi(), hf_hub_download


def remote_inventory(args):
    api, _ = hub()
    info = api.repo_info(args.repo, repo_type="model")
    rows = [{"path": item.path, "bytes": item.size} for item in
            api.list_repo_tree(args.repo, repo_type="model", revision=info.sha, recursive=True)
            if hasattr(item, "size")]
    value = {"repo": args.repo, "revision": info.sha, "private": info.private, "files": rows,
             "ready_pointers": [r["path"] for r in rows if r["path"].endswith("LATEST_READY.json")],
             "training_pointers": [r["path"] for r in rows if r["path"].endswith("LATEST_COMPLETE.json")],
             "resource_candidates": [r for r in rows if not r["path"].startswith("ready/")
                 and "checkpoints/" not in r["path"] and
                 (r["bytes"] > 32 * 1024**2 or any(word in r["path"] for word in ("assets/", "cache_s1", ".part-")))]}
    write(Path(args.output) / "REMOTE_INVENTORY.json", value)
    print(json.dumps({key: value[key] for key in ("repo", "revision", "private", "ready_pointers", "training_pointers", "resource_candidates")}, indent=2))
    print(f"[inventory] files={len(rows)}; full tree saved to {args.output}/REMOTE_INVENTORY.json", flush=True)
    return value


def download_payload(args):
    """Download an explicitly selected native payload at an immutable revision."""
    api, download = hub()
    if not re.fullmatch(r"[0-9a-f]{40}", args.revision):
        raise ValueError("Select the immutable revision from REMOTE_INVENTORY.json.")
    prefix = str(safe_relative(args.prefix)).rstrip("/") + "/"
    destination = Path(args.destination).resolve()
    files = {}
    for item in api.list_repo_tree(args.repo, repo_type="model", revision=args.revision, recursive=True):
        if not hasattr(item, "size") or not item.path.startswith(prefix):
            continue
        relative = str(safe_relative(item.path[len(prefix):]))
        path = Path(download(args.repo, item.path, revision=args.revision, repo_type="model"))
        lfs = getattr(item, "lfs", None)
        expected = getattr(lfs, "sha256", None) if not isinstance(lfs, dict) else lfs.get("sha256")
        if path.stat().st_size != item.size:
            raise ValueError(f"Payload size differs: {item.path}")
        if expected:
            if digest(path) != expected:
                raise ValueError(f"Payload SHA256 differs: {item.path}")
        else:
            raw = path.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if blob != getattr(item, "blob_id", None):
                raise ValueError(f"Payload Git blob differs: {item.path}")
        target = destination / relative
        if not target.resolve().is_relative_to(destination):
            raise ValueError("Payload target escaped destination.")
        if target.exists() and digest(target) != digest(path):
            raise ValueError(f"Existing payload differs: {target}; use a separate destination.")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(path, target)
        files[relative] = {"bytes": item.size, "sha256": digest(target)}
        print(f"[payload] verified {relative}", flush=True)
    if not files:
        raise ValueError(f"No files beneath selected payload prefix: {prefix}")
    write(destination / "HF_PAYLOAD.json", {"repo": args.repo, "revision": args.revision, "prefix": prefix, "files": files,
          "note": "Archives require separate extraction; cache completion is established by the cache audit, not this download."})


def download_ready(args):
    listing = remote_inventory(args)
    api, download = hub()
    pointer_name = f"ready/{args.run_id}/LATEST_READY.json"
    if pointer_name not in listing["ready_pointers"]:
        raise ValueError(f"Missing {pointer_name}; inspect REMOTE_INVENTORY.json instead of using a checkpoint pointer.")
    pointer = read(download(args.repo, pointer_name, revision=listing["revision"], repo_type="model"))
    revision = pointer.get("revision", pointer.get("package_revision"))
    package = pointer.get("package", pointer.get("package_path", pointer.get("path_in_repo")))
    if isinstance(package, dict):
        package = package.get("path")
    expected = pointer.get("sha256", pointer.get("package_sha256"))
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Ready pointer needs an immutable 40-character package revision.")
    if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise ValueError("Ready pointer has no valid package SHA256.")
    safe_relative(package)
    if not package.startswith(f"ready/{args.run_id}/") or not package.endswith(".tar.zst"):
        raise ValueError("Ready pointer references an unexpected package namespace.")
    path = Path(download(args.repo, package, revision=revision, repo_type="model",
                         local_dir=str(Path(args.output) / "hub")))
    if digest(path) != expected or ("bytes" in pointer and path.stat().st_size != pointer["bytes"]):
        raise ValueError("Downloaded ready package failed size/SHA256 verification.")
    target = Path(args.output) / "restored"
    extract_archive(path, target)
    marker = unique_file(target, "READY.json")
    metadata = read(marker)
    if metadata.get("phase") != "admitted_not_started" or metadata.get("run_id") != args.run_id:
        raise ValueError("Ready package does not describe this unstarted run.")
    snapshot = unique_file(target, "snapshot.json", required=False)
    if snapshot:
        verify_files(snapshot.parent, read(snapshot)["files"])
    _, old, _ = admission(target)
    write(Path(args.output) / "RECOVERED_READY.json", {"pointer": pointer, "pointer_revision": listing["revision"],
          "package_sha256": expected, "restored": str(target.resolve()), "ready": metadata,
          "prior_binding": old["binding"]})
    print(f"[ready] verified; phase=admitted_not_started; restored={target.resolve()}", flush=True)
    print("[resources] A small ready package is not proof that weights, raw episodes or cache shards were backed up.")


def overlay(source, destination, preservation, protected=()):
    count = 0
    for path in sorted(Path(source).rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(source)
        if not eligible(relative) or any(relative.as_posix().startswith(p) for p in protected):
            continue
        target = Path(destination) / relative
        if not target.resolve().is_relative_to(Path(destination).resolve()):
            raise ValueError(f"Source overlay escaped destination: {relative}")
        if target.exists() and digest(target) != digest(path):
            saved = Path(preservation) / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        count += 1
    return count


def restore_code(args):
    ready, root = Path(args.ready).resolve(), Path(args.root).resolve()
    if not (root / ".git").exists():
        raise ValueError("Clone the user's Git repository before restoring saved physical sources.")
    work = root / "outputs/recovery_aws_v2/source_archives"
    preserved = root / "outputs/recovery_aws_v2/source_before_restore"
    specs = (("FastWAM.source.tar.gz", root, "src/fastwam/__init__.py"),
             ("RMBench.source.tar.gz", root / "resources/RMBench", "envs/_base_task.py"),
             ("PyTorch3D.source.tar.gz", root / "resources/PyTorch3D", "pytorch3d/__init__.py"))
    result = {}
    for filename, destination, marker in specs:
        archive = unique_file(ready, filename, required=filename != "PyTorch3D.source.tar.gz")
        if archive is None:
            print(f"[missing-source] {filename}; clone the recorded version before simulator compilation.")
            continue
        extracted = work / filename.removesuffix(".tar.gz")
        extract_archive(archive, extracted)
        roots = [p.parent.parent for p in extracted.rglob(Path(marker).name)
                 if p.as_posix().endswith(marker)]
        if marker.startswith("src/"):
            roots = [p.parent.parent.parent for p in extracted.rglob("__init__.py")
                     if p.as_posix().endswith(marker)]
        if len(roots) != 1:
            raise ValueError(f"Cannot uniquely locate source root for {filename}: {roots}")
        protected = ("scripts/memory_s1/portable/", "configs/memory_s1/s1_variable_t_h200.yaml") if destination == root else ()
        count = overlay(roots[0], destination, preserved / destination.name, protected)
        result[filename] = {"sha256": digest(archive), "files": count, "destination": str(destination)}
    # Reference repositories are freshly cloned at the recorded public commits;
    # restored archives without .git are not passed off as clean Git checkouts.
    write(root / "outputs/recovery_aws_v2/SOURCE_RESTORE.json", result)
    verify_source_hashes(ready, root, assets=False)
    print("[sources] saved production sources restored; portable tools and H200 config preserved.", flush=True)


def verify_source_hashes(ready, root, assets):
    _, old, _ = admission(ready)
    bound = old["binding"]
    root = Path(root)
    core = {p.relative_to(root).as_posix(): digest(p) for p in sorted((root / "src/fastwam/models/wan22").rglob("*.py"))}
    implementation = {p.name: digest(p) for p in sorted((root / "src/fastwam/memory_s1").glob("*.py"))}
    support = {p.relative_to(root).as_posix(): digest(p) for p in sorted((root / "scripts/memory_s1").glob("*"))
               if p.is_file() and p.suffix in (".py", ".sh")}
    for name, value in (("core_sha", core), ("implementation_sha", implementation), ("support_sha", support)):
        if canonical(value) != bound[name]:
            raise ValueError(f"Restored production code differs from prior admission: {name}")
    if assets:
        simulator = root / "resources/RMBench"
        folders = ("envs", "scripts", "script", "env_cfg", "task_config", "description", "data", "assets")
        files = {p.relative_to(simulator).as_posix(): digest(p) for folder in folders
                 for p in sorted((simulator / folder).rglob("*")) if p.is_file() and "__pycache__" not in p.parts
                 and p.suffix.lower() in (".py", ".json", ".yaml", ".yml", ".urdf", ".srdf", ".stl", ".obj", ".glb", ".dae")}
        if canonical(files) != bound["simulator_source_sha"]:
            raise ValueError("Simulator sources/assets differ from the old binding; keep downloads and inspect the differences.")
    print(f"[source-binding] production code verified; simulator_assets={assets}", flush=True)


def protected_download(args):
    cfg = config(args.config)
    root = Path(cfg["root"])
    ready = Path(args.ready)
    expected = {}
    old_lock = unique_file(ready, "download_lock.json", required=False)
    lock = read(old_lock) if old_lock else {"repositories": {}, "files": {}}
    current = root / "resources/download_lock.json"
    if current.exists():
        lock = read(current)
    for name, row in lock.get("files", {}).items():
        expected[name.replace("\\", "/")] = row["sha256"]
    # These are the already verified released base/statistics used by this run.
    expected.setdefault("resources/base/robotwin_uncond_3cam_384.pt", "776475b22566a791854ecf31cf3b50f25e7d8d94c343132ec16eb94994aa9e63")
    expected.setdefault("resources/base/robotwin_uncond_3cam_384_dataset_stats.json", "7a02c46cfc8c5e746c0afbe41fca73f723eda34cbc083f8ca54f76d8f7468095")
    frozen = unique_file(ready, "frozen_resources.json", required=False)
    if frozen:
        for name, row in read(frozen).items():
            expected[name.replace("\\", "/")] = row["sha256"]
    write(root / "outputs/recovery_aws_v2/EXPECTED_DOWNLOADS.json", {"files": expected, "prior_lock": lock})
    if not current.exists():
        write(current, lock)
    # Restored production scripts remain byte-identical to their admission binding.
    # Recovery uses maintained public sources without editing that old downloader.
    downloader = Path(__file__).resolve().with_name("resource_download.py")
    command = [sys.executable, "-u", str(downloader), "--root", str(root)]
    command += [f"--{key}" for key in ("models", "data", "assets") if getattr(args, key)]
    if len(command) == 5:
        raise ValueError("Choose at least one of --models --data --assets.")
    environment = {**os.environ, "HF_HUB_OFFLINE": "0", "TRANSFORMERS_OFFLINE": "0"}
    subprocess.run(command, cwd=root, env=environment, check=True)
    changed = []
    for name, value in expected.items():
        path = root / str(safe_relative(name))
        if path.is_file() and digest(path) != value:
            changed.append(name)
    _, _, reports = admission(ready)
    for row in reports["data"]["episodes"]:
        task, episode = row["episode_id"].split("/")
        path = Path(cfg["paths"]["raw"]) / task / "aloha_agilex/data" / f"{episode}.hdf5"
        if path.is_file() and digest(path) != row["raw_sha256"]:
            changed.append(str(path.relative_to(root)))
    if changed:
        write(root / "outputs/recovery_aws_v2/DOWNLOAD_MISMATCH.json", {"files": changed, "expected": expected})
        write(current, lock)
        raise ValueError(f"Protected original checksums differ: {changed}. New bytes are retained, never approved.")
    print("[download] Original known hashes retained and checked; newly resolved revisions are recorded separately.")


def ready_pack(args):
    cfg = config(args.config)
    root, run = Path(cfg["root"]), Path(cfg["paths"]["run"])
    from_package = run / "integration_admission.json"
    if not from_package.exists():
        raise ValueError("Generate the actual H200 integration admission before publishing readiness.")
    if (run / "checkpoints").exists() and any((run / "checkpoints").rglob("resume.pt")):
        raise ValueError("Training has started; use checkpoint backup rather than admitted_not_started.")
    stage = Path(args.output).resolve() / "payload"
    if (Path(args.output) / "PACKAGE.json").exists():
        raise ValueError("Ready snapshots are immutable; choose a new output directory.")
    stage.mkdir(parents=True, exist_ok=True)
    selected = [root / name for name in ("src", "scripts/memory_s1", "configs", "requirements", "pyproject.toml", ".gitignore")]
    selected += [root / "resources/download_lock.json", Path(cfg["paths"]["prepared"]), run / "integration_admission.json",
                 run / "integration_evidence", run / "storage_plan.json", root / "outputs/recovery_aws_v2/environment"]
    selected += [p for p in (run / "provenance", run / "parent_provenance") if p.exists()]
    review = run / "alignment_recovery_review.json"
    if review.exists():
        selected.append(review)
        selected += [p for p in (run / "data_review").rglob("*") if p.is_file()
                     and p.suffix.lower() in (".json", ".jsonl", ".log", ".png", ".jpg")]
    missing = [str(p) for p in selected if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Required reconstruction material is missing: {missing}")
    source_files = inventory(selected, root)
    for name in source_files:
        if "docs" in Path(name).parts:
            continue
        destination = stage / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, destination)
    # Keep the original exact simulator/build source archives as reconstruction inputs.
    old_ready = root / cfg.get("recovery", {}).get("ready_directory", "outputs/recovery_aws_v2/restored")
    for name in ("FastWAM.source.tar.gz", "RMBench.source.tar.gz", "PyTorch3D.source.tar.gz", "reference.source.tar.gz"):
        source = unique_file(old_ready, name, required=False)
        if source:
            destination = stage / "reconstruction_sources" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    cache = Path(cfg["paths"]["cache"])
    for name in ("manifest.json", "identity.json"):
        source = cache / name
        if source.exists():
            destination = stage / "resource_metadata/cache" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    frozen = {}
    for key in ("base", "stats", "vae", "t5", "tokenizer"):
        path = Path(cfg["paths"][key])
        candidates = [path] if path.is_file() else sorted(path.rglob("*"))
        for item in candidates:
            if item.is_file() and ".cache" not in item.parts:
                frozen[item.relative_to(root).as_posix()] = {"bytes": item.stat().st_size, "sha256": digest(item)}
    write(stage / "resource_metadata/frozen_resources.json", frozen)
    snapshot_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + f"_{time.time_ns()}"
    commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    bundle = stage / "source.bundle"
    subprocess.run(["git", "-C", str(root), "bundle", "create", str(bundle), "HEAD", "refs/heads/memory"], check=True)
    write(stage / "READY.json", {"schema": "fastwam-s1-ready-v1", "snapshot_id": snapshot_id, "run_id": run.name,
          "phase": "admitted_not_started", "source_commit": commit, "resolved_config": cfg,
          "prepared_tensors_included": True, "cache_payload_included": False, "frozen_weights_included": False})
    _, bound, _ = admission(stage)
    files = inventory([stage], stage)
    write(stage / "snapshot.json", {"schema": "fastwam-s1-ready-v1", "phase": "admitted_not_started",
          "snapshot_id": snapshot_id, "run_id": run.name, "binding": bound["binding"], "files": files})
    files = inventory([stage], stage)
    path = Path(args.output).resolve() / "ready.tar.zst"
    temporary = path.with_suffix(".partial")
    with temporary.open("wb") as output:
        compressor = subprocess.Popen(["zstd", "-T4", "-3", "-c"], stdin=subprocess.PIPE, stdout=output)
        try:
            with tarfile.open(fileobj=compressor.stdin, mode="w|") as archive:
                add_verified(archive, stage, files)
        finally:
            compressor.stdin.close()
            code = compressor.wait()
        if code != 0:
            raise ValueError("Ready compression failed; no pointer may reference this package.")
    temporary.replace(path)
    write(Path(args.output) / "PACKAGE.json", {"snapshot_id": snapshot_id, "run_id": run.name,
          "package": str(path), "bytes": path.stat().st_size, "sha256": digest(path), "phase": "admitted_not_started"})
    print(f"[ready-package] {path} bytes={path.stat().st_size}; model/cache payloads are separate.", flush=True)


def ready_upload(args):
    cfg = config(args.config)
    api, download = hub()
    root = Path(cfg["root"])
    spec = importlib.util.spec_from_file_location("portable_hf_tools", root / "scripts/memory_s1/hf_tools.py")
    utilities = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(utilities)
    metadata = read(Path(args.directory) / "PACKAGE.json")
    package = Path(metadata["package"])
    if digest(package) != metadata["sha256"]:
        raise ValueError("Ready package changed after packing.")
    plan = read(Path(cfg["paths"]["run"]) / "storage_plan.json")
    if plan["cache_signature"] != read(Path(cfg["paths"]["run"]) / "integration_admission.json")["binding"]["cache_signature"]:
        raise ValueError("Recompute the configuration-bound storage budget.")
    proposed = plan["planned_new_bytes"] + metadata["bytes"] + 1024**2
    budget = utilities.check_budget(api, proposed, cfg["hf"]["quota_gib"], cfg["hf"]["reserve_gib"])
    repo = cfg["hf"]["backup_repo"]
    utilities.ensure_private(api, repo, "model")
    remote = f"ready/{metadata['run_id']}/{metadata['snapshot_id']}/ready.tar.zst"
    result = api.upload_file(path_or_fileobj=str(package), path_in_repo=remote, repo_id=repo, repo_type="model",
                             commit_message=f"Save verified pre-training readiness {metadata['run_id']}")
    check = download(repo, remote, revision=result.oid, repo_type="model")
    if digest(check) != metadata["sha256"]:
        raise ValueError("Uploaded immutable package failed readback; latest-ready pointer is unchanged.")
    pointer = {key: metadata[key] for key in ("run_id", "snapshot_id", "phase", "bytes", "sha256")}
    pointer.update(repo=repo, revision=result.oid, package=remote)
    pointer_file = Path(args.directory) / "LATEST_READY.json"
    write(pointer_file, pointer)
    publication = api.upload_file(path_or_fileobj=str(pointer_file), path_in_repo=f"ready/{metadata['run_id']}/LATEST_READY.json",
                                  repo_id=repo, repo_type="model", commit_message="Publish verified pre-training ready pointer")
    reread = read(download(repo, f"ready/{metadata['run_id']}/LATEST_READY.json", revision=publication.oid, repo_type="model"))
    if reread != pointer:
        raise ValueError("Latest-ready pointer readback differs.")
    write(Path(cfg["paths"]["run"]) / "LATEST_READY_REMOTE.json", {**pointer, "pointer_revision": publication.oid, "budget": budget})
    print(f"[HF ready] verified revision={result.oid}; training checkpoint pointer was not modified.", flush=True)


def environment(args):
    root = Path(args.root).resolve()
    output = root / "outputs/recovery_aws_v2/environment"
    output.mkdir(parents=True, exist_ok=True)
    for name, prefix in (("training", "/opt/mwam"), ("hf", "/opt/hf-tools"), ("simulator", "/opt/rmbench-env")):
        python = str(Path(prefix) / "bin/python")
        packages = subprocess.check_output([python, "-m", "pip", "list", "--format=json"], text=True)
        write(output / f"{name}-pip-list.json", json.loads(packages))
        probe = "import sys, platform; print(sys.executable); print(sys.version); print(platform.platform())"
        if name != "hf":
            probe += "; import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.device_count())"
        (output / f"{name}-runtime.txt").write_text(subprocess.check_output([python, "-c", probe], text=True), encoding="utf-8")
    (output / "nvidia-smi.txt").write_text(subprocess.check_output(["nvidia-smi"], text=True), encoding="utf-8")
    host = root / "outputs/recovery_aws_v2/container-host.json"
    if not host.is_file():
        raise FileNotFoundError("Capture the actual Docker digest/mounts on the host before environment capture.")
    shutil.copy2(host, output / host.name)
    conda = Path("/opt/miniforge/bin/conda")
    if conda.is_file():
        (output / "simulator-conda-explicit.txt").write_text(subprocess.check_output(
            [str(conda), "list", "-p", "/opt/rmbench-env", "--explicit"], text=True), encoding="utf-8")
    # Only the two patched packages are copied, never authentication or environment secrets.
    simulator = "/opt/rmbench-env/bin/python"
    for module in ("sapien", "mplib"):
        folder = Path(subprocess.check_output([simulator, "-c", f"import {module}; from pathlib import Path; print(Path({module}.__file__).parent)"], text=True).strip().splitlines()[-1])
        for path in folder.rglob("*.py"):
            target = output / "simulator-patches" / module / path.relative_to(folder)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    print(f"[environment] reconstruction records saved: {output}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("inventory", "download-ready"):
        item = sub.add_parser(name)
        item.add_argument("--repo", default="hhyfred/fastwam-memory-s1-backup")
        item.add_argument("--output", required=True)
        if name == "download-ready":
            item.add_argument("--run-id", default="memory_s1_variable_t_seed17_v2")
    for name in ("restore-code", "verify-sources"):
        item = sub.add_parser(name)
        item.add_argument("--root", required=True)
        item.add_argument("--ready", required=True)
    item = sub.add_parser("resource-download")
    item.add_argument("--config", required=True)
    item.add_argument("--ready", required=True)
    for flag in ("models", "data", "assets"):
        item.add_argument(f"--{flag}", action="store_true")
    item = sub.add_parser("pack-ready")
    item.add_argument("--config", required=True)
    item.add_argument("--output", required=True)
    item = sub.add_parser("conda-spec")
    item.add_argument("--ready", required=True)
    item.add_argument("--output", required=True)
    item = sub.add_parser("upload-ready")
    item.add_argument("--config", required=True)
    item.add_argument("--directory", required=True)
    item = sub.add_parser("environment")
    item.add_argument("--root", required=True)
    item = sub.add_parser("pins")
    item.add_argument("--ready", required=True)
    item.add_argument("--kind", choices=("training", "simulator"), required=True)
    item.add_argument("--output", required=True)
    item = sub.add_parser("download-payload")
    item.add_argument("--repo", default="hhyfred/fastwam-memory-s1-backup")
    item.add_argument("--revision", required=True)
    item.add_argument("--prefix", required=True)
    item.add_argument("--destination", required=True)
    args = parser.parse_args()
    functions = {"inventory": remote_inventory, "download-ready": download_ready, "restore-code": restore_code,
                 "resource-download": protected_download, "pack-ready": ready_pack, "upload-ready": ready_upload,
                 "environment": environment, "pins": pins, "conda-spec": conda_spec, "download-payload": download_payload}
    if args.command == "verify-sources":
        verify_source_hashes(args.ready, args.root, assets=True)
    else:
        functions[args.command](args)


if __name__ == "__main__":
    main()
