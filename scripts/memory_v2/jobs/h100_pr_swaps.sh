#!/usr/bin/env bash
# H100: PR decomposition on the 300 val pairs - which part of the partner's history drives the switch?
#   content : partner's history content, re-timed to the own clock (same ages)
#   clock   : own history content, re-timed to the partner's clock (same ages)
# (swap=all is the existing PR.) start model: off only; Ours: on/off/null; the others: on only.
set -u
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
PY=/opt/mwam/bin/python
CFG=configs/memory_v2/train_v2_A.yaml
PAIRS=/workspace/FastWAM-memory2/outputs/memory_v2/pairs/pairs_v1.json
O=/workspace/FastWAM-memory2/outputs/memory_v2
for swap in content clock; do
  echo "[swaps] $(date) start model swap=$swap"
  $PY -m fastwam.memory_v2.train_v2 pr --config $CFG --checkpoint init --pairs $PAIRS --limit 300 \
    --swap $swap --set 'eval.modes=["off"]' --output $O/pr/start
  for run in v2_A_memory_only v2_A_cf v2_A_bfull v2_A_noabs v2_A_b0; do
    modes='["on"]'
    [ "$run" = v2_A_memory_only ] && modes='["on", "off", "null"]'
    extra=""
    [ "$run" = v2_A_noabs ] && extra="--set memory_v2.memory.absolute_time=false"
    echo "[swaps] $(date) $run swap=$swap modes=$modes"
    $PY -m fastwam.memory_v2.train_v2 pr --config $CFG $extra --checkpoint $O/$run/checkpoints/update_001340.pt \
      --pairs $PAIRS --limit 300 --swap $swap --set "eval.modes=$modes" --output $O/pr/$run
  done
done
$PY /workspace/FastWAM-memory2/scripts/memory_v2/show_results.py > $O/RESULTS_pr_swaps.txt 2>&1
echo "[swaps] $(date) all done -> $O/RESULTS_pr_swaps.txt"
