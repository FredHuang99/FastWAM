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
  cd /workspace/FastWAM-memory2
  [ -d .git ] || git init -q
  git remote get-url origin >/dev/null 2>&1 || git remote add origin https://github.com/FredHuang99/FastWAM.git
  git fetch -q origin memory2
  WANT=$(awk '/^memory2 HEAD/{print $3}' "$MIG/records/git_and_roots.txt")
  git checkout -q -f -B memory2 origin/memory2
  echo "HEAD $(git rev-parse HEAD) (A100 was ${WANT:-unknown}; newer is fine, the scripts are backward compatible)"
  git config --global --add safe.directory /workspace/FastWAM-memory2
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
  step "simulator env (conda + torch 2.4.1 cu124 + curobo/pytorch3d for sm90)"
  bash scripts/memory_s1/portable/install_environments.sh simulator
  bash scripts/memory_s1/portable/install_environments.sh patches
  $HFPY -u scripts/memory_s1/portable/recovery.py restore-simulator --root "$FW_ROOT" --ready "$READY_DIR" --mode current
  bash scripts/memory_s1/portable/install_environments.sh render
}

case "${1:?system|download|code|env|verify|test|reference|simulator}" in
  system) system ;; download) download ;; code) code ;; env) env_ ;; verify) verify ;; test) test_ ;; reference) reference ;;
  simulator) simulator ;;
  *) echo "unknown step $1"; exit 2 ;;
esac
