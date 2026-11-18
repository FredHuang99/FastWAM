#!/usr/bin/env bash
# mwam-a40, 11-18 (Opus; plan v14 section 7 item 5, user approved 18:33): every <minutes> (default 30) the A40 pushes
# a small snapshot of its results to the branch results-a40 of the project repo, so Opus can read the verdicts while
# the user is away. Only small, whitelisted files (verdict JSONs, the logs of verdict / report / smoke / check cards, a
# fresh pool report, the auto-pull log); never episode folders, videos or models. The branch holds ONE commit, replaced
# each time (force push to results-a40 only; memory2 is never pushed from here). Separate clone in
# /workspace/mwam_results (its own git config and credential file, nothing in the work repo changes).
#   setup (once, interactive; the user types a GitHub fine-grained token with Contents read/write on FredHuang99/FastWAM;
#   it is stored only in /workspace/mwam_results/.git/credentials, mode 600, never printed):
#     docker exec -it mwam-a40 bash /workspace/FastWAM-memory2/scripts/fullft/results_push.sh setup
#   then: results_push.sh start [minutes] | status | stop | once
# Log: /workspace/FastWAM-memory2/outputs/fullft/RESULTS_PUSH.log
set -u
R=${R:-/workspace/FastWAM-memory2}
W=${W:-/workspace/mwam_results}
OUT=$R/outputs/fullft
PIDF=$OUT/RESULTS_PUSH.pid
LOG=$OUT/RESULTS_PUSH.log
URL=${URL:-https://github.com/FredHuang99/FastWAM.git}
BR=results-a40
G() { git -c safe.directory='*' -C $W "$@"; }
say() { echo "[push] $(TZ=Asia/Shanghai date '+%F %T') $*" >> $LOG; }
running() { [ -f $PIDF ] && kill -0 "$(cat $PIDF)" 2>/dev/null && grep -q results_push /proc/$(cat $PIDF)/cmdline 2>/dev/null; }

snapshot() {
  local S=$W/snap Q=$R/outputs/memory_v2/queue5
  rm -rf $S; mkdir -p $S/fullft $S/tasks $S/report
  cp -p $OUT/E*_VERDICT*.json $OUT/E*_SCALES.json $OUT/E6_REPORT.json $OUT/PRESS_*_VERDICT.json $OUT/AUTO_PULL.log $S/fullft/ 2>/dev/null
  for f in $Q/tasks/*verdict*.log $Q/tasks/*report*.log $Q/tasks/*scales*.log $Q/tasks/*smoke*.log $Q/tasks/*check*.log \
           $Q/tasks/*entries*.log $Q/tasks/*prep*.log $Q/tasks/*BANK*.log $Q/tasks/*index-matters*.log $Q/tasks/*clock-put*.log; do
    [ -f "$f" ] && tail -c 200000 "$f" > $S/tasks/$(basename "$f")
  done
  (cd $R && PYTHONPATH=src timeout 600 /opt/mwam/bin/python scripts/memory_v2/pool5.py report --hours 24 2>/dev/null | tail -n 1) > $S/report/latest_path.txt
  local rp; rp=$(tail -n 1 $S/report/latest_path.txt)
  [ -f "$rp" ] && head -c 3000000 "$rp" > $S/report/LATEST_REPORT.md
  (cd $Q/state 2>/dev/null && /opt/mwam/bin/python - > $S/report/STATES.tsv <<'PY'
import json, glob
for f in sorted(glob.glob("*.json")):
    try:
        s = json.load(open(f))
    except Exception:
        continue
    if not str(s.get("id", "")).startswith(("A40", "A100")):
        continue
    print("\t".join(str(s.get(k, "")) for k in ("id", "status", "verdict", "start", "end", "attempt", "gpu")))
PY
  )
  df -h $R/outputs | tail -n 1 > $S/report/disk.txt
  nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader > $S/report/gpus.txt 2>/dev/null
  echo "$(TZ=Asia/Shanghai date '+%F %T') $(hostname) $(git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-60)" > $S/STAMP.txt
}

push_once() {
  snapshot
  G checkout -q --orphan tmp_$$ 2>/dev/null || return 1
  G rm -rq --cached . 2>/dev/null
  G add -A snap
  G -c user.name="mwam-a40" -c user.email="mwam-a40@localhost" commit -qm "A40 results snapshot $(TZ=Asia/Shanghai date '+%F %T')" || return 1
  G branch -qD $BR 2>/dev/null; G branch -qm $BR
  timeout 300 git -c safe.directory='*' -C $W push -q -f origin $BR 2>> $LOG
}

case "${1:-}" in
  setup)
    mkdir -p $W
    [ -d $W/.git ] || git -c safe.directory='*' init -q $W
    G remote get-url origin >/dev/null 2>&1 || G remote add origin $URL
    G config credential.helper "store --file=$W/.git/credentials"
    G config credential.useHttpPath false
    if [ ! -s $W/.git/credentials ]; then
      read -r -p "GitHub user name [FredHuang99]: " U; U=${U:-FredHuang99}
      read -r -s -p "fine-grained token (Contents read/write on FredHuang99/FastWAM; not shown): " TOK; echo
      [ -n "$TOK" ] || { echo "no token: nothing stored"; exit 1; }
      printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' "$U" "$TOK" | G credential approve
      unset TOK; chmod 600 $W/.git/credentials
    fi
    echo "test push to $BR ..."
    if push_once; then echo "OK: $BR pushed ($(G log --oneline -1 | cut -c1-60))"; say "setup OK"; else echo "push FAILED (see $LOG); fix the token and run setup again (rm $W/.git/credentials first)"; exit 1; fi
    ;;
  once) push_once && echo "pushed" || echo "push FAILED (see $LOG)";;
  start)
    if running; then echo "[push] already running (pid $(cat $PIDF))"; tail -n 3 $LOG; exit 0; fi
    [ -s $W/.git/credentials ] || { echo "[push] run setup first"; exit 1; }
    rm -f $OUT/RESULTS_PUSH_STOP
    setsid bash $R/scripts/fullft/results_push.sh loop "${2:-30}" > /dev/null 2>&1 < /dev/null &
    sleep 3; running && echo "[push] started (pid $(cat $PIDF), every ${2:-30} min); log $LOG" || echo "[push] FAILED to start"
    ;;
  loop)
    echo $$ > $PIDF
    M=${2:-30}; say "loop start: every $M min"
    while true; do
      [ -f $OUT/RESULTS_PUSH_STOP ] && { say "stop"; rm -f $OUT/RESULTS_PUSH_STOP $PIDF; exit 0; }
      if push_once; then say "pushed"; else say "push FAILED"; fi
      sleep $(( M * 60 ))
    done
    ;;
  status) running && echo "[push] running (pid $(cat $PIDF))" || echo "[push] NOT running"; tail -n 5 $LOG 2>/dev/null;;
  stop) touch $OUT/RESULTS_PUSH_STOP; echo "[push] stop requested";;
  *) echo "usage: results_push.sh setup | once | start [minutes] | status | stop"; exit 2;;
esac
