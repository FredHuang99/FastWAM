#!/usr/bin/env bash
# Old H200 HOST, 11-22 23:44 (Opus; user 23:43 pasted the waiter log). Does now, once, what h200_after_e9.sh was to do.
# That waiter cannot get there: (1) two copies run (started 03:40 and 13:10; both write ~/mwam_h200_after_e9.log); (2) its
# "a fullft trainer runs in mwam2" check matches its own shell inside the container (docker exec bash -c "pgrep -f
# fastwam.fullft.train ..." has that text in its command line) [inferred: the host shows GPU0 at 15 MiB, so nothing
# trains; the check below uses the [f] pattern, which cannot match itself].
# Steps (stops at the first failed check; nothing is deleted):
#   1 stop both waiters (ours; matched by the text they were started with); list what is left
#   2 E9 (ar2_arev) has SUMMARY.json and .relayed_e30; no fastwam.fullft.train process in mwam2; host GPU0 < 2000 MiB
#   3 docker restart mwam2; inside, nvidia-smi must see GPU0
#   4 inside: the timer pull and the training queue (h200_queue.sh) -> its next line, the ranking body record (80 entries)
#   5 after 3 min: the queue log
#   docker exec mwam2 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && bash -c "$(docker exec mwam2 cat /workspace/FastWAM-memory2/scripts/fullft/h200_restart_now.sh)" 2>&1 | tee ~/h200_restart_now.log
set -u
C=mwam2
R=/workspace/FastWAM-memory2
say() { echo "[restart] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
inside() { docker exec $C bash -c "$1"; }
P="RUN=ar2_""arev"                 # split so that this script's own command line does not match
say "1 waiters running: $(pgrep -f "$P" | tr '\n' ' ')"
pkill -f "$P"; sleep 2
left=$(pgrep -f "$P" | tr '\n' ' ')
[ -z "$left" ] && say "waiters stopped" || { say "waiters still running: $left; stop"; exit 1; }
say "2 checks"
inside "test -f $R/outputs/fullft/ar2_arev/SUMMARY.json" || { say "no ar2_arev/SUMMARY.json: stop"; exit 1; }
inside "test -f $R/outputs/fullft/ar2_arev/.relayed_e30" || { say "ar2_arev e30 not relayed: stop"; exit 1; }
procs=$(inside "ps -eo pid,etime,cmd | grep -a '[f]astwam.fullft.train' | cut -c1-160")
if [ -n "$procs" ]; then say "trainer processes in $C (nothing restarted):"; echo "$procs"; exit 1; fi
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ')
{ [[ "$used" =~ ^[0-9]+$ ]] && [ "$used" -lt 2000 ]; } || { say "host GPU0 '$used' MiB: stop"; exit 1; }
say "E9 finished and relayed; no trainer in $C; host GPU0 $used MiB"
say "3 docker restart $C"
docker restart $C > /dev/null || { say "docker restart FAILED"; exit 1; }
sleep 30
inside "nvidia-smi -i 0 --query-gpu=index,memory.used --format=csv,noheader" || { say "nvidia-smi still fails inside $C: stop (queue NOT started)"; exit 1; }
say "4 timer pull and training queue"
inside "bash $R/scripts/fullft/auto_pull.sh start"
docker exec -d $C bash $R/scripts/fullft/h200_queue.sh
say "queue started; the queue log in 3 min:"
sleep 180
inside "tail -n 12 \$(ls -t $R/outputs/fullft/H200_QUEUE_*.txt | head -1)"
say "done"
