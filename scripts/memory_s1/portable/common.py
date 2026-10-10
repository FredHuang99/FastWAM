"""Portable snapshot primitives; no training or Hub imports."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import time

SCHEMA = "fastwam-s1-ready-v1"
RUNTIME_NAMES = {"STOP_REQUESTED", "STOP.json", "launcher.json", "launcher.pid", "latest_log.txt"}
EXCLUDED_PARTS = {".git", ".cache", "__pycache__", "packages", ".ssh", ".aws", ".venv", "node_modules"}


def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024**2), b""):
            value.update(block)
    return value.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def command(argv, cwd=None):
    result = subprocess.run([str(a) for a in argv], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def safe_relative(name):
    p = PurePosixPath(name)
    if not name or p.is_absolute() or ".." in p.parts or ":" in name or "\\" in name:
        raise ValueError(f"Unsafe archive path: {name}")
    return p


def eligible(path):
    p = Path(path)
    parts = {s.lower() for s in p.parts}
    name = p.name.lower()
    return not (parts & EXCLUDED_PARTS or p.name in RUNTIME_NAMES or p.suffix in (".sock", ".tmp", ".pid")
                or name in {"token", "stored_tokens", ".netrc", ".git-credentials", "credentials", "id_rsa", "id_ed25519"}
                or name.endswith((".pem", ".key")) or name.startswith(".env"))


def inventory(paths, root):
    root = Path(root).absolute()
    rows = {}
    for item in paths:
        item = Path(item).absolute()
        if not item.exists():
            raise FileNotFoundError(item)
        candidates = [item] if item.is_file() else sorted(item.rglob("*"))
        for path in candidates:
            if path.is_file() and eligible(path.relative_to(root)):
                name = path.relative_to(root).as_posix()
                rows[name] = {"bytes": path.stat().st_size, "sha256": digest(path)}
    return dict(sorted(rows.items()))


def verify_files(root, files):
    root = Path(root)
    for index, (name, info) in enumerate(files.items(), 1):
        path = root / str(safe_relative(name))
        if not path.is_file() or path.stat().st_size != info["bytes"] or digest(path) != info["sha256"]:
            raise ValueError(f"Missing or changed file: {path}")
        if index % 100 == 0:
            print(f"[verify] {index}/{len(files)}", flush=True)


def copy_files(root, destination, files):
    for name in files:
        target = Path(destination) / str(safe_relative(name))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(root) / name, target, follow_symlinks=True)


def extract(stream, destination, expected=None):
    destination = Path(destination).resolve()
    for member in stream:
        name = str(safe_relative(member.name))
        if not member.isfile() or (expected is not None and name not in expected):
            raise ValueError(f"Unexpected/nonregular archive entry: {name}")
        target = destination / name
        if not target.resolve().is_relative_to(destination):
            raise ValueError(f"Archive escaped destination: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        source = stream.extractfile(member)
        temporary = target.with_name(target.name + ".restoring")
        with source, temporary.open("wb") as output:
            shutil.copyfileobj(source, output, 8 * 1024**2)
        os.chmod(temporary, member.mode & 0o777)
        temporary.replace(target)


class ProgressFile:
    """Hash source bytes while tar reads them and emit measured byte-based ETA."""
    def __init__(self, path, expected, progress):
        self.file = open(path, "rb")
        self.expected, self.progress = expected, progress
        self.sha = hashlib.sha256()
        self.count = 0

    def read(self, size=-1):
        block = self.file.read(size)
        self.sha.update(block)
        self.count += len(block)
        self.progress["done"] += len(block)
        now = time.monotonic()
        if now - self.progress["last"] >= 10:
            elapsed = now - self.progress["start"]
            rate = self.progress["done"] / max(elapsed, 0.001)
            remaining = (self.progress["total"] - self.progress["done"]) / max(rate, 1)
            print(f"[pack] {self.progress['done']/2**30:.2f}/{self.progress['total']/2**30:.2f} GiB "
                  f"rate={rate/2**20:.1f} MiB/s ETA={remaining/60:.1f} min", flush=True)
            self.progress["last"] = now
        return block

    def close(self):
        self.file.close()
        if self.count != self.expected["bytes"] or self.sha.hexdigest() != self.expected["sha256"]:
            raise ValueError("Source changed after snapshot inventory; discard the incomplete package.")


def add_verified(archive, root, files):
    progress = {"done": 0, "total": sum(r["bytes"] for r in files.values()), "start": time.monotonic(), "last": 0}
    for name, info in files.items():
        path = Path(root) / name
        entry = tarfile.TarInfo(name)
        entry.size, entry.mode = info["bytes"], path.stat().st_mode & 0o777
        reader = ProgressFile(path, info, progress)
        try:
            archive.addfile(entry, reader)
        finally:
            reader.close()


def load_snapshot(directory):
    directory = Path(directory).resolve()
    manifest = read(directory / "snapshot.json")
    if manifest.get("schema") != SCHEMA or manifest.get("phase") != "admitted_not_started":
        raise ValueError("This is not a complete pre-training ready snapshot.")
    return directory, manifest
