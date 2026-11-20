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
import os
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
                                   cfg.model.video_shift, cfg.model.action_shift, rule.ledger_features)
    model.set_trainable(cfg.model.train_video, cfg.model.lora_rank)
    model.load_state_dict(state["weights"], strict=True)
    model.requires_grad_(False)
    model.to(device=device, dtype=torch.bfloat16).eval()
    model.compute_dtype = None
    return model, cfg, state


def effective_rule(rule):
    """11-16 test-time ledger timing (descriptive ablations only; the model's own rule otherwise):
      MWAM_LEDGER_LAG=k          entries become visible k frames after confirmation instead of the trained lag
      MWAM_EVENT_DELTA=d         the detector's reversal threshold (metres; trained: rule.event_delta)
      MWAM_EVENT_MIN_PATH=m      the detector's debounce path (metres; trained: rule.event_min_path)
      MWAM_EVENT_PROVISIONAL=p   11-20 plan v16 T1 (earlier side): provisional write at a p-metre reversal (the v3c writer,
                                 events.EventRule.provisional; 0 = off; trained: rule.event_provisional)
    Unset -> the trained value. Every decision logs the values used ("event_rule": [delta, min_path, lag])."""
    import dataclasses
    changes = {}
    for env, key, cast in (("MWAM_LEDGER_LAG", "lag", int), ("MWAM_EVENT_DELTA", "event_delta", float),
                           ("MWAM_EVENT_MIN_PATH", "event_min_path", float),
                           ("MWAM_EVENT_PROVISIONAL", "event_provisional", float)):
        value = os.environ.get(env, "").strip()
        if value:
            changes[key] = cast(value)
    return dataclasses.replace(rule, **changes) if changes else rule


def count_counterfactual(entries: List[dict], mode: str) -> List[dict]:
    """11-14 test-time ledger counterfactuals on the number of completed moves (a move = a close followed by an open of
    the same arm). dropfirst: the first completed move is removed (close + its open) -> one move fewer counted from the
    moment it is complete. addmove: the first completed move is entered twice -> one move more counted. Other entries
    (top / bottom) and moves in progress are untouched; before the first move completes nothing changes."""
    first_close = next((i for i, e in enumerate(entries) if e["kind"] == "close"), None)
    if first_close is None:
        return entries
    arm = int(entries[first_close]["arm"])
    first_open = next((i for i in range(first_close + 1, len(entries))
                       if entries[i]["kind"] == "open" and int(entries[i]["arm"]) == arm), None)
    if first_open is None:
        return entries
    if mode == "dropfirst":
        return [e for i, e in enumerate(entries) if i not in (first_close, first_open)]
    out = list(entries)
    out[first_open + 1:first_open + 1] = [dict(entries[first_close]), dict(entries[first_open])]
    return out


def press_counterfactual(entries: List[dict], mode: str) -> List[dict]:
    """11-16 night: test-time counterfactuals on the number of presses (a press = a 'bottom' followed by a 'top' of the
    same arm, the detector's turning points of one stroke). addpress: the first completed press is entered twice ->
    one press more counted from the moment its 'top' is written; droppress: it is removed -> one press fewer. Applied to
    the full list of written entries, before the event_max cut; before the first press completes nothing changes."""
    b = next((i for i, e in enumerate(entries) if e["kind"] == "bottom"), None)
    if b is None:
        return entries
    arm = int(entries[b]["arm"])
    t = next((i for i in range(b + 1, len(entries)) if entries[i]["kind"] == "top" and int(entries[i]["arm"]) == arm), None)
    if t is None:
        return entries
    if mode == "droppress":
        return [e for i, e in enumerate(entries) if i not in (b, t)]
    out = list(entries)
    out[t + 1:t + 1] = [dict(entries[b]), dict(entries[t])]
    return out


def freeze_counterfactual(entries: List[dict], k: int) -> List[dict]:
    """11-15 test-time counterfactual 'freezeK': the ledger stops being written once K moves are complete (a move = a
    close followed by an open of the same arm): everything after the open that completes move K is withheld, so a
    later move (e.g. the third block move of a swap) happens but is never recorded. Before move K completes the
    ledger is unchanged. Applied to the full list of written entries, before the event_max cut."""
    holding = {}
    done = 0
    for i, e in enumerate(entries):
        arm = int(e["arm"])
        if e["kind"] == "close":
            holding[arm] = True
        elif e["kind"] == "open" and holding.get(arm):
            holding[arm] = False
            done += 1
            if done == int(k):
                return entries[:i + 1]
    return entries


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
    if rule.variant in ("event", "prop", "arev"):
        keep |= set(int(e) for e in events)
    return keep


