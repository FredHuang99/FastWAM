"""CPU causal metrics: actual entity IDs, executed clocks, separate phases."""
from __future__ import annotations

import math
import statistics

import numpy as np

ARMS = (0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)
GRIPPERS = (6, 13)
MODES = ("policy", "expert", "expert_arm", "expert_gripper")


def compose(mode, frame, predicted, expert_targets, prefix=48):
    """Replace explicit command columns only; input proprio remains actual."""
    if mode not in MODES or frame < 0 or frame % 16:
        raise ValueError("Invalid component treatment / decision boundary")
    reference = np.asarray(expert_targets[frame:frame + 32], dtype=np.float32)
    if reference.shape != (32, 14) or not np.isfinite(reference).all():
        raise ValueError("Need 32 genuine same-scene expert targets")
    if frame < prefix or mode == "expert":
        return reference.copy()
    value = np.asarray(predicted, dtype=np.float32)
    if value.shape != (32, 14) or not np.isfinite(value).all():
        raise ValueError("Need a finite original 32x14 policy chunk")
    value = value.copy()
    if mode == "expert_arm":
        value[:, ARMS] = reference[:, ARMS]
    elif mode == "expert_gripper":
        value[:, GRIPPERS] = reference[:, GRIPPERS]
    return value


def target_phase(index, expert_targets, prefix=48):
    """Names refer to the reference commands, never fabricated grasp labels."""
    grip = np.asarray(expert_targets, dtype=np.float64)[:, 13]
    changes = np.flatnonzero(grip < .999)
    closed = np.flatnonzero(grip < .05)
    start = int(changes[0]) if len(changes) else len(grip)
    end = int(closed[0]) if len(closed) else len(grip)
    if index < prefix:
        return "expert_prefix"
    if index < start:
        return "reference_preclosure"
    if index <= end:
        return "reference_closing"
    return "reference_postclosure"


def finger_contact(row, object_name, threshold):
    """Two right fingers on ONE object, with recorded positive impulse."""
    record = row.get("object_contacts") or {}
    obj = record.get("objects", {}).get(object_name, {})
    fingers = record.get("aliases", {}).get("fingers", {}).get("right", [])
    ids = {f["id"] for f in fingers if f.get("id")}
    if (record.get("available") is not True or obj.get("aliases_resolved") is not True
            or len(ids) != 2):
        return {"known": False, "two_fingers": None, "impulse": None}
    touches, impulse = set(), 0.0
    for pair in obj.get("matched_pairs", []):
        strength = float(pair.get("impulse", 0.0))
        if not math.isfinite(strength) or strength < 0:
            raise ValueError("Invalid recorded contact impulse")
        impulse += strength
        if strength > threshold:
            touches.update(ids & {pair.get("a_id"), pair.get("b_id")})
    return {"known": True, "two_fingers": len(touches) == 2,
            "contacting_finger_ids": sorted(touches), "impulse": impulse}


