"""Independent GPU policy workers and distributed resident-model validation."""
from __future__ import annotations

import argparse
import copy
from contextlib import contextmanager
import gc
from multiprocessing.connection import Listener
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
import traceback

from .eval_state import EpisodeQueue, cuda_gpu_uuid, digest, durable_json, is_alive, locked, process_identity, read, signature, stop_mode, summarize

from .simulator_backend import ENVIRONMENT_KEY, configured_backend, backend_contract
from .selection_runtime import duration, event, live_details, format_active, episode_work, failure_report, tail_text
from .eval_state import EvaluationInterrupted, check_stop


def gpu_inventory():
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader"], text=True)
    return {int(row.split(",")[0]): row.split(",")[1].strip() for row in output.strip().splitlines()}


def gpu_uuid_for_model(model):
    return cuda_gpu_uuid(next(model.memory.parameters()).device.index)


def simulator_environment(cfg, gpu_uuid):
    environment = dict(os.environ)
    backend = configured_backend(cfg)
    environment[ENVIRONMENT_KEY] = backend["name"]
    if backend.get("cuda_launch_blocking"):
        environment["CUDA_LAUNCH_BLOCKING"] = "1"
    elif backend["name"] in ("builtin_torch_async_v2", "fused_graph_v1"):
        environment.pop("CUDA_LAUNCH_BLOCKING", None)
    prefix = Path(cfg["closed_loop"]["simulator_python"]).parent.parent
    environment.update(CUDA_VISIBLE_DEVICES=gpu_uuid, CUDA_DEVICE_ORDER="PCI_BUS_ID", CUDA_HOME=str(prefix),
                       PYTHONUNBUFFERED="1", OMP_NUM_THREADS="4", MKL_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4")
    environment["MEMORY_S1_ARCHIVE_STRIDE"] = str(cfg.get("history", {}).get("archive_stride", 8))
    environment["MEMORY_S1_RECORD_FRAME_STRIDE"] = str(cfg.get("diagnostic", {}).get("record_frame_stride", 1))
    environment["PATH"] = str(prefix / "bin") + os.pathsep + environment["PATH"]
    environment["LD_LIBRARY_PATH"] = os.pathsep.join([str(prefix / "lib"), str(prefix / "targets/x86_64-linux/lib"), environment.get("LD_LIBRARY_PATH", "")])
    if backend["name"] == "fused_graph_v1":
        # Match the build environment; do not inherit training CUDA 13 or the old
        # simulator's CUDA 12.4 libraries and editable Python search paths.
        for key in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_PREFIX", "C_INCLUDE_PATH", "CPLUS_INCLUDE_PATH"):
            environment.pop(key, None)
        environment["PATH"] = os.pathsep.join([str(prefix / "bin"), "/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin"])
        environment["LD_LIBRARY_PATH"] = os.pathsep.join([
            str(prefix / "lib"), str(prefix / "targets/x86_64-linux/lib"),
            "/usr/local/nvidia/lib", "/usr/local/nvidia/lib64",
        ])
        environment.update(CC="/usr/bin/gcc-12", CXX="/usr/bin/g++-12", CUDAHOSTCXX="/usr/bin/g++-12",
                           TORCH_CUDA_ARCH_LIST=str(cfg.get("recovery", {}).get("cuda_arch", "9.0")), MAX_JOBS="2",
                           CPATH=os.pathsep.join([str(prefix / "include"), str(prefix / "targets/x86_64-linux/include")]),
                           LIBRARY_PATH=os.pathsep.join([str(prefix / "lib"), str(prefix / "targets/x86_64-linux/lib"), str(prefix / "targets/x86_64-linux/lib/stubs")]),
                           TORCH_EXTENSIONS_DIR=str(Path(cfg["root"]) / cfg.get("hardware", {}).get("extensions_directory", "outputs/fused_environment_h100_v1/torch_extensions_torch260_cu126_sm90")))
    lock_root = Path(cfg["root"]) / cfg.get("hardware", {}).get("warmup_lock_directory", str(Path(cfg["paths"]["run"]) / "selection_locks"))
    lock_root.mkdir(parents=True, exist_ok=True)
    environment["MEMORY_S1_WARMUP_LOCK"] = str(lock_root / f"{gpu_uuid}.warmup.lock")
    return environment


def terminate_owned(process, timeout=20):
    # Every child passed here was created with start_new_session=True by this module.
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def cleanup_simulators(root):
    for path in Path(root).rglob("simulator_owner.json"):
        owner = read(path)
        if not is_alive(owner):
            continue
        # These leaders were created in independent sessions by execute_job.
        if os.getpgid(owner["pid"]) != owner["pid"]:
            raise RuntimeError(f"Unexpected simulator process group: {path}")
        os.killpg(owner["pid"], signal.SIGTERM)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and is_alive(owner):
            time.sleep(0.1)
        if is_alive(owner):
            os.killpg(owner["pid"], signal.SIGKILL)


def protocol(cfg, mode):
    loop = cfg["closed_loop"]
    internal = mode in ("diagnostic", "internal")
    root = Path(cfg["root"]) / loop["simulator_root"]
    inventory = {}
    for directory in ("envs", "scripts", "env_cfg", "description"):
        for path in sorted((root / directory).rglob("*")):
            if path.is_file() and path.suffix in (".py", ".yml", ".yaml", ".json") and "__pycache__" not in path.parts:
                inventory[str(path.relative_to(root))] = digest(path)
    value = {"seed": loop["internal_seed"] if internal else loop["official_seed"],
            "count": loop["internal_episodes"] if internal else loop["official_episodes"],
            "tasks": cfg.get("comparison", {}).get("tasks", ["put_back_block", "swap_blocks"]), "task_config": "demo_clean", "instruction_type": "seen",
            "candidate_rule": "first K expert-feasible increasing seeds", "language_seed_rule": "scene_seed xor 0x51A17, freeze literal string",
            "python_scene_random": "random.seed(scene_seed) before expert and policy setup",
            "simulator_source": signature(inventory), "simulator_backend": configured_backend(cfg)}
    filtering = backend_contract(loop.get("curobo_backend", "upstream"))
    if filtering != value["simulator_backend"]:
        value["scene_filter_backend"] = filtering
    return value


def prepare_scenes(cfg, mode, gpu_uuids, stop_root):
    contract = protocol(cfg, mode)
    diagnostic = cfg.get("diagnostic", {})
    if cfg.get("selection_runtime", {}).get("profile") == "fused-resident" and not diagnostic.get("scenes_from"):
        raise ValueError("Fused comparison requires inherited scenes; expert search is disabled")
    if diagnostic.get("scenes_from"):
        if mode != "diagnostic":
            source = Path(diagnostic["scenes_from"])
            saved = read(source)
            if saved["contract"] != contract:
                raise ValueError("Frozen evaluation scenes refer to another complete protocol.")
            for task in contract["tasks"]:
                rows = [row for row in saved["scenes"] if row["task"] == task]
                if len(rows) != contract["count"] or len({row["seed"] for row in rows}) != len(rows):
                    raise ValueError("Full evaluations cannot borrow a prefix or incomplete scene bank.")
            if len(saved["scenes"]) != contract["count"] * len(contract["tasks"]):
                raise ValueError("Frozen scene bank has extra tasks.")
            return contract, saved["scenes"], source
        source = Path(diagnostic["scenes_from"])
        saved = read(source)
        if saved["contract"] != contract:
            raise ValueError("Old scene protocol/simulator changed; do not silently reuse different scenes.")
        count = int(diagnostic.get("episodes_per_task", 2))
        if count <= 0:
            raise ValueError("A positive diagnostic scene count is required.")
        scenes = []
        for task in contract["tasks"]:
            candidates = sorted((s for s in saved["scenes"] if s["task"] == task), key=lambda s: s["ordinal"])
            if len(candidates) < count or len({s["seed"] for s in candidates}) != len(candidates):
                raise ValueError(f"Missing or duplicate old scenes for {task}.")
            scenes.extend(candidates[:count])
        borrowed = {**contract, "subset_per_task": count, "parent_scenes_sha": digest(source),
                    "purpose": "base_compatibility_prefix_diagnostic"}
        directory = Path(stop_root) / "borrowed_scenes"
        directory.mkdir(parents=True, exist_ok=True)
        durable_json(directory / "manifest.json", {"contract": borrowed, "scenes": scenes, "source": str(source)})
        print(f"[scenes] reused {len(scenes)} frozen scenes from {source}; expert replanning skipped", flush=True)
        return borrowed, scenes, directory
    # Candidate acceptance is always determined by the existing reference backend.
    # Accelerated rollouts reuse the same expert-feasible seeds and literal instructions.
    planning_cfg = copy.deepcopy(cfg)
    planning_cfg.setdefault("selection_runtime", {})["backend"] = cfg["closed_loop"].get("curobo_backend", "upstream")
    filtering_contract = protocol(planning_cfg, mode)
    root = Path(cfg["paths"]["run"]) / "scene_manifests" / signature(filtering_contract)[:16]
    root.mkdir(parents=True, exist_ok=True)
    with locked(root / "planner.lock", blocking=False):
        durable_json(root / "contract.json", filtering_contract)
        processes = []
        pending = [task for task in contract["tasks"]
                   if not (root / f"{task}.json").exists() or not read(root / f"{task}.json").get("complete")]
        started, last_print = time.monotonic(), 0
        limit = 6 * 3600 if mode == "official" else 2 * 3600
        durable_json(Path(stop_root) / "planning.json", {"directory": str(root), "contract": contract})
        try:
            while pending or processes:
                if (Path(cfg["paths"]["run"]) / "STOP_REQUESTED").exists():
                    durable_json(Path(stop_root) / "STOP.json", {"mode": "now", "reason": "training safe stop"})
                check_stop(stop_root)
                if time.monotonic()-started > limit:
                    raise TimeoutError(f"Scene planning exceeded {duration(limit)}; saved seeds retained: {root}")
                busy = {uuid for _, _, _, uuid in processes}
                for uuid in gpu_uuids:
                    if uuid in busy or not pending or stop_mode(stop_root):
                        continue
                    task = pending.pop(0)
                    output = root / f"{task}.json"
                    command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/sim_eval.py"),
                               "--operation", "plan", "--task", task, "--output", str(output), "--contract", str(root / "contract.json"),
                               "--episodes", str(contract["count"]), "--seed", str(contract["seed"]),
                               "--gpu-uuid", uuid, "--stop-root", str(stop_root)]
                    environment = simulator_environment(planning_cfg, uuid)
                    environment["MEMORY_S1_PROGRESS_ROOT"] = str(root / f"{task}.progress")
                    log = (root / f"{task}.planner.log").open("a", encoding="utf-8")
                    process = subprocess.Popen(command, env=environment,
                                               cwd=Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"], stdout=log,
                                               stderr=subprocess.STDOUT, start_new_session=True)
                    processes.append((task, process, log, uuid))
                    durable_json(root / f"{task}.owner.json", process_identity(process.pid))
                    event(stop_root, "planning_dispatch", task=task, gpu=uuid, queued=pending)
                for item in list(processes):
                    task, process, log, uuid = item
                    if process.poll() is not None:
                        terminate_owned(process)
                        log.close()
                        processes.remove(item)
                        if stop_mode(stop_root):
                            raise EvaluationInterrupted("Scene filtering stopped; unfinished seed will run again.")
                        if process.returncode:
                            raise RuntimeError(f"Scene planner failed: {root / (task + '.planner.log')}")
                if stop_mode(stop_root) and not processes:
                    raise EvaluationInterrupted("Scene filtering drained.")
                if time.monotonic()-last_print >= 15:
                    counts = {task: len(read(root / f"{task}.json")["scenes"]) if (root / f"{task}.json").exists() else 0 for task in contract["tasks"]}
                    details = live_details(root)
                    durable_json(Path(stop_root) / "status.json", {"stage": "planning", "accepted": counts,
                                 "required_per_task": contract["count"], "queued": pending, "active": details,
                                 "elapsed_seconds": time.monotonic()-started, "eta_seconds": None})
                    description = "; ".join(f"{r['phase']} {r['state']} batch={r.get('batch', '-')} age={duration(r['phase_age_seconds'])}" for r in details)
                    print(f"[planning heartbeat] accepted={counts}/{contract['count']} per task | elapsed={duration(time.monotonic()-started)} | ETA=unknown | {description} | queued={pending}", flush=True)
                    last_print = time.monotonic()
                time.sleep(.5)
        finally:
            for _, process, log, _ in processes:
                terminate_owned(process)
                log.close()
        scenes = []
        for task in contract["tasks"]:
            value = read(root / f"{task}.json")
            if value["contract"] != filtering_contract or not value["complete"] or value["sha256"] != signature(value["scenes"]):
                raise ValueError("Incomplete/corrupt scene manifest.")
            # Runtime timings and GPU assignments are provenance, not scene identity.
            scenes.extend([{key: row[key] for key in ("task", "seed", "ordinal", "instruction", "episode_info")} for row in value["scenes"]])
        return contract, scenes, root


