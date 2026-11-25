#!/usr/bin/env bash
# mwam5090, 11-25 14:20 (Opus; user 14:08: everything until Friday 10:00 runs by itself). A small task runner for the
# 5090's two GPUs, so new 5090 work arrives through the repo (auto_pull.sh) instead of a command each time -- the 5090
# counterpart of the A40's queue5 cards. The task file is RE-READ before every pick:
#   scripts/fullft/q5090.txt   lines "id | where | condition | command"
#     where      gpu0 | gpu1 | gpu (either) | cpu
#     condition  a shell test run in the repository root ("-" = none); the line waits until it passes
#     command    run with bash in the repository root, env GPU=<index> (empty for cpu); the command picks its GPU
#                itself (CUDA_VISIBLE_DEVICES=$GPU / PF_GPUS=$GPU / GEN_GPU=$GPU)
#   A GPU is free when < 2000 MiB are in use on it at two looks 60 s apart and no task of this runner runs there (work
#   started by hand, e.g. the generator, keeps its GPU). The first eligible line in file order goes first. Each task runs
#   once: outputs/fullft/q5090/<id>.running (pid gpu start) -> <id>.done or <id>.failed (exit code); log <id>.log.
#   A failed task is not retried by itself (rm its .failed marker to run it again). cpu tasks run beside everything,
#   at most 2 at a time.
#   outputs/fullft/Q5090_STOP: start nothing new (running tasks continue); removed when seen.
#   docker exec mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/q5090.sh start | status | stop
# Own log: outputs/fullft/Q5090.log ; state outputs/fullft/Q5090_STATE.txt (rewritten every round)
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
QD=$OUT/q5090
QF=${QF:-$R/scripts/fullft/q5090.txt}
PIDF=$OUT/Q5090.pid
LOG=$OUT/Q5090.log
mkdir -p $QD
say() { echo "[q5090] $(TZ=Asia/Shanghai date '+%F %T') $*" >> $LOG; }
running() { [ -f $PIDF ] && kill -0 "$(cat $PIDF)" 2>/dev/null && grep -q q5090 /proc/$(cat $PIDF)/cmdline 2>/dev/null; }
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '; }
task_alive() { local f=$QD/$1.running; [ -f $f ] && kill -0 "$(cut -d' ' -f1 $f)" 2>/dev/null; }
ours_on() { local f; for f in $QD/*.running; do [ -f "$f" ] || continue; kill -0 "$(cut -d' ' -f1 $f)" 2>/dev/null && [ "$(cut -d' ' -f2 $f)" = "gpu$1" ] && return 0; done; return 1; }
n_cpu() { local f n=0; for f in $QD/*.running; do [ -f "$f" ] || continue; kill -0 "$(cut -d' ' -f1 $f)" 2>/dev/null && [ "$(cut -d' ' -f2 $f)" = cpu ] && n=$((n + 1)); done; echo $n; }
probe() { local u1 u2; ours_on $1 && return 1; u1=$(used $1); [[ "$u1" =~ ^[0-9]+$ ]] && [ $u1 -lt 2000 ] || return 1; sleep 60; u2=$(used $1); [[ "$u2" =~ ^[0-9]+$ ]] && [ $u2 -lt 2000 ]; }
declare -A FREE
gpu_free() {    # looked at once per round; a GPU just given to a task is not free any more this round
  if [ -z "${FREE[$1]:-}" ]; then probe $1 && FREE[$1]=1 || FREE[$1]=0; fi
  [ "${FREE[$1]}" = 1 ]
}

launch() {      # id where gpu command
  local id=$1 where=$2 g=$3 cmd=$4
  ( cd $R && GPU=$g setsid bash -c "$cmd" > $QD/$id.log 2>&1 < /dev/null; rc=$?
    rm -f $QD/$id.running
    if [ $rc = 0 ]; then echo "$(TZ=Asia/Shanghai date '+%F %T')" > $QD/$id.done; else echo "exit $rc $(TZ=Asia/Shanghai date '+%F %T')" > $QD/$id.failed; fi
    echo "[q5090] $(TZ=Asia/Shanghai date '+%F %T') $id finished, exit code $rc" >> $LOG ) &
  echo "$! $([ -n "$g" ] && echo gpu$g || echo cpu) $(TZ=Asia/Shanghai date '+%F %T')" > $QD/$id.running
  say "start $id on $([ -n "$g" ] && echo GPU $g || echo cpu): $(echo "$cmd" | cut -c1-200)"
}

round() {
  local line id where cond cmd g state
  FREE=()
  : > $OUT/Q5090_STATE.tmp
  while IFS= read -r line; do
    [[ "$line" =~ ^[[:space:]]*# ]] && continue
    [ -z "${line// /}" ] && continue
    id=$(echo "$line" | cut -d'|' -f1 | xargs); where=$(echo "$line" | cut -d'|' -f2 | xargs)
    cond=$(echo "$line" | cut -d'|' -f3 | sed 's/^ *//; s/ *$//'); cmd=$(echo "$line" | cut -d'|' -f4- | sed 's/^ *//')
    [ -n "$id" ] && [ -n "$cmd" ] || continue
    if [ -f $QD/$id.done ]; then state="done $(cat $QD/$id.done)"
    elif [ -f $QD/$id.failed ]; then state="FAILED $(cat $QD/$id.failed)"
    elif task_alive $id; then state="running $(cut -d' ' -f2- $QD/$id.running)"
    else
      rm -f $QD/$id.running
      if [ "$cond" != "-" ] && ! (cd $R && bash -c "$cond") > /dev/null 2>&1 < /dev/null; then state="waiting (condition)"
      else
        g=""
        case $where in
          gpu0|gpu1) gpu_free ${where#gpu} && g=${where#gpu};;
          gpu) gpu_free 0 && g=0 || { gpu_free 1 && g=1; };;
          cpu) [ $(n_cpu) -lt 2 ] && g=cpu;;
        esac
        if [ "$where" = cpu ] && [ "$g" = cpu ]; then launch "$id" cpu "" "$cmd"; state="started (cpu)"
        elif [ -n "$g" ] && [ "$g" != cpu ]; then launch "$id" "$where" "$g" "$cmd"; FREE[$g]=0; state="started (GPU $g)"
        else state="waiting ($where busy)"; fi
      fi
    fi
    printf '%-28s %-5s %s\n' "$id" "$where" "$state" >> $OUT/Q5090_STATE.tmp
  done < $QF
  { echo "q5090 $(TZ=Asia/Shanghai date '+%F %T'); GPU0 $(used 0) MiB, GPU1 $(used 1) MiB"; cat $OUT/Q5090_STATE.tmp; } > $OUT/Q5090_STATE.txt
}

