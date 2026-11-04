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
    sys.path.insert(0, str(root / 'scripts/memory_s1'))
    import sim_eval
    import deploy_policy
    import numpy as np
    from sim_feedback import physical_state, object_snapshot
    from sim_instrumentation import joint_details, contact_pairs, object_contacts

    class BoundedPolicy(deploy_policy.RPCPolicy):
        def request(self, environment, command):
            start = time.monotonic()
            response = self.call({'command': command, 'current_id': self.frame_id,
                'observations': self.pending, 'task': self.config['task_name'],
                'episode_seed': environment._memory_seed, 'instruction': environment.get_instruction()})
            self.pending = []
            self.timings['rpc_seconds'] += time.monotonic() - start
            return response

        def execute(self, environment, observation):
            sim_eval.check_stop(self.config.get('memory_stop_root'))
            if environment.step_lim != case['cap']: raise ValueError('Official task limit differs from frozen protocol')
            if self.frame_id >= case['cap']: raise ValueError('Attempted action beyond official limit')
            # Capture only the ordinary loop observation, once per completed target.
            self.pending.append(self.capture(environment, observation))
            if not self.actions:
                count = execution_count(self.frame_id, case['cap'], int(job.get('execute', EXECUTE)))
                response = self.request(environment, 'decide')
                actions = np.asarray(response['actions'], dtype=np.float32)
                if actions.shape != (32, 14) or not np.isfinite(actions).all() or response['execute'] != count:
                    raise ValueError('RPC action shape/finiteness/execution contract mismatch')
                self.actions.extend(actions[:count])
                print(f'[decision] frame={self.frame_id} execute={count} cap={case["cap"]}', flush=True)
            sim_eval.check_stop(self.config.get('memory_stop_root'))
            started = time.monotonic(); target = self.actions.popleft()
            before_steps = getattr(environment, '_memory_physics_steps', None)
            before = physical_state(environment.robot); objects_before = object_snapshot(environment)
            objects_before.update(task_state(environment))
            environment.take_action(target, action_type='qpos')
            self.timings['action_execution_seconds'] += time.monotonic() - started
            after = physical_state(environment.robot); contacts = contact_pairs(environment.scene)
            objects_after = object_snapshot(environment)
            objects_after.update(task_state(environment))
            append(directory / 'executed_actions.jsonl', {
                'completed_target_id': self.frame_id + 1, 'target': target.tolist(),
                'physical_before': before.tolist(), 'physical_after': after.tolist(),
                'physical_abs_error': np.abs(after - target).tolist(),
                'command_echo_before': np.asarray(observation['joint_action']['vector']).tolist(),
                'objects_before': objects_before, 'objects_after': objects_after,
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
