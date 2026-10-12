#!/usr/bin/env bash
# Explicit user-invoked build; leaves the old simulator and training Python intact.
set -euo pipefail
STAGE=prerequisites
trap 'code=$?; printf "[environment error] stage=%s line=%s exit=%s; original simulator is unchanged\n" "$STAGE" "$LINENO" "$code" >&2; exit "$code"' ERR
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
OLD=/opt/rmbench-env
NEW=/opt/rmbench-fused-env
BUILD="$ROOT/outputs/fused_environment_h100_v1"
HELPER="$ROOT/scripts/memory_s1/portable/fused_environment.py"
mkdir -p "$BUILD"
exec 9>"$BUILD/build.lock"
flock -n 9 || { echo 'A fused environment build is already active.' >&2; exit 1; }
unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT CUDA_LAUNCH_BLOCKING PYTHONPATH PYTHONHOME VIRTUAL_ENV
unset CONDA_PINNED_PACKAGES CONDA_OVERRIDE_CUDA CONDA_OVERRIDE_GLIBC
export OMP_NUM_THREADS=4 MAX_JOBS=2 TORCH_CUDA_ARCH_LIST=9.0
export CONDA_SUBDIR=linux-64 CONDA_PIP_INTEROP_ENABLED=false
DRIVER_LIBS=/usr/local/nvidia/lib:/usr/local/nvidia/lib64
export LD_LIBRARY_PATH="$OLD/lib:$OLD/targets/x86_64-linux/lib:$DRIVER_LIBS"
test -x "$OLD/bin/python"
test -x /opt/miniforge/bin/conda
"$OLD/bin/python" "$HELPER" preflight --root "$ROOT" --output "$BUILD/prerequisites.json"
if [[ ! -f "$BUILD/before.json" ]]; then
  CUDA_HOME="$OLD" \
    "$OLD/bin/python" "$HELPER" snapshot --output "$BUILD/before.json"
fi
if [[ ! -x "$NEW/bin/python" ]]; then
  STAGE=clone
  /opt/miniforge/bin/conda create -y -p "$NEW" --clone "$OLD"
fi
export CUDA_HOME="$NEW" CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 CUDAHOSTCXX=/usr/bin/g++-12
export PATH="$NEW/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export LD_LIBRARY_PATH="$NEW/lib:$NEW/targets/x86_64-linux/lib:$DRIVER_LIBS"
export CPATH="$NEW/include:$NEW/targets/x86_64-linux/include"
export LIBRARY_PATH="$NEW/lib:$NEW/targets/x86_64-linux/lib:$NEW/targets/x86_64-linux/lib/stubs"
unset C_INCLUDE_PATH CPLUS_INCLUDE_PATH
# Avoid overwriting .so files in the original editable CuRobo checkout.
export TORCH_EXTENSIONS_DIR="$BUILD/torch_extensions_torch260_cu126_sm90"
if [[ -f "$BUILD/COMPLETE.json" ]]; then
  "$NEW/bin/python" "$HELPER" verify --before "$BUILD/before.json" --output "$BUILD/current.json"
  echo '[environment] existing fused environment verified; no reinstall'
  exit 0
fi
# Validate sources before any environment mutation or extension compilation.
STAGE=sources
"$NEW/bin/python" "$HELPER" copy-source --source "$ROOT/resources/RMBench/envs/curobo" --output "$BUILD/curobo"
"$NEW/bin/python" "$HELPER" copy-source --source "$ROOT/resources/PyTorch3D" --output "$BUILD/pytorch3d"
STAGE=cuda_plan
if [[ -f "$BUILD/CUDA_COMPLETE.json" ]]; then
  "$NEW/bin/python" "$HELPER" cuda-check --prefix "$NEW" \
    --before "$BUILD/CUDA_COMPLETE.json" --plan "$BUILD/CUDA_COMPLETE.json" \
    --output "$BUILD/cuda-current.json"
  echo '[cuda] completed development installation verified; skip solve/remove/install'
else
# A clean dry-run solve must not inherit retired packages or old toolkit pins.
# No binary package is installed until BOTH the new set and removal are checked.
CUDA_ATTEMPT="$BUILD/cuda_$(date -u +%Y%m%dT%H%M%SZ)_$$"
"$NEW/bin/python" "$HELPER" cuda-specs --prefix "$NEW" --output "$CUDA_ATTEMPT"
CHANNELS=(--override-channels -c nvidia/label/cuda-12.6.3 -c conda-forge --strict-channel-priority)
echo "[cuda] solving clean CUDA 12.6 development packages; diagnostics=$CUDA_ATTEMPT"
if ! /opt/miniforge/bin/conda create -y -p "$CUDA_ATTEMPT/solve-prefix" "${CHANNELS[@]}" \
    --no-default-packages --no-pin \
    --file "$CUDA_ATTEMPT/requested-specs.txt" --dry-run --json > "$CUDA_ATTEMPT/solve.json"; then
  cat "$CUDA_ATTEMPT/solve.json"
  echo '[cuda] solve failed before removal; no environment changed' >&2
  exit 1
