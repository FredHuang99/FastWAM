#!/usr/bin/env bash
set -euo pipefail
ROOT="${FW_ROOT:-/workspace/FastWAM}"
MODE="${1:?Choose system, hf, training, simulator, patches or render}"
cd "$ROOT"
CONFIG="${CONFIG:-configs/memory_s1/s1_variable_t_h200.yaml}"
mapfile -t PROFILE < <(python3 - "$CONFIG" "$ROOT" <<'PY'
import sys
from pathlib import Path
import yaml
cfg = yaml.safe_load(Path(sys.argv[1]).read_text())
profile = cfg.get("recovery", {})
print(profile.get("expected_world_size", 2))
print(Path(sys.argv[2]) / profile.get("output", "outputs/recovery_aws_v2"))
print(Path(sys.argv[2]) / profile.get("ready_directory", "outputs/recovery_aws_v2/restored"))
print(profile.get("cuda_arch", "9.0"))
print(profile.get("max_jobs", 4))
PY
)
EXPECTED_GPUS="${PROFILE[0]}"
export RECOVERY_ROOT="${RECOVERY_ROOT:-${PROFILE[1]}}"
READY="${READY_DIR:-${PROFILE[2]}}"
mkdir -p "$RECOVERY_ROOT"
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
    --kind training --output "$RECOVERY_ROOT/training-recorded-pins.txt"
  /opt/mwam/bin/python -m pip install -r "$RECOVERY_ROOT/training-recorded-pins.txt"
  /opt/mwam/bin/python - "$ROOT" "$EXPECTED_GPUS" <<'PY'
from pathlib import Path
import site
import sys
Path(site.getsitepackages()[0], "fastwam_source.pth").write_text(str(Path(sys.argv[1]) / "src") + "\n")
import torch
assert torch.__version__.startswith("2.10.0a0"), torch.__version__
assert torch.version.cuda == "13.0", torch.version.cuda
assert torch.cuda.device_count() == int(sys.argv[2]), torch.cuda.device_count()
print("Training Python:", sys.executable, "PyTorch:", torch.__version__, "CUDA:", torch.version.cuda)
PY
  /opt/mwam/bin/python -c 'import fastwam.memory_s1.train, fastwam.memory_s1.integration; print("S1 imports: OK")'
  ;;
simulator)
  if [[ ! -x /opt/miniforge/bin/conda ]]; then
    INSTALLER="/tmp/mwam-Miniforge3.sh"
    curl -fL --retry 3 -o "$INSTALLER" \
      https://github.com/conda-forge/miniforge/releases/download/25.3.1-0/Miniforge3-Linux-x86_64.sh
    mkdir -p "$RECOVERY_ROOT/environment"
    sha256sum "$INSTALLER" > "$RECOVERY_ROOT/environment/miniforge-installer.sha256"
    bash "$INSTALLER" -b -u -p /opt/miniforge
  fi
  if [[ ! -x /opt/rmbench-env/bin/python ]]; then
    /opt/hf-tools/bin/python scripts/memory_s1/portable/recovery.py conda-spec --ready "$READY" \
      --output "$RECOVERY_ROOT/simulator-saved-conda.txt"
    if [[ -f "$RECOVERY_ROOT/simulator-saved-conda.txt" ]]; then
      /opt/miniforge/bin/conda create -y -p /opt/rmbench-env --file "$RECOVERY_ROOT/simulator-saved-conda.txt"
    else
      /opt/miniforge/bin/conda create -y -p /opt/rmbench-env -c conda-forge python=3.10 pip
      /opt/miniforge/bin/conda install -y -p /opt/rmbench-env -c nvidia cuda-toolkit=12.4.1
    fi
  fi
  export CUDA_HOME=/opt/rmbench-env CC=gcc-12 CXX=g++-12 TORCH_CUDA_ARCH_LIST="${PROFILE[3]}" MAX_JOBS="${PROFILE[4]}"
  export PATH="/opt/rmbench-env/bin:$PATH"
  export LD_LIBRARY_PATH="/opt/rmbench-env/lib:/opt/rmbench-env/targets/x86_64-linux/lib:${LD_LIBRARY_PATH:-}"
  PY=/opt/rmbench-env/bin/python
  "$PY" -m pip install 'torch==2.4.1' 'torchvision==0.19.1' --index-url https://download.pytorch.org/whl/cu124
  printf '%s\n' 'torch==2.4.1' 'torchvision==0.19.1' 'numpy<2' 'zarr<3' 'moviepy<2' \
    > "$RECOVERY_ROOT/simulator-constraints.txt"
  /opt/hf-tools/bin/python scripts/memory_s1/portable/recovery.py pins --ready "$READY" \
    --kind simulator --output "$RECOVERY_ROOT/simulator-recorded-pins.txt"
  # The actual fork requirements are restored before this operation.
  "$PY" -m pip install -c "$RECOVERY_ROOT/simulator-constraints.txt" \
    -r resources/RMBench/scripts/requirements.txt -c "$RECOVERY_ROOT/simulator-recorded-pins.txt"
  "$PY" -m pip install -c "$RECOVERY_ROOT/simulator-constraints.txt" \
    -r "$RECOVERY_ROOT/simulator-recorded-pins.txt"
  "$PY" -m pip install -c "$RECOVERY_ROOT/simulator-constraints.txt" \
    'numpy<2' 'zarr<3' 'moviepy<2' PyYAML Pillow toppra 'setuptools==69.5.1' 'warp-lang==1.12.0' ninja
  if [[ ! -f resources/PyTorch3D/setup.py ]]; then
    git clone --branch v0.7.8 --depth 1 https://github.com/facebookresearch/pytorch3d.git resources/PyTorch3D
  fi
  if [[ ! -f resources/RMBench/envs/curobo/setup.py ]]; then
    echo 'The saved CuRobo source is missing. Restore its recorded commit before continuing.' >&2
    exit 2
  fi
  # Source archives omit .git; recover the distribution version from saved
  # environment records rather than asking setuptools-scm to infer it.
  CUROBO_VERSION="$("$PY" - <<'PY'
