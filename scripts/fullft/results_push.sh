#!/usr/bin/env bash
# Results snapshot -> the branch results-<machine> of the project repo, so Opus can read results and machine health
# while the user is away. 11-18 (Opus, plan v14 7.5, user 18:33) for the A40; 11-25 14:10 (user: "a100, old h200, new
# h200, h100, 5090 like the A40: results synced automatically, with a heartbeat / health check; watch the 1 TB HF space")
# generalised to every machine. Only small, whitelisted files: verdict / report JSONs, the tails of recent logs, training
# progress lines, export names, queue / runner state, GPU and disk use, the HF storage report; never episodes, videos,
# models or caches. The branch holds ONE commit, replaced each time (force push to results-<machine> only; memory2 is
# never pushed from here). Separate clone in $W (own git config and credential file; nothing in the work repo changes).
# From 11-25 the loop runs `results_push.sh once` each round, so a newer version of this file is used without a restart.
#   setup (once, interactive; the user types a GitHub fine-grained token with Contents read/write on FredHuang99/FastWAM;
#   stored only in $W/.git/credentials, mode 600, never printed), then the loop starts:
#     results_push.sh setup <machine>        machine: a40 | a100 | h100 | h200o | h200n | g5090
#   then: results_push.sh start [minutes] | restart [minutes] | status | stop | once
# Containers: R=/workspace/FastWAM-memory2, W=/workspace/mwam_results. New H200 (GaaS, no container): R / W under
# ~/mwam (W=~/mwam/results_push); there the loop runs inside each slot job (gaas_run.pbs), never on the login node.
# Log: $R/outputs/fullft/RESULTS_PUSH.log
set -u
if [ -z "${R:-}" ]; then
  if [ -d /workspace/FastWAM-memory2 ]; then R=/workspace/FastWAM-memory2; else R=$HOME/mwam/FastWAM-memory2; fi
fi
if [ -z "${W:-}" ]; then
  if [ "$R" = /workspace/FastWAM-memory2 ]; then W=/workspace/mwam_results; else W=$HOME/mwam/results_push; fi
