"""Host-only allowlisted Docker identity capture; excludes container environment/secrets."""
import argparse
import json
import os
from pathlib import Path
import platform
import subprocess
import time


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--container', choices=['mwam','mwam-a100'], default='mwam')
    args=parser.parse_args()
    command=['docker'] if os.geteuid()==0 else ['sudo','-n','docker']
    info=json.loads(subprocess.check_output(command+['inspect',args.container],text=True))[0]
    image=json.loads(subprocess.check_output(command+['image','inspect',info['Image']],text=True))[0]
    repositories=[m for m in info['Mounts'] if m['Destination']=='/workspace/FastWAM']
    if len(repositories)!=1 or repositories[0]['Type']!='bind' or not info['State']['Running']:
        raise ValueError('Expected a running container with one project bind at /workspace/FastWAM')
    if not image.get('RepoDigests'): raise ValueError('Image has no immutable registry digest')
    root=Path(repositories[0]['Source']).resolve()
    folder='recovery_aws_h100' if args.container=='mwam' else 'recovery_aws_a100_v1'
    output=root/'outputs'/folder/'container-host.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    if output.exists(): output.rename(output.with_name(f'container-host.previous_{time.time_ns()}.json'))
    value={'container':args.container,'captured_unix':time.time(),'container_id':info['Id'],'name':info['Name'],
           'image_id':info['Image'],'image_reference':info['Config']['Image'],'repo_digests':image['RepoDigests'],
           'mounts':[{k:m.get(k) for k in ('Type','Source','Destination','RW')} for m in info['Mounts']],
           'host_os':platform.platform(),'host_kernel':platform.release(),
           'runtime':{key:info['HostConfig'].get(key) for key in ('IpcMode','NetworkMode','Ulimits','DeviceRequests','ShmSize')},
           'lease_start':'See existing lease.json; capture time is not the rental start.'}
    temp=output.with_suffix('.partial'); temp.write_text(json.dumps(value,indent=2)+'\n'); temp.replace(output)
    print(output)


if __name__=='__main__': main()
