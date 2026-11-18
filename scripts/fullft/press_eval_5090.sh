#!/usr/bin/env bash
# mwam5090, 11-18 19:30 BJ (Opus, plan v14 5.2 item 3; written before any press_count / press_v3c closed-loop result).
# The 5090 is not on the auto-pull (user 18:08), so this one script carries it through the user's absence
# (11-19 all day -> 11-20 14:00). GPU1 only (PF_GPUS, default 1; GPU0 fell off the bus twice). Steps:
#   0 relay: the Obs event file (for the old H200's obs_arprop readiness; plan v14 5.2 item 5) -> diag/events_obs
#   1 waits for pf_eval_5090.sh (E3: press_fast) to end (at most 24 h)
#   2 E4 press_count (old H200, done ~11-19 07:10): e10 / e20 / e30 on scenes 1-50 (closed_loop/g1) as they reach the
#     relay; P-SEL picks the epoch; the pick on 51-100 (closed_loop/sel); press_series_verdict.py --card E4 against
#     press_fast at the epoch E3 chose; the two counterfactuals (MWAM_LEDGER=ordplus1 / duppress, scenes 1-50,
#     closed_loop/abl) and --card E4cf; verdicts to the relay (diag/press_series_verdict)
#   3 fallback (plan v14 5.1): replicate with other diffusion noise (MWAM_NOISE_SALT=r2, closed_loop/rep) the picks of
#     press_fast and press_count on 51-100
#   4 E14 press_v3c (old H200, ~11-20 morning): same as 2 against press_count at the epoch E4 chose, --card E14
#   then: description (press_errors / press_ledger_audit) and exit
# Rerunnable: finished episodes are skipped (a seed folder without result.json is renamed *_interrupted_* and rerun).
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/press_eval_5090.sh
# Own log: outputs/fullft/PRESS_EVAL_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
F=$R/outputs/fullft
LOG=$F/PRESS_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[pe] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
BANK=$O/closed_loop/scenes_seed42_n100_press_button
PF_GPUS=${PF_GPUS:-1}
echo "[pe] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPUs $PF_GPUS"

# 0 Obs event file for the old H200
E=$F/events/events_observe_and_pickup.json
if [ -s $E ]; then
  $HFPY scripts/memory_v2/migrate/relay.py put $E --prefix diag/events_obs 2>&1 | tail -n 1
else
  echo "[pe] no $E here: the old H200's obs_arprop cannot get its event file from the 5090"
fi

# 1 E3 first
i=0
while pgrep -f "[p]f_eval_5090.sh" >/dev/null && [ $i -lt 288 ]; do
  [ $i = 0 ] && echo "[pe] $(date '+%F %T') pf_eval_5090.sh (E3) still running: waiting (at most 24 h)"; sleep 300; i=$((i + 1)); done
echo "[pe] $(date '+%F %T') E3: $(cat $F/PRESS_FAST_VERDICT.json 2>/dev/null | tr -d '\n' | cut -c1-200)"

empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[pe] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
run() {        # GPU, shard (of 2), checkpoint, label, folder, extra args...
  local g=$1 sh=$2 ck=$3 l=$4 out=$5; shift 5
  claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l --scenes $BANK \
      --tasks press_button --execute 8 --output $O/closed_loop/$out "$@" --shard $sh/2 >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[pe] $(date '+%F %T') $l ${*} shard $sh/2 on GPU $g pass $pass exit code $?; finished $(n_done $out $l)"
  done
}
both() {
  local p0 p1 g ok=()
  for g in $PF_GPUS; do gpu_ok $g && ok+=($g); done
  if [ ${#ok[@]} -ge 2 ]; then run ${ok[0]} 0 "$@" & p0=$!; run ${ok[1]} 1 "$@" & p1=$!; wait $p0 $p1; return; fi
  [ ${#ok[@]} = 1 ] || { echo "[pe] $(date '+%F %T') no allowed GPU answers (PF_GPUS=$PF_GPUS): stopping"; exit 1; }
  run ${ok[0]} 0 "$@"; run ${ok[0]} 1 "$@"
}
fetch() {      # run tag (waits for the relay, checks sha256, 5 tries)
  local run=$1 tag=$2 e=$EX/$1_$2 k
  until $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${run}_$tag --repo hhyfred/memwam-fullft 2>/dev/null \
        | grep -q "^export_$tag.pt.sha256 "; do sleep 300; done
  for k in 1 2 3 4 5; do
    [ -f $e/export_$tag.pt ] && (cd $e && sha256sum -c export_$tag.pt.sha256 >/dev/null 2>&1) && return 0
    echo "[pe] $(date '+%F %T') fetching ${run}_$tag (try $k)"
    $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/${run}_$tag --repo hhyfred/memwam-fullft --out $e 2>&1 \
      | grep -v "Processing\|Download\|%|" | tail -n 2
  done
  (cd $e && sha256sum -c export_$tag.pt.sha256)
}
series() {     # run -> evaluates e10 / e20 / e30 on 1-50, P-SEL, the pick on 51-100; prints the picked tag last
  local run=$1 tag l sp
  for tag in e10 e20 e30; do
    l=${run}_$tag
    [ "$(n_done g1 $l)" -ge 50 ] && { echo "[pe] $l: 1-50 already done" >&2; continue; }
    echo "[pe] $(date '+%F %T') waiting for exports/$l on the relay" >&2
    fetch $run $tag >&2 || { echo "[pe] $l: sha256 still wrong after 5 tries: skipped" >&2; continue; }
    echo "[pe] $(date '+%F %T') ===== $l on scenes 1-50" >&2
    both $EX/$l/export_$tag.pt $l g1 --limit 50 >&2
  done
  sp=$($PY scripts/fullft/press_select.py --run $run 2>/dev/null | awk '/^SELECTED/ {print $3}')
  [ -n "$sp" ] || { echo "[pe] P-SEL for $run not ready" >&2; return 1; }
  echo "[pe] $(date '+%F %T') ===== P-SEL picked $sp: ${run}_$sp on scenes 51-100" >&2
  both $EX/${run}_$sp/export_$sp.pt ${run}_$sp sel --from-scene 51 --limit 50 >&2
  echo $sp
}
put_verdict() { $HFPY scripts/memory_v2/migrate/relay.py put $F/PRESS_$1_VERDICT.json --prefix diag/press_series_verdict 2>&1 | tail -n 1; }

# 2 E4
E3TAG=$($PY -c "import json; print(json.load(open('$F/PRESS_FAST_VERDICT.json'))['tag'])" 2>/dev/null)
SP4=$(series press_count)
if [ -n "$SP4" ]; then
  if [ -n "$E3TAG" ]; then
    $PY scripts/fullft/press_series_verdict.py --card E4 --new press_count_$SP4 --ref press_fast_$E3TAG; put_verdict E4
  else
    echo "[pe] E4: no E3 verdict (PRESS_FAST_VERDICT.json): E4 has no reference -> NO READING"
  fi
  echo "[pe] $(date '+%F %T') ===== E4 counterfactuals on press_count_$SP4, scenes 1-50"
  export MWAM_LEDGER=ordplus1; both $EX/press_count_$SP4/export_$SP4.pt press_count_${SP4}_ordplus1 abl --limit 50
  export MWAM_LEDGER=duppress; both $EX/press_count_$SP4/export_$SP4.pt press_count_${SP4}_duppress abl --limit 50
  unset MWAM_LEDGER
  $PY scripts/fullft/press_series_verdict.py --card E4cf --base press_count_$SP4; put_verdict E4cf
fi

# 3 fallback: noise replicates of the two picks on 51-100
export MWAM_NOISE_SALT=r2
[ -n "$E3TAG" ] && { echo "[pe] $(date '+%F %T') ===== replicate press_fast_$E3TAG on 51-100 (noise r2)"; both $EX/press_fast_$E3TAG/export_$E3TAG.pt press_fast_$E3TAG rep --from-scene 51 --limit 50; }
[ -n "$SP4" ] && { echo "[pe] $(date '+%F %T') ===== replicate press_count_$SP4 on 51-100 (noise r2)"; both $EX/press_count_$SP4/export_$SP4.pt press_count_$SP4 rep --from-scene 51 --limit 50; }
unset MWAM_NOISE_SALT

# 4 E14
SP14=$(series press_v3c)
if [ -n "$SP14" ] && [ -n "$SP4" ]; then
  $PY scripts/fullft/press_series_verdict.py --card E14 --new press_v3c_$SP14 --ref press_count_$SP4; put_verdict E14
fi
echo "[pe] $(date '+%F %T') ===== description"
$PY scripts/fullft/press_errors.py --folder closed_loop/g1 press_count_e10 press_count_e20 press_count_e30 press_v3c_e10 press_v3c_e20 press_v3c_e30 2>&1 | tail -n 40
$PY scripts/fullft/press_ledger_audit.py ${SP4:+sel:press_count_$SP4} ${SP14:+sel:press_v3c_$SP14} 2>&1 | tail -n 40
