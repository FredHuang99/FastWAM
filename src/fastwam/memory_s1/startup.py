"""Explicit pre-launch checks and a lifetime lock for the owned torchrun process."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

from .common import atomic_json, load_config, read_json
from .eval_state import locked, process_identity, is_alive, cuda_gpu_uuid
from .readiness import verify_materials


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("command", choices=("check", "guard", "materials"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--micro-batch", type=int)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--resume")
    args = parser.parse_args()
    cfg = load_config(args.config)
    run = Path(cfg["paths"]["run"])
    micro = args.micro_batch if args.micro_batch is not None else cfg["micro_batch"]
    workers = args.workers if args.workers is not None else cfg.get("startup", {}).get("expected_world_size", cfg.get("recovery", {}).get("expected_world_size", 8))
    if args.command == "materials":
        print(verify_materials(cfg), flush=True)
        return
    previous = read_json(run / "launcher.json") if (run / "launcher.json").exists() else {}
    if any(is_alive(previous.get(key)) for key in ("owner", "child")):
        raise ValueError("This run already has a live launcher/torchrun process.")
    import torch
    if workers != cfg.get("startup", {}).get("expected_world_size", workers) or torch.cuda.device_count() < workers:
        raise ValueError("Requested workers differ from the configuration or visible GPU count.")
    if micro <= 0 or cfg["global_batch"] % (micro * workers):
        raise ValueError("micro_batch * workers must divide global_batch exactly.")
    if (run / "STOP_REQUESTED").exists():
        raise ValueError("An unresolved STOP_REQUESTED marker exists; inspect the previous stop.")
    if args.resume:
        from .checkpoint import verified_load
        verified_load(args.resume)
    elif (run / "LATEST_LOCAL.json").exists():
        raise ValueError("An existing run requires explicit RESUME.")
    if cfg.get("startup", {}).get("require_ready"):
        report = verify_materials(cfg, require_ready=not args.resume, micro=micro)
        atomic_json(run / "STARTUP_CHECK.json", report)
    if args.command == "check":
        print(f"[startup] passed world={workers} micro={micro} accumulation={cfg['global_batch']//(micro*workers)}", flush=True)
        return
    with locked(run / "training.lock", blocking=False):
        previous = read_json(run / "launcher.json") if (run / "launcher.json").exists() else {}
        if any(is_alive(previous.get(key, {})) for key in ("owner", "child")):
            raise ValueError("An owned launcher/torchrun process is still active for this run.")
        owner = process_identity()
        atomic_json(run / "launcher.json", {"owner": owner, "config": args.config, "world": workers, "micro_batch": micro})
        command = [sys.executable, "-m", "torch.distributed.run", "--standalone", "--nnodes=1",
                   f"--nproc_per_node={workers}", "-m", "fastwam.memory_s1.train", "--config", args.config,
                   "--micro-batch", str(micro)]
        if args.resume:
            command += ["--resume", args.resume]
        environment = dict(os.environ)
        environment.pop("CUDA_LAUNCH_BLOCKING", None)
        atomic_json(run / "TORCHRUN_COMMAND.json", {"argv": command, "owner": owner,
                    "gpu_uuids": [cuda_gpu_uuid(i) for i in range(workers)]})
        # Keep the lock until the actual torchrun child exits, including its checkpoint upload.
        import signal
        def stop(signum, frame):
            (run / "STOP_REQUESTED").touch()
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        child = subprocess.Popen(command, env=environment)
        try:
            atomic_json(run / "launcher.json", {"owner": owner, "child": process_identity(child.pid), "command": command})
            code = child.wait()
        finally:
            if child.poll() is None:
                (run / "STOP_REQUESTED").touch()
                child.terminate()
                child.wait()
        atomic_json(run / "launcher.json", {"owner": owner, "command": command, "exit_code": code})
        raise SystemExit(code)


if __name__ == "__main__":
    main()
