"""Fixed-scene comparison and observed CuRobo acceleration; no training changes."""
from __future__ import annotations

import copy
import csv
import functools
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import weakref

try:
    from .eval_state import read, digest, signature, durable_json
except ImportError:
    from eval_state import read, digest, signature, durable_json

TASKS = ["put_back_block", "swap_blocks"]
STEPS = [0, 500, 1000, 1500, 2000]


def comparison_spec(cfg):
    """Selection is a subset of exported weights, independent of training milestones."""
    value = cfg.get("comparison", {"tasks": TASKS, "steps": STEPS,
                                   "episodes_per_task": cfg["closed_loop"]["internal_episodes"]})
    steps = value.get("steps")
    if (value.get("tasks") != TASKS or not isinstance(steps, list) or not steps
            or any(type(step) is not int or step not in STEPS for step in steps)
            or len(set(steps)) != len(steps) or not any(step > 0 for step in steps)
            or value.get("episodes_per_task") != 10
            or cfg["closed_loop"]["internal_episodes"] != 10):
        raise ValueError("Comparison requires the two tasks, 10 shared scenes/task, and unique exported candidate steps")
    return {"tasks": list(TASKS), "steps": list(steps), "episodes_per_task": 10}


def package_inventory():
    """Simulator Python only; no renderer, warmup or parameter updates."""
    import importlib
    import importlib.metadata as metadata
    import torch
    result = {"python": sys.version, "executable": sys.executable,
              "torch": torch.__version__, "cuda": torch.version.cuda,
              "driver": subprocess.check_output(["nvidia-smi", "--query-gpu=uuid,name,driver_version",
                                                    "--format=csv,noheader"], text=True).strip(), "packages": {}}
    for module, distribution in (("sapien", "sapien"), ("mplib", "mplib"),
                                 ("curobo", "nvidia-curobo"), ("pytorch3d", "pytorch3d"), ("warp", "warp-lang")):
        loaded = importlib.import_module(module)
        root = Path(loaded.__file__).resolve().parent
        files = {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob("*"))
                 if p.is_file() and p.suffix in (".py", ".so", ".yaml", ".yml", ".json")}
        result["packages"][module] = {"version": metadata.version(distribution), "root": str(root), "files": files}
    return result


def runtime_binding(cfg):
    from .eval_parallel import simulator_environment, gpu_inventory
    gpu = cfg.get("selection_runtime", {}).get("gpu_index", 0)
    environment = simulator_environment(cfg, gpu_inventory()[gpu])
    result = subprocess.run([cfg["closed_loop"]["simulator_python"], str(Path(__file__).resolve()), "inventory"],
                            env=environment, capture_output=True, text=True, check=True, timeout=180)
    rows = [line[len("INVENTORY="):] for line in result.stdout.splitlines() if line.startswith("INVENTORY=")]
    if len(rows) != 1:
        raise ValueError(f"Simulator inventory missing: {result.stdout}\n{result.stderr}")
    value = json.loads(rows[0])
    if not value["torch"].startswith("2.6.0") or value["cuda"] != "12.6":
        raise ValueError("Fused profile requires the isolated PyTorch 2.6.0/cu126 simulator; finish prepare_fused_env.sh first. No planner was started.")
    return value


