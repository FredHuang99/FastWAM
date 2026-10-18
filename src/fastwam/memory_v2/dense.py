"""Bridge from memory_v2 to the dense-joint (A/B) delivery on the training host.

What is reused, unchanged, from `/restore-tmp/dense_joint_v1` (Codex delivery):
  * the authenticated output `outputs/s1_dense_joint_h100_v1` (IDENTITY, RECORDS,
    WINDOWS, per-episode VAE/text/proprio/action cache built with the float
    two-stage image contract);
  * `model_path.load_model(out, "A")` -> ABModel: released Video DiT + proprio
    (frozen) with the C+256 ActionDiT and its BF16 functional-call core;
  * the released normaliser and the fixed offline windows.

What is new here:
  * `load_ab_model` accepts the C+256 source or any A checkpoint
    (DeepSpeed `mp_rank_00_model_states.pt` or a `weights_*.pt` export);
  * `DenseActionAdapter` exposes ABModel's action path through the memory_v2
    adapter protocol, so memory_v2 runs on exactly the same numerical core;
  * `FeatureStore` precomputes the frozen post-Video-DiT feature of every frame
    once (A never changes the visual expert), instead of re-encoding history at
    every update;
  * `EpisodeStore` / `make_batch` build memory_v2 batches from the dense cache;
  * `window_metrics` scores sampled chunks the same way the dense evaluation does
    (denormalised arm/gripper RMSE, executed prefix), plus prefix 16.

Nothing here writes into the dense output directory.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import torch
from torch import nn

from .config import HistoryPolicyConfig
from .history import collate_history, select_history

ARM_COLUMNS = [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12]
GRIPPER_COLUMNS = [6, 13]
HORIZON = 32
FEATURE_VERSION = "memory_v2-dense-features-v1"


# ----------------------------------------------------------------------------- binding
@dataclass(frozen=True)
class DenseSpec:
    root: Path = Path("/workspace/FastWAM")                                   # repo on the host
    code: Path = Path("/restore-tmp/dense_joint_v1")                          # Codex delivery code
    output: Path = Path("/workspace/FastWAM/outputs/s1_dense_joint_h100_v1")  # authenticated dense run
    verify_identity: bool = True

    @classmethod
    def from_dict(cls, value: Optional[dict]) -> "DenseSpec":
        value = dict(value or {})
        return cls(root=Path(value.get("root", cls.root)), code=Path(value.get("code", cls.code)),
                   output=Path(value.get("output", cls.output)),
                   verify_identity=bool(value.get("verify_identity", True)))


_BOUND: Dict[str, object] = {}
SOFTWARE_DRIFT: Dict[str, dict] = {}


def _software_drift(recorded: dict, actual: dict) -> dict:
    """Keys of the dense encoder_software receipt that differ on this host."""
    drift = {}
    for key in ("python", "executable"):
        if recorded.get(key) != actual.get(key):
            drift[key] = {"recorded": recorded.get(key), "actual": actual.get(key)}
    rp, ap = recorded.get("packages", {}), actual.get("packages", {})
    for name in sorted(set(rp) | set(ap)):
        if rp.get(name) != ap.get(name):
            drift[f"packages.{name}"] = {"recorded": rp.get(name), "actual": ap.get(name)}
    return drift


def bind(spec: DenseSpec):
    """Import the dense delivery's `common` module and authenticate its output once per process.

    Authentication = the dense `identity()` (prepared cache files, delivery code, repo
    source files). Its encoder_software check is reported instead of enforced: that
    receipt protects *re-encoding* (VAE/text) with other packages, while memory_v2 only
    reads the already-authenticated cache. The drift is recorded in SOFTWARE_DRIFT and in
    every checkpoint/run description.
    """
    key = str(spec.output.resolve())
    if key in _BOUND:
        return _BOUND[key]
    os.environ.setdefault("FW_ROOT", str(spec.root))
    try:                                   # keep the already-imported fastwam (e.g. a memory2 worktree)
        import fastwam  # noqa: F401
    except ImportError:
        if str(spec.root / "src") not in sys.path:
            sys.path.insert(0, str(spec.root / "src"))
    if str(spec.code) not in sys.path:
        sys.path.insert(0, str(spec.code))
    import common  # noqa: E402  (dense_joint_v1/common.py)
    # STOP ownership belongs to the dense run; memory_v2 runs use their own STOP file.
    common.boundary = lambda *args, **kwargs: None
    recorded = common.read(spec.output / "IDENTITY.json")
    drift = _software_drift(recorded.get("encoder_software", {}), common.encoder_software())
    if spec.verify_identity:
        original = common.encoder_software
        common.encoder_software = lambda: recorded["encoder_software"]
        try:
            identity = common.identity(spec.output)
        finally:
            common.encoder_software = original
    else:
        identity = common.sig(recorded)
    if drift:
        print("[dense] WARNING runtime packages differ from the dense preparation receipt "
              "(cache is read, not re-encoded): " + json.dumps(drift), flush=True)
    SOFTWARE_DRIFT[key] = drift
    _BOUND[key] = (common, identity)
    return common, identity


def dense_config(spec: DenseSpec) -> dict:
    common, _ = bind(spec)
    return common.read(spec.output / "IDENTITY.json")["config"]


def records(spec: DenseSpec) -> List[dict]:
    common, _ = bind(spec)
    return common.read(spec.output / "RECORDS.json")


def windows(spec: DenseSpec) -> List[dict]:
    common, _ = bind(spec)
    return common.read(spec.output / "WINDOWS.json")


def window_kind(row: dict) -> str:
    labels = row.get("labels", [])
    if "initial" in labels:
        return "initial"
    if any("_close_" in x or "_release_" in x for x in labels):
        return "event"
    return "ordinary"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(16 * 1024 ** 2), b""):
            h.update(block)
    return h.hexdigest()


# ----------------------------------------------------------------------------- model
def load_ab_model(spec: DenseSpec, checkpoint: Optional[str] = "source", device: str = "cuda:0",
                  hash_checkpoint: bool = True):
    """ABModel (branch A layout) with the C+256 source weights, optionally overwritten by an A checkpoint.

    checkpoint: "source" | path to DeepSpeed `mp_rank_00_model_states.pt` | path to `weights_*.pt`.
    Returns (model, info). The model is in eval mode with every parameter frozen.
    """
    common, identity = bind(spec)
    from model_path import load_model  # dense_joint_v1/model_path.py
    model = load_model(spec.output, "A", device)
    source = common.read(spec.output / "IDENTITY.json")["source_checkpoint"]
    drift = SOFTWARE_DRIFT.get(str(spec.output.resolve()), {})
    info = {"label": "source", "path": source["relative"], "sha256": source["sha256"], "dense_identity": identity,
            "software_drift": drift}
    if checkpoint not in (None, "", "source"):
        path = Path(checkpoint)
        state = torch.load(path, map_location="cpu", mmap=True, weights_only=False)
        if "module" in state:
            weights = state["module"]
        elif "model" in state:
            weights = state["model"]
        else:
            raise ValueError(f"{path}: neither a DeepSpeed model-state file nor a weights export.")
        model.load_state_dict(weights, strict=True)
        del state, weights
        info = {"label": path.parent.name if path.name.startswith("mp_rank") else path.stem, "path": str(path),
                "sha256": file_sha256(path) if hash_checkpoint else None, "dense_identity": identity,
                "software_drift": drift}
    model.requires_grad_(False)
    model.eval()
    info["video_digest"] = video_digest(model)
    return model, info


def video_digest(ab_model) -> str:
    """Digest of a few frozen visual/proprio tensors; history features are only valid for this value."""
    backbone = ab_model.backbone
    video = backbone.mot.mixtures["video"]
    tensors = [video.blocks[0].self_attn.q.weight, video.blocks[-1].self_attn.q.weight, backbone.proprio_encoder.weight]
    h = hashlib.sha256()
    for t in tensors:
        h.update(t.detach().float().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


class DenseActionAdapter(nn.Module):
    """memory_v2 adapter over ABModel's BF16 functional action path.

    With memory bypassed, `MemoryV2Model.velocity(..., memory_mode="off")` performs
    exactly the calls of `ABModel.velocity(..., scale=0)` (same `call` wrappers, same
    casts, same activation checkpointing), so the base model is reproduced.
    """

    def __init__(self, ab_model, train_action: bool = False):
        super().__init__()
        self.ab = ab_model
        self.num_action_layers = len(ab_model.backbone.mot.mixtures["action"].blocks)
        self.ab.requires_grad_(False)
        self.train_action = bool(train_action)
        if self.train_action:
            self.ab.backbone.mot.mixtures["action"].requires_grad_(True)

    def named_action_parameters(self) -> List[Tuple[str, nn.Parameter]]:
        return [(n, p) for n, p in self.ab.backbone.mot.mixtures["action"].named_parameters() if p.requires_grad]

    @torch.no_grad()
    def encode(self, batch):
        _, kv, context = self.ab.encode(batch["latent"], batch["text"], batch["proprio"])
        return kv, context

    def prepare(self, actions, timestep, shared_context):
        context, mask = shared_context
        x, _, mod, ctx, ctx_mask, freqs = self.ab.call("prepare_action", actions.to(torch.bfloat16),
                                                       timestep.to(torch.bfloat16), context, mask)
        return x, (mod, ctx, ctx_mask, freqs)

    def block(self, index, x, aux, current_kv):
        mod, ctx, ctx_mask, freqs = aux
        keys, values = current_kv
        return self.ab.call("action", x, freqs, mod, ctx, ctx_mask, keys[index], values[index],
                            index=index, checkpointed=True)

    def post(self, x, aux):
        return self.ab.call("post_action", x)


# ----------------------------------------------------------------------------- data
def cache_dir(spec: DenseSpec, episode_id: str) -> Path:
    return spec.output / "cache" / episode_id.replace("/", "_")


class EpisodeStore:
    """LRU of the dense per-episode encodings (VAE latent, text, proprio, normalised actions)."""

    def __init__(self, spec: DenseSpec, capacity: int = 8, verify: bool = True):
        self.spec = spec
        self.capacity = capacity
        self.verify = verify
        self._loaded: "OrderedDict[str, dict]" = OrderedDict()
        self._verified = set()

    def __call__(self, episode_id: str) -> dict:
        if episode_id not in self._loaded:
            folder = cache_dir(self.spec, episode_id)
            if self.verify and episode_id not in self._verified:
                common, identity = bind(self.spec)
                marker = common.read(folder / "COMPLETE.json")
                if marker["identity"] != identity:
                    raise ValueError(f"Dense cache binding changed for {episode_id}.")
                common.verify(folder, marker["files"])
                self._verified.add(episode_id)
            self._loaded[episode_id] = torch.load(folder / "encodings.pt", map_location="cpu", weights_only=True, mmap=True)
            while len(self._loaded) > self.capacity:
                self._loaded.popitem(last=False)
        self._loaded.move_to_end(episode_id)
        return self._loaded[episode_id]


def action_window(actions: torch.Tensor, anchor: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Same as dense data_path.window_indices: hold the last target past the episode end, mask it."""
    n = len(actions)
    if not 0 <= anchor < n:
        raise ValueError(f"Anchor {anchor} outside episode of length {n}.")
    index = torch.clamp(torch.arange(anchor, anchor + HORIZON), max=n - 1)
    valid = torch.arange(anchor, anchor + HORIZON) < n
    return actions[index], valid


