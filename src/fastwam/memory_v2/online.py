"""memory_v2 closed loop on RMBench (policy side).

Built on Codex's dense-joint online path (/restore-tmp/dense_joint_v1/physical.py: Session + rollout), which runs
the frozen C+256 policy in the production simulator with 32 predicted / 24 executed actions, the dense float image
contract (data_path.mosaic) and an exact command-to-execution check. The simulator side is a self-contained copy
of Codex's adapter (scripts/memory_v2/sim/, adds an optional target cap for smoke tests); the policy side is new:

  * frozen C+256 (ABModel with its memory_s1 readout, online rule T=8 / episode-seeded phase / decision stride 24,
    exactly as physical.rollout configures it)
  * + memory_v2: history chosen by memory_v2.history.select_history, the same function as offline training;
    per-frame post-Video-DiT features computed online with the same call as FeatureStore.build
  * memory modes: on | null (history masked, learned null tokens) | off (memory_v2 bypassed = C+256)
  * --dependence: at every decision also sample the other modes from the same noise and log how much the executed
    chunk would change without memory (arm RMSE, radians, executed prefix)

Commands (policy python /opt/mwam, PYTHONPATH=<memory2>/src, cwd <memory2>):
  preflight : read-only inventory of everything the loop needs (GPUs, dense delivery, simulator envs, CuRobo
              extensions, existing expert-feasible scene banks, checkpoints); no model, no GPU memory
  parity    : online-path features/batches/actions vs the offline cache path on dense val windows (GPU, minutes)
  plan      : expert-feasible scene bank per task (production sim_eval --operation plan)
  run       : roll out one checkpoint in one or more memory modes over a scene bank (resumable, shardable)
  summary   : success / lift / reward / memory dependence per (label, mode, task) + paired comparisons
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

LIMITS = {"put_back_block": 500, "swap_blocks": 1000}        # official target caps (Codex's frozen protocol)
EXECUTE = 24
HORIZON = 32
REPO = Path(__file__).resolve().parents[3]                   # <memory2>/src/fastwam/memory_v2/online.py -> <memory2>
SIM_CODE = REPO / "scripts/memory_v2/sim"
SEED_DIR = re.compile(r"seed_\d+")


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".{os.getpid()}.partial")
    tmp.write_text(json.dumps(value, indent=1, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def append(path, value):
    with Path(path).open("a", encoding="utf-8") as f:
        f.write(json.dumps(value, allow_nan=False) + "\n")


def execution_count(frame: int, limit: int) -> int:
    if not 0 <= frame < limit:
        raise ValueError("Target outside the official limit")
    return min(EXECUTE, limit - frame)


def apply_overrides(value: dict, overrides: Sequence[str]) -> dict:
    """key.sub=value (YAML-parsed), the same syntax as train_v2 --set."""
    import yaml
    value = copy.deepcopy(value)
    for item in overrides:
        key, _, raw = item.partition("=")
        target = value
        parts = key.split(".")
        for part in parts[:-1]:
            target = target.setdefault(part, {})
        target[parts[-1]] = yaml.safe_load(raw)
    return value


def policy_config(config: Path, checkpoint: Optional[str], overrides: Sequence[str]):
    """The checkpoint's own training config (+ --set overrides); the YAML only for 'init'."""
    import torch
    from .train_v2 import TrainConfig, load_config
    if checkpoint and checkpoint != "init":
        state = torch.load(checkpoint, map_location="cpu", weights_only=False, mmap=True)
        return TrainConfig.from_dict(apply_overrides(state["config"], overrides)), state
    return load_config(config, overrides), None


def run_label(checkpoint: Optional[str]) -> str:
    if not checkpoint or checkpoint == "init":
        return "init"
    path = Path(checkpoint)
    return path.parent.parent.name if path.parent.name == "checkpoints" else path.stem


def assemble(encoded: Dict[int, tuple], text, text_valid, current: int, selection, s1_ids: Optional[List[int]],
             tokens_per_frame: int = 120, width: int = 3072) -> dict:
    """One decision's memory_v2 batch (CPU), key for key what dense.make_batch builds offline.

    encoded[i] = (latent [48,1,24,20], normalised proprio [14], post-Video-DiT feature [120,3072] bf16);
    text [1,L,D], text_valid [1,L]; s1_ids = memory_s1's past frames (current excluded) or None (no s1 base).
    """
    import torch
    from .history import collate_history
    latent, proprio, _ = encoded[current]
    history = collate_history([[encoded[i][2] for i in selection.ids]], [selection], tokens_per_frame=tokens_per_frame,
                              width=width, dtype=torch.bfloat16)
    batch = {"latent": latent[None], "text": text, "text_valid": text_valid, "proprio": proprio[None],
             "actions": torch.zeros(1, HORIZON, 14), "action_valid": torch.ones(1, HORIZON, dtype=torch.bool), **history}
    if s1_ids is not None:
        n = max(1, len(s1_ids))
        s1_history = torch.zeros(1, n, tokens_per_frame, width, dtype=torch.bfloat16)
        s1_frames = torch.zeros(1, n, dtype=torch.long)
        s1_valid = torch.zeros(1, n, dtype=torch.bool)
        for j, i in enumerate(s1_ids):
            s1_history[0, j], s1_frames[0, j], s1_valid[0, j] = encoded[i][2], i, True
        batch.update(s1_history=s1_history, s1_frame_ids=s1_frames, s1_valid=s1_valid)
    return batch


