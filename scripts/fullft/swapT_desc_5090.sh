#!/usr/bin/env bash
# mwam5090, 11-28 (Opus; plan v22 1.2 / 4.3: card 9b's failure split and diagnostic 12; reused for cards 36 / 36b).
# Zero training, DESCRIBED ONLY (the 5090 is its own comparison group). For one export RUN_TAG:
#   1 the export (here, else the relay mirror, else the relay through export_fetch.sh; sha256 checked)
#   2 closed loop on the official seed-42 swap_T bank, scenes 1-50, execute 8, MWAM_OBJECT_LOG=1 (T-block poses and
#     orientations, both end-effectors), closed_loop/swaptdiag/<RUN>_<TAG> -- the same setting as card 11's episodes
#   3 swapT_split.py with card 11's classes (fixed 11-24) -> outputs/fullft/SWAPT_SPLIT_<RUN>_<TAG>.json
#   4 diagnostic 12 measurements: swapT_diag5_5090.py e (--first 10 until CLASSES_12 is set; full afterwards)
#   q5090.txt: <id> | gpu1 | bash scripts/fullft/relay_has.sh <RUN>_<TAG> | export GPU=$(bash scripts/fullft/cuda_ordinal.sh $GPU); RUN=<RUN> TAG=<TAG> bash scripts/fullft/swapT_desc_5090.sh
# Own log: outputs/fullft/SWAPT_DESC_5090_<RUN>_<TAG>_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
RUN=${RUN:?RUN=<training>}; TAG=${TAG:-e30}
L=${RUN}_${TAG}
LOG=$F/SWAPT_DESC_5090_${L}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[swd] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK
PY=/opt/mwam/bin/python
T=swap_T
C=$O/closed_loop
BANK=$C/scenes_seed42_n100_$T
OUT=$C/swaptdiag
G=${GPU:-1}
say() { echo "[swd] $(date '+%F %T') $*"; }
say "start $L; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
$PY scripts/memory_v2/official_scenes.py complete $BANK $T 100 > /dev/null 2>&1 || { say "the seed-42 swap_T bank is not complete here: stop"; exit 1; }
E=$F/exports/$L; M=/mnt/hf/relay_mirror/memwam-fullft/exports/$L
if [ ! -f $E/export_$TAG.pt ] && [ -f $M/export_$TAG.pt ]; then E=$M; fi
if [ ! -f $E/export_$TAG.pt ]; then RUN=$RUN TAG=$TAG POLL=60 bash scripts/fullft/export_fetch.sh || { say "$L: fetch failed"; exit 1; }; E=$F/exports/$L; fi
(cd $E && sha256sum -c --quiet export_$TAG.pt.sha256) || { say "$L: sha256 mismatch"; exit 1; }
mkdir -p $OUT
for pass in 1 2; do
  MWAM_OBJECT_LOG=1 CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $E/export_$TAG.pt --label $L \
    --scenes $BANK --tasks $T --limit 50 --execute 8 --output $OUT >> $C/swaptdiag_$L.log 2>&1
  rc=$?
  n=$(ls $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | wc -l)
  say "scenes 1-50 pass $pass exit code $rc; episodes with a result $n"
  [ $n -ge 50 ] && break
done
[ $n -ge 50 ] || { say "only $n of 50 episodes: stop (no split)"; exit 1; }
$PY scripts/fullft/swapT_split.py swaptdiag:$L --out SWAPT_SPLIT_$L.json || { say "split failed"; exit 1; }
if $PY -c "import importlib.util as u,sys; s=u.spec_from_file_location('d','scripts/fullft/swapT_diag5_5090.py'); m=u.module_from_spec(s); s.loader.exec_module(m); sys.exit(0 if m.CLASSES_12 else 1)"; then
  $PY scripts/fullft/swapT_diag5_5090.py e --items swaptdiag:$L
else
  $PY scripts/fullft/swapT_diag5_5090.py e --first 10 --items swaptdiag:$L
fi
say "SWAPT DESC $L done"
