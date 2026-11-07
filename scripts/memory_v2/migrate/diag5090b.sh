#!/usr/bin/env bash
# mwam5090 container (11-08 00:xx), step 2 of the 5090 online diagnosis. diag5090.sh found: same scene (4300030), same
# weights, same CPU-seeded noise, but the 5090's first executed chunk = the A100's delayed by two targets (arm RMSE
# 0.0054 at lag 2, 0.040 at lag 0); 5090 T5 (CPU and GPU) vs the H100 cache 2.3-3.1 %, VAE 0.4 %.
#   1 the same scene's frame-0 request dumped (online.py run --dump-first, 8 targets) and its first executed row in full
#     (robot state, object poses: compare with the A100's row of the same scene)
#   2 first_decision.py: that request replayed with the instruction encoded on the CPU (must reproduce step 1), on the
#     GPU, and taken from the dense cache (H100); each vs the A100's first 8 targets at lags 0-3
# Uses GPU 0 only (keep it out of the pool's allowed GPUs). Read-only for the queue.
# Own log: /workspace/FastWAM-memory2/outputs/memory_v2/report/DIAG5090B_<time>.txt
#   bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/diag5090b.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/DIAG5090B_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[diag5090b] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[diag5090b] $(date '+%F %T') ===== $*"; }
cd "$R"
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=0
PY=/opt/mwam/bin/python
SEED=4300030
EP=$O/closed_loop/check5090b/x7_first5090b/on/put_back_block/seed_$SEED
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader

step "1 frame-0 request of put_back seed $SEED (X7, 10 steps, 8 targets)"
if [ ! -f "$EP/request_000000.pkl" ]; then
  $PY -m fastwam.memory_v2.online run --checkpoint $O/a2C_6ep/checkpoints/update_004020.pt --label x7_first5090b \
    --scenes $O/closed_loop/scenes_seed42_n100_put_back_block --tasks put_back_block --seeds put_back_block:$SEED \
    --execute 8 --max-targets 8 --dump-first --output $O/closed_loop/check5090b > $O/closed_loop/check5090b_run.log 2>&1
  echo "run exit code $?"
fi
ls -la "$EP/request_000000.pkl" || { echo "no request dumped; last lines of the run log:"; tail -n 20 $O/closed_loop/check5090b_run.log; exit 1; }
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/check5090b --label x7_first5090b --first put_back_block:$SEED \
  --first-full put_back_block:$SEED --out /dev/null | sed -n '/== first targets/,$p'

step "2 replay frame 0 with three text encodings vs the A100's first 8 targets"
$PY scripts/memory_v2/migrate/first_decision.py --request "$EP/request_000000.pkl" \
  --ref scripts/memory_v2/migrate/ref_a100_put_4300030.json --replayed "$EP/executed_actions.jsonl"
