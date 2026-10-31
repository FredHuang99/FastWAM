"""pool5: run queue5 tasks on whichever allowed GPU is empty - no GPU guard, no fixed lane per GPU.

One dispatcher per machine pops the queue (queue5_tasks.yaml order, dependencies as in queue5) and starts each GPU task
on an allowed GPU that has been empty (memory.used < free_mib, any user) for free_seconds; one task per GPU. Every task
runs in its own `exec` process (own session), so the dispatcher can restart without touching running work.

    python scripts/memory_v2/pool5.py start [--lanes L,..] [--gpus G,..]   stop queue5 lane processes of those lanes
                                                            (jobs keep running, get adopted), start the dispatcher
    python scripts/memory_v2/pool5.py pool                  the dispatcher itself (log queue5/pool.log)
    python scripts/memory_v2/pool5.py status                one screen: GPUs, running tasks with progress + ETA, queue
    python scripts/memory_v2/pool5.py report [--hours 12]   everything needed for a check-in -> queue5/report/*.md
    python scripts/memory_v2/pool5.py pause --gpu G ...     stop our task(s) on GPU G, keep them for a re-run, and
                                                            remove G from the allowed GPUs (lend it to others)
    python scripts/memory_v2/pool5.py allow --gpus 0,1,2,3  set the allowed GPUs (read by the dispatcher every cycle)

Settings: outputs/memory_v2/queue5/POOL_CONFIG.json (created with defaults, re-read every cycle):
    gpus           allowed GPU indices as this container sees them
    lanes          the queue5 lanes the pool runs (tasks of other lanes are left to their lane processes)
    free_mib       a GPU counts as empty below this memory use (any process, any user)
    free_seconds   ... continuously for this long before a task is started on it
    max_attempts   failures (incl. stalls and non-graceful exits) before a task is judged as it is
    retry_minutes  wait before a failed task is tried again (any empty GPU)
    stall_minutes  no log / output written for this long -> the task is stopped and retried
What can happen to a task, and what the pool does:
    waiting       no empty allowed GPU / dependencies / retry wait     -> shown with the reason in `status`
    start failed  exec or the job exits non-zero at once (bad env)     -> retried, then judged ERROR with the log tail
    run failed    the job exits non-zero (OOM: someone took the GPU)   -> retried on any empty GPU (finished episodes
                                                                          and training checkpoints are reused)
    episode errs  closed loop ends with ERROR.json episodes            -> re-run (only those episodes), then judged
    stalled       nothing written for stall_minutes                    -> job stopped (TERM, KILL), retried
    died          exec process gone without a verdict (kill -9, crash,  -> job still alive: adopted and waited for;
                  container restart)                                      otherwise retried
    judged        finished (or attempts used up)                       -> verdict + autopsy + ledger, as in queue5
State: queue5/state/<id>.json (fields attempt, last_failure, failures, retry_after); dispatcher log queue5/pool.log;
per task: queue5/exec/<id>.log (pool side) and queue5/tasks/<id>.log (the job).
"""
import argparse
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import queue5 as q  # noqa: E402

CFG_PATH = q.Q / "POOL_CONFIG.json"
POOL = q.Q / "pool.json"
EXEC = q.Q / "exec"
REPORTS = q.Q / "report"
DEFAULTS = {"gpus": [], "lanes": ["loop", "train", "extra", "gpu0", "cpu"], "free_mib": 1000, "free_seconds": 180,
            "max_attempts": 3, "retry_minutes": 10, "stall_minutes": 120, "poll_seconds": 30}
SELF = str(Path(__file__).resolve())
FAIL_HINTS = [("CUDA out of memory", "GPU out of memory"), ("OutOfMemoryError", "GPU out of memory"),
              ("CUDA error", "CUDA error"), ("no kernel image", "CUDA kernels not built for this GPU"),
              ("Failed to initialize NVML", "NVML lost (restart the container)"), ("Killed", "killed (host OOM?)"),
              ("ModuleNotFoundError", "missing Python module"), ("FileNotFoundError", "missing file"),
              ("Traceback", "Python exception")]


def log(msg):
    print(f"[pool] {q.now_bj()} {msg}", flush=True)


def config():
    cfg = dict(DEFAULTS)
    cfg.update(q.read_json(CFG_PATH, {}) or {})
    if not CFG_PATH.exists():
        q.write_json(CFG_PATH, cfg)
    return cfg


