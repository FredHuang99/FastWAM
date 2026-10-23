#!/usr/bin/env bash
# Phase 2c queue (single H100, unattended), after the 2x2 verdict "pairs suffice; endpoint not needed":
#   1. B-anchor + pairs  (D's objective, history = initial frame only)  -> is the full archive needed?
#   2. D seed 19, B-full seed 19                                       -> third seed of the main comparison
#   3. B-anchor without pairs (Ours' objective, anchor only)
#   4. content-swap PR for the seed-18 runs; RESULTS_2c.txt
set -u
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
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
log() { echo "[queue] $(date '+%F %T') $*"; }
done_run() { grep -q '"complete": true' "$O/$1/train.log" 2>/dev/null; }

evaluate_run() { local run=$1; shift; log "full eval $run"
  $PY -m fastwam.memory_v2.train_v2 evaluate --config $CFG "$@" \
    --checkpoint $O/$run/checkpoints/update_001340.pt --windows 0 --output $O/$run/eval_full; }
pr_run() { local run=$1 swap=$2; shift 2; log "PR $run swap=$swap"
  $PY -m fastwam.memory_v2.train_v2 pr --config $CFG "$@" --checkpoint $O/$run/checkpoints/update_001340.pt \
    --pairs $PAIRS --limit 300 --swap $swap --set 'eval.modes=["on"]' --output $O/pr/$run; }
train_run() { local run=$1; shift
  if done_run $run; then log "$run already complete"; return; fi
  log "train $run"; $PY -m fastwam.memory_v2.train_v2 train --config $CFG "$@" --set name=$run --set output=$O/$run; }

train_run v2_A_anchor_cf $ANCHOR $PAIRSET
evaluate_run v2_A_anchor_cf $ANCHOR
for swap in all content; do pr_run v2_A_anchor_cf $swap $ANCHOR; done

train_run v2_A_cf_s19 --set seed=19 $PAIRSET
evaluate_run v2_A_cf_s19
pr_run v2_A_cf_s19 all

train_run v2_A_bfull_s19 --set seed=19 $BFULL
evaluate_run v2_A_bfull_s19 $BFULL
pr_run v2_A_bfull_s19 all $BFULL

train_run v2_A_anchor $ANCHOR
evaluate_run v2_A_anchor $ANCHOR
for swap in all content; do pr_run v2_A_anchor $swap $ANCHOR; done

pr_run v2_A_cf_s18 content
pr_run v2_A_bfull_s18 content $BFULL
$PY /workspace/FastWAM-memory2/scripts/memory_v2/show_results.py > $O/RESULTS_2c.txt 2>&1
log "all done -> $O/RESULTS_2c.txt"
