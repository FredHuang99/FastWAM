#!/usr/bin/env bash
# mwam2 (old H200), 11-28 16:50 (Opus; plan v22 card 36): the condition of the queue line swapT_ow (h200_queue.sh runs
# a line's condition at every pick; exit 0 = runnable). swapT_ow = swapT_arprop_h2's exact line (new H200) + the release
# weighting; this machine never trained swap_T, so the inputs may be missing. Cheap once ready (marker); otherwise at
# most one attempt per 2 h:
#   0 scripts/fullft/GO_card36 must exist (committed with the registration, before the run)
#   1 the swap_T training cache (dense_swap_T_v1) via cache_ready.sh (cache relay, sha256 checked)
#   2 events_swap_T.json from the relay (diag/events_b1, the file the H100 and the new H200 trained swapT_arprop /
#     swapT_arprop_h2 with) into outputs/fullft/events/ (an existing file is never overwritten)
#   3 ledger_ready.py --variant arprop --tasks swap_T (CPU only) -> marker READY_arprop_swap_T
# /opt/mwam/bin/python only. Log: outputs/fullft/CARD36_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
[ -f scripts/fullft/GO_card36 ] || exit 1
[ -f $F/READY_arprop_swap_T ] && [ -f outputs/memory_v2/press/dense_swap_T_v1/.verified ] && [ -s $F/events/events_swap_T.json ] && exit 0
T=$F/CARD36_READY_TRIED
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 7200 ]; then exit 1; fi
touch $T
exec >> $F/CARD36_READY.log 2>&1
say() { echo "[card36] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
say "attempt"
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
rm -f $F/CACHE_READY_TRIED_GO_card36        # cache_ready.sh keeps its own 2-h marker; this script already limits tries
bash scripts/fullft/cache_ready.sh GO_card36 dense_swap_T_v1 || { say "swap_T cache not ready (see CACHE_READY.log): NOT READY"; exit 1; }
E=$F/events/events_swap_T.json
mkdir -p $F/events $F/relay_in/events_b1
if [ ! -s $E ]; then
  HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_b1 --out $F/relay_in/events_b1 2>&1 | tail -n 2
  [ -s $F/relay_in/events_b1/events_swap_T.json ] || { say "events_swap_T.json not on the relay: NOT READY"; exit 1; }
  cp $F/relay_in/events_b1/events_swap_T.json $E && say "events file copied (sha256 $(sha256sum $E | cut -c1-16))"
fi
PYTHONPATH=src CUDA_VISIBLE_DEVICES= $PY scripts/fullft/ledger_ready.py --variant arprop --tasks swap_T \
  --marker READY_arprop_swap_T --skip-tests 2>&1 | grep -v '^\.\+$' | tail -n 8
[ -f $F/READY_arprop_swap_T ] && { say "READY"; exit 0; }
say "NOT READY (see above)"; exit 1
