"""Bounded S1 investigation. Historical evidence is read, never re-approved."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import csv
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

from .common import atomic_json, fingerprint, load_config, read_json, seed_for, sha256
from .history import evaluation_phase, select_ids, online_contract, training_period, training_phase

VERSION = "s1-diagnosis-v1"
TASKS = ("put_back_block", "swap_blocks")
STAGES = ("inherit", "inventory", "offline", "paths", "gradients", "expert", "fixed", "recorded", "contacts", "phase_trace", "random", "micro", "retest8", "retest40", "report", "backup")


def check_stop(root):
    if (Path(root) / "STOP_REQUESTED").exists():
        raise InterruptedError("Stopped at a diagnostic boundary; completed cases are retained.")


def immutable_json(path, value):
    path = Path(path)
    if path.exists() and read_json(path) != value:
        raise ValueError(f"Identity changed: {path}; use a new diagnostic directory.")
    if not path.exists():
        atomic_json(path, value)


def safe_rows(path):
    """Only a final torn line is recoverable; report it instead of discarding silently."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    result, torn = [], None
    for i, line in enumerate(lines):
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            if i != len(lines)-1:
                raise ValueError(f"Corrupt interior JSONL record: {path}:{i+1}")
            torn = {"line": i+1, "sha256": hashlib.sha256(line.encode()).hexdigest()}
    return result, torn


