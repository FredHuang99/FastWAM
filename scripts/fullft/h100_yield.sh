#!/usr/bin/env bash
# gpu24 / mwam-h100n (user 11-17 19:42 / 19:51): the queue keeps rotating as before (every free GPU, 1-minute rule, we
# never preempt). Only when someone asks for a GPU:
#   h100_yield.sh <gpu>           (a) immediate graceful exit of our training on that GPU: it writes its resume checkpoint
#                                 at the next update and exits (<run>/STOP, the trainer's own stop path); the run goes
#                                 back to its queue line (so it is first again) and resumes from its resume.pt on the next
#                                 free GPU. No freeze: if nobody takes the GPU within the queue's 1-minute rule, our queue
#                                 takes it again.
#   h100_yield.sh <gpu> <hours>   (a) + (b): the GPU is also FROZEN for `hours` (outputs/fullft/H100_HOLD_<gpu>; written
#                                 before the stop): h100_queue.sh does not take it before the freeze ends, and after it
#                                 only by the usual 1-minute rule (still in use by someone -> we just wait).
#   h100_yield.sh hold <gpu> <hours>   (b) alone: freeze the GPU for `hours`, or EXTEND a running freeze by `hours`
#                                 (from its current end); no training is touched.
#   h100_yield.sh any [hours]     (a) [+ (b)] for our training that comes last in h100_queue.txt
#   h100_yield.sh list            our trainings per GPU (progress), memory in use, freezes
#   h100_yield.sh release <gpu>   end a freeze now
# Steps of a yield: [the freeze first;] the run's launcher (it would retry a stopped run at once on the next free GPU)
# is stopped and the run's QUEUE_GPU points at the trainer itself, so no dispatcher starts the run twice meanwhile;
# STOP; wait (at most 40 min: one update ~17 s, the checkpoint write a few minutes) until the trainer has exited; STOP and
# QUEUE_GPU removed; a line in <run>/YIELDS. Works for runs started by any dispatcher version. Nothing is deleted.
#   docker exec mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/h100_yield.sh 2
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
QF=${QF:-$R/scripts/fullft/h100_queue.txt}
GPUS=${GPUS:-"0 1 2 3"}
WAIT_MIN=${WAIT_MIN:-40}
alive() { [ -f "$1" ] && kill -0 "$(cut -d' ' -f2 "$1")" 2>/dev/null; }
run_on() { local f; for f in $OUT/*/QUEUE_GPU; do alive "$f" && [ "$(cut -d' ' -f1 "$f")" = "$1" ] && basename "$(dirname "$f")"; done; }
progress() { grep -ao 'u [0-9]*/[0-9]*' $OUT/QUEUE_$1.log 2>/dev/null | tail -1; }
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '; }
hold_txt() {
  local u; u=$( { tr -dc '0-9' < $OUT/H100_HOLD_$1; } 2>/dev/null )
  [ -n "$u" ] && [ "$(date +%s)" -lt "$u" ] && echo "frozen for others until $(date -d @$u '+%m-%d %H:%M')"
}

case "${1:-}" in
  list)
    for g in $GPUS; do
      r=$(run_on $g)
      if [ -n "$r" ]; then w="ours: $r ($(progress $r))"; else w="not ours"; fi
      echo "GPU $g: $(used $g) MiB; $w $(hold_txt $g)"
    done
    exit 0 ;;
  release)
    g=${2:?gpu}; rm -f $OUT/H100_HOLD_$g; echo "GPU $g: freeze ended"; exit 0 ;;
  hold)
    g=${2:?gpu}; h=${3:?hours}; now=$(date +%s)
    u=$( { tr -dc '0-9' < $OUT/H100_HOLD_$g; } 2>/dev/null ); [ -n "$u" ] && [ "$u" -gt "$now" ] || u=$now
    u=$(( u + ${h%.*} * 3600 )); echo $u > $OUT/H100_HOLD_$g
    echo "GPU $g: frozen for others until $(date -d @$u '+%F %T') (our queue does not take it before; after it only if free)"
    exit 0 ;;
  any)
    g=""
    while IFS='|' read -r run _; do
      run=$(echo "$run" | xargs)
      case "$run" in ''|\#*) continue;; esac
      alive $OUT/$run/QUEUE_GPU && g=$(cut -d' ' -f1 $OUT/$run/QUEUE_GPU)
    done < $QF
    [ -n "$g" ] || { echo "no training of ours is running: nothing to yield"; exit 0; } ;;
  [0-9]*) g=$1 ;;
  *) sed -n 2,21p "$0"; exit 2 ;;