def physical_metrics(actions, observations, interventions, expert, spec):
    prefix, cap = spec["expert_prefix_targets"], spec["target_cap"]
    count = len(actions)
    if not prefix < count <= cap or [r["completed_target_id"] for r in actions] != list(range(1, count + 1)):
        raise ValueError("Missing or repeated executed target IDs")
    if [r["frame_id"] for r in observations] != list(range(count)):
        raise ValueError("Incomplete per-target observation sequence")
    if [r["frame_id"] for r in interventions] != list(range(0, count, 16)):
        raise ValueError("Incomplete decision sequence")
    reference = np.asarray(expert["targets"], dtype=np.float32)
    clock = 0
    phase_rows, trajectory = {}, []
    obj = spec["object"]
    initial = actions[0]["objects_before"][obj]
    first_close = None
    run, longest, lifted_contact_run = 0, 0, False
    peak_height, drop_while_closed = -math.inf, False
    for i, row in enumerate(actions):
        number = i + 1
        expected = np.asarray(interventions[i // 16]["actions"][i % 16], np.float32)
        command = np.asarray(row["target"], np.float32)
        if not np.array_equal(command, expected):
            raise ValueError(f"Executor/returned command differ at target {number}")
        if number <= prefix and not np.array_equal(command, reference[i]):
            raise ValueError(f"Common expert prefix differs at target {number}")
        step, delta, dt = row.get("physics_step_id"), row.get("physics_steps"), row.get("physics_timestep")
        if (step is None or delta is None or dt is None or delta < 0 or dt <= 0
                or not math.isfinite(dt) or step != clock + delta
                or observations[i].get("physics_step_id") != clock):
            raise ValueError(f"Observation/execution physical clock mismatch at target {number}")
        clock = step
        actual = np.asarray(row["physical_after"], np.float64)
        if actual.shape != (14,) or not np.isfinite(actual).all():
            raise ValueError("Invalid physical robot state")
        contact = finger_contact(row, obj, spec["contact_impulse_threshold"])
        position = row["objects_after"][obj]["p"]
        lift = float(position[2] - initial["p"][2])
        if not math.isfinite(lift):
            raise ValueError("Invalid object lift")
        phase = target_phase(i, reference, prefix)
        if number > prefix:
            if first_close is None and command[13] < .5:
                first_close = number
            peak_height = max(peak_height, lift)
            # A commanded release is excluded; drift while holding is separate.
            drop_while_closed |= peak_height - lift >= spec["lift_threshold_m"] and command[13] <= .2
            run = run + 1 if lift >= spec["lift_threshold_m"] and contact["two_fingers"] is True else 0
            longest = max(longest, run)
            lifted_contact_run |= longest >= spec["lift_consecutive_targets"]
        ref_error = command.astype(np.float64) - reference[i].astype(np.float64)
        item = {"target_id": number, "phase": phase, "physics_step_id": step,
                "physics_steps": delta, "physical_seconds": delta * dt,
                "right_gripper_command": float(command[13]), "right_gripper_physical": float(actual[13]),
                "right_gripper_reference": float(reference[i, 13]),
                "arm_reference_rmse_rad": float(np.sqrt(np.mean(ref_error[list(ARMS)] ** 2))),
                "left_arm_reference_rmse_rad": float(np.sqrt(np.mean(ref_error[:6] ** 2))),
                "right_arm_reference_rmse_rad": float(np.sqrt(np.mean(ref_error[7:13] ** 2))),
                "arm_tracking_rmse_rad": float(np.sqrt(np.mean((actual[list(ARMS)] - command[list(ARMS)]) ** 2))),
                "command_echo_previous_max_abs": float(np.max(np.abs(np.asarray(row["command_echo_before"]) -
                        np.asarray(actions[i - 1]["target"])))) if i else None,
                "object_lift_m": lift, "object_position": position, "contact": contact,
                "right_ee_pose": row["joint_details"]["right"]["ee_pose"],
                "right_ee_link": row["joint_details"]["right"].get("ee_link_name"),
                "ee_scope": "configured link world pose, not fingertip center"}
        trajectory.append(item)
        phase_rows.setdefault(phase, []).append(item)
    phases = {}
    for name, rows in phase_rows.items():
        phases[name] = {"targets": len(rows), "arm_reference_rmse_rad": statistics.mean(x["arm_reference_rmse_rad"] for x in rows),
                       "left_arm_reference_rmse_rad": statistics.mean(x["left_arm_reference_rmse_rad"] for x in rows),
                       "right_arm_reference_rmse_rad": statistics.mean(x["right_arm_reference_rmse_rad"] for x in rows),
                       "arm_tracking_rmse_rad": statistics.mean(x["arm_tracking_rmse_rad"] for x in rows),
                       "right_gripper_reference_mae": statistics.mean(abs(x["right_gripper_command"] - x["right_gripper_reference"]) for x in rows),
                       "physics_seconds": sum(x["physical_seconds"] for x in rows),
                       "max_object_lift_m": max(x["object_lift_m"] for x in rows)}
    intervals = [x["physical_seconds"] for x in trajectory]
    policy = trajectory[prefix:]
    return {"executed_targets": count, "expert_prefix_targets": prefix,
            "first_right_close_after_handoff": first_close, "phase_metrics": phases,
            "object": obj, "max_lift_after_handoff_m": max(x["object_lift_m"] for x in policy),
            "final_lift_m": trajectory[-1]["object_lift_m"],
            "two_finger_contact_known_targets": sum(x["contact"]["known"] for x in policy),
            "longest_lift_with_two_finger_impulse_targets": longest,
            "lift_contact_proxy_observed": bool(lifted_contact_run),
            "drop_while_close_command_observed": bool(drop_while_closed),
            "physical_target_interval_seconds": {"min": min(intervals), "median": statistics.median(intervals), "max": max(intervals)},
            "physical_timing": "measured actual steps; not an assumed fixed 15-Hz interval",
            "proxy_scope": "finite-prefix retained-lift/contact observation, not task success or accuracy"}, trajectory


def interpretation(results):
    """Expose factorial outcomes without claiming a universal training cause."""
    if set(results) != set(MODES):
        return {"state": "partial", "conclusion": "Wait for the missing component controls", "root_cause_confirmed": False}
    p, e, a, g = (results[name] for name in MODES)
    if not e["metrics"]["lift_contact_proxy_observed"]:
        conclusion = "Positive-control lift/contact was not observed within the prefix; review execution and proxy before attributing policy failure"
    elif p["metrics"]["lift_contact_proxy_observed"]:
        conclusion = "The policy retained-lift proxy is observed in this prefix; analyze later dropping and task stages separately"
    else:
        left, right = a["metrics"]["lift_contact_proxy_observed"], g["metrics"]["lift_contact_proxy_observed"]
        conclusion = {(True, False): "Expert arm commands rescue the observed prefix; prioritize pose/location prediction",
                      (False, True): "Expert gripper commands rescue the observed prefix; prioritize closing timing/coordination",
                      (False, False): "Neither single-component substitution rescues the prefix; inspect arm/gripper interaction",
                      (True, True): "Either component substitution rescues the prefix; both are viable local interventions"}[(left, right)]
    return {"state": "complete", "conclusion": conclusion, "root_cause_confirmed": False,
            "scope": "one frozen swap scene, one original checkpoint/noise policy; upstream training mechanism needs evidence",
            "benchmark_accuracy": None}
