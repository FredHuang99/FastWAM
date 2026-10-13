"""Single H100, matched diagnostic arms, immutable complete-update recovery."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import signal
import statistics
import time
import traceback

from .grasp_bridge import files, read, sha, signature, verify, write
from .memory_repair import PROBE_CASES, require_completion, stop_check
from .memory_repair_math import (ARMS, MODES, QUERY_SCALE, fit_gate, gradient_summary,
                                 mechanism_gate, query_scale)

_STOP = False


def boundary(output):
    if _STOP:
        raise InterruptedError("Worker stop deferred to a complete-update/case boundary")
    stop_check(output)


def progress(directory, stage, completed=0, total=0, **extra):
    write(directory / "progress.json", {"stage": stage, "completed": completed, "total": total,
                                       "updated_unix": time.time(), **extra})


def complete(directory, identity, result, external_files=None):
    write(directory / "result.json", result)
    mapping = {path.relative_to(directory).as_posix(): sha(path) for path in directory.rglob("*")
               if path.is_file() and not path.is_symlink()
               and not set(path.relative_to(directory).parts) & {"checkpoints", "interrupted", "encoded", "__pycache__"}
               and path.suffix != ".log" and not path.name.endswith(".partial")
               and path.name not in ("COMPLETE.json", "progress.json", "ERROR.json", "FILES.json")}
    write(directory / "COMPLETE.json", {"identity": identity, "files": mapping, **({"external_files": external_files} if external_files else {})})


def append(path, row):
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row, allow_nan=False) + "\n"); stream.flush()


def transfer(batch, device):
    return {key: value.to(device) for key, value in batch.items()}


def encoded_windows(model, encoders, cfg, output, selected, stage):
    import torch
    from .common import atomic_torch
    from .memory_probe_worker import assemble
    result = {}
    for window in selected:
        boundary(output)
        progress(stage,"encode_frozen_window",len(result),len(selected),case=window["id"],
                 operation_started_unix=time.time(),eta_scope="initial encoding; no measured total yet")
        folder = output / "encoded" / window["id"]
        folder.mkdir(parents=True, exist_ok=True)
        identity = signature({"run": read(output / "PREPARED.json")["identity"], "window": window})
        path = folder / "batch.pt"
        receipt_path = folder / "COMPLETE.json"
        if receipt_path.exists():
            value = read(receipt_path)
            if value["identity"] != identity: raise ValueError("Small diagnostic encoding identity changed")
            verify(folder, value["files"])
            saved = torch.load(path, map_location="cpu", weights_only=True)
        else:
            start = time.monotonic()
            batch, targets = assemble(model, encoders, cfg, output / "inputs" / window["id"], window)
            saved = {"batch": {k: v.detach().cpu() for k, v in batch.items()}, "targets": targets.detach().cpu()}
            atomic_torch(path, saved)
            write(receipt_path, {"identity": identity, "files": {path.name: sha(path)}})
            print(f"[encode] {window['id']} history={len(window['observations'])} seconds={time.monotonic()-start:.1f}", flush=True)
        result[window["id"]] = (window, saved["batch"], saved["targets"])
    return result


def merge_batches(batches):
    import torch
    if not batches: raise ValueError("Empty micro batch")
    result = {}
    length = max(x["history"].shape[1] for x in batches)
    for key in batches[0]:
        values = []
        for batch in batches:
            value = batch[key]
            if key in ("history", "frame_ids", "history_valid"):
                padded = value.new_zeros((1, length, *value.shape[2:]))
                padded[:, :value.shape[1]] = value
                value = padded
            values.append(value)
        result[key] = torch.cat(values)
    if ((result["frame_ids"] > result["t"][:, None]) & result["history_valid"]).any():
        raise ValueError("Future frame entered a padded micro batch")
    if not result["action_valid"].all(): raise ValueError("Diagnostic windows must have 32 genuine targets")
    return result


def gradients(model):
    import torch
    values = {name: float(p.grad.float().norm()) for name, p in model.memory.named_parameters() if p.grad is not None}
    if not values or not all(__import__('math').isfinite(v) for v in values.values()) or max(values.values()) == 0:
        raise FloatingPointError("Memory gradients are missing, zero or non-finite")
    if any(p.requires_grad or p.grad is not None for p in model.backbone.parameters()):
        raise ValueError("Frozen base gained a gradient")
    return values


def collector_record(collector, model, mode):
    import torch
    from .memory_probe_worker import tensor_statistics
    # Collector normally subtracts unscaled slots. Correct that diagnostic field
    # explicitly rather than mislabelling the repair's added slot component.
    scaled = model.memory.queries.detach() * (QUERY_SCALE if mode == MODES[1] else 1.)
    actual = torch.from_numpy(collector.arrays["query_input"]).to(scaled.device)
    collector.records["learned_queries_unscaled"] = collector.records["learned_queries"]
    collector.records["learned_queries"] = tensor_statistics(scaled)
    collector.records["shared_condition"] = tensor_statistics(actual - scaled[None])
    collector.records["query_scale"] = QUERY_SCALE if mode == MODES[1] else 1.
    return collector.records


def action_metrics(actions, native, targets, readout):
    from .memory_probe_worker import slot_statistics
    error = (native[:, :16]-targets[:, :16]).float()
    # Executor clips only grippers; evaluate both raw and executed convention.
    clipped = native[:, :16, [6, 13]].clamp(0, 1)
    return {"arm_rmse_first16_rad": float(error[..., list(ARMS)].square().mean().sqrt()),
            "wrist_mae_first16_rad": float(error[..., 12].abs().mean()),
            "gripper_mae_first16": float((clipped-targets[:, :16, [6,13]]).abs().mean()),
            "raw_gripper_mae_first16": float(error[..., [6,13]].abs().mean()),
            "joint_mae_first16": error.abs().mean((0,1)).cpu().tolist(),
            "readout": slot_statistics(readout), "wrist_target16": float(native[0,15,12]),
            "gripper_target16": float(clipped[0,15,1]), "normalized_actions_finite": bool(actions.isfinite().all())}


def zero(root, output, bound, model, encoders, weights):
    import numpy as np
    import torch
    from .common import ReleaseNormalizer
    from .diagnosis_gpu import load_weight
    from .memory_probe_worker import Collector, receipt, reuse, slot_statistics
    stage = output / "zero"; identity = signature(bound)
    windows = [w for w in read(output / "WINDOWS.json") if w["id"] in PROBE_CASES]
    prepared = encoded_windows(model, encoders, bound["config"], output, windows, stage)
    norm = ReleaseNormalizer(bound["config"]["paths"]["stats"])
    device = next(model.memory.parameters()).device
    rows, actions, durations = [], [], []
    completed = 0
    for label in ("step_000000", "step_002000"):
        load_weight(model, weights, label)
        versions = {n:p._version for n,p in model.memory.named_parameters()}
        for key in PROBE_CASES:
            window, host, _ = prepared[key]; batch = transfer(host, device)
            info = window["noise"]["production"]
            noise = torch.from_numpy(np.load(output / "inputs" / key / info["path"], allow_pickle=False)).to(device)
            for mode in MODES:
                boundary(output)
                case = stage / "mechanism" / f"{label}_{key}_{mode}"
                case_id = signature({"run":identity,"weight":label,"case":key,"mode":mode,"tau":.9})
                value = reuse(case, case_id, output)
                if value is None:
                    progress(stage,"FM_backward_no_update",completed,32,case=key,mode=mode,operation_started_unix=time.time())
                    started = time.monotonic(); model.zero_grad(set_to_none=True)
                    with query_scale(model.memory, mode), Collector(model.memory) as collector:
                        loss, detail = model(batch, noise, torch.tensor([.9], device=device))
                        if not bool(loss.isfinite()): raise FloatingPointError("Non-finite mechanism FM")
                        loss.backward()
                    grad = gradients(model)
                    value = {"weight":label,"case":key,"mode":mode,"loss":float(loss.detach()),
                             "readout":slot_statistics(torch.from_numpy(collector.arrays["reader_3"])),
                             "gradients":gradient_summary(grad),"parameter_gradients":grad,"optimizer_updates":0,
                             "seconds":time.monotonic()-started}
                    write(case / "trace.json", collector_record(collector, model, mode))
                    np.savez_compressed(case / "slots.npz", **{k:v for k,v in collector.arrays.items() if k.startswith("reader_") or k=="query_input"})
                    receipt(case,case_id,value)
                model.zero_grad(set_to_none=True); rows.append(value); completed+=1; durations.append(value["seconds"])
                progress(stage,"FM_backward_no_update",completed,32,case=key,mode=mode,
                         eta_seconds=statistics.mean(durations)*(32-completed),eta_scope="remaining diagnostic calls; initialization excluded")
                print(f"[zero] {completed}/32 {label} {key} {mode} loss={value['loss']:.6f} updates=0",flush=True)
        if versions != {n:p._version for n,p in model.memory.named_parameters()}:
            raise ValueError("Zero-update probes modified memory parameters")
    load_weight(model, weights, "step_002000")
    for key in PROBE_CASES:
        window, host, target_host = prepared[key]; batch=transfer(host,device); targets=target_host.to(device)
        for name in ("production","independent"):
            noise=torch.from_numpy(np.load(output/"inputs"/key/window["noise"][name]["path"],allow_pickle=False)).to(device)
            for mode in MODES:
                boundary(output); case=stage/"actions"/f"{key}_{name}_{mode}"
                case_id=signature({"run":identity,"case":key,"noise":name,"mode":mode})
                value=reuse(case,case_id,output)
                if value is None:
                    progress(stage,"action_sample",completed,32,case=key,mode=mode,operation_started_unix=time.time())
                    started=time.monotonic()
                    with torch.no_grad(), query_scale(model.memory,mode): prediction,readout=model.sample(batch,noise)
                    native=norm.denormalize(prediction); torch.cuda.synchronize(device)
                    if mode=="original" and name=="production":
                        with np.load(output/"references"/f"{key}.npz",allow_pickle=False) as ref:
                            if not np.array_equal(prediction.cpu().numpy(),ref["normalized_actions"]):
                                raise ValueError(f"Original output no longer exactly reproduces authenticated probe: {key}")
                    value={"case":key,"noise":name,"mode":mode,**action_metrics(prediction,native,targets,readout),
                           "seconds":time.monotonic()-started,"optimizer_updates":0}
                    np.savez_compressed(case/"actions.npz",normalized=prediction.cpu().numpy(),native=native.cpu().numpy(),target=targets.cpu().numpy())
                    receipt(case,case_id,value)
                actions.append(value);completed+=1;durations.append(value["seconds"])
                progress(stage,"action_sample",completed,32,case=key,mode=mode,
                         eta_seconds=statistics.mean(durations)*(32-completed),eta_scope="remaining diagnostic calls; no simulation")
                print(f"[zero] {completed}/32 {key} {name} {mode} arm_RMSE={value['arm_rmse_first16_rad']:.6f}rad",flush=True)
    gate=mechanism_gate(rows,bound["protocol"]["mechanism_thresholds"])
    complete(stage,identity,{"mechanisms":rows,"actions":actions,"gate":gate,"optimizer_updates":0,"simulation_episodes":0})
    print(f"[zero gate] {gate}; fit is {'eligible' if gate['passed'] else 'blocked'}",flush=True)


def repair_logs(directory, recovered):
    """Preserve incomplete lines/updates after the last published checkpoint."""
    for name in ("updates.jsonl","samples.jsonl"):
        path=directory/name
        if not path.exists(): continue
        good, tail=[],[]
        for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
            try:
                row=json.loads(line)
                if not line.endswith("\n") or row["update"]>recovered: tail.append(line)
                else: good.append(row)
            except (ValueError,KeyError): tail.append(line)
        keys=[(r["update"],r.get("global_slot",-1)) for r in good]
        if len(keys)!=len(set(keys)) or keys!=sorted(keys): raise ValueError(f"Duplicate/nonmonotonic committed log: {path}")
        expected=recovered*(16 if name=="samples.jsonl" else 1)
        if len(good)!=expected: raise ValueError(f"Missing committed log records: {path}; expected={expected}, actual={len(good)}")
        if tail:
            archive=directory/"interrupted"/f"{name}_{time.time_ns()}";archive.parent.mkdir(parents=True,exist_ok=True)
            archive.write_text(''.join(tail),encoding="utf-8")
            temporary=path.with_name(path.name+".partial")
            temporary.write_text(''.join(json.dumps(r,allow_nan=False)+"\n" for r in good),encoding="utf-8");temporary.replace(path)


def fit(root, output, bound, model, encoders, weights):
    import numpy as np
    import torch
    from .common import ReleaseNormalizer, atomic_torch, seed_for
    from .diagnosis_gpu import load_weight
    from .memory_probe_worker import receipt, reuse
    stage=output/"fit";identity=signature(bound);cfg=bound["config"];spec=bound["protocol"]
    require_completion(output,"zero",identity,passed=True)
    windows=read(output/"WINDOWS.json");prepared=encoded_windows(model,encoders,cfg,output,windows,stage)
    device=next(model.memory.parameters()).device;norm=ReleaseNormalizer(cfg["paths"]["stats"])
    trains={task:sorted(w["id"] for w in windows if w["group"]=="train" and w["item"]["task"]==task)
            for task in ("put_back_block","swap_blocks")}
    if any(len(x)!=2 for x in trains.values()): raise ValueError("Each task requires its two authentic training windows")
    def measure(mode,phase):
        result=[];model.eval()
        weight_sha=(bound["weights"]["step_002000"]["sha256"] if phase=="before"
                    else read(stage/mode/"checkpoints/LATEST.json")["sha256"])
        for window,host,target_host in prepared.values():
            batch=transfer(host,device);targets=target_host.to(device)
            for name in spec["evaluation_noises"]:
                boundary(output);case=stage/mode/"measurements"/f"{phase}_{window['id']}_{name}"
                case_id=signature({"run":identity,"mode":mode,"phase":phase,"window":window,"noise":name,"weight_sha256":weight_sha})
                value=reuse(case,case_id,output)
                if value is None:
                    progress(stage,"measure_"+phase,len(result),24,case=window["id"],mode=mode,operation_started_unix=time.time())
                    started=time.monotonic();noise=torch.from_numpy(np.load(output/"inputs"/window["id"]/window["noise"][name]["path"],allow_pickle=False)).to(device)
                    with torch.no_grad():prediction,readout=model.sample(batch,noise)
                    native=norm.denormalize(prediction);torch.cuda.synchronize(device)
                    value={"case":window["id"],"task":window["item"]["task"],"group":window["group"],"mode":mode,
                           "phase":phase,"noise":name,"noise_seed":window["noise"][name]["seed"],
                           **action_metrics(prediction,native,targets,readout),"seconds":time.monotonic()-started}
                    np.savez_compressed(case/"actions.npz",normalized=prediction.cpu().numpy(),native=native.cpu().numpy(),target=targets.cpu().numpy())
                    receipt(case,case_id,value)
                result.append(value)
                eta=statistics.mean(x["seconds"] for x in result)*(24-len(result))
                progress(stage,"measure_"+phase,len(result),24,case=window["id"],mode=mode,eta_seconds=eta,
                         eta_scope="remaining samples in this arm/measurement phase; training/other arm excluded")
                print(f"[fit {mode} {phase}] {len(result)}/24 {window['id']} noise={name} arm={value['arm_rmse_first16_rad']:.6f}rad ETA~{eta:.0f}s",flush=True)
        return result
    measurements=[];stream_records={}
    for mode in MODES:
        boundary(output);directory=stage/mode;directory.mkdir(parents=True,exist_ok=True)
        load_weight(model,weights,"step_002000")
        optimizer=torch.optim.AdamW(model.memory.parameter_groups(),lr=cfg["learning_rate"],betas=(.9,.95),eps=1e-8)
        completed=0
        with query_scale(model.memory,mode):
            # Before measurements always refer to the shared original checkpoint.
            measurements.extend(measure(mode,"before"))
            latest=directory/"checkpoints/LATEST.json"
            if latest.exists():
                saved=read(latest);verify(latest.parent,{saved["file"]:saved["sha256"]})
                state=torch.load(latest.parent/saved["file"],map_location="cpu",weights_only=True)
                if state["identity"]!=identity or state["mode"]!=mode or state["source_weight"]!=bound["weights"]["step_002000"]:
                    raise ValueError("Diagnostic optimizer recovery identity mismatch")
                completed=int(state["diagnostic_updates"])
                if not 0<=completed<=64:raise ValueError("Invalid recovered diagnostic update")
                model.memory.load_state_dict(state["memory"],strict=True);optimizer.load_state_dict(state["optimizer"])
                del state
            repair_logs(directory,completed)
            def save_point():
                folder=directory/"checkpoints";folder.mkdir(parents=True,exist_ok=True)
                name=f"update_{completed:03d}.pt";path=folder/name;record=folder/f"update_{completed:03d}.json"
                if record.exists():
                    saved=read(record);verify(folder,{name:saved["sha256"]})
                else:
                    if path.exists():
                        displaced=directory/"interrupted"/f"unpublished_{name}_{time.time_ns()}";displaced.parent.mkdir(parents=True,exist_ok=True);path.rename(displaced)
                    memory={n:p.detach().cpu().clone() for n,p in model.memory.state_dict().items()}
                    atomic_torch(path,{"identity":identity,"mode":mode,"query_scale":QUERY_SCALE if mode==MODES[1] else 1.,
                         "source_weight":bound["weights"]["step_002000"],"diagnostic_updates":completed,
                         "memory":memory,"optimizer":optimizer.state_dict(),"scope":"fresh-optimizer isolated fit, not formal S1 continuation"})
                    saved={"file":name,"sha256":sha(path),"diagnostic_updates":completed,"identity":identity,"mode":mode};write(record,saved)
                write(latest,saved)
                print(f"[checkpoint] {mode} diagnostic_update={completed}/64 immutable+verified",flush=True)
            times=[]
            try:
                for update in range(completed+1,65):
                    boundary(output);start=time.monotonic();model.train();optimizer.zero_grad(set_to_none=True)
                    progress(stage,"optimizer_update",update-1,64,mode=mode,operation_started_unix=time.time(),
                             eta_seconds=statistics.mean(times[-10:])*(65-update) if times else None,
                             eta_scope="current arm updates; checkpoint and action measurement excluded")
                    slots=[]
                    for slot in range(16):
                        task=("put_back_block","swap_blocks")[(update+slot)%2]
                        choice=seed_for(cfg["seed"],update,slot,"query-repair-window-v1")%2
                        key=trains[task][choice];window=prepared[key][0]
                        ns=seed_for(cfg["seed"],update,slot,"query-repair-training-noise-v1")
                        ts=seed_for(cfg["seed"],update,slot,"query-repair-training-tau-v1")
                        # Independent purposes and branch-free derivation ensure matched arms.
                        noise=torch.randn(1,32,14,generator=torch.Generator(device="cpu").manual_seed(ns))
                        tau=torch.rand(1,generator=torch.Generator(device="cpu").manual_seed(ts))
                        slots.append((key,noise,tau,{"update":update,"global_slot":slot,"case":key,"task":task,
                             "noise_seed":ns,"tau_seed":ts,"tau":float(tau),"T":8,"phase":window["sampling"]["phase"],
                             "frame_ids":[r["frame_id"] for r in window["observations"]]}))
                    losses=[]
                    for index in range(0,16,spec["micro_batch"]):
                        boundary(output);items=slots[index:index+spec["micro_batch"]]
                        batch=merge_batches([transfer(prepared[k][1],device) for k,_,_,_ in items])
                        noise=torch.cat([n for _,n,_,_ in items]).to(device);tau=torch.cat([t for _,_,t,_ in items]).to(device)
                        loss,_=model(batch,noise,tau)
                        if not bool(loss.isfinite()):raise FloatingPointError("Non-finite bounded training loss")
                        (loss/spec["accumulation"]).backward();losses.append(float(loss.detach()))
                    values=gradients(model);grad=torch.nn.utils.clip_grad_norm_(model.memory.parameters(),1.,error_if_nonfinite=True)
                    # Signals only set a flag; an optimizer step cannot be interrupted by Python's stop handler.
                    optimizer.step()
                    if any(not bool(p.isfinite().all()) for p in model.memory.parameters()):raise FloatingPointError("Optimizer created non-finite memory weights")
                    completed=update;torch.cuda.synchronize(device);seconds=time.monotonic()-start;times.append(seconds)
                    append(directory/"updates.jsonl",{"update":update,"loss":statistics.mean(losses),"grad_norm":float(grad),
                           "gradient_summary":gradient_summary(values),"seconds":seconds,"global_slots":16,"optimizer_steps":1})
                    for _,_,_,row in slots:append(directory/"samples.jsonl",row)
                    eta=statistics.mean(times[-10:])*(64-update)
                    progress(stage,"optimizer_updates",update,64,mode=mode,eta_seconds=eta,
                             eta_scope="remaining updates in current arm; checkpoints/measurements/other arm excluded")
                    print(f"[fit] {mode} update={update}/64 loss={statistics.mean(losses):.6f} grad={float(grad):.6f} seconds={seconds:.2f} ETA~{eta:.0f}s",flush=True)
                    if update%spec["checkpoint_every"]==0:save_point()
            except InterruptedError:
                optimizer.zero_grad(set_to_none=True);save_point();raise
            boundary(output);repair_logs(directory,64)
            measurements.extend(measure(mode,"after"))
            final=directory/"candidate.pt"
            candidate_record=directory/"CANDIDATE.json"
            if candidate_record.exists():
                saved=read(candidate_record);verify(directory,{saved["file"]:saved["sha256"]})
                payload=torch.load(final,map_location="cpu",weights_only=True)
                if (payload["identity"]!=identity or payload["mode"]!=mode or payload["diagnostic_updates"]!=64
                        or any(not torch.equal(value.detach().cpu(),payload["memory"][name]) for name,value in model.memory.state_dict().items())):
                    raise ValueError("Existing diagnostic candidate differs from the recovered complete update")
                del payload
            else:
                if final.exists():
                    archive=directory/"interrupted"/f"unpublished_candidate_{time.time_ns()}.pt"
                    archive.parent.mkdir(parents=True,exist_ok=True);final.rename(archive)
                atomic_torch(final,{"identity":identity,"mode":mode,"query_scale":QUERY_SCALE if mode==MODES[1] else 1.,
                     "diagnostic_updates":64,"source_weight":bound["weights"]["step_002000"],
                     "memory":{n:p.detach().cpu().clone() for n,p in model.memory.state_dict().items()},"scope":"diagnostic candidate; not a benchmark-selected model"})
                write(candidate_record,{"file":final.name,"sha256":sha(final),"identity":identity,"mode":mode,"diagnostic_updates":64})
        stream_records[mode]=[json.loads(line) for line in (directory/"samples.jsonl").read_text().splitlines()]
        del optimizer
    if stream_records[MODES[0]]!=stream_records[MODES[1]]:raise ValueError("The two arms did not use identical 16-slot streams")
    if len(measurements)!=96:raise ValueError("Paired before/after action sample budget incomplete")
    gate=fit_gate(measurements,spec["fit_thresholds"])
    complete(stage,identity,{"measurements":measurements,"gate":gate,"updates_per_arm":64,"global_slots_per_update":16,
            "matched_stream_sha256":signature(stream_records[MODES[0]]),"fresh_optimizer":True,"constant_learning_rate":cfg["learning_rate"],
            "scheduler":"none in this isolated 64-update experiment","fixed_training_history":"T=8, frozen per-window phase; formal S1 sampler unchanged"})
    print(f"[fit gate] eligible_for_physical={gate['eligible_for_physical']}; both original checkpoint files unchanged",flush=True)


def physical(root,output,bound,model,encoders):
    import numpy as np
    import torch
    from . import selection_runtime
    from .grasp_diagnosis import direct, request_for
    from .initial_intervention_worker import run_case
    stage=output/"physical";identity=signature(bound)
    require_completion(output,"fit",identity,passed=True)
    folder=output/"fit"/MODES[1];receipt=read(folder/"CANDIDATE.json");verify(folder,{receipt["file"]:receipt["sha256"]})
    saved=torch.load(folder/receipt["file"],map_location="cpu",weights_only=True)
    if saved["identity"]!=identity or saved["mode"]!=MODES[1] or saved["diagnostic_updates"]!=64 or saved["query_scale"]!=QUERY_SCALE:
        raise ValueError("Physical candidate identity/scale mismatch")
    model.memory.load_state_dict(saved["memory"],strict=True);model.eval();del saved
    current=dict(bound,diagnostic_candidate=receipt)
    bundle=read(output/"frozen/FROZEN.json")
    with query_scale(model.memory,MODES[1]):
        # Derive a candidate-specific baseline; the RPC must reproduce it before
        # executing the altered first block. This never edits the old baseline.
        item=bundle["inputs"]["put_back_block_online_initial"]
        info=bundle["noise"]["put_back_block"]["offline"]
        noise=torch.from_numpy(np.load(output/"frozen"/info["path"],allow_pickle=False))
        trace=direct(model,encoders,bound["config"],request_for(output/"frozen",item),noise)
        (output/"baselines").mkdir(exist_ok=True)
        np.savez_compressed(output/"baselines/put_back_block_offline.npz",normalized=trace["normalized_actions"][None].numpy())
        del trace
        results=[]
        for variant,task in (("first-noise","put_back_block"),("expert-prefix","swap_blocks")):
            boundary(output)
            progress(stage,"simulator_initialization",0,128,case=task,mode=MODES[1],
                     eta_scope="current prefix; simulator initialization unmeasured")
            original_details=selection_runtime.live_details
            def details_with_progress(progress_root):
                details=original_details(progress_root)
                live=[row for row in details if row.get("phase")=="rollout" and row.get("targets",0)>0]
                row=live[-1] if live else (details[-1] if details else {})
                targets=row.get("targets",0);seconds=row.get("rollout_seconds")
                eta=None
                if targets and seconds is not None:
                    rate=max((seconds+row.get("heartbeat_age_seconds",0))/targets,row.get("seconds_per_target") or 0)
                    eta=max(0,128-targets)*rate
                progress(stage,row.get("phase","simulator_initialization"),targets,128,case=task,mode=MODES[1],
                         eta_seconds=eta,eta_scope="measured time to current prefix target cap; success may end earlier; cleanup excluded")
                return details
            # Existing expert-prefix and noise protocol are intentional: each
            # pairs with the signed historical intervention, not a full benchmark.
            selection_runtime.live_details=details_with_progress
            try:
                run_case(root,output,current,variant,task,model,encoders,bound["runtime"]["gpu"].split(",")[0].strip())
            finally:
                selection_runtime.live_details=original_details
            results.append(read(output/variant/task/"result.json"))
    external={}
    for variant,task in (("first-noise","put_back_block"),("expert-prefix","swap_blocks")):
        directory=output/variant/task;case_receipt=read(directory/"COMPLETE.json")
        verify(directory,case_receipt["files"])
        external.update({f"{variant}/{task}/{name}":value for name,value in case_receipt["files"].items()})
        external[f"{variant}/{task}/COMPLETE.json"]=sha(directory/"COMPLETE.json")
    complete(stage,identity,{"cases":results,"target_cap":128,"simulation_episodes":2,"benchmark_accuracy":None,
            "historical_comparison":"put:first-noise; swap:expert-prefix48; frozen scenes/noise/protocol unchanged",
            "candidate":receipt,"scope":"grasp mechanism diagnostic; expert-assisted results are not policy success rates"},external)


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument("stage",choices=("zero","fit","physical"));parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True);parser.add_argument("--gpu-uuid",required=True)
    args=parser.parse_args();root=args.root.resolve();output=args.output.resolve();directory=output/args.stage
    def request_stop(*_):
        global _STOP
        _STOP=True
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,request_stop)
    try:
        import torch
        from .diagnosis_gpu import load_weight
        from .eval_state import cuda_gpu_uuid
        from .integration_contract import configure_numerics
        from .model import S1Model,load_observation_encoders
        bound=read(output/"IDENTITY.json");cfg=bound["config"]
        if torch.cuda.device_count()!=1 or cuda_gpu_uuid(0)!=args.gpu_uuid or torch.cuda.get_device_capability(0)!=(9,0):
            raise ValueError("Expose exactly the bound H100")
        verify(output,read(output/"PREPARED.json")["files"]);configure_numerics(cfg)
        progress(directory,"model_load",0,1,eta_scope="unmeasured model initialization")
        print(f"[model_load] {args.stage}; frozen base; independent repair outputs; initialization has no measured ETA",flush=True)
        model=S1Model(cfg,torch.device("cuda:0")).eval();encoders=load_observation_encoders(cfg,torch.device("cuda:0"))
        weights={"weights":{name:{"path":str(root/record["relative"]),"sha256":record["sha256"]} for name,record in bound["weights"].items()},"resources":bound["resources"]}
        load_weight(model,weights,"step_002000")
        globals()[args.stage](root,output,bound,model,encoders,weights) if args.stage in ("zero","fit") else physical(root,output,bound,model,encoders)
        for record in bound["weights"].values():verify(root,{record["relative"]:record["sha256"]})
        print(f"[complete] {args.stage}; checkpoints verified unchanged; unique root cause requires review",flush=True)
    except BaseException as error:
        write(directory/"ERROR.json",{"error":repr(error),"state":"interrupted" if isinstance(error,InterruptedError) else "error","traceback":traceback.format_exc()});raise


if __name__=="__main__":main()
