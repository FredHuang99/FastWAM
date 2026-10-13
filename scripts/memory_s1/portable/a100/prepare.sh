#!/usr/bin/env bash
# A100-only reconstruction from the actual H100 fused environment records.
set -euo pipefail
ROOT="${FW_ROOT:-/workspace/FastWAM}"
cd "$ROOT"
BASE="$ROOT/outputs/recovery_aws_a100_v1"
INPUT="$BASE/migration"
BUILD="$ROOT/outputs/fused_environment_a100_v1"
NEW=/opt/rmbench-a100-env
HELPER="$ROOT/scripts/memory_s1/portable/a100/a100_migration.py"
mkdir -p "$BUILD"
exec 9>"$BUILD/build.lock"
flock -n 9 || { echo 'An A100 simulator build is already active'; exit 1; }
unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT CUDA_LAUNCH_BLOCKING PYTHONPATH PYTHONHOME VIRTUAL_ENV
unset CONDA_PINNED_PACKAGES CONDA_OVERRIDE_CUDA CONDA_OVERRIDE_GLIBC
export PIP_CONFIG_FILE=/dev/null CONDA_SUBDIR=linux-64
export CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 CUDAHOSTCXX=/usr/bin/g++-12
export CUDA_HOME="$NEW" TORCH_CUDA_ARCH_LIST=8.0 MAX_JOBS="${A100_COMPILE_JOBS:-16}"
export TORCH_EXTENSIONS_DIR="$BUILD/torch_extensions_torch260_cu126_sm80"
export PATH="$NEW/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export LD_LIBRARY_PATH="$NEW/lib:$NEW/targets/x86_64-linux/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64"
export CPATH="$NEW/include:$NEW/targets/x86_64-linux/include"
export LIBRARY_PATH="$NEW/lib:$NEW/targets/x86_64-linux/lib:$NEW/targets/x86_64-linux/lib/stubs"
export OMP_NUM_THREADS=4
[[ "$MAX_JOBS" =~ ^[1-9][0-9]*$ ]] || { echo 'A100_COMPILE_JOBS must be positive'; exit 2; }
test -f "$INPUT/simulator-conda-explicit.txt"
if [[ -f "$BUILD/COMPLETE.json" ]]; then
  "$NEW/bin/python" - "$BUILD/COMPLETE.json" "$INPUT/FILES.json" "${BASH_SOURCE[0]}" <<'PY'
import hashlib, importlib.metadata as md, json, sys
from pathlib import Path
digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
value = json.loads(Path(sys.argv[1]).read_text())
assert value['input_manifest_sha256'] == digest(sys.argv[2]), 'Migration input changed; preserve the old environment'
assert value['build_script_sha256'] == digest(sys.argv[3]), 'Build recipe changed; preserve the old environment'
assert value['prefix'] == sys.prefix and value['architecture'] == '8.0'
for name, version in value['packages'].items():
    assert md.version(name) == version, name
for row in value['extensions'].values():
    assert digest(row['path']) == row['sha256'], row['path']
import torch
assert torch.__version__ == value['torch'] and torch.version.cuda == value['cuda']
print('[reuse] Installed A100 packages, extension hashes, source manifest and recipe match')
PY
  exit 0
fi
if [[ ! -x /opt/miniforge/bin/conda ]]; then
  curl -fL --retry 3 -o "$BUILD/miniforge.sh" https://github.com/conda-forge/miniforge/releases/download/25.3.1-0/Miniforge3-Linux-x86_64.sh
  sha256sum "$BUILD/miniforge.sh" > "$BUILD/miniforge.sha256"
  bash "$BUILD/miniforge.sh" -b -u -p /opt/miniforge
fi
if [[ ! -x "$NEW/bin/python" ]]; then
  # Exact resolved CUDA 12.6 packages; no old CUDA 12.4 clone or new solver request.
  /opt/miniforge/bin/conda create -y -p "$NEW" --file "$INPUT/simulator-conda-explicit.txt"
fi
"$NEW/bin/nvcc" --version | tee "$BUILD/nvcc.txt"
grep -q 'release 12.6,' "$BUILD/nvcc.txt"
"$NEW/bin/python" -m pip install --disable-pip-version-check --no-input \
  torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu126
/opt/hf-tools/bin/python "$HELPER" pins --root "$ROOT" --kind simulator --output "$BUILD/simulator-pins.txt"
printf '%s\n' 'torch==2.6.0' 'torchvision==0.21.0' 'torchaudio==2.6.0' > "$BUILD/torch-constraints.txt"
"$NEW/bin/python" -m pip install --disable-pip-version-check --no-input \
  -c "$BUILD/torch-constraints.txt" -r "$BUILD/simulator-pins.txt"