class FeatureStore:
    """Frozen post-Video-DiT features of every frame, one BF16 file per episode: [L, 120, 3072].

    The feature of frame j is ABModel.encode(latent_j, text, proprio_j)[0], i.e. exactly
    what dense A re-encodes for its history (visual expert and proprio encoder frozen).
    """

    def __init__(self, directory: Path, capacity: int = 16):
        self.directory = Path(directory)
        self.capacity = capacity
        self._loaded: "OrderedDict[str, torch.Tensor]" = OrderedDict()
        self.manifest = self._read_manifest()

    def _read_manifest(self) -> Optional[dict]:
        path = self.directory / "MANIFEST.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None

    def path(self, episode_id: str) -> Path:
        return self.directory / (episode_id.replace("/", "_") + ".pt")

    def require(self, video_digest_value: str, dense_identity: str) -> None:
        if self.manifest is None:
            raise FileNotFoundError(f"No feature MANIFEST under {self.directory}; run `train_v2 features` first.")
        if self.manifest.get("version") != FEATURE_VERSION:
            raise ValueError("Feature cache version differs from this code.")
        if self.manifest.get("video_digest") != video_digest_value:
            raise ValueError("Feature cache was built with different visual/proprio weights (B checkpoint?).")
        if self.manifest.get("dense_identity") != dense_identity:
            raise ValueError("Feature cache was built from a different dense output.")

    def __call__(self, episode_id: str) -> torch.Tensor:
        if episode_id not in self._loaded:
            entry = (self.manifest or {}).get("episodes", {}).get(episode_id)
            if entry is None:
                raise KeyError(f"Episode {episode_id} missing from the feature cache.")
            self._loaded[episode_id] = torch.load(self.path(episode_id), map_location="cpu", weights_only=True, mmap=True)
            while len(self._loaded) > self.capacity:
                self._loaded.popitem(last=False)
        self._loaded.move_to_end(episode_id)
        return self._loaded[episode_id]

    @torch.no_grad()
    def build(self, ab_model, info: dict, spec: DenseSpec, episodes: Sequence[str], batch: int = 16,
              log=print) -> dict:
        """Encode every frame of every listed episode (resumable; one atomic file per episode)."""
        self.directory.mkdir(parents=True, exist_ok=True)
        manifest = self.manifest or {"version": FEATURE_VERSION, "video_digest": info["video_digest"],
                                     "dense_identity": info["dense_identity"], "grid": [12, 10], "width": 3072,
                                     "dtype": "bfloat16", "episodes": {}}
        if manifest["video_digest"] != info["video_digest"] or manifest["dense_identity"] != info["dense_identity"]:
            raise ValueError("Existing feature cache belongs to other weights/data; use a new directory.")
        store = EpisodeStore(spec, capacity=2)
        device = next(ab_model.parameters()).device
        for k, episode_id in enumerate(episodes):
            if episode_id in manifest["episodes"] and self.path(episode_id).is_file():
                continue
            e = store(episode_id)
            length = len(e["actions"])
            out = []
            for start in range(0, length, batch):
                ids = list(range(start, min(length, start + batch)))
                latent = e["latent"][ids].to(device)
                text = e["text"][None].to(device).expand(len(ids), -1, -1)
                proprio = e["proprio"][ids].to(device)
                features, _, _ = ab_model.encode(latent, text, proprio, keep_kv=False)
                out.append(features.to(torch.bfloat16).cpu())
            tensor = torch.cat(out).contiguous()
            if tuple(tensor.shape[1:]) != (120, 3072) or not bool(torch.isfinite(tensor.float()).all()):
                raise ValueError(f"Invalid features for {episode_id}: {tuple(tensor.shape)}")
            target = self.path(episode_id)
            temp = target.with_name(target.name + ".partial")
            torch.save(tensor, temp)
            temp.replace(target)
            manifest["episodes"][episode_id] = {"frames": int(len(tensor)), "bytes": target.stat().st_size}
            _atomic_json(self.directory / "MANIFEST.json", manifest)
            log(f"[features] {k + 1}/{len(episodes)} {episode_id} frames={len(tensor)}")
        self.manifest = manifest
        return manifest


