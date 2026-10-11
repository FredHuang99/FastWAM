"""One reviewed source transition, retaining immutable parent evidence."""
from __future__ import annotations

from pathlib import Path
import shutil
import importlib.metadata
import subprocess
import sys

from .common import atomic_json, fingerprint, read_json, sha256


def source_inventory(root):
    root = Path(root)
    paths = list((root / "src/fastwam/memory_s1").glob("*.py"))
    paths += [p for p in (root / "scripts/memory_s1").glob("*") if p.is_file() and p.suffix in (".py", ".sh")]
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(paths)}


def verify_parent(snapshot):
    snapshot = Path(snapshot)
    value = read_json(snapshot / "snapshot.json")
    for relative, expected in value["files"].items():
        path = (snapshot / relative).resolve()
        if not path.is_relative_to(snapshot.resolve()) or sha256(path) != expected:
            raise ValueError(f"Parent snapshot file changed: {relative}")
    admission = read_json(snapshot / "integration_admission.json")
    if admission.get("passed") is not True or admission["binding"] != value["binding"]:
        raise ValueError("Parent admission is not a verified six-stage admission.")
    sources = value["source_files"]
    for relative, expected in sources.items():
        if sha256(snapshot / "sources" / relative) != expected:
            raise ValueError(f"Parent source payload changed: {relative}")
    implementation = {Path(p).name: digest for p, digest in sources.items() if p.startswith("src/fastwam/memory_s1/")}
    support = {p: digest for p, digest in sources.items() if p.startswith("scripts/memory_s1/")}
    if fingerprint(implementation) != value["binding"]["implementation_sha"] or fingerprint(support) != value["binding"]["support_sha"]:
        raise ValueError("Frozen parent sources do not authenticate the admitted implementation.")
    for name, item in admission["reports"].items():
        path = snapshot / "integration_evidence" / item["file"]
        report = read_json(path)
        if sha256(path) != item["sha256"] or not report.get("passed") or report["binding"] != value["binding"]:
            raise ValueError(f"Parent evidence mismatch: {name}")
    return value


def verify_transition(cfg, snapshot):
    from .integration_contract import binding
    parent = verify_parent(snapshot)
    contract_path = Path(cfg["root"]) / "scripts/memory_s1/portable/phase_transition.json"
    contract = read_json(contract_path)
    before, after = parent["source_files"], source_inventory(cfg["root"])
    changes = contract["changes"]
    for name in set(before) | set(after) | set(changes):
        if before.get(name) == after.get(name):
            continue
        approved = changes.get(name)
        if approved != {"before": before.get(name), "after": after.get(name)}:
            raise ValueError(f"Unreviewed source difference: {name}. Parent evidence cannot be inherited.")
    now = binding(cfg)
    runtime = read_json(Path(snapshot) / "integration_evidence/runtime.json")
    import torch
    for name, expected in runtime["versions"].items():
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        if actual != expected:
            raise ValueError(f"Changed runtime dependency requires fresh evidence: {name}")
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=index,name,uuid,driver_version", "--format=csv,noheader"], text=True)
    if runtime["python"] != sys.version or runtime["torch_cuda"] != torch.version.cuda or runtime["nvidia"] != gpu:
        raise ValueError("GPU/driver/Python/CUDA changed; inherit only after fresh affected-stage checks.")
    if parent["cache_manifest_sha256"] != sha256(Path(cfg["paths"]["cache"]) / "manifest.json"):
        raise ValueError("The dense cache manifest changed after the admitted parent snapshot.")
    parent_data = read_json(Path(snapshot) / "integration_evidence/data.json")
    if parent_data["prior_review_sha"] != sha256(Path(cfg["paths"]["prepared"]) / "alignment_approved.json"):
        raise ValueError("The actual alignment approval differs from the inherited data evidence.")
    for key in ("cache_signature", "prepared_sha", "sources_sha", "core_sha", "simulator_source_sha", "inference", "numerics", "simulator_backend"):
        if now.get(key) != parent["binding"].get(key):
            raise ValueError(f"Changed dependency requires fresh evidence: {key}")
    return {"contract_sha256": sha256(contract_path), "parent_snapshot_sha256": sha256(Path(snapshot) / "snapshot.json"),
            "parent_binding": parent["binding"], "current_binding": now,
            "scope": "reviewed_phase_and_training_support_change; unchanged_visual_contract_and_execution_protocol"}


def verify_inherited(cfg, report):
    if report.get("evidence_origin") != "inherited":
        return
    run = Path(cfg["paths"]["run"])
    parent = run / "parent_provenance"
    proof = verify_transition(cfg, parent)
    origin = report["parent_report"]
    original = parent / "integration_evidence" / origin["file"]
    if proof != report["transition"] or sha256(original) != origin["sha256"]:
        raise ValueError("Inherited report provenance no longer matches the reviewed transition.")


def migrate(cfg, snapshot):
    from .integration_contract import output_root, binding
    snapshot = Path(snapshot).resolve()
    parent = verify_parent(snapshot)
    run, output = Path(cfg["paths"]["run"]), output_root(cfg)
    if (run / "LATEST_LOCAL.json").exists():
        raise ValueError("Cannot change an already-started training run.")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("sources.json", "reference_sources.tar.gz", "adapter_audit.json", "runtime.json"):
        source = snapshot / "integration_evidence" / name
        shutil.copy2(source, output / name)
    proof = verify_transition(cfg, snapshot)
    destination = run / "parent_provenance"
    if destination.exists():
        if sha256(destination / "snapshot.json") != sha256(snapshot / "snapshot.json"):
            raise ValueError("Another parent snapshot already occupies this run.")
    else:
        shutil.copytree(snapshot, destination)
    admission = read_json(snapshot / "integration_admission.json")
    for name in ("model", "execution", "data", "pilot", "cache"):
        atomic_json(output / f"{name}.json", {"version": parent["binding"]["version"], "passed": True,
            "binding": binding(cfg), "evidence_origin": "inherited", "parent_report": admission["reports"][name],
            "transition": proof, "note": "Original evidence is preserved, not relabeled as a fresh execution."})
    # Reuse the exact local reference tensors for the fresh gate-zero loss checks.
    old_model = Path(parent["integration_root"]) / "model"
    model = output / "model"
    model.mkdir(exist_ok=True)
    for relative, expected in parent["reference_tensors"].items():
        source = old_model / relative
        if not source.is_file() or sha256(source) != expected:
            raise ValueError(f"Missing reference tensor: {source}; rerun only the model stage before training preflight.")
        target = model / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            try:
                target.hardlink_to(source)
            except OSError:
                shutil.copy2(source, target)
        if sha256(target) != expected:
            raise ValueError(f"Reference tensor changed: {target}")
    atomic_json(output / "transition.json", proof)
    print("[inherit] model/execution/data/pilot/cache authenticated; fresh training preflight remains required.", flush=True)