def evaluation_identity(cfg, contract, scenes, conditions, weights, evidence, record_frames):
    from .history import online_contract
    from .protocol import inference_contract
    root = Path(cfg["root"])
    source = {}
    for directory in ("src/fastwam/memory_s1", "src/fastwam/models/wan22", "scripts/memory_s1"):
        for path in sorted((root / directory).rglob("*.py")):
            source[str(path.relative_to(root))] = digest(path)
    return signature({"protocol": contract, "scenes": scenes, "conditions": conditions,
                      "base": digest(cfg["paths"]["base"]), "stats": digest(cfg["paths"]["stats"]),
                      "vae": digest(cfg["paths"]["vae"]), "t5": digest(cfg["paths"]["t5"]),
                      "weights": digest(weights) if weights else "gate_zero_diagnostic_only",
                      "evidence": evidence, "source": source, "noise_seed": cfg["seed"],
                      "predict": 32, "execute": 16, "denoising_steps": 10, "record_frames": record_frames,
                      "history_sampling": cfg.get("history", {"online_period": 8, "archive_stride": 8}),
                      "history_algorithm": online_contract(cfg),
                      "inference_contract": inference_contract(), "diagnostic": cfg.get("diagnostic", {}),
                      "selection_runtime": cfg.get("selection_runtime", {})})


