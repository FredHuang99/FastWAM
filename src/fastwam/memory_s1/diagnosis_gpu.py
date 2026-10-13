"""GPU/physical stages of the bounded S1 investigation; invoked explicitly."""
from __future__ import annotations

import copy
import gc
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import torch

from .common import atomic_json, fingerprint, read_json, seed_for, sha256, ReleaseNormalizer
from .data import CachedEpisodes, collate, history_variant, official_decoder
from .history import evaluation_phase, resolve_online, override_online, online_arguments
from .s1_diagnosis import check_stop, immutable_json, require_stage, TASKS


def load_weight(model, bound, label):
    label = "step_000000" if label == "gate_zero" else label
    record = bound["weights"][label]
    if sha256(record["path"]) != record["sha256"]:
        raise ValueError("Checkpoint changed during diagnosis.")
    payload = torch.load(record["path"], map_location="cpu", weights_only=True)
    expected_step=int(label.rsplit('_',1)[1])
    if payload.get('completed_updates')!=expected_step or any(payload.get('identity',{}).get(k+'_sha256')!=bound['resources'][k] for k in ('base','stats')):
        raise ValueError('Weight update/base/normalizer identity mismatch.')
    model.memory.load_state_dict(payload["memory"], strict=True)
    model.eval()


def setup(cfg):
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("Expose exactly one GPU for the bounded diagnostic.")
    from .integration_contract import configure_numerics
    configure_numerics(cfg)
    from .model import S1Model
    device = torch.device("cuda:0")
    model = S1Model(cfg, device).eval()
    return model, device, {s: CachedEpisodes(cfg,s) for s in ("train","val")}


def noise_for(cfg, window, device):
    # Synthetic episode seed 0 provides paired offline noise, independent of T
    # and weight. Actual rollout requests use their recorded episode/noise seed.
    seed = seed_for(cfg['seed'], 0, window['anchor'], 'closed-loop-noise')
    generator = torch.Generator(device='cpu').manual_seed(seed)
    noise = torch.randn(1,32,14,generator=generator).to(device)
    tau_seed = seed_for(cfg['seed'],window['id'],0,'diagnostic-fm-time-v1')
    tau = torch.rand(1,generator=torch.Generator(device='cpu').manual_seed(tau_seed)).to(device)
    return noise, tau, seed


def record_for(dataset, window):
    return next(r for r in dataset.by_task[window['task']] if r['episode_id']==window['episode_id'])


def sample_for(dataset, window, period, phase, condition='full'):
    sample = dataset.at(record_for(dataset,window),window['anchor'],period,phase)
    if condition=='permute_history':
        sample=dict(sample); sample['history']=sample['history'].clone()
        positions=torch.nonzero(sample['frame_ids']!=sample['t']).flatten()
        if len(positions)>1:
            sample['history'][positions]=sample['history'][positions.flip(0)]
        return sample
    return history_variant(sample,condition)


def error_metrics(actions, batch, normalizer, raw_targets=None, raw_state=None):
    prediction=normalizer.denormalize(actions.float())
    represented_target=normalizer.denormalize(batch['actions'].float())
    target=represented_target if raw_targets is None else raw_targets.to(actions.device)
    valid=batch['action_valid']
    diff=prediction-target
    mean,scale=normalizer.fields['state']
    state=batch['proprio'].float()*scale.to(batch['proprio'].device)+mean.to(batch['proprio'].device)
    if raw_state is not None:state=raw_state.to(actions.device)
    hold=state[:,None].expand_as(target)
    def metrics(mask):
        count=int(mask.sum())
        if not count:
            return None
        mse=((actions-batch['actions']).square()*mask[...,None]).sum()/(14*count)
        mae=(diff.abs()*mask[...,None]).sum((0,1))/count
        return {'valid_targets':count,'normalized_mse':float(mse),'joint_mae':mae.tolist(),
            'left_arm_mae':float(mae[:6].mean()),'right_arm_mae':float(mae[7:13].mean()),
            'gripper_mae':mae[[6,13]].tolist(),
            'hold_joint_mae':((hold-target).abs()*mask[...,None]).sum((0,1)).div(count).tolist()}
    first=valid.clone();first[:,16:]=False
    second=valid.clone();second[:,:16]=False
    moving=(target-hold).abs().amax(-1)>.01
    return {'all':metrics(valid),'first16':metrics(first),'last16':metrics(second),
            'label_roundtrip_max_abs':float(((represented_target-target).abs()*valid[...,None]).max()),
            'moving':metrics(valid&moving),'near_hold':metrics(valid&~moving),
            'predicted_gripper':prediction[0,:, [6,13]].tolist(),
            'target_gripper':target[0,:, [6,13]].tolist(),
            'predicted_native':prediction[0].tolist(), 'target_native':target[0].tolist(),
            'current_state_native':state[0].tolist(), 'action_valid':valid[0].tolist(),
            'units':'joint radians / native gripper units; no Cartesian millimetre interpretation'}


