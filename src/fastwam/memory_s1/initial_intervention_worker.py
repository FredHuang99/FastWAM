"""One-GPU worker: reuse production simulator/RPC, change only explicit treatments."""
from __future__ import annotations

import argparse
import hashlib
import json
from multiprocessing.connection import Listener
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import traceback

import numpy as np

from .grasp_bridge import read, write, sha, signature, files, verify, owned_popen, stop_children
from .initial_intervention import TASKS, check_stop


def append(path, row):
    with Path(path).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, allow_nan=False) + "\n")


def rows(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def finish(directory, identity, result):
    write(directory / "result.json", result)
    mapping = {k: v for k, v in files(directory).items() if k != "COMPLETE.json"
               and "interrupted" not in Path(k).parts and not k.endswith(".log")}
    write(directory / "COMPLETE.json", {"identity": identity, "files": mapping})


def reuse_or_archive(directory, identity):
    if (directory / "COMPLETE.json").exists():
        record = read(directory / "COMPLETE.json")
        if record["identity"] != identity:
            raise ValueError(f"Case identity changed: {directory}")
        verify(directory, record["files"])
        print(f"[reuse] {directory.name}", flush=True)
        return True
    if directory.exists():
        archive = directory.parent / "interrupted" / f"{directory.name}_{time.time_ns()}"
        archive.parent.mkdir(parents=True, exist_ok=True)
        directory.rename(archive)
    directory.mkdir(parents=True)
    return False


def initial_alignment(request, item, folder, expert, directory):
    from PIL import Image
    observation = request["observations"][0]
    if observation["frame_id"] != 0 or not np.array_equal(np.asarray(observation["proprio"], np.float32), np.asarray(item["proprio"], np.float32)):
        raise ValueError("Initial command state differs from frozen observation")
    hashes = []
    for raw, shape, name in zip(observation["images"], observation["shapes"], item["images"]):
        actual = np.frombuffer(raw, dtype=np.uint8).reshape(shape)
        with Image.open(folder / name) as image:
            expected = np.asarray(image.convert("RGB"))
        if not np.array_equal(actual, expected):
            raise ValueError(f"Initial rendered pixels differ from the paired input: {name}")
        hashes.append(hashlib.sha256(actual.tobytes()).hexdigest())
    trace = rows(directory / "qualification_trace.jsonl")
    if len(trace) != 1 or trace[0]["target_id"] != 0:
        raise ValueError("Missing initial physical scene trace")
    actual = trace[0]
    initial = expert["initial"]
    if not np.allclose(actual["physical"], initial["physical"], atol=1e-5, rtol=0):
        raise ValueError("Expert initial physical robot state differs")
    for name, expected in initial["objects"].items():
        if isinstance(expected, dict) and "p" in expected:
            if name not in actual["objects"] or any(not np.allclose(actual["objects"][name][key], expected[key], atol=1e-5, rtol=0) for key in ("p", "q")):
                raise ValueError(f"Expert initial object pose differs: {name}")
    write(directory / "initial_alignment.json", {"passed": True, "pixels_sha256": hashes,
          "physical_atol": 1e-5, "source": "frozen same-scene expert and online initial observation"})


class Intervention:
    """Only this private RPC handler can inject noise or return expert targets."""
    def __init__(self, session, stage, task, folder, bundle, directory, output):
        self.session, self.stage, self.task = session, stage, task
        self.folder, self.directory, self.output = folder, directory, output
        self.item = bundle["inputs"][task + "_online_initial"]
        expert_path = folder / bundle["experts"][task]["path"]
        if sha(expert_path) != bundle["experts"][task]["sha256"]:
            raise ValueError("Frozen expert source changed")
        self.expert = read(expert_path)
        self.expert_targets = np.asarray(self.expert["targets"], dtype=np.float32)
        if self.expert_targets.ndim != 2 or self.expert_targets.shape[1] != 14 or len(self.expert_targets) < 64 or not np.isfinite(self.expert_targets).all():
            raise ValueError("Expected at least 64 finite original expert targets")
        info = bundle["noise"][task]["offline"]
        noise_path = folder / info["path"]
        if sha(noise_path) != info["sha256"]:
            raise ValueError("Saved offline noise changed")
        self.noise = np.load(noise_path, allow_pickle=False)
        if self.noise.shape != (1, 32, 14) or self.noise.dtype != np.float32 or not np.isfinite(self.noise).all():
            raise ValueError("Expected the saved finite float32 [1,32,14] noise")
        self.next_frame = 0
        self.last_observation = -1
        self.prefix_observations = []
        self.reset_seen = False

    def handle(self, request):
        if request["command"] == "reset":
            if self.next_frame:
                raise ValueError("Unexpected mid-episode reset; preserve this interrupted attempt")
            self.session.reset()
            self.reset_seen = True
            return {"ok": True}
        if request["command"] != "decide" or not self.reset_seen:
            raise ValueError("Expected reset then decide")
        frame = int(request["current_id"])
        if frame != self.next_frame or frame >= 128:
            raise ValueError(f"Duplicate/skipped/out-of-budget decision: {frame}, expected {self.next_frame}")
        if (request["task"] != self.task or request["episode_seed"] != self.item["seed"]
                or request["instruction"] != self.item["instruction"]):
            raise ValueError("Frozen task/scene/instruction mismatch")
        observations = request["observations"]
        expected = list(range(self.last_observation + 1, frame + 1))
        if [int(row["frame_id"]) for row in observations] != expected:
            raise ValueError("Missing/duplicate real observations between action blocks")
        for row in observations:
            if len(row["images"]) != 3 or len(row["shapes"]) != 3:
                raise ValueError("Expected all three views")
            state = np.asarray(row["proprio"])
            if state.shape != (14,) or not np.isfinite(state).all():
                raise ValueError("Invalid observed proprioception")
        if frame == 0:
            initial_alignment(request, self.item, self.folder, self.expert, self.directory)
        self.last_observation = frame
        inherited = []
        override = self.stage == "first-noise" and frame == 0
        if self.stage == "expert-prefix" and frame < 48:
            self.prefix_observations.extend(observations)
            actions = self.expert_targets[frame:frame+32].tolist()
            role = "expert_prefix"
            noise_rule = "none; no model/no noise draw"
        else:
            actual_request = request
            if self.prefix_observations:
                inherited = [row["frame_id"] for row in self.prefix_observations]
                actual_request = dict(request, observations=self.prefix_observations + observations)
                if [row["frame_id"] for row in actual_request["observations"]] != list(range(49)) or frame != 48:
                    raise ValueError("Takeover must receive actual frames 0..48 exactly once")
                self.prefix_observations = []
            role = "policy"
            self.session.trace = {} if override else None
            response = self.session.decide(actual_request, diagnostic_noise=self.noise if override else None)
            actions = response["actions"]
            noise_rule = "frozen_offline_first_block" if override else "unchanged_closed_loop_seed_derivation"
            if override:
                trace = self.session.trace
                with np.load(self.output / "baselines" / f"{self.task}_offline.npz", allow_pickle=False) as baseline:
                    actual = trace["normalized_actions"].float().numpy()
                    if not np.array_equal(actual, baseline["normalized"][0]):
                        raise ValueError("First intervention prediction differs from reviewed offline-noise baseline; no action executed")
                write(self.directory / "first_prediction_verified.json", {"exact": True, "baseline": f"{self.task}_offline.npz"})
                self.session.trace = None
            if sorted(self.session.raw_archive) != list(range(frame + 1)):
                raise ValueError("Policy history lacks a real completed-target observation")
        array = np.asarray(actions, np.float32)
        if array.shape != (32, 14) or not np.isfinite(array).all():
            raise ValueError("Invalid action chunk")
        append(self.directory / "interventions.jsonl", {"frame_id": frame, "task": self.task, "role": role,
               "noise_rule": noise_rule, "override_noise_sha256": hashlib.sha256(self.noise.tobytes()).hexdigest() if override else None,
               "observation_ids_received": expected, "inherited_prefix_ids": inherited,
               "policy_raw_ids": sorted(self.session.raw_archive), "executed_target_ids": list(range(frame+1, frame+17)),
               "action_chunk_sha256": hashlib.sha256(array.tobytes()).hexdigest(), "actions": array.tolist()})
        self.next_frame += 16
        return {"ok": True, "actions": array.tolist()}


def physical_summary(directory, stage, task, expert):
    result = read(directory / "simulator_result.json")
    count = int(result["executed_targets"])
    if result["status"] != "complete" or result["target_limit"] != 128 or not 0 < count <= 128:
        raise ValueError("Incorrect status/target cap/count; not a model failure")
    if count < 128 and not result["success"]:
        raise ValueError("Incomplete prefix without an official success")
    actions = rows(directory / "executed_actions.jsonl")
    observations = rows(directory / "observations.jsonl")
    if [r["completed_target_id"] for r in actions] != list(range(1, count+1)) or [r["frame_id"] for r in observations] != list(range(count)):
        raise ValueError("Executed target / observed frame numbering is incomplete")
    interventions = rows(directory / "interventions.jsonl")
    if [r["frame_id"] for r in interventions] != list(range(0, count, 16)):
        raise ValueError("Incomplete decision coverage")
    for row in actions:
        number = row["completed_target_id"] - 1
        requested = interventions[number // 16]["actions"][number % 16]
        if not np.array_equal(np.asarray(row["target"], np.float32), np.asarray(requested, np.float32)):
            raise ValueError("Executor target differs from the returned action queue")
        if row["physics_step_id"] is None or row["physics_steps"] is None or row["physics_steps"] < 0:
            raise ValueError("Missing physical clock")
    # An observation must occur at the previous target boundary, without advancing physics.
    if observations[0]["physics_step_id"] != 0 or any(
            observations[i]["physics_step_id"] != actions[i-1]["physics_step_id"] for i in range(1, count)):
        raise ValueError("Observation/RPC advanced physics between targets")
    prefix = 48 if stage == "expert-prefix" else 0
    if prefix and count <= prefix:
        raise ValueError("Expert prefix ended before policy takeover; report as blocked, not a policy result")
    if prefix:
        expected = np.asarray(expert["targets"][:48], np.float32)
        if not np.array_equal(np.asarray([r["target"] for r in actions[:48]], np.float32), expected):
            raise ValueError("Expert prefix command stream differs")
    lifts = {}
    baseline = actions[0]["objects_before"]
    at_handoff = actions[prefix-1]["objects_after"] if prefix else baseline
    for name, value in baseline.items():
        if not isinstance(value, dict) or "p" not in value:
            continue
        heights = [(r["completed_target_id"], r["objects_after"][name]["p"][2]) for r in actions if name in r["objects_after"]]
        policy = [(i, z) for i, z in heights if i > prefix]
        lifts[name] = {"max_lift_from_initial": max(z for _, z in heights)-value["p"][2],
                       "at_handoff_lift": at_handoff[name]["p"][2]-value["p"][2],
                       "policy_max_additional_lift": max(z for _, z in policy)-at_handoff[name]["p"][2],
                       "policy_peak_target_id": max(policy, key=lambda pair: pair[1])[0]}
    write(directory / "physical_summary.json", {"objects": lifts, "scope": "completed-target samples; lift does not prove a stable grasp"})
    return {"stage": stage, "task": task, "seed": result["seed"], "executed_targets": count,
            "expert_targets": min(prefix, count), "policy_targets": max(0, count-prefix),
            "first_right_close": next((r["completed_target_id"] for r in actions if r["target"][13] < .5), None),
            "wrist_tracking_mae_rad": float(np.mean([r["physical_abs_error"][12] for r in actions])),
            "object_lifts_m": lifts, "timings": result["timings"], "task_accuracy": None,
            "official_success_observed": bool(result["success"]), "termination": result["termination"],
            "scope": "diagnostic only; expert-assisted prefix is never counted as policy success"}


def run_case(root, output, bound, stage, task, model, encoders, gpu):
    from .eval_parallel import simulator_environment
    from .sim_bridge import InferenceSession
    from .selection_runtime import live_details, format_active
    from .simulator_backend import configured_backend
    identity = signature(bound)
    directory = output / stage / task
    if reuse_or_archive(directory, identity):
        return
    write(output / stage / "progress.json", {"stage": "simulator_start", "task": task, "started_unix": time.time()})
    cfg = bound["config"]
    folder = output / "frozen"
    bundle = read(folder / "FROZEN.json")
    session = InferenceSession(model, cfg, encoders, "full", directory, None, cfg["seed"])
    router = Intervention(session, stage, task, folder, bundle, directory, output)
    scene = router.expert["scene"]
    if any(scene[key] != router.item[key] for key in ("task", "seed", "instruction")):
        raise ValueError("Expert scene and frozen policy input differ")
    job = {"id": f"{stage}:{task}", "attempt": 1, "scene": scene, "condition": "full"}
    write(directory / "job.json", job)
    key = os.urandom(24)
    progress = directory / "simulator_progress"
    env = simulator_environment(cfg, gpu)
    env.update(MEMORY_S1_RPC_KEY=key.hex(), MEMORY_S1_PROGRESS_ROOT=str(progress), MEMORY_S1_RECORD_FRAME_STRIDE="1")
    child = None
    started = time.monotonic()
    try:
        with tempfile.TemporaryDirectory(prefix="s1-initial-", dir="/tmp") as sockets:
            socket_path = Path(sockets) / "rpc.sock"
            command = [cfg["closed_loop"]["simulator_python"], "-u", str(root / "scripts/memory_s1/sim_eval.py"),
                       "--operation", "episode", "--job", str(directory / "job.json"), "--output", str(directory),
                       "--socket", str(socket_path), "--seed", str(cfg["seed"]), "--gpu-uuid", gpu,
                       "--stop-root", str(output), "--record-frames", "--record-feedback", "--qualification-trace",
                       "--max-targets", "128", "--scene-count", "1"]
            write(directory / "command.json", command)
            with Listener(str(socket_path), family="AF_UNIX", authkey=key) as listener, (directory / "simulator.log").open("w", encoding="utf-8") as log:
                listener._listener._socket.settimeout(1)
                child = owned_popen(command, cwd=root / cfg["closed_loop"]["simulator_root"], env=env, stdout=log, stderr=subprocess.STDOUT)
                last = 0.0
                while child.poll() is None:
                    check_stop(output)
                    elapsed = time.monotonic()-started
                    if elapsed > bound["protocol"]["case_timeout_seconds"]:
                        raise TimeoutError(f"{task} exceeded bounded wall time; this is an infrastructure error, not task failure")
                    if elapsed-last >= 15:
                        details = live_details(progress)
                        print(f"[{stage}] task={task} elapsed={elapsed:.0f}s cap=128", flush=True)
                        for detail in details:
                            print("  " + format_active(detail), flush=True)
                        write(output / stage / "progress.json", {"stage": stage, "task": task, "elapsed_seconds": elapsed,
                              "active": details, "updated_unix": time.time()})
                        last = elapsed
                    try:
                        connection = listener.accept()
                    except TimeoutError:
                        continue
                    with connection:
                        if not connection.poll(15):
                            raise TimeoutError("Simulator connected without sending its request")
                        request = connection.recv()
                        try:
                            reply = router.handle(request)
                        except BaseException:
                            connection.send({"ok": False, "error": traceback.format_exc()})
                            raise
                        connection.send(reply)
                if child.returncode != 0:
                    raise RuntimeError(f"Simulator exited {child.returncode}:\n" + (directory / "simulator.log").read_text(errors="replace")[-16000:])
        value = read(directory / "simulator_result.json")
        if value["simulator_backend"] != configured_backend(cfg):
            raise ValueError("Simulator backend contract changed")
        backends = list(progress.glob("fused_backend_*.json"))
        if len(backends) < 2 or any(not read(path)["passed"] for path in backends):
            raise ValueError("Both-arm fused backend evidence is missing/failed")
        result = physical_summary(directory, stage, task, router.expert)
        result.update(gpu_uuid=gpu, wall_seconds=time.monotonic()-started)
    finally:
        if child is not None:
            stop_children([child])
        session.reset()
    # No file from a live simulator is signed as completed.
    finish(directory, identity, result)
    print(f"[case complete] {stage} {task} targets={result['executed_targets']}/128; task_acc=not_applicable", flush=True)


def micro(root, output, bound, model, encoders):
    """Conditional fit of ONE real training initial window; never writes weights."""
    import torch
    from .grasp_diagnosis import direct, request_for
    from .common import ReleaseNormalizer
    directory = output / "micro"
    identity = signature(bound)
    # A micro run is atomic; an interrupted run restarts from original step 2000.
    for old in list(directory.iterdir()):
        if old.name in ("command.json", "interrupted") or old.suffix == ".log":
            continue
        destination = directory / "interrupted" / f"{old.name}_{time.time_ns()}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        old.rename(destination)
    cfg = bound["config"]
    folder = output / "frozen"
    bundle = read(folder / "FROZEN.json")
    device = next(model.memory.parameters()).device
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    saved = {key: value.detach().cpu().clone() for key, value in model.memory.state_dict().items()}
    prepared = {}
    measurements = []
    train_id = "put_back_block_train_initial"
    train_item = bundle["inputs"][train_id]
    if train_item["origin"]["split"] != "train" or train_item["anchor"] != 0 or not train_item["targets"]:
        raise ValueError("Only the reviewed actual training initial window may be fitted")
    taus = ((torch.arange(16, dtype=torch.float32) + .5) / 16).tolist()
    write(directory / "protocol.json", {"train_window": train_id, "train_noise": "online", "updates": 16,
          "tau_schedule": taus, "learning_rate": cfg["learning_rate"], "optimizer": "fresh AdamW; original parameter groups; betas=.9,.95",
          "gradient_clip": 1.0, "weight_output": None, "scope": "local fitting diagnostic; not S1 continuation"})
    def to_device(value):
        if isinstance(value, torch.Tensor):
            return value.to(device)
        if isinstance(value, dict):
            return {key: to_device(v) for key, v in value.items()}
        return value
    try:
        for key, item in bundle["inputs"].items():
            check_stop(output)
            noise = torch.from_numpy(np.load(folder / bundle["noise"][item["task"]]["online"]["path"], allow_pickle=False))
            trace = direct(model, encoders, cfg, request_for(folder, item), noise)
            batch = to_device(trace["batch"])
            target = item["targets"] if item["targets"] is not None else read(folder / bundle["experts"][item["task"]]["path"])["targets"][:32]
            target = torch.as_tensor(target, dtype=torch.float32, device=device)[None]
            if target.shape != (1, 32, 14):
                raise ValueError("Initial micro windows must have 32 real targets; no fabricated padding")
            batch["actions"] = normalizer.normalize(target, "action")
            prepared[key] = (item, batch, target)
            del trace
        def measure(label):
            model.eval()
            for key, (item, batch, target) in prepared.items():
                for name in ("online", "offline", "independent"):
                    check_stop(output)
                    noise = torch.from_numpy(np.load(folder / bundle["noise"][item["task"]][name]["path"], allow_pickle=False)).to(device)
                    with torch.no_grad():
                        prediction, _ = model.sample(batch, noise)
                        native = normalizer.denormalize(prediction.float())
                    error = (native[:, :16] - target[:, :16]).abs().mean((0, 1)).cpu().tolist()
                    item_result = {"phase": label, "input": key, "noise": name,
                         "fit_condition": key == train_id and name == "online", "joint_mae_first16": error,
                         "wrist_target16": float(native[0, 15, 12]), "expert_wrist_target16": float(target[0, 15, 12])}
                    measurements.append(item_result)
                    append(directory / "actions.jsonl", item_result)
                    np.savez_compressed(directory / f"{label}_{key}_{name}.npz", native=native.cpu().numpy(), target=target.cpu().numpy())
                    print(f"[micro {label}] {key} noise={name} wrist_mae={error[12]:.6f}", flush=True)
        measure("before")
        batch = prepared[train_id][1]
        noise = torch.from_numpy(np.load(folder / bundle["noise"][train_item["task"]]["online"]["path"], allow_pickle=False)).to(device)
        optimizer = torch.optim.AdamW(model.memory.parameter_groups(), lr=cfg["learning_rate"], betas=(.9, .95))
        if any(p.requires_grad for p in model.backbone.parameters()):
            raise ValueError("Base must remain frozen")
        for index, tau in enumerate(taus, 1):
            check_stop(output)
            model.train()
            optimizer.zero_grad(set_to_none=True)
            loss, detail = model(batch, noise, torch.tensor([tau], device=device))
            if not torch.isfinite(loss):
                raise FloatingPointError("Nonfinite isolated loss")
            loss.backward()
            gradients = {name: float(p.grad.float().norm()) for name, p in model.memory.named_parameters() if p.grad is not None}
            if not gradients or not all(np.isfinite(v) for v in gradients.values()) or max(gradients.values()) == 0:
                raise FloatingPointError("Missing/nonfinite/all-zero memory gradients on the actual failing sample")
            if any(p.grad is not None for p in model.backbone.parameters()):
                raise ValueError("Frozen base acquired a gradient")
            norm = torch.nn.utils.clip_grad_norm_(model.memory.parameters(), 1., error_if_nonfinite=True)
            optimizer.step()
            if any(not torch.isfinite(p).all() for p in model.memory.parameters()):
                raise FloatingPointError("Isolated optimizer produced nonfinite parameters")
            append(directory / "updates.jsonl", {"update": index, "tau": tau, "loss": float(loss.detach()),
                   "unweighted_fm": float(detail["unweighted_fm"].mean()), "grad_norm": float(norm), "parameter_gradients": gradients})
            print(f"[micro] isolated_update={index}/16 loss={float(loss.detach()):.6f} grad={float(norm):.6f}", flush=True)
        measure("after")
        changed = sum(not torch.equal(value.detach().cpu(), saved[key]) for key, value in model.memory.state_dict().items())
        if not changed:
            raise ValueError("No memory parameters changed during isolated fitting")
    finally:
        model.memory.load_state_dict(saved, strict=True)
        model.eval()
    if not all(torch.equal(value.detach().cpu(), saved[key]) for key, value in model.memory.state_dict().items()):
        raise ValueError("Could not restore original in-memory weights")
    finish(directory, identity, {"optimizer_updates": 16, "original_weights_restored": True,
           "weight_file_written": False, "changed_tensors_before_restore": changed, "measurements": measurements,
           "root_cause": "Interpret fixed-condition improvement separately from held-out noise/input change; no automatic retraining"})


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("stage", choices=("first-noise", "expert-prefix", "micro"))
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-uuid", required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Worker terminated")))
    bound = read(output / "IDENTITY.json")
    try:
        prior_error = output / args.stage / "ERROR.json"
        if prior_error.exists():
            saved_error = output / args.stage / "interrupted" / f"ERROR_{time.time_ns()}.json"
            saved_error.parent.mkdir(parents=True, exist_ok=True)
            prior_error.rename(saved_error)
        import torch
        from .eval_state import cuda_gpu_uuid
        from .integration_contract import configure_numerics
        from .model import S1Model, load_observation_encoders
        from .diagnosis_gpu import load_weight
        cfg = bound["config"]
        if torch.cuda.device_count() != 1 or cuda_gpu_uuid(0) != args.gpu_uuid or torch.cuda.get_device_capability(0) != (9, 0):
            raise ValueError("One bound H100 must be visible")
        configure_numerics(cfg)
        print("[model_load] step=2000, no dense dataset/cache; initialization ETA=unknown", flush=True)
        write(output / args.stage / "progress.json", {"stage": "model_load", "started_unix": time.time()})
        device = torch.device("cuda:0")
        model = S1Model(cfg, device).eval()
        encoders = load_observation_encoders(cfg, device)
        bundle = read(output / "frozen/FROZEN.json")
        load_weight(model, {"weights": {"step_002000": {"path": str(root / bound["weight"]["relative"]), "sha256": bound["weight"]["sha256"]}},
                           "resources": bundle["resources"]}, "step_002000")
        if args.stage == "micro":
            micro(root, output, bound, model, encoders)
        else:
            for index, task in enumerate(TASKS, 1):
                check_stop(output)
                print(f"[{args.stage}] case={index}/2 task={task} cap=128", flush=True)
                run_case(root, output, bound, args.stage, task, model, encoders, args.gpu_uuid)
            mapping = {}
            for task in TASKS:
                directory = output / args.stage / task
                verify(directory, read(directory / "COMPLETE.json")["files"])
                mapping.update({f"{task}/{k}": v for k, v in files(directory).items()})
            write(output / args.stage / "COMPLETE.json", {"identity": signature(bound), "files": mapping})
        print(f"[complete] {args.stage}; original checkpoint unchanged", flush=True)
    except BaseException:
        write(output / args.stage / "ERROR.json", {"traceback": traceback.format_exc()})
        raise


if __name__ == "__main__":
    main()
