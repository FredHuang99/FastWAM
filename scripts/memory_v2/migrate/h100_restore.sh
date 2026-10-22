#!/usr/bin/env bash
# Inside mwam-h100. Steps, in order: system | download | code | env | verify | test | reference | simulator
# (`/opt/hf-tools/bin/hf auth login` once after `system`). Rerunning a step is safe.
set -euo pipefail
REPO=${HF_REPO:-hhyfred/memwam-h100-migration-v1}
HF=/mnt/hf
MIG=/workspace/FastWAM-memory2/outputs/migration_h100_v1
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
export PYTHONPATH=/workspace/FastWAM-memory2/src
step() { echo "[restore] $(date '+%F %T') $*"; }

hftools() {
  [ -x "$HFPY" ] || { python3 -m venv /opt/hf-tools; $HFPY -m pip install -q 'huggingface-hub==1.19.0' 'PyYAML==6.0.2'; }
}

download() {
  hftools
  step "download $REPO -> $HF"
  $HFPY - "$REPO" "$HF" <<'PY'
import sys
from huggingface_hub import snapshot_download
print(snapshot_download(repo_id=sys.argv[1], repo_type="model", local_dir=sys.argv[2], max_workers=16))
PY
}

code() {
  step "memory2 code into /workspace/FastWAM-memory2 (outputs/ untouched)"
  git config --global --add safe.directory /workspace/FastWAM-memory2
  cd /workspace/FastWAM-memory2
  [ -d .git ] || git init -q
  git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/FredHuang99/FastWAM.git
  git fetch -q origin memory2
  WANT=$(awk '/^memory2 HEAD/{print $3}' "$MIG/records/git_and_roots.txt")
  git checkout -q -f -B memory2 origin/memory2
  echo "HEAD $(git rev-parse HEAD) (A100 was ${WANT:-unknown}; newer is fine, the scripts are backward compatible)"
}

system() {
  step "system packages + /opt/hf-tools"
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --no-install-recommends \
    git curl ca-certificates zstd python3-venv build-essential gcc-12 g++-12 cmake ninja-build \
    libvulkan1 vulkan-tools libgl1 libglib2.0-0 libegl1 libx11-6 libxext6 libsm6 ffmpeg >/dev/null
  hftools
  $HFPY -c "import huggingface_hub; print('huggingface_hub', huggingface_hub.__version__)"
}

env_() {
  step "/opt/mwam venv on the image's torch (system site packages)"
  [ -x "$PY" ] || python3 -m venv --system-site-packages /opt/mwam
  $PY - "$MIG/records/mwam_venv_local.txt" "$MIG/h100_pins.txt" <<'PY'
import importlib.metadata as md, re, sys
system = {}
for d in md.distributions():
    system[re.sub(r"[-_.]+", "-", d.metadata["Name"]).lower()] = d.version
keep, skipped = [], []
for line in open(sys.argv[1]):
    line = line.strip()
    if not line or "==" not in line:
        continue
    name, version = line.split("==", 1)
    key = re.sub(r"[-_.]+", "-", name).lower()
    if key in system or key.startswith("fastwam") or "+" in version or key in ("pip", "setuptools", "wheel"):
        skipped.append(f"{line}  (image has {system.get(key, '-')})")
    else:
        keep.append(line)
open(sys.argv[2], "w").write("\n".join(keep) + "\n")
print(f"install {len(keep)} venv-only packages; keep the image's version for {len(skipped)}:")
print("\n".join("  " + s for s in skipped))
PY
  unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT
  PIP_CONFIG_FILE=/dev/null $PY -m pip install --no-deps -r "$MIG/h100_pins.txt"
  # transformers 4.49 needs huggingface-hub<1 and tokenizers<0.22 (the image has newer): take the A100 versions
  EXTRA=$(grep -i "^huggingface[-_]hub==\|^tokenizers==" "$MIG/records/mwam_freeze_all.txt" | tr '\n' ' ')
  [ -n "$EXTRA" ] && PIP_CONFIG_FILE=/dev/null $PY -m pip install --no-deps $EXTRA
  $PY -m pip check || echo "[restore] pip check reported the conflicts above (review; --no-deps install keeps the image's torch stack)"
  $PY -m pip install -q pytest
  $PY - <<'PY'
import sys, torch, numpy
print("python", sys.version.split()[0], "torch", torch.__version__, "cuda", torch.version.cuda, "numpy", numpy.__version__,
      "gpu", torch.cuda.get_device_name(0))
PY
}

