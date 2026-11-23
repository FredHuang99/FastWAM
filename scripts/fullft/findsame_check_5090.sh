#!/usr/bin/env bash
# mwam5090, 11-23 15:45 (Opus; user 14:53: find the find-same root cause and fix it). Read-only checks, ~15 min:
#   1 (CPU) findsame_labels.py: grasp-pose labels of the next-pose head (11-23 part (2b)), arm motion onset, the
#     reference box of the closed loop's frames vs the training demos' frames (F0CHECK's wall heuristic gave the
#     reverse of the expectation, so it is replaced by a direct comparison)
#   2 (GPU 1) obs_probe.py --window onset on obs_ar e30 and obs_arprop e30: is frame 0 used at the arm's motion onset
#     (where the reach to the chosen object starts; the earlier probe looked at the final approach [g - 48, g - 1])
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/findsame_check_5090.sh
# Own log: outputs/fullft/FINDSAME_CHECK_5090_<time>.txt ; result lines start with "[labels]", "[frames]", "OBS PROBE".
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/FINDSAME_CHECK_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[fs] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
G=${PF_GPUS:-1}
say() { echo "[fs] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"

say "===== 1 labels and frames (CPU)"
CUDA_VISIBLE_DEVICES= $PY scripts/fullft/findsame_labels.py 2>&1 | grep -v "Warning\|warn(" || say "step 1 FAILED"

say "===== 2 is frame 0 used at the motion onset? (obs_probe.py --window onset)"
export_of() {
  local E=$F/exports/$1 M=/mnt/hf/relay_mirror/memwam-fullft/exports/$1
  [ -f $E/export_e30.pt ] || E=$M
  (cd $E && sha256sum -c --quiet export_e30.pt.sha256) >&2 && echo $E/export_e30.pt
}
until u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G | tr -d ' ') && [ "$u" -lt 2000 ]; do
  say "GPU $G in use ($u MiB); waiting 5 min"; sleep 300; done
for L in obs_ar_e30 obs_arprop_e30; do
  CK=$(export_of $L) || { say "no checked $L export: skipped"; continue; }
  CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $CK --window onset 2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
done
say "DONE"