def gpu_table():
    """{index: {"used": MiB, "total": MiB, "util": %}} as this container sees them."""
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return {}
    table = {}
    for line in out.strip().splitlines():
        p = [x.strip() for x in line.split(",")]
        if len(p) == 4 and p[0].isdigit():
            table[int(p[0])] = {"used": int(p[1]) if p[1].isdigit() else 10**6, "total": int(p[2]) if p[2].isdigit() else 0,
                                "util": int(p[3]) if p[3].isdigit() else 100}
    return table


def alive_exec(pid):
    return q.pid_alive(pid, "pool5.py exec")


def alive_lane(pid):
    return q.pid_alive(pid, "queue5.py run")


def group_alive(pgid):
    try:
        os.killpg(int(pgid), 0)
    except (OSError, TypeError, ValueError):
        return False
    return q.pid_alive(pgid)


def log_tail(path, n=40):
    try:
        return Path(path).read_text(errors="replace").splitlines()[-n:]
    except OSError:
        return []


def classify(lines):
    text = "\n".join(lines)
    for needle, why in FAIL_HINTS:
        if needle in text:
            return why
    return "non-zero exit"


def outputs(task):
    if task["kind"] == "closed_loop":
        return [q.resolve(q.effective(task)["output"])]
    if task["kind"] in ("train", "eval"):
        return [q.O / task["run"]]
    return []


def last_activity(task):
    """Newest mtime of the task log and its output (closed loop: episode folders; train: metrics / stdout)."""
    times = []
    for p in [q.Q / "tasks" / f"{task['id']}.log"]:
        if p.exists():
            times.append(p.stat().st_mtime)
    for out in outputs(task):
        if task["kind"] == "train":
            for name in ("metrics.jsonl", "stdout.log"):
                if (out / name).exists():
                    times.append((out / name).stat().st_mtime)
        elif out.exists():
            for d in out.glob("*/*/*/seed_*"):
                try:
                    times.append(max(f.stat().st_mtime for f in d.iterdir()) if any(d.iterdir()) else d.stat().st_mtime)
                except (OSError, ValueError):
                    pass
    return max(times) if times else None


# ============================================================================ progress / ETA
def _opt(args, flag, default=None):
    args = [str(a) for a in args or []]
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default


def loop_scenes(task):
    """(task, seed) of the scenes this closed loop runs (same selection as online.py: tasks, seeds, limit, shard)."""
    task = q.effective(task)
    wanted = task.get("tasks") or ["put_back_block", "swap_blocks"]
    rows = []
    for spec in q.scene_args(task) or []:
        if spec == "frozen":
            return None
        path = Path(spec)
        for f in (sorted(path.glob("*.json")) if path.is_dir() else [path]):
            value = q.read_json(f, {})
            rows += (value.get("scenes") if isinstance(value, dict) else value) or []
    seen, scenes = set(), []
    for s in rows:
        key = (s.get("task"), int(s.get("seed", -1)))
        if s.get("task") in wanted and key not in seen:
            seen.add(key)
            scenes.append(s)
    scenes.sort(key=lambda s: (wanted.index(s["task"]), s.get("ordinal", 0), int(s["seed"])))
    args = [str(a) for a in (task.get("online_args") or [])]
    seeds = [str(x) for x in task.get("seeds") or []]
    if seeds:
        want = {(x.split(":")[0], int(x.split(":")[1])) if ":" in x else (None, int(x)) for x in seeds}
        scenes = [s for s in scenes if (s["task"], int(s["seed"])) in want or (None, int(s["seed"])) in want]
    limit = int(_opt(args, "--limit", 0) or 0)
    if limit:
        count, kept = {}, []
        for s in scenes:
            count[s["task"]] = count.get(s["task"], 0) + 1
            if count[s["task"]] <= limit:
                kept.append(s)
        scenes = kept
    k, n = (int(x) for x in _opt(args, "--shard", "0/1").split("/"))
    return [(s["task"], int(s["seed"])) for s in scenes[k::n]]


