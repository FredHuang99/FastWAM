#!/usr/bin/env bash
# mwam5090 container (11-12, DESCRIPTIVE, no verdict; filler until the e20 export): execution length on the new base.
# N7 epoch e10, official scenes 1-N of one task, execute 4 and 16 (the official protocol and every other run: 8).
# Why: the e10 screening fails swap mostly by running out of the target limit after the three moves (s3 13/20, pressed
# 4/20, 48/50 timeouts); on the old base execution length was a strong dose (24 / 12 / 8 -> put success 0 / 1 / 3).
# Expectation written before running: put: execute 4 within -0.05 progress of execute 8. swap: if the stall is
# re-planning hesitation, execute 16 raises "pressed" and success; if it is a decision ("done -> press") problem,
# execution length leaves "pressed" unchanged.
# Each execute value is paired with execute 8 (closed_loop/g1, label ar_2task_e10, same scenes) by pair_eq --rule report.
#   docker exec -d -e GPU=0 -e TASK=put_back_block mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/execlen_5090.sh
#   docker exec -d -e GPU=1 -e TASK=swap_blocks    mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/execlen_5090.sh
# Env: EXECS ("4 16"), N (50), RUN (ar_2task), TAG (e10). Own log: outputs/fullft/EXECLEN_<task>_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
GPU=${GPU:-0}; TASK=${TASK:?}; EXECS=${EXECS:-"4 16"}; N=${N:-50}; RUN=${RUN:-ar_2task}; TAG=${TAG:-e10}
LOG=$R/outputs/fullft/EXECLEN_${TASK}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[execlen] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
CK=$R/outputs/fullft/exports/${RUN}_${TAG}/export_${TAG}.pt
[ -f "$CK" ] || { echo "no export $CK: stopping"; exit 1; }
for x in $EXECS; do
  L=${RUN}_${TAG}_x$x
  echo; echo "[execlen] $(date '+%F %T') ===== $TASK, execute $x, scenes 1-$N"
  for pass in 1 2; do
    $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L --scenes $O/closed_loop/scenes_seed42_n100_$TASK \
      --tasks $TASK --limit $N --execute $x --output $O/closed_loop/execlen >> $O/closed_loop/execlen_$L.log 2>&1
    echo "pass $pass exit code $?; finished $(ls $O/closed_loop/execlen/$L/on/$TASK/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
  done
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/execlen --label $L --out /dev/null | grep -E "/on |n=" | tail -n 2
  $PY scripts/fullft/pair_eq.py --name execlen_${TASK}_x$x --rule report --tasks $TASK \
    --a-folders closed_loop/execlen --a-label $L --b-folders closed_loop/g1 --b-label ${RUN}_${TAG} 2>&1 | tail -n 3
done
