#!/usr/bin/env bash
# mwam5090, 11-22 18:30 (Opus; user 18:23: find out why observe_and_pickup does badly). Diagnosis only, no verdict
# (the 5090 is its own machine group; the A40 numbers stay the table's).
#   1 the exports obs_ar_e30 and obs_arprop_e30: here, else the relay mirror (/mnt/hf/relay_mirror/memwam-fullft), else
#     the relay; sha256 checked
#   2 each on observe_and_pickup official scenes 1-50, execute 8 (as on the A40), with the object record on
#     (MWAM_OBJECT_LOG=1: positions of the five candidates, the target index and fail_flag after every executed target;
#     passive reads, the policy and the simulation are unchanged) -> closed_loop/a3diag
#     GPUs: PF_GPUS (default "1"); with "0 1" the two models run side by side. A GPU must be empty (< 2000 MiB) first.
#   3 obs_split.py: success / moved before the wall / picked the wrong object (same category or not) / lifted the right
#     one then failed / lifted nothing
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/obs_diag_5090.sh
#   (two GPUs: docker exec -d -e PF_GPUS="0 1" mwam5090 bash ...)
# Own log: outputs/fullft/OBS_DIAG_5090_<time>.txt ; the result line starts with "OBS SPLIT".
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
LOG=$F/OBS_DIAG_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[obsdiag] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=observe_and_pickup
BANK=$O/closed_loop/scenes_seed42_n100_$T
OUT=$O/closed_loop/a3diag
GPUS=(${PF_GPUS:-1})
say() { echo "[obsdiag] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPUs ${GPUS[*]}"
[ -d $BANK ] || { say "no scene bank $BANK: stop"; exit 1; }
grep -q "OBJECT_LOG" scripts/memory_v2/sim/sim_adapter.py || { say "sim_adapter.py has no object record (git pull): stop"; exit 1; }

export_of() {       # label -> path of a checked export_e30.pt (or empty)
  local L=$1 E=$F/exports/$1 M=/mnt/hf/relay_mirror/memwam-fullft/exports/$1
  if [ ! -f $E/export_e30.pt ] && [ -f $M/export_e30.pt ]; then E=$M; fi
  if [ ! -f $E/export_e30.pt ]; then
    E=$F/exports/$L; mkdir -p $E
    $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft --out $E 2>&1 \
      | grep -v "Processing\|Download\|%|" >&2
  fi
  (cd $E && sha256sum -c --quiet export_e30.pt.sha256) >&2 && echo $E/export_e30.pt
}
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
run() {             # gpu, label
  local CK; CK=$(export_of $2) || true
  [ -n "$CK" ] || { say "$2: no checked export (here / mirror / relay): skipped"; return 1; }
  until empty $1; do say "GPU $1 in use; waiting 5 min"; sleep 300; done
  say "$2 on GPU $1 ($CK), scenes 1-50"
  for pass in 1 2; do       # a second pass only re-runs episodes without result.json
    MWAM_OBJECT_LOG=1 CUDA_VISIBLE_DEVICES=$1 $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $2 --scenes $BANK \
      --tasks $T --limit 50 --execute 8 --output $OUT >> $OUT/../a3diag_$2.log 2>&1
    say "$2 pass $pass exit code $?; finished $(ls $OUT/$2/on/$T/seed_*/result.json 2>/dev/null | wc -l)/50"
  done
}
mkdir -p $OUT
if [ ${#GPUS[@]} -ge 2 ]; then
  run ${GPUS[0]} obs_ar_e30 & P0=$!
  run ${GPUS[1]} obs_arprop_e30 & P1=$!
  wait $P0 $P1
else
  run ${GPUS[0]} obs_ar_e30
  run ${GPUS[0]} obs_arprop_e30
fi
say "===== failure split"
$PY scripts/fullft/obs_split.py a3diag:obs_ar_e30 a3diag:obs_arprop_e30 && say "OBS SPLIT done"
