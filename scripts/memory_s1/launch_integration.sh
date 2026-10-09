#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false CUBLAS_WORKSPACE_CONFIG=:4096:8
PYTHON="${MEMORY_S1_PYTHON:-/opt/mwam/bin/python}"
OUTPUT=""
ARGS=("$@")
for ((i=0; i<${#ARGS[@]}; i++)); do
  if [[ "${ARGS[$i]}" == "--output" ]]; then OUTPUT="${ARGS[$((i+1))]}"; fi
done
if [[ -z "$OUTPUT" ]]; then
  echo "Usage: bash scripts/memory_s1/launch_integration.sh --config CONFIG --output DIR --stage model|execution|pilot|cache|training|admit [--resume] [--hf-results]" >&2
  exit 2
fi
mkdir -p "$OUTPUT/launches"
LOG="$OUTPUT/launches/$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
export INTEGRATION_EXIT="${LOG%.log}.exit"
printf '%q ' "$PYTHON" -u -m fastwam.memory_s1.integration run "${ARGS[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
nohup bash -c '
  "$@"
  code=$?
  printf "%s\n" "$code" > "$INTEGRATION_EXIT"
  exit "$code"
' mwam-integration "$PYTHON" -u -m fastwam.memory_s1.integration run "${ARGS[@]}" > "$LOG" 2>&1 < /dev/null &
printf '%s\n' "$!" > "$OUTPUT/launcher.pid"
printf '%s\n' "$LOG" > "$OUTPUT/latest_log.txt"
printf 'Started PID=%s\nLog: %s\nExit: %s\n' "$!" "$LOG" "$INTEGRATION_EXIT"
printf 'Status: %q -m fastwam.memory_s1.integration status --output %q\n' "$PYTHON" "$OUTPUT"
printf 'Stop: %q -m fastwam.memory_s1.integration stop --output %q\n' "$PYTHON" "$OUTPUT"
