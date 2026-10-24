#!/usr/bin/env bash
# memory_v2 closed loop on the A100 (policy: /opt/mwam; simulator: the dense config's, or $SIM_PY).
#   bash closed_loop.sh preflight                    read-only inventory + CPU unit tests (no GPU memory)
#   bash closed_loop.sh parity  <gpu> [run]          online path vs offline cache, 8 val windows (default run v2_A_cf)
#   bash closed_loop.sh smoke   <gpu> [run]          2 frozen scenes x (off, on), first 96 targets, dependence logged
#   bash closed_loop.sh frozen  <gpu> [run]          2 frozen scenes x (off, on), official 500/1000 caps
#   bash closed_loop.sh plan    <gpu> [seed] [n]     expert-feasible scene bank (default seed 17, 10 per task)
#   bash closed_loop.sh bank    <gpu> <run|init> "<modes>" <scenes> [k/n]
#   bash closed_loop.sh guide   <gpu> <run> <scale> <scenes> [task:seed ...]   memory guidance, mode on, label <run>_g<scale>
#   bash closed_loop.sh eval    <gpu> <ckpt.pt> <label> "<modes>" <scenes> [out] [extra online args]   no --dependence
#   bash closed_loop.sh summary [output folder]
#   bash closed_loop.sh render  <gpu>                SAPIEN offscreen render probe
#   bash closed_loop.sh chain   <lane> <gpu> [run]   wait for a Phase-3 lane to finish, then parity -> smoke -> bank
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
[ -n "${VK_ICD:-}" ] && SIM+=(--vk-icd "$VK_ICD")
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
render)
  # SAPIEN offscreen camera probe in the simulator env (a few hundred MB on <gpu>): as the container is, and with
  # a generated NVIDIA Vulkan ICD file (the container has no /etc/vulkan/icd.d/nvidia_icd.json).
  gpu ${2:-}
  SPY=${SIM_PY:-/opt/rmbench-fused-env/bin/python}
  echo "-- Vulkan ICD files and NVIDIA graphics libraries"
  find /etc /usr/share /usr/local/share /usr/local/nvidia -maxdepth 4 -name '*icd*.json' 2>/dev/null | head
  ls -l /usr/lib/x86_64-linux-gnu/libGLX_nvidia.so* /usr/lib/x86_64-linux-gnu/libEGL_nvidia.so* \
    /usr/lib/x86_64-linux-gnu/libnvidia-glcore.so* /usr/local/nvidia/lib64/libGLX_nvidia.so* 2>&1 | head
  echo "NVIDIA_DRIVER_CAPABILITIES=${NVIDIA_DRIVER_CAPABILITIES:-unset}"
  mkdir -p $CL/vulkan
  ICD=$CL/vulkan/nvidia_icd.json
  printf '{"file_format_version":"1.0.0","ICD":{"library_path":"libGLX_nvidia.so.0","api_version":"1.3.0"}}\n' > $ICD
  probe() {
    timeout 300 env -u PYTHONPATH -u VIRTUAL_ENV "$@" $SPY - <<'PY'
import numpy as np, sapien
renderer = sapien.render.RenderSystem(device="cuda:0")
scene = sapien.Scene([sapien.physx.PhysxCpuSystem(), renderer])
camera = scene.add_camera("probe", 64, 64, 1.0, 0.1, 10)
scene.step(); scene.update_render(); camera.take_picture()
pixels = camera.get_picture("Color")
assert pixels.shape == (64, 64, 4) and np.isfinite(pixels).all()
print("RENDER OK", sapien.__version__, renderer.device, pixels.shape)
PY
  }
  echo "-- probe 1: container as is (VK_ICD_FILENAMES=${VK_ICD_FILENAMES:-unset})"
  probe 2>&1 | tail -n 6
  echo "-- probe 2: VK_ICD_FILENAMES=$ICD"
  probe VK_ICD_FILENAMES=$ICD 2>&1 | tail -n 6 ;;
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
guide)
  # Memory guidance on chosen scenes, mode on only, no --dependence (faster). Label <run>_g<scale> in $CL/bank,
  # so the summary pairs it scene-by-scene with <run>/on (same noise seeds; only the guidance differs).
  gpu ${2:-}; RUN=${3:?run}; SCALE=${4:?guidance scale, e.g. 2}; SCENES=${5:?scene manifest folder}; shift 5
  $M run --checkpoint $(ck $RUN) --label ${RUN}_g${SCALE} --modes on --scenes $SCENES --guidance $SCALE \
    --seeds "$@" --output $CL/bank "${SIM[@]}" ;;
