#!/usr/bin/env bash
# Dry run (3 updates, nothing saved, no eval) of the press_button stage-1 and stage-2 recipes for one history rule:
# peak GPU memory (peak_gpu_gb) and seconds per update, before the real runs of that arm start. Exit 0 only if both
# stages run. Stage 1 = the v2_A_cf recipe (memory only, pairs 16 / update); stage 2 = the X7 recipe (lr_action 1e-5,
# lr_memory 2e-5, pairs 8 / update) without init_memory (memory zero-initialised: same memory use, nothing to load).
# The pair filter is the median visual distance of the press train pairs, as for the two-task runs.
#
#   bash scripts/memory_v2/press/dry_run.sh <tag> <micro_batch stage 1> <micro_batch stage 2> [--set key=value ...]
#   e.g. bash scripts/memory_v2/press/dry_run.sh B 4 2 --set memory_v2.history.landmark_stride=8
set -u
TAG=${1:?tag}; MB1=${2:?micro batch stage 1}; MB2=${3:?micro batch stage 2}; shift 3
R=/workspace/FastWAM-memory2
O=${MEMV2_OUT:-$R/outputs/memory_v2}
PY=${MEMV2_PY:-/opt/mwam/bin/python}
P=$O/pairs/pairs_press_v1.json
cd "$R" || exit 1
VIS=$($PY -c "import json, statistics, sys; p = json.load(open(sys.argv[1]))['train']; print(statistics.median(x['visual_distance'] for x in p))" "$P") || { echo "no pair filter from $P"; exit 1; }
echo "pairs $P: median visual distance $VIS"
run() {
  local stage=$1 mb=$2; shift 2
  echo "== dry run $TAG $stage: micro_batch $mb $*"
  PYTHONPATH=src $PY -m fastwam.memory_v2.train_v2 train --config configs/memory_v2/train_v2_press.yaml \
    --allow-high-action-lr --dry-run 3 --set "name=dry_press_${TAG}_$stage" --set "output=$O/dry/press_${TAG}_$stage" \
    --set "schedule.micro_batch=$mb" --set "pairs.file=$P" --set pairs.weight=0.5 --set "pairs.max_visual_distance=$VIS" "$@"
}
run stage1 "$MB1" --set pairs.per_update=16 "$@" || { echo "DRY RUN FAILED ($TAG stage 1)"; exit 1; }
run stage2 "$MB2" --set optim.lr_action=1e-5 --set optim.lr_memory=2e-5 --set pairs.per_update=8 "$@" \
  || { echo "DRY RUN FAILED ($TAG stage 2)"; exit 1; }
echo "DRY RUN OK ($TAG): see peak_gpu_gb and seconds in the [train] lines above"
