"""Explicit one-scene H100 arm/gripper intervention; original step2000 only."""
from __future__ import annotations

import argparse
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
from .grasp_causal_metrics import MODES, interpretation

STAGES = ("prepare", "run", "report", "pack")
TOOLS = ("configs/memory_s1/grasp_causal_h100.json", "scripts/memory_s1/portable/h100/grasp_causal.sh",
         "src/fastwam/memory_s1/grasp_causal.py", "src/fastwam/memory_s1/grasp_causal_worker.py",
         "src/fastwam/memory_s1/grasp_causal_metrics.py", "src/fastwam/memory_s1/initial_intervention_worker.py",
         "src/fastwam/memory_s1/initial_intervention.py", "src/fastwam/memory_s1/grasp_bridge.py",
         "src/fastwam/memory_s1/memory_probe.py", "src/fastwam/memory_s1/memory_probe_worker.py",
         "src/fastwam/memory_s1/memory_repair.py", "src/fastwam/memory_s1/selection_runtime.py",
         "src/fastwam/memory_s1/eval_parallel.py", "src/fastwam/memory_s1/simulator_backend.py",
         "src/fastwam/memory_s1/fused_evaluation.py", "scripts/memory_s1/sim_eval.py",
         "scripts/memory_s1/sim_executor.py", "scripts/memory_s1/sim_feedback.py",
         "scripts/memory_s1/sim_instrumentation.py", "scripts/memory_s1/deploy_policy.py")


class CausalBlocked(RuntimeError):
    """Expected diagnostic refusal, distinct from infrastructure errors."""


def profile(root):
    spec = read(root / TOOLS[0])
    if (spec["schema"] != "grasp-component-causal-v1" or spec["machine"] != "h100"
            or spec["task"] != "swap_blocks" or spec["checkpoint_step"] != 2000
            or spec["cases"] != list(MODES) or spec["expert_prefix_targets"] != 48 or spec["target_cap"] != 128
            or spec.get("rpc_reset_protocol") != "idempotent_before_first_decision_v1"):
        raise ValueError("Expected original step2000, one swap scene, four component conditions, 48/128 targets")
    for key in ("output", "repair_output"):
        if not checked_path(root, spec[key]).is_relative_to(root / "outputs"):
            raise ValueError(f"Expected outputs directory for {key}")
    return spec


def stop_check(output):
    if (output / "STOP.json").exists():
        raise InterruptedError("Causal diagnostic stopped; use explicit resume run")


def case_identity(bound, mode):
    return signature({"run": signature(bound), "component_mode": mode})


def completed_case(output, bound, mode):
    folder = output / "cases" / mode
    if not (folder / "COMPLETE.json").exists():
        return None
    receipt = read(folder / "COMPLETE.json")
    if receipt["identity"] != case_identity(bound, mode):
        raise ValueError(f"Case identity changed: {folder}")
    verify(folder, receipt["files"])
    result = read(folder / "result.json")
    if result["mode"] != mode or result["checkpoint_step"] != 2000:
        raise ValueError("Completed component/checkpoint differs")
    return result


def reviewed_archive(old, digest):
    """A later pack must not hide the already-reviewed immutable package."""
    candidates = []
    pointer = old / "LATEST_PACKAGE.json"
    if pointer.exists():
        path = Path(read(pointer)["archive"]).resolve()
        if not path.is_relative_to(old.resolve() / "packages"):
            raise ValueError("Repair package pointer escapes its packages directory")
        candidates.append(path)
    candidates.extend(sorted((old / "packages").glob("*/memory_repair.tar.gz")))
    for path in dict.fromkeys(candidates):
        if path.is_file() and sha(path) == digest:
            return path
    raise FileNotFoundError(f"Reviewed repair package missing: SHA256={digest}; preserve other packages")