"$NEW/bin/python" "$HELPER" patches --root "$ROOT"
attempt="$BUILD/build_$(date -u +%Y%m%dT%H%M%SZ)_$$"
mkdir -p "$attempt/wheels/curobo" "$attempt/wheels/pytorch3d"
cp -a "$INPUT/build_sources/curobo" "$attempt/curobo"
cp -a "$INPUT/build_sources/pytorch3d" "$attempt/pytorch3d"
CUROBO_VERSION="$("$NEW/bin/python" -c 'import json,sys;print(json.load(open(sys.argv[1]))["nvidia-curobo"])' "$BUILD/simulator-pins.sources.json")"
# Independent source trees, separate logs/wheels, two builds with MAX_JOBS each.
pids=()
cleanup() {
  local pid
  for pid in "${pids[@]}"; do
    if kill -0 "$pid" 2>/dev/null; then kill -TERM -- "-$pid" 2>/dev/null || true; fi
  done
  wait || true
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
setsid "$NEW/bin/python" -m pip wheel --no-deps --no-build-isolation --no-cache-dir \
  --wheel-dir "$attempt/wheels/pytorch3d" "$attempt/pytorch3d" > "$attempt/pytorch3d.log" 2>&1 &
pids+=("$!")
SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NVIDIA_CUROBO="$CUROBO_VERSION" \
  setsid "$NEW/bin/python" -m pip wheel --no-deps --no-build-isolation --no-cache-dir \
  --wheel-dir "$attempt/wheels/curobo" "$attempt/curobo" > "$attempt/curobo.log" 2>&1 &
pids+=("$!")
printf '[compile] two builds, %s compiler processes per build; logs=%s\n' "$MAX_JOBS" "$attempt"
result=0
for pid in "${pids[@]}"; do wait "$pid" || result=1; done
pids=()
if (( result )); then tail -n 80 "$attempt/pytorch3d.log" "$attempt/curobo.log"; exit 1; fi
"$NEW/bin/python" - "$attempt" <<'PY'
from pathlib import Path
import subprocess, sys
root = Path(sys.argv[1])
for name in ('pytorch3d', 'curobo'):
    wheels = list((root/'wheels'/name).glob('*.whl'))
    if len(wheels) != 1:
        raise SystemExit(f'Expected one wheel for {name}: {wheels}')
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps', '--force-reinstall', str(wheels[0])], check=True)
PY
"$NEW/bin/python" - "$BUILD" "$attempt" "$INPUT" "${BASH_SOURCE[0]}" <<'PY'
import hashlib, importlib, importlib.metadata as md, json, sys
from pathlib import Path
import torch
assert sys.version_info[:2] == (3,10)
assert torch.__version__.split('+')[0] == '2.6.0' and torch.version.cuda == '12.6'
assert torch.cuda.device_count() == 8
assert all(torch.cuda.get_device_capability(i) == (8,0) for i in range(8))
expected = json.loads((Path(sys.argv[1])/'simulator-pins.sources.json').read_text())
assert all(md.version(name) == version for name, version in expected.items()), expected
for name in ('sapien', 'mplib'):
    package = Path(importlib.import_module(name).__file__).parent
    saved = Path(sys.argv[3])/'patches'/name
    for path in saved.rglob('*.py'):
        assert (package/path.relative_to(saved)).read_bytes() == path.read_bytes(), path
    native = json.loads((Path(sys.argv[3])/'simulator-native-hashes.json').read_text())[name]
    for relative, expected_hash in native.items():
        assert hashlib.sha256((package/relative).read_bytes()).hexdigest() == expected_hash, relative
extensions = {}
for name in ('pytorch3d._C', 'curobo.curobolib.lbfgs_step_cu', 'curobo.curobolib.line_search_cu',
             'curobo.curobolib.kinematics_fused_cu', 'curobo.curobolib.tensor_step_cu', 'curobo.curobolib.geom_cu'):
    path = Path(importlib.import_module(name).__file__).resolve()
    assert path.is_relative_to(Path(sys.prefix).resolve()), path
    extensions[name] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
out = Path(sys.argv[1])/'COMPLETE.json'
data = {'architecture': '8.0', 'python': sys.version, 'torch': torch.__version__, 'cuda': torch.version.cuda,
        'prefix': sys.prefix, 'build': sys.argv[2], 'extensions': extensions,
        'input_manifest_sha256': hashlib.sha256((Path(sys.argv[3])/'FILES.json').read_bytes()).hexdigest(),
        'build_script_sha256': hashlib.sha256(Path(sys.argv[4]).read_bytes()).hexdigest(),
        'packages': {n: md.version(n) for n in ('nvidia-curobo','pytorch3d','sapien','mplib','warp-lang')},
        'scope': 'installation_only_not_planner_or_task_qualification'}
out.with_suffix('.partial').write_text(json.dumps(data, indent=2))
out.with_suffix('.partial').replace(out)
print('[installed] A100 SM80 simulator. Per-GPU checks and task warmup remain required.')
PY