@torch.no_grad()
def decide_encoded(model: FullModel, rule: HistoryRule, cache: FrameCache, encoded: Dict[int, tuple], current: int,
                   text: torch.Tensor, noise: torch.Tensor, steps: int = 10, events: List[int] = (),
                   ledger: Optional[tuple] = None) -> dict:
    """One decision from per-frame encodings: encoded[i] = (latent [48, 1, 24, 20], normalised proprio [14]).
    events: the KNOWN event frames (lag applied); ledger (arprop): (features [S, F], valid [S]) of data.ledger_tensor."""
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
    if ledger is not None:
        batch.update(ledger=ledger[0][None].to(device), ledger_valid=ledger[1][None].to(device))
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
        import os
        self.text_source = os.environ.get("MWAM_TEXT_SOURCE", "t5").strip().lower() or "t5"
        if self.text_source not in ("t5", "cache"):
            raise ValueError(f"MWAM_TEXT_SOURCE must be t5 or cache, got {self.text_source!r}")
        self._text_memo: Dict[str, tuple] = {}
        self.text_fingerprints: Dict[str, str] = {}
        self.t5 = self.tokenizer = None
        if self.text_source == "t5":                                       # cache: T5 is never called, not loaded
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
        """11-12: every official scene bank has ONE instruction per task, and T5 runs on the CPU on < 60 GB cards
        (bf16 on the A100 host's EPYC 7742 takes ~380 s per episode). Encoded once per process (same numbers).
        MWAM_TEXT_SOURCE=cache: the dense training cache's text of an episode with the same instruction instead of
        T5 here (identical on every machine, and what training saw); an instruction the cache lacks is an error."""
        hit = self._text_memo.get(instruction)
        if hit is None:
            if self.text_source == "cache":
                hit = self._cache_text(instruction)
            else:
                from fastwam.memory_s1.model import encode_text
                dev = self.device if self.t5_on_gpu else torch.device("cpu")
                features, valid = encode_text(self.t5, self.tokenizer, instruction, dev)
                hit = (features.to(self.device), valid.to(self.device))
            self._text_memo[instruction] = hit
        return hit[0].clone(), hit[1].clone()

    def _cache_text(self, instruction: str):
        from fastwam.memory_v2 import dense
        recs = [r for r in dense.records(self.spec) if r.get("instruction") == instruction]
        if recs:
            enc = dense.EpisodeStore(self.spec, verify=False)(recs[0]["episode_id"])
        else:      # 11-13: a model trained on other caches (C1: press/dense_<task>_v1) -> its own training roots
            import json
            for root in getattr(self.run_cfg.data, "roots", []) or []:
                rows = json.loads((Path(root) / "RECORDS.json").read_text(encoding="utf-8"))
                recs = [r for r in rows if r.get("instruction") == instruction]
                if recs:
                    path = Path(root) / "cache" / recs[0]["episode_id"].replace("/", "_") / "encodings.pt"
                    enc = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
                    break
        if not recs:
            raise ValueError(f"MWAM_TEXT_SOURCE=cache: no training episode has the instruction {instruction!r}")
        import hashlib
        text = enc["text"].to(torch.bfloat16).contiguous()
        valid = enc["text_valid"].bool().contiguous()
        # fingerprint of exactly what the model gets: the same 12 hex characters on two machines = identical text input
        fp = hashlib.sha256(text.view(torch.int16).cpu().numpy().tobytes() + valid.cpu().numpy().tobytes()).hexdigest()[:12]
        self.text_fingerprints[instruction] = f"{recs[0]['episode_id']}:{fp}"
        print(f"[fullft] text from the training cache ({recs[0]['episode_id']}, {len(recs)} episodes share it; "
              f"fingerprint {fp})", flush=True)
        return text[None].to(self.device), valid[None].to(self.device)

    def base_label(self, label: str) -> str:
        return f"{label}_off"

    def describe(self) -> dict:
        return {"checkpoint": self.checkpoint, "kind": "fullft", "history": str(self.rule),
                "train_video": self.run_cfg.model.train_video, "run": self.run_cfg.name,
                "export_state": self.export_state, "t5_on_gpu": self.t5_on_gpu, "text_source": self.text_source,
                "text_fingerprints": dict(self.text_fingerprints), "noise_salt": os.environ.get("MWAM_NOISE_SALT", ""),
                "ledger_ablation": os.environ.get("MWAM_LEDGER", ""),
                "clock_ablation": os.environ.get("MWAM_CLOCK", ""), "clock_scale": os.environ.get("MWAM_CLOCK_SCALE", ""),
                "token_budget": os.environ.get("MWAM_BUDGET", ""), "event_frames": os.environ.get("MWAM_EVFRAMES", "")}


