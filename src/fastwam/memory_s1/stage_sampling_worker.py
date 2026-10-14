"""Single-GPU paired sampling pilot; private weights and bounded physical checks."""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import json
from multiprocessing.connection import Listener
import os
from pathlib import Path
import signal
import statistics
import subprocess
import tempfile
import time

import numpy as np

from .grasp_bridge import checked_path, files, owned_popen, read, sha, signature, stop_children, verify, write
from .stage_sampling_math import BRANCHES, TASKS, action_errors
from .stage_sampling_pilot import boundary, require_prepared, stage_result


def progress(output, model, phase, completed, total, **extra):
    write(output/"PROGRESS.json", {"model":model,"phase":phase,"completed":completed,"total":total,
                                  "updated_unix":time.time(),**extra})


def complete(directory, bound, result):
    write(directory/"result.json",result)
    mapping={name:value for name,value in files(directory).items() if name != "COMPLETE.json"
             and not set(Path(name).parts)&{"checkpoints","interrupted"} and not name.endswith((".log",".partial",".tmp"))}
    write(directory/"COMPLETE.json", {"identity":signature(bound),"files":mapping})


def cache_stamp_bootstrap(output, cfg):
    """Reuse prior full checksums only while size/time/inode stamps are unchanged."""
    from .data import _file_stamp, _VERIFIED_FILES
    root=Path(cfg["paths"]["cache"])
    for name,record in read(output/"CACHE_VERIFIED.json").items():
        path=checked_path(root,name); stamp=_file_stamp(path)
        if list(stamp) != record["stamp"]: raise ValueError(f"Cache changed after preparation: {path}; no stale checksum reuse")
        _VERIFIED_FILES[str(path)]=(stamp,record["sha256"])


def load_original(model, root, bound):
    from .diagnosis_gpu import load_weight
    record=bound["weights"]["step_002000"]; path=checked_path(root,record["relative"])
    verify(root,{record["relative"]:record["sha256"]})
    load_weight(model,{"weights":{"step_002000":{"path":str(path),"sha256":record["sha256"]}},
                      "resources":bound["resources"]},"step_002000")


def candidate(model, output, bound, branch):
    import torch
    stage_result(output,"fit",bound,required=True)
    folder=output/"fit"/branch; record=read(folder/"CANDIDATE.json")
    verify(folder,{record["file"]:record["sha256"]})
    value=torch.load(folder/record["file"],map_location="cpu",weights_only=True)
    if (value["identity"] != signature(bound) or value["branch"] != branch or value["pilot_updates"] != 128
            or value["source_update"] != 2000 or value["source_checkpoint"] != bound["source_checkpoint"]):
        raise ValueError("Diagnostic candidate source/update/branch differs")
    model.memory.load_state_dict(value["memory"],strict=True); model.eval()
    return {"kind":"diagnostic_candidate","branch":branch,"source_update":2000,"pilot_updates":128,
            "sha256":record["sha256"],"file":str(folder/record["file"])}