def progress(task, s):
    """(done, total, unit, eta epoch or None, note)."""
    kind = task["kind"]
    if kind == "train":
        m = q.train_metrics(task["run"])
        total = (q.read_json(q.O / task["run"] / "CONFIG.json", {}) or {}).get("total_updates", 0)
        done = m.get("updates", 0)
        eta = time.time() + max(0, total - done) * m["seconds_per_update"] if m.get("seconds_per_update") and total else None
        return done, total, "updates", eta, ("complete" if m.get("complete") else "")
    if kind != "closed_loop":
        return None
    try:
        scenes = loop_scenes(task)
    except Exception:                              # noqa: BLE001
        scenes = None
    modes = q.effective(task).get("modes") or ["on"]
    out = q.resolve(q.effective(task)["output"])
    wanted = set(scenes or [])
    done, stamps, errors = 0, [], 0
    for res in out.glob("*/*/*/seed_*/result.json"):
        mode, tname, seed = res.parent.parent.parent.name, res.parent.parent.name, int(res.parent.name.split("_")[1])
        if mode in modes and (not wanted or (tname, seed) in wanted):
            done += 1
            stamps.append(res.stat().st_mtime)
    for e in out.glob("*/*/*/seed_*/ERROR.json"):
        if not (e.parent / "result.json").exists():
            errors += 1
    total = len(scenes) * len(modes) if scenes is not None else None
    eta = None
    stamps.sort()
    recent = [t for t in stamps if t >= time.time() - 6 * 3600][-11:]
    if total and len(recent) >= 3 and s.get("status") == "running":
        per = (recent[-1] - recent[0]) / (len(recent) - 1)
        eta = time.time() + max(0, total - done) * per
    return done, total, "episodes", eta, (f"{errors} open episode errors" if errors else "")


def fmt_eta(eta):
    if not eta:
        return "ETA ?"
    left = (eta - time.time()) / 3600
    return f"ETA {datetime.fromtimestamp(eta, q.BJ):%m-%d %H:%M} ({left:.1f} h)"


# ============================================================================ exec: one task, one attempt
def cmd_exec(args):
    tasks = {t["id"]: t for t in q.load_tasks()}
    task, tid = tasks[args.id], args.id
    cfg = config()
    s = q.state(tid)
    attempt = int(s.get("attempt") or 1)
    started = s.get("start") if args.adopt and s.get("start") else q.now_bj()
    q.set_state(tid, status="running", pid=os.getpid(), gpu=args.gpu, start=started, lane=task.get("lane"),
                waiting=None, retry_after=None, stall_killed=None, paused=None, host=socket.gethostname())
    if args.adopt:
        child = s.get("child_pid")
        log(f"{tid}: adopting process group {child} (attempt {attempt}); waiting for it to end")
        while group_alive(child):
            time.sleep(15)
    elif not args.judge_only:
        q.ledger_append({"id": tid, "kind": task["kind"], "status": "running", "start": started, "lane": task.get("lane"),
                         "gpu": args.gpu, "attempt": attempt, "hypothesis": task.get("hypothesis"),
                         "pass_if": task.get("pass_if")})
    if args.judge_only:
        rc, cut = args.rc, False
    else:
        log(f"{tid}: start (attempt {attempt}/{cfg['max_attempts']}) on GPU {args.gpu}; job log {q.Q / 'tasks' / (tid + '.log')}")
        try:
            rc, cut = q.execute(task, args.gpu)
        except Exception as error:                 # noqa: BLE001
            log(f"{tid}: crashed in the queue: {error!r}")
            rc, cut = 99, False
    failure = None
    if not args.judge_only and rc != "skip" and not cut:
        if rc not in (0, None):
            s = q.state(tid)
            failure = ("stalled: nothing written for " + str(cfg["stall_minutes"]) + " min" if s.get("stall_killed")
                       else f"rc={rc}: " + classify(log_tail(q.Q / "tasks" / f"{tid}.log", 60)))
        elif task["kind"] == "closed_loop":
            open_errors = q.error_dirs([q.effective(task)["output"]], q.effective(task)["label"])
            if open_errors:
                failure = f"{len(open_errors)} episodes ended with ERROR.json (re-run retries only those)"
    if failure:
        s = q.state(tid)
        failures = (s.get("failures") or []) + [{"attempt": attempt, "gpu": args.gpu, "time": q.now_bj(), "why": failure,
                                                 "log_tail": log_tail(q.Q / "tasks" / f"{tid}.log", 15)}]
        if attempt < int(cfg["max_attempts"]):
            retry = time.time() + 60 * float(cfg["retry_minutes"])
            q.set_state(tid, status="pending", last_failure=failure, failures=failures, retry_after=retry, pid=None,
                        child_pid=None)
            log(f"{tid}: attempt {attempt} failed ({failure}); retry after "
                f"{datetime.fromtimestamp(retry, q.BJ):%H:%M} on any empty GPU")
            return
        q.set_state(tid, last_failure=failure, failures=failures)
        log(f"{tid}: attempt {attempt} failed ({failure}); attempts used up: judging what exists")
    q.finish(task, rc, cut, started)
    q.set_state(tid, pid=None)


