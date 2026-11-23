#!/usr/bin/env bash
# mwam2 (old H200), 11-22 (Opus, plan v19 B5): the condition of the queue line ranking_arprop (h200_queue.sh runs a
# line's condition at every pick; exit 0 = runnable). Ranking body-record arm, paired with ranking_ar (new H200; the two
# H200s are IDENTICAL). Cheap when ready (marker); otherwise at most one attempt per 2 h:
#   0 GO_ranking_arprop must exist: Opus writes it (through the repo, scripts/fullft/GO_ranking_arprop) after the event
#     counts of the nine tasks' demos are in Status 11-22 (plan v19: count before training, see whether any demo has
#     more than 32 body events)
#   0b the ranking cache from the cache relay when it is not here (11-23; before, a missing cache made this exit 1 silently)
#   1 the ranking event file from the relay (diag/events_b1, put there by the 5090 on 11-17; the H100 and the new H200
#     used files of the same batch) into outputs/fullft/events/ (an existing file is never overwritten)
#   2 ledger_ready.py --variant arprop --tasks blocks_ranking_try --event-max 69 (event file / 69 text slots; CPU only;
#     user 11-22 02:23: record size 80 for ranking)
#     -> marker READY_arprop_blocks_ranking_try
# This machine has no /opt/hf-tools: /opt/mwam/bin/python only. Log: outputs/fullft/RANKING_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
[ -f scripts/fullft/GO_ranking_arprop ] || exit 1
[ -f $F/READY_arprop_blocks_ranking_try ] && exit 0
T=$F/RANKING_READY_TRIED
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 7200 ]; then exit 1; fi
touch $T
exec >> $F/RANKING_READY.log 2>&1
echo "[ranking] $(TZ=Asia/Shanghai date '+%F %T') attempt"
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
# 11-23 00:35 (Opus): the queue restarted at 00:20 passed this line over in silence and started ar2_prop_s18: the check
# above used to need the ranking cache already verified here, and this machine never had it (ranking_ar trained on the
# new H200, which fetched it from the cache relay) [inferred]. Now: fetch it from the cache relay once (sha256 checked by
# cache_relay.py), or verify a copy already here; every step is logged.
CD=outputs/memory_v2/press/dense_blocks_ranking_try_v1
if [ ! -f $CD/.verified ]; then
  if [ -d $CD ]; then
    $HFPY scripts/fullft/cache_relay.py verify $CD 2>&1 | tail -n 4; rc=${PIPESTATUS[0]}
  else
    echo "[ranking] fetching the ranking cache from the cache relay ($(df -h $R/outputs | tail -n 1 | awk '{print $4}') free)"
    HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/fullft/cache_relay.py get --name dense_blocks_ranking_try_v1 \
      --dest outputs/memory_v2/press 2>&1 | tail -n 4; rc=${PIPESTATUS[0]}
  fi
  [ "$rc" = 0 ] || { echo "[ranking] cache fetch / sha256 check failed (exit $rc): NOT READY"; exit 1; }
  touch $CD/.verified && echo "[ranking] cache verified ($(du -sh $CD | cut -f1))"
fi
E=$F/events/events_blocks_ranking_try.json
mkdir -p $F/events $F/relay_in/events_b1
if [ ! -s $E ]; then
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_b1 --out $F/relay_in/events_b1 2>&1 | tail -n 2
  [ -s $F/relay_in/events_b1/events_blocks_ranking_try.json ] || { echo "[ranking] not on the relay"; exit 1; }
  cp $F/relay_in/events_b1/events_blocks_ranking_try.json $E && echo "[ranking] event file copied"
fi
PYTHONPATH=src CUDA_VISIBLE_DEVICES= $PY scripts/fullft/ledger_ready.py --variant arprop --tasks blocks_ranking_try \
  --event-max 69 --marker READY_arprop_blocks_ranking_try --skip-tests 2>&1 | grep -v '^\.\+$' | tail -n 8
[ -f $F/READY_arprop_blocks_ranking_try ] && { echo "[ranking] READY"; exit 0; }
echo "[ranking] NOT READY (see above)"; exit 1