def window_anchors(states, targets, anchors):
    import numpy as np
    anchors = sorted(set(map(int, anchors)))
    if not anchors:
        raise ValueError("Episode has no valid anchor.")
    changes = np.flatnonzero(np.any(np.abs(np.diff(targets[:, [6, 13]], axis=0)) > .05, axis=1)) + 1
    event = int(changes[0]) if len(changes) else None
    # These are diagnostic windows, not a claim that every episode needs memory.
    nearest = lambda x: min(anchors, key=lambda a: (abs(a-x), a))
    return {"initial": anchors[0], "gripper": nearest(event if event is not None else len(states)//3),
            "middle": nearest(len(states)//2), "tail": anchors[-1]}, event


def case_plan(windows, cfg):
    cases = []
    representatives = [w for w in windows if w["stage"] == "gripper"]
    for w in windows:
        for label in ("gate_zero", "step_000000", "step_001500", "step_002000"):
            periods = (1, 4, 8, 16) if label in ("step_001500", "step_002000") else (8,)
            for period in periods:
                phase = evaluation_phase(cfg, period, w["episode_id"])
                cases.append({"window": w["id"], "weight": label, "T": period, "phase": phase,
                              "condition": "gate_zero" if label == "gate_zero" else "full", "sample": True})
    for w in representatives:
        for label in ("step_001500", "step_002000"):
            for period in range(1, 17):
                if period not in (1, 4, 8, 16):
                    cases.append({"window": w["id"], "weight": label, "T": period,
                        "phase": evaluation_phase(cfg, period, w["episode_id"]), "condition": "full", "sample": False})
            phase = evaluation_phase(cfg, 8, w["episode_id"])
            cases.append({"window": w["id"], "weight": label, "T": 8, "phase": (phase+4)%8, "condition": "full", "sample": True})
            for condition in ("current_only", "permute_history"):
                cases.append({"window": w["id"], "weight": label, "T": 8, "phase": phase, "condition": condition, "sample": True})
    for row in cases:
        row["id"] = fingerprint(row)[:20]
    if len({r["id"] for r in cases}) != len(cases):
        raise ValueError("Duplicate diagnostic cases.")
    return cases


def source_files(cfg):
    root = Path(cfg["root"])
    return {str(p.relative_to(root)).replace("\\", "/"): sha256(p)
            for folder in ("src/fastwam", "scripts/memory_s1", "configs/memory_s1")
            for p in sorted((root / folder).rglob("*"))
            if p.is_file() and p.suffix in (".py", ".sh", ".yaml", ".json")}


def identity(cfg):
    import torch
    from .fused_evaluation import runtime_binding
    from .posttrain import runtime_options
    runtime_cfg=copy.deepcopy(cfg);runtime_cfg['selection_runtime']=runtime_options('fused-resident')
    simulator=runtime_binding(runtime_cfg)
    from .integration_contract import simulator_sources
    reference_lock=Path(cfg['paths']['run'])/'integration_evidence/sources.json'
    if not reference_lock.exists():reference_lock=Path(cfg['root'])/cfg['integration']['output']/'sources.json'
    references=read_json(reference_lock)
    for repo in references['repositories'].values():
        for relative,expected in repo['files'].items():
            if sha256(Path(cfg['root'])/repo['path']/relative)!=expected:
                raise ValueError(f'Pinned reference content changed: {relative}')
    run = Path(cfg["paths"]["run"])
    weights = {f"step_{step:06d}": {"path": str(run / "weights" / f"step_{step:06d}.pt"),
               "sha256": sha256(run / "weights" / f"step_{step:06d}.pt")} for step in (0, 1500, 2000)}
    required = [Path(cfg["paths"]["prepared"]) / "manifest.json", Path(cfg["paths"]["prepared"]) / "alignment_approved.json",
                Path(cfg["paths"]["cache"]) / "manifest.json"]
    return {"version": VERSION, "config": cfg, "source": source_files(cfg), "weights": weights,
            "git_commit":subprocess.check_output(['git','-C',cfg['root'],'rev-parse','HEAD'],text=True).strip(),
            "simulator_sources_sha256":simulator_sources(cfg),"reference_sources":references,
            "environment":{"inference_python":sys.version,"torch":torch.__version__,"cuda":torch.version.cuda,
                "simulator":simulator,"flags":{k:os.environ.get(k) for k in ('CUDA_LAUNCH_BLOCKING','CUBLAS_WORKSPACE_CONFIG')}},
            "resources": {k: sha256(cfg["paths"][k]) for k in ("base", "stats", "vae", "t5")},
            "evidence": {str(p): sha256(p) for p in required}, "history": online_contract(cfg),
            "diagnostic_scenes_sha256": sha256(Path(cfg['root'])/cfg['diagnosis']['scenes'])}


def inventory(cfg, root, bound):
    import numpy as np
    import torch
    from .data import read_episode, choose_instruction
    from .phase_validation import verify_full_inventory
    prepared = Path(cfg["paths"]["prepared"])
    manifest = read_json(prepared / "manifest.json")
    from .common import make_cache_contract
    cached=read_json(Path(cfg['paths']['cache'])/'manifest.json')
    if cached['signature']!=fingerprint(make_cache_contract(cfg,manifest)):
        raise ValueError('Dense cache encoding/resources differ from this run; preserve it and inspect the contract.')
    approval = read_json(prepared / "alignment_approved.json")
    if approval.get("approved") is not True or approval.get("manifest_sha") != fingerprint(manifest):
        raise ValueError("Real alignment review does not bind this prepared manifest.")
    episodes, windows, groups = [], [], {}
    if len(manifest["episodes"]) != 100:
        raise ValueError("Expected the original 100 episodes; investigate inventory before using windows.")
    raw_digests, scalar_digests = {}, {}
    for index, record in enumerate(manifest["episodes"]):
        check_stop(root)
        raw = Path(cfg["root"]) / record["raw"]
        if sha256(raw) != record["raw_sha256"]:
            raise ValueError(f"Raw hash mismatch: {record['episode_id']}")
        state, action, cameras, kind, metadata, embedded = read_episode(raw)
        stored = torch.load(prepared / record["file"], map_location="cpu", weights_only=True)
        instruction, _ = choose_instruction(raw, embedded)
        if not (np.array_equal(state, stored["states"].numpy()) and np.array_equal(action, stored["targets"].numpy())
                and instruction == record["instruction"] and cameras == record["camera_paths"]
                and kind == record["source_kind"] and metadata == record["attributes"]):
            raise ValueError(f"Raw/prepared discrepancy: {record['episode_id']}")
        anchors, event = window_anchors(state, action, stored["anchors"].tolist())
        scalar_sha = hashlib.sha256(state.tobytes()+action.tobytes()).hexdigest()
        for mapping, key in ((raw_digests, record["raw_sha256"]), (scalar_digests, scalar_sha)):
            mapping.setdefault(key, []).append({"id": record["episode_id"], "split": record["split"]})
        row = {"id": record["episode_id"], "task": record["task"], "split": record["split"], "length": len(state),
               "camera_paths": cameras, "instruction": instruction, "source_kind": kind,
               "raw_sha256": record["raw_sha256"], "scalar_sha256": scalar_sha,
               "duplicate_state_ids": (np.flatnonzero(np.all(np.diff(state, axis=0) == 0, axis=1))+1).tolist(),
               "gripper_event_ids": {str(j): (np.flatnonzero(np.abs(np.diff(action[:, j]))>.05)+1).tolist() for j in (6,13)},
               "frequency_metadata": metadata.get("stored_frequency"), "physical_timeline": "unknown_without_verified_collector_intervals",
               "action_min": action.min(0).tolist(), "action_max": action.max(0).tolist(), "anchors": anchors, "first_gripper_event": event}
        episodes.append(row)
        atomic_json(root/'evidence'/'scalar_sequences'/f'{index:03d}.json',{'episode_id':record['episode_id'],
            'states':state.tolist(),'targets':action.tolist(),'anchors':stored['anchors'].tolist(),
            'index_semantics':kind,'physical_time':'unknown unless independently verified'})
        groups.setdefault((record["task"], record["split"]), []).append((record, row))
        print(f"[inventory] data {index+1}/100 {record['episode_id']}", flush=True)
    for task in TASKS:
        for split, expected in (("train",45), ("val",5)):
            candidates = groups.get((task, split), [])
            if len(candidates) != expected:
                raise ValueError(f"Wrong split count: {task}/{split}: {len(candidates)}")
            # Prefer an episode with a real gripper event, deterministic tie break.
            record, row = min(candidates, key=lambda pair: (pair[1]["first_gripper_event"] is None, pair[0]["episode_id"]))
            for stage, anchor in row["anchors"].items():
                windows.append({"id": f"{task}_{split}_{stage}", "task": task, "split": split, "stage": stage,
                    "episode_id": record["episode_id"], "anchor": anchor, "record": record,
                    "has_gripper_event": row["first_gripper_event"] is not None})
    cases = case_plan(windows, cfg)
    selector_rows = []
    for window in windows:
        for period in range(1,17):
            for phase in range(period):
                anchor = window["anchor"]
                actual = select_ids(range(anchor+1), anchor, period, phase=phase)
                expected = sorted({0, anchor, *range(0,anchor+1,16), *range(phase,anchor+1,period)})
                if actual != expected:
                    raise ValueError("Selector differs from independent set construction.")
                selector_rows.append({"window": window["id"], "T": period, "phase": phase, "ids": actual})
    atomic_json(root / "windows.json", {"windows": windows, "cases": cases, "selector_cases": len(selector_rows),
        "representatives": [w["id"] for w in windows if w["stage"] == "gripper"],
        "fm_phase_estimator": "one predetermined uniform phase per T, equal T weight; small-sample estimate",
        "sampling_counts": dict(Counter(("action_sample" if c["sample"] else "single_fm") for c in cases))})
    atomic_json(root / "selector_cases.json", selector_rows)
    atomic_json(root / "data_audit.json", {"episodes": episodes, "cross_split_raw_duplicates": [v for v in raw_digests.values() if len({r['split'] for r in v})>1],
        "cross_split_scalar_duplicates": [v for v in scalar_digests.values() if len({r['split'] for r in v})>1],
        "review_sha256": sha256(prepared / "alignment_approved.json"), "physical_units": "joint radians and gripper convention; not Cartesian millimetres"})
    atomic_json(root / "cache_inventory.json", verify_full_inventory(cfg))
    audit_training(cfg, root)
    collect_evidence(cfg, root, bound)
    return {"complete": True, "episodes": 100, "windows": 16, "selector_cases": len(selector_rows),
            "root_cause": "undetermined; inspect data/train/evaluation evidence and run paired checks"}


def audit_training(cfg, root):
    run = Path(cfg["paths"]["run"])
    counts, phases, lengths, mismatches, files = Counter(), Counter(), [], [], []
    # Actual samples only: do not substitute regenerated samples for missing logs.
    for path in sorted(run.glob("*samples*.jsonl")):
        rows, torn = safe_rows(path)
        files.append({"path": str(path), "sha256": sha256(path), "torn_final_line": torn})
        for row in rows:
            samples = row.get("samples", [row])
            for sample in samples:
                period = sample.get("T", sample.get("history_period"))
                phase = sample.get("phase", sample.get("history_phase"))
                if period is None or phase is None:
                    continue
                counts[str(period)] += 1
                phases[f"{period}:{phase}"] += 1
                if not 1 <= period <= 16 or not 0 <= phase < period:
                    mismatches.append({"reason": "illegal T/phase", "row": sample})
                ids = sample.get("frame_ids", sample.get("read_frame_ids"))
                if ids is not None:
                    lengths.append(len(ids))
                update=sample.get('sampling_update');slot=sample.get('global_slot')
                if update is not None and slot is not None and (period != training_period(cfg,update,slot) or phase != training_phase(cfg,update,slot,period)):
                    mismatches.append({'reason':'actual logged sampling differs from stateless training recipe','row':sample})
    atomic_json(root / "training_sampling.json", {"files": files, "T_counts": counts, "phase_counts": phases,
        "samples": sum(counts.values()), "history_lengths": lengths, "invalid": mismatches,
        "status": "observed" if counts else "missing_actual_sampling_logs", "uniformity": "frequency report, not an exact-equality gate",
        "rng_check": "stateless unit regression; empirical independence is not proved by counts"})


def collect_evidence(cfg, root, bound):
    import torch
    target = root / "evidence"
    target.mkdir(exist_ok=True)
    paths = []
    for name, directory in (("training", Path(cfg["paths"]["run"])), ("prepared", Path(cfg["paths"]["prepared"]))):
        for path in sorted(directory.glob("*")):
            if path.is_file() and path.suffix in (".json", ".jsonl", ".csv", ".yaml") and path.stat().st_size < 64*2**20:
                destination = target / name / path.name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, destination)
                paths.append({"source": str(path), "copy": str(destination.relative_to(root)), "sha256": sha256(path)})
    for relative in bound["source"]:
        source = Path(cfg["root"]) / relative
        destination = target / "source" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    additional=[Path(cfg['paths']['stats']),Path(cfg['root'])/'resources/download_lock.json',
                Path(cfg['paths']['cache'])/'manifest.json']
    run=Path(cfg['paths']['run'])
    for folder in (run/'integration_evidence',run/'provenance'):
        additional.extend(p for p in folder.rglob('*') if p.is_file() and
                          (p.suffix in ('.json','.yaml','.yml','.patch','.txt') or p.name in ('simulator_sources.tar.gz','reference_sources.tar.gz','source.bundle')))
    missing=[]
    for source in additional:
        if not source.is_file():missing.append(str(source));continue
        if source.stat().st_size>64*2**20:missing.append(f'oversized compact evidence: {source}');continue
        relative=source.resolve().relative_to(Path(cfg['root']).resolve())
        destination=target/'support'/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,destination)
        paths.append({'source':str(source),'copy':str(destination.relative_to(root)),'sha256':sha256(source)})
    patch=subprocess.check_output(['git','-C',cfg['root'],'diff','--binary','HEAD','--','src/fastwam','scripts/memory_s1','configs/memory_s1'])
    (target/'server_source.patch').write_bytes(patch)
    old = Path(cfg["root"]) / cfg["diagnosis"]["old_evaluation"]
    results = []
    from .eval_state import EpisodeQueue
    for path in sorted(old.rglob("queue.json")):
        if "packages" in path.relative_to(old).parts:
            continue
        queue = EpisodeQueue(path.parent)
        saved = queue.snapshot()
        for job in saved["jobs"]:
            row = {"queue": str(path), "job": job["id"], "state": job["state"]}
            if job["state"] == "complete":
                result = queue.result(job, saved["identity"])
                row["result"] = result
                attempt = path.parent / job["directory"]
                for name in ("result.json", "complete.json", "decisions.jsonl", "executed_actions.jsonl", "simulator_backend.json"):
                    source = attempt / name
                    if source.is_file():
                        destination = target / "old_evaluation" / source.relative_to(old)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, destination)
            results.append(row)
    atomic_json(root / "old_results.json", {"expected": 40, "observed": len(results), "jobs": results})
    weights = {}
    for label, record in bound["weights"].items():
        payload = torch.load(record["path"], map_location="cpu", weights_only=True)
        if not isinstance(payload.get("memory"), dict):
            raise ValueError(f"Missing memory state: {label}")
        weights[label] = {**record, "metadata": {k: v for k,v in payload.items() if isinstance(v,(str,int,float,bool,type(None)))},
            "parameters": {k: {"shape": list(v.shape), "finite": bool(torch.isfinite(v).all()),
                             "norm": float(v.float().norm()), "sha256": hashlib.sha256(v.contiguous().reshape(-1).view(torch.uint8).numpy().tobytes()).hexdigest()}
                           for k,v in payload["memory"].items()}}
    atomic_json(root / "weight_audit.json", weights)
    distinct={label:sum(value['sha256']!=weights['step_000000']['parameters'][name]['sha256']
                       for name,value in item['parameters'].items()) for label,item in weights.items()}
    atomic_json(root/'weight_changes.json',{'changed_parameters_from_actual_step0':distinct,
        'step0_is_strict_base':False,'strict_base_condition':'gate_zero'})
    checkpoints=[]
    from .checkpoint import verified_load
    for marker in sorted((Path(cfg['paths']['run'])/'checkpoints').glob('step_*/complete.json')):
        # Locally generated, checksum-verified complete points include numpy RNG state.
        payload=verified_load(marker.parent)
        optimizer=payload['optimizer'];entries=list(optimizer['state'].values())
        checkpoints.append({'path':str(marker.parent),'marker':read_json(marker),'updates':payload['completed_updates'],
            'sampler_next_update':payload['sampler_next_update'],'scheduler':payload['scheduler'],
            'optimizer_groups':optimizer['param_groups'],'optimizer_states':len(entries),
            'optimizer_step_values':sorted({float(v['step']) for v in entries if 'step' in v}),
            'moments_finite':all(bool(torch.isfinite(v[k]).all()) for v in entries for k in ('exp_avg','exp_avg_sq') if k in v),
            'progress':payload['progress']})
        del payload
    atomic_json(root/'checkpoint_audit.json',{'checkpoints':checkpoints,'missing':[] if checkpoints else ['local complete optimizer/scheduler recovery point']})
    import importlib.metadata as md
    environment = {"python": sys.version, "executable": sys.executable,
        "packages": sorted((d.metadata['Name'], d.version) for d in md.distributions() if d.metadata.get('Name')),
        "flags": {k: os.environ.get(k) for k in ("CUDA_LAUNCH_BLOCKING","CUBLAS_WORKSPACE_CONFIG","CUDA_VISIBLE_DEVICES","OMP_NUM_THREADS")}}
    atomic_json(root / "environment.json", environment)
    host = Path(cfg["root"]) / cfg["diagnosis"]["container_record"]
    if host.exists():
        shutil.copy2(host, target / "container-host.json")
    atomic_json(root / "evidence_manifest.json", {"files": paths,
        "missing": missing + ([] if host.exists() else [str(host)]) + ([] if len(results)==40 else ["complete inventory of 40 previous episodes"]),
        "credentials_collected": False, "optimizer_state": "checkpoint_audit.json; weights alone do not contain optimizer/scheduler"})


