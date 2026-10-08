"""RMBench policy API. Capture slots are indexed by completed target commands."""
from __future__ import annotations

from collections import deque
from multiprocessing.connection import Client
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image


class RPCPolicy:
    def __init__(self, config):
        self.config = config
        self.socket = config["memory_socket"]
        self.key = bytes.fromhex(os.environ["MEMORY_S1_RPC_KEY"])
        self.reset()

    def call(self, request):
        with Client(self.socket, family="AF_UNIX", authkey=self.key) as connection:
            connection.send(request)
            result = connection.recv()
        if not result["ok"]:
            raise RuntimeError(result["error"])
        return result

    def reset(self):
        self.actions = deque()
        self.pending = []
        self.frame_id = 0
        self.call({"command": "reset"})

    def capture(self, environment, observation):
        cameras = observation["observation"]
        images = [np.ascontiguousarray(cameras[name]["rgb"], dtype=np.uint8) for name in ("head_camera", "left_camera", "right_camera")]
        state = np.asarray(observation["joint_action"]["vector"], dtype=np.float32)
        if state.shape != (14,):
            raise ValueError(f"Aloha state shape is {state.shape}; expected 14.")
        if self.config.get("memory_record_frames"):
            directory = Path(self.config["memory_output"]) / "frames" / str(environment._memory_seed)
            directory.mkdir(parents=True, exist_ok=True)
            Image.fromarray(images[0]).save(directory / f"head_{self.frame_id:06d}.png")
        return {"frame_id": self.frame_id, "images": [image.tobytes() for image in images],
                "shapes": [list(image.shape) for image in images], "proprio": state.tolist()}

    def execute(self, environment, observation):
        if self.frame_id % 8 == 0:
            self.pending.append(self.capture(environment, observation))
        if not self.actions:
            if self.frame_id % 16:
                raise RuntimeError("Chunk was exhausted outside a 16-target decision boundary.")
            started = time.monotonic()
            result = self.call({"command": "decide", "current_id": self.frame_id, "observations": self.pending,
                                "task": self.config["task_name"], "episode_seed": environment._memory_seed,
                                "instruction": environment.get_instruction()})
            self.pending = []
            actions = np.asarray(result["actions"], dtype=np.float32)
            if actions.shape != (32, 14):
                raise ValueError("Model must return 32x14 action targets.")
            self.actions.extend(actions[:16])
            print(f"[decision] frame={self.frame_id} RPC+inference={time.monotonic()-started:.3f}s", flush=True)
        environment.take_action(self.actions.popleft(), action_type="qpos")
        self.frame_id += 1


def get_model(config):
    return RPCPolicy(config)


def reset_model(model):
    model.reset()


def eval(TASK_ENV, model, observation):
    model.execute(TASK_ENV, observation)
