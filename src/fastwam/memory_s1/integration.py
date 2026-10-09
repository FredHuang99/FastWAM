"""Bounded official/production integration checks and S1 admission, without task-score gating."""
from __future__ import annotations

import argparse
import ast
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import time

import h5py
import numpy as np
import torch

from .common import (ReleaseNormalizer, append_jsonl, atomic_json, atomic_torch, fingerprint,
                     load_config, make_cache_contract, read_json, seed_for, sha256, TASKS)
from .data import official_decoder, observation_tensor, read_episode, choose_instruction, CachedEpisodes, collate
from .integration_contract import (VERSION, FASTWAM_COMMIT, RMBENCH_COMMIT, REQUIRED, binding,
                                   configure_numerics, exact_difference, output_root)
from .eval_state import check_stop, stop_mode, process_identity, is_alive, locked, EvaluationInterrupted
from .rootcause import run_child, child_environment, expert_scenes, parallel_group
from .eval_parallel import gpu_inventory


def source_root(cfg, kind):
    key = "reference_root" if kind == "fastwam" else "public_rmbench_root"
    return (Path(cfg["root"]) / cfg["integration"][key]).resolve()


def sources(cfg):
    output = output_root(cfg)
    output.mkdir(parents=True, exist_ok=True)
    repositories = {}
    specs = (("fastwam", "https://github.com/yuantianyuan01/FastWAM.git", FASTWAM_COMMIT),
             ("rmbench", "https://github.com/YTY101/RMBench.git", RMBENCH_COMMIT))
    env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1"}
    for kind, url, commit in specs:
        root = source_root(cfg, kind)
        if not root.exists():
            root.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["git", "clone", "--filter=blob:none", "--no-checkout", url, str(root)], check=True, env=env)
            subprocess.run(["git", "-C", str(root), "checkout", "--detach", commit], check=True, env=env)
        head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], text=True)
        if head != commit or dirty:
            raise ValueError(f"Reference checkout changed: {root}; preserve it and restore the pinned clean source.")
        if kind == "fastwam":
            paths = [p for folder in ("src", "configs", "experiments/robotwin/fastwam_policy")
                     for p in sorted((root / folder).rglob("*")) if p.is_file()
                     and p.suffix in (".py", ".yaml", ".yml", ".json") and "__pycache__" not in p.parts]
        else:
            paths = [root / ".fastwam/eval_policy.py"]
            target = subprocess.check_output(["git", "-C", str(root), "show", f"{commit}:policy/fastwam_policy"], text=True).strip()
            if target != "/workspace/FastWAM/experiments/robotwin/fastwam_policy":
                raise ValueError("Public adapter no longer resolves the expected official policy.")
        repositories[kind] = {"url": url, "commit": commit, "path": str(root.relative_to(cfg["root"])),
                              "files": {str(p.relative_to(root)): sha256(p) for p in paths}}
        if kind == "rmbench":
            repositories[kind]["policy_symlink"] = target
        print(f"[sources] {kind} commit={commit} tracked_files={len(paths)}", flush=True)
    atomic_json(output / "sources.json", {"version": VERSION, "repositories": repositories,
        "public_adapter_scope": "Pinned evaluation entry delegates to the official RoboTwin policy; it supplies no RMBench checkpoint or full training recipe."})
    adapter_path = source_root(cfg, "rmbench")/".fastwam/eval_policy.py"
    tree = ast.parse(adapter_path.read_text(encoding="utf-8"))
    entry = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "eval_policy")
    calls = {n.func.attr for n in ast.walk(entry) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    if not {"get_obs", "should_request_observation", "setup_demo", "play_once"} <= calls:
        raise ValueError("The public adapter no longer follows the checked expert/observation/policy protocol.")
    atomic_json(output/"adapter_audit.json", {
        "source": ".fastwam/eval_policy.py", "sha256": sha256(adapter_path),
        "policy_target": repositories["rmbench"]["policy_symlink"],
        "public_route": "get_obs -> imported official policy eval -> step -> take_action(qpos)",
        "our_route": "get_obs -> RPCPolicy capture/queue -> take_action(qpos)",
        "differences": {"execute": "Both references explicitly use 16; RoboTwin's released default is 24.",
                       "capture": "Our dense archive retains each completed target; the public entry can skip within-chunk get_obs.",
                       "environment": "Actual fork/demo_clean/Aloha settings are preserved and audited by the simulator.",
                       "weights": "Both numerical routes use the same local released checkpoint, without RMBench adaptation."}})
    # Archive only pinned code/configuration, never weights, credentials, .git or model downloads.
    with tarfile.open(output / "reference_sources.tar.gz", "w:gz") as archive:
        for kind, info in repositories.items():
            root = source_root(cfg, kind)
            for relative in info["files"]:
                archive.add(root / relative, arcname=f"{kind}/{relative}", recursive=False)
    print(f"[sources] source lock and compact snapshot: {output}", flush=True)


def normalizer_probe(actions, noise, tau):
    from fastwam.models.wan22.schedulers.scheduler_continuous import WanContinuousFlowMatchScheduler
    return WanContinuousFlowMatchScheduler(shift=1.0).add_noise(actions, noise, 1000*tau)


def case_bank(cfg, output):
    manifest = read_json(Path(cfg["paths"]["prepared"]) / "manifest.json")
    decoder = official_decoder(Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"])
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    records = []
    for task in TASKS:
        rows = sorted((r for r in manifest["episodes"] if r["task"] == task and r["split"] == "val"),
                      key=lambda r: r["episode_id"])
        if len(rows) < 2:
            raise ValueError(f"Two validation episodes are required: {task}")
        records.extend(rows[:2])
    cases = []
    for record in records:
        path = Path(cfg["root"]) / record["raw"]
        if sha256(path) != record["raw_sha256"]:
            raise ValueError(f"Raw episode changed: {path}")
        episode = torch.load(Path(cfg["paths"]["prepared"]) / record["file"], map_location="cpu", weights_only=True)
        with h5py.File(path, "r") as file:
            for frame in (0, 64, 128):
                if frame >= record["length"]:
                    raise ValueError("The twelve-case bank has a missing anchor.")
                slot = len(cases)
                seed = seed_for(cfg["seed"], slot, frame, "closed-loop-noise")
                noise = torch.randn(1, 32, 14, generator=torch.Generator().manual_seed(seed))
                targets = torch.empty(32, 14)
                count = min(32, len(episode["targets"]) - frame)
                targets[:count] = episode["targets"][frame:frame+count]
                targets[count:] = targets[count-1]
                valid = torch.arange(32) < count
                actions = normalizer.normalize(targets, "action")[None]
                tau = torch.tensor([0.37], dtype=torch.float32)
                cases.append({"case_id": f"{record['episode_id']}:{frame}", "record": record,
                    "task": record["task"], "frame_id": frame, "episode_seed": slot,
                    "images": [torch.from_numpy(decoder(file[key][frame]).copy()) for key in record["camera_paths"]],
                    "state": episode["states"][frame], "instruction": record["instruction"],
                    "noise_seed": seed, "noise": noise, "actions_raw": targets[None],
                    "actions": actions, "action_valid": valid[None], "probe_tau": tau,
                    "probe_noisy": normalizer_probe(actions, noise, tau)})
    atomic_torch(output / "request.pt", {"config": cfg, "cases": cases})
    atomic_json(output / "cases.json", [{key: value for key, value in c.items()
                if key in ("case_id", "task", "frame_id", "episode_seed", "noise_seed", "instruction")} for c in cases])
    return cases


def report(cfg, name, passed, **details):
    value = {"version": VERSION, "binding": binding(cfg), "passed": bool(passed), **details}
    atomic_json(output_root(cfg) / f"{name}.json", value)
    return value


def require_report(cfg, name):
    value = read_json(output_root(cfg) / f"{name}.json")
    if not value.get("passed") or value.get("binding") != binding(cfg):
        raise ValueError(f"Missing, failed or stale integration stage: {name}")
    return value


def fixture_trace(model, encoders, cfg, case):
    from .model import encode_text, encode_latent
    from .checkpoint import to_cpu
    device = next(model.memory.parameters()).device
    images = [x.numpy() for x in case["images"]]
    mosaic = observation_tensor(images, device)
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    state = normalizer.normalize(case["state"][None], "state").to(device)
    vae, text_encoder, tokenizer = encoders
    trace = {}
    model.backbone.integration_trace = trace
    with torch.no_grad(), torch.autocast("cuda", enabled=False):
        text, valid = encode_text(text_encoder, tokenizer, case["instruction"], device)
        latent = encode_latent(vae, mosaic)
        feature, kv, context = model.backbone.encode_observation(latent, text, state)
        trace.update(to_cpu({"mosaic": mosaic, "proprio": state, "text": text,
                        "context": context[0], "context_mask": context[1],
                        "latent": latent, "feature": feature, "kv": kv, "noise": case["noise"], "text_valid": valid}))
        noise = case["noise"].to(device)
        with velocity_capture(model, trace):
            actions, _ = model.sample({}, noise, gate_scale=0, prepared_conditions=(kv, context, None))
        trace["normalized_actions"] = actions[0].cpu()
        raw = normalizer.denormalize(actions)
        trace["denormalized_actions"] = raw.cpu()
        raw[..., [6, 13]] = raw[..., [6, 13]].clamp(0, 1)
        trace["clipped_actions"] = raw[0].cpu()
        probe_actions = case["actions"].to(device)
        probe_tau = case["probe_tau"].to(device)
        probe_noisy = model.scheduler.add_noise(probe_actions, noise, 1000*probe_tau)
        probe = model.backbone.action_velocity(probe_noisy,
                    1000*probe_tau, context, kv, model.memory, None, 0)
        trace["probe_velocity"] = probe.cpu()
        trace["probe_weight"] = model.scheduler.training_weight(1000*probe_tau).cpu()
        trace["ground_truth"] = probe_actions.cpu()
        trace["probe_noisy"] = probe_noisy.cpu()
        trace["probe_target"] = model.scheduler.training_target(probe_actions, noise, 1000*probe_tau).cpu()
    model.backbone.integration_trace = None
    return trace


@contextmanager
def velocity_capture(model, trace):
    original = model.backbone.action_velocity
    previous_trace = getattr(model.backbone, "integration_trace", None)
    model.backbone.integration_trace = trace
    trace.update(velocity=[], noisy_actions=[], timesteps=[])
    def wrapped(actions, timestep, *args, **kwargs):
        result = original(actions, timestep, *args, **kwargs)
        trace["velocity"].append(result.detach().cpu())
        trace["noisy_actions"].append(actions.detach().to(torch.bfloat16).cpu())
        trace["timesteps"].append(timestep.detach().to(torch.bfloat16).cpu())
        return result
    model.backbone.action_velocity = wrapped
    try:
        yield
    finally:
        model.backbone.action_velocity = original
        model.backbone.integration_trace = previous_trace


def compare_trace(actual, expected, probe=True):
    order = ("mosaic", "proprio", "text", "text_valid", "latent", "context", "context_mask", "feature", "noise",
             "video_mask", "action_mask",
             "kv", "noisy_actions", "timesteps", "velocity", "normalized_actions",
             "denormalized_actions", "clipped_actions")
    if probe:
        order += ("ground_truth", "probe_noisy", "probe_target", "probe_velocity", "probe_weight")
    rows = {}
    def compare(a, b):
        if isinstance(a, torch.Tensor):
            return exact_difference(a, b)
        if len(a) != len(b):
            return {"exact": False, "lengths": [len(a), len(b)]}
        children = [compare(x, y) for x, y in zip(a, b)]
        return {"exact": all(r["exact"] for r in children), "items": children}
    for name in order:
        if name not in actual or name not in expected:
            rows[name] = {"exact": False, "missing": name}
        else:
            rows[name] = compare(actual[name], expected[name])
        if not rows[name]["exact"]:
            return {"passed": False, "first_divergence": name, "segments": rows}
    return {"passed": True, "first_divergence": None, "segments": rows}


def online_trace(model, encoders, cfg, case, directory):
    from .sim_bridge import InferenceSession
    decoder = official_decoder(Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"])
    record = case["record"]
    episode = torch.load(Path(cfg["paths"]["prepared"]) / record["file"], map_location="cpu", weights_only=True)
    observations = []
    with h5py.File(Path(cfg["root"]) / record["raw"], "r") as file:
        for frame in range(case["frame_id"]+1):
            images = [np.ascontiguousarray(decoder(file[key][frame])) for key in record["camera_paths"]]
            observations.append({"frame_id": frame, "images": [image.tobytes() for image in images],
                "shapes": [list(image.shape) for image in images], "proprio": episode["states"][frame].tolist()})
    trace = {}
    session = InferenceSession(model, cfg, encoders, "gate_zero", directory, None, cfg["seed"], trace=trace)
    request = {"current_id": case["frame_id"], "task": case["task"], "episode_seed": case["episode_seed"],
               "instruction": case["instruction"], "observations": observations}
    with velocity_capture(model, trace):
        session.decide(request)
    trace["text_valid"] = session.text_valid.detach().cpu()
    session.reset()
    return trace


def model_check(cfg, root, uuid):
    from .model import S1Model, load_observation_encoders
    directory = root / "model"
    directory.mkdir(parents=True, exist_ok=True)
    if (directory/"comparisons.jsonl").exists():
        shutil.move(str(directory/"comparisons.jsonl"), str(directory/f"comparisons_interrupted_{time.time_ns()}.jsonl"))
    cases = case_bank(cfg, directory)
    official = directory / "official"
    command = [sys.executable, "-u", str(Path(cfg["root"]) / "scripts/memory_s1/integration_reference.py"),
               "--reference-root", str(source_root(cfg, "fastwam")), "--request", str(directory/"request.pt"),
               "--output", str(official)]
    env = child_environment(uuid)
    env["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    # Finish and unload the entire upstream process before loading the production model.
    run_child(command, directory/"official.log", cfg["root"], env, root, cfg["integration"]["subprocess_timeout"])
    metadata = read_json(official/"summary.json")
    if not metadata["exact_self_repeat"] or metadata["cases"] != 12:
        raise RuntimeError("The upstream oracle did not establish twelve deterministic cases.")
    os.environ["CUDA_VISIBLE_DEVICES"] = uuid
    configure_numerics(cfg)
    device = torch.device("cuda:0")
    model = S1Model(cfg, device).eval()
    encoders = load_observation_encoders(cfg, device)
    rows, started = [], time.monotonic()
    for slot, case in enumerate(cases):
        check_stop(root)
        expected = torch.load(official/f"case_{slot:02d}.pt", map_location="cpu", weights_only=True)
        offline = fixture_trace(model, encoders, cfg, case)
        row = {"case_id": case["case_id"], "offline": compare_trace(offline, expected)}
        if row["offline"]["passed"]:
            actual_online = online_trace(model, encoders, cfg, case, directory/"online"/f"{slot:02d}")
            row["online"] = compare_trace(actual_online, expected, probe=False)
        row["passed"] = row["offline"]["passed"] and row.get("online", {}).get("passed", False)
        append_jsonl(directory/"comparisons.jsonl", row)
        rows.append(row)
        print(f"[model] {slot+1}/12 passed={row['passed']} ETA={(time.monotonic()-started)/(slot+1)*(11-slot):.1f}s", flush=True)
        if not row["passed"]:
            report(cfg, "model", False, cases=rows, oracle=metadata, first_failure=case["case_id"])
            raise RuntimeError(f"First real-path divergence: {case['case_id']}; inspect comparisons.jsonl.")
    report(cfg, "model", True, cases=rows, oracle=metadata, exact=True, scope="actual_offline_and_online_gate_zero")


def source_semantics(cfg):
    root = Path(cfg["root"]) / cfg["closed_loop"]["simulator_root"]
    collector = root / "envs/_base_task.py"
    converter = root / "envs/utils/pkl2hdf5.py"
    tree = ast.parse(converter.read_text(encoding="utf-8"))
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    node = functions.get("create_xpolicylab_hdf5")
    if node is None:
        raise ValueError("Cannot establish the state/action/image timeline from this converter.")
    def is_slice(node, lower, upper):
        return isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Slice) and (
            ast.dump(node.slice.lower) if node.slice.lower is not None else None) == lower and (
            ast.dump(node.slice.upper) if node.slice.upper is not None else None) == upper
    minus_one = ast.dump(ast.UnaryOp(op=ast.USub(), operand=ast.Constant(1)))
    one = ast.dump(ast.Constant(1))
    state_shift = action_shift = image_shift = False
    for call in (n for n in ast.walk(node) if isinstance(n, ast.Call)):
        if isinstance(call.func, ast.Attribute) and call.func.attr == "create_dataset":
            data = next((a.value for a in call.keywords if a.arg == "data"), None)
            if isinstance(call.func.value, ast.Name):
                state_shift |= call.func.value.id == "state" and is_slice(data, None, minus_one)
                action_shift |= call.func.value.id == "action" and is_slice(data, one, None)
        if isinstance(call.func, ast.Name) and call.func.id == "_write_camera_group" and len(call.args) > 2:
            image_shift |= is_slice(call.args[2], None, minus_one)
    methods = {n.name: n for n in ast.walk(ast.parse(collector.read_text(encoding="utf-8")))
               if isinstance(n, ast.FunctionDef)}
    getters = {"get_left_arm_jointState", "get_right_arm_jointState"}
    get_obs_calls = {n.func.attr for n in ast.walk(methods["get_obs"]) if isinstance(n, ast.Call)
                     and isinstance(n.func, ast.Attribute)}
    dense = methods.get("take_dense_action")
    cadence = dense is not None and any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod)
                and isinstance(n.right, ast.Name) and n.right.id == "save_freq" for n in ast.walk(dense))
    flags = {"state_records_exclude_last": state_shift, "targets_are_next_records": action_shift,
             "images_exclude_last": image_shift, "state_from_native_robot_getters": getters <= get_obs_calls,
             "collection_modulo_physics_loop": cadence}
    if not all(flags.values()):
        raise ValueError(f"Unknown collection/conversion semantics: {flags}; explicit review is required.")
    return {"checks": flags, "collector_sha": sha256(collector), "converter_sha": sha256(converter),
            "state_offset": 0, "action_offset": 1, "frequency_semantics": "physics-loop saving interval, not Hz",
            "action_semantics": "absolute next recorded command joint target; physical qpos remains separate"}


def data_check(cfg):
    manifest = read_json(Path(cfg["paths"]["prepared"])/"manifest.json")
    approval = read_json(Path(cfg["paths"]["prepared"])/"alignment_approved.json")
    if approval.get("approved") is not True or approval["manifest_sha"] != fingerprint(manifest):
        raise ValueError("The prior concrete data review does not match the prepared dataset.")
    semantics = source_semantics(cfg)
    rows = []
    for record in manifest["episodes"]:
        raw = Path(cfg["root"])/record["raw"]
        if sha256(raw) != record["raw_sha256"]:
            raise ValueError(f"Raw file changed: {raw}")
        state, actions, cameras, kind, metadata, embedded = read_episode(raw)
        instruction, _ = choose_instruction(raw, embedded)
        stored = torch.load(Path(cfg["paths"]["prepared"])/record["file"], map_location="cpu", weights_only=True)
        if not (np.array_equal(state, stored["states"].numpy()) and np.array_equal(actions, stored["targets"].numpy())
                and cameras == record["camera_paths"] and instruction == record["instruction"]
                and metadata == record["attributes"] and kind == record["source_kind"]):
            raise ValueError(f"Actual prepared data differs: {record['episode_id']}")
        if kind == "official_shifted_state_action" and (
                metadata.get("source_format") != "RMBench" or metadata.get("source_path") != "native_collection"):
            raise ValueError("Converted data provenance does not match the checked native converter.")
        if len(state) > 1 and not np.allclose(actions[:-1], state[1:], atol=1e-5, rtol=0):
            raise ValueError(f"Next-record target alignment differs: {record['episode_id']}")
        duplicate_ids = (np.nonzero(np.all(np.diff(state, axis=0) == 0, axis=1))[0]+1).tolist()
        gripper_events = {str(j): (np.nonzero(np.abs(np.diff(actions[:, j])) > 0.05)[0]+1).tolist()
                          for j in (6, 13)}
        tail = int(stored["anchors"][-1])
        rows.append({"episode_id": record["episode_id"], "length": len(state), "last_anchor": tail,
                     "last_valid_actions": min(32, len(actions)-tail), "frequency_field": metadata.get("stored_frequency"),
                     "split": record["split"], "raw_sha256": record["raw_sha256"],
                     "duplicate_command_record_ids": duplicate_ids, "gripper_target_event_ids": gripper_events})
    return report(cfg, "data", True, episodes=rows, source=semantics,
                  prior_review_sha=sha256(Path(cfg["paths"]["prepared"])/"alignment_approved.json"),
                  scope="collector_and_converter_semantics_plus_actual_saved_records")


def execution_check(cfg, root, uuids, resume):
    require_report(cfg, "model")
    require_report(cfg, "data")
    scenes = expert_scenes(cfg)
    bank = torch.load(root/"model/request.pt", map_location="cpu", weights_only=True)["cases"]
    for task in TASKS:
        selected = [(i, c) for i, c in enumerate(bank) if c["task"] == task][:2]
        chunks = [torch.load(root/f"model/official/case_{i:02d}.pt", map_location="cpu",
                             weights_only=True)["clipped_actions"].tolist() for i, _ in selected]
        path = root/f"execution/{task}_chunks.json"
        atomic_json(path, {"chunks": chunks, "case_ids": [c["case_id"] for _, c in selected]})
        scene = next(s for s in scenes if s["task"] == task)
        scene.update(integration_actions_file=str(path),
                     integration_reference_root=str(source_root(cfg, "fastwam")))
    identity = binding(cfg)
    expert = parallel_group(cfg, root, "execution/expert", scenes, ["expert"], "expert", uuids, resume, identity)
    if not all(row["success"] for row in expert["episodes"]):
        report(cfg, "execution", False, expert=expert, reason="Official expert failed in seed-zero environment.")
        raise RuntimeError("Official expert failed; inspect simulator/asset evidence.")
    from .eval_state import EpisodeQueue
    native_queue = EpisodeQueue(root/"execution/expert")
    cadence = {}
    for job in native_queue.snapshot()["jobs"]:
        path = native_queue.root/job["directory"]/"cadence.json"
        cadence[job["scene"]["task"]] = read_json(path)
    data = read_json(root/"data.json")
    data["native_recollection_cadence"] = cadence
    data["timing_scope"] = "Source-defined observation/next-record command alignment; exact physics intervals are reported only when native recollection matches."
    atomic_json(root/"data.json", data)
    execution = parallel_group(cfg, root, "execution/commands", scenes, ["reference", "production"],
                               "integration_actions", uuids, resume, identity)
    from .eval_state import EpisodeQueue
    queue = EpisodeQueue(root/"execution/commands")
    results = {}
    for job in queue.snapshot()["jobs"]:
        directory = queue.root/job["directory"]
        result = read_json(directory/"simulator_result.json")
        calls = [json.loads(line) for line in (directory/"executed_actions.jsonl").read_text().splitlines()]
        results[(job["scene"]["task"], job["condition"])] = (result, calls)
    comparisons = []
    for task in TASKS:
        (ref, rc), (prod, pc) = results[(task, "reference")], results[(task, "production")]
        ref_targets = np.asarray([row["target"] for row in rc], dtype=np.float32)
        prod_targets = np.asarray([row["target"] for row in pc], dtype=np.float32)
        planned = np.asarray(read_json(root/f"execution/{task}_chunks.json")["chunks"], dtype=np.float32)[:, :16].reshape(32, 14)
        exact = (ref_targets.shape == prod_targets.shape == planned.shape
                 and np.array_equal(ref_targets, planned) and np.array_equal(prod_targets, planned))
        no_obs_steps = all(not value["physical_summary"]["observation_or_rpc_advanced_physics"] for value in (ref, prod))
        physical = all(np.isfinite(np.asarray([r["physical_after"] for r in rows])).all() for rows in (rc, pc))
        physical &= all(value["physical_summary"]["physics_steps"] > 0 for value in (ref, prod))
        physical_delta = float(np.max(np.abs(np.asarray([r["physical_after"] for r in rc]) -
                    np.asarray([r["physical_after"] for r in pc])))) if len(rc) == len(pc) else None
        passed = exact and no_obs_steps and physical and all(value["executed_targets"] == 32 for value in (ref, prod))
        comparisons.append({"task": task, "passed": bool(passed), "exact_target_sequence": exact,
            "get_obs_does_not_advance_physics": no_obs_steps, "physical_feedback_finite": bool(physical),
            "physical_path_max_delta": physical_delta, "scope": "two fixed chunks, no base success criterion"})
    value = report(cfg, "execution", all(r["passed"] for r in comparisons), comparisons=comparisons, expert=expert,
                   evidence_root="execution", scope="original_official_queue_vs_actual_RPC_queue")
    if not value["passed"]:
        raise RuntimeError("Action queue/execution contract failed; inspect execution.json.")
    return value



def pilot_check(cfg, root, uuid):
    from .dense import cache_observation
    from .model import S1Model, load_observation_encoders, encode_text
    require_report(cfg, "model")
    require_report(cfg, "data")
    require_report(cfg, "execution")
    os.environ["CUDA_VISIBLE_DEVICES"] = uuid
    configure_numerics(cfg)
    device = torch.device("cuda:0")
    model = S1Model(cfg, device).eval()
    vae, encoder, tokenizer = load_observation_encoders(cfg, device)
    normalizer = ReleaseNormalizer(cfg["paths"]["stats"])
    cases = torch.load(root/"model/request.pt", map_location="cpu", weights_only=True)["cases"]
    rows, started = [], time.monotonic()
    for index, case in enumerate(cases):
        check_stop(root)
        text, valid = encode_text(encoder, tokenizer, case["instruction"], device)
        encoded = cache_observation(model.backbone, vae, text, normalizer, case["state"],
                                    [image.numpy() for image in case["images"]], device)
        value = {key: tensor.detach().cpu() for key, tensor in encoded.items()}
        value.update(text=text.cpu(), text_valid=valid.cpu(), frame_id=case["frame_id"])
        path = root/f"pilot/case_{index:02d}.pt"
        atomic_torch(path, value)
        saved = torch.load(path, map_location="cpu", weights_only=True)
        official = torch.load(root/f"model/official/case_{index:02d}.pt", map_location="cpu", weights_only=True)
        checks = {key: exact_difference(saved[key], official[key])
                  for key in ("mosaic", "proprio", "text", "text_valid", "latent", "feature")}
        row = {"case_id": case["case_id"], "checks": checks, "sha256": sha256(path),
               "passed": all(item["exact"] for item in checks.values())}
        rows.append(row)
        append_jsonl(root/"pilot/checks.jsonl", row)
        print(f"[pilot] {index+1}/12 exact={row['passed']} ETA={(time.monotonic()-started)/(index+1)*(11-index):.1f}s",
              flush=True)
        if not row["passed"]:
            report(cfg, "pilot", False, cases=rows, first_failure=case["case_id"])
            raise ValueError("Actual dense-cache encoder differs from the independent official trace.")
    return report(cfg, "pilot", True, cases=rows, scope="shared_dense_encoder_and_serialization_vs_official")


def cache_check(cfg, root, uuid):
    from .model import S1Model
    from .evaluate import audit_cache
    require_report(cfg, "pilot")
    os.environ["CUDA_VISIBLE_DEVICES"] = uuid
    configure_numerics(cfg)
    dataset = CachedEpisodes(cfg, "val")
    manifest = read_json(Path(cfg["paths"]["prepared"])/"manifest.json")
    expected = fingerprint(make_cache_contract(cfg, manifest))
    if dataset.signature != expected or {r["episode_id"] for r in dataset.manifest["episodes"]} != {
            r["episode_id"] for r in manifest["episodes"]}:
        raise ValueError("Full cache identity/episode coverage mismatch.")
    total = sum(len(r["shards"]) for r in dataset.manifest["episodes"])
    done, started = 0, time.monotonic()
    for record in dataset.manifest["episodes"]:
        check_stop(root)
        path = dataset.root/record["file"]
        if sha256(path) != record["cache_sha256"]:
            raise ValueError(f"Episode checksum mismatch: {path}")
        ids = []
        for shard in record["shards"]:
            path = dataset.root/shard["file"]
            marker = read_json(path.with_suffix(".complete.json"))
            block = torch.load(path, map_location="cpu", weights_only=True)
            planned = list(range(shard["first"], shard["last"]+1))
            if (sha256(path) != shard["sha256"] or marker["sha256"] != shard["sha256"]
                    or marker["signature"] != expected or block["signature"] != expected
                    or marker["frame_ids"] != planned or block["frame_ids"].tolist() != planned):
                raise ValueError(f"Shard identity/checksum/index mismatch: {path}")
            if any(not torch.isfinite(block[name]).all() for name in ("features", "latents", "proprio")):
                raise ValueError(f"Non-finite cache: {path}")
            if (tuple(block["features"].shape) != (len(planned), 120, 3072)
                    or tuple(block["latents"].shape) != (len(planned), 48, 1, 24, 20)
                    or tuple(block["proprio"].shape) != (len(planned), 14)):
                raise ValueError(f"Shard shape mismatch: {path}")
            ids.extend(planned)
            done += 1
            if done % 16 == 0:
                print(f"[cache-files] {done}/{total} ETA={(time.monotonic()-started)/done*(total-done):.1f}s", flush=True)
        if ids != list(range(record["length"])):
            raise ValueError(f"Missing/duplicated dense frames: {record['episode_id']}")
    model = S1Model(cfg, torch.device("cuda:0")).eval()
    comparisons = audit_cache(model, dataset, cfg, torch.device("cuda:0"))
    return report(cfg, "cache", True, cache_signature=expected, shards=done,
                  frames=sum(r["length"] for r in manifest["episodes"]), comparisons=comparisons,
                  scope="complete_shard_integrity_plus_twelve_raw_RGB_encoding_cases")


def training_check(cfg, root, uuid):
    from .model import S1Model
    from .history import select_ids, training_period
    require_report(cfg, "cache")
    os.environ["CUDA_VISIBLE_DEVICES"] = uuid
    configure_numerics(cfg)
    device = torch.device("cuda:0")
    torch.manual_seed(cfg["seed"])
    model = S1Model(cfg, device).eval()
    dataset = CachedEpisodes(cfg, "val")
    cases = torch.load(root/"model/request.pt", map_location="cpu", weights_only=True)["cases"]
    rows = []
    for index, case in enumerate(cases):
        check_stop(root)
        record = next(r for r in dataset.by_task[case["task"]] if r["episode_id"] == case["record"]["episode_id"])
        sample = dataset.at(record, case["frame_id"], period=8)
        batch = collate([sample], device)
        expected = torch.load(root/f"model/official/case_{index:02d}.pt", map_location="cpu", weights_only=True)
        noise, tau = case["noise"].to(device), case["probe_tau"].to(device)
        capture = {}
        with torch.no_grad(), velocity_capture(model, capture):
            loss, diagnostic = model(batch, noise, tau, gate_scale=0)
        target = model.scheduler.training_target(batch["actions"], noise, 1000*tau)
        noisy = model.scheduler.add_noise(batch["actions"], noise, 1000*tau)
        checks = {
            "actions": exact_difference(batch["actions"], expected["ground_truth"]),
            "action_valid": exact_difference(batch["action_valid"], case["action_valid"]),
            "noise": exact_difference(noise, case["noise"]),
            "noisy": exact_difference(noisy, expected["probe_noisy"]),
            "target": exact_difference(target, expected["probe_target"]),
            "velocity": exact_difference(capture["velocity"][0], expected["probe_velocity"]),
            "weight": exact_difference(model.scheduler.training_weight(1000*tau), expected["probe_weight"])}
        count = case["action_valid"].sum(1).to(device)
        oracle_error = ((expected["probe_velocity"].to(device).float()-expected["probe_target"].to(device)).square()
                        *case["action_valid"].to(device)[..., None]).sum((1, 2))/(14*count)
        oracle_loss = (expected["probe_weight"].to(device)*oracle_error).mean()
        checks["masked_loss"] = exact_difference(loss, oracle_loss)
        row = {"case_id": case["case_id"], "passed": all(c["exact"] for c in checks.values()), "checks": checks,
               "loss": float(loss)}
        rows.append(row)
        append_jsonl(root/"training/official_loss_checks.jsonl", row)
        print(f"[training-oracle] {index+1}/12 exact={row['passed']} loss={float(loss):.6f}", flush=True)
        if not row["passed"]:
            report(cfg, "training", False, oracle=rows, first_failure=case["case_id"])
            raise ValueError("Gate-zero training forward or masked loss differs from upstream.")
    # Exercise ragged history and a padded action tail using real stored training data.
    training = CachedEpisodes(cfg, "train")
    samples, mask_checks = [], []
    for task, period in zip(TASKS, (1, 16)):
        record = sorted(training.by_task[task], key=lambda r: r["episode_id"])[0]
        anchor = int(training.load(record)["anchors"][-1])
        for t in range(1, 17):
            item = training.at(record, anchor, period=t)
            selected = select_ids(range(anchor+1), anchor, t)
            if item["frame_ids"].tolist() != selected or anchor not in selected or max(selected) > anchor:
                raise ValueError("Production selection contains future frames or drops the current decision.")
            mask_checks.append({"task": task, "anchor": anchor, "T": t, "frames": len(selected),
                                "valid_actions": int(item["action_valid"].sum())})
        samples.append(training.at(record, anchor, period=period))
    batch = collate(samples, device)
    if batch["history_valid"].sum(1).tolist() != [len(s["frame_ids"]) for s in samples]:
        raise ValueError("History padding differs from actual selected lengths.")
    if not (~batch["action_valid"]).any():
        raise ValueError("The functional admission sample did not exercise a padded action tail.")
    periods = [training_period(cfg, step, slot) for step in range(32) for slot in range(16)]
    if not all(1 <= period <= 16 for period in periods):
        raise ValueError("Random training periods are outside the declared recipe.")
    model.train()
    model.zero_grad(set_to_none=True)
    generator = torch.Generator(device="cpu").manual_seed(cfg["seed"])
    noise = torch.randn(2, 32, 14, generator=generator).to(device)
    tau = torch.tensor([0.25, 0.75], device=device)
    attention_checks, handles = [], []
    def observe_attention(name, expects_history):
        def capture(module, args):
            source_valid = args[2] if len(args) > 2 else None
            if expects_history:
                expected_valid = batch["history_valid"].repeat_interleave(120, dim=1)
                passed = source_valid is not None and torch.equal(source_valid, expected_valid)
            else:
                passed = source_valid is None
            attention_checks.append({"module": name, "passed": bool(passed),
                                     "source_tokens": args[1].shape[1],
                                     "mask_shape": list(source_valid.shape) if source_valid is not None else None})
            if not passed:
                raise ValueError(f"Actual attention mask differs from the declared contract: {name}")
        return capture
    for index, block in enumerate(model.memory.reader):
        handles.append(block.cross.register_forward_pre_hook(observe_attention(f"reader.{index}.cross", True)))
        handles.append(block.self_attention.register_forward_pre_hook(observe_attention(f"reader.{index}.self", False)))
    for name, block in model.memory.injectors.items():
        handles.append(block.attention.register_forward_pre_hook(observe_attention(f"injector.{name}", False)))
    try:
        loss, diagnostic = model(batch, noise, tau)
        loss.backward()
    finally:
        for handle in handles:
            handle.remove()
    groups = {}
    missing, nonfinite = [], []
    for name, parameter in model.memory.named_parameters():
        if parameter.grad is None:
            missing.append(name)
            continue
        if not torch.isfinite(parameter.grad).all():
            nonfinite.append(name)
        group = ".".join(name.split(".")[:2]) if name.startswith(("reader.", "injectors.")) else name.split(".")[0]
        groups[group] = groups.get(group, 0.0)+float(parameter.grad.float().square().sum())
    frozen = all(not p.requires_grad and p.grad is None for p in model.backbone.parameters())
    passed = bool(torch.isfinite(loss) and frozen and not missing and not nonfinite and all(v > 0 for v in groups.values()))
    value = report(cfg, "training", passed, oracle=rows, history_mask_cases=mask_checks,
                   period_histogram={str(t): periods.count(t) for t in range(1, 17)},
                   gradient_norms={key: value**0.5 for key, value in groups.items()},
                   missing_gradients=missing, nonfinite_gradients=nonfinite, frozen_without_gradients=frozen,
                   functional_loss=float(loss), actual_attention_masks=attention_checks,
                   valid_actions=batch["action_valid"].sum(1).tolist(),
                   history_lengths=batch["history_valid"].sum(1).tolist(), optimizer_updates=0,
                   scope="actual_S1_forward_backward_no_optimizer_update")
    model.zero_grad(set_to_none=True)
    if not passed:
        raise ValueError("S1 gradient/freeze/mask admission failed; inspect training.json.")
    return value


def admit(cfg):
    expected = binding(cfg)
    run = Path(cfg["paths"]["run"])
    evidence = run/"integration_evidence"
    reports = {}
    for name in REQUIRED:
        value = require_report(cfg, name)
        destination = evidence/f"{name}.json"
        atomic_json(destination, value)
        reports[name] = {"file": destination.name, "sha256": sha256(destination)}
    for name in ("sources.json", "reference_sources.tar.gz", "adapter_audit.json", "runtime.json"):
        shutil.copy2(output_root(cfg)/name, evidence/name)
    simulator = Path(cfg["root"])/cfg["closed_loop"]["simulator_root"]
    simulator_files = {}
    with tarfile.open(evidence/"simulator_sources.tar.gz", "w:gz") as archive:
        for folder in ("envs", "scripts", "script", "env_cfg", "task_config", "description", "data"):
            for path in sorted((simulator/folder).rglob("*")):
                if path.is_file() and path.suffix in (".py", ".yaml", ".yml", ".json") and "__pycache__" not in path.parts:
                    relative = str(path.relative_to(simulator))
                    simulator_files[relative] = sha256(path)
                    archive.add(path, arcname=relative, recursive=False)
    atomic_json(evidence/"simulator_sources.json", {"files": simulator_files,
                                                  "archive_sha256": sha256(evidence/"simulator_sources.tar.gz")})
    value = {"version": VERSION, "passed": True, "binding": expected, "reports": reports,
             "criterion": "model_execution_labels_cache_gradients_not_zero_shot_success",
             "reference_snapshot_sha256": sha256(evidence/"reference_sources.tar.gz"),
             "simulator_snapshot_manifest_sha256": sha256(evidence/"simulator_sources.json")}
    atomic_json(run/"integration_admission.json", value)
    from .integration_contract import verify_admission
    verify_admission(cfg, expected["cache_signature"])
    print(f"[admission] passed: {run/'integration_admission.json'}", flush=True)


def restore_reference(cfg):
    """Restore only hash-locked reference source files from the training recovery bundle."""
    evidence = Path(cfg["paths"]["run"])/"integration_evidence"
    lock = read_json(evidence/"sources.json")
    admission = read_json(Path(cfg["paths"]["run"])/"integration_admission.json")
    archive = evidence/"reference_sources.tar.gz"
    if sha256(archive) != admission["reference_snapshot_sha256"]:
        raise ValueError("Reference recovery archive checksum mismatch.")
    with tarfile.open(archive, "r:gz") as stream:
        members = {member.name: member for member in stream.getmembers()}
        for kind, info in lock["repositories"].items():
            root = source_root(cfg, kind)
            for relative, expected in info["files"].items():
                target = (root/relative).resolve()
                if not target.is_relative_to(root) or target == root:
                    raise ValueError("Reference archive path escapes its pinned root.")
                member = members[f"{kind}/{relative}"]
                if not member.isfile():
                    raise ValueError("Only locked regular source files may be restored.")
                data = stream.extractfile(member).read()
                import hashlib
                if hashlib.sha256(data).hexdigest() != expected:
                    raise ValueError("Reference source member checksum mismatch.")
                if target.exists() and sha256(target) != expected:
                    raise ValueError(f"Existing reference differs; preserve it before restore: {target}")
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(data)
    atomic_json(output_root(cfg)/"sources.json", lock)
    print("[reference-restore] locked source restored; model/data downloads are separate.", flush=True)


def restore_simulator(cfg):
    evidence = Path(cfg["paths"]["run"])/"integration_evidence"
    admission = read_json(Path(cfg["paths"]["run"])/"integration_admission.json")
    manifest_path = evidence/"simulator_sources.json"
    if sha256(manifest_path) != admission["simulator_snapshot_manifest_sha256"]:
        raise ValueError("Simulator source manifest checksum mismatch.")
    manifest = read_json(manifest_path)
    archive = evidence/"simulator_sources.tar.gz"
    if sha256(archive) != manifest["archive_sha256"]:
        raise ValueError("Simulator source archive checksum mismatch.")
    root = (Path(cfg["root"])/cfg["closed_loop"]["simulator_root"]).resolve()
    if not root.is_dir():
        raise ValueError("Clone the user's RMBench fork and restore assets before source recovery.")
    import hashlib
    with tarfile.open(archive, "r:gz") as stream:
        for member in stream.getmembers():
            target = (root/member.name).resolve()
            if not target.is_relative_to(root) or target == root or not member.isfile():
                raise ValueError("Unexpected simulator recovery member.")
            data = stream.extractfile(member).read()
            if hashlib.sha256(data).hexdigest() != manifest["files"].get(member.name):
                raise ValueError("Simulator source member checksum mismatch.")
            if target.exists() and sha256(target) != manifest["files"][member.name]:
                preserved = Path(cfg["paths"]["run"])/"simulator_before_restore"/str(time.time_ns())/member.name
                preserved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, preserved)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    print("[simulator-restore] Exact saved sources restored; changed prior files retained in simulator_before_restore.",
          flush=True)


