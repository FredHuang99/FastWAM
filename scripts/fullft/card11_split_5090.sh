#!/usr/bin/env bash
# mwam5090, 11-24 20:45 (Opus; plan v20 card 11): the swap_T failure split with the classes fixed at 20:45 from the
# first 10 episodes per model (swapT_split.py classify). Waits until card11_5090.sh has scenes 1-50 of both models, then
# runs the split (CPU, read-only). Classes only in the summary; every episode's measurements in outputs/fullft/SWAPT_SPLIT.json.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/card11_split_5090.sh
# Own log: outputs/fullft/CARD11_SPLIT_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/CARD11_SPLIT_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[split] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src
say() { echo "[split] $(date '+%F %T') $*"; }
grep -q "^CLASSES = classify" scripts/fullft/swapT_split.py || { say "classes not committed here (git pull): stop"; exit 1; }
C11=$(ls -t $F/CARD11_5090_*.txt | head -1)
say "waiting for $C11 to report scenes 1-50 of both models"
until grep -q "scenes 1-50 done for both" $C11; do
  grep -q "finished, exit code [1-9]" $C11 && { say "card 11 ended with an error: $(tail -n 1 $C11)"; exit 1; }
  sleep 300
done
say "card 11 closed loops done; split with the classes fixed at 20:45"
/opt/mwam/bin/python scripts/fullft/swapT_split.py swaptdiag:swapT_ar_e30 swaptdiag:swapT_arprop_e30 > $F/swapT_split_full.txt 2>&1
rc=$?
grep "^== \|^  *[0-9][0-9]*  [A-Za-z]" $F/swapT_split_full.txt
say "split exit code $rc (all measurements: outputs/fullft/swapT_split_full.txt, SWAPT_SPLIT.json)"
