#!/usr/bin/env bash
# mwam5090, 11-26 12:20 (Opus, unattended round 5). Plan v20 card 7 (obs_match) DESCRIBED parts, after its MAIN read
# NO HELP (A40 V20_OBSMATCH.json, 11-26 08:11: 12 vs 13). The card's next step depends on them: "NO HELP and the probe
# shows the model read the match frame -> the problem is the action, back to the failure split; NO HELP and not read ->
# this road stops". Registered described items done here (read-only, descriptive):
#   1 obs_probe with the match frame swapped for another demo's (>= 2 % at the onset = the cue is read):
#     obs_probe.py --swap matchref (11-26), onset window on all / trained / held-out demos, and the wait window.
#   2 on the 5090 with MWAM_OBJECT_LOG=1, the first-close-on-target rate: obs_match e30 closed loop, the official seed-42
#     scenes 1-50, execute 8 (as a3diag's obs_ar e30 of 11-22), then obs_grasp.py / obs_split.py beside a3diag:obs_ar_e30.
#   Not here: the counterfactual closed loop with another scene's match frame (needs an online switch; not written).
# Run by q5090.sh (GPU=$GPU). Own log: outputs/fullft/CARD7PROBE_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
LOG=$F/CARD7PROBE_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c7p] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK MWAM_TOLD_COUNTS
PY=/opt/mwam/bin/python
T=observe_and_pickup
BANK=$O/closed_loop/scenes_seed42_n100_$T
G=${GPU:-1}
L=obs_match_e30
say() { echo "[c7p] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
[ -d $O/press/zoom_obs_match_a476d745 ] || { say "match cache zoom_obs_match_a476d745 not on this machine: stop"; exit 1; }
RUN=obs_match TAG=e30 POLL=60 bash scripts/fullft/export_fetch.sh || { say "obs_match e30: fetch failed"; exit 1; }
CK=$F/exports/$L/export_e30.pt
say "===== 1 match-frame swap probe"
for args in "onset all" "onset train" "onset val" "wait all"; do
  set -- $args
  say "window $1 split $2"
  CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $CK --swap matchref --window $1 --split $2 --choice 6 \
    2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
done
say "===== 2 closed loop with the object record (scenes 1-50, execute 8)"
[ -d $BANK ] || { say "no scene bank $BANK: stop"; exit 1; }
OUT=$O/closed_loop/c7obj
for pass in 1 2; do
  MWAM_OBJECT_LOG=1 CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L \
    --scenes $BANK --tasks $T --limit 50 --execute 8 --output $OUT >> $O/closed_loop/c7obj_$L.log 2>&1
  say "pass $pass exit code $?; finished $(ls $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | wc -l)/50"
done
$PY scripts/fullft/obs_grasp.py a3diag:obs_ar_e30 c7obj:$L
$PY scripts/fullft/obs_split.py a3diag:obs_ar_e30 c7obj:$L
say "CARD 7 PROBE done"
