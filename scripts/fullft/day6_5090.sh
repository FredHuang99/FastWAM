#!/usr/bin/env bash
# mwam5090, 11-16. Replaces night5_5090.sh: its runs waited for task_watch to evaluate press_ar_e10, but task_watch had
# skipped e10 after a dropped download (570 MB of 12 GB, no retry), so from 11-16 02:55 BJ both GPUs sat idle except
# for task_watch's press_ar e20 (deviation 32). night5's last item (press_arprop e30 on 51-100) is dropped: e30 is
# known to be worse than e20 (replicate 1/50, first count right 8) and 51-100 is kept for node P-SEL.
# Written 11-16 14:20 BJ, before these runs; expectations below. Fixed pipeline; every GPU run first waits (at most
# 150 min) while task_watch has a press_ar export on the relay that it has not evaluated yet.
#   CPU  press_ledger_audit.py on every press label so far (its reading is pre-registered in its header); again at the end
#   1    press_ar e10 on scenes 1-50 (fetch: relay get now retries); marks exports/press_ar_e10/.evaluated
#        (completes the AR curve; descriptive)
#   2    press_arprop e20 with the ledger OFF at test time, scenes 1-50 (closed_loop/abl, label press_arprop_e20_off):
#        the causal test at the epoch that counts. Expectation: success <= 2/50 and first count right <= 10/50
#        (ledger on: 9/50 and 28/50, replicate 9 and 27)
#   3    SELECT=1 only (node P-SEL, registered in scripts/fullft/press_select.py before any press run on 51-100):
#        the selected export of press_arprop, then of press_ar (after its e30 is evaluated), on scenes 51-100
#        (closed_loop/sel); then the paired table. Descriptive; the registered S-C verdict is unchanged.
#   if task_watch ends without evaluating press_ar_e30 (e.g. its download failed), this script evaluates it.
#   docker exec -d -e SELECT=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/day6_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
SELECT=${SELECT:-0}
LOG=$R/outputs/fullft/DAY6_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[day6] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
BANK=$O/closed_loop/scenes_seed42_n100_press_button
echo "[day6] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); SELECT=$SELECT"
AUDIT="g1:press_arprop_e10 g1:press_arprop_e20 g1:press_arprop_e30 rep:press_arprop_e20_r1 rep:press_arprop_e30_r1
       abl:press_arprop_e30_off g1:press_ar_e20"
$PY scripts/fullft/press_ledger_audit.py $AUDIT > $R/outputs/fullft/PRESS_AUDIT_$(date +%Y%m%d_%H%M).txt 2>&1 &
AUD=$!
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[day6] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
on_relay() { $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/$1 --repo hhyfred/memwam-fullft 2>/dev/null \
             | grep -q "sha256 "; }
