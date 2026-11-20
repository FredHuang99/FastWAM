#!/usr/bin/env bash
# mwam-h100n (gpu24), 11-20 17:30 BJ (Opus; user 17:04: "E15 停；且 graceful"). Run once, detached; safe to run again.
# The 11-20 log pack showed rearrange_arprop and swapT_arprop FAILED twice each on 11-18 / 11-19: the dispatcher's main
# loop and a launcher's resumed retry picked the same free GPU within a minute, both trainers ran out of memory. Fixed
# in h100_queue.sh (atomic GPU claim). Steps:
#   1 stop the running dispatcher's main loop (QUEUE_STOP_H100; it ends at its next look, <= 10 min). Running trainers
#     (rearrange_clock, swapT_clock, battery_count) are not touched by this.
#   2 the two FAILED markers are renamed (kept as QUEUE_FAILED_20261119), so the two lines are picked again
#   3 E15 battery_count: graceful yield (h100_yield.sh <its GPU>: resume.pt written at the next update, then exit); its
#     queue line now waits for outputs/fullft/GO_battery_count, so nothing restarts it
#   4 a new dispatcher with the fixed h100_queue.sh; it picks rearrange_arprop (first in the file) for the GPU E15 left,
#     swapT_arprop for the next free one (swapT_clock ends ~11-21 03:30 BJ)
#   docker exec -d mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/h100_v15b.sh
# Log: outputs/fullft/H100_V15B_<time>.txt (step by step; the last lines are h100_yield.sh list and the new plan)
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
cd $R
LOG=$OUT/H100_V15B_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[v15b] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
alive() { [ -f "$1" ] && kill -0 "$(cut -d' ' -f2 "$1")" 2>/dev/null; }
say "checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-70)"
grep -q "H100_CLAIM_" scripts/fullft/h100_queue.sh || { say "h100_queue.sh has no GPU claim yet (git pull first): stop"; exit 1; }
grep -q "GO_battery_count" scripts/fullft/h100_queue.txt || { say "the queue file has no E15 gate yet (git pull first): stop"; exit 1; }

# 1 the running dispatcher
if [ -f $OUT/H100_QUEUE.pid ] && kill -0 "$(cat $OUT/H100_QUEUE.pid)" 2>/dev/null; then
  P=$(cat $OUT/H100_QUEUE.pid)
  L=$(ls -t $OUT/H100_QUEUE_2*.txt | grep -v _dry | head -1)
  say "1 dispatcher pid $P (log $L) is running: writing QUEUE_STOP_H100"
  touch $OUT/QUEUE_STOP_H100
  for i in $(seq 1 90); do grep -q "QUEUE_STOP_H100 found" "$L" && break; sleep 10; done
  grep -q "QUEUE_STOP_H100 found" "$L" || { say "it did not stop its main loop within 15 min: nothing else done"; exit 1; }
  say "1 its main loop has ended ($(grep -h 'QUEUE_STOP_H100 found' "$L" | tail -1))"
else
  say "1 no dispatcher main loop is running"
fi

# 2 the two lost ledger runs back into the queue (nothing deleted)
for r in rearrange_arprop swapT_arprop; do
  if [ -f $OUT/$r/QUEUE_FAILED ]; then
    mv $OUT/$r/QUEUE_FAILED $OUT/$r/QUEUE_FAILED_20261119 && say "2 $r: QUEUE_FAILED -> QUEUE_FAILED_20261119 (re-queued)"
  else
    say "2 $r: no QUEUE_FAILED (already re-queued or finished: $(ls $OUT/$r/SUMMARY.json 2>/dev/null || echo 'no SUMMARY'))"
  fi
  [ -f $OUT/$r/resume.pt ] && say "2 $r: a resume.pt exists, the run resumes from it" || say "2 $r: no resume.pt, the run starts from update 0"
done

# 3 E15: graceful stop
if alive $OUT/battery_count/QUEUE_GPU; then
  g=$(cut -d' ' -f1 $OUT/battery_count/QUEUE_GPU)
  say "3 battery_count trains on GPU $g: graceful yield (resume.pt at the next update; at most 40 min)"
  bash scripts/fullft/h100_yield.sh $g
  say "3 yield exit code $?; battery_count/YIELDS: $(tail -n 1 $OUT/battery_count/YIELDS 2>/dev/null)"
else
  say "3 battery_count is not training (nothing to yield)"
fi

# 4 the fixed dispatcher
rm -f $OUT/QUEUE_STOP_H100
if [ -f $OUT/H100_QUEUE.pid ] && kill -0 "$(cat $OUT/H100_QUEUE.pid)" 2>/dev/null; then
  say "4 a dispatcher runs already (pid $(cat $OUT/H100_QUEUE.pid)): not starting another"
else
  setsid bash $R/scripts/fullft/h100_queue.sh > /dev/null 2>&1 < /dev/null &
  sleep 150
  L=$(ls -t $OUT/H100_QUEUE_2*.txt | grep -v _dry | head -1)
  say "4 new dispatcher pid $(cat $OUT/H100_QUEUE.pid 2>/dev/null); its log $L:"
  tail -n 12 "$L"
fi
bash scripts/fullft/h100_yield.sh list
say "done; log $LOG"
