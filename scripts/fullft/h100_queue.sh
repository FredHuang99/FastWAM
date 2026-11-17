#!/usr/bin/env bash
# mwam-h100n container (gpu24, 4x H100 NVL 94 GB, shared with other users; 11-16): train the runs of h100_queue.txt,
# each on its own GPU, as GPUs become free (user 11-15: every GPU may be used, grabbed by a queue with the 1-minute rule).
#   * GPU g is free when it has < 1000 MiB in use at three looks 30 s apart (60 s) and none of our trainers runs on it
#   * the queue file is re-read before every pick; same format and pick rule as h200_queue.txt (first line that is not
#     finished / failed / running here and whose condition holds); several runs train at once, one per free GPU
#   * recipe = the H200 recipe (configs/fullft/base_2task.yaml + the line's --set values) with a smaller micro batch and
#     a larger accumulation, 64 samples per update either way (the H200 peak was 93.8 GiB at micro 8; the H100 NVL has 94 GB)
#   * before the first run, once: train.py smoke (200 updates on one episode of the first runnable line's data) with
#     micro 4 x 16; if it fails, again with micro 2 x 32; the passing pair is used for every run (outputs/fullft/H100_MB);
#     both fail -> the queue stops with the reason
#   * per run: export_watch.sh (exports e10 / e20 / e30 go to the relay), the trainer, one resumed retry on a free GPU,
#     else <run>/QUEUE_FAILED (that run is skipped, the others continue)
#   * outputs/fullft/QUEUE_STOP_H100: start nothing new (running trainers continue); the file is removed when seen
#   * 11-17 19:42 (user; replaces the 16:50 "at most 2 GPUs"): the queue keeps taking every free GPU (1-minute rule);
#     when another user needs a GPU, h100_yield.sh frees it gracefully: the trainer saves resume.pt and exits, the GPU is
#     HELD for others for some hours (outputs/fullft/H100_HOLD_<gpu> = expiry time; this queue does not take a held GPU),
#     and the stopped run goes back to the queue (same line, so it is first again) and resumes from its resume.pt on the
#     next free GPU. Optional cap: outputs/fullft/H100_MAX_RUNS (one number; default MAX_RUNS = the number of GPUs, no
#     cap), re-read before every start. Other users' share of the GPUs (information only): gpu_share.sh (sampler, every
#     10 min) + gpu_share_report.py (last 24 h); the heartbeat prints its one-line summary
#   docker exec -d mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/h100_queue.sh
#   DRY=1 ...   print the plan (next line, why the others wait, GPU memory) and exit
# Own log: outputs/fullft/H100_QUEUE_<time>.txt; trainer stdout: outputs/fullft/QUEUE_<run>.log
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
QF=${QF:-$R/scripts/fullft/h100_queue.txt}
GPUS=${GPUS:-"0 1 2 3"}
MAX_RUNS=${MAX_RUNS:-$(echo $GPUS | wc -w)}
mkdir -p $OUT
LOG=$OUT/H100_QUEUE_$(date +%Y%m%d_%H%M)$([ "${DRY:-0}" = 1 ] && echo _dry).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[h100q] $(date "+%F %T") dispatcher finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
PY=${PY:-/opt/mwam/bin/python}
echo "[h100q] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); queue $QF; GPUs $GPUS"

