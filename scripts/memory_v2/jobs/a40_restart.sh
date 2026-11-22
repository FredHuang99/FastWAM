#!/usr/bin/env bash
# A40 HOST (outside the container), 11-22 (Opus). Since about 11-22 06:50 nvidia-smi inside mwam-a40 fails ("Failed to
# initialize NVML: Unknown Error", results-a40 snapshot 10:19); the pool5 dispatcher is alive but sees no GPU, so no
# A40 task has started since. The same fix as 11-20: restart the container, then start what ran inside it.
#   1 on the host: nvidia-smi works (else stop: the host itself needs attention)
#   2 docker restart mwam-a40; inside: nvidia-smi must list the GPUs (else stop)
#   3 inside: the timer pull (auto_pull.sh start), the results snapshot to results-a40 (results_push.sh start), the
#     pool5 dispatcher for the a40 lanes (a40_start.sh: deadline, pool config, all eight GPUs; tasks left half-done
#     resume, finished episodes are skipped)
#   4 prints the pool status
# Touches nothing else (other users' processes are outside this container).
#   bash -c "$(docker exec mwam-a40 cat /workspace/FastWAM-memory2/scripts/memory_v2/jobs/a40_restart.sh)"
set -u
C=mwam-a40
R=/workspace/FastWAM-memory2
say() { echo "[a40] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
inside() { docker exec $C bash -c "$1"; }
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader > /dev/null 2>&1 || { say "nvidia-smi fails on the HOST: stop (nothing restarted)"; exit 1; }
say "host GPUs:"; nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
say "restarting $C"
docker restart $C > /dev/null || { say "docker restart FAILED"; exit 1; }
sleep 20
inside "nvidia-smi --query-gpu=index,memory.used --format=csv,noheader" || { say "nvidia-smi still fails inside $C: stop (nothing started)"; exit 1; }
inside "bash $R/scripts/fullft/auto_pull.sh start"
inside "bash $R/scripts/fullft/results_push.sh start"
inside "bash $R/scripts/memory_v2/jobs/a40_start.sh"
say "done; status in 2 min:"
sleep 120
inside "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/pool5.py status" | head -n 30