def oracle_presses(raw: Dict[int, dict], current: int) -> List[dict]:
    """Plan v18 Z0 (11-21): the press entries an oracle writer would give, from the simulator's own counters
    (observation['task_counts'], sent only when the job has oracle_counts; MWAM_LEDGER=oracle sets it). A press of
    button 1 / 2 that the counter shows first at observation f becomes a 'bottom' entry with frame f - 1 (the step
    that pressed it) and confirmed f, so the first decision at or after f reads it (zero writing delay). The pressing
    arm is the one whose end effector is nearest the button in x, y at f (as press_ledger_audit). The confirm button
    is left out (the trained ledger never holds it). Detector 'bottom' entries are replaced by these; other kinds stay."""
    import math
    out, prev = [], None
    for f in range(current + 1):
        r = raw.get(f) or {}
        counts = r.get("task_counts")
        if counts is None:
            raise ValueError("MWAM_LEDGER=oracle needs observations with task_counts (the job's oracle_counts)")
        if prev is not None:
            for k, name in ((1, "press_cnt_1"), (2, "press_cnt_2")):
                for _ in range(max(0, int(counts.get(name, 0)) - int(prev.get(name, 0)))):
                    button = (r.get("task_buttons") or {}).get(f"button{k}")
                    pose = r.get("endpose") or {}
                    arm = 0
                    if button and pose.get("left") and pose.get("right"):
                        d = [math.dist(pose[s][:2], button[:2]) for s in ("left", "right")]
                        arm = 0 if d[0] <= d[1] else 1
                    out.append({"frame": f - 1, "arm": arm, "kind": "bottom", "confirmed": f, "oracle": k})
        prev = counts
    return out


def visible_events(events: List[dict], hide_after: Optional[int]) -> List[dict]:
    """Plan v17 T2b blind arm: the events whose entry was confirmed at or before `hide_after` (the previous decision's
    frame); None (every other run) returns the list itself, unchanged."""
    if hide_after is None:
        return events
    return [e for e in events if int(e.get("confirmed", e["frame"])) <= int(hide_after)]


def event_frames_off() -> bool:
    """11-19 plan v15 E9 (test time, arev only): MWAM_EVFRAMES=off shows no event frame (anchor + recent window only)."""
    raw = os.environ.get("MWAM_EVFRAMES", "").strip().lower()
    if raw not in ("", "off"):
        raise ValueError(f"MWAM_EVFRAMES must be unset or 'off', got {raw!r}")
    return raw == "off"


