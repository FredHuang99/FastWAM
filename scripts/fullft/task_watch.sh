#!/usr/bin/env bash
# mwam5090 (11-14): evaluate single-task fullft runs as their exports reach the relay, with nobody at the keyboard.
# For each run in RUNS, and within it each tag in TAGS: wait for exports/<run>_<tag>/export_<tag>.pt.sha256 on the
# relay, fetch + sha256 check, then official scenes 1-N of TASK, execute 8, 10 steps, fixed pipeline (OIDN 2.0.1 +
# training-cache text), shard 0/2 on GPU0 and 1/2 on GPU1 in parallel (each GPU empty for 90 s first), up to 3 attempts;
# label <run>_<tag> in closed_loop/g1; marker exports/<run>_<tag>/.evaluated only with N finished episodes.
# Descriptive (progress / same-machine comparisons); registered verdicts are written separately before the runs.
#   docker exec -d -e RUNS="press_arprop press_ar" -e TASK=press_button mwam5090 bash .../scripts/fullft/task_watch.sh
# Env: RUNS, TASK, TAGS ("e10 e20 e30"), N (50), POLL (300). Own log: outputs/memory_v2/report/TASK_WATCH_<task>_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
RUNS=${RUNS:?}; TASK=${TASK:?}; TAGS=${TAGS:-"e10 e20 e30"}; N=${N:-50}; POLL=${POLL:-300}
LOG=$O/report/TASK_WATCH_${TASK}_$(date +%Y%m%d_%H%M).txt
mkdir -p $O/report
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[tw] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
BANK=$O/closed_loop/scenes_seed42_n100_$TASK
[ -d $BANK ] || { echo "no scene bank $BANK"; exit 1; }
echo "[tw] $(date '+%F %T') start; runs $RUNS; task $TASK; tags $TAGS; N $N"
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
stable() { empty $1 && sleep 90 && empty $1; }
n_done() { ls $O/closed_loop/g1/$1/on/$TASK/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
for RUN in $RUNS; do          # run by run (its exports arrive e10 -> e20 -> e30 before the next run's)
  for TAG in $TAGS; do
    E=$R/outputs/fullft/exports/${RUN}_${TAG}; L=${RUN}_${TAG}
    [ -f $E/.evaluated ] && { echo "[tw] $L: already evaluated"; continue; }
    echo "[tw] $(date '+%F %T') waiting for exports/$L on the relay"
    until $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/$L --repo hhyfred/memwam-fullft 2>/dev/null \
          | grep -q "^export_${TAG}.pt.sha256 "; do sleep $POLL; done
    [ -f $E/export_${TAG}.pt ] || $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft \
        --out $E 2>&1 | grep -v "Processing\|Download\|%|"
    (cd $E && sha256sum -c export_${TAG}.pt.sha256) || { echo "[tw] $L sha256 mismatch: delete $E and rerun"; continue; }
    pids=""
    for g in 0 1; do
      ( for attempt in 1 2 3; do
          until stable $g; do sleep 120; done
          echo "[tw] $(date '+%F %T') $L shard $g/2 on GPU $g (attempt $attempt)"
          CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $E/export_${TAG}.pt --label $L --scenes $BANK \
            --tasks $TASK --limit $N --shard $g/2 --execute 8 --output $O/closed_loop/g1 >> $O/closed_loop/g1_$L.log 2>&1
          [ "$(n_done $L)" -ge "$N" ] && exit 0
          sleep 60
        done ) &
      pids="$pids $!"
    done
    wait $pids     # never a bare `wait` after `exec > >(tee)`
    if [ "$(n_done $L)" -ge "$N" ]; then
      touch $E/.evaluated
      echo "[tw] $(date '+%F %T') $L done:"
      $PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label $L --out /dev/null 2>/dev/null | grep -E "/on " | head -n 3
    else
      echo "[tw] $(date '+%F %T') $L incomplete ($(n_done $L)/$N): NOT marked; rerun this script"
    fi
  done
done