case "${1:-}" in
  start)
    if running; then echo "[q5090] already running (pid $(cat $PIDF))"; tail -n 3 $LOG; exit 0; fi
    setsid bash $R/scripts/fullft/q5090.sh loop > /dev/null 2>&1 < /dev/null &
    sleep 3; running && echo "[q5090] started (pid $(cat $PIDF)); log $LOG; state $OUT/Q5090_STATE.txt" || echo "[q5090] FAILED to start"
    ;;
  loop)
    echo $$ > $PIDF
    say "loop start on $(hostname); task file $QF"
    while true; do
      if [ -f $OUT/Q5090_STOP ]; then say "Q5090_STOP: nothing new starts"; rm -f $OUT/Q5090_STOP; touch $OUT/Q5090_PAUSED; fi
      [ -f $OUT/Q5090_PAUSED ] || round
      sleep 120
    done
    ;;
  status) running && echo "[q5090] running (pid $(cat $PIDF))" || echo "[q5090] NOT running"; cat $OUT/Q5090_STATE.txt 2>/dev/null; tail -n 5 $LOG 2>/dev/null;;
  stop) touch $OUT/Q5090_STOP; echo "[q5090] stop requested (running tasks continue; rm outputs/fullft/Q5090_PAUSED to resume)";;
  *) echo "usage: q5090.sh start | status | stop"; exit 2;;
esac