@contextmanager
def loading_slot(root, count=2):
    import fcntl
    stream = None
    try:
        while stream is None:
            if stop_mode(root) or (Path(root) / "ABORT.json").exists():
                raise RuntimeError("Stopped before loading a policy model.")
            for index in range(count):
                candidate = (Path(root) / f"load_{index}.lock").open("a+")
                try:
                    fcntl.flock(candidate, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    stream = candidate
                    break
                except BlockingIOError:
                    candidate.close()
            if stream is None:
                time.sleep(1)
        yield
    finally:
        if stream:
            stream.close()


def execute_job(model, encoders, cfg, queue, job, gpu_uuid, record_frames, evidence, timeout, resident=None):
    from .sim_bridge import InferenceSession
    directory = queue.root / job["directory"]
    started = time.monotonic()
    temporary = Path("/tmp/mwam-eval") / signature(str(queue.root.resolve()))[:12]
    temporary.mkdir(parents=True, exist_ok=True)
    socket_path = temporary / f"p{os.getpid()}.sock"
    socket_path.unlink(missing_ok=True)
    if resident and resident.get("task") != job["scene"]["task"]:
        terminate_owned(resident["process"])
        resident.clear()
    key = resident["key"] if resident else os.urandom(24)
    process = None
    completed = False
    session = InferenceSession(model, cfg, encoders, job["condition"], directory, evidence, cfg["seed"])
    try:
        with Listener(str(socket_path), family="AF_UNIX", authkey=key) as listener, (directory / "simulator.log").open("w", encoding="utf-8") as log:
            listener._listener._socket.settimeout(1)
            environment = simulator_environment(cfg, gpu_uuid)
            environment["MEMORY_S1_RPC_KEY"] = key.hex()
            progress_root = queue.root / "simulator_progress" / str(os.getpid())
            environment["MEMORY_S1_PROGRESS_ROOT"] = str(progress_root)
            command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/sim_eval.py"),
                       "--operation", "episode", "--job", str(directory / "job.json"), "--output", str(directory),
                       "--socket", str(socket_path), "--seed", str(cfg["seed"]), "--gpu-uuid", gpu_uuid,
                       "--stop-root", str(queue.root)]
            command += ["--scene-count", str(sum(j["scene"]["task"] == job["scene"]["task"]
                          and j["condition"] == job["condition"] for j in queue.snapshot()["jobs"]))]
            if cfg.get("selection_runtime", {}).get("qualification"):
                command.append("--qualification-trace")
            if resident is not None:
                service = queue.root / "resident" / str(os.getpid())
                service.mkdir(parents=True, exist_ok=True)
                command += ["--service", str(service)]
            if record_frames or cfg.get('diagnostic',{}).get('capture_evidence',False):
                command.append("--record-frames")
            diagnostic = cfg.get("diagnostic", {})
            if diagnostic.get("max_targets", 0):
                command += ["--max-targets", str(diagnostic["max_targets"])]
            if diagnostic.get("record_feedback", False):
                command.append("--record-feedback")
            if resident:
                process = resident["process"]
                if process.poll() is not None:
                    raise RuntimeError("Resident simulator exited between episodes; resume will create a new worker.")
                durable_json(service / "next.json", {"job": str(directory / "job.json"), "output": str(directory)})
            else:
                bootstrap = (service / "bootstrap.log").open("a", encoding="utf-8") if resident is not None else None
                try:
                    process = subprocess.Popen(command, cwd=Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"],
                                               env=environment, stdout=bootstrap or log, stderr=subprocess.STDOUT, start_new_session=True)
                finally:
                    if bootstrap:
                        bootstrap.close()
                if resident is not None:
                    resident.update(process=process, key=key, task=job["scene"]["task"])
                    durable_json(service / "simulator_owner.json", process_identity(process.pid))
            if resident is None:
                durable_json(directory / "simulator_owner.json", process_identity(process.pid))
            while process.poll() is None:
                check_stop(queue.root)
                if resident is not None and (directory / "service_complete.json").exists():
                    marker = read(directory / "service_complete.json")
                    if marker != {"job": job["id"], "attempt": job["attempt"]}:
                        raise ValueError("Resident result belongs to another episode")
                    break
                if (Path(cfg["paths"]["run"]) / "STOP_REQUESTED").exists():
                    durable_json(queue.root / "STOP.json", {"mode": "now", "reason": "training safe stop"})
                if time.monotonic() - started > timeout:
                    raise TimeoutError(f"Episode exceeded {timeout}s; inspect simulator.log")
                try:
                    connection = listener.accept()
                except TimeoutError:
                    continue
                with connection:
                    if not connection.poll(30):
                        raise TimeoutError("RPC client connected without sending a request.")
                    request = connection.recv()
                    try:
                        if request["command"] == "reset":
                            session.reset()
                            response = {"ok": True}
                        elif request["command"] == "decide":
                            inference_started = time.monotonic()
                            progress = queue.root / "workers" / f"progress_{job['worker']}"
                            event(progress, "inference", task=job["scene"]["task"], seed=job["scene"]["seed"],
                                  job_id=job["id"], targets=request["current_id"])
                            response = {"ok": True, **session.decide(request)}
                            event(progress, "inference", "complete", task=job["scene"]["task"],
                                  seed=job["scene"]["seed"], seconds=time.monotonic()-inference_started)
                        else:
                            raise ValueError("Unknown RPC command.")
                    except Exception:
                        response = {"ok": False, "error": traceback.format_exc()}
                    connection.send(response)
            result_path = directory / "simulator_result.json"
            if not result_path.is_file():
                startup_log = service / "bootstrap.log" if resident is not None else directory / "simulator.log"
                raise RuntimeError(f"Simulator exited {process.poll()} before producing its result. "
                                   f"Startup log: {startup_log}\n{tail_text(startup_log)}")
            if resident is None:
                terminate_owned(process)
            value = read(result_path)
            if value["status"] == "complete" and process.returncode not in (None, 0):
                raise RuntimeError(f"Simulator failed after producing a result: exit={process.returncode}")
        if value["status"] == "complete":
            if value.get("simulator_backend") != configured_backend(cfg):
                raise ValueError("Simulator returned a different CuRobo backend contract.")
            value["wall_seconds"] = time.monotonic() - started
            value["policy_gpu_uuid"] = gpu_uuid
            queue.publish(job, value)
            completed = True
        else:
            queue.finish(job, value["status"], value.get("error"))
    except EvaluationInterrupted as error:
        queue.finish(job, "interrupted", str(error))
    except Exception:
        error = traceback.format_exc()
        durable_json(directory / "error.json", {"error": error})
        queue.finish(job, "error", error)
        raise
    finally:
        if process is not None and (resident is None or not completed):
            terminate_owned(process)
            if resident is not None:
                resident.clear()
        socket_path.unlink(missing_ok=True)
        session.reset()