# ============================================================================ policy
class Policy:
    """Frozen C+256 + a memory_v2 checkpoint (+ observation encoders for the closed loop)."""

    def __init__(self, cfg, state, checkpoint: str, device="cuda:0", encoders: bool = True, t5_on_gpu: Optional[bool] = None):
        import torch
        from . import dense
        from .model import MemoryV2Model
        from fastwam.memory_s1.common import ReleaseNormalizer
        self.torch, self.device, self.cfg, self.checkpoint = torch, torch.device(device), cfg, checkpoint
        self.spec = dense.DenseSpec.from_dict(cfg.dense)
        self.ab, self.info = dense.load_ab_model(self.spec, cfg.init_checkpoint, str(self.device))
        if cfg.base_memory == "none" and hasattr(self.ab, "memory"):
            del self.ab.memory
        self.adapter = dense.DenseActionAdapter(self.ab, train_action=False, base_memory=cfg.base_memory)
        self.model = MemoryV2Model(self.adapter, cfg.v2.memory)
        self.model.memory.to(device=self.device, dtype=torch.float32)
        self.trained_action = False
        if state is not None:
            self.model.memory.load_state_dict(state["memory"], strict=True)
            if state.get("action") is not None:
                self.trained_action = True
                named = dict(self.ab.backbone.mot.mixtures["action"].named_parameters())
                with torch.no_grad():
                    for n, v in state["action"].items():
                        named[n].copy_(v.to(named[n].device, named[n].dtype))
        self.model.eval()
        # Codex's online configuration of the base (physical.rollout): memory_s1 reads T=8, phase from the dense
        # config's online rule (episode-seeded), decision stride 24, every executed target archived.
        self.dense_cfg = copy.deepcopy(dense.dense_config(self.spec))
        self.dense_cfg.setdefault("history", {}).update(online_mode="fixed", online_cycle=[], online_period=cfg.s1_period,
                                                        archive_stride=1)
        self.s1 = dense.S1Policy(period=cfg.s1_period) if cfg.base_memory == "s1" else None
        self.normaliser = ReleaseNormalizer(self.path("stats"))
        self.vae = self.t5 = self.tokenizer = self.mosaic = None
        self.t5_on_gpu = None
        if encoders:
            from fastwam.models.wan22.helpers.loader import _load_registered_model
            from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
            self.vae = _load_registered_model(self.path("vae"), "wan_video_vae", torch.bfloat16, str(self.device))
            self.vae.eval().requires_grad_(False)
            if t5_on_gpu is None:                          # 40 GB cards: park the T5 on the CPU between episodes
                t5_on_gpu = torch.cuda.get_device_properties(self.device).total_memory > 60 * 2 ** 30
            self.t5_on_gpu = bool(t5_on_gpu)
            self.t5 = _load_registered_model(self.path("t5"), "wan_video_text_encoder", torch.bfloat16,
                                             str(self.device) if self.t5_on_gpu else "cpu")
            self.t5.eval().requires_grad_(False)
            self.tokenizer = HuggingfaceTokenizer(self.path("tokenizer"), seq_len=128, clean="whitespace",
                                                  local_files_only=True)
            dense.bind(self.spec)                           # dense delivery code on sys.path
            from data_path import mosaic                    # official_robotwin_float_two_resize_v1 (Codex)
            self.mosaic = mosaic

    def path(self, key: str) -> str:
        value = Path(self.dense_cfg["paths"][key])
        return str(value if value.is_absolute() else Path(self.spec.root) / value)

    def encode_text(self, instruction: str):
        from fastwam.memory_s1.model import encode_text
        if self.t5_on_gpu:
            return encode_text(self.t5, self.tokenizer, instruction, self.device)
        self.t5.to(self.device)
        try:
            return encode_text(self.t5, self.tokenizer, instruction, self.device)
        finally:
            self.t5.to("cpu")
            self.torch.cuda.empty_cache()

    def base_label(self, label: str) -> str:
        """memory_v2 'off' is the C+256 policy itself whenever the action expert and base are the released ones."""
        plain = (not self.trained_action and self.cfg.init_checkpoint in ("source", "", None) and self.cfg.base_memory == "s1")
        return "C256" if plain else f"{label}_off"

    def describe(self) -> dict:
        return {"checkpoint": self.checkpoint, "init_checkpoint": self.cfg.init_checkpoint, "base_memory": self.cfg.base_memory,
                "s1_period": self.cfg.s1_period, "history_policy": dict(self.cfg.v2.history.__dict__),
                "guidance": dict(self.cfg.v2.guidance.__dict__), "trained_action": self.trained_action,
                "dense_identity": self.info.get("dense_identity"), "video_digest": self.info.get("video_digest"),
                "software_drift": self.info.get("software_drift"), "t5_on_gpu": self.t5_on_gpu}


class Session:
    """One episode: raw observation archive -> cached per-frame encodings -> memory_v2 decisions."""

    def __init__(self, policy: Policy, directory: Path, mode: str, steps: int, guidance_scale: float, dependence: bool,
                 tag: str = "", limit: int = 0):
        self.p, self.directory, self.mode = policy, Path(directory), mode
        self.steps, self.scale, self.dependence, self.tag, self.limit = steps, guidance_scale, dependence, tag, limit
        self.reset()

    def reset(self):
        self.raw: Dict[int, dict] = {}
        self.encoded: Dict[int, tuple] = {}
        self.text = self.text_valid = self.instruction = self.seed = self.task = None
        self.decisions = 0
        self.started = time.monotonic()

    def _encode(self, ids):
        import numpy as np
        from fastwam.memory_s1.model import encode_latent
        torch, p = self.p.torch, self.p
        for i in ids:
            if i in self.encoded:
                continue
            r = self.raw[i]
            arrays = [np.frombuffer(b, dtype=np.uint8).reshape(s) for b, s in zip(r["images"], r["shapes"])]
            image = p.mosaic(arrays)[None].to(p.device, torch.bfloat16)
            latent = encode_latent(p.vae, image)                                       # [1, 48, 1, 24, 20]
            proprio = p.normaliser.normalize(torch.tensor(r["proprio"], dtype=torch.float32)[None], "state").to(p.device)
            feature = p.ab.encode(latent, self.text, proprio, keep_kv=False)[0]         # [1, 120, 3072]
            self.encoded[i] = (latent[0].cpu(), proprio[0].cpu(), feature[0].to(torch.bfloat16).cpu())

    def decide(self, request: dict):
        from fastwam.memory_s1.common import seed_for
        from fastwam.memory_s1.history import resolve_online, select_ids
        from fastwam.memory_s1.sim_bridge import diagnostic_action_noise
        from .config import GuidanceConfig
        from .dense import ARM_COLUMNS
        from .history import select_history
        torch, p = self.p.torch, self.p
        start = time.monotonic()
        current = int(request["current_id"])
        with torch.no_grad():
            if self.text is None:
                self.instruction, self.seed, self.task = request["instruction"], request["episode_seed"], request["task"]
                self.text, self.text_valid = p.encode_text(self.instruction)
            if (request["instruction"], request["episode_seed"]) != (self.instruction, self.seed):
                raise ValueError("Episode identity changed without reset")
            for r in request["observations"]:
                self.raw[int(r["frame_id"])] = r
            if sorted(self.raw) != list(range(current + 1)):
                raise ValueError("Missing contiguous observations")
            s1_ids, sampling = None, None
            if p.s1 is not None:                         # frozen memory_s1, online rule of C+256
                sampling = resolve_online(p.dense_cfg, self.task, int(self.seed), current)
                ids = select_ids(range(current + 1), current, sampling["period"], phase=sampling["phase"],
                                 decision_stride=p.s1.decision_stride)
                if ids[-1] != current:
                    raise ValueError("memory_s1 selection must end at the current frame")
                s1_ids = ids[:-1]
            selection = select_history(range(current + 1), current, p.cfg.v2.history)
            encode_start = time.monotonic()
            self._encode(sorted(set(s1_ids or []) | set(selection.ids) | {current}))
            encode_seconds = time.monotonic() - encode_start
            batch = assemble(self.encoded, self.text, self.text_valid, current, selection, s1_ids)
            batch = {k: v.to(p.device) for k, v in batch.items()}
            conditions = p.model.conditions(batch)
            noise_seed = seed_for(p.dense_cfg["seed"], self.seed, current, "closed-loop-noise")
            noise = diagnostic_action_noise(noise_seed).to(torch.bfloat16).float().to(p.device)   # dense BF16 start
            g = p.cfg.v2.guidance
            steps = self.steps or g.steps
            guidance = GuidanceConfig(steps=steps, shift=g.shift, scale=self.scale, min_sigma=g.min_sigma)
            normalised, _ = p.model.sample(conditions, noise, guidance, memory_mode=self.mode)
            raw = p.normaliser.denormalize(normalised[0])
            dependence = {}
            if self.dependence:
                plain = GuidanceConfig(steps=steps, shift=g.shift, scale=1.0, min_sigma=g.min_sigma)
                for other in ("on", "null", "off"):
                    if other == self.mode and self.scale == 1.0:
                        continue
                    alt, _ = p.model.sample(conditions, noise, plain, memory_mode=other)
                    delta = (raw - p.normaliser.denormalize(alt[0]))[:EXECUTE][:, ARM_COLUMNS]
                    dependence[f"arm_rmse_vs_{other}"] = float(delta.square().mean().sqrt())
            actions = raw.clone()
            actions[:, [6, 13]] = actions[:, [6, 13]].clamp(0, 1)
            if not bool(torch.isfinite(actions).all()):
                raise ValueError("Non-finite action")
        seconds = time.monotonic() - start
        append(self.directory / "decisions.jsonl", {
            "frame_id": current, "mode": self.mode, "steps": steps, "guidance_scale": self.scale,
            "v2_frame_ids": list(selection.ids), "v2_roles": list(selection.roles), "s1_frame_ids": s1_ids,
            "s1_sampling": sampling, "noise_seed": noise_seed, "dependence": dependence,
            "normalized_actions": normalised[0].cpu().tolist(), "actions_after_gripper_clip": actions.cpu().tolist(),
            "encoded_frames": len(self.encoded), "encode_seconds": encode_seconds, "seconds": seconds})
        if self.decisions % 4 == 0:
            dep = " ".join(f"{k[12:]}={v:.4f}" for k, v in dependence.items())
            print(f"[decide] {now()} {self.tag} frame={current}/{self.limit} hist={len(selection.ids)} "
                  f"s1={len(s1_ids or [])} policy={seconds:.1f}s elapsed={time.monotonic() - self.started:.0f}s {dep}", flush=True)
        self.decisions += 1
        return actions.cpu().numpy()


