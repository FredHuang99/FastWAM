"""Bounded root-cause diagnostics, independent GPU workers and restartable evidence."""
from __future__ import annotations

import argparse
import csv
import importlib.metadata
import importlib.util
import json
from multiprocessing.connection import Listener
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

from .common import append_jsonl, code_version, load_config, seed_for
from .eval_state import EpisodeQueue, EvaluationInterrupted, check_stop, digest, durable_json, is_alive, locked, process_identity, read, signature, stop_mode, summarize
from .eval_parallel import gpu_inventory, loading_slot, simulator_environment, terminate_owned, cleanup_simulators

TASKS = ("put_back_block", "swap_blocks")
POSITIVE_TASKS = ("stack_blocks_two", "handover_block")
PREFIXES = {"put_back_block": "Pick up the block and put it at the center of the table.",
            "swap_blocks": "Pick up one block and place it in the empty tray."}
VERSION = "fastwam-rootcause-independent-v1"


def environment_root(cfg, kind):
    relative = cfg["closed_loop"]["simulator_root"] if kind == "rmbench" else cfg["rootcause"]["robotwin_root"]
    return (Path(cfg["root"]) / relative).resolve()


def source_identity(root):
    names = ("envs", "scripts", "script", "env_cfg", "task_config", "description")
    return {str(path.relative_to(root)): digest(path) for name in names for path in sorted((root / name).rglob("*"))
            if path.is_file() and path.suffix in (".py", ".json", ".yml", ".yaml") and "__pycache__" not in path.parts}


def asset_identity(root):
    files = {}
    for path in sorted((root / "assets").rglob("*")):
        if not path.is_file() or path.suffix in (".zip", ".zst", ".tar", ".gz", ".pyc") or ".cache" in path.parts:
            continue
        files[str(path.relative_to(root))] = digest(path)
        if len(files) % 200 == 0:
            print(f"[identity] {root.name} assets checked={len(files)}", flush=True)
    return files


def runtime_identity(cfg):
    print("[identity] hashing existing weights and actual simulator sources; no downloads", flush=True)
    resources = {}
    for key in ("base", "stats", "vae", "t5"):
        resources[key] = digest(cfg["paths"][key])
        print(f"[identity] {key} verified", flush=True)
    resources["tokenizer"] = signature({str(p.relative_to(cfg["paths"]["tokenizer"])): digest(p)
        for p in sorted(Path(cfg["paths"]["tokenizer"]).rglob("*")) if p.is_file() and ".cache" not in p.parts})
    resources["manifest"] = digest(Path(cfg["paths"]["prepared"]) / "manifest.json")
    scene_file = Path(cfg["root"]) / cfg["rootcause"]["rm_scenes_from"]
    if not scene_file.is_file():
        raise FileNotFoundError(f"Frozen four-scene source missing: {scene_file}; pass the existing evidence scenes.json path in the diagnostic config.")
    resources["rm_scenes"] = digest(scene_file)
    return {"version": VERSION, "config": cfg, "resources": resources, "code": code_version(cfg["root"]),
        "simulator_sources": {kind: source_identity(environment_root(cfg, kind)) for kind in ("rmbench", "robotwin")},
        "simulator_assets": {kind: asset_identity(environment_root(cfg, kind)) for kind in ("rmbench", "robotwin")}}


def child_environment(uuid=None):
    env = dict(os.environ)
    env.update(PYTHONUNBUFFERED="1", OMP_NUM_THREADS="4", OPENBLAS_NUM_THREADS="4", MKL_NUM_THREADS="4")
    if uuid:
        env.update(CUDA_VISIBLE_DEVICES=uuid, CUDA_DEVICE_ORDER="PCI_BUS_ID")
    return env


def run_child(command, log, cwd, env, stop_root, timeout=2400):
    with Path(log).open("a", encoding="utf-8") as stream:
        process = subprocess.Popen(command, cwd=cwd, env=env, stdout=stream,
            stderr=subprocess.STDOUT, start_new_session=True)
        owner_path = Path(log).parent / "simulator_owner.json" if Path(log).name == "simulator.log" else Path(log).with_suffix(".owner.json")
        durable_json(owner_path, process_identity(process.pid))
        started, last_print = time.monotonic(), 0
        try:
            while process.poll() is None:
                check_stop(stop_root)
                if time.monotonic() - started > timeout:
                    raise TimeoutError(f"Child exceeded {timeout}s: {log}")
                if time.monotonic() - last_print > 30:
                    print(f"[child] elapsed={time.monotonic()-started:.0f}s log={log}", flush=True)
                    last_print = time.monotonic()
                time.sleep(0.5)
            if process.returncode:
                raise RuntimeError(f"Child exit={process.returncode}; inspect {log}")
        finally:
            terminate_owned(process)