def token_budget() -> int:
    """11-19 plan v15 E22b (test time): MWAM_BUDGET=K keeps only K memory tokens (ledger: the last K entries; clock:
    K samples spread uniformly over the elapsed time); unset / 0 = as trained."""
    raw = os.environ.get("MWAM_BUDGET", "").strip()
    k = int(raw) if raw else 0
    if k < 0:
        raise ValueError(f"MWAM_BUDGET must be >= 0, got {raw!r}")
    return k


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
        from .events import EventDetector, rule_for
        self.rule = effective_rule(self.p.rule)
        self.detector = EventDetector(rule_for(self.rule))
        self.events: List[dict] = []                  # detected online, each with "confirmed" (= the frame it was seen)
        self.detected_upto = -1
        self.raw: Dict[int, dict] = {}
        self.encoded: Dict[int, tuple] = {}
        self.cache = FrameCache()
        self.text = self.instruction = self.seed = self.task = None
        self.decisions = 0
        self.started = time.monotonic()
        self.hide_after: Optional[int] = None         # plan v17 T2b blind arm: set (and cleared) by ReplanDriver only

    def observe(self, request: dict) -> List[dict]:
        """Plan v17 T2b (memory_v2.online.ReplanDriver): store the observations of a request and stream the event
        detector up to its frame WITHOUT deciding; returns the events confirmed by this call. decide() afterwards
        sees the same raw frames and events (its own _detect is then a no-op)."""
        current = int(request["current_id"])
        for r in request["observations"]:
            self.raw[int(r["frame_id"])] = r
        if sorted(self.raw) != list(range(current + 1)):
            raise ValueError("Missing contiguous observations")
        before = len(self.events)
        self._detect(current)
        return list(self.events[before:])

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

    def _proprio(self, frame: int) -> torch.Tensor:
        """Normalised proprio of an observed frame (as the training caches store it)."""
        r = self.raw[frame]
        return self.p.normaliser.normalize(torch.tensor(r["proprio"], dtype=torch.float32)[None], "state")[0]

    def _detect(self, current: int) -> None:
        """Stream the event detector over the frames not seen yet (commanded gripper = proprio columns 6 / 13, end-
        effector positions from the adapter's endpose): the same EventDetector the demos' events came from."""
        import numpy as np
        for i in range(self.detected_upto + 1, current + 1):
            r = self.raw[i]
            pose = r.get("endpose")
            if not pose:
                raise ValueError("observation without endpose: the simulator adapter predates 11-11 (event variants)")
            grip = [float(r["proprio"][6]), float(r["proprio"][13])]
            pos = np.asarray([pose["left"][:3], pose["right"][:3]], dtype=np.float64)
            for e in self.detector.step(i, grip, pos):
                e["confirmed"] = e.pop("visible", i)        # 11-19 provisional write: the earlier visible frame
                self.events.append(e)
            self.detected_upto = i

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
            known, ledger, entries = [], None, []
            if p.rule.variant in ("event", "prop", "arprop", "arev"):
                from .data import check_ledger_slots, ledger_tensor
                from .events import event_frames
                from .history import ledger_entries
                self._detect(current)
                seen = visible_events(self.events, self.hide_after)        # = self.events unless T2b blind
                known = event_frames(seen, before=current, known_by=current - int(self.rule.lag))
                if p.rule.variant == "arev" and event_frames_off():     # 11-19 plan v15 E9: event frames switched off
                    known = []
                if p.rule.variant == "arprop":
                    if self.decisions == 0:
                        check_ledger_slots(self.text[0], p.rule.event_max, "(online instruction)")
                    evs = seen + visible_events(self.detector.pending(), self.hide_after)   # 11-19: undecided
                                                                       # provisional entries (none when off)
                    entries = ledger_entries(self.rule, current, evs)
                    mode = os.environ.get("MWAM_LEDGER", "").strip().lower()      # 11-14: test-time ablations
                    if mode == "oracle":                 # 11-21 plan v18 Z0: zero-delay write of the TRUE presses
                        evs_o = [e for e in evs if e.get("kind") != "bottom"] + oracle_presses(self.raw, current)
                        entries = ledger_entries(self.rule, current, evs_o)
                    elif mode == "off":
                        entries = []                     # no entry = what the model sees before the first event
                    elif mode == "drop1":
                        entries = entries[:-1]           # the most recent event withheld: one event fewer counted
                    elif mode in ("dropfirst", "addmove"):
                        entries = count_counterfactual(entries, mode)[-int(p.rule.event_max):]
                    elif mode in ("addpress", "droppress"):      # 11-16: one press more / fewer (press_counterfactual)
                        import dataclasses
                        full = ledger_entries(dataclasses.replace(self.rule, event_max=10 ** 6), current, evs)
                        entries = press_counterfactual(full, mode)[-int(p.rule.event_max):]
                    elif mode.startswith("freeze") and mode[6:].isdigit():   # 11-15: freezeK (ledger stops at move K)
                        import dataclasses
                        full = ledger_entries(dataclasses.replace(self.rule, event_max=10 ** 6), current, evs)
                        entries = freeze_counterfactual(full, int(mode[6:]))[-int(p.rule.event_max):]
                    elif mode in ("ordplus1", "duppress"):      # 11-17 plan v13 E4: code + 1 / one more press, same code
                        import dataclasses
                        from .history import ordinal_counterfactual
                        full = ledger_entries(dataclasses.replace(self.rule, event_max=10 ** 6), current, evs)
                        entries = ordinal_counterfactual(full, mode)[-int(p.rule.event_max):]
                    elif mode:
                        raise ValueError(f"unknown MWAM_LEDGER mode {mode!r} (off | drop1 | dropfirst | addmove | freezeK | "
                                         "addpress | droppress | ordplus1 | duppress | oracle)")
                    budget = token_budget()                      # 11-19 plan v15 E22b: only the last K entries
                    if budget:
                        entries = entries[-budget:]
                    ledger = ledger_tensor(p.rule, entries, self._proprio)
            if p.rule.variant == "arclk":                       # 11-17 plan v13 E5: clock tokens (time-indexed)
                from .data import check_ledger_slots, clock_tensor
                from .history import clock_frames
                if self.decisions == 0:
                    check_ledger_slots(self.text[0], p.rule.event_max, "(online instruction)")
                scale = float(os.environ.get("MWAM_CLOCK_SCALE", "").strip() or 1.0)   # E5 timestamp x1.5 / x0.5
                cmode = os.environ.get("MWAM_CLOCK", "").strip().lower()   # 11-19 plan v15 E21: off | freeze | flat
                budget = token_budget()                          # 11-19 plan v15 E22b: K uniform samples, not 32
                if budget:
                    import dataclasses
                    frames = clock_frames(dataclasses.replace(p.rule, event_max=min(budget, int(p.rule.event_max))), current)
                else:
                    frames = clock_frames(p.rule, current)
                ledger = clock_tensor(p.rule, frames, self._proprio, scale, mode=cmode, current=current)
                entries = [{"frame": f, "arm": -1, "kind": "clock", "confirmed": f} for f in frames]
            ids, _ = select(p.rule, current, known)
            self._encode(sorted(set(ids) | {current} | (set(known) if p.rule.variant == "prop" else set())))
            noise_frame = 0 if self.noise_mode == "per_episode" else int(request.get("noise_frame", current))
            salt = os.environ.get("MWAM_NOISE_SALT", "").strip()   # 11-13: replicate runs (same scenes, other noise)
            seed = seed_for(p.dense_cfg["seed"], self.seed, noise_frame, "closed-loop-noise" + (f"-{salt}" if salt else ""))
            noise = diagnostic_action_noise(seed).to(torch.bfloat16).float()      # [1, 32, 14] (11-11: was [None]-ed
                                                                                   # to [1, 1, 32, 14] and crashed)
            out = decide_encoded(p.model, p.rule, self.cache, self.encoded, current, self.text, noise, self.steps,
                                 known, ledger)
            raw = p.normaliser.denormalize(out["normalised"].float().cpu())
            actions = raw.clone()
            actions[:, [6, 13]] = actions[:, [6, 13]].clamp(0, 1)
            if not bool(torch.isfinite(actions).all()):
                raise ValueError("Non-finite action")
            for i in [i for i in self.encoded if i not in keep_set(p.rule, current, known) and i != current]:
                del self.encoded[i]
        seconds = time.monotonic() - start
        append(self.directory / "decisions.jsonl", {
            "frame_id": current, "mode": self.mode, "steps": self.steps, "history_ids": out["ids"],
            "history_positions": out["positions"], "noise_seed": seed, "seconds": seconds,
            "normalized_actions": out["normalised"].float().cpu().tolist(), "actions_after_gripper_clip": actions.tolist(),
            "cached_frames": len(self.cache.kv), "events_known": known,
            "ledger": [[int(e["frame"]), int(e["arm"]), e["kind"], int(e["confirmed"])] + ([int(e["ordinal"])] if "ordinal" in e else [])
                       for e in entries],
            "event_rule": [float(self.rule.event_delta), float(self.rule.event_min_path), int(self.rule.lag),
                           float(self.rule.event_provisional)],
            **({"hide_after": int(self.hide_after)} if self.hide_after is not None else {})})
        if self.decisions % 4 == 0:
            print(f"[decide] {now()} {self.tag} frame={current}/{self.limit} hist={len(out['ids'])} "
                  f"policy={seconds:.1f}s elapsed={time.monotonic() - self.started:.0f}s", flush=True)
        self.decisions += 1
        return actions.numpy()


FullPolicy.session_cls = FullSession
