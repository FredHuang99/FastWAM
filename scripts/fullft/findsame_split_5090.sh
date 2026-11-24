#!/usr/bin/env bash
# mwam5090, 11-24 15:50 (Opus). obs_pose's next-pose head, before the arm moves, has squared error 0.034 on the 50
# demos (frame 0 swapped 0.034, no-motion 0.80; FINDSAME_POSE_5090_20261124_0711.txt), but 0.21 on the validation
# anchors during training (no-motion 0.53; metrics.jsonl). Same probe, train demos vs held-out val demos, separately:
# does the head know the target on demos it never trained on? Read-only, GPU 1, ~10 min.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/findsame_split_5090.sh
# Own log: outputs/fullft/FINDSAME_SPLIT_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/FINDSAME_SPLIT_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[split] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
G=${PF_GPUS:-1}
CK=$F/exports/obs_pose_e30/export_e30.pt
(cd $(dirname $CK) && sha256sum -c --quiet export_e30.pt.sha256) || { echo "[split] obs_pose_e30 not here / sha256 differs"; exit 1; }
echo "[split] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
for S in val train; do
  n=6; [ $S = val ] && n=20
  for W in wait onset; do
    CUDA_VISIBLE_DEVICES=$G /opt/mwam/bin/python scripts/fullft/obs_probe.py --export $CK --window $W --split $S --choice $n \
      2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
  done
done
echo "[split] $(date '+%F %T') DONE"