def audit(cfg, output, identity, uuid):
    output.mkdir(parents=True, exist_ok=True)
    report = {"identity": identity, "repositories": {}, "versions": {}, "base_admission": "not_approved"}
    for name, root in (("fastwam", Path(cfg["root"])), ("rmbench", environment_root(cfg, "rmbench")),
                       ("robotwin", environment_root(cfg, "robotwin"))):
        info = {}
        for key, arguments in (("commit", ["rev-parse", "HEAD"]), ("status", ["status", "--short"]),
                               ("diff", ["diff", "HEAD", "--binary"]), ("untracked", ["ls-files", "--others", "--exclude-standard"])):
            result = subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True)
            info[key] = result.stdout if result.returncode == 0 else result.stderr
        # No environment token values or credential-bearing remote URLs are collected.
        (output / f"{name}.git.diff").write_text(info.pop("diff"), encoding="utf-8")
        report["repositories"][name] = info
    for name in ("torch", "transformers", "numpy", "hydra-core", "huggingface-hub"):
        try:
            report["versions"][name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            report["versions"][name] = None
    report["training_python"] = sys.executable
    report["python_version"] = sys.version
    report["policy_contract"] = {"predict": 32, "execute_rmbench": 16, "execute_robotwin": 24,
        "denoise_steps": 10, "noise": "CPU FP32 seed 17, cast BF16; derived-noise intervention separately recorded",
        "proprio_source": "original command target vector; physical qpos only used for audit",
        "preprocessing": "released BF16 before affine; legacy FP32-before-BF16 compared in D1",
        "prompt": "original robot-video task template; complete task unless prefix_instruction intervention",
        "observation_calls": "RMBench every completed target; original RoboTwin positive control only at decision boundaries"}
    report["runtime"] = {"driver_capabilities": os.environ.get("NVIDIA_DRIVER_CAPABILITIES"),
        "container_image_digest": os.environ.get("MWAM_IMAGE_DIGEST")}
    report["import_paths"] = {name: importlib.util.find_spec(name).origin for name in ("fastwam", "torch", "transformers", "numpy")}
    report["installed_distributions"] = sorted({d.metadata["Name"]: d.version for d in importlib.metadata.distributions() if d.metadata.get("Name")}.items())
    for kind, tasks in (("rmbench", TASKS), ("robotwin", POSITIVE_TASKS)):
        destination = output / f"{kind}_preflight.json"
        command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/rootcause_sim.py"),
            "--operation", "preflight", "--output", str(destination), "--tasks", *tasks]
        try:
            run_child(command, output / f"{kind}_preflight.log", environment_root(cfg, kind),
                simulator_environment(cfg, uuid), output.parent, 300)
        except RuntimeError:
            if not destination.exists():
                raise
        report[kind] = read(destination)
    report["complete"] = True
    report["ready_rmbench"] = report["rmbench"]["ready"]
    report["ready_robotwin"] = report["robotwin"]["ready"]
    durable_json(output / "summary.json", report)
    print(f"[D0] RMBench ready={report['ready_rmbench']} RoboTwin ready={report['ready_robotwin']}", flush=True)
    return report


def expert_scenes(cfg):
    manifest = read(Path(cfg["paths"]["prepared"]) / "manifest.json")
    scenes = []
    for task in TASKS:
        rows = [r for r in manifest["episodes"] if r["task"] == task and r["episode_id"].split("/")[-1] == "episode_0000000"]
        if len(rows) != 1:
            raise ValueError(f"Reviewed episode_0000000 unavailable: {task}")
        row = rows[0]
        if digest(Path(cfg["root"]) / row["raw"]) != row["raw_sha256"]:
            raise ValueError(f"Reviewed raw episode changed: {row['raw']}")
        scenes.append({"task": task, "seed": 0, "ordinal": 0, "instruction": row["instruction"],
            "environment": "rmbench", "episode": str(Path(cfg["paths"]["prepared"]) / row["file"]),
            "raw": row["raw"], "raw_sha256": row["raw_sha256"], "camera_paths": row["camera_paths"]})
    return scenes


def queue_progress(queue, workers):
    state = queue.snapshot()
    done = [job for job in state["jobs"] if job["state"] == "complete"]
    means = {}
    for row in done:
        result = queue.result(row, state["identity"])
        means.setdefault(row["scene"]["task"], []).append(result["wall_seconds"])
    lanes = [0.0] * max(1, workers)
    provisional = False
    for row in state["jobs"]:
        if row["state"] not in ("pending", "running"):
            continue
        measured = means.get(row["scene"]["task"], [])
        seconds = sum(measured) / len(measured) if measured else row["estimate_seconds"]
        provisional |= not bool(measured)
        if row["state"] == "running":
            seconds = max(0, seconds - (time.time() - row["started"]))
        lanes[min(range(len(lanes)), key=lanes.__getitem__)] += seconds
    result = {"completed": len(done), "total": len(state["jobs"]), "eta_seconds": max(lanes),
        "eta_provisional": provisional, "stop": stop_mode(queue.root),
        "errors": sum(j["state"] == "error" for j in state["jobs"])}
    durable_json(queue.root / "status.json", result)
    return result


def publish(queue, job, result):
    directory = queue.root / job["directory"]
    durable_json(directory / "result.json", result)
    files = {str(p.relative_to(directory)): digest(p) for p in directory.rglob("*")
        if p.is_file() and p.suffix in (".json", ".jsonl", ".npz", ".log")
        and p.name not in ("complete.json", "simulator_owner.json")}
    durable_json(directory / "complete.json", {"identity": queue.snapshot()["identity"], "job_id": job["id"], "files": files})
    queue.finish(job, "complete")


