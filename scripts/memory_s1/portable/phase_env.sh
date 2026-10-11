#!/usr/bin/env bash
# Source this file; it only defines variables/functions and creates log directories.
export FW_ROOT=/workspace/FastWAM
export CFG=configs/memory_s1/s1_variable_t_h100_phase.yaml
export RUN_ROOT="$FW_ROOT/outputs/memory_s1_variable_t_h100_phase_seed17"
export INTEGRATION_ROOT="$FW_ROOT/outputs/fastwam_rmbench_integration_h100_phase_v1"
export RECOVERY_ROOT="$FW_ROOT/outputs/recovery_aws_h100"
export CACHE_ROOT="$FW_ROOT/resources/cache_s1_dense_h100_v1"
export PARENT_SNAPSHOT="$RECOVERY_ROOT/phase_parent"
export TMPDIR="$RECOVERY_ROOT/tmp"
export HF_HUB_CACHE="$RECOVERY_ROOT/hf_cache"
export CUDA_VISIBLE_DEVICES=0 PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
export CUBLAS_WORKSPACE_CONFIG=:4096:8
unset CUDA_LAUNCH_BLOCKING TORCH_SHOW_CPP_STACKTRACES
mkdir -p "$TMPDIR" "$HF_HUB_CACHE" "$RUN_ROOT/launches"
cd "$FW_ROOT" || return 1

bg_run() {
  local name="${1:?Pass a job name}"; shift
  local log="$RUN_ROOT/launches/${name}_$(date -u +%Y%m%dT%H%M%S)_${BASHPID}.log"
  printf '%q ' "$@" > "${log%.log}.command"
  printf '\n' >> "${log%.log}.command"
  FW_JOB_EXIT="${log%.log}.exit" nohup bash -c '
    "$@"
    result=$?
    printf "%s\n" "$result" > "$FW_JOB_EXIT"
    exit "$result"
  ' mwam-phase-job "$@" > "$log" 2>&1 < /dev/null &
  local pid=$!
  printf '%s\n' "$log" > "$RUN_ROOT/latest_${name}_log.txt"
  python - "$pid" "${log%.log}.owner.json" <<'PY'
import json, sys
from pathlib import Path
pid = int(sys.argv[1])
p = Path(f"/proc/{pid}/stat")
value = {"pid": pid, "start_ticks": p.read_text().rsplit(")", 1)[1].split()[19] if p.exists() else None}
Path(sys.argv[2]).write_text(json.dumps(value))
PY
  printf 'PID=%s\nLog=%s\n' "$pid" "$log"
}

fw_wait() {
  local name="${1:?Pass a job name}" log code
  log="$(cat "$RUN_ROOT/latest_${name}_log.txt")" || return 1
  while [[ ! -f "${log%.log}.exit" ]]; do
    if ! python - "${log%.log}.owner.json" <<'PY'
import json, sys
from pathlib import Path
owner = json.loads(Path(sys.argv[1]).read_text())
p = Path(f"/proc/{owner['pid']}/stat")
fields = p.read_text().rsplit(")", 1)[1].split() if p.exists() else []
sys.exit(0 if fields and fields[0] != "Z" and fields[19] == owner["start_ticks"] else 1)
PY
    then
      [[ -f "${log%.log}.exit" ]] && break
      echo "Job ended without an exit marker. Inspect: $log" >&2
      return 1
    fi
    sleep 10
  done
  code="$(cat "${log%.log}.exit")"
  tail -n 12 "$log"
  printf 'Exit code: %s\n' "$code"
  [[ "$code" == 0 ]]
}
