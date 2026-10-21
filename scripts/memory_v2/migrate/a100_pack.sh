#!/usr/bin/env bash
# A100 container (root@6e4b37a15066): records -> traces -> manifest -> stage -> HF upload.
#   bash a100_pack.sh records|trace|build|stage|upload|local     (local = records+trace+build+stage)
# Env: CUDA_VISIBLE_DEVICES (one free GPU, for trace), HF_REPO, SKIP (e.g. "features simulator"), EXCLUDE (fnmatch).
set -euo pipefail
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
MIG=/workspace/FastWAM-memory2/outputs/migration_h100_v1
HERE=/workspace/FastWAM-memory2/scripts/memory_v2/migrate
CFG=configs/memory_v2/train_v2_A.yaml
O=/workspace/FastWAM-memory2/outputs/memory_v2
REPO=${HF_REPO:-hhyfred/memwam-h100-migration-v1}
mkdir -p "$MIG/records" "$MIG/traces"
step() { echo "[pack] $(date '+%F %T') $*"; }

records() {
  step "records -> $MIG/records"
  R=$MIG/records
  $PY - > "$R/runtime.json" <<'PY'
import json, platform, subprocess, sys
import numpy, torch
out = {"python": sys.version, "executable": sys.executable, "prefix": sys.prefix, "platform": platform.platform(),
       "torch": torch.__version__, "cuda": torch.version.cuda, "cudnn": torch.backends.cudnn.version(),
       "numpy": numpy.__version__}
try:
    out["nvidia_smi"] = subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
                                       capture_output=True, text=True).stdout.strip().splitlines()
except OSError:
    pass
print(json.dumps(out, indent=1))
PY
  $PY -m pip freeze --all > "$R/mwam_freeze_all.txt"
  $PY - > "$R/mwam_venv_local.txt" <<'PY'
import importlib.metadata as md, os, sys
prefix = os.path.realpath(sys.prefix)
rows = set()
for d in md.distributions():
    location = os.path.realpath(str(d.locate_file("")))
    if location.startswith(prefix + os.sep):
        rows.add(f"{d.metadata['Name']}=={d.version}")
print("\n".join(sorted(rows, key=str.lower)))
PY
  /usr/bin/python3 -m pip list --format=freeze > "$R/system_freeze.txt" 2>/dev/null || true
  for env in /opt/rmbench-env /opt/rmbench-a100-env; do
    if [ -x "$env/bin/python" ]; then
      n=$(basename "$env")
      [ -x /opt/miniforge/bin/conda ] && /opt/miniforge/bin/conda list -p "$env" --explicit > "$R/${n}_conda_explicit.txt" || true
      "$env/bin/python" -m pip freeze --all > "$R/${n}_pip_freeze.txt" || true
    fi
  done
  {
    echo "memory2 HEAD $(git -C /workspace/FastWAM-memory2 rev-parse HEAD)"
    git -C /workspace/FastWAM-memory2 status --short | head -50
    if [ -d /workspace/FastWAM/.git ]; then
      echo "FastWAM HEAD $(git -C /workspace/FastWAM rev-parse HEAD) branch $(git -C /workspace/FastWAM rev-parse --abbrev-ref HEAD)"
      git -C /workspace/FastWAM status --short | head -50
    fi
    for p in /workspace/FastWAM /workspace/FastWAM-memory2 /restore-tmp /restore-tmp/dense_joint_v1; do echo "realpath $p -> $(readlink -f "$p")"; done
  } > "$R/git_and_roots.txt"
  df -hT /workspace/FastWAM /workspace/FastWAM-memory2 /restore-tmp > "$R/df.txt" 2>&1 || true
  ls "$R"
}

trace() {
  : "${CUDA_VISIBLE_DEVICES:?set CUDA_VISIBLE_DEVICES to one free GPU (UUID)}"
  T="$PY $HERE/trace_run.py"
  step "trace 1/3 evaluate Ours (16 windows) = A100 reference"
  $T --out "$MIG/traces/evaluate.json" -m fastwam.memory_v2.train_v2 evaluate --config $CFG \
    --checkpoint $O/v2_A_memory_only/checkpoints/update_001340.pt --windows 16 --output "$MIG/reference_a100"
  step "trace 2/3 pr (4 pairs)"
  $T --out "$MIG/traces/pr.json" -m fastwam.memory_v2.train_v2 pr --config $CFG \
    --checkpoint $O/v2_A_cf/checkpoints/update_001340.pt --pairs $O/pairs/pairs_v1.json --limit 4 --output "$MIG/probe_pr"
  step "trace 3/3 train --dry-run 2 with pairs"
  $T --out "$MIG/traces/train.json" -m fastwam.memory_v2.train_v2 train --config $CFG --dry-run 2 \
    --set name=probe --set output="$MIG/probe_train" --set pairs.file=$O/pairs/pairs_v1.json --set pairs.weight=0.5
}

build() {
  [ -x "$HFPY" ] || { step "creating /opt/hf-tools"; python3 -m venv /opt/hf-tools; $HFPY -m pip install -q 'huggingface-hub==1.19.0' 'PyYAML==6.0.2'; }
  step "build manifest (skip: ${SKIP:-none})"
  # shellcheck disable=SC2086
  $HFPY $HERE/manifest.py build --mig "$MIG" ${SKIP:+--skip $SKIP} ${EXCLUDE:+--exclude $EXCLUDE}
}

stage()  { step "stage"; $HFPY $HERE/manifest.py stage --mig "$MIG" --workers 8; }
upload() { step "upload -> $REPO"; $HFPY $HERE/manifest.py upload --mig "$MIG" --repo "$REPO" --workers 8; }

case "${1:?records|trace|build|stage|upload|local}" in
  records) records ;; trace) trace ;; build) build ;; stage) stage ;; upload) upload ;;
  local) records; trace; build; stage; step "local done; check the size table above, then: bash $0 upload" ;;
  *) echo "unknown step $1"; exit 2 ;;
esac
