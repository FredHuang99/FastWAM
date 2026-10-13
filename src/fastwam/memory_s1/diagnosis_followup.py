"""Small follow-up diagnostics with explicit historical evidence provenance."""
from __future__ import annotations

import copy
import csv
import hashlib
import json
from pathlib import Path
import shutil
import time

from .common import atomic_json, fingerprint, read_json, sha256

REQUIRED = ("inventory", "offline", "paths", "gradients", "expert", "fixed", "recorded", "contacts", "phase_trace")
INHERITABLE = ("inventory", "paths", "gradients", "expert")
# These changes add diagnostics/observability. The learned model and its input
# contract must be byte-identical before old numerical evidence can be cited.
DIAGNOSTIC_CHANGES = {
    "src/fastwam/memory_s1/s1_diagnosis.py",
    "src/fastwam/memory_s1/diagnosis_gpu.py",
    "src/fastwam/memory_s1/diagnosis_followup.py",
    "src/fastwam/memory_s1/eval_parallel.py",
    "src/fastwam/memory_s1/posttrain.py",
    "scripts/memory_s1/deploy_policy.py",
    "scripts/memory_s1/sim_instrumentation.py",
    "scripts/memory_s1/portable/launch_diagnosis.sh",
    "scripts/memory_s1/portable/diagnosis_control.py",
}


def artifact_files(root, stage):
    root = Path(root)
    names = {
        "inherit": ("INHERITANCE.json", "windows.json", "selector_cases.json", "historical", "evidence/current_source"),
        "inventory": ("windows.json", "selector_cases.json", "data_audit.json", "cache_inventory.json",
                      "training_sampling.json", "evidence_manifest.json", "weight_audit.json", "checkpoint_audit.json"),
        "offline": ("offline_cases", "T_estimator.json", "same_selected_inputs.json", "offline_analysis.json", "offline_actions.csv"),
        "recorded": ("recorded",), "phase_trace": ("phase_trace",), "contacts": ("contacts",),
        "fixed": ("fixed/QUALIFICATION.json", "fixed/qualification"),
        "random": ("random/step_002000",), "expert": ("expert",), "paths": ("paths",),
        "gradients": (), "micro": ("micro_curve.json",),
    }.get(stage, ())
    files = {}
    for name in names:
        path = root / name
        candidates = path.rglob("*") if path.is_dir() else (path,)
        for item in candidates:
            if not item.is_file() or item.name.endswith(".lock") or "owner" in item.name:
                continue
            if any(p in item.relative_to(root).parts for p in ("packages", "launches", "workers", "resident")):
                continue
            if "simulator_progress" in item.relative_to(root).parts and not item.name.startswith('fused_backend_'):
                continue
            if item.name in ("STOP.json", "STOP_REQUESTED", "progress.json", "status.json", "latest_log.txt", "launcher.json"):
                continue
            files[item.relative_to(root).as_posix()] = sha256(item)
    return files


def validate_manifest(directory, files):
    directory = Path(directory).resolve()
    for relative, expected in files.items():
        path = (directory / relative).resolve()
        if not path.is_relative_to(directory) or not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Evidence file missing/changed: {path}")


def stage_record(root, stage):
    """Verify current evidence, or read an explicitly scoped historical citation."""
    root = Path(root)
    current_identity = fingerprint(read_json(root / "identity.json"))
    path = root / f"{stage}.json"
    if path.exists():
        value = read_json(path)
        if value.get("complete") is not True or value.get("identity") != current_identity:
            raise ValueError(f"Incomplete/stale {stage}: {path}")
        if "artifacts" in value:
            validate_manifest(root, value["artifacts"])
        for source, expected in value.get('external_inputs',{}).items():
            if sha256(source) != expected: raise ValueError(f'Recorded source input changed: {source}')
        return value
    lineage_path = root / "INHERITANCE.json"
    if stage not in INHERITABLE or not lineage_path.exists():
        raise ValueError(f"Finish {stage} first: {path}")
    lineage = read_json(lineage_path)
    stage_record(root,'inherit')
    if lineage["current_identity"] != current_identity:
        raise ValueError("Historical citation belongs to a different current run")
    citation = lineage["stages"].get(stage)
    if citation is None:
        raise ValueError(f"No verified historical citation for {stage}")
    historical = root / "historical"
    if sha256(historical/'identity.json') != lineage['parent_identity_sha256']:
        raise ValueError('Historical identity copy changed')
    validate_manifest(historical, citation["files"])
    value = read_json(historical / f"{stage}.json")
    if value.get("complete") is not True or value.get("identity") != lineage["parent_identity"]:
        raise ValueError(f"Historical {stage} has the wrong original identity")
    return {**value, "evidence_origin": "historical", "original_identity": value["identity"],
            "citation": citation, "scope": "Original sampled checks; not a rerun under the current source"}


