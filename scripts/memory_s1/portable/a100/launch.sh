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
previous_hf_home="${HF_HOME:-}"
export HF_HOME="$FW_ROOT/.cache/huggingface_a100" TMPDIR="$RECOVERY_ROOT/tmp"
if [[ -z "${HF_TOKEN_PATH:-}" || ! -f "$HF_TOKEN_PATH" ]]; then
  for login_home in "$HF_HOME" "$previous_hf_home" "$FW_ROOT/.cache/huggingface" "${XDG_CACHE_HOME:-$HOME/.cache}/huggingface"; do
    if [[ -n "$login_home" && -f "$login_home/token" ]]; then export HF_TOKEN_PATH="$login_home/token"; break; fi
  done
fi
export TORCH_EXTENSIONS_DIR="$FW_ROOT/outputs/fused_environment_a100_v1/torch_extensions_torch260_cu126_sm80"
unset CUDA_LAUNCH_BLOCKING HF_HUB_OFFLINE TRANSFORMERS_OFFLINE PYTHONPATH PYTHONHOME VIRTUAL_ENV CONDA_PREFIX
mkdir -p "$RECOVERY_ROOT/launches" "$TMPDIR" "$HF_HOME"
HELPER="$FW_ROOT/scripts/memory_s1/portable/a100/a100_migration.py"
ACTION="${1:-status}"
resume=()
if [[ "$ACTION" == resume ]]; then ACTION="${2:?Usage: launch.sh resume STAGE}"; resume=(--resume); fi
configure_a100_nccl() {
  # The eight-GPU single-node profile passed on this A100 host. Keep it local
  # to NCCL/cache launches; simulator compilation and H100 keep their own libs.
  local variable
  while IFS= read -r variable; do
    case "$variable" in
      NCCL_*|UCX_*|OMPI_*|PMIX_*|UCC_*|HCOLL_*|FI_*) unset "$variable" ;;
    esac
  done < <(compgen -e)
  unset LD_PRELOAD CUDA_HOME CUDA_PATH MASTER_ADDR MASTER_PORT RANK LOCAL_RANK WORLD_SIZE
  export LD_LIBRARY_PATH=/usr/local/nvidia/lib:/usr/local/nvidia/lib64:/usr/local/cuda/lib64:/usr/local/lib
  export PYTHONFAULTHANDLER=1 TORCH_SHOW_CPP_STACKTRACES=1
  export NCCL_NET_PLUGIN=none NCCL_TUNER_PLUGIN=none NCCL_PROFILER_PLUGIN=none NCCL_ENV_PLUGIN=none
  export NCCL_IB_DISABLE=1 NCCL_NET=Socket NCCL_SOCKET_IFNAME='=lo' NCCL_SOCKET_FAMILY=AF_INET
  export NCCL_CUMEM_HOST_ENABLE=0
  export NCCL_DEBUG=INFO NCCL_DEBUG_SUBSYS=INIT,ENV,GRAPH,NET,P2P,SHM
  export NCCL_DEBUG_FILE="${LOG%.log}.nccl.%h.%p.log"
  export FW_A100_NCCL_PROFILE=a100-single-node-nccl-v1
  export FW_A100_NCCL_ENVIRONMENT="${LOG%.log}.environment.json"
  export FW_A100_NCCL_ATTEMPT="${LOG%.log}.workers"
}
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
    if [[ "$code" != 0 ]]; then
      python3 "$HELPER" failure --root "$FW_ROOT" --log "$log"
    fi
    printf 'Exit code: %s\n' "$code"
    exit "$code" ;;
  system|hf) command=(bash scripts/memory_s1/portable/install_environments.sh "$ACTION") ;;
  inventory) command=(/opt/hf-tools/bin/python -u scripts/memory_s1/portable/recovery.py inventory --output "$RECOVERY_ROOT/inventory") ;;
  fetch|payloads|restore) command=(/opt/hf-tools/bin/python -u "$HELPER" "$ACTION" --root "$FW_ROOT") ;;
  patch-sources) command=(/opt/hf-tools/bin/python -u "$HELPER" restore --root "$FW_ROOT" --overlay-sources) ;;
  resources|verify-resources)
    command=(/opt/hf-tools/bin/python -u "$HELPER" "$ACTION" --root "$FW_ROOT") ;;
  training)
    # Use the actual exported application's pip inventory, not a stale ready environment.
    export READY_DIR="$RECOVERY_ROOT/migration"
    command=(/opt/hf-tools/bin/python -u "$HELPER" training --root "$FW_ROOT") ;;
  references)
    command=(/opt/mwam/bin/python -u -m fastwam.memory_s1.integration restore-reference --config "$CONFIG") ;;
  simulator) command=(bash scripts/memory_s1/portable/a100/prepare.sh) ;;
  devices)
    test -f "$FW_ROOT/outputs/fused_environment_a100_v1/COMPLETE.json"
    command=(/opt/hf-tools/bin/python -u "$HELPER" devices --root "$FW_ROOT") ;;
  nccl)
    command=(/opt/mwam/bin/python -u scripts/memory_s1/portable/a100/nccl_bootstrap.py nccl --root "$FW_ROOT") ;;
  planners|models)
    export PYTHONPATH="$FW_ROOT/src"
    command=(/opt/mwam/bin/python -u -m fastwam.memory_s1.grasp_bridge "$ACTION" --root "$FW_ROOT" --machine a100 "${resume[@]}") ;;
  report)
    command=(/opt/hf-tools/bin/python -u "$HELPER" report --root "$FW_ROOT") ;;
  backup)
    export PYTHONPATH="$FW_ROOT/src"
    command=(/opt/hf-tools/bin/python -u -m fastwam.memory_s1.grasp_bridge backup --root "$FW_ROOT" --machine a100) ;;
  cache)
    test -f "$RECOVERY_ROOT/DEVICES_COMPLETE.json"
    test -f "$RECOVERY_ROOT/NCCL_COMPLETE.json"
    # dense.cache itself verifies a matching local pilot report before any encoding.
    command=(/opt/mwam/bin/python -u scripts/memory_s1/portable/a100/nccl_bootstrap.py cache --root "$FW_ROOT" --config "$CONFIG") ;;
  *) echo 'Usage: launch.sh system|hf|inventory|fetch|payloads|restore|resources|patch-sources|verify-resources|training|references|simulator|devices|planners|models|nccl|report|backup|cache|status|wait|watch|stop'; exit 2 ;;