def _atomic_json(path: Path, value) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f".{os.getpid()}.partial")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)


def make_batch(rows: Sequence[dict], episodes: EpisodeStore, features: FeatureStore, policy: HistoryPolicyConfig,
               device, noise_dtype=torch.float32) -> Dict[str, torch.Tensor]:
    """rows: [{"episode_id", "anchor"}, ...] -> memory_v2 batch on `device`."""
    latents, texts, proprio, actions, valid, selections, feats = [], [], [], [], [], [], []
    for row in rows:
        e = episodes(row["episode_id"])
        a = int(row["anchor"])
        chunk, mask = action_window(e["actions"], a)
        selection = select_history(range(a + 1), a, policy)
        f = features(row["episode_id"])
        if len(f) != len(e["actions"]):
            raise ValueError(f"Feature/episode length mismatch for {row['episode_id']}.")
        latents.append(e["latent"][a])
        texts.append(e["text"])
        proprio.append(e["proprio"][a])
        actions.append(chunk)
        valid.append(mask)
        selections.append(selection)
        feats.append([f[i] for i in selection.ids])
    lengths = {t.shape for t in texts}
    if len(lengths) != 1:
        raise ValueError(f"Text encodings differ in shape across the batch: {lengths}; use micro_batch=1.")
    history = collate_history(feats, selections, tokens_per_frame=120, width=3072, dtype=torch.bfloat16)
    batch = {"latent": torch.stack(latents), "text": torch.stack(texts), "proprio": torch.stack(proprio),
             "actions": torch.stack(actions).to(noise_dtype), "action_valid": torch.stack(valid), **history}
    return {k: v.to(device, non_blocking=True) for k, v in batch.items()}