def worker_loop(cfg, output, worker, weights=None, resident_model=None, record_frames=False, evidence=None, timeout=2400, scene_cap=None):
    import torch
    from .model import S1Model, load_observation_encoders
    queue = EpisodeQueue(output)
    own_model = resident_model is None
    model = resident_model
    encoders = None
    resident = {} if cfg.get("selection_runtime", {}).get("resident_simulator") else None
    try:
        load_started = time.monotonic()
        print(f"[worker {worker}] waiting for model/encoder loading slot", flush=True)
        event(queue.root / "workers" / f"progress_{worker}", "model_load", worker=worker)
        with loading_slot(queue.root):
            if own_model:
                model = S1Model(cfg, torch.device("cuda:0"))
                if weights:
                    value = torch.load(weights, map_location="cpu", weights_only=True)
                    if value["identity"]["base_sha256"] != digest(cfg["paths"]["base"]) or value["identity"]["stats_sha256"] != digest(cfg["paths"]["stats"]):
                        raise ValueError("Memory weights refer to different base/statistics.")
                    model.memory.load_state_dict(value["memory"], strict=True)
            model.eval()
            encoders = load_observation_encoders(cfg, next(model.memory.parameters()).device)
        print(f"[worker {worker}] model/encoders ready; load_and_wait_seconds={time.monotonic()-load_started:.1f}", flush=True)
        event(queue.root / "workers" / f"progress_{worker}", "model_load", "complete", worker=worker, seconds=time.monotonic()-load_started)
        uuid = gpu_uuid_for_model(model)
        durable_json(queue.root / "workers" / f"{worker}.json", {"owner": process_identity(), "gpu_uuid": uuid, "torch": torch.__version__, "cuda": torch.version.cuda})
        while True:
            if resident_model is not None and (Path(cfg["paths"]["run"]) / "STOP_REQUESTED").exists():
                durable_json(queue.root / "STOP.json", {"mode": "now", "reason": "training safe stop"})
            job = queue.claim(worker, scene_cap=scene_cap)
            if job is None:
                break
            print(f"[worker {worker}] start {job['id']} attempt={job['attempt']} GPU={uuid}", flush=True)
            execute_job(model, encoders, cfg, queue, job, uuid, record_frames, evidence, timeout, resident)
            print(f"[worker {worker}] finish {job['id']}", flush=True)
            if resident_model is not None and worker == "rank_0":
                status = progress(queue, int(os.environ.get("WORLD_SIZE", 1)))
                print(f"[validation] {status['completed']}/{status['total']} ETA~{duration(status['eta_seconds'])} provisional={status['eta_provisional']}", flush=True)
                upload_results(cfg, output)
    except EvaluationInterrupted:
        event(queue.root / "workers" / f"progress_{worker}", "worker", "interrupted", worker=worker)
        raise
    except Exception:
        error = traceback.format_exc()
        durable_json(queue.root / "workers" / f"error_{worker}.json", {"error": error, "owner": process_identity()})
        event(queue.root / "workers" / f"progress_{worker}", "worker", "error", worker=worker, error=error)
        raise
    finally:
        if resident:
            terminate_owned(resident["process"])
        del encoders
        gc.collect()
        torch.cuda.empty_cache()
        if not own_model and model is not None:
            model.train()


