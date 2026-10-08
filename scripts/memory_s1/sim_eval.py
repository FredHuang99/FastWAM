"""Use the pinned official evaluator while exporting correctly counted results."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--socket", required=True)
    parser.add_argument("--task", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--episodes", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--record-frames", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    sys.path[:0] = [str(root), str(root / "policy"), str(root / "description/utils"), str(Path(__file__).parent)]
    specification = importlib.util.spec_from_file_location("official_rmbench_eval", root / "scripts/eval_policy.py")
    official = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(official)
    rows = []
    original_eval = official.eval_policy
    original_class = official.class_decorator

    def audited_class(task):
        environment = original_class(task)
        setup, close = environment.setup_demo, environment.close_env
        attempts = [0]
        def setup_with_seed(*positional, **kwargs):
            attempts[0] += 1
            if attempts[0] > 10000:
                raise RuntimeError("Expert feasibility filtering exceeded 10000 setups; inspect the simulator logs.")
            environment._memory_seed = int(kwargs["seed"])
            environment._memory_policy_active = False
            return setup(*positional, **kwargs)
        def close_with_result(*positional, **kwargs):
            if getattr(environment, "_memory_policy_active", False):
                rows.append({"seed": environment._memory_seed, "success": bool(environment.eval_success),
                             "max_reward": float(environment.max_reward), "executed_targets": int(environment.take_action_cnt)})
                environment._memory_policy_active = False
            return close(*positional, **kwargs)
        environment.setup_demo = setup_with_seed
        environment.close_env = close_with_result
        return environment

    original_decorator = official.eval_function_decorator
    def functions(policy, name):
        function = original_decorator(policy, name)
        if name == "eval":
            def active(environment, model, observation):
                environment._memory_policy_active = True
                return function(environment, model, observation)
            return active
        return function

    def counted_eval(*positional, **kwargs):
        kwargs["test_num"] = args.episodes
        return original_eval(*positional, **kwargs)

    official.class_decorator = audited_class
    official.eval_function_decorator = functions
    official.eval_policy = counted_eval
    config = {"task_name": args.task, "task_config": "demo_clean", "ckpt_setting": f"memory_s1_{args.mode}",
              "policy_name": "deploy_policy", "instruction_type": "seen", "seed": args.seed,
              "memory_socket": args.socket, "memory_output": args.output, "memory_record_frames": args.record_frames}
    official.main(config)
    if len(rows) != args.episodes:
        raise RuntimeError(f"Official evaluator returned {len(rows)} episodes, expected {args.episodes}.")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(json.dumps({"episodes": rows, "success_rate": sum(row["success"] for row in rows) / len(rows),
                                                     "seed": args.seed, "count": args.episodes, "mode": args.mode,
                                                     "note": "The stock main summary assumes 100; this export uses the actual count."}, indent=2))


if __name__ == "__main__":
    main()
