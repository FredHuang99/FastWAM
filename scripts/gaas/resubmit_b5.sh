#!/bin/bash
# NTU GaaS login node, 11-21 14:40 (Opus). Every job that started after 11-21 01:49 failed at "sandbox from the SIF"
# (cover_arprop 115871 07:06, ar2_tw 115034 11:10, press_count_s18 / s19 115933 / 115934 01:49); the build's own error was
# thrown away. gaas_run.pbs (this commit) now logs the node's free space and the build error, and runs the SIF directly
# when no sandbox can be built. This script:
#   1 prints what could explain it: home usage / quota, the biggest run folders, the SIF, each failed job's node
#   2 resubmits the four runs (a run with SUMMARY.json, or whose job is still queued / running, is skipped):
#     cover_arprop and ar2_tw as before (96 h, one GPU each = the group's usual two), press_count_s18 / s19 with
#     walltime 48 h (user 01:11: the group's other two GPUs over the weekend)
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/resubmit_b5.sh
# Log: ~/mwam/logs/RESUBMIT_B5_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
mkdir -p $W/logs
LOG=$W/logs/RESUBMIT_B5_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[b5] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-70)"
say "home: $(df -h $HOME | tail -n 1)"
(lfs quota -h -u "$(id -un)" $HOME 2>/dev/null || quota -s 2>/dev/null) | tail -n 4
say "biggest under outputs/fullft:"; du -sh $R/outputs/fullft/*/ 2>/dev/null | sort -h | tail -n 6
say "SIF: $(ls -la $W/sif/ 2>/dev/null | tail -n +2 | tr '\n' ' ')"
for r in cover_arprop ar2_tw press_count_s18 press_count_s19; do
  L=$(ls -t $W/logs/RUN_${r}_*.txt 2>/dev/null | head -1)
  say "$r: last job log $(basename "${L:-none}"): $(grep -m1 -o 'host [^;]*' "$L" 2>/dev/null) | $(grep FAILED "$L" 2>/dev/null | tail -n 1 | cut -c1-120)"
done
for r in cover_arprop ar2_tw press_count_s18 press_count_s19; do
  [ -f $R/outputs/fullft/$r/SUMMARY.json ] && { say "$r: finished already, skipped"; continue; }
  if [ -s $R/outputs/fullft/$r/GAAS_JOB ] && qstat "$(cat $R/outputs/fullft/$r/GAAS_JOB)" > /dev/null 2>&1; then
    say "$r: job $(cat $R/outputs/fullft/$r/GAAS_JOB) still queued / running, skipped"; continue
  fi
  case $r in press_count_s1*) opt=(-l walltime=48:00:00 -v RUN=$r,WALL_H=48);; *) opt=(-v RUN=$r);; esac
  j=$(cd $W && qsub "${opt[@]}" $R/scripts/gaas/gaas_run.pbs) || { say "$r: qsub FAILED"; continue; }
  echo "$j" > $R/outputs/fullft/$r/GAAS_JOB
  say "$r: submitted job $j"
done
qstat -u "$(id -un)"
say "done"
