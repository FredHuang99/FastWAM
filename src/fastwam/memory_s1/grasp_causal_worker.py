"""Bounded component controls with real feedback, no fitting or new scenes."""
from __future__ import annotations

import argparse
import hashlib
from multiprocessing.connection import Listener
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import traceback

import numpy as np

from .grasp_bridge import checked_path, read, write, signature, verify, owned_popen, stop_children
from .grasp_causal import (CausalBlocked, case_identity, completed_case, require_prepared, stop_check)
from .grasp_causal_metrics import MODES, compose, physical_metrics
from .initial_intervention_worker import append, rows, finish, reuse_or_archive, initial_alignment


def progress(output, mode, phase, completed, **extra):
    write(output / "PROGRESS.json", {"mode": mode, "phase": phase, "completed": completed,
                                   "updated_unix": time.time(), **extra})


def weight_loader_binding(root, bound):
    """Adapt immutable relative provenance to the existing strict loader API."""
    record = bound["weights"]["step_002000"]
    path = checked_path(root, record["relative"])
    verify(root, {record["relative"]: record["sha256"]})
    return {"weights": {"step_002000": {"path": str(path), "sha256": record["sha256"]}},
            "resources": bound["resources"]}


def reference_handoff(output, bound, actual, source):
    """Observe an existing boundary only. No render/step/success calls."""
    spec = bound["protocol"]
    if actual["target_id"] != spec["expert_prefix_targets"]:
        raise ValueError("Handoff must be the observation after exactly 48 targets")
    path = output / "HANDOFF_REFERENCE.json"
    if not path.exists():
        write(path, {"identity": signature(bound), "source": source, "trace": actual})
        return {"passed": True, "reference": source, "established": True}
    recorded = read(path)
    if recorded["identity"] != signature(bound):
        raise ValueError("Handoff reference identity changed")
    expected = recorded["trace"]
    errors = []
    if actual["rgb"] != expected["rgb"]:
        errors.append("rendered RGB hashes")
    for field in ("physical", "command_state"):
        if not np.allclose(actual[field], expected[field], atol=spec["handoff_atol"], rtol=0):
            errors.append(field)
    if set(actual["objects"]) != set(expected["objects"]):
        errors.append("object inventory")
    else:
        for name, pose in expected["objects"].items():
            value = actual["objects"][name]
            if isinstance(pose, dict) and "p" in pose:
                for field in ("p", "q"):
                    if not np.allclose(value[field], pose[field], atol=spec["handoff_atol"], rtol=0):
                        errors.append(name + "." + field)
            elif value != pose:
                errors.append(name)
    if errors:
        raise CausalBlocked("Common expert handoff differs: " + ", ".join(errors) + "; no post-handoff target was executed")
    return {"passed": True, "reference": recorded["source"], "established": False,
            "physical_atol": spec["handoff_atol"], "rgb_exact": True}