used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' '; }
alive() { [ -f "$1" ] && kill -0 "$(cut -d' ' -f2 "$1")" 2>/dev/null; }
ours_on() { local f; for f in $OUT/*/QUEUE_GPU; do alive "$f" && [ "$(cut -d' ' -f1 "$f")" = "$1" ] && return 0; done; return 1; }
running() { local f n=0; for f in $OUT/*/QUEUE_GPU; do alive "$f" && n=$((n + 1)); done; echo $n; }
max_runs() {      # the cap: outputs/fullft/H100_MAX_RUNS if it holds a number, else MAX_RUNS
  local v; v=$( { tr -dc '0-9' < $OUT/H100_MAX_RUNS; } 2>/dev/null ); echo "${v:-$MAX_RUNS}"
}
held() {          # GPU $1 is held for another user (h100_yield.sh) until the time in H100_HOLD_<gpu>; expired holds go
  local f=$OUT/H100_HOLD_$1 u
  [ -f $f ] || return 1
  u=$(tr -dc '0-9' < $f)
  [ -n "$u" ] && [ "$(date +%s)" -lt "$u" ] && return 0
  rm -f $f; return 1
}
watching() {      # an export_watch.sh for run $1 is alive (also one started by an earlier dispatcher: RUN is in its env)
  local p
  for p in $(pgrep -f "[e]xport_watch.sh"); do
    { tr '\0' '\n' < /proc/$p/environ; } 2>/dev/null | grep -qx "RUN=$1" && return 0
  done
  return 1
}
free_gpu() {      # prints the first free GPU (1-minute rule), else returns 1
  local g k
  for g in $GPUS; do
    ours_on $g && continue
    held $g && continue
    for k in 1 2 3; do
      [ "$(used $g)" -lt 1000 ] || continue 2
      [ $k -lt 3 ] && sleep 30
    done
    echo $g; return 0
  done
  return 1
}
pick() {          # prints "run|sets" of the next runnable line; reasons for the others go to stderr
  local run sets cond
  while IFS='|' read -r run sets cond; do
    case "$run" in [[:space:]]*\#*|\#*) continue;; esac          # comments first (quotes in them upset xargs)
    run=$(echo "$run" | xargs); sets=$(echo "$sets" | xargs); cond=$(echo "${cond:-}" | xargs)
    [ -z "$run" ] && continue
    if [ -f $OUT/$run/SUMMARY.json ]; then echo "  $run: finished" >&2; continue; fi
    if [ -f $OUT/$run/QUEUE_FAILED ]; then echo "  $run: FAILED earlier (see $OUT/$run/QUEUE_FAILED)" >&2; continue; fi
    if alive $OUT/$run/QUEUE_GPU; then echo "  $run: training on GPU $(cut -d' ' -f1 $OUT/$run/QUEUE_GPU)" >&2; continue; fi
    if [ -n "$cond" ] && ! bash -c "$cond" >/dev/null 2>&1; then echo "  $run: waits (condition: $cond)" >&2; continue; fi
    echo "$run|$sets"; return 0
  done < <(grep -v '^[[:space:]]*$' "$QF")
  return 1
}
sets_args() { local s; for s in "$@"; do printf -- '--set\n%s\n' "$s"; done; }

