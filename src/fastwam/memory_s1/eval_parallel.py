"""Independent GPU policy workers and distributed resident-model validation."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import gc
from multiprocessing.connection import Listener
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback

from .eval_state import EpisodeQueue, cuda_gpu_uuid, digest, durable_json, is_alive, locked, process_identity, read, signature, stop_mode, summarize


def gpu_inventory():
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader"], text=True)
    return {int(row.split(",")[0]): row.split(",")[1].strip() for row in output.strip().splitlines()}


def gpu_uuid_for_model(model):
    return cuda_gpu_uuid(next(model.memory.parameters()).device.index)


def simulator_environment(cfg, gpu_uuid):
    environment = dict(os.environ)
    prefix = Path(cfg["closed_loop"]["simulator_python"]).parent.parent
    environment.update(CUDA_VISIBLE_DEVICES=gpu_uuid, CUDA_DEVICE_ORDER="PCI_BUS_ID", CUDA_HOME=str(prefix),
                       PYTHONUNBUFFERED="1", OMP_NUM_THREADS="4", MKL_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4")
    environment["MEMORY_S1_ARCHIVE_STRIDE"] = str(cfg.get("history", {}).get("archive_stride", 8))
    environment["PATH"] = str(prefix / "bin") + os.pathsep + environment["PATH"]
    environment["LD_LIBRARY_PATH"] = os.pathsep.join([str(prefix / "lib"), str(prefix / "targets/x86_64-linux/lib"), environment.get("LD_LIBRARY_PATH", "")])
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
    return {"seed": loop["internal_seed"] if internal else loop["official_seed"],
            "count": loop["internal_episodes"] if internal else loop["official_episodes"],
            "tasks": ["put_back_block", "swap_blocks"], "task_config": "demo_clean", "instruction_type": "seen",
            "candidate_rule": "first K expert-feasible increasing seeds", "language_seed_rule": "scene_seed xor 0x51A17, freeze literal string",
            "python_scene_random": "random.seed(scene_seed) before expert and policy setup",
            "simulator_source": signature(inventory)}


def prepare_scenes(cfg, mode, gpu_uuids, stop_root):
    contract = protocol(cfg, mode)
    root = Path(cfg["paths"]["run"]) / "scene_manifests" / signature(contract)[:16]
    root.mkdir(parents=True, exist_ok=True)
    with locked(root / "planner.lock"):
        durable_json(root / "contract.json", contract)
        processes = []
        try:
            for index, task in enumerate(contract["tasks"]):
                output = root / f"{task}.json"
                if output.exists() and read(output).get("complete"):
                    continue
                command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/sim_eval.py"),
                           "--operation", "plan", "--task", task, "--output", str(output), "--contract", str(root / "contract.json"),
                           "--episodes", str(contract["count"]), "--seed", str(contract["seed"]),
                           "--gpu-uuid", gpu_uuids[index % len(gpu_uuids)], "--stop-root", str(stop_root)]
                log = (root / f"{task}.planner.log").open("a", encoding="utf-8")
                process = subprocess.Popen(command, env=simulator_environment(cfg, gpu_uuids[index % len(gpu_uuids)]),
                                           cwd=Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"], stdout=log,
                                           stderr=subprocess.STDOUT, start_new_session=True)
                processes.append((task, process, log))
                durable_json(root / f"{task}.owner.json", process_identity(process.pid))
            started, last_print = time.monotonic(), 0
            limit = 6 * 3600 if mode == "official" else 2 * 3600
            while any(process.poll() is None for _, process, _ in processes):
                if (Path(cfg["paths"]["run"]) / "STOP_REQUESTED").exists():
                    durable_json(Path(stop_root) / "STOP.json", {"mode": "now", "reason": "training safe stop during scene planning"})
                if stop_mode(stop_root) or time.monotonic() - started > limit:
                    raise RuntimeError("Scene planning stopped or timed out; partial manifests are preserved.")
                if any(process.poll() not in (None, 0) for _, process, _ in processes):
                    raise RuntimeError(f"Scene planner failed; inspect {root}/*.planner.log")
                if time.monotonic() - last_print >= 30:
                    progress = {task: len(read(root / f"{task}.json")["scenes"]) if (root / f"{task}.json").exists() else 0 for task in contract["tasks"]}
                    print(f"[planning] accepted={progress}; count_per_task={contract['count']}; logs={root}", flush=True)
                    last_print = time.monotonic()
                time.sleep(1)
            if any(process.returncode != 0 for _, process, _ in processes):
                raise RuntimeError(f"Scene planner failed; inspect {root}")
        finally:
            for _, process, log in processes:
                if process.poll() is None:
                    terminate_owned(process)
                log.close()
        scenes = []
        for task in contract["tasks"]:
            value = read(root / f"{task}.json")
            if value["contract"] != contract or not value["complete"] or value["sha256"] != signature(value["scenes"]):
                raise ValueError("Incomplete/corrupt scene manifest.")
            # Runtime timings and GPU assignments are provenance, not scene identity.
            scenes.extend([{key: row[key] for key in ("task", "seed", "ordinal", "instruction", "episode_info")} for row in value["scenes"]])
        return contract, scenes, root


def evaluation_identity(cfg, contract, scenes, conditions, weights, evidence, record_frames):
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
                      "history_sampling": cfg.get("history", {"online_period": 8, "archive_stride": 8})})


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


def execute_job(model, encoders, cfg, queue, job, gpu_uuid, record_frames, evidence, timeout):
    from .sim_bridge import InferenceSession
    directory = queue.root / job["directory"]
    started = time.monotonic()
    temporary = Path("/tmp/mwam-eval") / signature(str(queue.root.resolve()))[:12]
    temporary.mkdir(parents=True, exist_ok=True)
    socket_path = temporary / f"p{os.getpid()}.sock"
    socket_path.unlink(missing_ok=True)
    key = os.urandom(24)
    process = None
    session = InferenceSession(model, cfg, encoders, job["condition"], directory, evidence, cfg["seed"])
    try:
        with Listener(str(socket_path), family="AF_UNIX", authkey=key) as listener, (directory / "simulator.log").open("w", encoding="utf-8") as log:
            listener._listener._socket.settimeout(1)
            environment = simulator_environment(cfg, gpu_uuid)
            environment["MEMORY_S1_RPC_KEY"] = key.hex()
            command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/sim_eval.py"),
                       "--operation", "episode", "--job", str(directory / "job.json"), "--output", str(directory),
                       "--socket", str(socket_path), "--seed", str(cfg["seed"]), "--gpu-uuid", gpu_uuid,
                       "--stop-root", str(queue.root)]
            if record_frames:
                command.append("--record-frames")
            process = subprocess.Popen(command, cwd=Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"],
                                       env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            durable_json(directory / "simulator_owner.json", process_identity(process.pid))
            while process.poll() is None:
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
                            response = {"ok": True, **session.decide(request)}
                        else:
                            raise ValueError("Unknown RPC command.")
                    except Exception:
                        response = {"ok": False, "error": traceback.format_exc()}
                    connection.send(response)
            terminate_owned(process)
            value = read(directory / "simulator_result.json")
            if value["status"] == "complete" and process.returncode != 0:
                raise RuntimeError(f"Simulator failed after producing a result: exit={process.returncode}")
        if value["status"] == "complete":
            value["wall_seconds"] = time.monotonic() - started
            value["policy_gpu_uuid"] = gpu_uuid
            queue.publish(job, value)
        else:
            queue.finish(job, value["status"], value.get("error"))
    except Exception:
        error = traceback.format_exc()
        durable_json(directory / "error.json", {"error": error})
        queue.finish(job, "error", error)
        raise
    finally:
        if process is not None:
            terminate_owned(process)
        socket_path.unlink(missing_ok=True)
        session.reset()


def worker_loop(cfg, output, worker, weights=None, resident_model=None, record_frames=False, evidence=None, timeout=2400):
    import torch
    from .model import S1Model, load_observation_encoders
    queue = EpisodeQueue(output)
    own_model = resident_model is None
    model = resident_model
    encoders = None
    try:
        load_started = time.monotonic()
        print(f"[worker {worker}] waiting for model/encoder loading slot", flush=True)
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
        uuid = gpu_uuid_for_model(model)
        durable_json(queue.root / "workers" / f"{worker}.json", {"owner": process_identity(), "gpu_uuid": uuid, "torch": torch.__version__, "cuda": torch.version.cuda})
        while True:
            if resident_model is not None and (Path(cfg["paths"]["run"]) / "STOP_REQUESTED").exists():
                durable_json(queue.root / "STOP.json", {"mode": "now", "reason": "training safe stop"})
            job = queue.claim(worker)
            if job is None:
                break
            print(f"[worker {worker}] start {job['id']} attempt={job['attempt']} GPU={uuid}", flush=True)
            execute_job(model, encoders, cfg, queue, job, uuid, record_frames, evidence, timeout)
            print(f"[worker {worker}] finish {job['id']}", flush=True)
            if resident_model is not None and worker == "rank_0":
                status = progress(queue, int(os.environ.get("WORLD_SIZE", 1)))
                print(f"[validation] {status['completed']}/{status['total']} ETA~{status['eta_seconds']/60:.1f}min provisional={status['eta_provisional']}", flush=True)
                upload_results(cfg, output)
    finally:
        del encoders
        gc.collect()
        torch.cuda.empty_cache()
        if not own_model and model is not None:
            model.train()


def progress(queue, workers):
    value = queue.snapshot()
    completed = [job for job in value["jobs"] if job["state"] == "complete"]
    by_task = {}
    estimates = {}
    for task in ("put_back_block", "swap_blocks"):
        rows = [queue.result(job, value["identity"]) for job in completed if job["scene"]["task"] == task]
        estimates[task] = sum(row["wall_seconds"] for row in rows) / len(rows) if rows else (370 if task == "put_back_block" else 740)
        by_task[task] = {"completed": len(rows), "measured_mean_seconds": estimates[task] if rows else None}
    workloads = [0.0] * max(1, workers)
    for job in sorted((j for j in value["jobs"] if j["state"] in ("pending", "running")), key=lambda j: estimates[j["scene"]["task"]], reverse=True):
        remaining = estimates[job["scene"]["task"]]
        if job["state"] == "running":
            remaining = max(0, remaining - (time.time() - job["started"]))
        index = min(range(len(workloads)), key=workloads.__getitem__)
        workloads[index] += remaining
    result = {"completed": len(completed), "total": len(value["jobs"]), "by_task": by_task,
              "eta_seconds": max(workloads), "eta_provisional": any(v["measured_mean_seconds"] is None for v in by_task.values()),
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
    from .history import override_online
    override_online(cfg, getattr(args, "history_period", None), getattr(args, "history_cycle", None))
    if not cfg["closed_loop"]["enabled"]:
        raise ValueError("Closed-loop evaluation is disabled in this configuration.")
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    inventory = gpu_inventory()
    uuids = [inventory[int(index)] for index in args.gpus.split(",")]
    if len(uuids) != len(set(uuids)):
        raise ValueError("Each worker must have a distinct GPU.")
    conditions = args.conditions
    if not args.weights and conditions != ["gate_zero"]:
        raise ValueError("Untrained diagnostics support gate_zero only.")
    evidence = load_evidence(args.evidence) if args.evidence else None
    if any(c.startswith("delete_") for c in conditions) and evidence is None:
        raise ValueError("Deletion conditions require a reviewed evidence manifest.")
    with locked(output / "launcher.lock", blocking=False):
        durable_json(output / "launcher.json", {"owner": process_identity(), "argv": sys.argv, "gpu_uuids": uuids})
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
        durable_json(output / "evaluation.json", {"config": cfg, "mode": args.mode, "conditions": conditions,
                                                   "weights": str(Path(args.weights).resolve()) if args.weights else None,
                                                   "evidence": evidence, "record_frames": args.record_frames, "scene_manifest": str(manifest)})
        durable_json(output / "scenes.json", {"contract": contract, "scenes": scenes})
        processes = []
        try:
            for worker, uuid in enumerate(uuids):
                directory = output / "workers"
                directory.mkdir(exist_ok=True)
                log = (directory / f"worker_{worker}.log").open("a", encoding="utf-8")
                environment = dict(os.environ)
                environment.update(CUDA_VISIBLE_DEVICES=uuid, CUDA_DEVICE_ORDER="PCI_BUS_ID", PYTHONUNBUFFERED="1",
                                   OMP_NUM_THREADS="4", MKL_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4")
                command = [sys.executable, "-u", "-m", "fastwam.memory_s1.eval_parallel", "worker", "--output", str(output),
                           "--worker", str(worker), "--timeout", str(args.episode_timeout)]
                process = subprocess.Popen(command, env=environment, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                processes.append((process, log))
            last_print, last_uploaded = 0, -1
            workers_started = time.monotonic()
            while any(process.poll() is None for process, _ in processes):
                hung = [j["id"] for j in queue.snapshot()["jobs"] if j["state"] == "running" and time.time() - j["started"] > args.episode_timeout + 60]
                if hung or time.monotonic() - workers_started > len(scenes) * len(conditions) * args.episode_timeout + 1800:
                    durable_json(output / "ABORT.json", {"error": "Worker timeout", "jobs": hung})
                    durable_json(output / "STOP.json", {"mode": "now", "reason": "worker timeout"})
                    break
                if any(process.poll() not in (None, 0) for process, _ in processes):
                    durable_json(output / "ABORT.json", {"error": "A policy worker failed; inspect workers/*.log"})
                if time.monotonic() - last_print >= 15:
                    status = progress(queue, len(uuids))
                    summarize(output, args.mode)
                    print(f"[progress] {status['completed']}/{status['total']} ETA~{status['eta_seconds']/60:.1f}min provisional={status['eta_provisional']} tasks={status['by_task']}", flush=True)
                    last_print = time.monotonic()
                    if args.hf_results and status["completed"] != last_uploaded:
                        try:
                            upload_results(cfg, output)
                            last_uploaded = status["completed"]
                        except Exception:
                            durable_json(output / "UPLOAD_FAILED.json", {"error": traceback.format_exc()})
                            durable_json(output / "STOP.json", {"mode": "drain", "time": time.time()})
                time.sleep(1)
        finally:
            for process, log in processes:
                if process.poll() is None:
                    terminate_owned(process)
                log.close()
            cleanup_simulators(output)
        summary = summarize(output, args.mode)
        if args.hf_results:
            upload_results(cfg, output)
        progress(queue, len(uuids))
        print(f"[finish] complete={summary['complete']} completed={summary['completed_episodes']}/{summary['planned_episodes']} output={output}", flush=True)
        return 0 if summary["complete"] and not (output / "ABORT.json").exists() and not (output / "UPLOAD_FAILED.json").exists() else 2


def distributed_validation(cfg, weights, output, resident_model):
    import torch.distributed as dist
    from .checkpoint import random_state, restore_random_state
    rank, world = dist.get_rank(), dist.get_world_size()
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
                durable_json(output / "evaluation.json", {"mode": "internal", "config": cfg, "weights": str(weights)})
                durable_json(output / "scenes.json", {"contract": contract, "scenes": scenes})
                box[0] = {"ok": True}
            except Exception:
                box[0] = {"ok": False, "error": traceback.format_exc()}
        dist.broadcast_object_list(box, src=0, device=device)
        if not box[0]["ok"]:
            raise RuntimeError(box[0]["error"])
        error = None
        try:
            worker_loop(cfg, output, f"rank_{rank}", resident_model=resident_model)
        except Exception:
            error = traceback.format_exc()
            durable_json(output / "ABORT.json", {"rank": rank, "error": error})
        errors = [None] * world
        dist.all_gather_object(errors, error)
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
    run.add_argument("--history-cycle", help="Decision periods, e.g. 8,4,16")
    run.add_argument("--weights")
    run.add_argument("--evidence")
    run.add_argument("--gpus", default="0,1,2,3,4,5,6,7")
    run.add_argument("--resume", action="store_true")
    run.add_argument("--record-frames", action="store_true")
    run.add_argument("--hf-results", action="store_true")
    run.add_argument("--episode-timeout", type=int, default=2400)
    worker = sub.add_parser("worker")
    worker.add_argument("--output", required=True)
    worker.add_argument("--worker", required=True)
    worker.add_argument("--timeout", type=int, default=2400)
    args = parser.parse_args()
    if args.command == "run":
        raise SystemExit(standalone(args))
    spec = read(Path(args.output) / "evaluation.json")
    worker_loop(spec["config"], args.output, args.worker, weights=spec["weights"], record_frames=spec["record_frames"],
                evidence=spec["evidence"], timeout=args.timeout)


if __name__ == "__main__":
    main()
