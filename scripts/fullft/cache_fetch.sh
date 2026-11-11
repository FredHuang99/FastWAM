#!/usr/bin/env bash
# mwam2 container (H200; plan v11, Opus checklist 2): fetch the dense caches put by cache_upload.sh (5090) into
# outputs/memory_v2/press/dense_<task>_v1 (the same path as on the 5090) and verify every file (size + sha256) and
# the cache markers. A task not on the relay yet is waited for. Verified folders are skipped (marker .verified).
# CPU / network only: the running training on GPU0 is not touched.
#   docker exec -d mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/cache_fetch.sh
# Own log: outputs/fullft/CACHE_FETCH_<time>.txt
set -u
R=/workspace/FastWAM-memory2
P=$R/outputs/memory_v2/press
mkdir -p $P $R/outputs/fullft
LOG=$R/outputs/fullft/CACHE_FETCH_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[fetch] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
TASKS=${TASKS:-"observe_and_pickup press_button battery_try rearrange_blocks swap_T cover_blocks blocks_ranking_try place_block_mat"}
HFPY=${HFPY:-/opt/mwam/bin/python}
cd $R
df -h /workspace | tail -1
for t in $TASKS; do
  N=dense_${t}_v1
  [ -f $P/$N/.verified ] && { echo "[fetch] $t: already verified"; continue; }
  until $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx "$N"; do
    echo "[fetch] $(date '+%F %T') $t: not on the relay yet"; sleep 600; done
  echo "[fetch] $(date '+%F %T') ===== $t"
  if $HFPY scripts/fullft/cache_relay.py get --name $N --dest $P; then touch $P/$N/.verified; else echo "[fetch] $t FAILED"; fi
done
du -sh $P/dense_*_v1 2>/dev/null; df -h /workspace | tail -1
