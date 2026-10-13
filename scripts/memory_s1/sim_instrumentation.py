"""Process-scoped physical instrumentation without extra physics advancement."""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import time

import numpy as np

from sim_feedback import object_snapshot, physical_state


def command_state(robot):
    return np.asarray(robot.get_left_arm_jointState() + robot.get_right_arm_jointState(), dtype=np.float64)


def joint_details(robot):
    result = {}
    for side in ("left", "right"):
        entity = getattr(robot, f"{side}_entity")
        active = entity.get_active_joints()
        indices = [active.index(joint) for joint in getattr(robot, f"{side}_arm_joints")]
        fingers = [active.index(joint) for joint, multiplier, offset in getattr(robot, f"{side}_gripper") if joint is not None]
        qpos = np.asarray(entity.get_qpos(), dtype=np.float64)
        qvel = np.asarray(entity.get_qvel(), dtype=np.float64)
        result[side] = {"arm_qpos": qpos[indices].tolist(), "arm_qvel": qvel[indices].tolist(),
            "finger_qpos": qpos[fingers].tolist(), "finger_qvel": qvel[fingers].tolist(),
            "finger_joint_names": [active[i].get_name() for i in fingers],
            "gripper_scale": list(map(float, getattr(robot, f"{side}_gripper_scale"))),
            "gripper_transform": [{"joint": joint.get_name(), "multiplier": float(multiplier), "offset": float(offset)}
                for joint, multiplier, offset in getattr(robot, f"{side}_gripper") if joint is not None]}
        link = getattr(robot, f"{side}_ee", None)
        if link is None:
            link = getattr(robot, f"{side}_ee_link", None)
        if link is not None and (hasattr(link, "get_pose") or hasattr(link, "global_pose")):
            pose = link.get_pose() if hasattr(link, "get_pose") else link.global_pose
            result[side]["ee_pose"] = {"p": np.asarray(pose.p).tolist(), "q": np.asarray(pose.q).tolist()}
            result[side]["ee_link_name"] = link.get_name() if hasattr(link, "get_name") else getattr(link, "name", None)
            result[side]["ee_pose_scope"] = "configured end-effector link world pose; not inferred fingertip center"
    return result


def entity_names(actor):
    """Resolve actual entity/link aliases, without guessing from name substrings."""
    names = set()
    for value in (actor, getattr(actor, 'actor', None), getattr(actor, 'entity', None), getattr(actor, 'body', None)):
        if value is None: continue
        for entity in (value, getattr(value, 'entity', None)):
            if entity is None: continue
            name = entity.get_name() if hasattr(entity, 'get_name') else getattr(entity, 'name', None)
            if name: names.add(str(name))
    return names


def entity_identity(actor):
    """Prefer SAPIEN scene entity IDs; never use names for contact attribution."""
    if actor is None:
        return None
    seen = set()
    while id(actor) not in seen:
        seen.add(id(actor))
        wrapped = next((getattr(actor, key, None) for key in ('actor', 'entity')
                        if getattr(actor, key, None) is not None and getattr(actor, key) is not actor), None)
        if wrapped is None:
            break
        actor = wrapped
    for name in ('per_scene_id', 'id'):
        value = getattr(actor, name, None)
        if isinstance(value, (int, np.integer)):
            return f'{name}:{int(value)}'
    for name in ('get_id',):
        method = getattr(actor, name, None)
        if callable(method):
            return f'id:{int(method())}'
    # Unresolved is reported as unknown rather than guessing from duplicate names.
    return None


def contact_aliases(environment):
    fingers = {'left': [], 'right': []}
    for side in ('left','right'):
        for joint, multiplier, offset in getattr(environment.robot, f'{side}_gripper'):
            if joint is None: continue
            child = joint.get_child_link() if hasattr(joint,'get_child_link') else getattr(joint,'child_link',None)
            fingers[side].append({'id': entity_identity(child), 'names': sorted(entity_names(child))})
    objects = {name: {'id': entity_identity(getattr(environment, name)), 'names': sorted(entity_names(getattr(environment,name)))}
               for name,value in object_snapshot(environment).items() if isinstance(value,dict) and 'p' in value}
    return {'version': 'entity-contact-v2', 'scope': 'IDs valid only inside this scene', 'fingers': fingers, 'objects': objects}


