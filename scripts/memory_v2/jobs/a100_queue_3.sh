#!/usr/bin/env bash
# Phase 3 on the 4-GPU A100 server, one lane per GPU (run each lane with its own CUDA_VISIBLE_DEVICES):
#   A : B-anchor + pairs (history = initial frame only, D objective)  ->  B-anchor (Ours objective)
#   B : D seed 19  ->  D landmark-stride sensitivity (12 / 8 / 48, no retraining)  ->  content PR of D seed 18
#   C : B-full seed 19  ->  content PR of B-full seed 18
#   bash a100_queue_3.sh A|B|C
set -u
LANE=${1:?lane A|B|C}
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
# 128 host cores shared with other users: PyTorch's default (one thread per core) made three lanes fight over
# CPU (load ~170, 80-140 s/update). Cap the CPU threads of each lane.
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-16} MKL_NUM_THREADS=${MKL_NUM_THREADS:-16}
PY=/opt/mwam/bin/python
CFG=configs/memory_v2/train_v2_A.yaml
O=/workspace/FastWAM-memory2/outputs/memory_v2
PAIRS=$O/pairs/pairs_v1.json
VIS=$($PY -c "import json,statistics;p=json.load(open('$PAIRS'))['train'];print(statistics.median(x['visual_distance'] for x in p))")
BFULL=$($PY -c "
import json; o=json.load(open('$O/v2_A_bfull/CONFIG.json'))['config']['memory_v2']['objective']
print(' '.join(f'--set memory_v2.objective.{k}={json.dumps(v)}' for k,v in o.items()))")
PAIRSET="--set pairs.file=$PAIRS --set pairs.weight=0.5 --set pairs.per_update=16 --set pairs.max_visual_distance=$VIS"
ANCHOR="--set memory_v2.history.anchor_frames=1 --set memory_v2.history.recent_frames=0 --set memory_v2.history.landmark_stride=1000000000 --set memory_v2.history.max_frames=1"
log() { echo "[lane $LANE] $(date '+%F %T') $*"; }
done_run() { grep -q '"complete": true' "$O/$1/train.log" 2>/dev/null; }

train_run() { local run=$1; shift
  if done_run $run; then log "$run already complete"; return; fi
  local resume=""; [ -f "$O/$run/checkpoints/LATEST.json" ] && resume="--resume"
  log "train $run $resume"; $PY -m fastwam.memory_v2.train_v2 train --config $CFG "$@" --set name=$run --set output=$O/$run $resume; }
evaluate_run() { local run=$1 out=$2; shift 2
  if [ -f "$O/$run/$out/update_001340.json" ]; then log "eval $run/$out exists"; return; fi
  log "full eval $run -> $out"
  $PY -m fastwam.memory_v2.train_v2 evaluate --config $CFG "$@" \
    --checkpoint $O/$run/checkpoints/update_001340.pt --windows 0 --output $O/$run/$out; }
pr_run() { local run=$1 swap=$2 out=$3; shift 3
  local suffix=""; [ "$swap" != all ] && suffix="_$swap"
  if [ -f "$O/pr/$out/pr_update_001340_val$suffix.json" ]; then log "PR $out $swap exists"; return; fi
  log "PR $run swap=$swap -> pr/$out"
  $PY -m fastwam.memory_v2.train_v2 pr --config $CFG "$@" --checkpoint $O/$run/checkpoints/update_001340.pt \
    --pairs $PAIRS --limit 300 --swap $swap --set 'eval.modes=["on"]' --output $O/pr/$out; }

case "$LANE" in
A)
  train_run v2_A_anchor_cf $ANCHOR $PAIRSET
  evaluate_run v2_A_anchor_cf eval_full $ANCHOR
  for s in all content; do pr_run v2_A_anchor_cf $s v2_A_anchor_cf $ANCHOR; done
  train_run v2_A_anchor $ANCHOR
  evaluate_run v2_A_anchor eval_full $ANCHOR
  for s in all content; do pr_run v2_A_anchor $s v2_A_anchor $ANCHOR; done
  ;;
B)
  train_run v2_A_cf_s19 --set seed=19 $PAIRSET
  evaluate_run v2_A_cf_s19 eval_full
  for s in all content; do pr_run v2_A_cf_s19 $s v2_A_cf_s19; done
  # landmark-stride sensitivity of D (trained with stride 24, cap 48 frames); denser strides lift the cap
  for lm in 12 8 48; do
    H="--set memory_v2.history.landmark_stride=$lm --set memory_v2.history.max_frames=96"
    evaluate_run v2_A_cf eval_full_lm$lm $H
    pr_run v2_A_cf all v2_A_cf_lm$lm $H
  done
  pr_run v2_A_cf_s18 content v2_A_cf_s18
  ;;
C)
  train_run v2_A_bfull_s19 --set seed=19 $BFULL
  evaluate_run v2_A_bfull_s19 eval_full $BFULL
  for s in all content; do pr_run v2_A_bfull_s19 $s v2_A_bfull_s19 $BFULL; done
  pr_run v2_A_bfull_s18 content v2_A_bfull_s18 $BFULL
  ;;
*) echo "unknown lane $LANE"; exit 2 ;;
esac
$PY /workspace/FastWAM-memory2/scripts/memory_v2/show_results.py > $O/RESULTS_3_$LANE.txt 2>&1
log "all done -> $O/RESULTS_3_$LANE.txt"
