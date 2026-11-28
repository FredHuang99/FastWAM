"""11-28 RoboMME step 4: the policy server's framing and loop against the client's episode loop (fake policy, fake
environment, a real AF_UNIX socket), plus the normalisation round trip and the noise draws."""
import importlib.util
import json
import threading
from multiprocessing.connection import Client
from pathlib import Path

import numpy as np
import torch

from fastwam.fullft import robomme_policy as rp

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location("robomme_client", ROOT / "scripts/robomme/robomme_client.py")
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class FakePolicy:
    def __init__(self):
        self.calls, self.task, self.episode, self.last = [], "", -1, {}

    def reset(self, task, episode, goal):
        self.task, self.episode, self.goal, self.next = task, episode, goal, 0
        self.calls.append(("reset", goal))

    def decide(self, frames):
        got = [int(f["frame"]) for f, _, _ in frames]
        assert got == list(range(self.next, self.next + len(got)))
        self.next = got[-1] + 1
        f, front, wrist = frames[-1]
        assert front.shape == (8, 8, 3) and int(front[0, 0, 0]) == got[-1] % 256 and int(wrist[0, 0, 0]) == 255
        self.calls.append(("decide", got))
        self.last = {"frame": got[-1]}
        return [[0.1 * got[-1]] * 7 for _ in range(4)]


class FakeEnv:
    def __init__(self, end_at=10, status="success"):
        self.t, self.end_at, self.status, self.actions = 0, end_at, status, []

    def obs(self):
        img = np.full((8, 8, 3), self.t % 256, np.uint8)
        return {"front_rgb_list": [np.zeros_like(img), img], "wrist_rgb_list": [img, np.full_like(img, 255)],
                "eef_state_list": [np.arange(6.0) + self.t], "gripper_state_list": [np.array([0.04, 0.04])]}

    def reset(self):
        return self.obs(), {"task_goal": ["pick up the cube twice", "alt"]}

    def step(self, a):
        self.actions.append(np.asarray(a))
        self.t += 1
        done = self.t >= self.end_at
        return self.obs(), 0.0, done, False, ({"status": self.status} if done else {})


def test_loop_over_a_socket(tmp_path):
    sock, key = str(tmp_path / "rpc.sock"), b"k3y"
    pol = FakePolicy()
    th = threading.Thread(target=rp.serve, args=(pol, sock, key, tmp_path / "log"), daemon=True)
    th.start()
    for _ in range(100):
        if Path(sock).exists():
            break
        threading.Event().wait(0.05)
    with Client(sock, family="AF_UNIX", authkey=key) as conn:
        remote = client.Remote(conn)
        env = FakeEnv(end_at=10)
        row = client.run_episode(env, remote, "PickXtimes", 3, 1300)
        env2 = FakeEnv(end_at=50, status="fail")
        row2 = client.run_episode(env2, remote, "PickXtimes", 4, 6)
        remote.call({"cmd": "close"})
    th.join(5)
    assert row["success"] and row["steps"] == 10 and row["goal"] == "pick up the cube twice"
    assert row2["status"] == "max_steps" and row2["steps"] == 6
    decides = [c[1] for c in pol.calls if c[0] == "decide"]
    assert decides[:3] == [[0], [1, 2, 3, 4], [5, 6, 7, 8]]
    assert np.allclose(env.actions[0], 0.0) and np.allclose(env.actions[4], 0.4)
    lines = (tmp_path / "log" / "decisions.jsonl").read_text().splitlines()
    assert len(lines) == len(decides) and json.loads(lines[0])["episode"] == 3


def test_norm_round_trip_and_noise(tmp_path):
    st = {"stats": {"proprio": {"scale": [2.0] * 8, "offset": [-1.0] * 8},
                    "actions": {"scale": [4.0] * 7, "offset": [1.0] * 7}}, "sha256": "x"}
    (tmp_path / "NORM_STATS.json").write_text(json.dumps(st))
    n = rp.Norm(tmp_path / "NORM_STATS.json")
    raw = torch.tensor([0.3, -0.2, 0.1, 0.0, 0.5, -0.4, 0.9])
    y = raw * 4.0 + 1.0
    back = n.actions(y[None])[0]
    assert torch.allclose(back, raw)
    assert float(n.actions(torch.full((1, 7), 99.0))[0, 6]) == 1.0          # gripper clipped
    assert torch.equal(n.proprio(torch.full((8,), 0.5)), torch.zeros(8))
    a, b = rp.noise_for(3, 16, 7), rp.noise_for(3, 16, 7)
    assert a.shape == (1, 32, 7) and torch.equal(a, b) and not torch.equal(a, rp.noise_for(3, 24, 7))
    assert not torch.equal(a, rp.noise_for(3, 16, 7, "r2"))
