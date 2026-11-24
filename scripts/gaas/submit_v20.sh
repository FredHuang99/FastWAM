#!/bin/bash
# NTU GaaS login node, 11-24 (Opus; plan v20 2.4a / section 5: card 1 now, card 3 on the GPU ar2_prop_novid frees
# (~18:30), card 4 on d1_w's (~20:00), the first ready of cards 5 / 6 / 7 else card 2 on press_none's (~11-25 00:50)).
# qsub / qstat only (no programs on the login node): every data fetch and check runs inside the job (gaas_run.pbs).
# Each lane gets SLOT jobs (RUN=@<slot>, scripts/gaas/slots.txt): the job picks, when it starts, the first ready run of
# its list, so a card whose prerequisites are missing is passed over and no GPU waits.
#   lane 1 (the GPU free since obs_pose): @A now (card 1 rearr_v3c_h2), then @A2 behind it
#   lane 2 behind ar2_prop_novid: @B (card 3 swapT_arprop_h2), then @B2 behind it (swapT_long)
#   lane 3 behind d1_w:           @C (card 4 ranking_v3c)
#   lane 4 behind press_none:     @D (card 5 / 6 / 7 when ready, else card 2 ar2_v3c)
# At most 4 GPUs of ours (user 11-22 23:53): a job without a dependency is submitted only while fewer than 4 of our jobs
# run or wait without one; a lane whose job already has a follower is left alone. Re-running this is safe (a slot whose
# job is queued / running is skipped; job ids in ~/mwam/slots/<slot>.job).
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_v20.sh
# Log: ~/mwam/logs/SUBMIT_V20_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
F=$R/outputs/fullft
SD=$W/slots
mkdir -p $W/logs $SD
LOG=$W/logs/SUBMIT_V20_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[v20] $(date '+%F %T') $*"; }
cd $R
ME=$(id -un)
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free"
[ -f scripts/gaas/slots.txt ] && grep -q '^rearr_v3c_h2 |' scripts/gaas/gaas_queue.txt || { say "slots.txt / the plan v20 lines are missing (git pull): stop"; exit 1; }
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
NOVID=$(jobof ar2_prop_novid 116646); D1W=$(jobof d1_w 116640); PNONE=$(jobof press_none 116648)
say "running now: ar2_prop_novid ${NOVID:-gone}, d1_w ${D1W:-gone}, press_none ${PNONE:-gone}"
slot A                                  # card 1 on the idle GPU
slot A2 "$(cat $SD/A.job 2>/dev/null)"
slot B "$NOVID"                         # card 3 (ar2_prop_novid's GPU)
slot B2 "$(cat $SD/B.job 2>/dev/null)"  # swapT_long behind it
slot C "$D1W"                           # card 4 (d1_w's GPU)
slot D "$PNONE"                         # cards 5 / 6 / 7, else card 2 (press_none's GPU)
# 11-24 20:40: one more behind each lane's last job (cards 7 / 8, then card 2), still 4 GPUs at most
slot A3 "$(cat $SD/A2.job 2>/dev/null)"
slot B3 "$(cat $SD/B2.job 2>/dev/null)"
slot D2 "$(cat $SD/D.job 2>/dev/null)"
for j in $(qselect -u "$ME" 2>/dev/null); do
  printf '  %-10s %-12s %-3s %-26s %s\n' "${j%%.*}" "$(qstat -f $j | awk -F' = ' '/Job_Name/{print $2}')" "$(jstate $j)" \
    "$(deps $j)" "$(qstat -f $j | tr -d '\n\t' | grep -o 'RUN=[^,]*' | head -1)"
done
say "done; each slot job writes ~/mwam/logs/PICK_<slot>_<time>.txt (what it picked and why) and RUN_<run>_<time>.txt"
