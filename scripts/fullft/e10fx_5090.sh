#!/usr/bin/env bash
# mwam5090, 11-13 evening (descriptive): N7 e10 again, now with the fixed pipeline (OIDN 2.0.1 + training-cache text),
# official scenes 1-50 of both tasks, label ar_2task_e10_fx (closed_loop/g1). Why: the 11-14 morning comparison
# ar2_prop e10 vs N7 e10 on the 5090 must use ONE pipeline (N7 e10 ran on 11-11/12 with OIDN 2.3.3 and CPU T5).
# put on GPU0, swap on GPU1 (each waits for its GPU to be empty for 90 s; GPU1 runs the D2 probe first). Ends ~20:30,
# before ar2_prop e10 (~00:50, eval_watch RUN=ar2_prop takes both GPUs then).
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/e10fx_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$R/outputs/fullft/E10FX_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[e10fx] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
CK=$R/outputs/fullft/exports/ar_2task_e10/export_e10.pt
L=ar_2task_e10_fx
[ -f $CK ] || { echo "missing $CK"; exit 1; }
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
lane() {   # GPU, task
  until empty $1 && sleep 90 && empty $1; do sleep 120; done
  echo "[e10fx] $(date '+%F %T') $2 on GPU $1"
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$1 $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L \
      --scenes $O/closed_loop/scenes_seed42_n100_$2 --tasks $2 --limit 50 --execute 8 --output $O/closed_loop/g1 \
      >> $O/closed_loop/g1_$L.log 2>&1
    echo "[e10fx] $(date '+%F %T') $2 pass $pass exit code $?; finished $(ls $O/closed_loop/g1/$L/on/$2/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
  done
}
lane 0 put_back_block & P0=$!
lane 1 swap_blocks & P1=$!
wait $P0 $P1      # never a bare `wait` after `exec > >(tee)`
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label $L --out /dev/null 2>/dev/null | grep -E "/on |n=" | head -n 4
