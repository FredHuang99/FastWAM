"""HF-only environment utility. Never load training dependencies or print tokens."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

# Enable Hub requests only in this independent HF utility process.
os.environ["HF_HUB_OFFLINE"] = "0"
os.environ["TRANSFORMERS_OFFLINE"] = "0"

from huggingface_hub import HfApi, CommitOperationAdd, snapshot_download


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def account_storage(api):
    username = api.whoami()["name"]
    if not callable(getattr(api, "list_user_repos", None)):
        raise RuntimeError(
            "HF account storage requires HfApi.list_user_repos; "
            "run this utility with /opt/hf-tools/bin/python and huggingface-hub==1.19.0."
        )
    total = 0
    inventory = []
    seen = set()
    # Read personal-namespace storage from the account endpoint, including buckets.
    # Do not enumerate buckets again or estimate storage from the current file tree.
    for repository in api.list_user_repos():
        repo_id = repository.id
        kind = repository.type
        visibility = repository.visibility
        if not isinstance(repo_id, str) or kind not in ("model", "dataset", "space", "bucket"):
            raise RuntimeError("HF returned an unsupported repository in the account storage listing.")
        key = (kind, repo_id)
        if key in seen:
            raise RuntimeError(f"HF returned a duplicate storage entry: {kind}/{repo_id}.")
        seen.add(key)
        if visibility not in ("public", "private"):
            raise RuntimeError(f"HF did not expose supported visibility for {repo_id}; quota cannot be verified.")
        if visibility == "public":
            continue
        used = repository.storage
        if isinstance(used, bool) or not isinstance(used, int) or used < 0:
            raise RuntimeError(f"HF did not expose valid account storage for {repo_id}; quota cannot be verified.")
        total += used
        inventory.append({"id": repo_id, "type": kind, "used_bytes": used})
    inventory.sort(key=lambda entry: (entry["type"], entry["id"]))
    return username, total, inventory


def check_budget(api, planned_bytes, quota_gib, reserve_gib):
    username, used, repositories = account_storage(api)
    quota, reserve = int(quota_gib * 2**30), int(reserve_gib * 2**30)
    if used + planned_bytes + reserve > quota:
        raise RuntimeError(f"Private quota guard: used={used/2**30:.2f}GiB proposed={planned_bytes/2**30:.2f}GiB reserve={reserve_gib}GiB exceeds {quota_gib}GiB. Local files are preserved.")
    return {"username": username, "used_bytes": used, "planned_bytes": planned_bytes,
            "quota_bytes": quota, "reserve_bytes": reserve, "repositories": repositories}


def ensure_private(api, repository, repo_type):
    username = api.whoami()["name"]
    if repository.split("/")[0] != username:
        raise ValueError("Backup repository owner differs from the authenticated user.")
    api.create_repo(repository, repo_type=repo_type, private=True, exist_ok=True)
    if api.repo_info(repository, repo_type=repo_type).private is not True:
        raise ValueError("Existing backup repository is public; this utility only uploads to private repositories.")


def checkpoint(args):
    started = time.monotonic()
    api = HfApi()
    run, directory = Path(args.run).resolve(), Path(args.checkpoint).resolve()
    if directory.parent != run / "checkpoints":
        raise ValueError("Checkpoint must be directly inside this run's checkpoints directory.")
    marker = json.loads((directory / "complete.json").read_text())
    if marker["sha256"] != digest(directory / "resume.pt"):
        raise ValueError("Local checkpoint checksum mismatch.")
    root = Path(marker["identity"]["code"].get("root", run.parents[1]))
    # Run root is configurable; code root is recorded explicitly by the launcher/config.
    config = json.loads((run / "config_resolved.json").read_text())
    root = Path(config["root"])
    provenance = run / "provenance"
    provenance.mkdir(exist_ok=True)
    (provenance / "git.diff").write_text(subprocess.check_output(["git", "-C", str(root), "diff", "HEAD", "--binary"], text=True))
    (provenance / "pip-freeze.txt").write_text(subprocess.check_output([config.get("training_python", "/usr/local/bin/python"), "-m", "pip", "list", "--format=freeze"], text=True))
    files = [(directory / "resume.pt", f"checkpoints/{directory.name}/resume.pt"),
             (directory / "complete.json", f"checkpoints/{directory.name}/complete.json")]
    # Save one complete Git source bundle and a patch covering tracked local modifications.
    bundle = provenance / "source.bundle"
    bundle_stamp = provenance / "source_bundle_commit.json"
    commit_id = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if not bundle.exists() or not bundle_stamp.exists() or json.loads(bundle_stamp.read_text())["commit"] != commit_id:
        subprocess.run(["git", "-C", str(root), "bundle", "create", str(bundle), "HEAD", "refs/heads/memory"], check=True)
        write_json(bundle_stamp, {"commit": commit_id, "sha256": digest(bundle)})
    resources = {}
    for key in ("base", "stats", "vae", "t5", "tokenizer"):
        path = Path(config["paths"][key])
        members = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file() and ".cache" not in p.parts]
        for member in members:
            resources[str(member.relative_to(root))] = {"sha256": digest(member), "bytes": member.stat().st_size}
    write_json(provenance / "frozen_resources.json", resources)
    for kind in ("prepared", "cache"):
        directory_root = Path(config["paths"][kind])
        for filename in ("manifest.json", "alignment_approved.json", "identity.json"):
            path = directory_root / filename
            if path.is_file():
                files.append((path, f"resource_metadata/{kind}/{filename}"))
    download_lock = root / "resources/download_lock.json"
    if download_lock.exists():
        files.append((download_lock, "resource_metadata/download_lock.json"))
    if (directory / "continuation.json").exists():
        files.append((directory / "continuation.json", f"checkpoints/{directory.name}/continuation.json"))
    for path in run.rglob("*"):
        if not path.is_file() or path.relative_to(run).parts[0] in ("checkpoints", "code") or path.suffix in (".sock", ".tmp", ".pid", ".lock"):
            continue
        if path.name in ("STOP_REQUESTED", "STOP.json", "ABORT.json", "launcher.pid", "UPLOAD_FAILED.json", "HF_EPISODES.json"):
            continue
        relative = path.relative_to(run)
        if ("launches" in relative.parts and path.suffix == ".log") or "frames" in relative.parts or "interrupted_logs" in relative.parts or "interrupted_artifacts" in relative.parts or path.name in ("BACKUP_FILES.json", "LATEST_REMOTE.json"):
            continue
        files.append((path, str(relative).replace(os.sep, "/")))
    for subdirectory in ("src/fastwam/memory_s1", "src/fastwam/models/wan22", "scripts/memory_s1", "configs/memory_s1", "requirements"):
        for path in (root / subdirectory).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                files.append((path, "code/" + str(path.relative_to(root)).replace(os.sep, "/")))
    for filename in ("configs/model/fastwam.yaml", "pyproject.toml", ".gitignore"):
        files.append((root / filename, "code/" + filename))
    # A snapshot hash manifest makes both download integrity and unchanged-file reuse explicit.
    snapshot_files = {remote: digest(path) for path, remote in files}
    manifest_path = directory / "backup_manifest.json"
    write_json(manifest_path, {"step": marker["completed_updates"], "files": snapshot_files})
    files.append((manifest_path, f"checkpoints/{directory.name}/backup_manifest.json"))
    previous_path = run / "BACKUP_FILES.json"
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else {}
    changed = [(path, remote) for path, remote in files if previous.get(remote) != digest(path)]
    estimated = sum(path.stat().st_size for path, _ in changed)
    expected = json.loads((run / "storage_plan.json").read_text())
    limit = expected["initial_checkpoint_estimate_bytes"] if marker["completed_updates"] == 0 else expected["full_checkpoint_estimate_bytes"]
    if (directory / "resume.pt").stat().st_size > limit:
        raise RuntimeError("The serialized checkpoint exceeds the preflight budget. Recompute storage_plan before retrying.")
    budget = check_budget(api, estimated, args.quota_gib, args.reserve_gib)
    ensure_private(api, args.repo, "model")
    run_id = run.name
    operations = [CommitOperationAdd(path_in_repo=f"runs/{run_id}/{remote}", path_or_fileobj=str(path)) for path, remote in changed]
    commit = None
    for start in range(0, len(operations), 50):
        commit = api.create_commit(args.repo, repo_type="model", operations=operations[start:start+50],
                                   commit_message=f"S1 update {marker['completed_updates']} ({run_id}), files {start+1}-{min(start+50,len(operations))}")
    revision = commit.oid if commit is not None else api.repo_info(args.repo, repo_type="model").sha
    pointer = {"run_id": run_id, "step": marker["completed_updates"], "directory": directory.name,
               "checkpoint_revision": revision, "resume_sha256": marker["sha256"],
               "backup_manifest_sha256": digest(manifest_path),
               "upload_seconds": time.monotonic() - started}
    pointer_path = directory / "remote_pointer.json"
    write_json(pointer_path, pointer)
    pointer_commit = api.upload_file(path_or_fileobj=str(pointer_path), path_in_repo=f"runs/{run_id}/LATEST_COMPLETE.json",
                                    repo_id=args.repo, repo_type="model", commit_message=f"Publish complete S1 pointer {marker['completed_updates']}")
    write_json(run / "BACKUP_FILES.json", {remote: digest(path) for path, remote in files})
    write_json(run / "LATEST_REMOTE.json", {**pointer, "pointer_revision": pointer_commit.oid, "budget": budget})
    print(f"[HF] complete update={pointer['step']} revision={revision}", flush=True)


def upload_package(args):
    api = HfApi()
    directory = Path(args.directory).resolve()
    files = [path for path in directory.iterdir() if path.is_file()]
    if not files or any(path.suffix not in (".zst", ".json", ".sha256") and ".part-" not in path.name for path in files):
        raise ValueError("Package folder must contain only archive shards, JSON manifest, and SHA256 lists.")
    check_budget(api, sum(path.stat().st_size for path in files), args.quota_gib, args.reserve_gib)
    ensure_private(api, args.repo, args.repo_type)
    result = api.upload_folder(folder_path=str(directory), path_in_repo=args.prefix,
                               repo_id=args.repo, repo_type=args.repo_type, commit_message="Upload verified portable S1 package")
    print(f"[HF package] revision={result.oid}", flush=True)


def download_resume(args):
    from huggingface_hub import hf_hub_download
    api = HfApi()
    pointer_file = hf_hub_download(args.repo, f"runs/{args.run_id}/LATEST_COMPLETE.json", repo_type="model")
    pointer = json.loads(Path(pointer_file).read_text())
    revision = pointer["checkpoint_revision"]
    prefix = f"runs/{args.run_id}"
    manifest_remote = f"{prefix}/checkpoints/{pointer['directory']}/backup_manifest.json"
    if pointer.get("backup_manifest_sha256"):
        path = hf_hub_download(args.repo, manifest_remote, repo_type="model", revision=revision, local_dir=args.output)
        if digest(path) != pointer["backup_manifest_sha256"]:
            raise ValueError("Backup manifest checksum mismatch.")
        manifest = json.loads(Path(path).read_text())
        wanted = [f"{prefix}/{relative}" for relative in manifest["files"]]
    else:
        raise ValueError("This downloader requires a checksummed variable-period backup manifest.")
    # Exact file names include source bundles, launch commands, environment records and pending queues.
    snapshot_download(args.repo, repo_type="model", revision=revision, local_dir=args.output, allow_patterns=wanted)
    root = Path(args.output) / "runs" / args.run_id
    for relative, expected in manifest["files"].items():
        path = (root / relative).resolve()
        if root.resolve() not in path.parents or not path.is_file() or digest(path) != expected:
            raise ValueError(f"Missing/corrupt downloaded backup material: {relative}")
    resume = root / "checkpoints" / pointer["directory"] / "resume.pt"
    if digest(resume) != pointer["resume_sha256"]:
        raise ValueError("Downloaded resume checksum mismatch.")
    write_json(root / "RESTORE_REMOTE.json", pointer)
    print(f"[restore] completed_update={pointer['step']} resume={resume}", flush=True)


def eval_results(args):
    import tempfile
    import shutil
    import sys
    # Import the standalone state module, then restore the search path.
    _state_directory = str(Path(__file__).resolve().parents[2] / "src/fastwam/memory_s1")
    sys.path.insert(0, _state_directory)
    try:
        from eval_state import EpisodeQueue, durable_json, read, signature
    finally:
        sys.path.remove(_state_directory)
    root = Path(args.evaluation).resolve()
    queue = EpisodeQueue(root)
    value = queue.snapshot()
    completed = [job for job in value["jobs"] if job["state"] == "complete"]
    for job in completed:
        queue.result(job, value["identity"])
    # Serialize a restartable snapshot; live worker leases are never restored as live jobs.
    for job in value["jobs"]:
        if job["state"] != "complete":
            job["state"] = "pending"
            job.pop("owner", None)
    prefix = f"evaluations/{args.run_id}/{value['identity']}"
    api = HfApi()
    with tempfile.TemporaryDirectory(prefix="mwam-eval-upload-") as temporary:
        temporary = Path(temporary)
        durable_json(temporary / "queue.json", value)
        for name in ("evaluation.json", "scenes.json", "summary.json", "status.json"):
            if (root / name).exists():
                shutil.copy2(root / name, temporary / name)
        operations = []
        sent_path = root / "HF_EPISODES.json"
        sent = read(sent_path) if sent_path.exists() else {"identity": value["identity"], "jobs": []}
        if sent["identity"] != value["identity"]:
            raise ValueError("HF episode pointer identity mismatch.")
        if not sent.get("code_saved"):
            config = read(root / "evaluation.json")["config"]
            source_root = Path(config["root"])
            for subtree in ("src", "scripts/memory_s1", "configs", "requirements"):
                for path in (source_root / subtree).rglob("*"):
                    if path.is_file() and "__pycache__" not in path.parts and path.suffix in (".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt", ".md"):
                        relative = str(path.relative_to(source_root)).replace(os.sep, "/")
                        operations.append(CommitOperationAdd(path_in_repo=f"{prefix}/code/{relative}", path_or_fileobj=str(path)))
            operations.append(CommitOperationAdd(path_in_repo=f"{prefix}/code/pyproject.toml", path_or_fileobj=str(source_root / "pyproject.toml")))
            bundle = temporary / "source.bundle"
            subprocess.run(["git", "-C", str(source_root), "bundle", "create", str(bundle), "HEAD", "refs/heads/memory"], check=True)
            operations.append(CommitOperationAdd(path_in_repo=f"{prefix}/code/source.bundle", path_or_fileobj=str(bundle)))
            scene_contract = read(root / "scenes.json")["contract"]
            manifest_root = Path(config["paths"]["run"]) / "scene_manifests" / signature(scene_contract)[:16]
            for path in manifest_root.glob("*.json"):
                operations.append(CommitOperationAdd(path_in_repo=f"{prefix}/run_metadata/scene_manifests/{manifest_root.name}/{path.name}", path_or_fileobj=str(path)))
        for job in completed:
            if job["directory"] in sent["jobs"]:
                continue
            directory = root / job["directory"]
            for name in ("job.json", "result.json", "decisions.jsonl", "simulator.log", "complete.json"):
                path = directory / name
                if path.exists():
                    operations.append(CommitOperationAdd(path_in_repo=f"{prefix}/{job['directory']}/{name}", path_or_fileobj=str(path)))
        snapshots = [p for p in temporary.iterdir() if p.suffix == ".json"]
        estimated = sum(Path(operation.path_or_fileobj).stat().st_size for operation in operations) + sum(p.stat().st_size for p in snapshots)
        check_budget(api, estimated, args.quota_gib, args.reserve_gib)
        ensure_private(api, args.repo, "model")
        for start in range(0, len(operations), 50):
            api.create_commit(args.repo, repo_type="model", operations=operations[start:start+50], commit_message="Save immutable completed evaluation episodes")
        commit = api.create_commit(args.repo, repo_type="model", operations=[CommitOperationAdd(path_in_repo=f"{prefix}/{p.name}", path_or_fileobj=str(p)) for p in snapshots],
                                   commit_message=f"Publish evaluation resume snapshot ({len(completed)} complete)")
        durable_json(sent_path, {"identity": value["identity"], "jobs": [job["directory"] for job in completed], "revision": commit.oid, "prefix": prefix, "code_saved": True})
        print(f"[HF evaluation] completed={len(completed)} revision={commit.oid} prefix={prefix}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    quota = sub.add_parser("quota")
    quota.add_argument("--planned-bytes", type=int, default=0)
    cp = sub.add_parser("checkpoint")
    cp.add_argument("--repo", required=True)
    cp.add_argument("--run", required=True)
    cp.add_argument("--checkpoint", required=True)
    package = sub.add_parser("upload-package")
    package.add_argument("--repo", required=True)
    package.add_argument("--repo-type", choices=("model", "dataset"), required=True)
    package.add_argument("--directory", required=True)
    package.add_argument("--prefix", required=True)
    restore = sub.add_parser("download-resume")
    restore.add_argument("--repo", required=True)
    restore.add_argument("--run-id", required=True)
    restore.add_argument("--output", required=True)
    evaluation = sub.add_parser("eval-results")
    evaluation.add_argument("--repo", required=True)
    evaluation.add_argument("--evaluation", required=True)
    evaluation.add_argument("--run-id", required=True)
    for target in (quota, cp, package, evaluation):
        target.add_argument("--quota-gib", type=float, default=100_000_000_000 / 2**30)
        target.add_argument("--reserve-gib", type=float, default=10)
    args = parser.parse_args()
    if args.command == "quota":
        print(json.dumps(check_budget(HfApi(), args.planned_bytes, args.quota_gib, args.reserve_gib), indent=2))
    elif args.command == "checkpoint":
        checkpoint(args)
    elif args.command == "upload-package":
        upload_package(args)
    elif args.command == "eval-results":
        eval_results(args)
    else:
        download_resume(args)


if __name__ == "__main__":
    main()