@torch.no_grad()
def offline(cfg, root, bound):
    plan=read_json(root/'windows.json'); windows={w['id']:w for w in plan['windows']}
    model,device,datasets=setup(cfg)
    normalizer=ReleaseNormalizer(cfg['paths']['stats'])
    destination=root/'offline_cases';destination.mkdir(exist_ok=True)
    current=None; reports=[]; started=time.monotonic(); fresh=0
    ordered=sorted(plan['cases'],key=lambda c:(c['weight'],c['window'],c['T'],c['phase'],c['condition']))
    for number,case in enumerate(ordered,1):
        check_stop(root)
        path=destination/f"{case['id']}.json"
        key=fingerprint({'case':case,'identity':bound})
        if path.exists():
            value=read_json(path)
            if value['identity']!=key: raise ValueError('Offline case identity mismatch.')
            reports.append(value);continue
        if current!=case['weight']:
            load_weight(model,bound,case['weight']);current=case['weight']
        window=windows[case['window']];dataset=datasets[window['split']]
        sample=sample_for(dataset,window,case['T'],case['phase'],case['condition'])
        batch=collate([sample],device)
        noise,tau,noise_seed=noise_for(cfg,window,device)
        tick=time.monotonic(); gate=0 if case['condition']=='gate_zero' else 1
        injection=[]
        def observe(module,inputs,output):
            residual=output.float()-inputs[0].float()
            rounded=output.to(torch.bfloat16).float()-inputs[0].to(torch.bfloat16).float()
            injection.append({'residual_rms':float(residual.square().mean().sqrt()),
                              'bf16_nonzero_fraction':float((rounded!=0).float().mean())})
        hooks=[module.register_forward_hook(observe) for module in model.memory.injectors.values()]
        try:
            loss,diagnostic=model(batch,noise,tau,gate_scale=gate)
            value={**case,'identity':key,'split':window['split'],'stage':window['stage'],
                'episode_id':window['episode_id'],'anchor':window['anchor'], 'frames':len(sample['frame_ids']),
                'frame_ids':sample['frame_ids'].tolist(),'mandatory_overlap':sum(i%16==0 or i==window['anchor'] for i in sample['frame_ids'].tolist()),
                'fm':float(loss),'fm_unweighted':float(diagnostic['unweighted_fm'].mean()),'tau':float(tau[0]),
                'noise_bin':min(2,int(float(tau[0])*3)),'noise_seed':noise_seed,
                'readout_norm':float(diagnostic['readout_norm']),'coverage':'unknown'}
            if case['sample']:
                actions,_=model.sample(batch,noise,gate_scale=gate)
                if not torch.isfinite(actions).all():raise FloatingPointError('Nonfinite action sample.')
                prepared=torch.load(Path(cfg['paths']['prepared'])/window['record']['file'],map_location='cpu',weights_only=True)
                targets=torch.empty(1,32,14);count=int(batch['action_valid'].sum())
                targets[0,:count]=prepared['targets'][window['anchor']:window['anchor']+count]
                targets[0,count:]=targets[0,count-1]
                metrics=error_metrics(actions,batch,normalizer,targets,prepared['states'][window['anchor']][None])
                value.update(metrics=metrics,sample_mse=metrics['all']['normalized_mse'],normalized_actions=actions[0].cpu().tolist())
            value['injection']=injection
        finally:
            for hook in hooks:hook.remove()
        if not np.isfinite(value['fm']):raise FloatingPointError('Nonfinite FM.')
        torch.cuda.synchronize();value['seconds']=time.monotonic()-tick
        atomic_json(path,value);reports.append(value);fresh+=1
        eta=(len(plan['cases'])-number)*(time.monotonic()-started)/fresh
        print(f"[offline] {number}/{len(plan['cases'])} {current} {window['id']} T={case['T']} phase={case['phase']} frames={value['frames']} FM={value['fm']:.6f} elapsed={time.monotonic()-started:.1f}s remaining~{eta:.1f}s (mixed-case measured estimate)",flush=True)
    means=[]
    for wid in plan['representatives']:
        for label in ('step_001500','step_002000'):
            values=[]
            for period in range(1,17):
                phase=evaluation_phase(cfg,period,windows[wid]['episode_id'])
                values.append(next(r['fm'] for r in reports if r['window']==wid and r['weight']==label and r['T']==period and r['phase']==phase and r['condition']=='full'))
            means.append({'window':wid,'weight':label,'equal_T_mean_FM':sum(values)/16,'scope':'one fixed uniform phase per T, small-sample estimator'})
    atomic_json(root/'T_estimator.json',means)
    same_inputs={};invariants=[]
    for r in reports:
        if 'normalized_actions' not in r or r['condition']!='full':continue
        key=(r['window'],r['weight'],tuple(r['frame_ids']))
        if key in same_inputs:
            old=same_inputs[key]
            equal=r['normalized_actions']==old['normalized_actions'] and r['fm']==old['fm']
            invariants.append({'a':old['id'],'b':r['id'],'exact':equal})
        else:same_inputs[key]=r
    atomic_json(root/'same_selected_inputs.json',invariants)
    if any(not r['exact'] for r in invariants):raise ValueError('Identical selected inputs/noise gave different outputs; inspect same_selected_inputs.json.')
    from .diagnosis_followup import offline_analysis
    offline_analysis(root)
    return {'complete':True,'cases':len(reports),'planned_cases':len(plan['cases']),
            'action_samples':sum(r['sample'] for r in reports),'single_fm':sum(not r['sample'] for r in reports),
            'optimizer_updates':0,'root_cause':'not inferred from average FM'}


