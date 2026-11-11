"""Move a dense cache FOLDER between our machines through a private HF repo (plan v11, Opus checklist 2).

The machines cannot reach each other. relay.py moves a few flat files; a cache folder has one encodings.pt per
episode (same name in every sub-folder), so it needs its own tool that keeps the folder structure and checks every
byte on arrival. The HF token is read by huggingface_hub from the container's login; it is never printed or written.

  put DIR [--name NAME]          sha256 manifest of every file -> upload_folder(path_in_repo=NAME); the manifest
                                 NAME/RELAY_MANIFEST.json is uploaded LAST (its presence means the folder is complete)
  get --name NAME --dest PARENT  snapshot_download of NAME/* into PARENT/NAME, then `verify`
  verify DIR [--name NAME]       every manifest file present with the same size and sha256; cache markers consistent
                                 (CACHE.json present, one COMPLETE.json per episode in RECORDS.json)
  ls                             names of the folders whose manifest is on the repo
Exit code 0 only if the step fully succeeded. Run with a python that has huggingface_hub (5090: /opt/hf-tools/bin/python,
H200: /opt/mwam/bin/python).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

REPO = "hhyfred/memwam-caches"
MANIFEST = "RELAY_MANIFEST.json"


def sha256(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                return h.hexdigest()
            h.update(block)


def files_of(folder: Path):
    """Relative paths of every regular file under folder (no hidden HF cache folders, no manifest)."""
    out = []
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder)
        if p.is_file() and not any(part.startswith(".") for part in rel.parts) and rel.name != MANIFEST:
            out.append(rel.as_posix())
    return out


def build_manifest(folder: Path, name: str) -> dict:
    rows = {}
    for rel in files_of(folder):
        p = folder / rel
        rows[rel] = {"size": p.stat().st_size, "sha256": sha256(p)}
    return {"name": name, "files": rows, "total_bytes": sum(r["size"] for r in rows.values()),
            "created": time.strftime("%Y-%m-%d %H:%M:%S")}


def cache_markers(folder: Path) -> list:
    """Problems with the dense-cache markers (empty list = consistent). Folders that are not dense caches pass."""
    records = folder / "RECORDS.json"
    if not records.exists():
        return []
    problems = []
    if not (folder / "CACHE.json").exists():
        problems.append("CACHE.json missing (the build did not finish)")
    rows = json.loads(records.read_text(encoding="utf-8"))
    complete = len(list((folder / "cache").glob("*/COMPLETE.json")))
    if complete != len(rows):
        problems.append(f"COMPLETE.json in {complete} episode folders, RECORDS.json lists {len(rows)}")
    return problems


def verify(folder: Path, manifest: dict) -> list:
    problems = []
    for rel, want in manifest["files"].items():
        p = folder / rel
        if not p.is_file():
            problems.append(f"missing {rel}")
        elif p.stat().st_size != want["size"]:
            problems.append(f"size {rel}: {p.stat().st_size} != {want['size']}")
        elif sha256(p) != want["sha256"]:
            problems.append(f"sha256 {rel} differs")
    extra = sorted(set(files_of(folder)) - set(manifest["files"]))
    if extra:
        problems.append(f"{len(extra)} files not in the manifest, e.g. {extra[:3]}")
    return problems + cache_markers(folder)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("put", "get", "verify", "ls"))
    ap.add_argument("folder", nargs="?")
    ap.add_argument("--name", default="")
    ap.add_argument("--dest", default="")
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--tries", type=int, default=3)
    args = ap.parse_args()

    if args.cmd == "verify":
        folder = Path(args.folder)
        name = args.name or folder.name
        manifest = json.loads((folder / MANIFEST).read_text()) if (folder / MANIFEST).exists() else None
        if manifest is None:
            raise SystemExit(f"[cache] no {MANIFEST} in {folder}")
        problems = verify(folder, manifest)
        print(f"[cache] verify {name}: {'OK' if not problems else 'FAILED'}; {len(manifest['files'])} files, "
              f"{manifest['total_bytes'] / 2 ** 30:.2f} GiB", flush=True)
        for line in problems[:20]:
            print("   ", line)
        sys.exit(1 if problems else 0)

    from huggingface_hub import HfApi, snapshot_download
    api = HfApi()

    if args.cmd == "ls":
        names = sorted({Path(x.path).parts[0] for x in api.list_repo_tree(args.repo, repo_type="model", recursive=True)
                        if hasattr(x, "size") and Path(x.path).name == MANIFEST})
        print("\n".join(names))
        return

    if args.cmd == "put":
        folder = Path(args.folder).resolve()
        name = args.name or folder.name
        problems = cache_markers(folder)
        if problems:
            raise SystemExit(f"[cache] {name} is not a finished cache: {problems}")
        t0 = time.time()
        manifest = build_manifest(folder, name)
        print(f"[cache] {name}: manifest of {len(manifest['files'])} files, {manifest['total_bytes'] / 2 ** 30:.2f} GiB "
              f"({time.time() - t0:.0f} s)", flush=True)
        api.create_repo(args.repo, repo_type="model", private=True, exist_ok=True)
        for attempt in range(1, args.tries + 1):
            try:
                t0 = time.time()
                api.upload_folder(repo_id=args.repo, repo_type="model", folder_path=str(folder), path_in_repo=name,
                                  ignore_patterns=[".*", "*/.*", MANIFEST], commit_message=f"cache {name}")
                print(f"[cache] {name}: uploaded in {time.time() - t0:.0f} s (attempt {attempt})", flush=True)
                break
            except Exception as e:                       # noqa: BLE001 (network; retried, then reported)
                print(f"[cache] {name}: upload attempt {attempt} failed: {type(e).__name__}: {e}", flush=True)
                if attempt == args.tries:
                    raise SystemExit(1)
                time.sleep(60 * attempt)
        tmp = Path(f"/tmp/{name}_{MANIFEST}")
        tmp.write_text(json.dumps(manifest, indent=1) + "\n")
        api.upload_file(path_or_fileobj=str(tmp), path_in_repo=f"{name}/{MANIFEST}", repo_id=args.repo,
                        repo_type="model", commit_message=f"cache {name} manifest")
        print(f"[cache] PUT DONE {name} -> {args.repo}/{name}", flush=True)
        return

    # get
    if not args.name or not args.dest:
        raise SystemExit("get needs --name and --dest")
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, args.tries + 1):
        try:
            t0 = time.time()
            snapshot_download(args.repo, repo_type="model", allow_patterns=[f"{args.name}/*"], local_dir=str(dest))
            print(f"[cache] {args.name}: downloaded in {time.time() - t0:.0f} s (attempt {attempt})", flush=True)
            break
        except Exception as e:                           # noqa: BLE001
            print(f"[cache] {args.name}: download attempt {attempt} failed: {type(e).__name__}: {e}", flush=True)
            if attempt == args.tries:
                raise SystemExit(1)
            time.sleep(60 * attempt)
    folder = dest / args.name
    manifest = json.loads((folder / MANIFEST).read_text())
    problems = verify(folder, manifest)
    print(f"[cache] GET {'OK' if not problems else 'FAILED'} {args.name}: {len(manifest['files'])} files, "
          f"{manifest['total_bytes'] / 2 ** 30:.2f} GiB in {folder}", flush=True)
    for line in problems[:20]:
        print("   ", line)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
