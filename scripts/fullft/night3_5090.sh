#!/usr/bin/env bash
# mwam5090, night 11-13 -> 11-14 (descriptive, no verdict). Keeps both GPUs busy until the ar2_prop e20 export.
# Fixed pipeline (OIDN 2.0.1 + training-cache text). Lane GPU0 starts when e10fx_5090.sh has finished its put run,
# lane GPU1 when e10fx has finished its swap run; then each claims its GPU only after 90 s empty.
#   R  noise replicates of N7 e30 swap 1-100 (MWAM_NOISE_SALT=r1, r2; labels ar_2task_e30_r1 / _r2, closed_loop/rep):
#      how many scenes flip between two runs of the SAME model on the SAME machine that differ only in the diffusion
#      noise -> the base rate for every paired comparison (AL4's 6-0, the ledger rule's +8 / +-3)
#   C  the 100-scene curves on this machine: N7 e20 and N7 e10 (fixed pipeline, ar_2task_e10_fx) on scenes 51-100
#   P  after eval_watch (RUN=ar2_prop) has marked e10 evaluated (~02:45): ar2_prop e10 on scenes 51-100
#   X  then execution length on the converged AR base: N7 e30 swap 1-50 with execute 4 (GPU0) and 16 (GPU1); paired
#      with execute 8 (closed_loop/g1) -- the e10 execlen readings (execlen_5090.sh) at the final epoch
# ~00:50-02:45 eval_watch takes both GPUs for ar2_prop e10 scenes 1-50 (it waits for empty GPUs; these lanes leave
# them free in time and wait for its marker before P).
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/night3_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/NIGHT3_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[night3] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
echo "[night3] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
E10FX=$(ls -t $R/outputs/fullft/E10FX_5090_*.txt 2>/dev/null | head -1)
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[night3] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/$3/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
loop() {    # GPU, checkpoint, label, task, folder, extra args...
  local g=$1 ck=$2 l=$3 t=$4 out=$5; shift 5
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l \
      --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --execute 8 --output $O/closed_loop/$out "$@" \
      >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[night3] $(date '+%F %T') $l $t pass $pass exit code $?; finished $(n_done $out $l $t)"
  done
}
wait_line() { [ -n "$E10FX" ] || return 0; until grep -q "$1" $E10FX; do sleep 120; done; }
wait_p() { until [ -f $EX/ar2_prop_e10/.evaluated ]; do sleep 300; done; }
E30=$EX/ar_2task_e30/export_e30.pt; E20=$EX/ar_2task_e20/export_e20.pt; E10=$EX/ar_2task_e10/export_e10.pt
lane0() {
  wait_line "put_back_block pass 2"; claim 0
  MWAM_NOISE_SALT=r1 loop 0 $E30 ar_2task_e30_r1 swap_blocks rep --limit 50
  loop 0 $E20 ar_2task_e20 swap_blocks g1 --from-scene 51 --limit 50
  loop 0 $E10 ar_2task_e10_fx swap_blocks g1 --from-scene 51 --limit 50
  MWAM_NOISE_SALT=r2 loop 0 $E30 ar_2task_e30_r2 swap_blocks rep --limit 50
  wait_p; claim 0
  loop 0 $EX/ar2_prop_e10/export_e10.pt ar2_prop_e10 swap_blocks g1 --from-scene 51 --limit 50
  loop 0 $E30 ar_2task_e30_x4 swap_blocks execlen --limit 50 --execute 4
}
lane1() {
  wait_line "swap_blocks pass 2"; claim 1
  MWAM_NOISE_SALT=r1 loop 1 $E30 ar_2task_e30_r1 swap_blocks rep --from-scene 51 --limit 50
  loop 1 $E20 ar_2task_e20 put_back_block g1 --from-scene 51 --limit 50
  loop 1 $E10 ar_2task_e10_fx put_back_block g1 --from-scene 51 --limit 50
  MWAM_NOISE_SALT=r2 loop 1 $E30 ar_2task_e30_r2 swap_blocks rep --from-scene 51 --limit 50
  wait_p; claim 1
  loop 1 $EX/ar2_prop_e10/export_e10.pt ar2_prop_e10 put_back_block g1 --from-scene 51 --limit 50
  loop 1 $E30 ar_2task_e30_x16 swap_blocks execlen --limit 50 --execute 16
}
lane0 & P0=$!
lane1 & P1=$!
wait $P0 $P1      # never a bare `wait` after `exec > >(tee)`
echo "[night3] $(date '+%F %T') ===== R noise replicates vs the original run (swap 1-100, report)"
for r in r1 r2; do
  $PY scripts/fullft/pair_eq.py --name rep_$r --rule report --a-folders closed_loop/rep --a-label ar_2task_e30_$r \
    --b-folders closed_loop/g1 --b-label ar_2task_e30 --tasks swap_blocks 2>&1 | grep -vi warn | grep swap_blocks
done
$PY scripts/fullft/pair_eq.py --name rep_r1r2 --rule report --a-folders closed_loop/rep --a-label ar_2task_e30_r2 \
  --b-folders closed_loop/rep --b-label ar_2task_e30_r1 --tasks swap_blocks 2>&1 | grep -vi warn | grep swap_blocks
for x in 4 16; do
  $PY scripts/fullft/pair_eq.py --name execlen_e30_x$x --rule report --a-folders closed_loop/execlen --a-label ar_2task_e30_x$x \
    --b-folders closed_loop/g1 --b-label ar_2task_e30 --tasks swap_blocks 2>&1 | grep -vi warn | grep swap_blocks
done
for L in ar_2task_e10_fx ar_2task_e20 ar_2task_e30 ar2_prop_e10; do
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label $L --out /dev/null 2>/dev/null | grep -E "^  (put|swap).*/on " | sed "s/^/  $L /"
done
