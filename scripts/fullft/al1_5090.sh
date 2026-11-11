#!/usr/bin/env bash
# mwam5090 container (plan v12 AL1, Opus checklist 2-3): is the PHYSICS the same on the 5090 as on the A100?
# No model: the simulator executes the A100's own executed targets (online.py --checkpoint replay:<pack>).
#   1 relay get the A100's pack (diag/al1_pack: X7 official episodes, put 31-50 + swap 1-20, packed on the A100)
#   2 tool acceptance (checklist 2): the 5090 replays 5 of its OWN eq5090b put episodes (scenes 31-35); every outcome
#     equal and every max object deviation <= 2 mm, else the tool is wrong -> stop here
#   3 the 5090 replays the A100 episodes (put 31-50, swap 1-20), execute 8, resumable (two passes)
#   4 compare -> AL1 reading (replay_pack.py: CONSISTENT / PARTIAL / INCONSISTENT; the floor = the A100 replaying its
#     own episodes, queue card AL1-a100-self, judged on the A100)
# GPU ${GPU:-0}, must be empty. Own log: outputs/fullft/align/AL1_5090_<time>.txt
#   docker exec -d -e GPU=0 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/al1_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
A=$R/outputs/fullft/align
P=$A/replay
mkdir -p $P
LOG=$A/AL1_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[al1] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[al1] $(date '+%F %T') ===== $*"; }
cd $R
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
PUTB=$O/closed_loop/scenes_seed42_n100_put_back_block
SWAPB=$O/closed_loop/scenes_seed42_n100_swap_blocks

step "1 the A100 pack"
[ -f $P/a100_x7.json.gz ] || /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py get --prefix diag/al1_pack --out $P \
  2>&1 | tail -1
ls -la $P/a100_x7.json.gz || { echo "no A100 pack on the relay yet: stopping"; exit 1; }

step "2 tool acceptance: the 5090 replays 5 of its own eq5090b put episodes (scenes 31-35)"
$PY scripts/fullft/replay_pack.py pack --name self_5090 --folders closed_loop/eq5090b --label x7_eq5090b \
  --task put_back_block --bank $PUTB --from-scene 31 --limit 5
for pass in 1 2; do
  $PY -m fastwam.memory_v2.online run --checkpoint replay:$P/self_5090.json.gz --label replay_self --scenes $PUTB \
    --tasks put_back_block --from-scene 31 --limit 5 --execute 8 --output $O/closed_loop/al1 >> $O/closed_loop/al1_run.log 2>&1
done
OUTC=$($PY scripts/fullft/replay_pack.py compare --pack $P/self_5090.json.gz --folder closed_loop/al1 --label replay_self \
  --name self_5090 --self-check 2>&1)
echo "$OUTC" | tail -n 10
echo "$OUTC" | grep -q "REPLAY READING self_5090: SELF-CHECK PASS" \
  || { echo "the 5090 does not reproduce its own episodes under replay (tool or 5090 physics not deterministic): stopping"; exit 1; }

step "3 the 5090 replays the A100's episodes"
for pass in 1 2; do
  $PY -m fastwam.memory_v2.online run --checkpoint replay:$P/a100_x7.json.gz --label replay_a100 --scenes $PUTB \
    --tasks put_back_block --from-scene 31 --limit 20 --execute 8 --output $O/closed_loop/al1 >> $O/closed_loop/al1_run.log 2>&1
  $PY -m fastwam.memory_v2.online run --checkpoint replay:$P/a100_x7.json.gz --label replay_a100 --scenes $SWAPB \
    --tasks swap_blocks --limit 20 --execute 8 --output $O/closed_loop/al1 >> $O/closed_loop/al1_run.log 2>&1
  echo "pass $pass: finished $(ls $O/closed_loop/al1/replay_a100/on/*/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
done

step "4 AL1 reading (the floor = the A100 self-replay, judged on the A100)"
$PY scripts/fullft/replay_pack.py compare --pack $P/a100_x7.json.gz --folder closed_loop/al1 --label replay_a100 --name al1_5090
