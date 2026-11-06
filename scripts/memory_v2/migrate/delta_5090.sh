#!/usr/bin/env bash
# A100 container (root@6e4b37a15066): A100 -> 5090 delta package on HF. Steps: build | stage | upload | all.
#   build  : delta_5090.py build (file list + weights-only copies of the large LATEST checkpoints)
#   stage  : manifest.py stage (sha256 + hardlink tree; no extra disk except the slim copies)
#   upload : manifest.py upload to the private repo (batched, resumable; needs `hf auth login` in this container)
# The script writes its own log: /workspace/FastWAM-memory2/outputs/migration_5090_v1/DELTA_RUN.log (append);
# the last line of each run says the step's exit code. Rerunning is safe (slim copies, hashes, uploaded files reused).
set -euo pipefail
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
MIG=/workspace/FastWAM-memory2/outputs/migration_5090_v1
REPO=${HF_REPO:-hhyfred/memwam-5090-delta-v1}
NAME=MANIFEST_5090_DELTA.json
HERE=/workspace/FastWAM-memory2/scripts/memory_v2/migrate
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
mkdir -p "$MIG"
exec > >(tee -a "$MIG/DELTA_RUN.log") 2>&1
STEP=${1:?build|stage|upload|all}
trap 'rc=$?; echo "[delta] $(date "+%F %T") step $STEP finished, exit code $rc"' EXIT
hftools() { [ -x "$HFPY" ] || { python3 -m venv /opt/hf-tools; $HFPY -m pip install -q 'huggingface-hub==1.19.0' 'PyYAML==6.0.2'; }; }
build() { $PY "$HERE/delta_5090.py" build; }
stage() { hftools; $HFPY "$HERE/manifest.py" stage --mig "$MIG" --name "$NAME"; }
upload() { hftools; $HFPY "$HERE/manifest.py" upload --mig "$MIG" --name "$NAME" --repo "$REPO"; }
case "$STEP" in
  build) build ;; stage) stage ;; upload) upload ;;
  all) build; stage; upload ;;
  *) echo "unknown step $STEP"; exit 2 ;;
esac
