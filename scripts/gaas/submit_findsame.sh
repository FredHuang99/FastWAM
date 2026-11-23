#!/bin/bash
# NTU GaaS login node, 11-23 (Opus; user 15:28 agreed): the find-same fix obs_pose takes the GPU that ar2_tw frees
# (~11-24 05:40); press_none moves behind d1_wn (~11-24 12:00). We still hold at most 4 GPUs (user 11-22 23:53).
#   1 events file of observe_and_pickup from the relay (diag/events_obs; the 5090's file that obs_arprop used) ->
#     outputs/fullft/events/events_observe_and_pickup.json (an existing file is never overwritten)
#   2 qsub obs_pose with depend=afterany on ar2_tw's job (NO_RESUBMIT: chained), walltime 48 h
#   3 press_none's job: its dependency moved from ar2_tw onto d1_wn (qalter); nothing else is changed
#   Stops without submitting when ar2_tw or d1_wn has no live job, or another of our queued jobs already waits on d1_wn
#   (two jobs behind one would take a fifth GPU).
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_findsame.sh
# Log: ~/mwam/logs/SUBMIT_FS_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
F=$R/outputs/fullft
HFPY=$W/envs/hf-tools/bin/python
PRESS_NONE=116648                 # use_spare_gpu.sh 11-22: press_none's job, released after ar2_tw
mkdir -p $W/logs $F/events
LOG=$W/logs/SUBMIT_FS_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[fs] $(date '+%F %T') $*"; }
cd $R
ME=$(id -un)
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free"
grep -q '^obs_pose |' scripts/gaas/gaas_queue.txt || { say "no obs_pose line in gaas_queue.txt (git pull): stop"; exit 1; }
qstat -u "$ME" -w 2>/dev/null | tail -n +4

# 1 events file
E=$F/events/events_observe_and_pickup.json
if [ -s $E ]; then say "events_observe_and_pickup.json in place ($(sha256sum $E | cut -c1-16))"
else
  IN=$F/relay_in/events_obs; mkdir -p $IN
  HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_obs --out $IN 2>&1 | grep "\[relay\]" | tail -n 3
  [ -s $IN/events_observe_and_pickup.json ] || { say "FAILED: no events_observe_and_pickup.json on the relay: nothing submitted"; exit 1; }
  cp $IN/events_observe_and_pickup.json $E && say "events fetched ($(stat -c %s $E) bytes, sha256 $(sha256sum $E | cut -c1-16))"
fi
say "events file: $(grep -o '"close"' $E | wc -l) close events"

# 2 / 3 jobs
live() { local a; a=$(cat $F/$1/GAAS_JOB 2>/dev/null); [ -n "$a" ] && qstat "$a" > /dev/null 2>&1 && echo "$a"; }
AR=$(live ar2_tw); WN=$(live d1_wn)
[ -n "$AR" ] || { say "ar2_tw has no live job (finished?): nothing submitted; tell Opus (a GPU may be free now)"; exit 1; }
[ -n "$WN" ] || { say "d1_wn has no live job: nothing submitted; tell Opus"; exit 1; }
wn=${WN%%.*}; ar=${AR%%.*}
for j in $(qselect -u "$ME" -s QH 2>/dev/null); do
  [ "${j%%.*}" = "$PRESS_NONE" ] && continue
  if qstat -f "$j" 2>/dev/null | tr -d '\n\t ' | grep -o 'depend=[^,]*' | grep -q "$wn"; then
    say "job ${j%%.*} already waits on d1_wn ($wn): nothing submitted (press_none behind it would be a fifth GPU); tell Opus"; exit 1
  fi
done
mkdir -p $F/obs_pose
if [ -s $F/obs_pose/GAAS_JOB ] && qstat "$(cat $F/obs_pose/GAAS_JOB)" > /dev/null 2>&1; then
  say "obs_pose: job $(cat $F/obs_pose/GAAS_JOB) already queued"
elif [ -f $F/obs_pose/SUMMARY.json ]; then
  say "obs_pose: finished already"
else
  J=$(cd $W && qsub -W depend=afterany:$AR -l walltime=48:00:00 -v RUN=obs_pose,WALL_H=48,NO_RESUBMIT=1,AUTO_CLEAN=1 \
      $R/scripts/gaas/gaas_run.pbs) || { say "obs_pose: qsub FAILED"; exit 1; }
  echo "$J" > $F/obs_pose/GAAS_JOB
  say "obs_pose: job $J, starts when ar2_tw ($ar) ends"
fi
ps=$(qstat -f $PRESS_NONE 2>/dev/null | awk -F' = ' '/job_state/{print $2}')
po=$(qstat -f $PRESS_NONE 2>/dev/null | awk -F' = ' '/Job_Owner/{split($2, a, "@"); print a[1]}')
if [ "$po" = "$ME" ] && { [ "$ps" = H ] || [ "$ps" = Q ]; }; then
  qalter -W depend=afterany:$WN $PRESS_NONE && say "press_none ($PRESS_NONE): now after d1_wn ($wn)" \
    || say "press_none: qalter FAILED (it still follows ar2_tw: the two jobs would start together; tell Opus)"
else
  say "press_none job $PRESS_NONE is not our queued / held job (state '${ps:-gone}'): left as it is; tell Opus"
fi
for j in $(qselect -u "$ME" 2>/dev/null); do
  printf '  %-10s %-14s %s  %s\n' "${j%%.*}" "$(qstat -f $j | awk -F' = ' '/Job_Name/{print $2}')" \
    "$(qstat -f $j | awk -F' = ' '/job_state/{print $2}')" "$(qstat -f $j | tr -d '\n\t ' | grep -o 'depend=[^,]*' | head -1)"
done
say "done"
