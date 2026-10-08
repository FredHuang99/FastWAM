#!/usr/bin/env bash
set -euo pipefail

EVAL_OUTPUT=""
EVAL_ARGS=("$@")
for ((i=0; i<${#EVAL_ARGS[@]}; i++)); do
  if [[ "${EVAL_ARGS[$i]}" == "--output" ]]; then
    EVAL_OUTPUT="${EVAL_ARGS[$((i+1))]}"
  fi
done
if [[ -z "$EVAL_OUTPUT" ]]; then
  echo "Usage: bash scripts/memory_s1/launch_eval.sh --config CONFIG --output DIR --mode diagnostic --conditions gate_zero --gpus 0,1,2,3,4,5,6,7 [--record-frames] [--hf-results] [--resume]" >&2
  exit 2
fi
mkdir -p "$EVAL_OUTPUT/launches"
EVAL_LOG="$EVAL_OUTPUT/launches/$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
export EVAL_EXIT="${EVAL_LOG%.log}.exit"
EVAL_PYTHON="${MEMORY_S1_PYTHON:-/opt/mwam/bin/python}"
export PYTHONUNBUFFERED=1
printf '%q ' "$EVAL_PYTHON" -u -m fastwam.memory_s1.eval_parallel run "${EVAL_ARGS[@]}" > "${EVAL_LOG%.log}.command"
printf '\n' >> "${EVAL_LOG%.log}.command"
nohup bash -c '
  "$@"
  result=$?
  printf "%s\n" "$result" > "$EVAL_EXIT"
  exit "$result"
' mwam-eval "$EVAL_PYTHON" -u -m fastwam.memory_s1.eval_parallel run "${EVAL_ARGS[@]}" > "$EVAL_LOG" 2>&1 < /dev/null &
printf '%s\n' "$!" > "$EVAL_OUTPUT/launcher.pid"
printf '%s\n' "$EVAL_LOG" > "$EVAL_OUTPUT/latest_log.txt"
printf 'Launcher PID: %s\nLog: %s\n' "$!" "$EVAL_LOG"
printf 'Watch: tail -f %q\n' "$EVAL_LOG"
printf 'Status: %q scripts/memory_s1/eval_control.py status --output %q\n' "$EVAL_PYTHON" "$EVAL_OUTPUT"
printf 'Safe stop: %q scripts/memory_s1/eval_control.py stop --output %q --mode now\n' "$EVAL_PYTHON" "$EVAL_OUTPUT"
