"""Explicit paired 128-update sampling experiment on the existing H100 cache."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import csv
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tarfile
import time
import traceback

from .grasp_bridge import (alive, checked_path, files, owned_popen, process, read,
                           sha, signature, stop_children, stop_owned_tree, verify, write)
from .memory_probe import archive_manifest, copy_verified, runtime, sources
from .memory_repair import simulator_runtime
from .stage_sampling_math import BRANCHES, TASKS, draw, event_partition, validation_anchors

PROFILE = "configs/memory_s1/stage_sampling_h100.json"
STAGES = ("prepare", "baseline", "fit", "evaluate", "physical", "report", "pack")
TOOLS = (PROFILE, "scripts/memory_s1/portable/h100/stage_sampling.sh",
         "src/fastwam/memory_s1/stage_sampling_pilot.py", "src/fastwam/memory_s1/stage_sampling_worker.py",
         "src/fastwam/memory_s1/stage_sampling_math.py", "src/fastwam/memory_s1/checkpoint.py",
         "src/fastwam/memory_s1/evaluate.py", "src/fastwam/memory_s1/train.py",
         "src/fastwam/memory_s1/grasp_causal_worker.py", "src/fastwam/memory_s1/grasp_causal_metrics.py",
         "src/fastwam/memory_s1/initial_intervention_worker.py", "src/fastwam/memory_s1/memory_repair_worker.py",
         "src/fastwam/memory_s1/selection_runtime.py", "src/fastwam/memory_s1/eval_parallel.py",
         "src/fastwam/memory_s1/simulator_backend.py", "src/fastwam/memory_s1/fused_evaluation.py",
         "scripts/memory_s1/sim_eval.py", "scripts/memory_s1/sim_executor.py", "scripts/memory_s1/sim_feedback.py",
         "scripts/memory_s1/sim_instrumentation.py", "scripts/memory_s1/deploy_policy.py")


def profile(root):
    spec = read(root / PROFILE)
    if (spec["schema"] != "stage-sampling-pilot-v1" or spec["machine"] != "h100"
            or spec["branches"] != list(BRANCHES) or spec["source_update"] != 2000
            or spec["updates_per_branch"] != 128 or spec["global_batch"] != 16
            or spec["micro_batch"] != 2 or spec["checkpoint_every"] != 32
            or spec["validation_episodes_per_task"] != 2 or spec["validation_noises"] != 3
            or spec["expert_prefix_targets"] != 48 or spec["target_cap"] != 128
            or spec["event_threshold"] != .5 or spec["event_horizon"] != 32
            or spec["optimizer"] != "inherit_step2000_adamw_moments_terminal_lr"):
        raise ValueError("Expected two original-architecture branches, inherited AdamW, 128 updates, global16=2x8")
    for key in ("output", "historical"):
        if not checked_path(root, spec[key]).is_relative_to(root / "outputs"):
            raise ValueError("Pilot directories must remain under outputs")
    return spec


def boundary(output):
    if (output / "STOP.json").exists():
        raise InterruptedError("Pilot stop requested; checkpoint at complete optimizer boundary; resume explicitly")


def stage_result(output, stage, bound, required=False):
    directory = output / stage
    marker = directory / "COMPLETE.json"
    if not marker.exists():
        if required:
            raise ValueError(f"Required stage incomplete: {stage}; inspect its log/status")
        return None
    receipt = read(marker)
    if receipt["identity"] != signature(bound):
        raise ValueError(f"Stage identity differs: {directory}")
    verify(directory, receipt["files"])
    return read(directory / "result.json")


def prepare(root, output, spec):
    import numpy as np
    import torch
    from .checkpoint import verified_load
    from .common import fingerprint, make_cache_contract, seed_for
    from .data import choose_instruction, read_episode, _file_stamp
    from .history import evaluation_phase, training_period, training_phase, recipe, select_ids
    from .integration_contract import simulator_sources
    from .grasp_causal import reviewed_archive
    old = checked_path(root, spec["historical"])
    if alive(read(old / "LAUNCH.json").get("owner")):
        raise ValueError("Historical source is still running")
    candidates = sorted((old / "packages").glob("*/grasp_causal.tar.gz"))
    archive = next((p for p in candidates if sha(p) == spec["historical_archive_sha256"]), None)
    if archive is None:
        raise FileNotFoundError("The reviewed causal archive is missing; preserve prior packages")
    manifest = archive_manifest(archive, spec["historical_archive_sha256"], "FILES.json")
    verify(old, {"IDENTITY.json": manifest["IDENTITY.json"], "REPORT.json": manifest["REPORT.json"]})
    prior = read(old / "IDENTITY.json")
    cfg = copy.deepcopy(prior["config"])
    for key, digest in prior["resources"].items():
        if sha(cfg["paths"][key]) != digest: raise ValueError(f"Model resource changed: {key}")
    verify(cfg["paths"]["tokenizer"], prior["tokenizer_files"])
    if sources(root) != prior["sources"] or runtime() != prior["runtime"]:
        raise ValueError("Original production sources/model runtime changed")
    if (simulator_runtime(cfg) != prior["simulator_runtime"] or simulator_sources(cfg) != prior["simulator_sources"]
            or cfg["history"]["train_min"] != 1 or cfg["history"]["train_max"] != 16
            or cfg["history"]["train_phase"] != "uniform" or cfg["history"]["online_period"] != 8):
        raise ValueError("Simulator or original random T/phase recipe differs")
    prepared, cache_root = Path(cfg["paths"]["prepared"]), Path(cfg["paths"]["cache"])
    data, approval, cache = read(prepared / "manifest.json"), read(prepared / "alignment_approved.json"), read(cache_root / "manifest.json")
    if (approval.get("approved") is not True or approval["manifest_sha"] != fingerprint(data)
            or cache["signature"] != fingerprint(make_cache_contract(cfg, data))
            or cache["contract"]["prepared_sha"] != fingerprint(data)):
        raise ValueError("Prepared approval and dense-cache encoding contract do not match")
    by_id = {r["episode_id"]: r for r in data["episodes"]}
    if len(by_id) != 100 or len(cache["episodes"]) != 100 or {r["episode_id"] for r in cache["episodes"]} != set(by_id):
        raise ValueError("Expected all 100 original episodes and no duplicate/missing cache records")
    for task in TASKS:
        for split, count in (("train", 45), ("val", 5)):
            if sum(r["task"] == task and r["split"] == split for r in data["episodes"]) != count:
                raise ValueError(f"Unexpected original split: {task}/{split}")
    source_run = Path(cfg["paths"]["run"])
    pointer = read(source_run / "LATEST_LOCAL.json")
    checkpoint = checked_path(source_run, pointer["directory"]) / "resume.pt"
    source = verified_load(checkpoint)
    weights = checked_path(root, prior["weights"]["step_002000"]["relative"])
    verify(root, {prior["weights"]["step_002000"]["relative"]: prior["weights"]["step_002000"]["sha256"]})
    weight = torch.load(weights, map_location="cpu", weights_only=True)
    if (pointer["step"] != 2000 or source["completed_updates"] != 2000 or source["sampler_next_update"] != 2000
            or source["identity"]["cache_signature"] != cache["signature"] or source["identity"]["data_sha"] != fingerprint(data)
            or set(source["memory"]) != set(weight["memory"])
            or any(not torch.equal(v, weight["memory"][k]) for k, v in source["memory"].items())):
        raise ValueError("Complete step2000 optimizer point differs from the reviewed weight/data/cache")
    for key in ("base", "stats"):
        if source["identity"][key + "_sha256"] != prior["resources"][key]:
            raise ValueError("Original optimizer point references different model resources")
    groups = source["optimizer"]["param_groups"]
    if (not source["optimizer"]["state"] or not source["rng_states"]
            or any(g["betas"] != (.9, .95) or abs(g["lr"] - cfg["min_learning_rate"]) > 1e-12 for g in groups)
            or len(source["rng_states"]) != 1 or source["config"]["seed"] != cfg["seed"]
            or recipe(source["config"]) != recipe(cfg)):
        raise ValueError("Expected original AdamW moments, RNG states and terminal learning rate")
    planned_bytes=10*checkpoint.stat().st_size+2*weights.stat().st_size+5*2**30
    if shutil.disk_usage(output).free < max(spec["local_reserve_gib"] * 2**30,planned_bytes):
        raise ValueError("Need at least 20 GiB free for paired private recovery points; no HF training uploads")
    bound = {"protocol": spec, "config": cfg, "sources": sources(root), "runtime": runtime(),
             "tools": {name: sha(root / name) for name in TOOLS}, "historical_identity": signature(prior),
             "weights": prior["weights"], "resources": prior["resources"], "tokenizer_files": prior["tokenizer_files"],
             "simulator_runtime": prior["simulator_runtime"], "simulator_sources": prior["simulator_sources"],
             "simulator_extensions": prior["simulator_extensions"],
             "prepared_sha256": sha(prepared / "manifest.json"), "approval_sha256": sha(prepared / "alignment_approved.json"),
             "cache_manifest_sha256": sha(cache_root / "manifest.json"),
             "source_checkpoint": {"relative": str(checkpoint.relative_to(root)), "sha256": sha(checkpoint),
                                   "complete_sha256": sha(checkpoint.parent / "complete.json"), "identity": source["identity"]},
             "terminal_lr": [g["lr"] for g in groups], "inherited_optimizer_states": len(source["optimizer"]["state"]),
             "git_commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
             "scope": spec["scope"]}
    del source, weight
    if (output / "IDENTITY.json").exists() and read(output / "IDENTITY.json") != bound:
        raise ValueError("Pilot identity changed; preserve this experiment and use a new output")
    if (output / "PREPARED.json").exists():
        verify(output, read(output / "PREPARED.json")["files"])
        print("[reuse] original split, paired plan and frozen validation inputs verified", flush=True); return
    inventory, stamps, prepared_files = {}, {}, {}
    started = time.monotonic()
    for i, record in enumerate(cache["episodes"]):
        boundary(output)
        raw = by_id[record["episode_id"]]
        for name in ("task", "raw", "raw_sha256", "length", "instruction", "split", "camera_paths"):
            if record[name] != raw[name]:
                raise ValueError(f"Cache/prepared episode field differs: {record['episode_id']}/{name}")
        path = checked_path(root, raw["raw"]); verify(root, {raw["raw"]: raw["raw_sha256"]})
        states, targets, cameras, kind, attributes, embedded = read_episode(path)
        instruction, _ = choose_instruction(path, embedded)
        if cameras != raw["camera_paths"] or kind != raw["source_kind"] or instruction != raw["instruction"] or len(states) != raw["length"]:
            raise ValueError("Raw training semantics differ from approved data")
        descriptor = checked_path(cache_root, record["file"])
        verify(cache_root, {record["file"]: record["cache_sha256"]})
        values = torch.load(descriptor, map_location="cpu", weights_only=True)
        anchors = values["anchors"].tolist()
        native_path=checked_path(prepared,record["file"])
        native=torch.load(native_path,map_location="cpu",weights_only=True)
        if (not np.array_equal(native["states"].numpy(),states) or not np.array_equal(native["targets"].numpy(),targets)
                or native["anchors"].tolist() != anchors):
            raise ValueError(f"Prepared state/action/anchor differs from raw source: {record['episode_id']}")
        prepared_files[record["file"]]={"sha256":sha(native_path),"stamp":list(_file_stamp(native_path))}
        del native
        if (values["signature"] != cache["signature"] or values["shards"] != record["shards"]
                or not np.array_equal(values["targets"].numpy(), targets)):
            raise ValueError(f"Cached actions/encoder identity differ: {record['episode_id']}")
        mapping = {record["file"]: record["cache_sha256"], **{x["file"]: x["sha256"] for x in record["shards"]}}
        verify(cache_root, mapping)
        for name, digest in mapping.items():
            stamps[name] = {"sha256": digest, "stamp": list(_file_stamp(checked_path(cache_root, name)))}
        inventory[record["episode_id"]] = {**event_partition(states, targets, anchors),
            "episode_id": record["episode_id"], "task": record["task"], "split": record["split"],
            "episodes_in_task": sum(r["task"] == record["task"] and r["split"] == record["split"] for r in cache["episodes"])}
        print(f"[data/cache] {i+1}/100 {record['episode_id']} split={record['split']} "
              f"bins={ {k:len(v) for k,v in inventory[record['episode_id']]['bins'].items()} } "
              f"elapsed={time.monotonic()-started:.1f}s ETA~{(time.monotonic()-started)/(i+1)*(99-i):.0f}s", flush=True)
    original_log=source_run/"samples.jsonl"
    original_audit={"available":False,"reason":"original sampling log missing; exposure is unknown"}
    if original_log.is_file():
        seen=set(); frequencies=Counter(); initials=Counter(); periods=Counter()
        for line in original_log.read_text(encoding="utf-8").splitlines():
            row=json.loads(line); key=(row["step"],row["global_slot"])
            record=inventory[row["episode_id"]]
            if (key in seen or not 1 <= row["step"] <= 2000 or not 0 <= row["global_slot"] < 16
                    or record["split"] != "train" or row["task"] != record["task"]
                    or row["anchor"] not in record["anchors"]
                    or row["frame_ids"] != select_ids(range(row["anchor"]+1),row["anchor"],row["T"],phase=row["phase"])):
                raise ValueError("Original sampling log has duplicate slots, non-training data, or history mismatch")
            kind=next(k for k,v in record["bins"].items() if row["anchor"] in v)
            seen.add(key); frequencies[(row["task"],kind)]+=1; periods[row["T"]]+=1
            if row["anchor"] == 0: initials[row["episode_id"]]+=1
        if len(seen) != 32000: raise ValueError(f"Original sample log incomplete: {len(seen)}/32000; preserve the source and recover its log")
        original_audit={"available":True,"source":str(original_log),"sha256":sha(original_log),"samples":len(seen),
            "event_bin_counts":{f"{t}/{k}":n for (t,k),n in frequencies.items()},"initial_anchor_exposures":dict(initials),
            "T_counts":dict(periods),"phase_coverage":"command transition bins; successful physical grasp coverage unknown"}
    plan = {branch: [] for branch in BRANCHES}
    for u in range(spec["updates_per_branch"]):
        step = spec["source_update"] + u
        for slot in range(16):
            task = TASKS[(step + slot) % 2]
            eligible = [r for r in cache["episodes"] if r["task"] == task and r["split"] == "train"]
            rng = np.random.default_rng(seed_for(cfg["seed"], step, slot, "sample"))
            record = eligible[int(rng.integers(len(eligible)))]; info = inventory[record["episode_id"]]
            T = training_period(cfg, step, slot); phase = training_phase(cfg, step, slot, T)
            for branch in BRANCHES:
                anchor, stage, original = draw(info, step, slot, branch, cfg["seed"], seed_for)
                plan[branch].append({"update": u+1, "sampling_update": step, "global_slot": slot,
                    "episode_id": record["episode_id"], "task": task, "anchor": anchor, "event_bin": stage,
                    "original_anchor": original, "T": T, "phase": phase,
                    "noise_seed": seed_for(cfg["seed"], step, slot, "noise"), "split": "train"})
    windows = []
    for task in TASKS:
        eligible = sorted((v for v in inventory.values() if v["task"] == task and v["split"] == "val"), key=lambda v:v["episode_id"])
        for record in eligible[:spec["validation_episodes_per_task"]]:
            for anchor, stage in validation_anchors(record):
                windows.append({"id": record["episode_id"].replace("/", "_")+f"_{anchor:04d}",
                    "episode_id": record["episode_id"], "task": task, "split": "val", "anchor": anchor, "stage": stage,
                    "T": 8, "phase": evaluation_phase(cfg, 8, record["episode_id"], "stage-pilot-heldout")})
    repair = checked_path(root, prior["protocol"]["repair_output"])
    rm = archive_manifest(reviewed_archive(repair, prior["protocol"]["repair_archive_sha256"]),
                          prior["protocol"]["repair_archive_sha256"], "FILES.json")
    copy_verified(repair, "frozen/FROZEN.json", rm, output / "frozen/FROZEN.json")
    frozen = read(output / "frozen/FROZEN.json")
    for task in TASKS:
        item = frozen["inputs"][task + "_online_initial"]
        record = frozen["experts"][task]
        for name in [record["path"], *item["images"]]:
            copy_verified(repair, "frozen/"+name, rm, output / "frozen" / name)
        expert = read(output / "frozen" / record["path"])
        if len(expert["targets"]) < spec["target_cap"] + 16 or spec["objects"][task] not in expert["initial"]["objects"]:
            raise ValueError("Same-scene expert/target object/horizon missing")
    for name in ("manifest.json", "alignment_approved.json"):
        shutil.copy2(prepared / name, output / ("prepared_" + name))
    write(output / "INVENTORY.json", inventory); write(output / "CACHE_VERIFIED.json", stamps)
    write(output / "PREPARED_DATA_FILES.json", prepared_files)
    write(output / "ORIGINAL_SAMPLING_AUDIT.json", original_audit)
    write(output / "CAPACITY.json", {"free_bytes":shutil.disk_usage(output).free,"planned_local_bytes":planned_bytes,
          "reserve_gib":spec["local_reserve_gib"],"hf_upload_started":False})
    write(output / "SAMPLE_PLAN.json", plan); write(output / "VALIDATION.json", windows); write(output / "IDENTITY.json", bound)
    mapping = {n: sha(output/n) for n in ("IDENTITY.json", "INVENTORY.json", "CACHE_VERIFIED.json", "PREPARED_DATA_FILES.json", "ORIGINAL_SAMPLING_AUDIT.json", "CAPACITY.json", "SAMPLE_PLAN.json", "VALIDATION.json",
               "prepared_manifest.json", "prepared_alignment_approved.json")}
    mapping.update({"frozen/"+name: digest for name,digest in files(output/"frozen").items()})
    write(output / "PREPARED.json", {"identity": signature(bound), "files": mapping})
    print(f"[prepared] 90 train episodes; <=16 held-out windows={len(windows)}; "
          "2x128 updates; inherited AdamW; no online expert trajectory in training", flush=True)


def require_prepared(root, output):
    from .integration_contract import simulator_sources
    bound = read(output / "IDENTITY.json")
    cfg = bound["config"]
    if (bound["protocol"] != profile(root) or bound["sources"] != sources(root) or bound["runtime"] != runtime()
            or bound["tools"] != {name:sha(root/name) for name in TOOLS}
            or bound["simulator_runtime"] != simulator_runtime(cfg) or bound["simulator_sources"] != simulator_sources(cfg)):
        raise ValueError("Pilot code/config/runtime changed; do not mix partial experiments")
    verify(output, read(output/"PREPARED.json")["files"])
    from .data import _file_stamp
    for name, record in read(output/"PREPARED_DATA_FILES.json").items():
        path=checked_path(Path(cfg["paths"]["prepared"]),name)
        if list(_file_stamp(path)) != record["stamp"]: raise ValueError(f"Prepared file changed after raw-data audit: {path}")
    for field, folder, name in (("prepared_sha256", "prepared", "manifest.json"), ("approval_sha256", "prepared", "alignment_approved.json"),
                                ("cache_manifest_sha256", "cache", "manifest.json")):
        if sha(Path(cfg["paths"][folder])/name) != bound[field]: raise ValueError(f"Changed {field}")
    for record in bound["weights"].values(): verify(root, {record["relative"]:record["sha256"]})
    cp = bound["source_checkpoint"]; verify(root, {cp["relative"]:cp["sha256"]})
    if sha(checked_path(root,cp["relative"]).parent/"complete.json") != cp["complete_sha256"]: raise ValueError("Source checkpoint marker changed")
    for key,digest in bound["resources"].items():
        if sha(cfg["paths"][key]) != digest: raise ValueError(f"Model resource changed: {key}")
    verify(cfg["paths"]["tokenizer"], bound["tokenizer_files"])
    for record in bound["simulator_extensions"].values():
        if sha(record["path"]) != record["sha256"]: raise ValueError("Loaded fused extension changed")
    return bound


def compute(root, output, stage):
    bound = require_prepared(root, output); boundary(output)
    gpu = bound["runtime"]["gpu"].split(",")[0].strip()
    apps = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"], text=True)
    if any(line.split(",")[0].strip() == gpu for line in apps.splitlines()): raise ValueError("H100 occupied by another task")
    directory = output / stage; directory.mkdir(exist_ok=True)
    log = directory / f"worker_{time.time_ns()}.log"
    command = [sys.executable, "-B", "-u", "-m", "fastwam.memory_s1.stage_sampling_worker", stage,
               "--root", str(root), "--output", str(output), "--gpu-uuid", gpu]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu); env.pop("CUDA_LAUNCH_BLOCKING", None)
    started, seen = time.monotonic(), 0
    with log.open("w", encoding="utf-8") as stream:
        child = owned_popen(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            with log.open(encoding="utf-8", errors="replace") as reader:
                while child.poll() is None:
                    print(reader.read(), end="", flush=True)
                    # Fit observes STOP at the update boundary and publishes its own full point.
                    if stage != "fit": boundary(output)
                    if time.monotonic()-started > bound["protocol"]["stage_timeout_seconds"]:
                        write(output/"STOP.json", {"reason":"stage_wall_time_cap", "time":time.time()})
                        try: child.wait(timeout=120 if stage == "fit" else 5)
                        except subprocess.TimeoutExpired: pass
                        raise TimeoutError(f"Stage wall-time cap exceeded; inspect {log}")
                    if time.monotonic()-seen >= 15:
                        state = read(output/"PROGRESS.json") if (output/"PROGRESS.json").exists() else {}
                        print(f"[pilot {stage}] model={state.get('model','-')} phase={state.get('phase','model_load')} "
                              f"done={state.get('completed',0)}/{state.get('total','-')} "
                              f"elapsed={time.monotonic()-started:.0f}s ETA_seconds={state.get('eta_seconds')} "
                              f"scope={state.get('eta_scope','initialization; estimate not yet measured')}", flush=True); seen=time.monotonic()
                    time.sleep(1)
                print(reader.read(), end="", flush=True)
            if child.returncode and (output/"STOP.json").exists(): raise InterruptedError("Pilot stopped; verified local points/cases preserved")
            if child.returncode: raise RuntimeError(f"Pilot worker exited {child.returncode}: {log}\n{log.read_text(errors='replace')[-10000:]}")
            stage_result(output, stage, bound, required=True)
        finally: stop_children([child])


def report(output, bound):
    value = {s: stage_result(output,s,bound) for s in ("baseline","fit","evaluate","physical")}
    missing = [s for s,v in value.items() if v is None]
    if value["physical"] is None:
        partial=[]
        for task in TASKS:
            for label in ("expert","original",*BRANCHES):
                folder=output/"physical"/task/"cases"/label
                if not (folder/"COMPLETE.json").exists(): continue
                task_bound={**bound,"protocol":{**bound["protocol"],"task":task,"object":bound["protocol"]["objects"][task]}}
                expected=signature({"identity":signature(task_bound),"label":label,
                    "candidate_sha":None if label in ("expert","original") else read(output/"fit"/label/"CANDIDATE.json")["sha256"]})
                receipt=read(folder/"COMPLETE.json")
                if receipt["identity"] != expected: raise ValueError("Partial physical case identity mismatch")
                verify(folder,receipt["files"]); partial.append(read(folder/"result.json"))
        value["physical"]={"cases":partial,"partial":True,"completed":len(partial),"total":8}
    result = {"identity":signature(bound), "stages":value, "missing":missing, "required_complete":not missing,
              "original_sampler":read(output/"ORIGINAL_SAMPLING_AUDIT.json"),
              "training_only_original_train_split": True,
              "interpretation":"Compare held-out approach/closing errors and retained contact/lift separately. Neither lower FM nor one prefix proves a unique Q/architecture cause.",
              "benchmark_accuracy":None, "scope":bound["scope"]}
    measurements = [r for s in ("baseline","evaluate") for r in (value[s] or {}).get("cases",[])]
    original={(r["id"],r["noise_index"]):r for r in measurements if r["model"] == "original"}
    changes=[]
    for r in measurements:
        if r["model"] == "original": continue
        before=original[(r["id"],r["noise_index"])]; a=before["metrics"]["executed16"]; b=r["metrics"]["executed16"]
        changes.append({"model":r["model"],"task":r["task"],"window":r["id"],"stage":r["stage"],"noise_index":r["noise_index"],
            "arm_rmse_change_rad":b["arm_rmse_rad"]-a["arm_rmse_rad"],"gripper_mae_change":b["gripper_mae"]-a["gripper_mae"],
            "wrong_sign_elements_change":b["wrong_motion_sign_elements"]-a["wrong_motion_sign_elements"],
            "before_half_close":before["metrics"]["half_close_offset"],"after_half_close":r["metrics"]["half_close_offset"],
            "before_readout":before["readout"],"after_readout":r["readout"],"scope":"paired held-out window/noise; not a grasp-success label"})
    result["paired_changes"]=changes; write(output/"REPORT.json",result)
    with (output/"heldout.csv").open("w",newline="",encoding="utf-8") as stream:
        columns=("model","task","episode_id","stage","anchor","noise_index","arm_rmse_rad","gripper_mae","fm","valid_targets","wrong_motion_sign_elements")
        writer=csv.DictWriter(stream,fieldnames=columns); writer.writeheader()
        for r in measurements:
            writer.writerow({**{k:r[k] for k in columns[:6]}, **{k:r["metrics"]["executed16"][k] for k in columns[6:] if k != "fm"}, "fm":r["fm"]})
    with (output/"physical.csv").open("w",newline="",encoding="utf-8") as stream:
        columns=("model","task","executed_targets","first_close_target","max_lift_m","retained_contact_lift","termination")
        writer=csv.DictWriter(stream,fieldnames=columns); writer.writeheader()
        for r in (value["physical"] or {}).get("cases",[]):
            m=r["metrics"]; writer.writerow(dict(zip(columns,(r["model"],r["task"],m["executed_targets"],m["first_right_close_after_handoff"],m["max_lift_after_handoff_m"],m["lift_contact_proxy_observed"],r["termination"]))))
    print(f"[report] complete={not missing}; missing={missing}; main result is phase/behavior comparison, not benchmark acc",flush=True)


def pack(root, output, bound):
    report(output,bound); package=output/"packages"/str(time.time_ns()); package.mkdir(parents=True)
    excluded={"packages","tmp","checkpoints","interrupted","__pycache__","launches"}
    selected=[p for p in output.rglob("*") if p.is_file() and not p.is_symlink()
              and not set(p.relative_to(output).parts)&excluded and p.suffix != ".pt"
              and p.name not in ("job.lock","LAUNCH.json","latest_log.txt","LATEST_PACKAGE.json","STOP.json","STATUS.json")
              and not p.name.endswith((".partial",".tmp"))]
    copied=[]
    for name in sorted(set(bound["sources"])|set(TOOLS)):
        destination=package/"source"/name; destination.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/name,destination); copied.append(destination)
    mapping={p.relative_to(output).as_posix():sha(p) for p in selected}
    mapping.update({p.relative_to(package).as_posix():sha(p) for p in copied}); write(package/"FILES.json",mapping)
    archive=package/"stage_sampling.tar.gz"
    with tarfile.open(archive,"w:gz") as tar:
        for p in selected: tar.add(p,arcname=p.relative_to(output).as_posix(),recursive=False)
        for p in copied+[package/"FILES.json"]: tar.add(p,arcname=p.relative_to(package).as_posix(),recursive=False)
    digest=sha(archive); (package/"SHA256SUMS").write_text(digest+"  stage_sampling.tar.gz\n",encoding="utf-8")
    write(output/"LATEST_PACKAGE.json",{"archive":str(archive),"sha256":digest,"identity":signature(bound),
          "excluded":"large optimizer/candidate tensors; both candidates remain in fit/BRANCH/candidate.pt"})
    print(f"[package] {archive}\nSHA256={digest}",flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument("stage",choices=(*STAGES,"status","stop"))
    parser.add_argument("--root",type=Path,default=Path("/workspace/FastWAM")); parser.add_argument("--resume",action="store_true")
    args=parser.parse_args(); root=args.root.resolve(); spec=profile(root); output=checked_path(root,spec["output"]); output.mkdir(parents=True,exist_ok=True)
    launch=read(output/"LAUNCH.json") if (output/"LAUNCH.json").exists() else {}
    if args.stage == "status":
        print(json.dumps({"running":alive(launch.get("owner")),"launch":launch,
            "status":read(output/"STATUS.json") if (output/"STATUS.json").exists() else None,
            "progress":read(output/"PROGRESS.json") if (output/"PROGRESS.json").exists() else None,
            "stop":(output/"STOP.json").exists()},indent=2)); return
    if args.stage == "stop":
        write(output/"STOP.json",{"time":time.time(),"scope":"this isolated pilot only"})
        if launch.get("stage") == "fit" and alive(launch.get("owner")):
            print("Stop requested; fitting finishes its current update and saves a full local recovery point. Use wait.",flush=True)
        else: stop_owned_tree(launch.get("owner")); print("Owned pilot tree stopped; completed cases preserved",flush=True)
        return
    owner=process(os.getpgrp()); exit_path=os.environ.get("FW_STAGE_SAMPLING_EXIT","")
    if not owner or owner["pid"] != os.getppid() or os.getsid(0) != owner["pid"] or not exit_path or not Path(exit_path).resolve().is_relative_to(output/"launches"):
        raise ValueError("Use the owned nohup H100 stage_sampling.sh entry")
    if alive(launch.get("owner")) and launch["owner"]["pid"] != owner["pid"]: raise ValueError("Another pilot stage is active")
    if (output/"STOP.json").exists() and args.stage not in ("report","pack"):
        if not args.resume: raise InterruptedError("STOP present; use resume STAGE")
        (output/"STOP.json").rename(output/f"STOP.resumed_{time.time_ns()}.json")
    def stop_signal(*_): write(output/"STOP.json",{"time":time.time(),"reason":"launcher_signal"})
    for sig in (signal.SIGINT,signal.SIGTERM): signal.signal(sig,stop_signal)
    write(output/"LAUNCH.json",{"owner":owner,"worker":process(os.getpid()),"stage":args.stage,"started":time.time(),"argv":sys.argv})
    write(output/"STATUS.json",{"stage":args.stage,"state":"running"}); started=time.monotonic()
    try:
        if args.stage == "prepare": prepare(root,output,spec)
        elif args.stage in ("baseline","fit","evaluate","physical"): compute(root,output,args.stage)
        else:
            bound=require_prepared(root,output); report(output,bound) if args.stage == "report" else pack(root,output,bound)
        write(output/"STATUS.json",{"stage":args.stage,"state":"complete","seconds":time.monotonic()-started})
        print(f"[complete] {args.stage} seconds={time.monotonic()-started:.1f}",flush=True)
    except BaseException as error:
        write(output/"STATUS.json",{"stage":args.stage,"state":"interrupted" if isinstance(error,InterruptedError) else "error",
             "error":repr(error),"traceback":traceback.format_exc()})
        if isinstance(error,InterruptedError):
            print("[stopped] Verified completed cases/local optimizer points preserved; resume STAGE is explicit",flush=True)
            raise SystemExit(130)
        raise


if __name__ == "__main__": main()
