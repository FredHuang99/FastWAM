#!/usr/bin/env bash
# mwam5090, 11-16 night (Opus). LAT-T: does the press ledger model count better when a press reaches the ledger sooner?
# Written 11-16 19:55 BJ, before any of these runs; readings pre-registered in scripts/fullft/lat_verdict.py and the
# rule pick in scripts/fullft/press_event_sweep.py. Test-time only (the trained models are not changed); scenes 1-50,
# the same noise seeds as the reference runs (closed_loop/g1), results in closed_loop/lat.
#   0    waits until day6_5090.sh has ended (at most 3 h)
#   CPU  press_event_sweep.py: replay of the event detector with other thresholds on the executed frames of the five
#        press ledger runs + the 50 demos; picks thresholds by its registered rule -> outputs/fullft/PRESS_FAST_RULE.json
#   T0   press_arprop e20, MWAM_LEDGER_LAG=0 (entries visible at confirmation instead of 4 frames later)  [both GPUs]
#   T1   press_arprop e20, lag 0 + the picked delta / min_path                                           [both GPUs]
#   T1'  press_arprop e30, the same                                                                      [both GPUs]
#        (the sweep keeps rule A -> T1 is skipped as a duplicate of T0 and e30 runs with lag 0 only)
#   then press_errors, press_ledger_audit and lat_verdict on the new labels.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/lat_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/LAT_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[lat] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
BANK=$O/closed_loop/scenes_seed42_n100_press_button
echo "[lat] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
i=0
while pgrep -f "[d]ay6_5090.sh" >/dev/null && [ $i -lt 36 ]; do
  [ $i = 0 ] && echo "[lat] $(date '+%F %T') day6 still running: waiting (at most 3 h)"; sleep 300; i=$((i + 1)); done
pgrep -f "[d]ay6_5090.sh" >/dev/null && { echo "[lat] day6 still running after 3 h: stopping"; exit 1; }
SWEEP=$R/outputs/fullft/PRESS_SWEEP_$(date +%Y%m%d_%H%M).txt
$PY scripts/fullft/press_event_sweep.py g1:press_arprop_e20 g1:press_arprop_e30 rep:press_arprop_e20_r1 \
  rep:press_arprop_e30_r1 sel:press_arprop_e20 > $SWEEP 2>&1 &
SW=$!
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }   # 11-16: GPU0 fell off the bus at 19:43
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[lat] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
fetch() {      # fetch + sha256 check of exports/<L>/export_<tag>.pt
  local L=$1 tag=$2 E=$EX/$1
  [ -f $E/export_$tag.pt ] && (cd $E && sha256sum -c --status export_$tag.pt.sha256 2>/dev/null) && return 0
  rm -f $E/export_$tag.pt $E/export_$tag.pt.sha256
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft --out $E 2>&1 \
    | grep -v "Processing\|Download\|%|"
  (cd $E && sha256sum -c export_$tag.pt.sha256)
}
run() {        # GPU, shard (of 2), checkpoint, label, folder, extra args...
  local g=$1 sh=$2 ck=$3 l=$4 out=$5; shift 5
  claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l --scenes $BANK \
      --tasks press_button --execute 8 --output $O/closed_loop/$out "$@" --shard $sh/2 >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[lat] $(date '+%F %T') $l ${*} shard $sh/2 on GPU $g pass $pass exit code $?; finished $(n_done $out $l)"
  done
}
both() {       # the two shards on GPUs 0 and 1; if one GPU is missing, both shards on the other, one after the other
  local p0 p1 g
  if gpu_ok 0 && gpu_ok 1; then run 0 0 "$@" & p0=$!; run 1 1 "$@" & p1=$!; wait $p0 $p1; return; fi
  if gpu_ok 0; then g=0; elif gpu_ok 1; then g=1; else echo "[lat] $(date '+%F %T') no GPU answers: stopping"; exit 1; fi
  echo "[lat] $(date '+%F %T') only GPU $g answers: both shards on it"
  run $g 0 "$@"; run $g 1 "$@"
}
fetch press_arprop_e20 e20 || { echo "[lat] e20 export missing"; exit 1; }
fetch press_arprop_e30 e30 || { echo "[lat] e30 export missing"; exit 1; }
LABELS=""; ARMS=""
echo "[lat] $(date '+%F %T') ===== T0 e20, lag 0"
export MWAM_LEDGER_LAG=0                  # exported (not a prefix): the background shards must see it
both $EX/press_arprop_e20/export_e20.pt press_arprop_e20_lag0 lat --limit 50
LABELS="press_arprop_e20_lag0"; ARMS="e20:press_arprop_e20_lag0"
wait $SW; echo "[lat] $(date '+%F %T') sweep exit code $?"; grep -E "^SELECTED|replay check" $SWEEP
D=$($PY -c "import json; print(json.load(open('$R/outputs/fullft/PRESS_FAST_RULE.json'))['delta'])" 2>/dev/null || echo 0.015)
M=$($PY -c "import json; print(json.load(open('$R/outputs/fullft/PRESS_FAST_RULE.json'))['min_path'])" 2>/dev/null || echo 0.03)
if [ "$D" != "0.015" ] || [ "$M" != "0.03" ]; then
  echo "[lat] $(date '+%F %T') ===== T1 e20, lag 0 + delta $D min_path $M"
  export MWAM_EVENT_DELTA=$D MWAM_EVENT_MIN_PATH=$M
  both $EX/press_arprop_e20/export_e20.pt press_arprop_e20_fast lat --limit 50
  echo "[lat] $(date '+%F %T') ===== T1' e30, lag 0 + delta $D min_path $M"
  both $EX/press_arprop_e30/export_e30.pt press_arprop_e30_fast lat --limit 50
  LABELS="$LABELS press_arprop_e20_fast press_arprop_e30_fast"
  ARMS="$ARMS e20:press_arprop_e20_fast e30:press_arprop_e30_fast"
else
  echo "[lat] $(date '+%F %T') sweep kept rule A: T1 skipped (= T0); ===== e30, lag 0 only"
  both $EX/press_arprop_e30/export_e30.pt press_arprop_e30_lag0 lat --limit 50
  LABELS="$LABELS press_arprop_e30_lag0"; ARMS="$ARMS e30:press_arprop_e30_lag0"
fi
unset MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH
echo "[lat] $(date '+%F %T') ===== summaries"
$PY scripts/fullft/press_errors.py --folder closed_loop/lat $LABELS
$PY scripts/fullft/press_ledger_audit.py $(for l in $LABELS; do printf 'lat:%s ' $l; done)
$PY scripts/fullft/lat_verdict.py $ARMS
