#!/usr/bin/env bash
# mwam5090 container (plan v11, Opus checklist 2): put the dense caches on the private HF repo hhyfred/memwam-caches
# so the H200 can fetch them (cache_fetch.sh). Order = when the H200 needs them: Obs (W1), Press (W2), Battery (W3),
# then the B1 tasks. A task whose build is not finished yet (no CACHE.json, e.g. C1 still running) is waited for.
# Already uploaded folders are skipped (marker .relayed in the folder). CPU / network only, no GPU.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/cache_upload.sh
# Own log: outputs/memory_v2/report/CACHE_UPLOAD_<time>.txt
set -u
R=/workspace/FastWAM-memory2
P=$R/outputs/memory_v2/press
LOG=$R/outputs/memory_v2/report/CACHE_UPLOAD_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[upload] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
TASKS=${TASKS:-"observe_and_pickup press_button battery_try rearrange_blocks swap_T cover_blocks blocks_ranking_try place_block_mat"}
HFPY=/opt/hf-tools/bin/python
cd $R
for t in $TASKS; do
  D=$P/dense_${t}_v1
  [ -f $D/.relayed ] && { echo "[upload] $t: already on the relay"; continue; }
  until [ -f $D/CACHE.json ]; do echo "[upload] $(date '+%F %T') $t: waiting for its build (CACHE.json)"; sleep 600; done
  echo "[upload] $(date '+%F %T') ===== $t ($(du -sh $D | cut -f1))"
  if $HFPY scripts/fullft/cache_relay.py put $D; then touch $D/.relayed; else echo "[upload] $t FAILED (next task continues)"; fi
done
echo "[upload] on the relay: $($HFPY scripts/fullft/cache_relay.py ls | tr '\n' ' ')"
