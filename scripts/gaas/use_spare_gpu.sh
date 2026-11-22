#!/bin/bash
# NTU GaaS login node, 11-22 18:30 (Opus; user 18:23: "check the new H200's spare GPU; if one is free, put our runs on it;
# do not waste compute"). Plain run = read-only check. With --yes, and only when the check finds a spare GPU, chain D
# goes back on (it was paused at 14:34 for the group):
#   ar2_tw (B2, the long-picture version) resumes now from its resume.pt (update 5475 of 20077, ~35 h left), then
#   press_none (job 116648, held at 14:34; its dependency is moved onto the new ar2_tw job, then it is released).
# Spare GPU = OUR jobs hold fewer than 4 GPUs in running or queued jobs (user 11-22 23:53: we pay for 4 H200s and use at
# most 4; other users' jobs in the project do not count; they are listed for information); held jobs wait on a
# dependency and hold no GPU. Home disk >= 160 GB free is noted (gaas_run.pbs waits for that anyway).
# Nothing of another user is touched; nothing is deleted.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && bash scripts/gaas/use_spare_gpu.sh [--yes]
# Log: ~/mwam/logs/SPARE_GPU_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
F=$R/outputs/fullft
PROJ=$(awk '/^#PBS -P /{print $3}' $R/scripts/gaas/gaas_run.pbs)
HELD=116648                    # press_none, chain D, held by the user at 14:34
LIMIT=4                        # user 11-22 13:07: the new H200 allows at most 4 GPUs
YES=0; [ "${1:-}" = --yes ] && YES=1
mkdir -p $W/logs
LOG=$W/logs/SPARE_GPU_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[spare] $(date '+%F %T') $*"; }
cd $R
say "code $(git log --oneline -1 | cut -c1-60); me $(id -un); home $(df -BG $HOME | tail -n 1 | awk '{print $4}') free"

echo "== our jobs"
qstat -u "$(id -un)" -w 2>/dev/null | tail -n +4

echo "== every job of the project (R running, Q queued, H held), any user"
used=0
for st in R Q H; do
  for j in $(qselect -P "$PROJ" -s $st 2>/dev/null); do
    info=$(qstat -f "$j" 2>/dev/null)
    own=$(echo "$info" | awk -F' = ' '/Job_Owner/{split($2, a, "@"); print a[1]}')
    name=$(echo "$info" | awk -F' = ' '/Job_Name/{print $2}')
    g=$(echo "$info" | awk -F' = ' '/Resource_List.ngpus/{print $2}')
    printf '  %-14s %s  %-10s %-12s gpus %s\n' "${j%%.*}" "$st" "$own" "$name" "${g:-?}"
    [ "$st" != H ] && [ "$own" = "$(id -un)" ] && used=$(( used + ${g:-1} ))   # user 23:53: only ours count
  done
done
echo "== the queue gpu_as"
qstat -Qf gpu_as 2>/dev/null | grep -E "state_count|resources_assigned.ngpus|max_run|enabled|started" | sed 's/^ */  /'

echo "== our runs"
for r in d2_press d1_w obs_none obs_zoom d1_wn cover_arprop ar2_prop_novid ar2_tw press_none press_count_s18 press_count_s19; do
  d=$F/$r; [ -d $d ] || continue
  u=$(grep -a -o 'u [0-9]*/[0-9]*' $F/QUEUE_$r.log 2>/dev/null | tail -n 1)
  printf '  %-16s job %-8s %-9s %-10s resume.pt %s\n' "$r" "$(cut -d. -f1 $d/GAAS_JOB 2>/dev/null)" \
    "$([ -f $d/SUMMARY.json ] && echo finished || echo -)" "${u:-no log}" "$([ -f $d/resume.pt ] && echo yes || echo no)"
done

free=$(df -BG $HOME | tail -n 1 | awk '{gsub("G", "", $4); print $4}')
spare=$(( LIMIT - used ))
say "our running / queued jobs hold $used GPU(s) (limit $LIMIT for us): spare $spare; home $free GB free"
if [ "$spare" -lt 1 ]; then say "NO SPARE GPU: nothing submitted"; exit 0; fi
[ "$free" -lt 160 ] && say "note: < 160 GB free; the job will wait for room before it trains (gaas_run.pbs)"
if [ $YES != 1 ]; then say "SPARE GPU: run again with --yes to resume chain D (ar2_tw now, press_none after it)"; exit 0; fi

# ---- --yes: chain D back on
[ -f $F/ar2_tw/SUMMARY.json ] && { say "ar2_tw finished already: nothing to resume"; exit 1; }
[ -f $F/ar2_tw/resume.pt ] || { say "ar2_tw has no resume.pt: stop (it would start from update 0)"; exit 1; }
if [ -s $F/ar2_tw/GAAS_JOB ] && qstat "$(cat $F/ar2_tw/GAAS_JOB)" > /dev/null 2>&1; then
  say "ar2_tw already has a live job $(cat $F/ar2_tw/GAAS_JOB): nothing submitted"; exit 1
fi
J=$(cd $W && qsub -l walltime=60:00:00 -v RUN=ar2_tw,WALL_H=60,NO_RESUBMIT=1,AUTO_CLEAN=1 $R/scripts/gaas/gaas_run.pbs) \
  || { say "qsub FAILED"; exit 1; }
echo "$J" > $F/ar2_tw/GAAS_JOB
say "ar2_tw -> job $J (resumes from resume.pt; walltime 60 h)"
hs=$(qstat -f $HELD 2>/dev/null | awk -F' = ' '/job_state/{print $2}')
ho=$(qstat -f $HELD 2>/dev/null | awk -F' = ' '/Job_Owner/{split($2, a, "@"); print a[1]}')
if [ "$hs" = H ] && [ "$ho" = "$(id -un)" ]; then
  qalter -W depend=afterany:$J $HELD && say "press_none ($HELD) now after $J" || say "qalter FAILED: press_none stays held"
  qrls -h u $HELD 2>/dev/null && say "press_none ($HELD) released (starts when $J ends)" || say "qrls: no user hold left on $HELD"
else
  say "press_none job $HELD is not our held job (state '${hs:-gone}'): left as it is"
fi
qstat -u "$(id -un)" -w 2>/dev/null | tail -n +4
say "done"
