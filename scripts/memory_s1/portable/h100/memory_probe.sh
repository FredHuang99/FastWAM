#!/usr/bin/env bash
# Explicit, bounded H100 probe. Every mutation runs in an owned nohup session.
set -euo pipefail
export FW_ROOT="${FW_ROOT:-/workspace/FastWAM}"
cd "$FW_ROOT"
export PYTHONPATH="$FW_ROOT/src" PYTHONNOUSERSITE=1 PYTHONUNBUFFERED=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
unset PYTHONHOME CUDA_LAUNCH_BLOCKING
PYTHON=/opt/mwam/bin/python
OUT="$($PYTHON -c 'import json,sys; from pathlib import Path; r=Path(sys.argv[1]).resolve(); p=(r/json.loads((r/"configs/memory_s1/memory_probe_h100.json").read_text())["output"]).resolve(); assert p.is_relative_to(r/"outputs"); print(p)' "$FW_ROOT")"
mkdir -p "$OUT/launches" "$OUT/tmp"
export TMPDIR="$OUT/tmp"
action="${1:-status}"
case "$action" in
  status|stop)
    exec "$PYTHON" -m fastwam.memory_s1.memory_probe "$action" --root "$FW_ROOT" ;;
  watch|wait)
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
      if flock -n "$OUT/job.lock" true; then
        echo "Launch ended without an exit receipt. Inspect $log"; exit 1
      fi
      sleep 3
    done ;;
esac
resume=()
if [[ "$action" == resume ]]; then action="${2:?Usage: memory_probe.sh resume STAGE}"; resume=(--resume); fi
case "$action" in
  prepare|probe|report|pack) ;;
  *) echo 'Stages: prepare probe report pack; controls: status watch wait stop resume STAGE'; exit 2 ;;
esac
exec 9>"$OUT/job.lock"
flock -n 9 || { echo 'A memory-probe stage is already active.'; exit 1; }
command=("$PYTHON" -u -m fastwam.memory_s1.memory_probe "$action" --root "$FW_ROOT" "${resume[@]}")
log="$OUT/launches/${action}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
printf '%q ' "${command[@]}" > "${log%.log}.command"
printf '\n' >> "${log%.log}.command"
FW_MEMORY_PROBE_EXIT="${log%.log}.exit" nohup setsid bash -c '
  trap '\''printf "143\n" > "$FW_MEMORY_PROBE_EXIT"; exit 143'\'' TERM
  "$@"
  rc=$?
  printf "%s\n" "$rc" > "$FW_MEMORY_PROBE_EXIT"
  exit "$rc"
' memory-probe "${command[@]}" > "$log" 2>&1 < /dev/null &
printf '%s\n' "$log" > "$OUT/latest_log.txt"
printf 'H100 stage=%s\nPID=%s\nLog=%s\nExit=%s\n' "$action" "$!" "$log" "${log%.log}.exit"
