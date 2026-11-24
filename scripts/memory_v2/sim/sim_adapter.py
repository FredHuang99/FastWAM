"""RMBench adapter for the memory_v2 closed loop: autonomous 32-predict / 24-execute from frame zero.

A self-contained copy of Codex's /restore-tmp/dense_joint_v1/sim_adapter.py (production setup, capture, action
call and passive feedback; no project patches, no extra simulation steps, no success queries), with two optional
job fields that the original fixes:
  * max_targets   : stop after this many executed targets (smoke tests; result termination
                    "diagnostic_target_limit"); 0 = the official 500 / 1000 cap
  * record_frames : save the three camera PNGs of every captured observation (qualitative figures)
  * execute       : targets executed per decision (default 24 of the 32 predicted; the policy side must agree)
Nothing is imported from the dense delivery, so its code identity is unchanged.

press_button (11-04): the frozen sim_feedback.object_snapshot logs block / button / press_cnt / press_flag / stage_id
only, so the press_button counters were not recorded. task_state() reads them passively (getattr only; no success
query, no extra simulation step) and merges them into objects_before / objects_after: press_cnt_1 / press_cnt_2 /
press_cnt_check_button, press_flag_*, card_id_1 / card_id_2, and per button (button1 / button2 / check_button) the
root position and the button joint value (pressed below -0.005, released above -0.001, as in envs/press_button.py).
Environments without these attributes (put_back_block, swap_blocks) log exactly what they logged before.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import sys
import time

EXECUTE = 24


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def append(path, value):
    with Path(path).open('a', encoding='utf-8') as f:
        f.write(json.dumps(value, allow_nan=False) + '\n')


TASK_NUMBERS = ('press_cnt_1', 'press_cnt_2', 'press_cnt_check_button', 'press_flag_1', 'press_flag_2',
                'press_flag_check_button', 'card_id_1', 'card_id_2')
TASK_BUTTONS = ('button1', 'button2', 'check_button')


def _number(value):
    """int / float / bool (numpy scalars included) as a plain JSON value, else None."""
    if isinstance(value, bool):
        return value
    item = getattr(value, 'item', None)
    if callable(item) and getattr(value, 'shape', None) == ():
        value = item()
    if isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value):        # json.dumps(allow_nan=False) must not fail
        return value
    return None


def task_state(environment):
    """Passive read of the press_button counters, cards and buttons (empty for other tasks)."""
    out = {}
    for name in TASK_NUMBERS:
        value = _number(getattr(environment, name, None))
        if value is not None:
            out[name] = value
    for name in TASK_BUTTONS:
        actor = getattr(environment, name, None)
        if actor is None:
            continue
        cell = {}
        try:
            pose = actor.get_pose()
            p = [float(x) for x in list(pose.p)[:3]]
            if all(math.isfinite(x) for x in p):
                cell['p'] = p
        except Exception:                                    # noqa: BLE001 (diagnostics only)
            pass
        try:
            art = actor.actor if hasattr(actor, 'actor') else actor
            names = [j.get_name() for j in art.get_active_joints()]
            joint = float(list(art.get_qpos())[names.index('button_joint')])
            if math.isfinite(joint):
                cell['joint'] = joint
        except Exception:                                    # noqa: BLE001
            pass
        if cell:
            out[name] = cell
    return out


def ee_poses(environment):
    """11-11 (plan v12): end-effector poses (robot.get_*_ee_pose, the same getter the demos' ee poses came from):
    online event detection (fullft arprop / arev) and the press part of K0. Passive read, no simulation step."""
    try:
        return {side: [float(x) for x in list(getattr(environment.robot, f'get_{side}_ee_pose')())[:7]]
                for side in ('left', 'right')}
    except Exception:                                        # noqa: BLE001 (the policy side reports a missing pose)
        return None


# 11-22 (plan v19 3.3, A3; redone 12:50 after reading RMBench envs/observe_and_pickup.py): OBJECT RECORD, off unless
# MWAM_OBJECT_LOG=1 (read once, in the simulator process, which inherits the closed loop's environment). Passive reads
# only (attribute reads and get_pose; no simulation step, no success query), every read wrapped. With the flag on:
#   objects_after['_actors']  = {attribute: [x, y, z]} of every posed attribute of the environment, lists by index
#                               (observe_and_pickup: object[0..4] = the table candidates, target_object = the reference
#                               shown on the shelf, shelf, wall once it exists)
#   objects_after['_quat']    = {attribute: [w, x, y, z]} of the same posed attributes (11-24, card 11)
#   objects_after['_flags']   = the task scalars WATCH (observe_and_pickup: fail_flag = an arm moved > 3 cm before the
#                               wall appeared, get_obs_cnt, target_object_idx; eval_success)
#   OBJECTS_META.json (first target): every scalar attribute, short lists of names / ids (object_modelnames,
#                               object_ids), each posed attribute's entity name and start position, and the scene's
#                               entities (name, position) at that moment
# Used to split failures into "picked the wrong object", "picked nothing" and "moved before the wall" (obs_split.py).
# With the flag off nothing below runs: the logs are exactly as before.
OBJECT_LOG = os.environ.get('MWAM_OBJECT_LOG', '').strip() == '1'
# 11-24 plan v20 card 5 (press_told): MWAM_TOLD_COUNTS=1 appends the scene's two card values to the instruction the
# policy receives (told.py, the same sentence the training text used). Privileged information: a diagnostic arm only,
# never a main-table entry. Off (default): the instruction is exactly environment.get_instruction().
TOLD_COUNTS = os.environ.get('MWAM_TOLD_COUNTS', '').strip() == '1'


def told(environment):
    if not TOLD_COUNTS:
        return ''
    import importlib.util
    spec = importlib.util.spec_from_file_location('mwam_told', str(Path(__file__).resolve().parent / 'told.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    n1, n2 = getattr(environment, 'card_id_1', None), getattr(environment, 'card_id_2', None)
    if n1 is None or n2 is None:
        raise ValueError('MWAM_TOLD_COUNTS=1 needs a press_button scene (card_id_1 / card_id_2)')
    return module.told_sentence(int(n1), int(n2))
WATCH = ('fail_flag', 'get_obs_cnt', 'target_object_idx', 'eval_success')
SKIP_ATTRS = ('robot', 'scene', 'cameras', 'viewer', 'renderer', 'engine', 'eval_video_ffmpeg')


def _entity_name(entity):
    try:
        value = entity.get_name() if hasattr(entity, 'get_name') else getattr(entity, 'name', '')
        return str(value or '')
    except Exception:                                        # noqa: BLE001 (diagnostics only)
        return ''


def _entity_position(entity):
    try:
        pose = entity.get_pose() if hasattr(entity, 'get_pose') else getattr(entity, 'pose', None)
        p = [float(x) for x in list(pose.p)[:3]]
        return [round(x, 4) for x in p] if all(math.isfinite(x) for x in p) else None
    except Exception:                                        # noqa: BLE001
        return None


def _posed(value):
    """The posed object behind an attribute value (RMBench Actor, a SAPIEN entity, or a wrapper with .actor)."""
    if hasattr(value, 'get_pose'):
        return value
    inner = getattr(value, 'actor', None)
    return inner if hasattr(inner, 'get_pose') else None


def _attributes(environment):
    try:
        return sorted(vars(environment).items())
    except TypeError:
        return []


def task_actors(environment):
    """{attribute: [x, y, z]} of the environment's posed attributes; a list of them as attribute[i]."""
    out = {}
    for name, value in _attributes(environment):
        if name.startswith('_') or name in SKIP_ATTRS:
            continue
        ent = _posed(value)
        if ent is not None:
            p = _entity_position(ent)
            if p is not None:
                out[name] = p
        elif isinstance(value, (list, tuple)) and 0 < len(value) <= 32 and all(_posed(v) is not None for v in value):
            for i, v in enumerate(value):
                p = _entity_position(_posed(v))
                if p is not None:
                    out[f'{name}[{i}]'] = p
    return out


def _entity_quat(entity):
    try:
        pose = entity.get_pose() if hasattr(entity, 'get_pose') else getattr(entity, 'pose', None)
        q = [float(x) for x in list(pose.q)[:4]]
        return [round(x, 5) for x in q] if all(math.isfinite(x) for x in q) else None
    except Exception:                                        # noqa: BLE001
        return None


def task_quats(environment):
    """11-24 (plan v20 card 11, swap_T: the success test is position AND orientation): {attribute: [w, x, y, z]} of the
    same posed attributes as task_actors (SAPIEN quaternion order); passive reads like task_actors."""
    out = {}
    for name, value in _attributes(environment):
        if name.startswith('_') or name in SKIP_ATTRS:
            continue
        ent = _posed(value)
        if ent is not None:
            q = _entity_quat(ent)
            if q is not None:
                out[name] = q
        elif isinstance(value, (list, tuple)) and 0 < len(value) <= 32 and all(_posed(v) is not None for v in value):
            for i, v in enumerate(value):
                q = _entity_quat(_posed(v))
                if q is not None:
                    out[f'{name}[{i}]'] = q
    return out


def task_flags(environment):
    return {name: _number(getattr(environment, name, None)) for name in WATCH
            if _number(getattr(environment, name, None)) is not None}


def scene_entities(environment):
    scene = getattr(environment, 'scene', None)
    for getter in ('get_all_actors', 'get_entities'):
        try:
            if hasattr(scene, getter):
                return list(getattr(scene, getter)())
        except Exception:                                    # noqa: BLE001
            pass
    return []


def object_meta(environment):
    """Scalars, short lists of names / ids, posed attributes (entity name + position) and the scene's entities."""
    scalars, lists, actors = {}, {}, {}
    for name, value in _attributes(environment):
        if name.startswith('__') or name in SKIP_ATTRS:
            continue
        number = _number(value)
        ent = _posed(value)
        if number is not None:
            scalars[name] = number
        elif isinstance(value, str) and len(value) < 200:
            scalars[name] = value
        elif ent is not None:
            actors[name] = {'entity': _entity_name(ent), 'p': _entity_position(ent)}
        elif isinstance(value, (list, tuple)) and 0 < len(value) <= 32:
            if all(_posed(v) is not None for v in value):
                actors[name] = [{'entity': _entity_name(_posed(v)), 'p': _entity_position(_posed(v))} for v in value]
            elif all(isinstance(v, str) or _number(v) is not None for v in value):
                lists[name] = [v if isinstance(v, str) else _number(v) for v in value]
    entities = [{'name': _entity_name(e), 'p': _entity_position(e)} for e in scene_entities(environment)]
    return {'scalars': scalars, 'lists': lists, 'actors': actors, 'scene_entities': entities}


def execution_count(frame, limit, execute=EXECUTE):
    if not 0 <= frame < limit:
        raise ValueError('Target outside official limit')
    if not 1 <= int(execute) <= 32:
        raise ValueError('execute must be within [1, 32]')
    return min(int(execute), limit - frame)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--socket', required=True)
    parser.add_argument('--gpu-uuid', required=True)
    parser.add_argument('--stop-root', required=True)
    args = parser.parse_args()
    root = args.root.resolve(); directory = args.output.resolve()
    job = read(directory / 'job.json'); case = job['causal_case']
    stress = job.get('stress') or {}
    hold_at = {int(x) for x in stress.get('at', [])} if stress.get('kind') == 'hold' else set()
    event_stress = stress.get('kind') == 'event'          # 11-17 plan v13 E1: one null-event injection per episode
    if event_stress:                                       # by file path: this process's `fastwam` may be another checkout
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            'mwam_fullft_inject', Path(__file__).resolve().parents[3] / 'src/fastwam/fullft/inject.py')
        inj = importlib.util.module_from_spec(spec); sys.modules['mwam_fullft_inject'] = inj; spec.loader.exec_module(inj)
        Trigger, targets_for, object_displacement = inj.Trigger, inj.targets_for, inj.object_displacement
        counters_changed, arm_return_error = inj.counters_changed, inj.arm_return_error
        trigger = Trigger(int(stress['n_open']), kind=stress.get('trigger_kind', 'open'))
    sys.path.insert(0, str(root / 'scripts/memory_s1'))
    import sim_eval
    import deploy_policy
    import numpy as np
    from sim_feedback import physical_state, object_snapshot
    from sim_instrumentation import joint_details, contact_pairs, object_contacts

    class BoundedPolicy(deploy_policy.RPCPolicy):
        def capture(self, environment, observation):
            item = super().capture(environment, observation)
            pose = ee_poses(environment)
            if pose is not None:
                item['endpose'] = pose
            if job.get('oracle_counts'):                   # 11-21 plan v18 Z0: the true press counters (oracle ledger)
                state = task_state(environment)
                item['task_counts'] = {k: state[k] for k in ('press_cnt_1', 'press_cnt_2', 'press_cnt_check_button')
                                       if k in state}
                item['task_buttons'] = {b: state[b]['p'] for b in ('button1', 'button2')
                                        if isinstance(state.get(b), dict) and 'p' in state[b]}
            return item

        def request(self, environment, command):
            start = time.monotonic()
            payload = {'command': command, 'current_id': self.frame_id,
                'observations': self.pending, 'task': self.config['task_name'],
                'episode_seed': environment._memory_seed, 'instruction': environment.get_instruction() + told(environment)}
            if getattr(self, 'inserted', None):
                payload['inserted'] = self.inserted
            response = self.call(payload)
            self.pending = []
            self.inserted = []
            self.timings['rpc_seconds'] += time.monotonic() - start
            return response

        def hold(self, environment, observation):
            """Tempo stress (plan v10 D.3): hold the last commanded position for k targets before this decision.
            Budget-neutral (the official cap counts policy targets only); the current frame is re-captured after the
            pause. 'history': the k hold frames go to the policy as req['inserted']; 'hidden': they are not shown."""
            held = getattr(self, 'held', set())
            if self.frame_id in held:
                return
            held.add(self.frame_id); self.held = held
            k, arm = int(stress['k']), stress['arm']
            last = getattr(self, 'last_target', None)
            target = np.asarray(last if last is not None else observation['joint_action']['vector'], dtype=np.float32)
            before = object_snapshot(environment); count_before = environment.take_action_cnt
            started = time.monotonic(); frames = []
            for _ in range(k):
                environment.take_action(target, action_type='qpos')
                environment.take_action_cnt = count_before                  # holds do not use the official budget
                if arm == 'history':
                    item = self.capture(environment, environment.get_obs())
                    item['frame_id'] = None; item['inserted'] = True
                    frames.append(item)
            self.pending[-1] = self.capture(environment, environment.get_obs())
            self.inserted = frames
            append(directory / 'stress.jsonl', {'frame': self.frame_id, 'k': k, 'arm': arm, 'target': target.tolist(),
                'objects_before': before, 'objects_after': object_snapshot(environment),
                'physical_after': physical_state(environment.robot).tolist(), 'shown': len(frames),
                'seconds': time.monotonic() - started})
            print(f'[stress] frame={self.frame_id} hold {k} ({arm}) shown={len(frames)}', flush=True)

        def inject(self, environment, observation):
            """Plan v13 E1: the null event (pause / fidget / airgrasp, fastwam.fullft.inject) right before this decision,
            budget-neutral like hold(); 'history': its frames go to the policy as req['inserted']; 'hidden': not shown.
            Validity (object displacement, task counters, the active arm's return) is logged to stress.jsonl."""
            kind, k, arm_mode, active = stress['inject'], int(stress['k']), stress['arm'], int(trigger.arm)
            last = getattr(self, 'last_target', None)
            base = np.asarray(last if last is not None else observation['joint_action']['vector'], dtype=np.float32)
            before = object_snapshot(environment); before.update(task_state(environment))
            phys_before = physical_state(environment.robot); count_before = environment.take_action_cnt
            started = time.monotonic(); frames = []
            for target in targets_for(kind, k, base, active):
                environment.take_action(target, action_type='qpos')
                environment.take_action_cnt = count_before                  # injections do not use the official budget
                if arm_mode == 'history':
                    item = self.capture(environment, environment.get_obs())
                    item['frame_id'] = None; item['inserted'] = True
                    frames.append(item)
            self.pending[-1] = self.capture(environment, environment.get_obs())
            self.inserted = frames
            after = object_snapshot(environment); after.update(task_state(environment))
            phys_after = physical_state(environment.robot)
            append(directory / 'stress.jsonl', {'frame': self.frame_id, 'kind': 'event', 'inject': kind, 'k': k,
                'arm': arm_mode, 'active_arm': active, 'open_frame': trigger.open_frame, 'shown': len(frames),
                'displacement_m': object_displacement(before, after), 'counters_changed': counters_changed(before, after),
                'arm_return_rad': arm_return_error(phys_before, phys_after, active), 'target': base.tolist(),
                'objects_before': before, 'objects_after': after, 'physical_after': np.asarray(phys_after).tolist(),
                'seconds': time.monotonic() - started})
            print(f'[stress] frame={self.frame_id} {kind} {k} ({arm_mode}) arm={active} shown={len(frames)}', flush=True)

        def execute(self, environment, observation):
            sim_eval.check_stop(self.config.get('memory_stop_root'))
            if environment.step_lim != case['cap']: raise ValueError('Official task limit differs from frozen protocol')
            if self.frame_id >= case['cap']: raise ValueError('Attempted action beyond official limit')
            # Capture only the ordinary loop observation, once per completed target.
            self.pending.append(self.capture(environment, observation))
            if not self.actions and self.frame_id in hold_at:
                self.hold(environment, observation)
            if event_stress and not trigger.fired:
                pose = ee_poses(environment)
                vec = np.asarray(observation['joint_action']['vector'], dtype=np.float64)
                if pose is None:
                    raise ValueError('event stress needs the end-effector poses')
                trigger.step(self.frame_id, [vec[6], vec[13]], [pose['left'][:3], pose['right'][:3]])
                if not self.actions and trigger.due:
                    self.inject(environment, observation)
                    trigger.fire()
            if not self.actions:
                count = execution_count(self.frame_id, case['cap'], int(job.get('execute', EXECUTE)))
                response = self.request(environment, 'decide')
                actions = np.asarray(response['actions'], dtype=np.float32)
                if actions.shape != (32, 14) or not np.isfinite(actions).all() or response['execute'] != count:
                    raise ValueError('RPC action shape/finiteness/execution contract mismatch')
                self.actions.extend(actions[:count])
                print(f'[decision] frame={self.frame_id} execute={count} cap={case["cap"]}', flush=True)
            sim_eval.check_stop(self.config.get('memory_stop_root'))
            started = time.monotonic(); target = self.actions.popleft(); self.last_target = target
            before_steps = getattr(environment, '_memory_physics_steps', None)
            before = physical_state(environment.robot); objects_before = object_snapshot(environment)
            objects_before.update(task_state(environment)); ee_before = ee_poses(environment)
            environment.take_action(target, action_type='qpos')
            self.timings['action_execution_seconds'] += time.monotonic() - started
            after = physical_state(environment.robot); contacts = contact_pairs(environment.scene)
            objects_after = object_snapshot(environment)
            objects_after.update(task_state(environment))
            if OBJECT_LOG:                                   # 11-22 A3 object record (off by default)
                try:
                    if not (directory / 'OBJECTS_META.json').exists():
                        (directory / 'OBJECTS_META.json').write_text(json.dumps(object_meta(environment), indent=1,
                                                                                default=str), encoding='utf-8')
                    objects_after['_actors'] = task_actors(environment)
                    objects_after['_quat'] = task_quats(environment)        # 11-24 card 11 (orientations)
                    objects_after['_flags'] = task_flags(environment)
                except Exception as error:                   # noqa: BLE001 (diagnostics must never stop an episode)
                    objects_after['_actors_error'] = repr(error)[:300]
            append(directory / 'executed_actions.jsonl', {
                'completed_target_id': self.frame_id + 1, 'target': target.tolist(),
                'physical_before': before.tolist(), 'physical_after': after.tolist(),
                'physical_abs_error': np.abs(after - target).tolist(),
                'command_echo_before': np.asarray(observation['joint_action']['vector']).tolist(),
                'objects_before': objects_before, 'objects_after': objects_after,
                'ee_before': ee_before, 'ee_after': ee_poses(environment),
                'joint_details': joint_details(environment.robot), 'contacts': contacts,
                'object_contacts': object_contacts(environment, contacts),
                'physics_step_id': getattr(environment, '_memory_physics_steps', None),
                'physics_steps': None if before_steps is None else environment._memory_physics_steps - before_steps,
                'physics_timestep': getattr(environment, '_memory_physics_dt', None),
                'seconds': time.monotonic() - started,
                'feedback_source': 'physical_qpos_unclipped_gripper_mean_fingers'})
            self.frame_id += 1

    deploy_policy.get_model = lambda config: BoundedPolicy(config)
    # Force this already imported, private adapter for this child only.
    official = sim_eval.load_official()
    original_lookup = official.eval_function_decorator
    official.eval_function_decorator = lambda policy, name: (
        getattr(deploy_policy, name) if policy == 'deploy_policy' else original_lookup(policy, name))
    from types import SimpleNamespace
    run_args = SimpleNamespace(job=str(directory / 'job.json'), output=str(directory),
        stop_root=args.stop_root, socket=args.socket, gpu_uuid=args.gpu_uuid,
        record_feedback=True, qualification_trace=True, record_frames=bool(job.get('record_frames', False)),
        max_targets=int(job.get('max_targets', 0) or 0), scene_count=1, seed=job['run_seed'], service=None)
    sim_eval.run_episode(run_args, official)


if __name__ == '__main__':
    main()