# ============================================================================ simulator plumbing
def detected_arch() -> str:
    import torch
    major, minor = torch.cuda.get_device_capability(0)
    return f"{major}.{minor}"


def simulator_config(dense_cfg: dict, root: Path, out: Path, args) -> dict:
    cfg = copy.deepcopy(dense_cfg)
    cfg["root"] = str(root)
    cfg.setdefault("history", {})["archive_stride"] = 1
    loop = cfg.setdefault("closed_loop", {})
    if args.simulator_python:
        loop["simulator_python"] = args.simulator_python
    if args.curobo_backend:
        loop["curobo_backend"] = args.curobo_backend
        cfg.setdefault("selection_runtime", {})["backend"] = args.curobo_backend
    recorded = str(cfg.setdefault("recovery", {}).get("cuda_arch", "9.0"))
    arch = args.cuda_arch or detected_arch()
    cfg["recovery"]["cuda_arch"] = arch
    hardware = cfg.setdefault("hardware", {})
    hardware["warmup_lock_directory"] = str(Path(out) / "warmup_locks")
    if args.extensions_dir:
        hardware["extensions_directory"] = args.extensions_dir
    elif arch != recorded:
        # Never load kernels JIT-built for another architecture; the first fused episode builds them here.
        hardware["extensions_directory"] = f"outputs/fused_environment_memory_v2_sm{arch.replace('.', '')}/torch_extensions"
        if arch not in _WARNED:
            _WARNED.add(arch)
            print(f"[closed-loop] WARNING dense config was recorded for sm{recorded}; this GPU is sm{arch}: TORCH_EXTENSIONS_DIR -> "
                  f"{root / hardware['extensions_directory']} (give --extensions-dir to reuse built kernels)", flush=True)
    return cfg


_WARNED: set = set()


def gpu_uuid() -> str:
    from fastwam.memory_s1.eval_state import cuda_gpu_uuid
    return cuda_gpu_uuid(0)


def episode_metrics(rows: List[dict]) -> dict:
    """Object progress from the adapter's per-target snapshots: block lift / planar travel, task stage counters."""
    first, lift, travel, counters = {}, {}, {}, {}
    for row in rows:
        for key in ("objects_before", "objects_after"):
            for name, value in (row.get(key) or {}).items():
                if isinstance(value, dict) and "p" in value:
                    x, y, z = (float(v) for v in value["p"][:3])
                    if name not in first:
                        first[name] = (x, y, z)
                    x0, y0, z0 = first[name]
                    lift[name] = max(lift.get(name, 0.0), z - z0)
                    travel[name] = max(travel.get(name, 0.0), math.hypot(x - x0, y - y0))
                elif isinstance(value, (int, float)) and not isinstance(value, bool):
                    c = counters.setdefault(name, {"first": value, "last": value, "max": value})
                    c["last"], c["max"] = value, max(c["max"], value)
    blocks = [n for n in first if n.startswith("block")]
    top = max((lift[n] for n in blocks), default=None)
    return {"lift_m": lift, "travel_m": travel, "counters": counters, "max_block_lift_m": top,
            "max_block_travel_m": max((travel[n] for n in blocks), default=None),
            "lifted_5cm": None if top is None else bool(top >= 0.05)}


