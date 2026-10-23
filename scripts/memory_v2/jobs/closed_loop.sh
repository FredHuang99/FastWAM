#!/usr/bin/env bash
# memory_v2 closed loop on the A100 (policy: /opt/mwam; simulator: the dense config's, or $SIM_PY).
#   bash closed_loop.sh preflight                    read-only inventory + CPU unit tests (no GPU memory)
#   bash closed_loop.sh parity  <gpu> [run]          online path vs offline cache, 8 val windows (default run v2_A_cf)
#   bash closed_loop.sh smoke   <gpu> [run]          2 frozen scenes x (off, on), first 96 targets, dependence logged
#   bash closed_loop.sh frozen  <gpu> [run]          2 frozen scenes x (off, on), official 500/1000 caps
#   bash closed_loop.sh plan    <gpu> [seed] [n]     expert-feasible scene bank (default seed 17, 10 per task)
#   bash closed_loop.sh bank    <gpu> <run|init> "<modes>" <scenes> [k/n]
#   bash closed_loop.sh summary [output folder]
# <gpu> = container GPU index. Simulator overrides (from the preflight):
#   SIM_PY=/opt/<env>/bin/python  CUROBO=fused_graph_v1|builtin_torch_v1|upstream  EXT_DIR=outputs/<dir>/torch_extensions...
set -u
STAGE=${1:?stage: preflight|parity|smoke|frozen|plan|bank|summary}
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8} MKL_NUM_THREADS=${MKL_NUM_THREADS:-8}
PY=/opt/mwam/bin/python
O=/workspace/FastWAM-memory2/outputs/memory_v2
CL=$O/closed_loop
mkdir -p $CL/logs
SIM=()
[ -n "${SIM_PY:-}" ] && SIM+=(--simulator-python "$SIM_PY")
[ -n "${CUROBO:-}" ] && SIM+=(--curobo-backend "$CUROBO")
[ -n "${EXT_DIR:-}" ] && SIM+=(--extensions-dir "$EXT_DIR")
ck() { if [ "$1" = init ]; then echo init; else echo $O/$1/checkpoints/update_001340.pt; fi; }
gpu() { export CUDA_VISIBLE_DEVICES=${1:?container GPU index}; echo "[closed-loop] $(date '+%F %T') stage=$STAGE CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES ${SIM[*]}"; }
M="$PY -m fastwam.memory_v2.online"
case "$STAGE" in
preflight)
  echo "memory2 $(git -c safe.directory='*' log --oneline -1)"
  $M preflight
  if $PY -c "import pytest" 2>/dev/null; then
    $PY -m pytest -q src/fastwam/memory_v2/tests/test_online.py src/fastwam/memory_v2/tests/test_history.py \
      src/fastwam/memory_v2/tests/test_dense.py
  else
    echo "(pytest is not installed in /opt/mwam: unit tests skipped)"
  fi ;;
parity)
  gpu ${2:-}; RUN=${3:-v2_A_cf}
  $M parity --checkpoint $(ck $RUN) --label $RUN --output $CL/parity ;;
smoke)
  gpu ${2:-}; RUN=${3:-v2_A_cf}
  $M run --checkpoint $(ck $RUN) --label $RUN --modes off on --scenes frozen --max-targets 96 --dependence \
    --output $CL/smoke "${SIM[@]}" ;;
frozen)
  gpu ${2:-}; RUN=${3:-v2_A_cf}
  $M run --checkpoint $(ck $RUN) --label $RUN --modes off on --scenes frozen --dependence --output $CL/frozen "${SIM[@]}" ;;
plan)
  gpu ${2:-}; SEED=${3:-17}; N=${4:-10}
  $M plan --seed $SEED --episodes $N --output $CL/scenes_seed${SEED}_n${N} "${SIM[@]}" ;;
bank)
  gpu ${2:-}; RUN=${3:?run or init}; MODES=${4:?modes, e.g. "on" or "off on"}; SCENES=${5:?scene manifest folder}; SHARD=${6:-0/1}
  $M run --checkpoint $(ck $RUN) --label $RUN --modes $MODES --scenes $SCENES --shard $SHARD --dependence \
    --output $CL/bank "${SIM[@]}" ;;
summary)
  $M summary --output ${2:-$CL/bank} ;;
*)
  echo "unknown stage $STAGE"; exit 2 ;;
esac
