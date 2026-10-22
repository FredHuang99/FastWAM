#!/usr/bin/env bash
# Phase 2b queue on the single H100 (runs unattended, in order):
#   1. wait for v2_A_bfull_cf (B-full + pairs, the 2x2 fourth cell) to finish
#   2. its full 401-window eval + PR all/content/clock (on mode)
#   3. D seed 18 (train, full eval, PR all)
#   4. B-full seed 18 (train, full eval, PR all)
#   5. RESULTS_2b.txt
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
log() { echo "[queue] $(date '+%F %T') $*"; }

done_run() { grep -q '"complete": true' "$O/$1/train.log" 2>/dev/null; }

evaluate_run() {   # $1 run, $2.. extra --set flags
  local run=$1; shift
  log "full eval $run"
  $PY -m fastwam.memory_v2.train_v2 evaluate --config $CFG "$@" \
    --checkpoint $O/$run/checkpoints/update_001340.pt --windows 0 --output $O/$run/eval_full
}

pr_run() {         # $1 run, $2 swap, $3.. extra --set flags
  local run=$1 swap=$2; shift 2
  log "PR $run swap=$swap"
  $PY -m fastwam.memory_v2.train_v2 pr --config $CFG "$@" --checkpoint $O/$run/checkpoints/update_001340.pt \
    --pairs $PAIRS --limit 300 --swap $swap --set 'eval.modes=["on"]' --output $O/pr/$run
}

train_run() {      # $1 run, $2.. --set flags
  local run=$1; shift
  if done_run $run; then log "$run already complete"; return; fi
  log "train $run"
  $PY -m fastwam.memory_v2.train_v2 train --config $CFG "$@" --set name=$run --set output=$O/$run
}

log "waiting for v2_A_bfull_cf"
while ! done_run v2_A_bfull_cf; do
  if ! pgrep -f "output=$O/v2_A_bfull_cf" >/dev/null && ! done_run v2_A_bfull_cf; then
    log "v2_A_bfull_cf is not running and not complete: stop (check $O/v2_A_bfull_cf/train.log)"; exit 1
  fi
  sleep 300
done
evaluate_run v2_A_bfull_cf $BFULL
for swap in all content clock; do pr_run v2_A_bfull_cf $swap $BFULL; done

train_run v2_A_cf_s18 --set seed=18 $PAIRSET
evaluate_run v2_A_cf_s18
pr_run v2_A_cf_s18 all

train_run v2_A_bfull_s18 --set seed=18 $BFULL
evaluate_run v2_A_bfull_s18 $BFULL
pr_run v2_A_bfull_s18 all $BFULL

$PY /workspace/FastWAM-memory2/scripts/memory_v2/show_results.py > $O/RESULTS_2b.txt 2>&1
log "all done -> $O/RESULTS_2b.txt"