tw_alive() { pgrep -f "[t]ask_watch.sh" >/dev/null; }
wait_e30() {   # until task_watch has evaluated press_ar_e30 or has ended (at most 10 h); then evaluate it here if needed
  local i=0
  while [ $i -lt 120 ] && [ ! -f $EX/press_ar_e30/.evaluated ] && tw_alive; do sleep 300; i=$((i + 1)); done
  [ -f $EX/press_ar_e30/.evaluated ] && return 0
  tw_alive && { echo "[day6] $(date '+%F %T') press_ar_e30 still not evaluated after 10 h; going on without it"; return 1; }
  until on_relay press_ar_e30; do sleep 300; done
  evaluate press_ar e30
}
yield_tw() {   # task_watch first: wait while it has an unevaluated press_ar export to take, at most 150 min
  local i=0
  while [ $i -lt 30 ] && tw_alive && [ ! -f $EX/press_ar_e30/.evaluated ] && on_relay press_ar_e30; do
    sleep 300; i=$((i + 1)); done
}
fetch() {      # fetch + sha256 check of exports/<L>/export_<tag>.pt
  local L=$1 tag=$2 E=$EX/$1
  [ -f $E/export_$tag.pt ] && (cd $E && sha256sum -c --status export_$tag.pt.sha256 2>/dev/null) && return 0
  rm -f $E/export_$tag.pt $E/export_$tag.pt.sha256
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft --out $E 2>&1 \
    | grep -v "Processing\|Download\|%|"
  (cd $E && sha256sum -c export_$tag.pt.sha256)
}
run() {        # GPU, checkpoint, label, folder, extra args...
  local g=$1 ck=$2 l=$3 out=$4; shift 4
  yield_tw; claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l --scenes $BANK \
      --tasks press_button --execute 8 --output $O/closed_loop/$out "$@" --shard $g/2 >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[day6] $(date '+%F %T') $l ${*} shard $g/2 pass $pass exit code $?; finished $(n_done $out $l)"
  done
}
both() {       # the same run on both GPUs (shards 0/2, 1/2); waits for both
  local p0 p1
  run 0 "$@" & p0=$!
  run 1 "$@" & p1=$!
  wait $p0 $p1          # never a bare `wait` after `exec > >(tee)`
}
evaluate() {   # run tag: fetch exports/<run>_<tag> and evaluate scenes 1-50 in closed_loop/g1; marks .evaluated
  local L=${1}_$2
  [ -f $EX/$L/.evaluated ] && { echo "[day6] $L already evaluated"; return 0; }
  fetch $L $2 || { echo "[day6] $L: fetch / sha256 failed"; return 1; }
  both $EX/$L/export_$2.pt $L g1 --limit 50
  [ "$(n_done g1 $L)" -ge 50 ] && touch $EX/$L/.evaluated && echo "[day6] $(date '+%F %T') $L evaluated"
}
echo "[day6] $(date '+%F %T') ===== 1 press_ar e10"
evaluate press_ar e10
echo "[day6] $(date '+%F %T') ===== 2 press_arprop e20, ledger off"
if fetch press_arprop_e20 e20; then
  export MWAM_LEDGER=off
  both $EX/press_arprop_e20/export_e20.pt press_arprop_e20_off abl --limit 50
  unset MWAM_LEDGER
fi
if [ "$SELECT" = 1 ]; then
  echo "[day6] $(date '+%F %T') ===== 3 P-SEL"
  SP=$($PY scripts/fullft/press_select.py --run press_arprop | tee /dev/stderr | awk '/^SELECTED/ {print $3}')
  [ -n "$SP" ] && fetch press_arprop_$SP $SP && \
    both $EX/press_arprop_$SP/export_$SP.pt press_arprop_$SP sel --from-scene 51 --limit 50
  wait_e30
  SA=$($PY scripts/fullft/press_select.py --run press_ar | tee /dev/stderr | awk '/^SELECTED/ {print $3}')
  [ -n "$SA" ] && fetch press_ar_$SA $SA && both $EX/press_ar_$SA/export_$SA.pt press_ar_$SA sel --from-scene 51 --limit 50
  [ -n "$SP" ] && [ -n "$SA" ] && $PY scripts/fullft/press_select.py --pair press_arprop_$SP press_ar_$SA
else
  wait_e30
fi
wait $AUD
echo "[day6] $(date '+%F %T') ===== summaries"
$PY scripts/fullft/press_errors.py --folder closed_loop/g1 press_ar_e10 press_ar_e20 press_ar_e30
$PY scripts/fullft/press_errors.py --folder closed_loop/abl press_arprop_e20_off press_arprop_e30_off
$PY scripts/fullft/press_verdict.py --folder closed_loop/g1 --prop press_arprop_e30 --control press_ar_e30
$PY scripts/fullft/press_ledger_audit.py g1:press_ar_e10 g1:press_ar_e30 abl:press_arprop_e20_off \
  $( [ "$SELECT" = 1 ] && ls -d $O/closed_loop/sel/*/ 2>/dev/null | xargs -n1 basename | sed 's/^/sel:/' )