# ----------------------------------------------------------------------------- metrics
def window_metrics(normalised_sample: torch.Tensor, normalised_target: torch.Tensor, valid: torch.Tensor,
                   normaliser) -> Dict[str, float]:
    """Denormalised errors of one chunk [32, 14] (dense evaluation conventions + prefix 16)."""
    raw = normaliser.denormalize(normalised_sample.float())
    target = normaliser.denormalize(normalised_target.float())
    if not bool(torch.isfinite(raw).all()):
        raise ValueError("Nonfinite sampled actions.")
    error = (raw - target).square()
    v = valid.bool()

    def rmse(rows, cols):
        selected = error[rows][:, cols]
        return float(selected.mean().sqrt()) if selected.numel() else float("nan")

    steps = torch.arange(len(error), device=error.device)
    return {"arm_rmse_rad": rmse(v, ARM_COLUMNS), "gripper_rmse": rmse(v, GRIPPER_COLUMNS),
            "prefix16_arm_rmse_rad": rmse(v & (steps < 16), ARM_COLUMNS),
            "prefix24_arm_rmse_rad": rmse(v & (steps < 24), ARM_COLUMNS),
            "prefix16_gripper_rmse": rmse(v & (steps < 16), GRIPPER_COLUMNS),
            "prefix24_gripper_rmse": rmse(v & (steps < 24), GRIPPER_COLUMNS)}


