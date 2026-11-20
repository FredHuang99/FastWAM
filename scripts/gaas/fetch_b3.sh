#!/bin/bash
# NTU GaaS login node, 11-20 20:00 (plan v16, Opus; user 19:12). New H200 line A after ranking_ar (~11-21 06:30): cover's
# ledger version cover_arprop (current setting; see the gaas_queue.txt line). Steps:
#   1 the event file of cover_blocks from the relay (diag/events_b1, put there by the 5090 on 11-17; the H100 used the
#     same file) -> outputs/fullft/events/events_cover_blocks.json (an existing file is never overwritten)
#   2 qsub cover_arprop with PBS depend=afterany on ranking_ar's job (same lane, still 2 GPUs at a time). If ranking_ar's
#     job is no longer queued, NOTHING is submitted (a plain qsub would take a third GPU); the log says so.
#   The job runs the repository's current gaas_run.pbs (git pull + hand-over), which makes READY_arprop_cover_blocks.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/fetch_b3.sh
# Log: ~/mwam/logs/FETCH_B3_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
mkdir -p $W/logs $R/outputs/fullft/events
LOG=$W/logs/FETCH_B3_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[b3] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-70)"
IN=$W/dl/events_b1; mkdir -p $IN
$HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_b1 --out $IN 2>&1 | grep "\[relay\]" | tail -n 6
E=$R/outputs/fullft/events/events_cover_blocks.json
if [ -s $E ]; then
  cmp -s $IN/events_cover_blocks.json $E && say "events_cover_blocks.json already in place (same file)" \
    || say "a DIFFERENT events_cover_blocks.json is in place: kept, not overwritten"
elif [ -s $IN/events_cover_blocks.json ]; then
  cp $IN/events_cover_blocks.json $E && say "events_cover_blocks.json copied ($(stat -c %s $E) bytes, sha256 $(sha256sum $E | cut -c1-16))"
else
  say "FAILED: no events_cover_blocks.json on the relay (diag/events_b1): nothing submitted"; exit 1
fi
lane_job() { local a; a=$(cat $R/outputs/fullft/$1/GAAS_JOB 2>/dev/null); [ -n "$a" ] && qstat "$a" > /dev/null 2>&1 && echo "$a"; }
RANK=$(lane_job ranking_ar)
[ -n "$RANK" ] || { say "ranking_ar's job is not queued any more: nothing submitted (would take a third GPU); tell Opus"; qstat -u "${USER:-$(id -un)}"; exit 1; }
mkdir -p $R/outputs/fullft/cover_arprop
if [ -s $R/outputs/fullft/cover_arprop/GAAS_JOB ]; then
  say "cover_arprop: already submitted ($(cat $R/outputs/fullft/cover_arprop/GAAS_JOB))"
else
  j=$(cd $W && qsub -W depend=afterany:$RANK -v RUN=cover_arprop $R/scripts/gaas/gaas_run.pbs) || { say "qsub FAILED"; exit 1; }
  echo "$j" > $R/outputs/fullft/cover_arprop/GAAS_JOB
  say "cover_arprop: submitted job $j (depend=afterany:$RANK)"
fi
qstat -u "${USER:-$(id -un)}"
for r in ranking_ar cover_ar press_clock; do
  L=$(ls -t $R/outputs/fullft/$r/logs/train_*.txt 2>/dev/null | head -1)
  [ -n "$L" ] && say "$r: $(grep -a 'u [0-9]*/\|summary' $L | tail -n 1 | cut -c1-150)"
done
say "done"
