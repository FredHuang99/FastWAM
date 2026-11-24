#!/usr/bin/env bash
# mwam5090, 11-24 (Opus; plan v20 card 11): swap_T failure split, zero training, descriptive (5090 = its own group).
#   1 exports swapT_ar_e30 and swapT_arprop_e30 (H100 training; here, else the relay mirror, else the relay; sha256)
#   2 the official seed-42 swap_T scene bank here (closed_loop/scenes_seed42_n100_swap_T); built as the A40's BANK card
#     when missing (official_scenes.py + online plan)
#   3 closed loop, execute 8, MWAM_OBJECT_LOG=1 (passive object record, now with orientations), closed_loop/swaptdiag:
#     first scenes 1-10 of both models, then the measurements of those 10 (swapT_split.py --first 10: the classes are
#     fixed from these BEFORE any full result is read), then scenes 11-50 of both
#   GPU: PF_GPUS (default 1); a GPU must be empty (< 2000 MiB) first.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/card11_5090.sh
# Own log: outputs/fullft/CARD11_5090_<time>.txt (no success counts in it); measurements outputs/fullft/SWAPT_SPLIT_FIRST.json
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
LOG=$F/CARD11_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c11] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=swap_T
C=$O/closed_loop
BANK=$C/scenes_seed42_n100_$T
OUT=$C/swaptdiag
G=${PF_GPUS:-1}
say() { echo "[c11] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
grep -q "task_quats" scripts/memory_v2/sim/sim_adapter.py || { say "sim_adapter.py without orientations (git pull): stop"; exit 1; }
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
export_of() {
  local L=$1 E=$F/exports/$1 M=/mnt/hf/relay_mirror/memwam-fullft/exports/$1
  if [ ! -f $E/export_e30.pt ] && [ -f $M/export_e30.pt ]; then E=$M; fi
  if [ ! -f $E/export_e30.pt ]; then
    E=$F/exports/$L; mkdir -p $E
    $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft --out $E 2>&1 | grep -v "Processing\|Download\|%|" >&2
  fi
  (cd $E && sha256sum -c --quiet export_e30.pt.sha256) >&2 && echo $E/export_e30.pt
}
until empty $G; do say "GPU $G in use; waiting 5 min"; sleep 300; done
if ! $PY scripts/memory_v2/official_scenes.py complete $BANK $T 100 > /dev/null 2>&1; then
  say "building the seed-42 $T bank (as the A40 BANK card)"
  for i in $(seq 1 60); do
    $PY scripts/memory_v2/official_scenes.py complete $BANK $T 100 && break
    CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online plan --seed 42 --episodes 100 --tasks $T --output $BANK >> $C/swaptdiag_bank.log 2>&1 && continue
    $PY scripts/memory_v2/official_scenes.py skip-expert-error $BANK $T; [ $? -eq 1 ] && { say "bank: skip-expert-error failed"; exit 1; }
  done
  $PY scripts/memory_v2/official_scenes.py complete $BANK $T 100 || { say "bank not complete: stop"; exit 1; }
fi
say "bank $BANK complete"
declare -A CK
for L in swapT_ar_e30 swapT_arprop_e30; do
  CK[$L]=$(export_of $L) || true
  [ -n "${CK[$L]}" ] || { say "$L: no checked export: stop"; exit 1; }
done
mkdir -p $OUT
run() {     # label, limit
  for pass in 1 2; do
    MWAM_OBJECT_LOG=1 CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint ${CK[$1]} --label $1 --scenes $BANK \
      --tasks $T --limit $2 --execute 8 --output $OUT >> $C/swaptdiag_$1.log 2>&1
    say "$1 scenes 1-$2 pass $pass exit code $?; episodes with a result $(ls $OUT/$1/on/$T/seed_*/result.json 2>/dev/null | wc -l)"
  done
}
for L in swapT_ar_e30 swapT_arprop_e30; do run $L 10; done
say "===== measurements of the first 10 episodes per model (the classes are fixed from these)"
$PY scripts/fullft/swapT_split.py --first 10 swaptdiag:swapT_ar_e30 swaptdiag:swapT_arprop_e30
for L in swapT_ar_e30 swapT_arprop_e30; do run $L 50; done
say "scenes 1-50 done for both; the split itself runs once the classes are committed (swapT_split.py)"
