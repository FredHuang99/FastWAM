#!/usr/bin/env bash
# Explicit H100 sampling pilot; A100 and original S1 entries stay independent.
set -euo pipefail
export FW_ROOT="${FW_ROOT:-/workspace/FastWAM}"
cd "$FW_ROOT"
export PYTHONPATH="$FW_ROOT/src" PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
unset PYTHONHOME CUDA_LAUNCH_BLOCKING
PYTHON=/opt/mwam/bin/python
OUT="$($PYTHON -B -c 'import json,sys; from pathlib import Path; r=Path(sys.argv[1]).resolve(); p=(r/json.loads((r/"configs/memory_s1/stage_sampling_h100.json").read_text())["output"]).resolve(); assert p.is_relative_to(r/"outputs"); print(p)' "$FW_ROOT")"
mkdir -p "$OUT/launches" "$OUT/tmp"
export TMPDIR="$OUT/tmp"
action="${1:-status}"
case "$action" in
  status|stop) exec "$PYTHON" -B -m fastwam.memory_s1.stage_sampling_pilot "$action" --root "$FW_ROOT" ;;
  wait|watch)
    test -f "$OUT/latest_log.txt"
    log="$(cat "$OUT/latest_log.txt")"
    if [[ "$action" == watch ]]; then exec tail -n 60 -F "$log"; fi
    seen=0
    while :; do
      if [[ -f "$log" ]]; then
        lines="$(wc -l < "$log")"
        if (( lines > seen )); then sed -n "$((seen+1)),${lines}p" "$log"; seen="$lines"; fi
      fi
      if [[ -f "${log%.log}.exit" ]]; then
        rc="$(cat "${log%.log}.exit")"; printf 'Exit code: %s\n' "$rc"; exit "$rc"
      fi
      if flock -n "$OUT/job.lock" true; then echo "Launch ended without exit receipt. Inspect $log"; exit 1; fi
      sleep 3
    done ;;
esac
resume=()
if [[ "$action" == resume ]]; then action="${2:?Usage: stage_sampling.sh resume STAGE}"; resume=(--resume); fi
case "$action" in
  prepare|baseline|fit|evaluate|physical|report|pack) ;;
  *) echo 'Stages: prepare baseline fit evaluate physical report pack; controls: status watch wait stop resume STAGE'; exit 2 ;;
esac
exec 9>"$OUT/job.lock"
flock -n 9 || { echo 'A sampling pilot stage is already active.'; exit 1; }
command=("$PYTHON" -B -u -m fastwam.memory_s1.stage_sampling_pilot "$action" --root "$FW_ROOT" "${resume[@]}")
log="$OUT/launches/${action}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
printf '%q ' "${command[@]}" > "${log%.log}.command"
printf '\n' >> "${log%.log}.command"
FW_STAGE_SAMPLING_EXIT="${log%.log}.exit" nohup setsid bash -c '
  trap '\''printf "143\n" > "$FW_STAGE_SAMPLING_EXIT"; exit 143'\'' TERM
  "$@"
  rc=$?
  printf "%s\n" "$rc" > "$FW_STAGE_SAMPLING_EXIT"
  exit "$rc"
' stage-sampling "${command[@]}" > "$log" 2>&1 < /dev/null &
printf '%s\n' "$log" > "$OUT/latest_log.txt"
printf 'H100 stage=%s\nPID=%s\nLog=%s\nExit=%s\n' "$action" "$!" "$log" "${log%.log}.exit"
