#!/usr/bin/env bash
# A-v2 queue on the 4-GPU A100 server: fine-tune the ActionDiT (memory-first stage 2) and evaluate it in closed loop
# without anybody at the keyboard. One lane per GPU; every lane writes its own log, skips finished steps, resumes
# interrupted training and stops between steps when $Q/STOP exists.
#
#   bash a100_queue_4.sh base   <gpu>   unit tests -> lr probe (2 x 100 real updates, no saving) -> pick the lr
#                                       -> A2C: ActionDiT + memory_v2 (from D) + pairs, EPOCHS epochs -> 401-window eval + PR
#   bash a100_queue_4.sh ablate <gpu>   waits for the lr choice and a free GPU -> A2C_nopairs (same, pairs off) -> eval + PR
#                                       AFTER=base: first wait until the base lane has exited (same GPU, run after A2C)
#   bash a100_queue_4.sh watch  <gpu>   waits for a free GPU -> closed loop of every epoch-end checkpoint as it appears
#                                       (A2C every epoch on+off, last epoch also null; nopairs last epoch) -> analysis
#   bash a100_queue_4.sh status         one screen: lanes, probe table, training progress / ETA, closed-loop results
#
# Logs (written by this script):  $Q/base.log  $Q/ablate.log  $Q/watch.log     with Q=outputs/memory_v2/queue4
# Stop: touch $Q/STOP (lanes stop before their next step); touch outputs/memory_v2/<run>/STOP.json (training saves + stops).
# Layout from 10-24 21:15 (only container GPUs 1 and 2 are ours, guarded with no release; GPU 0/3 belong to others):
#   GPU2: base (A2C)  ->  ablate with AFTER=base (A2C_nopairs on the same card, then its closed loop in mode off)
#   GPU1: watch (noabs; A2C after every epoch on+off, last epoch +null; A2C_nopairs last epoch mode on)
# Deadline: no lane starts a new step after QUEUE_DEADLINE (default Tue 2026-10-27 00:00 Beijing, when the GPU guard
# releases the cards); a step already running is not interrupted.
# Measured on the A100 (10-24): ActionDiT training 36 s/update at global batch 64 (no pairs), 670 updates/epoch
# => one epoch ~ 6.7 h (~8 h with pairs). Hence 3 epochs and no 1e-4 probe (A335: 1e-4 raised the loss 3.8x).
# Env: EPOCHS (3), PROBE_UPDATES (100), LRS ("1e-5 3e-5"), LR_MEMORY (2e-5), MB_TRY ("4 2 1"), NEED_MIB (30000),
# SIM_PY/CUROBO/EXT_DIR/VK_ICD
# (simulator overrides, as closed_loop.sh).
set -u
LANE=${1:?lane base|ablate|watch|status}
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-16} MKL_NUM_THREADS=${MKL_NUM_THREADS:-16}
PY=/opt/mwam/bin/python
CFG=configs/memory_v2/train_v2_A.yaml
O=/workspace/FastWAM-memory2/outputs/memory_v2
Q=$O/queue4
CL=$O/closed_loop
BANK=$CL/scenes_seed17_n10
CLOUT=$CL/a2
DCKPT=$O/v2_A_cf/checkpoints/update_001340.pt
PAIRS=$O/pairs/pairs_v1.json
SCRIPTS=/workspace/FastWAM-memory2/scripts/memory_v2
EPOCHS=${EPOCHS:-3}
PROBE_UPDATES=${PROBE_UPDATES:-100}
LRS=${LRS:-"1e-5 3e-5"}
LR_MEMORY=${LR_MEMORY:-2e-5}
MB_TRY=${MB_TRY:-"4 2 1"}
mkdir -p $Q $CLOUT
log() { echo "[$LANE] $(date '+%F %T') $*"; }
QUEUE_DEADLINE=${QUEUE_DEADLINE:-"2026-10-27 00:00 +0800"}
DEADLINE_TS=$(date -d "$QUEUE_DEADLINE" +%s)
stop_requested() {
  [ -f $Q/STOP ] && { log "STOP found: lane stops here"; return 0; }
  [ "$(date +%s)" -ge "$DEADLINE_TS" ] && { log "queue deadline $QUEUE_DEADLINE reached: lane stops here"; return 0; }
  return 1
}

