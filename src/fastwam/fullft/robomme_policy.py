"""RoboMME closed loop, policy side (plan v22 6.6 step 4; Status 11-28 12.10), 11-28 17:28 Opus. Runs in mwam5090 on one
GPU; the simulator side (scripts/robomme/robomme_client.py) runs in RoboMME's own image. The two talk over an AF_UNIX
socket in a folder both containers mount (multiprocessing.connection with an authkey read from a key file). Every
message is bytes: a 4-byte big-endian header length, a JSON header, then raw uint8 image bytes -- neither side
unpickles the other's numpy (the two images pin different numpy versions).
  request {"cmd": "reset", "task", "episode", "goal"}                         -> {"ok": true}
  request {"cmd": "decide", "frames": [{"frame", "eef" [6], "grip" [2], "shape" [H, W, 3]}, ...]} + per frame the
          front then the wrist image bytes (every frame since the last decision, contiguous from 0)
                                                                              -> {"ok": true, "actions": [[7] x execute]}
  request {"cmd": "close"}                                                     -> {"ok": true}; the server exits
Per frame the training path (scripts/robomme/robomme_encode.py): libero_image (224 x 448, [-1, 1]) -> the eager
single-frame VAE (memory_s1.encode_latent); proprio = eef_state (6) + gripper_state (2) normalised with the dense root's
NORM_STATS.json (robomme_norm.py: min/max -> [-1, 1], clamp +-5). Text: T5 of the goal (memory_s1.encode_text, the
training call), T5 kept on the CPU, memoised per goal. One decision = fullft.online.decide_encoded (the export's history
selection, frame cache and sampling; --steps, default the export's sample_steps); the 32 actions are denormalised with
the inverse min/max map, the gripper clipped to [-1, 1], and the first --execute returned (absolute ee_pose: position 3
+ RPY 3 + gripper 1, RoboMME's ee_pose action space).
Noise: per decision, torch.Generator seeded from (episode, frame[, MWAM_NOISE_SALT]) -> [1, 32, action_dim] standard
normal (the same draws for every checkpoint on the same episode and frame).
Variants: none / ar (no events needed). Variants that read body events (arprop, prop, event, arev) are refused here
until the single-arm online event writer exists (RoboMME's events are those of robomme_convert.py: gripper command of the
executed action, end-effector height).
  CUDA_VISIBLE_DEVICES=<g> PYTHONPATH=src /opt/mwam/bin/python -m fastwam.fullft.robomme_policy --checkpoint X \\
      --root outputs/robomme/dense_robomme_v1 --socket DIR/rpc.sock --key-file DIR/rpc.key --execute 8 --log DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch

HORIZON = 32
_ENCODE = None


def libero_image(front, wrist):
    """scripts/robomme/robomme_encode.py's libero_image (the training cache's image path), loaded from the repo."""
    global _ENCODE
    if _ENCODE is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "robomme_encode", Path(__file__).resolve().parents[3] / "scripts/robomme/robomme_encode.py")
        _ENCODE = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_ENCODE)
    return _ENCODE.libero_image(front, wrist)


# ----------------------------------------------------------------------------- framing (shared with the client)
def pack(header: dict, payload: bytes = b"") -> bytes:
    h = json.dumps(header).encode()
    return struct.pack(">I", len(h)) + h + payload


def unpack(message: bytes) -> Tuple[dict, bytes]:
    (n,) = struct.unpack(">I", message[:4])
    return json.loads(message[4:4 + n].decode()), message[4 + n:]


def split_images(frames: List[dict], payload: bytes):
    """[(frame dict, front uint8 [H, W, 3], wrist uint8 [H, W, 3])] from a decide request."""
    import numpy as np
    out, at = [], 0
    for f in frames:
        h, w, c = (int(x) for x in f["shape"])
        size = h * w * c
        front = np.frombuffer(payload[at:at + size], dtype=np.uint8).reshape(h, w, c)
        wrist = np.frombuffer(payload[at + size:at + 2 * size], dtype=np.uint8).reshape(h, w, c)
        at += 2 * size
        out.append((f, front, wrist))
    if at != len(payload):
        raise ValueError(f"payload holds {len(payload)} bytes, the frames describe {at}")
    return out


# ----------------------------------------------------------------------------- normalisation
class Norm:
    """NORM_STATS.json of the dense root (robomme_norm.py)."""

    def __init__(self, path: Path):
        doc = json.loads(Path(path).read_text())
        st = doc["stats"]
        self.sha = doc.get("sha256", "")
        self.p_scale, self.p_offset = torch.tensor(st["proprio"]["scale"]), torch.tensor(st["proprio"]["offset"])
        self.a_scale, self.a_offset = torch.tensor(st["actions"]["scale"]), torch.tensor(st["actions"]["offset"])

    def proprio(self, raw: torch.Tensor) -> torch.Tensor:
        return torch.clamp(raw.float() * self.p_scale + self.p_offset, -5.0, 5.0)

    def actions(self, normalised: torch.Tensor) -> torch.Tensor:
        a = (normalised.float().cpu() - self.a_offset) / self.a_scale
        a[..., -1] = a[..., -1].clamp(-1.0, 1.0)
        return a


def noise_for(episode: int, frame: int, action_dim: int, salt: str = "") -> torch.Tensor:
    key = f"robomme-closed-loop|{int(episode)}|{int(frame)}" + (f"|{salt}" if salt else "")
    seed = int(hashlib.sha256(key.encode()).hexdigest()[:15], 16)
    g = torch.Generator().manual_seed(seed)
    return torch.randn(1, HORIZON, int(action_dim), generator=g)


# ----------------------------------------------------------------------------- the policy
class RoboMMEPolicy:
    EVENT_VARIANTS = ("arprop", "prop", "event", "arev")

    def __init__(self, checkpoint: str, root: str, device: str = "cuda", steps: int = 0, execute: int = 8):
        from fastwam.models.wan22.helpers.loader import _load_registered_model
        from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
        from .online import load_export
        self.device = torch.device(device)
        self.model, self.cfg, _ = load_export(checkpoint, device)
        self.rule = self.cfg.rule
        if self.rule.variant in self.EVENT_VARIANTS:
            raise ValueError(f"history '{self.rule.variant}' needs the single-arm online event writer (not written yet)")
        self.action_dim = None
        self.steps = int(steps or getattr(self.cfg.model, "sample_steps", 10) or 10)
        self.execute = int(execute)
        root = Path(root)
        self.norm = Norm(root / "NORM_STATS.json")
        self.action_dim = int(self.norm.a_scale.numel())
        enc = getattr(self.model.mot.mixtures["action"], "action_encoder", None)
        if enc is not None and int(enc.in_features) != self.action_dim:
            raise ValueError(f"the export's action width {enc.in_features} != NORM_STATS actions {self.action_dim}")
        if int(self.model.proprio_encoder.in_features) != int(self.norm.p_scale.numel()):
            raise ValueError("the export's proprio width does not match NORM_STATS proprio")
        paths = json.loads((root / "IDENTITY.json").read_text())["config"]["paths"]
        self.vae = _load_registered_model(paths["vae"], "wan_video_vae", torch.bfloat16, str(self.device))
        self.vae.eval().requires_grad_(False)
        self.t5 = _load_registered_model(paths["t5"], "wan_video_text_encoder", torch.bfloat16, "cpu")
        self.t5.eval().requires_grad_(False)
        self.tokenizer = HuggingfaceTokenizer(paths["tokenizer"], seq_len=128, clean="whitespace", local_files_only=True)
        self.text_memo: Dict[str, torch.Tensor] = {}
        self.salt = os.environ.get("MWAM_NOISE_SALT", "").strip()
        self.reset("", -1, "")

    def reset(self, task: str, episode: int, goal: str):
        from .online import FrameCache
        self.task, self.episode, self.goal = task, int(episode), goal
        self.raw: Dict[int, tuple] = {}
        self.encoded: Dict[int, tuple] = {}
        self.cache = FrameCache()
        self.text = None
        self.decisions = 0
        self.seen_upto = -1
        if goal:
            if goal not in self.text_memo:
                from fastwam.memory_s1.model import encode_text
                f, _ = encode_text(self.t5, self.tokenizer, goal, "cpu")
                self.text_memo[goal] = f.to(torch.bfloat16)
            self.text = self.text_memo[goal].to(self.device)

    @torch.no_grad()
    def _encode(self, ids):
        import numpy as np
        from fastwam.memory_s1.model import encode_latent
        todo = [i for i in ids if i not in self.encoded]
        for i in todo:
            front, wrist, eef, grip = self.raw[i]
            image = libero_image(front[None], wrist[None])                     # [1, 3, 224, 448] in [-1, 1]
            latent = encode_latent(self.vae, image.to(self.device))[0]          # [48, 1, 14, 28]
            proprio = self.norm.proprio(torch.tensor(np.concatenate([eef, grip]), dtype=torch.float32))
            self.encoded[i] = (latent, proprio.to(self.device))

    @torch.no_grad()
    def decide(self, frames) -> List[List[float]]:
        import numpy as np
        from .history import select
        from .online import decide_encoded, keep_set
        if self.text is None:
            raise ValueError("decide before reset")
        got = [int(f["frame"]) for f, _, _ in frames]
        if not got or got != list(range(self.seen_upto + 1, self.seen_upto + 1 + len(got))):
            raise ValueError(f"frames {got[:3]}... do not continue from {self.seen_upto} contiguously")
        for f, front, wrist in frames:
            self.raw[int(f["frame"])] = (np.array(front), np.array(wrist), np.asarray(f["eef"], np.float64),
                                         np.asarray(f["grip"], np.float64))
        self.seen_upto = current = got[-1]
        ids, _ = select(self.rule, current, [])
        self._encode(sorted(set(ids) | {current}))
        noise = noise_for(self.episode, current, self.action_dim, self.salt).to(torch.bfloat16).float()
        out = decide_encoded(self.model, self.rule, self.cache, self.encoded, current, self.text, noise, self.steps,
                             [], None)
        actions = self.norm.actions(out["normalised"])
        if not bool(torch.isfinite(actions).all()):
            raise ValueError("Non-finite action")
        keep = keep_set(self.rule, current, [])
        for i in [i for i in self.raw if i not in keep and i != current]:
            del self.raw[i]
            self.encoded.pop(i, None)
        self.last = {"frame": current, "history_ids": list(out["ids"]), "normalised": out["normalised"].float().cpu().tolist()}
        self.decisions += 1
        return actions[: self.execute].tolist()


# ----------------------------------------------------------------------------- server
def serve(policy, socket: str, key: bytes, log_dir: Path):
    from multiprocessing.connection import Listener
    log_dir.mkdir(parents=True, exist_ok=True)
    dec = (log_dir / "decisions.jsonl").open("a")
    if os.path.exists(socket):
        os.unlink(socket)
    with Listener(socket, family="AF_UNIX", authkey=key) as listener:
        print(f"[robomme-policy] {time.strftime('%F %T')} listening on {socket}", flush=True)
        with listener.accept() as conn:
            while True:
                header, payload = unpack(conn.recv_bytes())
                cmd = header.get("cmd")
                try:
                    if cmd == "reset":
                        policy.reset(header["task"], int(header["episode"]), header["goal"])
                        reply = {"ok": True}
                    elif cmd == "decide":
                        t0 = time.monotonic()
                        acts = policy.decide(split_images(header["frames"], payload))
                        dec.write(json.dumps({"task": policy.task, "episode": policy.episode, **policy.last,
                                              "seconds": round(time.monotonic() - t0, 3), "actions": acts}) + "\n")
                        dec.flush()
                        reply = {"ok": True, "actions": acts}
                    elif cmd == "close":
                        conn.send_bytes(pack({"ok": True}))
                        print(f"[robomme-policy] {time.strftime('%F %T')} close", flush=True)
                        return 0
                    else:
                        reply = {"ok": False, "error": f"unknown cmd {cmd!r}"}
                except Exception as e:                                      # noqa: BLE001 (reported to the client)
                    import traceback
                    traceback.print_exc()
                    reply = {"ok": False, "error": f"{type(e).__name__}: {e}"[:500]}
                conn.send_bytes(pack(reply))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--root", default="/workspace/FastWAM-memory2/outputs/robomme/dense_robomme_v1")
    ap.add_argument("--socket", required=True)
    ap.add_argument("--key-file", required=True)
    ap.add_argument("--execute", type=int, default=8)
    ap.add_argument("--steps", type=int, default=0)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    policy = RoboMMEPolicy(a.checkpoint, a.root, "cuda", a.steps, a.execute)
    print(f"[robomme-policy] {a.checkpoint}: history {policy.rule.variant}, action dim {policy.action_dim}, "
          f"steps {policy.steps}, execute {policy.execute}, norm {policy.norm.sha[:16]}", flush=True)
    return serve(policy, a.socket, Path(a.key_file).read_bytes().strip(), Path(a.log))


if __name__ == "__main__":
    raise SystemExit(main())
