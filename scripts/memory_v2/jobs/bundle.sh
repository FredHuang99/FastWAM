#!/usr/bin/env bash
# Host-side, read-only review bundle of one machine (11-10). Works on any checkout (also the H200's older one): fetch it
# WITHOUT touching the working tree, then run it (container: A100 6e4b37a15066, H200 mwam2, 5090 mwam5090):
#   docker exec <container> bash -lc "cd /workspace/FastWAM-memory2 && git -c safe.directory='*' fetch -q origin memory2 && git -c safe.directory='*' show origin/memory2:scripts/memory_v2/jobs/bundle.sh" > /root/mwam_reports/bundle.sh && bash /root/mwam_reports/bundle.sh [hours]
# Writes /root/mwam_reports/BUNDLE_<host>_<time>.txt (attach it): checkout and GPUs, the pool report of the last <hours>
# (default 120), then scripts/memory_v2/bundle_inside.py from origin/memory2 (verdicts of the window with autopsies,
# running tasks' curves / episode peeks, report files of the window), dispatcher log, disk.
# It starts, stops, resets and updates nothing (autopsy files of finished tasks are rewritten, as host_pool.sh autopsy
# does; verdicts and the ledger are unchanged).
set -u
H=${1:-120}
C=${C:-$(docker ps --format '{{.ID}} {{.Names}}' | awk '$1 ~ /^6e4b37a15066/ {print $1} $2 == "mwam2" || $2 == "mwam-aws" || $2 == "mwam5090" {print $2}' | head -1)}
[ -n "$C" ] || { echo "no MemWAM container running here"; exit 1; }
R=/workspace/FastWAM-memory2
OUT=/root/mwam_reports
mkdir -p $OUT
F=$OUT/BUNDLE_$(hostname)_$(date +%Y%m%d_%H%M).txt
G="git -c safe.directory='*'"
echo "collecting into $F (a few minutes: autopsies of the window's tasks) ..."
{
  echo "===== header"
  date; hostname; echo "container $C; window $H h"
  docker exec "$C" bash -lc "cd $R && $G log --oneline -1 && echo 'origin/memory2:' && $G log --oneline -1 origin/memory2 && $G status --short | head -5"
  nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader
  nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader
  echo; echo "===== pool report (last $H h)"
  f=$(docker exec "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/pool5.py report --hours $H" | tail -1)
  docker exec "$C" cat "$f"
  docker exec "$C" bash -lc "cd $R && $G show origin/memory2:scripts/memory_v2/bundle_inside.py" \
    | docker exec -i "$C" bash -lc "cd $R && PYTHONPATH=src /opt/mwam/bin/python - $H"
  echo; echo "===== dispatcher log (last 80 lines)"
  docker exec "$C" tail -n 80 $R/outputs/memory_v2/queue5/pool.log
  echo; echo "===== disk"
  docker exec "$C" df -h $R/outputs/memory_v2 | tail -1
} > "$F" 2>&1
echo "BUNDLE: $F ($(wc -l < "$F") lines)"
