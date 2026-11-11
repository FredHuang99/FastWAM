"""Closed loop for fullft exports (plan v10 item 7): the memory_v2 online plumbing (simulator, RPC, scene banks,
stress, verdict files) with a FullModel policy instead of the frozen C+256 stack.

FullPolicy   loads a bf16 export (train.py export_*.pt) into FullModel + the observation encoders of the dense
             delivery (the same VAE / T5 / mosaic / released normaliser that built the training caches)
FullSession  per episode: raw observations -> per-frame latent + normalised proprio (once per frame) -> per-frame
             history K / V (once per frame: a frame's K / V depend only on its latent, proprio and the text) ->
             at each decision: history.select (the training rule) -> re-rotated K / V -> current frame prefilled
             with history -> 10-step Euler chunk from the dense-BF16 noise of (dense seed, episode seed, frame)
`decide_encoded` is the pure part (no simulator, no encoders): tests compare it with FullModel.sample on the same
inputs, which is how training draws its samples.
"""
from __future__ import annotations

import copy
import time
from pathlib import Path
from typing import Dict, List, Optional

import torch

from .history import HistoryRule, select
from .model import FullModel, History, rerotate

ARM_COLUMNS = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]


def is_fullft_export(path: Optional[str]) -> bool:
    if not path or path == "init" or not Path(path).is_file():
        return False
    state = torch.load(path, map_location="cpu", weights_only=False, mmap=True)
    return isinstance(state, dict) and "weights" in state and "variant" in state


def load_export(path: str, device="cuda:0") -> tuple:
    from .config import _build, RunConfig
    torch.backends.cuda.enable_cudnn_sdp(False)                 # as in training (train.safe_attention_backends)
    state = torch.load(path, map_location="cpu", weights_only=False, mmap=True)
    cfg = _build(RunConfig, state["config"])
    rule = cfg.rule
    model = FullModel.from_release(cfg.model.architecture, cfg.model.base, rule.variant, rule.event_slots,
                                   cfg.model.video_shift, cfg.model.action_shift)
    model.set_trainable(cfg.model.train_video, cfg.model.lora_rank)
    model.load_state_dict(state["weights"], strict=True)
    model.requires_grad_(False)
    model.to(device=device, dtype=torch.bfloat16).eval()
    model.compute_dtype = None
    return model, cfg, state


class FrameCache:
    """Per-episode history K / V per frame id (before re-rotation), kept on the model's device."""

    def __init__(self):
        self.kv: Dict[int, tuple] = {}

    def ensure(self, model: FullModel, ids: List[int], encoded: Dict[int, tuple], text: torch.Tensor):
        missing = [i for i in ids if i not in self.kv]
        if missing:
            latent = torch.stack([encoded[i][0] for i in missing]).to(text.device)
            proprio = torch.stack([encoded[i][1] for i in missing]).to(text.device)
            keys, values = model.prefill_frames(latent, text.expand(len(missing), -1, -1), proprio)
            for n, i in enumerate(missing):
                self.kv[i] = ([k[n] for k in keys], [v[n] for v in values])

    def history(self, model: FullModel, ids: List[int], positions: List[float]) -> Optional[History]:
        if not ids:
            return None
        layers = model.num_layers
        keys, values = [], []
        pos = torch.tensor([positions], dtype=torch.float32)
        for l in range(layers):
            k = torch.stack([self.kv[i][0][l] for i in ids])[None]           # [1, K, T, W]
            v = torch.stack([self.kv[i][1][l] for i in ids])[None]
            k = rerotate(k, pos.to(k.device), model.num_heads)
            keys.append(k.reshape(1, -1, k.shape[-1]))
            values.append(v.reshape(1, -1, v.shape[-1]))
        valid = torch.ones(1, keys[0].shape[1], dtype=torch.bool, device=keys[0].device)
        return History(keys, values, valid)

    def evict(self, keep: set):
        for i in [i for i in self.kv if i not in keep]:
            del self.kv[i]


def keep_set(rule: HistoryRule, current: int, events: List[int]) -> set:
    """Frames a later decision may still select (everything else can leave the cache)."""
    keep = {0}
    horizon = max(rule.recent) if rule.recent else 0
    keep |= {i for i in range(max(0, current - horizon), current + 1)}
    if rule.variant == "tw":
        keep |= set(range(rule.tw_stride, current + 1, rule.tw_stride))
    if rule.variant in ("event", "prop"):
        keep |= set(int(e) for e in events)
    return keep