def package(cfg, compact=True):
    root = output_root(cfg)
    directory = root/"packages"/f"{time.time_ns()}"
    directory.mkdir(parents=True, exist_ok=True)
    archive = directory/"integration.tar.zst"
    members = {}
    temporary = directory/"integration.tar"
    with tarfile.open(temporary, "w") as stream:
        for path in sorted(root.rglob("*")):
            if not path.is_file() or "packages" in path.parts or path.suffix in (".lock", ".sock"):
                continue
            relative = path.relative_to(root)
            if compact and (path.suffix.lower() not in (".json", ".jsonl", ".log", ".gz") or "frames" in relative.parts):
                continue
            members[str(relative)] = sha256(path)
            stream.add(path, arcname=str(relative), recursive=False)
        for subtree in ("src", "scripts/memory_s1", "configs", "requirements"):
            for path in sorted((Path(cfg["root"])/subtree).rglob("*")):
                if path.is_file() and path.suffix in (".py", ".sh", ".yaml", ".yml", ".json", ".txt") and "__pycache__" not in path.parts:
                    relative = "code/"+str(path.relative_to(cfg["root"]))
                    members[relative] = sha256(path)
                    stream.add(path, arcname=relative, recursive=False)
    subprocess.run(["zstd", "-T4", "-3", "--rm", str(temporary)], check=True)
    atomic_json(directory/"manifest.json", {"archive": archive.name, "sha256": sha256(archive),
                "members": members, "compact": compact, "bytes": archive.stat().st_size})
    (directory/"SHA256.sha256").write_text(f"{sha256(archive)}  {archive.name}\n")
    print(f"[package] {directory} bytes={archive.stat().st_size}", flush=True)
    return directory


