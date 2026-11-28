"""RoboMME closed loop, simulator side (plan v22 6.6 step 4), 11-28 17:29 Opus. Runs ONLY inside RoboMME's own image
(robomme:582ab30; numpy + robomme, no fastwam import): `uv run --no-sync python /mwam/robomme_client.py ...`.
The policy (src/fastwam/fullft/robomme_policy.py, in mwam5090) listens on an AF_UNIX socket in a folder both containers
mount; messages = 4-byte header length + JSON header + raw uint8 images (the framing is copied here, not imported).
Per test episode k (RoboMME's own builder: BenchmarkEnvBuilder(task, dataset, action_space="ee_pose", max_steps), the
episode's environment seed fixed in its metadata):
  reset -> goal = info["task_goal"][0] (the string the training demos carry: robomme_convert.py reads task_goal[0]);
  the current frame = the last element of each *_list observation (earlier ones are video-demo frames, skipped as in
  the conversion); frame 0 = that frame;
  loop: send every frame since the last decision (front / wrist uint8, eef_state 6, gripper_state 2) -> receive
  `execute` absolute ee_pose actions -> env.step each; stop at info["status"] == "error" (e.g. an IK failure), or
  terminated / truncated (outcome = info["status"]; success = "success"), or --max-steps executed actions.
Writes <out>/episodes.jsonl (task, episode, goal, success, status, steps, seconds, error) and <out>/SUMMARY.json.
  python robomme_client.py --socket /cl/rpc.sock --key-file /cl/rpc.key --task PickXtimes --episodes 0 1 --out /cl
"""
from __future__ import annotations

import argparse
import json
import struct
import time
from pathlib import Path

import numpy as np


def pack(header: dict, payload: bytes = b"") -> bytes:
    h = json.dumps(header).encode()
    return struct.pack(">I", len(h)) + h + payload


def unpack(message: bytes):
    (n,) = struct.unpack(">I", message[:4])
    return json.loads(message[4:4 + n].decode()), message[4 + n:]


def last(x):
    """The current element of a RoboMME *_list observation value (a list / array of per-substep values)."""
    if isinstance(x, (list, tuple)):
        return x[-1]
    a = np.asarray(x)
    return a


def frame_of(obs: dict, k: int) -> tuple:
    front = np.ascontiguousarray(np.asarray(last(obs["front_rgb_list"]), dtype=np.uint8))
    wrist = np.ascontiguousarray(np.asarray(last(obs["wrist_rgb_list"]), dtype=np.uint8))
    eef = np.asarray(last(obs["eef_state_list"]), dtype=np.float64).reshape(-1)[:6]
    grip = np.asarray(last(obs["gripper_state_list"]), dtype=np.float64).reshape(-1)[:2]
    if front.shape != wrist.shape or front.ndim != 3:
        raise ValueError(f"front {front.shape} / wrist {wrist.shape}")
    return {"frame": k, "eef": eef.tolist(), "grip": grip.tolist(), "shape": list(front.shape)}, front, wrist


class Remote:
    def __init__(self, conn):
        self.conn = conn

    def call(self, header: dict, payload: bytes = b"") -> dict:
        self.conn.send_bytes(pack(header, payload))
        reply, _ = unpack(self.conn.recv_bytes())
        if not reply.get("ok"):
            raise RuntimeError(f"policy error: {reply.get('error')}")
        return reply

    def decide(self, pending):
        payload = b"".join(front.tobytes() + wrist.tobytes() for _, front, wrist in pending)
        return self.call({"cmd": "decide", "frames": [f for f, _, _ in pending]}, payload)["actions"]


def run_episode(env, remote: Remote, task: str, episode: int, max_steps: int) -> dict:
    t0 = time.monotonic()
    obs, info = env.reset()
    goal = info["task_goal"][0] if isinstance(info.get("task_goal"), (list, tuple)) else str(info.get("task_goal"))
    remote.call({"cmd": "reset", "task": task, "episode": int(episode), "goal": goal})
    pending, k, steps = [frame_of(obs, 0)], 0, 0
    status, error = "max_steps", ""
    while steps < max_steps:
        actions = remote.decide(pending)
        pending = []
        done = False
        for a in actions:
            obs, reward, terminated, truncated, info = env.step(np.asarray(a, dtype=np.float32))
            steps += 1
            if info is not None and info.get("status") == "error":
                status, error, done = "error", str(info.get("error_message", ""))[:300], True
                break
            if bool(terminated) or bool(truncated):
                status, done = str(info.get("status", "unknown")), True
                break
            k += 1
            pending.append(frame_of(obs, k))
            if steps >= max_steps:
                break
        if done:
            break
    return {"task": task, "episode": int(episode), "goal": goal, "success": status == "success", "status": status,
            "steps": steps, "seconds": round(time.monotonic() - t0, 1), "error": error}


def main():
    from multiprocessing.connection import Client
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--socket", required=True)
    ap.add_argument("--key-file", required=True)
    ap.add_argument("--task", default="PickXtimes")
    ap.add_argument("--dataset", default="test")
    ap.add_argument("--episodes", type=int, nargs="*", default=None, help="default: every episode of the split")
    ap.add_argument("--max-steps", type=int, default=1300, help="RoboMME's MME-VLA setting")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from robomme.env_record_wrapper import BenchmarkEnvBuilder
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    builder = BenchmarkEnvBuilder(env_id=a.task, dataset=a.dataset, action_space="ee_pose", max_steps=a.max_steps)
    episodes = a.episodes if a.episodes else list(range(builder.get_episode_num()))
    key = Path(a.key_file).read_bytes().strip()
    rows = []
    with Client(a.socket, family="AF_UNIX", authkey=key) as conn:
        remote = Remote(conn)
        try:
            for ep in episodes:
                env = builder.make_env_for_episode(ep)
                try:
                    row = run_episode(env, remote, a.task, ep, a.max_steps)
                finally:
                    env.close()
                rows.append(row)
                with (out / "episodes.jsonl").open("a") as f:
                    f.write(json.dumps(row) + "\n")
                print(f"[robomme-client] {time.strftime('%F %T')} {a.task} episode {ep}: {row['status']} "
                      f"after {row['steps']} steps ({row['seconds']} s){' ' + row['error'] if row['error'] else ''}",
                      flush=True)
        finally:
            remote.call({"cmd": "close"})
    summary = {"task": a.task, "dataset": a.dataset, "episodes": len(rows), "success": sum(r["success"] for r in rows),
               "errors": sum(r["status"] == "error" for r in rows), "max_steps": a.max_steps}
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[robomme-client] DONE {json.dumps(summary)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
