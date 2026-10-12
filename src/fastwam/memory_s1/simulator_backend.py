"""Explicit CuRobo backend contract; importable without the training package."""
from __future__ import annotations

import functools
import inspect
import os

ENVIRONMENT_KEY = "MEMORY_S1_CUROBO_BACKEND"
SWITCHES = ("use_cuda_kernel", "use_cuda_line_search_kernel", "use_cuda_update_best_kernel")
_active = None


def backend_contract(name="upstream"):
    if name not in ("upstream", "builtin_torch_v1", "builtin_torch_async_v2", "fused_graph_v1"):
        raise ValueError(f"Unsupported CuRobo backend: {name!r}")
    value = {"name": name, "version": "explicit-curobo-backend-v1"}
    if name.startswith("builtin_torch"):
        value.update(optimizer="LBFGS", use_cuda_graph=False, cuda_launch_blocking=name == "builtin_torch_v1",
                     **dict.fromkeys(SWITCHES, False))
    elif name == "fused_graph_v1":
        value.update(optimizer="LBFGS", use_cuda_graph=True, cuda_launch_blocking=False,
                     native_validity_guards=True, **dict.fromkeys(SWITCHES, True))
    return value


def configured_backend(cfg):
    return backend_contract(cfg.get("selection_runtime", {}).get("backend", cfg.get("closed_loop", {}).get("curobo_backend", "upstream")))


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

    if contract["cuda_launch_blocking"]:
        os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
    else:
        os.environ.pop("CUDA_LAUNCH_BLOCKING", None)
    from curobo.opt.newton.lbfgs import LBFGSOpt, LBFGSOptConfig
    from curobo.wrap.reacher.motion_gen import MotionGenConfig, MotionGen
    try:
        from .selection_runtime import install_warmup_observer
    except ImportError:
        from selection_runtime import install_warmup_observer
    install_warmup_observer(MotionGen)
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

    if contract["name"] == "fused_graph_v1":
        @functools.wraps(original_init)
        def fused_init(self, config=None):
            if config is not None:
                for key in SWITCHES:
                    setattr(config, key, True)
            # Native constructors retain their dimension/algorithm safety guards.
            original_init(self, config)

        @functools.wraps(original_load)
        def load_with_graph(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)
            bound.arguments["use_cuda_graph"] = True
            return original_load(*bound.args, **bound.kwargs)

        LBFGSOpt.__init__ = fused_init
        MotionGenConfig.load_from_robot_config = staticmethod(load_with_graph)
        try:
            from .fused_evaluation import observe_fused_backend
        except ImportError:
            from fused_evaluation import observe_fused_backend
        observe_fused_backend(LBFGSOpt, MotionGen)
        LBFGSOpt._fastwam_backend = dict(contract)
        _active = contract
        print(f"[backend] pid={os.getpid()} fused_graph_v1; native guards retained; launch_blocking unset", flush=True)
        return dict(contract)

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
    print(f"[backend] pid={os.getpid()} {contract['name']}; fused kernels=False; cuda_graph=False; launch_blocking={contract['cuda_launch_blocking']}", flush=True)
    return dict(contract)
