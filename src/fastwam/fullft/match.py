"""Plan v20 card 7 (obs_match, 11-24, Opus): the MATCH FRAME, the matcher fixed by card 13a's probe (FS-P1 v2, 11-24
18:52: dinov2 crop 40/50 >= 35 -> card 7 with it). ONE function for both sides, so the training cache
(scripts/fullft/match_build.py) and the closed loop (online.FullSession, history.zoom_match) see the same pixels:
  match_image(head0, rule) -> uint8 image of the head camera's size: frame 0's table crop (zoom_cur_box, resized back
  as zoom.crop_resize) with every candidate object brightened by its similarity to the reference (zoom_ref_box):
  factor 0.25 everywhere, 0.25 + 0.75 * w_k inside candidate k's box (w_k = the candidates' scores scaled to [0, 1],
  the best = 1). It then replaces the reference zoom frame (zoom.ZOOM_REF) and goes through the mosaic and the VAE.
Candidates and scores exactly as match_probe.py v2 (its settings are copied, not re-tuned): colour regions of frame 0's
table box (distance > 40 to the box's median colour, >= 12 px, centre inside the projected candidate area), regions
closer than 6 px merged, the 5 largest kept; score = cosine of DINOv2 CLS embeddings of the reference box and of each
candidate box (margin 30 %, 224 x 224). The encoder: facebook/dinov2-base at the revision and file sha256 of the probe
(a frozen public self-supervised encoder, user 11-24; transformers' native Dinov2Model from safetensors, no remote code;
a different file is an error). No parameter is trained on our data; no annotation; no language model.
"""
from __future__ import annotations

import hashlib
import math
import os
from pathlib import Path
from typing import List, Optional, Sequence

import numpy as np

MODEL = "facebook/dinov2-base"
REVISION = "f9e44c814b77203eaa57a6bdbbd535f21ede1415"
SHA256 = "d73036b56966966d07975d696bde331762f37297e2f095de8cea0040c3aa0841"
RMBENCH = Path(os.environ.get("MWAM_RMBENCH", "/workspace/FastWAM/resources/RMBench"))
CAND_3D = ((-0.40, 0.40), (-0.30, -0.05), (0.741, 0.80))
FG, MIN_AREA, MERGE_PX, KEEP, MARGIN = 40.0, 12, 6, 5, 0.3
LOW, HIGH = 0.25, 0.75


def head_camera(rmbench: Path = RMBENCH):
    """(position, forward, left, fovy_deg, w, h) of the head camera (as scripts/fullft/zoom_tools.head_camera)."""
    import yaml
    task = yaml.safe_load((rmbench / "env_cfg/task_config/demo_clean.yml").read_text())
    spec = yaml.safe_load((rmbench / "env_cfg/task_config/_camera_config.yml").read_text())[task["camera"]["head_camera_type"]]
    for cfg in sorted((rmbench / "assets/embodiments").glob("*/config.yml")):
        value = yaml.safe_load(cfg.read_text()) or {}
        for cam in value.get("static_camera_list") or []:
            if cam.get("name") == "head_camera":
                pos = [float(x) for x in cam["position"]]
                fwd = [float(x) for x in (cam.get("forward") or [-x for x in pos])]
                left = [float(x) for x in (cam.get("left") or [-fwd[1], fwd[0], 0.0])]
                return pos, fwd, left, float(spec["fovy"]), int(spec["w"]), int(spec["h"])
    raise FileNotFoundError(f"no head_camera in {rmbench}/assets/embodiments/*/config.yml")


def project(point, cam):
    pos, fwd, left, fovy, w, h = (np.asarray(cam[0], float), np.asarray(cam[1], float), np.asarray(cam[2], float),
                                  cam[3], cam[4], cam[5])
    fwd, left = fwd / np.linalg.norm(fwd), left / np.linalg.norm(left)
    up = np.cross(fwd, left)
    f = (h / 2.0) / math.tan(math.radians(fovy) / 2.0)
    d = np.asarray(point, float) - pos
    depth = float(fwd @ d)
    return (w / 2.0 - f * float(left @ d) / depth) / w, (h / 2.0 - f * float(up @ d) / depth) / h


_AREA: Optional[List[float]] = None


def candidate_area() -> List[float]:
    global _AREA
    if _AREA is None:
        cam = head_camera()
        c = [project((x, y, z), cam) for x in CAND_3D[0] for y in CAND_3D[1] for z in CAND_3D[2]]
        _AREA = [min(p[0] for p in c), min(p[1] for p in c), max(p[0] for p in c), max(p[1] for p in c)]
    return _AREA


def _label(mask):
    from scipy import ndimage
    return ndimage.label(mask)