def execute_job(policy, cfg, queue, job, uuid, parent_stop):
    directory = queue.root / job["directory"]
    experiment = read(queue.root / "evaluation.json")
    operation, executor = experiment["operation"], "upstream_topp"
    if operation == "replay":
        executor = "dense_native" if job["condition"] == "dense" else "upstream_topp"
    elif job["condition"] == "dense_control":
        executor = "dense_native"
    scene = job["scene"]
    execute = 24 if job["condition"] in ("execute_24", "positive") else 16
    instruction = PREFIXES[scene["task"]] if job["condition"] == "prefix_instruction" else scene["instruction"]
    payload = {**job, "scene": {**scene, "instruction": instruction}, "execute": execute,
        "max_targets": 0 if scene["environment"] == "robotwin" else (512 if operation == "policy" else 0),
        "episode": scene.get("episode"), "cadence": scene.get("cadence"),
        "noise": "derived" if job["condition"] == "derived_noise" else "fixed",
        "preprocessor": "released_uint8_to_device_bf16_then_affine_v1", "executor": executor,
        "skip_get_obs_within_replan": scene["environment"] == "robotwin"}
    durable_json(directory / "job.json", {**payload, "identity": queue.snapshot()["identity"]})
    command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/rootcause_sim.py"),
        "--operation", operation, "--output", str(directory), "--job", str(directory / "job.json"),
        "--gpu-uuid", uuid, "--executor", executor, "--stop-root", str(parent_stop)]
    started, process = time.monotonic(), None
    env = simulator_environment(cfg, uuid)
    socket_path = Path("/tmp") / f"mwam-rootcause-{os.getpid()}.sock"
    socket_path.unlink(missing_ok=True)
    key = os.urandom(24)
    try:
        if operation != "policy":
            run_child(command, directory / "simulator.log", environment_root(cfg, scene["environment"]),
                env, parent_stop, cfg["rootcause"]["episode_timeout"])
        else:
            env["MEMORY_S1_RPC_KEY"] = key.hex()
            command += ["--socket", str(socket_path)]
            with Listener(str(socket_path), family="AF_UNIX", authkey=key) as listener, (directory / "simulator.log").open("w", encoding="utf-8") as log:
                listener._listener._socket.settimeout(1)
                process = subprocess.Popen(command, cwd=environment_root(cfg, scene["environment"]), env=env,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                durable_json(directory / "simulator_owner.json", process_identity(process.pid))
                while process.poll() is None:
                    check_stop(parent_stop)
                    if time.monotonic() - started > cfg["rootcause"]["episode_timeout"]:
                        raise TimeoutError("Policy episode exceeded its fixed timeout.")
                    try:
                        connection = listener.accept()
                    except TimeoutError:
                        continue
                    with connection:
                        if not connection.poll(30):
                            raise TimeoutError("Connected simulator did not send an RPC request.")
                        request = connection.recv()
                        try:
                            import numpy as np
                            from .rootcause_model import current_observation
                            noise_seed = seed_for(cfg["seed"], scene["seed"], request["current_id"], "closed-loop-noise") if payload["noise"] == "derived" else cfg["seed"]
                            policy.seed = noise_seed
                            inference_started = time.monotonic()
                            actions = policy._infer_action_chunk(current_observation(request["images"], request["proprio"]), request["instruction"])
                            if actions.shape != (32, 14) or not np.isfinite(actions).all():
                                raise ValueError("The released policy returned invalid actions.")
                            row = {"frame_id": request["current_id"], "noise_seed": noise_seed,
                                "instruction": request["instruction"], "seconds": time.monotonic() - inference_started,
                                "predict": 32, "execute": execute, "noise_rule": payload["noise"],
                                "actions": actions.tolist(), "gripper_outside_unit": int(((actions[:, [6, 13]] < 0) | (actions[:, [6, 13]] > 1)).sum()),
                                "postprocess": "original_released_denormalization; executor retains native gripper semantics"}
                            append_jsonl(directory / "decisions.jsonl", row)
                            response = {"ok": True, "actions": actions.tolist()}
                        except Exception:
                            response = {"ok": False, "error": traceback.format_exc()}
                        connection.send(response)
                if process.returncode:
                    raise RuntimeError(f"Simulator exit={process.returncode}; inspect {directory / 'simulator.log'}")
        result = read(directory / "simulator_result.json")
        result["wall_seconds"] = time.monotonic() - started
        result["contract"] = {k: payload[k] for k in ("execute", "max_targets", "noise", "preprocessor", "executor")}
        publish(queue, job, result)
    except EvaluationInterrupted:
        queue.finish(job, "interrupted", "Stop requested; restart this whole scene on resume.")
    except Exception:
        error = traceback.format_exc()
        durable_json(directory / "error.json", {"error": error})
        queue.finish(job, "error", error)
        raise
    finally:
        if process is not None:
            terminate_owned(process)
        socket_path.unlink(missing_ok=True)


def worker(args):
    queue = EpisodeQueue(args.output)
    experiment = read(queue.root / "evaluation.json")
    cfg, policy = experiment["config"], None
    parent = Path(experiment["parent_stop"])
    try:
        while not stop_mode(parent):
            job = queue.claim(args.worker)
            if job is None:
                break
            if experiment["operation"] == "policy" and policy is None:
                from .rootcause_model import load_released_policy
                print(f"[worker {args.worker}] waiting for independent model load", flush=True)
                loading_started = time.monotonic()
                with loading_slot(queue.root, 2):
                    policy = load_released_policy(cfg)
                print(f"[worker {args.worker}] model ready; wait_and_load_seconds={time.monotonic()-loading_started:.1f}", flush=True)
            print(f"[worker {args.worker}] start {job['id']} GPU={args.gpu_uuid}", flush=True)
            execute_job(policy, cfg, queue, job, args.gpu_uuid, parent)
            print(f"[worker {args.worker}] finish {job['id']}", flush=True)
    finally:
        del policy


def parallel_group(cfg, root, name, scenes, conditions, operation, uuids, resume, identity):
    directory = root / name
    directory.mkdir(parents=True, exist_ok=True)
    queue = EpisodeQueue(directory)
    group_identity = signature({"root_identity": identity, "operation": operation, "scenes": scenes, "conditions": conditions})
    queue.initialize(group_identity, scenes, conditions, resume)
    durable_json(directory / "evaluation.json", {"config": cfg, "operation": operation,
        "parent_stop": str(root), "conditions": conditions, "scope": "rootcause_diagnostic_only"})
    durable_json(directory / "scenes.json", {"contract": {"root_identity": identity}, "scenes": scenes})
    processes = []
    group_started = time.monotonic()
    try:
        pending = sum(j["state"] != "complete" for j in queue.snapshot()["jobs"])
        for index, uuid in enumerate(uuids[:pending]):
            logs = directory / "workers"
            logs.mkdir(exist_ok=True)
            stream = (logs / f"worker_{index}.log").open("a", encoding="utf-8")
            command = [sys.executable, "-u", "-m", "fastwam.memory_s1.rootcause", "worker",
                "--output", str(directory), "--worker", str(index), "--gpu-uuid", uuid]
            process = subprocess.Popen(command, cwd=cfg["root"], env=child_environment(uuid),
                stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
            durable_json(logs / f"worker_{index}.owner.json", process_identity(process.pid))
            processes.append((process, stream))
        last = 0
        while any(process.poll() is None for process, _ in processes):
            check_stop(root)
            if time.monotonic() - group_started > len(scenes) * len(conditions) * cfg["rootcause"]["episode_timeout"] + 1800:
                raise TimeoutError("Diagnostic workers exceeded the bounded group runtime.")
            if any(process.poll() not in (None, 0) for process, _ in processes):
                raise RuntimeError(f"A diagnostic worker failed; inspect {directory / 'workers'}")
            if time.monotonic() - last > 15:
                status = queue_progress(queue, len(uuids))
                print(f"[{name}] {status['completed']}/{status['total']} ETA={status['eta_seconds']/60:.1f}min provisional={status['eta_provisional']}", flush=True)
                last = time.monotonic()
            time.sleep(1)
        if any(process.returncode for process, _ in processes):
            raise RuntimeError(f"A diagnostic worker failed: {directory}")
    finally:
        for process, stream in processes:
            if process.poll() is None:
                terminate_owned(process)
            stream.close()
        cleanup_simulators(directory)
        summarize(directory, "rootcause")
        queue_progress(queue, len(uuids))
    result = summarize(directory, "rootcause")
    queue_progress(queue, len(uuids))
    if not result["complete"]:
        raise EvaluationInterrupted("Diagnostic group incomplete; completed scenes are preserved.")
    return result


def phase_d2(cfg, root, uuids, resume, identity):
    scenes = expert_scenes(cfg)
    oracle = parallel_group(cfg, root, "D2/expert", scenes, ["expert"], "expert", uuids, resume, identity)
    if not all(row["success"] for row in oracle["episodes"]):
        durable_json(root / "D2/summary.json", {"complete": True, "passed": False, "oracle": oracle,
            "dense_control_required": False, "error": "Live expert failed; resolve environment/asset execution first."})
        raise RuntimeError("At least one live expert failed. Inspect D2/expert before model diagnosis or training.")
    queue = EpisodeQueue(root / "D2/expert")
    for scene in scenes:
        job = next(j for j in queue.snapshot()["jobs"] if j["scene"]["task"] == scene["task"])
        scene["cadence"] = str(queue.root / job["directory"] / "cadence.json")
    replay = parallel_group(cfg, root, "D2/replay", scenes, ["upstream", "dense"], "replay", uuids, resume, identity)
    dense_candidate = []
    for task in TASKS:
        upstream = next(r for r in replay["episodes"] if r["task"] == task and r["condition"] == "upstream")
        dense = next(r for r in replay["episodes"] if r["task"] == task and r["condition"] == "dense")
        def evidence(row):
            return any(e["contact_seen"] and e["max_lift_run"] >= 5 and e["max_xy_m"] >= 0.05
                for name, e in row["physical_summary"]["events"].items() if name in ("block", "block1", "block2", "box"))
        dense_candidate.append((dense["success"] and not upstream["success"]) or (evidence(dense) and not evidence(upstream)))
    result = {"complete": True, "passed": True, "oracle": oracle, "replay": replay,
        "dense_control_required": any(dense_candidate), "automatic_base_admission": False,
        "note": "Fixed-15 intervals remain approximate unless cadence.json verified every native command. Expert success alone does not prove a matching saved scene."}
    durable_json(root / "D2/summary.json", result)


def phase_d3(cfg, root, uuids, resume, identity):
    audit_report = read(root / "D0/summary.json")
    if not audit_report["ready_robotwin"]:
        raise RuntimeError("Original RoboTwin assets/configs missing; see D0/robotwin_preflight.json. Do not substitute RMBench or bypass the positive control.")
    plan_root = root / "D3/positive_scenes"
    plan_root.mkdir(parents=True, exist_ok=True)
    processes = []
    try:
        for index, task in enumerate(POSITIVE_TASKS):
            destination = plan_root / f"{task}.json"
            if destination.exists() and read(destination).get("complete"):
                continue
            command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/rootcause_sim.py"),
                "--operation", "plan", "--output", str(destination), "--tasks", task,
                "--gpu-uuid", uuids[index % len(uuids)], "--stop-root", str(root)]
            stream = (plan_root / f"{task}.log").open("a", encoding="utf-8")
            process = subprocess.Popen(command, cwd=environment_root(cfg, "robotwin"),
                env=simulator_environment(cfg, uuids[index % len(uuids)]), stdout=stream,
                stderr=subprocess.STDOUT, start_new_session=True)
            durable_json(plan_root / f"{task}.owner.json", process_identity(process.pid))
            processes.append((process, stream))
        started = time.monotonic()
        while any(p.poll() is None for p, _ in processes):
            check_stop(root)
            if time.monotonic() - started > cfg["rootcause"]["planning_timeout"] or any(p.poll() not in (0, None) for p, _ in processes):
                raise RuntimeError(f"Bounded RoboTwin planning failed; inspect {plan_root}")
            time.sleep(1)
        if any(p.returncode for p, _ in processes):
            raise RuntimeError(f"RoboTwin planner failed: {plan_root}")
    finally:
        for process, stream in processes:
            if process.poll() is None:
                terminate_owned(process)
            stream.close()
    positive_scenes = [s for task in POSITIVE_TASKS for s in read(plan_root / f"{task}.json")["scenes"]]
    positive = parallel_group(cfg, root, "D3/positive", positive_scenes, ["positive"], "policy", uuids, resume, identity)
    saved = read(Path(cfg["root"]) / cfg["rootcause"]["rm_scenes_from"])
    scenes = []
    for task in TASKS:
        rows = sorted((s for s in saved["scenes"] if s["task"] == task), key=lambda s: s["ordinal"])
        if len(rows) < 2:
            raise ValueError("The existing frozen bank must contain two scenes per task.")
        scenes.extend([{**s, "environment": "rmbench"} for s in rows[:2]])
    conditions = ["baseline", "derived_noise", "execute_24", "prefix_instruction"]
    factors = parallel_group(cfg, root, "D3/rmbench", scenes, conditions, "policy", uuids, resume, identity)
    dense = None
    if read(root / "D2/summary.json")["dense_control_required"]:
        dense = parallel_group(cfg, root, "D3/dense_control", scenes, ["dense_control"], "policy", uuids, resume, identity)
    durable_json(root / "D3/summary.json", {"complete": True, "positive": positive, "factors": factors,
        "dense_control": dense, "scope": "Four-condition 512-target RMBench prefixes and four original-environment positive controls; no official RMBench success estimate."})


def evidence_summary(root):
    rows = []
    for path in sorted(root.glob("D[23]/*/summary.json")):
        report = read(path)
        for episode in report.get("episodes", []):
            events = episode["physical_summary"]["events"]
            objects = [e for name, e in events.items() if name in ("block", "block1", "block2", "box")]
            rows.append({"group": str(path.parent.relative_to(root)), "task": episode["task"],
                "seed": episode["seed"], "condition": episode["condition"], "success": episode["success"],
                "truncated": episode.get("truncated", False), "targets": episode["executed_targets"],
                "max_lift_m": max((e["max_lift_m"] for e in objects), default=0),
                "max_xy_m": max((e["max_xy_m"] for e in objects), default=0),
                "max_lift_run": max((e["max_lift_run"] for e in objects), default=0),
                "contact_seen": any(e["contact_seen"] for e in objects), "seconds": episode["wall_seconds"],
                "observation_rpc_physics_steps": sum(r["physics_steps_during_operation"] for r in episode["physical_summary"].get("wall_operations", [])),
                "observation_seconds": sum(r["seconds"] for r in episode["physical_summary"].get("wall_operations", []) if r["operation"] == "get_obs")})
    if rows:
        with (root / "comparison.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    conclusions = []
    d1 = root / "D1/summary.json"
    if d1.exists():
        cases = [json.loads(line) for line in (root / "D1/cases.jsonl").read_text().splitlines() if line.strip()]
        conclusions.append({"hypothesis": "deployment_input_or_forward_error", "evidence": str(d1),
            "supported": not read(d1)["passed"], "limitation": "Aligned preprocessing does not prove the base is task-adapted."})
        conclusions.append({"hypothesis": "legacy_image_arithmetic_differs_from_release",
            "supported": any(not r["legacy_preprocessing"]["mosaic"]["allclose"] for r in cases),
            "evidence": "D1/cases.jsonl: legacy_preprocessing versus independent released path",
            "repair": "Only diagnostic aligned branch changed; review effect before updating S1 or invalidating its cache.",
            "counterevidence": "Small BF16 pixel or latent differences alone do not establish the cause of failed grasping."})
    d2 = root / "D2/summary.json"
    if d2.exists():
        conclusions.append({"hypothesis": "executor_cadence_mismatch", "evidence": str(d2),
            "supported": None, "candidate": read(d2)["dense_control_required"],
            "limitation": "Check cadence verification and scene alignment before causal attribution."})
    def manipulation(row):
        return row["contact_seen"] and row["max_lift_m"] >= .03 and row["max_lift_run"] >= 5 and row["max_xy_m"] >= .05
    positives = [r for r in rows if r["group"] == "D3/positive"]
    factors = [r for r in rows if r["group"] == "D3/rmbench"]
    baseline = [r for r in factors if r["condition"] == "baseline"]
    positive_ok = bool(positives) and all(r["success"] or manipulation(r) for r in positives)
    conclusions.append({"hypothesis": "global_deployment_or_robotwin_environment_fault",
        "supported": False if positive_ok else None, "requires_investigation": bool(positives) and not positive_ok,
        "evidence": positives, "counterevidence": "Original-environment success or sustained contact/lift/transport contradicts a global inability to control the robot.",
        "limitation": "Four scenes are diagnostics, not a reproduction of published benchmark scores."})
    for condition in ("derived_noise", "execute_24", "prefix_instruction"):
        contrasts = []
        for base in baseline:
            other = next((r for r in factors if r["task"] == base["task"] and r["seed"] == base["seed"] and r["condition"] == condition), None)
            if other:
                contrasts.append({"task": base["task"], "seed": base["seed"],
                    "baseline_evidence": manipulation(base), "intervention_evidence": manipulation(other),
                    "baseline_lift_m": base["max_lift_m"], "intervention_lift_m": other["max_lift_m"]})
        conclusions.append({"hypothesis": condition, "supported": None if not contrasts else any(not c["baseline_evidence"] and c["intervention_evidence"] for c in contrasts),
            "evidence": contrasts, "repair": "Keep each intervention separate; review matched images/contacts/trajectories before changing the research protocol.",
            "limitation": "Prefix instructions assess visible initial manipulation only; seed or execute-length gains do not prove a memory mechanism."})
    conclusions.append({"hypothesis": "get_obs_wall_time_alters_physics",
        "supported": None if not rows else any(r["observation_rpc_physics_steps"] for r in rows),
        "evidence": "physical_summary.json and wall_operations.jsonl: physical step deltas during get_obs/RPC",
        "limitation": "Zero step deltas show no direct physics advancement by these calls in the synchronous protocol; they do not establish real-world asynchronous behavior."})
    oracle = [r for r in rows if r["group"] == "D2/expert"]
    default_replays = [r for r in rows if r["group"] == "D2/replay" and r["condition"] == "upstream"]
    adaptation_evidence = positive_ok and bool(baseline) and all(not manipulation(r) for r in baseline) and len(oracle) == 2 and all(r["success"] for r in oracle) and len(default_replays) == 2 and all(r["success"] for r in default_replays)
    conclusions.append({"hypothesis": "missing_RMBench_adaptation", "supported": adaptation_evidence if positives and baseline else None,
        "evidence": "Released RoboTwin checkpoint was not adapted on RMBench; compare positive controls and prefix interventions.",
        "limitation": "No automatic P2 start or base admission. Several causes may coexist."})
    durable_json(root / "rootcause_summary.json", {"episodes": rows, "hypotheses": conclusions,
        "automatic_base_admission": False, "next_step": "Review physical evidence and contrasts before S1 or a separate P2 plan."})
    if rows:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        figure, axes = plt.subplots(2, 1, figsize=(max(10, len(rows) * .3), 7), sharex=True)
        labels = [f"{r['task']}\n{r['seed']}\n{r['condition']}" for r in rows]
        axes[0].bar(range(len(rows)), [r["max_lift_m"] for r in rows])
        axes[0].set_ylabel("Maximum object lift (m)")
        axes[1].bar(range(len(rows)), [r["max_xy_m"] for r in rows])
        axes[1].set_ylabel("Maximum object XY displacement (m)")
        axes[1].set_xticks(range(len(rows)), labels, rotation=70, fontsize=6)
        figure.suptitle("Diagnostic geometry only: review contacts and physical trajectories")
        figure.tight_layout()
        for suffix in ("png", "pdf"):
            figure.savefig(root / f"comparison.{suffix}", dpi=160)
        plt.close(figure)


def pack(root, cfg, output, compact=True):
    output.mkdir(parents=True, exist_ok=True)
    name = f"rootcause_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{time.time_ns()}"
    manifest = {}
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or "packages" in path.parts or path.suffix in (".sock", ".lock"):
            continue
        if compact and ("frames" in path.parts or path.suffix.lower() in (".jpg", ".mp4")):
            continue
        files.append((path, Path("evidence") / path.relative_to(root)))
    source_root = Path(cfg["root"])
    for subtree in ("src", "scripts/memory_s1", "experiments/robotwin", "configs", "requirements"):
        for path in (source_root / subtree).rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix in (".py", ".sh", ".json", ".yaml", ".yml", ".toml", ".txt"):
                files.append((path, Path("code") / path.relative_to(source_root)))
    files.append((source_root / "pyproject.toml", Path("code/pyproject.toml")))
    import tarfile
    archive_tar = output / f"{name}.tar"
    with tarfile.open(archive_tar, "w") as archive:
        for path, relative in files:
            manifest[str(relative)] = digest(path)
            archive.add(path, arcname=str(relative), recursive=False)
    subprocess.run(["zstd", "-T0", "-3", "--rm", str(archive_tar)], check=True)
    archive = Path(str(archive_tar) + ".zst")
    durable_json(output / f"{name}.json", {"files": manifest, "archive": archive.name,
        "sha256": digest(archive), "compact": compact, "bytes": archive.stat().st_size})
    (output / f"{name}.sha256").write_text(f"{digest(archive)}  {archive.name}\n", encoding="utf-8")
    print(f"[package] {archive} bytes={archive.stat().st_size}", flush=True)
    return name


def upload_phase(root, cfg, phase, directory=None):
    if directory is None:
        directory = root / "packages" / f"hf_{phase}_{time.time_ns()}"
        pack(root, cfg, directory, compact=True)
    else:
        directory = Path(directory).resolve()
        if not directory.is_relative_to((root / "packages").resolve()):
            raise ValueError("Retry packages must remain inside this diagnostic run.")
        for path in directory.glob("*.json"):
            record = read(path)
            archive = directory / record["archive"]
            if digest(archive) != record["sha256"]:
                raise ValueError(f"Retained package checksum mismatch: {archive}")
    command = [cfg["hf"]["python"], str(Path(cfg["root"]) / "scripts/memory_s1/hf_tools.py"), "upload-package",
        "--repo", cfg["hf"]["backup_repo"], "--repo-type", "model", "--directory", str(directory),
        "--prefix", f"rootcause/{root.name}/{phase}/{directory.name}",
        "--quota-gib", str(cfg["hf"]["quota_gib"]), "--reserve-gib", str(cfg["hf"]["reserve_gib"])]
    started = time.monotonic()
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=600)
        error = result.stderr if result.returncode else None
    except subprocess.TimeoutExpired:
        result, error = None, "HF upload timed out after 600 seconds."
    if error is not None:
        durable_json(root / "UPLOAD_FAILED.json", {"phase": phase, "package": str(directory), "command": command,
            "stdout": result.stdout if result else "", "stderr": error})
        raise RuntimeError("HF upload failed; compact package retained. Retry the saved command before resuming.")
    print(result.stdout, flush=True)
    append_jsonl(root / "hf_uploads.jsonl", {"phase": phase, "package": str(directory),
        "stdout": result.stdout, "seconds": time.monotonic() - started, "command": command})
    (root / "UPLOAD_FAILED.json").unlink(missing_ok=True)


def run(args):
    cfg = load_config(args.config)
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    inventory = gpu_inventory()
    uuids = [inventory[int(index)] for index in args.gpus.split(",")]
    if len(set(uuids)) != len(uuids):
        raise ValueError("GPU assignments must be distinct.")
    with locked(root / "launcher.lock", blocking=False):
        marker = root / "identity.json"
        identity = runtime_identity(cfg)
        if marker.exists():
            if read(marker) != identity:
                raise ValueError("Sources/resources/config changed; preserve this run and choose a new output directory.")
            if not args.resume:
                raise ValueError("Existing diagnostic output requires --resume.")
            for owner_file in root.rglob("*.owner.json"):
                if is_alive(read(owner_file)):
                    raise RuntimeError(f"Old child is still alive: {owner_file}")
            (root / "STOP.json").unlink(missing_ok=True)
        else:
            durable_json(marker, identity)
        durable_json(root / "launcher.json", {"owner": process_identity(), "argv": sys.argv, "gpu_uuids": uuids})
        def stop(signum, frame):
            durable_json(root / "STOP.json", {"mode": "now", "signal": signum})
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        failed_upload = root / "UPLOAD_FAILED.json"
        if failed_upload.exists():
            saved = read(failed_upload)
            print(f"[HF] retrying retained {saved['phase']} package before further work", flush=True)
            upload_phase(root, cfg, saved["phase"], saved["package"])
        phases = ("D0", "D1", "D2", "D3") if args.stage == "all" else (args.stage,)
        for phase in phases:
            check_stop(root)
            summary = root / phase / "summary.json"
            if summary.exists() and read(summary).get("complete"):
                if phase in ("D1", "D2") and not read(summary)["passed"]:
                    raise RuntimeError(f"{phase} failed; fix the reported cause before continuing.")
                print(f"[{phase}] complete result reused", flush=True)
                continue
            for dependency in {"D0": (), "D1": ("D0",), "D2": ("D0", "D1"), "D3": ("D0", "D1", "D2")}[phase]:
                path = root / dependency / "summary.json"
                if not path.exists() or not read(path).get("complete") or (dependency in ("D1", "D2") and not read(path)["passed"]):
                    raise ValueError(f"Complete {dependency} before {phase}.")
            started = time.monotonic()
            durable_json(root / "status.json", {"phase": phase, "state": "running", "started": time.time()})
            if phase == "D0":
                audit(cfg, root / "D0", identity, uuids[0])
            elif phase == "D1":
                if not read(root / "D0/summary.json")["ready_rmbench"]:
                    raise RuntimeError("RMBench preflight has missing imports/assets.")
                destination = root / "D1"
                destination.mkdir(exist_ok=True)
                run_child([sys.executable, "-u", "-m", "fastwam.memory_s1.rootcause", "compare", "--config", args.config,
                    "--output", str(destination), "--stop-root", str(root)], destination / "comparison.log", cfg["root"],
                    child_environment(uuids[0]), root, 3600)
                if not read(summary)["passed"]:
                    evidence_summary(root)
                    raise RuntimeError("D1 first divergence found; closed-loop diagnostics are not started.")
            elif phase == "D2":
                phase_d2(cfg, root, uuids, args.resume, signature(identity))
            else:
                phase_d3(cfg, root, uuids, args.resume, signature(identity))
            append_jsonl(root / "phase_timings.jsonl", {"phase": phase, "seconds": time.monotonic() - started})
            evidence_summary(root)
            if args.hf_results:
                upload_phase(root, cfg, phase)
            durable_json(root / "status.json", {"phase": phase, "state": "complete", "summary": str(summary)})
            print(f"[{phase}] complete; report={summary}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    launch = sub.add_parser("run")
    launch.add_argument("--config", required=True)
    launch.add_argument("--output", required=True)
    launch.add_argument("--stage", choices=("D0", "D1", "D2", "D3", "all"), default="all")
    launch.add_argument("--gpus", default="0,1,2,3,4,5,6,7")
    launch.add_argument("--resume", action="store_true")
    launch.add_argument("--hf-results", action="store_true")
    compare = sub.add_parser("compare")
    compare.add_argument("--config", required=True)
    compare.add_argument("--output", required=True)
    compare.add_argument("--stop-root")
    child = sub.add_parser("worker")
    child.add_argument("--output", required=True)
    child.add_argument("--worker", required=True)
    child.add_argument("--gpu-uuid", required=True)
    for name in ("status", "stop", "summarize"):
        action = sub.add_parser(name)
        action.add_argument("--output", required=True)
    package = sub.add_parser("pack")
    package.add_argument("--config", required=True)
    package.add_argument("--output", required=True)
    package.add_argument("--destination", required=True)
    package.add_argument("--include-images", action="store_true")
    args = parser.parse_args()
    if args.command == "run":
        try:
            run(args)
        except BaseException as error:
            root = Path(args.output).resolve()
            owner = read(root / "launcher.json").get("owner") if (root / "launcher.json").exists() else None
            if root.is_dir() and owner and owner["pid"] == os.getpid():
                previous = read(root / "status.json") if (root / "status.json").exists() else {}
                previous.update(state="interrupted" if isinstance(error, EvaluationInterrupted) else "error",
                    error=str(error), ended=time.time())
                durable_json(root / "status.json", previous)
                evidence_summary(root)
                if args.hf_results and not (root / "UPLOAD_FAILED.json").exists():
                    upload_phase(root, load_config(args.config), previous["state"])
            raise
    elif args.command == "compare":
        from .rootcause_model import independent_comparison
        independent_comparison(load_config(args.config), args.output, args.stop_root)
    elif args.command == "worker":
        worker(args)
    elif args.command == "stop":
        durable_json(Path(args.output) / "STOP.json", {"mode": "now", "time": time.time()})
        print("Stop requested; owned workers exit and unfinished scenes restart on resume.")
    elif args.command == "status":
        root = Path(args.output)
        for name in ("status.json", "launcher.json", "UPLOAD_FAILED.json"):
            if (root / name).exists():
                value = read(root / name)
                if name == "launcher.json":
                    value["alive"] = is_alive(value["owner"])
                print(name, json.dumps(value, indent=2))
        for path in sorted(root.glob("D[23]/*/status.json")):
            print(path.parent.name, json.dumps(read(path)))
    elif args.command == "summarize":
        evidence_summary(Path(args.output))
    else:
        pack(Path(args.output).resolve(), load_config(args.config), Path(args.destination).resolve(), not args.include_images)


if __name__ == "__main__":
    main()
