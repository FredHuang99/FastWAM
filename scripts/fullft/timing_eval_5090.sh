#!/usr/bin/env bash
# mwam5090, 11-20 20:00 BJ (Opus, plan v16 T1 / T2; user 19:12; written before any T1 / T2 episode). GPU1 only (PF_GPUS,
# default 1). Test time only, no training: press_count e30 (the E4 pick, already here) on press scenes 1-50, default noise,
# paired with the existing closed_loop/g1 run of the same model. Readings registered in scripts/fullft/timing_verdict.py.
# Order (most decisive first; ~2 h per 50 episodes on one GPU):
#   1 lag16  MWAM_LEDGER_LAG=16 (later)          -> closed_loop/tim, label press_count_e30_lag16
#   2 prov   MWAM_EVENT_PROVISIONAL=0.002 (earlier)                     press_count_e30_prov
#   3 exec4  --execute 4 (decisions twice as often)                     press_count_e30_exec4
#   4 lag8   MWAM_LEDGER_LAG=8 (the middle of the dose)                 press_count_e30_lag8
# After each step: timing_verdict.py (partial words say WAIT) and the press ledger audit of the new run; the verdict
# JSON goes to the relay (diag/timing_verdict). Rerunnable: finished episodes are skipped.
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/timing_eval_5090.sh
# Own log: outputs/fullft/TIMING_EVAL_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
F=$R/outputs/fullft
LOG=$F/TIMING_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[te] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
BANK=$O/closed_loop/scenes_seed42_n100_press_button
PF_GPUS=${PF_GPUS:-1}
CK=$EX/press_count_e30/export_e30.pt
echo "[te] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPUs $PF_GPUS"
[ -f $CK ] || { echo "[te] no $CK on this machine: stop"; exit 1; }
grep -q MWAM_EVENT_PROVISIONAL src/fastwam/fullft/online.py || { echo "[te] online.py has no MWAM_EVENT_PROVISIONAL (git pull): stop"; exit 1; }
i=0
while pgrep -f "[p]ress_eval_5090.sh|[p]f_eval_5090.sh" >/dev/null && [ $i -lt 144 ]; do
  [ $i = 0 ] && echo "[te] another 5090 evaluation chain runs: waiting (at most 12 h)"; sleep 300; i=$((i + 1)); done

empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[te] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/tim/$1/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
run() {        # GPU, shard (of 2), label, execute
  local g=$1 sh=$2 l=$3 ex=$4
  claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $l --scenes $BANK \
      --tasks press_button --execute $ex --output $O/closed_loop/tim --limit 50 --shard $sh/2 >> $O/closed_loop/tim_$l.log 2>&1
    echo "[te] $(date '+%F %T') $l shard $sh/2 on GPU $g pass $pass exit code $?; finished $(n_done $l)"
  done
}
both() {       # label, execute
  local p0 p1 g ok=()
  for g in $PF_GPUS; do gpu_ok $g && ok+=($g); done
  if [ ${#ok[@]} -ge 2 ]; then run ${ok[0]} 0 "$@" & p0=$!; run ${ok[1]} 1 "$@" & p1=$!; wait $p0 $p1; return; fi
  [ ${#ok[@]} = 1 ] || { echo "[te] $(date '+%F %T') no allowed GPU answers (PF_GPUS=$PF_GPUS): stopping"; exit 1; }
  run ${ok[0]} 0 "$@"; run ${ok[0]} 1 "$@"
}
verdict() {
  $PY scripts/fullft/timing_verdict.py 2>&1 | tail -n 12
  $PY scripts/fullft/press_ledger_audit.py tim:$1 2>&1 | grep -E "^==|over-pressing|visibility delay|READING" | head -n 6
  $HFPY scripts/memory_v2/migrate/relay.py put $F/TIMING_VERDICT.json --prefix diag/timing_verdict 2>&1 | tail -n 1
}
step() {       # label, execute, env assignments...
  local l=$1 ex=$2; shift 2
  [ "$(n_done $l)" -ge 50 ] && { echo "[te] $l: already done"; verdict $l; return; }
  echo "[te] $(date '+%F %T') ===== $l (execute $ex; $*)"
  ( for a in "$@"; do export "$a"; done; both $l $ex )
  verdict $l
}
step press_count_e30_lag16 8 MWAM_LEDGER_LAG=16
step press_count_e30_prov 8 MWAM_EVENT_PROVISIONAL=0.002
step press_count_e30_exec4 4
step press_count_e30_lag8 8 MWAM_LEDGER_LAG=8
echo "[te] $(date '+%F %T') ===== all four done"
$PY scripts/fullft/timing_verdict.py
