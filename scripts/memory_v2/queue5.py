"""Week-plan v3 queue: task file -> lanes -> ledger -> verdict -> autopsy.

    queue5.py run    --lane loop  --gpu 1      one lane: runs its tasks from the task file in order, re-reading it before
                                              every pick (tasks can be added / edited while the lanes run)
    queue5.py status                          one screen: lanes, GPUs, every task's state / verdict, running work, deadline
    queue5.py verdict --id X1-exec8           recompute metrics + verdict + autopsy of a finished task (new ledger entry)
    queue5.py ledger                          re-render LEDGER.md from LEDGER.jsonl
    queue5.py reset  --id X1-exec8            set a task back to pending (its outputs stay; a closed loop resumes)
    queue5.py check                           preflight: inputs of every task, training sets vs the reference config

Task file (YAML, default scripts/memory_v2/jobs/queue5_tasks.yaml). Each task:
    id, lane, kind, hypothesis, after: [ids that must be done first], wait_for_exit: [regex on process command lines],
    need_mib (free memory on the lane's GPU before starting; 0 = no GPU), timeout_h,
    pass_if / inconclusive_if: Python expressions over m (metrics), r (reference metrics), helpers sign_p(a, b), get(d, "a.b")
    min_episodes, on_pass, on_fail, on_inconclusive, failure_explanations: [{if: expr over m, r, c (class counts), then: text}]
    hold: true (never picked until removed), requires_pass: [ids] (SKIPPED unless every one of them PASSed)
  kind closed_loop: checkpoint (path, or <run>/last = the run's final checkpoint), label, modes, scenes: [..] (missing
                    scene folders are dropped; 'frozen' = Codex's 2 scenes), tasks, seeds, online_args: [..], output,
                    reference: {folders: [..], label, modes}   (paired comparison on the same scenes)
                    best_of: {ids: [..], key: "put_back_block/on.regrasp", args: {id: [online args]}, fallback: [args],
                              use: {id: {label: .., output: ..}}}
                    (online args of the best PASSing task, and optionally its label / output folder, so episodes
                    already there are reused; no PASS -> fallback, or SKIPPED without one)
                    parity_with: {folders, label, modes}: per-frame max |action difference| vs that run (U1 smoke)
  kind analysis:    folders: [..], label, modes, tasks, reference   (no GPU: metrics of existing episodes only)
  kind train:       run, sets: [--set values, {O} = outputs/memory_v2]; stdout -> outputs/memory_v2/<run>/stdout.log
  kind eval:        run, checkpoint (default: the run's last), pr (default true), reference_run
  kind shell:       command (bash -c; {GPU} and {O} are replaced), kill_output: folder whose simulator workers die with it
Verdicts: PASS / FAIL (pass_if) | INCONCLUSIVE (inconclusive_if, too few episodes, interrupted) | ERROR | SKIPPED |
DONE (no pass_if: a descriptive run).

Everything lives in outputs/memory_v2/: LEDGER.jsonl / LEDGER.md, queue5/state/<id>.json, queue5/tasks/<id>.log,
queue5/<lane>.log (from queue5.sh), autopsy/AUTOPSY_<id>.md. Nothing starts after QUEUE_DEADLINE (default 2026-10-30
12:00 +0800); a task still running then is interrupted (SIGINT -> SIGTERM -> SIGKILL, simulator workers included) and
judged INCONCLUSIVE. touch outputs/memory_v2/queue5/STOP: the lanes start nothing new.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
O = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2"))
Q = O / "queue5"
LEDGER = O / "LEDGER.jsonl"
AUTOPSY = O / "autopsy"
PY = os.environ.get("MEMV2_PY", "/opt/mwam/bin/python")
CFG = "configs/memory_v2/train_v2_A.yaml"
BJ = timezone(timedelta(hours=8))
DEADLINE = datetime.strptime(os.environ.get("QUEUE_DEADLINE", "2026-10-30 12:00 +0800"), "%Y-%m-%d %H:%M %z").timestamp()
TASKS = Path(os.environ.get("QUEUE5_TASKS", str(REPO / "scripts/memory_v2/jobs/queue5_tasks.yaml")))
POLL = int(os.environ.get("QUEUE5_POLL", "60"))
# progress (week plan v4 1.2): the number of these stages reached in order, / 6; a simulator success counts 6 / 6
PROGRESS = {"put_back_block": ("lifted", "centre", "pressed", "regrasp", "returned", "success"),
            "swap_blocks": ("lifted", "s1", "s2", "s3", "pressed", "success")}
STAGES = {"put_back_block": ("lifted", "centre", "pressed", "stage1", "regrasp", "returned", "success"),
          "swap_blocks": ("lifted", "s1", "s2", "s3", "pressed", "success")}


def now_bj():
    return datetime.now(BJ).strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    print(f"[queue5] {now_bj()} {msg}", flush=True)


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(value, indent=1, default=str), encoding="utf-8")
    tmp.replace(path)


def resolve(p):
    p = str(p).replace("{O}", str(O))
    return Path(p) if p.startswith("/") else O / p


def pid_alive(pid, expect=None):
    """Running (not a zombie) and, with `expect`, its command line contains that text (guards against pid reuse)."""
    try:
        os.kill(int(pid), 0)
    except (OSError, TypeError, ValueError):
        return False
    try:
        if Path(f"/proc/{int(pid)}/stat").read_text().rsplit(")", 1)[1].split()[0] == "Z":
            return False
        if expect and expect not in Path(f"/proc/{int(pid)}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace"):
            return False
    except OSError:
        pass
    return True


# ============================================================================ task file / state / ledger
MODE_WORDS = {True: "on", False: "off", None: "null"}


def load_tasks(path=TASKS):
    import yaml
    value = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    tasks = value.get("tasks", [])
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate task ids in {path}")
    for t in tasks:
        if t.get("kind") not in ("closed_loop", "analysis", "train", "eval", "shell"):
            raise ValueError(f"task {t.get('id')}: unknown kind {t.get('kind')}")
        for holder in (t, t.get("reference") or {}):          # YAML 1.1: unquoted on / off / null are True / False / None
            if "modes" in holder:
                holder["modes"] = [x if isinstance(x, str) else MODE_WORDS[x] for x in holder["modes"]]
    return tasks


def state(tid):
    return read_json(Q / "state" / f"{tid}.json", {"id": tid, "status": "pending"})


def set_state(tid, **kw):
    s = state(tid)
    s.update(kw)
    write_json(Q / "state" / f"{tid}.json", s)
    return s


def ledger_append(entry):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")
    render_ledger()


def render_ledger():
    rows = {}
    if LEDGER.exists():
        for line in LEDGER.read_text(encoding="utf-8").splitlines():
            if line.strip():
                e = json.loads(line)
                rows[e["id"]] = {**rows.get(e["id"], {}), **e}
    out = ["# LEDGER (latest entry per run; source LEDGER.jsonl)", "",
           "| id | kind | status | verdict | start | end | headline | autopsy |", "|---|---|---|---|---|---|---|---|"]
    for tid, e in rows.items():
        out.append(f"| {tid} | {e.get('kind', '')} | {e.get('status', '')} | {e.get('verdict', '')} | {e.get('start', '')} | "
                   f"{e.get('end', '')} | {str(e.get('headline', ''))[:160]} | {e.get('autopsy') or ''} |")
    out += ["", "## hypotheses and pre-registered thresholds", ""]
    for tid, e in rows.items():
        out.append(f"- **{tid}**: {e.get('hypothesis', '')}  \n  pass_if: `{e.get('pass_if', '')}`")
    (O / "LEDGER.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def effective(task):
    """The task with the overrides chosen at run time (best_of 'use': label / output of the winner)."""
    override = state(task["id"]).get("override") or {}
    return {**task, **override} if override else task


def runnable(task, by_id, lane):
    if task.get("lane") != lane or task.get("hold") or state(task["id"])["status"] != "pending":
        return False
    return all(dep in by_id and state(dep)["status"] == "done" for dep in task.get("after", []) or [])


# ============================================================================ helpers for pass_if
def sign_p(a, b):
    """Two-sided exact sign test p for a discordant split a vs b."""
    n = a + b
    if n == 0:
        return 1.0
    k = min(a, b)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def perm_p(diffs, rounds=20000):
    """Two-sided exact sign-flip permutation test of mean(diffs) = 0 (paired differences): enumerated for
    <= 20 non-zero differences, otherwise `rounds` random flips with seed 0 (p = (hits + 1) / (rounds + 1))."""
    import itertools
    import random
    d = [float(x) for x in diffs if abs(float(x)) > 1e-12]
    if not d:
        return 1.0
    observed = abs(sum(d)) - 1e-12
    if len(d) <= 20:
        hits = total = 0
        for signs in itertools.product((1, -1), repeat=len(d)):
            total += 1
            hits += abs(sum(s * x for s, x in zip(signs, d))) >= observed
        return hits / total
    rng = random.Random(0)
    hits = sum(abs(sum(x if rng.random() < 0.5 else -x for x in d)) >= observed for _ in range(rounds))
    return (hits + 1) / (rounds + 1)


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def bootstrap_ci(diffs, rounds=10000, level=0.95):
    import random
    d = [float(x) for x in diffs]
    if not d:
        return [0.0, 0.0]
    rng = random.Random(0)
    means = sorted(sum(rng.choice(d) for _ in d) / len(d) for _ in range(rounds))
    lo, hi = int((1 - level) / 2 * rounds), int((1 + level) / 2 * rounds) - 1
    return [round(means[lo], 4), round(means[hi], 4)]


def progress(task, a):
    """Fraction of the task's stages reached in order (success = 1)."""
    stages = PROGRESS.get(task, ())
    if not stages:
        return 0.0
    if a.get("success"):
        return 1.0
    n = 0
    for k in stages:
        if not a.get(k):
            break
        n += 1
    return n / len(stages)