def upload_results(cfg, stage):
    root = output_root(cfg)
    directory = package(cfg, compact=True)
    command = [cfg["hf"]["python"], str(Path(cfg["root"])/"scripts/memory_s1/hf_tools.py"),
        "upload-package", "--repo", cfg["hf"]["backup_repo"], "--repo-type", "model",
        "--directory", str(directory), "--prefix", f"integration/{root.name}/{stage}/{directory.name}",
        "--quota-gib", str(cfg["hf"]["quota_gib"]), "--reserve-gib", str(cfg["hf"]["reserve_gib"])]
    started = time.monotonic()
    env = os.environ.copy()
    env.pop("HF_HUB_OFFLINE", None)
    env.pop("TRANSFORMERS_OFFLINE", None)
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=600, env=env)
    except subprocess.TimeoutExpired:
        atomic_json(root/"UPLOAD_FAILED.json", {"stage": stage, "command": command,
                    "directory": str(directory), "stderr": "HF upload timed out after 600 seconds."})
        raise
    if result.returncode:
        atomic_json(root/"UPLOAD_FAILED.json", {"stage": stage, "command": command,
                    "directory": str(directory), "stdout": result.stdout, "stderr": result.stderr})
        raise RuntimeError("HF upload failed; retained compact package and retry command are in UPLOAD_FAILED.json.")
    print(result.stdout, flush=True)
    append_jsonl(root/"hf_uploads.jsonl", {"stage": stage, "seconds": time.monotonic()-started,
                                       "directory": str(directory), "response": result.stdout})
    (root/"UPLOAD_FAILED.json").unlink(missing_ok=True)