# ============================================================================ the dispatcher
def spawn(tid, gpu, *extra):
    EXEC.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONPATH=str(q.REPO / "src"))
    with open(EXEC / f"{tid}.log", "a", encoding="utf-8") as f:
        f.write(f"\n[pool] {q.now_bj()} exec {tid} GPU {gpu} {' '.join(extra)}\n")
        f.flush()
        cmd = [q.PY, "-u", SELF, "exec", "--id", tid] + (["--gpu", str(gpu)] if gpu is not None else []) + list(extra)
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=str(q.REPO), start_new_session=True)
    q.set_state(tid, status="running", pid=p.pid, gpu=gpu, waiting=None)
    return p.pid


def deps_done(task, by_id):
    return all(d in by_id and q.state(d)["status"] == "done" for d in task.get("after", []) or [])


def needs_gpu(task):
    return task.get("lane") != "cpu" and task["kind"] != "analysis" and int(task.get("need_mib", 30000)) > 0


def reconcile(tasks, cfg, occupied):
    """Running tasks of our lanes: alive -> GPU occupied; exec gone -> adopt the job or re-queue."""
    for t in tasks:
        if t.get("lane") not in cfg["lanes"]:
            continue
        s = q.state(t["id"])
        if s["status"] not in ("running", "waiting"):
            continue
        if alive_exec(s.get("pid")) or alive_lane(s.get("pid")):
            if s.get("gpu") is not None:
                occupied[int(s["gpu"])] = t["id"]
            continue
        child = s.get("child_pid")
        if s["status"] == "running" and child and group_alive(child) and not s.get("paused"):
            log(f"{t['id']}: its job (group {child}) runs without a pool process: adopting it on GPU {s.get('gpu')}")
            spawn(t["id"], s.get("gpu"), "--adopt")
            if s.get("gpu") is not None:
                occupied[int(s["gpu"])] = t["id"]
            continue
        if s["status"] == "waiting" or s.get("paused") or s.get("paused_at"):
            if child and group_alive(child):
                continue                           # a paused job is still shutting down
            q.set_state(t["id"], status="pending", pid=None, child_pid=None, paused=None, paused_at=None,
                        waiting="paused / waiting before; re-queued")
            log(f"{t['id']}: was paused; back in the queue (attempt counter unchanged)")
            continue
        why = "exec process died without a verdict (killed / crash / container restart)"
        failures = (s.get("failures") or []) + [{"attempt": s.get("attempt"), "gpu": s.get("gpu"), "time": q.now_bj(),
                                                 "why": why}]
        q.set_state(t["id"], status="pending", pid=None, child_pid=None, last_failure=why, failures=failures,
                    retry_after=time.time() + 60)
        log(f"{t['id']}: {why}; back in the queue")


def stall_check(tasks, cfg):
    limit = 60 * float(cfg["stall_minutes"])
    for t in tasks:
        s = q.state(t["id"])
        if s["status"] != "running" or not alive_exec(s.get("pid")) or not s.get("child_pid"):
            continue
        child = int(s["child_pid"])
        if s.get("stall_killed"):
            if group_alive(child) and time.time() - float(s["stall_killed"]) > 120:
                os.killpg(child, signal.SIGKILL)
                log(f"{t['id']}: stalled job still alive after TERM: SIGKILL group {child}")
            continue
        last = last_activity(t)
        if last and time.time() - last > limit and group_alive(child):
            q.set_state(t["id"], stall_killed=time.time())
            os.killpg(child, signal.SIGTERM)
            log(f"{t['id']}: nothing written for {(time.time() - last) / 60:.0f} min: SIGTERM group {child} (will retry)")