def run_episode(policy: Policy, scene: dict, mode: str, label: str, out: Path, args) -> dict:
    import numpy as np
    from multiprocessing.connection import Listener
    from fastwam.memory_s1.eval_parallel import simulator_environment
    from fastwam.memory_s1.grasp_bridge import owned_popen, stop_children
    task = scene["task"]
    limit = LIMITS[task]
    directory = out / label / mode / task / f"seed_{scene['seed']}"
    if (directory / "result.json").exists():
        return read(directory / "result.json")
    if directory.exists():
        directory.rename(directory.with_name(directory.name + f"_interrupted_{time.time_ns()}"))
    directory.mkdir(parents=True)
    root = Path(policy.spec.root)
    gpu = gpu_uuid()
    sim_cfg = simulator_config(policy.dense_cfg, root, out, args)
    write(directory / "job.json", {"id": f"{label}:{mode}:{task}:{scene['seed']}", "attempt": 1, "scene": scene,
                                   "condition": f"memory_v2_{mode}", "run_seed": policy.dense_cfg["seed"],
                                   "causal_case": {"task": task, "fork": 0, "capture": [], "cap": limit},
                                   "max_targets": int(args.max_targets), "record_frames": bool(args.record_frames),
                                   "policy": policy.describe(), "label": label})
    target_limit = min(limit, args.max_targets) if args.max_targets else limit
    session = Session(policy, directory, mode, args.steps, args.guidance, args.dependence,
                      tag=f"{label}/{mode} {task} seed={scene['seed']}", limit=target_limit)
    key = os.urandom(24)
    env = simulator_environment(sim_cfg, gpu)
    env.update(FW_CAUSAL_SIM_ROOT=str(root), MEMORY_S1_RPC_KEY=key.hex(), MEMORY_S1_ARCHIVE_STRIDE="1",
               MEMORY_S1_PROGRESS_ROOT=str(directory / "simulator_progress"))
    if args.vk_icd and not env.get("VK_ICD_FILENAMES"):
        env["VK_ICD_FILENAMES"] = args.vk_icd
    child, start, next_frame, last, reset, commands = None, time.monotonic(), 0, -1, False, []
    (out / "tmp").mkdir(parents=True, exist_ok=True)
    print(f"[closed-loop] {now()} start {label}/{mode} {task} seed={scene['seed']} target_limit={target_limit} -> {directory}",
          flush=True)
    try:
        with tempfile.TemporaryDirectory(prefix="v2-", dir=out / "tmp") as temp:
            socket = Path(temp) / "rpc.sock"
            cmd = [sim_cfg["closed_loop"]["simulator_python"], "-B", "-u", str(SIM_CODE / "sim_worker.py"), "--root", str(root),
                   "--output", str(directory), "--socket", str(socket), "--gpu-uuid", gpu, "--stop-root", str(out)]
            with Listener(str(socket), family="AF_UNIX", authkey=key) as listener, (directory / "simulator.log").open("w") as log:
                listener._listener._socket.settimeout(1)
                child = owned_popen(cmd, cwd=root / sim_cfg["closed_loop"]["simulator_root"], env=env,
                                    stdout=log, stderr=subprocess.STDOUT)
                while child.poll() is None:
                    if time.monotonic() - start > args.episode_timeout:
                        raise TimeoutError("Infrastructure timeout; not a model failure")
                    try:
                        c = listener.accept()
                    except TimeoutError:
                        continue
                    with c:
                        if not c.poll(60):
                            raise TimeoutError("RPC request timeout")
                        req = c.recv()
                        try:
                            if req["command"] == "reset":
                                if next_frame:
                                    raise ValueError("Mid-episode reset")
                                session.reset()
                                reset = True
                                c.send({"ok": True})
                                continue
                            frame = int(req["current_id"])
                            if not reset or frame != next_frame:
                                raise ValueError(f"Invalid decision sequence (frame {frame}, expected {next_frame})")
                            identity = (req["task"], int(req["episode_seed"]), req["instruction"])
                            if identity != (task, int(scene["seed"]), scene["instruction"]):
                                raise ValueError(f"Scene identity mismatch between job and simulator: {identity}")
                            if [int(r["frame_id"]) for r in req["observations"]] != list(range(last + 1, frame + 1)):
                                raise ValueError("Observation gap")
                            actions = session.decide(req)
                            n = execution_count(frame, limit)
                            commands.extend(actions[:n])
                            c.send({"ok": True, "actions": actions.tolist(), "execute": n})
                            last, next_frame = frame, next_frame + n
                        except Exception as error:
                            c.send({"ok": False, "error": str(error)})
                            raise
                if child.returncode:
                    raise RuntimeError((directory / "simulator.log").read_text(errors="replace")[-8000:])
        value = read(directory / "simulator_result.json")
        if value.get("status") != "complete":
            raise RuntimeError(f"Simulator episode {value.get('status')}: {str(value.get('error'))[-4000:]}")
        rows = [json.loads(s) for s in (directory / "executed_actions.jsonl").read_text().splitlines() if s.strip()]
        if len(rows) != value["executed_targets"]:
            raise ValueError("Executed target count differs")
        for i, r in enumerate(rows):
            if r["completed_target_id"] != i + 1 or not np.array_equal(np.asarray(r["target"], np.float32), commands[i]):
                raise ValueError("Command-to-execution mismatch")
        decisions = [json.loads(s) for s in (directory / "decisions.jsonl").read_text().splitlines() if s.strip()]
        dependence = {}
        for d in decisions:
            for k, v in (d.get("dependence") or {}).items():
                dependence.setdefault(k, []).append(v)
        result = {"label": label, "mode": mode, "task": task, "seed": scene["seed"], "ordinal": scene.get("ordinal"),
                  "checkpoint": policy.checkpoint, "success": bool(value["success"]), "max_reward": value.get("max_reward"),
                  "executed_targets": value["executed_targets"], "target_limit": value.get("target_limit"),
                  "termination": value.get("termination"), "truncated": value.get("truncated"),
                  "command_to_execution_exact": True, "decisions": len(decisions),
                  "policy_seconds_mean": sum(d["seconds"] for d in decisions) / max(1, len(decisions)),
                  "dependence_mean": {k: sum(v) / len(v) for k, v in dependence.items()},
                  "steps": args.steps or policy.cfg.v2.guidance.steps, "guidance_scale": args.guidance,
                  "simulator_backend": value.get("simulator_backend"), "simulator_seconds": value.get("simulator_seconds"),
                  "wall_seconds": time.monotonic() - start, **episode_metrics(rows)}
        write(directory / "result.json", result)
        dep = " ".join(f"{k}={v:.4f}" for k, v in result["dependence_mean"].items())
        print(f"[closed-loop] {now()} done  {label}/{mode} {task} seed={scene['seed']} success={result['success']} "
              f"targets={result['executed_targets']}/{result['target_limit']} reward={result['max_reward']} "
              f"lift={result['max_block_lift_m']} {dep} {result['wall_seconds']:.0f}s", flush=True)
        return result
    finally:
        if child:
            stop_children([child])


# ============================================================================ scenes
def load_scenes(specs: Sequence[str], root: Path, tasks: Sequence[str]) -> List[dict]:
    """'frozen' = Codex's two frozen online scenes (one per task); otherwise scene manifests (files or folders)."""
    rows = []
    for spec in specs:
        if spec == "frozen":
            ident = read(root / "outputs/s1_dense_joint_h100_v1/IDENTITY.json")
            frozen = Path(ident["frozen"])
            frozen = frozen if frozen.is_absolute() else root / frozen
            bundle = read(frozen / "FROZEN.json")
            rows += [read(frozen / bundle["experts"][t]["path"])["scene"] for t in tasks if t in bundle["experts"]]
            continue
        path = Path(spec)
        for f in (sorted(path.glob("*.json")) if path.is_dir() else [path]):
            value = read(f)
            scenes = value.get("scenes") if isinstance(value, dict) else value
            if isinstance(scenes, list):
                rows += scenes
    seen, out = set(), []
    for s in rows:
        key = (s["task"], int(s["seed"]))
        if s["task"] in tasks and key not in seen:
            seen.add(key)
            out.append({k: s[k] for k in ("task", "seed", "ordinal", "instruction", "episode_info") if k in s})
    return sorted(out, key=lambda s: (list(tasks).index(s["task"]), s.get("ordinal", 0), s["seed"]))


def select_scenes(scenes: List[dict], limit: int, shard: str, seeds: Sequence[str] = ()) -> List[dict]:
    """--seeds keeps only the listed scenes: 'task:seed' or a bare seed (any task)."""
    if seeds:
        want = {(x.split(":")[0], int(x.split(":")[1])) if ":" in x else (None, int(x)) for x in seeds}
        scenes = [s for s in scenes if (s["task"], int(s["seed"])) in want or (None, int(s["seed"])) in want]
    if limit:
        count, kept = {}, []
        for s in scenes:
            count[s["task"]] = count.get(s["task"], 0) + 1
            if count[s["task"]] <= limit:
                kept.append(s)
        scenes = kept
    k, n = (int(x) for x in shard.split("/"))
    if not 0 <= k < n:
        raise ValueError("--shard k/n needs 0 <= k < n")
    return scenes[k::n]


