#!/usr/bin/env bash
# mwam5090, 11-26 02:10 (Opus, unattended round 3). Plan v20 card 13b = supplement 3 (P1, descriptive only): the train /
# held-out split probe that findsame_split_5090.sh ran on obs_pose (FINDSAME_SPLIT, 11-24), now on the three-frame model
# obs_ar e30 and the no-history model obs_none e30, both windows (wait = before the arm moves, onset = the start of the
# reach). Question: is "memorising the training scenes" general on observe_and_pickup, not a product of the pose head?
# Reading (plan v20 3.3, descriptive): per model and split, (swap - true) / true of the action loss (2 % line, obs_probe's
# rule) and the action loss itself, train demos against held-out demos. The val_action curves of supplement 3 live in
# the H200s' training logs (not on this machine): not part of this script.
# Read-only; fetches the two exports from the relay if they are not here (sha256 checked); one GPU ($GPU from q5090.sh).
#   q5090.txt line: card13b | gpu | - | bash scripts/fullft/card13b_5090.sh
# Own log: outputs/fullft/CARD13B_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/CARD13B_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[13b] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
G=${GPU:-${PF_GPUS:-1}}
echo "[13b] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
for RUN in obs_ar obs_none; do
  RUN=$RUN TAG=e30 POLL=60 bash scripts/fullft/export_fetch.sh || { echo "[13b] ${RUN}_e30: fetch failed"; exit 1; }
  CK=$F/exports/${RUN}_e30/export_e30.pt
  for S in val train; do
    n=6; [ $S = val ] && n=20
    for W in wait onset; do
      echo "[13b] $(date '+%F %T') ${RUN}_e30 split $S window $W"
      CUDA_VISIBLE_DEVICES=$G /opt/mwam/bin/python scripts/fullft/obs_probe.py --export $CK --window $W --split $S --choice $n \
        2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
    done
  done
done
echo "[13b] $(date '+%F %T') CARD 13B done"
