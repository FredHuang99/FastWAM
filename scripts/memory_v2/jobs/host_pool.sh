#!/usr/bin/env bash
# Host-side helper for pool5 (run as root on the A100 or H200 host; copied to /root/mwam_reports/host_pool.sh).
# The container is found automatically (A100: 6e4b37a15066, H200: mwam2); override with C=<name>.
#
#   bash /root/mwam_reports/host_pool.sh status              one screen: GPUs, running tasks (progress, ETA), queue
#   bash /root/mwam_reports/host_pool.sh report [hours]      full report -> /root/mwam_reports/REPORT_*.md (send me)
#   bash /root/mwam_reports/host_pool.sh log <task> [n]      last n lines of a task's job log (+ training stdout)
#   bash /root/mwam_reports/host_pool.sh follow <task>       live view of a task's job log (Ctrl-C leaves, task keeps running)
#   bash /root/mwam_reports/host_pool.sh pool-log [n]        dispatcher log (starts, retries, adoptions, stalls)
#   bash /root/mwam_reports/host_pool.sh update              git pull in the container + refresh this script
#   bash /root/mwam_reports/host_pool.sh start [--lanes L] [--gpus G]   take over from the queue5 lanes, start dispatcher
#   bash /root/mwam_reports/host_pool.sh allow 0,1,2,3       GPUs the pool may use (container indices)
#   bash /root/mwam_reports/host_pool.sh pause <gpu>         lend a GPU: stop our task on it (kept for a re-run)
#   bash /root/mwam_reports/host_pool.sh stop                stop the dispatcher only (running tasks continue)
set -u
C=${C:-$(docker ps --format '{{.ID}} {{.Names}}' | awk '$1 ~ /^6e4b37a15066/ {print $1} $2 == "mwam2" {print $2}' | head -1)}
[ -n "$C" ] || { echo "no MemWAM container running here (A100: 6e4b37a15066, H200: mwam2)"; exit 1; }
R=/workspace/FastWAM-memory2
Q=$R/outputs/memory_v2/queue5
OUT=/root/mwam_reports
mkdir -p $OUT
pool() { docker exec "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/pool5.py $*"; }
cmd=${1:-status}; shift || true
case "$cmd" in
  status)   pool status ;;
  report)   f=$(pool report --hours "${1:-12}" | tail -1)
            docker cp "$C:$f" "$OUT/" && echo "REPORT: $OUT/$(basename "$f")  ($(wc -l < "$OUT/$(basename "$f")") lines)" ;;
  log)      pool log --id "$1" --lines "${2:-60}" ;;
  follow)   docker exec -it "$C" tail -n 30 -f "$Q/tasks/$1.log" ;;
  pool-log) docker exec "$C" tail -n "${1:-60}" "$Q/pool.log" ;;
  update)   docker exec "$C" bash -lc "cd $R && git -c safe.directory='*' pull --ff-only origin memory2 >/dev/null && git -c safe.directory='*' log --oneline -1" \
              && docker cp "$C:$R/scripts/memory_v2/jobs/host_pool.sh" "$OUT/host_pool.sh" && echo "host_pool.sh refreshed" ;;
  start)    pool start "$@" ;;
  allow)    pool allow --gpus "$1" ;;
  pause)    pool pause --gpu "$1" ;;
  stop)     docker exec "$C" touch "$Q/POOL_STOP"; sleep 45; pool status | head -1 ;;
  *)        sed -n '2,16p' "$0" ;;
esac
