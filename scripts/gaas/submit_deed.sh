#!/bin/bash
# NTU GaaS login node, 11-22 (Opus, plan v19 D2 / D1). Transfers and qsub only (training runs in the jobs):
#   1 state: our jobs
#   2 file: the provisional-writer events file of press (events_press_button_v3c.json) from the relay (diag/press_v3c)
#     into outputs/fullft/events (never overwritten; its rule field must say provisional=0.002)
#   3 qsub, in this order (plan v19 5.1: D2 first, then the two D1 arms; a run that has SUMMARY.json or a queued /
#     running job is skipped): d2_press (~17 h), d1_w, d1_wn (~26 h each); walltime 48 h. They queue behind the jobs
#     already queued (B4, obs_none, press_none); the group quota decides when each starts.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/submit_deed.sh
# Log: ~/mwam/logs/SUBMIT_DEED_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
mkdir -p $W/logs
LOG=$W/logs/SUBMIT_DEED_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[deed] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-70); home $(df -h $HOME | tail -n 1 | awk '{print $4}') free"
[ -f scripts/fullft/GO_deed ] || { say "no scripts/fullft/GO_deed in this checkout (git pull): stop"; exit 1; }
qstat -u "$(id -un)" 2>/dev/null | tail -n +4
E=$R/outputs/fullft/events/events_press_button_v3c.json
if [ -s $E ]; then say "v3c events in place ($(sha256sum $E | cut -c1-16))"
else
  IN=$R/outputs/fullft/relay_in/press_v3c
  mkdir -p $IN $(dirname $E)
  HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/press_v3c --out $IN 2>&1 | tail -n 2
  if [ -s $IN/events_press_button_v3c.json ] && grep -q "provisional=0.002" $IN/events_press_button_v3c.json; then
    cp $IN/events_press_button_v3c.json $E && say "v3c events fetched ($(sha256sum $E | cut -c1-16))"
  else
    say "v3c events NOT fetched (or rule field without provisional=0.002): d2_press would fail its check; D1 still submitted"
  fi
fi
for e in events_put_back_block events_swap_blocks; do
  [ -s $R/outputs/fullft/events/$e.json ] && say "$e.json in place" || say "$e.json MISSING: the D1 arms would fail their check"
done
for r in d2_press d1_w d1_wn; do
  if [ $r = d2_press ] && [ ! -s $E ]; then say "$r: no v3c events, not submitted"; continue; fi
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