def exact(a,b):
    if isinstance(a,torch.Tensor):
        if a.shape!=b.shape:return {'exact':False,'shape':[list(a.shape),list(b.shape)]}
        return {'exact':bool(torch.equal(a.cpu(),b.cpu())), 'max_abs':float((a.float().cpu()-b.float().cpu()).abs().max())}
    return {'exact':a==b}


def request_from_raw(cfg, window, current=None):
    import h5py
    from .data import read_episode
    record=window['record']; current=window['anchor'] if current is None else current
    raw=Path(cfg['root'])/record['raw'];state,*_=read_episode(raw)
    decoder=official_decoder(Path(cfg['root'])/cfg['closed_loop']['simulator_root'])
    observations=[]
    with h5py.File(raw,'r') as handle:
        for frame in range(current+1):
            images=[np.ascontiguousarray(decoder(handle[key][frame]),dtype=np.uint8) for key in record['camera_paths']]
            observations.append({'frame_id':frame,'images':[i.tobytes() for i in images],
                                 'shapes':[list(i.shape) for i in images],'proprio':state[frame].tolist()})
    return {'current_id':current,'episode_seed':0,'task':window['task'],'instruction':record['instruction'],'observations':observations}


@torch.no_grad()
def paths(cfg, root, bound):
    from .model import load_observation_encoders
    from .sim_bridge import InferenceSession
    from .phase_validation import loader_comparison
    plan=read_json(root/'windows.json'); windows=[w for w in plan['windows'] if w['id'] in plan['representatives']]
    from .common import atomic_torch
    from .integration import fixture_trace,compare_trace,normalizer_probe,source_root
    normalizer=ReleaseNormalizer(cfg['paths']['stats']); cases=[]
    for w in windows:
        req=request_from_raw(cfg,w);observation=req['observations'][-1]
        episode=torch.load(Path(cfg['paths']['prepared'])/w['record']['file'],map_location='cpu',weights_only=True)
        raw=torch.empty(32,14);count=min(32,len(episode['targets'])-w['anchor'])
        raw[:count]=episode['targets'][w['anchor']:w['anchor']+count];raw[count:]=raw[count-1]
        noise,tau,seed=noise_for(cfg,w,'cpu');actions=normalizer.normalize(raw,'action')[None]
        cases.append({'case_id':w['id'],'record':w['record'],'task':w['task'],'frame_id':w['anchor'],
            'episode_seed':0,'images':[torch.from_numpy(np.frombuffer(b,dtype=np.uint8).reshape(s).copy()) for b,s in zip(observation['images'],observation['shapes'])],
            'state':episode['states'][w['anchor']],'instruction':req['instruction'],'noise_seed':seed,'noise':noise,
            'actions_raw':raw[None],'actions':actions,'action_valid':(torch.arange(32)<count)[None],
            'probe_tau':tau,'probe_noisy':normalizer_probe(actions,noise,tau)})
    atomic_torch(root/'paths'/'request.pt',{'config':cfg,'cases':cases})
    official=root/'paths'/'official'
    run_child([sys.executable,'-u',str(Path(cfg['root'])/'scripts/memory_s1/integration_reference.py'),
        '--reference-root',str(source_root(cfg,'fastwam')),'--request',str(root/'paths'/'request.pt'),
        '--output',str(official)],cfg,root,official)
    model,device,datasets=setup(cfg);load_weight(model,bound,'step_002000')
    encoders=load_observation_encoders(cfg,device)
    all_reports=[];reference_inputs=[]
    for w in windows:
        check_stop(root); print(f"[paths] {w['id']} raw/cache/online and 8->1->16->8",flush=True)
        request=request_from_raw(cfg,w)
        history_cfg=copy.deepcopy(cfg); history_cfg['history'].update(online_mode='fixed',online_cycle=[],online_phase='fixed',phase=0)
        session=InferenceSession(model,history_cfg,encoders,'full',root/'paths'/w['id'],None,cfg['seed'],trace={})
        dataset=datasets[w['split']]; rows=[]
        # Repeat A after dense/sparse switch, then reset B and reconstruct A from raw.
        outputs=[]
        for period in (8,1,16,8):
            override_online(history_cfg,period=period,phase=0)
            reply=session.decide(request)
            trace=session.trace; sample=sample_for(dataset,w,period,0); batch=collate([sample],device)
            direct=loader_comparison(dataset,record_for(dataset,w),sample)
            comparisons={k:exact(trace['batch'][k],batch[k]) for k in ('latent','proprio','text','text_valid','history','frame_ids','history_valid')}
            noise,_,_=noise_for(cfg,w,device)
            actions,_=model.sample(batch,noise)
            comparisons['normalized_actions']=exact(trace['normalized_actions'],actions[0])
            rows.append({'T':period,'phase':0,'direct_loader':direct,'comparisons':comparisons,
                         'raw_ids':trace['raw_ids'],'encoded_ids':trace['encoded_ids'],'read_ids':trace['batch']['frame_ids'][0].tolist()})
            outputs.append(trace['normalized_actions'].clone())
            if any(not r['exact'] for r in comparisons.values()):
                from .common import atomic_torch
                atomic_torch(root/'paths'/w['id']/'first_divergence.pt',{'online':trace,'cached_batch':{k:v.cpu() for k,v in batch.items()},'cached_actions':actions.cpu()})
                atomic_json(root/'paths'/w['id']/'report.json',{'complete':False,'comparisons':rows})
                raise ValueError(f"First raw/cache/online discrepancy in {w['id']}; tensors preserved.")
        repeat=exact(outputs[0],outputs[-1])
        same=session.decide({**request,'observations':request['observations'][-1:]})
        batched=exact(outputs[0],session.trace['normalized_actions'])
        other=next(candidate for candidate in windows if candidate['task']!=w['task'])
        session.reset(); session.decide(request_from_raw(cfg,other,0)); session.reset()
        final=session.decide(request);reset=exact(outputs[0],session.trace['normalized_actions'])
        if not repeat['exact'] or not reset['exact'] or not batched['exact']:raise ValueError('A/B/A, request batching or T-switch result changed with identical inputs.')
        # Invalid padding should not affect a valid readout/action; future IDs remain rejected.
        batch=collate([sample_for(dataset,w,8,0)],device)
        padded={k:v.clone() for k,v in batch.items()}
        padded['history']=torch.cat([batch['history'],torch.ones_like(batch['history'][:,:1])],1)
        padded['frame_ids']=torch.cat([batch['frame_ids'],torch.full_like(batch['frame_ids'][:,:1],w['anchor']+999)],1)
        padded['history_valid']=torch.cat([batch['history_valid'],torch.zeros_like(batch['history_valid'][:,:1])],1)
        noise,_,_=noise_for(cfg,w,device)
        base,_=model.sample(batch,noise);padding,_=model.sample(padded,noise)
        delta=exact(base,padding)
        # Numerical padding differences are measurements, not relaxed auto-approval.
        value={'window':w['id'],'comparisons':rows,'repeat':repeat,'reset':reset,'request_batching':batched,'padding':delta,'optimizer_updates':0}
        atomic_json(root/'paths'/w['id']/'report.json',value);all_reports.append(value)
        observation=request['observations'][-1]
        reference_inputs.append((w,observation))
        del session,request,batch,padded
    reference=[]
    for index,(w,observation) in enumerate(reference_inputs):
        check_stop(root)
        expected=torch.load(official/f'case_{index:02d}.pt',map_location='cpu',weights_only=True)
        actual=fixture_trace(model,encoders,cfg,cases[index])
        value=compare_trace(actual,expected)
        atomic_json(root/'paths'/w['id']/'official.json',value);reference.append(value)
        if not value['passed']:
            atomic_torch(root/'paths'/w['id']/'first_official_divergence.pt',actual)
            raise ValueError(f"Independent official first divergence: {value['first_divergence']}")
    return {'complete':True,'windows':all_reports,'official_passed':all(r['passed'] for r in reference),
            'padding_exact':all(r['padding']['exact'] for r in all_reports),'optimizer_updates':0}


