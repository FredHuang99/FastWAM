#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
ARGS=("$@")
OUTPUT=""
PHASE=""
for ((i=0; i<${#ARGS[@]}; i++)); do
  if [[ "${ARGS[$i]}" == --output ]]; then OUTPUT="${ARGS[$((i+1))]}"; fi
  if [[ "${ARGS[$i]}" == --phase ]]; then PHASE="${ARGS[$((i+1))]}"; fi
done
if [[ -z "$OUTPUT" || -z "$PHASE" ]]; then
  echo 'Pass --config CFG --run RUN --output OUTPUT --phase offline|selection|official|memory [--gpus 0] [--resume] [--hf-results]' >&2
  exit 2
fi
mkdir -p "$OUTPUT/launches"
PYTHON_BIN="${MEMORY_S1_PYTHON:-/opt/mwam/bin/python}"
LOG="$OUTPUT/launches/${PHASE}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
COMMAND=("$PYTHON_BIN" -u -m fastwam.memory_s1.posttrain run "${ARGS[@]}")
printf '%q ' "${COMMAND[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
export POSTTRAIN_EXIT="${LOG%.log}.exit"
nohup bash -c '
  "$@"
  code=$?
  printf "%s\n" "$code" > "$POSTTRAIN_EXIT"
  exit "$code"
' mwam-posttrain "${COMMAND[@]}" > "$LOG" 2>&1 < /dev/null &
printf '%s\n' "$!" > "$OUTPUT/launcher.pid"
printf '%s\n' "$LOG" > "$OUTPUT/latest_log.txt"
printf 'Started PID=%s\nLog=%s\nExit=%s\n' "$!" "$LOG" "$POSTTRAIN_EXIT"
