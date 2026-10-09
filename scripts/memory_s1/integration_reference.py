"""Pinned official FastWAM tracing in a process isolated from the S1 package."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import time


def checksum(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def cpu(value):
    import torch
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().clone()
    if isinstance(value, dict):
        return {key: cpu(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [cpu(item) for item in value]
    return value


def equal(a, b):
    import torch
    if isinstance(a, torch.Tensor):
        return isinstance(b, torch.Tensor) and a.dtype == b.dtype and torch.equal(a, b)
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(equal(a[key], b[key]) for key in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def load_policy(root, cfg):
    """Execute upstream factory and policy; replace only unused imports/local paths."""
    import torch
    from omegaconf import DictConfig, OmegaConf
    path = root / "experiments/robotwin/fastwam_policy/deploy_policy.py"
    spec = importlib.util.spec_from_file_location("pinned_official_policy", path)
    module = importlib.util.module_from_spec(spec)
    prompt_path = root / "src/fastwam/datasets/lerobot/robot_video_dataset.py"
    prompt_tree = ast.parse(prompt_path.read_text(encoding="utf-8"))
    prompts = [node for node in prompt_tree.body if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "DEFAULT_PROMPT" for t in node.targets)]
    if len(prompts) != 1:
        raise ValueError("The pinned prompt constant is ambiguous.")
    prompt = ast.literal_eval(prompts[0].value)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "fastwam.datasets.lerobot.robot_video_dataset":
            if [(a.name, a.asname) for a in node.names] != [("DEFAULT_PROMPT", None)]:
                raise ValueError("Unexpected upstream dataset import.")
            tree.body[i] = ast.copy_location(ast.Assign(
                targets=[ast.Name(id="DEFAULT_PROMPT", ctx=ast.Store())], value=ast.Constant(prompt)), node)
    exec(compile(ast.fix_missing_locations(tree), str(path), "exec"), module.__dict__)
    runtime = root / "src/fastwam/runtime.py"
    factory = [node for node in ast.parse(runtime.read_text(encoding="utf-8")).body
               if isinstance(node, ast.FunctionDef) and node.name == "create_fastwam"]
    if len(factory) != 1:
        raise ValueError("The pinned factory is ambiguous.")
    namespace = {"__name__": "fastwam.runtime", "__package__": "fastwam",
                 "torch": torch, "DictConfig": DictConfig, "OmegaConf": OmegaConf}
    exec(compile(ast.Module(body=factory, type_ignores=[]), str(runtime), "exec"), namespace)
    original_instantiate = module.instantiate
    def instantiate(config, **kwargs):
        if config.get("_target_") == "fastwam.runtime.create_fastwam":
            return namespace["create_fastwam"](
                **{key: value for key, value in config.items() if not key.startswith("_")}, **kwargs)
        return original_instantiate(config, **kwargs)
    module.instantiate = instantiate
    from fastwam.models.wan22.helpers import loader
    from fastwam.models.wan22.helpers.io import ModelConfig
    original_resolve = loader._resolve_configs
    original_load = torch.nn.Module.load_state_dict
    def resolve(**kwargs):
        dit, _, _, _ = original_resolve(**kwargs)
        return (dit, ModelConfig(path=cfg["paths"]["t5"]), ModelConfig(path=cfg["paths"]["vae"]),
                ModelConfig(path=cfg["paths"]["tokenizer"]))
    def strict_load(model, state_dict, strict=True, assign=False):
        return original_load(model, state_dict, strict=True, assign=assign)
    composed = module._compose_sim_cfg(None, "sim_robotwin.yaml", None)
    if not composed.model.get("skip_dit_load_from_pretrain", False):
        raise ValueError("Pinned config would download DiT weights; expected checkpoint-only loading.")
    loader._resolve_configs = resolve
    torch.nn.Module.load_state_dict = strict_load
    try:
        policy = module.WorldActionRobotWinPolicy(
            model_cfg=composed.model, processor_cfg=composed.data.train.processor,
            checkpoint_path=cfg["paths"]["base"], dataset_stats_path=Path(cfg["paths"]["stats"]),
            device="cuda:0", model_dtype=torch.bfloat16, action_horizon=32, replan_steps=16,
            num_inference_steps=10, sigma_shift=1.0, seed=17, text_cfg_scale=1.0,
            negative_prompt="", rand_device="cpu", tiled=False, timing_enabled=False, num_video_frames=1)
    finally:
        loader._resolve_configs = original_resolve
        torch.nn.Module.load_state_dict = original_load
    policy.model.eval().requires_grad_(False)
    return policy, prompt, {"deployment_sha": checksum(path), "factory_sha": checksum(runtime),
                            "prompt_sha": checksum(prompt_path), "released_execute": int(composed.EVALUATION.replan_steps),
                            "resolved_model": OmegaConf.to_container(composed.model, resolve=True),
                            "resolved_processor": OmegaConf.to_container(composed.data.train.processor, resolve=True),
                            "research_execute": 16, "predict": 32, "denoise_steps": 10}


def install_capture(policy, state):
    """Observe unchanged upstream calls, without substituting their returned tensors."""
    model = policy.model
    def watch(obj, name, handler):
        original = getattr(obj, name)
        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            handler(args, kwargs, result)
            return result
        setattr(obj, name, wrapped)
    watch(policy, "_build_robotwin_image_tensor", lambda a, k, r: state["trace"].update(mosaic=cpu(r)))
    watch(policy, "_normalize_state", lambda a, k, r: state["trace"].update(proprio=cpu(r)))
    watch(model, "encode_prompt", lambda a, k, r: state["trace"].update(text=cpu(r[0]), text_mask=cpu(r[1])))
    watch(model, "_encode_input_image_latents_tensor", lambda a, k, r: state["trace"].update(latent=cpu(r)))
    watch(model, "_append_proprio_to_context", lambda a, k, r: state["trace"].update(context=cpu(r[0]), context_mask=cpu(r[1])))
    def post(a, k, result):
        block = k.get("block", a[0] if a else None)
        if block is model.video_expert.blocks[-1]:
            state["trace"]["feature"] = cpu(result)
    watch(model.mot, "_apply_expert_post_block_tensor", post)
    watch(model.mot, "prefill_video_cache_tensor",
          lambda a, k, r: state["trace"].update(kv=cpu(r), video_mask=cpu(k.get("video_attention_mask", a[5] if len(a) > 5 else None))))
    def velocity(a, k, result):
        trace = state["trace"]
        trace.setdefault("velocity", []).append(cpu(result))
        trace.setdefault("noisy_actions", []).append(cpu(k.get("latents_action", a[0] if a else None)))
        trace.setdefault("timesteps", []).append(cpu(k.get("timestep_action", a[1] if len(a) > 1 else None)))
        trace["action_mask"] = cpu(k.get("action_attention_mask", a[6] if len(a) > 6 else None))
    watch(model, "_denoise_action_with_video_cache", velocity)
    watch(model, "infer_action", lambda a, k, r: state["trace"].update(normalized_actions=cpu(r["action"])))
    watch(policy, "_denormalize_action",
          lambda a, k, r: state["trace"].update(denormalized_actions=__import__("torch").from_numpy(r.copy())))


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--reference-root", required=True)
    parser.add_argument("--request", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.reference_root).resolve()
    # Resolve every fastwam import from the pinned checkout, never from the editable S1 installation.
    sys.path[:0] = [str(root / "src"), str(root)]
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    import torch
    request = torch.load(args.request, map_location="cpu", weights_only=True)
    cfg = request["config"]
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    math_backend = cfg["integration"]["attention_backend"] == "math"
    torch.backends.cuda.enable_flash_sdp(not math_backend)
    torch.backends.cuda.enable_mem_efficient_sdp(not math_backend)
    torch.backends.cuda.enable_math_sdp(True)
    policy, prompt, metadata = load_policy(root, cfg)
    imported = {name: str(Path(module.__file__).resolve()) for name, module in sys.modules.items()
                if name.startswith("fastwam") and getattr(module, "__file__", None)}
    if any(not Path(path).is_relative_to(root) for path in imported.values()):
        raise RuntimeError("Reference process imported FastWAM code outside the pinned checkout.")
    state = {"trace": {}}
    install_capture(policy, state)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    for slot, case in enumerate(request["cases"]):
        images = [image.numpy() for image in case["images"]]
        observation = {"observation": {name: {"rgb": image} for name, image in
                       zip(("head_camera", "left_camera", "right_camera"), images)},
                       "joint_action": {"vector": case["state"].numpy()}}
        traces = []
        for repetition in range(2):
            state["trace"] = {}
            policy.seed = int(case["noise_seed"])
            with torch.no_grad(), torch.autocast("cuda", enabled=False):
                denormalized = policy._infer_action_chunk(observation, case["instruction"])
            trace = state["trace"]
            noise = case["noise"].to(dtype=torch.bfloat16)
            if not torch.equal(noise, trace["noisy_actions"][0]):
                raise RuntimeError("Official sampled noise differs from the explicit fixture.")
            trace["noise"] = case["noise"].clone()
            trace["clipped_actions"] = torch.from_numpy(denormalized.copy())
            trace["clipped_actions"][:, [6, 13]] = trace["clipped_actions"][:, [6, 13]].clamp(0, 1)
            traces.append(trace)
        if not equal(traces[0], traces[1]):
            raise RuntimeError(f"Official reference is not deterministic: {case['case_id']}")
        trace = traces[0]
        # Ask the upstream action path to evaluate the S1 supervision input as well.
        action_key = policy.processor.shape_meta["action"][0]["key"]
        action_norm = policy.processor.normalizer.normalizers["action"][action_key]
        ground_truth = action_norm.forward(case["actions_raw"].clone()).to("cuda:0")
        tau = case["probe_tau"].to("cuda:0")
        scheduler = policy.model.train_action_scheduler
        timestep = 1000 * tau
        probe_noise = case["noise"].to("cuda:0")
        probe = scheduler.add_noise(ground_truth, probe_noise, timestep)
        target = scheduler.training_target(ground_truth, probe_noise, timestep)
        _, text_valid = policy.model.tokenizer(prompt.format(task=case["instruction"]),
                                              return_mask=True, add_special_tokens=True)
        trace["text_valid"] = text_valid.bool().cpu()
        trace["ground_truth"] = cpu(ground_truth)
        trace["probe_noisy"] = cpu(probe)
        trace["probe_target"] = cpu(target)
        with torch.no_grad(), torch.autocast("cuda", enabled=False):
            probe_velocity = policy.model._denoise_action_with_video_cache(
                probe.to(torch.bfloat16), (1000 * tau).to(torch.bfloat16),
                trace["context"].to("cuda:0"), trace["context_mask"].to("cuda:0"),
                [k.to("cuda:0") for k in trace["kv"][0]], [v.to("cuda:0") for v in trace["kv"][1]],
                trace["action_mask"].to("cuda:0"))
        trace["probe_velocity"] = cpu(probe_velocity)
        trace["probe_weight"] = cpu(scheduler.training_weight(1000 * tau))
        # The probe hook appends data to the active repeat; preserve the ten-step sampling trace.
        trace["velocity"] = trace["velocity"][:10]
        trace["noisy_actions"] = trace["noisy_actions"][:10]
        trace["timesteps"] = trace["timesteps"][:10]
        torch.save(trace, output / f"case_{slot:02d}.pt")
        elapsed = time.monotonic() - started
        print(f"[official] {slot+1}/12 exact_self_repeat=True elapsed={elapsed:.1f}s ETA={elapsed/(slot+1)*(12-slot-1):.1f}s", flush=True)
    metadata.update(passed=True, cases=len(request["cases"]), exact_self_repeat=True, imports=imported,
                    prompt=prompt, seconds=time.monotonic()-started, torch=torch.__version__,
                    cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(),
                    backend=cfg["integration"]["attention_backend"])
    (output / "summary.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