def gradients(cfg,root,bound):
    from .phase_validation import accumulation_check
    model,device,datasets=setup(cfg);load_weight(model,bound,'step_002000')
    measured=[];reference=None;reports=[]
    # 2x8 repeated once establishes same-path noise before comparing 1x16.
    for index,micro in enumerate((2,2,1)):
        check_stop(root);sink={}
        report=accumulation_check(model,datasets['train'],cfg,device,micro,check_masks=index==0,gradient_sink=sink)
        if reference is None:reference=sink
        else:
            errors={}
            for name,value in reference.items():
                actual=sink[name]; delta=actual-value; ref_norm=value.norm(); current_norm=actual.norm()
                cosine=float(torch.nn.functional.cosine_similarity(value.flatten(),actual.flatten(),dim=0)) if ref_norm>1e-12 and current_norm>1e-12 else None
                errors[name]={'max_abs':float(delta.abs().max()), 'reference_l2':float(ref_norm),
                    'current_l2':float(current_norm),'delta_l2':float(delta.norm()),'cosine':cosine,
                    'relative_l2':float(delta.norm()/(ref_norm+1e-12)),
                    'near_zero_reference':bool(ref_norm<=1e-8)}
            ref_l2=torch.stack([v.square().sum() for v in reference.values()]).sum().sqrt()
            actual_l2=torch.stack([v.square().sum() for v in sink.values()]).sum().sqrt()
            delta_l2=torch.stack([(sink[n]-v).square().sum() for n,v in reference.items()]).sum().sqrt()
            dot=torch.stack([(sink[n]*v).sum() for n,v in reference.items()]).sum()
            errors['_overall']={'reference_l2':float(ref_l2),'current_l2':float(actual_l2),'delta_l2':float(delta_l2),
                                'relative_l2':float(delta_l2/(ref_l2+1e-12)),
                                'cosine':float(dot/(ref_l2*actual_l2)) if ref_l2>1e-12 and actual_l2>1e-12 else None}
            measured.append(errors)
        reports.append(report)
    value={'complete':True,'optimizer_updates':0,'runs':reports,'repeat_noise':measured[0], 'microbatch_delta':measured[1],
           'verdict':'review deltas against repeat noise; no tolerance enlarged automatically'}
    return value