gpu_free_mib() { nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits -i "$1" 2>/dev/null | tr -d ' '; }
NEED_MIB=${NEED_MIB:-30000}
wait_gpu() {                                   # usable = >= NEED_MIB free, twice, one minute apart (another user's
  log "waiting for container GPU $G to have >= $NEED_MIB MiB free"   # small job may share the card)
  while true; do
    stop_requested && exit 0
    f=$(gpu_free_mib $G); [ "${f:-0}" -ge $NEED_MIB ] || { sleep 60; continue; }
    sleep 60; f=$(gpu_free_mib $G); [ "${f:-0}" -ge $NEED_MIB ] && break
  done
  log "GPU $G has $f MiB free"
}
json_get() { $PY -c "import json,sys; v=json.load(open(sys.argv[1]))
for k in sys.argv[2].split('.'): v=v[k]
print(v)" "$1" "$2" 2>/dev/null; }
run_total() { json_get $O/$1/CONFIG.json total_updates; }
run_upe() { json_get $O/$1/CONFIG.json updates_per_epoch; }
last_ckpt() { printf "%s/%s/checkpoints/update_%06d.pt" $O $1 "$(run_total $1)"; }

# ------------------------------------------------------------------------------------------------ training helpers
train() {                                      # train <run> <--set ...>; returns 0 only with COMPLETE.json
  local run=$1; shift
  if [ -f $O/$run/COMPLETE.json ]; then log "$run already complete"; return 0; fi
  if [ -f $O/$run/GUARD.json ]; then log "$run was stopped by its guard: $(cat $O/$run/GUARD.json)"; return 1; fi
  local attempt
  for attempt in 1 2 3; do
    local resume=""; [ -f $O/$run/checkpoints/LATEST.json ] && resume="--resume"
    log "train $run (attempt $attempt) $resume; stdout -> $O/$run/stdout.log"
    mkdir -p $O/$run
    $PY -m fastwam.memory_v2.train_v2 train --config $CFG --allow-high-action-lr --set name=$run --set output=$O/$run \
      "$@" $resume >> $O/$run/stdout.log 2>&1
    local rc=$?
    [ -f $O/$run/COMPLETE.json ] && { log "$run complete"; return 0; }
    [ -f $O/$run/GUARD.json ] && { log "$run GUARD tripped: $(cat $O/$run/GUARD.json)"; return 1; }
    log "train $run exited rc=$rc without COMPLETE.json; last lines:"; tail -n 5 $O/$run/stdout.log
    stop_requested && return 1
    [ -f $O/$run/checkpoints/LATEST.json ] || return 1          # nothing to resume from: do not loop
    sleep 30
  done
  return 1
}
evaluate_run() {                               # 401-window eval + PR of the final checkpoint
  local run=$1; shift
  local ck; ck=$(last_ckpt $run)
  [ -f "$ck" ] || { log "no final checkpoint for $run ($ck)"; return 1; }
  if [ ! -f $O/$run/eval_full/$(basename ${ck%.pt}).json ]; then
    log "eval_full $run"; $PY -m fastwam.memory_v2.train_v2 evaluate --config $CFG "$@" --checkpoint $ck --windows 0 \
      --output $O/$run/eval_full >> $O/$run/stdout.log 2>&1
  fi
  if ! ls $O/pr/$run/pr_*_val.json >/dev/null 2>&1; then
    log "PR $run"; $PY -m fastwam.memory_v2.train_v2 pr --config $CFG "$@" --checkpoint $ck --pairs $PAIRS --limit 300 \
      --set 'eval.modes=["on","off","null"]' --output $O/pr/$run >> $O/$run/stdout.log 2>&1
  fi
  log "eval_full/PR $run done: $O/$run/eval_full  $O/pr/$run"
}
common_sets() {                                # the A2C recipe, lr from the probe, micro_batch from the probe
  local lr=$1 mb=$2
  echo "--set optim.lr_action=$lr --set optim.lr_memory=$LR_MEMORY --set init_memory=$DCKPT --set schedule.epochs=$EPOCHS" \
       "--set schedule.micro_batch=$mb --set schedule.eval_every=335 --set schedule.keep_last=2 --set schedule.save_every=200" \
       "--set guard.loss_factor=2.5 --set guard.start_update=120"
}
pair_sets() {
  local vis; vis=$($PY -c "import json,statistics;p=json.load(open('$PAIRS'))['train'];print(statistics.median(x['visual_distance'] for x in p))")
  echo "--set pairs.file=$PAIRS --set pairs.weight=0.5 --set pairs.per_update=8 --set pairs.max_visual_distance=$vis"
}
probe_done() { [ -f $1/train.log ] && [ "$(grep -c '"fm"' $1/train.log)" -ge $((PROBE_UPDATES * 8 / 10)) ]; }

# ------------------------------------------------------------------------------------------------ lanes
case "$LANE" in
base)
  G=${2:?container GPU index}; export CUDA_VISIBLE_DEVICES=$G
  exec >> $Q/base.log 2>&1
  log "start on GPU $G; $(git -c safe.directory='*' log --oneline -1)"
  log "unit tests (no pytest in /opt/mwam: scripts/memory_v2/minitest.py)"
  $PY $SCRIPTS/minitest.py test_train_v2 test_motion test_pairs test_history 2>&1 | tail -n 15
  stop_requested && exit 0
  wait_gpu
  # ---- lr probe: 100 real updates per lr from C+256 + D's memory, epochs=1 schedule (warm-up ends at ~34), no saving
  mkdir -p $O/a2probe
  for lr in $LRS; do
    d=$O/a2probe/lr$lr
    if probe_done $d; then log "probe lr=$lr exists"; continue; fi
    for mb in $MB_TRY; do
      stop_requested && exit 0
      rm -rf $d; mkdir -p $d
      log "probe lr=$lr micro_batch=$mb: $PROBE_UPDATES updates (dry-run, nothing saved); stdout -> $d/stdout.log"
      $PY -m fastwam.memory_v2.train_v2 train --config $CFG --allow-high-action-lr --dry-run $PROBE_UPDATES \
        --set name=a2probe_lr$lr --set output=$d --set optim.lr_action=$lr --set optim.lr_memory=$LR_MEMORY \
        --set init_memory=$DCKPT --set schedule.epochs=1 --set schedule.micro_batch=$mb \
        --set schedule.probe_every=0 --set schedule.eval_every=0 > $d/stdout.log 2>&1
      if grep -qi "out of memory" $d/stdout.log; then log "OOM at micro_batch $mb"; echo "OOM micro_batch=$mb" >> $d/train.log; continue; fi
      if probe_done $d; then echo $mb > $Q/MICRO_BATCH; break; fi
      log "probe lr=$lr micro_batch=$mb ended early; last lines:"; tail -n 5 $d/stdout.log; break
    done
  done
  log "probe table"
  $PY $SCRIPTS/pick_lr.py $O/a2probe --out $O/a2probe/CHOICE.json --min-updates $((PROBE_UPDATES * 8 / 10))
  LR=$(json_get $O/a2probe/CHOICE.json choice)
  if [ -z "$LR" ] || [ "$LR" = None ]; then log "PROBE FAILED: no lr qualifies (see $O/a2probe/CHOICE.json); lane stops"; exit 1; fi
  MB=$(cat $Q/MICRO_BATCH 2>/dev/null || echo 4)
  log "chosen lr_action=$LR micro_batch=$MB"
  stop_requested && exit 0
  # ---- A2C: ActionDiT + memory_v2 (init from D) + counterfactual pairs
  train a2C $(common_sets $LR $MB) $(pair_sets) || exit 1
  stop_requested && exit 0
  evaluate_run a2C
  log "lane done" ;;
