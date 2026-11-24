#!/usr/bin/env bash
# mwam5090, 11-24 night (Opus; plan v20 section 5, the 5090's closed-loop GPU): in order on GPU ${PF_GPUS:-1}
#   1 card 5's text table (press_told_text.py --relay, T5 only, a few minutes) -> relay diag/press_told; the new H200's
#     slot job and the A40 fetch it
#   2 card 11, the swap_T failure split (card11_5090.sh: scenes 1-10 of both models, the first-10 measurements, then
#     11-50), a few hours
#   3 the development-scene baselines of the five tasks not at target (dev_eval_5090.sh: 30 dev scenes each, the
#     current best model of each task), so the new versions' e10 / e20 have a same-machine reference
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/v20_night_5090.sh
# Own log: outputs/fullft/V20_NIGHT_5090_<time>.txt (card 11 writes its own CARD11_5090_<time>.txt as well)
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/V20_NIGHT_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[night] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
G=${PF_GPUS:-1}
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
echo "[night] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
until empty $G; do echo "[night] $(date '+%F %T') GPU $G in use; waiting 2 min"; sleep 120; done
echo "[night] ===== 1 card 5 text table"
CUDA_VISIBLE_DEVICES=$G /opt/mwam/bin/python scripts/fullft/press_told_text.py --relay 2>&1 | grep -v "Warning\|warn("
echo "[night] press_told_text exit code ${PIPESTATUS[0]}"
echo "[night] ===== 2 card 11 (own log CARD11_5090_<time>.txt)"
PF_GPUS=$G bash scripts/fullft/card11_5090.sh > /dev/null 2>&1
echo "[night] card 11 exit code $?; $(ls -t $F/CARD11_5090_*.txt | head -1)"
echo "[night] ===== 3 development-scene baselines (own log DEV_EVAL_5090_<time>.txt; results DEV_EVAL.tsv)"
PF_GPUS=$G DEV_RUNS="ranking_ar_e30:blocks_ranking_try rearrange_arprop_e30:rearrange_blocks swapT_ar_e30:swap_T obs_arprop_e30:observe_and_pickup press_fast_e30:press_button" \
  bash scripts/fullft/dev_eval_5090.sh > /dev/null 2>&1
echo "[night] dev baselines exit code $?"; tail -n 6 $F/DEV_EVAL.tsv
