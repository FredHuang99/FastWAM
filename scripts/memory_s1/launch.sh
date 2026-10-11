#!/usr/bin/env bash
set -euo pipefail
export CUBLAS_WORKSPACE_CONFIG=:4096:8
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
export FW_ROOT="$REPO_ROOT" PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export WANDB_MODE=disabled
CONFIG="${CONFIG:-configs/memory_s1/s1.yaml}"
# Bind the launcher and workers to the active Python environment.
PYTHON_BIN="$(python -c 'import sys; print(sys.executable)')"
export PYTHON_EXEC="$PYTHON_BIN"
read -r CONFIG_GPUS CONFIG_MICRO < <("$PYTHON_BIN" -c 'import sys; from fastwam.memory_s1.common import load_config; c=load_config(sys.argv[1]); print(c.get("startup", {}).get("expected_world_size", c.get("recovery", {}).get("expected_world_size", 8)), c["micro_batch"])' "$CONFIG")
GPUS="${GPUS:-$CONFIG_GPUS}"
MICRO_BATCH="${MICRO_BATCH:-$CONFIG_MICRO}"
RESOLVED_RUN="$("$PYTHON_BIN" -c 'import sys; from fastwam.memory_s1.common import load_config; print(load_config(sys.argv[1])["paths"]["run"])' "$CONFIG")"
if [[ -n "${RUN_DIR:-}" && "$RUN_DIR" != "$RESOLVED_RUN" ]]; then
  echo 'RUN_DIR differs from the configured trainer output; edit the config instead.' >&2; exit 1
fi
RUN_DIR="$RESOLVED_RUN"
mkdir -p "$RUN_DIR/launches"
if [[ -e "$RUN_DIR/STOP_REQUESTED" ]]; then
  echo "An old STOP_REQUESTED marker exists. Inspect the previous stop and remove it before launch." >&2
  exit 1
fi
LAUNCH_ID="$(date -u +%Y%m%dT%H%M%SZ)_$$"
LOG="$RUN_DIR/launches/$LAUNCH_ID.log"
COMMAND=("$PYTHON_BIN" -m fastwam.memory_s1.startup guard --config "$CONFIG" --workers "$GPUS" --micro-batch "$MICRO_BATCH")
if [[ -n "${RESUME:-}" ]]; then COMMAND+=(--resume "$RESUME"); fi
printf '%q ' "${COMMAND[@]}" > "$RUN_DIR/launches/$LAUNCH_ID.command"
printf '\n' >> "$RUN_DIR/launches/$LAUNCH_ID.command"
export TRAIN_EXIT="${LOG%.log}.exit"
nohup bash -c '
  "$@"
  result=$?
  printf "%s\n" "$result" > "$TRAIN_EXIT"
  exit "$result"
' mwam-train "${COMMAND[@]}" > "$LOG" 2>&1 < /dev/null &
PID=$!
printf '%s\n' "$LOG" > "$RUN_DIR/latest_log.txt"
printf '%s\n' "$PID" > "$RUN_DIR/launcher.pid"
printf 'run=%s\nlaunch=%s\npid=%s\nlog=%s\npython=%s\n' "$RUN_DIR" "$LAUNCH_ID" "$PID" "$LOG" "$PYTHON_BIN" > "$RUN_DIR/launches/$LAUNCH_ID.info"
printf 'Python: %s\nStarted PID=%s.\nLog: tail -f %q\nStatus: ps -p %q -o pid,etime,cmd\nSafe stop: bash scripts/memory_s1/safe_stop.sh %q\n' "$PYTHON_BIN" "$PID" "$LOG" "$PID" "$RUN_DIR"