eval)
  # Any checkpoint file, no --dependence (~3x faster per decision). Output folder defaults to $CL/a2.
  gpu ${2:-}; CKPT=${3:?checkpoint .pt}; LABEL=${4:?label}; MODES=${5:?modes}; SCENES=${6:?scene manifest folder}; OUT=${7:-$CL/a2}
  shift 7 2>/dev/null || shift $#
  $M run --checkpoint $CKPT --label $LABEL --modes $MODES --scenes $SCENES --output $OUT "${SIM[@]}" "$@" ;;
summary)
  $M summary --output ${2:-$CL/bank} ;;
chain)
  # Take over the GPU of a Phase-3 lane the moment its whole queue is done (polls every minute, so the GPU guard
  # never sees it idle), then: parity -> smoke -> (only if all 4 smoke episodes completed) the scene bank in
  # modes off+on, or the 2 frozen scenes at full length if the bank is not planned yet.
  LANE=${2:?lane A|B|C}; G=${3:?container GPU index}; RUN=${4:-v2_A_cf}
  SELF=/workspace/FastWAM-memory2/scripts/memory_v2/jobs/closed_loop.sh
  UUID=$(nvidia-smi --query-gpu=index,uuid --format=csv,noheader | awk -F', ' -v i=$G '$1==i{print $2}')
  echo "[chain] $(date -u '+%F %T') UTC waiting for $O/RESULTS_3_$LANE.txt and no training process on GPU $G ($UUID)"
  while true; do
    busy=0
    for pid in $(pgrep -f "python.*fastwam.memory_v2.train_v2"); do
      v=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | sed -n 's/^CUDA_VISIBLE_DEVICES=//p')
      if [ "$v" = "$UUID" ] || [ "$v" = "$G" ]; then busy=1; fi
    done
    if [ -f $O/RESULTS_3_$LANE.txt ] && [ $busy = 0 ]; then break; fi
    sleep 60
  done
  echo "[chain] $(date -u '+%F %T') UTC GPU $G is free: parity"
  bash $SELF parity $G $RUN
  echo "[chain] $(date -u '+%F %T') UTC smoke"
  bash $SELF smoke $G $RUN
  n=$(ls $CL/smoke/*/*/*/seed_*/result.json 2>/dev/null | wc -l)
  echo "[chain] $(date -u '+%F %T') UTC smoke episodes completed: $n / 4"
  if [ "$n" -lt 4 ]; then echo "[chain] smoke incomplete: stopping here (errors: ls $CL/smoke/*/*/*/seed_*/ERROR.json)"; exit 1; fi
  BANK=$CL/scenes_seed17_n10
  if $PY - $BANK <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
ok = all((d / f"{t}.json").exists() and json.loads((d / f"{t}.json").read_text()).get("complete") for t in ("put_back_block", "swap_blocks"))
sys.exit(0 if ok else 1)
PY
  then
    echo "[chain] $(date -u '+%F %T') UTC scene bank $BANK complete: bank run, modes off + on"
    bash $SELF bank $G $RUN "off on" $BANK
  else
    echo "[chain] $(date -u '+%F %T') UTC scene bank not complete: the 2 frozen scenes at full length"
    bash $SELF frozen $G $RUN
  fi
  echo "[chain] $(date -u '+%F %T') UTC chain finished" ;;
*)
  echo "unknown stage $STAGE"; exit 2 ;;
esac