def measure(root, output, bound, model, label, dataset, directory):
    import torch
    from .common import ReleaseNormalizer, seed_for
    from .data import collate
    from .memory_probe_worker import receipt, reuse, slot_statistics
    cfg=bound["config"]; norm=ReleaseNormalizer(cfg["paths"]["stats"]); device=next(model.memory.parameters()).device
    windows=read(output/"VALIDATION.json"); results=[]; model.eval(); durations=[]
    records={r["episode_id"]:r for values in dataset.by_task.values() for r in values}
    weight=(load_original(model,root,bound) or {"kind":"original","source_update":2000,"pilot_updates":0,
            "sha256":bound["weights"]["step_002000"]["sha256"]}) if label == "original" else candidate(model,output,bound,label)
    total=len(windows)*bound["protocol"]["validation_noises"]
    for window in windows:
        record=records[window["episode_id"]]
        if record["split"] != "val": raise ValueError("Training episode entered held-out evaluation")
        sample=dataset.at(record,window["anchor"],window["T"],window["phase"])
        batch=collate([sample],device)
        value=dataset.load(record)
        target=torch.zeros(32,14); count=int(sample["action_valid"].sum())
        target[:count]=value["targets"][window["anchor"]:window["anchor"]+count]
        if count < 32: target[count:]=target[count-1]
        # Native state is recovered with STATE stats, not action denormalization.
        # Read approved native states; normalized/clamped cache state is not invertible.
        prepared=torch.load(Path(cfg["paths"]["prepared"])/record["file"],map_location="cpu",weights_only=True)
        current=prepared["states"][window["anchor"]].numpy(); del prepared
        for noise_index in range(3):
            boundary(output); case=directory/f"{window['id']}_noise{noise_index}"
            ns=seed_for(cfg["seed"],window["id"],noise_index,"stage-pilot-heldout-noise-v1")
            tau=(.1,.5,.9)[noise_index]
            case_id=signature({"identity":signature(bound),"window":window,"weight":weight,"noise_seed":ns,"tau":tau})
            result=reuse(case,case_id,output)
            if result is None:
                progress(output,label,"heldout_action_sampling",len(results),total,window=window["id"],noise_index=noise_index)
                started=time.monotonic(); noise=torch.randn(1,32,14,generator=torch.Generator(device="cpu").manual_seed(ns)).to(device)
                with torch.no_grad():
                    loss,diag=model(batch,noise,torch.tensor([tau],device=device)); prediction,readout=model.sample(batch,noise)
                native=norm.denormalize(prediction); torch.cuda.synchronize(device)
                result={**window,"model":label,"noise_index":noise_index,"noise_seed":ns,"tau":tau,
                    "fm":float(loss),"unweighted_fm":float(diag["unweighted_fm"].mean()),
                    "metrics":action_errors(native[0].cpu().numpy(),target.numpy(),sample["action_valid"].numpy(),current),
                    "readout":slot_statistics(readout),"read_frame_ids":sample["frame_ids"].tolist(),
                    "weight":weight,"seconds":time.monotonic()-started}
                if not np.isfinite([result["fm"],result["unweighted_fm"]]).all(): raise FloatingPointError("Held-out FM is non-finite")
                np.savez_compressed(case/"actions.npz",native=native[0].cpu().numpy(),target=target.numpy(),current=current,
                                    valid=sample["action_valid"].numpy(),normalized=prediction[0].cpu().numpy())
                receipt(case,case_id,result)
            results.append(result); durations.append(result["seconds"])
            eta=statistics.mean(durations[-12:])*(total-len(results))
            progress(output,label,"heldout",len(results),total,eta_seconds=eta,eta_scope="this model's remaining held-out samples; load/training/physics excluded")
            print(f"[heldout {label}] {len(results)}/{total} {window['task']} {window['stage']} "
                  f"anchor={window['anchor']} noise={noise_index} arm={result['metrics']['executed16']['arm_rmse_rad']:.6f}rad "
                  f"grip={result['metrics']['executed16']['gripper_mae']:.6f} ETA~{eta:.0f}s",flush=True)
    return results


def save_point(directory, bound, model, optimizer, completed, branch):
    from .checkpoint import random_state, to_cpu
    from .common import atomic_torch
    folder=directory/"checkpoints"; folder.mkdir(exist_ok=True)
    name=f"update_{completed:03d}_{time.time_ns()}.pt"; path=folder/name
    atomic_torch(path,{"identity":signature(bound),"branch":branch,"pilot_updates":completed,
        "source_checkpoint":bound["source_checkpoint"],"memory":to_cpu(model.memory.state_dict()),
        "optimizer":to_cpu(optimizer.state_dict()),"rng":random_state(),"scope":"private bounded sampling pilot"})
    record={"file":name,"sha256":sha(path),"identity":signature(bound),"branch":branch,"pilot_updates":completed}
    write(folder/(name+".complete.json"),record); write(folder/"LATEST.json",record)
    print(f"[checkpoint] {branch} private_update={completed}/128 full local point verified; original run unchanged",flush=True)


