"""Bounded grasp investigation and independent machine qualification (no training)."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tarfile
import time
import traceback

HISTORICAL_REVISION = 'c1aaa6dafddc0909cf1d89cacf966eeffbec6b9c'
TASKS = ('put_back_block', 'swap_blocks')
ANCHORS = {'put_back_block': [0, 48, 64, 96], 'swap_blocks': [0, 48, 80, 96]}
STEPS = (1500, 2000)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.partial')
    with temp.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temp.replace(path)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(8*1024**2), b''):
            h.update(block)
    return h.hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def checked_path(root, relative):
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError(f'Unsafe relative path: {relative}')
    return path


def files(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(Path(root).rglob('*'))
            if p.is_file() and not p.is_symlink() and p.name != 'FILES.json'
            and '__pycache__' not in p.parts and not p.name.endswith('.partial')}


def verify(root, mapping):
    for name, expected in mapping.items():
        path = checked_path(root, name)
        actual = sha(path) if path.is_file() else 'MISSING'
        if actual != expected:
            raise ValueError(f'Checksum mismatch: {path}; expected={expected}; actual={actual}')


def process(pid):
    try:
        fields = Path(f'/proc/{int(pid)}/stat').read_text().rsplit(')', 1)[1].split()
        return {'pid': int(pid), 'start_ticks': fields[19], 'state': fields[0]}
    except (OSError, ValueError, IndexError):
        return None


def alive(owner):
    now = process(owner['pid']) if owner else None
    return bool(now and now['state'] != 'Z' and now['start_ticks'] == owner['start_ticks'])


def stop_owned_tree(owner, grace=20):
    """Snapshot descendants, verify PID birth times, terminate only this launch."""
    if not alive(owner): return
    if os.getpgid(owner['pid']) != owner['pid']:
        raise ValueError('Recorded owner is not the launch session leader')
    rows={}
    for path in Path('/proc').iterdir():
        if not path.name.isdigit(): continue
        try:
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            rows[int(path.name)]={'pid':int(path.name),'parent':int(fields[1]),'state':fields[0],'start_ticks':fields[19]}
        except (OSError,ValueError,IndexError): continue
    selected={owner['pid']:owner}
    while True:
        additions={pid:row for pid,row in rows.items() if row['parent'] in selected and pid not in selected}
        if not additions: break
        selected.update(additions)
    for row in reversed(list(selected.values())):
        if alive(row):
            try: os.kill(row['pid'],signal.SIGTERM)
            except ProcessLookupError: pass
    deadline=time.monotonic()+grace
    while time.monotonic()<deadline and any(alive(row) for row in selected.values()): time.sleep(.2)
    for row in reversed(list(selected.values())):
        if alive(row):
            try: os.kill(row['pid'],signal.SIGKILL)
            except ProcessLookupError: pass


def stop_children(children):
    def owned(child):
        current=process(child.pid)
        return hasattr(child,'_bridge_start') and (current is None or current['start_ticks']==child._bridge_start)
    for child in children:
        if owned(child):
            try: os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError: pass
    for child in children:
        try: child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            if owned(child): os.killpg(child.pid, signal.SIGKILL)
            child.wait(timeout=10)
        # A crashed simulator can leave multiprocessing planners in its owned group.
        if owned(child):
            try: os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError: pass


def owned_popen(command, **kwargs):
    child=subprocess.Popen(command,start_new_session=True,**kwargs)
    owner=process(child.pid)
    if owner is not None: child._bridge_start=owner['start_ticks']
    return child


def load_profile(root, machine):
    profile = read(root / f'configs/memory_s1/grasp_{machine}.json')
    if profile['machine'] != machine:
        raise ValueError('Machine profile mismatch')
    return profile


def load_cfg(root, profile):
    from .common import load_config
    cfg = load_config(root / profile['config'])
    cfg['closed_loop']['simulator_python'] = profile['simulator_python']
    cfg['closed_loop']['curobo_backend'] = 'fused_graph_v1'
    cfg['history'].update(online_period=8, online_cycle=[], online_mode='fixed', online_phase='episode_seeded')
    cfg.setdefault('hardware', {}).update(extensions_directory=profile['extensions_directory'],
                                        warmup_lock_directory=profile['output']+'/warmup_locks')
    cfg.setdefault('recovery', {})['cuda_arch'] = profile['cuda_arch']
    return cfg


def frozen(root, profile):
    folder = root / profile['inputs']
    verify(folder, read(folder/'FILES.json'))
    value = read(folder/'FROZEN.json')
    if value['historical_revision'] != HISTORICAL_REVISION:
        raise ValueError('Frozen inputs cite a different historical diagnosis')
    return folder, value


def historical_manifest(old):
    """Authenticate the manifest inside the already-read-back archive; no download."""
    receipt = read(old/'HF_diagnosis.json')
    if receipt.get('revision') != HISTORICAL_REVISION or not receipt.get('readback_verified'):
        raise ValueError(f'Expected verified historical receipt {HISTORICAL_REVISION}: {old}')
    package_id = Path(receipt['package']).parent.name
    folder = old/'packages'/package_id
    archive = folder/'readback'/receipt['package']
    if not archive.exists():
        archive = folder/'posttrain.tar.zst'
    if sha(archive) != receipt['sha256']:
        raise ValueError(f'Historical archive differs from fixed revision: {archive}')
    result = None
    child = subprocess.Popen(['zstd', '-dc', str(archive)], stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=child.stdout, mode='r|') as tar:
            for member in tar:
                if member.name == 'manifest.json' and member.isfile():
                    result = json.load(tar.extractfile(member))
        child.stdout.close()
        if child.wait(timeout=30): raise RuntimeError('Historical archive decompression failed')
    finally:
        if child.poll() is None: child.terminate(); child.wait(timeout=10)
    if result is None: raise ValueError('Historical archive has no authenticated manifest')
    return receipt, result['files']


def freeze(root, profile, output):
    import numpy as np
    import torch
    from PIL import Image
    from .common import seed_for
    from .data import official_decoder, read_episode
    destination = root/profile['inputs']
    if (destination/'FILES.json').exists():
        frozen(root, profile); print('[reuse] Frozen input files verified', flush=True); return
    old = root/profile['historical']
    receipt, manifest = historical_manifest(old)
    def source(relative):
        if relative not in manifest:
            raise ValueError(f'Historical package did not cover required input: {relative}')
        verify(old, {relative: manifest[relative]})
        return old/relative
    bound = read(source('identity.json'))
    windows = read(source('windows.json'))['windows']
    recorded = read(source('recorded/input_manifest.json'))
    cfg = load_cfg(root, profile)
    destination.mkdir(parents=True, exist_ok=True)
    inputs, noise, experts, inherited = {}, {}, {}, {}
    def save_views(key, arrays):
        names = []
        for i, array in enumerate(arrays):
            name = f'images/{key}_{i}.png'; target = destination/name
            target.parent.mkdir(parents=True, exist_ok=True)
            Image.fromarray(np.asarray(array, dtype=np.uint8)).save(target)
            names.append(name)
        return names
    for task in TASKS:
        request = next(r for r in recorded['requests'] if r['task'] == task and r['current_id'] == 0)
        row = request['observations'][0]
        images = []
        for camera, pixel_hash in zip(('head','left','right'), row['pixels_sha256']):
            matches = [n for n in recorded['copies'] if f'/{task}/' in n and n.endswith(f'/{camera}_000000.png')]
            if len(matches) != 1: raise ValueError(f'Ambiguous historical pixels: {task}/{camera}')
            array = np.asarray(Image.open(source(matches[0])).convert('RGB'))
            if hashlib.sha256(array.tobytes()).hexdigest() != pixel_hash:
                raise ValueError(f'Raw RGB identity differs: {matches[0]}')
            images.append(array)
        key = task+'_online_initial'
        inputs[key] = {'task':task, 'seed':request['seed'], 'instruction':request['instruction'],
                       'proprio':row['proprio'], 'images':save_views(key, images), 'anchor':0,
                       'origin':request['input_identity'], 'targets':None}
        previous = read(source(f'recorded/step_002000_{task}_000000.json'))
        noise[task] = {}
        for name, seed in [('online', previous['noise_seed']), ('offline', seed_for(17,0,0,'closed-loop-noise')),
                           ('independent', seed_for(17, task, 0, 'grasp-independent-noise-v1'))]:
            array = torch.randn(1,32,14,generator=torch.Generator(device='cpu').manual_seed(seed)).numpy()
            if name == 'online' and not np.array_equal(array, np.asarray(previous['action_noise'], dtype=np.float32)):
                raise ValueError('Recorded noise cannot be reproduced; do not replace it')
            path = f'noise/{task}_{name}.npy'; (destination/path).parent.mkdir(exist_ok=True)
            np.save(destination/path, array, allow_pickle=False)
            noise[task][name] = {'path':path, 'seed':seed, 'sha256':sha(destination/path)}
        inherited[task] = {'normalized_actions':previous['normalized_actions'],
                           'input_identity':request['input_identity'], 'scope':'historical H100 production T8 initial input'}
        matches = [n for n in manifest if n.startswith('historical/expert/reference/') and f'/{task}/' in n and n.endswith('/expert_targets.json')]
        if len(matches) != 1: raise ValueError(f'Expected exactly one saved expert: {task}')
        expert = read(source(matches[0]))
        result = read(source(str(Path(matches[0]).with_name('simulator_result.json')).replace('\\','/')))
        if result.get('success') is not True or expert['scene']['seed'] != request['seed']:
            raise ValueError(f'Expert success/scene identity missing: {task}')
        name = f'experts/{task}.json'; write(destination/name, expert)
        experts[task] = {'path':name, 'sha256':sha(destination/name), 'source':matches[0]}
    decoder = official_decoder(root/cfg['closed_loop']['simulator_root'])
    for key in ('put_back_block_train_initial', 'swap_blocks_val_initial'):
        window = next(w for w in windows if w['id'] == key)
        record = window['record']; raw = root/record['raw']
        if sha(raw) != record['raw_sha256']: raise ValueError(f'Raw demo changed: {raw}')
        states, targets, camera_paths, *_ = read_episode(raw)
        import h5py
        with h5py.File(raw, 'r') as stream:
            arrays = [decoder(stream[name][0]) for name in camera_paths]
        task = window['task']
        inputs[key] = {'task':task, 'seed':inputs[task+'_online_initial']['seed'], 'anchor':0,
            'instruction':record['instruction'], 'proprio':np.asarray(states[0]).tolist(),
            'images':save_views(key, arrays), 'targets':np.asarray(targets[:32]).tolist(),
            'origin':{'raw':record['raw'], 'sha256':record['raw_sha256'], 'split':window['split']}}
    weights = {}
    for label, item in bound['weights'].items():
        path = Path(cfg['paths']['run'])/'weights'/f'{label}.pt'
        if sha(path) != item['sha256']: raise ValueError(f'Historical weight changed: {path}')
        weights[label] = {'relative':path.relative_to(root).as_posix(), 'sha256':item['sha256']}
    write(destination/'FROZEN.json', {'schema':'grasp-frozen-v1', 'historical_revision':HISTORICAL_REVISION,
        'historical_receipt':receipt, 'historical_manifest_sha256':signature(manifest),
        'inputs':inputs, 'noise':noise, 'experts':experts, 'weights':weights, 'resources':bound['resources'],
        'history':cfg['history'], 'anchors':ANCHORS, 'h100_recorded':inherited,
        'tokenizer_files':{p.relative_to(Path(cfg['paths']['tokenizer'])).as_posix():sha(p)
            for p in Path(cfg['paths']['tokenizer']).rglob('*') if p.is_file() and '.cache' not in p.parts},
        'scope':'immutable inputs and historical references, not new approval'})
    write(destination/'FILES.json', files(destination))
    print('[freeze] 4 inputs, 6 noise tensors, 2 saved experts; no GPU or dense cache used', flush=True)


def current_identity(root, profile, bundle):
    import importlib.metadata
    cfg = load_cfg(root, profile)
    for key, expected in bundle['resources'].items():
        if key in cfg['paths']:
            path=Path(cfg['paths'][key])
            actual=sha(path) if path.is_file() else 'MISSING'
            if actual != expected: raise ValueError(f'Resource differs: {path}; expected={expected}; actual={actual}')
    for row in bundle['weights'].values(): verify(root, {row['relative']:row['sha256']})
    verify(cfg['paths']['tokenizer'],bundle['tokenizer_files'])
    source = {}
    for directory in ('src/fastwam', 'scripts/memory_s1'):
        for p in sorted((root/directory).rglob('*')):
            if p.is_file() and p.suffix in ('.py','.sh','.json'):
                source[p.relative_to(root).as_posix()] = sha(p)
    # Robot/mesh/config identity is separate from the historical host's software.
    from .integration_contract import simulator_sources
    return {'schema':'grasp-runtime-v1', 'profile':profile, 'config':cfg,
        'frozen_sha256':sha(root/profile['inputs']/'FILES.json'), 'source':source,
        'simulator_sources_sha256':simulator_sources(cfg),
        'environment':{d.metadata['Name']:d.version for d in importlib.metadata.distributions() if d.metadata['Name']},
        'driver_gpus':subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,driver_version','--format=csv,noheader'], text=True),
        'simulator_install':sha(root/profile['simulator_receipt']),
        'historical_revision':HISTORICAL_REVISION}


def inventory(profile):
    rows = [r.split(',') for r in subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,name','--format=csv,noheader'], text=True).strip().splitlines()]
    selected = [(int(r[0]),r[1].strip(),r[2].strip()) for r in rows if int(r[0]) in profile['gpus']]
    if len(selected) != len(profile['gpus']) or any(profile['gpu_name'] not in r[2] for r in selected):
        raise ValueError(f'Expected {profile["gpu_name"]} devices {profile["gpus"]}; got {selected}')
    return [r[1] for r in selected]


def receipt(output, stage, identity, *, required=True):
    path = output/'receipts'/f'{stage}.json'
    if not path.exists():
        if required: raise FileNotFoundError(f'Complete prerequisite stage first: {path}')
        return None
    value = read(path)
    if value['identity'] != identity: raise ValueError(f'Stage identity changed; preserve prior output: {path}')
    verify(output, value['files'])
    if not value.get('passed'): raise ValueError(f'Stage has blockers: {path}')
    return value


def jobs_for(stage, bundle, gpus):
    if stage in ('paths','models'):
        return [{'id':f'{key}_{step}', 'kind':'paths', 'input':key, 'step':step,
                 **({'gpu':i} if stage == 'models' else {})}
                for i,(key,step) in enumerate((k,s) for k in bundle['inputs'] for s in STEPS)]
    if stage == 'noise':
        return [{'id':f'{task}_{step}_{name}', 'kind':'noise', 'input':task+'_online_initial', 'step':step,'noise':name}
                for task in TASKS for step in STEPS for name in ('offline','independent')]
    if stage == 'teacher':
        return [{'id':f'{task}_{anchor:03d}_{step}', 'kind':'teacher','task':task,'anchor':anchor,'step':step}
                for task in TASKS for anchor in ANCHORS[task] for step in STEPS]
    if stage in ('expert-observe','planners'):
        return [{'id':f'{task}_{i}', 'kind':'expert', 'task':task, 'cap':128 if stage == 'expert-observe' else 32,
                 **({'gpu':i} if stage == 'planners' else {})}
                for i,task in enumerate(TASKS if stage == 'expert-observe' else [TASKS[i%2] for i in range(len(gpus))])]
    raise ValueError(stage)


def parallel(root, profile, output, stage, identity, bundle):
    gpus = inventory(profile); jobs = jobs_for(stage, bundle, gpus)
    buckets = [[] for _ in gpus]
    for i, job in enumerate(jobs): buckets[job.get('gpu',i%len(gpus))].append(job)
    children, streams, paths = [], [], []
    started = time.monotonic()
    reused = len(list((output/stage).glob('worker_*/cases/*/complete.json')))
    try:
        for index, cases in enumerate(buckets):
            if not cases: continue
            directory = output/stage/f'worker_{index}'
            directory.mkdir(parents=True, exist_ok=True)
            spec = directory/'jobs.json'
            write(spec, {'jobs':cases,'identity':identity,'gpu_uuid':gpus[index], 'stage':stage})
            log = (directory/f'worker_{time.time_ns()}.log').open('w'); streams.append(log); paths.append(Path(log.name))
            env = dict(os.environ); env.pop('CUDA_LAUNCH_BLOCKING',None)
            env.update(CUDA_VISIBLE_DEVICES=gpus[index],PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4')
            command = ['/opt/mwam/bin/python','-u','-m','fastwam.memory_s1.grasp_diagnosis',
                       '--root',str(root),'--machine',profile['machine'],'--jobs',str(spec)]
            children.append(owned_popen(command, env=env, stdout=log, stderr=subprocess.STDOUT))
        while True:
            completed = len(list((output/stage).glob('worker_*/cases/*/complete.json')))
            elapsed = time.monotonic()-started
            newly_completed = max(0, completed-reused)
            eta = (f'{elapsed/newly_completed*(len(jobs)-completed):.0f}s provisional' if newly_completed
                   else ('0s' if completed == len(jobs) else 'unknown; no newly completed case'))
            active = []
            for index in range(len(buckets)):
                path = output/stage/f'worker_{index}/progress.json'
                if path.exists(): active.append((index,read(path)))
            print(f'[{stage}] {completed}/{len(jobs)} elapsed={elapsed:.0f}s ETA={eta}; includes current worker loads, excludes later uploads', flush=True)
            for index,row in active:
                age=row.get('elapsed_seconds', max(0,time.time()-row.get('started_unix',time.time())))
                target=f" targets={row['targets']}/{row['cap']}" if 'targets' in row else ''
                print(f"  GPU{index} {row.get('gpu','?')} | {row.get('stage','?')} | case={row.get('case','?')}{target} | elapsed={age:.0f}s",flush=True)
            failed = [i for i,p in enumerate(children) if p.poll() not in (None,0)]
            if failed:
                for i in failed: print(paths[i].read_text(errors='replace')[-12000:], flush=True)
                raise RuntimeError(f'First worker failure: {paths[failed[0]]}')
            if all(p.poll() is not None for p in children): break
            if (output/'STOP').exists(): raise InterruptedError('User stop requested')
            if elapsed > profile['stage_timeout_seconds']: raise TimeoutError('Bounded stage timeout; no result counted as model failure')
            time.sleep(15)
        results = []
        for path in (output/stage).glob('worker_*/cases/*/complete.json'):
            value = read(path)
            if value['identity'] != identity: raise ValueError(f'Case identity mismatch: {path}')
            verify(path.parent,value['files']); results.append(read(path.parent/'result.json'))
        if len(results) != len(jobs) or len({r['id'] for r in results}) != len(jobs):
            raise ValueError('Missing/duplicate case during merge')
        passed = all(r.get('passed',False) for r in results)
        write(output/f'{stage}.json', {'passed':passed,'cases':results,'elapsed_seconds':time.monotonic()-started,
                                      'optimizer_updates':0,'task_success_rate':None})
        mapping = {p.relative_to(output).as_posix():sha(p) for p in (output/stage).rglob('*') if p.is_file()
                   and p.suffix not in ('.log',) and p.name != 'progress.json' and 'interrupted' not in p.parts}
        mapping[f'{stage}.json'] = sha(output/f'{stage}.json')
        write(output/'receipts'/f'{stage}.json', {'identity':identity,'passed':passed,'files':mapping})
        if not passed: raise ValueError(f'{stage} found blockers; inspect {output/stage}.json; report/backup remain available')
    finally:
        stop_children(children)
        for stream in streams: stream.close()


def report(root, profile, output):
    import csv
    rows = {}
    for stage in ('paths','noise','expert-observe','teacher','planners','models'):
        p = output/f'{stage}.json'
        rows[stage] = read(p) if p.exists() else {'status':'not_run'}
    missing = [s for s in ('paths','noise','expert-observe','teacher') if rows[s].get('status') == 'not_run']
    value = {'historical_revision':HISTORICAL_REVISION, 'machine':profile['machine'], 'stages':rows,
        'missing':missing,'diagnostic_execution_complete':not missing, 'root_cause':'not automatically determined',
        'historical_contact_limitation':'old name-based contact attribution cannot separate same-named objects',
        'units':'native joint radians and normalized gripper units; no inferred Cartesian accuracy',
        'success_rate':None,'next_action':'Review first path divergence, paired noise response and expert-state action errors before any correction/retraining'}
    write(output/'REPORT.json',value)
    columns=['stage','id','step','task','input','anchor','noise','passed','left_arm_mean_displacement','right_arm_mean_displacement','right_wrist_first','right_wrist_mae','valid_targets','first_divergence']
    with (output/'actions.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns); writer.writeheader()
        for stage,record in rows.items():
            for case in record.get('cases',[]):
                row={k:case.get(k) for k in columns}; metric=case.get('metrics',{})
                row.update(stage=stage,left_arm_mean_displacement=metric.get('left_arm_mean_displacement'),
                    right_arm_mean_displacement=metric.get('right_arm_mean_displacement'),
                    right_wrist_first=metric.get('right_wrist',[None])[0],
                    right_wrist_mae=metric.get('joint_mae',[None]*14)[12],valid_targets=metric.get('valid_targets'),
                    first_divergence=json.dumps(case.get('first_divergence'),ensure_ascii=False))
                writer.writerow(row)
    print(json.dumps({k:v for k,v in value.items() if k!='stages'},indent=2),flush=True)


def backup(root, profile, output):
    """Include all checksummed small observations/traces; no silent suffix filtering."""
    from huggingface_hub import HfApi, hf_hub_download
    os.environ['HF_HUB_OFFLINE']='0'
    package = output/'packages'/str(time.time_ns()); package.mkdir(parents=True)
    archive = package/'grasp.tar.gz'
    frozen_root,_ = frozen(root,profile)
    if frozen_root != output/'frozen':
        for name in ('FROZEN.json','FILES.json', *read(frozen_root/'FILES.json')):
            target=package/'frozen'/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(frozen_root/name,target)
    source_root=package/'source'
    for folder in ('src/fastwam/memory_s1','scripts/memory_s1','configs/memory_s1'):
        for path in (root/folder).rglob('*'):
            if path.is_file() and path.suffix in ('.py','.sh','.yaml','.json'):
                target=source_root/path.relative_to(root); target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)
    selected = [p for p in output.rglob('*') if p.is_file() and not p.is_symlink()
                and not set(p.relative_to(output).parts)&{'packages','interrupted','__pycache__'}
                and p.name not in ('job.lock','STOP','LAUNCH.json','latest_log.txt')]
    manifest = {p.relative_to(output).as_posix():sha(p) for p in selected}
    for directory in (source_root,package/'frozen'):
        if directory.exists():
            manifest.update({p.relative_to(package).as_posix():sha(p) for p in directory.rglob('*') if p.is_file()})
    write(package/'FILES.json',manifest)
    with tarfile.open(archive,'w:gz') as tar:
        for path in selected: tar.add(path, arcname=path.relative_to(output).as_posix(),recursive=False)
        tar.add(package/'FILES.json',arcname='BACKUP_FILES.json',recursive=False)
        for directory in (source_root,package/'frozen'):
            if directory.exists():
                for path in directory.rglob('*'):
                    if path.is_file(): tar.add(path,arcname=path.relative_to(package).as_posix(),recursive=False)
    helper_path = root/'scripts/memory_s1/hf_tools.py'
    spec=importlib.util.spec_from_file_location('grasp_hf_tools',helper_path); helper=importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
    api=HfApi(); repo='hhyfred/fastwam-memory-s1-backup'
    if not api.repo_info(repo).private: raise ValueError('Evidence repository must be private')
    helper.check_budget(api,archive.stat().st_size,100_000_000_000/2**30,10)
    remote=f'grasp/{profile["machine"]}/{package.name}/grasp.tar.gz'
    uploaded=api.upload_file(repo_id=repo,path_in_repo=remote,path_or_fileobj=str(archive))
    recovered=hf_hub_download(repo,remote,revision=uploaded.oid,local_dir=package/'readback')
    if sha(recovered)!=sha(archive): raise ValueError('Backup readback mismatch')
    receipt={'repo':repo,'revision':uploaded.oid,'package':remote,'sha256':sha(archive),'readback_verified':True}
    write(output/'HF_grasp.json',receipt)
    print('[backup] '+json.dumps(receipt),flush=True)


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('stage',choices=['freeze','export-migration','paths','noise','expert-observe','teacher','planners','models','report','backup','status','stop'])
    parser.add_argument('--root',type=Path,default=Path('/workspace/FastWAM'))
    parser.add_argument('--machine',choices=['h100','a100'],required=True)
    parser.add_argument('--resume',action='store_true')
    args=parser.parse_args(); root=args.root.resolve(); profile=load_profile(root,args.machine); output=root/profile['output']
    if args.stage in ('planners','models') and args.machine!='a100':
        raise ValueError('Eight-device qualification is A100-only; H100 uses paths/expert-observe')
    if args.stage=='export-migration' and args.machine!='h100':
        raise ValueError('Only H100 exports the authoritative migration bundle')
    output.mkdir(parents=True,exist_ok=True)
    if args.stage=='status':
        p=output/'LAUNCH.json'; value=read(p) if p.exists() else {}
        value['running']=alive(value.get('owner')); value['stop']=(output/'STOP').exists()
        value['receipts']=[p.stem for p in (output/'receipts').glob('*.json')]
        value['stage_status']=read(output/'stage_status.json') if (output/'stage_status.json').exists() else None
        print(json.dumps(value,indent=2)); return
    if args.stage=='stop':
        value=read(output/'LAUNCH.json') if (output/'LAUNCH.json').exists() else {}
        write(output/'STOP',{'time':time.time(),'scope':'this diagnostic only'})
        owner=value.get('owner')
        stop_owned_tree(owner)
        print('Stop requested; resume requires an explicit resume command.'); return
    signal.signal(signal.SIGTERM,lambda *_: (_ for _ in ()).throw(InterruptedError('User terminated diagnostic')))
    signal.signal(signal.SIGINT,lambda *_: (_ for _ in ()).throw(InterruptedError('User interrupted diagnostic')))
    if (output/'STOP').exists():
        if not args.resume: raise ValueError('STOP present; use resume STAGE explicitly')
        (output/'STOP').rename(output/f'STOP.resumed_{time.time_ns()}')
    write(output/'LAUNCH.json',{'owner':process(os.getpgrp()),'worker':process(os.getpid()),'stage':args.stage,'argv':sys.argv,'started':time.time()})
    started=time.monotonic()
    try:
        if args.stage=='freeze':
            if args.machine!='h100': raise ValueError('A100 must fetch the verified H100 frozen inputs')
            freeze(root,profile,output)
        elif args.stage=='export-migration':
            folder,_=frozen(root,profile)
            subprocess.run(['/opt/hf-tools/bin/python','-u',str(root/'scripts/memory_s1/portable/a100/a100_migration.py'),
                'export','--root',str(root),'--diagnosis',str(root/profile['historical']),'--frozen',str(folder)],check=True)
        elif args.stage=='report': report(root,profile,output)
        elif args.stage=='backup': backup(root,profile,output)
        else:
            if args.machine=='a100' and args.stage not in ('planners','models'):
                ready=root/'outputs/recovery_aws_a100_v1/A100_DIAGNOSIS_READY.json'
                if not ready.exists() or not read(ready).get('ready'):
                    raise ValueError('Complete the independent A100 qualification and recovery report first')
            _,bundle=frozen(root,profile)
            bound=current_identity(root,profile,bundle); identity=signature(bound)
            previous=output/'CURRENT.json'
            if previous.exists() and read(previous)!=bound: raise ValueError('Current runtime changed; use a new independent output profile')
            write(previous,bound)
            if receipt(output,args.stage,identity,required=False): print('[reuse] Stage receipt and artifacts verified'); return
            prerequisites={'noise':['paths'],'expert-observe':['paths'],'teacher':['paths','expert-observe']}
            for stage in prerequisites.get(args.stage,[]): receipt(output,stage,identity)
            parallel(root,profile,output,args.stage,identity,bundle)
        write(output/'stage_status.json',{'stage':args.stage,'state':'complete','seconds':time.monotonic()-started})
    except BaseException as error:
        write(output/'stage_status.json',{'stage':args.stage,'state':'interrupted' if isinstance(error,InterruptedError) else 'error',
            'error':repr(error),'traceback':traceback.format_exc(),'seconds':time.monotonic()-started})
        raise


if __name__=='__main__': main()
