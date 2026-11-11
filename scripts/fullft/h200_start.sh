#!/usr/bin/env bash
# mwam2 container (H200 GPU0, plan v10 N5 -> N7, 11-11): full fine-tuning, first the smoke test, then the two-task
# base run with history "ar" (anchor + t-16 + t-32), 30 frame-epochs, lr 1e-4, 64 samples / update.
#   N5 smoke (pre-registered, train.py): 2 episodes (1 per task), 200 updates: gate-0 history == none exactly,
#      peak memory <= 135 GiB, fixed-noise action loss down >= 80 %. FAIL -> stop here (nothing else starts).
#   N7 train: configs/fullft/base_2task.yaml; resumable (re-running this script resumes from resume.pt);
#      exports at frame-epochs 10 / 20 / 30 -> outputs/fullft/ar_2task/export_e*.pt (the G1 closed loop loads them).
# GPU ${GPU:-0} must have < 2000 MiB in use. Own log: outputs/fullft/H200_START_<time>.txt (the trainer also writes
# outputs/fullft/<run>/logs/*.txt and metrics.jsonl).
#   docker exec -d mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/h200_start.sh
set -u
R=/workspace/FastWAM-memory2
OUT=$R/outputs/fullft
mkdir -p $OUT
LOG=$OUT/H200_START_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[h200] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "[h200] $(date '+%F %T') GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping (free it first)"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
PY=/opt/mwam/bin/python
if [ ! -f $OUT/smoke_ar/SMOKE.json ] || ! grep -q '"pass": true' $OUT/smoke_ar/SMOKE.json; then
  echo "[h200] $(date '+%F %T') ===== N5 smoke (200 updates on 2 episodes)"
  $PY -m fastwam.fullft.train smoke --config configs/fullft/base_2task.yaml --set name=smoke_ar --updates 200
  rc=$?
  echo "[h200] smoke exit code $rc"
  [ $rc -eq 0 ] || { echo "[h200] SMOKE FAILED: nothing else starts; send outputs/fullft/smoke_ar/logs/"; exit 1; }
fi
echo "[h200] $(date '+%F %T') ===== N7 train ar_2task"
$PY -m fastwam.fullft.train train --config configs/fullft/base_2task.yaml --set name=ar_2task
echo "[h200] train exit code $?"
