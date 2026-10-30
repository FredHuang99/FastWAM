"""Pause queue5 lanes to free their GPUs for other users, keeping everything needed to resume them later.

    PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/queue5_pause.py loop gpu0

For every lane named:
  1. the lane process is stopped first (SIGTERM, then SIGKILL), so nobody judges the interrupted task;
  2. the task it was running is stopped: its process group gets SIGINT (the closed loop stops its simulators; every
     finished episode stays on disk) -> SIGTERM -> SIGKILL, then leftover simulator workers of its output folder, then
     any python process still started with CUDA_VISIBLE_DEVICES=<lane GPU>;
  3. the task state stays 'running' under the dead lane pid: a lane started again with queue5_restart.sh puts it back to
     pending and re-runs it, skipping finished episodes (training resumes from LATEST.json). No verdict, no ledger line;
  4. outputs/memory_v2/queue5/paused/<lane>.json records the lane, GPU (index, UUID), task, finished episodes and the
     resume command.
A lane whose running task is a training run is refused without --allow-train (updates since the last checkpoint are
lost). Exit 1 if a lane GPU still holds memory afterwards. Log: outputs/memory_v2/queue5/paused/pause_<time>.log
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import queue5 as q  # noqa: E402

P = q.Q / "paused"
P.mkdir(parents=True, exist_ok=True)
LOG = P / f"pause_{time.strftime('%Y%m%d_%H%M%S')}.log"
RESTART = "/workspace/FastWAM-memory2/scripts/memory_v2/jobs/queue5_restart.sh"


def say(msg):
    line = f"[pause] {q.now_bj()} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def proc_table():
    """{pid: (state, pgrp)} of every process visible here."""
    out = {}
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                fields = (d / "stat").read_text().rsplit(")", 1)[1].split()
                out[int(d.name)] = (fields[0], int(fields[2]))
            except (OSError, IndexError, ValueError):
                pass
    return out


def group_alive(pgid):
    return any(st != "Z" and pg == pgid for st, pg in proc_table().values())


def cmdline(pid):
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace").strip()
    except OSError:
        return ""


def gpus():
    """{container index: (uuid, used MiB)}."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=index,uuid,memory.used", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError) as error:
        say(f"nvidia-smi failed: {error!r}")
        out = ""
    table = {}
    for line in out.strip().splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) == 3 and parts[0].isdigit():
            table[int(parts[0])] = (parts[1], int(parts[2]) if parts[2].isdigit() else -1)
    return table


def gpu_processes(gpu):
    """Python processes started with CUDA_VISIBLE_DEVICES=<gpu> (lane jobs inherit it), except this one."""
    found = []
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) == os.getpid():
            continue
        try:
            env = (d / "environ").read_bytes().split(b"\0")
        except OSError:
            continue
        if f"CUDA_VISIBLE_DEVICES={gpu}".encode() in env and "python" in cmdline(d.name):
            found.append(int(d.name))
    return found


