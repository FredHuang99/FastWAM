"""Simulator-side audit, expert replay, bounded scene planning and policy diagnostics."""
from __future__ import annotations

import argparse
from collections import deque
import importlib
import importlib.metadata
import importlib.util
import json
from multiprocessing.connection import Client
import os
from pathlib import Path
import random
import sys
import time
import subprocess

import numpy as np
from PIL import Image
import yaml

from sim_eval import check_stop, durable_json, verify_gpu
from sim_executor import execute_target
from sim_feedback import object_snapshot, physical_state
from sim_instrumentation import PhysicalRecorder, command_state, joint_details, contact_pairs


def load_official(root):
    root = Path(root).resolve()
    sys.path[:0] = [str(root), str(root / "policy"), str(root / "description/utils")]
    path = root / ("scripts/eval_policy.py" if (root / "scripts/eval_policy.py").exists() else "script/eval_policy.py")
    spec = importlib.util.spec_from_file_location("rootcause_official_simulator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    import sapien
    context = sapien.render.RenderSystem(device="cuda:0")
    def scene(engine, config=None):
        if config is not None:
            sapien.physx.set_scene_config(config)
        return sapien.Scene([sapien.physx.PhysxCpuSystem(), sapien.render.RenderSystem(device="cuda:0")])
    sapien.Engine.create_scene = scene
    module._rootcause_renderer = context
    return module


def config_directory(root):
    root = Path(root)
    return root / ("env_cfg/task_config" if (root / "env_cfg/task_config").exists() else "task_config")


def settings(root, official, task):
    directory = config_directory(root)
    task_config = "demo_randomized" if task in ("stack_blocks_two", "handover_block") else "demo_clean"
    cfg = yaml.safe_load((directory / f"{task_config}.yml").read_text(encoding="utf-8"))
    cameras = yaml.safe_load((directory / "_camera_config.yml").read_text(encoding="utf-8"))
    embodiments = yaml.safe_load((directory / "_embodiment_config.yml").read_text(encoding="utf-8"))
    embodiment = cfg["embodiment"]
    if embodiment != ["aloha-agilex"]:
        raise ValueError(f"Expected the original Aloha embodiment, got {embodiment}; do not silently replace it.")
    robot_file = embodiments["aloha-agilex"]["file_path"]
    robot_cfg = official.get_embodiment_config(robot_file)
    head = cameras[cfg["camera"]["head_camera_type"]]
    cfg.update(task_name=task, task_config=task_config, ckpt_setting="rootcause_diagnostic",
        eval_mode=True, eval_video_log=False, eval_video_save_dir=None, render_freq=0,
        save_data=False, collect_data=False, head_camera_h=head["h"], head_camera_w=head["w"],
        left_robot_file=robot_file, right_robot_file=robot_file, dual_arm_embodied=True,
        left_embodiment_config=robot_cfg, right_embodiment_config=robot_cfg)
    return cfg


def preflight(args):
    root = Path.cwd()
    directory = config_directory(root)
    task_config = "demo_randomized" if args.tasks[0] in ("stack_blocks_two", "handover_block") else "demo_clean"
    required = [directory / name for name in (f"{task_config}.yml", "_camera_config.yml", "_embodiment_config.yml", "_eval_step_limit.yml")]
    required += [root / "envs" / f"{task}.py" for task in args.tasks]
    if (root / "envs/utils/rand_create_cluttered_actor.py").exists():
        required += [root / "assets/objects/objaverse/list.json", root / "assets/objects/same.json"]
    missing = [str(path) for path in required if not path.exists()]
    report = {"root": str(root), "missing": missing, "ready": not missing, "versions": {}, "imports": {}}
    report.update(python=sys.executable, python_version=sys.version, task_config_name=task_config)
    for name in ("torch", "sapien", "mplib", "curobo", "pytorch3d"):
        spec = importlib.util.find_spec(name)
        report["imports"][name] = spec.origin if spec else None
        try:
            report["versions"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            report["versions"][name] = "not-distribution-metadata"
    if not missing:
        embodiments = yaml.safe_load((directory / "_embodiment_config.yml").read_text(encoding="utf-8"))
        robot_root = Path(embodiments["aloha-agilex"]["file_path"])
        if not robot_root.is_absolute():
            robot_root = root / robot_root
        report["robot_root"] = str(robot_root)
        if not (robot_root / "config.yml").exists():
            report["missing"].append(str(robot_root / "config.yml"))
        else:
            from sim_eval import signature
            import hashlib
            files = {}
            for path in robot_root.rglob("*"):
                if path.is_file():
                    files[str(path.relative_to(robot_root))] = hashlib.sha256(path.read_bytes()).hexdigest()
            report["robot_files"] = files
            report["robot_identity"] = signature(files)
        report["task_config"] = yaml.safe_load((directory / f"{task_config}.yml").read_text(encoding="utf-8"))
        report["camera_config"] = yaml.safe_load((directory / "_camera_config.yml").read_text(encoding="utf-8"))
        report["step_limits"] = yaml.safe_load((directory / "_eval_step_limit.yml").read_text(encoding="utf-8"))
        if robot_root.is_dir() and (robot_root / "config.yml").is_file():
            report["robot_config"] = yaml.safe_load((robot_root / "config.yml").read_text(encoding="utf-8"))
            for key in ("urdf_path", "srdf_path"):
                relative = report["robot_config"].get(key)
                if relative and not (robot_root / relative).is_file():
                    report["missing"].append(str(robot_root / relative))
            if "curobo" in str(report["robot_config"].get("planner", "")).lower() and not (robot_root / "curobo.yml").is_file():
                report["missing"].append(str(robot_root / "curobo.yml"))
        if report["task_config"].get("domain_randomization", {}).get("random_background"):
            textures = root / "assets/background_texture/unseen"
            if not textures.is_dir() or not any(textures.iterdir()):
                report["missing"].append(str(textures))
        for package, location in report["imports"].items():
            if location and Path(location).is_file():
                import hashlib
                report.setdefault("import_sha256", {})[package] = hashlib.sha256(Path(location).read_bytes()).hexdigest()
        report["ready"] = not report["missing"] and all(report["imports"].values())
    driver = subprocess.run(["nvidia-smi", "--query-gpu=uuid,driver_version,name", "--format=csv,noheader"], capture_output=True, text=True)
    report["driver"] = driver.stdout if driver.returncode == 0 else driver.stderr
    report["remediation"] = {"official_instructions": "https://robotwin-platform.github.io/doc/usage/robotwin-install.html",
        "asset_repository": "TianxingChen/RoboTwin2.0", "automatic_download": False,
        "rule": "Restore original RoboTwin configs/assets; do not substitute RMBench configs or upgrade simulator dependencies."}
    durable_json(args.output, report)
    print(json.dumps(report, indent=2), flush=True)
    return 0 if report["ready"] else 3


def save_images(output, observation, frame_id):
    output = Path(output) / "frames"
    output.mkdir(exist_ok=True)
    for name in ("head_camera", "left_camera", "right_camera"):
        Image.fromarray(np.asarray(observation["observation"][name]["rgb"], dtype=np.uint8)).save(output / f"{name}_{frame_id:06d}.png")


def target_row(environment, recorder, target, before, started, before_steps):
    after = physical_state(environment.robot)
    return {"completed_target_id": recorder.target_id, "target": np.asarray(target).tolist(),
        "physical_before": before.tolist(), "physical_after": after.tolist(),
        "physical_abs_error": np.abs(after - target).tolist(), "abs_error": np.abs(after - target).tolist(),
        "command_echo_after": command_state(environment.robot).tolist(),
        "command_echo_abs_error": np.abs(command_state(environment.robot) - target).tolist(),
        "joint_details": joint_details(environment.robot), "contacts": contact_pairs(environment.scene),
        "objects_after": object_snapshot(environment), "physics_steps": recorder.steps - before_steps,
        "physics_step_id": recorder.steps, "sim_time": recorder.steps * recorder.dt,
        "seconds": time.monotonic() - started, "feedback_source": "physical_qpos_unclipped_gripper_mean_fingers"}


def replay(environment, recorder, args, job):
    import torch
    episode = torch.load(job["episode"], map_location="cpu", weights_only=True)
    expected = episode["states"][0].numpy()
    initial = np.abs(command_state(environment.robot) - expected)
    if float(initial.max()) > 1e-3:
        raise ValueError(f"Initial commanded state mismatch: {initial.tolist()}")
    cadence = json.loads(Path(job["cadence"]).read_text()) if job.get("cadence") else {}
    intervals = cadence.get("intervals", []) if cadence.get("verified") else []
    targets = episode["targets"].numpy()
    job["original_step_limit"] = environment.step_lim
    environment.step_lim = max(environment.step_lim, len(targets))
    rows = []
    limit = min(len(targets), args.max_targets) if args.max_targets else len(targets)
    for index, target in enumerate(targets[:limit]):
        check_stop(args.stop_root)
        recorder.target_id = index + 1
        before, tick, started = physical_state(environment.robot), recorder.steps, time.monotonic()
        interval = intervals[index] if intervals else 15
        # Duplicate native records must not be assigned an invented positive duration.
        if args.executor == "dense_native" and intervals and interval == 0:
            if not np.allclose(command_state(environment.robot), target, atol=1e-5, rtol=0):
                raise ValueError("A verified zero-duration native record changes its command target.")
            environment.take_action_cnt += 1
        else:
            execute_target(environment, target, args.executor, interval)
        rows.append(target_row(environment, recorder, target, before, started, tick))
        if index % 16 == 15 or index == 0:
            with recorder.wall_operation("get_obs"):
                save_images(args.output, environment.get_obs(), index + 1)
        if index % 16 == 15:
            mean = sum(r["seconds"] for r in rows) / len(rows)
            print(f"[replay] {index+1}/{limit} executor={args.executor} ETA={(limit-index-1)*mean:.1f}s", flush=True)
        if environment.eval_success:
            break
    report = {"targets": rows, "initial_state_abs_error": job["initial_physical_error"],
        "initial_command_error": initial.tolist(), "cadence_verified": bool(intervals),
        "cadence_scope": "verified_native_intervals" if intervals else "approximate_fixed_15_physics_steps",
        "scene_match_review_required": not bool(intervals), "feedback_source": "physical_qpos_unclipped_gripper"}
    report.update(original_step_limit=job["original_step_limit"], replay_step_limit=environment.step_lim,
        observation_record_ids=list(range(len(episode["states"]))), target_source="next stored command state")
    durable_json(Path(args.output) / "alignment_replay.json", report)


def policy_episode(environment, recorder, args, job):
    key = bytes.fromhex(os.environ["MEMORY_S1_RPC_KEY"])
    actions, frame_id = deque(), 0
    target_limit = min(environment.step_lim, job["max_targets"]) if job["max_targets"] else environment.step_lim
    while frame_id < target_limit and not environment.eval_success:
        check_stop(args.stop_root)
        # The original RoboTwin positive control skips observations inside its chunk.
        if not actions or job["scene"]["environment"] != "robotwin":
            with recorder.wall_operation("get_obs"):
                observation = environment.get_obs()
        if not actions:
            save_images(args.output, observation, frame_id)
            request = {"current_id": frame_id, "task": job["scene"]["task"], "episode_seed": job["scene"]["seed"],
                "instruction": job["scene"]["instruction"],
                "images": [np.ascontiguousarray(observation["observation"][name]["rgb"], dtype=np.uint8)
                    for name in ("head_camera", "left_camera", "right_camera")],
                "proprio": command_state(environment.robot)}
            with recorder.wall_operation("RPC_inference"):
                with Client(args.socket, family="AF_UNIX", authkey=key) as connection:
                    connection.send(request)
                    reply = connection.recv()
            if not reply["ok"]:
                raise RuntimeError(reply["error"])
            predicted = np.asarray(reply["actions"], dtype=np.float32)
            if predicted.shape != (32, 14) or not np.isfinite(predicted).all():
                raise ValueError("Invalid 32x14 model action chunk.")
            actions.extend(predicted[:job["execute"]])
            print(f"[decision] frame={frame_id} execute={job['execute']} physics_tick={recorder.steps}", flush=True)
        target = actions.popleft()
        recorder.target_id = frame_id + 1
        before, tick, started = physical_state(environment.robot), recorder.steps, time.monotonic()
        execute_target(environment, target, args.executor, 15)
        row = target_row(environment, recorder, target, before, started, tick)
        with (Path(args.output) / "executed_actions.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
        frame_id += 1
    with recorder.wall_operation("get_obs"):
        save_images(args.output, environment.get_obs(), frame_id)
    return target_limit


def run_scene(args):
    root = Path.cwd()
    official = load_official(root)
    job = json.loads(Path(args.job).read_text())
    scene = job["scene"]
    cfg = settings(root, official, scene["task"])
    environment = official.class_decorator(scene["task"])
    started = time.monotonic()
    random.seed(scene["seed"])
    try:
        environment.setup_demo(now_ep_num=scene["ordinal"], seed=scene["seed"], is_test=True, **cfg)
        gpu = verify_gpu(args.gpu_uuid, environment.scene)
        save_images(args.output, environment.get_obs(), 0)
        initial_physical = physical_state(environment.robot).copy()
        if job.get("episode"):
            import torch
            initial_episode = torch.load(job["episode"], map_location="cpu", weights_only=True)
            job["initial_physical_error"] = np.abs(initial_physical - initial_episode["states"][0].numpy()).tolist()
        if scene.get("raw"):
            import h5py
            codec_spec = importlib.util.spec_from_file_location("rootcause_image_codec", root / "data/decode_image_bit.py")
            codec = importlib.util.module_from_spec(codec_spec)
            codec_spec.loader.exec_module(codec)
            raw = Path(__file__).resolve().parents[2] / scene["raw"]
            import hashlib
            if hashlib.sha256(raw.read_bytes()).hexdigest() != scene["raw_sha256"]:
                raise ValueError("Reviewed raw episode changed before scene alignment.")
            observation = environment.get_obs()
            comparison = {}
            with h5py.File(raw, "r") as file:
                for name, key in zip(("head_camera", "left_camera", "right_camera"), scene["camera_paths"]):
                    saved = codec.decode_image_bit(file[key][0])
                    actual = observation["observation"][name]["rgb"]
                    Image.fromarray(saved).save(Path(args.output) / "frames" / f"expected_{name}_000000.png")
                    comparison[name] = {"saved_shape": list(saved.shape), "actual_shape": list(actual.shape),
                        "mae": float(np.abs(saved.astype(float) - actual.astype(float)).mean()) if saved.shape == actual.shape else None}
            durable_json(Path(args.output) / "initial_scene_alignment.json", {"views": comparison,
                "review_required": True, "raw_sha256": scene["raw_sha256"],
                "note": "Compare saved and current layouts; small JPEG/render differences are not an automatic rejection or approval."})
        target_limit = 0
        with PhysicalRecorder(environment, args.output, args.stop_root) as recorder:
            if args.operation == "expert":
                environment.play_once()
                expert_success = bool(environment.plan_success and environment.check_success())
                job_episode = job.get("episode")
                cadence = {"verified": False, "intervals": [], "reason": "No matching saved episode."}
                if job_episode:
                    import torch
                    episode = torch.load(job_episode, map_location="cpu", weights_only=True)
                    native = np.concatenate((episode["states"].numpy(), episode["targets"][-1:].numpy()), axis=0)
                    commands = np.asarray([r["command_state"] for r in recorder.boundaries])
                    matched = commands.shape == native.shape and np.allclose(commands, native, atol=1e-5, rtol=0)
                    cadence = {"verified": bool(matched), "native_records": len(native), "observed_boundaries": len(commands),
                        "intervals": np.diff([r["physics_step_id"] for r in recorder.boundaries]).tolist() if matched else [],
                        "reason": "All recollected command records match." if matched else "Recollection does not reproduce every command record; fixed-15 replay is approximate."}
                durable_json(Path(args.output) / "cadence.json", cadence)
            elif args.operation == "replay":
                replay(environment, recorder, args, job)
                expert_success = bool(environment.eval_success)
            else:
                environment.set_instruction(instruction=scene["instruction"])
                target_limit = policy_episode(environment, recorder, args, job)
                expert_success = bool(environment.eval_success)
        value = {"status": "complete", "success": expert_success, "task": scene["task"], "seed": scene["seed"],
            "condition": job["condition"], "operation": args.operation, "executor": args.executor,
            "environment_root": str(root), "gpu": gpu, "executed_targets": int(environment.take_action_cnt),
            "effective_simulator_config": cfg,
            "initial_physical_state": initial_physical.tolist(),
            "max_reward": float(environment.max_reward) if hasattr(environment, "max_reward") else None,
            "diagnostic_prefix": bool(job.get("max_targets")),
            "truncated": bool(target_limit and target_limit < environment.step_lim and not expert_success),
            "target_limit": target_limit, "simulator_seconds": time.monotonic() - started,
            "physical_summary": json.loads((Path(args.output) / "physical_summary.json").read_text())}
        durable_json(Path(args.output) / "simulator_result.json", value)
        print(f"[complete] {scene['task']} operation={args.operation} success={expert_success}", flush=True)
    finally:
        environment.close_env(clear_cache=True)


def plan(args):
    official = load_official(Path.cwd())
    path = Path(args.output)
    saved = json.loads(path.read_text()) if path.exists() else {"scenes": [], "next_seed": 1800000, "candidates": 0, "complete": False}
    if saved["complete"]:
        return
    cfg = settings(Path.cwd(), official, args.tasks[0])
    for _ in range(saved["candidates"], 20):
        check_stop(args.stop_root)
        seed = saved["next_seed"]
        environment = official.class_decorator(args.tasks[0])
        accepted, info, error = False, None, None
        try:
            random.seed(seed)
            environment.setup_demo(now_ep_num=len(saved["scenes"]), seed=seed, is_test=True, **cfg)
            info = environment.play_once()
            accepted = bool(environment.plan_success and environment.check_success())
            verify_gpu(args.gpu_uuid, environment.scene)
        except Exception as exception:
            error = repr(exception)
        finally:
            environment.close_env(clear_cache=True)
        saved["next_seed"] += 1
        saved["candidates"] += 1
        if accepted:
            random.seed(seed ^ 0x51A17)
            np.random.seed(seed ^ 0x51A17)
            descriptions = official.generate_episode_descriptions(args.tasks[0], [info["info"]], 2)
            instruction = str(np.random.choice(descriptions[0]["unseen"]))
            saved["scenes"].append({"task": args.tasks[0], "seed": seed, "ordinal": len(saved["scenes"]),
                "instruction": instruction, "episode_info": info, "environment": "robotwin"})
        saved["complete"] = len(saved["scenes"]) == 2
        durable_json(path, saved)
        print(f"[plan] {args.tasks[0]} candidates={saved['candidates']}/20 accepted={len(saved['scenes'])}/2 error={error}", flush=True)
        if saved["complete"]:
            return
    raise RuntimeError("Fewer than two expert-feasible scenes after the fixed 20-candidate budget.")


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--operation", choices=("preflight", "expert", "replay", "plan", "policy"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--tasks", nargs="+", default=["put_back_block", "swap_blocks"])
    parser.add_argument("--job")
    parser.add_argument("--socket")
    parser.add_argument("--gpu-uuid")
    parser.add_argument("--stop-root")
    parser.add_argument("--executor", choices=("upstream_topp", "dense_native"), default="upstream_topp")
    parser.add_argument("--max-targets", type=int, default=0)
    args = parser.parse_args()
    if args.operation == "preflight":
        raise SystemExit(preflight(args))
    if args.operation == "plan":
        plan(args)
    else:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        run_scene(args)


if __name__ == "__main__":
    main()