def cmd_pool(args):
    me = os.getpid()
    sys.stdout = sys.stderr = open(q.Q / "pool.log", "a", encoding="utf-8", buffering=1)
    info = q.read_json(POOL, {}) or {}
    if info.get("pid") not in (None, me) and q.pid_alive(info.get("pid"), "pool5.py pool"):
        raise SystemExit(f"a pool already runs as pid {info['pid']}")
    cfg = config()
    lanes_alive = [f.stem for f in (q.Q / "lanes").glob("*.json")
                   if f.stem in cfg["lanes"] and alive_lane((q.read_json(f, {}) or {}).get("pid"))]
    if lanes_alive:
        raise SystemExit(f"lane processes still serve {lanes_alive}: stop them first (jobs/pool_start.sh does)")
    start = q.now_bj()
    log(f"pool pid {me}: lanes {cfg['lanes']}, GPUs {cfg['gpus']}; config {CFG_PATH}")
    free_since, last_stall, said = {}, 0.0, {}
    while True:
        cfg = config()
        deadline = q._deadline()
        q.write_json(POOL, {"pid": me, "start": start, "beat": q.now_bj(), "host": socket.gethostname(),
                            "gpus": cfg["gpus"], "lanes": cfg["lanes"],
                            "deadline": datetime.fromtimestamp(deadline, q.BJ).strftime("%Y-%m-%d %H:%M")})
        if (q.Q / "POOL_STOP").exists():
            (q.Q / "POOL_STOP").unlink()
            log("POOL_STOP found: the dispatcher exits (running tasks keep running; the next dispatcher adopts them)")
            return
        try:
            tasks = q.load_tasks()
        except Exception as error:                 # noqa: BLE001
            log(f"task file unreadable ({error!r}); retry in 5 min")
            time.sleep(300)
            continue
        by_id = {t["id"]: t for t in tasks}
        occupied = {}
        reconcile(tasks, cfg, occupied)
        if time.time() - last_stall > 300:
            stall_check(tasks, cfg)
            last_stall = time.time()
        table = gpu_table()
        now = time.time()
        for g in cfg["gpus"]:
            g = int(g)
            empty = g in table and table[g]["used"] < int(cfg["free_mib"]) and g not in occupied
            free_since[g] = free_since.get(g) or now if empty else None
        ready = [int(g) for g in cfg["gpus"] if free_since.get(int(g)) and now - free_since[int(g)] >= cfg["free_seconds"]]
        running_any = any(q.state(t["id"])["status"] == "running" for t in tasks if t.get("lane") in cfg["lanes"])
        if now >= deadline:
            if not running_any:
                log("deadline reached and nothing runs: the pool exits")
                return
            time.sleep(cfg["poll_seconds"])
            continue
        gpu_blocked = False                        # an earlier GPU task waits: later GPU tasks do not overtake it
        for t in tasks:
            tid = t["id"]
            if t.get("lane") not in cfg["lanes"] or t.get("hold"):
                continue
            s = q.state(tid)
            if s["status"] != "pending" or not deps_done(t, by_id):
                continue
            if s.get("retry_after") and now < float(s["retry_after"]):
                continue
            missing = [d for d in t.get("requires_pass") or [] if q.state(d).get("verdict") != "PASS"]
            passed = [d for d in t.get("requires_not_pass") or [] if q.state(d).get("verdict") == "PASS"]
            if missing or passed:
                log(f"{tid}: skipped ({'requires PASS of ' + str(missing) if missing else str(passed) + ' PASSed'})")
                q.set_state(tid, status="running", start=q.now_bj(), pid=me)
                q.finish(t, "skip", False, q.now_bj())
                continue
            if any(q.running(p) for p in t.get("wait_for_exit") or []):
                continue
            attempt = int(s.get("attempt") or 0) + 1
            if s.get("last_failure") and attempt > int(cfg["max_attempts"]):
                log(f"{tid}: {attempt - 1} attempts used: judging what exists")
                spawn(tid, None, "--judge-only", "--rc", "98")
                continue
            if not needs_gpu(t):
                q.set_state(tid, attempt=attempt)
                spawn(tid, None)
                continue
            if gpu_blocked or not ready:
                if said.get(tid) != "nogpu":
                    q.set_state(tid, waiting=f"no empty allowed GPU (allowed {cfg['gpus']})")
                    said[tid] = "nogpu"
                gpu_blocked = True                 # keep the queue order: the next GPU goes to the first waiting task
                continue
            g = ready.pop(0)
            free_since[g] = None
            q.set_state(tid, attempt=attempt, start=q.now_bj())
            pid = spawn(tid, g)
            said.pop(tid, None)
            log(f"{tid}: started on GPU {g} (attempt {attempt}, exec pid {pid})")
        time.sleep(cfg["poll_seconds"])


# ============================================================================ pause / allow
def cmd_allow(args):
    cfg = config()
    cfg["gpus"] = [int(x) for x in args.gpus.split(",") if x.strip() != ""]
    q.write_json(CFG_PATH, cfg)
    print(f"allowed GPUs now {cfg['gpus']} ({CFG_PATH}); the pool reads it within one cycle")


