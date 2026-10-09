#!/usr/bin/env bash
set -euo pipefail
OUTPUT=""
ARGS=("$@")
for ((i=0; i<${#ARGS[@]}; i++)); do
  if [[ "${ARGS[$i]}" == "--output" ]]; then OUTPUT="${ARGS[$((i+1))]}"; fi
done
[[ -n "$OUTPUT" ]] || { echo "Pass --config CONFIG --output DIR" >&2; exit 2; }
mkdir -p "$OUTPUT/launches"
LOG="$OUTPUT/launches/$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
export COMPATIBILITY_EXIT="${LOG%.log}.exit" PYTHONUNBUFFERED=1
PYTHON_BIN="${MEMORY_S1_PYTHON:-$(python -c 'import sys; print(sys.executable)')}"
printf '%q ' "$PYTHON_BIN" -u -m fastwam.memory_s1.base_compatibility "${ARGS[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
nohup bash -c '
  "$@"
  result=$?
  printf "%s\n" "$result" > "$COMPATIBILITY_EXIT"
  exit "$result"
' mwam-compatibility "$PYTHON_BIN" -u -m fastwam.memory_s1.base_compatibility "${ARGS[@]}" > "$LOG" 2>&1 < /dev/null &
printf '%s\n' "$!" > "$OUTPUT/launcher.pid"
printf '%s\n' "$LOG" > "$OUTPUT/latest_log.txt"
printf 'Started PID=%s\nLog: %s\nExit: %s\n' "$!" "$LOG" "$COMPATIBILITY_EXIT"
