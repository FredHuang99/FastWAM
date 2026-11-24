#!/usr/bin/env bash
# mwam5090, 11-24 15:20 (Opus; before the switch to Fable). The find-same fix obs_pose got FS VERDICT: NO HELP (A40,
# 11-24 12:51: 11 vs obs_ar 13, D -0.02, CI [-0.09, +0.05]). Its registered DESCRIBED checks (gaas_queue.txt above
# obs_pose), read-only, one GPU (PF_GPUS, default 1), ~20 min:
#   1 obs_pose e30 from the relay (export_fetch.sh, sha256 checked; kept if already here)
#   2 obs_probe.py on obs_pose e30, three windows: wait [8, m - 25] (the arm still; only frame 0 tells the target),
#     onset [m - 24, m + 8], choice [g - 48, g - 1]: action loss with frame 0 true / swapped / no history, and the
#     next-pose head's squared error true / frame 0 swapped / predicting no motion
#   3 obs_probe.py --window wait on obs_ar e30 (onset and choice were measured 11-23) for the comparison
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/findsame_pose_5090.sh
# Own log: outputs/fullft/FINDSAME_POSE_5090_<time>.txt ; result lines start with "wait", "onset", "choice", "late", "OBS PROBE".
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/FINDSAME_POSE_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[pose] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
G=${PF_GPUS:-1}
say() { echo "[pose] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
say "===== 1 obs_pose e30 from the relay"
RUN=obs_pose TAG=e30 POLL=60 timeout 3600 bash scripts/fullft/export_fetch.sh | grep -v "waiting for" | tail -n 4 \
  || { say "fetch FAILED"; exit 1; }
export_of() {
  local E=$F/exports/$1 M=/mnt/hf/relay_mirror/memwam-fullft/exports/$1
  [ -f $E/export_e30.pt ] || E=$M
  (cd $E && sha256sum -c --quiet export_e30.pt.sha256) >&2 && echo $E/export_e30.pt
}
until u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G | tr -d ' ') && [ "$u" -lt 2000 ]; do
  say "GPU $G in use ($u MiB); waiting 5 min"; sleep 300; done
say "===== 2 obs_probe on obs_pose e30 (wait / onset / choice)"
CK=$(export_of obs_pose_e30) || { say "no checked obs_pose_e30 export"; exit 1; }
for W in wait onset choice; do
  CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $CK --window $W 2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
done
say "===== 3 obs_probe --window wait on obs_ar e30"
CK=$(export_of obs_ar_e30) || { say "no checked obs_ar_e30 export"; exit 1; }
CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $CK --window wait 2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
say "DONE"
