#!/usr/bin/env bash
# mwam5090, 11-16 night (Opus, written 21:20 BJ before any of these runs). Fills the 5090 from the end of LAT-T
# (~23:40) to the morning; every run is on press_arprop e20, the model P-SEL selected.
#   CF-A  MWAM_LEDGER=addpress, scenes 1-50 (closed_loop/abl): the first completed press is entered twice
#   CF-D  MWAM_LEDGER=droppress, scenes 1-50 (closed_loop/abl): the first completed press is removed
#         readings registered in scripts/fullft/press_pair.py (does the model COUNT ledger entries?); same noise as g1
#   H     the LAT-T T1 setting (lag 0 + the sweep's thresholds; lag 0 alone if the sweep kept rule A) on the held-out
#         scenes 51-100 (closed_loop/latsel), against sel:press_arprop_e20 (8/50, first count right 26): descriptive
#   R     the same setting on scenes 1-50 with the noise salt r1 (closed_loop/latrep), against rep:press_arprop_e20_r1
#         (9/50, 27): is the LAT-T reading robust to the diffusion noise; descriptive
# Waits (at most 6 h) until lat_5090.sh and press_fast_5090.sh have ended; first completes P-SEL's press_ar e30 on
# 51-100 if the 19:43 GPU loss cut it short. Then press_errors / audit / press_pair. One GPU missing -> both shards on
# the other.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/lat2_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
EX=$R/outputs/fullft/exports
LOG=$R/outputs/fullft/LAT2_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[lat2] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH
PY=/opt/mwam/bin/python
BANK=$O/closed_loop/scenes_seed42_n100_press_button
CK=$EX/press_arprop_e20/export_e20.pt
echo "[lat2] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
i=0
while pgrep -f "[l]at_5090.sh|[p]ress_fast_5090.sh|[d]ay6_5090.sh" >/dev/null && [ $i -lt 72 ]; do
  [ $i = 0 ] && echo "[lat2] $(date '+%F %T') LAT-T still running: waiting (at most 6 h)"; sleep 300; i=$((i + 1)); done
pgrep -f "[l]at_5090.sh|[p]ress_fast_5090.sh" >/dev/null && { echo "[lat2] LAT-T still running after 6 h: stopping"; exit 1; }
[ -f $CK ] || { echo "[lat2] $CK missing"; exit 1; }
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
gpu_ok() { nvidia-smi -i $1 --query-gpu=index --format=csv,noheader >/dev/null 2>&1; }   # 11-16: GPU0 fell off the bus at 19:43
claim() { until empty $1 && sleep 90 && empty $1; do sleep 120; done; echo "[lat2] $(date '+%F %T') GPU $1 claimed"; }
n_done() { ls $O/closed_loop/$1/$2/on/press_button/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
run() {        # GPU, shard (of 2), label, folder, extra args...
  local g=$1 sh=$2 l=$3 out=$4; shift 4
  claim $g
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $l --scenes $BANK \
      --tasks press_button --execute 8 --output $O/closed_loop/$out "$@" --shard $sh/2 >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[lat2] $(date '+%F %T') $l ${*} shard $sh/2 on GPU $g pass $pass exit code $?; finished $(n_done $out $l)"
  done
}
both() {       # the two shards on GPUs 0 and 1; if one GPU is missing, both shards on the other, one after the other
  local p0 p1 g
  if gpu_ok 0 && gpu_ok 1; then run 0 0 "$@" & p0=$!; run 1 1 "$@" & p1=$!; wait $p0 $p1; return; fi
  if gpu_ok 0; then g=0; elif gpu_ok 1; then g=1; else echo "[lat2] $(date '+%F %T') no GPU answers: stopping"; exit 1; fi
  echo "[lat2] $(date '+%F %T') only GPU $g answers: both shards on it"
  run $g 0 "$@"; run $g 1 "$@"
}
A=$(n_done sel press_ar_e30)
if [ "$A" -lt 50 ] && [ -f $EX/press_ar_e30/export_e30.pt ]; then    # 11-16: GPU0 fell off the bus at 19:43 during P-SEL
  echo "[lat2] $(date '+%F %T') ===== P-SEL completion: press_ar_e30 on scenes 51-100 has $A/50"
  CK0=$CK; CK=$EX/press_ar_e30/export_e30.pt
  both press_ar_e30 sel --from-scene 51 --limit 50
  CK=$CK0
  $PY scripts/fullft/press_select.py --pair press_arprop_e20 press_ar_e30
fi
echo "[lat2] $(date '+%F %T') ===== CF-A addpress"
export MWAM_LEDGER=addpress; both press_arprop_e20_addpress abl --limit 50
echo "[lat2] $(date '+%F %T') ===== CF-D droppress"
export MWAM_LEDGER=droppress; both press_arprop_e20_droppress abl --limit 50
unset MWAM_LEDGER
D=$($PY -c "import json; print(json.load(open('$R/outputs/fullft/PRESS_FAST_RULE.json'))['delta'])" 2>/dev/null || echo 0.015)
M=$($PY -c "import json; print(json.load(open('$R/outputs/fullft/PRESS_FAST_RULE.json'))['min_path'])" 2>/dev/null || echo 0.03)
L=press_arprop_e20_fast; [ "$D" = "0.015" ] && [ "$M" = "0.03" ] && L=press_arprop_e20_lag0
export MWAM_LEDGER_LAG=0 MWAM_EVENT_DELTA=$D MWAM_EVENT_MIN_PATH=$M
echo "[lat2] $(date '+%F %T') ===== H $L (lag 0, delta $D, min_path $M) on scenes 51-100"
both $L latsel --from-scene 51 --limit 50
echo "[lat2] $(date '+%F %T') ===== R $L noise salt r1, scenes 1-50"
export MWAM_NOISE_SALT=r1; both $L latrep --limit 50
unset MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_NOISE_SALT
echo "[lat2] $(date '+%F %T') ===== summaries"
$PY scripts/fullft/press_errors.py --folder closed_loop/abl press_arprop_e20_addpress press_arprop_e20_droppress
$PY scripts/fullft/press_ledger_audit.py abl:press_arprop_e20_addpress abl:press_arprop_e20_droppress latsel:$L latrep:$L
$PY scripts/fullft/press_pair.py abl:press_arprop_e20_addpress~g1:press_arprop_e20~addpress \
  abl:press_arprop_e20_droppress~g1:press_arprop_e20~droppress latsel:$L~sel:press_arprop_e20 \
  latrep:$L~rep:press_arprop_e20_r1 latrep:$L~lat:$L