def require_stage(root, stage):
    from .diagnosis_followup import stage_record
    return stage_record(root, stage)


def report(cfg, root, bound):
    from .diagnosis_followup import REQUIRED, stage_record
    matrix = {}
    for stage in STAGES:
        if stage in ("report", "backup"): continue
        try:
            matrix[stage] = stage_record(root, stage)
        except (ValueError, OSError) as error:
            matrix[stage] = {"complete": False, "status": "not_run" if not (root/f"{stage}.json").exists() else "invalid",
                             "reason": str(error)}
    for stage in matrix:
        error = root / f"{stage}.error.json"
        if error.exists():
            matrix[stage] = {"status": "error", **read_json(error)}
    missing = [stage for stage in REQUIRED if matrix[stage].get("complete") is not True]
    expected_cases = read_json(root/'windows.json')['cases'] if (root/'windows.json').exists() else []
    case_paths = list((root/'offline_cases').glob('*.json'))
    counts = {"offline_planned": len(expected_cases), "offline_result_files": len(case_paths),
              "offline_status": "not_run" if not case_paths else matrix['offline'].get('status','complete' if matrix['offline'].get('complete') else 'incomplete'),
              "error_stages": [s for s,r in matrix.items() if r.get('status') in ('error','invalid')]}
    atomic_json(root / "status_matrix.json", matrix)
    offline = [read_json(p) for p in sorted((root / "offline_cases").glob("*.json"))]
    counts.update(offline_action_samples=sum(bool(r.get('sample')) for r in offline),
                  offline_single_fm=sum(r.get('sample') is False for r in offline),
                  offline_completed_verified=len(offline) if matrix['offline'].get('complete') else 0,
                  offline_missing_cases=sorted({c['id'] for c in expected_cases}-{r['id'] for r in offline}),
                  offline_case_errors=sum(bool(r.get('error')) for r in offline))
    fields = ["window", "split", "stage", "weight", "condition", "T", "phase", "frames", "fm", "fm_unweighted", "sample_mse",
              "left_arm_mae", "right_arm_mae", "left_gripper_mae", "right_gripper_mae", "seconds", "coverage"]
    for row in offline:
        metrics = row.get('metrics', {}).get('all')
        if metrics:
            row.update(left_arm_mae=metrics['left_arm_mae'], right_arm_mae=metrics['right_arm_mae'],
                       left_gripper_mae=metrics['gripper_mae'][0], right_gripper_mae=metrics['gripper_mae'][1])
    with (root / "history_diagnostics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(offline)
    rows = []
    from .eval_state import EpisodeQueue
    for step in (1500,2000):
        directory = root / "retest" / f"step_{step:06d}"
        if not (directory / "queue.json").exists():
            continue
        queue = EpisodeQueue(directory); value = queue.snapshot()
        for task in TASKS:
            jobs = [j for j in value['jobs'] if j['scene']['task']==task]
            done = [queue.result(j,value['identity']) for j in jobs if j['state']=='complete']
            success = sum(r['success'] for r in done)
            rows.append({"step":step,"task":task,"success":success,"completed":len(done),"planned":len(jobs),
                         "acc":success/len(done) if done else None,"official_limit":sum(r.get('termination')=='official_target_limit' for r in done),
                         "error":sum(j['state']=='error' for j in jobs),"interrupted":sum(j['state']=='interrupted' for j in jobs)})
    atomic_json(root / "success_table.json", {"protocol":"fixed T=8, original episode phase, 32/16/10", "rows":rows})
    if rows:
        with (root / "success_table.csv").open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    trajectories=[]
    for mode,folder in (('fixed',root/'fixed'/'qualification'),('seeded_per_decision',root/'random')):
        for path in folder.rglob('queue.json'):
            if 'packages' in path.parts:continue
            queue=EpisodeQueue(path.parent);state=queue.snapshot()
            for job in state['jobs']:
                item={'mode':mode,'task':job['scene']['task'],'seed':job['scene']['seed'],'state':job['state'],
                      'task_acc':None,'scope':'short prefix is not a task failure or success-rate estimate'}
                if job['state']=='complete':
                    result=queue.result(job,state['identity']);attempt=path.parent/job['directory']
                    decisions,_=safe_rows(attempt/'decisions.jsonl')
                    item.update(termination=result.get('termination'),executed_targets=result.get('executed_targets'),
                        sampling=[{k:r.get(k) for k in ('frame_id','history_period','history_phase','read_frame_ids','noise_seed','readout_norm')} for r in decisions])
                trajectories.append(item)
    atomic_json(root/'random_policy_diagnostics.json',{'trajectories':trajectories,
        'attribution':'Only recorded-input paired comparisons isolate numerical differences; diverged rollouts have different later observations.'})
    # Do not infer memory use from a flat average; preserve every window and condition.
    if offline:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(8,4))
        for label in ('step_001500','step_002000'):
            pairs=[]
            for period in (1,4,8,16):
                selected=[r['fm'] for r in offline if r['weight']==label and r['T']==period and r['condition']=='full' and r.get('sample')
                          and r['phase']==evaluation_phase(cfg,period,r['episode_id'])]
                if selected:pairs.append((period,sum(selected)/len(selected)))
            if pairs:ax.plot(*zip(*pairs),marker='o',label=label)
        ax.set(xlabel='History period T',ylabel='FM (diagnostic windows; phases listed in CSV)')
        ax.legend();fig.tight_layout();fig.savefig(root/'history_diagnostics.png');fig.savefig(root/'history_diagnostics.pdf');plt.close(fig)
    value = {"complete": True, "report_generated": True, "required_diagnostics_complete": not missing,
             "missing_required_stages": missing, "counts": counts,
             "root_cause":"undetermined; reviewed causal evidence is required", "matrix":"status_matrix.json"}
    atomic_json(root/'DIAGNOSIS_STATUS.json', value)
    print(f"[report] generated=True required_complete={not missing} missing={missing} cases={counts}",flush=True)
    return value


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument("stage",choices=STAGES)
    parser.add_argument("--config",required=True)
    parser.add_argument("--output",required=True)
    parser.add_argument("--resume",action="store_true")
    parser.add_argument("--confirmed-fix",help="Reviewed root-cause/fix JSON, mandatory before retest")
    parser.add_argument("--parent", help="Original diagnostic directory; read-only historical citations")
    args=parser.parse_args()
    cfg=load_config(args.config)
    if args.parent: cfg.setdefault('diagnosis',{})['parent'] = str(Path(args.parent).resolve())
    root=Path(args.output).resolve();root.mkdir(parents=True,exist_ok=True)
    from .eval_state import locked, process_identity
    with locked(root / "diagnosis.lock",blocking=False):
        if args.resume:
            (root / "STOP_REQUESTED").unlink(missing_ok=True)
            (root / "STOP.json").unlink(missing_ok=True)
        check_stop(root)
        atomic_json(root / "owner.json",{"owner":process_identity(),"argv":sys.argv,"started":time.time(),"stage":args.stage})
        started=time.monotonic()
        try:
            bound=identity(cfg);immutable_json(root / "identity.json",bound)
            prior=root/f'{args.stage}.json'
            if args.resume and args.stage not in ('report','backup') and prior.exists():
                require_stage(root,args.stage)
                error=root/f'{args.stage}.error.json'
                if error.exists():error.rename(root/f'{args.stage}.resolved_error_{time.time_ns()}.json')
                print(f"[already complete] {args.stage}; identity and artifact hashes verified",flush=True)
                return
            if prior.exists():prior.rename(root/f'{args.stage}.previous_{time.time_ns()}.json')
            if args.stage=="inherit":
                from .diagnosis_followup import inherit
                if not cfg.get('diagnosis',{}).get('parent'): raise ValueError('Pass --parent with the original evidence directory')
                value=inherit(cfg,root,bound)
            elif args.stage=="inventory":
                value=inventory(cfg,root,bound)
            elif args.stage=="report":
                value=report(cfg,root,bound)
            elif args.stage=="backup":
                from .posttrain import upload_compact
                upload_compact(cfg,Path(cfg['paths']['run']),root,'diagnosis')
                value={"complete":True,"remote_readback":read_json(root/'HF_diagnosis.json')}
            else:
                require_stage(root,"inventory")
                from . import diagnosis_gpu
                value=diagnosis_gpu.run_stage(args.stage,cfg,root,bound,args)
            from .diagnosis_followup import artifact_files
            atomic_json(root / f"{args.stage}.json",{**value,"seconds":time.monotonic()-started,"identity":fingerprint(bound),
                       "artifacts":artifact_files(root,args.stage)})
            error=root/f'{args.stage}.error.json'
            if error.exists():error.rename(root/f'{args.stage}.resolved_error_{time.time_ns()}.json')
            print(f"[complete] {args.stage} elapsed={time.monotonic()-started:.1f}s",flush=True)
        except BaseException:
            import traceback
            atomic_json(root / f"{args.stage}.error.json",{"complete":False,"traceback":traceback.format_exc(),"seconds":time.monotonic()-started})
            raise
        finally:
            atomic_json(root / "owner.json",{"owner":None,"stage":args.stage,"finished":time.time()})


if __name__=="__main__":
    main()
