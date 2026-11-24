#!/usr/bin/env bash
# mwam5090, 11-24 night, GPU 0 (user 18:52: GPU 0 may be used). In order:
#   1 card 5's text table (press_told_text.py --relay; the control's events file comes from the relay if missing here)
#   2 card 8's scene generation (gen_obs_5090.sh: render check first, then 155 + 600 scenes and their caches)
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/gpu0_night_5090.sh
# Own log: outputs/fullft/GPU0_NIGHT_5090_<time>.txt (gen_obs writes GEN_OBS_5090_<time>.txt as well)
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/GPU0_NIGHT_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[gpu0] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo "[gpu0] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); $(nvidia-smi -i 0 --query-gpu=name,memory.used,temperature.gpu --format=csv,noheader)"
echo "[gpu0] ===== 1 card 5 text table"
CUDA_VISIBLE_DEVICES=0 /opt/mwam/bin/python scripts/fullft/press_told_text.py --relay 2>&1 | grep -v "Warning\|warn("
echo "[gpu0] press_told_text exit code ${PIPESTATUS[0]}"
echo "[gpu0] ===== 2 card 8 generation (own log GEN_OBS_5090_<time>.txt)"
GEN_GPU=0 bash scripts/fullft/gen_obs_5090.sh > /dev/null 2>&1
echo "[gpu0] gen_obs exit code $?; $(ls -t $F/GEN_OBS_5090_*.txt | head -1)"