def inherit(cfg, root, bound):
    parent = Path(cfg["diagnosis"]["parent"]).resolve()
    root = Path(root).resolve()
    if parent == root or parent.is_relative_to(root) or root.is_relative_to(parent):
        raise ValueError("Use a separate follow-up directory outside the original evidence tree")
    old = read_json(parent / "identity.json")
    old_cfg, new_cfg = copy.deepcopy(old["config"]), copy.deepcopy(cfg)
    old_cfg.pop("diagnosis", None); new_cfg.pop("diagnosis", None)
    if old_cfg != new_cfg:
        raise ValueError("Non-diagnostic configuration differs from the historical run")
    for key in ("weights", "resources", "evidence", "history", "simulator_sources_sha256", "reference_sources", "environment"):
        if old[key] != bound[key]:
            raise ValueError(f"Cannot inherit changed dependency: {key}")
    changed = {p for p in set(old["source"]) | set(bound["source"])
               if old["source"].get(p) != bound["source"].get(p)}
    unsupported = changed - DIAGNOSTIC_CHANGES
    if unsupported:
        raise ValueError(f"Changed non-diagnostic sources: {sorted(unsupported)}; rerun affected checks")
    validate_manifest(parent / "evidence/source", old["source"])
    manifest = read_json(parent / "evidence_manifest.json")
    validate_manifest(parent, {r["copy"]: r["sha256"] for r in manifest["files"]})
    original_scenes = read_json(parent/'SCENE_INHERITANCE.json')
    if bound['diagnostic_scenes_sha256'] != original_scenes['source_sha256']:
        raise ValueError('Frozen scene bank changed since original diagnosis; no replacement scenes allowed')
    historical = root / "historical"
    historical.mkdir(exist_ok=True)
    historical_inputs = {r['copy']:r['sha256'] for r in manifest['files']}
    historical_inputs.update({f'evidence/source/{p}':h for p,h in old['source'].items()})
    historical_inputs.update({p.relative_to(parent).as_posix():sha256(p)
                              for p in (parent/'evidence/scalar_sequences').glob('*.json')})
    for relative,digest in historical_inputs.items():
        target=historical/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and sha256(target)!=digest: raise ValueError(f'Historical input copy changed: {target}')
        if not target.exists(): shutil.copy2(parent/relative,target)
    stages = {}
    for stage in INHERITABLE:
        value = read_json(parent / f"{stage}.json")
        if value.get("complete") is not True or value.get("identity") != fingerprint(old):
            raise ValueError(f"Original {stage} is incomplete or has a different identity")
        files = artifact_files(parent, stage)
        files[f"{stage}.json"] = sha256(parent / f"{stage}.json")
        if stage == "paths":
            # Large oracle tensors are not needed to cite the already reviewed
            # scalar comparisons. Keep their identity, without copying entities.
            files = {p: h for p, h in files.items() if not p.endswith(".pt")}
        for relative, digest in files.items():
            target = historical / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and sha256(target) != digest:
                raise ValueError(f"Existing historical copy changed: {target}")
            if not target.exists(): shutil.copy2(parent / relative, target)
        stages[stage] = {"source": str(parent / f"{stage}.json"), "files": files,
                         "original_identity": fingerprint(old)}
    for name in ("identity.json", "evidence_manifest.json", "training_sampling.json", "weight_changes.json", "old_results.json",
                 "frozen_scenes.json", "SCENE_INHERITANCE.json"):
        target = historical / name
        if target.exists() and sha256(target) != sha256(parent / name):
            raise ValueError(f"Historical copy changed: {target}")
        shutil.copy2(parent / name, target)
    # Plans are copied unchanged; no approval or historical report is re-signed.
    for name in ("windows.json", "selector_cases.json"):
        shutil.copy2(parent / name, root / name)
    lineage = {"current_identity": fingerprint(bound), "parent": str(parent), "parent_identity": fingerprint(old),
               "parent_identity_sha256": sha256(parent / "identity.json"), "changed_diagnostic_sources": sorted(changed),
               "stages": stages, "old_reports_modified": False,
               "qualification": "Current 32-target qualification is required after instrumentation changes"}
    atomic_json(root / "INHERITANCE.json", lineage)
    # Current source is archived separately from the historical source inventory.
    for relative in bound["source"]:
        target = root / "evidence/current_source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(Path(cfg["root"]) / relative, target)
    print(f"[inherit] {len(stages)} historical citations verified; original evidence unchanged", flush=True)
    return {"complete": True, "stages": list(stages), "parent_identity": fingerprint(old)}


