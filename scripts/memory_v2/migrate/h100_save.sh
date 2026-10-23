#!/usr/bin/env bash
# Inside mwam-h100, before the instance goes away:
#   1. stop the GPU queue; an unfinished training run saves a resumable checkpoint (STOP.json)
#   2. tar the built environments (/opt/rmbench-env with CuRobo/PyTorch3D for sm90, /opt/mwam)
#   3. complete manifest = previous payload + H100 results; stage; incremental upload to the same HF repo
# Rerunning resumes (hashes cached, uploaded files skipped). ENVS=0 skips the environment tarballs.
set -euo pipefail
trap 'echo "[save] FAILED (exit $?) at line $LINENO: $BASH_COMMAND" >&2' ERR
REPO=${HF_REPO:-hhyfred/memwam-h100-migration-v1}
MIG=/mnt/tmp/save_h100
HERE=/workspace/FastWAM-memory2/scripts/memory_v2/migrate
HFPY=/opt/hf-tools/bin/python
step() { echo "[save] $(date '+%F %T') $*"; }
mkdir -p "$MIG/envs" "$MIG/records"

step "stop queues and running jobs"
pkill -f "jobs/h100_queue_2" || true
for pid in $(pgrep -f "fastwam.memory_v2.train_v2 train" || true); do
  out=$(tr '\0' '\n' < /proc/$pid/cmdline | sed -n 's/^output=//p' | tail -1)
  [ -n "$out" ] && { echo '{"reason": "H100 save"}' > "$out/STOP.json"; step "STOP.json -> $out (pid $pid)"; }
done
for i in $(seq 1 60); do pgrep -f "fastwam.memory_v2.train_v2 train" >/dev/null || break; sleep 10; done
pkill -f "fastwam.memory_v2.train_v2" || true          # unfinished evaluate/pr runs: results would be partial
nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader || true

step "environment records"
/opt/mwam/bin/python -m pip freeze --all > "$MIG/records/h100_mwam_freeze.txt" 2>/dev/null || true
/opt/rmbench-env/bin/python -m pip freeze --all > "$MIG/records/h100_rmbench_pip_freeze.txt" 2>/dev/null || true
/opt/miniforge/bin/conda list -p /opt/rmbench-env --explicit > "$MIG/records/h100_rmbench_conda_explicit.txt" 2>/dev/null || true
git -C /workspace/FastWAM-memory2 rev-parse HEAD > "$MIG/records/h100_memory2_head.txt"
cp "$MIG"/records/*.txt /workspace/FastWAM-memory2/outputs/migration_h100_v1/records/ 2>/dev/null || true

TARS=()
if [ "${ENVS:-1}" = 1 ]; then
  for env in rmbench-env mwam; do
    t="$MIG/envs/$env.tar.zst"
    if [ ! -s "$t" ]; then
      step "tar /opt/$env -> $t"
      tar -C /opt -cf - --exclude='__pycache__' "$env" | zstd -T0 -3 -q -o "$t.partial"
      mv "$t.partial" "$t"
    fi
    TARS+=("$t")
  done
  ls -la "$MIG/envs"
fi

step "manifest (previous payload + H100 results)"
$HFPY $HERE/h100_save.py --mig "$MIG" --old /mnt/hf/MANIFEST.json ${TARS[@]:+--env-tar "${TARS[@]}"}
step "stage"
$HFPY $HERE/manifest.py stage --mig "$MIG" --workers 16
step "upload -> $REPO (only new/changed files travel)"
$HFPY $HERE/manifest.py upload --mig "$MIG" --repo "$REPO" --workers 16
step "all done"
