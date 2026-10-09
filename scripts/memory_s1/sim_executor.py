"""Explicit diagnostic executors; upstream TOPP remains the default."""
from __future__ import annotations

import numpy as np

DENSE_SOURCE = "https://github.com/OpenBMB/MiniCPM-Robot/blob/main/MiniCPM-RobotManip/evaluation/rmbench/rmbench_env.py"


def execute_target(environment, target, executor="upstream_topp", substeps=15):
    target = np.asarray(target, dtype=np.float64)
    if target.shape != (14,) or not np.isfinite(target).all():
        raise ValueError("Expected a finite absolute 14-dimensional Aloha target.")
    if executor == "upstream_topp":
        environment.take_action(target, action_type="qpos")
        return
    if executor != "dense_native" or int(substeps) < 1:
        raise ValueError("Unknown executor or nonpositive dense interval.")
    if environment.eval_success or environment.take_action_cnt >= environment.step_lim:
        return
    robot = environment.robot
    current = np.asarray(robot.get_left_arm_jointState() + robot.get_right_arm_jointState(), dtype=np.float64)
    interval = int(substeps) * float(environment.scene.get_timestep())
    left_velocity = (target[:6] - current[:6]) / interval
    right_velocity = (target[7:13] - current[7:13]) / interval
    left_grip = np.linspace(current[6], target[6], int(substeps) + 1)[1:]
    right_grip = np.linspace(current[13], target[13], int(substeps) + 1)[1:]
    environment.take_action_cnt += 1
    for index in range(int(substeps)):
        robot.set_arm_joints(target[:6], left_velocity, "left")
        robot.set_arm_joints(target[7:13], right_velocity, "right")
        robot.set_gripper(float(left_grip[index]), "left")
        robot.set_gripper(float(right_grip[index]), "right")
        environment.scene.step()
        if environment.check_success():
            environment.eval_success = True
            break
    environment._update_render()
