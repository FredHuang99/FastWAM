#!/usr/bin/env bash
# mwam5090, 11-22 (Opus, plan v19 3.3 A3). GPU1 only (PF_GPUS, default 1). The zoom latents of the observe_and_pickup
# training cache for the two fixed boxes, then onto the cache relay for the new H200:
#   boxes (chosen 11-22 13:05 from the frame sheet SHEET.png of 4 demos x 4 frames, user 12:49):
#     reference  x 0.395-0.675, y 0.06-0.34 of the head camera (the shelf object of frame 0; every reference seen lies in
#                x 0.49-0.58, y 0.13-0.27; 4:3 like the camera, about 3.6x)
#     candidates x 0-1, y 0.42-1.0 (the table; full width, so only about 1.7x vertically)
#   1 zoom_tools.py build: pipeline check (the full box must reproduce the cache's latent[0]), then 50 episodes
#   2 cache_relay.py put (sha256 manifest last) as zoom_obs_<tag>
# Rerunnable (finished episodes are kept; a relay name already complete is not uploaded again).
#   docker exec -d -e PF_GPUS=1 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/zoom_build_5090.sh
# Own log: outputs/fullft/ZOOM_BUILD_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/ZOOM_BUILD_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[zoom] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
G=${PF_GPUS:-1}
REF="0.395 0.06 0.675 0.34"
CUR="0.0 0.42 1.0 1.0"
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G | tr -d ' ')
[[ "$used" =~ ^[0-9]+$ ]] && [ "$used" -lt 2000 ] || { echo "[zoom] GPU $G in use ($used MiB): stop"; exit 1; }
echo "[zoom] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/zoom_tools.py build --ref-box $REF --cur-box $CUR || { echo "[zoom] build FAILED"; exit 1; }
TAG=$($PY -c "
import sys; sys.path.insert(0, 'src')
from fastwam.fullft.history import HistoryRule
from fastwam.fullft.zoom import box_tag
print(box_tag(HistoryRule('ar', zoom=True, zoom_ref_box=(${REF// /,}), zoom_cur_box=(${CUR// /,}))))")
D=$R/outputs/memory_v2/press/zoom_dense_observe_and_pickup_v1_$TAG
[ -f $D/ZOOM.json ] || { echo "[zoom] no $D/ZOOM.json"; exit 1; }
echo "[zoom] $(date '+%F %T') built $D ($(du -sh $D | cut -f1)); relay as zoom_obs_$TAG"
HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/fullft/cache_relay.py put $D --name zoom_obs_$TAG 2>&1 | tail -n 4
echo "[zoom] $(date '+%F %T') ZOOM READY tag $TAG (relay name zoom_obs_$TAG)"