@torch.no_grad()
def decide_encoded(model: FullModel, rule: HistoryRule, cache: FrameCache, encoded: Dict[int, tuple], current: int,
                   text: torch.Tensor, noise: torch.Tensor, steps: int = 10, events: List[int] = ()) -> dict:
    """One decision from per-frame encodings: encoded[i] = (latent [48, 1, 24, 20], normalised proprio [14])."""
    ids, positions = select(rule, current, events)
    cache.ensure(model, ids, encoded, text)
    history = cache.history(model, ids, positions)
    device = text.device
    batch = {"latent": encoded[current][0][None].to(device), "text": text,
             "proprio": encoded[current][1][None].to(device), "anchor": torch.tensor([current], device=device)}
    if rule.variant == "prop":
        frames = [int(e) for e in events if 0 < int(e) < current][-rule.event_max:]
        states = torch.zeros(1, rule.event_max, 14, device=device)
        valid = torch.zeros(1, rule.event_max, dtype=torch.bool, device=device)
        for j, f in enumerate(frames):
            states[0, j], valid[0, j] = encoded[f][1].to(device), True
        batch.update(event_proprio=states, event_valid=valid)
    actions = model.sample(batch, noise.to(device), steps, history)
    cache.evict(keep_set(rule, current, events))
    return {"normalised": actions[0], "ids": ids, "positions": positions}


class FullPolicy:
    """Duck-typed stand-in for memory_v2.online.Policy (what run_episode / cmd_run use)."""

    session_cls = None                                                     # set below

    def __init__(self, checkpoint: str, device="cuda:0", t5_on_gpu: Optional[bool] = None):
        from fastwam.memory_v2 import dense
        from fastwam.memory_s1.common import ReleaseNormalizer
        self.torch, self.device, self.checkpoint = torch, torch.device(device), checkpoint
        self.model, self.run_cfg, state = load_export(checkpoint, device)
        self.rule = self.run_cfg.rule
        self.export_state = dict(state.get("state", {}))
        del state
        self.spec = dense.DenseSpec()
        self.info = {}
        self.dense_cfg = copy.deepcopy(dense.dense_config(self.spec))
        self.normaliser = ReleaseNormalizer(self.run_cfg.model.stats)
        from fastwam.models.wan22.helpers.loader import _load_registered_model
        from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
        self.vae = _load_registered_model(self.path("vae"), "wan_video_vae", torch.bfloat16, str(self.device))
        self.vae.eval().requires_grad_(False)
        if t5_on_gpu is None:
            t5_on_gpu = torch.cuda.get_device_properties(self.device).total_memory > 60 * 2 ** 30
        self.t5_on_gpu = bool(t5_on_gpu)
        self.t5_cpu_encode = not self.t5_on_gpu
        self.t5 = _load_registered_model(self.path("t5"), "wan_video_text_encoder", torch.bfloat16,
                                         str(self.device) if self.t5_on_gpu else "cpu")
        self.t5.eval().requires_grad_(False)
        self.tokenizer = HuggingfaceTokenizer(self.path("tokenizer"), seq_len=128, clean="whitespace",
                                              local_files_only=True)
        dense.bind(self.spec)
        from data_path import mosaic                                       # the training caches' image contract
        self.mosaic = mosaic

    def path(self, key: str) -> str:
        value = Path(self.dense_cfg["paths"][key])
        return str(value if value.is_absolute() else Path(self.spec.root) / value)

    def encode_text(self, instruction: str):
        from fastwam.memory_s1.model import encode_text
        dev = self.device if self.t5_on_gpu else torch.device("cpu")
        features, valid = encode_text(self.t5, self.tokenizer, instruction, dev)
        return features.to(self.device), valid.to(self.device)

    def base_label(self, label: str) -> str:
        return f"{label}_off"

    def describe(self) -> dict:
        return {"checkpoint": self.checkpoint, "kind": "fullft", "history": str(self.rule),
                "train_video": self.run_cfg.model.train_video, "run": self.run_cfg.name,
                "export_state": self.export_state, "t5_on_gpu": self.t5_on_gpu}


