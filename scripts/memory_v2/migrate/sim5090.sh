#!/usr/bin/env bash
# mwam5090 container (11-07): the RMBench simulator environment for the RTX 5090 (sm_120), equal to the A100's
# /opt/rmbench-fused-env except the GPU stack. The A100 env (simkit/freeze.txt, collected by sim_kit_a100.py):
# python 3.10, torch 2.6.0+cu126 (no sm_120 kernels), conda CUDA 12.6.3, CuRobo 0.7.8 and PyTorch3D 0.7.8 wheels built
# for sm80, no patched site-packages files (0 of 50,592 differ from their RECORD). Here:
#   torch 2.7.1 / torchvision 0.22.1 / torchaudio 2.7.1 (cu128) and conda CUDA 12.8.1 (nvcc for sm_120);
#   CuRobo and PyTorch3D built for sm_120 from the A100's own build sources (simkit/sources);
#   every other package at the A100's exact version (pip --no-deps).
# The env lives in the bind-mounted /opt/rmbench-env; /opt/rmbench-fused-env (the path the dense config and the
# memory_v2 scripts use) is a symlink to it.
# Steps: conda | env | pip | build | check | gate | all (= conda env pip build check gate). Rerunning a step is safe.
# Own log: /workspace/FastWAM/outputs/fused_environment_5090_sm120/SIM5090.log (append; last line = exit code).
set -euo pipefail
KIT=/workspace/FastWAM-memory2/outputs/migration_5090_v1/simkit
ENV=/opt/rmbench-env
LINK=/opt/rmbench-fused-env
OUT=/workspace/FastWAM/outputs/fused_environment_5090_sm120
CONDA=/opt/miniforge/bin/conda
CUDA_LABEL=nvidia/label/cuda-12.8.1
TORCH=(torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1)
mkdir -p "$OUT"
exec > >(tee -a "$OUT/SIM5090.log") 2>&1
STEP=${1:?conda|env|pip|build|check|gate|all}
trap 'rc=$?; echo "[sim5090] $(date "+%F %T") step $STEP finished, exit code $rc"' EXIT
step() { echo "[sim5090] $(date '+%F %T') $*"; }
unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT PYTHONPATH PYTHONHOME VIRTUAL_ENV CONDA_PINNED_PACKAGES
export PIP_CONFIG_FILE=/dev/null PYTHONUNBUFFERED=1 CONDA_SUBDIR=linux-64
[ -f "$KIT/KIT.json" ] || { echo "simkit missing at $KIT: run h100_restore.sh delta after the A100 shipped it"; exit 1; }

build_env() {   # compiler / CUDA variables for every build or JIT step
  export CUDA_HOME=$ENV CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 CUDAHOSTCXX=/usr/bin/g++-12
  export TORCH_CUDA_ARCH_LIST=12.0 FORCE_CUDA=1 OMP_NUM_THREADS=4
  export PATH="$ENV/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  export LD_LIBRARY_PATH="$ENV/lib:$ENV/targets/x86_64-linux/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64"
  export CPATH="$ENV/include:$ENV/targets/x86_64-linux/include"
  export LIBRARY_PATH="$ENV/lib:$ENV/targets/x86_64-linux/lib:$ENV/targets/x86_64-linux/lib/stubs"
  unset C_INCLUDE_PATH CPLUS_INCLUDE_PATH NVCC_APPEND_FLAGS NVCC_PREPEND_FLAGS
}

conda_() {
  if [ -x "$CONDA" ]; then step "miniforge present: $($CONDA --version)"; return; fi
  step "miniforge 25.3.1-0 -> /opt/miniforge (same installer as the A100)"
  curl -fL --retry 3 -o /mnt/tmp/Miniforge3-25.3.1-0.sh \
    https://github.com/conda-forge/miniforge/releases/download/25.3.1-0/Miniforge3-Linux-x86_64.sh
  sha256sum /mnt/tmp/Miniforge3-25.3.1-0.sh | tee "$OUT/miniforge.sha256"
  bash /mnt/tmp/Miniforge3-25.3.1-0.sh -b -u -p /opt/miniforge
  $CONDA --version
}

env_() {
  if [ ! -x "$ENV/bin/python" ]; then
    step "conda env $ENV: python 3.10 (the A100: $(grep -E '^python ' "$KIT/conda_cuda.txt" | awk '{print $2}'))"
    $CONDA create -y -p "$ENV" --override-channels -c conda-forge python=3.10 pip
  fi
  if ! "$ENV/bin/nvcc" --version 2>/dev/null | grep -q 'release 12.8'; then
    step "CUDA 12.8.1 development packages ($CUDA_LABEL; the A100 has the same set at 12.6.3)"
    $CONDA install -y -p "$ENV" --override-channels --strict-channel-priority -c "$CUDA_LABEL" -c conda-forge \
      cuda-version=12.8 cuda-minimal-build cuda-cudart-dev cuda-cccl cuda-cupti cuda-nvrtc-dev cuda-nvtx \
      cuda-profiler-api libcublas-dev libcufft-dev libcurand-dev libcusolver-dev libcusparse-dev libnvjitlink
  fi
  "$ENV/bin/nvcc" --version | tail -n 2
  ln -sfn "$ENV" "$LINK"
  step "$LINK -> $(readlink "$LINK"); python $("$LINK/bin/python" -c 'import sys; print(sys.version.split()[0])')"
}

