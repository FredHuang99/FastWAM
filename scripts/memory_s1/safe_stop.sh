#!/usr/bin/env bash
set -euo pipefail
RUN_DIR="${1:?Pass the absolute run directory}"
if [[ ! -d "$RUN_DIR" ]]; then echo "Run directory does not exist: $RUN_DIR" >&2; exit 1; fi
touch "$RUN_DIR/STOP_REQUESTED"
echo "Stop requested. Workers save/upload at the next completed update, then exit."
echo "Wait for [saved], [finish] stopped=True and launch exit code 2 before stopping the machine."
