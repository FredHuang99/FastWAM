#!/usr/bin/env bash
# User 11-18 18:08 (plan v14 5.2 item 1): the A40, A100, H100 and old H200 containers pull the repo on a timer, so
# task cards, queue lines and the scripts they call that Opus pushes go live without a command from the user
# (the user is away 11-19 all day -> 11-20 14:00). User 11-19 09:47: the 5090 is included too.
# Every <minutes> (default 10): git fetch origin memory2, then a fast-forward-only merge. Never resets, never touches
# a running process: a running bash script keeps its old file (git replaces files, the open one stays), a running
# trainer / closed loop keeps its loaded code; only tasks that start later use the new code. A failed fast-forward
# (local edits, diverged history) changes nothing and is logged. The pool / queue re-reads its task file by itself.
#   bash /workspace/FastWAM-memory2/scripts/fullft/auto_pull.sh start [minutes]   (detaches; one per container)
#   bash /workspace/FastWAM-memory2/scripts/fullft/auto_pull.sh status | stop
# Log: outputs/fullft/AUTO_PULL.log (one line per pull that changed something, a heartbeat every hour; BJ time).
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
mkdir -p $OUT
PIDF=$OUT/AUTO_PULL.pid
LOG=$OUT/AUTO_PULL.log
G() { git -c safe.directory='*' -C $R "$@"; }
say() { echo "[pull] $(TZ=Asia/Shanghai date '+%F %T') $*" >> $LOG; }
running() { [ -f $PIDF ] && kill -0 "$(cat $PIDF)" 2>/dev/null && grep -q auto_pull /proc/$(cat $PIDF)/cmdline 2>/dev/null; }

case "${1:-start}" in
  start)
    if running; then echo "[pull] already running (pid $(cat $PIDF)); log $LOG"; tail -n 3 $LOG; exit 0; fi
    rm -f $OUT/AUTO_PULL_STOP
    setsid bash $R/scripts/fullft/auto_pull.sh loop "${2:-10}" > /dev/null 2>&1 < /dev/null &
    sleep 5
    running && echo "[pull] started (pid $(cat $PIDF), every ${2:-10} min); log $LOG" || echo "[pull] FAILED to start; see $LOG"
    tail -n 3 $LOG
    ;;
  loop)
    echo $$ > $PIDF
    M=${2:-10}
    say "start on $(hostname): every $M min; checkout $(G log --oneline -1 | cut -c1-70)"
    last_beat=$(date +%s)
    while true; do
      [ -f $OUT/AUTO_PULL_STOP ] && { say "AUTO_PULL_STOP found: exit"; rm -f $OUT/AUTO_PULL_STOP $PIDF; exit 0; }
      before=$(G rev-parse HEAD)
      if timeout 300 git -c safe.directory='*' -C $R fetch -q origin memory2 2>> $LOG; then
        if G merge --ff-only -q FETCH_HEAD 2>> $LOG; then
          after=$(G rev-parse HEAD)
          if [ "$before" != "$after" ]; then
            say "pulled $(G log --oneline $before..$after | wc -l) commit(s) -> $(G log --oneline -1 | cut -c1-70); files: $(G diff --name-only $before $after | tr '\n' ' ' | cut -c1-400)"
          fi
        else
          say "fast-forward FAILED: nothing changed; local state: $(G status --short --untracked-files=no | head -5 | tr '\n' ';')"
        fi
      else
        say "fetch failed (network?): nothing changed"
      fi
      if [ $(( $(date +%s) - last_beat )) -ge 3600 ]; then say "alive; at $(G log --oneline -1 | cut -c1-70)"; last_beat=$(date +%s); fi
      sleep $(( M * 60 ))
    done
    ;;
  status)
    running && echo "[pull] running (pid $(cat $PIDF))" || echo "[pull] NOT running"
    tail -n 5 $LOG 2>/dev/null
    ;;
  stop)
    touch $OUT/AUTO_PULL_STOP; echo "[pull] stop requested (takes effect at the next wake-up)"
    ;;
  *) echo "usage: auto_pull.sh start [minutes] | status | stop"; exit 2;;
esac