def micro(cfg,root,bound):
    """Explicit optional stage; never overwrites a training checkpoint."""
    from .evaluate import deterministic_noise
    model,device,datasets=setup(cfg);load_weight(model,bound,'step_002000')
    windows=[w for w in read_json(root/'windows.json')['windows'] if w['stage']=='gripper']
    initial={k:v.cpu().clone() for k,v in model.memory.state_dict().items()}
    optimizer=torch.optim.AdamW(model.memory.parameter_groups(),lr=cfg['learning_rate'],betas=(.9,.95))
    history=[]
    for update in range(16):
        check_stop(root);model.train();optimizer.zero_grad(set_to_none=True);total=0.
        for slot,w in enumerate(windows):
            sample=sample_for(datasets[w['split']],w,8,evaluation_phase(cfg,8,w['episode_id']))
            batch=collate([sample],device);noise,tau,_=noise_for(cfg,w,device)
            loss,_=model(batch,noise,tau);(loss/4).backward();total+=float(loss)/4
        if any(p.grad is None or not torch.isfinite(p.grad).all() for p in model.memory.parameters()):raise ValueError('Invalid micro-training gradient.')
        torch.nn.utils.clip_grad_norm_(model.memory.parameters(),1.0,error_if_nonfinite=True);optimizer.step();history.append(total)
        atomic_json(root/'micro_curve.json',{'loss':history,'isolated':True,'not_a_training_checkpoint':True})
    model.memory.load_state_dict(initial,strict=True)
    return {'complete':True,'updates':16,'loss':history,'discarded_parameters':True,'scope':'deliberately includes held-out windows; never use for selection or training resume'}


