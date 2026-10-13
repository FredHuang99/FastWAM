#!/usr/bin/env bash
# Independent A100 setup. No H100 diagnostic, evaluation, or training is launched.
set -euo pipefail
export FW_ROOT="${FW_ROOT:-/workspace/FastWAM}"
cd "$FW_ROOT"
export CONFIG="$FW_ROOT/configs/memory_s1/recovery_a100.yaml"
export RECOVERY_ROOT="$FW_ROOT/outputs/recovery_aws_a100_v1"
export READY_DIR="$RECOVERY_ROOT/restored"
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 CUDA_DEVICE_ORDER=PCI_BUS_ID
export PYTHONUNBUFFERED=1 CUBLAS_WORKSPACE_CONFIG=:4096:8
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export HF_HOME="$FW_ROOT/.cache/huggingface_a100" TMPDIR="$RECOVERY_ROOT/tmp"
export TORCH_EXTENSIONS_DIR="$FW_ROOT/outputs/fused_environment_a100_v1/torch_extensions_torch260_cu126_sm80"
unset CUDA_LAUNCH_BLOCKING HF_HUB_OFFLINE TRANSFORMERS_OFFLINE PYTHONPATH PYTHONHOME VIRTUAL_ENV CONDA_PREFIX
mkdir -p "$RECOVERY_ROOT/launches" "$TMPDIR" "$HF_HOME"
HELPER="$FW_ROOT/scripts/memory_s1/portable/a100/a100_migration.py"
ACTION="${1:-status}"
case "$ACTION" in
  status|stop)
    exec python3 "$HELPER" "$ACTION" --root "$FW_ROOT" ;;
  wait|watch)
    test -f "$RECOVERY_ROOT/latest_log.txt"
    log="$(cat "$RECOVERY_ROOT/latest_log.txt")"
    if [[ "$ACTION" == watch ]]; then exec tail -n 60 -F "$log"; fi
    while [[ ! -f "${log%.log}.exit" ]]; do
      python3 "$HELPER" status --root "$FW_ROOT"
      sleep 10
      if ! flock -n "$RECOVERY_ROOT/job.lock" true; then continue; fi
      [[ -f "${log%.log}.exit" ]] || { echo "Job ended without exit receipt; inspect $log"; exit 1; }
    done
    tail -n 60 "$log"
    code="$(cat "${log%.log}.exit")"
    printf 'Exit code: %s\n' "$code"
    exit "$code" ;;
  system|hf) command=(bash scripts/memory_s1/portable/install_environments.sh "$ACTION") ;;
  inventory) command=(/opt/hf-tools/bin/python -u scripts/memory_s1/portable/recovery.py inventory --output "$RECOVERY_ROOT/inventory") ;;
  fetch|payloads|restore) command=(/opt/hf-tools/bin/python -u "$HELPER" "$ACTION" --root "$FW_ROOT") ;;
  patch-sources) command=(/opt/hf-tools/bin/python -u "$HELPER" restore --root "$FW_ROOT" --overlay-sources) ;;
  resources)
    command=(/opt/hf-tools/bin/python -u scripts/memory_s1/portable/recovery.py resource-download --config "$CONFIG" --ready "$READY_DIR" --models --data --assets) ;;
  training)
    # Use the actual exported application's pip inventory, not a stale ready environment.
    export READY_DIR="$RECOVERY_ROOT/migration"
    command=(bash scripts/memory_s1/portable/install_environments.sh training) ;;
  references)
    command=(/opt/mwam/bin/python -u -m fastwam.memory_s1.integration restore-reference --config "$CONFIG") ;;
  simulator) command=(bash scripts/memory_s1/portable/a100/prepare.sh) ;;
  devices)
    test -f "$FW_ROOT/outputs/fused_environment_a100_v1/COMPLETE.json"
    command=(/opt/hf-tools/bin/python -u "$HELPER" devices --root "$FW_ROOT") ;;
  nccl)
    command=(/opt/mwam/bin/torchrun --standalone --nnodes=1 --nproc_per_node=8 "$HELPER" nccl --root "$FW_ROOT") ;;
  cache)
    test -f "$RECOVERY_ROOT/DEVICES_COMPLETE.json"
    test -f "$RECOVERY_ROOT/NCCL_COMPLETE.json"
    # dense.cache itself verifies a matching local pilot report before any encoding.
    command=(/opt/mwam/bin/torchrun --standalone --nnodes=1 --nproc_per_node=8 -m fastwam.memory_s1.dense cache --config "$CONFIG") ;;
  *) echo 'Usage: launch.sh system|hf|inventory|fetch|payloads|restore|resources|patch-sources|training|references|simulator|devices|nccl|cache|status|wait|watch|stop'; exit 2 ;;
esac
exec 9>"$RECOVERY_ROOT/job.lock"
flock -n 9 || { echo 'Another A100 setup stage is active; wait first.'; exit 1; }
LOG="$RECOVERY_ROOT/launches/${ACTION}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
printf '%q ' "${command[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
FW_A100_EXIT="${LOG%.log}.exit" nohup setsid bash -c '
  trap '\''printf "143\n" > "$FW_A100_EXIT"; exit 143'\'' TERM
  "$@"
  code=$?
  printf "%s\n" "$code" > "$FW_A100_EXIT"
  exit "$code"
' a100-stage "${command[@]}" > "$LOG" 2>&1 < /dev/null &
pid=$!
python3 "$HELPER" register --root "$FW_ROOT" --pid "$pid" --log "$LOG"
printf '%s\n' "$LOG" > "$RECOVERY_ROOT/latest_log.txt"
printf 'Stage=%s\nPID=%s\nLog=%s\nExit=%s\n' "$ACTION" "$pid" "$LOG" "${LOG%.log}.exit"
