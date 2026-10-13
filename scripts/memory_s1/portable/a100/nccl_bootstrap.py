"""A100-only torchrun bootstrap: restore known NCCL policy after Torch imports."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import time
import traceback

from a100_migration import (nccl, nccl_environment_snapshot, nccl_runtime_paths,
                            restore_nccl_runtime, sha, write)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('stage',choices=('nccl','cache'))
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--worker',action='store_true')
    args = parser.parse_args()
    args.root = args.root.resolve()
    if args.stage == 'cache' and args.config is None:
        parser.error('cache requires --config')
    environment,attempt = nccl_runtime_paths(args.root)
    rank = os.environ.get('LOCAL_RANK')
    try:
        if args.worker:
            if args.stage == 'nccl':
                nccl(args)
            else:
                before = nccl_environment_snapshot()
                # Both Torch and the target module import before restoration.
                # dense.main has not run and cannot have constructed a group yet.
                sys.path.insert(0,str(args.root/'src'))
                from fastwam.memory_s1 import dense
                import torch
                torch.cuda.set_device(int(rank))
                restore_nccl_runtime(args.root,'cache_worker',before)
                sys.argv = ['dense','cache','--config',str(args.config)]
                dense.main()
        else:
            before = nccl_environment_snapshot()
            from torch.distributed import run
            runtime_path = restore_nccl_runtime(args.root,'launcher',before)
            command = ['--standalone','--nnodes=1','--nproc_per_node=8',str(Path(__file__).resolve()),
                       args.stage,'--root',str(args.root),'--worker']
            if args.config is not None:
                command += ['--config',str(args.config)]
            command_path = attempt/'torchrun_command.json'
            write(command_path,command)
            run.main(command)
            # Publish only after torchrun has joined every worker successfully.
            # The separate receipt collector must authenticate this evidence,
            # rather than compare its own interpreter's communication defaults.
            write(attempt/'launcher_result.json',{'passed':True,'stage':args.stage,
                  'pid':os.getpid(),'exit_code':0,'returned_normally':True,
                  'environment_sha256':sha(environment),'runtime_evidence_sha256':sha(runtime_path),
                  'command_sha256':sha(command_path),'completed_unix':time.time()})
    except BaseException as error:
        if not isinstance(error,SystemExit) or error.code not in (0,None):
            label = f'rank_{int(rank)}' if args.worker and rank is not None else 'launcher'
            write(attempt/(label+'.error.json'),{'rank':int(rank) if rank is not None else None,
                  'pid':os.getpid(),'stage':args.stage,'created_unix':time.time(),
                  'traceback':traceback.format_exc(),'error':repr(error)})
        raise


if __name__ == '__main__':
    main()