def run_child(command,cfg,root,directory):
    from .rootcause import run_child as owned_child
    directory.mkdir(parents=True,exist_ok=True)
    atomic_json(root/'active.json',{'directory':str(directory),'command':command})
    environment=dict(os.environ);environment.pop('CUDA_LAUNCH_BLOCKING',None)
    # rootcause helper checks STOP.json. Diagnostic STOP_REQUESTED is propagated by launcher.
    try:
        owned_child(command,directory/'launcher.log',cfg['root'],environment,root,
                    timeout=int(cfg['diagnosis'].get('stage_timeout',7200)))
    except Exception:
        from .selection_runtime import failure_report
        print(failure_report(directory),flush=True)
        raise


def evaluation(cfg,root,bound,stage,args):
    from .posttrain import runtime_options,verify_qualification
    from .fused_evaluation import inherit_scenes,runtime_binding,qualify_fused
    import yaml
    current=copy.deepcopy(cfg); current['closed_loop']['enabled']=True
    current['history']['diagnostic_manifest_sha256']=sha256(root/'windows.json')
    current['selection_runtime']=runtime_options('fused-resident')
    current['selection_runtime']['frozen_scenes']=str(Path(cfg['root'])/cfg['diagnosis']['scenes'])
    current['selection_runtime']['environment']=runtime_binding(current)
    scenes=inherit_scenes(current,root)
    # inherit_scenes returns a path in current versions; always use the emitted immutable bank.
    scenes=root/'frozen_scenes.json'
    qualification=root/'fixed'/'QUALIFICATION.json'
    from types import SimpleNamespace
    if stage=='fixed':
        if cfg['diagnosis'].get('parent'):
            require_stage(root,'offline');require_stage(root,'recorded')
        current['history'].update(online_mode='fixed',online_period=8,online_cycle=[],online_phase='episode_seeded')
        arguments=SimpleNamespace(gpus='0',episode_timeout=cfg['rootcause']['episode_timeout'],phase='qualify',hf_results=False,runtime_profile='fused-resident')
        (root/'fixed').mkdir(exist_ok=True)
        (root/'fixed'/'evaluation_config.yaml').write_text(yaml.safe_dump(current,sort_keys=False))
        atomic_json(root/'active.json',{'directory':str(root/'fixed')})
        qualify_fused(current,Path(cfg['paths']['run']),root/'fixed',
                      {2000:Path(bound['weights']['step_002000']['path'])},arguments)
        return {'complete':True,'scope':'32_target_diagnostic_not_accuracy','qualification':str(qualification)}
    verify_qualification(current,SimpleNamespace(runtime_profile='fused-resident',qualification_report=str(qualification)))
    current['selection_runtime']['qualification_report']=str(qualification)
    current['diagnostic']={'scenes_from':str(scenes),'s1_investigation':True}
    current['history'].update(online_mode='seeded_per_decision' if stage=='random' else 'fixed',online_period=8,online_cycle=[],online_phase='episode_seeded')
    if stage in ('fixed','random','phase_trace'):
        current['diagnostic'].update(episodes_per_task=1,max_targets=160 if stage=='phase_trace' else 32,
                                     record_feedback=True,capture_evidence=True)
        if stage=='phase_trace':
            require_stage(root,'offline');require_stage(root,'recorded');require_stage(root,'contacts')
            current['diagnostic']['phase_trace']=True
        labels=['step_002000'];mode='diagnostic';scope=root/stage
    else:
        if stage=='retest40':require_stage(root,'retest8')
        for prerequisite in ('offline','paths','gradients','expert','fixed','recorded','contacts','phase_trace'):
            require_stage(root,prerequisite)
        if not args.confirmed_fix:
            raise ValueError('Retest requires --confirmed-fix with reviewed reproduction, mechanism, patch and regression evidence.')
        fix=read_json(args.confirmed_fix)
        for key in ('reproduction','first_divergence','mechanism','patch','regression'):
            if not fix.get(key):raise ValueError(f'Missing fix evidence: {key}')
        if fix.get('source')!=bound['source']:
            raise ValueError('Fix review must bind the actual current source inventory.')
        immutable_json(root/'confirmed_fix.json',fix)
        labels=['step_002000','step_001500'];mode='internal';scope=root/'retest'
    config_file=root/f'{stage}_config.yaml'
    # Retest8 and retest40 use an identical configuration; only the claim budget differs.
    if stage.startswith('retest'):config_file=root/'retest_config.yaml'
    content=yaml.safe_dump(current,sort_keys=False)
    if config_file.exists() and config_file.read_text()!=content:raise ValueError('Existing eval configuration differs.')
    config_file.write_text(content)
    for label in labels:
        check_stop(root);directory=scope/label
        command=[sys.executable,'-u','-m','fastwam.memory_s1.eval_parallel','run','--config',str(config_file),
                 '--output',str(directory),'--weights',bound['weights'][label]['path'],'--mode',mode,'--conditions','full',
                 '--gpus','0','--episode-timeout',str(cfg['rootcause']['episode_timeout']),'--resume',*online_arguments(current)]
        if stage=='retest8':command+=['--scene-cap','2']
        run_child(command,current,root,directory)
    if stage=='phase_trace':
        from .diagnosis_followup import trace_summary
        trace_summary(root)
    return {'complete':True,'scope':'full_task_fixed_T8' if stage.startswith('retest') else ('160_target_diagnostic_not_accuracy' if stage=='phase_trace' else '32_target_diagnostic_not_accuracy'),
            'sampling':current['history'],'models':labels,'scene_cap':2 if stage=='retest8' else None}


