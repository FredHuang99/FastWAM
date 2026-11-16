#!/usr/bin/env bash
# mwam-a40 (GPU18, 8x A40; 11-16): start the pool5 dispatcher for the A40 lanes once the simulator env passed its gate.
#   checks: the A40 simulator env passed its gate (sim5090.sh SIM_PROFILE=a40, "gate passed"); else NOT READY, exit 1
#   then: deadline 2027-01-05 23:59, POOL_CONFIG free_mib 1000 / free_seconds 60 (user 11-15: the 1-minute rule),
#   lanes a40 + a40cpu, all eight GPUs allowed (a GPU somebody else uses is simply not empty); prints the status
#   docker exec mwam-a40 bash /workspace/FastWAM-memory2/scripts/memory_v2/jobs/a40_start.sh
set -u
R=/workspace/FastWAM-memory2
SIMLOG=/workspace/FastWAM/outputs/fused_environment_a40_sm86/SIM_a40.log
grep -q "gate passed" $SIMLOG 2>/dev/null || { echo "NOT READY: no 'gate passed' in $SIMLOG yet"; tail -n 3 $SIMLOG 2>/dev/null; exit 1; }
cd $R
git -c safe.directory='*' pull -q --ff-only origin memory2 && git -c safe.directory='*' log --oneline -1 | cut -c1-60
Q=$R/outputs/memory_v2/queue5
mkdir -p $Q
echo "2027-01-05 23:59 +0800" > $Q/DEADLINE
/opt/mwam/bin/python - "$Q/POOL_CONFIG.json" <<'PY'
import json, pathlib, sys
p = pathlib.Path(sys.argv[1])
c = json.loads(p.read_text()) if p.exists() else {}
c.update(free_mib=1000, free_seconds=60, share_mib=0)
p.write_text(json.dumps(c, indent=1))
print("POOL_CONFIG", c)
PY
PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/pool5.py start --lanes a40,a40cpu --gpus 0,1,2,3,4,5,6,7 | head -n 24