fi
OUT=$R/outputs/fullft
mkdir -p $OUT
PIDF=$OUT/RESULTS_PUSH.pid
LOG=$OUT/RESULTS_PUSH.log
URL=${URL:-https://github.com/FredHuang99/FastWAM.git}
MACHINE=${MACHINE:-$(cat $W/MACHINE 2>/dev/null || echo a40)}
BR=results-$MACHINE
G() { git -c safe.directory='*' -C $W "$@"; }
say() { echo "[push] $(TZ=Asia/Shanghai date '+%F %T') $*" >> $LOG; }
running() { [ -f $PIDF ] && kill -0 "$(cat $PIDF)" 2>/dev/null && grep -q results_push /proc/$(cat $PIDF)/cmdline 2>/dev/null; }
age_min() { [ -e "$1" ] && echo $(( ( $(date +%s) - $(stat -c %Y "$1") ) / 60 )) || echo -1; }
pid_alive() { local f=$1; [ -f "$f" ] && kill -0 "$(cut -d' ' -f1 "$f" | tr -dc 0-9)" 2>/dev/null; }
pyhf() { local p; for p in /opt/hf-tools/bin/python $HOME/mwam/envs/hf-tools/bin/python /opt/mwam/bin/python; do [ -x $p ] && { echo $p; return; }; done; }

common() {      # every machine
  local S=$1 f n
  mkdir -p $S/fullft $S/logs $S/report
  echo "$(TZ=Asia/Shanghai date '+%F %T') $(hostname) $MACHINE $(git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-60)" > $S/STAMP.txt
  { df -h $R/outputs 2>/dev/null | tail -n 1; df -h $HOME 2>/dev/null | tail -n 1; } > $S/report/disk.txt
  nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader > $S/report/gpus.txt 2>/dev/null
  nvidia-smi --query-compute-apps=gpu_bus_id,pid,used_memory --format=csv,noheader >> $S/report/gpus.txt 2>/dev/null
  tail -n 60 $OUT/AUTO_PULL.log > $S/fullft/AUTO_PULL.log 2>/dev/null
  tail -n 20 $LOG > $S/fullft/RESULTS_PUSH.log 2>/dev/null
  tail -n 30 $OUT/RELAY_RETRY.log > $S/fullft/RELAY_RETRY.log 2>/dev/null
  # small result files of the last 4 days (verdicts, reports, splits, checks)
  find $OUT -maxdepth 1 -name '*.json' -size -1500k -mtime -4 -exec cp -p {} $S/fullft/ \; 2>/dev/null
  find $OUT -maxdepth 1 -name '*.tsv' -size -1500k -mtime -4 -exec cp -p {} $S/fullft/ \; 2>/dev/null
  # tails of the 45 most recent top-level logs (queues, launchers, night scripts, builds)
  n=0
  for f in $(ls -t $OUT/*.txt $OUT/*.log 2>/dev/null | grep -v "QUEUE_.*\.log$\|RESULTS_PUSH\|AUTO_PULL" | head -n 45); do
    [ $(age_min $f) -le $((4 * 1440)) ] || continue
    tail -n 400 "$f" | tail -c 120000 > $S/logs/$(basename "$f"); n=$((n + 1))
  done
  # training progress: the last progress line of every trainer log of the last 4 days, its age, finished / failed
  : > $S/report/TRAINING.txt
  for f in $(ls -t $OUT/QUEUE_*.log 2>/dev/null); do
    [ $(age_min $f) -le $((4 * 1440)) ] || continue
    local run=${f##*/QUEUE_}; run=${run%.log}
    printf '%-24s last write %5s min ago | %s | %s %s\n' "$run" "$(age_min $f)" \
      "$(grep -a -o 'u [0-9]*/[0-9]*[^|]\{0,60\}' $f | tail -n 1)" \
      "$([ -f $OUT/$run/SUMMARY.json ] && echo FINISHED)" "$([ -f $OUT/$run/QUEUE_FAILED ] && echo FAILED)" >> $S/report/TRAINING.txt
    tail -n 30 "$f" | tail -c 20000 > $S/logs/QUEUE_$run.tail
  done
  ls -l --time-style='+%m-%d %H:%M' $OUT/exports/*/export_e*.pt 2>/dev/null | awk '{print $6, $7, $5, $8}' | tail -n 200 > $S/report/EXPORTS.txt
  # health: one line per check; "BAD" marks what needs a look
  {
    echo "machine $MACHINE host $(hostname) at $(TZ=Asia/Shanghai date '+%F %T')"
    if [ "$MACHINE" != h200n ]; then      # the new H200 has no auto_pull: each job pulls when it starts
      pid_alive $OUT/AUTO_PULL.pid && echo "ok   auto_pull alive (last log $(age_min $OUT/AUTO_PULL.log) min)" || echo "BAD  auto_pull not running"
    fi
    case $MACHINE in
      a40|a100) pgrep -f "[p]ool5.py" >/dev/null && echo "ok   pool5 dispatcher alive" || echo "BAD  pool5 dispatcher not running";;
      h100) f=$(ls -t $OUT/H100_QUEUE_*.txt 2>/dev/null | grep -v _dry | head -1)
            pgrep -f "[h]100_queue.sh" >/dev/null && echo "ok   h100_queue alive (log $(age_min "$f") min)" || echo "BAD  h100_queue not running";;
      h200o) f=$(ls -t $OUT/H200_QUEUE_*.txt 2>/dev/null | grep -v _dry | head -1)
             pgrep -f "[h]200_queue.sh" >/dev/null && echo "ok   h200_queue alive (log $(age_min "$f") min)" || echo "BAD  h200_queue not running";;
      g5090) pid_alive $OUT/Q5090.pid && echo "ok   q5090 runner alive" || echo "BAD  q5090 runner not running";;
      h200n) echo "info pushed from slot job ${PBS_JOBID:-?} on $(hostname)";;
    esac
    awk -F', ' 'NF >= 5 && $1 ~ /^[0-9]+$/ {u = $5; gsub(/[^0-9]/, "", u); m = $3; gsub(/[^0-9]/, "", m);
      printf "%s  GPU %s: %s MiB, %s %%\n", (u + 0 == 0 && m + 0 < 1500 ? "idle" : "ok  "), $1, m, u}' $S/report/gpus.txt
    awk '{p = $5; gsub("%", "", p); if (p + 0 >= 90) print "BAD  disk " $6 " " $5 " used (" $4 " free)"; else print "ok   disk " $6 " " $5 " used (" $4 " free)"}' $S/report/disk.txt
    awk -F'last write' '{split($2, a, " "); m = a[1] + 0; if ($0 ~ /FINISHED|FAILED/) next;
      if (m > 60 && m <= 1440) print "BAD  trainer silent " m " min: " $1; else if (m > 1440) print "info trainer idle " m " min (paused / waiting in its queue?): " $1}' $S/report/TRAINING.txt
    grep -h "FAILED" $S/report/TRAINING.txt | sed 's/^/BAD  /'
  } > $S/report/HEALTH.txt
}

hf_report() {   # the HF storage (1 TB); computed at most every 2 h, by the machines with an HF python
  local S=$1 py; py=$(pyhf)
  [ -n "$py" ] || return 0
  if [ ! -f $OUT/HF_USAGE.txt ] || [ $(age_min $OUT/HF_USAGE.txt) -ge 120 ]; then
    (cd $R && timeout 900 $py scripts/fullft/hf_usage.py > /dev/null 2>> $LOG)
  fi
  cp -p $OUT/HF_USAGE.txt $OUT/HF_USAGE.json $S/report/ 2>/dev/null
  grep -h "^WARN\|^BAD" $OUT/HF_USAGE.txt >> $S/report/HEALTH.txt 2>/dev/null
}

pool5_part() {  # A40 / A100: pool5 report, verdict / report / smoke / check card logs, task states
  local S=$1 Q=$R/outputs/memory_v2/queue5 f pre=$2
  mkdir -p $S/tasks
  for f in $Q/tasks/*verdict*.log $Q/tasks/*report*.log $Q/tasks/*scales*.log $Q/tasks/*smoke*.log $Q/tasks/*check*.log \
           $Q/tasks/*entries*.log $Q/tasks/*prep*.log $Q/tasks/*BANK*.log $Q/tasks/*index-matters*.log $Q/tasks/*clock-put*.log \
           $Q/tasks/*fetch*.log; do
    [ -f "$f" ] && tail -c 200000 "$f" > $S/tasks/$(basename "$f")
  done
  (cd $R && PYTHONPATH=src timeout 600 /opt/mwam/bin/python scripts/memory_v2/pool5.py report --hours 24 2>/dev/null | tail -n 1) > $S/report/latest_path.txt
  local rp; rp=$(tail -n 1 $S/report/latest_path.txt)
  [ -f "$rp" ] && head -c 3000000 "$rp" > $S/report/LATEST_REPORT.md
  (cd $Q/state 2>/dev/null && PRE="$pre" /opt/mwam/bin/python - > $S/report/STATES.tsv <<'PY'
import json, glob, os
pre = tuple(os.environ.get("PRE", "A40").split(","))
for f in sorted(glob.glob("*.json")):
    try:
        s = json.load(open(f))
    except Exception:
        continue
    if not str(s.get("id", "")).startswith(pre):
        continue
    print("\t".join(str(s.get(k, "")) for k in ("id", "status", "verdict", "start", "end", "attempt", "gpu")))
PY
  )
}

g5090_part() {  # 5090: the q5090 runner's state and task logs
  local S=$1 f
  mkdir -p $S/q5090
  [ -f $OUT/Q5090_STATE.txt ] && cp -p $OUT/Q5090_STATE.txt $S/report/
  for f in $(ls -t $OUT/q5090/*.log 2>/dev/null | head -n 40); do tail -n 200 "$f" | tail -c 60000 > $S/q5090/$(basename "$f"); done
  ls $OUT/q5090/ 2>/dev/null | grep -v '\.log$' > $S/q5090/MARKERS.txt
}

h200n_part() {  # new H200 (GaaS): slot pick / run logs on the shared home, our jobs
  local S=$1 f L=$HOME/mwam/logs
  mkdir -p $S/gaas
  for f in $(ls -t $L/PICK_*.txt $L/RUN_*.txt $L/SUBMIT_*.txt 2>/dev/null | head -n 40); do
    tail -n 300 "$f" | tail -c 80000 > $S/gaas/$(basename "$f")
  done
  { qstat -u "$(id -un)" 2>&1 | tail -n +3; } > $S/report/QSTAT.txt 2>/dev/null
  ls $HOME/mwam/slots/ 2>/dev/null | while read -r x; do echo "$x $(cat $HOME/mwam/slots/$x 2>/dev/null)"; done > $S/report/SLOTS.txt
}

snapshot() {
  local S=$W/snap
  rm -rf $S; mkdir -p $S
  common $S
  case $MACHINE in
    a40) pool5_part $S A40; hf_report $S;;
    a100) pool5_part $S A100;;
    g5090) g5090_part $S; hf_report $S;;
    h200n) h200n_part $S;;
  esac
}

push_once() {
  [ -d $W/.git ] || { say "no clone in $W: run setup"; return 1; }
  snapshot
  G checkout -q --orphan tmp_$$ 2>/dev/null || return 1
  G rm -rq --cached . 2>/dev/null
  G add -A snap
  G -c user.name="mwam-$MACHINE" -c user.email="mwam-$MACHINE@localhost" commit -qm "$MACHINE results snapshot $(TZ=Asia/Shanghai date '+%F %T')" || return 1
  G branch -qD $BR 2>/dev/null; G branch -qm $BR
  timeout 300 git -c safe.directory='*' -C $W push -q -f origin $BR 2>> $LOG
}

case "${1:-}" in
  setup)
    [ -n "${2:-}" ] && MACHINE=$2 && BR=results-$MACHINE
    case $MACHINE in a40|a100|h100|h200o|h200n|g5090) ;; *) echo "machine must be one of a40 a100 h100 h200o h200n g5090"; exit 2;; esac
    mkdir -p $W
    [ -d $W/.git ] || git -c safe.directory='*' init -q $W
    echo "$MACHINE" > $W/MACHINE
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
    if push_once; then echo "OK: $BR pushed ($(G log --oneline -1 | cut -c1-60))"; say "setup OK ($MACHINE)"; else echo "push FAILED (see $LOG); fix the token and run setup again (rm $W/.git/credentials first)"; tail -n 3 $LOG; exit 1; fi
    [ "$MACHINE" = h200n ] && { echo "h200n: the slot jobs push (gaas_run.pbs); nothing is started on the login node"; exit 0; }
    bash $R/scripts/fullft/results_push.sh start
    ;;
  once)
    push_once && { say "pushed"; echo "pushed"; } || { say "push FAILED"; echo "push FAILED (see $LOG)"; }
    # 11-25: exports that missed the (full) HF relay are retried on the container machines (relay_retry.sh, detached)
    case $MACHINE in h100|h200o) [ -f $R/scripts/fullft/relay_retry.sh ] && \
      setsid bash $R/scripts/fullft/relay_retry.sh > /dev/null 2>&1 < /dev/null & ;; esac
    ;;
  start)
    if running; then echo "[push] already running (pid $(cat $PIDF))"; tail -n 3 $LOG; exit 0; fi
    [ -s $W/.git/credentials ] || { echo "[push] run setup first"; exit 1; }
    rm -f $OUT/RESULTS_PUSH_STOP
    setsid bash $R/scripts/fullft/results_push.sh loop "${2:-30}" > /dev/null 2>&1 < /dev/null &
    sleep 3; running && echo "[push] started (pid $(cat $PIDF), every ${2:-30} min, $BR); log $LOG" || echo "[push] FAILED to start"
    ;;
  restart)      # an old loop (before 11-25 it kept its own copy of the code) is stopped at once and a new one started
    if running; then kill "$(cat $PIDF)" 2>/dev/null; sleep 2; rm -f $PIDF; echo "[push] old loop stopped"; fi
    bash $R/scripts/fullft/results_push.sh start "${2:-30}"
    ;;
  loop)
    echo $$ > $PIDF
    M=${2:-30}; say "loop start: every $M min ($BR)"
    while true; do
      [ -f $OUT/RESULTS_PUSH_STOP ] && { say "stop"; rm -f $OUT/RESULTS_PUSH_STOP $PIDF; exit 0; }
      bash $R/scripts/fullft/results_push.sh once > /dev/null 2>&1
      sleep $(( M * 60 ))
    done
    ;;
  status) running && echo "[push] running (pid $(cat $PIDF), $BR)" || echo "[push] NOT running ($BR)"; tail -n 5 $LOG 2>/dev/null;;
  stop) touch $OUT/RESULTS_PUSH_STOP; echo "[push] stop requested";;
  *) echo "usage: results_push.sh setup <machine> | once | start [minutes] | restart [minutes] | status | stop"; exit 2;;
esac
