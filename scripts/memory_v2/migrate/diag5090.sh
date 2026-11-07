#!/usr/bin/env bash
# mwam5090 container (11-07 23:30): why did S4 (X7, 4 Euler steps) lift the block in only 21/50 put_back scenes on the
# 5090 when X7 at 10 steps lifts it in 98/100 on the A100 / H200 and offline 4 steps equal 10 steps? Read-only for the
# queue (no state, verdict or autopsy is written); run it with the pool paused (GPU 0 must be free).
#   1 loop_peek of S2 (paused, partial) and S4: stage tables, per-episode means, error kinds
#   2 N1-prof-5090: the failed profile cases' errors from its job log
#   3 online_check5090.py: online T5 (CPU = the 5090 path, and GPU) and VAE latents vs the dense cache
#   4 first decision on one official put_back scene that X7 ran on the A100 (official/put_x7_s0, smallest seed with a
#     result): X7, 10 steps, execute 8, 16 targets, camera PNGs saved; its first 8 executed targets are printed for
#     comparison with the A100's episode of the same scene (same CPU-seeded noise -> same first chunk up to numerics)
# Own log: /workspace/FastWAM-memory2/outputs/memory_v2/report/DIAG5090_<time>.txt; PNGs: report/diag5090_png/
#   bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/diag5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/DIAG5090_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[diag5090] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[diag5090] $(date '+%F %T') ===== $*"; }
cd "$R"
export PYTHONPATH=$R/src
PY=/opt/mwam/bin/python
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader

step "1 S2 (paused) and S4: what the 5090 episodes did"
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/s2_steps2 --label x7_steps2_exec8 --out /dev/null
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/s4_steps4 --label x7_steps4_exec8 --out /dev/null

step "2 N1-prof-5090: errors of the failed profile cases (job log)"
J=$O/queue5/tasks/N1-prof-5090.log
if [ -f "$J" ]; then
  grep -n -E '^\[profile\]|Error|error:|Traceback|OutOfMemory|out of memory' "$J" | tail -n 60
  echo "--- last traceback:"
  awk '/Traceback/{buf=""} {buf=buf $0 "\n"} END{printf "%s", buf}' "$J" | tail -n 40
else
  echo "no job log at $J"
fi

step "3 online encoders vs the dense cache (GPU 0)"
CUDA_VISIBLE_DEVICES=0 $PY scripts/memory_v2/migrate/online_check5090.py

step "4 first decision of one official put_back scene (GPU 0)"
SEED=$(ls -d $O/closed_loop/official/put_x7_s0/a2C6_e6/on/put_back_block/seed_*/result.json 2>/dev/null \
       | sed -n 's#.*/seed_\([0-9]*\)/result.json#\1#p' | sort -n | head -1)
echo "SEED=$SEED (smallest put_back seed with an A100 result in official/put_x7_s0, label a2C6_e6, mode on)"
if [ -n "$SEED" ]; then
  CUDA_VISIBLE_DEVICES=0 $PY -m fastwam.memory_v2.online run --checkpoint $O/a2C_6ep/checkpoints/update_004020.pt \
    --label x7_first5090 --scenes $O/closed_loop/scenes_seed42_n100_put_back_block --tasks put_back_block \
    --seeds put_back_block:$SEED --execute 8 --max-targets 16 --record-frames --output $O/closed_loop/check5090 \
    > $O/closed_loop/check5090_run.log 2>&1
  echo "run exit code $?; last lines of $O/closed_loop/check5090_run.log:"
  grep -E 'T5|instruction encoded|done |ERROR' $O/closed_loop/check5090_run.log | tail -n 6
  $PY scripts/memory_v2/loop_peek.py --folder closed_loop/check5090 --label x7_first5090 --first put_back_block:$SEED --out /dev/null \
    | sed -n '/== first targets/,$p'
  mkdir -p $O/report/diag5090_png
  find $O/closed_loop/check5090/x7_first5090 -name '*.png' | sort | head -n 3 | while read -r f; do
    cp "$f" "$O/report/diag5090_png/$(echo "${f#$O/closed_loop/check5090/x7_first5090/}" | tr '/' '_')"
  done
  echo "PNGs (first 3 by name):"; ls -la $O/report/diag5090_png
fi