def cmd_pause(args):
    """Stop our task(s) on the GPUs (exec first, so nothing is judged; then the job group SIGINT -> TERM -> KILL),
    keep them for a re-run (no attempt counted), and drop the GPUs from the allowed list."""
    gpus = [int(x) for x in args.gpu]
    cfg = config()
    cfg["gpus"] = [g for g in cfg["gpus"] if int(g) not in gpus]
    q.write_json(CFG_PATH, cfg)
    print(f"allowed GPUs now {cfg['gpus']}")
    victims = [t for t in q.load_tasks() if q.state(t["id"])["status"] == "running" and q.state(t["id"]).get("gpu") is not None
               and int(q.state(t["id"])["gpu"]) in gpus]
    for t in victims:
        s = q.state(t["id"])
        q.set_state(t["id"], paused=q.now_bj())
        if alive_exec(s.get("pid")):
            os.kill(int(s["pid"]), signal.SIGKILL)
        child = s.get("child_pid")
        for sig, wait in ((signal.SIGINT, 120), (signal.SIGTERM, 60), (signal.SIGKILL, 30)):
            if not group_alive(child):
                break
            os.killpg(int(child), sig)
            end = time.time() + wait
            while time.time() < end and group_alive(child):
                time.sleep(2)
        if t["kind"] == "closed_loop":
            q.kill_sim_workers(q.resolve(q.effective(t)["output"]))
        print(f"{t['id']}: paused on GPU {s.get('gpu')} ({'job still alive!' if group_alive(child) else 'job stopped'}); "
              "it goes back to the queue and resumes on an allowed GPU")
    time.sleep(5)
    table = gpu_table()
    for g in gpus:
        print(f"GPU {g}: {table.get(g, {}).get('used', '?')} MiB used now")
    if not victims:
        print(f"no task of ours ran on GPU {gpus}")


# ============================================================================ status / report
def status_lines(cfg=None):
    cfg = cfg or config()
    lines = []
    info = q.read_json(POOL, {}) or {}
    alive = q.pid_alive(info.get("pid"), "pool5.py pool")
    deadline = q._deadline()
    lines.append(f"== pool5 {q.now_bj()} on {socket.gethostname()}: dispatcher pid {info.get('pid')} "
                 f"{'ALIVE' if alive else 'NOT RUNNING'} (last beat {info.get('beat')}); allowed GPUs {cfg['gpus']}; "
                 f"lanes {cfg['lanes']}; nothing new starts after {datetime.fromtimestamp(deadline, q.BJ):%m-%d %H:%M}")
    table = gpu_table()
    tasks = q.load_tasks()
    ours = {int(q.state(t['id'])['gpu']): t["id"] for t in tasks
            if q.state(t["id"])["status"] == "running" and q.state(t["id"]).get("gpu") is not None}
    for g, v in sorted(table.items()):
        who = ours.get(g) or ("empty" if v["used"] < cfg["free_mib"] else "OTHER USER")
        lines.append(f"   GPU {g}: {v['used']:>6}/{v['total']} MiB, {v['util']:>3}% busy  -> {who}"
                     f"{'' if g in [int(x) for x in cfg['gpus']] else '   (not allowed)'}")
    lanes = [f"{f.stem}:{'alive' if alive_lane((q.read_json(f, {}) or {}).get('pid')) else 'stopped'}"
             for f in sorted((q.Q / "lanes").glob("*.json"))]
    lines.append(f"   queue5 lane processes: {' '.join(lanes)}")
    counts = {}
    for t in tasks:
        st = q.state(t["id"])["status"]
        counts[st] = counts.get(st, 0) + 1
    lines.append(f"   tasks: {counts.get('done', 0)} done, {counts.get('running', 0)} running, "
                 f"{counts.get('pending', 0)} pending, {sum(1 for t in tasks if t.get('hold'))} on hold")
    lines.append("")
    lines.append("RUNNING")
    for t in tasks:
        s = q.state(t["id"])
        if s["status"] not in ("running", "waiting"):
            continue
        who = ("pool" if alive_exec(s.get("pid")) else "lane" if alive_lane(s.get("pid")) else "NO PROCESS")
        p = progress(t, s)
        prog = (f"{p[0]}/{p[1] if p[1] is not None else '?'} {p[2]}  {fmt_eta(p[3])}  {p[4]}" if p else "")
        last = last_activity(t)
        idle = f"  last write {(time.time() - last) / 60:.0f} min ago" if last else ""
        lines.append(f"  {t['id']:<18} {t['kind']:<11} GPU {s.get('gpu')}  attempt {s.get('attempt', 1)}  since "
                     f"{str(s.get('start'))[5:16]}  [{who}]  {prog}{idle}")
    lines.append("")
    lines.append("QUEUE (pool lanes, in start order)")
    by_id = {t["id"]: t for t in tasks}
    for t in tasks:
        s = q.state(t["id"])
        if s["status"] != "pending" or t.get("lane") not in cfg["lanes"]:
            continue
        if t.get("hold"):
            why = "on hold"
        elif not deps_done(t, by_id):
            why = "after " + ", ".join(d for d in t.get("after", []) if q.state(d)["status"] != "done")
        elif s.get("retry_after") and time.time() < float(s["retry_after"]):
            why = f"retry at {datetime.fromtimestamp(float(s['retry_after']), q.BJ):%H:%M} ({s.get('last_failure')})"
        else:
            why = s.get("waiting") or "next empty GPU"
        p = progress(t, s)
        done = f"  [{p[0]}/{p[1]} {p[2]} already done]" if p and p[0] else ""
        lines.append(f"  {t['id']:<18} {t['kind']:<11} {why}{done}")
    failed = [(t["id"], q.state(t["id"])) for t in tasks if q.state(t["id"]).get("last_failure")]
    if failed:
        lines.append("")
        lines.append("FAILURES SEEN (latest per task)")
        for tid, s in failed:
            lines.append(f"  {tid:<18} attempt {s.get('attempt')}: {s.get('last_failure')}  -> now {s['status']}"
                         f"{' ' + str(s.get('verdict')) if s.get('verdict') else ''}")
    recent = [(t["id"], q.state(t["id"])) for t in tasks if q.state(t["id"]).get("verdict")]
    recent.sort(key=lambda x: str(x[1].get("end") or ""))
    lines.append("")
    lines.append("LATEST VERDICTS")
    for tid, s in recent[-8:]:
        lines.append(f"  {str(s.get('end'))[5:16]}  {tid:<18} {s.get('verdict'):<13} {q.headline(by_id[tid], s.get('metrics', {}))[:150]}")
    return lines


