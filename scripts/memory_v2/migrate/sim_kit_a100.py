"""A100 (11-07): the simulator kit for the 5090 workstation: what pip cannot reproduce from the fused env's freeze.

The 5090 (sm_120) needs torch >= 2.7 / CUDA 12.8 and its own builds of CuRobo and PyTorch3D; every other package is
installed there at the A100's exact version. What a plain install would miss is collected here:

  freeze.txt, conda_cuda.txt   pip freeze --all; conda CUDA / compiler packages (for the record)
  modified/<rel>               site-packages files whose sha256 differs from their distribution's RECORD (applied
                               patches, e.g. sapien / mplib), excluding the rebuilt stacks (torch, nvidia-*, triton,
                               CuRobo, PyTorch3D)
  unowned/<rel>                small text files (.py .pth .json .yaml .txt .cfg) in site-packages that no RECORD lists
  sources/<name>               the source trees the env's CuRobo / PyTorch3D wheels were built from (searched next to
                               the wheel the env was installed from, then in the RMBench checkout)
  KIT.json                     everything above with sha256, sizes and origins

Read-only for the environment and the sources (it only writes the kit folder). Run with the simulator python:
  /opt/rmbench-fused-env/bin/python scripts/memory_v2/migrate/sim_kit_a100.py [--out DIR]
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata as md
import json
import os
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path
from urllib.parse import unquote, urlparse

DEFAULT_OUT = "/workspace/FastWAM-memory2/outputs/migration_5090_v1/simkit"
REBUILT = ("torch", "torchvision", "torchaudio", "triton", "nvidia-curobo", "pytorch3d", "pip", "setuptools", "wheel")
REBUILT_PREFIX = ("nvidia-",)
REBUILT_DIRS = ("torch", "torchvision", "torchaudio", "triton", "nvidia", "curobo", "pytorch3d", "functorch", "torchgen",
                "pip", "setuptools", "_distutils_hack", "pkg_resources", "wheel")
TEXT = (".py", ".pth", ".json", ".yaml", ".yml", ".txt", ".cfg", ".toml")
SKIP_SOURCE = {"build", "dist", ".git", "__pycache__", ".eggs"}


def norm(name: str) -> str:
    return name.lower().replace("_", "-").replace(".", "-")


def rebuilt(dist_name: str) -> bool:
    n = norm(dist_name)
    return n in REBUILT or n.startswith(REBUILT_PREFIX)


def b64sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return base64.urlsafe_b64encode(h.digest()).rstrip(b"=").decode()


def hexsha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def copy_tree(src: Path, dst: Path) -> int:
    n = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_SOURCE and not d.endswith(".egg-info")]
        for name in files:
            if name.endswith((".so", ".o", ".pyc", ".whl")):
                continue
            p = Path(root) / name
            q = dst / p.relative_to(src)
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
            n += 1
    return n


def wheel_origin(dist_name: str):
    try:
        d = md.distribution(dist_name)
    except md.PackageNotFoundError:
        return None
    raw = d.read_text("direct_url.json")
    if not raw:
        return None
    url = json.loads(raw).get("url", "")
    return Path(unquote(urlparse(url).path)) if url.startswith("file://") else None


def find_source(marker: str, wheel, fallbacks):
    """A folder that contains `marker` (relative path) near the wheel the env was installed from, else a fallback."""
    tried = []
    if wheel is not None:
        for up in list(wheel.parents)[:8]:
            tried.append(str(up))
            if not up.is_dir():
                continue
            hits = sorted(up.glob(f"**/{marker}"))[:5]
            if hits:
                root = Path(str(hits[0])[: -len(marker)].rstrip("/"))
                return root, tried
    for f in fallbacks:
        tried.append(str(f))
        if (Path(f) / marker).exists():
            return Path(f), tried
    return None, tried


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--max-unowned-mb", type=float, default=200.0)
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    site = Path(sysconfig.get_paths()["purelib"])
    kit = {"python": sys.version.split()[0], "prefix": sys.prefix, "site_packages": str(site), "modified": [],
           "unowned": [], "unowned_skipped": 0, "sources": {}}
    (out / "freeze.txt").write_text(subprocess.run([sys.executable, "-m", "pip", "freeze", "--all"], capture_output=True,
                                                   text=True).stdout)
    conda = Path("/opt/miniforge/bin/conda")
    if conda.exists():
        listing = subprocess.run([str(conda), "list", "-p", sys.prefix], capture_output=True, text=True).stdout
        (out / "conda_cuda.txt").write_text("\n".join(l for l in listing.splitlines()
                                                      if any(k in l for k in ("cuda", "nvcc", "gcc", "gxx", "python "))))
    owned = set()
    checked = 0
    for dist in md.distributions():
        name = dist.metadata["Name"] or "?"
        files = dist.files or []
        for f in files:
            p = Path(dist.locate_file(f)).resolve() if not Path(str(f)).is_absolute() else Path(str(f))
            owned.add(str(p))
            if rebuilt(name) or f.hash is None or f.hash.mode != "sha256" or not p.is_file():
                continue
            checked += 1
            if b64sha(p) != f.hash.value:
                try:
                    rel = p.relative_to(site)
                except ValueError:
                    continue
                q = out / "modified" / rel
                q.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, q)
                kit["modified"].append({"dist": name, "version": dist.version, "file": str(rel),
                                        "sha256": hexsha(p), "size": p.stat().st_size})
    budget = args.max_unowned_mb * 1e6
    for root, dirs, files in os.walk(site):
        rel_root = Path(root).relative_to(site)
        if rel_root == Path("."):
            dirs[:] = [d for d in dirs if d not in REBUILT_DIRS and not d.endswith((".dist-info", ".egg-info"))]
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            p = (Path(root) / name).resolve()
            if str(p) in owned or not name.endswith(TEXT):
                continue
            size = p.stat().st_size
            if size > budget:
                kit["unowned_skipped"] += 1
                continue
            budget -= size
            rel = Path(root, name).relative_to(site)
            q = out / "unowned" / rel
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, q)
            kit["unowned"].append({"file": str(rel), "sha256": hexsha(p), "size": size})
    fw = Path("/workspace/FastWAM")
    for name, dist_name, marker, fallbacks in (
            ("curobo", "nvidia-curobo", "src/curobo/curobolib/cpp/lbfgs_step_cuda.cpp", [fw / "resources/RMBench/envs/curobo"]),
            ("pytorch3d", "pytorch3d", "pytorch3d/csrc/ext.cpp", [fw / "resources/PyTorch3D"])):
        wheel = wheel_origin(dist_name)
        src, tried = find_source(marker, wheel, fallbacks)
        try:
            version = md.version(dist_name)
        except md.PackageNotFoundError:
            version = None
        row = {"dist": dist_name, "wheel": str(wheel) if wheel else None, "searched": tried, "version": version}
        if src is not None:
            row["source"] = str(src)
            row["files"] = copy_tree(src, out / "sources" / name)
        else:
            row["source"] = None
        kit["sources"][name] = row
    kit["record_files_checked"] = checked
    (out / "KIT.json").write_text(json.dumps(kit, indent=1))
    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    print(f"[simkit] {out}: {len(kit['modified'])} modified files (of {checked} checked against RECORD), "
          f"{len(kit['unowned'])} unowned text files ({kit['unowned_skipped']} too large, skipped), total {total / 1e6:.1f} MB")
    for row in kit["modified"]:
        print(f"  modified  {row['dist']}=={row['version']}  {row['file']}")
    for name, row in kit["sources"].items():
        print(f"  source {name}: {row['source'] or 'NOT FOUND'} ({row.get('files', 0)} files); wheel {row['wheel']}")
    print(f"[simkit] unowned files (first 30 of {len(kit['unowned'])}):")
    for row in kit["unowned"][:30]:
        print(f"  unowned   {row['file']}")


if __name__ == "__main__":
    main()
