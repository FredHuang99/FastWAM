#!/usr/bin/env bash
# mwam2 (old H200), 11-17 17:20 (Opus), one-off: carry out deviation 40 / 43 and restart the queue.
#   1 stop the queue loop (the running trainer is not touched by this)   2 STOP press_arev (it saves resume.pt, exits)
#   3 press_fast_ready.sh (fixed 9c79cc5: relay get with /opt/mwam's python) -> READY_press_fast + the fast files in place
#   4 READY_v13 (ledger_ready on the fast events file; plan v13 E4 / E7 lines wait for it)   5 start h200_queue.sh again
# Written as a script because a one-line `docker exec ... bash -lc '...'` that both kills and restarts the queue kills
# itself (its own command line contains the queue script's name). Own log: outputs/fullft/H200_SWITCH_<time>.txt
#   docker exec mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/h200_switch.sh
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/H200_SWITCH_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
cd $R
export PYTHONPATH=$R/src
PY=/opt/mwam/bin/python
echo "[switch] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
echo "[switch] processes now:"; pgrep -af "[f]astwam.fullft.train|[h]200_queue|[e]xport_watch" | cut -c1-140
if pgrep -f "[h]200_queue.sh" >/dev/null; then pkill -f "[h]200_queue.sh"; sleep 2; echo "[switch] queue loop stopped"; fi
if pgrep -f "[n]ame=press_arev" >/dev/null; then
  touch $F/press_arev/STOP
  echo "[switch] $(date '+%T') STOP written for press_arev; waiting for it to save resume.pt and exit (at most 20 min)"
  for i in $(seq 1 120); do pgrep -f "[n]ame=press_arev" >/dev/null || break; sleep 10; done
  pgrep -f "[n]ame=press_arev" >/dev/null && { echo "[switch] press_arev still runs after 20 min: stopping here"; exit 1; }
  tail -n 3 $F/QUEUE_press_arev.log | cut -c1-160
else
  echo "[switch] press_arev is not training"
fi
rm -f $F/press_arev/STOP
echo "[switch] $(date '+%T') press_fast_ready.sh:"
DEBUG=1 bash scripts/fullft/press_fast_ready.sh; echo "[switch] press_fast_ready exit $?"
ls -la $F/READY_press_fast $F/PRESS_FAST_RULE.json $F/events/events_press_button_fast.json 2>&1 | cut -c1-140
if [ -s $F/events/events_press_button_fast.json ]; then
  echo "[switch] $(date '+%T') READY_v13 (unit tests + data checks on the fast events file):"
  $PY scripts/fullft/ledger_ready.py --variant arprop --tasks press_button \
    --events $F/events/events_press_button_fast.json --marker READY_v13 2>&1 | tail -n 5
fi
echo "[switch] $(date '+%T') queue plan:"
DRY=1 bash scripts/fullft/h200_queue.sh 2>&1 | grep -E "waits|next:|nothing" | cut -c1-160
setsid nohup bash scripts/fullft/h200_queue.sh > /dev/null 2>&1 < /dev/null &
sleep 30
echo "[switch] $(date '+%T') queue started; its log:"
tail -n 6 "$(ls -t $F/H200_QUEUE_*.txt | grep -v _dry | head -1)" | cut -c1-160
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader -i 0
echo "[switch] $(date '+%F %T') done; log $LOG"
