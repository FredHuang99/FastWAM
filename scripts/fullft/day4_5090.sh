#!/usr/bin/env bash
# mwam5090, 11-14 (descriptive, no verdict; the registered verdict is the A100's at e30). Fixed pipeline.
# Each lane starts when eval_watch's ar2_prop e20 run on ITS GPU has 50 episodes (GPU1 put, GPU0 swap), then 90 s empty.
#   C  ar2_prop e20 on scenes 51-100 (the ledger's 100-scene curve next to AR's)
#   A  test-time ledger ablations of ar2_prop e20 (mechanism; written 11-14 13:50 before any run):
#      off   (MWAM_LEDGER=off: no ledger entry ever)        expected: swap falls toward AR-like "kept moving";
#                                                             put falls toward "press skipped"
#      drop1 (MWAM_LEDGER=drop1: the latest event withheld)  expected: more "kept moving" / later press on swap
#      If neither moves the numbers, the gain does not come from reading the ledger (e.g. training side effects).
#   R  noise replicate r1 of ar2_prop e20 swap 1-100 (its run-to-run spread, next to AR's +-3 of 100)
#   E  after eval_watch marks ar2_prop e30 evaluated: e30 on scenes 51-100, then the same-machine progress numbers
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/day4_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/DAY4_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[day4] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
E20=$EX/ar2_prop_e20/export_e20.pt
echo "[day4] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[day4] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/$3/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
loop() {    # GPU, checkpoint, label, task, folder, extra args...
  local g=$1 ck=$2 l=$3 t=$4 out=$5; shift 5
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l \
      --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --execute 8 --output $O/closed_loop/$out "$@" \
      >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[day4] $(date '+%F %T') $l $t pass $pass exit code $?; finished $(n_done $out $l $t)"
  done
}
wait_e20() { until [ "$(n_done g1 ar2_prop_e20 $1)" -ge 50 ]; do sleep 120; done; }
wait_e30() { until [ -f $EX/ar2_prop_e30/.evaluated ]; do sleep 300; done; }
lane1() {
  wait_e20 put_back_block; claim 1
  loop 1 $E20 ar2_prop_e20 put_back_block g1 --from-scene 51 --limit 50
  MWAM_LEDGER=off loop 1 $E20 ar2_prop_e20_off put_back_block abl --limit 50
  MWAM_NOISE_SALT=r1 loop 1 $E20 ar2_prop_e20_r1 swap_blocks rep --limit 50
  MWAM_LEDGER=drop1 loop 1 $E20 ar2_prop_e20_drop1 swap_blocks abl --limit 25
  wait_e30; claim 1
  loop 1 $EX/ar2_prop_e30/export_e30.pt ar2_prop_e30 put_back_block g1 --from-scene 51 --limit 50
}
lane0() {
  wait_e20 swap_blocks; claim 0
  loop 0 $E20 ar2_prop_e20 swap_blocks g1 --from-scene 51 --limit 50
  MWAM_LEDGER=off loop 0 $E20 ar2_prop_e20_off swap_blocks abl --limit 50
  MWAM_LEDGER=drop1 loop 0 $E20 ar2_prop_e20_drop1 swap_blocks abl --from-scene 26 --limit 25
  MWAM_NOISE_SALT=r1 loop 0 $E20 ar2_prop_e20_r1 swap_blocks rep --from-scene 51 --limit 50
  wait_e30; claim 0
  loop 0 $EX/ar2_prop_e30/export_e30.pt ar2_prop_e30 swap_blocks g1 --from-scene 51 --limit 50
}
lane1 & P1=$!
lane0 & P0=$!
wait $P1 $P0     # never a bare `wait` after `exec > >(tee)`
echo "[day4] $(date '+%F %T') ===== summaries"
for L in ar2_prop_e20 ar2_prop_e30; do
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label $L --out /dev/null 2>/dev/null | grep -E "^  (put|swap).*/on " | sed "s/^/  $L /"
done
for L in ar2_prop_e20_off ar2_prop_e20_drop1; do
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/abl --label $L --out /dev/null 2>/dev/null | grep -E "^  (put|swap).*/on " | sed "s/^/  $L /"
  $PY scripts/fullft/press_gap.py --folder closed_loop/abl --label $L 2>/dev/null | sed "s/^/  $L /"
done
$PY scripts/fullft/pair_eq.py --name rep_ar2p_e20 --rule report --a-folders closed_loop/rep --a-label ar2_prop_e20_r1 \
  --b-folders closed_loop/g1 --b-label ar2_prop_e20 --tasks swap_blocks 2>&1 | grep -vi warn | grep swap_blocks
for pair in "ar2_prop_e20 ar_2task_e20" "ar2_prop_e30 ar_2task_e30"; do
  set -- $pair
  $PY scripts/fullft/ledger_verdict.py --folder closed_loop/g1 --arm $1 --control $2 --progress --n 100 2>&1 | head -n 3
done
