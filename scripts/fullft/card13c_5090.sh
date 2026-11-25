#!/usr/bin/env bash
# mwam5090, 11-25 (Opus; plan v20 card 13c, P1, descriptive): is observe_and_pickup's "four in ten episodes never close
# the gripper" the policy switching targets between re-plans? obs_ar_e30 on the official seed-42 scenes 1-50 with the
# object record (MWAM_OBJECT_LOG=1) at execute 16 and 32 (execute 8 = the 11-22 a3diag run of the same model, scenes and
# record: reused). Then obs_grasp.py / obs_split.py on all three. Described only: episodes that never close the gripper,
# the first close's object = the target, successes. (Plan's expectation: success up to about the blind-pick level, the
# first-close rate unchanged.) Run by q5090.sh (GPU=$GPU). Own log: outputs/fullft/CARD13C_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
LOG=$F/CARD13C_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c13c] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK MWAM_TOLD_COUNTS
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=observe_and_pickup
BANK=$O/closed_loop/scenes_seed42_n100_$T
G=${GPU:-1}
L=obs_ar_e30
say() { echo "[c13c] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
[ -d $BANK ] || { say "no scene bank $BANK: stop"; exit 1; }
E=$F/exports/$L; M=/mnt/hf/relay_mirror/memwam-fullft/exports/$L
if [ ! -f $E/export_e30.pt ] && [ -f $M/export_e30.pt ]; then E=$M; fi
if [ ! -f $E/export_e30.pt ]; then
  mkdir -p $F/exports/$L; E=$F/exports/$L
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft --out $E 2>&1 | tail -n 2
fi
(cd $E && sha256sum -c --quiet export_e30.pt.sha256) || { say "$L: export not verified: stop"; exit 1; }
for X in 16 32; do
  OUT=$O/closed_loop/obsexec$X
  for pass in 1 2; do
    MWAM_OBJECT_LOG=1 CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $E/export_e30.pt --label $L \
      --scenes $BANK --tasks $T --limit 50 --execute $X --output $OUT >> $O/closed_loop/obsexec${X}_$L.log 2>&1
    say "execute $X pass $pass exit code $?; finished $(ls $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | wc -l)/50"
  done
done
say "===== grasp and split (execute 8 = a3diag of 11-22)"
$PY scripts/fullft/obs_grasp.py a3diag:$L obsexec16:$L obsexec32:$L
$PY scripts/fullft/obs_split.py a3diag:$L obsexec16:$L obsexec32:$L
say "CARD 13C done"