ablate)
  G=${2:?container GPU index}; export CUDA_VISIBLE_DEVICES=$G
  exec >> $Q/ablate.log 2>&1
  log "start; waiting for the lr choice ($O/a2probe/CHOICE.json) and GPU $G"
  if [ -n "${AFTER:-}" ]; then
    log "waiting for the $AFTER lane to exit first (same GPU)"
    while pgrep -f "a100_queue_4.sh $AFTER( |\$)" >/dev/null; do stop_requested && exit 0; sleep 120; done
    if grep -q "lane done" $Q/$AFTER.log 2>/dev/null; then log "$AFTER lane finished"; else log "$AFTER lane exited WITHOUT 'lane done' (see $Q/$AFTER.log); continuing"; fi
  fi
  while true; do
    LR=$(json_get $O/a2probe/CHOICE.json choice 2>/dev/null)
    [ -n "$LR" ] && [ "$LR" != None ] && break
    stop_requested && exit 0
    sleep 120
  done
  MB=$(cat $Q/MICRO_BATCH 2>/dev/null || echo 4)
  log "lr_action=$LR micro_batch=$MB"
  wait_gpu
  stop_requested && exit 0
  train a2C_nopairs $(common_sets $LR $MB) || exit 1
  stop_requested && exit 0
  evaluate_run a2C_nopairs
  # its closed loop in mode off here (GPU1 runs mode on at the same time) so both finish before the deadline
  stop_requested && exit 0
  ck=$(last_ckpt a2C_nopairs); label=a2C_nopairs_e$EPOCHS
  if [ -f "$ck" ] && [ ! -f $CLOUT/DONE_${label}_off ]; then
    wait_gpu
    log "closed loop $label mode off on GPU $G"
    bash $SCRIPTS/jobs/closed_loop.sh eval $G $ck $label off $BANK $CLOUT
    touch $CLOUT/DONE_${label}_off
    $PY -m fastwam.memory_v2.online summary --output $CLOUT > $CLOUT/summary.txt 2>&1
    $PY $SCRIPTS/closed_loop_stages.py $CLOUT --quiet > $CLOUT/stages.txt 2>&1
    $PY $SCRIPTS/closed_loop_stages.py $CLOUT --grasps --quiet --expert $O/motion/motion_audit.json > $CLOUT/grasps.txt 2>&1
  fi
  log "lane done" ;;
