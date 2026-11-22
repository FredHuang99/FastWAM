#!/bin/bash
# NTU GaaS login node, 11-22 (Opus, plan v19 A3). Transfers and qsub only (training runs in the job):
#   1 the zoom latents zoom_obs_02102ba0 from the cache relay (built on the 5090 by zoom_build_5090.sh; sha256 against
#     their manifest) into outputs/memory_v2/press/ (skipped when already here)
#   2 qsub obs_zoom (~5-6 h, walltime 24 h); a run with SUMMARY.json or a queued / running job is skipped
#   3 plan v19 5.1 order is D2 -> A3 -> D1: if d1_w (or else d1_wn) is still queued, `qorder` swaps it with obs_zoom so
#     the zoom run starts before the D1 arms (D2 keeps its place); if qorder is refused, the order stays and this says so
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_zoom.sh
# Log: ~/mwam/logs/SUBMIT_ZOOM_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
NAME=zoom_obs_02102ba0
mkdir -p $W/logs
LOG=$W/logs/SUBMIT_ZOOM_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[zoom] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free"
P=$R/outputs/memory_v2/press
if [ -f $P/$NAME/ZOOM.json ]; then say "$NAME here"
else
  HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/fullft/cache_relay.py get --name $NAME --dest $P 2>&1 | tail -n 3
  [ -f $P/$NAME/ZOOM.json ] && say "$NAME fetched ($(du -sh $P/$NAME | cut -f1))" || { say "$NAME NOT fetched: nothing submitted"; exit 1; }
fi
r=obs_zoom
mkdir -p $R/outputs/fullft/$r
if [ -f $R/outputs/fullft/$r/SUMMARY.json ]; then say "$r: finished already"; exit 0; fi
if [ -s $R/outputs/fullft/$r/GAAS_JOB ] && qstat "$(cat $R/outputs/fullft/$r/GAAS_JOB)" > /dev/null 2>&1; then
  say "$r: job $(cat $R/outputs/fullft/$r/GAAS_JOB) still queued / running"
else
  j=$(cd $W && qsub -l walltime=24:00:00 -v RUN=$r,WALL_H=24 $R/scripts/gaas/gaas_run.pbs) || { say "$r: qsub FAILED"; exit 1; }
  echo "$j" > $R/outputs/fullft/$r/GAAS_JOB
  say "$r: submitted job $j"
fi
J=$(cat $R/outputs/fullft/$r/GAAS_JOB)
for d in d1_w d1_wn; do
  F=$R/outputs/fullft/$d/GAAS_JOB
  [ -s $F ] || continue
  if qstat -f "$(cat $F)" 2>/dev/null | grep -q "job_state = Q"; then
    if qorder "$(cat $F)" "$J" 2>&1; then say "qorder: $r ($J) now before $d ($(cat $F))"
    else say "qorder refused: the order stays (obs_zoom after the D1 arms)"; fi
    break
  fi
done
qstat -u "$(id -un)" 2>/dev/null | tail -n +4
say "done"
