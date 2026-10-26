#!/usr/bin/env bash
# Extra closed loop in the guarded window (container GPUs 1 and 2, until Tue 2026-10-27 00:00 Beijing):
# more swap_blocks scenes for the headline comparison a2C_e3 memory on vs history masked (null).
#
#   1  wait until a100_final.sh has exited
#   2  in parallel: GPU1 plans N new expert-feasible swap scenes with seed 18, GPU2 with seed 19
#      (scenes that are already in the seed-17 bank are dropped)
#   3  each GPU runs a2C_e3 modes "on null" on its own new scenes (scene by scene: on, then null, so a stop at the
#      deadline still leaves complete pairs) -> outputs/memory_v2/closed_loop/a2_more
#   4  stage + grasp analysis of a2_more, and of a2_more together with the 10 seed-17 scenes -> EXTRA_*.txt
# Everything ends at the deadline.
#
#   nohup bash scripts/memory_v2/jobs/a100_extra.sh > /dev/null 2>&1 &     log: outputs/memory_v2/queue4/extra.log
set -u
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-16} MKL_NUM_THREADS=${MKL_NUM_THREADS:-16}
PY=/opt/mwam/bin/python
O=/workspace/FastWAM-memory2/outputs/memory_v2
Q=$O/queue4
CL=$O/closed_loop
OUT=$CL/a2_more
OLD=$CL/scenes_seed17_n10
SCRIPTS=/workspace/FastWAM-memory2/scripts/memory_v2
QUEUE_DEADLINE=${QUEUE_DEADLINE:-"2026-10-27 00:00 +0800"}
DEADLINE_TS=$(date -d "$QUEUE_DEADLINE" +%s)
N=${N:-8}
E3=$O/a2C/checkpoints/update_002010.pt
mkdir -p $Q $OUT
exec >> $Q/extra.log 2>&1
log() { echo "[extra] $(date '+%F %T') $*"; }
left() { echo $(( DEADLINE_TS - $(date +%s) )); }

plan_and_run() {                               # plan_and_run <gpu> <seed>
  local g=$1 seed=$2
  local bank=$CL/scenes_seed${seed}_n${N}_swap_blocks
  if ! $PY -c "import json,sys; sys.exit(0 if json.load(open('$bank/swap_blocks.json')).get('complete') else 1)" 2>/dev/null; then
    log "GPU $g: planning $N swap_blocks scenes, seed $seed -> $bank"
    timeout --kill-after=60 $(left) bash $SCRIPTS/jobs/closed_loop.sh plan $g $seed $N swap_blocks >> $Q/extra_plan_gpu$g.log 2>&1
  fi
  local seeds
  seeds=$($PY - $bank/swap_blocks.json $OLD/swap_blocks.json <<'PY'
import json, sys
new = json.load(open(sys.argv[1])).get("scenes", [])
old = {int(s["seed"]) for s in json.load(open(sys.argv[2])).get("scenes", [])}
print(" ".join(f"swap_blocks:{int(s['seed'])}" for s in new if int(s["seed"]) not in old))
PY
)
  if [ -z "$seeds" ]; then log "GPU $g: no new swap scenes from seed $seed (see $Q/extra_plan_gpu$g.log)"; return 1; fi
  log "GPU $g: new scenes $seeds"
  [ $(left) -gt 600 ] || { log "GPU $g: no time left to run"; return 1; }
  log "GPU $g: closed loop a2C_e3 [on null] on $(echo $seeds | wc -w) scenes (at most $(( $(left) / 3600 )) h)"
  timeout --kill-after=60 $(left) bash $SCRIPTS/jobs/closed_loop.sh eval $g $E3 a2C_e3 "on null" $bank $OUT \
    --tasks swap_blocks --seeds $seeds >> $Q/extra_run_gpu$g.log 2>&1
  log "GPU $g: closed loop ended (rc=$?)"
}

log "start; $(git -c safe.directory='*' log --oneline -1); deadline $QUEUE_DEADLINE; $N scenes per GPU"
while pgrep -f "a100_final.sh" >/dev/null; do [ $(left) -gt 0 ] || exit 0; sleep 120; done
log "a100_final.sh has exited"
plan_and_run 1 18 &
sleep 60
plan_and_run 2 19 &
wait
log "analysis"
$PY -m fastwam.memory_v2.online summary --output $OUT > $OUT/summary.txt 2>&1
$PY $SCRIPTS/closed_loop_stages.py $OUT --quiet > $OUT/EXTRA_stages.txt 2>&1
$PY $SCRIPTS/closed_loop_stages.py $OUT --grasps --quiet --expert $O/motion/motion_audit.json > $OUT/EXTRA_grasps.txt 2>&1
# pooled with the seed-17 scenes: copy (link) the a2 episodes of a2C_e3 on/null swap into a combined folder
POOL=$CL/a2_pool; rm -rf $POOL; mkdir -p $POOL
for src in $CL/a2 $OUT; do
  for mode in on null; do
    for d in $src/a2C_e3/$mode/swap_blocks/seed_*; do
      [ -f $d/result.json ] || continue
      mkdir -p $POOL/a2C_e3/$mode/swap_blocks; ln -sfn $d $POOL/a2C_e3/$mode/swap_blocks/$(basename $d)
    done
  done
done
$PY $SCRIPTS/closed_loop_stages.py $POOL --quiet > $OUT/EXTRA_pooled_stages.txt 2>&1
grep -A 12 "stage reach" $OUT/EXTRA_pooled_stages.txt
grep -A 6 "paired" $OUT/EXTRA_pooled_stages.txt
log "extra done"