watch)
  G=${2:?container GPU index}
  exec >> $Q/watch.log 2>&1
  log "start; closed loop of epoch-end checkpoints -> $CLOUT (scenes $BANK)"
  wait_gpu
  # ---- while the first epoch trains: (1) summarise the finished bank (C256 / D on / D null / B0 null), CPU only;
  # (2) the time-conditioning test: D without absolute time (v2_A_noabs) on the same scenes, mode on.
  if [ ! -f $CL/bank/bank_summary.txt ]; then
    log "bank summary + stage/grasp analysis -> $CL/bank/bank_summary.txt"
    { $PY -m fastwam.memory_v2.online summary --output $CL/bank; $PY $SCRIPTS/closed_loop_stages.py $CL/bank --quiet;
      $PY $SCRIPTS/closed_loop_stages.py $CL/bank --grasps --quiet --expert $O/motion/motion_audit.json; } > $CL/bank/bank_summary.txt 2>&1
  fi
  NOABS=$O/v2_A_noabs/checkpoints/update_001340.pt
  if [ -f $NOABS ] && [ ! -f $CLOUT/DONE_noabs ]; then
    stop_requested && exit 0
    log "closed loop v2_A_noabs/on (D without absolute-time features): does the right gripper still close in the air at the expert's time?"
    bash $SCRIPTS/jobs/closed_loop.sh eval $G $NOABS noabs on $BANK $CLOUT --set memory_v2.memory.absolute_time=false
    touch $CLOUT/DONE_noabs
    $PY $SCRIPTS/closed_loop_stages.py $CLOUT --grasps --quiet --expert $O/motion/motion_audit.json > $CLOUT/grasps.txt 2>&1
    tail -n 8 $CLOUT/grasps.txt
  fi
  while true; do
    stop_requested && exit 0
    if [ -f $O/a2probe/CHOICE.json ] && [ "$(json_get $O/a2probe/CHOICE.json choice)" = None ]; then
      log "the lr probe failed (base lane); nothing to evaluate, lane stops"; exit 1
    fi
    pending=0
    for spec in "a2C:$(seq -s " " 1 $EPOCHS)" "a2C_nopairs:$EPOCHS"; do
      run=${spec%%:*}
      upe=$(run_upe $run); [ -n "$upe" ] || { pending=1; continue; }
      for e in ${spec#*:}; do
        [ "$e" -le "$EPOCHS" ] || continue
        ck=$(printf "%s/%s/checkpoints/update_%06d.pt" $O $run $((e * upe)))
        label=${run}_e$e
        marker=$CLOUT/DONE_$label
        [ -f $marker ] && continue
        if [ ! -f "$ck" ]; then
          [ -f $O/$run/COMPLETE.json ] || [ -f $O/$run/GUARD.json ] || pending=1
          continue
        fi
        modes="on off"; [ "$e" = "$EPOCHS" ] && modes="on off null"
        [ "$run" = a2C_nopairs ] && modes="on"          # mode off of A2C_nopairs runs on the ablate lane's GPU
        log "closed loop $label modes [$modes]"
        bash $SCRIPTS/jobs/closed_loop.sh eval $G $ck $label "$modes" $BANK $CLOUT
        touch $marker
        log "analysis after $label"
        $PY -m fastwam.memory_v2.online summary --output $CLOUT > $CLOUT/summary.txt 2>&1
        $PY $SCRIPTS/closed_loop_stages.py $CLOUT --quiet > $CLOUT/stages.txt 2>&1
        $PY $SCRIPTS/closed_loop_stages.py $CLOUT --grasps --quiet --expert $O/motion/motion_audit.json > $CLOUT/grasps.txt 2>&1
        tail -n 30 $CLOUT/stages.txt
        stop_requested && exit 0
      done
    done
    if [ $pending = 0 ]; then log "every epoch checkpoint evaluated; lane done"; exit 0; fi
    sleep 300
  done ;;
status)
  echo "== queue4 $(date '+%F %T')   (stop all: touch $Q/STOP)"
  for lane in base ablate watch; do
    [ -f $Q/$lane.log ] && { echo "-- $lane.log (last 3)"; tail -n 3 $Q/$lane.log; }
  done
  if [ -f $O/a2probe/CHOICE.json ]; then echo "-- lr probe (CHOICE.json)"; $PY -c "