smoke() {         # once: find the micro batch that fits; writes outputs/fullft/H100_MB ("4 16" or "2 32")
  [ -s $OUT/H100_MB ] && return 0
  local next sets g pair m a
  until next=$(pick 2>/dev/null); do echo "[h100q] $(date '+%F %T') smoke: nothing runnable yet; next look in 10 min"; sleep 600; done
  sets=${next#*|}
  for pair in "4 16" "2 32"; do
    m=${pair% *}; a=${pair#* }
    until g=$(free_gpu); do sleep 60; done
    echo "[h100q] $(date '+%F %T') smoke with micro $m x accumulation $a on GPU $g (data of ${next%%|*})"
    mapfile -t A < <(sets_args name=h100_smoke_m$m $sets schedule.micro_batch=$m schedule.accumulation=$a)
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.fullft.train smoke --config configs/fullft/base_2task.yaml "${A[@]}" \
      >> $OUT/QUEUE_h100_smoke.log 2>&1
    echo "[h100q] $(date '+%F %T') smoke micro $m exit code $?: $(grep -h 'SMOKE ' $OUT/h100_smoke_m$m/*.txt 2>/dev/null | tail -1 | cut -c1-220)"
    if grep -q '"pass": true' $OUT/h100_smoke_m$m/SMOKE.json 2>/dev/null; then echo "$m $a" > $OUT/H100_MB; return 0; fi
  done
  echo "[h100q] smoke failed with micro 4 and 2: the queue stops (see $OUT/QUEUE_h100_smoke.log)"; return 1
}

launch() {        # run, sets, gpu: the trainer in the background, one resumed retry on a free GPU
  local run=$1 sets=$2 g=$3
  mkdir -p $OUT/$run
  (
    read -r m a < $OUT/H100_MB
    mapfile -t A < <(sets_args name=$run $sets schedule.micro_batch=$m schedule.accumulation=$a)
    watching $run || { RUN=$run nohup bash scripts/fullft/export_watch.sh > /dev/null 2>&1 & }   # one per run (a resumed run keeps its watcher)
    for attempt in 1 2; do
      echo "$g $BASHPID" > $OUT/$run/QUEUE_GPU
      echo "[h100q] $(date '+%F %T') ===== $run attempt $attempt on GPU $g (micro $m x $a; $(used $g) MiB before)"
      CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.fullft.train train --config configs/fullft/base_2task.yaml "${A[@]}" \
        >> $OUT/QUEUE_$run.log 2>&1
      rc=$?
      echo "[h100q] $(date '+%F %T') $run trainer exit code $rc"
      [ -f $OUT/$run/SUMMARY.json ] && break
      if [ $attempt = 1 ]; then
        echo "[h100q] $run: no SUMMARY.json; one resumed retry on the next free GPU"; sleep 120
        until g=$(free_gpu); do sleep 60; done
      fi
    done
    if [ -f $OUT/$run/SUMMARY.json ]; then
      echo "[h100q] $(date '+%F %T') $run finished: $(head -c 400 $OUT/$run/SUMMARY.json)"
    else
      { echo "exit code $rc at $(date '+%F %T'); last trainer lines:"; tail -n 30 $OUT/QUEUE_$run.log; } > $OUT/$run/QUEUE_FAILED
      echo "[h100q] $run FAILED twice (reason in $OUT/$run/QUEUE_FAILED); the other runs continue"
    fi
    rm -f $OUT/$run/QUEUE_GPU
  ) &
  sleep 5
}

if [ "${DRY:-0}" = 1 ]; then
  for g in $GPUS; do echo "  GPU $g: $(used $g) MiB$(ours_on $g && echo ' (ours)')$(held $g && echo " (held for others until $(date -d @$(cat $OUT/H100_HOLD_$g) '+%m-%d %H:%M'))")"; done
  echo "[h100q] picking:"; NEXT=$(pick) && echo "[h100q] next: $NEXT" || echo "[h100q] nothing runnable now"
  echo "[h100q] micro batch: $(cat $OUT/H100_MB 2>/dev/null || echo 'not measured yet (smoke runs first)')"
  echo "[h100q] our trainers alive: $(running); cap $(max_runs)$([ -s $OUT/H100_MAX_RUNS ] && echo ' (from H100_MAX_RUNS)')"
  exit 0
fi
echo $$ > $OUT/H100_QUEUE.pid        # h100_restart.sh: one dispatcher at a time (removed when the main loop ends)
smoke || exit 1
echo "[h100q] $(date '+%F %T') micro x accumulation: $(cat $OUT/H100_MB)"
beat=0
while true; do
  [ -f $OUT/QUEUE_STOP_H100 ] && { echo "[h100q] QUEUE_STOP_H100 found: nothing new starts"; rm -f $OUT/QUEUE_STOP_H100 $OUT/H100_QUEUE.pid; break; }
  if [ $(( $(date +%s) - beat )) -ge 1800 ]; then         # heartbeat every 30 min: GPU memory and our runs
    beat=$(date +%s)
    echo "[h100q] $(date '+%F %T') GPUs: $(for g in $GPUS; do printf '%s:%sMiB%s ' $g "$(used $g)" "$(ours_on $g && echo '(ours)')"; done)ours alive $(running), cap $(max_runs)"
    echo "[h100q] $($PY scripts/fullft/gpu_share_report.py --short 2>/dev/null || echo 'GPU share: no samples (start scripts/fullft/gpu_share.sh)')"
  fi
  if ! NEXT=$(pick 2>/dev/null); then sleep 600; continue; fi
  if [ "$(running)" -ge "$(max_runs)" ]; then sleep 300; continue; fi     # the cap (user 11-17)
  if ! g=$(free_gpu); then sleep 60; continue; fi
  NEXT=$(pick) || continue          # re-pick with reasons in the log (the GPU look took up to a few minutes)
  [ "$(running)" -ge "$(max_runs)" ] && continue
  echo "[h100q] $(date '+%F %T') next: ${NEXT%%|*} on GPU $g (ours alive $(running), cap $(max_runs))"
  launch "${NEXT%%|*}" "${NEXT#*|}" "$g"
done
while pgrep -f "fastwam.fullft.train train" >/dev/null; do sleep 600; done