def get(d, dotted, default=0):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


SAFE = {"min": min, "max": max, "abs": abs, "len": len, "sum": sum, "any": any, "all": all, "sorted": sorted,
        "round": round, "perm_p": perm_p, "mean": mean}


def evaluate_expr(expr, m, r, **extra):
    """pass_if / inconclusive_if / failure_explanations: an expression over m, r (and c), no builtins beyond SAFE."""
    if not expr:
        return None
    env = {"__builtins__": {}, **SAFE, "m": m, "r": r, "sign_p": sign_p, "get": get, **extra}
    return bool(eval(expr, env))


# ============================================================================ metrics
def _stages_module():
    spec = importlib.util.spec_from_file_location("closed_loop_stages", REPO / "scripts/memory_v2/closed_loop_stages.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def episodes(folders, label, modes=None, tasks=None):
    """{(task, mode, seed): stage analysis} of every finished episode of <label> (and <label>_off) in the folders;
    the simulator's success flag replaces the reconstructed one. A later folder wins on duplicates."""
    cls = _stages_module()
    out = {}
    for folder in folders:
        for res in sorted(resolve(folder).glob("*/*/*/seed_*/result.json")):
            d = res.parent
            if not re.fullmatch(r"seed_\d+", d.name) or not (d / "executed_actions.jsonl").exists():
                continue
            r = read_json(res, {})
            if r.get("label") not in (label, f"{label}_off"):
                continue
            if (modes and r.get("mode") not in modes) or (tasks and r.get("task") not in tasks):
                continue
            snaps, counters = cls.read_rows(d / "executed_actions.jsonl")
            if len(snaps) < 2 or not snaps[0]:
                continue
            a = cls.analyse_put_back(snaps, counters) if r["task"] == "put_back_block" else cls.analyse_swap(snaps, counters)
            a["success"] = bool(r.get("success"))
            a["dir"] = str(d)
            out[(r["task"], r["mode"], int(r["seed"]))] = a
    return out


def error_dirs(folders, label, modes=None, tasks=None):
    """Episode folders with ERROR.json and no result.json: [(task, mode, seed, ERROR.json path)]."""
    out = []
    for folder in folders:
        for e in sorted(resolve(folder).glob("*/*/*/seed_*/ERROR.json")):
            d = e.parent
            task, mode, lab = d.parent.name, d.parent.parent.name, d.parent.parent.parent.name
            if (re.fullmatch(r"seed_\d+", d.name) and not (d / "result.json").exists() and lab in (label, f"{label}_off")
                    and (not modes or mode in modes) and (not tasks or task in tasks)):
                out.append((task, mode, int(d.name.split("_")[1]), e))
    return out


def stage_table(eps):
    m = {}
    for (task, mode, seed), a in eps.items():
        cell = m.setdefault(f"{task}/{mode}", {"n": 0, **{k: 0 for k in STAGES.get(task, ())}, "progress_sum": 0.0,
                                               "decided": 0, "correct": 0})
        cell["n"] += 1
        for k in STAGES.get(task, ()):
            cell[k] += bool(a.get(k))
        cell["progress_sum"] += progress(task, a)
        if a.get("choice_correct") is not None:
            name = "correct_mat" if task == "put_back_block" else "second_correct"
            cell[name] = cell.get(name, 0) + bool(a["choice_correct"])
            cell["decided"] += 1
            cell["correct"] += bool(a["choice_correct"])
        if task == "put_back_block":
            cell["centred"] = cell.get("centred", 0) + bool(a.get("centre"))
            cell["pressed_after_centre"] = cell.get("pressed_after_centre", 0) + bool(a.get("centre") and a.get("pressed"))
    for cell in m.values():
        cell["progress_mean"] = round(cell.pop("progress_sum") / cell["n"], 4) if cell["n"] else 0.0
        if "centred" in cell:
            cell["pressed_given_centre"] = round(cell["pressed_after_centre"] / cell["centred"], 4) if cell["centred"] else None
    return m


def paired(eps_a, eps_b, mode_a, mode_b):
    """{task: {stage: [only_a, only_b, n_common]}} on the scenes present in both."""
    out = {}
    seeds = {(t, s) for (t, md, s) in eps_a if md == mode_a} & {(t, s) for (t, md, s) in eps_b if md == mode_b}
    for task, seed in sorted(seeds):
        a, b = eps_a[(task, mode_a, seed)], eps_b[(task, mode_b, seed)]
        cell = out.setdefault(task, {k: [0, 0, 0] for k in STAGES.get(task, ())})
        for k in STAGES.get(task, ()):
            cell[k][0] += bool(a.get(k)) and not bool(b.get(k))
            cell[k][1] += bool(b.get(k)) and not bool(a.get(k))
            cell[k][2] += 1
    return out


def decisions(d):
    path = Path(d) / "decisions.jsonl"
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def parity(eps, spec, tasks=None):
    """Same scenes, same frames: max |action difference| between these episodes and spec {folders, label}."""
    ref = episodes(spec["folders"], spec["label"], spec.get("modes"), tasks)
    first, worst, n, ref_s = [], 0.0, 0, []
    for key, a in eps.items():
        if key not in ref:
            continue
        mine = {x["frame_id"]: x for x in decisions(a["dir"])}
        theirs = {x["frame_id"]: x for x in decisions(ref[key]["dir"])}
        common = sorted(set(mine) & set(theirs))
        for i, f in enumerate(common):
            u, v = mine[f]["actions_after_gripper_clip"], theirs[f]["actions_after_gripper_clip"]
            diff = max(abs(x - y) for ru, rv in zip(u, v) for x, y in zip(ru, rv))
            worst = max(worst, diff)
            n += 1
            if i == 0:
                first.append(diff)
        res = read_json(Path(ref[key]["dir"]) / "result.json", {}) or {}
        if res.get("policy_seconds_mean") is not None:
            ref_s.append(float(res["policy_seconds_mean"]))
    return {"parity_decisions": n, "parity_first_max_abs": max(first) if first else None,
            "parity_max_abs": worst if n else None, "policy_seconds_ref": round(mean(ref_s), 3) if ref_s else None}


def progress_pairs(eps_a, eps_b, mode_a, mode_b):
    """{task: {diffs, mean_a, mean_b, delta, ci, p, n}}: progress a - b on the scenes present in both."""
    out = {}
    seeds = {(t, s) for (t, md, s) in eps_a if md == mode_a} & {(t, s) for (t, md, s) in eps_b if md == mode_b}
    by_task = {}
    for task, seed in sorted(seeds):
        by_task.setdefault(task, []).append((progress(task, eps_a[(task, mode_a, seed)]),
                                             progress(task, eps_b[(task, mode_b, seed)])))
    for task, rows in by_task.items():
        diffs = [round(a - b, 6) for a, b in rows]
        out[task] = {"diffs": diffs, "mean_a": round(mean(a for a, _ in rows), 4), "mean_b": round(mean(b for _, b in rows), 4),
                     "delta": round(mean(diffs), 4), "ci": bootstrap_ci(diffs), "p": round(perm_p(diffs), 5),
                     "n": len(rows)}
    return out


def loop_metrics(task):
    folders = task.get("folders") or [task["output"]]
    eps = episodes(folders, task["label"], task.get("modes"), task.get("tasks"))
    m = stage_table(eps)
    m["episodes"] = len(eps)
    m["errors"] = len(error_dirs(folders, task["label"], task.get("modes"), task.get("tasks")))
    gaps, exact, policy_s, choices, n_cand = set(), True, [], [], 0
    for a in eps.values():
        d = Path(a["dir"])
        rows = decisions(d)
        frames = [x["frame_id"] for x in rows]
        gaps |= {b - a_ for a_, b in zip(frames, frames[1:])}
        res = read_json(d / "result.json", {}) or {}
        exact = exact and bool(res.get("command_to_execution_exact"))
        if res.get("policy_seconds_mean") is not None:
            policy_s.append(float(res["policy_seconds_mean"]))
        for x in rows:
            if x.get("candidate_distances"):
                choices.append(int(x.get("choice", 0)))
                n_cand = max(n_cand, len(x["candidate_distances"]))
    m["decision_gaps"] = sorted(gaps)
    m["command_to_execution_exact"] = exact
    m["policy_seconds_mean"] = round(mean(policy_s), 3) if policy_s else None
    m["candidates_logged"] = n_cand
    m["choice_nonzero_frac"] = round(mean(c != 0 for c in choices), 4) if choices else None
    if task.get("parity_with"):
        m.update(parity(eps, task["parity_with"], task.get("tasks")))
    modes = task.get("modes") or sorted({md for (_, md, _) in eps})
    if "on" in modes and "null" in modes:
        m["on_vs_null"] = paired(eps, eps, "on", "null")
        m["prog_on_vs_null"] = progress_pairs(eps, eps, "on", "null")
    r = {}
    ref = task.get("reference")
    if ref:
        ref_eps = episodes(ref["folders"], ref["label"], ref.get("modes"), task.get("tasks"))
        mine = {(t, s) for (t, md, s) in eps}
        ref_eps = {k: v for k, v in ref_eps.items() if (k[0], k[2]) in mine}      # the same scenes only
        r = stage_table(ref_eps)
        r["episodes"] = len(ref_eps)
        ref_modes = ref.get("modes") or sorted({md for (_, md, _) in ref_eps})
        if "on" in ref_modes and "null" in ref_modes:
            r["on_vs_null"] = paired(ref_eps, ref_eps, "on", "null")
            r["prog_on_vs_null"] = progress_pairs(ref_eps, ref_eps, "on", "null")
        for mode in modes:
            if mode in ref_modes:
                m.setdefault("vs_reference", {})[mode] = paired(eps, ref_eps, mode, mode)
                m.setdefault("prog_vs_reference", {})[mode] = progress_pairs(eps, ref_eps, mode, mode)
    return m, r


def train_metrics(run):
    d = O / run
    m = {"run": run, "complete": (d / "COMPLETE.json").exists(), "guard": read_json(d / "GUARD.json")}
    rows = []
    if (d / "metrics.jsonl").exists():
        for line in (d / "metrics.jsonl").read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
    rows = [x for x in rows if "fm" in x]
    if rows:
        fm = [x["fm"] for x in rows]
        k = min(30, max(1, len(fm) // 3))
        first, last = sorted(fm[:k])[k // 2], sorted(fm[-k:])[k // 2]
        tail = rows[-20:]
        m.update(updates=rows[-1]["update"], fm_first=first, fm_last=last, fm_ratio=last / first if first else None,
                 seconds_per_update=sum(x.get("seconds", 0) for x in tail) / len(tail))
    m["eval_curve"] = []
    for e in sorted((d / "eval").glob("update_*.json")):
        o = (read_json(e, {}) or {}).get("overall", {})
        m["eval_curve"].append({"update": int(e.stem.split("_")[1]), **{k: o.get(f"{k}/arm_rmse_rad") for k in ("on", "off", "null")}})
    return m


def pr_metrics(run):
    files = sorted((O / "pr" / run).glob("pr_*_val.json"))
    if not files:
        return {}
    s = (read_json(files[-1], {}) or {}).get("summary", {})
    out = {}
    for key in ("all", "put_back_block", "swap_blocks"):
        for mode, v in (s.get(key) or {}).items():
            if isinstance(v, dict):
                out[f"pr_{key}_{mode}"] = v.get("pr")
    return out


def full_eval(run):
    files = sorted((O / run / "eval_full").glob("update_*.json"))
    if not files:
        return {}
    o = (read_json(files[-1], {}) or {}).get("overall", {})
    return {f"full_{k}": o.get(f"{k}/arm_rmse_rad") for k in ("on", "off", "null")}


def flat(d, prefix=""):
    out = {}
    for k, v in (d or {}).items():
        if isinstance(v, dict):
            out.update(flat(v, f"{prefix}{k}."))
        else:
            out[f"{prefix}{k}"] = v
    return out


def config_diff(run, reference):
    a = flat((read_json(O / run / "CONFIG.json", {}) or {}).get("config"))
    b = flat((read_json(O / reference / "CONFIG.json", {}) or {}).get("config"))
    if not a or not b:
        return None
    return {k: [a.get(k), b.get(k)] for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)}


def run_metrics(task):
    m = {**train_metrics(task["run"]), **pr_metrics(task["run"]), **full_eval(task["run"])}
    r = {}
    if task.get("reference_run"):
        rr = task["reference_run"]
        r = {**train_metrics(rr), **pr_metrics(rr), **full_eval(rr)}
        m["config_diff"] = config_diff(task["run"], rr)
    return m, r


def headline(task, m):
    if not m:
        return ""
    if task["kind"] in ("closed_loop", "analysis"):
        parts = []
        for key, cell in sorted(m.items()):
            if "/" in key and isinstance(cell, dict) and "n" in cell:
                parts.append(f"{key} n={cell['n']} " + " ".join(f"{k}={cell.get(k, 0)}" for k in STAGES.get(key.split('/')[0], ()))
                             + (f" prog={cell['progress_mean']:.2f}" if "progress_mean" in cell else ""))
        for t, cell in (m.get("on_vs_null") or {}).items():
            key = "s2" if t == "swap_blocks" else "pressed"
            v = cell.get(key)
            if v:
                parts.append(f"{t} on/null only {key} {v[0]}/{v[1]} p={sign_p(v[0], v[1]):.3f}")
        for t, c in (m.get("prog_on_vs_null") or {}).items():
            parts.append(f"{t} dprog on-null {c['delta']:+.3f} {c['ci']} p={c['p']:.4f} n={c['n']}")
        if m.get("errors"):
            parts.append(f"errors={m['errors']}")
        return "; ".join(parts)
    if task["kind"] in ("train", "eval"):
        c = m.get("eval_curve") or [{}]
        f = lambda v: "-" if v is None else f"{v:.4f}"
        ratio = m.get("fm_ratio")
        return (f"updates={m.get('updates')} fm x{ratio:.2f} " if ratio else f"updates={m.get('updates')} ") + \
               f"offline on {f(c[0].get('on'))}->{f(c[-1].get('on'))} off {f(c[0].get('off'))}->{f(c[-1].get('off'))} " \
               f"null {f(c[0].get('null'))}->{f(c[-1].get('null'))} full_on={f(m.get('full_on'))} " \
               f"pr_on={f(m.get('pr_all_on'))}" + (f" guard={m['guard']}" if m.get("guard") else "")
    return f"rc={m.get('rc')}"


def judge(task, rc, interrupted):
    kind = task["kind"]
    try:
        if kind in ("closed_loop", "analysis"):
            m, r = loop_metrics(task)
        elif kind in ("train", "eval"):
            m, r = run_metrics(task)
        else:
            m, r = {"rc": rc}, {}
    except Exception as error:                    # noqa: BLE001
        return "ERROR", {"metrics_error": repr(error)}, {}
    enough = m.get("episodes", 0) >= int(task.get("min_episodes", 1)) if kind in ("closed_loop", "analysis") else True
    if rc not in (0, None) and not interrupted and not (kind in ("closed_loop", "analysis") and enough):
        return "ERROR", m, r                      # a closed loop with some failed episodes is judged on the rest
    if kind == "train" and not m.get("complete"):
        return ("INCONCLUSIVE" if interrupted else "ERROR"), m, r
    if not enough or interrupted:
        return "INCONCLUSIVE", m, r
    try:
        if evaluate_expr(task.get("inconclusive_if"), m, r):
            return "INCONCLUSIVE", m, r
        ok = evaluate_expr(task.get("pass_if"), m, r)
    except Exception as error:                    # noqa: BLE001
        m["pass_if_error"] = repr(error)
        return "INCONCLUSIVE", m, r
    if ok is None:
        return ("DONE" if rc in (0, None) else "ERROR"), m, r
    return ("PASS" if ok else "FAIL"), m, r


# ============================================================================ running
VIEWERS = {"pgrep", "pkill", "grep", "egrep", "tail", "less", "more", "cat", "vim", "vi", "nano"}


def running(pattern):
    """Is a process (other than this one, pgrep / grep / tail ... showing the pattern) running whose command line
    matches `pattern` (regex, like pgrep -f)? Two lanes polling at once would otherwise see each other's pgrep."""
    rx, me = re.compile(pattern), os.getpid()
    for d in Path("/proc").iterdir():
        if not d.name.isdigit() or int(d.name) == me:
            continue
        try:
            raw = (d / "cmdline").read_bytes()
        except OSError:
            continue
        args = raw.rstrip(b"\0").split(b"\0") if raw else []
        if not args or Path(args[0].decode(errors="replace")).name in VIEWERS:
            continue
        if rx.search(" ".join(a.decode(errors="replace") for a in args)):
            return True
    return False


def gpu_free_mib(gpu):
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits", "-i", str(gpu)],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        return int(out.splitlines()[0])
    except Exception:                             # noqa: BLE001
        return 0


def wait_ready(task, gpu):
    """Wait for the wait_for_exit processes to end and for need_mib free on the GPU (twice, POLL s apart)."""
    patterns = task.get("wait_for_exit") or []
    need = int(task.get("need_mib", 30000))
    said = None
    while time.time() < DEADLINE:
        if (Q / "STOP").exists():
            return False
        busy = [p for p in patterns if running(p)]
        use_gpu = gpu is not None and need > 0
        free = gpu_free_mib(gpu) if use_gpu else None
        if not busy and (not use_gpu or free >= need):
            if not use_gpu:
                time.sleep(min(POLL, 10))
                if not any(running(p) for p in patterns):
                    return True
                continue
            time.sleep(POLL)
            busy = [p for p in patterns if running(p)]
            if not busy and gpu_free_mib(gpu) >= need:
                return True
            continue
        why = (f"waiting for {', '.join(busy)} to exit" if busy else f"GPU {gpu} has {free} MiB free < {need}")
        if why != said:
            log(f"{task['id']}: {why}")
            set_state(task["id"], waiting=why)
            said = why
        time.sleep(POLL)
    return False


def kill_sim_workers(out):
    """Simulator workers run in their own session (owned_popen): kill each matching session."""
    found = subprocess.run(["pgrep", "-f", f"sim_worker.py .*--output {out}/"], capture_output=True, text=True).stdout.split()
    for sig in (signal.SIGTERM, signal.SIGKILL):
        for pid in found:
            try:
                os.killpg(int(pid), sig)
            except (ProcessLookupError, PermissionError, ValueError):
                pass
        time.sleep(5)
    if found:
        log(f"killed leftover simulator workers {found}")


def run_cmd(cmd, logfile, env, timeout, tid=None):
    """Run in its own session; at the timeout SIGINT (the closed loop stops its simulators) -> SIGTERM -> SIGKILL."""
    with open(logfile, "a", encoding="utf-8") as f:
        f.write(f"\n[queue5] {now_bj()} $ {' '.join(map(str, cmd))}\n")
        f.flush()
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, env=env, cwd=str(REPO), start_new_session=True)
        if tid:
            set_state(tid, child_pid=p.pid)
        try:
            return p.wait(timeout=max(1, timeout)), False
        except subprocess.TimeoutExpired:
            for sig, wait in ((signal.SIGINT, 120), (signal.SIGTERM, 60), (signal.SIGKILL, 30)):
                try:
                    os.killpg(p.pid, sig)
                except ProcessLookupError:
                    break
                try:
                    p.wait(timeout=wait)
                    break
                except subprocess.TimeoutExpired:
                    continue
            f.write(f"\n[queue5] {now_bj()} interrupted at the deadline / timeout\n")
            return p.returncode, True


def checkpoint_path(value):
    value = str(value)
    if value.endswith("/last"):
        run = value[:-len("/last")]
        total = int((read_json(O / run / "CONFIG.json", {}) or {}).get("total_updates", 0))
        return O / run / "checkpoints" / f"update_{total:06d}.pt"
    return resolve(value)


def scene_args(task):
    scenes = []
    for s in task["scenes"]:
        if s == "frozen":
            scenes.append(s)
        elif resolve(s).exists():
            scenes.append(str(resolve(s)))
        else:
            log(f"{task['id']}: scene folder {resolve(s)} does not exist: dropped")
    return scenes


def closed_loop_cmd(task, extra):
    cmd = [PY, "-m", "fastwam.memory_v2.online", "run", "--checkpoint", str(checkpoint_path(task["checkpoint"])),
           "--label", task["label"], "--modes", *task["modes"], "--scenes", *scene_args(task),
           "--output", str(resolve(task["output"]))]
    if task.get("tasks"):
        cmd += ["--tasks", *task["tasks"]]
    if task.get("seeds"):
        cmd += ["--seeds", *map(str, task["seeds"])]
    sim = [("SIM_PY", "--simulator-python"), ("CUROBO", "--curobo-backend"), ("EXT_DIR", "--extensions-dir"),
           ("VK_ICD", "--vk-icd")]
    cmd += [a for env, flag in sim if os.environ.get(env) for a in (flag, os.environ[env])]
    return cmd + [str(a) for a in (task.get("online_args") or [])] + [str(a) for a in extra]


def best_args(task):
    spec = task.get("best_of")
    if not spec:
        return []
    best, best_val = None, None
    for tid in spec["ids"]:
        s = state(tid)
        if s.get("verdict") != "PASS":
            continue
        val = get(s.get("metrics", {}), spec["key"], 0)
        if best_val is None or val > best_val:
            best, best_val = tid, val
    if best is not None and spec.get("use", {}).get(best):
        set_state(task["id"], override=dict(spec["use"][best]))
    if best is None:
        if "fallback" in spec:
            log(f"{task['id']}: none of {spec['ids']} passed; fallback args {spec['fallback']}")
            return [str(a) for a in spec["fallback"] or []]
        log(f"{task['id']}: none of {spec['ids']} passed: skipped")
        return None
    log(f"{task['id']}: best of {spec['ids']} = {best} ({spec['key']}={best_val}) -> args {spec['args'][best]}")
    return [str(a) for a in spec["args"][best]]


def set_aside(d):
    """A run folder without a checkpoint to resume from (e.g. an OOM at start) would mix old logs into the new run."""
    if d.exists() and not (d / "checkpoints" / "LATEST.json").exists() and not (d / "COMPLETE.json").exists():
        target = d.with_name(f"{d.name}.stale_{datetime.now(BJ):%m%d_%H%M}")
        d.rename(target)
        log(f"{d.name}: folder without a checkpoint moved aside -> {target}")


def execute(task, gpu):
    tid, kind = task["id"], task["kind"]
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"),
               OMP_NUM_THREADS=os.environ.get("OMP_NUM_THREADS", "16"), MKL_NUM_THREADS=os.environ.get("MKL_NUM_THREADS", "16"))
    if gpu is not None:
        env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    logfile = Q / "tasks" / f"{tid}.log"
    logfile.parent.mkdir(parents=True, exist_ok=True)

    def left():
        cap = DEADLINE - time.time()
        if task.get("timeout_h"):
            cap = min(cap, task_start + float(task["timeout_h"]) * 3600 - time.time())
        return cap

    task_start = time.time()
    if kind == "analysis":
        return 0, False
    if kind == "closed_loop":
        extra = best_args(task)
        if extra is None:
            return "skip", False
        task = effective(task)
        out = resolve(task["output"])
        out.mkdir(parents=True, exist_ok=True)
        ck = checkpoint_path(task["checkpoint"])
        if not ck.exists() or not scene_args(task):
            with open(logfile, "a", encoding="utf-8") as f:
                f.write(f"[queue5] {now_bj()} missing checkpoint {ck} or no scene folder\n")
            return 1, False
        rc, cut = run_cmd(closed_loop_cmd(task, extra), logfile, env, left(), tid)
        if cut:
            kill_sim_workers(out)
        return rc, cut
    if kind == "train":
        d = O / task["run"]
        rc, cut = 1, False
        if (d / "GUARD.json").exists():
            return 1, False
        if not (d / "COMPLETE.json").exists():
            set_aside(d)
        for attempt in range(3):
            if (d / "COMPLETE.json").exists() or (d / "GUARD.json").exists():
                break
            d.mkdir(parents=True, exist_ok=True)
            resume = ["--resume"] if (d / "checkpoints" / "LATEST.json").exists() else []
            cmd = [PY, "-m", "fastwam.memory_v2.train_v2", "train", "--config", CFG, "--allow-high-action-lr",
                   "--set", f"name={task['run']}", "--set", f"output={d}"]
            for s in task.get("sets", []):
                cmd += ["--set", str(s).replace("{O}", str(O))]
            with open(logfile, "a", encoding="utf-8") as f:
                f.write(f"[queue5] {now_bj()} train attempt {attempt + 1} {' '.join(resume)}; stdout -> {d / 'stdout.log'}\n")
            rc, cut = run_cmd(cmd + resume, d / "stdout.log", env, left(), tid)
            if cut or (d / "COMPLETE.json").exists() or not (d / "checkpoints" / "LATEST.json").exists():
                break
            log(f"{tid}: training exited rc={rc}; resuming (attempt {attempt + 2})")
            time.sleep(30)
        return (0 if (d / "COMPLETE.json").exists() else rc or 1), cut
    if kind == "eval":
        run = task["run"]
        cfg = read_json(O / run / "CONFIG.json", {})
        ck = resolve(task["checkpoint"]) if task.get("checkpoint") else \
            O / run / "checkpoints" / f"update_{int(cfg.get('total_updates', 0)):06d}.pt"
        if not ck.exists():
            with open(logfile, "a", encoding="utf-8") as f:
                f.write(f"[queue5] {now_bj()} no checkpoint {ck}\n")
            return 1, False
        rc = 0
        if not (O / run / "eval_full" / f"{ck.stem}.json").exists():
            rc, cut = run_cmd([PY, "-m", "fastwam.memory_v2.train_v2", "evaluate", "--config", CFG, "--checkpoint", str(ck),
                               "--windows", "0", "--output", str(O / run / "eval_full")], logfile, env, left(), tid)
            if cut:
                return rc, True
        if task.get("pr", True) and not list((O / "pr" / run).glob("pr_*_val.json")):
            rc2, cut = run_cmd([PY, "-m", "fastwam.memory_v2.train_v2", "pr", "--config", CFG, "--checkpoint", str(ck),
                                "--pairs", str(O / "pairs" / "pairs_v1.json"), "--limit", "300",
                                "--set", 'eval.modes=["on","off","null"]', "--output", str(O / "pr" / run)],
                               logfile, env, left(), tid)
            rc = rc or rc2
            if cut:
                return rc, True
        return rc, False
    if kind == "shell":
        cmd = ["bash", "-c", task["command"].replace("{GPU}", str(gpu)).replace("{O}", str(O))]
        rc, cut = run_cmd(cmd, logfile, env, left(), tid)
        if cut and task.get("kill_output"):
            kill_sim_workers(resolve(task["kill_output"]))
        return rc, cut
    raise ValueError(f"unknown kind {kind}")


def finish(task, rc, cut, started):
    task = effective(task)
    tid = task["id"]
    if rc == "skip":
        verdict, m, r = "SKIPPED", {}, {}
    else:
        verdict, m, r = judge(task, rc, cut)
    end = now_bj()
    set_state(tid, status="done", verdict=verdict, end=end, rc=rc, interrupted=cut, metrics=m, reference=r, waiting=None)
    autopsy = AUTOPSY / f"AUTOPSY_{tid}.md"
    if verdict != "SKIPPED":
        try:
            subprocess.run([PY, str(REPO / "scripts/memory_v2/autopsy.py"), "--id", tid], timeout=3600, cwd=str(REPO),
                           env=dict(os.environ, PYTHONPATH=str(REPO / "src"), CUDA_VISIBLE_DEVICES=""))
        except Exception as error:                # noqa: BLE001
            log(f"{tid}: autopsy failed: {error!r}")
        m = state(tid).get("metrics", m)          # the autopsy adds the failure-class counts
    ledger_append({"id": tid, "kind": task["kind"], "status": "done", "verdict": verdict, "start": started, "end": end,
                   "rc": rc, "interrupted": cut, "lane": task.get("lane"), "hypothesis": task.get("hypothesis"),
                   "pass_if": task.get("pass_if"),
                   "config": {k: v for k, v in task.items() if k not in ("hypothesis", "failure_explanations", "on_pass",
                                                                        "on_fail", "on_inconclusive")},
                   "metrics": m, "reference": r, "headline": headline(task, m),
                   "autopsy": str(autopsy) if autopsy.exists() else None})
    log(f"{tid}: {verdict}  {headline(task, m)}")


def recover(lane):
    """A task left 'running' by a lane that died goes back to pending (closed loops skip finished episodes,
    training resumes from LATEST.json)."""
    for t in load_tasks():
        s = state(t["id"])
        if t.get("lane") == lane and s["status"] in ("running", "waiting") and not pid_alive(s.get("pid"), "queue5.py"):
            child = s.get("child_pid")
            if s["status"] == "running" and pid_alive(child):
                log(f"{t['id']}: its process {child} still runs (lane restarted): waiting for it to end, then the task "
                    "is re-run (finished work reused) and judged")
                set_state(t["id"], pid=os.getpid())         # status shows it as running under this lane meanwhile
                while pid_alive(child):
                    time.sleep(POLL)
            log(f"{t['id']}: was {s['status']} under dead pid {s.get('pid')}: back to pending (finished work is reused)")
            set_state(t["id"], status="pending")


def cmd_run(args):
    lane, gpu = args.lane, args.gpu
    log(f"lane {lane} on GPU {gpu}; tasks {TASKS}; deadline {datetime.fromtimestamp(DEADLINE, BJ):%Y-%m-%d %H:%M} Beijing")
    for other in (Q / "lanes").glob("*.json"):
        info = read_json(other, {})
        if info.get("lane") == lane and info.get("pid") != os.getpid() and pid_alive(info.get("pid"), "queue5.py"):
            raise SystemExit(f"lane {lane} already runs as pid {info['pid']}")
    write_json(Q / "lanes" / f"{lane}.json", {"lane": lane, "gpu": gpu, "pid": os.getpid(), "start": now_bj()})
    recover(lane)
    idle = False
    while time.time() < DEADLINE:
        if (Q / "STOP").exists():
            log("STOP found: lane exits")
            return
        try:
            tasks = load_tasks()
        except Exception as error:                # noqa: BLE001
            log(f"task file unreadable ({error!r}); retry in 5 min")
            time.sleep(300)
            continue
        by_id = {t["id"]: t for t in tasks}
        task = next((t for t in tasks if runnable(t, by_id, lane)), None)
        if task is None:
            if not idle:
                waiting = [t["id"] for t in tasks if t.get("lane") == lane and state(t["id"])["status"] == "pending"]
                log(f"no runnable task (pending, waiting on dependencies: {waiting}); re-checking every 5 min")
                idle = True
            time.sleep(min(300, max(1, POLL * 5)))
            continue
        idle = False
        tid = task["id"]
        missing = [d for d in task.get("requires_pass") or [] if state(d).get("verdict") != "PASS"]
        if missing:
            log(f"{tid}: requires PASS of {missing}: skipped")
            set_state(tid, status="running", start=now_bj(), lane=lane, gpu=gpu, pid=os.getpid())
            finish(task, "skip", False, now_bj())
            continue
        set_state(tid, status="waiting", lane=lane, gpu=gpu, pid=os.getpid())
        if not wait_ready(task, gpu):
            set_state(tid, status="pending")
            log(f"{tid}: not started (STOP or deadline)")
            return
        started = now_bj()
        set_state(tid, status="running", start=started, lane=lane, gpu=gpu, pid=os.getpid(), waiting=None)
        ledger_append({"id": tid, "kind": task["kind"], "status": "running", "start": started, "lane": lane,
                       "hypothesis": task.get("hypothesis"), "pass_if": task.get("pass_if")})
        log(f"{tid}: start ({task['kind']}); log {Q / 'tasks' / (tid + '.log')}")
        try:
            rc, cut = execute(task, gpu)
        except Exception as error:                # noqa: BLE001
            log(f"{tid}: crashed in the queue: {error!r}")
            rc, cut = 99, False
        finish(task, rc, cut, started)
    log("deadline reached: lane exits")


def cmd_status(args):
    left = (DEADLINE - time.time()) / 3600
    print(f"== queue5 {now_bj()} Beijing   deadline {datetime.fromtimestamp(DEADLINE, BJ):%m-%d %H:%M} ({left:.1f} h left)"
          f"   stop: touch {Q / 'STOP'}{'   (STOP present)' if (Q / 'STOP').exists() else ''}")
    for f in sorted((Q / "lanes").glob("*.json")):
        info = read_json(f, {})
        print(f"  lane {info.get('lane'):<7} GPU {info.get('gpu')}  pid {info.get('pid')} "
              f"{'alive' if pid_alive(info.get('pid'), 'queue5.py') else 'NOT RUNNING'}  (since {info.get('start')})")
    smi = subprocess.run(["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu", "--format=csv,noheader"],
                         capture_output=True, text=True).stdout.strip()
    if smi:
        print("  GPUs: " + " | ".join(smi.splitlines()))
    try:
        tasks = load_tasks()
    except Exception as error:                    # noqa: BLE001
        print(f"  task file unreadable: {error!r}")
        return
    print(f"\n{'id':<17}{'lane':<7}{'kind':<12}{'status':<9}{'verdict':<14}{'start':<13}headline / progress")
    for t in tasks:
        s = state(t["id"])
        status = s["status"]
        if status in ("waiting", "running") and not pid_alive(s.get("pid"), "queue5.py"):
            status += "?"                         # its lane died: it restarts when the lane is started again
        t = effective(t)
        hl = headline(t, s.get("metrics", {})) if s.get("metrics") else ""
        print(f"{t['id']:<17}{t.get('lane', ''):<7}{t['kind']:<12}{status:<9}{str(s.get('verdict') or ''):<14}"
              f"{str(s.get('start') or '')[5:16]:<13}{hl[:150]}")
        if s["status"] == "waiting" and s.get("waiting"):
            print(f"{'':<17}  {s['waiting']}")
        if s["status"] == "running":
            if t["kind"] in ("train", "eval"):
                m = train_metrics(t["run"])
                if m.get("updates"):
                    total = (read_json(O / t["run"] / "CONFIG.json", {}) or {}).get("total_updates", 0)
                    eta = time.time() + max(0, total - m["updates"]) * m["seconds_per_update"]
                    c = m["eval_curve"][-1] if m["eval_curve"] else {}
                    if t.get("reference_run"):
                        diff = config_diff(t["run"], t["reference_run"]) or {}
                        keys = [k for k in diff if k not in ("name", "output")]
                        print(f"{'':<17}  config vs {t['reference_run']}: {', '.join(keys) or 'identical'}")
                    print(f"{'':<17}  update {m['updates']}/{total}  fm x{m['fm_ratio']:.2f}  {m['seconds_per_update']:.0f} s/update"
                          f"  ETA {datetime.fromtimestamp(eta, BJ):%m-%d %H:%M}  last eval (update {c.get('update')}) "
                          f"on {c.get('on')} off {c.get('off')} null {c.get('null')}  guard {m.get('guard')}")
                else:
                    print(f"{'':<17}  loading / initial evaluation; stdout {O / t['run'] / 'stdout.log'}")
            elif t["kind"] == "closed_loop":
                out = resolve(t["output"])
                done = [p for p in out.glob(f"{t['label']}/*/*/seed_*/result.json")]
                errs = [p for p in out.glob(f"{t['label']}/*/*/seed_*/ERROR.json") if not (p.parent / "result.json").exists()]
                print(f"{'':<17}  {len(done)} episodes finished, {len(errs)} errors in {out}/{t['label']}")
    df = subprocess.run(["df", "-BG", "--output=avail", str(O)], capture_output=True, text=True).stdout.split()[-1:]
    print(f"\n  disk free {df[0] if df else '?'}   ledger {O / 'LEDGER.md'}   autopsies {AUTOPSY}/")
    verdicts = {t["id"]: state(t["id"]).get("verdict") for t in tasks if state(t["id"]).get("verdict")}
    if verdicts:
        print("  verdicts so far: " + "  ".join(f"{k}={v}" for k, v in verdicts.items()))


def cmd_verdict(args):
    t = {x["id"]: x for x in load_tasks()}[args.id]
    s = state(args.id)
    finish(t, s.get("rc", 0), bool(s.get("interrupted")), s.get("start") or now_bj())


def _same(a, b):
    try:
        return math.isclose(float(a), float(b), rel_tol=1e-9, abs_tol=0.0)
    except (TypeError, ValueError):
        return str(a).strip("\"'") == str(b).strip("\"'")


def cmd_check(args):
    """Preflight before the lanes start: every input a task needs, and training sets vs the reference config."""
    bad, warn = [], []
    try:
        tasks = load_tasks()
    except Exception as error:                    # noqa: BLE001
        print(f"FAIL task file {TASKS}: {error!r}")
        raise SystemExit(1)
    ids = {t["id"] for t in tasks}
    produced = {str(resolve(t["output"])) for t in tasks if t.get("output")}
    trained = {t["run"] for t in tasks if t["kind"] == "train"}
    print(f"task file {TASKS}: {len(tasks)} tasks; deadline {datetime.fromtimestamp(DEADLINE, BJ):%Y-%m-%d %H:%M} Beijing; "
          f"outputs {O}")
    for t in tasks:
        tid = t["id"]
        for dep in (t.get("after") or []) + (t.get("requires_pass") or []):
            if dep not in ids:
                bad.append(f"{tid}: depends on unknown task {dep}")
        for key in ("pass_if", "inconclusive_if"):
            if t.get(key):
                try:
                    compile(t[key], key, "eval")
                except SyntaxError as error:
                    bad.append(f"{tid}: {key} does not parse: {error}")
        if t.get("checkpoint"):
            ck = str(t["checkpoint"])
            run = ck[:-len("/last")] if ck.endswith("/last") else None
            if run and run in trained:
                pass                              # produced by a train task of this queue
            elif not checkpoint_path(ck).exists():
                bad.append(f"{tid}: checkpoint {checkpoint_path(ck)} missing")
        planners = [x for x in tasks if x["kind"] == "shell" and "closed_loop.sh plan" in str(x.get("command"))
                    and state(x["id"])["status"] != "done"]
        for sc in t.get("scenes") or []:
            if sc != "frozen" and not resolve(sc).exists():
                (warn if planners else bad).append(f"{tid}: scene folder {resolve(sc)} missing "
                                                   f"(planned by {', '.join(x['id'] for x in planners) or 'nothing'}; "
                                                   "dropped at run time if still missing)")
        for f in (t.get("folders") or []) + ((t.get("reference") or {}).get("folders") or []):
            if not resolve(f).exists() and str(resolve(f)) not in produced:
                warn.append(f"{tid}: folder {resolve(f)} missing")
        for value in t.get("sets") or []:
            k, _, v = str(value).replace("{O}", str(O)).partition("=")
            if v.startswith("/") and not Path(v.split()[0]).exists():
                bad.append(f"{tid}: --set {k} points to a missing file {v}")
        if t["kind"] == "train" and t.get("reference_run"):
            ref = flat((read_json(O / t["reference_run"] / "CONFIG.json", {}) or {}).get("config"))
            if not ref:
                warn.append(f"{tid}: reference run {t['reference_run']} has no CONFIG.json yet (compared at run time)")
            else:
                for value in t.get("sets") or []:
                    k, _, v = str(value).replace("{O}", str(O)).partition("=")
                    v = v.split("#")[0].strip()
                    if k in ref and not _same(ref[k], v):
                        print(f"  note {tid}: {k} = {v} (reference {t['reference_run']}: {ref[k]})")
                    elif k not in ref:
                        print(f"  note {tid}: {k} = {v} (not in the reference config)")
                pairs = {k: v for k, v in ref.items() if k.startswith("pairs.") and v not in (None, "", 0, 0.0)}
                print(f"  {tid}: reference {t['reference_run']} pair settings {pairs or 'none'}")
        d = O / t["run"] if t.get("run") and t["kind"] == "train" and state(tid)["status"] == "pending" else None
        if d is not None and d.exists() and not (d / "checkpoints" / "LATEST.json").exists():
            warn.append(f"{tid}: {d} exists without a checkpoint: it will be moved aside to {d.name}.stale_<time>")
        if d is not None and (d / "COMPLETE.json").exists():
            warn.append(f"{tid}: {d} is already complete: the task only records it")
    for gpu in (1, 2):
        free = gpu_free_mib(gpu)
        print(f"  GPU {gpu}: {free} MiB free now (lanes wait for their own threshold)")
    held = {t["id"] for t in tasks if t.get("hold")}
    for line in [b for b in bad if b.split(":")[0] in held]:
        warn.append(f"{line} [task on hold: fix before releasing it]")
    bad = [b for b in bad if b.split(":")[0] not in held]
    for line in warn:
        print(f"WARN {line}")
    for line in bad:
        print(f"FAIL {line}")
    print("CHECK " + ("FAILED" if bad else "OK"))
    raise SystemExit(1 if bad else 0)


def cmd_reset(args):
    set_state(args.id, status="pending", verdict=None, metrics=None, reference=None, waiting=None, override=None)
    print(f"{args.id}: pending")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--lane", required=True)
    r.add_argument("--gpu", type=int, default=None)
    sub.add_parser("status")
    for name in ("verdict", "reset"):
        v = sub.add_parser(name)
        v.add_argument("--id", required=True)
    sub.add_parser("ledger")
    sub.add_parser("check")
    args = ap.parse_args()
    {"run": cmd_run, "status": cmd_status, "verdict": cmd_verdict, "reset": cmd_reset, "check": cmd_check,
     "ledger": lambda a: render_ledger()}[args.cmd](args)


if __name__ == "__main__":
    main()
