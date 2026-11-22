#!/bin/bash
# NTU GaaS login node, 11-22 (Opus). The group may use at most 4 GPUs (user 11-22 13:07); PBS itself let 10 of our jobs
# run on 11-22 04:00 and all ten died at 05:21. From now on our runs go as FOUR CHAINS: within a chain each job starts
# only after the previous one ended (qsub -W depend=afterany), so at most 4 run at once, and nothing runs on the login
# node. Chained jobs never resubmit themselves (NO_RESUBMIT=1); a job that fails or stops lets the chain go on.
#   chain A  press_count_s19 (~3 h, resumes at 9000) -> d2_press (~17 h) -> d1_w (~32 h)
#   chain B  press_count_s18 (~5 h, resumes at 8000) -> obs_none (~2 h, resumes) -> obs_zoom (~4 h; fetches its zoom
#            latents from the cache relay itself) -> d1_wn (~32 h)
#   (11-22 13:20: the two nearly finished seed replicates go first: with --auto-clean they free 2 x 68 GB within ~5 h,
#   which gives the later runs room for two checkpoint saves at once; D2 starts ~3 h later than first planned)
#   chain C  cover_arprop (~21 h, resumes) -> ar2_prop_novid (~31 h)
#   chain D  ar2_tw (~36 h, resumes) -> press_none (~13 h)
#   [estimates: updates left / the 11-21-22 rates; plan v19 5.1 order D2 -> A3 -> D1 first, the main-table runs next]
# A run with SUMMARY.json is left out. Refuses to submit while any job of ours is queued or running (the chains would
# exceed 4). Walltime per job: about 1.6 x the estimate (no job comes near it, so no STOP / resubmit).
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_chains.sh [--auto-clean]
#   --auto-clean: a finished run's resume.pt (~72 GB) is removed once its last export is on the relay (AUTO_CLEAN=1;
#   only with the user's approval)
# Log: ~/mwam/logs/SUBMIT_CHAINS_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
mkdir -p $W/logs
LOG=$W/logs/SUBMIT_CHAINS_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[chains] $(date '+%F %T') $*"; }
CLEAN=0; [ "${1:-}" = --auto-clean ] && CLEAN=1
cd $R
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free; auto-clean $CLEAN"
live=$(qstat -u "$(id -un)" 2>/dev/null | awk 'NR > 5 && ($10 == "Q" || $10 == "R" || $10 == "H")' | wc -l)
if [ "$live" -gt 0 ]; then
  qstat -u "$(id -un)" | tail -n +4
  say "$live job(s) of ours are queued or running: nothing submitted (the chains would exceed 4 GPUs)"; exit 1
fi
declare -A HOURS=([d2_press]=30 [d1_w]=52 [d1_wn]=52 [press_count_s18]=12 [press_count_s19]=12 [obs_none]=10 [obs_zoom]=10
                  [cover_arprop]=36 [ar2_prop_novid]=52 [ar2_tw]=60 [press_none]=24)
chain() {        # name, runs...
  local name=$1 prev="" r j dep; shift
  for r in "$@"; do
    if [ -f $R/outputs/fullft/$r/SUMMARY.json ]; then say "chain $name: $r finished already, left out"; continue; fi
    grep -v '^[[:space:]]*#' scripts/gaas/gaas_queue.txt | awk -F'|' '{x=$1; gsub(/[[:space:]]/, "", x); print x}' | grep -qx "$r" \
      || { say "chain $name: no queue line for $r, left out"; continue; }
    dep=(); [ -n "$prev" ] && dep=(-W depend=afterany:$prev)
    mkdir -p $R/outputs/fullft/$r
    j=$(cd $W && qsub "${dep[@]}" -l walltime=${HOURS[$r]}:00:00 -v RUN=$r,WALL_H=${HOURS[$r]},NO_RESUBMIT=1,AUTO_CLEAN=$CLEAN \
        $R/scripts/gaas/gaas_run.pbs) || { say "chain $name: qsub FAILED for $r; the chain stops here"; return 1; }
    echo "$j" > $R/outputs/fullft/$r/GAAS_JOB
    say "chain $name: $r -> job $j${prev:+ (after $prev)}, walltime ${HOURS[$r]} h"
    prev=$j
  done
}
chain A press_count_s19 d2_press d1_w
chain B press_count_s18 obs_none obs_zoom d1_wn
chain C cover_arprop ar2_prop_novid
chain D ar2_tw press_none
qstat -u "$(id -un)" 2>/dev/null | tail -n +4
say "done"
