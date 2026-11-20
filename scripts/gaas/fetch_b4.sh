#!/bin/bash
# NTU GaaS login node, 11-21 01:40 (plan v18 N1, Opus; user 01:11: if the group's other two H200s are free over the
# weekend, start two jobs that finish within 48 h). Two training-seed replicates of press_count (seed 18 / 19; lines in
# gaas_queue.txt). Run it ONLY after the check showed the two GPUs free. Steps:
#   1 the fast writer's two files from the relay (diag/press_fast, put there by the 5090 on 11-16; the old H200 trained
#     press_count on them): PRESS_FAST_RULE.json -> outputs/fullft/, events_press_button_fast.json -> outputs/fullft/events/
#     (an existing file is never overwritten; a different one is reported and nothing is submitted)
#   2 qsub press_count_s18 and press_count_s19, walltime 48 h (WALL_H=48: the trainer saves and stops 45 min before),
#     no dependency (they start as soon as PBS gives the GPUs). A run already submitted is not submitted again.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/fetch_b4.sh
# Log: ~/mwam/logs/FETCH_B4_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
mkdir -p $W/logs $R/outputs/fullft/events
LOG=$W/logs/FETCH_B4_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[b4] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-70)"
IN=$W/dl/press_fast; mkdir -p $IN
$HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/press_fast --out $IN 2>&1 | grep "\[relay\]" | tail -n 6
ok=1
place() {      # file in the download, destination
  local src=$IN/$1 dst=$2
  if [ -s $dst ]; then
    cmp -s $src $dst && say "$1 already in place (same file)" || { say "a DIFFERENT $1 is in place: kept, nothing submitted"; ok=0; }
  elif [ -s $src ]; then
    cp $src $dst && say "$1 copied ($(stat -c %s $dst) bytes, sha256 $(sha256sum $dst | cut -c1-16))"
  else
    say "FAILED: no $1 on the relay (diag/press_fast)"; ok=0
  fi
}
place PRESS_FAST_RULE.json $R/outputs/fullft/PRESS_FAST_RULE.json
place events_press_button_fast.json $R/outputs/fullft/events/events_press_button_fast.json
[ $ok = 1 ] || { say "nothing submitted"; exit 1; }
say "rule: $(cat $R/outputs/fullft/PRESS_FAST_RULE.json | tr -d '\n' | cut -c1-200)"
for run in press_count_s18 press_count_s19; do
  mkdir -p $R/outputs/fullft/$run
  if [ -s $R/outputs/fullft/$run/GAAS_JOB ] && qstat "$(cat $R/outputs/fullft/$run/GAAS_JOB)" > /dev/null 2>&1; then
    say "$run: already submitted ($(cat $R/outputs/fullft/$run/GAAS_JOB))"; continue
  fi
  j=$(cd $W && qsub -l walltime=48:00:00 -v RUN=$run,WALL_H=48 $R/scripts/gaas/gaas_run.pbs) || { say "$run: qsub FAILED"; continue; }
  echo "$j" > $R/outputs/fullft/$run/GAAS_JOB
  say "$run: submitted job $j (walltime 48 h)"
done
qstat -u "${USER:-$(id -un)}"
say "done"
