#!/usr/bin/env bash
# mwam-h100n (gpu24), 11-17 evening (user 19:42: the queue keeps taking every free GPU, h100_yield.sh frees one when
# someone needs it; both arms of a task train on the H100 = deviation 39 stays). Restart the training queue with the
# current code, and prepare the ledger side of the four B1 tasks. Run after `git pull`; safe to run again.
#   1 the previous dispatcher: its main loop must have ended (QUEUE_STOP_H100 since 14:35); if its log does not say so,
#     the stop marker is written and this waits for it (at most 12 min). Its running trainers are not touched.
#   2 the GPU share sampler (gpu_share.sh start; information only)
#   3 a new dispatcher (h100_queue.sh), unless one runs already (outputs/fullft/H100_QUEUE.pid)
#   4 in the background (log outputs/fullft/H100_B1_READY_<time>.txt): the event files of the four B1 tasks from the
#     relay (diag/events_b1, put there by the 5090 on 11-17) into outputs/fullft/events/ (an existing file is never
#     overwritten), then ledger_ready.py per task (unit tests once; CPU only, no GPU visible); every task that passes is
#     added to outputs/fullft/READY_arprop (the tasks already in it stay, battery_try included). The queue lines
#     rearrange_arprop / swapT_arprop / cover_arprop / ranking_arprop wait for exactly this (ranking also for G2').
#   docker exec mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/h100_restart.sh
set -u
R=${R:-/workspace/FastWAM-memory2}
PYM=${PYM:-/opt/mwam/bin/python}
OUT=$R/outputs/fullft
cd $R
B1="rearrange_blocks swap_T cover_blocks blocks_ranking_try"

if [ "${1:-}" = ready ]; then                                   # step 4, detached
  export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=4
  HFPY=${HFPY:-/opt/hf-tools/bin/python}; [ -x $HFPY ] || HFPY=$PYM
  IN=$OUT/relay_in/events_b1; mkdir -p $IN $OUT/events
  echo "[b1] $(date '+%F %T') relay get diag/events_b1 ($HFPY)"
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_b1 --out $IN 2>&1 | tail -n 6
  ls -la $IN
  for f in $IN/events_*.json; do
    [ -s "$f" ] || continue
    t=$OUT/events/$(basename $f)
    if [ -f $t ]; then cmp -s $f $t && echo "[b1] $(basename $f): already in place (same)" \
                                    || echo "[b1] $(basename $f): a DIFFERENT file is in place; kept it, not overwritten"
    else cp $f $t && echo "[b1] $(basename $f): copied"; fi
  done
  first=1
  for task in $B1; do
    if grep -q "\"$task\"" $OUT/READY_arprop 2>/dev/null; then echo "[b1] $task: already in READY_arprop"; continue; fi
    [ -f outputs/memory_v2/press/dense_${task}_v1/.verified ] || { echo "[b1] $task: cache not verified yet, skipped"; continue; }
    [ -s $OUT/events/events_$task.json ] || { echo "[b1] $task: no event file, skipped"; continue; }
    echo "[b1] $(date '+%F %T') ledger_ready $task"
    $PYM scripts/fullft/ledger_ready.py --variant arprop --tasks $task --marker READY_arprop_$task \
      $([ $first = 1 ] || echo --skip-tests) 2>&1 | grep -v '^\.\+$' | tail -n 8
    first=0
    if [ -f $OUT/READY_arprop_$task ]; then
      $PYM - $OUT/READY_arprop $task <<'PY'
import json, sys
from pathlib import Path
p, task = Path(sys.argv[1]), sys.argv[2]
tasks = json.loads(p.read_text())["tasks"] if p.exists() else []
if task not in tasks:
    tasks.append(task)
p.write_text(json.dumps({"tasks": tasks}) + "\n")
print(f"[b1] READY_arprop now: {tasks}")
PY
    else
      echo "[b1] $task: NOT READY (see above); not added"
    fi
  done
  echo "[b1] $(date '+%F %T') done; READY_arprop: $(cat $OUT/READY_arprop 2>/dev/null)"
  exit 0
fi

echo "[restart] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-70)"
# 1 previous dispatcher
if [ -f $OUT/H100_QUEUE.pid ] && kill -0 "$(cat $OUT/H100_QUEUE.pid)" 2>/dev/null; then
  echo "[restart] a current dispatcher runs already (pid $(cat $OUT/H100_QUEUE.pid)): not starting another"; NEW=0
else
  NEW=1
  L=$(ls -t $OUT/H100_QUEUE_2*.txt 2>/dev/null | grep -v _dry | head -1)
  if [ -n "$L" ] && ! grep -q "QUEUE_STOP_H100 found\|dispatcher finished" "$L"; then
    echo "[restart] the previous dispatcher ($L) has not stopped its main loop: writing QUEUE_STOP_H100"
    touch $OUT/QUEUE_STOP_H100
    for i in $(seq 1 72); do grep -q "QUEUE_STOP_H100 found" "$L" && break; sleep 10; done
    grep -q "QUEUE_STOP_H100 found" "$L" || { echo "[restart] it did not stop within 12 min: nothing started"; exit 1; }
  fi
  echo "[restart] previous dispatcher: $(grep -h "QUEUE_STOP_H100 found\|dispatcher finished" "$L" 2>/dev/null | tail -1)"
fi
# 2 sampler
bash scripts/fullft/gpu_share.sh start | head -n 1
# 3 dispatcher
if [ $NEW = 1 ]; then
  setsid bash $R/scripts/fullft/h100_queue.sh > /dev/null 2>&1 < /dev/null &
  sleep 30
  L=$(ls -t $OUT/H100_QUEUE_2*.txt | grep -v _dry | head -1)
  echo "[restart] new dispatcher pid $(cat $OUT/H100_QUEUE.pid 2>/dev/null); its log $L:"
  tail -n 6 "$L"
fi
# 4 B1 ledger readiness, detached
B=$OUT/H100_B1_READY_$(date +%Y%m%d_%H%M).txt
setsid bash $R/scripts/fullft/h100_restart.sh ready > $B 2>&1 < /dev/null &
echo "[restart] B1 event files + readiness checks in the background -> $B"
bash scripts/fullft/h100_yield.sh list
