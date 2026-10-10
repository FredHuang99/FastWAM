#!/usr/bin/env bash
set -euo pipefail
ROOT="${FW_ROOT:-/workspace/FastWAM}"
READY="${READY_DIR:-$ROOT/outputs/recovery_aws_v2/restored}"
MODE="${1:?Choose system, hf, training, simulator or patches}"
cd "$ROOT"
# Drop the image's global install constraints in these child installs only.
unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT
export PIP_CONFIG_FILE=/dev/null PYTHONUNBUFFERED=1

case "$MODE" in
system)
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git curl ca-certificates zstd python3-venv build-essential gcc-12 g++-12 cmake ninja-build \
    libvulkan1 vulkan-tools libgl1 libglib2.0-0 libegl1 libx11-6 libxext6 libsm6 ffmpeg
  ;;
hf)
  python3 -m venv /opt/hf-tools
  /opt/hf-tools/bin/python -m pip install 'huggingface-hub==1.19.0' 'PyYAML==6.0.2'
  ;;
training)
  python3 -m venv --system-site-packages /opt/mwam
  /opt/hf-tools/bin/python scripts/memory_s1/portable/recovery.py pins --ready "$READY" \
    --kind training --output outputs/recovery_aws_v2/training-recorded-pins.txt
  /opt/mwam/bin/python -m pip install -r outputs/recovery_aws_v2/training-recorded-pins.txt
  /opt/mwam/bin/python - "$ROOT" <<'PY'
from pathlib import Path
import site
import sys
Path(site.getsitepackages()[0], "fastwam_source.pth").write_text(str(Path(sys.argv[1]) / "src") + "\n")
import torch
assert torch.__version__.startswith("2.10.0a0"), torch.__version__
assert torch.version.cuda == "13.0", torch.version.cuda
assert torch.cuda.device_count() == 2
print("Training Python:", sys.executable, "PyTorch:", torch.__version__, "CUDA:", torch.version.cuda)
PY
  /opt/mwam/bin/python -c 'import fastwam.memory_s1.train, fastwam.memory_s1.integration; print("S1 imports: OK")'
  ;;
simulator)
  if [[ ! -x /opt/miniforge/bin/conda ]]; then
    INSTALLER="/tmp/mwam-Miniforge3.sh"
    curl -fL --retry 3 -o "$INSTALLER" \
      https://github.com/conda-forge/miniforge/releases/download/25.3.1-0/Miniforge3-Linux-x86_64.sh
    mkdir -p outputs/recovery_aws_v2/environment
    sha256sum "$INSTALLER" > outputs/recovery_aws_v2/environment/miniforge-installer.sha256
    bash "$INSTALLER" -b -p /opt/miniforge
  fi
  if [[ ! -x /opt/rmbench-env/bin/python ]]; then
    /opt/hf-tools/bin/python scripts/memory_s1/portable/recovery.py conda-spec --ready "$READY" \
      --output outputs/recovery_aws_v2/simulator-saved-conda.txt
    if [[ -f outputs/recovery_aws_v2/simulator-saved-conda.txt ]]; then
      /opt/miniforge/bin/conda create -y -p /opt/rmbench-env --file outputs/recovery_aws_v2/simulator-saved-conda.txt
    else
      /opt/miniforge/bin/conda create -y -p /opt/rmbench-env -c conda-forge python=3.10 pip
      /opt/miniforge/bin/conda install -y -p /opt/rmbench-env -c nvidia cuda-toolkit=12.4.1
    fi
  fi
  export CUDA_HOME=/opt/rmbench-env CC=gcc-12 CXX=g++-12 TORCH_CUDA_ARCH_LIST=9.0 MAX_JOBS=8
  export PATH="/opt/rmbench-env/bin:$PATH"
  export LD_LIBRARY_PATH="/opt/rmbench-env/lib:/opt/rmbench-env/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
  PY=/opt/rmbench-env/bin/python
  "$PY" -m pip install 'torch==2.4.1' 'torchvision==0.19.1' --index-url https://download.pytorch.org/whl/cu124
  printf '%s\n' 'torch==2.4.1' 'torchvision==0.19.1' 'numpy<2' 'zarr<3' 'moviepy<2' \
    > outputs/recovery_aws_v2/simulator-constraints.txt
  /opt/hf-tools/bin/python scripts/memory_s1/portable/recovery.py pins --ready "$READY" \
    --kind simulator --output outputs/recovery_aws_v2/simulator-recorded-pins.txt
  # The actual fork requirements are restored before this operation.
  "$PY" -m pip install -c outputs/recovery_aws_v2/simulator-constraints.txt \
    -r resources/RMBench/scripts/requirements.txt -c outputs/recovery_aws_v2/simulator-recorded-pins.txt
  "$PY" -m pip install -c outputs/recovery_aws_v2/simulator-constraints.txt \
    -r outputs/recovery_aws_v2/simulator-recorded-pins.txt
  "$PY" -m pip install -c outputs/recovery_aws_v2/simulator-constraints.txt \
    'numpy<2' 'zarr<3' 'moviepy<2' PyYAML Pillow toppra 'setuptools==69.5.1' 'warp-lang==1.12.0' ninja
  if [[ ! -f resources/PyTorch3D/setup.py ]]; then
    git clone --branch v0.7.8 --depth 1 https://github.com/facebookresearch/pytorch3d.git resources/PyTorch3D
  fi
  if [[ ! -f resources/RMBench/envs/curobo/setup.py ]]; then
    echo 'The saved CuRobo source is missing. Restore its recorded commit before continuing.' >&2
    exit 2
  fi
  "$PY" -m pip install ./resources/PyTorch3D --no-build-isolation
  "$PY" -m pip install -e ./resources/RMBench/envs/curobo --no-build-isolation
  "$PY" - <<'PY'
import sys
import torch
import sapien, mplib, curobo
from pytorch3d import _C
assert sys.version_info[:2] == (3, 10)
assert torch.__version__.split("+")[0] == "2.4.1"
assert torch.version.cuda == "12.4"
assert torch.cuda.is_available()
print("Simulator imports: OK; extension architecture target: 9.0")
PY
  ;;
patches)
  /opt/rmbench-env/bin/python - "$READY" <<'PY'
from pathlib import Path
import hashlib
import shutil
import sys
import sapien, mplib
ready = Path(sys.argv[1])
modules = {"sapien": Path(sapien.__file__).parent, "mplib": Path(mplib.__file__).parent}
found = []
for path in ready.rglob("*.py"):
    for name, destination in modules.items():
        parts = path.parts
        if name in parts and any("patch" in part.lower() for part in parts):
            index = parts.index(name)
            relative = Path(*parts[index+1:])
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            found.append(str(target))
if not found:
    raise SystemExit("Saved simulator patches were not found; inspect the ready package rather than assuming an unpatched environment is equivalent.")
print("Restored saved simulator patch files:", len(found))
PY
  ;;
*) echo "Unknown environment operation: $MODE" >&2; exit 2 ;;
esac