def observe_fused_backend(LBFGSOpt, MotionGen):
    """Observe successful graph calls and effective flags without changing tensors."""
    import torch
    refs, counts, graphs = [], {"captures": 0, "replays": 0}, {}
    original_init = LBFGSOpt.__init__

    @functools.wraps(original_init)
    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        refs.append(weakref.ref(self))
    LBFGSOpt.__init__ = init
    for name, counter in (("capture_end", "captures"), ("replay", "replays")):
        original = getattr(torch.cuda.CUDAGraph, name)
        def observed(self, *args, _original=original, _counter=counter, **kwargs):
            value = _original(self, *args, **kwargs)
            counts[_counter] += 1
            graphs.setdefault(id(self), {"captures": 0, "replays": 0})[_counter] += 1
            return value
        setattr(torch.cuda.CUDAGraph, name, observed)
    warmup = MotionGen.warmup

    @functools.wraps(warmup)
    def checked_warmup(self, *args, **kwargs):
        before = dict(counts)
        value = warmup(self, *args, **kwargs)
        effective = []
        for ref in refs:
            opt = ref()
            if opt is None:
                continue
            switches = {key: bool(getattr(opt, key, False)) for key in
                        ("use_cuda_kernel", "use_cuda_line_search_kernel", "use_cuda_update_best_kernel", "use_cuda_graph")}
            d_opt = int(getattr(opt, "d_opt", 0))
            history = int(getattr(opt, "history", 0))
            guard = not switches["use_cuda_line_search_kernel"] and d_opt >= 1024
            lbfgs_guard = not switches["use_cuda_kernel"] and (d_opt >= 1024 or history > 31 or (d_opt*history+33)*4 >= 48000)
            graph = getattr(opt, "cu_opt_graph", None)
            effective.append({**switches, "d_opt": d_opt, "history": history, "native_line_search_guard": guard,
                              "native_lbfgs_guard": lbfgs_guard, "graph_object_created": graph is not None,
                              "graph_calls": graphs.get(id(graph), {"captures": 0, "replays": 0})})
            if ((not switches["use_cuda_kernel"] and not lbfgs_guard) or not switches["use_cuda_update_best_kernel"] or
                    (not switches["use_cuda_line_search_kernel"] and not guard)):
                raise RuntimeError(f"Fused backend unexpectedly disabled: {effective[-1]}")
        if not effective or not any(r["use_cuda_kernel"] for r in effective) or not any(
                r["use_cuda_graph"] and min(r["graph_calls"].values()) > 0 for r in effective):
            raise RuntimeError(f"Warmup did not demonstrate LBFGS graph capture/replay: {counts}, {effective}")
        extensions = {name: {"path": str(Path(module.__file__).resolve()), "sha256": digest(module.__file__)}
                      for name, module in list(sys.modules.items())
                      if name.startswith("curobo") and str(getattr(module, "__file__", "")).endswith(".so")}
        if not extensions:
            raise RuntimeError("No loaded CuRobo native extension observed")
        root = os.environ.get("MEMORY_S1_PROGRESS_ROOT")
        if not root:
            raise RuntimeError("Fused backend requires a progress/evidence directory")
        row = {"pid": os.getpid(), "passed": True, "effective": effective, "extensions": extensions,
               "graphs": dict(counts), "warmup_graph_calls": {k: counts[k]-before[k] for k in counts},
               "launch_blocking": os.environ.get("CUDA_LAUNCH_BLOCKING"),
               "batch": kwargs.get("batch", args[0] if args else 1)}
        if row["launch_blocking"] is not None:
            raise RuntimeError("CUDA_LAUNCH_BLOCKING unexpectedly set in planner")
        durable_json(Path(root) / f"fused_backend_{os.getpid()}_{time.time_ns()}.json", row)
        print(f"[fused verified] pid={os.getpid()} optimizers={len(effective)} captures={counts['captures']} replays={counts['replays']}", flush=True)
        return value
    MotionGen.warmup = checked_warmup


def inherit_scenes(cfg, root):
    """Only the explicitly recorded runtime backend changes; scene records do not."""
    from .eval_parallel import protocol
    from .integration_contract import simulator_sources
    source = Path(cfg["selection_runtime"]["frozen_scenes"])
    prior, expected = read(source), protocol(cfg, "internal")
    def scene_contract(value):
        return {k: v for k, v in value.items() if k not in ("simulator_backend", "scene_filter_backend")}
    if scene_contract(prior["contract"]) != scene_contract(expected):
        raise ValueError("Frozen scene/source/camera/instruction protocol changed; no new seeds generated")
    scenes = prior["scenes"]
    if len(scenes) != 20 or set(s["task"] for s in scenes) != set(TASKS):
        raise ValueError("Expected existing two-task, twenty-scene bank")
    for task in TASKS:
        selected = [s for s in scenes if s["task"] == task]
        if len(selected) != 10 or len({s["seed"] for s in selected}) != 10 or sorted(s["ordinal"] for s in selected) != list(range(10)):
            raise ValueError(f"Incomplete/duplicate frozen scenes: {task}")
        if any(not s.get("instruction") or not isinstance(s.get("episode_info"), dict) for s in selected):
            raise ValueError("Frozen instructions/expert provenance missing")
    admission_path = Path(cfg["paths"]["run"]) / "integration_admission.json"
    admission, assets_sha = read(admission_path), simulator_sources(cfg)
    if admission.get("passed") is not True or admission["binding"]["simulator_source_sha"] != assets_sha:
        raise ValueError("Task/asset/robot files differ from admitted run; preserve and inspect differences")
    lineage = {"source": str(source.resolve()), "source_sha256": digest(source), "source_contract": prior["contract"],
               "scenes_sha256": signature(scenes), "simulator_assets_sha256": assets_sha,
               "admission_sha256": digest(admission_path), "new_backend": expected["simulator_backend"],
               "note": "Existing expert-filtered scenes retained; old scores are not imported."}
    destination = Path(root) / "frozen_scenes.json"
    value = {"contract": expected, "scenes": scenes}
    if destination.exists() and read(destination) != value:
        raise ValueError("A different frozen bank exists in this output")
    durable_json(destination, value)
    durable_json(Path(root) / "SCENE_INHERITANCE.json", lineage)
    print("[scenes] reused 20 frozen scenes (10/task); expert search skipped", flush=True)
    return destination


