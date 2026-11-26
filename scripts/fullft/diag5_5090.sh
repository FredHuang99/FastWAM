#!/usr/bin/env bash
# mwam5090, 11-27 02:10 (Opus; plan v21 6.5 diagnostic 5, zero training, DESCRIBED ONLY). One script, one part per call:
#   PART=b1   (cpu) swapT_diag5_5090.py b --first 10: measurements of the first 10 back-at-own-start episodes of card 11
#             (closed_loop/swaptdiag) per model + 5 successes; the classes are fixed from these (Status), then PART=b
#   PART=b    (cpu) the full (b) run (refuses until CLASSES_5B is set in swapT_diag5_5090.py)
#   PART=d    (cpu) swapT_diag5_5090.py d: release pose of each arm from the other arm's grasp readings, 50 demos
#   PART=c    (gpu) obs_probe.py --task swap_T --window carry: frame-0 swap while both blocks are carried, trained (45) and
#             held-out (5) demos, swapT_ar e30 and swapT_arprop e30 (2 % line, obs_probe's rule)
# Read-only. Exports: here, else the relay mirror, else the relay (sha256 checked). The body-record probe needs swap_T's
# events file (rule A, relay diag/events_b1) and the dense cache dense_swap_T_v1 (cache relay): fetched if missing.
#   q5090.txt lines: diag5-b1 | cpu | ... ; diag5-d | cpu | ... ; diag5-c | gpu | ...
# Own log: outputs/fullft/DIAG5_5090_<part>_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
PART=${PART:?PART=b1|b|c|d}
LOG=$F/DIAG5_5090_${PART}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[d5] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
echo "[d5] $(date '+%F %T') part $PART; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
case $PART in
  b1) $PY scripts/fullft/swapT_diag5_5090.py b --first 10 ;;
  b)  $PY scripts/fullft/swapT_diag5_5090.py b ;;
  d)  $PY scripts/fullft/swapT_diag5_5090.py d ;;
  c)
    G=${GPU:-${PF_GPUS:-1}}
    EV=$F/events/events_swap_T.json
    if [ ! -s $EV ]; then
      M=/mnt/hf/relay_mirror/memwam-diag-v1/diag/events_b1/events_swap_T.json
      if [ -s $M ]; then mkdir -p $F/events && cp $M $EV
      else IN=$F/relay_in/events_b1; mkdir -p $IN $F/events
           $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_b1 --out $IN 2>&1 | grep "\[relay\]" | tail -n 2
           [ -s $IN/events_swap_T.json ] && cp $IN/events_swap_T.json $EV; fi
    fi
    [ -s $EV ] || { echo "[d5] no events_swap_T.json (relay diag/events_b1): the body-record probe cannot run"; exit 1; }
    echo "[d5] events $EV sha256 $(sha256sum $EV | cut -c1-16)"
    D=$R/outputs/memory_v2/press/dense_swap_T_v1
    if [ ! -f $D/.verified ]; then
      HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/fullft/cache_relay.py get --name dense_swap_T_v1 --dest $(dirname $D) 2>&1 | tail -n 3
      [ ${PIPESTATUS[0]} -eq 0 ] && touch $D/.verified || { echo "[d5] dense_swap_T_v1 not fetched / verified"; exit 1; }
    fi
    for L in swapT_ar_e30 swapT_arprop_e30; do
      E=$F/exports/$L; M=/mnt/hf/relay_mirror/memwam-fullft/exports/$L
      if [ ! -f $E/export_e30.pt ] && [ -f $M/export_e30.pt ]; then E=$M; fi
      if [ ! -f $E/export_e30.pt ]; then RUN=${L%_e30} TAG=e30 POLL=60 bash scripts/fullft/export_fetch.sh || { echo "[d5] $L: fetch failed"; exit 1; }; E=$F/exports/$L; fi
      (cd $E && sha256sum -c --quiet export_e30.pt.sha256) || { echo "[d5] $L sha256 mismatch"; exit 1; }
      for S in val train; do
        n=6; [ $S = val ] && n=20
        echo "[d5] $(date '+%F %T') $L split $S window carry"
        CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $E/export_e30.pt --task swap_T --window carry \
          --split $S --choice $n 2>&1 | grep -v "Warning\|warn(\|^  [0-9]*/[0-9]*$"
      done
    done ;;
  *) echo "[d5] unknown PART $PART"; exit 2 ;;
esac
echo "[d5] $(date '+%F %T') DIAG 5 part $PART done"