def stop_lane(lane):
    info = q.read_json(q.Q / "lanes" / f"{lane}.json", {})
    pid = info.get("pid")
    if q.pid_alive(pid, f"queue5.py run --lane {lane}"):
        os.kill(int(pid), signal.SIGTERM)
        for _ in range(30):
            if not q.pid_alive(pid):
                break
            time.sleep(1)
        if q.pid_alive(pid):
            os.kill(int(pid), signal.SIGKILL)
            time.sleep(2)
        say(f"lane {lane}: lane process {pid} stopped" + (" (STILL ALIVE)" if q.pid_alive(pid) else ""))
    else:
        say(f"lane {lane}: lane process {pid} was not running")
    return info


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lanes", nargs="+")
    ap.add_argument("--allow-train", action="store_true")
    args = ap.parse_args()
    say(f"pausing lanes {args.lanes}; log {LOG}")

    # what each lane is doing now
    tasks = q.load_tasks()
    plan = {}
    for lane in args.lanes:
        info = q.read_json(q.Q / "lanes" / f"{lane}.json", {})
        if info.get("gpu") is None:
            raise SystemExit(f"lane {lane}: no GPU recorded in {q.Q / 'lanes' / (lane + '.json')}; nothing paused")
        current = [(t, q.state(t["id"])) for t in tasks
                   if t.get("lane") == lane and q.state(t["id"])["status"] in ("running", "waiting")]
        for t, s in current:
            if s["status"] == "running" and t["kind"] == "train" and not args.allow_train:
                raise SystemExit(f"lane {lane} runs training {t['id']}: refused (use --allow-train); nothing paused")
        plan[lane] = (info, current)

    # 1. lane processes first: an interrupted task must not be judged
    for lane in args.lanes:
        stop_lane(lane)

    # 2. the tasks: SIGINT to every process group, then escalate
    children = {}
    for lane, (_info, current) in plan.items():
        for t, s in current:
            child = s.get("child_pid")
            try:
                leader = bool(child) and q.pid_alive(child) and os.getsid(int(child)) == int(child)
            except OSError:
                leader = False
            expect = (str(q.resolve(q.effective(t)["output"])) if t["kind"] == "closed_loop" else
                      "fastwam" if t["kind"] in ("train", "eval") else "")
            if s["status"] == "running" and leader and expect not in cmdline(child):
                say(f"lane {lane}: task {t['id']} child {child} is not the task (pid reused?): {cmdline(child)[:160]}")
                leader = False
            if s["status"] == "running" and leader:
                children[int(child)] = (lane, t)
                say(f"lane {lane}: task {t['id']} process group {child}: {cmdline(child)[:200]}")
            else:
                say(f"lane {lane}: task {t['id']} ({s['status']}) has no live process")
    for sig, wait in ((signal.SIGINT, 120), (signal.SIGTERM, 60), (signal.SIGKILL, 30)):
        live = [c for c in children if group_alive(c)]
        if not live:
            break
        for c in live:
            try:
                os.killpg(c, sig)
            except ProcessLookupError:
                pass
        say(f"{signal.Signals(sig).name} -> process groups {live}; waiting up to {wait}s")
        end = time.time() + wait
        while time.time() < end and any(group_alive(c) for c in live):
            time.sleep(2)
    for c, (lane, t) in children.items():
        say(f"lane {lane}: task {t['id']} process group {c} " + ("STILL ALIVE" if group_alive(c) else "ended"))

    # 3. leftovers: simulator workers (own sessions) and anything else started on the lane GPU
    for lane, (info, current) in plan.items():
        for t, _s in current:
            if t["kind"] == "closed_loop":
                q.kill_sim_workers(q.resolve(q.effective(t)["output"]))
        rest = gpu_processes(info["gpu"])
        for pid in rest:
            say(f"lane {lane}: leftover on GPU {info['gpu']}: pid {pid} {cmdline(pid)[:160]} -> SIGKILL")
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
    time.sleep(10)

    # 4. records + check
    table, bad = gpus(), []
    for lane, (info, current) in plan.items():
        gpu = info["gpu"]
        uuid, used = table.get(gpu, ("?", -1))
        rows = []
        for t, s in current:
            done = None
            if t["kind"] == "closed_loop":
                done = len(list(q.resolve(q.effective(t)["output"]).glob("*/*/*/seed_*/result.json")))
            q.set_state(t["id"], paused_at=q.now_bj())
            rows.append({"task": t["id"], "status_before": s["status"], "child_pid": s.get("child_pid"),
                         "finished_episodes": done})
            say(f"lane {lane}: task {t['id']} paused ({s['status']}); finished episodes on disk: {done}")
        q.write_json(P / f"{lane}.json", {"lane": lane, "gpu": gpu, "uuid": uuid, "paused_at": q.now_bj(),
                                         "lane_pid": info.get("pid"), "tasks": rows,
                                         "resume": f"bash {RESTART} {lane}:{gpu}"})
        say(f"lane {lane}: container GPU {gpu} ({uuid}) memory used now {used} MiB")
        if used > 1000:
            bad.append(lane)
    lanes = " ".join(f"{lane}:{plan[lane][0]['gpu']}" for lane in args.lanes)
    say(f"resume later (inside the container): bash {RESTART} {lanes}")
    if bad:
        say(f"WARNING: GPU of lanes {bad} still holds memory: check nvidia-smi before releasing it")
        sys.exit(1)
    say("done: lanes paused, their GPUs are empty")


if __name__ == "__main__":
    main()