def cmd_status(args):
    print("\n".join(status_lines()))


def cmd_report(args):
    REPORTS.mkdir(parents=True, exist_ok=True)
    cfg = config()
    tasks = q.load_tasks()
    lines = [f"# pool5 report {q.now_bj()} ({socket.gethostname()})", "", "```"] + status_lines(cfg) + ["```", ""]
    since = time.time() - args.hours * 3600
    for t in tasks:
        s = q.state(t["id"])
        log_path = q.Q / "tasks" / f"{t['id']}.log"
        touched = log_path.exists() and log_path.stat().st_mtime >= since
        if s["status"] == "running" or touched or (s.get("last_failure") and s["status"] != "done"):
            lines += [f"## {t['id']} ({s['status']}, attempt {s.get('attempt')}, GPU {s.get('gpu')})", ""]
            if s.get("failures"):
                lines += ["failures:", "```", json.dumps([{k: v for k, v in f.items() if k != "log_tail"}
                                                          for f in s["failures"]], indent=1, ensure_ascii=False), "```"]
            lines += [f"job log tail ({log_path}):", "```"] + log_tail(log_path, 25) + ["```"]
            ex = EXEC / f"{t['id']}.log"
            if ex.exists():
                lines += [f"pool log for this task ({ex}):", "```"] + log_tail(ex, 8) + ["```"]
            if t["kind"] == "train":
                lines += ["training stdout tail:", "```"] + log_tail(q.O / t["run"] / "stdout.log", 10) + ["```"]
            lines.append("")
    for s in ("done",):
        recent = [(t, q.state(t["id"])) for t in tasks if q.state(t["id"]).get("verdict")
                  and str(q.state(t["id"]).get("end") or "") >= datetime.fromtimestamp(since, q.BJ).strftime("%Y-%m-%d %H:%M")]
        if recent:
            lines += [f"## verdicts in the last {args.hours} h", ""]
            for t, st in recent:
                lines.append(f"- {t['id']}: **{st.get('verdict')}** ({st.get('end')}) {q.headline(t, st.get('metrics', {}))}")
                autopsy = q.AUTOPSY / f"AUTOPSY_{t['id']}.md"
                if autopsy.exists():
                    lines.append(f"  autopsy: {autopsy}")
            lines.append("")
    lines += ["## dispatcher log (pool.log, last 40 lines)", "```"] + log_tail(q.Q / "pool.log", 40) + ["```"]
    for lane in ("cpu",):
        lines += [f"## lane {lane} log (last 10 lines)", "```"] + log_tail(q.Q / f"{lane}.log", 10) + ["```"]
    df = subprocess.run(["df", "-BG", "--output=avail", str(q.O)], capture_output=True, text=True).stdout.split()[-1:]
    lines += ["", f"disk free: {df[0] if df else '?'}"]
    path = REPORTS / f"REPORT_{datetime.now(q.BJ):%Y%m%d_%H%M}_{socket.gethostname()}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(path)


