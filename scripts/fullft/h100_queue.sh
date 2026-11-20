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
#   * 11-17 19:42 / 19:51 (user; the 16:50 "at most 2 GPUs" is revoked): rotation and waiting exactly as before (every
#     free GPU by the 1-minute rule; we never preempt). Only when someone asks: h100_yield.sh <gpu> stops our training
#     there gracefully (resume.pt saved; the run goes back to its queue line and resumes on the next free GPU). A FREEZE
#     of a GPU exists only when set explicitly (h100_yield.sh <gpu> <hours> or h100_yield.sh hold <gpu> <hours>):
#     outputs/fullft/H100_HOLD_<gpu> = expiry time; this queue does not take a frozen GPU before then, and after it only
#     by the usual 1-minute rule (still in use by someone -> we wait). Other users' share of the GPUs (information only):
#     gpu_share.sh (sampler, every 10 min) + gpu_share_report.py (last 24 h); the heartbeat prints its one-line summary
#   docker exec -d mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/h100_queue.sh
#   DRY=1 ...   print the plan (next line, why the others wait, GPU memory) and exit
# Own log: outputs/fullft/H100_QUEUE_<time>.txt; trainer stdout: outputs/fullft/QUEUE_<run>.log
set -u
R=${R:-/workspace/FastWAM-memory2}
OUT=$R/outputs/fullft
QF=${QF:-$R/scripts/fullft/h100_queue.txt}
GPUS=${GPUS:-"0 1 2 3"}
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
held() {          # GPU $1 is frozen for another user (explicit h100_yield.sh hold) until H100_HOLD_<gpu>; expired go
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
claimed() {       # GPU $1 was claimed by a pick in the last 10 min (a stale claim is removed)
  local c=$OUT/H100_CLAIM_$1
  [ -d $c ] || return 1
  [ $(( $(date +%s) - $(stat -c %Y $c) )) -lt 600 ] && return 0
  rmdir $c 2>/dev/null; return 1
}
free_gpu() {      # prints the first free GPU (1-minute rule) and CLAIMS it, else returns 1
  # 11-20 fix: the main loop and a launcher's resumed retry both look for a free GPU; on 11-19 both picked the same
  # GPU three times within a minute and both trainers ran out of memory (rearrange_arprop, swapT_arprop lost). The
  # claim is an atomic mkdir after the looks: the second picker fails the mkdir and goes on to the next GPU. It lapses
  # after 10 min (the trainer holds > 1000 MiB long before that, and QUEUE_GPU marks it ours).
  local g k
  for g in $GPUS; do
    ours_on $g && continue
    held $g && continue
    claimed $g && continue
    for k in 1 2 3; do
      [ "$(used $g)" -lt 1000 ] || continue 2
      [ $k -lt 3 ] && sleep 30
    done
    mkdir $OUT/H100_CLAIM_$g 2>/dev/null || continue
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
  for g in $GPUS; do echo "  GPU $g: $(used $g) MiB$(ours_on $g && echo ' (ours)')$(held $g && echo " (frozen for others until $(date -d @$(cat $OUT/H100_HOLD_$g) '+%m-%d %H:%M'))")"; done
  echo "[h100q] picking:"; NEXT=$(pick) && echo "[h100q] next: $NEXT" || echo "[h100q] nothing runnable now"
  echo "[h100q] micro batch: $(cat $OUT/H100_MB 2>/dev/null || echo 'not measured yet (smoke runs first)')"
  echo "[h100q] our trainers alive: $(running)"
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
    echo "[h100q] $(date '+%F %T') GPUs: $(for g in $GPUS; do printf '%s:%sMiB%s ' $g "$(used $g)" "$(ours_on $g && echo '(ours)')"; done)ours alive $(running)"
    echo "[h100q] $($PY scripts/fullft/gpu_share_report.py --short 2>/dev/null || echo 'GPU share: no samples (start scripts/fullft/gpu_share.sh)')"
  fi
  if ! NEXT=$(pick 2>/dev/null); then sleep 600; continue; fi
  if ! g=$(free_gpu); then sleep 60; continue; fi
  NEXT=$(pick) || continue          # re-pick with reasons in the log (the GPU look took up to a few minutes)
  echo "[h100q] $(date '+%F %T') next: ${NEXT%%|*} on GPU $g"
  launch "${NEXT%%|*}" "${NEXT#*|}" "$g"
done
while pgrep -f "fastwam.fullft.train train" >/dev/null; do sleep 600; done