def fit(root, output, bound, model):
    import torch
    from .checkpoint import verified_load, restore_random_state
    from .common import atomic_torch
    from .data import CachedEpisodes, collate
    from .evaluate import deterministic_noise
    from .initial_intervention_worker import append
    from .memory_repair_worker import repair_logs, gradients
    from .train import learning_rate_factor
    stage_result(output,"baseline",bound,required=True)
    stage=output/"fit"; cfg=bound["config"]; dataset=CachedEpisodes(cfg,"train"); plan=read(output/"SAMPLE_PLAN.json")
    identity=signature(bound); device=next(model.memory.parameters()).device; streams={}; summaries={}
    records={r["episode_id"]:r for values in dataset.by_task.values() for r in values}
    for branch in BRANCHES:
        boundary(output); directory=stage/branch; directory.mkdir(exist_ok=True)
        source=verified_load(checked_path(root,bound["source_checkpoint"]["relative"]))
        model.memory.load_state_dict(source["memory"],strict=True)
        optimizer=torch.optim.AdamW(model.memory.parameter_groups(),lr=cfg["learning_rate"],betas=(.9,.95))
        optimizer.load_state_dict(source["optimizer"]); restore_random_state(source["rng_states"][0]); del source
        allowed={id(p) for p in model.memory.parameters()}
        if {id(p) for g in optimizer.param_groups for p in g["params"]} != allowed or {id(p) for p in model.parameters() if p.requires_grad} != allowed:
            raise ValueError("Only the original memory parameters may be optimized")
        completed=0; latest=directory/"checkpoints/LATEST.json"
        if latest.exists():
            saved=read(latest); verify(latest.parent,{saved["file"]:saved["sha256"]})
            marker=read(latest.parent/(saved["file"]+".complete.json"))
            if marker != saved: raise ValueError("Private checkpoint pointer and immutable receipt differ")
            state=torch.load(latest.parent/saved["file"],map_location="cpu",weights_only=False)
            if state["identity"] != identity or state["branch"] != branch or state["source_checkpoint"] != bound["source_checkpoint"]:
                raise ValueError("Private optimizer recovery identity mismatch")
            completed=int(state["pilot_updates"])
            if not 0 <= completed <= 128: raise ValueError("Bad private recovery cursor")
            model.memory.load_state_dict(state["memory"],strict=True); optimizer.load_state_dict(state["optimizer"])
            restore_random_state(state["rng"]); del state
        repair_logs(directory,completed)
        if not latest.exists(): save_point(directory,bound,model,optimizer,completed,branch)
        times=[]; last_print=time.monotonic()
        for update in range(completed+1,129):
            boundary(output); started=time.monotonic(); model.train(); optimizer.zero_grad(set_to_none=True)
            torch.cuda.reset_peak_memory_stats(device)
            rows=plan[branch][(update-1)*16:update*16]; log_rows=[]; losses=[]
            progress(output,branch,"optimizer_update",update-1,128,eta_seconds=statistics.mean(times[-10:])*(129-update) if times else None,
                     eta_scope="this branch's updates; cache-load/checkpoint/other branch/evaluation separately timed")
            for start in range(0,16,2):
                current=rows[start:start+2]; samples=[]
                for row in current:
                    if records[row["episode_id"]]["split"] != "train" or row["split"] != "train": raise ValueError("Held-out/online data entered training")
                    sample=(dataset.sample(row["sampling_update"],row["global_slot"]) if branch == "uniform"
                            else dataset.at(records[row["episode_id"]],row["anchor"],row["T"],row["phase"]))
                    if (sample["episode_id"] != row["episode_id"] or int(sample["t"]) != row["anchor"]
                            or sample["history_period"] != row["T"] or sample["history_phase"] != row["phase"]):
                        raise ValueError("Planned sampling and actual model input differ")
                    samples.append(sample); log_rows.append({**row,"frame_ids":sample["frame_ids"].tolist(),
                        "valid_targets":int(sample["action_valid"].sum()),"evidence_coverage":"unknown"})
                batch=collate(samples,device)
                noise,tau=deterministic_noise(cfg["seed"],rows[0]["sampling_update"],[r["global_slot"] for r in current],device)
                for entry,t in zip(log_rows[-2:],tau): entry["tau"]=float(t)
                loss,_=model(batch,noise,tau)
                if not bool(loss.isfinite()): raise FloatingPointError("Non-finite pilot loss")
                (loss/8).backward(); losses.append(float(loss.detach()))
                if time.monotonic()-last_print >= 15:
                    print(f"[fit {branch}] update={update}/128 accumulation={start//2+1}/8 "
                          f"current_update_elapsed={time.monotonic()-started:.1f}s",flush=True); last_print=time.monotonic()
            values=gradients(model)
            if any(p.grad is None for p in model.memory.parameters()): raise ValueError("A memory parameter lacks a gradient")
            norm=torch.nn.utils.clip_grad_norm_(model.memory.parameters(),1.,error_if_nonfinite=True)
            # The original cosine is already at its floor; do not restart warmup.
            expected=cfg["learning_rate"]*learning_rate_factor(rows[0]["sampling_update"],cfg)
            if any(abs(g["lr"]-expected)>1e-12 for g in optimizer.param_groups): raise ValueError("Terminal learning-rate drift")
            optimizer.step()
            if any(not bool(p.isfinite().all()) for p in model.memory.parameters()): raise FloatingPointError("Non-finite updated memory weights")
            completed=update; torch.cuda.synchronize(device); seconds=time.monotonic()-started; times.append(seconds)
            append(directory/"updates.jsonl",{"update":update,"loss":statistics.mean(losses),"grad_norm":float(norm),"lr":expected,
                "seconds":seconds,"global_slots":16,"optimizer_steps":1,"max_memory_gradient_norm":max(values.values()),
                "query_gradient_norm":values.get("queries"),
                "peak_gpu_gib":torch.cuda.max_memory_allocated(device)/2**30})
            for row in log_rows: append(directory/"samples.jsonl",row)
            eta=statistics.mean(times[-10:])*(128-update)
            print(f"[fit {branch}] {update}/128 loss={statistics.mean(losses):.6f} lr={expected:.2e} "
                  f"grad={float(norm):.5f} update_seconds={seconds:.2f} ETA~{eta:.0f}s (this branch, excluding checkpoints)",flush=True)
            progress(output,branch,"optimizer_updates",update,128,eta_seconds=eta,eta_scope="remaining updates in this branch; checkpoint/other branch/evaluation excluded")
            if update % 32 == 0 or (output/"STOP.json").exists(): save_point(directory,bound,model,optimizer,completed,branch)
            boundary(output)
        repair_logs(directory,128); model.eval()
        path=directory/"candidate.pt"
        if (directory/"CANDIDATE.json").exists():
            previous=read(directory/"CANDIDATE.json"); verify(directory,{previous["file"]:previous["sha256"]})
            value=torch.load(path,map_location="cpu",weights_only=True)
            if value["identity"] != identity or any(not torch.equal(v.detach().cpu(),value["memory"][k]) for k,v in model.memory.state_dict().items()):
                raise ValueError("Existing candidate differs from the full private recovery point")
            del value
        else:
            if path.exists():
                displaced=directory/"interrupted"/f"unpublished_candidate_{time.time_ns()}.pt"; displaced.parent.mkdir(exist_ok=True); path.rename(displaced)
            atomic_torch(path,{"identity":identity,"branch":branch,"source_update":2000,"pilot_updates":128,
                "source_checkpoint":bound["source_checkpoint"],"memory":{k:v.detach().cpu() for k,v in model.memory.state_dict().items()},
                "scope":"private sampling candidate; not a benchmark-selected checkpoint"})
            write(directory/"CANDIDATE.json",{"file":path.name,"sha256":sha(path),"identity":identity,"branch":branch,"pilot_updates":128})
        streams[branch]=[json.loads(line) for line in (directory/"samples.jsonl").read_text().splitlines()]
        counts=Counter((r["task"],r["event_bin"]) for r in streams[branch])
        summaries[branch]={"updates":128,"sample_count":len(streams[branch]),"event_bin_counts":{f"{t}/{b}":n for (t,b),n in counts.items()}}
        del optimizer; gc.collect(); torch.cuda.empty_cache()
    for a,b in zip(streams[BRANCHES[0]],streams[BRANCHES[1]]):
        for key in ("update","sampling_update","global_slot","episode_id","task","T","phase","noise_seed","tau","original_anchor","split"):
            if a[key] != b[key]: raise ValueError(f"Non-anchor treatment changed paired input stream: {key}")
    if any(len(rows) != 2048 for rows in streams.values()): raise ValueError("Expected exactly 2048 global slots per branch")
    complete(stage,bound,{"branches":summaries,"source_update":2000,"optimizer_moments_inherited":True,
        "learning_rate":bound["terminal_lr"],"random_T_phase_preserved":True,"training_online_expert_samples":0,
        "pairing":"same task/episode/noise/tau/T/phase; only anchor probabilities differ", "benchmark_accuracy":None})


