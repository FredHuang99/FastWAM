#!/usr/bin/env bash
# 11-25 (Opus; unattended until Friday 10:00): start a machine's queue runner only if it is not running already.
#   bash scripts/fullft/ensure_runner.sh h100 | h200o
# h100 -> h100_queue.sh (mwam-h100n), h200o -> h200_queue.sh (mwam2). Prints what it found / did.
set -u
R=${R:-/workspace/FastWAM-memory2}
case "${1:-}" in
  h100) S=h100_queue.sh;;
  h200o) S=h200_queue.sh;;
  *) echo "usage: ensure_runner.sh h100 | h200o"; exit 2;;
esac
P=$(pgrep -f "scripts/fullft/${S//./\\.}" | tr '\n' ' ')
if [ -n "${P// /}" ]; then echo "[ensure] $S running (pid $P)"; exit 0; fi
cd $R && setsid nohup bash $R/scripts/fullft/$S > /dev/null 2>&1 < /dev/null &
sleep 5
P=$(pgrep -f "scripts/fullft/${S//./\\.}" | tr '\n' ' ')
[ -n "${P// /}" ] && echo "[ensure] $S started (pid $P)" || echo "[ensure] $S FAILED to start"
