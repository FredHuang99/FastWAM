#!/bin/bash
# NTU GaaS login node, 11-28 17:00 (Opus; plan v22b part 3 section 5, user step 3). Copy of submit_v21.sh with the plan
# v22 chains: FOUR follower slot jobs behind each of the four running / held lanes, so no GPU waits for a human:
#   D8-D11 behind D7 (card 25 obs_cf200, ~19:30 tonight)    A8-A11 behind A7 (card 23 ar2_pw, ~11-29 11:45)
#   B8-B11 behind B7 (obs_s800_20, ~11-30 08:30)            C6-C9 behind C5 (held; obs_s1600 from ~18:10 to ~12-01 05:00)
# The lists are in scripts/gaas/slots.txt (plan v22b 1.0 priority order, then the fillers); a job reads its list when it
# starts, so lists can change later without resubmitting. Still at most 4 GPUs: every new job waits (afterany) on the job
# before it in its lane. Re-running is safe: a slot whose job is queued / running is skipped.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_v22.sh
# Log: ~/mwam/logs/SUBMIT_V22_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
F=$R/outputs/fullft
SD=$W/slots
mkdir -p $W/logs $SD
LOG=$W/logs/SUBMIT_V22_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[v22] $(date '+%F %T') $*"; }
cd $R
ME=$(id -un)
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free"
[ -f scripts/gaas/slots.txt ] && grep -q '^swapT_ow_s18 |' scripts/gaas/gaas_queue.txt && grep -q '^D8 |' scripts/gaas/slots.txt || { say "slots.txt / the plan v22 lines are missing (git pull): stop"; exit 1; }
live() { [ -n "$1" ] && qstat "$1" > /dev/null 2>&1; }
jstate() { qstat -f "$1" 2>/dev/null | awk -F' = ' '/job_state/{print $2}'; }
# 11-24 18:35: the depend attribute only (qstat -f prints "    depend = afterany:116646.gaas@gaas"); the earlier
# squeeze-and-grep also caught Error_Path=...mwam_run.e<own id>, so B2 was refused as "118109 waits on 118109"
deps() { qstat -f "$1" 2>/dev/null | sed -n 's/^[[:space:]]*depend = //p' | head -1 | cut -d@ -f1; }
jobof() { local j; j=$(cat $F/$1/GAAS_JOB 2>/dev/null); [ -n "$j" ] || j=$2; live "$j" && echo "$j"; }
free_starters() {   # our jobs running, or queued without a dependency (they start as soon as a GPU is free)
  local n=0 j s
  for j in $(qselect -u "$ME" 2>/dev/null); do
    s=$(jstate "$j")
    if [ "$s" = R ]; then n=$((n + 1)); elif [ "$s" = Q ] && [ -z "$(deps "$j")" ]; then n=$((n + 1)); fi
  done
  echo $n
}
waits_on() {        # another of our queued / held jobs already depends on job $1 (then a new follower = a 5th GPU)
  local j t=${1%%.*}
  for j in $(qselect -u "$ME" -s QH 2>/dev/null); do
    deps "$j" | grep -q "$t" && { echo "${j%%.*}"; return 0; }
  done
  return 1
}
slot() {            # slot [job it follows]
  local s=$1 dep=${2:-} j w
  j=$(cat $SD/$s.job 2>/dev/null)
  if live "$j"; then say "slot $s: job $j already $(jstate $j)"; return 0; fi
  if [ -n "$dep" ] && live "$dep"; then
    if w=$(waits_on "$dep"); then say "slot $s: job $w already waits on ${dep%%.*}: not submitted (would be a 5th GPU)"; return 1; fi
    j=$(cd $W && qsub -W depend=afterany:$dep -l walltime=96:00:00 -v RUN=@$s,WALL_H=96 $R/scripts/gaas/gaas_run.pbs) \
      || { say "slot $s: qsub FAILED"; return 1; }
    say "slot $s: job $j, starts when ${dep%%.*} ends"
  else
    [ -n "$dep" ] && say "slot $s: the job it was to follow (${dep:-none}) is gone: its GPU is free"
    if [ "$(free_starters)" -ge 4 ]; then say "slot $s: 4 of our jobs already run / wait without a dependency: not submitted"; return 1; fi
    j=$(cd $W && qsub -l walltime=96:00:00 -v RUN=@$s,WALL_H=96 $R/scripts/gaas/gaas_run.pbs) || { say "slot $s: qsub FAILED"; return 1; }
    say "slot $s: job $j, starts now (no dependency)"
  fi
  echo "$j" > $SD/$s.job
}
qstat -u "$ME" -w 2>/dev/null | tail -n +4
say "lanes now: D7 $(cat $SD/D7.job 2>/dev/null) A7 $(cat $SD/A7.job 2>/dev/null) B7 $(cat $SD/B7.job 2>/dev/null) C5 $(cat $SD/C5.job 2>/dev/null)"
# Four followers per lane (plan v22b part 3 section 4 item 1: at least 4 behind each card). Each follower waits on the
# one before it (afterany), so a lane never holds more than one GPU; the lists are read when each job starts.
for lane in "D7 D8 D9 D10 D11" "A7 A8 A9 A10 A11" "B7 B8 B9 B10 B11" "C5 C6 C7 C8 C9"; do
  set -- $lane; prev=$1; shift
  for s in "$@"; do slot $s "$(cat $SD/$prev.job 2>/dev/null)" || break; prev=$s; done
done
for j in $(qselect -u "$ME" 2>/dev/null); do
  printf '  %-10s %-12s %-3s %-26s %s\n' "${j%%.*}" "$(qstat -f $j | awk -F' = ' '/Job_Name/{print $2}')" "$(jstate $j)" \
    "$(deps $j)" "$(qstat -f $j | tr -d '\n\t' | grep -o 'RUN=[^,]*' | head -1)"
done
say "done; each slot job writes ~/mwam/logs/PICK_<slot>_<time>.txt (what it picked and why) and RUN_<run>_<time>.txt"
