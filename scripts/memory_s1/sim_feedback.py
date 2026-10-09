"""Physical SAPIEN feedback for diagnostics; never supplied to the policy."""
from __future__ import annotations

import numpy as np


def physical_state(robot):
    result = []
    for side in ("left", "right"):
        entity = getattr(robot, f"{side}_entity")
        active = entity.get_active_joints()
        qpos = np.asarray(entity.get_qpos(), dtype=np.float64)
        joints = getattr(robot, f"{side}_arm_joints")
        if len(joints) != 6:
            raise ValueError("Diagnostic physical feedback expects the six-joint Aloha arms.")
        result.extend(float(qpos[active.index(joint)]) for joint in joints)
        scale = getattr(robot, f"{side}_gripper_scale")
        span = float(scale[1] - scale[0])
        if span == 0:
            raise ValueError("Physical gripper scale has zero span.")
        fingers = []
        for joint, multiplier, offset in getattr(robot, f"{side}_gripper"):
            if joint is not None and float(multiplier) != 0:
                coordinate = (float(qpos[active.index(joint)]) - float(offset)) / float(multiplier)
                fingers.append((coordinate - float(scale[0])) / span)
        if not fingers:
            raise ValueError("No measurable physical gripper joints; command echo is not a substitute.")
        result.append(float(np.mean(fingers)))
    state = np.asarray(result, dtype=np.float64)
    if state.shape != (14,) or not np.isfinite(state).all():
        raise ValueError("Invalid physical qpos feedback.")
    return state


def object_snapshot(environment):
    result = {}
    for name in ("block", "block1", "block2", "button"):
        actor = getattr(environment, name, None)
        if actor is not None and hasattr(actor, "get_pose"):
            pose = actor.get_pose()
            result[name] = {"p": np.asarray(pose.p).tolist(), "q": np.asarray(pose.q).tolist()}
    for name in ("stage_id", "press_cnt", "press_flag"):
        value = getattr(environment, name, None)
        if isinstance(value, (int, float, bool, np.integer, np.floating, np.bool_)):
            result[name] = value.item() if isinstance(value, np.generic) else value
    return result