esac
exec 9>"$RECOVERY_ROOT/job.lock"
flock -n 9 || { echo 'Another A100 setup stage is active; wait first.'; exit 1; }
if [[ -f "$RECOVERY_ROOT/STOP" ]]; then
  (( ${#resume[@]} )) || { echo 'STOP present; explicitly use launch.sh resume STAGE'; exit 1; }
  mv -- "$RECOVERY_ROOT/STOP" "$RECOVERY_ROOT/STOP.resumed_$(date -u +%Y%m%dT%H%M%SZ)_$$"
fi
python3 "$HELPER" precheck --root "$FW_ROOT" --stage "$ACTION"
# Qualification shares the A100 diagnostic lock, not the H100 lease.
if [[ "$ACTION" == planners || "$ACTION" == models || "$ACTION" == backup ]]; then
  mkdir -p "$FW_ROOT/outputs/s1_grasp_bridge_a100_v1"
  exec 8>"$FW_ROOT/outputs/s1_grasp_bridge_a100_v1/job.lock"
  flock -n 8 || { echo 'A100 diagnostic stage is active'; exit 1; }
fi
LOG="$RECOVERY_ROOT/launches/${ACTION}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
if [[ "$ACTION" == nccl || "$ACTION" == cache ]]; then
  configure_a100_nccl
  /opt/hf-tools/bin/python "$HELPER" nccl-runtime --root "$FW_ROOT" --stage "$ACTION"
fi
printf '%q ' "${command[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
FW_A100_STAGE="$ACTION" FW_A100_HELPER="$HELPER" FW_A100_EXIT="${LOG%.log}.exit" nohup setsid bash -c '
  trap '\''printf "143\n" > "$FW_A100_EXIT"; exit 143'\'' TERM
  if [[ "$FW_A100_STAGE" == nccl || "$FW_A100_STAGE" == cache ]]; then
    printf "[nccl runtime] profile=%s environment=%s logs=%s\n" "$FW_A100_NCCL_PROFILE" "$FW_A100_NCCL_ENVIRONMENT" "$NCCL_DEBUG_FILE"
  fi
  "$@"
  code=$?
  if [[ "$code" == 0 && "$FW_A100_STAGE" != system && "$FW_A100_STAGE" != hf && "$FW_A100_STAGE" != inventory ]]; then
    /opt/hf-tools/bin/python "$FW_A100_HELPER" mark --root "$FW_ROOT" --stage "$FW_A100_STAGE" || code=$?
  fi
  printf "%s\n" "$code" > "$FW_A100_EXIT"
  exit "$code"
' a100-stage "${command[@]}" > "$LOG" 2>&1 < /dev/null &
pid=$!
python3 "$HELPER" register --root "$FW_ROOT" --pid "$pid" --log "$LOG"
printf '%s\n' "$LOG" > "$RECOVERY_ROOT/latest_log.txt"
printf 'Stage=%s\nPID=%s\nLog=%s\nExit=%s\n' "$ACTION" "$pid" "$LOG" "${LOG%.log}.exit"
