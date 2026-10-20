#!/usr/bin/env bash
# GPU A: PR on matched-present pairs for the start model, Ours, B-full, noabs; full 401-window eval of
# noabs; then the capacity-only control B0 (memory_dropout=1: history never seen in training).
# Run from /workspace/FastWAM-memory2 with CUDA_VISIBLE_DEVICES set. Each step logs to stdout.
set -u
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
PY=/opt/mwam/bin/python
CFG=configs/memory_v2/train_v2_A.yaml
PAIRS=/workspace/FastWAM-memory2/outputs/memory_v2/pairs/pairs_v1.json
O=/workspace/FastWAM-memory2/outputs/memory_v2
N=${PR_PAIRS:-300}

echo "[gpu-a] $(date) PR start model"
$PY -m fastwam.memory_v2.train_v2 pr --config $CFG --checkpoint init --pairs $PAIRS --limit $N \
  --set 'eval.modes=["off"]' --output $O/pr/start
for run in v2_A_memory_only v2_A_bfull v2_A_noabs; do
  echo "[gpu-a] $(date) PR $run"
  extra=""
  [ "$run" = v2_A_noabs ] && extra="--set memory_v2.memory.absolute_time=false"
  $PY -m fastwam.memory_v2.train_v2 pr --config $CFG $extra \
    --checkpoint $O/$run/checkpoints/update_001340.pt --pairs $PAIRS --limit $N --output $O/pr/$run
done
echo "[gpu-a] $(date) full eval noabs"
$PY -m fastwam.memory_v2.train_v2 evaluate --config $CFG --set memory_v2.memory.absolute_time=false \
  --checkpoint $O/v2_A_noabs/checkpoints/update_001340.pt --windows 0 --output $O/v2_A_noabs/eval_full
echo "[gpu-a] $(date) train B0 (capacity-only control)"
$PY -m fastwam.memory_v2.train_v2 train --config $CFG \
  --set name=v2_A_b0 --set output=$O/v2_A_b0 --set memory_v2.objective.memory_dropout=1.0
echo "[gpu-a] $(date) all done"