def dense_config_light(spec) -> dict:
    """IDENTITY config without authenticating the dense cache (planning needs no model)."""
    return read(Path(spec.output) / "IDENTITY.json")["config"]


def cmd_plan(args):
    """Expert-feasible scenes via the production planner (sim_eval --operation plan) in the simulator env."""
    from fastwam.memory_s1.eval_parallel import simulator_environment
    from fastwam.memory_s1.simulator_backend import configured_backend
    from . import dense
    cfg, _ = policy_config(args.config, None, args.set)
    spec = dense.DenseSpec.from_dict(cfg.dense)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    sim_cfg = simulator_config(dense_config_light(spec), Path(spec.root), out, args)
    gpu = gpu_uuid()
    env = simulator_environment(sim_cfg, gpu)
    if args.vk_icd and not env.get("VK_ICD_FILENAMES"):
        env["VK_ICD_FILENAMES"] = args.vk_icd
    for task in args.tasks:
        manifest = out / f"{task}.json"
        contract = out / f"{task}.contract.json"
        if not contract.exists():
            write(contract, {"simulator_backend": configured_backend(sim_cfg), "task": task, "seed": args.seed,
                             "episodes": args.episodes, "task_config": "demo_clean", "instruction_type": "seen",
                             "candidate_rule": "first K expert-feasible increasing seeds (sim_eval plan)",
                             "purpose": "memory_v2 closed loop"})
        env["MEMORY_S1_PROGRESS_ROOT"] = str(out / f"{task}.progress")
        cmd = [sim_cfg["closed_loop"]["simulator_python"], "-B", "-u", str(Path(spec.root) / "scripts/memory_s1/sim_eval.py"),
               "--operation", "plan", "--task", task, "--episodes", str(args.episodes), "--seed", str(args.seed),
               "--output", str(manifest), "--contract", str(contract), "--gpu-uuid", gpu, "--stop-root", str(out)]
        print(f"[plan] {now()} {task}: {args.episodes} expert-feasible scenes, seed {args.seed} -> {manifest}", flush=True)
        subprocess.run(cmd, cwd=Path(spec.root) / sim_cfg["closed_loop"]["simulator_root"], env=env, check=True)
        value = read(manifest)
        print(f"[plan] {now()} {task}: complete={value.get('complete')} scenes={len(value.get('scenes', []))}", flush=True)


def cmd_run(args):
    import torch
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    cfg, state = policy_config(args.config, args.checkpoint, args.set)
    policy = Policy(cfg, state, args.checkpoint, "cuda:0", encoders=True,
                    t5_on_gpu={"auto": None, "gpu": True, "cpu": False}[args.t5])
    del state
    label = args.label or run_label(args.checkpoint)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    scenes = select_scenes(load_scenes(args.scenes, Path(policy.spec.root), args.tasks), args.limit, args.shard,
                           args.seeds)
    labels = {m: (policy.base_label(label) if m == "off" else label) for m in args.modes}
    tag = f"{label}_{'-'.join(args.modes)}_{args.shard.replace('/', 'of')}"
    write(out / "runs" / f"{tag}.json", {"policy": policy.describe(), "labels": labels, "scenes": scenes,
                                         "args": {k: (str(v) if isinstance(v, Path) else v) for k, v in vars(args).items()},
                                         "started": now()})
    print(f"[closed-loop] {now()} {len(scenes)} scenes x modes {args.modes} -> labels {labels}; checkpoint {args.checkpoint}; "
          f"T5 on {'GPU' if policy.t5_on_gpu else 'CPU'}; max_targets={args.max_targets or 'official'}", flush=True)
    for scene in scenes:
        for mode in args.modes:
            if (out / "STOP.json").exists():
                print(f"[closed-loop] {now()} STOP.json found; stopping before the next episode", flush=True)
                return
            try:
                run_episode(policy, scene, mode, labels[mode], out, args)
            except Exception as error:                        # one broken episode must not stop the bank
                d = out / labels[mode] / mode / scene["task"] / f"seed_{scene['seed']}"
                write(d / "ERROR.json", {"error": repr(error)[-8000:], "time": now()})
                print(f"[closed-loop] {now()} ERROR {labels[mode]}/{mode} {scene['task']} seed={scene['seed']}: "
                      f"{repr(error)[-2000:]}", flush=True)
                if args.stop_on_error:
                    raise
    cmd_summary(args)


def wilson(k, n, z=1.96):
    if not n:
        return None
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    r = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return [max(0.0, (c - r) / d), min(1.0, (c + r) / d)]


def mcnemar_exact(only_a: int, only_b: int) -> float:
    m = only_a + only_b
    if not m:
        return 1.0
    return min(1.0, 2 * sum(math.comb(m, j) for j in range(min(only_a, only_b) + 1)) / 2 ** m)


def collect(out: Path) -> List[dict]:
    return [read(p) for p in sorted(out.glob("*/*/*/seed_*/result.json")) if SEED_DIR.fullmatch(p.parent.name)]