def offline_analysis(root):
    """Expose native joint errors and pairing; never infer a cause from FM alone."""
    root = Path(root)
    plan = read_json(root / "windows.json")
    rows = [read_json(p) for p in sorted((root / "offline_cases").glob("*.json"))]
    expected = {c["id"] for c in plan["cases"]}
    if {r["id"] for r in rows} != expected or len(rows) != len(expected):
        raise ValueError("Offline case inventory is incomplete or contains unexpected cases")
    detail = []
    for row in rows:
        for portion in ("all", "first16", "last16", "moving", "near_hold"):
            metrics = row.get("metrics", {}).get(portion)
            if metrics is None: continue
            detail.append({k: row[k] for k in ("id", "window", "split", "stage", "weight", "condition", "T", "phase")}
                          | {"portion": portion, "valid_targets": metrics["valid_targets"],
                             "left_wrist_mae_rad": metrics["joint_mae"][5],
                             "right_wrist_mae_rad": metrics["joint_mae"][12],
                             "left_arm_mae_rad": metrics["left_arm_mae"], "right_arm_mae_rad": metrics["right_arm_mae"],
                             "left_gripper_mae": metrics["gripper_mae"][0], "right_gripper_mae": metrics["gripper_mae"][1],
                             "normalized_mse": metrics["normalized_mse"]})
    with (root / "offline_actions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(detail[0])); writer.writeheader(); writer.writerows(detail)
    atomic_json(root / "offline_analysis.json", {"planned": len(expected), "completed": len(rows),
        "action_samples": sum(r["sample"] for r in rows), "single_fm": sum(not r["sample"] for r in rows),
        "detail_csv": "offline_actions.csv", "root_cause": "undetermined; inspect paired native-unit errors"})


def reconstruct_requests(cfg, root):
    """Authenticate PNG pixels and command-state observations, never synthesize state."""
    import numpy as np
    from PIL import Image
    from .eval_state import EpisodeQueue
    from .history import resolve_online
    from .s1_diagnosis import safe_rows, TASKS
    parent = Path(cfg["diagnosis"]["parent"])
    source = parent / "fixed/qualification/fused"
    queue = EpisodeQueue(source); state = queue.snapshot()
    jobs = state["jobs"]
    if len(jobs) != 2 or {j["scene"]["task"] for j in jobs} != set(TASKS):
        raise ValueError("Need the original two fixed-prefix scenes")
    inputs = []
    files = {}
    for job in jobs:
        if job["state"] != "complete": raise ValueError("Original fixed prefix is incomplete")
        result = queue.result(job, state["identity"])
        directory = source / job["directory"]
        decisions, torn = safe_rows(directory / "decisions.jsonl")
        observations, obs_torn = safe_rows(directory / "qualification_trace.jsonl")
        if torn or obs_torn: raise ValueError("Recorded prefix has torn input/log records")
        by_frame = {int(r["target_id"]): r for r in observations}
        if len(by_frame) != len(observations): raise ValueError("Duplicate observation frame IDs")
        frames = {}
        for frame in range(17):
            if frame not in by_frame: raise ValueError(f"Missing original observation {frame}")
            record = by_frame[frame]
            images = []
            for camera, file_prefix in (("head_camera", "head"), ("left_camera", "left"), ("right_camera", "right")):
                path = directory / "frames" / str(result["seed"]) / f"{file_prefix}_{frame:06d}.png"
                with Image.open(path) as image: array = np.asarray(image.convert("RGB"), dtype=np.uint8)
                if hashlib.sha256(array.tobytes()).hexdigest() != record["rgb"][camera]:
                    raise ValueError(f"PNG does not match original observed pixels: {path}")
                images.append(array)
                files[str(path.resolve())] = sha256(path)
            proprio = np.asarray(record["command_state"], dtype=np.float32)
            if proprio.shape != (14,) or not np.isfinite(proprio).all(): raise ValueError("Invalid recorded command state")
            frames[frame] = {"frame_id": frame, "images": [i.tobytes() for i in images],
                             "shapes": [list(i.shape) for i in images], "proprio": proprio.tolist()}
        for name in ("qualification_trace.jsonl", "decisions.jsonl", "complete.json", "result.json"):
            path = directory / name; files[str(path.resolve())] = sha256(path)
        for current_id in (0, 16):
            matches = [r for r in decisions if r["frame_id"] == current_id]
            if len(matches) != 1: raise ValueError(f"Missing/duplicate original decision {current_id}")
            decision = matches[0]
            sampling = resolve_online(cfg, result["task"], result["seed"], current_id)
            if sampling["period"] != decision["history_period"] or sampling["phase"] != decision["history_phase"]:
                raise ValueError("Current sampling rule differs from the original request")
            request = {"current_id": current_id, "episode_seed": result["seed"], "task": result["task"],
                       "instruction": result["instruction"], "observations": [frames[i] for i in range(current_id+1)]}
            # JSON fingerprints cannot represent bytes; observation signatures do.
            payload = {"task": result["task"], "seed": result["seed"], "current_id": current_id,
                       "instruction": result["instruction"], "sampling": sampling,
                       "observations": [{"frame_id": i, "proprio": frames[i]["proprio"], "shapes": frames[i]["shapes"],
                            "pixels_sha256": [hashlib.sha256(b).hexdigest() for b in frames[i]["images"]]} for i in range(current_id+1)]}
            inputs.append({"id": f"{result['task']}_{current_id:06d}", "request": request,
                           "decision": decision, "input_identity": fingerprint(payload), "input_manifest": payload})
    copies = {}
    for source, digest in files.items():
        relative = Path('recorded/source') / Path(source).relative_to(parent.resolve())
        destination = Path(root) / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists() and sha256(destination) != digest:
            raise ValueError(f'Original request copy changed: {destination}')
        if not destination.exists(): shutil.copy2(source, destination)
        copies[relative.as_posix()] = digest
    atomic_json(Path(root) / "recorded/input_manifest.json", {"files": files, "copies": copies,
        "requests": [{"id": r["id"], "input_identity": r["input_identity"], **r["input_manifest"]} for r in inputs],
        "state_source": "Original qualification_trace command_state; physical qpos is never substituted"})
    return inputs


def recorded(cfg, root, bound):
    import numpy as np
    import torch
    from .diagnosis_gpu import setup, load_weight
    from .model import load_observation_encoders
    from .sim_bridge import InferenceSession
    from .s1_diagnosis import check_stop
    inputs = reconstruct_requests(cfg, root)  # Validate materials before loading models.
    model, device, datasets = setup(cfg)
    del datasets
    encoders = load_observation_encoders(cfg, device)
    destination = Path(root) / "recorded"
    destination.mkdir(exist_ok=True)
    completed = []; failures = []; started = time.monotonic()
    for label in ("step_002000", "gate_zero", "step_000000", "step_001500"):
        load_weight(model, bound, label)
        for item in inputs:
            check_stop(root)
            path = destination / f"{label}_{item['id']}.json"
            key = fingerprint({"input": item["input_identity"], "weight": label, "identity": bound})
            if path.exists():
                prior = read_json(path)
                if prior["identity"] != key: raise ValueError("Recorded-input result identity changed")
                completed.append(prior)
                if label == "step_002000" and not prior["original_reproduction"]["exact"]: failures.append(prior)
                continue
            calls = []; injections = []
            original = model.backbone.action_velocity
            def velocity(*args, **kwargs):
                value = original(*args, **kwargs)
                calls.append({"timestep": args[1].detach().float().cpu().tolist(),
                              "actions_before": args[0].detach().float().cpu().tolist(),
                              "velocity": value.detach().float().cpu().tolist()})
                return value
            def observe(module, args, output):
                residual = output.detach().float() - args[0].detach().float()
                rounded = output.detach().to(torch.bfloat16).float() - args[0].detach().to(torch.bfloat16).float()
                injections.append({"layer": names[id(module)], "residual_rms": float(residual.square().mean().sqrt()),
                                   "bf16_nonzero_fraction": float((rounded != 0).float().mean())})
            names = {id(module): name for name, module in model.memory.injectors.items()}
            hooks = [m.register_forward_hook(observe) for m in model.memory.injectors.values()]
            model.backbone.action_velocity = velocity
            trace = {}
            session = InferenceSession(model, cfg, encoders, "gate_zero" if label == "gate_zero" else "full",
                                       destination / f"{label}_{item['id']}", None, cfg["seed"], trace=trace)
            try:
                with torch.no_grad(): session.decide(item["request"])
            finally:
                model.backbone.action_velocity = original
                for hook in hooks: hook.remove()
            actual = trace["normalized_actions"].float().numpy()
            expected = np.asarray(item["decision"]["normalized_actions"], dtype=np.float32)
            decision = json.loads((session.output / "decisions.jsonl").read_text().splitlines()[-1])
            if decision["noise_seed"] != item["decision"]["noise_seed"]:
                raise ValueError("Replay used different action noise")
            if len(calls) != 10: raise ValueError("Expected the original 10-step sampler")
            reproduction = {"exact": bool(np.array_equal(actual, expected)),
                            "max_abs": float(np.abs(actual-expected).max()),
                            "claim": "original action reproduction" if label == "step_002000" else "paired model comparison"}
            differences = np.argwhere(actual != expected)
            if len(differences):
                target, joint = map(int, differences[0])
                reproduction['first_action_difference'] = {'target_index_zero_based': target,
                    'joint_index_zero_based': joint, 'original': float(expected[target,joint]),
                    'replayed': float(actual[target,joint])}
            readout = trace.get("readout")
            value = {"identity": key, "input_identity": item["input_identity"], "weight": label, "task": item["request"]["task"],
                     "frame_id": item["request"]["current_id"], "noise_seed": decision["noise_seed"],
                     "sampling": trace["sampling"], "read_frame_ids": decision["read_frame_ids"],
                     "normalized_actions": actual.tolist(), "denormalized_actions": decision["actions_before_gripper_clip"],
                     "clipped_actions": decision["actions_after_gripper_clip"], "denoising": calls,
                     "injection": injections, "original_reproduction": reproduction,
                     "normalized_proprio": trace["proprio"].float().tolist(),
                     "action_noise": trace["noise"].float().tolist(),
                     "memory_readout": None if readout is None else readout.float().tolist(),
                     "readout_token_std": None if readout is None else float(readout.float().std(dim=1).mean()),
                     "elapsed_seconds": time.monotonic()-started}
            atomic_json(path, value); completed.append(value)
            print(f"[recorded] {len(completed)}/16 {label} {item['id']} original_exact={reproduction['exact']} "
                  f"max_abs={reproduction['max_abs']:.6g} elapsed={time.monotonic()-started:.1f}s", flush=True)
            if label == "step_002000" and not reproduction["exact"]: failures.append(value)
        if failures:
            atomic_json(destination / "first_divergence.json", {"cases": failures, "tolerance_relaxed": False})
            raise ValueError("Step 2000 does not reproduce original requests; inspect recorded/first_divergence.json before comparing models")
    if len(completed) != 16: raise ValueError("Recorded-input comparison is incomplete")
    atomic_json(destination / "summary.json", {"complete": True, "cases": 16, "original_step2000_exact": True,
               "optimizer_updates": 0, "scope": "Paired recorded observations; not a task accuracy estimate"})
    return {"complete": True, "cases": 16, "original_step2000_exact": True, "optimizer_updates": 0,
            "external_inputs":read_json(destination/'input_manifest.json')['files']}


def contacts(cfg, root, bound):
    """Validate new contact mapping on saved successful expert targets only."""
    from .eval_parallel import gpu_inventory
    from .eval_state import EpisodeQueue
    from .posttrain import runtime_options
    from .rootcause import parallel_group
    from .s1_diagnosis import TASKS
    parent = Path(cfg['diagnosis']['parent'])
    source = parent / 'expert/reference'
    queue = EpisodeQueue(source); state = queue.snapshot()
    scenes = []; inputs = {}
    for task in TASKS:
        jobs = [j for j in state['jobs'] if j['scene']['task'] == task]
        if len(jobs) != 1 or jobs[0]['state'] != 'complete':
            raise ValueError(f'Missing original successful expert: {task}')
        job = jobs[0]; result = queue.result(job, state['identity'])
        if result['success'] is not True: raise ValueError('Original expert was not successful')
        targets = source / job['directory'] / 'expert_targets.json'
        inputs[str(targets.resolve())] = sha256(targets)
        scene = copy.deepcopy(job['scene'])
        scene.update(environment='rmbench', root=str(Path(cfg['root'])/cfg['closed_loop']['simulator_root']),
                     expert_targets=str(targets))
        scenes.append(scene)
    current = copy.deepcopy(cfg)
    current['rootcause']['s1_diagnosis'] = True
    current['selection_runtime'] = runtime_options('fused-resident')
    parallel_group(current, Path(root), 'contacts/production', scenes, ['production'], 'expert_replay',
                   [gpu_inventory()[0]], True, bound)
    queue = EpisodeQueue(Path(root)/'contacts/production'); state = queue.snapshot(); rows = []
    for job in state['jobs']:
        result = queue.result(job, state['identity'])
        physical = read_json(queue.root/job['directory']/'physical_summary.json')
        hits = {name: value for name, value in physical['events'].items() if value['contact_seen'] is True}
        passed = result['success'] is True and physical['contacts_available'] and bool(hits)
        rows.append({'task': result['task'], 'seed': result['seed'], 'expert_success': result['success'],
                     'passed': bool(passed), 'aliases': physical['contact_aliases'], 'positive_objects': hits,
                     'scope': 'Saved successful expert targets; same frozen scene and production executor'})
    passed = len(rows) == 2 and all(row['passed'] for row in rows)
    atomic_json(Path(root)/'contacts/validation.json', {'passed': passed, 'episodes': rows,
                'negative_contact_claim': 'Not validated; target-boundary absence remains unknown'})
    if not passed:
        raise ValueError('Contact mapping not validated on both successful experts; inspect contacts/validation.json')
    return {'complete': True, 'passed': True, 'episodes': rows, 'external_inputs': inputs}


def trace_summary(root):
    import numpy as np
    from .eval_state import EpisodeQueue
    from .s1_diagnosis import safe_rows
    directory = Path(root) / "phase_trace/step_002000"
    queue = EpisodeQueue(directory); state = queue.snapshot(); output = []
    if len(state["jobs"]) != 2: raise ValueError("Phase trace requires exactly two scenes")
    for job in state["jobs"]:
        if job["state"] != "complete": raise ValueError("Phase trace did not finish its requested prefix")
        result = queue.result(job, state["identity"]); attempt = directory / job["directory"]
        actions, torn = safe_rows(attempt / "executed_actions.jsonl")
        if torn or len(actions) != result["executed_targets"]: raise ValueError("Incomplete phase feedback")
        if [r["completed_target_id"] for r in actions] != list(range(1, len(actions)+1)): raise ValueError("Target handoff/index mismatch")
        if not 0 < len(actions) <= 160: raise ValueError("Invalid diagnostic prefix budget")
        if len(actions) < 160 and not result["success"]: raise ValueError("Prefix ended early without task success")
        q = np.asarray([r["target"] for r in actions]); actual = np.asarray([r["physical_after"] for r in actions])
        if not np.isfinite(q).all() or not np.isfinite(actual).all(): raise ValueError("Non-finite physical feedback")
        rows = []
        for r in actions:
            row = {"target_id": r["completed_target_id"], "physics_step_id": r["physics_step_id"],
                   "sim_time": r["physics_step_id"]*r["physics_timestep"],
                   "right_wrist_target_rad": r["target"][12], "right_wrist_actual_rad": r["physical_after"][12],
                   "right_gripper_target": r["target"][13], "right_gripper_actual": r["physical_after"][13]}
            for side in ("left", "right"):
                pose = r["joint_details"][side].get("ee_pose")
                if pose is None: raise ValueError(f"Actual {side} end-effector pose is unavailable")
                row.update({f"{side}_ee_{axis}": v for axis,v in zip(("x","y","z","qw","qx","qy","qz"), pose["p"]+pose["q"])})
            rows.append(row)
        csv_path = attempt / "phase_trace.csv"
        with csv_path.open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        events = {}
        initial = actions[0]["objects_before"]
        for name, obj in initial.items():
            if not isinstance(obj,dict) or "p" not in obj: continue
            positions=np.asarray([r["objects_after"][name]["p"] for r in actions]);origin=np.asarray(obj["p"])
            hits=[r["completed_target_id"] for r in actions if r["object_contacts"]["objects"].get(name,{}).get("gripper_contact") is True]
            events[name]={"max_lift_m":float((positions[:,2]-origin[2]).max()),
                          "max_xy_m":float(np.linalg.norm(positions[:,:2]-origin[:2],axis=1).max()),
                          "observed_contact_target_ids":hits,
                          "contact_absence": "unknown; contact sampled only at completed targets"}
        first_close=np.flatnonzero(q[:,13]<.3)
        summaries={"task":result["task"],"seed":result["seed"],"targets":len(actions),"termination":result["termination"],
                   "task_acc":None,"scope":"160-target diagnostic, not full-task accuracy",
                   "first_right_close":int(first_close[0])+1 if len(first_close) else None,
                   "joint_tracking_mae_rad":np.abs(q-actual)[:,[0,1,2,3,4,5,7,8,9,10,11,12]].mean(0).tolist(),
                   "objects":events,"video_playback_fps":15,"video_time_scope":"Observation-index playback; physical time is in phase_trace.csv",
                   "final_stage":{k:actions[-1]["objects_after"].get(k) for k in ("stage_id","press_cnt","press_flag")}}
        atomic_json(attempt / "phase_summary.json",summaries);output.append(summaries)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,axes=plt.subplots(2,1,figsize=(9,6),sharex=True)
        ids=np.arange(1,len(actions)+1)
        axes[0].plot(ids,q[:,12],label="right wrist target");axes[0].plot(ids,actual[:,12],label="actual")
        axes[0].set_ylabel("Joint angle (rad)");axes[0].legend()
        axes[1].plot(ids,q[:,13],label="right gripper target");axes[1].plot(ids,actual[:,13],label="actual")
        axes[1].set(xlabel="Completed target",ylabel="Native gripper units");axes[1].legend()
        fig.tight_layout();fig.savefig(attempt/"phase_trace.png");fig.savefig(attempt/"phase_trace.pdf");plt.close(fig)
        make_video(attempt,result["seed"],len(actions))
        print(f"[phase_trace] {result['task']} targets={len(actions)}/160 termination={result['termination']} "
              f"first_close={summaries['first_right_close']} objects={events}",flush=True)
    atomic_json(Path(root)/"phase_trace/summary.json",{"complete":True,"episodes":output,"task_acc":None})
    return output


def make_video(attempt, seed, count):
    import imageio.v2 as imageio
    from PIL import Image
    # Observations already consumed by the policy; no simulator calls or RNG.
    with imageio.get_writer(attempt/"phase_trace.mp4",fps=15,macro_block_size=1) as writer:
        for index in range(count):
            path=attempt/"frames"/str(seed)/f"head_{index:06d}.png"
            with Image.open(path) as image: writer.append_data(image.convert("RGB"))