def run(args):
    cfg = load_config(args.config)
    root = output_root(cfg)
    if Path(args.output).resolve() != root:
        raise ValueError("--output differs from the configuration-bound integration directory.")
    root.mkdir(parents=True, exist_ok=True)
    with locked(root/"launcher.lock", blocking=False):
        prior = read_json(root/"launcher.json") if (root/"launcher.json").exists() else {}
        if is_alive(prior.get("owner")):
            raise ValueError("An owned integration launcher is already running.")
        if (root/"STOP.json").exists():
            if not args.resume:
                raise ValueError("A prior stop marker exists; inspect it and use --resume.")
            (root/"STOP.json").unlink()
        print("[identity] verifying source/resource/data hashes; no model downloads or parameter updates", flush=True)
        atomic_json(root/"launcher.json", {"owner": process_identity(), "stage": args.stage,
                                          "argv": sys.argv, "binding": binding(cfg)})
        from importlib import metadata as package_metadata
        versions = {}
        for name in ("torch", "transformers", "numpy", "hydra-core", "huggingface-hub"):
            try:
                versions[name] = package_metadata.version(name)
            except package_metadata.PackageNotFoundError:
                versions[name] = None
        atomic_json(root/"runtime.json", {"python": sys.version, "executable": sys.executable,
            "versions": versions, "torch_cuda": torch.version.cuda, "numerics": cfg["integration"]["attention_backend"],
            "nvidia": subprocess.check_output(["nvidia-smi", "--query-gpu=index,name,uuid,driver_version",
                                              "--format=csv,noheader"], text=True)})
        started = time.monotonic()
        atomic_json(root/"status.json", {"stage": args.stage, "state": "running", "started": time.time()})
        try:
            previous = read_json(root/f"{args.stage}.json") if (root/f"{args.stage}.json").exists() else {}
            reuse = args.resume and args.stage != "admit" and previous.get("passed") is True
            if reuse:
                require_report(cfg, args.stage)
                print(f"[resume] {args.stage} already passed with the same identity; reuse its evidence.", flush=True)
            else:
                inventory = gpu_inventory()
                uuids = [inventory[int(index)] for index in args.gpus.split(",")]
                if args.stage == "model":
                    model_check(cfg, root, uuids[0])
                elif args.stage == "execution":
                    data_check(cfg)
                    execution_check(cfg, root, uuids, args.resume)
                elif args.stage == "pilot":
                    pilot_check(cfg, root, uuids[0])
                elif args.stage == "cache":
                    cache_check(cfg, root, uuids[0])
                elif args.stage == "training":
                    training_check(cfg, root, uuids[0])
                else:
                    admit(cfg)
            if args.hf_results:
                upload_results(cfg, args.stage)
            atomic_json(root/"status.json", {"stage": args.stage, "state": "complete", "seconds": time.monotonic()-started})
        except EvaluationInterrupted:
            atomic_json(root/"status.json", {"stage": args.stage, "state": "stopped", "seconds": time.monotonic()-started})
            raise SystemExit(2)
        except Exception as error:
            atomic_json(root/"status.json", {"stage": args.stage, "state": "error", "seconds": time.monotonic()-started,
                                           "error": f"{type(error).__name__}: {error}"})
            raise