pip_() {
  local PY=$ENV/bin/python
  step "torch stack for sm_120: ${TORCH[*]} (cu128)"
  $PY -m pip install --disable-pip-version-check --no-input "${TORCH[@]}" --index-url https://download.pytorch.org/whl/cu128
  # Everything else exactly as the A100 env (no dependency resolution: the freeze is already a resolved set).
  # Left out: the torch stack and its CUDA wheels (installed above), local wheels (CuRobo / PyTorch3D, built below),
  # conda-provided pip / packaging (file:// lines).
  grep -v -E '^(torch|torchvision|torchaudio|triton)==|^nvidia-[a-z0-9-]+-cu1[0-9]==| @ ' "$KIT/freeze.txt" > "$OUT/pins_from_a100.txt"
  grep -E '^(torch|torchvision|torchaudio|triton)==|^nvidia-[a-z0-9-]+-cu1[0-9]==| @ ' "$KIT/freeze.txt" > "$OUT/pins_not_copied.txt" || true
  step "$(wc -l < "$OUT/pins_from_a100.txt") packages at the A100 versions (--no-deps); not copied: $(tr '\n' ' ' < "$OUT/pins_not_copied.txt" | cut -c1-400)"
  $PY -m pip install --disable-pip-version-check --no-input --no-deps -r "$OUT/pins_from_a100.txt"
  $PY -c "import packaging" 2>/dev/null || $PY -m pip install --disable-pip-version-check --no-input packaging
  $PY -m pip check || step "pip check reported the lines above (review; expected only around the rebuilt packages)"
}

build_one() {   # name: build a wheel from the A100's build source, sm_120
  local name=$1 PY=$ENV/bin/python
  rm -rf "$OUT/build/$name" "$OUT/wheels/$name"
  mkdir -p "$OUT/build" "$OUT/wheels/$name"
  cp -a "$KIT/sources/$name" "$OUT/build/$name"
  $PY -m pip wheel --disable-pip-version-check --no-deps --no-build-isolation --no-cache-dir \
    --wheel-dir "$OUT/wheels/$name" "$OUT/build/$name" > "$OUT/build_$name.log" 2>&1
}

build() {
  build_env
  export MAX_JOBS=${MAX_JOBS:-12}
  local V
  V=$(python3 -c "import json; print(json.load(open('$KIT/KIT.json'))['sources']['curobo']['version'])")
  export SETUPTOOLS_SCM_PRETEND_VERSION="$V" SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NVIDIA_CUROBO="$V"
  step "nvcc $(nvcc --version | grep -o 'release [0-9.]*'); $(/usr/bin/gcc-12 --version | head -1); TORCH_CUDA_ARCH_LIST=$TORCH_CUDA_ARCH_LIST MAX_JOBS=$MAX_JOBS x 2 builds"
  step "building PyTorch3D and CuRobo $V in parallel (logs $OUT/build_pytorch3d.log, $OUT/build_curobo.log)"
  build_one pytorch3d & p1=$!
  build_one curobo & p2=$!
  rc=0
  wait $p1 || { rc=1; step "PyTorch3D build FAILED; first errors:"; grep -n -m 20 -E "error:|error |FAILED:|fatal" "$OUT/build_pytorch3d.log" || tail -n 40 "$OUT/build_pytorch3d.log"; }
  wait $p2 || { rc=1; step "CuRobo build FAILED; first errors:"; grep -n -m 20 -E "error:|error |FAILED:|fatal" "$OUT/build_curobo.log" || tail -n 40 "$OUT/build_curobo.log"; }
  [ $rc = 0 ] || exit 1
  for name in pytorch3d curobo; do
    "$ENV/bin/python" -m pip install --disable-pip-version-check --no-deps --force-reinstall "$OUT"/wheels/$name/*.whl
  done
  ls -la "$OUT"/wheels/*/
}

