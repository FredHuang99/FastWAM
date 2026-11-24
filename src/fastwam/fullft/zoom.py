"""Plan v19 3.3 (A3, observe_and_pickup, 11-22): the two zoom history frames. ONE function builds the zoomed camera
images for both sides, so the training cache (scripts/fullft/build_zoom.py) and the closed loop (online.FullSession)
see the same pixels:
  zoom_images(images, box, camera) -> the three camera images with camera `camera` (0 = head) replaced by its crop to
  `box` (normalised x0, y0, x1, y1), resized back to that camera's own size (PIL bilinear, the resampling the
  mosaic uses); the other two cameras unchanged. The result then goes through the usual mosaic and the single-frame VAE
  encoder, like any frame.
Cache files: <data.zoom_root>/<episode id with '/' -> '_'>.pt = {"ref": [48, 1, 24, 20] (frame 0, zoom_ref_box),
"cur": [L, 48, 1, 24, 20] (every frame, zoom_cur_box), "tag": box_tag(rule), "episode_id", "length"}; the tag ties a
file to the boxes it was built with (a model whose boxes differ refuses the file).
Online cache keys (FrameCache / encoded): ZOOM_REF for the reference crop (kept all episode), cur_key(t) for the
current crop at decision t (dropped with the decision's other frames).
"""
from __future__ import annotations

import hashlib
import json
from typing import List, Sequence

import numpy as np

ZOOM_REF = -1


def cur_key(current: int) -> int:
    """Online key of the current-frame zoom at decision `current` (negative: never a frame id)."""
    return -(int(current) + 2)


def box_tag(rule) -> str:
    """8 hex chars naming the zoom boxes and camera (cache files carry it; a mismatch is an error)."""
    spec = {"ref": [round(float(x), 6) for x in rule.zoom_ref_box], "cur": [round(float(x), 6) for x in rule.zoom_cur_box],
            "camera": int(rule.zoom_camera)}
    if getattr(rule, "zoom_match", False):            # 11-24 card 7: a match-frame cache never passes for a plain one
        spec["match"] = "dinov2-crop-v2"
    return hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:8]


def pixel_box(box: Sequence[float], width: int, height: int):
    """Normalised (x0, y0, x1, y1) -> integer pixel box (left, top, right, bottom), at least one pixel wide / high."""
    x0, y0, x1, y1 = (float(v) for v in box)
    left, top = int(np.floor(x0 * width)), int(np.floor(y0 * height))
    right, bottom = int(np.ceil(x1 * width)), int(np.ceil(y1 * height))
    left, top = min(max(left, 0), width - 1), min(max(top, 0), height - 1)
    right, bottom = max(min(right, width), left + 1), max(min(bottom, height), top + 1)
    return left, top, right, bottom


def crop_resize(rgb: np.ndarray, box: Sequence[float]) -> np.ndarray:
    """uint8 HWC image -> its crop to the normalised box, resized back to H x W (PIL bilinear)."""
    from PIL import Image
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[-1] != 3:
        raise ValueError(f"zoom expects uint8 HWC RGB, got {rgb.dtype} {rgb.shape}")
    h, w = rgb.shape[:2]
    left, top, right, bottom = pixel_box(box, w, h)
    crop = Image.fromarray(np.ascontiguousarray(rgb[top:bottom, left:right]))
    return np.asarray(crop.resize((w, h), Image.Resampling.BILINEAR))


def zoom_images(images: Sequence[np.ndarray], box: Sequence[float], camera: int = 0) -> List[np.ndarray]:
    """The three camera images with camera `camera` replaced by its zoom (the others unchanged, not copied)."""
    out = list(images)
    out[int(camera)] = crop_resize(np.asarray(out[int(camera)]), box)
    return out