def cmd_summary(args):
    out = Path(args.output)
    rows = collect(out)
    groups = {}
    for r in rows:
        groups.setdefault((r["label"], r["mode"], r["task"]), []).append(r)
    summary = {}

    def mean(xs):
        return sum(xs) / len(xs) if xs else None

    def f(x, w=9, p=2):
        return f"{x:>{w}.{p}f}" if x is not None else f"{'-':>{w}}"

    print(f"\n{'label/mode':<24}{'task':<16}{'n':>4}{'success':>9}{'  95% CI':<15}{'lift5cm':>8}{'reward':>8}"
          f"{'targets':>9}{'dep_null':>9}{'dep_off':>9}{'dep_on':>9}{'pol_s':>7}")
    for (label, mode, task), rs in sorted(groups.items()):
        n = len(rs)
        k = sum(r["success"] for r in rs)
        dep = lambda key: [r["dependence_mean"][key] for r in rs if key in (r.get("dependence_mean") or {})]
        item = {"n": n, "success": k / n, "wilson95": wilson(k, n),
                "lifted_5cm": mean([r["lifted_5cm"] for r in rs if r.get("lifted_5cm") is not None]),
                "max_reward_mean": mean([r["max_reward"] for r in rs if r.get("max_reward") is not None]),
                "executed_targets_mean": mean([r["executed_targets"] for r in rs]),
                "dependence_vs_null": mean(dep("arm_rmse_vs_null")), "dependence_vs_off": mean(dep("arm_rmse_vs_off")),
                "dependence_vs_on": mean(dep("arm_rmse_vs_on")),
                "policy_seconds_mean": mean([r.get("policy_seconds_mean", 0) for r in rs]),
                "truncated": sum(bool(r.get("truncated")) for r in rs)}
        summary[f"{label}/{mode}/{task}"] = item
        ci = item["wilson95"]
        print(f"{label + '/' + mode:<24}{task:<16}{n:>4}{item['success']:>9.2f}  [{ci[0]:.2f},{ci[1]:.2f}]  "
              f"{f(item['lifted_5cm'], 8)}{f(item['max_reward_mean'], 8)}{f(item['executed_targets_mean'], 9, 0)}"
              f"{f(item['dependence_vs_null'], 9, 4)}{f(item['dependence_vs_off'], 9, 4)}{f(item['dependence_vs_on'], 9, 4)}"
              f"{f(item['policy_seconds_mean'], 7, 1)}"
              + (f"   ({item['truncated']} truncated by --max-targets)" if item["truncated"] else ""))
    by_scene = {}
    for r in rows:
        by_scene.setdefault((r["task"], r["seed"]), {})[f"{r['label']}/{r['mode']}"] = r["success"]
    conditions = sorted({f"{r['label']}/{r['mode']}" for r in rows})
    paired = {}
    if len(conditions) > 1:
        print(f"\npaired on common scenes (A vs B):{'':<22}{'n':>4}{'both':>6}{'only A':>8}{'only B':>8}{'neither':>9}  McNemar p")
    for i, a in enumerate(conditions):
        for b in conditions[i + 1:]:
            common = [v for v in by_scene.values() if a in v and b in v]
            if not common:
                continue
            both = sum(v[a] and v[b] for v in common)
            only_a = sum(v[a] and not v[b] for v in common)
            only_b = sum(v[b] and not v[a] for v in common)
            neither = len(common) - both - only_a - only_b
            p = mcnemar_exact(only_a, only_b)
            paired[f"{a} vs {b}"] = {"n": len(common), "both": both, "only_a": only_a, "only_b": only_b,
                                     "neither": neither, "mcnemar_p": p}
            print(f"  {a:<24} vs {b:<24}{len(common):>4}{both:>6}{only_a:>8}{only_b:>8}{neither:>9}  {p:.3f}")
    errors = [str(e) for e in sorted(out.glob("*/*/*/seed_*/ERROR.json")) if SEED_DIR.fullmatch(e.parent.name)
              and not (e.parent / "result.json").exists()]
    write(out / "SUMMARY.json", {"summary": summary, "paired": paired, "episodes": len(rows), "errors": errors, "time": now()})
    print(f"\n[summary] {len(rows)} episodes, {len(errors)} open errors -> {out / 'SUMMARY.json'}")
    for e in errors[:10]:
        print(f"   ERROR {e}: {read(e)['error'][-300:]}")


