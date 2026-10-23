"""Complete the partial RMBench copy on this machine from its saved source archives (add-only, never overwrites).

The A100's resources/RMBench is a file subset (earlier: missing CuRobo sources, scripts/requirements.txt,
data/decode_image_bit.py, env_cfg/task_config/demo_clean.yml). Instead of fixing one missing file per crash,
compare the checkout with every saved RMBench source archive (RMBench.source.tar.gz of the recovery ready packages,
simulator_sources.tar.gz of the integration evidence) and with the asset lock, then add every missing file.

    /opt/mwam/bin/python scripts/memory_v2/sim/rmbench_complete.py            # dry run: report only
    /opt/mwam/bin/python scripts/memory_v2/sim/rmbench_complete.py --apply    # add the missing files

Existing files are never modified; files that differ from an archive are only reported. Demo data (data/demo_*)
is out of scope (evaluation does not read it).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath

R = Path("/workspace/FastWAM/resources/RMBench")
SEARCH = ("/workspace/FastWAM/outputs", "/workspace/FastWAM/resources", "/migration", "/restore-tmp", "/root", "/workspace")
NAMES = {"RMBench.source.tar.gz", "simulator_sources.tar.gz", "download_lock.json"}
SKIP_DIRS = {"cache", "features_dense_v1", "checkpoints", "__pycache__", ".git", "demo_clean", "torch_extensions",
             "site-packages", "node_modules", "prepared_dense_h100_v1", "frames"}


def find_inputs(max_depth=7):
    found = set()
    for base in SEARCH:
        base = Path(base)
        if not base.is_dir():
            continue
        start = len(base.parts)
        for directory, subdirs, files in os.walk(base, followlinks=False):
            depth = len(Path(directory).parts) - start
            subdirs[:] = [d for d in subdirs if d not in SKIP_DIRS and depth < max_depth]
            for name in files:
                if name in NAMES:
                    found.add(Path(directory, name).resolve())
    return sorted(found)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def archive_members(path: Path):
    """relative RMBench path -> TarInfo, for the single RMBench root inside the archive."""
    with tarfile.open(path, "r:gz") as tar:
        members = [m for m in tar.getmembers() if m.isfile()]
    names = [m.name for m in members]
    prefixes = {n[:-len("envs/_base_task.py")] for n in names if n.endswith("envs/_base_task.py")}
    if len(prefixes) > 1:
        raise ValueError(f"{path}: several RMBench roots {sorted(prefixes)}")
    prefix = prefixes.pop() if prefixes else ""          # simulator_sources.tar.gz is stored relative to the root
    out = {}
    for m in members:
        if not m.name.startswith(prefix):
            continue
        rel = PurePosixPath(m.name[len(prefix):])
        if not rel.parts or rel.is_absolute() or ".." in rel.parts or "__pycache__" in rel.parts:
            continue
        if rel.parts[0] == "data" and len(rel.parts) > 1 and rel.parts[1].startswith("demo_"):
            continue
        out[str(rel)] = m
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="add the missing files (default: report only)")
    args = ap.parse_args()
    if not (R / "envs/_base_task.py").exists():
        raise SystemExit(f"{R} is not an RMBench checkout")
    inputs = find_inputs()
    print(f"== RMBench completeness  apply={args.apply}  checkout={R}")
    print("-- saved inputs found:")
    for p in inputs:
        print(f"   {p}  {p.stat().st_size / 2 ** 20:.1f} MiB")
    plan, differ, sources = {}, [], Counter()
    for path in inputs:
        if path.name == "download_lock.json":
            continue
        try:
            members = archive_members(path)
        except Exception as error:
            print(f"   skip {path}: {error!r}")
            continue
        print(f"-- {path.name} ({path.parent}): {len(members)} RMBench files")
        with tarfile.open(path, "r:gz") as tar:
            for rel, member in members.items():
                target = R / rel
                if target.is_file():
                    continue
                if rel not in plan:
                    data = tar.extractfile(member).read()
                    plan[rel] = (data, str(path))
                    sources[path.name] += 1
    for path in inputs:                                   # differing files: report only (first archive wins)
        if path.name == "download_lock.json":
            continue
        try:
            members = archive_members(path)
        except Exception:
            continue
        with tarfile.open(path, "r:gz") as tar:
            for rel, member in members.items():
                target = R / rel
                if target.is_file() and member.size == target.stat().st_size:
                    continue
                if target.is_file() and len(differ) < 200:
                    differ.append(f"{rel} (archive {member.size} B, checkout {target.stat().st_size} B)")
        break
    missing_assets = []
    for path in inputs:
        if path.name != "download_lock.json":
            continue
        try:
            files = json.loads(path.read_text()).get("files", {})
        except Exception:
            continue
        for name in files:
            name = name.replace("\\", "/")
            if name.startswith("resources/RMBench/assets/") and not (R / name.removeprefix("resources/RMBench/")).is_file():
                missing_assets.append(name)
    by_folder = Counter(PurePosixPath(rel).parts[0] for rel in plan)
    print(f"-- missing in the checkout and available in an archive: {len(plan)} files  {dict(by_folder)}")
    for rel in sorted(plan)[:60]:
        print(f"   + {rel}")
    if len(plan) > 60:
        print(f"   ... {len(plan) - 60} more")
    print(f"-- present but different size from the archive (NOT changed): {len(differ)}")
    for row in differ[:15]:
        print(f"   ~ {row}")
    print(f"-- assets listed in download locks but missing: {len(set(missing_assets))}")
    for name in sorted(set(missing_assets))[:15]:
        print(f"   ! {name}")
    if args.apply and plan:
        report = R.parent / f"RMBench_completed_{os.getpid()}.json"
        written = []
        for rel, (data, source) in sorted(plan.items()):
            target = R / rel
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.with_name(target.name + ".partial")
            tmp.write_bytes(data)
            tmp.replace(target)
            written.append({"file": rel, "sha256": sha(data), "source": source})
        report.write_text(json.dumps({"added": written, "note": "add-only; no existing file changed"}, indent=1))
        print(f"-- ADDED {len(written)} files; list with sources and sha256: {report}")
    elif plan:
        print("-- dry run: rerun with --apply to add them")
    print("-- checkout folders now:")
    for folder in ("assets/embodiments", "assets/objects", "env_cfg/task_config", "envs", "description"):
        p = R / folder
        print(f"   {folder:<22} {'exists' if p.exists() else 'MISSING'}  files={sum(1 for _ in p.rglob('*')) if p.exists() else 0}")
    archives = [p for p in inputs if p.name != "download_lock.json"]
    required = [R / "env_cfg/task_config/demo_clean.yml", R / "data/decode_image_bit.py", R / "scripts/eval_policy.py"]
    absent = [str(p) for p in required if not p.exists()]
    if not archives:
        print("-- no saved RMBench source archive was found on this machine")
    if absent:
        print(f"-- still missing required files: {absent}")
    ok = bool(archives) and not absent and not missing_assets and (args.apply or not plan)
    print("COMPLETE" if ok else "INCOMPLETE")


if __name__ == "__main__":
    main()