import json
from pathlib import Path
from packaging.version import Version

import os
record = json.loads((Path(os.environ["RECOVERY_ROOT"]) / "simulator-recorded-pins.sources.json").read_text())
packages = record.get("source_installed", {})
versions = {packages[name] for name in ("nvidia-curobo", "curobo") if name in packages}
if len(versions) != 1:
    raise SystemExit("Missing or conflicting recorded CuRobo versions; regenerate pins using the current recovery.py.")
version = versions.pop()
Version(version)
print(version)
PY
  )"
  printf '[build] CuRobo version from saved environment: %s; GPU architecture: %s\n' "$CUROBO_VERSION" "$TORCH_CUDA_ARCH_LIST"
  "$PY" -m pip install ./resources/PyTorch3D --no-build-isolation
  SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NVIDIA_CUROBO="$CUROBO_VERSION" \
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
render)
  /opt/rmbench-env/bin/python - <<'PY'
import importlib.metadata
import json
import os
from pathlib import Path
import numpy as np
import sapien
from PIL import Image

# The production simulator uses SAPIEN 3 and selects its renderer explicitly.
version = importlib.metadata.version("sapien")
sapien.render.set_global_config(offscreen_only=True)
renderer = sapien.render.RenderSystem(device="cuda:0")
scene = sapien.Scene([sapien.physx.PhysxCpuSystem(), renderer])
camera = scene.add_camera("recovery_probe", 64, 64, 1.0, 0.1, 10)
scene.step()
scene.update_render()
camera.take_picture()
pixels = camera.get_picture("Color")
assert pixels.shape == (64, 64, 4) and np.isfinite(pixels).all()
output = Path(os.environ["RECOVERY_ROOT"]) / "environment"
output.mkdir(parents=True, exist_ok=True)
Image.fromarray((np.clip(pixels[..., :3], 0, 1) * 255).astype(np.uint8)).save(output / "render_probe.png")
(output / "render_probe.json").write_text(json.dumps({
    "passed": True, "sapien_version": version,
    "camera_api": "get_picture", "requested_render_device": "cuda:0",
    "render_device": str(renderer.device), "rgba_shape": list(pixels.shape),
    "scope": "offscreen_camera_readback_not_RMBench_task_admission",
}, indent=2), encoding="utf-8")
print("SAPIEN:", version, "Render device:", renderer.device)
print("Simulator offscreen render: OK", pixels.shape, "API=get_picture")
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