# ============================================================================ parity (online path vs offline cache)
def cmd_parity(args):
    """On dense val windows: (1) features computed online from the cached latents vs the FeatureStore features,
    (2) the online batch (assemble) vs dense.make_batch, (3) sampled actions from both batches, same noise."""
    import torch
    from . import dense
    from .config import GuidanceConfig
    from .history import select_history
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    cfg, state = policy_config(args.config, args.checkpoint, args.set)
    policy = Policy(cfg, state, args.checkpoint, "cuda:0", encoders=False)
    del state
    device = policy.device
    episodes = dense.EpisodeStore(policy.spec)
    features = dense.FeatureStore(Path(cfg.features))
    features.require(policy.info["video_digest"], policy.info["dense_identity"])
    picked, per = [], {}
    for r in sorted((r for r in dense.windows(policy.spec) if r["split"] == "val"), key=lambda r: (-int(r["anchor"]), r["id"])):
        if per.get(r["task"], 0) < max(1, args.windows // 2):        # latest anchors: the longest histories
            per[r["task"]] = per.get(r["task"], 0) + 1
            picked.append(r)
    g = cfg.v2.guidance
    guidance = GuidanceConfig(steps=g.steps, shift=g.shift, scale=1.0, min_sigma=g.min_sigma)
    report, worst = [], {"feature_rel": 0.0, "batch_abs": 0.0, "action_arm_rmse": 0.0}
    exact_keys = ("frame_ids", "roles", "history_valid", "current_ids", "s1_frame_ids", "s1_valid", "text_valid")
    with torch.no_grad():
        for row in picked:
            a = int(row["anchor"])
            offline = dense.make_batch([row], episodes, features, cfg.v2.history, device, s1=policy.s1, spec=policy.spec)
            e, f = episodes(row["episode_id"]), features(row["episode_id"])
            selection = select_history(range(a + 1), a, cfg.v2.history)
            s1_ids = None
            if policy.s1 is not None:
                s1_ids = policy.s1.ids(a, dense.s1_phase(policy.spec, row, policy.s1.period))[:-1]
            text = e["text"][None].to(device)
            encoded, rel = {}, []
            for i in sorted(set(s1_ids or []) | set(selection.ids) | {a}):
                latent, proprio = e["latent"][i], e["proprio"][i]
                feature = policy.ab.encode(latent[None].to(device), text, proprio[None].to(device), keep_kv=False)[0][0]
                cached = f[i].to(device).float()
                rel.append(float((feature.float() - cached).norm() / cached.norm().clamp_min(1e-12)))
                encoded[i] = (latent, proprio, feature.to(torch.bfloat16).cpu())
            online = assemble(encoded, e["text"][None], e["text_valid"][None], a, selection, s1_ids)
            online = {k: v.to(device) for k, v in online.items()}
            mismatched = [k for k in exact_keys if k in offline and not torch.equal(online[k].cpu(), offline[k].cpu())]
            mismatched += [k for k in offline if k not in online] + [k for k in online if k not in offline]
            float_keys = ("latent", "text", "proprio", "history") + (("s1_history",) if s1_ids is not None else ())
            float_diff = max(float((online[k].float() - offline[k].float()).abs().max()) for k in float_keys)
            noise = dense.window_noise(row, (HORIZON, 14), device)[None]
            case = {"episode_id": row["episode_id"], "task": row["task"], "anchor": a, "history": len(selection.ids),
                    "s1_history": None if s1_ids is None else len(s1_ids), "feature_rel_max": max(rel),
                    "exact_key_mismatch": mismatched, "batch_float_absmax": float_diff}
            c_off, c_on = policy.model.conditions(offline), policy.model.conditions(online)
            for mode in args.modes:
                s_off, _ = policy.model.sample(c_off, noise, guidance, memory_mode=mode)
                s_on, _ = policy.model.sample(c_on, noise, guidance, memory_mode=mode)
                m_off = dense.window_metrics(s_off[0], offline["actions"][0], offline["action_valid"][0], policy.normaliser)
                m_on = dense.window_metrics(s_on[0], offline["actions"][0], offline["action_valid"][0], policy.normaliser)
                delta = (policy.normaliser.denormalize(s_on[0]) - policy.normaliser.denormalize(s_off[0]))[:, dense.ARM_COLUMNS]
                case[mode] = {"arm_rmse_offline_path": m_off["arm_rmse_rad"], "arm_rmse_online_path": m_on["arm_rmse_rad"],
                              "online_vs_offline_arm_rmse": float(delta.square().mean().sqrt())}
                worst["action_arm_rmse"] = max(worst["action_arm_rmse"], case[mode]["online_vs_offline_arm_rmse"])
            worst["feature_rel"] = max(worst["feature_rel"], case["feature_rel_max"])
            worst["batch_abs"] = max(worst["batch_abs"], float_diff)
            report.append(case)
            modes = "  ".join(f"{m}: offline {case[m]['arm_rmse_offline_path']:.4f} online {case[m]['arm_rmse_online_path']:.4f} "
                              f"diff {case[m]['online_vs_offline_arm_rmse']:.5f}" for m in args.modes)
            print(f"[parity] {row['task']:<15} anchor={a:<4} hist={len(selection.ids):<3} s1={case['s1_history']}  "
                  f"feat_rel={case['feature_rel_max']:.2e} batch_abs={float_diff:.2e} "
                  f"exact_mismatch={mismatched or 'none'}  {modes}", flush=True)
    passed = (all(not c["exact_key_mismatch"] for c in report) and worst["feature_rel"] < args.feature_tol
              and worst["action_arm_rmse"] < args.action_tol)
    out = Path(args.output)
    path = out / f"parity_{args.label or run_label(args.checkpoint)}.json"
    write(path, {"passed": passed, "worst": worst, "tolerances": {"feature_rel": args.feature_tol, "action_arm_rmse_rad": args.action_tol},
                 "checkpoint": args.checkpoint, "policy": policy.describe(), "cases": report, "time": now()})
    print(f"[parity] {'PASS' if passed else 'CHECK'}  worst feature rel diff {worst['feature_rel']:.2e} (tol {args.feature_tol:g}); "
          f"worst online-vs-offline action arm RMSE {worst['action_arm_rmse']:.5f} rad (tol {args.action_tol:g}); "
          f"batch float absmax {worst['batch_abs']:.2e} -> {path}", flush=True)


# ============================================================================ preflight (read-only inventory)
SIM_PROBE = r"""
import json, sys
r = {"python": sys.version.split()[0]}
try:
    import torch
    r["torch"] = torch.__version__; r["cuda"] = torch.version.cuda; r["cuda_available"] = torch.cuda.is_available()
    if torch.cuda.is_available():
        r["device"] = torch.cuda.get_device_name(0); r["capability"] = ".".join(map(str, torch.cuda.get_device_capability(0)))
except Exception as e: r["torch_error"] = repr(e)[:200]
for name in ("sapien", "mplib", "curobo", "pytorch3d", "numpy"):
    try:
        m = __import__(name); r[name] = getattr(m, "__version__", "ok")
    except Exception as e: r[name] = "ERROR " + repr(e)[:160]
for name in ("curobo.curobolib.lbfgs_step_cu", "curobo.curobolib.kinematics_fused_cu", "curobo.curobolib.geom_cu", "pytorch3d._C"):
    try:
        __import__(name); r[name] = "ok"
    except Exception as e: r[name] = "ERROR " + repr(e)[:160]
print("PROBE " + json.dumps(r))
"""


def cmd_preflight(args):
    root = Path(args.root)
    memory2 = REPO
    print(f"== preflight {now()}  root={root}  memory2={memory2}")

    def exists(path):
        return "OK     " if Path(path).exists() else "MISSING"

    print("\n-- 1. GPUs (index, uuid, name, used, total, util) and compute processes")
    for query in (["--query-gpu=index,uuid,name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader"],
                  ["--query-compute-apps=gpu_uuid,pid,used_memory", "--format=csv,noheader"]):
        try:
            print(subprocess.run(["nvidia-smi"] + query, capture_output=True, text=True, timeout=30).stdout.rstrip() or "  (none)")
        except Exception as error:
            print(f"  nvidia-smi failed: {error!r}")

    print("\n-- 2. dense delivery (Codex) and its config")
    code = Path(args.dense_code)
    for name in ("common.py", "data_path.py", "model_path.py", "recipe.json", "physical.py", "sim_worker.py", "sim_adapter.py"):
        print(f"  {exists(code / name)} {code / name}")
    ident_path = root / "outputs/s1_dense_joint_h100_v1/IDENTITY.json"
    print(f"  {exists(ident_path)} {ident_path}")
    sim_python = None
    if ident_path.exists():
        ident = read(ident_path)
        cfg = ident["config"]
        for section in ("closed_loop", "selection_runtime", "hardware", "recovery", "history"):
            value = cfg.get(section)
            if section == "history" and value:
                value = {k: v for k, v in value.items() if k.startswith("online") or k in ("archive_stride", "phase")}
            print(f"  config.{section}: {json.dumps(value)[:700]}")
        print(f"  config.seed: {cfg.get('seed')}")
        for k, v in (cfg.get("paths") or {}).items():
            p = Path(v) if Path(v).is_absolute() else root / v
            print(f"  paths.{k:<12} {exists(p)} {p}")
        sim_python = (cfg.get("closed_loop") or {}).get("simulator_python")
        frozen = Path(ident.get("frozen", ""))
        frozen = frozen if frozen.is_absolute() else root / frozen
        print(f"  frozen bundle: {exists(frozen / 'FROZEN.json')} {frozen / 'FROZEN.json'}")
        if (frozen / "FROZEN.json").exists():
            for task, item in read(frozen / "FROZEN.json").get("experts", {}).items():
                try:
                    s = read(frozen / item["path"])["scene"]
                    print(f"     {task}: seed={s.get('seed')} ordinal={s.get('ordinal')} instruction={s.get('instruction')!r}")
                except Exception as error:
                    print(f"     {task}: unreadable ({error!r})")

    print("\n-- 3. simulator-side sources")
    for rel in ("scripts/memory_s1/sim_eval.py", "scripts/memory_s1/deploy_policy.py", "scripts/memory_s1/sim_feedback.py",
                "scripts/memory_s1/sim_instrumentation.py", "src/fastwam/memory_s1/eval_state.py",
                "src/fastwam/memory_s1/selection_runtime.py", "src/fastwam/memory_s1/simulator_backend.py",
                "src/fastwam/memory_s1/fused_evaluation.py", "resources/RMBench/scripts/eval_policy.py",
                "resources/RMBench/envs/curobo"):
        print(f"  {exists(root / rel)} {root / rel}")
    for name in ("sim_worker.py", "sim_adapter.py"):
        print(f"  {exists(SIM_CODE / name)} {SIM_CODE / name}")

    print("\n-- 4. simulator Python environments (import probe, first visible GPU)")
    candidates = [p for p in dict.fromkeys([sim_python, "/opt/rmbench-fused-env/bin/python", "/opt/rmbench-a100-env/bin/python",
                                             "/opt/rmbench-env/bin/python"]) if p]
    for py in candidates:
        if not Path(py).exists():
            print(f"  MISSING {py}")
            continue
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "PYTHONHOME", "VIRTUAL_ENV", "CONDA_PREFIX")}
        prefix = Path(py).parent.parent
        env["LD_LIBRARY_PATH"] = os.pathsep.join([str(prefix / "lib"), str(prefix / "targets/x86_64-linux/lib"),
                                                  "/usr/local/nvidia/lib", "/usr/local/nvidia/lib64"])
        try:
            r = subprocess.run([py, "-c", SIM_PROBE], capture_output=True, text=True, timeout=300, env=env,
                               cwd=str(root / "resources/RMBench") if (root / "resources/RMBench").exists() else None)
            line = next((l for l in r.stdout.splitlines() if l.startswith("PROBE ")), None)
            print(f"  FOUND   {py}\n          {line[6:] if line else (r.stderr[-800:] or r.stdout[-800:])}")
        except Exception as error:
            print(f"  FAILED  {py}: {error!r}")

    print("\n-- 5. CuRobo torch-extension directories (fused_graph_v1 JIT kernels)")
    found = []
    for base in (root / "outputs", root):
        if base.exists():
            for d in sorted(base.glob("*/torch_extensions*")) + sorted(base.glob("*/*/torch_extensions*")):
                if d.is_dir() and d not in found:
                    found.append(d)
                    print(f"  {d}  [{', '.join(sorted(x.name for x in d.iterdir())[:8])}]")
    if not found:
        print("  (none found under outputs/)")

    print("\n-- 6. existing expert-feasible scene banks")
    banks = 0
    if (root / "outputs").exists():
        paths = sorted((root / "outputs").glob("**/scene_manifests/*/*.json")) + \
            sorted((root / "outputs").glob("**/borrowed_scenes/manifest.json"))
        for path in paths:
            if path.name == "contract.json" or path.name.endswith(".error.json"):
                continue
            try:
                value = read(path)
            except Exception:
                continue
            scenes = value.get("scenes") or []
            contract = value.get("contract") or {}
            backend = (contract.get("simulator_backend") or {}).get("name")
            print(f"  {path}\n      tasks={sorted({str(s.get('task')) for s in scenes})} n={len(scenes)} complete={value.get('complete')} "
                  f"contract_seed={contract.get('seed')} count={contract.get('count')} backend={backend} "
                  f"seeds={[s.get('seed') for s in scenes][:4]}")
            banks += 1
    if not banks:
        print("  (none)")

    print("\n-- 7. memory_v2 checkpoints (update_001340)")
    for ck in sorted((memory2 / "outputs/memory_v2").glob("v2_*/checkpoints/update_001340.pt")):
        print(f"  {ck}  {ck.stat().st_size / 2 ** 20:.0f} MiB")

    print("\n-- 8. rendering / policy env")
    for p in ("/etc/vulkan/icd.d/nvidia_icd.json", "/usr/share/vulkan/icd.d/nvidia_icd.json"):
        print(f"  {exists(p)} {p}")
    print(f"  VK_ICD_FILENAMES={os.environ.get('VK_ICD_FILENAMES')}")
    for name in ("torch", "pynvml", "yaml", "numpy", "torchvision", "pytest"):
        try:
            m = __import__(name)
            print(f"  policy {name}: {getattr(m, '__version__', 'ok')}")
        except Exception as error:
            print(f"  policy {name}: ERROR {error!r}")
    try:
        import shutil
        print(f"  disk free under {memory2}: {shutil.disk_usage(memory2).free / 2 ** 30:.0f} GiB")
        print(f"  host RAM free: {int(open('/proc/meminfo').read().split('MemAvailable:')[1].split()[0]) / 2 ** 20:.0f} GiB")
    except Exception:
        pass
    print(f"\n== preflight done {now()}")


