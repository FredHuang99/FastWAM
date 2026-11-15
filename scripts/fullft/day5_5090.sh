#!/usr/bin/env bash
# mwam5090, 11-15 (descriptive mechanism runs on the FINAL ledger model ar2_prop e30; no verdict). Fixed pipeline.
# Written 11-15 15:40, after the A100 verdict (USEFUL) and the e20 counterfactuals, and BEFORE any run below.
# Expectations (scenes 1-50 unless said; base = ar2_prop_e30 on the same scenes: swap 50/50, put 50/50):
#   off      (no ledger entry ever)              swap: success <= 5/50 and "kept moving" >= 40/50 (e20 gave 0/50, 50)
#                                                put : success >= 45/50 (e20: put does not need the ledger, 50/50)
#   freeze2  (NEW: the ledger stops after the 2nd completed move; the 3rd move happens but is never recorded)
#            swap: if the stop decision reads the most recent recorded move -> "kept moving" >= 30/50, success <= 20/50
#                  if success >= 40/50 -> the third move need not be recorded (presence / vision suffice): reading rejected
#   addmove  (first move entered twice)          swap: "pressed before s3" >= 20/50 (e20: 9/50, below)  [replication]
#   dropfirst(first move erased)                 swap: "kept moving" >= 30/50       (e20: 0/50, below)  [replication]
#   press off (press_arprop e30, ledger off, press_button 1-50, after its normal run is evaluated):
#            count accuracy collapses: success <= max(2, half the ledger-on success) and n1 correct <= half of ledger-on
#   r1       (other diffusion noise, ar2_prop e30 swap 1-100): spread only (e20 replicate: 95 vs 97 of 100)
# Part 1 (now; sized to end before press_arprop e30 reaches the relay ~19:25 BJ):
#   GPU0  freeze2 swap 1-50 -> addmove swap 1-50 -> freeze2 swap 51-100 shard 0/2
#   GPU1  off swap 1-50     -> off put 1-50      -> freeze2 swap 51-100 shard 1/2
# Part 2 (after task_watch marks press_arprop_e30 evaluated; at the latest 23:00 BJ): press off e30, shard g/2 on GPU g
# Part 3 (night; each run waits while a press_ar export is on the relay and not yet evaluated, so task_watch goes first):
#   GPU0  dropfirst swap 1-50 -> r1 swap 1-50        GPU1  off swap 51-100 -> r1 swap 51-100
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/day5_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/DAY5_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[day5] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
E30=$EX/ar2_prop_e30/export_e30.pt
P30=$EX/press_arprop_e30/export_e30.pt
echo "[day5] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ -f $E30 ] || { echo "no $E30"; exit 1; }
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[day5] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/$3/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
pending() {   # 0 if a press_ar export is on the relay but not yet evaluated here (task_watch's turn)
  local L
  for L in press_ar_e10 press_ar_e20 press_ar_e30; do
    [ -f $EX/$L/.evaluated ] && continue
    $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/$L --repo hhyfred/memwam-fullft 2>/dev/null \
      | grep -q "sha256 " && return 0
  done
  return 1
}
yield_press() { while pending; do sleep 300; done; }
loop() {    # GPU, checkpoint, label, task, folder, ledger mode ("" = normal), noise salt, extra args...
  local g=$1 ck=$2 l=$3 t=$4 out=$5 mode=$6 salt=$7; shift 7
  claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g MWAM_LEDGER=$mode MWAM_NOISE_SALT=$salt $PY -m fastwam.memory_v2.online run --checkpoint $ck \
      --label $l --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --execute 8 --output $O/closed_loop/$out "$@" \
      >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[day5] $(date '+%F %T') $l $t ${*} pass $pass exit code $?; finished $(n_done $out $l $t)"
  done
}
report() {  # folder, label
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/$1 --label $2 --out /dev/null 2>/dev/null | grep -E "^  [a-z_]+/on " | sed "s/^/  $2 /"
  $PY scripts/fullft/press_gap.py --folder closed_loop/$1 --label $2 2>/dev/null | grep -v "0 episodes" | sed "s/^/  $2 /"
}
lane0() {
  loop 0 $E30 ar2_prop_e30_freeze2 swap_blocks abl freeze2 "" --limit 50
  loop 0 $E30 ar2_prop_e30_addmove swap_blocks abl addmove "" --limit 50
  loop 0 $E30 ar2_prop_e30_freeze2 swap_blocks abl freeze2 "" --from-scene 51 --limit 50 --shard 0/2
}
lane1() {
  loop 1 $E30 ar2_prop_e30_off swap_blocks abl off "" --limit 50
  loop 1 $E30 ar2_prop_e30_off put_back_block abl off "" --limit 50
  loop 1 $E30 ar2_prop_e30_freeze2 swap_blocks abl freeze2 "" --from-scene 51 --limit 50 --shard 1/2
}
lane0 & P0=$!
lane1 & P1=$!
wait $P0 $P1     # never a bare `wait` after `exec > >(tee)`
echo "[day5] $(date '+%F %T') ===== part 1 done"
for L in ar2_prop_e30_off ar2_prop_e30_freeze2 ar2_prop_e30_addmove; do report abl $L; done
DEADLINE=$(TZ=Asia/Shanghai date -d "2026-11-15 23:00" +%s)
echo "[day5] $(date '+%F %T') part 2 waits for $EX/press_arprop_e30/.evaluated (or 23:00 BJ)"
until [ -f $EX/press_arprop_e30/.evaluated ] || [ "$(date +%s)" -ge "$DEADLINE" ]; do sleep 300; done
if [ -f $P30 ]; then
  loop 0 $P30 press_arprop_e30_off press_button abl off "" --limit 50 --shard 0/2 & Q0=$!
  loop 1 $P30 press_arprop_e30_off press_button abl off "" --limit 50 --shard 1/2 & Q1=$!
  wait $Q0 $Q1
  report abl press_arprop_e30_off
else
  echo "[day5] $(date '+%F %T') no $P30: press off skipped"
fi
echo "[day5] $(date '+%F %T') ===== part 3"
lane0n() {
  yield_press; loop 0 $E30 ar2_prop_e30_dropfirst swap_blocks abl dropfirst "" --limit 50
  yield_press; loop 0 $E30 ar2_prop_e30_r1 swap_blocks rep "" r1 --limit 50
}
lane1n() {
  yield_press; loop 1 $E30 ar2_prop_e30_off swap_blocks abl off "" --from-scene 51 --limit 50
  yield_press; loop 1 $E30 ar2_prop_e30_r1 swap_blocks rep "" r1 --from-scene 51 --limit 50
}
lane0n & P0=$!
lane1n & P1=$!
wait $P0 $P1
echo "[day5] $(date '+%F %T') ===== summaries"
for L in ar2_prop_e30_off ar2_prop_e30_freeze2 ar2_prop_e30_addmove ar2_prop_e30_dropfirst press_arprop_e30_off; do report abl $L; done
report rep ar2_prop_e30_r1
$PY scripts/fullft/pair_eq.py --name rep_ar2p_e30 --rule report --a-folders closed_loop/rep --a-label ar2_prop_e30_r1 \
  --b-folders closed_loop/g1 --b-label ar2_prop_e30 --tasks swap_blocks 2>&1 | grep -vi warn | grep swap_blocks
