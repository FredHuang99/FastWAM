#!/usr/bin/env bash
# Final phase on the two guarded GPUs (container 1 and 2) until the deadline (Tue 2026-10-27 00:00 Beijing).
# Replaces the watch and ablate lanes of a100_queue_4.sh (their markers RETIRED_* are written here); the base lane
# (A2C training -> eval_full + PR on GPU2) keeps running untouched.
#
#   A  wait until the base lane has exited and A2C's last checkpoint exists (a2C_e2 keeps running on GPU1 meanwhile)
#   B  stop a2C_e2 (finished episodes are kept; it is resumed in D)
#   C  a2C_e3 modes on / off / null, the 20 scenes split over GPU1 (shard 1/2) and GPU2 (shard 0/2)   ~9 h
#   D  leftover time: GPU1 resumes a2C_e2 (on, off); GPU2 re-runs a2C_e1 (on, off; its episodes failed with CUDA OOM
#      on 10-24 night because a manual run shared GPU1) - finished episodes are skipped, failed ones redone
# Every closed loop is killed at the deadline. Analysis after C and D -> $CLOUT/{summary,stages,grasps}.txt.
#
#   nohup bash scripts/memory_v2/jobs/a100_final.sh > /dev/null 2>&1 &      log: outputs/memory_v2/queue4/final.log
#   stop: touch outputs/memory_v2/queue4/STOP   (before the next phase; running closed loops continue)
set -u
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-16} MKL_NUM_THREADS=${MKL_NUM_THREADS:-16}
PY=/opt/mwam/bin/python
O=/workspace/FastWAM-memory2/outputs/memory_v2
Q=$O/queue4
CL=$O/closed_loop
CLOUT=$CL/a2
BANK=$CL/scenes_seed17_n10
SCRIPTS=/workspace/FastWAM-memory2/scripts/memory_v2
QUEUE_DEADLINE=${QUEUE_DEADLINE:-"2026-10-27 00:00 +0800"}
DEADLINE_TS=$(date -d "$QUEUE_DEADLINE" +%s)
NEED_MIB=${NEED_MIB:-30000}
CK=$O/a2C/checkpoints
E1=$CK/update_000670.pt; E2=$CK/update_001340.pt; E3=$CK/update_002010.pt
mkdir -p $Q $CLOUT
exec >> $Q/final.log 2>&1
log() { echo "[final] $(date '+%F %T') $*"; }
stop_requested() {
  [ -f $Q/STOP ] && { log "STOP found: stops here"; return 0; }
  [ "$(date +%s)" -ge "$DEADLINE_TS" ] && { log "deadline $QUEUE_DEADLINE reached: stops here"; return 0; }
  return 1
}
free_mib() { nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i "$1" 2>/dev/null | tr -d ' '; }
wait_free() {                                  # >= NEED_MIB free, twice, one minute apart
  local g=$1 f
  while true; do
    stop_requested && exit 0
    f=$(free_mib $g); [ "${f:-0}" -ge $NEED_MIB ] || { sleep 60; continue; }
    sleep 60; f=$(free_mib $g); [ "${f:-0}" -ge $NEED_MIB ] && break
  done
  log "GPU $g has $f MiB free"
}
kill_tree() { local p=$1 s=$2 c; for c in $(pgrep -P $p); do kill_tree $c $s; done; kill -$s $p 2>/dev/null; }
stop_eval() {                                  # stop every running closed loop of <label> (driver, policy, simulators)
  local label=$1 p sig
  for sig in TERM KILL; do
    for p in $(pgrep -f "closed_loop.sh eval [0-9] [^ ]+ $label "); do kill_tree $p $sig; done
    for p in $(pgrep -f "fastwam.memory_v2.online run .*--label $label "); do kill_tree $p $sig; done
    sleep 20
  done
  log "stopped closed loop $label (finished episodes are kept)"
}
run_eval() {                                   # run_eval <gpu> <ckpt> <label> <modes> [extra args]; ends at the deadline
  local g=$1 ck=$2 label=$3 modes=$4; shift 4
  local left=$(( DEADLINE_TS - $(date +%s) ))
  [ $left -gt 120 ] || { log "no time left for $label on GPU $g"; return 1; }
  log "closed loop $label [$modes] on GPU $g $* (at most $((left / 3600)) h)"
  timeout --kill-after=60 $left bash $SCRIPTS/jobs/closed_loop.sh eval $g $ck $label "$modes" $BANK $CLOUT "$@" \
    >> $Q/final_${label}_gpu$g.log 2>&1
  local rc=$?
  [ $rc = 124 ] && { log "$label on GPU $g hit the deadline"; stop_eval $label; }
  log "closed loop $label on GPU $g ended (rc=$rc)"
}
analyse() {
  $PY -m fastwam.memory_v2.online summary --output $CLOUT > $CLOUT/summary.txt 2>&1
  $PY $SCRIPTS/closed_loop_stages.py $CLOUT --quiet > $CLOUT/stages.txt 2>&1
  $PY $SCRIPTS/closed_loop_stages.py $CLOUT --grasps --quiet --expert $O/motion/motion_audit.json > $CLOUT/grasps.txt 2>&1
  log "analysis -> $CLOUT/stages.txt"
  grep -A 40 "stage reach" $CLOUT/stages.txt | head -n 40
}

log "start; $(git -c safe.directory='*' log --oneline -1); deadline $QUEUE_DEADLINE"
touch $Q/RETIRED_watch $Q/RETIRED_ablate
# ------------------------------------------------------------------ A
log "A: waiting for the base lane to exit (A2C training -> eval_full + PR) and $E3; a2C_e2 keeps running on GPU1"
while pgrep -f "a100_queue_4.sh base( |$)" >/dev/null; do stop_requested && exit 0; sleep 300; done
if [ -f $E3 ]; then
  # ---------------------------------------------------------------- B
  stop_requested && exit 0
  stop_eval a2C_e2
  wait_free 1; wait_free 2
  # ---------------------------------------------------------------- C
  run_eval 1 $E3 a2C_e3 "on off null" --shard 1/2 &
  sleep 90                                     # stagger the two model loads
  run_eval 2 $E3 a2C_e3 "on off null" --shard 0/2 &
  wait
  analyse
  cp $CLOUT/stages.txt $CLOUT/FINAL_e3_stages.txt; cp $CLOUT/grasps.txt $CLOUT/FINAL_e3_grasps.txt
else
  log "base lane exited without $E3 (see $Q/base.log): no e3; going to D"
fi
# ------------------------------------------------------------------ D
stop_requested && exit 0
wait_free 1; wait_free 2
run_eval 1 $E2 a2C_e2 "on off" &
sleep 90
run_eval 2 $E1 a2C_e1 "on off" &
wait
analyse
log "final done"
