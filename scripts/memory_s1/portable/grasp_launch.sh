#!/usr/bin/env bash
# Foreground shell only dispatches explicitly requested stages, each with nohup.
set -euo pipefail
export FW_ROOT="${FW_ROOT:-/workspace/FastWAM}"
cd "$FW_ROOT"
machine="${FW_BRIDGE_MACHINE:?Use the independent h100/a100 diagnose.sh entry}"
case "$machine" in h100|a100) ;; *) exit 2 ;; esac
OUT="$FW_ROOT/outputs/s1_grasp_bridge_${machine}_v1"
mkdir -p "$OUT/launches" "$OUT/tmp"
export TMPDIR="$OUT/tmp" PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
unset CUDA_LAUNCH_BLOCKING HF_HUB_OFFLINE TRANSFORMERS_OFFLINE PYTHONHOME
export PYTHONPATH="$FW_ROOT/src"
previous_hf_home="${HF_HOME:-}"
export HF_HOME="$FW_ROOT/.cache/huggingface_${machine}"
# Separate caches while reusing an existing token by path; never copy/print credentials.
if [[ -z "${HF_TOKEN_PATH:-}" || ! -f "$HF_TOKEN_PATH" ]]; then
  for login_home in "$HF_HOME" "$previous_hf_home" "$FW_ROOT/.cache/huggingface" "${XDG_CACHE_HOME:-$HOME/.cache}/huggingface"; do
    if [[ -n "$login_home" && -f "$login_home/token" ]]; then export HF_TOKEN_PATH="$login_home/token"; break; fi
  done
fi
action="${1:-status}"
helper="$FW_ROOT/src/fastwam/memory_s1/grasp_bridge.py"
case "$action" in
  status|stop) exec python3 -m fastwam.memory_s1.grasp_bridge "$action" --root "$FW_ROOT" --machine "$machine" ;;
  watch|wait)
    test -f "$OUT/latest_log.txt"; log="$(cat "$OUT/latest_log.txt")"
    if [[ "$action" == watch ]]; then exec tail -n 80 -F "$log"; fi
    while [[ ! -f "${log%.log}.exit" ]]; do
      tail -n 6 "$log"
      sleep 10
      if flock -n "$OUT/job.lock" true && [[ ! -f "${log%.log}.exit" ]]; then
        echo "Process ended without exit receipt. Inspect $log"; exit 1
      fi
    done
    tail -n 80 "$log"; rc="$(cat "${log%.log}.exit")"; echo "Exit code: $rc"; exit "$rc" ;;
esac
resume=()
if [[ "$action" == resume ]]; then action="${2:?Usage: diagnose.sh resume STAGE}"; resume=(--resume); fi
case "$action" in freeze|export-migration|paths|noise|expert-observe|teacher|planners|models|report|backup) ;; *) echo 'Stages: freeze export-migration paths noise expert-observe teacher report backup; A100 also planners models; controls: status watch wait stop resume STAGE'; exit 2 ;; esac
python=/opt/mwam/bin/python
[[ "$action" != backup ]] || python=/opt/hf-tools/bin/python
command=("$python" -u -m fastwam.memory_s1.grasp_bridge "$action" --root "$FW_ROOT" --machine "$machine" "${resume[@]}")
exec 9>"$OUT/job.lock"
flock -n 9 || { echo 'This machine already has an active grasp stage.'; exit 1; }
log="$OUT/launches/${action}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
printf '%q ' "${command[@]}" > "${log%.log}.command"; printf '\n' >> "${log%.log}.command"
FW_BRIDGE_EXIT="${log%.log}.exit" nohup setsid bash -c '
  trap '\''printf "143\n" > "$FW_BRIDGE_EXIT"; exit 143'\'' TERM
  "$@"
  rc=$?
  printf "%s\n" "$rc" > "$FW_BRIDGE_EXIT"
  exit "$rc"
' bridge-stage "${command[@]}" > "$log" 2>&1 < /dev/null &
pid=$!
printf '%s\n' "$log" > "$OUT/latest_log.txt"
printf 'Machine=%s Stage=%s\nPID=%s\nLog=%s\nExit=%s\n' "$machine" "$action" "$pid" "$log" "${log%.log}.exit"