def progress(queue, workers):
    value = queue.snapshot()
    completed = [job for job in value["jobs"] if job["state"] == "complete"]
    by_task, rows = {}, []
    for task in ("put_back_block", "swap_blocks"):
        selected = [read(queue.root / job["directory"] / "result.json") for job in completed if job["scene"]["task"] == task]
        rows.extend(selected)
        by_task[task] = {"completed": len(selected),
                         "measured_mean_seconds": sum(row["wall_seconds"] for row in selected)/len(selected) if selected else None}
    active = live_details(queue.root / "simulator_progress") + live_details(queue.root / "workers")
    config = read(queue.root / "evaluation.json").get("config", {})
    limits = config.get("selection_runtime", {}).get("eta_target_limits", {})
    prefix = config.get("diagnostic", {}).get("max_targets", 0)
    if prefix:
        limits = {task: min(cap, prefix) for task, cap in limits.items()}
        limits.update({job["scene"]["task"]: prefix for job in value["jobs"] if job["scene"]["task"] not in limits})
    projection = episode_work(value["jobs"], rows, active, limits, workers)
    launcher = read(queue.root / "launcher.json") if (queue.root / "launcher.json").exists() else {}
    result = {"stage": "episodes", "completed": len(completed), "total": len(value["jobs"]), "by_task": by_task,
              **projection, "elapsed_seconds": time.time()-launcher.get("started", value["created"]),
              "active": active,
              "stop": stop_mode(queue.root), "errors": sum(j["state"] == "error" for j in value["jobs"])}
    durable_json(queue.root / "status.json", result)
    return result


def upload_results(cfg, output):
    if not cfg["hf"]["enabled"]:
        return
    command = [cfg["hf"]["python"], str(Path(cfg["root"]) / "scripts/memory_s1/hf_tools.py"), "eval-results",
               "--repo", cfg["hf"]["backup_repo"], "--evaluation", str(output), "--run-id", Path(cfg["paths"]["run"]).name,
               "--quota-gib", str(cfg["hf"]["quota_gib"]), "--reserve-gib", str(cfg["hf"]["reserve_gib"])]
    started = time.monotonic()
    subprocess.run(command, check=True, timeout=600)
    from .common import append_jsonl
    append_jsonl(Path(output) / "upload_timings.jsonl", {"seconds": time.monotonic() - started, "time": time.time()})


