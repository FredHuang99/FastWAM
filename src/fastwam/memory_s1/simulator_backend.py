"""Explicit CuRobo backend contract; importable without the training package."""
from __future__ import annotations

import functools
import inspect
import os

ENVIRONMENT_KEY = "MEMORY_S1_CUROBO_BACKEND"
SWITCHES = ("use_cuda_kernel", "use_cuda_line_search_kernel", "use_cuda_update_best_kernel")
_active = None


def backend_contract(name="upstream"):
    if name not in ("upstream", "builtin_torch_v1"):
        raise ValueError(f"Unsupported CuRobo backend: {name!r}")
    value = {"name": name, "version": "explicit-curobo-backend-v1"}
    if name == "builtin_torch_v1":
        value.update(optimizer="LBFGS", use_cuda_graph=False, cuda_launch_blocking=True,
                     **dict.fromkeys(SWITCHES, False))
    return value


def configured_backend(cfg):
    return backend_contract(cfg.get("closed_loop", {}).get("curobo_backend", "upstream"))


def configure_backend(name=None):
    global _active
    contract = backend_contract(name if name is not None else os.environ.get(ENVIRONMENT_KEY, "upstream"))
    if _active is not None:
        if _active != contract:
            raise RuntimeError("Cannot change the CuRobo backend inside a running simulator.")
        return dict(_active)
    if contract["name"] == "upstream":
        _active = contract
        return dict(contract)

    os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    from curobo.opt.newton.lbfgs import LBFGSOpt, LBFGSOptConfig
    from curobo.wrap.reacher.motion_gen import MotionGenConfig
    missing = set(SWITCHES) - set(LBFGSOptConfig.__dataclass_fields__)
    if missing:
        raise RuntimeError(f"Unsupported CuRobo flags: {sorted(missing)}")
    previous = getattr(LBFGSOpt, "_fastwam_backend", None)
    if previous is not None:
        if previous != contract:
            raise RuntimeError("CuRobo was already configured with a different backend.")
        _active = contract
        return dict(contract)

    original_init = LBFGSOpt.__init__
    original_load = MotionGenConfig.load_from_robot_config
    signature = inspect.signature(original_load)
    if "use_cuda_graph" not in signature.parameters:
        raise RuntimeError("CuRobo loader does not expose use_cuda_graph.")

    @functools.wraps(original_init)
    def compatible_init(self, config=None):
        if config is not None:
            for key in SWITCHES:
                setattr(config, key, False)
        original_init(self, config)
        for key in SWITCHES:
            setattr(self, key, False)

    @functools.wraps(original_load)
    def load_without_graph(*args, **kwargs):
        bound = signature.bind_partial(*args, **kwargs)
        bound.arguments["use_cuda_graph"] = False
        return original_load(*bound.args, **bound.kwargs)

    LBFGSOpt.__init__ = compatible_init
    MotionGenConfig.load_from_robot_config = staticmethod(load_without_graph)
    LBFGSOpt._fastwam_backend = dict(contract)
    _active = contract
    print(f"[backend] pid={os.getpid()} builtin_torch_v1; fused LBFGS/line-search/update-best=False; cuda_graph=False", flush=True)
    return dict(contract)
