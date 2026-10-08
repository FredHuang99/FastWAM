"""Replay next-record joint targets in a reviewed matching RMBench scene."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image
import torch
import yaml


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--task", choices=("put_back_block", "swap_blocks"), required=True)
    parser.add_argument("--episode", required=True)
    parser.add_argument("--scene-seed", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-targets", type=int, default=128)
    args = parser.parse_args()
    root = Path.cwd()
    sys.path[:0] = [str(root), str(root / "policy"), str(root / "description/utils")]
    spec = importlib.util.spec_from_file_location("rmbench_official_eval", root / "scripts/eval_policy.py")
    official = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(official)
    settings = yaml.safe_load((root / "env_cfg/task_config/demo_clean.yml").read_text())
    settings.update(task_name=args.task, task_config="demo_clean", ckpt_setting="alignment_replay",
                    eval_mode=True, eval_video_save_dir=None, render_freq=0, save_data=False, collect_data=False)
    camera = yaml.safe_load((root / "env_cfg/task_config/_camera_config.yml").read_text())[settings["camera"]["head_camera_type"]]
    settings.update(head_camera_h=camera["h"], head_camera_w=camera["w"])
    embodiments = yaml.safe_load((root / "env_cfg/task_config/_embodiment_config.yml").read_text())
    robot_file = embodiments["aloha-agilex"]["file_path"]
    robot = official.get_embodiment_config(robot_file)
    settings.update(left_robot_file=robot_file, right_robot_file=robot_file, dual_arm_embodied=True,
                    left_embodiment_config=robot, right_embodiment_config=robot)
    episode = torch.load(args.episode, map_location="cpu", weights_only=True)
    environment = official.class_decorator(args.task)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    errors = []
    try:
        environment.setup_demo(now_ep_num=0, seed=args.scene_seed, is_test=True, **settings)
        observation = environment.get_obs()
        initial_state_error = np.abs(np.asarray(observation["joint_action"]["vector"]) - episode["states"][0].numpy()).tolist()
        Image.fromarray(observation["observation"]["head_camera"]["rgb"]).save(output / "sim_initial_head.png")
        for index, target in enumerate(episode["targets"][:args.max_targets].numpy()):
            environment.take_action(target, action_type="qpos")
            observation = environment.get_obs()
            state = np.asarray(observation["joint_action"]["vector"], dtype=np.float32)
            errors.append({"native_record": index, "target_source_record": index + 1,
                           "target": target.tolist(), "observed": state.tolist(), "abs_error": np.abs(state - target).tolist()})
            if index % 16 == 15:
                Image.fromarray(observation["observation"]["head_camera"]["rgb"]).save(output / f"sim_after_{index+1:06d}_targets.png")
            if environment.eval_success or environment.take_action_cnt >= environment.step_lim:
                break
        report = {"task": args.task, "scene_seed": args.scene_seed, "episode": args.episode,
                  "initial_state_abs_error": initial_state_error, "targets": errors,
                  "max_reward": float(environment.max_reward), "success": bool(environment.eval_success),
                  "scene_match_review_required": True,
                  "note": "Compare the initial scene/object arrangement with the raw episode. A seed or matching robot state alone does not prove a matching scene."}
        (output / "alignment_replay.json").write_text(json.dumps(report, indent=2))
    finally:
        environment.close_env()


if __name__ == "__main__":
    main()
