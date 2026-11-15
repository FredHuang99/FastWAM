#!/usr/bin/env bash
# mwam5090, night 11-15 -> 11-16 (descriptive). Starts when day5_5090.sh has finished; every run first waits while a
# press_ar export is on the relay and not yet evaluated (task_watch goes first). Fixed pipeline.
# Why (written 11-15 21:20, before these runs): press_arprop e30 scored 0/50 on press_button 1-50 (first count right
# 10, second 12) after 9/50 at e20 (first count right 28). Is the drop real or diffusion-noise luck?
#   r1 noise replicates (same scenes, other diffusion noise) of press_arprop e30 and e20, press 1-50:
#     e30 r1 success >= 5/50 -> e30's 0/50 is largely noise;  e30 r1 <= 2/50 and first count right <= 15 -> the drop is real
#   press_arprop e30 on press 51-100: the same model on 50 more scenes (size of the e30 number)
# GPU g runs shard g/2 of each. Summary: press_errors.py on all press labels.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/night5_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/NIGHT5_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[night5] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
P30=$EX/press_arprop_e30/export_e30.pt
P20=$EX/press_arprop_e20/export_e20.pt
echo "[night5] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
D5=$(ls -t $R/outputs/fullft/DAY5_5090_*.txt | head -1)
until grep -q "finished, exit code" $D5; do sleep 120; done
echo "[night5] $(date '+%F %T') day5 finished ($D5)"
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[night5] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
pending() {
  local L
  for L in press_ar_e10 press_ar_e20 press_ar_e30; do
    [ -f $EX/$L/.evaluated ] && continue
    $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/$L --repo hhyfred/memwam-fullft 2>/dev/null \
      | grep -q "sha256 " && return 0
  done
  return 1
}
yield_press() { while pending; do sleep 300; done; }
run() {   # GPU, checkpoint, label, folder, salt, extra args...
  local g=$1 ck=$2 l=$3 out=$4 salt=$5; shift 5
  yield_press; claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g MWAM_NOISE_SALT=$salt $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l \
      --scenes $O/closed_loop/scenes_seed42_n100_press_button --tasks press_button --execute 8 \
      --output $O/closed_loop/$out "$@" --shard $g/2 >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[night5] $(date '+%F %T') $l ${*} shard $g/2 pass $pass exit code $?; finished $(n_done $out $l)"
  done
}
lane() {
  run $1 $P30 press_arprop_e30_r1 rep r1 --limit 50
  run $1 $P20 press_arprop_e20_r1 rep r1 --limit 50
  run $1 $P30 press_arprop_e30 g1 "" --from-scene 51 --limit 50
}
lane 0 & P0=$!
lane 1 & P1=$!
wait $P0 $P1     # never a bare `wait` after `exec > >(tee)`
echo "[night5] $(date '+%F %T') ===== summaries"
$PY scripts/fullft/press_errors.py --folder closed_loop/g1 press_arprop_e20 press_arprop_e30
$PY scripts/fullft/press_errors.py --folder closed_loop/rep press_arprop_e20_r1 press_arprop_e30_r1
$PY scripts/fullft/press_errors.py --folder closed_loop/abl press_arprop_e30_off
