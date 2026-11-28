#!/usr/bin/env bash
# HOST side, 11-28 16:15 (Opus; plan v22b part 3 section 5, user steps 1 and 2). Restart one of our training
# containers whose nvidia-smi fails ("Failed to initialize NVML: Unknown Error", seen in every snapshot of the old H200
# and the H100 since at least 11-27 12:36), then bring its daemons back: the timer pull (auto_pull.sh), the results
# push (results_push.sh) and the training queue (h200_queue.sh / h100_queue.sh, through ensure_runner.sh).
# Same steps as h200_restart_now.sh (11-22), without its E9-specific checks. Stops at the first failed check; deletes
# nothing; touches no process of anyone else (only our own container is restarted).
#   usage (on the host; the script is read from inside the container after a git pull):
#     C=<container> M=<h200o|h100> bash -c "$(docker exec <container> cat /workspace/FastWAM-memory2/scripts/fullft/container_restart.sh)"
#   steps:
#     1 inside: no training, export upload or cache fetch running (else stop); C must be the machine M's container
#     2 docker restart; wait 30 s
#     3 inside: nvidia-smi must list the GPUs (old H200: GPU0; H100: GPUs 0-3); else stop (daemons NOT started)
#     4 inside: auto_pull.sh start; results_push.sh restart; ensure_runner.sh <M>
#     5 after 3 min: the queue log tail and the three daemons' status
# Log (host): ~/container_restart_<M>_<time>.log
set -u
C=${C:?container name, e.g. C=mwam2}
M=${M:?machine, h200o or h100}
R=/workspace/FastWAM-memory2
LOG=$HOME/container_restart_${M}_$(date +%Y%m%d_%H%M).log
exec > >(tee -a "$LOG") 2>&1
say() { echo "[restart] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
inside() { docker exec $C bash -c "$1"; }
case $M in
  h200o) Q=h200_queue.sh; QL="H200_QUEUE_*.txt"; GPUQ="-i 0";;
  h100)  Q=h100_queue.sh; QL="H100_QUEUE_*.txt"; GPUQ="";;
  *) say "M must be h200o or h100"; exit 2;;
esac
say "container $C, machine $M; code inside: $(inside "git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-60")"
say "1 a training, an export upload or a cache fetch running inside $C?"
# 11-28 code audit: a failed docker exec must not read as "nothing running"; uploads / fetches count too (their
# exports would stay off the relay; relay_retry.sh, started by results_push.sh once, retries only what failed)
procs=$(inside "ps -eo pid,etime,cmd | grep -aE '[f]astwam.fullft.train|[e]xport_watch|[e]xport_relay|[r]elay.py put|[c]ache_relay' | cut -c1-160") \
  || { say "docker exec into $C failed: stop (nothing restarted)"; exit 1; }
if [ -n "$procs" ]; then say "processes that a restart would kill, in $C (nothing restarted):"; echo "$procs"; exit 1; fi
want=$([ $M = h200o ] && echo mwam2 || echo mwam-h100n)
[ "$C" = "$want" ] || { say "container $C does not belong to machine $M (expected $want): stop"; exit 1; }
say "none; nvidia-smi inside before the restart: $(inside "nvidia-smi -L 2>&1 | head -1")"
say "2 docker restart $C"
docker restart $C > /dev/null || { say "docker restart FAILED"; exit 1; }
sleep 30
say "3 nvidia-smi inside after the restart:"
if ! inside "nvidia-smi $GPUQ --query-gpu=index,name,memory.used --format=csv,noheader"; then
  say "nvidia-smi still fails inside $C: stop (daemons NOT started). The host's own nvidia-smi:"
  nvidia-smi --query-gpu=index,name,memory.used --format=csv,noheader 2>&1 | head -8
  exit 1
fi
say "4 daemons"
inside "bash $R/scripts/fullft/auto_pull.sh start"
inside "bash $R/scripts/fullft/results_push.sh restart"
inside "bash $R/scripts/fullft/ensure_runner.sh $M"
say "5 waiting 3 min, then the queue log"
sleep 180
inside "tail -n 12 \$(ls -t $R/outputs/fullft/$QL | head -1)"
inside "bash $R/scripts/fullft/results_push.sh status | head -2; pgrep -fa 'scripts/fullft/(auto_pull|$Q)' | cut -c1-120"
say "done; log $LOG"
