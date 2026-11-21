#!/usr/bin/env bash
# GaaS job container (11-21 15:30, Opus): exports that finished while the HF relay was full (403 "set up automatic
# credit recharge", from 11-20 ~22:45) go on the relay once there is room. scripts/gaas/relay_backlog.txt lines:
# RUN TAG [TAG ...]. Every 30 min, for up to 24 h: export_watch.sh for the tags without a .relayed_<tag> marker
# (3 tries each, as for a fresh export); stops when every listed tag is marked. Started in the background by
# gaas_run.pbs, one job at a time (lock outputs/fullft/.relay_backlog_lock, removed on exit, stale after 25 h).
set -u
R=/workspace/FastWAM-memory2; OUT=$R/outputs/fullft; LIST=${LIST:-$R/scripts/gaas/relay_backlog.txt}   # H100: LIST=..._h100.txt
LOG=$OUT/RELAY_BACKLOG_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'echo "[backlog] $(date "+%F %T") finished; log $LOG"; rmdir $OUT/.relay_backlog_lock 2>/dev/null' EXIT
cd $R
for round in $(seq 1 48); do
  left=0
  while read -r run tags; do
    case "$run" in ""|\#*) continue;; esac
    todo=""; for t in $tags; do                 # only exports this machine has (export_watch would wait for others)
      [ -f $OUT/$run/.relayed_$t ] || { [ -f $OUT/$run/export_$t.pt ] && todo="$todo $t"; }; done
    [ -z "$todo" ] && continue
    left=1
    echo "[backlog] $(date '+%F %T') round $round: $run$todo"
    RUN=$run TAGS="${todo# }" POLL=60 bash scripts/fullft/export_watch.sh > /dev/null 2>&1 < /dev/null
    echo "[backlog] $(date '+%F %T') $run relayed now: $(ls $OUT/$run/.relayed_* 2>/dev/null | xargs -n1 basename 2>/dev/null | tr '\n' ' ')"
  done < $LIST
  [ $left = 0 ] && { echo "[backlog] $(date '+%F %T') every listed export is on the relay"; exit 0; }
  sleep 1800
done
echo "[backlog] $(date '+%F %T') gave up after 24 h"
