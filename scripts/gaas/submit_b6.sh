#!/bin/bash
# NTU GaaS login node, 11-22 (Opus, plan v19). Transfers and qsub only (training runs in the jobs):
#   1 state: our jobs, and the tail of each running job's log (are cover_arprop, ar2_tw, press_count_s18 / s19 alive;
#     did the upload-only job 116423 finish)
#   2 files: the put / swap event files from ~/mwam/dl/events_2task into outputs/fullft/events (never overwritten);
#     the observe_and_pickup training cache from the cache relay if it is not here (scripts/fullft/cache_relay.py get,
#     sha256 checked against its manifest)
#   3 qsub, in this order (a run that has SUMMARY.json or a queued / running job is skipped):
#     ar2_prop_novid (plan v19 B4, ~26 h), obs_none (~5-6 h), press_none (~17 h); walltime 48 h each.
#     The group quota decides when each starts; the order of submission is the order of start.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_b6.sh
# Log: ~/mwam/logs/SUBMIT_B6_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
mkdir -p $W/logs
LOG=$W/logs/SUBMIT_B6_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[b6] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free"
qstat -u "$(id -un)" 2>/dev/null | tail -n +4
for r in cover_arprop ar2_tw press_count_s18 press_count_s19 relay_backlog; do
  L=$(ls -t $W/logs/RUN_${r}_*.txt 2>/dev/null | head -1)
  say "$r: $(basename "${L:-none}"): $(grep -aE 'trainer exit|attempt|FAILED|finished|relay backlog:|relayed:|done' "$L" 2>/dev/null | tail -n 2 | tr '\n' ' ' | cut -c1-220)"
  [ -f $R/outputs/fullft/QUEUE_$r.log ] && say "$r: $(grep -a 'u [0-9]*/' $R/outputs/fullft/QUEUE_$r.log | tail -n 1 | cut -c1-120)"
done
for e in events_put_back_block events_swap_blocks; do
  D=$R/outputs/fullft/events/$e.json S=$W/dl/events_2task/$e.json
  if [ -s $D ]; then say "$e.json in place ($(sha256sum $D | cut -c1-16))"
  elif [ -s $S ]; then mkdir -p $(dirname $D); cp $S $D && say "$e.json copied from dl/events_2task"
  else say "$e.json MISSING (neither in place nor in dl/events_2task): ar2_prop_novid will wait"; fi
done
P=$R/outputs/memory_v2/press
if [ -f $P/dense_observe_and_pickup_v1/RELAY_MANIFEST.json ]; then say "observe cache here"
else
  say "observe cache: fetching from the cache relay"
  HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/fullft/cache_relay.py get --name dense_observe_and_pickup_v1 --dest $P 2>&1 | tail -n 4
  [ -f $P/dense_observe_and_pickup_v1/RELAY_MANIFEST.json ] && say "observe cache fetched ($(du -sh $P/dense_observe_and_pickup_v1 | cut -f1))" \
    || say "observe cache FAILED: obs_none will fail its data check; nothing else changes"
fi
for r in ar2_prop_novid obs_none press_none; do
  mkdir -p $R/outputs/fullft/$r
  [ -f $R/outputs/fullft/$r/SUMMARY.json ] && { say "$r: finished already, skipped"; continue; }
  if [ -s $R/outputs/fullft/$r/GAAS_JOB ] && qstat "$(cat $R/outputs/fullft/$r/GAAS_JOB)" > /dev/null 2>&1; then
    say "$r: job $(cat $R/outputs/fullft/$r/GAAS_JOB) still queued / running, skipped"; continue
  fi
  j=$(cd $W && qsub -l walltime=48:00:00 -v RUN=$r,WALL_H=48 $R/scripts/gaas/gaas_run.pbs) || { say "$r: qsub FAILED"; continue; }
  echo "$j" > $R/outputs/fullft/$r/GAAS_JOB
  say "$r: submitted job $j"
done
qstat -u "$(id -un)" 2>/dev/null | tail -n +4
say "done"
