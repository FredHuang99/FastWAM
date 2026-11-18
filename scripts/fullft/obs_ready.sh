#!/usr/bin/env bash
# mwam2 (old H200), 11-18 (Opus, plan v14 5.2 item 5): the condition of the queue line obs_arprop (h200_queue.sh runs a
# line's condition at every pick; exit 0 = runnable). Obs ledger arm = the main table's ninth task, paired with obs_ar
# (trained on this machine). Cheap when ready (marker); otherwise at most one attempt per 2 h:
#   1 the Obs event file from the relay (diag/events_obs, put there by the 5090's press_eval_5090.sh step 0) into
#     outputs/fullft/events/ (an existing file is never overwritten)
#   2 ledger_ready.py --variant arprop --tasks observe_and_pickup (unit tests, event file / text-slot checks; CPU only)
#     -> marker READY_arprop_observe_and_pickup (check 3 = equal; the subset reading of deviation 44 is NOT applied here)
# This machine has no /opt/hf-tools: /opt/mwam/bin/python only. Log: outputs/fullft/OBS_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
[ -f $F/READY_arprop_observe_and_pickup ] && exit 0
[ -f outputs/memory_v2/press/dense_observe_and_pickup_v1/.verified ] || exit 1
T=$F/OBS_READY_TRIED
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 7200 ]; then exit 1; fi
touch $T
exec >> $F/OBS_READY.log 2>&1
echo "[obs] $(TZ=Asia/Shanghai date '+%F %T') attempt"
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
E=$F/events/events_observe_and_pickup.json
mkdir -p $F/events $F/relay_in/events_obs
if [ ! -s $E ]; then
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_obs --out $F/relay_in/events_obs 2>&1 | tail -n 2
  [ -s $F/relay_in/events_obs/events_observe_and_pickup.json ] || { echo "[obs] not on the relay yet"; exit 1; }
  cp $F/relay_in/events_obs/events_observe_and_pickup.json $E && echo "[obs] event file copied"
fi
PYTHONPATH=src CUDA_VISIBLE_DEVICES= $PY scripts/fullft/ledger_ready.py --variant arprop --tasks observe_and_pickup \
  --marker READY_arprop_observe_and_pickup 2>&1 | grep -v '^\.\+$' | tail -n 8
[ -f $F/READY_arprop_observe_and_pickup ] && { echo "[obs] READY"; exit 0; }
echo "[obs] NOT READY (see above)"; exit 1