import json; c = json.load(open('$O/a2probe/CHOICE.json'))
for r in c['probes']: print(f\"   lr {r['lr']:.0e}: {r['updates']} updates, final/start {r.get('final_ratio', float('nan')):.2f}, peak/start {r.get('peak_ratio', float('nan')):.2f}  {r['status']} {r.get('reason', '')}\")
print('   choice:', c['choice'])"
  else for d in $O/a2probe/lr*; do [ -f $d/train.log ] && echo "-- probe $(basename $d): $(grep -c '"fm"' $d/train.log) updates; last: $(grep '"fm"' $d/train.log | tail -n 1 | cut -c1-160)"; done; fi
  for run in a2C a2C_nopairs; do
    [ -f $O/$run/metrics.jsonl ] || continue
    $PY - $O/$run <<'PY'
import json, sys, time
from pathlib import Path
d = Path(sys.argv[1]); cfg = json.loads((d / "CONFIG.json").read_text())
rows = [json.loads(l) for l in (d / "metrics.jsonl").read_text().splitlines() if l.strip()]
r = rows[-1]; total = cfg["total_updates"]; sec = sum(x["seconds"] for x in rows[-20:]) / len(rows[-20:])
eta = (total - r["update"]) * sec
state = "COMPLETE" if (d / "COMPLETE.json").exists() else "GUARD " + (d / "GUARD.json").read_text().strip() if (d / "GUARD.json").exists() else "running"
print(f"-- {d.name}: update {r['update']}/{total} (epoch {r['epoch']}) fm {r['fm']:.4f} pair {r.get('pair_loss', float('nan')):.4f} "
      f"lr_action {r['lr'].get('action', 0):.1e} {sec:.0f}s/update ETA {eta/3600:.1f} h  peak {r.get('peak_gpu_bytes', 0)/2**30:.1f} GB  [{state}]")
evals = sorted((d / "eval").glob("update_*.json"))
if evals:
    e = json.loads(evals[-1].read_text())["overall"]
    print(f"   last eval {evals[-1].stem}: arm RMSE on {e.get('on/arm_rmse_rad', float('nan')):.4f} off {e.get('off/arm_rmse_rad', float('nan')):.4f} null {e.get('null/arm_rmse_rad', float('nan')):.4f}")
PY
  done
  ls $CLOUT/DONE_* >/dev/null 2>&1 && { echo "-- closed loop done: $(ls $CLOUT | grep DONE_ | tr '\n' ' ')"; [ -f $CLOUT/stages.txt ] && grep -A 40 "stage reach" $CLOUT/stages.txt | head -n 24; }
  ;;
*) echo "unknown lane $LANE"; exit 2 ;;
esac
