#!/usr/bin/env bash
# GPU B: Ours + counterfactual history training on matched-present train pairs
# (query current frame + donor history -> donor future), then PR of the result.
# Visual filter: keep the train pairs whose current frames are closest (below the median distance).
set -u
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
PY=/opt/mwam/bin/python
CFG=configs/memory_v2/train_v2_A.yaml
PAIRS=/workspace/FastWAM-memory2/outputs/memory_v2/pairs/pairs_v1.json
O=/workspace/FastWAM-memory2/outputs/memory_v2
W=${PAIR_WEIGHT:-0.5}
VIS=$($PY -c "import json,statistics;p=json.load(open('$PAIRS'))['train'];print(statistics.median(x['visual_distance'] for x in p))")
echo "[gpu-b] $(date) pairs weight=$W max_visual_distance=$VIS (train median)"
$PY -m fastwam.memory_v2.train_v2 train --config $CFG \
  --set name=v2_A_cf --set output=$O/v2_A_cf \
  --set pairs.file=$PAIRS --set pairs.weight=$W --set pairs.per_update=16 --set pairs.max_visual_distance=$VIS
echo "[gpu-b] $(date) PR v2_A_cf"
$PY -m fastwam.memory_v2.train_v2 pr --config $CFG --checkpoint $O/v2_A_cf/checkpoints/update_001340.pt \
  --pairs $PAIRS --limit ${PR_PAIRS:-300} --output $O/pr/v2_A_cf
echo "[gpu-b] $(date) full eval v2_A_cf"
$PY -m fastwam.memory_v2.train_v2 evaluate --config $CFG \
  --checkpoint $O/v2_A_cf/checkpoints/update_001340.pt --windows 0 --output $O/v2_A_cf/eval_full
echo "[gpu-b] $(date) all done"
