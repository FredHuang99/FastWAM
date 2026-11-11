#!/usr/bin/env bash
# mwam2 container (H200, GPU0 only = ours; plan v12 F.2, Opus checklist 13): train the runs of h200_queue.txt one
# after another on GPU0, so the H200 never waits for a human.
#   * the queue file is RE-READ before every pick (edit it, git pull, the next pick sees it)
#   * pick = the first line whose run is neither finished (<run>/SUMMARY.json) nor failed (<run>/QUEUE_FAILED) and
#     whose condition (third field, a shell test run in the repo) holds; a line whose condition fails is skipped for
#     now and tried again at the next pick (e.g. P1 waits for its code; Press-AR runs first)
#   * waits until GPU0 has < 2000 MiB in use and no fullft trainer runs (N7 first finishes by itself)
#   * per run: export_watch.sh RUN=<run> in the background (exports e10 / e20 / e30 go to the relay as they appear),
#     then `fastwam.fullft.train train --config configs/fullft/base_2task.yaml --set name=<run> <sets>`;
#     no SUMMARY.json after the trainer exits -> one resumed retry; still none -> <run>/QUEUE_FAILED and the queue
#     STOPS (exit 1) with the reason in its log
#   * outputs/fullft/QUEUE_STOP: finish the current run, then stop
#   docker exec -d mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/h200_queue.sh
#   DRY=1 ...   print the plan (which line would run next and why the others wait) and exit
# Own log: outputs/fullft/H200_QUEUE_<time>.txt; trainer stdout: outputs/fullft/QUEUE_<run>.log
set -u
R=/workspace/FastWAM-memory2
OUT=$R/outputs/fullft
QF=${QF:-$R/scripts/fullft/h200_queue.txt}
mkdir -p $OUT
LOG=$OUT/H200_QUEUE_$(date +%Y%m%d_%H%M)$([ "${DRY:-0}" = 1 ] && echo _dry).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[queue] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=8
PY=/opt/mwam/bin/python
echo "[queue] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); queue file $QF"

pick() {          # prints "run|sets" of the next runnable line; reasons for the others go to stderr
  local run sets cond
  while IFS='|' read -r run sets cond; do
    run=$(echo "$run" | xargs); sets=$(echo "$sets" | xargs); cond=$(echo "${cond:-}" | xargs)
    [ -z "$run" ] && continue; case "$run" in \#*) continue;; esac
    if [ -f $OUT/$run/SUMMARY.json ]; then echo "  $run: finished" >&2; continue; fi
    if [ -f $OUT/$run/QUEUE_FAILED ]; then echo "  $run: FAILED earlier (see $OUT/$run/QUEUE_FAILED)" >&2; continue; fi
    if [ -n "$cond" ] && ! bash -c "$cond" >/dev/null 2>&1; then echo "  $run: waits (condition: $cond)" >&2; continue; fi
    echo "$run|$sets"; return 0
  done < <(grep -v '^[[:space:]]*$' "$QF")
  return 1
}

while true; do
  [ -f $OUT/QUEUE_STOP ] && { echo "[queue] QUEUE_STOP found: stopping"; rm -f $OUT/QUEUE_STOP; exit 0; }
  echo "[queue] $(date '+%F %T') picking:"
  if ! NEXT=$(pick); then
    if [ "${DRY:-0}" = 1 ]; then echo "[queue] nothing runnable now"; exit 0; fi
    echo "[queue] $(date '+%F %T') nothing runnable now; next look in 10 min"; sleep 600; continue
  fi
  RUN=${NEXT%%|*}; SETS=${NEXT#*|}
  echo "[queue] next: $RUN  sets: $SETS"
  [ "${DRY:-0}" = 1 ] && exit 0
  until used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 0 | tr -d ' ') && [ "$used" -lt 2000 ] \
        && ! pgrep -f "fastwam.fullft.train" >/dev/null; do
    echo "[queue] $(date '+%F %T') GPU0 busy ($used MiB) or a trainer runs; waiting"; sleep 300
  done
  ARGS=(); for s in $SETS; do ARGS+=(--set "$s"); done
  RUN=$RUN nohup bash scripts/fullft/export_watch.sh > /dev/null 2>&1 &
  for attempt in 1 2; do
    echo "[queue] $(date '+%F %T') ===== $RUN attempt $attempt (GPU0 $used MiB before)"
    $PY -m fastwam.fullft.train train --config configs/fullft/base_2task.yaml --set name=$RUN "${ARGS[@]}" \
      >> $OUT/QUEUE_$RUN.log 2>&1
    rc=$?
    echo "[queue] $(date '+%F %T') $RUN trainer exit code $rc"
    [ -f $OUT/$RUN/SUMMARY.json ] && break
    [ $attempt = 1 ] && { echo "[queue] no SUMMARY.json: one resumed retry in 2 min"; sleep 120; }
  done
  if [ ! -f $OUT/$RUN/SUMMARY.json ]; then
    mkdir -p $OUT/$RUN
    { echo "exit code $rc at $(date '+%F %T'); last trainer lines:"; tail -n 30 $OUT/QUEUE_$RUN.log; } > $OUT/$RUN/QUEUE_FAILED
    echo "[queue] $RUN FAILED twice: the queue stops here (reason in $OUT/$RUN/QUEUE_FAILED)"; cat $OUT/$RUN/QUEUE_FAILED; exit 1
  fi
  echo "[queue] $(date '+%F %T') $RUN finished: $(head -c 400 $OUT/$RUN/SUMMARY.json)"
done