esac
H=${2:-0}
LOG=$OUT/H100_YIELD_$(date +%Y%m%d_%H%M%S)_gpu$g.txt
exec > >(tee -a "$LOG") 2>&1
if [ "${H%.*}" -gt 0 ] 2>/dev/null; then
  bash $R/scripts/fullft/h100_yield.sh hold $g $H | sed 's/^/[yield] /'
  frz="frozen until $(date -d @$(cat $OUT/H100_HOLD_$g) '+%m-%d %H:%M')"
else
  frz="not frozen (our queue takes it again after its 1-minute rule if nobody uses it)"
fi
run=$(run_on $g | head -1)
if [ -z "$run" ]; then
  echo "[yield] no training of ours on GPU $g ($(used $g) MiB in use): nothing to stop; GPU $g $frz"; exit 0
fi
f=$OUT/$run/QUEUE_GPU
sub=$(cut -d' ' -f2 $f)
tr=$(pgrep -P $sub -f "fastwam.fullft.train train" | head -1)
echo "[yield] $run on GPU $g: launcher pid $sub, trainer pid ${tr:-none} ($(progress $run))"
if [ -z "$tr" ]; then                       # the launcher sits between two attempts: no trainer to stop
  kill $sub 2>/dev/null; rm -f $f
  echo "[yield] $(date '+%F %T') $run: launcher stopped between attempts; the run is back in the queue"
  echo "$(date '+%F %T') yielded GPU $g (between attempts)" >> $OUT/$run/YIELDS; exit 0
fi
echo "$g $tr" > $f                          # the run stays 'running' (by its trainer) while it saves
kill $sub 2>/dev/null                       # its launcher would retry the stopped run on the next free GPU
touch $OUT/$run/STOP
echo "[yield] $(date '+%F %T') STOP written; waiting for the checkpoint and the exit (at most $WAIT_MIN min)"
for i in $(seq 1 $(( WAIT_MIN * 6 ))); do
  kill -0 $tr 2>/dev/null || break
  [ $(( i % 12 )) = 0 ] && echo "[yield] $(date '+%T') still saving / running: $(tail -n 1 $OUT/QUEUE_$run.log | cut -c1-150)"
  sleep 10
done
if kill -0 $tr 2>/dev/null; then
  echo "[yield] the trainer has not exited after $WAIT_MIN min; it keeps GPU $g. STOP stays (it will stop at its next"
  echo "        update); look at $OUT/QUEUE_$run.log, then run this again"
  exit 1
fi
rm -f $OUT/$run/STOP $f
last=$(grep -a 'resume checkpoint saved at update' $OUT/QUEUE_$run.log | tail -1 | grep -o 'update [0-9]*')
grep -aq 'STOP found' <(tail -n 20 $OUT/QUEUE_$run.log) && ok="saved and exited" || ok="EXITED WITHOUT the STOP line (check the log)"
echo "$(date '+%F %T') yielded GPU $g: $ok, resume.pt at $last" >> $OUT/$run/YIELDS
echo "[yield] $(date '+%F %T') $run: $ok; resume.pt at $last. GPU $g now $(used $g) MiB, $frz."
echo "[yield] $run is back in the queue and resumes from that checkpoint on the next free GPU (h100_queue.sh must run)"