def main():
    parser = argparse.ArgumentParser(__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("sources", "restore-reference", "restore-simulator", "package"):
        child = sub.add_parser(name)
        child.add_argument("--config", required=True)
        if name == "package":
            child.add_argument("--full", action="store_true")
    child = sub.add_parser("run")
    child.add_argument("--config", required=True)
    child.add_argument("--output", required=True)
    child.add_argument("--stage", choices=("model", "execution", "pilot", "cache", "training", "admit"), required=True)
    child.add_argument("--gpus", default="0,1,2,3,4,5,6,7")
    child.add_argument("--resume", action="store_true")
    child.add_argument("--hf-results", action="store_true")
    for name in ("status", "stop"):
        child = sub.add_parser(name)
        child.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.command == "run":
        run(args)
    elif args.command in ("status", "stop"):
        root = Path(args.output)
        if args.command == "stop":
            atomic_json(root/"STOP.json", {"mode": "now", "requested": time.time()})
            print("Stop requested; completed evidence stays valid, interrupted simulator episodes restart on resume.")
        else:
            for name in ("status.json", "launcher.json"):
                if (root/name).exists():
                    value = read_json(root/name)
                    if name == "launcher.json":
                        value["alive"] = is_alive(value.get("owner"))
                    print(name, json.dumps(value, indent=2))
    else:
        cfg = load_config(args.config)
        if args.command == "sources":
            sources(cfg)
        elif args.command == "restore-reference":
            restore_reference(cfg)
        elif args.command == "restore-simulator":
            restore_simulator(cfg)
        else:
            package(cfg, compact=not args.full)


if __name__ == "__main__":
    main()
