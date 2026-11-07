#!/usr/bin/env bash
# A100 container (11-08): the A100 side of the 5090 online diagnosis. On the 5090, frame 0 of official put_back
# seed 4300030 gives a first chunk = the A100's (11-03 official episode) delayed by 2 targets, whatever the text
# encoding (CPU / GPU / dense cache: all within 0.0013 rad of each other) and with the same initial robot state and
# object poses; what is left is the image the simulator renders (or the 5090's policy numerics on it).
#   1 GPU ${GPU:-0} must be EMPTY (< 2000 MiB used): this never shares a GPU with a running task
#   2 X7, 10 steps, execute 8, 8 targets, frame 0's request dumped -> closed_loop/check_a100 (label x7_first_a100);
#     its first 8 targets vs the official 11-03 episode (is the A100 itself reproducible across days?)
#   3 first_decision.py on that request (T5 = the A100's GPU-visit path, and the dense cache text)
#   4 relay put -> hhyfred/memwam-diag-v1 diag/a100_4300030 (request, executed targets, report) for the 5090
# Own log: /workspace/FastWAM-memory2/outputs/memory_v2/report/FIRSTRENDER_A100_<time>.txt
#   docker exec -e GPU=0 6e4b37a15066 bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/firstrender_a100.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/FIRSTRENDER_A100_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[firstrender] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[firstrender] $(date '+%F %T') ===== $*"; }
cd "$R"
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping (choose an empty GPU: GPU=<n>)"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU
PY=/opt/mwam/bin/python
SEED=4300030
EP=$O/closed_loop/check_a100/x7_first_a100/on/put_back_block/seed_$SEED

step "2 frame-0 request of put_back seed $SEED on the A100"
if [ ! -f "$EP/request_000000.pkl" ]; then
  $PY -m fastwam.memory_v2.online run --checkpoint $O/a2C_6ep/checkpoints/update_004020.pt --label x7_first_a100 \
    --scenes $O/closed_loop/scenes_seed42_n100_put_back_block --tasks put_back_block --seeds put_back_block:$SEED \
    --execute 8 --max-targets 8 --dump-first --output $O/closed_loop/check_a100 > $O/closed_loop/check_a100_run.log 2>&1
  echo "run exit code $?"
fi
ls -la "$EP/request_000000.pkl" || { tail -n 20 $O/closed_loop/check_a100_run.log; exit 1; }
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/check_a100 --label x7_first_a100 --first put_back_block:$SEED --out /dev/null \
  | sed -n '/== first targets/,$p'
echo "--- official 11-03 episode (reference):"
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/official/put_x7_s0 --label a2C6_e6 --first put_back_block:$SEED --out /dev/null \
  | sed -n '/(on)/,$p'

step "3 replay on the A100 (T5 visit path / dense cache text)"
$PY scripts/memory_v2/migrate/first_decision.py --request "$EP/request_000000.pkl" --variants cpu cache \
  --ref scripts/memory_v2/migrate/ref_a100_put_4300030.json --replayed "$EP/executed_actions.jsonl"
REP=$(ls -t $O/report/FIRST_DECISION_*.md | head -1)

step "4 relay to the 5090"
cp "$REP" $O/closed_loop/check_a100/FIRST_DECISION_A100.md
/opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py put "$EP/request_000000.pkl" "$EP/executed_actions.jsonl" \
  $O/closed_loop/check_a100/FIRST_DECISION_A100.md --prefix diag/a100_4300030
