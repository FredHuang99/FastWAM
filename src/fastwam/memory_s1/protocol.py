"""Lightweight released prompt and sampling contracts; no dataset imports."""
from __future__ import annotations

import ast
from pathlib import Path

TASK_PROMPT = "A video recorded from a robot's point of view executing the following instruction: {task}"
PROMPT_VERSION = "released_robot_video_task_wrapper_v2"
SAMPLER_VERSION = "released_bf16_euler_v2"


def format_task_prompt(instruction):
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("A nonempty whole-task instruction is required.")
    prefix = TASK_PROMPT.partition("{task}")[0]
    return instruction if instruction.startswith(prefix) else TASK_PROMPT.format(task=instruction)


def prompt_contract():
    return {"version": PROMPT_VERSION, "template": TASK_PROMPT, "add_special_tokens": True}


def precision_contract():
    return {"version": "released_explicit_bf16_precision_v3",
            "frozen_weights_dtype": "bfloat16", "vae_autocast": False,
            "text_autocast": False, "video_autocast": False, "action_autocast": False,
            "action_timestep_dtype": "bfloat16", "memory_autocast": "bfloat16"}


def inference_contract():
    return {"prompt": prompt_contract(), "sampler": SAMPLER_VERSION,
            "steps": 10, "shift": 1.0, "noise": "cpu_fp32_then_bf16",
            "action_state_dtype": "bfloat16", "predict": 32, "execute": 16,
            "precision": precision_contract()}


def verify_released_prompt(root):
    path = Path(root) / "src/fastwam/datasets/lerobot/robot_video_dataset.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "DEFAULT_PROMPT" for t in node.targets):
            if ast.literal_eval(node.value) != TASK_PROMPT:
                raise ValueError("Released DEFAULT_PROMPT changed; update the memory encoding contract explicitly.")
            return
    raise ValueError(f"Cannot find the released DEFAULT_PROMPT in {path}.")
