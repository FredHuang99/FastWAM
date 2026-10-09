"""Freeze official feasible scenes, or execute one frozen policy episode."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import random
import sys
import time
import traceback

# Simulator Python imports only the standard-library state module.
# Import the standalone state module, then restore the search path.
_state_directory = str(Path(__file__).resolve().parents[2] / "src/fastwam/memory_s1")
sys.path.insert(0, _state_directory)
try:
    from eval_state import EvaluationInterrupted, check_stop, cuda_gpu_uuid, durable_json, read, signature
finally:
    sys.path.remove(_state_directory)


def verify_gpu(expected, scene):
    if not expected:
        return {}
    import torch
    import pynvml
    torch.empty(1, device="cuda:0")
    cuda_uuid = cuda_gpu_uuid(0)
    render_device = scene.render_system.device
    pci = getattr(render_device, "pci_string", None)
    pynvml.nvmlInit()
    try:
        if pci:
            render_uuid = pynvml.nvmlDeviceGetUUID(pynvml.nvmlDeviceGetHandleByPciBusId(pci.encode()))
            if isinstance(render_uuid, bytes):
                render_uuid = render_uuid.decode()
        else:
            identifier = getattr(render_device, "cuda_id", None)
            if identifier is None or identifier < 0:
                raise RuntimeError("SAPIEN did not expose a verifiable render device; inspect its installed API.")
            render_uuid = cuda_gpu_uuid(identifier)
    finally:
        pynvml.nvmlShutdown()
    if cuda_uuid != expected or render_uuid != expected:
        raise RuntimeError(f"Simulator/Vulkan GPU mismatch: expected={expected}, CUDA={cuda_uuid}, renderer={render_uuid}")
    return {"expected_gpu_uuid": expected, "cuda_gpu_uuid": cuda_uuid, "render_gpu_uuid": render_uuid, "pid": os.getpid()}


def load_official():
    root = Path.cwd()
    sys.path[:0] = [str(root), str(root / "policy"), str(root / "description/utils"), str(Path(__file__).parent)]
    specification = importlib.util.spec_from_file_location("official_rmbench_eval", root / "scripts/eval_policy.py")
    official = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(official)
    import sapien
    # The v3 compatibility SapienRenderer wrapper can ignore device kwargs.
    # Initialize the render context explicitly and select it in every scene.
    selected_render_system = sapien.render.RenderSystem(device="cuda:0")
    engine = sapien.Engine
    def selected_scene(self, config=None):
        if config is not None:
            sapien.physx.set_scene_config(config)
        return sapien.Scene([sapien.physx.PhysxCpuSystem(), sapien.render.RenderSystem(device="cuda:0")])
    engine.create_scene = selected_scene
    official._memory_render_context = selected_render_system
    return official


def plan_scenes(args, official):
    path = Path(args.output)
    contract = read(args.contract)
    if path.exists():
        saved = read(path)
        if saved["contract"] != contract:
            raise ValueError("Scene manifest contract changed; use a new manifest path.")
        if saved["complete"]:
            return
    else:
        saved = {"contract": contract, "scenes": [], "next_seed": 100000 * (1 + args.seed), "complete": False}
    official.eval_function_decorator = lambda policy, name: lambda config: None
    def freeze(task, environment, config, model, start, **unused):
        config["eval_mode"] = True
        render_frequency = config["render_freq"]
        config["render_freq"] = 0
        for _ in range(10000):
            if len(saved["scenes"]) >= args.episodes:
                saved["complete"] = True
                saved["sha256"] = signature(saved["scenes"])
                durable_json(path, saved)
                return saved["next_seed"], 0, 0
            check_stop(args.stop_root)
            seed, ordinal = saved["next_seed"], len(saved["scenes"])
            started = time.monotonic()
            accepted, info, error = False, None, None
            try:
                random.seed(seed)
                environment.setup_demo(now_ep_num=ordinal, seed=seed, is_test=True, **config)
                info = environment.play_once()
                environment.close_env()
                accepted = bool(environment.plan_success and environment.check_success())
            except EvaluationInterrupted:
                raise
            except Exception:
                error = traceback.format_exc()
                try:
                    environment.close_env()
                except Exception:
                    pass
            if accepted:
                check_stop(args.stop_root)
                config["render_freq"] = render_frequency
                try:
                    random.seed(seed)
                    environment.setup_demo(now_ep_num=ordinal, seed=seed, is_test=True, **config)
                    # Upstream shuffles templates using unseeded Python random.
                    # Persist this single draw and replay the literal instruction.
                    random.seed(seed ^ 0x51A17)
                    descriptions = official.generate_episode_descriptions(task, [info["info"]], args.episodes)
                    instruction = str(official.np.random.choice(descriptions[0]["seen"]))
                    gpu = verify_gpu(args.gpu_uuid, environment.scene)
                finally:
                    environment.close_env(clear_cache=True)
                    config["render_freq"] = 0
                saved["scenes"].append({"task": task, "seed": seed, "ordinal": ordinal,
                                        "instruction": instruction, "episode_info": info["info"],
                                        "filter_seconds": time.monotonic() - started, "gpu": gpu})
            saved["next_seed"] = seed + 1
            durable_json(path, saved)
            print(f"[scene-plan] {task} accepted={len(saved['scenes'])}/{args.episodes} candidate={seed} feasible={accepted} seconds={time.monotonic()-started:.1f}", flush=True)
            if error:
                print(error, flush=True)
        raise RuntimeError("Feasibility filtering exceeded 10000 candidates; inspect setup errors.")
    official.eval_policy = freeze
    official.main({"task_name": args.task, "task_config": "demo_clean", "ckpt_setting": "memory_s1_scene_plan",
                   "policy_name": "deploy_policy", "instruction_type": "seen", "seed": args.seed})


def run_episode(args, official):
    job = read(args.job)
    scene = job["scene"]
    output = Path(args.output)
    def evaluate(task, environment, config, model, start, **unused):
        config["eval_mode"] = True
        config["eval_video_log"] = False
        config.pop("eval_video_save_dir", None)
        started = time.monotonic()
        timings = {"observation_seconds": 0.0, "policy_seconds": 0.0}
        try:
            check_stop(args.stop_root)
            before = time.monotonic()
            random.seed(scene["seed"])
            environment.setup_demo(now_ep_num=scene["ordinal"], seed=scene["seed"], is_test=True, **config)
            environment._memory_seed = scene["seed"]
            environment.set_instruction(instruction=scene["instruction"])
            gpu = verify_gpu(args.gpu_uuid, environment.scene)
            timings["setup_seconds"] = time.monotonic() - before
            official.eval_function_decorator("deploy_policy", "reset_model")(model)
            function = official.eval_function_decorator("deploy_policy", "eval")
            target_limit = min(environment.step_lim, args.max_targets) if args.max_targets else environment.step_lim
            while environment.take_action_cnt < target_limit:
                check_stop(args.stop_root)
                before = time.monotonic()
                observation = environment.get_obs()
                timings["observation_seconds"] += time.monotonic() - before
                before = time.monotonic()
                function(environment, model, observation)
                timings["policy_seconds"] += time.monotonic() - before
                if environment.eval_success:
                    break
            if args.max_targets and args.record_frames:
                before = time.monotonic()
                final_observation = environment.get_obs()
                timings["observation_seconds"] += time.monotonic() - before
                model.capture(environment, final_observation)
            timings.update(model.timings)
            value = {"status": "complete", "task": task, "seed": scene["seed"], "ordinal": scene["ordinal"],
                     "instruction": scene["instruction"], "condition": job["condition"],
                     "success": bool(environment.eval_success), "max_reward": float(environment.max_reward),
                     "executed_targets": int(environment.take_action_cnt), "gpu": gpu, "timings": timings,
                     "diagnostic_prefix": bool(args.max_targets), "target_limit": int(target_limit),
                     "truncated": bool(args.max_targets and not environment.eval_success and target_limit < environment.step_lim),
                     "termination": "success" if environment.eval_success else ("diagnostic_target_limit" if args.max_targets and target_limit < environment.step_lim else "official_target_limit")}
        except EvaluationInterrupted as error:
            value = {"status": "interrupted", "error": str(error)}
        except Exception:
            value = {"status": "error", "error": traceback.format_exc()}
        finally:
            environment.close_env(clear_cache=True)
        value["simulator_seconds"] = time.monotonic() - started
        durable_json(output / "simulator_result.json", value)
        print(f"[episode] {scene['task']} seed={scene['seed']} status={value['status']} seconds={value['simulator_seconds']:.1f}", flush=True)
        if value["status"] == "error":
            raise RuntimeError(value["error"])
        return scene["seed"] + 1, int(value.get("success", False)), value.get("max_reward", 0)
    official.eval_policy = evaluate
    episode_tag = "memory_s1_episode_" + signature({"job": job["id"], "attempt": job["attempt"], "output": str(output)})[:12]
    official.main({"task_name": scene["task"], "task_config": "demo_clean", "ckpt_setting": episode_tag,
                   "policy_name": "deploy_policy", "instruction_type": "seen", "seed": args.seed,
                   "memory_socket": args.socket, "memory_output": args.output, "memory_stop_root": args.stop_root,
                   "memory_record_frames": args.record_frames, "memory_record_feedback": args.record_feedback})


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--operation", choices=("plan", "episode"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--task")
    parser.add_argument("--episodes", type=int)
    parser.add_argument("--contract")
    parser.add_argument("--job")
    parser.add_argument("--socket")
    parser.add_argument("--stop-root")
    parser.add_argument("--gpu-uuid")
    parser.add_argument("--record-frames", action="store_true")
    parser.add_argument("--record-feedback", action="store_true")
    parser.add_argument("--max-targets", type=int, default=0)
    args = parser.parse_args()
    if args.max_targets < 0:
        parser.error("max-targets cannot be negative")
    official = load_official()
    if args.operation == "plan":
        plan_scenes(args, official)
    else:
        run_episode(args, official)


if __name__ == "__main__":
    main()
