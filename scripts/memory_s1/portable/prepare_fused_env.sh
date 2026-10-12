#!/usr/bin/env bash
# Explicit user-invoked build; leaves the old simulator and training Python intact.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
OLD=/opt/rmbench-env
NEW=/opt/rmbench-fused-env
BUILD="$ROOT/outputs/fused_environment_h100_v1"
HELPER="$ROOT/scripts/memory_s1/portable/fused_environment.py"
mkdir -p "$BUILD"
exec 9>"$BUILD/build.lock"
flock -n 9 || { echo 'A fused environment build is already active.' >&2; exit 1; }
unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT CUDA_LAUNCH_BLOCKING PYTHONPATH
export OMP_NUM_THREADS=4 MAX_JOBS=4 TORCH_CUDA_ARCH_LIST=9.0
test -x "$OLD/bin/python"
test -x /opt/miniforge/bin/conda
command -v gcc-12 >/dev/null
command -v g++-12 >/dev/null
if [[ ! -f "$BUILD/before.json" ]]; then
  CUDA_HOME="$OLD" LD_LIBRARY_PATH="$OLD/lib:$OLD/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}" \
    "$OLD/bin/python" "$HELPER" snapshot --output "$BUILD/before.json"
fi
if [[ ! -x "$NEW/bin/python" ]]; then
  /opt/miniforge/bin/conda create -y -p "$NEW" --clone "$OLD"
fi
export CUDA_HOME="$NEW" CC=gcc-12 CXX=g++-12
export PATH="$NEW/bin:$PATH"
export LD_LIBRARY_PATH="$NEW/lib:$NEW/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
# Avoid overwriting .so files in the original editable CuRobo checkout.
export TORCH_EXTENSIONS_DIR="$BUILD/torch_extensions"
if [[ -f "$BUILD/COMPLETE.json" ]]; then
  "$NEW/bin/python" "$HELPER" verify --before "$BUILD/before.json" --output "$BUILD/current.json"
  echo '[environment] existing fused environment verified; no reinstall'
  exit 0
fi
# Conda clone preserves exact CUDA 12.4 component requests. Replacing only the
# toolkit metapackage leaves incompatible visual-tools/libcufile/Nsight pins.
# Save the old inventory, update every CUDA request, and pin other packages.
CUDA_ATTEMPT="$BUILD/cuda_$(date -u +%Y%m%dT%H%M%SZ)_$$"
"$NEW/bin/python" "$HELPER" cuda-specs --prefix "$NEW" --output "$CUDA_ATTEMPT"
CONDA_CUDA=(/opt/miniforge/bin/conda install -y -p "$NEW"
  --override-channels -c nvidia/label/cuda-12.6.3 -c conda-forge
  --update-specs --no-pin)
echo "[cuda] solving fixed 12.6.3 release; diagnostics=$CUDA_ATTEMPT"
if ! env -u CONDA_PINNED_PACKAGES CONDA_SUBDIR=linux-64 "${CONDA_CUDA[@]}" \
    --file "$CUDA_ATTEMPT/requested-specs.txt" --dry-run --json > "$CUDA_ATTEMPT/solve.json"; then
  cat "$CUDA_ATTEMPT/solve.json"
  echo '[cuda] solve failed; no CUDA transaction applied; original simulator unchanged' >&2
  exit 1
fi
"$NEW/bin/python" "$HELPER" cuda-plan --prefix "$NEW" \
  --before "$CUDA_ATTEMPT/before.json" --plan "$CUDA_ATTEMPT/solve.json" \
  --output "$CUDA_ATTEMPT/resolved.json"
echo '[cuda] installing the reviewed package versions/builds into the isolated clone'
env -u CONDA_PINNED_PACKAGES CONDA_SUBDIR=linux-64 "${CONDA_CUDA[@]}" \
  --file "$CUDA_ATTEMPT/resolved.specs.txt"
"$NEW/bin/python" "$HELPER" cuda-check --prefix "$NEW" \
  --before "$CUDA_ATTEMPT/before.json" --plan "$CUDA_ATTEMPT/resolved.json" \
  --output "$CUDA_ATTEMPT/installed.json"
"$NEW/bin/python" -m pip install --disable-pip-version-check --no-input \
  torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
"$NEW/bin/python" -m pip install --disable-pip-version-check --no-input --no-deps warp-lang==1.12.0
"$NEW/bin/python" "$HELPER" copy-source --source "$ROOT/resources/RMBench/envs/curobo" --output "$BUILD/curobo"
"$NEW/bin/python" "$HELPER" copy-source --source "$ROOT/resources/PyTorch3D" --output "$BUILD/pytorch3d"
CUROBO_VERSION="$("$NEW/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["packages"]["curobo"]["version"])' "$BUILD/before.json")"
"$NEW/bin/nvcc" --version | tee "$BUILD/nvcc.txt"
"$NEW/bin/python" -m pip install --no-input --no-deps --no-build-isolation --force-reinstall "$BUILD/pytorch3d"
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NVIDIA_CUROBO="$CUROBO_VERSION" \
  "$NEW/bin/python" -m pip install --no-input --no-deps --no-build-isolation --force-reinstall "$BUILD/curobo"
"$NEW/bin/python" "$HELPER" verify --before "$BUILD/before.json" --output "$BUILD/COMPLETE.json"
echo '[environment] isolated simulator ready; fused functional qualification is still required'