check() {
  build_env
  step "import probe (the same probe as online preflight)"
  (cd /workspace/FastWAM/resources/RMBench && "$LINK/bin/python" - <<'PY'
import json, sys
r = {"python": sys.version.split()[0]}
import torch
r.update(torch=torch.__version__, cuda=torch.version.cuda, available=torch.cuda.is_available(),
         device=torch.cuda.get_device_name(0), capability=".".join(map(str, torch.cuda.get_device_capability(0))),
         arch_list=torch.cuda.get_arch_list())
x = torch.randn(256, 256, device="cuda"); r["matmul"] = float((x @ x).abs().mean())
for name in ("sapien", "mplib", "curobo", "pytorch3d", "numpy", "warp"):
    try:
        m = __import__(name); r[name] = getattr(m, "__version__", "ok")
    except Exception as e:
        r[name] = "ERROR " + repr(e)[:200]
for name in ("curobo.curobolib.lbfgs_step_cu", "curobo.curobolib.line_search_cu", "curobo.curobolib.kinematics_fused_cu",
             "curobo.curobolib.tensor_step_cu", "curobo.curobolib.geom_cu", "pytorch3d._C"):
    try:
        __import__(name); r[name] = "ok"
    except Exception as e:
        r[name] = "ERROR " + repr(e)[:200]
print(json.dumps(r, indent=1))
bad = [k for k, v in r.items() if isinstance(v, str) and v.startswith("ERROR")]
sys.exit(1 if bad or r["capability"] != "12.0" or "sm_120" not in r["arch_list"] else 0)
PY
  )
  step "package versions vs the A100 env (expected differences: torch stack, its CUDA wheels, CuRobo / PyTorch3D builds, pip / packaging)"
  "$ENV/bin/python" -m pip freeze --all > "$OUT/freeze_5090.txt"
  python3 - "$KIT/freeze.txt" "$OUT/freeze_5090.txt" <<'PY'
import re, sys
def read(p):
    out = {}
    for line in open(p):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name = re.split(r"==| @ ", line)[0].lower().replace("_", "-")
        out[name] = line
    return out
a, b = read(sys.argv[1]), read(sys.argv[2])
expected = re.compile(r"^(torch|torchvision|torchaudio|triton|nvidia-.*-cu1\d|nvidia-curobo|pytorch3d|pip|packaging)$")
diff = [(k, a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
unexpected = [d for d in diff if not expected.match(d[0])]
for k, x, y in diff:
    print(f"  {'EXPECTED  ' if expected.match(k) else 'UNEXPECTED'} {k}: A100 {x}  |  5090 {y}")
print(f"  {len(diff)} differing packages, {len(unexpected)} unexpected")
sys.exit(1 if unexpected else 0)
PY
  step "site-packages files vs their RECORD (the A100: 0 modified)"
  "$LINK/bin/python" /workspace/FastWAM-memory2/scripts/memory_v2/migrate/sim_kit_a100.py --out "$OUT/record_check" | sed -n "1,6p"
  step "offscreen render probe (SAPIEN, cuda:0)"
  "$LINK/bin/python" - "$OUT" <<'PY'
import sys
from pathlib import Path
import numpy as np, sapien
from PIL import Image
renderer = sapien.render.RenderSystem(device="cuda:0")
scene = sapien.Scene([sapien.physx.PhysxCpuSystem(), renderer])
camera = scene.add_camera("probe", 64, 64, 1.0, 0.1, 10)
scene.step(); scene.update_render(); camera.take_picture()
pixels = camera.get_picture("Color")
assert pixels.shape == (64, 64, 4) and np.isfinite(pixels).all()
Image.fromarray((np.clip(pixels[..., :3], 0, 1) * 255).astype(np.uint8)).save(Path(sys.argv[1]) / "render_probe.png")
print("SAPIEN", sapien.__version__, "render device", renderer.device, "offscreen render OK", pixels.shape)
PY
}

gate() {
  # One complete expert episode per task through the production planner (CuRobo, rendering, the fused_graph_v1
  # kernels JIT-built for sm_120 on first use), as sim_ready.sh step 4 on the A100, in a scratch folder.
  build_env
  local T=/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/sim_ready_5090_$(date -u +%Y%m%d_%H%M%S)
  mkdir -p "$T"
  cd /workspace/FastWAM-memory2
  for task in put_back_block swap_blocks; do
    local start rc
    start=$(date +%s)
    set +e
    PYTHONPATH=/workspace/FastWAM-memory2/src CUDA_VISIBLE_DEVICES=${GATE_GPU:-0} OMP_NUM_THREADS=8 MKL_NUM_THREADS=8 \
      timeout 2400 /opt/mwam/bin/python -m fastwam.memory_v2.online plan --tasks $task --seed 17 --episodes 1 \
      --output "$T" > "$T/$task.log" 2>&1
    rc=$?
    set -e
    step "gate $task: exit $rc after $(( $(date +%s) - start )) s (log $T/$task.log)"
    grep -E '\[scene-plan\]|\[plan\].*complete' "$T/$task.log" | tail -n 3 || true
    if [ $rc != 0 ]; then
      grep -v -E 'UserWarning|warn\(' "$T/$task.log" | tail -n 30
      exit 1
    fi
  done
  step "gate passed: the 5090 simulator plans and renders both tasks"
}

case "$STEP" in
  conda) conda_ ;; env) env_ ;; pip) pip_ ;; build) build ;; check) check ;; gate) gate ;;
  all) conda_; env_; pip_; build; check; gate ;;
  *) echo "unknown step $STEP"; exit 2 ;;
esac
