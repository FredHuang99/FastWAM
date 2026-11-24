#!/usr/bin/env bash
# mwam5090, 11-24 (Opus; plan v20 card 7, after card 13a passed its gate 18:52): the match-frame zoom cache
# (match_build.py: checks first, then 50 episodes; VAE + the pinned frozen encoder, a few GB) -> the cache relay
# (cache_relay.py put) for the new H200's obs_match. Runs beside the night's other work: on the first GPU of
# ${MB_GPUS:-"0 1"} with >= 6 GB free (no waiting for an empty card).
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/match_build_5090.sh
# Own log: outputs/fullft/MATCH_BUILD_5090_<time>.txt ; examples outputs/memory_v2/press/zoom_obs_match_a476d745/match_*.png
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/MATCH_BUILD_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[mb] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
HFPY=/opt/hf-tools/bin/python
G=""
for g in ${MB_GPUS:-0 1}; do
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i $g 2>/dev/null | tr -d ' ')
  [[ "$free" =~ ^[0-9]+$ ]] && [ "$free" -ge 6000 ] && { G=$g; break; }
done
[ -n "$G" ] || { echo "[mb] no GPU with >= 6 GB free: stop"; exit 1; }
echo "[mb] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
CUDA_VISIBLE_DEVICES=$G /opt/mwam/bin/python scripts/fullft/match_build.py 2>&1 | grep -v "Warning\|warn("
rc=${PIPESTATUS[0]}
[ $rc = 0 ] || { echo "[mb] match_build exit code $rc: nothing uploaded"; exit 1; }
D=$R/outputs/memory_v2/press/zoom_obs_match_a476d745
$HFPY scripts/fullft/cache_relay.py put $D 2>&1 | tail -n 2
$HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx zoom_obs_match_a476d745 && echo "[mb] on the cache relay" || echo "[mb] UPLOAD FAILED"
