"""Read identities and request boundary stops; never kill an arbitrary PID."""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'src'))
from fastwam.memory_s1.common import atomic_json,load_config,read_json
from fastwam.memory_s1.eval_state import is_alive,process_identity


def status(root):
    for path in (root/'launch.json',root/'owner.json'):
        if path.exists():
            value=read_json(path)
            print(f'{path.name}: running={is_alive(value.get("owner"))} stage={value.get("stage","-")} log={value.get("log","-")}')
    for path in sorted(root.glob('*.error.json')):
        print(f'ERROR: {path}')
    active=root/'active.json'
    if active.exists():
        directory=Path(read_json(active)['directory'])
        print(f'Child: {directory}')
        for name in ('status.json','progress.json'):
            if (directory/name).exists():print(json.dumps(read_json(directory/name),ensure_ascii=False))
    latest=root/'latest_log.txt'
    if latest.exists():
        log=Path(latest.read_text().strip());end=log.with_suffix('.exit')
        print('Exit:',end.read_text().strip() if end.exists() else 'pending')
        if log.exists():print('\n'.join(log.read_text(errors='replace').splitlines()[-8:]))


def stop(root):
    root.mkdir(parents=True,exist_ok=True)
    (root/'STOP_REQUESTED').touch()
    atomic_json(root/'STOP.json',{'mode':'now','time':time.time(),'reason':'explicit diagnostic stop'})
    # Only these recorded evaluation directories are affected. No process enumeration or pkill.
    for path in list(root.rglob('queue.json'))+list(root.rglob('active.json')):
        if 'packages' in path.relative_to(root).parts:continue
        destination=Path(read_json(path)['directory']) if path.name=='active.json' else path.parent
        if not destination.resolve().is_relative_to(root.resolve()):
            raise ValueError(f'Refuse stop outside diagnostic root: {destination}')
        atomic_json(destination/'STOP.json',{'mode':'now','time':time.time(),'reason':'explicit diagnostic stop'})
    print('Stop requested. Wait for the recorded exit code before updating code or starting another stage.')


def main():
    p=argparse.ArgumentParser(__doc__);p.add_argument('action',choices=('status','stop','stop-old','idle','register'))
    p.add_argument('--root',required=True);p.add_argument('--config',required=True)
    p.add_argument('--pid',type=int);p.add_argument('--log');a=p.parse_args();root=Path(a.root).resolve()
    if a.action=='status':status(root)
    elif a.action=='stop':stop(root)
    elif a.action=='stop-old':
        cfg=load_config(a.config);old=Path(cfg['root'])/cfg['diagnosis']['old_evaluation']
        if not old.exists():raise FileNotFoundError(old)
        status(old);stop(old)
    elif a.action=='register':
        atomic_json(root/'launch.json',{'owner':process_identity(a.pid),'log':a.log,'time':time.time()})
    elif a.action=='idle':
        for path in (root/'launch.json',root/'owner.json'):
            if path.exists() and is_alive(read_json(path).get('owner')):raise RuntimeError(f'Diagnostic still active: {path}')
        for path in root.rglob('*owner.json'):
            if 'packages' in path.relative_to(root).parts:continue
            value=read_json(path);owner=value.get('owner',value)
            if is_alive(owner):raise RuntimeError(f'Child still active: {path}')
        print('No recorded diagnostic process is active.')


if __name__=='__main__':main()
