#!/usr/bin/env bash
# Host-side helper for pool5 (run as root on the A100 or H200 host; copied to /root/mwam_reports/host_pool.sh).
# The container is found automatically (A100: 6e4b37a15066, H200: mwam2, AWS: mwam-aws, 5090: mwam5090); override with C=<name>.
#
#   bash /root/mwam_reports/host_pool.sh status              one screen: GPUs, running tasks (progress, ETA), queue
#   bash /root/mwam_reports/host_pool.sh report [hours]      full report -> /root/mwam_reports/REPORT_*.md (send me)
#   bash /root/mwam_reports/host_pool.sh log <task> [n]      last n lines of a task's job log (+ training stdout)
#   bash /root/mwam_reports/host_pool.sh follow <task>       live view of a task's job log (Ctrl-C leaves, task keeps running)
#   bash /root/mwam_reports/host_pool.sh pool-log [n]        dispatcher log (starts, retries, adoptions, stalls)
#   bash /root/mwam_reports/host_pool.sh update              git pull in the container + refresh this script
#   bash /root/mwam_reports/host_pool.sh start [--lanes L] [--gpus G]   take over from the queue5 lanes, start dispatcher
#   bash /root/mwam_reports/host_pool.sh allow 0,1,2,3       GPUs the pool may use (container indices)
#   bash /root/mwam_reports/host_pool.sh reset A B ...       finished tasks back to pending, attempts reset (after a fix)
#   bash /root/mwam_reports/host_pool.sh pause <gpu>         lend a GPU: stop our task on it (kept for a re-run)
#   bash /root/mwam_reports/host_pool.sh curve D2-pilot-train  in-training eval curve of a running train task
#                                                            (monitoring only; the verdict is judged once, at the end)
#   bash /root/mwam_reports/host_pool.sh stop                stop the dispatcher only (running tasks continue)
#   bash /root/mwam_reports/host_pool.sh deadline ["2026-11-10 20:00"]   show / set queue5/DEADLINE (Beijing time) and
#                                                            move running tasks that kept an older deadline onto it
#                                                            (their jobs keep running; nothing is restarted)
#   bash /root/mwam_reports/host_pool.sh get BOUNDARY2 PRESS_SOURCE ...   copy the newest outputs/memory_v2/report/
#                                                            <NAME>_* file of each name here (send me those)
#   bash /root/mwam_reports/host_pool.sh autopsy PB-events3 ...   rewrite autopsy/AUTOPSY_<id>.md of finished tasks
#                                                            (verdict and ledger unchanged) and copy each here
#   bash /root/mwam_reports/host_pool.sh check [regex]       queue preflight (queue5.py check); with a regex only the
#                                                            matching lines, e.g. check PB- (sets vs the reference run)
set -u
C=${C:-$(docker ps --format '{{.ID}} {{.Names}}' | awk '$1 ~ /^6e4b37a15066/ {print $1} $2 == "mwam2" || $2 == "mwam-aws" || $2 == "mwam5090" {print $2}' | head -1)}
[ -n "$C" ] || { echo "no MemWAM container running here (A100: 6e4b37a15066, H200: mwam2, AWS: mwam-aws, 5090: mwam5090)"; exit 1; }
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
  reset)    for n in "$@"; do
              docker exec "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/queue5.py reset --id $n"
            done ;;
  pause)    pool pause --gpu "$1" ;;
  curve)    docker exec "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/queue5.py curve $*" ;;
  stop)     docker exec "$C" touch "$Q/POOL_STOP"; sleep 45; pool status | head -1 ;;
  deadline) if [ -n "${1:-}" ]; then
              docker exec "$C" /opt/mwam/bin/python -c "import sys; from datetime import datetime; v=sys.argv[1].strip()+' +0800'; datetime.strptime(v, '%Y-%m-%d %H:%M %z'); open('$Q/DEADLINE','w').write(v+chr(10)); print('DEADLINE <-', v)" "$1" || exit 1
              pool readopt --execute
            else
              pool readopt
            fi ;;
  get)      for n in "$@"; do
              f=$(docker exec "$C" bash -lc "ls -t $R/outputs/memory_v2/report/${n}_* 2>/dev/null | grep -v '[.]json$' | head -1")
              if [ -n "$f" ]; then docker cp "$C:$f" "$OUT/" && echo "$n: $OUT/$(basename "$f")  ($(wc -l < "$OUT/$(basename "$f")") lines)"
              else echo "$n: no report yet (task still running? see: bash $OUT/host_pool.sh status)"; fi
            done ;;
  autopsy)  for n in "$@"; do
              docker exec "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/autopsy.py --id $n --no-phase >/dev/null" \
                && docker cp "$C:$R/outputs/memory_v2/autopsy/AUTOPSY_$n.md" "$OUT/" && echo "$n: $OUT/AUTOPSY_$n.md" \
                || echo "$n: autopsy failed (see the lines above)"
            done ;;
  check)    docker exec "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/queue5.py check" 2>&1 \
              | grep -E -- "${1:-.}|^CHECK" ;;
  *)        sed -n '2,27p' "$0" ;;
esac
