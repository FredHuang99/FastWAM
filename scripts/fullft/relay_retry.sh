#!/usr/bin/env bash
# 11-25 (Opus; HF relay at 99 % while its freed space shows up only within 36 h): on the training machines in containers
# (H100, old H200; the new H200 has relay_backlog.sh in its jobs; the 5090 trains nothing), exports that never reached the relay are tried again.
# Started (detached) by results_push.sh every round; one at a time per machine (lock dir, stale after 3 h). An export
# outputs/fullft/<run>/export_<tag>.pt without .relayed_<tag>, older than 30 min, with no live export_watch.sh for its
# run -> export_relay.sh, then the relay listing must show the .pt and its .sha256 -> .relayed_<tag>. Log RELAY_RETRY.log.
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
L=$OUT/.relay_retry_lock
LOG=$OUT/RELAY_RETRY.log
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
say() { echo "[retry] $(TZ=Asia/Shanghai date '+%F %T') $*" >> $LOG; }
[ -d $L ] && [ $(( $(date +%s) - $(stat -c %Y $L) )) -gt 10800 ] && rmdir $L 2>/dev/null
mkdir $L 2>/dev/null || exit 0
trap 'rmdir $L 2>/dev/null' EXIT
watching() { local p; for p in $(pgrep -f "[e]xport_watch.sh"); do tr '\0' '\n' < /proc/$p/environ 2>/dev/null | grep -qx "RUN=$1" && return 0; done; return 1; }
cd $R
for f in $(ls -t $OUT/*/export_e*.pt 2>/dev/null); do
  run=$(basename $(dirname $f)); tag=$(basename $f .pt); tag=${tag#export_}
  [ -f $OUT/$run/.relayed_$tag ] && continue
  age=$(( $(date +%s) - $(stat -c %Y $f) ))
  [ $age -ge 1800 ] || continue
  [ $age -le 129600 ] || continue          # only exports of the last 36 h (older ones predate the .relayed markers)
  watching $run && continue
  say "$run $tag: not on the relay yet -> upload"
  RUN=$run TAG=$tag bash scripts/fullft/export_relay.sh > /dev/null 2>&1
  ls=$($HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${run}_$tag --repo hhyfred/memwam-fullft 2>/dev/null)
  if echo "$ls" | grep -q "^export_$tag.pt " && echo "$ls" | grep -q "^export_$tag.pt.sha256 "; then
    touch $OUT/$run/.relayed_$tag; say "$run $tag: relayed"
  else
    say "$run $tag: still not on the relay (full?); next round"; break
  fi
done
