#!/usr/bin/env bash
# mwam5090, 11-17 (Opus, written 15:15 BJ before press_fast started training). Evaluates press_fast as its exports reach
# the relay, with nobody at the keyboard, then gives the registered verdict:
#   1. waits until lat2_5090.sh / lat_5090.sh / press_fast_5090.sh / day6_5090.sh have ended (at most 8 h)
#   2. e10, e20, e30 of press_fast (H200: about 22:15, 03:00, 07:45 BJ): fetch from the relay, sha256, scenes 1-50
#      (closed_loop/g1, label press_fast_<tag>), both GPUs; the checkpoint carries lag 0 and the sweep thresholds, so no
#      ledger env override is set (any left over is unset)
#   3. P-SEL rule (press_select.py --run press_fast) picks the epoch; the pick runs on scenes 51-100 (closed_loop/sel)
#   4. press_fast_verdict.py (rule registered 11-16 19:55): paired with sel:press_arprop_e20; verdict to the relay
#      (diag/press_fast_verdict); press_errors / press_ledger_audit as description
# One GPU missing -> both shards on the other. Rerunnable: finished episodes are skipped.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/pf_eval_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/PF_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[pfe] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
BANK=$O/closed_loop/scenes_seed42_n100_press_button
RUN=press_fast
echo "[pfe] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
i=0
while pgrep -f "[l]at2_5090.sh|[l]at_5090.sh|[p]ress_fast_5090.sh|[d]ay6_5090.sh" >/dev/null && [ $i -lt 96 ]; do
  [ $i = 0 ] && echo "[pfe] $(date '+%F %T') earlier 5090 scripts still running: waiting (at most 8 h)"; sleep 300; i=$((i + 1)); done
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[pfe] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
run() {        # GPU, shard (of 2), checkpoint, label, folder, extra args...
  local g=$1 sh=$2 ck=$3 l=$4 out=$5; shift 5
  claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l --scenes $BANK \
      --tasks press_button --execute 8 --output $O/closed_loop/$out "$@" --shard $sh/2 >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[pfe] $(date '+%F %T') $l ${*} shard $sh/2 on GPU $g pass $pass exit code $?; finished $(n_done $out $l)"
  done
}
both() {
  local p0 p1 g
  if gpu_ok 0 && gpu_ok 1; then run 0 0 "$@" & p0=$!; run 1 1 "$@" & p1=$!; wait $p0 $p1; return; fi
  if gpu_ok 0; then g=0; elif gpu_ok 1; then g=1; else echo "[pfe] $(date '+%F %T') no GPU answers: stopping"; exit 1; fi
  echo "[pfe] $(date '+%F %T') only GPU $g answers: both shards on it"
  run $g 0 "$@"; run $g 1 "$@"
}
fetch() {      # tag -> the checkout path of the export (waits for the relay, checks sha256, 5 tries)
  local tag=$1 e=$EX/${RUN}_$1 k
  until $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${RUN}_$tag --repo hhyfred/memwam-fullft 2>/dev/null \
        | grep -q "^export_$tag.pt.sha256 "; do sleep 300; done
  for k in 1 2 3 4 5; do
    [ -f $e/export_$tag.pt ] && (cd $e && sha256sum -c export_$tag.pt.sha256 >/dev/null 2>&1) && return 0
    echo "[pfe] $(date '+%F %T') fetching ${RUN}_$tag (try $k)"
    $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/${RUN}_$tag --repo hhyfred/memwam-fullft --out $e 2>&1 \
      | grep -v "Processing\|Download\|%|" | tail -n 2
  done
  (cd $e && sha256sum -c export_$tag.pt.sha256)
}
for TAG in e10 e20 e30; do
  L=${RUN}_$TAG
  [ "$(n_done g1 $L)" -ge 50 ] && { echo "[pfe] $L: 1-50 already done"; continue; }
  echo "[pfe] $(date '+%F %T') waiting for exports/$L on the relay"
  fetch $TAG || { echo "[pfe] $L: sha256 still wrong after 5 tries: stopping"; exit 1; }
  echo "[pfe] $(date '+%F %T') ===== $L on scenes 1-50"
  both $EX/$L/export_$TAG.pt $L g1 --limit 50
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label $L --out /dev/null 2>/dev/null | grep -E "/on " | head -n 2
done
SP=$($PY scripts/fullft/press_select.py --run $RUN | tee /dev/stderr | awk '/^SELECTED/ {print $3}')
[ -n "$SP" ] || { echo "[pfe] P-SEL not ready: stopping"; exit 1; }
echo "[pfe] $(date '+%F %T') ===== P-SEL picked $SP: ${RUN}_$SP on scenes 51-100"
both $EX/${RUN}_$SP/export_$SP.pt ${RUN}_$SP sel --from-scene 51 --limit 50
$PY scripts/fullft/press_select.py --pair press_arprop_e20 ${RUN}_$SP
$PY scripts/fullft/press_fast_verdict.py --tag $SP
$HFPY scripts/memory_v2/migrate/relay.py put $R/outputs/fullft/PRESS_FAST_VERDICT.json --prefix diag/press_fast_verdict 2>&1 | tail -n 1
echo "[pfe] $(date '+%F %T') ===== description"
$PY scripts/fullft/press_errors.py --folder closed_loop/g1 ${RUN}_e10 ${RUN}_e20 ${RUN}_e30
$PY scripts/fullft/press_ledger_audit.py g1:${RUN}_e10 g1:${RUN}_e20 g1:${RUN}_e30 sel:${RUN}_$SP
