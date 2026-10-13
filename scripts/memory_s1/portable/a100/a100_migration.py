"""Explicit H100 export / A100 recovery. Never launch a diagnostic or change old evidence."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import tarfile
import tempfile
import time
from urllib.parse import urlsplit, parse_qs

REPO = "hhyfred/fastwam-memory-s1-backup"
RUN = "memory_s1_variable_t_h100_phase_seed17"
POINTER = "migration/a100_after_h100/LATEST.json"
HISTORICAL_REVISION = 'c1aaa6dafddc0909cf1d89cacf966eeffbec6b9c'
SKIP = {".git", ".cache", "__pycache__", "build", "dist", ".pytest_cache", "node_modules", "packages"}
RMBENCH_RUNTIME_DIRS = {"eval_result", "eval_results", "logs", "outputs"}
MIGRATION_QUARANTINE = ".migration_runtime_quarantine"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
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


def migration_runtime(name):
    parts = PurePosixPath(name).parts
    return (len(parts) >= 4 and parts[:3] == ("project", "resources", "RMBench")
            and parts[3] in RMBENCH_RUNTIME_DIRS)


def migration_name(raw):
    """Keep the portable path policy; only quarantined legacy logs may contain colons."""
    if not isinstance(raw, str):
        raise ValueError(f"Invalid migration member name: {raw!r}")
    name = raw
    while name.startswith("./"):
        name = name[2:]
    path = PurePosixPath(name)
    if (not name or not path.parts or path.is_absolute() or ".." in path.parts or "\\" in name
            or any(ord(c) < 32 or ord(c) == 127 for c in name)
            or path.parts[0] == MIGRATION_QUARANTINE
            or (":" in name and not migration_runtime(name))):
        raise ValueError(f"Unsafe migration archive path: {raw}")
    return path.as_posix()


def migration_member_path(package, name):
    name = migration_name(name)
    if migration_runtime(name):
        # Never create legacy timestamp/ADS names or restore logs as simulator source.
        key = hashlib.sha256(name.encode("utf-8")).hexdigest()
        relative = Path(MIGRATION_QUARANTINE) / (key + ".blob")
    else:
        relative = Path(name)
    package = Path(package).resolve()
    candidate = package / relative
    path = candidate.resolve()
    if not path.is_relative_to(package) or candidate.is_symlink():
        raise ValueError(f"Migration destination escapes/is a symlink: {name}")
    return path


def verify_migration_files(package):
    quarantined = {}
    for name, row in read(Path(package) / "FILES.json").items():
        path = migration_member_path(package, name)
        if not path.is_file() or path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise ValueError(f"Migration member mismatch: {name}")
        if migration_runtime(name):
            quarantined[name] = {**row, "stored_as": path.relative_to(Path(package).resolve()).as_posix()}
    return quarantined


def extract_migration_archive(archive, package):
    """Verify all members; preserve legacy runtime bytes under portable hashed names."""
    package = Path(package).resolve()
    with tarfile.open(archive, "r:gz") as tar:
        members = {}
        for member in tar.getmembers():
            if member.isdir() and member.name in ("", ".", "./"):
                continue
            name = migration_name(member.name)
            if member.isdir():
                continue
            if not member.isfile() or name in members:
                raise ValueError(f"Duplicate or non-regular migration member: {member.name}")
            members[name] = member
        if "FILES.json" not in members or members["FILES.json"].size > 64 * 1024**2:
            raise ValueError("Missing/oversized migration FILES.json")

        def unique_object(pairs):
            value = {}
            for key, item in pairs:
                if key in value:
                    raise ValueError(f"Duplicate migration manifest key: {key}")
                value[key] = item
            return value

        with tar.extractfile(members["FILES.json"]) as stream:
            manifest_bytes = stream.read()
        manifest = json.loads(manifest_bytes, object_pairs_hook=unique_object)
        if not isinstance(manifest, dict) or set(members) != set(manifest) | {"FILES.json"}:
            raise ValueError("Migration archive members differ from FILES.json")
        for name, row in manifest.items():
            if (name == "FILES.json" or migration_name(name) != name or not isinstance(row, dict)
                    or type(row.get("bytes")) is not int or row["bytes"] < 0
                    or not isinstance(row.get("sha256"), str)
                    or not re.fullmatch(r"[0-9a-f]{64}", row["sha256"])
                    or members[name].size != row["bytes"]):
                raise ValueError(f"Invalid migration manifest member: {name}")
        expected_files = {**manifest, "FILES.json": {
            "bytes": len(manifest_bytes), "sha256": hashlib.sha256(manifest_bytes).hexdigest()}}
        # Validate every destination and existing partial file before writing anything.
        destinations = {name: migration_member_path(package, name) for name in members}
        for name, path in destinations.items():
            if path.exists():
                expected = expected_files[name]
                if not path.is_file():
                    raise ValueError(f"Existing migration destination is not a file: {path}")
                if path.stat().st_size != expected["bytes"] or sha(path) != expected["sha256"]:
                    raise ValueError(f"Existing migration file differs; preserve it first: {path}")
        for name, member in members.items():
            target = destinations[name]
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".migration-restore-", delete=False) as out:
                    temporary = Path(out.name)
                    checksum = hashlib.sha256()
                    with tar.extractfile(member) as stream:
                        for block in iter(lambda: stream.read(8 * 1024**2), b""):
                            checksum.update(block)
                            out.write(block)
                expected = expected_files[name]
                if temporary.stat().st_size != expected["bytes"] or checksum.hexdigest() != expected["sha256"]:
                    raise ValueError(f"Migration archived bytes mismatch: {name}")
                temporary.chmod(member.mode & 0o777)
                temporary.replace(target)
            finally:
                if temporary is not None and temporary.exists():
                    temporary.unlink()
    return verify_migration_files(package)


def copy_tree(source, target, *, source_only=False, exclude_top=()):
    source, target = Path(source), Path(target)
    if not source.is_dir():
        raise FileNotFoundError(source)
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        if rel.parts[0] in exclude_top:
            continue
        if path.is_symlink() or not path.is_file() or set(rel.parts) & SKIP:
            continue
        if any(p.endswith(".egg-info") for p in rel.parts) or path.suffix in (".so", ".pyc", ".o", ".a", ".pem", ".key"):
            continue
        if path.name.startswith(".env") or path.name in ("token", "stored_tokens", "credentials", ".netrc"):
            continue
        if source_only and path.suffix.lower() not in (".py", ".yaml", ".yml", ".json", ".toml", ".txt", ".sh", ".cu", ".h", ".cuh", ".cpp", ".c", ".hpp", ".md", ".cfg", ".ini", ".urdf", ".srdf", ".xml", ".xacro"):
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
    evidence = args.diagnosis / 'HF_diagnosis.json'
    if not evidence.is_file() or read(evidence).get("readback_verified") is not True:
        raise ValueError("Finish this H100 diagnosis and its verified backup first; no diagnostic will be started here.")
    if read(evidence)['revision'] != HISTORICAL_REVISION:
        raise ValueError(f'Expected diagnosis revision {HISTORICAL_REVISION}, got {read(evidence)["revision"]}')
    if args.frozen is None:
        raise ValueError('--frozen is required; export does not wait for new GPU diagnostics')
    sys.path.insert(0, str(root/'src'))
    from fastwam.memory_s1.grasp_bridge import verify, historical_manifest
    historical_manifest(evidence.parent)
    verify(args.frozen, read(args.frozen/'FILES.json'))
    frozen_value = read(args.frozen/'FROZEN.json')
    if frozen_value['historical_revision'] != HISTORICAL_REVISION:
        raise ValueError('Frozen input history differs')
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
    copy_tree(args.frozen, payload/'frozen_inputs')
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
    copy_tree(root / "resources/RMBench", payload / "project/resources/RMBench",
              source_only=True, exclude_top=RMBENCH_RUNTIME_DIRS)
    for name in ("src", "scripts/memory_s1", "configs", "requirements"):
        copy_tree(root / name, payload / "historical_code" / name, source_only=True)
    copy_tree(root / "resources/prepared_dense_h100_v1", payload / "project/resources/prepared_dense_h100_v1")
    host = root/'outputs/recovery_aws_h100/container-host.json'
    if not host.is_file():
        raise FileNotFoundError(f'Capture actual mwam image/digest/mounts on the host first: {host}')
    # Export only an allowlisted host record, never docker inspect Config.Env.
    host_value = read(host)
    if not host_value.get('image_id') or not host_value.get('repo_digests'):
        raise ValueError('container-host.json must contain image_id and repo_digests')
    write(payload/'container-host.json',{k:host_value[k] for k in ('image_id','repo_digests','mounts','container') if k in host_value})
    patch = subprocess.check_output(['git','-C',str(root),'diff','--binary','HEAD','--','src','scripts/memory_s1','configs','requirements'])
    (payload/'historical_code/worktree.patch').write_bytes(patch)
    # Final source/asset identity is measured after H100's real patches, not inferred from a branch name.
    resource_files = {}
    for directory in ('resources/RMBench/assets','resources/RMBench/envs','resources/RMBench/task_config','resources/RMBench/env_cfg','resources/RMBench/data/demo_clean','resources/tokenizer'):
        for p in sorted((root/directory).rglob('*')):
            if p.is_file() and not p.is_symlink() and not set(p.relative_to(root).parts)&SKIP and p.suffix not in ('.so','.pyc','.o'):
                resource_files[p.relative_to(root).as_posix()] = sha(p)
    for key in ('base','stats','vae','t5'):
        p = Path(read(evidence.parent/'identity.json')['config']['paths'][key])
        resource_files[p.relative_to(root).as_posix()] = sha(p)
    write(payload/'RESOURCE_IDENTITY.json',resource_files)
    # Old Windows/H100 source paths are provenance only; current A100 code stays separate.
    write(payload/'CODE_IDENTITY.json',{p.relative_to(root).as_posix():sha(p) for folder in ('src','scripts/memory_s1','configs')
        for p in sorted((root/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.sh','.yaml','.json')})
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
    checkpoint = read(download(args.repo, f"runs/{RUN}/LATEST_COMPLETE.json", revision=repository_revision))
    if checkpoint['step'] != 2000:
        raise ValueError('Migration requires the completed S1 update 2000 recovery point')
    write(payload / "CHECKPOINT_REMOTE.json", checkpoint)
    # Save actual frozen banks without importing any completed evaluation into a new queue.
    banks = list((root / "outputs/posttrain_h100_phase_seed17_top2_v2").glob("frozen_scenes.json"))
    if len(banks) != 1 or len(read(banks[0]).get("scenes", [])) != 20:
        raise ValueError("Expected the existing 20-scene bank; no seed search is allowed")
    shutil.copy2(banks[0], payload / "frozen_scenes.json")
    write(payload / "ORIGIN.json", {"commit": run(["git", "-C", root, "rev-parse", "HEAD"]).strip(),
          "run": RUN, "diagnosis": read(evidence), "export_tool_sha256": sha(__file__), "phase": "grasp_bridge_migration_v1",
          "frozen_inputs_sha256":sha(args.frozen/'FILES.json'),"checkpoint_pointer_read_revision":repository_revision,
          "does_not_include": ["models", "raw_hdf5", "asset_meshes", "dense_cache", "CUDA_binaries", "tokens", "RMBench_runtime_logs"],
          "note": "Historical code is evidence only. It must not overwrite the new A100 entry points."})
    files = {p.relative_to(payload).as_posix(): {"sha256": sha(p), "bytes": p.stat().st_size}
             for p in sorted(payload.rglob("*")) if p.is_file()}
    for name in files:
        if migration_name(name) != name or migration_runtime(name):
            raise ValueError(f"Non-portable/runtime file in new migration payload: {name}")
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
               "schema":"grasp_bridge_migration_v1", "diagnosis_revision":HISTORICAL_REVISION,
               "frozen_inputs_sha256":sha(args.frozen/'FILES.json'),
               "bytes": archive.stat().st_size, "readback_verified": True, "budget": budget}
    write(output / "LATEST.json", pointer)
    publication = api.upload_file(repo_id=args.repo, path_or_fileobj=str(output / "LATEST.json"), path_in_repo=POINTER)
    if read(download(args.repo, POINTER, revision=publication.oid)) != pointer:
        raise ValueError("Migration pointer readback mismatch")
    write(output / "UPLOAD_COMPLETE.json", {**pointer, "pointer_revision": publication.oid})
    write(args.frozen.parent/'MIGRATION_COMPLETE.json',{**pointer,'pointer_revision':publication.oid})
    print(json.dumps(pointer, indent=2), flush=True)


def fetch(args):
    api, download = hub()
    output = args.root / "outputs/recovery_aws_a100_v1"
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / "MIGRATION_REMOTE.json"
    selected = output / "MIGRATION_SELECTED.json"
    if receipt.exists():
        pointer = read(receipt)  # A restart never silently selects a newer migration.
    elif selected.exists():
        pointer = read(selected)  # Preserve the selection even if extraction fails.
    else:
        revision = api.repo_info(args.repo).sha
        pointer = read(download(args.repo, POINTER, revision=revision))
        pointer["pointer_revision"] = revision
    if pointer["repo"] != args.repo or not pointer["readback_verified"]:
        raise ValueError("Unverified/mismatched migration pointer")
    if pointer.get('schema') != 'grasp_bridge_migration_v1' or pointer.get('diagnosis_revision') != HISTORICAL_REVISION:
        raise ValueError(f'Stale pinned migration: {receipt}. Preserve it explicitly, then fetch the new verified export; no silent revision switch.')
    if selected.exists() and read(selected) != pointer:
        raise ValueError(f'Migration selection differs from the completed receipt: {selected}')
    if not selected.exists():
        write(selected, pointer)
    archive = Path(download(args.repo, pointer["package"], revision=pointer["revision"]))
    if sha(archive) != pointer["sha256"] or archive.stat().st_size != pointer["bytes"]:
        raise ValueError("Migration archive checksum mismatch")
    target = output / "migration"
    quarantined = extract_migration_archive(archive, target)
    write(output / "MIGRATION_RUNTIME_QUARANTINE.json", {
        "archive_sha256": pointer["sha256"], "revision": pointer["revision"],
        "policy": "rmb_runtime_quarantine_v1", "files": quarantined,
        "note": "Original manifest and bytes verified; runtime logs are never restored as source."})
    print(f"[migration] verified legacy runtime files quarantined={len(quarantined)}; source hashes unchanged", flush=True)
    if (read(target/'ORIGIN.json')['diagnosis']['revision'] != HISTORICAL_REVISION or
            sha(target/'frozen_inputs/FILES.json') != pointer['frozen_inputs_sha256']):
        raise ValueError('Migration historical diagnosis/frozen identity mismatch')
    write(receipt, pointer)
    mark(args.root,'fetch')
    print("[migration] verified", target, flush=True)


def restore(args):
    root = args.root
    package = root / "outputs/recovery_aws_a100_v1/migration"
    files = read(package / "FILES.json")
    require(args.root, 'payloads')
    verify_migration_files(package)
    # Never restore live leases, checkpoints or historical code over current code.
    for name, row in files.items():
        if not name.startswith("project/") or migration_runtime(name):
            continue
        # Download public asset bytes first; apply final URDF/config patches afterwards.
        if name.startswith('project/resources/RMBench/assets/') and not args.overlay_sources:
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
    mark(args.root, 'patch-sources' if args.overlay_sources else 'restore')


def payloads(args):
    root = args.root
    output = root / "outputs/recovery_aws_a100_v1"
    package = output / "migration"
    require(root,'fetch')
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
    frozen_weights = read(package/'frozen_inputs/FROZEN.json')['weights']
    for label in ('step_000000','step_001500','step_002000'):
        name=f'weights/{label}.pt'
        if files.get(name) != frozen_weights[label]['sha256']:
            raise ValueError(f'Checkpoint manifest lacks the exact frozen weight: {name}')
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
    mark(root,'payloads')


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


DEPENDENCIES = {
    'payloads':['fetch'], 'restore':['payloads'], 'resources':['restore'],
    'patch-sources':['resources'], 'verify-resources':['patch-sources'],
    'training':['verify-resources'], 'references':['training'], 'simulator':['references'],
    'devices':['simulator'], 'planners':['devices'], 'models':['planners'],
    'nccl':['devices'], 'report':['models','nccl'], 'backup':['report']}


def mark(root, stage):
    base=root/'outputs/recovery_aws_a100_v1'
    migration=base/'MIGRATION_REMOTE.json'
    write(base/'receipts'/f'{stage}.json', {'complete':True,'stage':stage,'migration_sha256':sha(migration),
        'time':time.time()})


def require(root, stage):
    base=root/'outputs/recovery_aws_a100_v1'
    path=base/'receipts'/f'{stage}.json'
    if not path.exists() or not read(path).get('complete') or read(path)['migration_sha256']!=sha(base/'MIGRATION_REMOTE.json'):
        raise ValueError(f'Complete matching A100 prerequisite first: {path}')


def precheck(args):
    for stage in DEPENDENCIES.get(args.stage,[]): require(args.root,stage)
    package=args.root/'outputs/recovery_aws_a100_v1/migration'
    if args.stage not in ('fetch','inventory','system','hf'):
        verify_migration_files(package)
    if args.stage in ('training','simulator'):
        source=read(package/'container-host.json')
        current=read(args.root/'outputs/recovery_aws_a100_v1/container-host.json')
        if not set(source['repo_digests'])&set(current['repo_digests']):
            raise ValueError('Container digest differs; resolve it before environment installation')


def training_env(args):
    precheck(argparse.Namespace(root=args.root,stage='training'))
    base=args.root/'outputs/recovery_aws_a100_v1'
    package=base/'migration'
    selected=base/'training-reuse-pins.txt'
    tool(args.root,'portable/recovery.py').pins(argparse.Namespace(ready=str(package),kind='training',output=str(selected)))
    expected=read(selected.with_suffix('.sources.json'))['selected']
    python=Path('/opt/mwam/bin/python')
    if python.exists():
        actual={r['name'].lower().replace('_','-'):r['version'] for r in json.loads(run([python,'-m','pip','list','--format=json']))}
        if all(actual.get(k)==v for k,v in expected.items()):
            result=subprocess.run([str(python),'-c',
                'import torch,fastwam.memory_s1.model; assert torch.__version__.startswith("2.10.0a0"); assert torch.version.cuda=="13.0"; assert torch.cuda.device_count()==8'],capture_output=True,text=True)
            if result.returncode==0:
                print('[reuse] Existing A100 model environment matches application pins, NVIDIA torch and 8 devices')
                mark(args.root,'training'); return
    env=dict(os.environ);env['READY_DIR']=str(package)
    env['CONFIG']=str(args.root/'configs/memory_s1/recovery_a100.yaml')
    subprocess.run(['bash',str(args.root/'scripts/memory_s1/portable/install_environments.sh'),'training'],check=True,env=env,cwd=args.root)
    mark(args.root,'training')


def resources(args):
    precheck(argparse.Namespace(root=args.root,stage='resources'))
    base=args.root/'outputs/recovery_aws_a100_v1'; package=base/'migration'
    original=read(package/'project/resources/download_lock.json')
    needed=('model:yuanty/fastwam','model:Wan-AI/Wan2.2-TI2V-5B','dataset:TianxingChen/RMBench')
    import re
    for name in needed:
        if not re.fullmatch('[0-9a-f]{40}',original['repositories'].get(name,'')):
            raise ValueError(f'Immutable publisher revision missing from exported lock: {name}; no latest-branch fallback')
    patched={n.removeprefix('project/') for n in read(package/'FILES.json') if n.startswith('project/resources/RMBench/assets/')}
    lock=base/'PUBLIC_DOWNLOAD_LOCK.json'
    expected={n:row for n,row in original['files'].items() if n not in patched}
    if not lock.exists(): write(lock,{'repositories':original['repositories'],'files':expected})
    write(base/'PUBLIC_EXPECTED.json',{'files':{n:r['sha256'] for n,r in expected.items()}})
    # Public revision authenticates downloaded pre-patch assets. Final patch identity is verified separately.
    subprocess.run([sys.executable,'-u',str(args.root/'scripts/memory_s1/portable/resource_download.py'),
        '--root',str(args.root),'--lock-file',str(lock),'--expected-file',str(base/'PUBLIC_EXPECTED.json'),
        '--models','--data','--assets'],check=True)
    mark(args.root,'resources')


def verify_resources(args):
    require(args.root,'patch-sources')
    base=args.root/'outputs/recovery_aws_a100_v1'
    for name,expected in read(base/'migration/RESOURCE_IDENTITY.json').items():
        path=(args.root/name).resolve()
        actual=sha(path) if path.is_file() else 'MISSING'
        if not path.is_relative_to(args.root) or actual!=expected:
            raise ValueError(f'Final resource mismatch {path}: expected={expected}, actual={actual}')
    mark(args.root,'verify-resources')
    print('[resources] published resources plus sourced patches match final H100 identities; no local admission inherited')


def recovery_report(args):
    base=args.root/'outputs/recovery_aws_a100_v1'
    for stage in ('verify-resources','references','devices','planners','models','nccl'): require(args.root,stage)
    bridge=args.root/'outputs/s1_grasp_bridge_a100_v1'
    for stage in ('planners','models'):
        value=read(bridge/'receipts'/f'{stage}.json')
        if not value['passed']: raise ValueError(f'A100 {stage} failed')
        for name,expected in value['files'].items():
            if sha(bridge/name)!=expected: raise ValueError(f'Changed qualification file: {name}')
    devices=read(base/'DEVICES_COMPLETE.json'); nccl_record=read(base/'NCCL_COMPLETE.json')
    if not devices['passed'] or len(devices['devices'])!=8 or not nccl_record['passed']:
        raise ValueError('Eight-device/NCCL proof incomplete')
    source_host=read(base/'migration/container-host.json'); target_host=read(base/'container-host.json')
    if not set(source_host['repo_digests'])&set(target_host['repo_digests']):
        raise ValueError('A100 model container digest differs from exported H100 image; inspect before qualification approval')
    value={'ready':True,'scope':'A100 diagnosis ready only; not training admission or benchmark success',
        'migration':read(base/'MIGRATION_REMOTE.json'),'devices':devices,'nccl':nccl_record,
        'planners':read(bridge/'planners.json'),'models':read(bridge/'models.json'),
        'container':target_host,'dense_cache_required':False,'optimizer_updates':0}
    write(base/'A100_DIAGNOSIS_READY.json',value); mark(args.root,'report')
    write(bridge/'A100_DIAGNOSIS_READY.json',value)
    print('[ready] A100 diagnosis ready: 8 device/planner/model checks + NCCL; no training/benchmark run')


def compile_budget(args):
    available=len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else os.cpu_count()
    memory=next(int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemAvailable:'))
    total=min(64,max(1,available-8),int(memory//(3*1024**3)))
    if total<2: raise ValueError('Need capacity for two compiler workers after CPU/memory reserves')
    requested=os.environ.get('A100_COMPILE_JOBS')
    per=max(1,total//2)
    if requested: per=min(per,int(requested))
    if per<1: raise ValueError('A100_COMPILE_JOBS must be positive')
    write(args.root/'outputs/fused_environment_a100_v1/compile_budget.json',
        {'available_cpu':available,'available_memory_bytes':memory,'total_limit':total,'jobs_per_build':per,'concurrent_builds':2})
    print(per)


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
    if not marker.exists():
        print('No A100 stage recorded'); return
    value = read(marker)
    owner = value["owner"]
    current = process(owner["pid"]) if owner else None
    if not current or current["state"] == "Z" or current["start_ticks"] != owner["start_ticks"]:
        print("No matching live A100 setup process")
        return
    if os.getpgid(owner["pid"]) != owner["pid"]:
        raise RuntimeError("Refusing to stop an unrelated process group")
    write(args.root/'outputs/recovery_aws_a100_v1/STOP',{'owner':owner,'time':time.time()})
    sys.path.insert(0,str(args.root/'src'))
    from fastwam.memory_s1.grasp_bridge import stop_owned_tree
    stop_owned_tree(owner)
    print("Stop requested for the recorded A100 setup only; retain partial files and inspect its exit receipt")


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("export", "fetch", "payloads", "restore", "pins", "patches", "device", "devices", "nccl", "register", "status", "stop", 'resources','verify-resources','precheck','mark','report','compile-budget','training'))
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"))
    parser.add_argument("--repo", default=REPO)
    parser.add_argument("--kind", choices=("training", "simulator"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pid", type=int)
    parser.add_argument("--log", type=Path)
    parser.add_argument('--diagnosis',type=Path,default=Path('/workspace/FastWAM/outputs/s1_zero_success_followup_v2'))
    parser.add_argument('--frozen',type=Path)
    parser.add_argument('--stage')
    parser.add_argument("--overlay-sources", action="store_true", help="Restore recorded simulator patches after asset download; preserve conflicting downloaded files")
    args = parser.parse_args()
    args.root = args.root.resolve()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    if args.command=='mark': mark(args.root,args.stage)
    else: globals()[{'report':'recovery_report','verify-resources':'verify_resources','compile-budget':'compile_budget','training':'training_env'}.get(args.command,args.command)](args)


if __name__ == "__main__":
    main()