def physical_case(root, output, bound, model, encoders, gpu, task, label, item, expert, folder, done):
    import torch
    from .eval_parallel import simulator_environment
    from .grasp_causal_worker import ComponentRouter
    from .grasp_causal_metrics import physical_metrics
    from .initial_intervention_worker import rows, reuse_or_archive
    from .selection_runtime import live_details, format_active, duration
    from .sim_bridge import InferenceSession
    from .simulator_backend import configured_backend
    task_root=output/"physical"/task; task_root.mkdir(exist_ok=True); (task_root/"tmp").mkdir(exist_ok=True)
    task_bound={**bound,"protocol":{**bound["protocol"],"task":task,"object":bound["protocol"]["objects"][task]}}
    ident=signature({"identity":signature(task_bound),"label":label,
        "candidate_sha":None if label in ("expert","original") else read(output/"fit"/label/"CANDIDATE.json")["sha256"]})
    directory=task_root/"cases"/label
    if reuse_or_archive(directory,ident): return read(directory/"result.json")
    if label == "expert":
        mode,session,weight="expert",None,{"kind":"same_scene_expert","pilot_updates":0}
    else:
        mode="policy"
        weight=(load_original(model,root,bound) or {"kind":"original","sha256":bound["weights"]["step_002000"]["sha256"],"pilot_updates":0}) if label == "original" else candidate(model,output,bound,label)
        session=InferenceSession(model,bound["config"],encoders,"full",directory,None,bound["config"]["seed"])
    write(directory/"MODEL.json",weight)
    router=ComponentRouter(session,mode,task_root,directory,task_bound,expert,item,folder)
    cfg=bound["config"]; spec=bound["protocol"]; key=os.urandom(24); events=directory/"simulator_progress"
    write(directory/"job.json",{"id":f"sampling-pilot:{task}:{label}","attempt":1,"scene":expert["scene"],"condition":"full"})
    env=simulator_environment(cfg,gpu); env.update(MEMORY_S1_RPC_KEY=key.hex(),MEMORY_S1_PROGRESS_ROOT=str(events),MEMORY_S1_RECORD_FRAME_STRIDE="1")
    child=None; started=time.monotonic(); last=0.
    try:
        with tempfile.TemporaryDirectory(prefix="pilot-",dir=task_root/"tmp") as sockets:
            socket=Path(sockets)/"rpc.sock"
            command=[cfg["closed_loop"]["simulator_python"],"-u",str(root/"scripts/memory_s1/sim_eval.py"),"--operation","episode",
                "--job",str(directory/"job.json"),"--output",str(directory),"--socket",str(socket),"--seed",str(cfg["seed"]),
                "--gpu-uuid",gpu,"--stop-root",str(output),"--record-frames","--record-feedback","--qualification-trace",
                "--max-targets",str(spec["target_cap"]),"--scene-count","1"]
            write(directory/"command.json",command)
            with Listener(str(socket),family="AF_UNIX",authkey=key) as listener, (directory/"simulator.log").open("w",encoding="utf-8") as log:
                listener._listener._socket.settimeout(1)
                child=owned_popen(command,cwd=root/cfg["closed_loop"]["simulator_root"],env=env,stdout=log,stderr=subprocess.STDOUT)
                while child.poll() is None:
                    boundary(output); elapsed=time.monotonic()-started
                    if elapsed > spec["case_timeout_seconds"]: raise TimeoutError("Bounded physical case wall-time exceeded; not a model failure")
                    if elapsed-last >= 15:
                        active=live_details(events); measured=[r for r in active if r.get("targets",0) and r.get("rollout_seconds") is not None]
                        target=max((r.get("targets") or 0 for r in active),default=max(0,router.next_frame-16)); eta=None
                        if measured:
                            rate=max((r["rollout_seconds"]+r.get("heartbeat_age_seconds",0))/r["targets"] for r in measured)
                            eta=max(0,128-target)*rate
                        progress(output,label,"physical_rollout",done,8,task=task,targets=target,eta_seconds=eta,
                                 eta_scope="current case to128 cap; initialization/other cases excluded")
                        print(f"[physical {label}/{task}] cases={done}/8 targets={target}/128 elapsed={duration(elapsed)} "
                              f"current_rollout_ETA~{duration(eta)}",flush=True)
                        for r in active: print("  "+format_active(r),flush=True)
                        last=elapsed
                    try: connection=listener.accept()
                    except TimeoutError: continue
                    with connection:
                        if not connection.poll(15): raise TimeoutError("RPC connection without request")
                        try: reply=router.handle(connection.recv())
                        except BaseException:
                            connection.send({"ok":False,"error":__import__("traceback").format_exc()}); raise
                        connection.send(reply)
                if child.returncode: raise RuntimeError(f"Simulator exited {child.returncode}:\n{(directory/'simulator.log').read_text(errors='replace')[-10000:]}")
        value=read(directory/"simulator_result.json"); backend_files=list(events.glob("fused_backend_*.json"))
        if (value["status"] != "complete" or value["task"] != task or value["seed"] != item["seed"]
                or value["target_limit"] != 128 or value["executed_targets"] <= 48
                or (value["executed_targets"] < 128 and not value["success"])
                or value["simulator_backend"] != configured_backend(cfg) or len(backend_files)<2
                or any(not read(p)["passed"] or read(p)["extensions"] != bound["simulator_extensions"] for p in backend_files)):
            raise ValueError("Incomplete/wrong physical or fused-backend evidence; do not count as model failure")
        metrics,trajectory=physical_metrics(rows(directory/"executed_actions.jsonl"),rows(directory/"observations.jsonl"),
                                           rows(directory/"interventions.jsonl"),expert,task_bound["protocol"])
        # Separate movement before closure from legitimate later object transport.
        # Displacement alone is not labelled as pushing or a successful grasp.
        first=rows(directory/"executed_actions.jsonl")[0]["objects_before"][task_bound["protocol"]["object"]]["p"]
        metrics["max_object_xy_displacement_m"]=max(float(np.linalg.norm(np.asarray(r["object_position"])[:2]-np.asarray(first)[:2])) for r in trajectory[48:])
        metrics["phase_object_xy_displacement_m"]={phase:max(float(np.linalg.norm(np.asarray(r["object_position"])[:2]-np.asarray(first)[:2]))
            for r in trajectory[48:] if r["phase"] == phase) for phase in {r["phase"] for r in trajectory[48:]}}
        write(directory/"TRAJECTORY.json",trajectory)
        result={"model":label,"task":task,"weight":weight,"metrics":metrics,"termination":value["termination"],
                "official_success_observed":value["success"],"benchmark_accuracy":None,"wall_seconds":time.monotonic()-started,
                "scope":"48-target expert prefix then bounded real feedback; no benchmark acc"}
    finally:
        if child is not None: stop_children([child])
        if session is not None: session.reset()
        torch.cuda.empty_cache()
    write(directory/"result.json",result)
    mapping={n:v for n,v in files(directory).items() if n != "COMPLETE.json" and not n.endswith(".log")}
    write(directory/"COMPLETE.json",{"identity":ident,"files":mapping})
    print(f"[physical complete] {label}/{task} max_lift={metrics['max_lift_after_handoff_m']:.4f}m "
          f"retained_contact={metrics['lift_contact_proxy_observed']} "
          f"preclosure_xy_motion={metrics['phase_object_xy_displacement_m'].get('reference_preclosure')}",flush=True)
    return result


