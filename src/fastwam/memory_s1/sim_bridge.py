"""Synchronous inference RPC and owned simulator subprocesses, with cleanup."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from multiprocessing.connection import Listener, Client

import numpy as np
import torch

from .common import TASKS, ReleaseNormalizer, atomic_json, append_jsonl, load_config, read_json, seed_for, sha256
from .data import mosaic_rgb, collate, history_variant, load_evidence


class InferenceSession:
    def __init__(self, model, cfg, encoders, condition, output, evidence, seed):
        self.model, self.cfg = model, cfg
        self.vae, self.text_encoder, self.tokenizer = encoders
        self.normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
        self.condition, self.output, self.evidence, self.seed = condition, Path(output), evidence, seed
        self.device = next(model.memory.parameters()).device
        self.reset()

    def reset(self):
        self.archive = {}
        self.observation_signatures = {}
        self.instruction = None
        self.text = self.text_valid = None
        self.episode_seed = None

    @torch.no_grad()
    def decide(self, request):
        from .model import encode_text, encode_latent
        if self.instruction is None:
            self.instruction = request["instruction"]
            self.episode_seed = int(request["episode_seed"])
            self.text, self.text_valid = encode_text(self.text_encoder, self.tokenizer, self.instruction, self.device)
        elif request["instruction"] != self.instruction or request["episode_seed"] != self.episode_seed:
            raise ValueError("Instruction/episode changed without reset.")
        current_id = int(request["current_id"])
        current_latent = current_proprio = current_feature = current_kv = current_context = None
        started = time.monotonic()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            for observation in request["observations"]:
                index = int(observation["frame_id"])
                if index > current_id or (index % 8 != 0 and index != current_id):
                    raise ValueError("Invalid/future observation slot.")
                signature = hashlib.sha256(b"".join(observation["images"]) + json.dumps([observation["shapes"], observation["proprio"]]).encode()).hexdigest()
                if index in self.archive:
                    if self.observation_signatures[index] != signature:
                        raise ValueError("The same frame_id was reused for different observation content.")
                    if index != current_id:
                        continue
                images = [np.frombuffer(raw, dtype=np.uint8).reshape(shape) for raw, shape in zip(observation["images"], observation["shapes"])]
                mosaic = mosaic_rgb(images)[None].to(self.device)
                proprio = self.normalizer.normalize(torch.tensor(observation["proprio"], device=self.device)[None], "state")
                latent = encode_latent(self.vae, mosaic)
                feature, kv, context = self.model.backbone.encode_observation(latent, self.text, proprio, keep_kv=index == current_id)
                self.archive[index] = feature[0].detach()
                self.observation_signatures[index] = signature
                if index == current_id:
                    current_latent, current_proprio, current_feature, current_kv, current_context = latent, proprio, feature, kv, context
            if current_latent is None or 0 not in self.archive:
                raise ValueError("Current observation and initial episode evidence must be uploaded.")
            indices = sorted(self.archive)
            sample = {"latent": current_latent[0], "proprio": current_proprio[0], "text": self.text[0],
                      "text_valid": self.text_valid[0], "history": torch.stack([self.archive[i] for i in indices]),
                      "frame_ids": torch.tensor(indices, device=self.device),
                      "history_valid": torch.ones(len(indices), device=self.device, dtype=torch.bool),
                      "actions": torch.zeros(32, 14, device=self.device), "action_valid": torch.ones(32, device=self.device, dtype=torch.bool),
                      "t": torch.tensor(current_id, device=self.device)}
            annotation = None
            if self.condition in ("delete_critical", "delete_irrelevant"):
                annotation = self.evidence["online"][request["task"]][str(self.episode_seed)]
            sample = history_variant(sample, self.condition, annotation)
            batch = {key: value[None] for key, value in sample.items()}
            readout = self.model.memory.read(current_feature, self.text, self.text_valid, current_proprio,
                                             batch["history"], batch["frame_ids"], batch["history_valid"])
            generator = torch.Generator(device="cpu").manual_seed(seed_for(self.seed, self.episode_seed, current_id, "closed-loop-noise"))
            noise = torch.randn(1, 32, 14, generator=generator).to(self.device)
            actions, _ = self.model.sample(batch, noise, gate_scale=0 if self.condition == "gate_zero" else 1,
                                           prepared_conditions=(current_kv, current_context, readout))
            actions = self.normalizer.denormalize(actions[0])
        if not torch.isfinite(actions).all():
            raise FloatingPointError("Non-finite generated action.")
        grippers = actions[:, [6, 13]]
        clipped = int(((grippers < 0) | (grippers > 1)).sum())
        actions[:, [6, 13]] = grippers.clamp(0, 1)
        torch.cuda.synchronize(self.device)
        append_jsonl(self.output / "decisions.jsonl", {"task": request["task"], "seed": self.episode_seed, "frame_id": current_id,
                                                       "condition": self.condition, "archive_frames": len(self.archive),
                                                       "read_frames": len(sample["frame_ids"]), "readout_norm": float(readout.float().norm(dim=-1).mean()),
                                                       "seconds": time.monotonic() - started, "gripper_clipped_scalars": clipped,
                                                       "predict": 32, "execute": 16})
        return {"actions": actions.cpu().tolist()}


def serve_process(listener, process, session):
    listener._listener._socket.settimeout(2.0)
    while process.poll() is None:
        try:
            connection = listener.accept()
        except TimeoutError:
            continue
        with connection:
            request = connection.recv()
            try:
                if request["command"] == "reset":
                    session.reset()
                    response = {"ok": True}
                elif request["command"] == "decide":
                    response = {"ok": True, **session.decide(request)}
                else:
                    raise ValueError("Unknown RPC command.")
            except Exception as error:
                response = {"ok": False, "error": repr(error)}
            connection.send(response)
    if process.returncode:
        raise RuntimeError(f"Simulator exited with code={process.returncode}.")


def run_closed_loop(cfg, weights, mode, conditions, output, resident_model=None, record_frames=False, evidence=None):
    from .model import S1Model, load_observation_encoders
    if not cfg["closed_loop"]["enabled"]:
        raise ValueError("Closed-loop validation is required for selecting the S1 checkpoint.")
    own_model = resident_model is None
    model = S1Model(cfg, torch.device("cuda:0")) if own_model else resident_model
    if own_model and weights:
        value = torch.load(weights, map_location="cpu", weights_only=True)
        if value["identity"]["base_sha256"] != sha256(cfg["paths"]["base"]) or value["identity"]["stats_sha256"] != sha256(cfg["paths"]["stats"]):
            raise ValueError("Evaluation weights refer to a different base or normalization.")
        model.memory.load_state_dict(value["memory"], strict=True)
    model.eval()
    device = next(model.memory.parameters()).device
    encoders = load_observation_encoders(cfg, device)
    episodes = cfg["closed_loop"]["internal_episodes"] if mode in ("internal", "diagnostic") else cfg["closed_loop"]["official_episodes"]
    seed = cfg["closed_loop"]["internal_seed"] if mode in ("internal", "diagnostic") else cfg["closed_loop"]["official_seed"]
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    all_results = []
    try:
        for condition in conditions:
            for task in TASKS:
                directory = output / condition / task
                directory.mkdir(parents=True, exist_ok=True)
                socket_path = directory / "policy.sock"
                if socket_path.exists():
                    raise FileExistsError(f"Stale/live socket exists: {socket_path}; inspect before retrying.")
                key = os.urandom(24)
                process = None
                with Listener(str(socket_path), family="AF_UNIX", authkey=key) as listener:
                    environment = dict(os.environ)
                    environment["MEMORY_S1_RPC_KEY"] = key.hex()
                    environment["PYTHONUNBUFFERED"] = "1"
                    # Keep each simulator in its isolated CUDA 12.4 environment.
                    simulator_prefix = Path(cfg["closed_loop"]["simulator_python"]).parent.parent
                    environment["CUDA_HOME"] = str(simulator_prefix)
                    environment["PATH"] = str(simulator_prefix / "bin") + os.pathsep + environment["PATH"]
                    environment["LD_LIBRARY_PATH"] = str(simulator_prefix / "lib") + os.pathsep + environment.get("LD_LIBRARY_PATH", "")
                    command = [cfg["closed_loop"]["simulator_python"], str(Path(cfg["root"]) / "scripts/memory_s1/sim_eval.py"),
                               "--socket", str(socket_path), "--task", task, "--output", str(directory),
                               "--episodes", str(episodes), "--seed", str(seed), "--mode", mode]
                    if record_frames:
                        command += ["--record-frames"]
                    sim_root = Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]
                    with (directory / "simulator.log").open("w") as log:
                        try:
                            process = subprocess.Popen(command, cwd=sim_root, env=environment, stdout=log, stderr=subprocess.STDOUT)
                            session = InferenceSession(model, cfg, encoders, condition, directory, evidence, seed)
                            serve_process(listener, process, session)
                        finally:
                            if process is not None and process.poll() is None:
                                process.terminate()
                                try:
                                    process.wait(timeout=20)
                                except subprocess.TimeoutExpired:
                                    process.kill()
                                    process.wait()
                result = read_json(directory / "results.json")
                all_results.extend([{**row, "condition": condition, "task": task} for row in result["episodes"]])
        reference = {}
        for condition in conditions:
            for task in TASKS:
                rows = [row for row in all_results if row["task"] == task and row["condition"] == condition]
                seeds = [row["seed"] for row in rows]
                if task in reference and reference[task] != seeds:
                    raise ValueError("Accepted scenario seeds changed across interventions; results are not comparable.")
                reference[task] = seeds
        full = [row for row in all_results if row["condition"] == conditions[0]]
        summary = {"mode": mode, "success_rate": sum(row["success"] for row in full) / len(full), "episodes": all_results,
                   "protocol": "Official expert-feasible seed filtering and success predicate; internal count is separately marked.",
                   "conditions": {condition: {"success_rate": sum(row["success"] for row in all_results if row["condition"] == condition) / sum(row["condition"] == condition for row in all_results)} for condition in conditions}}
        def rate(rows):
            import math
            count = len(rows)
            proportion = sum(row["success"] for row in rows) / count
            denominator = 1 + 1.96**2 / count
            center = (proportion + 1.96**2 / (2 * count)) / denominator
            half = 1.96 * math.sqrt(proportion * (1-proportion) / count + 1.96**2 / (4 * count**2)) / denominator
            return {"episodes": count, "success_rate": proportion, "wilson_95": [center-half, center+half]}
        summary["by_task"] = {task: {condition: rate([row for row in all_results if row["task"] == task and row["condition"] == condition])
                                     for condition in conditions} for task in TASKS}
        atomic_json(output / "summary.json", summary)
        return summary
    finally:
        del encoders
        gc.collect()
        torch.cuda.empty_cache()
        if not own_model:
            model.train()


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--weights")
    parser.add_argument("--mode", choices=("diagnostic", "internal", "official"), required=True)
    parser.add_argument("--conditions", nargs="+", default=["full"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--evidence")
    parser.add_argument("--record-frames", action="store_true")
    args = parser.parse_args()
    if args.mode != "diagnostic" and not args.weights:
        parser.error("Internal/official evaluation requires trained --weights.")
    if any(condition.startswith("delete_") for condition in args.conditions) and not args.evidence:
        parser.error("Deletion conditions require a reviewed --evidence manifest.")
    cfg = load_config(args.config)
    result = run_closed_loop(cfg, args.weights, args.mode, args.conditions, args.output,
                             record_frames=args.record_frames, evidence=load_evidence(args.evidence) if args.evidence else None)
    print(f"[eval] success_rate={result['success_rate']:.4f}; results={args.output}", flush=True)


if __name__ == "__main__":
    main()
