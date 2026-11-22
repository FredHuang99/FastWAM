#!/usr/bin/env bash
# Old H200 HOST (outside the container), 11-22 03:50 (Opus; the user is away until Monday morning, 11-22 03:36).
# The container mwam2 lost its GPU management library again (nvidia-smi: "Failed to initialize NVML"); the training
# keeps running, but the queue's next pick waits on nvidia-smi forever. This does the 11-20 17:13 procedure by itself,
# once, after E9 (ar2_arev) is done:
#   1 every 10 min: E9 has SUMMARY.json, and its e30 export is relayed (.relayed_e30: the only one the A40 cards fetch;
#     11-22 13:10 change: e10 never got its marker (the relay was full on 11-21), so waiting for all three would idle the
#     GPU 3 h; at most 3 h for e30, then it goes on), and no fullft trainer runs in the container
#   2 on the host: GPU0 has < 2000 MiB in use (GPU0 is ours; nothing else is touched)
#   3 docker restart mwam2; inside: nvidia-smi must see GPU0 (else stop and log)
#   4 inside: the timer pull (auto_pull.sh start) and the training queue (h200_queue.sh) -> the queue's next line
#     (ranking_arprop: 80 entries, gate GO_ranking_arprop + ranking_ready.sh; then the later lines)
# Gives up after 48 h. Log: ~/mwam_h200_after_e9.log (the nohup redirect).
#   docker exec mwam2 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && nohup bash -c "$(docker exec mwam2 cat /workspace/FastWAM-memory2/scripts/fullft/h200_after_e9.sh)" > ~/mwam_h200_after_e9.log 2>&1 &
set -u
C=mwam2
R=/workspace/FastWAM-memory2
RUN=ar2_arev
say() { echo "[after-e9] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
inside() { docker exec $C bash -c "$1"; }
say "start (host $(hostname)); waiting for $RUN"
t0=$(date +%s); seen=""
while :; do
  [ $(( $(date +%s) - t0 )) -gt $(( 48 * 3600 )) ] && { say "48 h passed without the conditions: giving up (nothing done)"; exit 1; }
  if inside "test -f $R/outputs/fullft/$RUN/SUMMARY.json"; then
    [ -n "$seen" ] || { seen=$(date +%s); say "$RUN SUMMARY.json found"; }
    missing=""
    for tag in e30; do inside "test -f $R/outputs/fullft/$RUN/.relayed_$tag" || missing="$missing $tag"; done
    for tag in e10 e20; do inside "test -f $R/outputs/fullft/$RUN/.relayed_$tag" || say "(note: $tag not relayed; not waited for)"; done
    if [ -n "$missing" ] && [ $(( $(date +%s) - seen )) -lt 10800 ]; then
      say "exports not relayed yet:$missing; waiting"; sleep 600; continue
    fi
    [ -n "$missing" ] && say "3 h after SUMMARY.json still not relayed:$missing (going on; they stay on disk)"
    if inside "pgrep -f fastwam.fullft.train > /dev/null"; then say "a fullft trainer runs in $C; waiting"; sleep 600; continue; fi
    used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0 2>/dev/null | tr -d ' ')
    if ! [[ "$used" =~ ^[0-9]+$ ]] || [ "$used" -ge 2000 ]; then say "host GPU0 in use or unreadable ($used MiB); waiting"; sleep 600; continue; fi
    say "GPU0 $used MiB on the host; restarting $C"
    docker restart $C || { say "docker restart FAILED"; exit 1; }
    sleep 30
    if ! inside "nvidia-smi -i 0 --query-gpu=index,memory.used --format=csv,noheader"; then
      say "nvidia-smi still fails inside $C after the restart: stop (the queue is NOT started)"; exit 1
    fi
    inside "bash $R/scripts/fullft/auto_pull.sh start"
    docker exec -d $C bash $R/scripts/fullft/h200_queue.sh
    say "timer pull and training queue started; in 3 min the queue log:"
    sleep 180
    inside "tail -n 12 \$(ls -t $R/outputs/fullft/H200_QUEUE_*.txt | head -1)"
    say "done"
    exit 0
  fi
  sleep 600
done