def prepare(root, spec, output):
    import numpy as np
    from .integration_contract import simulator_sources
    old = checked_path(root, spec["repair_output"])
    manifest = archive_manifest(reviewed_archive(old, spec["repair_archive_sha256"]),
                                spec["repair_archive_sha256"], "FILES.json")
    required = ("IDENTITY.json", "WINDOWS.json", "fit/result.json", "zero/result.json", "frozen/FROZEN.json",
                "fit/original/samples.jsonl", "fit/query_scale_64/samples.jsonl",
                "prepared_manifest.json", "prepared_alignment_approved.json")
    verify(old, {name: manifest[name] for name in required})
    prior = read(old / "IDENTITY.json")
    if sources(root) != prior["sources"] or runtime() != prior["runtime"]:
        raise ValueError("Production/model runtime changed since the reviewed repair; retain old evidence")
    cfg = copy.deepcopy(prior["config"])
    if (Path(cfg["root"]).resolve() != root or cfg["history"].get("online_period") != 8
            or cfg["history"].get("online_mode", "fixed") != "fixed" or cfg["history"].get("online_cycle")
            or cfg["history"]["archive_stride"] != 1):
        raise ValueError("Expected the original dense archive and fixed T=8 protocol")
    if simulator_runtime(cfg) != prior["simulator_runtime"]:
        raise ValueError("Simulator Python/packages changed since the reviewed evidence")
    probe_dir = checked_path(root, prior["protocol"]["probe_output"])
    probe_manifest = archive_manifest(checked_path(root, prior["protocol"]["probe_archive"]),
                                      prior["protocol"]["probe_archive_sha256"], "FILES.json")
    verify(probe_dir, {"IDENTITY.json": probe_manifest["IDENTITY.json"]})
    probe = read(probe_dir / "IDENTITY.json")
    if signature(probe) != prior["probe_identity"]:
        raise ValueError("Repair/probe provenance differs")
    history = checked_path(root, probe["protocol"]["intervention_output"])
    history_manifest = archive_manifest(checked_path(root, probe["protocol"]["intervention_archive"]),
                                        probe["protocol"]["intervention_archive_sha256"], "FILES.json")
    verify(history, {"IDENTITY.json": history_manifest["IDENTITY.json"]})
    historic = read(history / "IDENTITY.json")
    sim_sources = simulator_sources(cfg)
    if sim_sources != historic["runtime"]["simulator_sources"]:
        raise ValueError("Simulator task/assets/robot/camera identity changed")
    bundle = read(old / "frozen/FROZEN.json")
    weight = prior["weights"]["step_002000"]
    verify(root, {weight["relative"]: weight["sha256"]})
    for key, digest in prior["resources"].items():
        if sha(cfg["paths"][key]) != digest:
            raise ValueError(f"Model resource changed: {cfg['paths'][key]}")
    verify(cfg["paths"]["tokenizer"], prior["tokenizer_files"])
    # Baseline reuse requires exact execution dependencies as well as inputs.
    execution = {name: sha(root / name) for name in TOOLS
                 if name.startswith("scripts/memory_s1/sim_") or name == "scripts/memory_s1/deploy_policy.py"}
    backend_names = [name for name in history_manifest
                     if name.startswith("expert-prefix/swap_blocks/simulator_progress/fused_backend_") and name.endswith(".json")]
    if len(backend_names) < 2:
        raise ValueError("Historical evidence lacks both-arm fused extension identities")
    verify(history, {name: history_manifest[name] for name in backend_names})
    old_extensions = {}
    for name in backend_names:
        backend = read(history / name)
        if not backend.get("passed"):
            raise ValueError("Historical fused backend qualification failed")
        for module, record in backend["extensions"].items():
            if module in old_extensions and old_extensions[module] != record:
                raise ValueError("Historical planners loaded different extension binaries")
            old_extensions[module] = record
    extensions = {}
    for name, record in old_extensions.items():
        path = Path(record["path"])
        if not path.is_file():
            raise FileNotFoundError(f"Missing simulator extension binary: {path}")
        extensions[name] = {"path": str(path), "sha256": sha(path)}
    reuse_core = {name: digest for name, digest in sources(root).items()
                  if not name.endswith("/grasp_bridge.py")}
    reusable = bool(spec["reuse_policy_baseline"] and weight == historic["weight"]
                    and cfg == historic["config"]
                    and extensions == old_extensions
                    and all(historic["code"].get(k) == v for k, v in (execution | reuse_core).items()))
    bound = {"schema": spec["schema"], "protocol": spec, "config": cfg, "sources": sources(root),
             "tools": {name: sha(root / name) for name in TOOLS}, "runtime": runtime(),
             "simulator_runtime": prior["simulator_runtime"], "simulator_sources": sim_sources,
             "simulator_extensions": extensions,
             "weights": {"step_002000": weight}, "resources": prior["resources"],
             "tokenizer_files": prior["tokenizer_files"], "repair_archive_sha256": spec["repair_archive_sha256"],
             "historical_identity": signature(historic), "history_directory": str(history),
             "baseline_reuse_eligible": reusable, "execution_sources": execution,
             "git_commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
             "working_diff_sha256": __import__("hashlib").sha256(subprocess.check_output(["git", "-C", str(root), "diff", "HEAD", "--binary"])).hexdigest(),
             "scope": "one-scene component intervention; zero optimizer updates; training root cause not assumed"}
    if (output / "IDENTITY.json").exists() and read(output / "IDENTITY.json") != bound:
        raise ValueError("Identity changed; preserve this output and use a new profile")
    if (output / "PREPARED.json").exists():
        verify(output, read(output / "PREPARED.json")["files"])
        print("[reuse] frozen scene, original weight and prepared audit verified", flush=True)
        return
    if shutil.disk_usage(output).free < spec["local_reserve_gib"] * 2**30:
        raise ValueError("Need 5 GiB free for four bounded evidence traces")
    for name in required:
        copy_verified(old, name, manifest, output / "historical_repair" / name)
    item = bundle["inputs"]["swap_blocks_online_initial"]
    needed = {"frozen/FROZEN.json", "frozen/" + bundle["experts"][spec["task"]]["path"]}
    needed.update("frozen/" + name for name in item["images"])
    for name in needed:
        copy_verified(old, name, manifest, output / name)
    expert = read(output / "frozen" / bundle["experts"][spec["task"]]["path"])
    targets = np.asarray(expert["targets"], np.float32)
    if (targets.ndim != 2 or targets.shape[1] != 14 or len(targets) < spec["target_cap"] + 16
            or not np.isfinite(targets).all() or spec["object"] not in expert["initial"]["objects"]):
        raise ValueError("Missing genuine expert horizon/object identity")
    review = []
    fit = read(old / "fit/result.json")
    if len(fit["measurements"]) != 96 or fit["updates_per_arm"] != 64:
        raise ValueError("Expected the reviewed 96 measurements from two 64-update arms")
    streams = {mode: [json.loads(line) for line in (old / "fit" / mode / "samples.jsonl").read_text().splitlines()]
               for mode in ("original", "query_scale_64")}
    if (streams["original"] != streams["query_scale_64"] or len(streams["original"]) != 1024
            or any(sorted(row["global_slot"] for row in streams["original"] if row["update"] == update)
                   != list(range(16)) for update in range(1, 65))):
        raise ValueError("Reviewed fitting streams/global slots differ")
    for window in read(old / "WINDOWS.json"):
        records = {}
        for mode in ("original", "query_scale_64"):
            for phase in ("before", "after"):
                subset = [r for r in fit["measurements"] if (r["case"], r["mode"], r["phase"]) == (window["id"], mode, phase)]
                if len(subset) != 3:
                    raise ValueError("Incomplete reviewed three-noise fit measurements")
                records[mode + "_" + phase] = {k: sum(r[k] for r in subset) / 3 for k in
                         ("arm_rmse_first16_rad", "gripper_mae_first16")}
                records[mode + "_" + phase]["by_noise"] = [{k: row[k] for k in
                    ("noise", "arm_rmse_first16_rad", "gripper_mae_first16", "joint_mae_first16")} for row in subset]
        review.append({"window": window["id"], "group": window["group"], "anchor": window["item"]["anchor"],
                       "origin": window["item"].get("origin"), "measurements": records})
    write(output / "GENERALIZATION_REVIEW.json", {"windows": review,
          "diagnostic_training_samples": {mode: {w["id"]: sum(row["case"] == w["id"] for row in streams[mode])
                for w in read(old / "WINDOWS.json") if w["group"] == "train"}
                for mode in ("original", "query_scale_64")},
          "assessment": "narrow-window fitting improves training windows but regresses held-out expert stages",
          "limitation": "This alone does not establish the full S1 training cause or prove Q generalization",
          "phase_average_warning": "Initial-motion improvement cannot cancel grasp/lift regression"})
    audit = []
    for window in read(old / "WINDOWS.json"):
        t = np.asarray(window["item"]["targets"], np.float32)
        indices = np.flatnonzero(t[:, 13] < .5)
        audit.append({"window": window["id"], "anchor": window["item"]["anchor"],
                      "observed_right_gripper": window["item"]["proprio"][13],
                      "next_right_gripper": t[:, 13].tolist(),
                      "first_local_target_below_half_zero_based": int(indices[0]) if len(indices) else None,
                      "source": window["item"].get("origin"), "raw_physical_interval": "unknown_without_collector_clock"})
    write(output / "SUPERVISION_AUDIT.json", {"windows": audit, "expert_physical_step_ids": expert["physical_step_ids"],
          "contract": "frame f is an observation after f completed targets; target[f] is next; actual clocks validated during each case",
          "same_frame_id_is_not_same_phase": True, "optimizer_updates": 0})
    # Save only authenticated, durable policy evidence; preserve old signatures.
    old_case = history / "expert-prefix" / spec["task"]
    if reusable and (old_case / "COMPLETE.json").exists():
        prefix = f"expert-prefix/{spec['task']}/"
        signed = {name: h for name, h in history_manifest.items() if name.startswith(prefix)}
        verify(history, signed)
        receipt = read(old_case / "COMPLETE.json")
        if receipt["identity"] != signature(historic):
            raise ValueError("Historical policy case has a different identity")
        verify(old_case, receipt["files"])
        for name in signed:
            copy_verified(history, name, history_manifest, output / "baseline_policy" / name.removeprefix(prefix))
        write(output / "BASELINE_REUSE.json", {"eligible": True, "historical_identity": signature(historic),
              "source": str(old_case), "files": files(output / "baseline_policy"),
              "reason": "exact core/runtime/scene/weight/config and execution source identities; handoff is checked again"})
    else:
        write(output / "BASELINE_REUSE.json", {"eligible": False, "reason": "No exact eligible complete historical policy case; run bounded policy control"})
    write(output / "IDENTITY.json", bound)
    mapping = {name: h for name, h in files(output).items() if not set(Path(name).parts) & {"launches", "tmp", "packages"}
               and name not in ("PREPARED.json", "LAUNCH.json", "STATUS.json", "latest_log.txt", "job.lock")}
    write(output / "PREPARED.json", {"identity": signature(bound), "files": mapping})
    print(f"[prepared] original step2000; swap seed={item['seed']}; prefix=48 cap=128; policy_reuse={read(output/'BASELINE_REUSE.json')['eligible']}", flush=True)