def standalone(args):
    from .common import load_config
    from .data import load_evidence
    cfg = load_config(args.config)
    from .protocol import inference_contract, verify_released_prompt
    verify_released_prompt(cfg["root"])
    diagnostic = cfg.setdefault("diagnostic", {})
    for key in ("scenes_from", "episodes_per_task", "max_targets", "compatibility_report"):
        value = getattr(args, key, None)
        if value is not None:
            diagnostic[key] = str(Path(value).resolve()) if key in ("scenes_from", "compatibility_report") else value
    if diagnostic.get("require_compatibility"):
        from .common import code_version
        if not diagnostic.get("compatibility_report"):
            raise ValueError("Pass --compatibility-report with a completed same-input numerical comparison first.")
        report = read(diagnostic["compatibility_report"])
        current_code = code_version(cfg["root"])
        if not (report.get("complete") is True and report.get("passed") is True
                and report.get("inference_contract") == inference_contract()
                and report.get("base_sha256") == digest(cfg["paths"]["base"])
                and report.get("stats_sha256") == digest(cfg["paths"]["stats"])
                and report.get("vae_sha256") == digest(cfg["paths"]["vae"])
                and report.get("t5_sha256") == digest(cfg["paths"]["t5"])
                and all(report.get("code", {}).get(key) == current_code[key] for key in ("implementation_sha", "core_sha"))):
            raise ValueError("Compatibility failed or refers to a different base/statistics/implementation. Preserve its reports; do not run the closed loop yet.")
        diagnostic["compatibility_sha256"] = digest(diagnostic["compatibility_report"])
    if cfg.get("diagnostic_only") and args.mode != "diagnostic":
        raise ValueError("This configuration is only for base diagnostics.")
    qualification = cfg.get("selection_runtime", {}).get("qualification", False)
    s1_prefix = (diagnostic.get('s1_investigation') is True and args.mode == 'diagnostic'
                 and diagnostic.get('scenes_from') and diagnostic.get('episodes_per_task') == 1
                 and diagnostic.get('max_targets') in (32,160)
                 and (diagnostic.get('max_targets') == 32 or diagnostic.get('phase_trace') is True))
    if diagnostic.get("max_targets", 0) and (args.mode != "diagnostic" or args.weights) and not (qualification or s1_prefix):
        raise ValueError("A short prefix is a base diagnostic, not a trained/official evaluation.")
    if diagnostic.get("max_targets", 0) < 0:
        raise ValueError("max-targets cannot be negative.")
    if diagnostic.get("episodes_per_task") and not diagnostic.get("scenes_from"):
        raise ValueError("Pass --scenes-from to select a subset of previously frozen scenes.")
    from .history import override_online
    override_online(cfg, getattr(args, "history_period", None), getattr(args, "history_cycle", None), getattr(args, "history_phase", None), getattr(args, "history_mode", None))
    if not cfg["closed_loop"]["enabled"]:
        raise ValueError("Closed-loop evaluation is disabled in this configuration.")
    output = Path(args.output).resolve()
    scene_cap = getattr(args, 'scene_cap', None)
    if scene_cap is not None and (scene_cap < 1 or args.mode != 'internal' or diagnostic.get('max_targets')):
        raise ValueError('A scene claim cap is only valid for complete internal episodes.')
    output.mkdir(parents=True, exist_ok=True)
    inventory = gpu_inventory()
    uuids = [inventory[int(index)] for index in args.gpus.split(",")]
    if len(uuids) != len(set(uuids)):
        raise ValueError("Each worker must have a distinct GPU.")
    conditions = args.conditions
    if not args.weights and (args.mode != "diagnostic" or any(c not in ("gate_zero", "native_base") for c in conditions)):
        raise ValueError("Untrained diagnostics support gate_zero/native_base only.")
    if "native_base" in conditions and (args.mode != "diagnostic" or args.weights):
        raise ValueError("native_base is an untrained released-base diagnostic.")
    evidence = load_evidence(args.evidence) if args.evidence else None
    if any(c.startswith("delete_") for c in conditions) and evidence is None:
        raise ValueError("Deletion conditions require a reviewed evidence manifest.")
    options = cfg.get("selection_runtime", {})
    if options.get("qualification"):
        expected_count = 1 if options.get("profile") == "fused-resident" else 2
        if args.mode != "diagnostic" or diagnostic.get("max_targets") != 32 or diagnostic.get("episodes_per_task") != expected_count:
            raise ValueError(f"Acceleration qualification requires {expected_count} 32-target scene(s) per task")
    elif options.get("profile", "serial") != "serial":
        from types import SimpleNamespace
        from .posttrain import verify_qualification
        verify_qualification(cfg, SimpleNamespace(runtime_profile=options["profile"], qualification_report=options.get("qualification_report")))
    with locked(output / "launcher.lock", blocking=False):
        durable_json(output / "launcher.json", {"owner": process_identity(), "argv": sys.argv, "gpu_uuids": uuids, "started": time.time()})
        if args.resume:
            for path in (output / "workers").glob("*.json"):
                value = read(path)
                if is_alive(value.get("owner")):
                    raise RuntimeError(f"An old worker is still alive: {path}")
            for path in output.rglob("simulator_owner.json"):
                if is_alive(read(path)):
                    raise RuntimeError(f"An old simulator is still alive: {path}; stop it before resuming.")
            (output / "STOP.json").unlink(missing_ok=True)
        def stop(signum, frame):
            durable_json(output / "STOP.json", {"mode": "now", "signal": signum, "time": time.time()})
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        contract, scenes, manifest = prepare_scenes(cfg, args.mode, uuids, output)
        print("[prepare] checking evaluation source and resource checksums", flush=True)
        identity = evaluation_identity(cfg, contract, scenes, conditions, args.weights, evidence, args.record_frames)
        queue = EpisodeQueue(output)
        queue.initialize(identity, scenes, conditions, args.resume)
        if diagnostic.get("compatibility_report"):
            source = Path(diagnostic["compatibility_report"]).parent
            destination = output / "compatibility"
            destination.mkdir(exist_ok=True)
            for name in ("summary.json", "cases.jsonl"):
                if (source / name).is_file():
                    shutil.copy2(source / name, destination / name)
        durable_json(output / "evaluation.json", {"config": cfg, "mode": args.mode, "conditions": conditions,
                                                   "scene_cap": scene_cap,
                                                   "weights": str(Path(args.weights).resolve()) if args.weights else None,
                                                   "evidence": evidence, "record_frames": args.record_frames, "scene_manifest": str(manifest),
                                                   "inference_contract": inference_contract()})
        durable_json(output / "scenes.json", {"contract": contract, "scenes": scenes})
        if all(job["state"] == "complete" for job in queue.snapshot()["jobs"]):
            summarize(output, args.mode, require_complete=True)
            print("[resume] all episodes verified; no model or simulator will be loaded", flush=True)
            return 0
        processes = []
        try:
            for worker, uuid in enumerate(uuids):
                directory = output / "workers"
                directory.mkdir(exist_ok=True)
                log = (directory / f"worker_{worker}.log").open("a", encoding="utf-8")
                environment = dict(os.environ)
                if options.get("backend") == "fused_graph_v1":
                    environment.pop("CUDA_LAUNCH_BLOCKING", None)
                environment.update(CUDA_VISIBLE_DEVICES=uuid, CUDA_DEVICE_ORDER="PCI_BUS_ID", PYTHONUNBUFFERED="1",
                                   OMP_NUM_THREADS="4", MKL_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4")
                command = [sys.executable, "-u", "-m", "fastwam.memory_s1.eval_parallel", "worker", "--output", str(output),
                           "--worker", str(worker), "--timeout", str(args.episode_timeout)]
                process = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                processes.append((process, log))
                durable_json(directory / f"launcher_{worker}.json", {"owner": process_identity(process.pid), "gpu_uuid": uuid})
            last_print, last_uploaded = 0, 0
            last_upload_time = time.monotonic()
            workers_started = time.monotonic()
            while any(process.poll() is None for process, _ in processes):
                if stop_mode(output) == "now":
                    break
                hung = [j["id"] for j in queue.snapshot()["jobs"] if j["state"] == "running" and time.time() - j["started"] > args.episode_timeout + 60]
                if hung or time.monotonic() - workers_started > len(scenes) * len(conditions) * args.episode_timeout + 1800:
                    durable_json(output / "ABORT.json", {"error": "Worker timeout", "jobs": hung})
                    durable_json(output / "STOP.json", {"mode": "now", "reason": "worker timeout"})
                    break
                if any(process.poll() not in (None, 0) for process, _ in processes):
                    if stop_mode(output):
                        break
                    durable_json(output / "ABORT.json", {"error": "A policy worker failed; inspect workers/*.log"})
                    break
                if time.monotonic() - last_print >= 15:
                    status = progress(queue, len(uuids))
                    summarize(output, args.mode)
                    print(f"[progress] {status['completed']}/{status['total']} elapsed={duration(status['elapsed_seconds'])} "
                          f"rollout_remaining~{duration(status['eta_seconds'])} source={status['eta_reason']} "
                          f"borrowed_task_estimates={status['borrowed_task_estimates']} "
                          "(measured target rate; initialization/cleanup/upload separate)", flush=True)
                    for row in status["active"]:
                        print(f"[active] {format_active(row)}", flush=True)
                    last_print = time.monotonic()
                    if args.hf_results and status["completed"] > last_uploaded and (status["completed"]-last_uploaded >= 5 or time.monotonic()-last_upload_time >= 600):
                        try:
                            upload_results(cfg, output)
                            last_uploaded = status["completed"]
                            last_upload_time = time.monotonic()
                        except Exception:
                            durable_json(output / "UPLOAD_FAILED.json", {"error": traceback.format_exc()})
                            durable_json(output / "STOP.json", {"mode": "drain", "time": time.time(), "deadline": time.time()+120})
                time.sleep(1)
        finally:
            for process, log in processes:
                if process.poll() is None:
                    terminate_owned(process)
                log.close()
            cleanup_simulators(output)
        summary = summarize(output, args.mode)
        selected = [j for j in queue.snapshot()['jobs'] if scene_cap is None or j['scene']['ordinal'] < scene_cap]
        requested_complete = bool(selected) and all(j['state'] == 'complete' for j in selected)
        durable_json(output / 'REQUESTED_SCOPE.json', {'scene_cap': scene_cap, 'complete': requested_complete,
                     'requested_episodes': len(selected), 'full_queue_complete': summary['complete']})
        if not requested_complete or (output / "ABORT.json").exists():
            details = failure_report(output)
            (output / "FAILURE_DETAILS.txt").write_text(details+"\n", encoding="utf-8")
            print(f"[evaluation failure]\n{details}", flush=True)
        if args.hf_results:
            upload_results(cfg, output)
        progress(queue, len(uuids))
        print(f"[finish] complete={summary['complete']} completed={summary['completed_episodes']}/{summary['planned_episodes']} output={output}", flush=True)
        return 0 if requested_complete and not (output / "ABORT.json").exists() and not (output / "UPLOAD_FAILED.json").exists() else 2


def distributed_validation(cfg, weights, output, resident_model):
    import torch.distributed as dist
    from .checkpoint import random_state, restore_random_state
    initialized = dist.is_initialized()
    if not initialized and int(os.environ.get("WORLD_SIZE", "1")) != 1:
        raise ValueError("Multi-worker validation requires an initialized process group.")
    rank, world = (dist.get_rank(), dist.get_world_size()) if initialized else (0, 1)
    distributed = world > 1
    device = next(resident_model.memory.parameters()).device
    output = Path(output)
    state = random_state()
    validation_started = time.time()
    box = [None]
    guard = None
    try:
        if rank == 0:
            try:
                guard = locked(output / "launcher.lock", blocking=False)
                guard.__enter__()
                (output / "STOP.json").unlink(missing_ok=True)
                uuids = list(gpu_inventory().values())[:min(2, world)]
                contract, scenes, manifest = prepare_scenes(cfg, "internal", uuids, output)
                identity = evaluation_identity(cfg, contract, scenes, ["full"], weights, None, False)
                EpisodeQueue(output).initialize(identity, scenes, ["full"], resume=(output / "queue.json").exists())
                from .protocol import inference_contract
                durable_json(output / "evaluation.json", {"mode": "internal", "config": cfg, "weights": str(weights),
                                                           "inference_contract": inference_contract()})
                durable_json(output / "scenes.json", {"contract": contract, "scenes": scenes})
                box[0] = {"ok": True}
            except Exception:
                box[0] = {"ok": False, "error": traceback.format_exc()}
        if distributed:
            dist.broadcast_object_list(box, src=0, device=device)
        if not box[0]["ok"]:
            raise RuntimeError(box[0]["error"])
        error = None
        try:
            worker_loop(cfg, output, f"rank_{rank}", resident_model=resident_model)
        except Exception:
            error = traceback.format_exc()
            durable_json(output / "ABORT.json", {"rank": rank, "error": error})
        if distributed:
            errors = [None] * world
            dist.all_gather_object(errors, error)
        else:
            errors = [error]
        box = [None]
        if rank == 0:
            try:
                if any(errors):
                    raise RuntimeError("\n".join(e for e in errors if e))
                result = summarize(output, "internal", require_complete=False)
                upload_results(cfg, output)
                timing_path = output / "upload_timings.jsonl"
                import json
                timings = [json.loads(line) for line in timing_path.read_text().splitlines()] if timing_path.exists() else []
                result["hf_upload_seconds_this_launch"] = sum(row["seconds"] for row in timings if row["time"] >= validation_started)
                box[0] = {"ok": True, "result": result}
            except Exception:
                box[0] = {"ok": False, "error": traceback.format_exc()}
        if distributed:
            dist.broadcast_object_list(box, src=0, device=device)
        if not box[0]["ok"]:
            raise RuntimeError(box[0]["error"])
        return box[0]["result"]
    finally:
        if guard is not None:
            guard.__exit__(None, None, None)
        restore_random_state(state)
        resident_model.train()


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--mode", choices=("diagnostic", "internal", "official"), required=True)
    run.add_argument("--conditions", nargs="+", default=["gate_zero"])
    run.add_argument("--history-period", type=int)
    run.add_argument("--history-mode", choices=("fixed", "cycle", "seeded_per_decision"))
    run.add_argument("--history-phase", type=int, help="Override the episode-seeded phase with a fixed residue")
    run.add_argument("--history-cycle", help="Decision periods, e.g. 8,4,16")
    run.add_argument("--weights")
    run.add_argument("--evidence")
    run.add_argument("--gpus", default="0")
    run.add_argument("--scene-cap", type=int, help="Claim ordinals below this cap; retain full queue identity for continuation")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--record-frames", action="store_true")
    run.add_argument("--hf-results", action="store_true")
    run.add_argument("--episode-timeout", type=int, default=2400)
    run.add_argument("--scenes-from", help="Reuse an existing frozen scenes.json for base diagnostics")
    run.add_argument("--episodes-per-task", type=int)
    run.add_argument("--max-targets", type=int, help="Diagnostic prefix limit; 0 keeps the complete episode")
    run.add_argument("--compatibility-report", help="Completed same-input comparison summary.json")
    worker = sub.add_parser("worker")
    worker.add_argument("--output", required=True)
    worker.add_argument("--worker", required=True)
    worker.add_argument("--timeout", type=int, default=2400)
    args = parser.parse_args()
    if args.command == "run":
        raise SystemExit(standalone(args))
    spec = read(Path(args.output) / "evaluation.json")
    worker_loop(spec["config"], args.output, args.worker, weights=spec["weights"], record_frames=spec["record_frames"],
                evidence=spec["evidence"], timeout=args.timeout, scene_cap=spec.get('scene_cap'))


if __name__ == "__main__":
    main()