class ComponentRouter:
    def __init__(self, session, mode, output, directory, bound, expert, item, folder):
        self.session, self.mode, self.output, self.directory = session, mode, output, directory
        self.bound, self.expert, self.item, self.folder = bound, expert, item, folder
        self.targets = np.asarray(expert["targets"], np.float32)
        self.next_frame, self.last_observation = 0, -1
        self.prefix_observations, self.reset_seen = [], False
        self.initial_reset_count = 0

    def handle(self, request):
        spec = self.bound["protocol"]
        if request["command"] == "reset":
            # RPCPolicy.__init__ and the official episode entry both reset.
            # Repeats before the first decision are idempotent; never erase a
            # partially handled observation or restart an active trajectory.
            if self.next_frame or self.last_observation != -1 or self.prefix_observations:
                append(self.directory / "rpc_lifecycle.jsonl", {"command": "reset", "accepted": False,
                       "reason": "decision_started", "next_frame": self.next_frame,
                       "last_observation": self.last_observation})
                raise ValueError("Unexpected mid-episode reset after a decision started")
            repeated = self.reset_seen
            if self.session is not None and not repeated:
                self.session.reset()
            self.initial_reset_count += 1
            append(self.directory / "rpc_lifecycle.jsonl", {"command": "reset", "accepted": True,
                   "ordinal": self.initial_reset_count, "idempotent_repeat": repeated,
                   "next_frame": self.next_frame, "last_observation": self.last_observation,
                   "protocol": spec["rpc_reset_protocol"]})
            self.reset_seen = True
            print(f"[rpc] {self.mode} initialization reset={self.initial_reset_count} "
                  f"idempotent_repeat={repeated}; targets=0", flush=True)
            return {"ok": True}
        if request["command"] != "decide" or not self.reset_seen:
            raise ValueError("Expected reset then decide")
        frame = int(request["current_id"])
        if frame != self.next_frame or not 0 <= frame < spec["target_cap"]:
            raise ValueError(f"Skipped/duplicate/out-of-budget request {frame}; expected {self.next_frame}")
        if any(request[a] != self.item[b] for a, b in
               (("task", "task"), ("episode_seed", "seed"), ("instruction", "instruction"))):
            raise ValueError("Frozen scene/instruction/seed differs")
        observations = request["observations"]
        expected_ids = list(range(self.last_observation + 1, frame + 1))
        if [int(row["frame_id"]) for row in observations] != expected_ids:
            raise ValueError("Missing/repeated actual observations")
        for row in observations:
            proprio = np.asarray(row["proprio"])
            if len(row["images"]) != 3 or len(row["shapes"]) != 3 or proprio.shape != (14,) or not np.isfinite(proprio).all():
                raise ValueError("Invalid three-view observation/proprioception")
        if frame == 0:
            initial_alignment(request, self.item, self.folder, self.expert, self.directory)
        if frame == spec["expert_prefix_targets"]:
            trace = next(r for r in rows(self.directory / "qualification_trace.jsonl") if r["target_id"] == frame)
            write(self.directory / "handoff_alignment.json", reference_handoff(self.output, self.bound, trace, self.mode))
        self.last_observation = frame
        predicted, inherited, decision = None, [], None
        if frame < spec["expert_prefix_targets"]:
            self.prefix_observations.extend(observations)
        elif self.mode != "expert":
            actual = request
            if self.prefix_observations:
                inherited = [r["frame_id"] for r in self.prefix_observations]
                actual = dict(request, observations=self.prefix_observations + observations)
                if frame != 48 or [r["frame_id"] for r in actual["observations"]] != list(range(49)):
                    raise ValueError("Model takeover must receive actual observations 0..48 exactly once")
                self.prefix_observations = []
            response = self.session.decide(actual)
            predicted = response["actions"]
            # Use the actual inference log rather than re-drawing or re-resolving T/noise.
            decision = rows(self.directory / "decisions.jsonl")[-1]
            if decision["frame_id"] != frame or sorted(self.session.raw_archive) != list(range(frame + 1)):
                raise ValueError("Model history/decision log is not this real request")
        effective = compose(self.mode, frame, predicted, self.targets, spec["expert_prefix_targets"])
        append(self.directory / "interventions.jsonl", {"frame_id": frame, "task": self.item["task"],
               "component_mode": self.mode, "role": "expert_prefix" if frame < 48 else self.mode,
               "noise_rule": "none" if predicted is None else "unchanged_closed_loop_seed_derivation",
               "noise_seed": None if decision is None else decision["noise_seed"],
               "history_sampling": None if decision is None else decision["history_sampling"],
               "read_frame_ids": [] if decision is None else decision["read_frame_ids"],
               "observation_ids_received": expected_ids, "inherited_prefix_ids": inherited,
               "predicted_actions": predicted, "expert_actions": self.targets[frame:frame + 32].tolist(),
               "actions": effective.tolist(), "action_chunk_sha256": hashlib.sha256(effective.tobytes()).hexdigest(),
               "executed_target_ids": list(range(frame + 1, frame + 17))})
        self.next_frame += 16
        return {"ok": True, "actions": effective.tolist()}