def object_contacts(environment, contacts=None, aliases=None):
    contacts = contact_pairs(environment.scene) if contacts is None else contacts
    aliases = contact_aliases(environment) if aliases is None else aliases
    results = {}
    for name, value in aliases['objects'].items():
        obj = value['id']
        side_hits = {}
        mapped = bool(obj and contacts['available'])
        for side, rows in aliases['fingers'].items():
            ids = {row['id'] for row in rows if row['id'] is not None}
            mapped = mapped and bool(rows) and all(row['id'] is not None for row in rows)
            side_hits[side] = [r for r in contacts['pairs'] if obj is not None and
                ((r['a_id'] == obj and r['b_id'] in ids) or (r['b_id'] == obj and r['a_id'] in ids))]
        hits = side_hits['left'] + side_hits['right']
        results[name] = {'gripper_contact':True if hits else (False if mapped else None),
                         'matched_pairs':hits,'aliases_resolved':mapped,
                         'by_side': {s: bool(v) if mapped or v else None for s,v in side_hits.items()},
                         'absence_is_task_failure':False}
    return {'objects':results,'aliases':aliases,'available':contacts['available'],
            'scope':'Instantaneous contact observation; negative values do not prove absence over an interval'}


def contact_pairs(scene):
    try:
        contacts = scene.get_contacts()
    except (AttributeError, NotImplementedError):
        return {"available": False, "pairs": [], "reason": "Installed scene exposes no get_contacts API."}
    def name(body):
        # SAPIEN 3 contacts expose physics components; names can live on entities.
        for actor in (getattr(body, "entity", None), body):
            if actor is not None:
                value = actor.get_name() if hasattr(actor, "get_name") else getattr(actor, "name", "")
                if value:
                    return str(value)
        return "unknown"
    pairs = []
    for contact in contacts:
        bodies = getattr(contact, "bodies", None)
        if bodies is not None and len(bodies) == 2:
            a, b = bodies
        else:
            a = getattr(contact, "actor0", getattr(contact, "body0", None))
            b = getattr(contact, "actor1", getattr(contact, "body1", None))
        points = getattr(contact, "points", [])
        impulse = sum(float(np.linalg.norm(np.asarray(getattr(p, "impulse", [0, 0, 0])))) for p in points)
        pairs.append({"a": name(a), "b": name(b), "a_id": entity_identity(a), "b_id": entity_identity(b),
            "impulse": impulse, 'points': [
                {'position': np.asarray(getattr(p, 'position', [])).tolist(),
                 'normal': np.asarray(getattr(p, 'normal', [])).tolist(),
                 'impulse': np.asarray(getattr(p, 'impulse', [])).tolist()} for p in points]})
    resolved = all(row["a_id"] is not None and row["b_id"] is not None for row in pairs)
    return {"available": resolved, "pairs": pairs, "names_resolved": resolved,
            "reason": None if resolved else "Contact entity identity unresolved; absence of contact cannot be inferred."}



class PassiveClock:
    """Count existing scene.step calls only; no reads, rendering, RNG or success calls."""
    def __init__(self, environment):
        self.environment = environment
        self.original = type(environment.scene).step
        environment._memory_physics_steps = 0
        environment._memory_physics_dt = float(environment.scene.get_timestep())

    def __enter__(self):
        def counted(scene, *args, **kwargs):
            value = self.original(scene, *args, **kwargs)
            if scene is self.environment.scene:
                self.environment._memory_physics_steps += 1
            return value
        type(self.environment.scene).step = counted
        return self

    def __exit__(self, *unused):
        type(self.environment.scene).step = self.original


