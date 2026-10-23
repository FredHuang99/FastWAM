"""RMBench adapter for the memory_v2 closed loop: autonomous 32-predict / 24-execute from frame zero.

A self-contained copy of Codex's /restore-tmp/dense_joint_v1/sim_adapter.py (production setup, capture, action
call and passive feedback; no project patches, no extra simulation steps, no success queries), with two optional
job fields that the original fixes:
  * max_targets   : stop after this many executed targets (smoke tests; result termination
                    "diagnostic_target_limit"); 0 = the official 500 / 1000 cap
  * record_frames : save the three camera PNGs of every captured observation (qualitative figures)
Nothing is imported from the dense delivery, so its code identity is unchanged.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time

EXECUTE = 24


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def append(path, value):
    with Path(path).open('a', encoding='utf-8') as f:
        f.write(json.dumps(value, allow_nan=False) + '\n')


def execution_count(frame, limit):
    if not 0 <= frame < limit:
        raise ValueError('Target outside official limit')
    return min(EXECUTE, limit - frame)


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
                count = execution_count(self.frame_id, case['cap'])
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
            environment.take_action(target, action_type='qpos')
            self.timings['action_execution_seconds'] += time.monotonic() - started
            after = physical_state(environment.robot); contacts = contact_pairs(environment.scene)
            append(directory / 'executed_actions.jsonl', {
                'completed_target_id': self.frame_id + 1, 'target': target.tolist(),
                'physical_before': before.tolist(), 'physical_after': after.tolist(),
                'physical_abs_error': np.abs(after - target).tolist(),
                'command_echo_before': np.asarray(observation['joint_action']['vector']).tolist(),
                'objects_before': objects_before, 'objects_after': object_snapshot(environment),
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
