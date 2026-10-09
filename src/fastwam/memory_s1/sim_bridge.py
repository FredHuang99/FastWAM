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
from .data import mosaic_rgb, observation_tensor, collate, history_variant, load_evidence
from .history import select_ids, online_period
from .protocol import format_task_prompt, inference_contract


class InferenceSession:
    def __init__(self, model, cfg, encoders, condition, output, evidence, seed, trace=None):
        self.model, self.cfg = model, cfg
        self.trace = trace
        self.vae, self.text_encoder, self.tokenizer = encoders
        self.normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
        self.condition, self.output, self.evidence, self.seed = condition, Path(output), evidence, seed
        self.device = next(model.memory.parameters()).device
        self.reference = None
        if condition == "native_base":
            from .native_reference import build_reference
            self.reference = build_reference(model.backbone, encoders)
        self.reset()

    def reset(self):
        self.archive = {}
        self.raw_archive = {}
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
            if self.reference is None:
                self.text, self.text_valid = encode_text(self.text_encoder, self.tokenizer, self.instruction, self.device)
            else:
                self.text, self.text_valid = self.reference.encode_prompt(format_task_prompt(self.instruction))
        elif request["instruction"] != self.instruction or request["episode_seed"] != self.episode_seed:
            raise ValueError("Instruction/episode changed without reset.")
        current_id = int(request["current_id"])
        current_latent = current_proprio = current_feature = current_kv = current_context = None
        started = time.monotonic()
        if self.reference is not None:
            return self.decide_native(request, started)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            for observation in request["observations"]:
                index = int(observation["frame_id"])
                if index < 0 or index > current_id:
                    raise ValueError("Negative/future observation ID.")
                signature = hashlib.sha256(b"".join(observation["images"]) + json.dumps([observation["shapes"], observation["proprio"]]).encode()).hexdigest()
                if index in self.raw_archive and self.observation_signatures[index] != signature:
                    raise ValueError("The same frame ID has different observation content.")
                self.raw_archive[index] = observation
                self.observation_signatures[index] = signature
            period = online_period(self.cfg, current_id)
            if self.cfg.get("history", {}).get("archive_stride", 8) == 1:
                if sorted(self.raw_archive) != list(range(current_id + 1)):
                    raise ValueError("Dense online archive is missing completed-action observations.")
            indices = select_ids(sorted(self.raw_archive), current_id, period)
            if indices != select_ids(range(current_id + 1), current_id, period):
                raise ValueError("Raw archive lacks observations required by this historical period.")
            if self.condition in ("gate_zero", "current_only"):
                indices = [current_id]
            newly_encoded = []
            for index in indices:
                if index in self.archive and index != current_id:
                    continue
                observation = self.raw_archive[index]
                images = [np.frombuffer(raw, dtype=np.uint8).reshape(shape) for raw, shape in zip(observation["images"], observation["shapes"])]
                mosaic = observation_tensor(images, self.device)
                proprio = self.normalizer.normalize(torch.tensor(observation["proprio"], device=self.device)[None], "state")
                latent = encode_latent(self.vae, mosaic)
                feature, kv, context = self.model.backbone.encode_observation(latent, self.text, proprio, keep_kv=index == current_id)
                self.archive[index] = feature[0].detach().cpu()
                newly_encoded.append(index)
                if index == current_id:
                    current_latent, current_proprio, current_feature, current_kv, current_context = latent, proprio, feature, kv, context
                    if self.trace is not None:
                        from .checkpoint import to_cpu
                        self.trace.update(to_cpu({"mosaic": mosaic, "proprio": proprio,
                            "latent": latent, "feature": feature, "kv": kv,
                            "text": self.text, "context": context[0], "context_mask": context[1]}))
            if current_latent is None:
                raise ValueError("Current observation must be uploaded.")
            sample = {"latent": current_latent[0], "proprio": current_proprio[0], "text": self.text[0],
                      "text_valid": self.text_valid[0], "history": torch.stack([self.archive[i] for i in indices]).to(self.device),
                      "frame_ids": torch.tensor(indices, device=self.device),
                      "history_valid": torch.ones(len(indices), device=self.device, dtype=torch.bool),
                      "actions": torch.zeros(32, 14, device=self.device), "action_valid": torch.ones(32, device=self.device, dtype=torch.bool),
                      "t": torch.tensor(current_id, device=self.device)}
            annotation = None
            if self.condition in ("delete_critical", "delete_irrelevant"):
                annotation = self.evidence["online"][request["task"]][str(self.episode_seed)]
            sample = history_variant(sample, self.condition, annotation)
            batch = {key: value[None] for key, value in sample.items()}
            readout = None if self.condition == "gate_zero" else self.model.memory.read(
                current_feature, self.text, self.text_valid, current_proprio,
                batch["history"], batch["frame_ids"], batch["history_valid"])
            noise_seed = seed_for(self.seed, self.episode_seed, current_id, "closed-loop-noise")
            generator = torch.Generator(device="cpu").manual_seed(noise_seed)
            noise = torch.randn(1, 32, 14, generator=generator).to(self.device)
            if self.trace is not None:
                self.trace["noise"] = noise.detach().cpu()
            actions, _ = self.model.sample(batch, noise, gate_scale=0 if self.condition == "gate_zero" else 1,
                                           prepared_conditions=(current_kv, current_context, readout))
        return self.finish_actions(request, actions[0], started, period, indices, sample["frame_ids"].tolist(), newly_encoded, readout, noise_seed)

    @torch.no_grad()
    def decide_native(self, request, started):
        from .native_reference import native_actions
        current_id = int(request["current_id"])
        for observation in request["observations"]:
            index = int(observation["frame_id"])
            if not 0 <= index <= current_id:
                raise ValueError("Negative/future observation ID.")
            self.raw_archive[index] = observation
        if current_id not in self.raw_archive:
            raise ValueError("Native reference requires the current observation.")
        observation = self.raw_archive[current_id]
        images = [np.frombuffer(raw, dtype=np.uint8).reshape(shape) for raw, shape in zip(observation["images"], observation["shapes"])]
        mosaic = observation_tensor(images, self.device)
        state = self.normalizer.normalize(torch.tensor(observation["proprio"], device=self.device)[None], "state")
        noise_seed = seed_for(self.seed, self.episode_seed, current_id, "closed-loop-noise")
        actions = native_actions(self.reference, mosaic, state, noise_seed, context=self.text)
        return self.finish_actions(request, actions, started, online_period(self.cfg, current_id), [current_id], [], [], None, noise_seed)

    def finish_actions(self, request, normalized, started, period, selected, read_ids, newly_encoded, readout, noise_seed):
        actions = self.normalizer.denormalize(normalized)
        if not torch.isfinite(actions).all():
            raise FloatingPointError("Non-finite generated action.")
        before_clip = actions.detach().cpu().tolist()
        if self.trace is not None:
            self.trace["normalized_actions"] = normalized.detach().float().cpu()
            self.trace["denormalized_actions"] = actions.detach().cpu()[None].clone()
        grippers = actions[:, [6, 13]]
        clipped = int(((grippers < 0) | (grippers > 1)).sum())
        actions[:, [6, 13]] = grippers.clamp(0, 1)
        if self.trace is not None:
            self.trace["clipped_actions"] = actions.detach().cpu().clone()
        torch.cuda.synchronize(self.device)
        append_jsonl(self.output / "decisions.jsonl", {"task": request["task"], "seed": self.episode_seed, "frame_id": int(request["current_id"]),
                                                       "condition": self.condition, "archive_frames": len(self.archive),
                                                       "raw_archive_frames": len(self.raw_archive), "history_period": period,
                                                       "selected_frame_ids": selected, "read_frame_ids": read_ids if readout is not None else [],
                                                       "newly_encoded_frame_ids": newly_encoded,
                                                       "read_frames": 0 if readout is None else len(read_ids),
                                                       "readout_norm": None if readout is None else float(readout.float().norm(dim=-1).mean()),
                                                       "seconds": time.monotonic() - started, "gripper_clipped_scalars": clipped,
                                                       "predict": 32, "execute": 16, "instruction": self.instruction,
                                                       "prompt": format_task_prompt(self.instruction), "noise_seed": noise_seed,
                                                       "inference_contract": inference_contract(),
                                                       "normalized_actions": normalized.detach().float().cpu().tolist(),
                                                       "actions_before_gripper_clip": before_clip,
                                                       "actions_after_gripper_clip": actions.detach().cpu().tolist()})
        return {"actions": actions.cpu().tolist()}


