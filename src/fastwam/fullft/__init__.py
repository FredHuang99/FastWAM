"""Full fine-tuning of FastWAM on RMBench with history as context frames (plan v10 A.3, route R2').

The released FastWAM (Wan2.2-TI2V-5B video expert + 1B action expert, RoboTwin weights) trained the official way:
video AND action experts trainable, video + action flow-matching losses, lr ~1e-4, every frame an anchor. History
frames are prefilled alone (like a current frame), their per-layer K/V are re-rotated to a negative temporal index
and appended to the joint attention of every layer behind a per-layer, per-head gate that is exactly 0 at start, so
the start equals the released model. The variants differ only in WHICH past frames are shown and HOW they are
indexed (history.py): none / ar / event / tw / clk / prop.

Modules: config (dataclasses + YAML), history (frame selection, pure Python, shared with the online path),
events (proprioceptive event detector, shared), data (dense-cache reader), model (FullModel), train (CLI).
"""
