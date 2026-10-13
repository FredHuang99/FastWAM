"""Freeze official feasible scenes, or execute one frozen policy episode."""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout, redirect_stderr
import importlib.util
import hashlib
import json
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
    from eval_state import EvaluationInterrupted, check_stop, cuda_gpu_uuid, durable_json, read, signature, stop_mode
    from selection_runtime import event
    from simulator_backend import configure_backend
    # Backend configuration imports fused_evaluation lazily. Keep this path
    # available until those standalone imports finish, including spawned workers.
    SIMULATOR_BACKEND = configure_backend()
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
    if contract.get("simulator_backend") != SIMULATOR_BACKEND:
        raise ValueError("Scene contract differs from the active CuRobo backend.")
    if path.exists():
        saved = read(path)
        if saved["contract"] != contract:
            raise ValueError("Scene manifest contract changed; use a new manifest path.")
        if saved["complete"]:
            return
    else:
        saved = {"contract": contract, "scenes": [], "next_seed": 100000 * (1 + args.seed), "complete": False}
    durable_json(path, saved)
    progress_root = os.environ.get("MEMORY_S1_PROGRESS_ROOT")
    official.eval_function_decorator = lambda policy, name: lambda config: None
    def freeze(task, environment, config, model, start, **unused):
        config["eval_mode"] = True
        render_frequency = config["render_freq"]
        config["render_freq"] = 0
        for _ in range(10000):
            if stop_mode(args.stop_root):
                raise EvaluationInterrupted("Scene filtering stopped at a candidate boundary.")
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
                event(progress_root, "scene_setup", task=task, seed=seed)
                environment.setup_demo(now_ep_num=ordinal, seed=seed, is_test=True, **config)
                event(progress_root, "expert_filter", task=task, seed=seed)
                info = environment.play_once()
                environment.close_env()
                accepted = bool(environment.plan_success and environment.check_success())
            except EvaluationInterrupted:
                raise
            except Exception:
                error = traceback.format_exc()
                durable_json(path.with_suffix(".error.json"), {"seed": seed, "error": error, "next_seed_preserved": True})
                try:
                    environment.close_env()
                except Exception:
                    pass
                raise RuntimeError("Scene infrastructure failed; the candidate seed was not skipped. " + error)
            if accepted:
                check_stop(args.stop_root)
                event(progress_root, "freeze_instruction", task=task, seed=seed)
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
            event(progress_root, "candidate", "complete", task=task, seed=seed, accepted=accepted, seconds=time.monotonic()-started)
            saved.setdefault("candidates", []).append({"seed": seed, "accepted": accepted, "seconds": time.monotonic()-started})
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
    def single_episode(task, environment, config, model, start, **unused):
        progress_root = os.environ.get("MEMORY_S1_PROGRESS_ROOT")
        fields = {"task": task, "seed": scene["seed"], "job_id": job["id"],
                  "scene_number": scene["ordinal"]+1, "scene_total": args.scene_count}
        config["eval_mode"] = True
        config["eval_video_log"] = False
        config.pop("eval_video_save_dir", None)
        started = time.monotonic()
        timings = {"observation_seconds": 0.0, "policy_seconds": 0.0}
        passive_clock = None
        try:
            check_stop(args.stop_root)
            before = time.monotonic()
            random.seed(scene["seed"])
            event(progress_root, "episode_setup", **fields)
            environment.setup_demo(now_ep_num=scene["ordinal"], seed=scene["seed"], is_test=True, **config)
            environment._memory_seed = scene["seed"]
            environment.set_instruction(instruction=scene["instruction"])
            if args.record_feedback:
                from sim_instrumentation import PassiveClock
                passive_clock = PassiveClock(environment)
                passive_clock.__enter__()
            gpu = verify_gpu(args.gpu_uuid, environment.scene)
            timings["setup_seconds"] = time.monotonic() - before
            official.eval_function_decorator("deploy_policy", "reset_model")(model)
            function = official.eval_function_decorator("deploy_policy", "eval")
            target_limit = min(environment.step_lim, args.max_targets) if args.max_targets else environment.step_lim
            rollout_started = time.monotonic()
            event(progress_root, "rollout", **fields, targets=0, target_limit=int(target_limit),
                  rollout_seconds=0, episode_elapsed_seconds=rollout_started-started)
            last_progress = rollout_started
            last_targets = 0
            while environment.take_action_cnt < target_limit:
                check_stop(args.stop_root)
                before = time.monotonic()
                observation = environment.get_obs()
                timings["observation_seconds"] += time.monotonic() - before
                if args.qualification_trace:
                    import numpy as np
                    from sim_feedback import physical_state, object_snapshot
                    # Observe existing data only; never request additional camera frames.
                    cameras = observation["observation"]
                    trace = {"target_id": int(environment.take_action_cnt),
                             "rgb": {name: hashlib.sha256(np.ascontiguousarray(cameras[name]["rgb"]).tobytes()).hexdigest()
                                     for name in ("head_camera", "left_camera", "right_camera")},
                             "command_state": np.asarray(observation["joint_action"]["vector"]).tolist(),
                             "physical": physical_state(environment.robot).tolist(), "objects": object_snapshot(environment)}
                    with (output / "qualification_trace.jsonl").open("a", encoding="utf-8") as stream:
                        stream.write(json.dumps(trace, sort_keys=True, allow_nan=False) + "\n")
                before = time.monotonic()
                function(environment, model, observation)
                timings["policy_seconds"] += time.monotonic() - before
                targets = int(environment.take_action_cnt)
                if ((targets >= 16 and last_targets < 16) or time.monotonic()-last_progress >= 15
                        or targets >= target_limit or environment.eval_success):
                    now = time.monotonic()
                    cumulative = (now-rollout_started)/targets if targets >= 16 else None
                    window = (now-last_progress)/(targets-last_targets) if targets > last_targets else 0
                    rate = max(cumulative, window) if cumulative is not None else None
                    budget_eta = max(0, target_limit-targets)*rate if rate is not None else None
                    event(progress_root, "rollout", **fields,
                          targets=targets, target_limit=int(target_limit), episode_elapsed_seconds=now-started,
                          rollout_seconds=now-rollout_started, seconds_per_target=rate,
                          observation_seconds=timings["observation_seconds"], policy_seconds=timings["policy_seconds"],
                          target_budget_eta_seconds=budget_eta)
                    last_progress, last_targets = now, targets
                if environment.eval_success:
                    break
            timings["rollout_seconds"] = time.monotonic()-rollout_started
            # Evidence capture uses observations already consumed by the normal loop.
            timings.update(model.timings)
            value = {"status": "complete", "task": task, "seed": scene["seed"], "ordinal": scene["ordinal"],
                     "instruction": scene["instruction"], "condition": job["condition"],
                     "success": bool(environment.eval_success), "max_reward": float(environment.max_reward),
                     "executed_targets": int(environment.take_action_cnt), "gpu": gpu, "timings": timings,
                     "simulator_backend": SIMULATOR_BACKEND,
                     "diagnostic_prefix": bool(args.max_targets), "target_limit": int(target_limit),
                     "truncated": bool(args.max_targets and not environment.eval_success and target_limit < environment.step_lim),
                     "termination": "success" if environment.eval_success else ("diagnostic_target_limit" if args.max_targets and target_limit < environment.step_lim else "official_target_limit")}
        except EvaluationInterrupted as error:
            value = {"status": "interrupted", "error": str(error)}
        except Exception:
            value = {"status": "error", "error": traceback.format_exc()}
        finally:
            if passive_clock is not None:
                passive_clock.__exit__()
            environment.close_env(clear_cache=True)
        value["simulator_seconds"] = time.monotonic() - started
        event(progress_root, "episode", value["status"], **fields, seconds=value["simulator_seconds"], timings=value.get("timings"))
        durable_json(output / "simulator_result.json", value)
        print(f"[episode] {scene['task']} seed={scene['seed']} status={value['status']} seconds={value['simulator_seconds']:.1f}", flush=True)
        if value["status"] == "error":
            raise RuntimeError(value["error"])
        return scene["seed"] + 1, int(value.get("success", False)), value.get("max_reward", 0)
    def evaluate(task, environment, config, model, start, **unused):
        nonlocal job, scene, output
        while True:
            if args.service:
                # Publish completion only after the attempt log has stopped changing.
                with (output / "simulator.log").open("a", encoding="utf-8") as log:
                    with redirect_stdout(log), redirect_stderr(log):
                        result = single_episode(task, environment, config, model, start, **unused)
                durable_json(output / "service_complete.json", {"job": job["id"], "attempt": job["attempt"]})
            else:
                return single_episode(task, environment, config, model, start, **unused)
            if read(output / "simulator_result.json")["status"] != "complete":
                return result
            event(os.environ.get("MEMORY_S1_PROGRESS_ROOT"), "resident_idle", "complete", task=task)
            inbox = Path(args.service) / "next.json"
            idle_started = time.monotonic()
            while not inbox.exists():
                if stop_mode(args.stop_root) or time.monotonic()-idle_started > 600:
                    return result
                time.sleep(.2)
            command = read(inbox)
            inbox.unlink()
            if command.get("stop"):
                return result
            job = read(command["job"])
            scene = job["scene"]
            if scene["task"] != task:
                raise ValueError("A resident simulator cannot switch task classes")
            output = Path(command["output"])
            model.config["memory_output"] = str(output)
            # Inference and history are reset by the normal reset_model call above.

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
    parser.add_argument("--service", help="Private resident worker inbox; qualification is required by the parent")
    parser.add_argument("--stop-root")
    parser.add_argument("--gpu-uuid")
    parser.add_argument("--record-frames", action="store_true")
    parser.add_argument("--record-feedback", action="store_true")
    parser.add_argument("--qualification-trace", action="store_true")
    parser.add_argument("--max-targets", type=int, default=0)
    parser.add_argument("--scene-count", type=int, default=10, help="Display only; never changes the frozen scene bank")
    args = parser.parse_args()
    if args.max_targets < 0:
        parser.error("max-targets cannot be negative")
    event(os.environ.get("MEMORY_S1_PROGRESS_ROOT"), "simulator_import")
    official = load_official()
    if args.operation == "plan":
        plan_scenes(args, official)
    else:
        run_episode(args, official)


if __name__ == "__main__":
    main()