def physical(root,output,bound,model,gpu):
    from .model import load_observation_encoders
    stage_result(output,"evaluate",bound,required=True)
    folder=output/"frozen"; frozen=read(folder/"FROZEN.json"); results=[]
    encoders=None
    try:
        for task in TASKS:
            expert=read(folder/frozen["experts"][task]["path"]); item=frozen["inputs"][task+"_online_initial"]
            for label in ("expert","original",*BRANCHES):
                boundary(output)
                if label != "expert" and encoders is None:
                    progress(output,label,"encoder_load",len(results),8)
                    encoders=load_observation_encoders(bound["config"],next(model.memory.parameters()).device)
                value=physical_case(root,output,bound,model,encoders,gpu,task,label,item,expert,folder,len(results))
                results.append(value)
                if label == "expert" and not value["metrics"]["lift_contact_proxy_observed"]:
                    raise ValueError(f"{task} expert positive-control grasp/lift not observed within128; report/pack remain available")
        complete(output/"physical",bound,{"cases":results,"total":8,"target_cap":128,"benchmark_accuracy":None,
                                         "scope":"two existing scenes, four conditions each; no new expert search"})
    finally:
        if encoders is not None: del encoders


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument("stage",choices=("baseline","fit","evaluate","physical"))
    parser.add_argument("--root",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--gpu-uuid",required=True); args=parser.parse_args()
    root,output=args.root.resolve(),args.output.resolve(); bound=require_prepared(root,output); directory=output/args.stage
    if stage_result(output,args.stage,bound): print(f"[reuse] {args.stage} complete and checksummed",flush=True); return
    directory.mkdir(exist_ok=True)
    def request_stop(*_): write(output/"STOP.json",{"time":time.time(),"reason":"worker_signal"})
    for sig in (signal.SIGINT,signal.SIGTERM): signal.signal(sig,request_stop)
    import torch
    from .data import CachedEpisodes
    from .integration_contract import configure_numerics
    from .model import S1Model
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1 or torch.cuda.get_device_capability(0) != (9,0):
        raise ValueError("Expose the single bound H100; A100 remains a separate environment")
    configure_numerics(bound["config"]); cache_stamp_bootstrap(output,bound["config"])
    progress(output,"-","model_load",0,128 if args.stage == "fit" else 1)
    model=S1Model(bound["config"],torch.device("cuda:0")).eval()
    if args.stage == "fit": fit(root,output,bound,model)
    elif args.stage == "physical": physical(root,output,bound,model,args.gpu_uuid)
    else:
        if args.stage == "evaluate": stage_result(output,"fit",bound,required=True)
        dataset=CachedEpisodes(bound["config"],"val"); result=[]
        for label in (("original",) if args.stage == "baseline" else BRANCHES):
            result.extend(measure(root,output,bound,model,label,dataset,directory/"measurements"/label))
        complete(directory,bound,{"cases":result,"split":"val","action_samples":len(result),"fm_forwards":len(result),
                                  "noise_shared_across_models":True,"benchmark_accuracy":None})
    count=256 if args.stage == "fit" else 8 if args.stage == "physical" else len(result)
    progress(output,args.stage,"complete",count,count,eta_seconds=0,eta_scope="requested stage complete")
    print(f"[complete worker] {args.stage}; original checkpoints remain unchanged",flush=True)


if __name__ == "__main__": main()