# ============================================================================ start / take over from queue5 lanes
def cmd_start(args):
    """Stop the queue5 lane processes of the pool lanes (their running jobs keep running and are adopted), then start
    the dispatcher in its own session. --lanes / --gpus update POOL_CONFIG.json first."""
    cfg = config()
    if args.lanes:
        cfg["lanes"] = [x for x in args.lanes.split(",") if x]
    if args.gpus is not None:
        cfg["gpus"] = [int(x) for x in args.gpus.split(",") if x.strip() != ""]
    q.write_json(CFG_PATH, cfg)
    info = q.read_json(POOL, {}) or {}
    if q.pid_alive(info.get("pid"), "pool5.py pool"):
        print(f"the pool already runs (pid {info['pid']}); allowed GPUs {cfg['gpus']}")
    else:
        for lane in cfg["lanes"]:
            pid = (q.read_json(q.Q / "lanes" / f"{lane}.json", {}) or {}).get("pid")
            if not alive_lane(pid):
                continue
            for _ in range(90):                    # a lane that is judging (job ended, autopsy running) finishes first
                judging = [t["id"] for t in q.load_tasks() if q.state(t["id"]).get("pid") == pid
                           and q.state(t["id"])["status"] == "running" and not group_alive(q.state(t["id"]).get("child_pid"))]
                if not judging:
                    break
                print(f"lane {lane}: judging {judging}; waiting")
                time.sleep(10)
            os.kill(int(pid), signal.SIGTERM)
            for _ in range(30):
                if not alive_lane(pid):
                    break
                time.sleep(1)
            if alive_lane(pid):
                os.kill(int(pid), signal.SIGKILL)
            print(f"lane {lane}: lane process {pid} stopped (its running job, if any, keeps running)")
        env = dict(os.environ, PYTHONPATH=str(q.REPO / "src"))
        p = subprocess.Popen([q.PY, "-u", SELF, "pool"], env=env, cwd=str(q.REPO), start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"dispatcher started: pid {p.pid}; log {q.Q / 'pool.log'}")
        time.sleep(20)
    print("\n".join(status_lines(config())))


def cmd_log(args):
    t = {x["id"]: x for x in q.load_tasks()}[args.id]
    s = q.state(args.id)
    print(f"== {args.id}: {s['status']} {s.get('verdict') or ''} attempt {s.get('attempt')} GPU {s.get('gpu')} "
          f"since {s.get('start')}; last failure: {s.get('last_failure')}")
    for title, path, n in (("job log", q.Q / "tasks" / f"{args.id}.log", args.lines),
                           ("training stdout", q.O / t["run"] / "stdout.log" if t.get("run") else None, 20),
                           ("pool log for this task", EXEC / f"{args.id}.log", 10)):
        if path and Path(path).exists():
            print(f"--- {title}: {path}")
            print("\n".join(log_tail(path, n)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pool")
    st = sub.add_parser("start")
    st.add_argument("--lanes")
    st.add_argument("--gpus")
    e = sub.add_parser("exec")
    e.add_argument("--id", required=True)
    e.add_argument("--gpu", type=int, default=None)
    e.add_argument("--adopt", action="store_true")
    e.add_argument("--judge-only", action="store_true")
    e.add_argument("--rc", type=int, default=98)
    sub.add_parser("status")
    r = sub.add_parser("report")
    r.add_argument("--hours", type=float, default=12)
    p = sub.add_parser("pause")
    p.add_argument("--gpu", action="append", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("--id", required=True)
    lg.add_argument("--lines", type=int, default=60)
    a = sub.add_parser("allow")
    a.add_argument("--gpus", required=True)
    args = ap.parse_args()
    {"pool": cmd_pool, "start": cmd_start, "exec": cmd_exec, "status": cmd_status, "report": cmd_report, "pause": cmd_pause,
     "allow": cmd_allow, "log": cmd_log}[args.cmd](args)


if __name__ == "__main__":
    main()