def run_closed_loop(cfg, weights, mode, conditions, output, resident_model=None, record_frames=False, evidence=None):
    """Compatibility API; new standalone evaluation uses independent GPU workers."""
    from types import SimpleNamespace
    from .eval_parallel import (standalone, gpu_inventory, gpu_uuid_for_model, prepare_scenes,
                                evaluation_identity, worker_loop)
    from .eval_state import EpisodeQueue, durable_json, summarize
    output = Path(output).resolve()
    if resident_model is not None:
        from .checkpoint import random_state, restore_random_state
        state = random_state()
        try:
            output.mkdir(parents=True, exist_ok=True)
            contract, scenes, _ = prepare_scenes(cfg, mode, [gpu_uuid_for_model(resident_model)], output)
            identity = evaluation_identity(cfg, contract, scenes, conditions, weights, evidence, record_frames)
            EpisodeQueue(output).initialize(identity, scenes, conditions, resume=(output / "queue.json").exists())
            durable_json(output / "scenes.json", {"contract": contract, "scenes": scenes})
            worker_loop(cfg, output, "resident", resident_model=resident_model, record_frames=record_frames, evidence=evidence)
            return summarize(output, mode, require_complete=True)
        finally:
            restore_random_state(state)
    raise ValueError("Use python -m fastwam.memory_s1.eval_parallel run for standalone evaluation; training uses distributed_validation on all ranks.")


def main():
    from .eval_parallel import standalone, gpu_inventory
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--weights")
    parser.add_argument("--mode", choices=("diagnostic", "internal", "official"), required=True)
    parser.add_argument("--conditions", nargs="+", default=["full"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--evidence")
    parser.add_argument("--record-frames", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--hf-results", action="store_true")
    parser.add_argument("--gpus")
    parser.add_argument("--episode-timeout", type=int, default=2400)
    args = parser.parse_args()
    if args.mode != "diagnostic" and not args.weights:
        parser.error("Internal/official evaluation requires trained --weights.")
    if args.gpus is None:
        inventory = gpu_inventory()
        visible = os.environ.get("CUDA_VISIBLE_DEVICES")
        if visible:
            inverse = {value: key for key, value in inventory.items()}
            args.gpus = ",".join(str(inverse[token] if token.startswith("GPU-") else int(token)) for token in visible.split(","))
        else:
            args.gpus = ",".join(map(str, inventory))
    raise SystemExit(standalone(args))


if __name__ == "__main__":
    main()