fi
"$NEW/bin/python" "$HELPER" cuda-plan --prefix "$NEW" \
  --before "$CUDA_ATTEMPT/before.json" --plan "$CUDA_ATTEMPT/solve.json" \
  --output "$CUDA_ATTEMPT/resolved.json"
mapfile -t CUDA_REMOVE < "$CUDA_ATTEMPT/remove-names.txt"
if (( ${#CUDA_REMOVE[@]} )); then
  STAGE=cuda_removal_plan
  if ! /opt/miniforge/bin/conda remove -y -p "$NEW" --no-pin --offline \
      --dry-run --json "${CUDA_REMOVE[@]}" > "$CUDA_ATTEMPT/remove-plan.json"; then
    cat "$CUDA_ATTEMPT/remove-plan.json"
    echo '[cuda] removal solve failed; no environment changed' >&2
    exit 1
  fi
  "$NEW/bin/python" "$HELPER" cuda-remove-plan --prefix "$NEW" \
    --before "$CUDA_ATTEMPT/before.json" --plan "$CUDA_ATTEMPT/remove-plan.json" \
    --output "$CUDA_ATTEMPT/removed-expected.json"
fi
STAGE=torch_dependency_plan
# Resolve the wheel dependencies before removing old CUDA packages as well.
"$NEW/bin/python" -m pip install --dry-run --report "$CUDA_ATTEMPT/torch-plan.json" \
  --disable-pip-version-check --no-input --only-binary=:all: \
  torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
if (( ${#CUDA_REMOVE[@]} )); then
  STAGE=cuda_removal
  echo '[cuda] removing only the reviewed CUDA packages from /opt/rmbench-fused-env'
  /opt/miniforge/bin/conda remove -y -p "$NEW" --no-pin --offline "${CUDA_REMOVE[@]}"
  "$NEW/bin/python" "$HELPER" cuda-removed --prefix "$NEW" \
    --before "$CUDA_ATTEMPT/before.json" --plan "$CUDA_ATTEMPT/removed-expected.json" \
    --output "$CUDA_ATTEMPT/removed.json"
fi
STAGE=cuda_install
echo '[cuda] installing the resolved development versions/builds into the clone'
/opt/miniforge/bin/conda install -y -p "$NEW" "${CHANNELS[@]}" --update-specs --no-pin \
  --file "$CUDA_ATTEMPT/resolved.specs.txt"
"$NEW/bin/python" "$HELPER" cuda-check --prefix "$NEW" \
  --before "$CUDA_ATTEMPT/before.json" --plan "$CUDA_ATTEMPT/resolved.json" \
  --output "$BUILD/CUDA_COMPLETE.json"
fi
STAGE=torch_install
"$NEW/bin/python" -m pip install --disable-pip-version-check --no-input --only-binary=:all: \
  torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
"$NEW/bin/python" -m pip install --disable-pip-version-check --no-input --no-deps warp-lang==1.12.0
CUROBO_VERSION="$("$NEW/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["packages"]["curobo"]["version"])' "$BUILD/before.json")"
PYTORCH3D_VERSION="$("$NEW/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["packages"]["pytorch3d"]["version"])' "$BUILD/before.json")"
"$NEW/bin/nvcc" --version | tee "$BUILD/nvcc.txt"
STAGE=pytorch3d_wheel
"$NEW/bin/python" "$HELPER" build-wheel --source "$BUILD/pytorch3d" --version "$PYTORCH3D_VERSION" --output "$BUILD/pytorch3d-wheel.json"
PYTORCH3D_WHEEL="$("$NEW/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["wheel"])' "$BUILD/pytorch3d-wheel.json")"
"$NEW/bin/python" -m pip install --no-input --no-deps --force-reinstall "$PYTORCH3D_WHEEL"
STAGE=curobo_wheel
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NVIDIA_CUROBO="$CUROBO_VERSION" \
  "$NEW/bin/python" "$HELPER" build-wheel --source "$BUILD/curobo" --version "$CUROBO_VERSION" --output "$BUILD/curobo-wheel.json"
CUROBO_WHEEL="$("$NEW/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["wheel"])' "$BUILD/curobo-wheel.json")"
"$NEW/bin/python" -m pip install --no-input --no-deps --force-reinstall "$CUROBO_WHEEL"
STAGE=verify
"$NEW/bin/python" "$HELPER" verify --before "$BUILD/before.json" --output "$BUILD/COMPLETE.json"
echo '[environment] isolated simulator ready; fused functional qualification is still required'