def qualification_key(cfg):
    from .common import code_version
    from .integration_contract import simulator_sources
    return {"kind": "fused-functional-v1", "source": code_version(cfg["root"]),
            "environment": cfg["selection_runtime"]["environment"],
            "scenes_sha256": digest(cfg["selection_runtime"]["frozen_scenes"]),
            "simulator_assets_sha256": simulator_sources(cfg),
            "base_sha256": digest(cfg["paths"]["base"]), "stats_sha256": digest(cfg["paths"]["stats"])}


def qualify_fused(cfg, run, root, weights, args):
    import yaml
    from .posttrain import closed_child
    from .eval_state import EpisodeQueue
    scene_file = inherit_scenes(cfg, root)
    current = copy.deepcopy(cfg)
    current["selection_runtime"]["qualification"] = True
    current["diagnostic"] = {"scenes_from": str(scene_file), "episodes_per_task": 1, "max_targets": 32, "record_feedback": True,
                             "capture_evidence": bool(cfg.get('diagnosis'))}
    path = Path(root) / "fused_prefix.yaml"
    path.write_text(yaml.safe_dump(current, sort_keys=False), encoding="utf-8")
    group = Path(root) / "qualification/fused"
    closed_child(path, weights[2000], root, group, "diagnostic", ["full"], args)
    queue = EpisodeQueue(group)
    state = queue.snapshot()
    if len(state["jobs"]) != 2 or any(j["state"] != "complete" for j in state["jobs"]):
        raise ValueError("Fused qualification needs one completed short prefix per task")
    evidence, timings = {}, []
    for job in state["jobs"]:
        result = queue.result(job, state["identity"])
        attempt = group / job["directory"]
        actions = [json.loads(s) for s in (attempt / "executed_actions.jsonl").read_text().splitlines()]
        if not actions or len(actions) != result["executed_targets"]:
            raise ValueError("Short prefix did not record executed targets")
        if [r["completed_target_id"] for r in actions] != list(range(1, len(actions)+1)):
            raise ValueError("Action/reset counter mismatch")
        for row in actions:
            for key in ("target", "physical_before", "physical_after"):
                if len(row[key]) != 14 or not all(math.isfinite(x) for x in row[key]):
                    raise ValueError(f"Invalid physical/action data: {key}")
        decisions = [json.loads(s) for s in (attempt / "decisions.jsonl").read_text().splitlines()]
        if not decisions or decisions[0]["frame_id"] != 0 or decisions[0]["raw_archive_frames"] != 1:
            raise ValueError("Memory reset evidence missing")
        if any(i > r["frame_id"] for r in decisions for i in r["read_frame_ids"]):
            raise ValueError("Future history read")
        timings.append({"task": result["task"], "wall_seconds": result["wall_seconds"], "timings": result["timings"]})
        for name in ("result.json", "executed_actions.jsonl", "decisions.jsonl", "qualification_trace.jsonl"):
            evidence[str((attempt / name).relative_to(root))] = digest(attempt / name)
    backend_files = list((group / "simulator_progress").rglob("fused_backend_*.json"))
    if len(backend_files) < 2:
        raise ValueError("Missing both-arm warmup evidence")
    for path in backend_files:
        record = read(path)
        if not record["passed"] or record["launch_blocking"] is not None or min(record["graphs"].values()) <= 0:
            raise ValueError(f"Incomplete fused/graph evidence: {path}")
        evidence[str(path.relative_to(root))] = digest(path)
    durable_json(Path(root) / "QUALIFICATION.json", {"passed": True, "binding": qualification_key(cfg),
                 "directory": str(root), "files": evidence, "timings": timings,
                 "scope": "Two functional prefixes, at most 32 targets each; no old-backend bit-equivalence or success-rate claim."})
    print("[qualification] fused kernels and actual graph capture/replay verified; 2/2 prefixes complete", flush=True)


