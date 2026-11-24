#!/usr/bin/env bash
# mwam-h100n, 11-19 14:00 (Opus; plan v14 E15 / E16, plan v15 E16b, user 18:33 + 11-19 13:21): condition of the H100
# queue lines battery_count / rearrange_clock / swapT_clock (exit 0 = runnable). Cheap when ready (marker
# outputs/fullft/READY_<run>); otherwise at most one attempt per 30 min, CPU only (no GPU visible):
#   battery_count    the battery data checks passed already (READY_arprop has battery_try, the battery_arprop line);
#                    here only the unit tests (they cover the ordinal code: test_ledger.py test_ordinal_*)
#   rearrange_clock  ledger_ready.py --variant arclk --no-events: unit tests + the last 32 text slots are padding in
#   swapT_clock      every episode of the task (the clock tokens are written there; no event file is read)
# The line's own condition also checks the task cache (.verified). Log: outputs/fullft/V15_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
run=${1:?usage: h100_v15_ready.sh <run>}
cd $R
[ -f $F/READY_$run ] && exit 0
T=$F/READY_TRIED_$run
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 1800 ]; then exit 1; fi
touch $T
exec >> $F/V15_READY.log 2>&1
echo "[v15] $(TZ=Asia/Shanghai date '+%F %T') $run: attempt"
PY=/opt/mwam/bin/python
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4
case $run in
  battery_count)
    grep -q '"battery_try"' $F/READY_arprop 2>/dev/null || { echo "[v15] battery_try not in READY_arprop"; exit 1; }
    if $PY -c "import pytest" 2>/dev/null; then
      $PY -m pytest -q -p no:cacheprovider src/fastwam/fullft/tests 2>&1 | tail -n 3
      rc=${PIPESTATUS[0]}
    else
      echo "[v15] WARNING pytest is not installed in this python: unit tests NOT run here (they pass on the other machines)"
      rc=0
    fi
    echo "[v15] unit tests exit code $rc"
    [ $rc -eq 0 ] && echo "{\"tasks\": [\"battery_try\"], \"checks\": \"READY_arprop + unit tests\"}" > $F/READY_$run ;;
  rearrange_clock|swapT_clock|battery_clock)        # 11-24 plan v20 section 5: battery_clock (H100 filler)
    task=rearrange_blocks; [ $run = swapT_clock ] && task=swap_T; [ $run = battery_clock ] && task=battery_try
    $PY scripts/fullft/ledger_ready.py --variant arclk --tasks $task --no-events --marker READY_$run 2>&1 \
      | grep -v '^\.\+$' | tail -n 6 ;;
  *) echo "[v15] unknown run $run"; exit 1 ;;
esac
[ -f $F/READY_$run ] && { echo "[v15] $run READY"; exit 0; }
echo "[v15] $run NOT READY (see above)"; exit 1
