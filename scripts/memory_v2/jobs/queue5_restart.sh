#!/usr/bin/env bash
# Restart queue5 lanes inside the policy container. Only the lane process is replaced: a task it was running keeps
# running in its own session; the new lane waits for that process, re-runs the task (finished episodes / checkpoints
# reused) and judges it. The new lane reads the deadline (QUEUE_DEADLINE or outputs/memory_v2/queue5/DEADLINE) and the
# current code.
#   bash scripts/memory_v2/jobs/queue5_restart.sh loop:1 train:2 extra:3 gpu0:0 cpu:
set -u
Q=/workspace/FastWAM-memory2/outputs/memory_v2/queue5
J=/workspace/FastWAM-memory2/scripts/memory_v2/jobs
for spec in "$@"; do
  lane=${spec%%:*}; gpu=${spec#*:}
  pid=$(/opt/mwam/bin/python -c "import json; print(json.load(open('$Q/lanes/$lane.json')).get('pid', ''))" 2>/dev/null)
  if [ -n "$pid" ] && tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q "queue5.py run --lane $lane"; then
    kill -TERM "$pid"
    # a killed lane whose parent does not reap it stays a zombie (state Z): that counts as exited
    alive() { [ -e "/proc/$1" ] && ! awk '{exit ($3 == "Z") ? 0 : 1}' "/proc/$1/stat" 2>/dev/null; }
    for _ in $(seq 1 30); do alive "$pid" || break; sleep 1; done
    if alive "$pid"; then echo "lane $lane: pid $pid did not exit; NOT restarted"; continue; fi
    echo "lane $lane: stopped lane process $pid"
  else
    echo "lane $lane: no live lane process (recorded pid '$pid')"
  fi
  setsid nohup bash "$J/queue5.sh" "$lane" $gpu > /dev/null 2>&1 < /dev/null &
  echo "lane $lane: started (GPU ${gpu:-none})"
done
sleep 30
bash "$J/queue5.sh" status | grep -E "^== queue5|^  lane "
