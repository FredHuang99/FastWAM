#!/usr/bin/env bash
# mwam5090, 11-28 08:50 (Opus, weekend round 4/5). Plan v21 card 25 (obs_cf200, registered 11-27 in gaas_queue.txt above
# its line) DESCRIBED items that were not written yet (read-only, descriptive; this machine is its own comparison group):
#   PART=probe  "the frame-0 swap at the onset on held-out generated demos (>= 2 % = frame 0 is used) for obs_cf200 and
#               obs_s200; the onset action loss, trained vs held-out": obs_probe.py --roots on the 10 probe-group demos
#               that no run trained on (dense_observe_and_pickup_cf10probe_v1: 2 table layouts x 5 targets, built by
#               card25_5090.sh, never in a training list), windows onset and wait, split all. RUNS = "run:tag ..."
#               (default "obs_cf200:e10 obs_s200:e30"). The trained-demo side is card13b_5090.sh's split train.
#   PART=close  "the first-close-on-target rate (5090, MWAM_OBJECT_LOG=1, scenes 1-50)": closed loop of RUN_TAG on the
#               official seed-42 scenes 1-50, execute 8 (as card7probe_5090.sh / a3diag of 11-22), then obs_grasp.py and
#               obs_split.py beside a3diag:obs_ar_e30 (6/29 first closes on the target). RUN / TAG (default obs_cf200 e10).
#   Written before the run (card 25): the frame-0 swap exceeds 2 % for obs_cf200 already at e10 (below 2 % for
#   obs_s200); the first close is on the target in more than 40 % of the episodes with a close (20 % = blind).
# Run by q5090.sh (GPU=$GPU). Own log: outputs/fullft/CARD25DESC_5090_<part>_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
P=$O/press
F=$R/outputs/fullft
PART=${PART:-probe}
LOG=$F/CARD25DESC_5090_${PART}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c25d] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK MWAM_TOLD_COUNTS
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
T=observe_and_pickup
G=${GPU:-1}
FAIL=0
say() { echo "[c25d] $(date '+%F %T') $*"; }
say "start PART=$PART; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"

if [ "$PART" = probe ]; then
  PR=$P/dense_${T}_cf10probe_v1
  if [ ! -f $PR/CACHE.json ]; then
    say "probe-group cache not here: fetching $(basename $PR) from the cache relay"
    $HFPY scripts/fullft/cache_relay.py get --name $(basename $PR) --dest $P 2>&1 | tail -n 3
  fi
  [ -f $PR/CACHE.json ] || { say "no probe-group cache $PR: stop"; exit 1; }
  say "probe groups: $(ls $PR | head -3 | tr '\n' ' ')... ($(du -sh $PR | cut -f1))"
  for rt in ${RUNS:-obs_cf200:e10 obs_s200:e30}; do
    RUN=${rt%%:*}; TAG=${rt##*:}
    RUN=$RUN TAG=$TAG POLL=60 bash scripts/fullft/export_fetch.sh || { say "${RUN}_$TAG: fetch failed"; FAIL=1; continue; }
    CK=$F/exports/${RUN}_$TAG/export_$TAG.pt
    for W in onset wait; do
      say "${RUN}_$TAG held-out generated probe groups, window $W"
      CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $CK --roots $PR --window $W --split all --choice 6 \
        --out $F/align/OBS_PROBE_${RUN}_${TAG}_${W}_cf10probe.json 2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
      rc=${PIPESTATUS[0]}; [ "$rc" = 0 ] || { say "${RUN}_$TAG window $W: probe FAILED (exit code $rc)"; FAIL=1; }
    done
  done
  say "CARD 25 DESCRIBED PROBE done"
  exit $FAIL
fi

if [ "$PART" = close ]; then
  RUN=${RUN:-obs_cf200}; TAG=${TAG:-e10}; L=${RUN}_$TAG
  BANK=$O/closed_loop/scenes_seed42_n100_$T
  [ -d $BANK ] || { say "no scene bank $BANK: stop"; exit 1; }
  RUN=$RUN TAG=$TAG POLL=60 bash scripts/fullft/export_fetch.sh || { say "$L: fetch failed"; exit 1; }
  CK=$F/exports/$L/export_$TAG.pt
  OUT=$O/closed_loop/c25obj
  for pass in 1 2; do       # the second pass only reruns episodes that did not finish
    MWAM_OBJECT_LOG=1 CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L \
      --scenes $BANK --tasks $T --limit 50 --execute 8 --output $OUT >> $O/closed_loop/c25obj_$L.log 2>&1
    say "pass $pass exit code $?; finished $(ls $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | wc -l)/50"
  done
  n=$(ls $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | wc -l)
  $PY scripts/fullft/obs_grasp.py a3diag:obs_ar_e30 c25obj:$L || { say "obs_grasp.py FAILED"; FAIL=1; }   # 11-28 audit: exit codes
  $PY scripts/fullft/obs_split.py a3diag:obs_ar_e30 c25obj:$L || { say "obs_split.py FAILED"; FAIL=1; }
  say "CARD 25 DESCRIBED CLOSE done ($n/50 episodes)"
  [ "$n" -ge 50 ] || exit 1
  exit $FAIL
fi
say "unknown PART=$PART"; exit 2
