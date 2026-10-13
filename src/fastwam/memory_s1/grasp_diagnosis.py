"""One visible GPU per worker; paired raw-input paths never use CachedEpisodes."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import numpy as np
import torch
from PIL import Image

from .grasp_bridge import (read, write, sha, files, verify, frozen, load_profile, load_cfg,
                           stop_children, owned_popen, ANCHORS)
from .common import ReleaseNormalizer
from .history import resolve_online, select_ids


def cpu(value):
    if isinstance(value, torch.Tensor): return value.detach().cpu().clone()
    if isinstance(value, dict): return {k:cpu(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [cpu(v) for v in value]
    return value


def summary(value):
    if isinstance(value,torch.Tensor):
        array=value.detach().cpu()
        # A size-one expanded dimension can be "contiguous" with stride zero.
        # Allocate a real flat buffer: byte views require rank >= 1 and stride(-1) == 1.
        packed=torch.empty(array.numel(),dtype=array.dtype,device='cpu')
        packed.copy_(array.reshape(-1))
        raw=packed.view(torch.uint8).numpy().tobytes()
        finite=bool(torch.isfinite(array).all())
        return {'shape':list(array.shape),'dtype':str(array.dtype),'sha256':hashlib.sha256(raw).hexdigest(),
                'min':float(array.min()) if array.numel() and finite else None,
                'max':float(array.max()) if array.numel() and finite else None,
                'finite':finite}
    if isinstance(value,dict): return {k:summary(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [summary(v) for v in value]
    return value


def compare(a,b,path=''):
    rows=[]
    if isinstance(a,torch.Tensor) and isinstance(b,torch.Tensor):
        same=a.shape==b.shape and a.dtype==b.dtype
        exact=same and torch.equal(a,b)
        rows.append({'stage':path,'exact':exact,'left':summary(a),'right':summary(b),
            'max_abs':float((a.float()-b.float()).abs().max()) if a.shape==b.shape and a.numel() else None})
    elif isinstance(a,dict) and isinstance(b,dict):
        for key in sorted(a.keys()|b.keys()):
            if key not in a or key not in b: rows.append({'stage':path+'/'+key,'exact':False,'reason':'missing field'})
            else: rows.extend(compare(a[key],b[key],path+'/'+key))
    elif isinstance(a,(list,tuple)) and isinstance(b,(list,tuple)):
        if len(a)!=len(b): rows.append({'stage':path,'exact':False,'reason':'length'})
        else:
            for i,(x,y) in enumerate(zip(a,b)): rows.extend(compare(x,y,f'{path}/{i}'))
    else: rows.append({'stage':path,'exact':a==b})
    return rows


@contextmanager
def observe_velocity(model, trace):
    original=model.backbone.action_velocity
    trace['denoising']=[]; trace['injection']=[]
    def wrapped(actions,timestep,*args,**kwargs):
        value=original(actions,timestep,*args,**kwargs)
        trace['denoising'].append(cpu({'actions_in':actions,'timestep':timestep,'velocity':value}))
        return value
    model.backbone.action_velocity=wrapped
    def injection(module,args,result):
        delta=result.float()-args[0].float()
        trace['injection'].append({'rms':float(delta.square().mean().sqrt()),'max_abs':float(delta.abs().max())})
    hooks=[m.register_forward_hook(injection) for m in model.memory.injectors.values()]
    try: yield
    finally:
        model.backbone.action_velocity=original
        for hook in hooks: hook.remove()


def request_for(folder, item, observations=None):
    observations=observations or [{'frame_id':item['anchor'],'proprio':item['proprio'],'images':item['images']}]
    rows=[]
    for row in observations:
        arrays=[np.ascontiguousarray(Image.open(folder/name).convert('RGB')) for name in row['images']]
        if row.get('pixels_sha256') and [hashlib.sha256(a.tobytes()).hexdigest() for a in arrays]!=row['pixels_sha256']:
            raise ValueError('Frozen observation pixels differ')
        rows.append({'frame_id':row['frame_id'],'proprio':row['proprio'],
                     'images':[a.tobytes() for a in arrays],'shapes':[list(a.shape) for a in arrays]})
    return {'task':item['task'],'episode_seed':item['seed'],'instruction':item['instruction'],
            'current_id':item['anchor'],'observations':rows}


@torch.no_grad()
def direct(model,encoders,cfg,request,noise):
    """Independently assemble the offline batch from raw frames, then model.sample."""
    from .data import observation_tensor
    from .model import encode_text, encode_latent
    vae,text_encoder,tokenizer=encoders; device=next(model.memory.parameters()).device
    norm=ReleaseNormalizer(cfg['paths']['stats']); trace={}
    sampling=resolve_online(cfg,request['task'],request['episode_seed'],request['current_id'])
    ids=select_ids(range(request['current_id']+1),request['current_id'],sampling['period'],phase=sampling['phase'])
    raw={r['frame_id']:r for r in request['observations']}
    with torch.autocast('cuda',dtype=torch.bfloat16):
        text,text_valid=encode_text(text_encoder,tokenizer,request['instruction'],device)
        features=[]
        for index in ids:
            row=raw[index]
            arrays=[np.frombuffer(a,dtype=np.uint8).reshape(s) for a,s in zip(row['images'],row['shapes'])]
            mosaic=observation_tensor(arrays,device)
            proprio=norm.normalize(torch.tensor(row['proprio'],dtype=torch.float32,device=device)[None],'state')
            latent=encode_latent(vae,mosaic)
            feature,kv,context=model.backbone.encode_observation(latent,text,proprio,keep_kv=index==request['current_id'])
            features.append(feature[0])
        batch={'latent':latent,'text':text,'text_valid':text_valid,'proprio':proprio,
               'history':torch.stack(features)[None],'frame_ids':torch.tensor(ids,device=device)[None],
               'history_valid':torch.ones(1,len(ids),device=device,dtype=torch.bool),
               'actions':torch.zeros(1,32,14,device=device),'action_valid':torch.ones(1,32,device=device,dtype=torch.bool),
               't':torch.tensor([request['current_id']],device=device)}
        trace.update(cpu({'mosaic':mosaic,'latent':latent,'proprio':proprio,'text':text,'feature':feature,
            'kv':kv,'context':context[0],'context_mask':context[1],'batch':batch,'noise':noise.to(device)}))
        with observe_velocity(model,trace): actions,readout=model.sample(batch,noise.to(device))
    denorm=norm.denormalize(actions[0]); clipped=denorm.clone(); clipped[:,[6,13]]=clipped[:,[6,13]].clamp(0,1)
    trace.update(cpu({'readout':readout,'normalized_actions':actions[0],
                     'denormalized_actions':denorm[None],'clipped_actions':clipped}))
    return trace


@torch.no_grad()
def online(model,encoders,cfg,request,noise,directory):
    from .sim_bridge import InferenceSession
    trace={}; directory.mkdir(parents=True,exist_ok=True)
    session=InferenceSession(model,cfg,encoders,'full',directory,None,17,trace=trace)
    with observe_velocity(model,trace): session.decide(request,diagnostic_noise=noise)
    del session
    return trace


def save_trace(directory,name,trace):
    # Scalar/tensor summaries include every layer KV; actual arrays preserve the small decision trace.
    write(directory/f'{name}.json',summary(trace))
    arrays={key:trace[key].float().numpy() for key in ('mosaic','latent','proprio','readout','noise','normalized_actions','denormalized_actions','clipped_actions')
            if isinstance(trace.get(key),torch.Tensor)}
    for i,row in enumerate(trace['denoising']):
        arrays[f'velocity_{i}']=row['velocity'].float().numpy()
        arrays[f'actions_in_{i}']=row['actions_in'].float().numpy()
    np.savez_compressed(directory/f'{name}.npz',**arrays)


def action_metrics(trace,item):
    prediction=trace['denormalized_actions'][0].float().numpy()
    current=np.asarray(item['proprio'],dtype=np.float32)
    out={'left_arm_mean_displacement':float(np.abs(prediction[:16,:6]-current[:6]).mean()),
         'right_arm_mean_displacement':float(np.abs(prediction[:16,7:13]-current[7:13]).mean()),
         'right_wrist':prediction[:,12].tolist(),'grippers':prediction[:,[6,13]].tolist(),
         'clip_count':int(np.count_nonzero(prediction!=trace['clipped_actions'].float().numpy()))}
    if item.get('targets'):
        target=np.asarray(item['targets'],dtype=np.float32); count=min(32,len(target))
        out.update(valid_targets=count,valid_mask=[i<count for i in range(32)],
                   joint_mae=np.abs(prediction[:count]-target[:count]).mean(0).tolist(),
                   first16_mae=np.abs(prediction[:min(16,count)]-target[:min(16,count)]).mean(0).tolist(),
                   hold_mae=np.abs(current-target[:count]).mean(0).tolist(),
                   target_right_wrist=target[:count,12].tolist(), target_grippers=target[:count,[6,13]].tolist())
    return out


def expert_case(root,profile,cfg,folder,bundle,case,directory,gpu,progress):
    from .eval_parallel import simulator_environment
    source=folder/bundle['experts'][case['task']]['path']; expert=read(source)
    scene=dict(expert['scene']); scene.update(root=str(root/'resources/RMBench'),expert_targets=str(source))
    job={'scene':scene,'condition':'production','max_targets':case['cap'],'capture_expert_observations':True}
    write(directory/'job.json',job)
    env=simulator_environment(cfg,gpu)
    env['MEMORY_S1_PROGRESS_ROOT']=str(directory/'simulator_progress')
    if case['cap']==32 and profile['machine']=='a100': env['MEMORY_S1_GRAPH_FRESH_PROBE']='1'
    command=[profile['simulator_python'],'-u',str(root/'scripts/memory_s1/rootcause_sim.py'),
        '--operation','expert_replay','--job',str(directory/'job.json'),'--output',str(directory),
        '--gpu-uuid',gpu,'--max-targets',str(case['cap']),'--executor','upstream_topp']
    write(directory/'command.json',command)
    with (directory/'simulator.log').open('w') as stream:
        child=owned_popen(command,cwd=root/'resources/RMBench',env=env,stdout=stream,stderr=subprocess.STDOUT)
        started=time.monotonic()
        try:
            while child.poll() is None:
                path=directory/'observations.jsonl'
                rows=path.read_text().splitlines() if path.exists() else []
                count=max(0,len(rows)-1)
                elapsed=time.monotonic()-started
                write(progress,{'stage':'expert-replay','gpu':gpu,'case':case['id'],'targets':count,'cap':case['cap'],
                                'elapsed_seconds':elapsed,'eta_seconds':elapsed/count*(case['cap']-count) if count else None})
                if elapsed>profile['case_timeout_seconds']: raise TimeoutError(f'Expert prefix timed out: {directory}')
                time.sleep(5)
            if child.returncode:
                raise RuntimeError((directory/'simulator.log').read_text(errors='replace')[-16000:])
        finally: stop_children([child])
    result=read(directory/'simulator_result.json')
    observations=[json.loads(s) for s in (directory/'observations.jsonl').read_text().splitlines()]
    count=result['executed_targets']
    if not 0<count<=case['cap'] or [r['frame_id'] for r in observations]!=list(range(count+1)):
        raise ValueError('Expert target cap or observation/label alignment failed')
    actions=[json.loads(s) for s in (directory/'executed_actions.jsonl').read_text().splitlines()]
    if len(actions)!=count or [r['completed_target_id'] for r in actions]!=list(range(1,count+1)):
        raise ValueError('Executed target sequence is incomplete')
    if result['physical_summary']['observation_or_rpc_advanced_physics']:
        raise ValueError('Observation advanced physics')
    backend=list((directory/'simulator_progress').glob('fused_backend_*.json'))
    if len(backend)<2 or any(not read(p)['passed'] for p in backend): raise ValueError('Both-arm fused warmup evidence missing')
    if case['cap']==32 and profile['machine']=='a100':
        probes=list((directory/'simulator_progress').glob('fresh_graph_*.json'))
        if len(probes)<2 or any(not read(p)['passed'] for p in probes): raise ValueError('Both-arm fresh graph evidence missing')
    return {'id':case['id'],'passed':True,'task':case['task'],'completed_targets':count,'target_cap':case['cap'],
            'observations':len(observations),'physical_events':result['physical_summary']['events'],
            'prefix_only':True,'success_rate':None,'seconds':result['simulator_seconds']}


def teacher_input(root,profile,folder,bundle,case):
    output=root/profile['output']
    matches=list((output/'expert-observe').glob(f'worker_*/cases/{case["task"]}_*/complete.json'))
    if len(matches)!=1: raise ValueError('Expected one completed expert-observe case per task')
    directory=matches[0].parent; verify(directory,read(matches[0])['files'])
    observations=[json.loads(s) for s in (directory/'observations.jsonl').read_text().splitlines()]
    anchor=case['anchor']
    if len(observations)<=anchor: raise ValueError(f'Expert prefix stopped before requested anchor {anchor}; no automatic extension')
    expert=read(folder/bundle['experts'][case['task']]['path'])
    row=observations[anchor]
    if row['completed_targets']!=anchor or row['next_target_index']!=anchor: raise ValueError('Teacher label off by one')
    item={'task':case['task'],'seed':expert['scene']['seed'],'instruction':expert['scene']['instruction'],
          'anchor':anchor,'proprio':row['proprio'],'targets':expert['targets'][anchor:anchor+32]}
    return item,request_for(directory,item,observations[:anchor+1]),row


def main():
    parser=argparse.ArgumentParser(__doc__); parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--machine',choices=['h100','a100'],required=True); parser.add_argument('--jobs',type=Path,required=True)
    args=parser.parse_args(); root=args.root.resolve(); profile=load_profile(root,args.machine)
    cfg=load_cfg(root,profile); folder,bundle=frozen(root,profile); spec=read(args.jobs)
    worker=args.jobs.parent; progress=worker/'progress.json'; output=root/profile['output']
    signal.signal(signal.SIGTERM,lambda *_: (_ for _ in ()).throw(InterruptedError('Worker terminated')))
    if torch.cuda.device_count()!=1: raise ValueError('Each worker must see exactly one GPU')
    from .eval_state import cuda_gpu_uuid
    if cuda_gpu_uuid(0)!=spec['gpu_uuid']: raise ValueError('Worker GPU UUID differs')
    model=encoders=None; loaded=None
    for number,case in enumerate(spec['jobs'],1):
        if (output/'STOP').exists(): raise InterruptedError('User stopped diagnostic')
        directory=worker/'cases'/case['id']
        if (directory/'complete.json').exists():
            receipt=read(directory/'complete.json')
            if receipt['identity']!=spec['identity'] or receipt['case']!=case: raise ValueError('Existing case identity differs')
            verify(directory,receipt['files']); continue
        if directory.exists():
            saved=worker/'interrupted'/f'{case["id"]}_{time.time_ns()}'
            saved.parent.mkdir(parents=True,exist_ok=True); directory.rename(saved)
        directory.mkdir(parents=True)
        write(progress,{'stage':'start','case':case['id'],'gpu':spec['gpu_uuid'],'completed':number-1,'total':len(spec['jobs'])})
        started=time.monotonic()
        if case['kind']=='expert':
            result=expert_case(root,profile,cfg,folder,bundle,case,directory,spec['gpu_uuid'],progress)
        else:
            if model is None:
                write(progress,{'stage':'model_load','case':case['id'],'gpu':spec['gpu_uuid'],'started_unix':time.time()})
                from .model import S1Model, load_observation_encoders
                from .integration_contract import configure_numerics
                configure_numerics(cfg); device=torch.device('cuda:0')
                model=S1Model(cfg,device).eval(); encoders=load_observation_encoders(cfg,device)
                print(f'[model-load] seconds={time.monotonic()-started:.1f}',flush=True)
            label=f'step_{case["step"]:06d}'
            if loaded!=label:
                from .diagnosis_gpu import load_weight
                load_weight(model,{'weights':{k:{'path':str(root/v['relative']),'sha256':v['sha256']} for k,v in bundle['weights'].items()},
                                   'resources':bundle['resources']},label); loaded=label
            if case['kind']=='teacher': item,request,physical=teacher_input(root,profile,folder,bundle,case)
            else:
                item=bundle['inputs'][case['input']]; request=request_for(folder,item); physical=None
            noise_name=case.get('noise','online')
            noise=torch.from_numpy(np.load(folder/bundle['noise'][item['task']][noise_name]['path'],allow_pickle=False))
            write(progress,{'stage':'sample','case':case['id'],'gpu':spec['gpu_uuid'],'completed':number-1,'total':len(spec['jobs']),
                            'T':8,'anchor':request['current_id'],'started_unix':time.time()})
            value=online(model,encoders,cfg,request,noise,directory/'online')
            save_trace(directory,'online',value)
            result={'id':case['id'],'passed':bool(torch.isfinite(value['clipped_actions']).all()),'step':case['step'],
                    'task':item['task'],'input':case.get('input'),'anchor':item['anchor'],'noise':noise_name,
                    'sampling':value['sampling'],'read_ids':value['batch']['frame_ids'][0].tolist(),
                    'metrics':action_metrics(value,item),'physical_observation':physical,
                    'action_samples':1,'seconds':time.monotonic()-started}
            if case['kind']=='paths':
                other=direct(model,encoders,cfg,request,noise); save_trace(directory,'offline',other)
                order=('mosaic','latent','proprio','text','feature','kv','context','context_mask','batch','readout','noise','denoising','normalized_actions','denormalized_actions','clipped_actions')
                comparisons=[]
                for key in order: comparisons.extend(compare(other[key],value[key],key))
                differing=[r for r in comparisons if not r['exact']]
                write(directory/'comparison.json',{'comparisons':comparisons,'first_divergence':differing[0] if differing else None,
                    'scope':'same GPU, frozen raw input and exact saved noise; no tolerance relaxed'})
                result.update(passed=result['passed'] and not differing,first_divergence=differing[0] if differing else None,action_samples=2)
                if case['step']==2000 and case['input'].endswith('_online_initial'):
                    prior=np.asarray(bundle['h100_recorded'][item['task']]['normalized_actions'],dtype=np.float32)
                    current=value['normalized_actions'].float().numpy()
                    result['historical_h100_difference']={'max_abs':float(np.abs(current-prior).max()),
                        'rms':float(np.square(current-prior).mean()**.5),'bitwise_required':False,
                        'scope':'historical production input/noise; environment differences are not proof of a fix'}
            del value
        write(directory/'result.json',result)
        write(directory/'complete.json',{'identity':spec['identity'],'case':case,
            'files':{n:h for n,h in files(directory).items() if n!='complete.json'}})
        print(f'[case] {case["id"]} passed={result["passed"]} seconds={time.monotonic()-started:.1f}',flush=True)
        write(progress,{'stage':'case_complete','case':case['id'],'gpu':spec['gpu_uuid'],'completed':number,'total':len(spec['jobs'])})


if __name__=='__main__': main()
