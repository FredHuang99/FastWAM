#!/usr/bin/env bash
set -euo pipefail
CONFIG="${CONFIG:-configs/memory_s1/s1_variable_t.yaml}"
GPUS="${GPUS:-8}"
export PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
CACHE_ROOT="$(python -c 'import sys; from fastwam.memory_s1.common import load_config; print(load_config(sys.argv[1])["paths"]["cache"])' "$CONFIG")"
mkdir -p "$CACHE_ROOT/launches"
if [[ -e "$CACHE_ROOT/STOP_REQUESTED" ]]; then
  echo "Clear the old cache STOP_REQUESTED after checking the previous launch." >&2; exit 1
fi
if [[ -f "$CACHE_ROOT/launcher.pid" ]] && kill -0 "$(cat "$CACHE_ROOT/launcher.pid")" 2>/dev/null; then
  echo "A recorded cache launcher is alive; refuse duplicate workers." >&2; exit 1
fi
LAUNCH_ID="$(date -u +%Y%m%dT%H%M%SZ)_$$"
LOG="$CACHE_ROOT/launches/$LAUNCH_ID.log"
export CACHE_EXIT="${LOG%.log}.exit"
COMMAND=(torchrun --standalone --nnodes=1 --nproc_per_node="$GPUS" -m fastwam.memory_s1.dense cache --config "$CONFIG")
printf '%q ' "${COMMAND[@]}" > "${LOG%.log}.command"
printf '\n' >> "${LOG%.log}.command"
nohup bash -c '
  "$@"
  result=$?
  printf "%s\n" "$result" > "$CACHE_EXIT"
  exit "$result"
' mwam-cache "${COMMAND[@]}" > "$LOG" 2>&1 < /dev/null &
printf '%s\n' "$!" > "$CACHE_ROOT/launcher.pid"
printf '%s\n' "$LOG" > "$CACHE_ROOT/latest_log.txt"
printf 'Started cache PID=%s\nLog: %s\nSafe stop: touch %q\n' "$!" "$LOG" "$CACHE_ROOT/STOP_REQUESTED"
