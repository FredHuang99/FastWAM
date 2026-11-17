#!/usr/bin/env bash
# GPU share sampler (user 11-17 16:50: on the shared H100 we use at most 2 GPUs; a simple statistic of the other users'
# GPU use over the past 24 h tells whether we may take all four again). Read-only: it only runs nvidia-smi.
#   one look every EVERY s (default 600): per GPU its compute utilisation, memory in use, the number of compute processes
#   the driver lists (0 when the container cannot see them), and whether one of our queue trainers runs on it (an alive
#   outputs/fullft/<run>/QUEUE_GPU file, the same test h100_queue.sh uses)
#   rows go to outputs/fullft/GPU_SHARE_<TAG>.tsv (TAG default h100); the summary is gpu_share_report.py
#   docker exec mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/gpu_share.sh start    (once; a second start
#                                                                    only says it already runs)
#   ... gpu_share.sh report [hours]      summary of the last 24 h (or the given hours)
#   ... gpu_share.sh stop
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
TAG=${TAG:-h100}
TSV=$OUT/GPU_SHARE_${TAG}.tsv
PIDF=$OUT/GPU_SHARE_${TAG}.pid
EVERY=${EVERY:-600}
PY=/opt/mwam/bin/python; [ -x $PY ] || PY=python3
mkdir -p $OUT

alive() { [ -f "$1" ] && kill -0 "$(cut -d' ' -f2 "$1")" 2>/dev/null; }
ours() { local f; for f in $OUT/*/QUEUE_GPU; do alive "$f" && cut -d' ' -f1 "$f"; done; }
sample() {
  local now iso o apps i u util mem n us
  now=$(date +%s); iso=$(date '+%F %T')
  o=" $(ours | tr '\n' ' ') "
  apps=$(nvidia-smi --query-compute-apps=gpu_uuid,used_memory --format=csv,noheader,nounits 2>/dev/null)
  nvidia-smi --query-gpu=index,uuid,utilization.gpu,memory.used --format=csv,noheader,nounits 2>/dev/null |
  while IFS=', ' read -r i u util mem; do
    [ -z "$i" ] && continue
    n=$(printf '%s\n' "$apps" | grep -c -- "$u")
    case "$o" in *" $i "*) us=1;; *) us=0;; esac
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$now" "$iso" "$i" "$util" "$mem" "$n" "$us"
  done >> $TSV
}

case "${1:-run}" in
  start)
    if [ -f $PIDF ] && kill -0 "$(cat $PIDF)" 2>/dev/null; then
      echo "gpu_share: already runs (pid $(cat $PIDF)); $(($(wc -l < $TSV) - 1)) rows in $TSV"; exit 0
    fi
    setsid bash $R/scripts/fullft/gpu_share.sh run > /dev/null 2>&1 < /dev/null &
    sleep 6
    echo "gpu_share: started (pid $(cat $PIDF 2>/dev/null)); one look every $EVERY s -> $TSV"
    tail -n 4 $TSV ;;
  stop)
    [ -f $PIDF ] && kill "$(cat $PIDF)" 2>/dev/null && echo "gpu_share: stopped"; rm -f $PIDF ;;
  report)
    exec $PY $R/scripts/fullft/gpu_share_report.py --tsv $TSV --hours "${2:-24}" ;;
  run)
    echo $$ > $PIDF
    [ -s $TSV ] || printf 'time\tiso\tgpu\tutil\tmem_mib\tapps\tours\n' > $TSV
    while true; do sample; sleep $EVERY; done ;;
  *) echo "usage: gpu_share.sh start | stop | report [hours]"; exit 2 ;;
esac
