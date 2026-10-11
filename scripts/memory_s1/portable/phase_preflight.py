"""Freeze the still-admitted old checkout before pulling; migrate only reviewed changes."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys


def freeze(args):
    # This command deliberately works with the previous production source checkout.
    from fastwam.memory_s1.common import load_config, sha256, atomic_json
    from fastwam.memory_s1.integration_contract import binding, verify_admission, output_root
    cfg = load_config(args.config)
    bound = binding(cfg)
    verify_admission(cfg, bound["cache_signature"])
    root, run, target = Path(cfg["root"]), Path(cfg["paths"]["run"]), Path(args.output).resolve()
    if target.exists():
        raise ValueError(f"Parent snapshots are immutable; inspect the existing snapshot: {target}")
    temporary = target.with_name(target.name + f".{os.getpid()}.partial")
    temporary.mkdir(parents=True, exist_ok=False)
    shutil.copy2(run / "integration_admission.json", temporary / "integration_admission.json")
    shutil.copytree(run / "integration_evidence", temporary / "integration_evidence")
    paths = list((root / "src/fastwam/memory_s1").glob("*.py"))
    paths += [p for p in (root / "scripts/memory_s1").glob("*") if p.is_file() and p.suffix in (".py", ".sh")]
    source_files = {}
    for path in paths:
        relative = path.relative_to(root).as_posix()
        destination = temporary / "sources" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        source_files[relative] = sha256(path)
    atomic_json(temporary / "parent_config.json", cfg)
    model = output_root(cfg) / "model"
    tensors = [model / "request.pt", *sorted((model / "official").glob("case_*.pt"))]
    if len(tensors) != 13 or not all(p.is_file() for p in tensors):
        raise ValueError("Expected the existing 12 reference cases and request.pt; preserve them before updating.")
    files = {p.relative_to(temporary).as_posix(): sha256(p) for p in temporary.rglob("*") if p.is_file()}
    atomic_json(temporary / "snapshot.json", {"binding": bound, "source_files": source_files, "files": files,
        "cache_manifest_sha256": sha256(Path(cfg["paths"]["cache"]) / "manifest.json"),
        "integration_root": str(output_root(cfg)), "reference_tensors": {p.relative_to(model).as_posix(): sha256(p) for p in tensors}})
    os.replace(temporary, target)
    print(f"[parent] verified snapshot: {target}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("freeze", "migrate"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--output")
    parser.add_argument("--parent")
    args = parser.parse_args()
    root = Path(os.environ.get("FW_ROOT", "/workspace/FastWAM"))
    sys.path.insert(0, str(root / "src"))
    if args.command == "freeze":
        if not args.output:
            parser.error("freeze requires --output")
        freeze(args)
    else:
        from fastwam.memory_s1.common import load_config
        from fastwam.memory_s1.phase_transition import migrate
        if not args.parent:
            parser.error("migrate requires --parent")
        migrate(load_config(args.config), args.parent)


if __name__ == "__main__":
    main()