def candidates(img: np.ndarray, cur_box: Sequence[float], area_box: Optional[Sequence[float]]) -> List[dict]:
    """match_probe.candidates + merge_close + keep, v2 settings."""
    h, w = img.shape[:2]
    x0, y0, x1, y1 = int(cur_box[0] * w), int(cur_box[1] * h), int(cur_box[2] * w), int(cur_box[3] * h)
    crop = img[y0:y1, x0:x1].astype(np.float32)
    table = np.median(crop.reshape(-1, 3), axis=0)
    lab, n = _label(np.linalg.norm(crop - table, axis=2) > FG)
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < MIN_AREA:
            continue
        cx, cy = (xs.mean() + x0) / w, (ys.mean() + y0) / h
        if area_box and not (area_box[0] <= cx <= area_box[2] and area_box[1] <= cy <= area_box[3]):
            continue
        out.append({"bbox": [int(xs.min() + x0), int(ys.min() + y0), int(xs.max() + x0 + 1), int(ys.max() + y0 + 1)],
                    "ys": ys + y0, "xs": xs + x0})
    changed = True
    while changed:
        changed = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                a, b = out[i]["bbox"], out[j]["bbox"]
                if max(a[0] - b[2], b[0] - a[2], a[1] - b[3], b[1] - a[3], 0) <= MERGE_PX:
                    ys = np.concatenate([out[i]["ys"], out[j]["ys"]])
                    xs = np.concatenate([out[i]["xs"], out[j]["xs"]])
                    out[i] = {"bbox": [int(xs.min()), int(ys.min()), int(xs.max() + 1), int(ys.max() + 1)], "ys": ys, "xs": xs}
                    del out[j]
                    changed = True
                    break
            if changed:
                break
    out = sorted(out, key=lambda c: -len(c["ys"]))[:KEEP]
    out.sort(key=lambda c: (c["xs"].mean(), c["ys"].mean()))
    return [{"bbox": c["bbox"], "area": int(len(c["ys"]))} for c in out]


def crop_box(img: np.ndarray, bbox, margin: float = MARGIN) -> np.ndarray:
    h, w = img.shape[:2]
    x0, y0, x1, y1 = bbox
    mx, my = (x1 - x0) * margin, (y1 - y0) * margin
    return img[max(0, int(y0 - my)): min(h, int(y1 + my)), max(0, int(x0 - mx)): min(w, int(x1 + mx))]


class Scorer:
    """The frozen encoder, pinned (revision + file sha256); loaded once per process."""
    _inst = None

    def __init__(self, device: str = "cuda:0"):
        import torch
        from huggingface_hub import hf_hub_download
        from transformers import Dinov2Model
        path = hf_hub_download(MODEL, "model.safetensors", revision=REVISION)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(1 << 24), b""):
                h.update(block)
        if h.hexdigest() != SHA256:
            raise ValueError(f"{MODEL}@{REVISION} model.safetensors sha256 {h.hexdigest()} != the probe's {SHA256}")
        self.torch, self.device = torch, device
        self.model = Dinov2Model.from_pretrained(MODEL, revision=REVISION, use_safetensors=True,
                                                 trust_remote_code=False).to(device).eval()
        self.mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)

    @classmethod
    def get(cls, device: str = "cuda:0") -> "Scorer":
        if cls._inst is None:
            cls._inst = cls(device)
        return cls._inst

    def cls(self, img: np.ndarray):
        t = self.torch.from_numpy(np.ascontiguousarray(img)).float().permute(2, 0, 1)[None].to(self.device) / 255.0
        t = self.torch.nn.functional.interpolate(t, size=(224, 224), mode="bilinear", align_corners=False)
        with self.torch.no_grad():
            return self.model(pixel_values=(t - self.mean) / self.std).last_hidden_state[0, 0]


def scores(head0: np.ndarray, ref_box, cands: List[dict], scorer: Scorer) -> List[float]:
    h, w = head0.shape[:2]
    r = head0[int(ref_box[1] * h):int(ref_box[3] * h), int(ref_box[0] * w):int(ref_box[2] * w)]
    rc = scorer.cls(r)
    return [float(scorer.torch.nn.functional.cosine_similarity(rc, scorer.cls(crop_box(head0, c["bbox"])), dim=0))
            for c in cands]


def overlay(head0: np.ndarray, cur_box, cands: List[dict], s: Sequence[float]) -> np.ndarray:
    """The table crop (zoom.crop_resize, same pixels as the plain current zoom) times the brightness map."""
    from .zoom import crop_resize, pixel_box
    h, w = head0.shape[:2]
    factor = np.full((h, w), LOW, np.float32)
    if cands:
        lo, hi = min(s), max(s)
        wts = [1.0 if hi - lo < 1e-9 else (v - lo) / (hi - lo) for v in s]
        for c, wk in zip(cands, wts):
            x0, y0, x1, y1 = c["bbox"]
            factor[max(0, y0 - 2):min(h, y1 + 2), max(0, x0 - 2):min(w, x1 + 2)] = LOW + HIGH * wk
    left, top, right, bottom = pixel_box(cur_box, w, h)
    from PIL import Image
    fmap = np.asarray(Image.fromarray(factor[top:bottom, left:right]).resize((w, h), Image.Resampling.BILINEAR))
    base = crop_resize(head0, cur_box).astype(np.float32)
    return np.clip(np.rint(base * fmap[..., None]), 0, 255).astype(np.uint8)


def match_image(head0: np.ndarray, ref_box, cur_box, scorer: Optional[Scorer] = None, area_box=None):
    """-> (uint8 image of head0's size, meta {candidates, scores})."""
    if head0.dtype != np.uint8 or head0.ndim != 3 or head0.shape[-1] != 3:
        raise ValueError(f"match_image expects uint8 HWC RGB, got {head0.dtype} {head0.shape}")
    area_box = candidate_area() if area_box is None else area_box
    cands = candidates(head0, cur_box, area_box)
    scorer = scorer or Scorer.get()
    s = scores(head0, ref_box, cands, scorer) if cands else []
    return overlay(head0, cur_box, cands, s), {"candidates": cands, "scores": [round(v, 5) for v in s]}
