"""Independent released-policy construction and complete-path comparisons."""
from __future__ import annotations

from contextlib import contextmanager
import ast
import importlib.util
from pathlib import Path
import time

import h5py
import numpy as np
import torch

from .common import ReleaseNormalizer, append_jsonl, atomic_json, fingerprint, read_json, seed_for, sha256
from .data import mosaic_rgb, official_decoder
from .base_compatibility import difference, kv_differences, kv_passed
from .protocol import format_task_prompt, precision_contract

PREPROCESSOR = "released_uint8_to_device_bf16_then_affine_v1"


def deployment_module(root):
    path = Path(root) / "experiments/robotwin/fastwam_policy/deploy_policy.py"
    spec = importlib.util.spec_from_file_location("independent_released_deployment", path)
    module = importlib.util.module_from_spec(spec)
    prompt_path = Path(root) / "src/fastwam/datasets/lerobot/robot_video_dataset.py"
    prompt_tree = ast.parse(prompt_path.read_text(encoding="utf-8"))
    assignments = [node for node in prompt_tree.body if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "DEFAULT_PROMPT" for target in node.targets)]
    if len(assignments) != 1:
        raise ValueError("The released prompt constant cannot be independently resolved.")
    prompt = ast.literal_eval(assignments[0].value)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for index, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "fastwam.datasets.lerobot.robot_video_dataset":
            if [(item.name, item.asname) for item in node.names] != [("DEFAULT_PROMPT", None)]:
                raise ValueError("The released deployment's dataset import changed; review it explicitly.")
            tree.body[index] = ast.copy_location(ast.Assign(targets=[ast.Name(id="DEFAULT_PROMPT", ctx=ast.Store())], value=ast.Constant(prompt)), node)
    exec(compile(ast.fix_missing_locations(tree), str(path), "exec"), module.__dict__)
    # Execute the unchanged released factory function without importing its unused trainer.
    from omegaconf import DictConfig, OmegaConf
    runtime_path = Path(root) / "src/fastwam/runtime.py"
    runtime_tree = ast.parse(runtime_path.read_text(encoding="utf-8"))
    factories = [node for node in runtime_tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_fastwam"]
    if len(factories) != 1:
        raise ValueError("The released create_fastwam factory cannot be resolved.")
    namespace = {"__name__": "fastwam.runtime", "__package__": "fastwam", "torch": torch,
        "DictConfig": DictConfig, "OmegaConf": OmegaConf}
    exec(compile(ast.Module(body=factories, type_ignores=[]), str(runtime_path), "exec"), namespace)
    original_instantiate = module.instantiate
    def instantiate(config, **kwargs):
        if str(config.get("_target_", "")) == "fastwam.runtime.create_fastwam":
            arguments = {key: value for key, value in config.items() if not key.startswith("_")}
            return namespace["create_fastwam"](**arguments, **kwargs)
        return original_instantiate(config, **kwargs)
    module.instantiate = instantiate
    module._rootcause_adapter = {"deployment_sha256": sha256(path), "factory_source_sha256": sha256(runtime_path),
        "prompt_source_sha256": sha256(prompt_path), "prompt": prompt,
        "scope": "Only unused training/dataset imports bypassed; original factory, processor and policy functions executed."}
    return module


@contextmanager
def local_components(cfg):
    from fastwam.models.wan22.helpers import loader
    from fastwam.models.wan22.helpers.io import ModelConfig
    original = loader._resolve_configs
    original_load = torch.nn.Module.load_state_dict
    paths = cfg["paths"]
    for key in ("base", "stats", "vae", "t5", "tokenizer"):
        if not Path(paths[key]).exists():
            raise FileNotFoundError(f"Missing local {key}: {paths[key]}; automatic downloads are disabled.")
    def resolve(**kwargs):
        dit, _, _, _ = original(**kwargs)
        return (dit, ModelConfig(path=paths["t5"]), ModelConfig(path=paths["vae"]),
                ModelConfig(path=paths["tokenizer"]))
    loader._resolve_configs = resolve
    def strict_load(module, state_dict, strict=True, assign=False):
        return original_load(module, state_dict, strict=True, assign=assign)
    torch.nn.Module.load_state_dict = strict_load
    try:
        yield
    finally:
        loader._resolve_configs = original
        torch.nn.Module.load_state_dict = original_load


def load_released_policy(cfg, device="cuda:0"):
    """Instantiate the original Hydra factory and processor without sharing S1 modules."""
    module = deployment_module(cfg["root"])
    composed = module._compose_sim_cfg(None, "sim_robotwin.yaml", None)
    with local_components(cfg):
        policy = module.WorldActionRobotWinPolicy(
            model_cfg=composed.model, processor_cfg=composed.data.train.processor,
            checkpoint_path=cfg["paths"]["base"], dataset_stats_path=Path(cfg["paths"]["stats"]),
            device=device, model_dtype=torch.bfloat16, action_horizon=32, replan_steps=16,
            num_inference_steps=10, sigma_shift=1.0, seed=cfg["seed"], text_cfg_scale=1.0,
            negative_prompt="", rand_device="cpu", tiled=False, timing_enabled=True,
            num_video_frames=1)
    # The released loader uses strict=False for MoT; reject omissions explicitly here.
    payload = torch.load(cfg["paths"]["base"], map_location="cpu", weights_only=True, mmap=True)
    if not {"mot", "proprio_encoder"} <= payload.keys():
        raise ValueError("The base must contain both complete MoT and proprio_encoder weights.")
    policy.model.mot.load_state_dict(payload["mot"], strict=True)
    policy.model.proprio_encoder.load_state_dict(payload["proprio_encoder"], strict=True)
    del payload
    policy.model.eval().requires_grad_(False)
    from omegaconf import OmegaConf
    policy._rootcause_load = {"independent": True, "factory": str(composed.model._target_),
        "import_adapter": module._rootcause_adapter,
        "strict_mot": True, "strict_proprio": True, "model_paths": policy.model.model_paths,
        "strict_encoder_loading": True, "model_config": OmegaConf.to_container(composed.model, resolve=True),
        "processor_config": OmegaConf.to_container(composed.data.train.processor, resolve=True),
        "preprocessor": PREPROCESSOR, "released_execute": int(composed.EVALUATION.replan_steps)}
    return policy


def current_observation(images, state):
    return {"observation": {name: {"rgb": image} for name, image in
            zip(("head_camera", "left_camera", "right_camera"), images)},
            "joint_action": {"vector": np.asarray(state, dtype=np.float32)}}


def aligned_mosaic(images, device):
    """Implement the released arithmetic independently of its deployment processor."""
    from PIL import Image
    parts = [np.asarray(Image.fromarray(image).resize(size, Image.Resampling.BILINEAR))
             for image, size in zip(images, ((320, 256), (160, 128), (160, 128)))]
    rgb = np.concatenate((parts[0], np.concatenate(parts[1:], axis=1)), axis=0).copy()
    return torch.from_numpy(rgb).permute(2, 0, 1)[None].to(device, torch.bfloat16) * (2.0 / 255.0) - 1.0


@torch.no_grad()
@torch.autocast("cuda", enabled=False)
def compare_case(model, policy, encoders, images, state, instruction, noise_seed):
    from .model import encode_latent, encode_text
    reference = policy.model
    device = reference.device
    native_mosaic = policy._build_robotwin_image_tensor(current_observation(images, state))
    custom_mosaic = aligned_mosaic(images, device)
    legacy_mosaic = mosaic_rgb(images)[None].to(device, torch.bfloat16)
    normalizer = ReleaseNormalizer(policy._rootcause_config["paths"]["stats"])
    proprio = normalizer.normalize(torch.as_tensor(state, device=device)[None], "state")
    native_proprio = policy._normalize_state(np.asarray(state, dtype=np.float32)).to(device)
    vae, text_encoder, tokenizer = encoders
    text, valid = encode_text(text_encoder, tokenizer, instruction, device)
    native_text, native_mask = reference.encode_prompt(format_task_prompt(instruction))
    latent = encode_latent(vae, custom_mosaic)
    native_latent = reference._encode_input_image_latents_tensor(native_mosaic, tiled=False)
    legacy_latent = encode_latent(vae, legacy_mosaic)
    _, kv, context = model.backbone.encode_observation(latent, text, proprio)
    native_context = reference._append_proprio_to_context(native_text, native_mask, native_proprio)
    expert = reference.video_expert
    prepared = expert.prepare(x=native_latent, timestep=torch.zeros(1, device=device, dtype=torch.bfloat16),
        context=native_context[0], context_mask=native_context[1], action=None,
        fuse_vae_embedding_in_latents=expert.fuse_vae_embedding_in_latents)
    tokens, _, modulation, ctx, ctx_mask, freqs, _, _, _, per_frame = prepared
    mask = reference._build_mot_attention_mask(tokens.shape[1], 32, per_frame, device)
    native_k, native_v = reference.mot.prefill_video_cache_tensor(
        tokens, freqs, modulation, ctx, ctx_mask, mask[:tokens.shape[1], :tokens.shape[1]])
    noise = torch.randn(1, 32, 14, generator=torch.Generator(device="cpu").manual_seed(noise_seed)).to(device)
    actions = noise.to(torch.bfloat16).clone()
    timesteps, deltas = reference.infer_action_scheduler.build_inference_schedule(10, device, actions.dtype, shift_override=1.0)
    trace = []
    for step, (timestep, delta) in enumerate(zip(timesteps, deltas)):
        velocity = reference._denoise_action_with_video_cache(
            actions, timestep[None], native_context[0], native_context[1], native_k, native_v, mask[tokens.shape[1]:])
        custom = model.backbone.action_velocity(actions, timestep[None], context, kv, model.memory, None, 0.0)
        trace.append({"step": step, "timestep": float(timestep), **difference(custom, velocity)})
        actions = reference.infer_action_scheduler.step(velocity, delta, actions)
    custom, _ = model.sample({}, noise, gate_scale=0.0, prepared_conditions=(kv, context, None))
    native = reference.infer_action(input_image=native_mosaic, proprio=native_proprio,
        prompt=format_task_prompt(instruction), action_horizon=32, num_inference_steps=10,
        sigma_shift=1.0, seed=noise_seed, rand_device="cpu", tiled=False, compile_action_infer=False)["action"]
    if native.ndim == 2:
        native = native[None]
    denorm = normalizer.denormalize(custom).cpu()
    native_denorm = torch.as_tensor(policy._denormalize_action(native))
    clipped, native_clipped = denorm.clone(), native_denorm.clone()
    clipped[..., [6, 13]] = clipped[..., [6, 13]].clamp(0, 1)
    native_clipped[..., [6, 13]] = native_clipped[..., [6, 13]].clamp(0, 1)
    report = {"mosaic": difference(custom_mosaic, native_mosaic, 0, 0),
        "proprio": difference(proprio, native_proprio, 0, 0), "text": difference(text, native_text, 0, 0),
        "latent": difference(latent, native_latent, 0, 0), "context": difference(context[0], native_context[0], 0, 0),
        "kv_layers": kv_differences(kv, (native_k, native_v)), "velocity_trace": trace,
        "normalized_actions": difference(custom, native), "denormalized_actions": difference(denorm, native_denorm),
        "clipped_actions": difference(clipped, native_clipped),
        "legacy_preprocessing": {"mosaic": difference(legacy_mosaic, native_mosaic, 0, 0),
            "latent": difference(legacy_latent, native_latent, 0, 0)},
        "noise_seed": noise_seed, "native_actions": native[0].float().cpu().tolist()}
    checks = {name: report[name]["allclose"] for name in
        ("mosaic", "proprio", "text", "latent", "context", "normalized_actions", "denormalized_actions", "clipped_actions")}
    checks.update(kv=kv_passed(report["kv_layers"]), velocity=all(row["allclose"] for row in trace))
    ordered_checks = ("mosaic", "proprio", "text", "latent", "context", "kv", "velocity",
                      "normalized_actions", "denormalized_actions", "clipped_actions")
    report.update(checks=checks, passed=all(checks.values()),
        first_divergence=next((key for key in ordered_checks if not checks[key]), None))
    return report


def independent_comparison(cfg, output, stop_root=None):
    from .eval_state import check_stop
    from .common import code_version
    from .model import S1Model, load_observation_encoders
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    approval = read_json(Path(cfg["paths"]["prepared"]) / "alignment_approved.json")
    if approval.get("approved") is not True or approval.get("manifest_sha") != fingerprint(manifest):
        raise ValueError("Prepared data alignment approval does not match its manifest.")
    records = []
    for task in ("put_back_block", "swap_blocks"):
        candidates = sorted((r for r in manifest["episodes"] if r["task"] == task and r["split"] == "val"), key=lambda r: r["episode_id"])
        if len(candidates) < 2:
            raise ValueError(f"Need two validation episodes: {task}")
        records.extend(candidates[:2])
    print("[D1] loading separate released and S1 models; all resources local", flush=True)
    policy = load_released_policy(cfg)
    policy._rootcause_config = cfg
    model = S1Model(cfg, torch.device("cuda:0")).eval()
    encoders = load_observation_encoders(cfg, torch.device("cuda:0"))
    native_pointers = {p.data_ptr() for p in policy.model.parameters()}
    if any(p.data_ptr() in native_pointers for p in model.parameters()) or any(
            p.data_ptr() in native_pointers for module in encoders[:2] for p in module.parameters()):
        raise RuntimeError("Independent branches unexpectedly share parameter storage.")
    decoder = official_decoder(Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"])
    rows, started = [], time.monotonic()
    cases_path = output / "cases.jsonl"
    if cases_path.exists():
        cases_path.rename(output / f"interrupted_cases_{time.time_ns()}.jsonl")
    for record in records:
        raw = Path(cfg["root"]) / record["raw"]
        if sha256(raw) != record["raw_sha256"]:
            raise ValueError(f"Raw episode checksum changed: {raw}")
        episode = torch.load(Path(cfg["paths"]["prepared"]) / record["file"], map_location="cpu", weights_only=True)
        with h5py.File(raw, "r") as file:
            for index in (0, 64, 128):
                check_stop(stop_root)
                if index >= record["length"]:
                    raise ValueError("The required 12-case bank has a missing anchor.")
                images = [decoder(file[key][index]) for key in record["camera_paths"]]
                row = compare_case(model, policy, encoders, images, episode["states"][index].numpy(),
                    record["instruction"], seed_for(cfg["seed"], index, len(rows), "base-compatibility-noise"))
                row.update(task=record["task"], episode_id=record["episode_id"], frame_id=index)
                append_jsonl(cases_path, row)
                rows.append(row)
                eta = (time.monotonic() - started) / len(rows) * (12 - len(rows))
                print(f"[D1] {len(rows)}/12 passed={row['passed']} first={row['first_divergence']} ETA={eta:.1f}s", flush=True)
    report = {"complete": True, "passed": all(r["passed"] for r in rows), "cases": len(rows),
        "load": policy._rootcause_load, "precision": precision_contract(), "code": code_version(cfg["root"]),
        "resources": {key: sha256(cfg["paths"][key]) for key in ("base", "stats", "vae", "t5")},
        "failed_cases": [{k: r[k] for k in ("episode_id", "frame_id", "first_divergence")} for r in rows if not r["passed"]],
        "seconds": time.monotonic() - started,
        "scope": "Independent official model/processor versus gate-zero S1, using released-aligned preprocessing. No admission approval or cache migration."}
    atomic_json(output / "summary.json", report)
    return report