def summarize_case(directory, mode, bound, expert, source):
    value = read(directory / "simulator_result.json")
    spec = bound["protocol"]
    if (value["status"] != "complete" or value["target_limit"] != spec["target_cap"]
            or value["task"] != spec["task"] or value["seed"] != expert["scene"]["seed"]
            or value["executed_targets"] <= spec["expert_prefix_targets"]
            or (value["executed_targets"] < spec["target_cap"] and not value["success"])):
        raise ValueError("Incomplete/wrong simulator prefix; do not count this as policy failure")
    actions = rows(directory / "executed_actions.jsonl")
    observations = rows(directory / "observations.jsonl")
    interventions = rows(directory / "interventions.jsonl")
    if len(actions) != value["executed_targets"]:
        raise ValueError("Simulator count and evidence count differ")
    if source in ("fresh", "verified_previous_expert"):
        for row in interventions:
            expected = compose(mode, row["frame_id"], row["predicted_actions"], expert["targets"], spec["expert_prefix_targets"])
            if not np.array_equal(expected, np.asarray(row["actions"], np.float32)):
                raise ValueError("Component replacement columns differ from the declared intervention")
    metrics, trajectory = physical_metrics(actions, observations, interventions, expert, spec)
    initialization = {"protocol": spec["rpc_reset_protocol"], "source": source}
    if source in ("fresh", "verified_previous_expert"):
        lifecycle = rows(directory / "rpc_lifecycle.jsonl")
        if (not lifecycle or any(not row.get("accepted") or row.get("command") != "reset"
                or row.get("ordinal") != index + 1 or row.get("next_frame") != 0
                or row.get("last_observation") != -1 or row.get("idempotent_repeat") != (index > 0)
                or row.get("protocol") != spec["rpc_reset_protocol"]
                for index, row in enumerate(lifecycle))):
            raise ValueError("Initial RPC resets lack a complete idempotent lifecycle receipt")
        initialization["reset_requests"] = len(lifecycle)
    else:
        initialization["reset_requests"] = None
        initialization["limitation"] = "RPC lifecycle was not separately recorded in the historical policy case"
    append_path = directory / "trajectory_metrics.jsonl"
    if append_path.exists():
        append_path.unlink()
    for row in trajectory:
        append(append_path, row)
    write(directory / "phase_metrics.json", metrics["phase_metrics"])
    return {"mode": mode, "checkpoint_step": 2000, "source": source, "metrics": metrics,
            "official_success_observed": bool(value["success"]), "termination": value["termination"],
            "timings": value["timings"], "rpc_initialization": initialization,
            "benchmark_accuracy": None, "optimizer_updates": 0,
            "component_scope": "policy feedback is real; expert fields substituted only in returned commands"}


def inherit_policy(output, bound, expert):
    import shutil
    reuse = read(output / "BASELINE_REUSE.json")
    if not reuse["eligible"]:
        return False
    directory = output / "cases/policy"
    if completed_case(output, bound, "policy"):
        return True
    verify(output / "baseline_policy", reuse["files"])
    reuse_or_archive(directory, case_identity(bound, "policy"))
    for name in reuse["files"]:
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        # Historical signatures/results remain historical, never overwritten as approvals.
        if name in ("COMPLETE.json", "result.json"):
            target = target.with_name("historical_" + target.name)
        shutil.copy2(output / "baseline_policy" / name, target)
    trace = next(r for r in rows(directory / "qualification_trace.jsonl") if r["target_id"] == 48)
    write(directory / "handoff_alignment.json", reference_handoff(output, bound, trace, "historical_policy"))
    result = summarize_case(directory, "policy", bound, expert, "verified_historical")
    result["inheritance"] = reuse
    finish(directory, case_identity(bound, "policy"), result)
    print("[reuse] policy baseline authenticated; no model/simulator episode was rerun", flush=True)
    return True


def inherit_expert(output, bound, expert):
    import shutil
    reuse = read(output / "EXPERT_REUSE.json")
    if not reuse["eligible"]:
        return False
    directory = output / "cases/expert"
    if completed_case(output, bound, "expert"):
        return True
    prior = reuse["previous_run_identity"]
    if (signature(prior) != reuse["historical_identity"]
            or read(output / "baseline_expert/COMPLETE.json")["identity"] != case_identity(prior, "expert")):
        raise ValueError("Inherited expert provenance differs from its original completion receipt")
    verify(output / "baseline_expert", reuse["files"])
    reuse_or_archive(directory, case_identity(bound, "expert"))
    for name in reuse["files"]:
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if name in ("COMPLETE.json", "result.json"):
            target = target.with_name("historical_" + target.name)
        shutil.copy2(output / "baseline_expert" / name, target)
    interventions = rows(directory / "interventions.jsonl")
    if any(row["predicted_actions"] is not None or row["component_mode"] != "expert"
           for row in interventions):
        raise ValueError("Inherited pure-expert control contains policy predictions")
    trace = next(r for r in rows(directory / "qualification_trace.jsonl") if r["target_id"] == 48)
    write(directory / "handoff_alignment.json", reference_handoff(output, bound, trace, "verified_previous_expert"))
    result = summarize_case(directory, "expert", bound, expert, "verified_previous_expert")
    result["inheritance"] = reuse
    finish(directory, case_identity(bound, "expert"), result)
    print("[reuse] completed expert control verified and recomputed; no simulator episode was rerun", flush=True)
    return True