def comparison_table(root, cfg, identity, render=False):
    """Never turn missing results into failures or publish a partial average."""
    from .eval_state import EpisodeQueue
    root, rows = Path(root), []
    spec = comparison_spec(cfg)
    for step in spec["steps"]:
        label = "base" if step == 0 else f"step_{step:06d}"
        folder = root / "selection" / label
        row = {"model": label, "step": step, "complete": False, "mean_success_rate": None, "tasks": {}}
        completed, states = [], {}
        if (folder / "queue.json").exists():
            queue = EpisodeQueue(folder)
            state = queue.snapshot()
            if len(state["jobs"]) != 20:
                raise ValueError("Comparison queue must contain twenty episodes/model")
            for job in state["jobs"]:
                states[job["state"]] = states.get(job["state"], 0)+1
                if job["state"] == "complete":
                    result = read(folder / job["directory"] / "result.json")
                    if result.get("status") != "complete" or result.get("diagnostic_prefix") or result.get("termination") not in ("success", "official_target_limit"):
                        raise ValueError("Prefix/invalid result cannot enter comparison")
                    if render:
                        queue.result(job, state["identity"])
                    completed.append(result)
        for task in TASKS:
            selected = [r for r in completed if r["task"] == task]
            successes = sum(r["success"] for r in selected)
            row["tasks"][task] = {"completed": len(selected), "planned": 10, "successes": successes,
                                   "success_rate": successes/10 if len(selected) == 10 else None}
        row["states"] = states
        row["complete"] = all(r["completed"] == 10 for r in row["tasks"].values())
        if row["complete"]:
            # Equal task denominators: integer-count formulation avoids rounding
            # disagreement with the existing 20-episode summary.
            row["mean_success_rate"] = sum(r["successes"] for r in row["tasks"].values())/20
        rows.append(row)
    value = {"identity": identity, "complete": all(r["complete"] for r in rows),
             "planned_episodes": len(spec["steps"]) * len(TASKS) * spec["episodes_per_task"],
             "comparison": spec,
             "scope": "two-task candidate comparison; not an independent final test", "models": rows}
    if (root / "BEST.json").exists():
        best = read(root / "BEST.json")
        if best["identity"] != identity:
            raise ValueError("BEST belongs to another comparison")
        value["best_step"] = best["step"]
        value["tied_success_steps"] = best["tied_success_steps"]
    durable_json(root / "comparison.json", value)
    columns = ["model", "put_back_block", "swap_blocks", "mean_success_rate", "completed", "errors"]
    temporary = root / "comparison.csv.partial"
    with temporary.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            label = row["model"] + (" (ours_best)" if row["step"] == value.get("best_step") else "")
            flat = {"model": label, "completed": sum(r["completed"] for r in row["tasks"].values()),
                    "errors": row["states"].get("error", 0), "mean_success_rate": "pending"}
            for task, metrics in row["tasks"].items():
                flat[task] = (f"{metrics['successes']}/10 ({metrics['success_rate']:.0%})" if metrics["success_rate"] is not None
                              else f"pending ({metrics['completed']}/10; {metrics['successes']} successes)")
            if row["complete"]:
                flat["mean_success_rate"] = f"{row['mean_success_rate']:.0%}"
            writer.writerow(flat)
    temporary.replace(root / "comparison.csv")
    if render:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        with (root / "comparison.csv").open(encoding="utf-8-sig") as stream:
            cells = list(csv.reader(stream))
        fig, ax = plt.subplots(figsize=(13, 3.5))
        ax.axis("off")
        table = ax.table(cellText=cells[1:], colLabels=cells[0], loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.auto_set_column_width(range(len(columns)))
        table.scale(1, 1.8)
        ax.set_title("Two RMBench tasks, 10 shared scenes/task; checkpoint selection results")
        fig.savefig(root / "comparison.png", dpi=180, bbox_inches="tight")
        plt.close(fig)
    return value


if __name__ == "__main__":
    if sys.argv[1:] != ["inventory"]:
        raise SystemExit("Usage: fused_evaluation.py inventory")
    print("INVENTORY=" + json.dumps(package_inventory(), sort_keys=True))
