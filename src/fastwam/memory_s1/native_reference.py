"""Call the original FastWAM methods while sharing already loaded frozen weights."""
from __future__ import annotations

import torch

from .protocol import format_task_prompt


def build_reference(backbone, encoders):
    from fastwam.models.wan22.fastwam import FastWAM
    vae, text, tokenizer = encoders
    device = next(backbone.parameters()).device
    reference = FastWAM(
        video_expert=backbone.mot.mixtures["video"],
        action_expert=backbone.mot.mixtures["action"], mot=backbone.mot,
        vae=vae, text_encoder=text, tokenizer=tokenizer, text_dim=4096,
        proprio_dim=None, device=str(device), torch_dtype=torch.bfloat16,
        action_train_shift=1.0, action_infer_shift=1.0)
    reference.proprio_dim = 14
    reference.proprio_encoder = backbone.proprio_encoder
    return reference.eval().requires_grad_(False)


@torch.no_grad()
def native_actions(reference, mosaic, proprio, seed, instruction=None, context=None):
    kwargs = {"prompt": format_task_prompt(instruction)} if context is None else {
        "prompt": None, "context": context,
        "context_mask": torch.ones(context.shape[:2], device=context.device, dtype=torch.bool)}
    return reference.infer_action(
        input_image=mosaic, proprio=proprio, action_horizon=32,
        num_inference_steps=10, sigma_shift=1.0, seed=seed, rand_device="cpu",
        tiled=False, compile_action_infer=False, **kwargs)["action"].to(reference.device)