verify() {
  hftools
  step "verify every file (size + sha256)"
  $HFPY /workspace/FastWAM-memory2/scripts/memory_v2/migrate/manifest.py verify --manifest $HF/MANIFEST.json --root $HF
}

test_() {
  cd /workspace/FastWAM-memory2
  step "pytest"
  $PY -m pytest -q /workspace/FastWAM-memory2/src/fastwam/memory_v2/tests
  step "dense identity + software drift vs the dense receipt"
  $PY - <<'PY'
from fastwam.memory_v2 import dense
spec = dense.DenseSpec()
common, identity = dense.bind(spec)
print("dense identity OK:", identity)
print("software drift:", dense.SOFTWARE_DRIFT.get(str(spec.output.resolve())) or "none")
PY
}

reference() {
  cd /workspace/FastWAM-memory2
  step "reference evaluate on H100 (same 16 windows as the A100 reference)"
  $PY -m fastwam.memory_v2.train_v2 evaluate --config configs/memory_v2/train_v2_A.yaml \
    --checkpoint /workspace/FastWAM-memory2/outputs/memory_v2/v2_A_memory_only/checkpoints/update_001340.pt \
    --windows 16 --output "$MIG/reference_h100"
  $HFPY /workspace/FastWAM-memory2/scripts/memory_v2/migrate/manifest.py compare \
    "$MIG/reference_a100/update_001340.json" "$MIG/reference_h100/update_001340.json"
}

simulator() {
  # Closed-loop RMBench environment, H100 recipe of the S1 runbook (sm90, torch 2.4.1 cu124),
  # ready package from the existing backup repo.
  cd /workspace/FastWAM
  export FW_ROOT=/workspace/FastWAM CONFIG=configs/memory_s1/s1_variable_t_h100.yaml
  export RECOVERY_ROOT=/workspace/FastWAM/outputs/recovery_aws_h100 READY_DIR=/workspace/FastWAM/outputs/recovery_aws_h100/restored
  hftools
  step "ready package from hhyfred/fastwam-memory-s1-backup"
  $HFPY scripts/memory_s1/portable/recovery.py download-ready --repo hhyfred/fastwam-memory-s1-backup \
    --run-id memory_s1_variable_t_seed17_v2 --output "$RECOVERY_ROOT"
  # The A100 copy of RMBench has no scripts/requirements.txt; the recorded pins (ready package) carry the
  # exact versions, so a placeholder that only repeats the numpy<2 constraint is enough.
  if [ ! -f resources/RMBench/scripts/requirements.txt ]; then
    echo 'numpy<2' > resources/RMBench/scripts/requirements.txt
    echo "[restore] created placeholder resources/RMBench/scripts/requirements.txt (pins come from the ready package)"
  fi
  step "simulator env (conda + torch 2.4.1 cu124 + curobo/pytorch3d for sm90)"
  bash scripts/memory_s1/portable/install_environments.sh simulator
  bash scripts/memory_s1/portable/install_environments.sh patches
  $HFPY -u scripts/memory_s1/portable/recovery.py restore-simulator --root "$FW_ROOT" --ready "$READY_DIR" --mode current
  bash scripts/memory_s1/portable/install_environments.sh render
}

