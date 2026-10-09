"""Identity-bound integration evidence; policy success is not an admission criterion."""
from __future__ import annotations

from pathlib import Path

from .common import code_version, fingerprint, make_cache_contract, read_json, sha256
from .protocol import inference_contract

FASTWAM_COMMIT = "7faa71108368fbb3b6885649f112af607427a2d4"
RMBENCH_COMMIT = "4955514916dce325e1e2a90f03b60e1ea6504829"
VERSION = "fastwam-rmbench-integration-v2"
REQUIRED = ("model", "execution", "data", "pilot", "cache", "training")


def numerics(cfg):
    return {"attention_backend": cfg.get("integration", {}).get("attention_backend", "math"),
            "tf32": False, "deterministic": True, "cublas_workspace": ":4096:8"}


def configure_numerics(cfg):
    import os
    import torch
    contract = numerics(cfg)
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", contract["cublas_workspace"])
    if os.environ["CUBLAS_WORKSPACE_CONFIG"] != contract["cublas_workspace"]:
        raise ValueError("CUBLAS_WORKSPACE_CONFIG differs from the integration contract.")
    if contract["attention_backend"] not in ("math", "auto"):
        raise ValueError("Unsupported integration attention backend.")
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    math_backend = contract["attention_backend"] == "math"
    torch.backends.cuda.enable_flash_sdp(not math_backend)
    torch.backends.cuda.enable_mem_efficient_sdp(not math_backend)
    torch.backends.cuda.enable_math_sdp(True)
    return contract


def output_root(cfg):
    return (Path(cfg["root"]) / cfg["integration"]["output"]).resolve()


def simulator_sources(cfg):
    root = (Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]).resolve()
    folders = ("envs", "scripts", "script", "env_cfg", "task_config", "description", "data", "assets")
    return fingerprint({str(p.relative_to(root)): sha256(p) for folder in folders
                        for p in sorted((root / folder).rglob("*"))
                        if p.is_file() and p.suffix.lower() in (".py", ".json", ".yaml", ".yml", ".urdf", ".srdf", ".stl", ".obj", ".glb", ".dae")
                        and "__pycache__" not in p.parts})


def binding(cfg):
    manifest = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    lock_path = output_root(cfg) / "sources.json"
    if not lock_path.is_file():
        lock_path = Path(cfg["paths"]["run"]) / "integration_evidence/sources.json"
    lock = read_json(lock_path)
    # Hash checkout content, so a stale Git HEAD cannot approve modified upstream files.
    for info in lock["repositories"].values():
        root = Path(cfg["root"]) / info["path"]
        for relative, expected in info["files"].items():
            if sha256(root / relative) != expected:
                raise ValueError(f"Pinned reference source changed: {relative}")
    code = code_version(cfg["root"])
    contract = make_cache_contract(cfg, manifest)
    return {"version": VERSION, "cache_signature": fingerprint(contract),
            "prepared_sha": fingerprint(manifest), "sources_sha": fingerprint(lock),
            "core_sha": code["core_sha"], "implementation_sha": code["implementation_sha"],
            "support_sha": code["support_sha"], "simulator_source_sha": simulator_sources(cfg),
            "inference": inference_contract(), "numerics": numerics(cfg)}


def verify_admission(cfg, cache_signature):
    path = Path(cfg["paths"]["run"]) / "integration_admission.json"
    value = read_json(path)
    expected = binding(cfg)
    if value.get("version") != VERSION or value.get("passed") is not True:
        raise ValueError("Integration admission has not passed; legacy base admission is not sufficient.")
    if value.get("binding") != expected or cache_signature != expected["cache_signature"]:
        raise ValueError("Integration admission no longer matches source, resources, data or cache.")
    evidence = Path(cfg["paths"]["run"]) / "integration_evidence"
    for name in REQUIRED:
        info = value["reports"].get(name)
        if not info or sha256(evidence / info["file"]) != info["sha256"]:
            raise ValueError(f"Missing or changed integration evidence: {name}")
        report = read_json(evidence / info["file"])
        if report.get("passed") is not True or report.get("binding") != expected:
            raise ValueError(f"Unapproved integration evidence: {name}")
    return value


def exact_difference(actual, expected):
    import torch
    if actual.shape != expected.shape:
        return {"exact": False, "actual_shape": list(actual.shape), "expected_shape": list(expected.shape)}
    a, b = actual.detach().cpu(), expected.detach().cpu()
    finite = bool(torch.isfinite(a).all() and torch.isfinite(b).all())
    delta = (a.float() - b.float()).abs()
    return {"exact": finite and a.dtype == b.dtype and torch.equal(a, b),
            "actual_dtype": str(a.dtype), "expected_dtype": str(b.dtype),
            "shape": list(a.shape), "mae": float(delta.mean()),
            "maximum_abs": float(delta.max()), "finite": finite}