class PhysicalRecorder:
    def __init__(self, environment, output, stop=None):
        self.environment, self.output, self.stop = environment, Path(output), stop
        self.output.mkdir(parents=True, exist_ok=True)
        self.steps, self.target_id = 0, 0
        self.dt = float(environment.scene.get_timestep())
        self.initial_objects = object_snapshot(environment)
        self.samples, self.boundaries, self.planning = [], [], []
        self.wall_operations = []
        self.events = {name: {"max_lift_m": 0.0, "max_xy_m": 0.0, "lift_steps": 0,
            "max_lift_run": 0, "current_lift_run": 0, "contact_seen": False}
            for name, value in self.initial_objects.items() if isinstance(value, dict) and "p" in value}
        self.contacts_available = True
        self.contact_aliases = contact_aliases(environment)
        self.contact_stream = None
        self.contact_mapping_validated = False
        self.finger_counts = {side: len(joint_details(environment.robot)[side]["finger_qpos"]) for side in ("left", "right")}
        self.original_step = type(environment.scene).step
        self.original_picture = environment._take_picture
        self.patches = []

    def sample(self):
        objects = object_snapshot(self.environment)
        contacts = contact_pairs(self.environment.scene)
        if self.contact_stream is not None and contacts['pairs']:
            self.contact_stream.write(json.dumps({'physics_step_id':self.steps,'target_id':self.target_id,
                'pairs':contacts['pairs'],'available':contacts['available']},allow_nan=False)+'\n')
        self.contacts_available &= contacts["available"]
        physical = physical_state(self.environment.robot)
        details = joint_details(self.environment.robot)
        velocity, ee, fingers = [], [], []
        for side in ("left", "right"):
            scale = getattr(self.environment.robot, f"{side}_gripper_scale")
            span = float(scale[1] - scale[0])
            normalized_velocities = [v / float(j[1]) / span for v, j in zip(details[side]["finger_qvel"],
                [j for j in getattr(self.environment.robot, f"{side}_gripper") if j[0] is not None]) if float(j[1]) != 0]
            velocity.extend(details[side]["arm_qvel"] + [float(np.mean(normalized_velocities))])
            if "ee_pose" not in details[side]:
                raise ValueError(f"Actual end-effector pose unavailable: {side}")
            ee.extend(details[side]["ee_pose"]["p"] + details[side]["ee_pose"]["q"])
            fingers.extend(details[side]["finger_qpos"] + details[side]["finger_qvel"])
        positions = []
        for name, event in self.events.items():
            p = np.asarray(objects[name]["p"])
            initial = np.asarray(self.initial_objects[name]["p"])
            lift, xy = float(p[2] - initial[2]), float(np.linalg.norm(p[:2] - initial[:2]))
            event["max_lift_m"] = max(event["max_lift_m"], lift)
            event["max_xy_m"] = max(event["max_xy_m"], xy)
            event["current_lift_run"] = event["current_lift_run"] + 1 if lift >= 0.03 else 0
            event["max_lift_run"] = max(event["max_lift_run"], event["current_lift_run"])
            event["lift_steps"] += int(lift >= 0.03)
            contact = object_contacts(self.environment, contacts, self.contact_aliases)['objects'][name]
            event['contact_seen'] |= contact['gripper_contact'] is True
            self.contacts_available &= contact['aliases_resolved']
            positions.extend(p.tolist())
        self.samples.append([self.steps, self.steps * self.dt, self.target_id, *physical.tolist(), *velocity, *ee, *fingers, *positions])

    def __enter__(self):
        from sim_eval import check_stop
        recorder = self
        self.contact_stream = (self.output/'contacts_entity.jsonl').open('w',encoding='utf-8')
        (self.output/'scene_entity_map.json').write_text(json.dumps(self.contact_aliases,indent=2),encoding='utf-8')
        def step(scene, *args, **kwargs):
            if scene is recorder.environment.scene:
                check_stop(recorder.stop)
            value = recorder.original_step(scene, *args, **kwargs)
            if scene is recorder.environment.scene:
                recorder.steps += 1
                recorder.sample()
            return value
        type(self.environment.scene).step = step
        def picture(*args, **kwargs):
            recorder.boundaries.append({"observation_record_id": len(recorder.boundaries),
                "physics_step_id": recorder.steps, "sim_time": recorder.steps * recorder.dt,
                "command_state": command_state(recorder.environment.robot).tolist()})
            # Keep collection writes disabled; record native calls without changing their cadence.
            return recorder.original_picture(*args, **kwargs)
        self.environment._take_picture = picture
        for side in ("left", "right"):
            planner = getattr(self.environment.robot, f"{side}_mplib_planner", None)
            if planner is None or not hasattr(planner, "TOPP"):
                continue
            original = planner.TOPP
            def observed_topp(*args, _original=original, _side=side, **kwargs):
                started = time.monotonic()
                try:
                    result = _original(*args, **kwargs)
                    position_count = len(result[1]) if len(result) > 1 else None
                    self.planning.append({"target_id": self.target_id, "side": _side,
                        "seconds": time.monotonic() - started, "raised": False,
                        "position_count": position_count, "empty_trajectory": position_count == 0})
                    return result
                except Exception as error:
                    self.planning.append({"target_id": self.target_id, "side": _side,
                        "seconds": time.monotonic() - started, "raised": True, "error": str(error)})
                    raise
            planner.TOPP = observed_topp
            self.patches.append((planner, original))
        return self

    def __exit__(self, *unused):
        type(self.environment.scene).step = self.original_step
        self.environment._take_picture = self.original_picture
        for planner, original in self.patches:
            planner.TOPP = original
        if self.contact_stream is not None:
            self.contact_stream.close()
        array = np.asarray(self.samples, dtype=np.float32)
        np.savez_compressed(self.output / "physical_trace.npz", values=array,
            columns=np.asarray(["physics_step_id", "sim_time", "executing_target_id", *[f"qpos_{i}" for i in range(14)],
                *[f"qvel_{i}" for i in range(14)],
                *[f"{side}_ee_{axis}" for side in ("left", "right") for axis in ("x", "y", "z", "qw", "qx", "qy", "qz")],
                *[f"{side}_finger_{kind}_{i}" for side in ("left", "right") for kind in ("qpos", "qvel") for i in range(self.finger_counts[side])],
                *[f"{name}_{axis}" for name in self.events for axis in "xyz"]]))
        # A positive observed pair is evidence. Negative conclusions require
        # independent validation on successful experts, not just resolved names.
        for event in self.events.values():
            if not event['contact_seen']: event['contact_seen'] = None
        report = {"physics_steps": self.steps, "timestep": self.dt, "simulated_seconds": self.steps * self.dt,
            "physics_step_origin": "zero immediately after setup_demo; setup physics is outside this trace",
            "executing_target_id_scope": "one-based policy/replay target; zero during live expert continuous execution",
            "initial_objects": self.initial_objects, "final_objects": object_snapshot(self.environment),
            "events": self.events, "contacts_available": self.contacts_available,
            "contact_aliases":self.contact_aliases, "contact_mapping_validated":self.contact_mapping_validated,
            "collection_boundaries": self.boundaries, "planning": self.planning,
            "planning_exceptions": sum(row["raised"] for row in self.planning),
            "observation_or_rpc_advanced_physics": any(r["physics_steps_during_operation"] for r in self.wall_operations),
            "wall_operations": self.wall_operations,
            "scope": "Geometric/contact evidence, not an automatic manipulation admission."}
        (self.output / "physical_summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    @contextmanager
    def wall_operation(self, name):
        before, started = self.steps, time.monotonic()
        try:
            yield
        finally:
            row = {"operation": name, "target_id": self.target_id, "seconds": time.monotonic() - started,
                "physics_steps_during_operation": self.steps - before}
            self.wall_operations.append(row)
            with (self.output / "wall_operations.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row) + "\n")