class FullSession:
    """Same constructor / reset / decide contract as memory_v2.online.Session; only mode 'on' exists."""

    def __init__(self, policy: FullPolicy, directory: Path, mode: str, steps: int, guidance_scale: float,
                 dependence: bool, tag: str = "", limit: int = 0, candidates: int = 1, coherence: str = "none",
                 noise: str = "per_decision", replay_cache: bool = True):
        if mode != "on" or candidates != 1 or coherence != "none" or guidance_scale != 1.0 or dependence:
            raise ValueError("fullft closed loop: only mode 'on', one candidate, no guidance / dependence")
        self.p, self.directory, self.mode = policy, Path(directory), mode
        self.steps, self.tag, self.limit, self.noise_mode = steps or 10, tag, limit, noise
        self.reset()

    def reset(self):
        self.raw: Dict[int, dict] = {}
        self.encoded: Dict[int, tuple] = {}
        self.cache = FrameCache()
        self.text = self.instruction = self.seed = self.task = None
        self.decisions = 0
        self.started = time.monotonic()

    def _encode(self, ids):
        import numpy as np
        from fastwam.memory_s1.model import encode_latent
        p = self.p
        for i in ids:
            if i in self.encoded:
                continue
            r = self.raw[i]
            arrays = [np.frombuffer(b, dtype=np.uint8).reshape(s) for b, s in zip(r["images"], r["shapes"])]
            image = p.mosaic(arrays)[None].to(p.device, torch.bfloat16)
            latent = encode_latent(p.vae, image)[0]                                   # [48, 1, 24, 20]
            proprio = p.normaliser.normalize(torch.tensor(r["proprio"], dtype=torch.float32)[None], "state")[0]
            self.encoded[i] = (latent, proprio.to(p.device))

    def decide(self, request: dict):
        import numpy as np
        from fastwam.memory_s1.common import seed_for
        from fastwam.memory_s1.sim_bridge import diagnostic_action_noise
        from fastwam.memory_v2.online import append, now
        p = self.p
        start = time.monotonic()
        current = int(request["current_id"])
        with torch.no_grad():
            if self.text is None:
                self.instruction, self.seed, self.task = request["instruction"], request["episode_seed"], request["task"]
                self.text, _ = p.encode_text(self.instruction)
            if (request["instruction"], request["episode_seed"]) != (self.instruction, self.seed):
                raise ValueError("Episode identity changed without reset")
            for r in request["observations"]:
                self.raw[int(r["frame_id"])] = r
            if sorted(self.raw) != list(range(current + 1)):
                raise ValueError("Missing contiguous observations")
            if p.rule.variant in ("event", "prop"):
                raise NotImplementedError("online event detection needs end-effector poses in the observations")
            ids, _ = select(p.rule, current)
            self._encode(sorted(set(ids) | {current}))
            noise_frame = 0 if self.noise_mode == "per_episode" else int(request.get("noise_frame", current))
            seed = seed_for(p.dense_cfg["seed"], self.seed, noise_frame, "closed-loop-noise")
            noise = diagnostic_action_noise(seed).to(torch.bfloat16).float()[None]
            out = decide_encoded(p.model, p.rule, self.cache, self.encoded, current, self.text, noise, self.steps)
            raw = p.normaliser.denormalize(out["normalised"].float().cpu())
            actions = raw.clone()
            actions[:, [6, 13]] = actions[:, [6, 13]].clamp(0, 1)
            if not bool(torch.isfinite(actions).all()):
                raise ValueError("Non-finite action")
            for i in [i for i in self.encoded if i not in keep_set(p.rule, current, []) and i != current]:
                del self.encoded[i]
        seconds = time.monotonic() - start
        append(self.directory / "decisions.jsonl", {
            "frame_id": current, "mode": self.mode, "steps": self.steps, "history_ids": out["ids"],
            "history_positions": out["positions"], "noise_seed": seed, "seconds": seconds,
            "normalized_actions": out["normalised"].float().cpu().tolist(), "actions_after_gripper_clip": actions.tolist(),
            "cached_frames": len(self.cache.kv)})
        if self.decisions % 4 == 0:
            print(f"[decide] {now()} {self.tag} frame={current}/{self.limit} hist={len(out['ids'])} "
                  f"policy={seconds:.1f}s elapsed={time.monotonic() - self.started:.0f}s", flush=True)
        self.decisions += 1
        return actions.numpy()


FullPolicy.session_cls = FullSession