# ============================================================================ CLI
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("preflight", "parity", "plan", "run", "summary"))
    ap.add_argument("--config", type=Path, default=Path("configs/memory_v2/train_v2_A.yaml"), help="only for --checkpoint init")
    ap.add_argument("--set", action="append", default=[], help="config override on top of the checkpoint's config")
    ap.add_argument("--checkpoint", default="init", help="memory_v2 checkpoint (.pt) or 'init'")
    ap.add_argument("--label", default="", help="result label (default: the run folder of the checkpoint)")
    ap.add_argument("--modes", nargs="+", default=None, choices=("on", "null", "off"))
    ap.add_argument("--scenes", nargs="+", default=["frozen"], help="'frozen' (Codex's 2 scenes) and/or scene manifests/folders")
    ap.add_argument("--tasks", nargs="+", default=list(LIMITS), choices=list(LIMITS))
    ap.add_argument("--limit", type=int, default=0, help="first N scenes per task")
    ap.add_argument("--seeds", nargs="*", default=[], help="only these scenes: task:seed or seed")
    ap.add_argument("--shard", default="0/1", help="k/n: this process takes scenes[k::n]")
    ap.add_argument("--output", default="outputs/memory_v2/closed_loop")
    ap.add_argument("--steps", type=int, default=0, help="Euler steps (0 = the checkpoint's, 10)")
    ap.add_argument("--guidance", type=float, default=1.0, help="memory guidance scale (1 = none)")
    ap.add_argument("--dependence", action="store_true", help="also sample the other modes: log the action change")
    ap.add_argument("--max-targets", type=int, default=0, help="smoke runs: stop after N executed targets (0 = official)")
    ap.add_argument("--record-frames", action="store_true", help="save camera PNGs of every frame")
    ap.add_argument("--episode-timeout", type=float, default=5400)
    ap.add_argument("--stop-on-error", action="store_true")
    ap.add_argument("--t5", default="auto", choices=("auto", "gpu", "cpu"), help="text encoder placement (auto: CPU on <60 GB cards)")
    ap.add_argument("--simulator-python", default="", help="override closed_loop.simulator_python of the dense config")
    ap.add_argument("--curobo-backend", default="", help="override the CuRobo backend (upstream|builtin_torch_v1|fused_graph_v1)")
    ap.add_argument("--cuda-arch", default="", help="simulator JIT arch (default: detected, 8.0 on A100)")
    ap.add_argument("--extensions-dir", default="", help="TORCH_EXTENSIONS_DIR (relative to the FastWAM root) for fused_graph_v1")
    ap.add_argument("--vk-icd", default="/etc/vulkan/icd.d/nvidia_icd.json" if Path("/etc/vulkan/icd.d/nvidia_icd.json").exists() else "")
    ap.add_argument("--seed", type=int, default=17, help="plan: scene seed (17 internal, 42 official)")
    ap.add_argument("--episodes", type=int, default=10, help="plan: scenes per task")
    ap.add_argument("--windows", type=int, default=8, help="parity: val windows (half per task)")
    ap.add_argument("--feature-tol", type=float, default=2e-2, help="parity: max relative feature difference")
    ap.add_argument("--action-tol", type=float, default=5e-3, help="parity: max online-vs-offline arm RMSE (rad)")
    ap.add_argument("--root", default="/workspace/FastWAM", help="preflight: FastWAM root")
    ap.add_argument("--dense-code", default="/restore-tmp/dense_joint_v1", help="preflight: Codex delivery")
    args = ap.parse_args(argv)
    if args.modes is None:
        args.modes = ["on", "off"] if args.command == "parity" else ["on"]
    {"preflight": cmd_preflight, "parity": cmd_parity, "plan": cmd_plan, "run": cmd_run, "summary": cmd_summary}[args.command](args)


if __name__ == "__main__":
    main()
