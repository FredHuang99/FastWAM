#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"
export FW_ROOT="$REPO_ROOT" PYTHONUNBUFFERED=1
export TOKENIZERS_PARALLELISM=false HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export WANDB_MODE=disabled
GPUS="${GPUS:-8}"
MICRO_BATCH="${MICRO_BATCH:-2}"
CONFIG="${CONFIG:-configs/memory_s1/s1.yaml}"
RESOLVED_RUN="$(python -c 'import sys; from fastwam.memory_s1.common import load_config; print(load_config(sys.argv[1])["paths"]["run"])' "$CONFIG")"
if [[ -n "${RUN_DIR:-}" && "$RUN_DIR" != "$RESOLVED_RUN" ]]; then
  echo 'RUN_DIR differs from the configured trainer output; edit the config instead.' >&2; exit 1
fi
RUN_DIR="$RESOLVED_RUN"
mkdir -p "$RUN_DIR/launches"
if [[ -e "$RUN_DIR/STOP_REQUESTED" ]]; then
  echo "An old STOP_REQUESTED marker exists. Inspect the previous stop and remove it before launch." >&2
  exit 1
fi
if [[ -f "$RUN_DIR/launcher.pid" ]] && kill -0 "$(cat "$RUN_DIR/launcher.pid")" 2>/dev/null; then
  echo "A launcher recorded for this run is still alive; refuse a duplicate launch." >&2
  exit 1
fi
LAUNCH_ID="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$RUN_DIR/launches/$LAUNCH_ID.log"
COMMAND=(torchrun --standalone --nnodes=1 --nproc_per_node="$GPUS" -m fastwam.memory_s1.train --config "$CONFIG" --micro-batch "$MICRO_BATCH")
if [[ -n "${RESUME:-}" ]]; then COMMAND+=(--resume "$RESUME"); fi
printf '%q ' "${COMMAND[@]}" > "$RUN_DIR/launches/$LAUNCH_ID.command"
printf '\n' >> "$RUN_DIR/launches/$LAUNCH_ID.command"
nohup "${COMMAND[@]}" > "$LOG" 2>&1 < /dev/null &
PID=$!
printf '%s\n' "$PID" > "$RUN_DIR/launcher.pid"
printf 'run=%s\nlaunch=%s\npid=%s\nlog=%s\n' "$RUN_DIR" "$LAUNCH_ID" "$PID" "$LOG" > "$RUN_DIR/launches/$LAUNCH_ID.info"
printf 'Started PID=%s.\nLog: tail -f %q\nStatus: ps -p %q -o pid,etime,cmd\nSafe stop: bash scripts/memory_s1/safe_stop.sh %q\n' "$PID" "$LOG" "$PID" "$RUN_DIR"