def expert(cfg,root,bound):
    """Same-scene official expert targets through production, with no scene search."""
    from .rootcause import parallel_group
    from .eval_parallel import gpu_inventory
    current=copy.deepcopy(cfg)
    current['rootcause']['s1_diagnosis']=True
    from .posttrain import runtime_options
    current['selection_runtime']=runtime_options('fused-resident')
    source=Path(cfg['root'])/cfg['diagnosis']['scenes'];saved=read_json(source)
    scenes=[]
    for task in TASKS:
        scene=copy.deepcopy(min((s for s in saved['scenes'] if s['task']==task),key=lambda s:s['ordinal']))
        scene.update(environment='rmbench',root=str(Path(cfg['root'])/cfg['closed_loop']['simulator_root']))
        scenes.append(scene)
    uuids=[gpu_inventory()[0]]
    # No model load: use the existing owned simulator queue for expert operations.
    value=parallel_group(current,root,'expert/reference',scenes,['expert'],'expert',uuids,True,bound)
    from .eval_state import EpisodeQueue
    queue=EpisodeQueue(root/'expert/reference');state=queue.snapshot()
    for job in state['jobs']:
        if job['state']!='complete':raise ValueError('Expert did not complete.')
        directory=queue.root/job['directory']
        if not read_json(directory/'simulator_result.json').get('success'):raise ValueError('Official expert failed; inspect environment before policy rollout.')
        targets=directory/'expert_targets.json'
        if not targets.exists():raise ValueError('Official expert did not record same-scene control targets.')
        scene=next(s for s in scenes if s['task']==job['scene']['task'])
        scene['expert_targets']=str(targets)
    replay=parallel_group(current,root,'expert/production',scenes,['production'],'expert_replay',uuids,True,bound)
    return {'complete':True,'official':value,'production':replay,'interpretation':'compare physical tracking and stages; do not transplant demonstrations between seeds'}


def run_stage(stage,cfg,root,bound,args):
    if stage=='contacts':
        require_stage(root,'expert')
        from .diagnosis_followup import contacts
        return contacts(cfg,root,bound)
    if stage=='recorded':
        require_stage(root,'offline')
        from .diagnosis_followup import recorded
        return recorded(cfg,root,bound)
    if stage in ('offline','paths','gradients','micro'):
        return globals()[stage](cfg,root,bound)
    if stage=='expert':return expert(cfg,root,bound)
    if stage in ('fixed','phase_trace','random','retest8','retest40'):return evaluation(cfg,root,bound,stage,args)
    raise ValueError(stage)