simulator_finish() {
  # Resume after `simulator` failed at the CuRobo editable install: setuptools-scm cannot see a version in the
  # .git-less source, and the per-distribution PRETEND variable was not picked up. Set the generic one as well,
  # only for this single pip call, then run the remaining steps of `simulator`.
  cd /workspace/FastWAM
  export FW_ROOT=/workspace/FastWAM CONFIG=configs/memory_s1/s1_variable_t_h100.yaml
  export RECOVERY_ROOT=/workspace/FastWAM/outputs/recovery_aws_h100 READY_DIR=/workspace/FastWAM/outputs/recovery_aws_h100/restored
  # Toolchain exactly as Codex's working H100 build (prepare_fused_env.sh): conda CUDA headers/libs live under
  # targets/x86_64-linux, so CPATH/LIBRARY_PATH must point there; host compiler pinned to gcc-12.
  N=/opt/rmbench-env
  export CUDA_HOME=$N CC=/usr/bin/gcc-12 CXX=/usr/bin/g++-12 CUDAHOSTCXX=/usr/bin/g++-12
  export TORCH_CUDA_ARCH_LIST=9.0 MAX_JOBS=${MAX_JOBS:-6} OMP_NUM_THREADS=4
  export PATH="$N/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  export LD_LIBRARY_PATH="$N/lib:$N/targets/x86_64-linux/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64"
  export CPATH="$N/include:$N/targets/x86_64-linux/include"
  export LIBRARY_PATH="$N/lib:$N/targets/x86_64-linux/lib:$N/targets/x86_64-linux/lib/stubs"
  unset C_INCLUDE_PATH CPLUS_INCLUDE_PATH PYTHONPATH PYTHONHOME VIRTUAL_ENV
  unset PIP_CONSTRAINT PIP_BUILD_CONSTRAINT UV_CONSTRAINT
  step "toolchain: nvcc $($N/bin/nvcc --version | grep -o 'release [0-9.]*'); $(/usr/bin/gcc-12 --version | head -1)"
  for h in cublas_v2.h cusparse.h cuda_runtime.h; do
    [ -f "$N/include/$h" ] || [ -f "$N/targets/x86_64-linux/include/$h" ] \
      || { echo "[restore] CUDA development header $h missing in $N (include/ and targets/x86_64-linux/include/)"; exit 1; }
  done
  hftools
  V=$(/opt/rmbench-env/bin/python -c "
import json, sys
r = json.load(open('$RECOVERY_ROOT/simulator-recorded-pins.sources.json')).get('source_installed', {})
v = {r[n] for n in ('nvidia-curobo', 'curobo') if n in r}
sys.exit('no recorded CuRobo version') if len(v) != 1 else print(v.pop())")
  step "CuRobo $V editable install (sm90, MAX_JOBS=$MAX_JOBS)"
  BUILDLOG=/mnt/tmp/curobo_build.log
  if ! SETUPTOOLS_SCM_PRETEND_VERSION="$V" SETUPTOOLS_SCM_PRETEND_VERSION_FOR_NVIDIA_CUROBO="$V" \
      $N/bin/python -m pip install -v -e ./resources/RMBench/envs/curobo --no-build-isolation > "$BUILDLOG" 2>&1; then
    echo "[restore] CuRobo build FAILED; full log $BUILDLOG; first compiler errors:"
    grep -n -m 20 -E "error:|error |FAILED:|fatal" "$BUILDLOG" || tail -n 60 "$BUILDLOG"
    exit 1
  fi
  tail -n 3 "$BUILDLOG"
  step "simulator imports"
  /opt/rmbench-env/bin/python - <<'PY'
import sys
import torch
import sapien, mplib, curobo
from pytorch3d import _C
assert sys.version_info[:2] == (3, 10)
assert torch.__version__.split("+")[0] == "2.4.1" and torch.version.cuda == "12.4" and torch.cuda.is_available()
print("Simulator imports: OK", torch.__version__, torch.cuda.get_device_name(0))
PY
  step "saved simulator patches"
  bash scripts/memory_s1/portable/install_environments.sh patches
  step "restore simulator sources"
  $HFPY -u scripts/memory_s1/portable/recovery.py restore-simulator --root "$FW_ROOT" --ready "$READY_DIR" --mode current
  step "offscreen render probe"
  bash scripts/memory_s1/portable/install_environments.sh render
  step "simulator finished"
}

case "${1:?system|download|code|env|verify|test|reference|simulator|simulator_finish}" in
  system) system ;; download) download ;; code) code ;; env) env_ ;; verify) verify ;; test) test_ ;; reference) reference ;;
  simulator) simulator ;; simulator_finish) simulator_finish ;;
  *) echo "unknown step $1"; exit 2 ;;
esac
