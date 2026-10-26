#!/usr/bin/env bash
# queue5 lanes (week plan v3). Tasks: scripts/memory_v2/jobs/queue5_tasks.yaml (re-read before every pick).
#   nohup bash scripts/memory_v2/jobs/queue5.sh loop 1  > /dev/null 2>&1 &     closed loop on container GPU1
#   nohup bash scripts/memory_v2/jobs/queue5.sh train 2 > /dev/null 2>&1 &     training (+ its closed loops) on GPU2
#   nohup bash scripts/memory_v2/jobs/queue5.sh cpu     > /dev/null 2>&1 &     analyses, no GPU
#   bash scripts/memory_v2/jobs/queue5.sh status                               one screen (daily check)
# Logs: outputs/memory_v2/queue5/<lane>.log, per task outputs/memory_v2/queue5/tasks/<id>.log;
# ledger outputs/memory_v2/LEDGER.md; autopsies outputs/memory_v2/autopsy/. Stop: touch outputs/memory_v2/queue5/STOP
# Deadline: QUEUE_DEADLINE (default "2026-10-30 12:00 +0800"); nothing starts after it, running work is interrupted.
set -u
LANE=${1:?lane: loop|train|cpu|status}
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-16} MKL_NUM_THREADS=${MKL_NUM_THREADS:-16}
PY=/opt/mwam/bin/python
Q=/workspace/FastWAM-memory2/outputs/memory_v2/queue5
mkdir -p $Q
if [ "$LANE" = status ]; then
  exec $PY scripts/memory_v2/queue5.py status
fi
GPU=${2:-}
exec >> $Q/$LANE.log 2>&1
echo "[queue5.sh] $(date '+%F %T') lane $LANE GPU ${GPU:-none}; $(git -c safe.directory='*' log --oneline -1)"
if [ -n "$GPU" ]; then
  exec $PY -u scripts/memory_v2/queue5.py run --lane $LANE --gpu $GPU
else
  export CUDA_VISIBLE_DEVICES=""
  exec $PY -u scripts/memory_v2/queue5.py run --lane $LANE
fi
