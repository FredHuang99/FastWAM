#!/usr/bin/env bash
set -euo pipefail

OUTPUT=""
ARGS=("$@")
for ((i=0; i<${#ARGS[@]}; i++)); do
  if [[ "${ARGS[$i]}" == "--output" ]]; then
    OUTPUT="${ARGS[$((i+1))]}"
  fi
done
if [[ -z "$OUTPUT" ]]; then
  echo "Usage: bash scripts/memory_s1/launch_rootcause.sh --config CONFIG --output DIR --stage D0|D1|D2|D3|all [--resume] [--hf-results]" >&2
  exit 2
fi
PYTHON="${MEMORY_S1_PYTHON:-/opt/mwam/bin/python}"
mkdir -p "$OUTPUT/launches"
LOG="$OUTPUT/launches/$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
export ROOTCAUSE_EXIT="${LOG%.log}.exit"
export PYTHONUNBUFFERED=1
printf '%q ' "$PYTHON" -u -m fastwam.memory_s1.rootcause run "${ARGS[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
nohup bash -c '
  "$@"
  code=$?
  printf "%s\n" "$code" > "$ROOTCAUSE_EXIT"
  exit "$code"
' rootcause "$PYTHON" -u -m fastwam.memory_s1.rootcause run "${ARGS[@]}" > "$LOG" 2>&1 < /dev/null &
printf '%s\n' "$!" > "$OUTPUT/launcher.pid"
printf '%s\n' "$LOG" > "$OUTPUT/latest_log.txt"
printf 'Started PID=%s\nLog: %s\nExit: %s\n' "$!" "$LOG" "$ROOTCAUSE_EXIT"
printf 'Status: %q -m fastwam.memory_s1.rootcause status --output %q\n' "$PYTHON" "$OUTPUT"
printf 'Stop: %q -m fastwam.memory_s1.rootcause stop --output %q\n' "$PYTHON" "$OUTPUT"