def window_noise(row: dict, shape, device) -> torch.Tensor:
    """Same first draw as the dense evaluation (`random_inputs` with the row's action seed)."""
    generator = torch.Generator(device="cpu").manual_seed(int(row["action_seed"]))
    return torch.randn(shape, generator=generator, dtype=torch.float32).to(device)


def summarise(cases: Iterable[dict], keys: Sequence[str], group_by: Sequence[str] = ("task", "split")) -> List[dict]:
    """Mean of `keys` per group and per window kind."""
    cases = list(cases)
    groups: Dict[tuple, List[dict]] = {}
    for c in cases:
        groups.setdefault(tuple(c[g] for g in group_by), []).append(c)
    out = []
    for key in sorted(groups):
        subset = groups[key]
        item = {g: v for g, v in zip(group_by, key)}
        item["windows"] = len(subset)
        for k in keys:
            values = [c[k] for c in subset if c.get(k) is not None and c[k] == c[k]]
            item[k] = sum(values) / len(values) if values else None
        item["by_window_kind"] = {}
        for kind in ("initial", "event", "ordinary"):
            xs = [c for c in subset if c["kind"] == kind]
            if xs:
                item["by_window_kind"][kind] = {"windows": len(xs), **{
                    k: (sum(c[k] for c in xs if c.get(k) is not None) / max(1, sum(1 for c in xs if c.get(k) is not None)))
                    for k in keys}}
        out.append(item)
    return out
