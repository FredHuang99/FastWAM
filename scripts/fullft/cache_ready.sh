#!/usr/bin/env bash
# mwam2 (old H200) / any queue machine, 11-28 12:50 (Opus, weekend round 5/5): a generic queue-line condition
# (h200_queue.sh / h100_queue.sh run a line's condition at every pick; exit 0 = runnable).
#   usage: bash scripts/fullft/cache_ready.sh <GO file name under scripts/fullft/> <cache name> [<cache name> ...]
#   0 scripts/fullft/<GO file> must exist (the user approves a run on this machine by having it committed); else exit 1
#   1 each cache outputs/memory_v2/press/<cache name>: verified copy (.verified) -> fine; a copy without .verified ->
#     cache_relay.py verify; no copy -> cache_relay.py get from the cache relay (sha256 checked); then .verified
#   At most one attempt per 2 h per GO file (marker outputs/fullft/CACHE_READY_TRIED_<GO>); cheap once all are verified.
# Written for obs_s800_s18 on the old H200 (GO_obs_s800_s18_h200o; the H200 class like obs_s800 on the new H200), so
# that the run does not need a new job on the new H200. Log: outputs/fullft/CACHE_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
GO=${1:?GO file name}; shift
[ -f scripts/fullft/$GO ] || exit 1
ok=1
for c in "$@"; do [ -f outputs/memory_v2/press/$c/.verified ] || ok=0; done
[ "$ok" = 1 ] && exit 0
T=$F/CACHE_READY_TRIED_$GO
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 7200 ]; then exit 1; fi
touch $T
exec >> $F/CACHE_READY.log 2>&1
echo "[cache-ready] $(TZ=Asia/Shanghai date '+%F %T') $GO: attempt ($(df -h $R/outputs | tail -n 1 | awk '{print $4}') free)"
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
for c in "$@"; do
  CD=outputs/memory_v2/press/$c
  [ -f $CD/.verified ] && { echo "[cache-ready] $c: verified copy here"; continue; }
  if [ -d $CD ]; then
    echo "[cache-ready] $c: copy here without .verified: verifying"
    $HFPY scripts/fullft/cache_relay.py verify $CD 2>&1 | tail -n 4; rc=${PIPESTATUS[0]}
  else
    echo "[cache-ready] $c: fetching from the cache relay"
    HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/fullft/cache_relay.py get --name $c --dest outputs/memory_v2/press \
      2>&1 | tail -n 4; rc=${PIPESTATUS[0]}
  fi
  [ "$rc" = 0 ] || { echo "[cache-ready] $c: fetch / sha256 check failed (exit $rc): NOT READY"; exit 1; }
  touch $CD/.verified && echo "[cache-ready] $c: verified ($(du -sh $CD | cut -f1))"
done
echo "[cache-ready] $(TZ=Asia/Shanghai date '+%F %T') $GO: READY"
exit 0
