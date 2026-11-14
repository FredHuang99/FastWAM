#!/usr/bin/env bash
# mwam5090, 11-14 evening: count counterfactuals of the ledger (ar2_prop e20, swap 1-50, fixed pipeline). Descriptive.
# Written 11-14 18:30, after ledger-off (swap 97/100 -> 0/50, all "kept moving") and drop1 (no effect: the latest
# entry is almost always a lift / lower, not a grasp) and before these runs:
#   dropfirst (the first completed move erased: one move fewer counted)  expected: "kept moving" >= 30/50, success <= 20/50
#   addmove   (the first completed move entered twice: one move more)    expected: "pressed before s3" >= 20/50, success <= 20/50
#   neither moves the numbers -> the model reads the ledger's presence / recency, not the count of moves
# GPU1 runs dropfirst now; GPU0 runs addmove when day4's last run there ends. Both finish long before ar2_prop e30.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/abl2_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$R/outputs/fullft/ABL2_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[abl2] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
CK=$R/outputs/fullft/exports/ar2_prop_e20/export_e20.pt
echo "[abl2] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[abl2] $(date '+%F %T') GPU $1 claimed"; }
run() {   # GPU, mode
  claim $1
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$1 MWAM_LEDGER=$2 $PY -m fastwam.memory_v2.online run --checkpoint $CK --label ar2_prop_e20_$2 \
      --scenes $O/closed_loop/scenes_seed42_n100_swap_blocks --tasks swap_blocks --limit 50 --execute 8 \
      --output $O/closed_loop/abl >> $O/closed_loop/abl_ar2_prop_e20_$2.log 2>&1
    echo "[abl2] $(date '+%F %T') $2 pass $pass exit code $?"
  done
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/abl --label ar2_prop_e20_$2 --out /dev/null 2>/dev/null | grep -E "^  swap.*/on "
  $PY scripts/fullft/press_gap.py --folder closed_loop/abl --label ar2_prop_e20_$2 2>/dev/null | grep -A4 "^swap"
}
run 1 dropfirst & P1=$!
run 0 addmove & P0=$!
wait $P1 $P0     # never a bare `wait` after `exec > >(tee)`
