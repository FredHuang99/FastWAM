"""Simulator-side entry of the memory_v2 closed loop (runs in closed_loop.simulator_python).

Same bootstrap as Codex's /restore-tmp/dense_joint_v1/sim_worker.py: configure the production CuRobo backend in
the main AND in spawned planner processes (multiprocessing spawn re-executes this module as __mp_main__, so the
sim_eval import stays outside the main guard), then hand over to sim_adapter.main in this directory.
"""
from pathlib import Path
import os
import sys

root = Path(os.environ['FW_CAUSAL_SIM_ROOT']).resolve(strict=True)
scripts = str(root / 'scripts/memory_s1')
sys.path.insert(0, scripts)
try:
    import sim_eval
    if Path(sim_eval.__file__).resolve() != root / 'scripts/memory_s1/sim_eval.py':
        raise RuntimeError('Unexpected simulator entry module: ' + str(sim_eval.__file__))
finally:
    sys.path.remove(scripts)

print(f'[backend bootstrap] pid={os.getpid()} module={__name__} source={sim_eval.__file__}', flush=True)

if __name__ == '__main__':
    from sim_adapter import main
    main()