def require_prepared(root, output):
    from .integration_contract import simulator_sources
    bound = read(output / "IDENTITY.json")
    if (bound["protocol"] != profile(root) or bound["sources"] != sources(root)
            or bound["tools"] != {name: sha(root / name) for name in TOOLS} or bound["runtime"] != runtime()
            or bound["simulator_runtime"] != simulator_runtime(bound["config"])
            or bound["simulator_sources"] != simulator_sources(bound["config"])):
        raise ValueError("Causal code/config/runtime/asset identity changed; do not mix results")
    verify(output, read(output / "PREPARED.json")["files"])
    for record in bound["weights"].values():
        verify(root, {record["relative"]: record["sha256"]})
    for key, digest in bound["resources"].items():
        if sha(bound["config"]["paths"][key]) != digest:
            raise ValueError(f"Model resource changed: {key}")
    verify(bound["config"]["paths"]["tokenizer"], bound["tokenizer_files"])
    for record in bound["simulator_extensions"].values():
        if not Path(record["path"]).is_file() or sha(record["path"]) != record["sha256"]:
            raise ValueError(f"Simulator extension changed: {record['path']}")
    return bound


def run(root, output):
    bound = require_prepared(root, output)
    if all(completed_case(output, bound, mode) for mode in MODES):
        print("[reuse] all four causal cases verified", flush=True)
        return
    for name in ("BLOCKED.json", "ERROR.json"):
        if (output / name).exists():
            previous = output / "previous_errors" / f"{time.time_ns()}_{name}"
            previous.parent.mkdir(exist_ok=True)
            (output / name).rename(previous)
    gpu = bound["runtime"]["gpu"].split(",")[0].strip()
    active = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"], text=True)
    if any(row.split(",")[0].strip() == gpu for row in active.splitlines()):
        raise CausalBlocked("H100 is occupied; explicitly stop its owning task first")
    folder = output / "run"
    folder.mkdir(exist_ok=True)
    log = folder / f"worker_{time.time_ns()}.log"
    command = ["/opt/mwam/bin/python", "-B", "-u", "-m", "fastwam.memory_s1.grasp_causal_worker",
               "--root", str(root), "--output", str(output), "--gpu-uuid", gpu]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=gpu)
    env.pop("CUDA_LAUNCH_BLOCKING", None)
    write(folder / "command.json", command)
    started, heartbeat = time.monotonic(), 0.
    with log.open("w", encoding="utf-8") as stream:
        child = owned_popen(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            with log.open(encoding="utf-8", errors="replace") as reader:
                while child.poll() is None:
                    print(reader.read(), end="", flush=True)
                    stop_check(output)
                    if time.monotonic() - started > bound["protocol"]["stage_timeout_seconds"]:
                        raise TimeoutError(f"Bounded diagnostic stage timeout: {log}")
                    if time.monotonic() - heartbeat >= 15:
                        state = read(output / "PROGRESS.json") if (output / "PROGRESS.json").exists() else {}
                        print(f"[causal] mode={state.get('mode','-')} phase={state.get('phase','model_load')} "
                              f"complete={state.get('completed',0)}/4 targets={state.get('targets',0)}/128 "
                              f"elapsed={time.monotonic()-started:.0f}s", flush=True)
                        heartbeat = time.monotonic()
                    time.sleep(1)
                print(reader.read(), end="", flush=True)
            if child.returncode == 3:
                raise CausalBlocked(f"Diagnostic control blocked; inspect {output / 'BLOCKED.json'}; report/pack remain available")
            if child.returncode:
                raise RuntimeError(f"Causal worker exited {child.returncode}: {log}\n{log.read_text(errors='replace')[-12000:]}")
            if not all(completed_case(output, bound, mode) for mode in MODES):
                raise ValueError("Worker returned without all four complete cases")
        finally:
            stop_children([child])


def report(output):
    bound = read(output / "IDENTITY.json")
    results = {mode: completed_case(output, bound, mode) for mode in MODES}
    results = {k: v for k, v in results.items() if v is not None}
    value = {"identity": signature(bound), "cases": results, "interpretation": interpretation(results),
             "generalization": read(output / "GENERALIZATION_REVIEW.json"),
             "supervision": read(output / "SUPERVISION_AUDIT.json"),
             "missing": [mode for mode in MODES if mode not in results], "optimizer_updates": 0,
             "scope": "component intervention; expert assistance excluded from benchmark success rate"}
    write(output / "REPORT.json", value)
    columns = ("mode", "source", "executed_targets", "max_lift_m", "final_lift_m", "lift_contact_proxy", "drop_while_closed", "first_right_close")
    with (output / "components.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for mode in MODES:
            case = results.get(mode)
            if case is None:
                writer.writerow({"mode": mode, "source": "pending"})
                continue
            m = case["metrics"]
            writer.writerow(dict(zip(columns, (mode, case["source"], m["executed_targets"], m["max_lift_after_handoff_m"],
                  m["final_lift_m"], m["lift_contact_proxy_observed"], m["drop_while_close_command_observed"], m["first_right_close_after_handoff"]))))
    phase_columns = ("mode", "phase", "targets", "left_arm_reference_rmse_rad", "right_arm_reference_rmse_rad",
                     "arm_tracking_rmse_rad", "right_gripper_reference_mae", "physics_seconds", "max_object_lift_m")
    with (output / "phases.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=phase_columns, extrasaction="ignore")
        writer.writeheader()
        for mode, case in results.items():
            for phase, metrics in case["metrics"]["phase_metrics"].items():
                writer.writerow({"mode": mode, "phase": phase, **metrics})
    print("MODE              SOURCE                TARGETS MAX_LIFT_m RETAINED_CONTACT DROP_WHILE_CLOSED", flush=True)
    for mode in MODES:
        case = results.get(mode)
        if case is None:
            print(f"{mode:<17} pending", flush=True)
        else:
            m = case["metrics"]
            print(f"{mode:<17} {case['source']:<21} {m['executed_targets']:>7} {m['max_lift_after_handoff_m']:>10.4f} "
                  f"{str(m['lift_contact_proxy_observed']):>16} {str(m['drop_while_close_command_observed']):>17}", flush=True)
    print(json.dumps(value["interpretation"], ensure_ascii=False, indent=2), flush=True)


def pack(root, output):
    report(output)
    bound = read(output / "IDENTITY.json")
    package = output / "packages" / str(time.time_ns())
    package.mkdir(parents=True)
    excluded = {"packages", "tmp", "interrupted", "__pycache__", "launches"}
    selected = [p for p in output.rglob("*") if p.is_file() and not p.is_symlink()
                and not set(p.relative_to(output).parts) & excluded and p.suffix != ".pt"
                and p.name not in ("job.lock", "LAUNCH.json", "latest_log.txt", "LATEST_PACKAGE.json", "STOP.json")
                and not p.name.endswith(".partial")]
    copied = []
    for name in sorted(set(bound["sources"]) | set(TOOLS)):
        p = package / "source" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, p)
        copied.append(p)
    mapping = {p.relative_to(output).as_posix(): sha(p) for p in selected}
    mapping.update({p.relative_to(package).as_posix(): sha(p) for p in copied})
    write(package / "FILES.json", mapping)
    archive = package / "grasp_causal.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        for p in selected:
            tar.add(p, arcname=p.relative_to(output).as_posix(), recursive=False)
        for p in copied + [package / "FILES.json"]:
            tar.add(p, arcname=p.relative_to(package).as_posix(), recursive=False)
    digest = sha(archive)
    (package / "SHA256SUMS").write_text(digest + "  grasp_causal.tar.gz\n", encoding="utf-8")
    write(output / "LATEST_PACKAGE.json", {"archive": str(archive), "sha256": digest, "identity": signature(bound)})
    print(f"[package] {archive}\nSHA256={digest}", flush=True)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("stage", choices=(*STAGES, "status", "stop"))
    parser.add_argument("--root", type=Path, default=Path("/workspace/FastWAM"))
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    spec = profile(root)
    output = checked_path(root, spec["output"])
    output.mkdir(parents=True, exist_ok=True)
    launch = read(output / "LAUNCH.json") if (output / "LAUNCH.json").exists() else {}
    if args.stage == "status":
        case_receipts = [mode for mode in MODES if (output / "cases" / mode / "COMPLETE.json").exists()]
        latest_report = read(output / "REPORT.json") if (output / "REPORT.json").exists() else {}
        print(json.dumps({"running": alive(launch.get("owner")), "launch": launch,
              "status": read(output / "STATUS.json") if (output / "STATUS.json").exists() else None,
              "progress": read(output / "PROGRESS.json") if (output / "PROGRESS.json").exists() else None,
              "completed_case_receipts": case_receipts, "total_cases": 4,
              "latest_report": latest_report.get("interpretation"),
              "diagnostic_block": read(output / "BLOCKED.json") if (output / "BLOCKED.json").exists() else None}, indent=2))
        return
    if args.stage == "stop":
        write(output / "STOP.json", {"time": time.time(), "scope": "recorded causal diagnostic tree only"})
        stop_owned_tree(launch.get("owner"))
        print("Stopped the recorded causal task. Complete cases retained; resume run is explicit.")
        return
    owner = process(os.getpgrp())
    receipt = os.environ.get("FW_GRASP_CAUSAL_EXIT", "")
    if (not owner or owner["pid"] != os.getppid() or os.getsid(0) != owner["pid"]
            or not receipt or not Path(receipt).resolve().is_relative_to(output / "launches")):
        raise ValueError("Use portable/h100/grasp_causal.sh owned nohup entry")
    if alive(launch.get("owner")) and launch["owner"]["pid"] != owner["pid"]:
        raise CausalBlocked("Another causal stage is active")
    if (output / "STOP.json").exists() and args.stage not in ("report", "pack"):
        if not args.resume:
            raise CausalBlocked("STOP exists; use explicit resume STAGE")
        (output / "STOP.json").rename(output / f"STOP.resumed_{time.time_ns()}.json")
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: (_ for _ in ()).throw(InterruptedError("Causal launcher stopped")))
    write(output / "LAUNCH.json", {"owner": owner, "worker": process(os.getpid()), "stage": args.stage,
                                   "started": time.time(), "argv": sys.argv})
    write(output / "STATUS.json", {"stage": args.stage, "state": "running"})
    started = time.monotonic()
    try:
        if args.stage == "prepare":
            prepare(root, spec, output)
        elif args.stage == "run":
            run(root, output)
        else:
            require_prepared(root, output)
            report(output) if args.stage == "report" else pack(root, output)
        write(output / "STATUS.json", {"stage": args.stage, "state": "complete", "seconds": time.monotonic() - started})
        print(f"[complete] {args.stage} seconds={time.monotonic()-started:.1f}", flush=True)
    except BaseException as error:
        state = "blocked" if isinstance(error, CausalBlocked) else "interrupted" if isinstance(error, InterruptedError) else "error"
        write(output / "STATUS.json", {"stage": args.stage, "state": state, "error": repr(error),
                                       "traceback": traceback.format_exc(), "seconds": time.monotonic()-started})
        if isinstance(error, CausalBlocked):
            print(f"[blocked] {error}", flush=True)
            raise SystemExit(3)
        raise


if __name__ == "__main__":
    main()
