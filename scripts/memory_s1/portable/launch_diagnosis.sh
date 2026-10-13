#!/usr/bin/env bash
# Run one explicitly requested stage. No stage automatically starts another.
set -euo pipefail
export FW_ROOT="${FW_ROOT:-/workspace/FastWAM}"
export DIAG_ROOT="${DIAG_ROOT:-$FW_ROOT/outputs/s1_zero_success_diagnosis_v1}"
export DIAG_CFG="${DIAG_CFG:-$FW_ROOT/configs/memory_s1/diagnose_h100_s1.yaml}"
PY="${MWAM_PYTHON:-/opt/mwam/bin/python}"
cd "$FW_ROOT"
export PYTHONPATH="$FW_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export CUDA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1
export OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
export CUBLAS_WORKSPACE_CONFIG=:4096:8
unset CUDA_LAUNCH_BLOCKING
action="${1:-status}"
if [ "$#" -gt 0 ]; then shift; fi
case "$action" in
  status|stop|stop-old)
    exec "$PY" scripts/memory_s1/portable/diagnosis_control.py "$action" --root "$DIAG_ROOT" --config "$DIAG_CFG"
    ;;
  wait|watch)
    if [ ! -f "$DIAG_ROOT/latest_log.txt" ]; then echo 'No diagnostic launch recorded.'; exit 1; fi
    log="$(cat "$DIAG_ROOT/latest_log.txt")"
    if [ "$action" = watch ]; then exec tail -n 60 -F "$log"; fi
    while [ ! -f "${log%.log}.exit" ]; do
      "$PY" scripts/memory_s1/portable/diagnosis_control.py status --root "$DIAG_ROOT" --config "$DIAG_CFG"
      sleep 15
      if [ ! -f "${log%.log}.exit" ] && "$PY" scripts/memory_s1/portable/diagnosis_control.py idle --root "$DIAG_ROOT" --config "$DIAG_CFG" >/dev/null 2>&1; then
        echo "Recorded processes exited without an exit file; inspect $log. No automatic retry."
        exit 1
      fi
    done
    tail -n 60 "$log"
    code="$(cat "${log%.log}.exit")"
    printf 'Exit code: %s\n' "$code"
    exit "$code"
    ;;
  inventory|offline|paths|gradients|expert|fixed|random|micro|retest8|retest40|report|backup) ;;
  *) echo "Unknown stage: $action"; exit 2 ;;
esac
mkdir -p "$DIAG_ROOT/launches"
exec 9>"$DIAG_ROOT/start.lock"
flock -n 9 || { echo 'Another launch is being prepared.'; exit 1; }
"$PY" scripts/memory_s1/portable/diagnosis_control.py idle --root "$DIAG_ROOT" --config "$DIAG_CFG"
stamp="$(date -u +%Y%m%dT%H%M%SZ)_$$"
log="$DIAG_ROOT/launches/${action}_${stamp}.log"
command=("$PY" -u -m fastwam.memory_s1.s1_diagnosis "$action" --config "$DIAG_CFG" --output "$DIAG_ROOT" --resume "$@")
printf '%q ' "${command[@]}" > "${log%.log}.command"
printf '\n' >> "${log%.log}.command"
printf '%s\n' "$log" > "$DIAG_ROOT/latest_log.txt"
FW_DIAG_EXIT="${log%.log}.exit" nohup bash -c '
  "$@"
  code=$?
  printf "%s\n" "$code" > "$FW_DIAG_EXIT"
  exit "$code"
' s1-diagnostic "${command[@]}" >"$log" 2>&1 < /dev/null 9>&- &
pid=$!
"$PY" scripts/memory_s1/portable/diagnosis_control.py register --root "$DIAG_ROOT" --config "$DIAG_CFG" --pid "$pid" --log "$log"
printf 'PID=%s\nLog=%s\nExit=%s\n' "$pid" "$log" "${log%.log}.exit"