def run_case(root, output, bound, mode, expert, item, folder, gpu, model, encoders, completed):
    from .eval_parallel import simulator_environment
    from .selection_runtime import live_details, format_active, duration
    from .simulator_backend import configured_backend
    directory = output / "cases" / mode
    if completed_case(output, bound, mode):
        print(f"[reuse] {mode} complete and checksummed", flush=True)
        return
    reuse_or_archive(directory, case_identity(bound, mode))
    session = None
    if mode != "expert":
        from .sim_bridge import InferenceSession
        session = InferenceSession(model, bound["config"], encoders, "full", directory, None, bound["config"]["seed"])
    router = ComponentRouter(session, mode, output, directory, bound, expert, item, folder)
    scene = expert["scene"]
    if any(scene[key] != item[key] for key in ("task", "seed", "instruction")):
        raise ValueError("Expert scene and initial policy input differ")
    write(directory / "job.json", {"id": "causal:" + mode, "attempt": 1, "scene": scene, "condition": "full"})
    cfg, spec = bound["config"], bound["protocol"]
    key = os.urandom(24)
    events = directory / "simulator_progress"
    env = simulator_environment(cfg, gpu)
    env.update(MEMORY_S1_RPC_KEY=key.hex(), MEMORY_S1_PROGRESS_ROOT=str(events), MEMORY_S1_RECORD_FRAME_STRIDE="1")
    child, started, last = None, time.monotonic(), 0.
    progress(output, mode, "simulator_start", completed, targets=0)
    try:
        with tempfile.TemporaryDirectory(prefix="causal-", dir=output / "tmp") as sockets:
            socket = Path(sockets) / "rpc.sock"
            command = [cfg["closed_loop"]["simulator_python"], "-u", str(root / "scripts/memory_s1/sim_eval.py"),
                       "--operation", "episode", "--job", str(directory / "job.json"), "--output", str(directory),
                       "--socket", str(socket), "--seed", str(cfg["seed"]), "--gpu-uuid", gpu,
                       "--stop-root", str(output), "--record-frames", "--record-feedback", "--qualification-trace",
                       "--max-targets", str(spec["target_cap"]), "--scene-count", "1"]
            write(directory / "command.json", command)
            with Listener(str(socket), family="AF_UNIX", authkey=key) as listener, (directory / "simulator.log").open("w", encoding="utf-8") as log:
                listener._listener._socket.settimeout(1)
                child = owned_popen(command, cwd=root / cfg["closed_loop"]["simulator_root"], env=env, stdout=log, stderr=subprocess.STDOUT)
                while child.poll() is None:
                    stop_check(output)
                    elapsed = time.monotonic() - started
                    if elapsed > spec["case_timeout_seconds"]:
                        raise TimeoutError(f"{mode} exceeded bounded wall time; infrastructure error, not policy failure")
                    if elapsed - last >= 15:
                        active = live_details(events)
                        target_rows = [r for r in active if r.get("targets") is not None]
                        target = max((r["targets"] for r in target_rows), default=max(0, router.next_frame - 16))
                        measured = [r for r in target_rows if r.get("rollout_seconds") is not None and r["targets"] >= 16]
                        eta = None
                        if measured:
                            rate = max(max(r.get("seconds_per_target") or 0,
                                      (r["rollout_seconds"] + r.get("heartbeat_age_seconds", 0)) / r["targets"]) for r in measured)
                            eta = max(0, spec["target_cap"] - target) * rate
                        stage = active[-1]["phase"] if active else "initializing"
                        progress(output, mode, stage, completed, targets=target, elapsed_seconds=elapsed,
                                 current_target_cap_eta_seconds=eta,
                                 eta_scope="current rollout to cap; model load/warmup/cleanup/other cases excluded")
                        print(f"[component] {mode} {completed}/4 targets={target}/128 elapsed={duration(elapsed)} "
                              f"current_rollout_ETA~{duration(eta)} (measured targets, excludes initialization/other cases)", flush=True)
                        for row in active:
                            print("  " + format_active(row), flush=True)
                        last = elapsed
                    try:
                        connection = listener.accept()
                    except TimeoutError:
                        continue
                    with connection:
                        if not connection.poll(15):
                            raise TimeoutError("Simulator connected without a request")
                        try:
                            reply = router.handle(connection.recv())
                        except BaseException:
                            connection.send({"ok": False, "error": traceback.format_exc()})
                            raise
                        connection.send(reply)
                if child.returncode:
                    raise RuntimeError(f"Simulator exited {child.returncode}:\n{(directory/'simulator.log').read_text(errors='replace')[-12000:]}")
        value = read(directory / "simulator_result.json")
        if value.get("simulator_backend") != configured_backend(cfg):
            raise ValueError("Actual simulator backend differs")
        backend_files = list(events.glob("fused_backend_*.json"))
        if len(backend_files) < 2 or any(not read(p)["passed"] for p in backend_files):
            raise ValueError("Both-arm fused/graph evidence missing or failed")
        if any(read(p)["extensions"] != bound["simulator_extensions"] for p in backend_files):
            raise ValueError("Actual loaded fused extension identities differ from preparation")
        result = summarize_case(directory, mode, bound, expert, "fresh")
        result.update(gpu_uuid=gpu, wall_seconds=time.monotonic() - started)
    finally:
        if child is not None:
            stop_children([child])
        if session is not None:
            session.reset()
    finish(directory, case_identity(bound, mode), result)
    print(f"[complete case] {mode} lift={result['metrics']['max_lift_after_handoff_m']:.4f}m "
          f"lift_contact_proxy={result['metrics']['lift_contact_proxy_observed']} accuracy=not_applicable", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--gpu-uuid", required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    bound = require_prepared(root, output)
    loader_binding = weight_loader_binding(root, bound)
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Causal worker stopped")))
    folder = output / "frozen"
    bundle = read(folder / "FROZEN.json")
    item = bundle["inputs"]["swap_blocks_online_initial"]
    expert = read(folder / bundle["experts"]["swap_blocks"]["path"])
    model, encoders = None, None
    try:
        inherit_policy(output, bound, expert)
        inherit_expert(output, bound, expert)
        for mode in MODES:
            stop_check(output)
            existing = completed_case(output, bound, mode)
            if existing:
                continue
            completed = sum(completed_case(output, bound, name) is not None for name in MODES)
            if mode in ("expert_arm", "expert_gripper"):
                positive = completed_case(output, bound, "expert")
                if positive is None or not positive["metrics"]["lift_contact_proxy_observed"]:
                    raise CausalBlocked("Expert positive-control lift/contact was not observed within 128 targets; mixed cases deferred for review")
            if mode != "expert" and model is None:
                progress(output, mode, "model_load", completed)
                import torch
                from .model import S1Model, load_observation_encoders
                from .diagnosis_gpu import load_weight
                if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
                    raise ValueError("Expose exactly the bound single H100")
                model = S1Model(bound["config"], torch.device("cuda:0")).eval()
                load_weight(model, loader_binding, "step_002000")
                encoders = load_observation_encoders(bound["config"], torch.device("cuda:0"))
            run_case(root, output, bound, mode, expert, item, folder, args.gpu_uuid, model, encoders, completed)
        progress(output, "all", "complete", 4, targets=128)
    except CausalBlocked as error:
        write(output / "BLOCKED.json", {"reason": str(error), "identity": signature(bound), "time": time.time()})
        print(f"[blocked] {error}; report and pack remain available", flush=True)
        raise SystemExit(3)
    except BaseException:
        write(output / "ERROR.json", {"traceback": traceback.format_exc(), "identity": signature(bound), "time": time.time()})
        raise


if __name__ == "__main__":
    main()
