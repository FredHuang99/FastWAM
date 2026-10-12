#!/usr/bin/env bash
# User-invoked only. Existing posttrain owns the queue, locks, backup and recovery.
set -euo pipefail
ACTION="${1:-}"
case "$ACTION" in prepare|qualify|run|status|stop|backup|watch) ;; *) echo 'Usage: launch_top2.sh prepare|qualify|run|status|stop|backup|watch {prepare|qualify|run}' >&2; exit 2 ;; esac
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT"
export FW_ROOT="$ROOT"
PY=/opt/mwam/bin/python
CFG="$ROOT/configs/memory_s1/eval_h100_top2.yaml"
RUN="$ROOT/outputs/memory_s1_variable_t_h100_phase_seed17"
QUAL="$ROOT/outputs/selection_fused_qualification_top2_h100_v2"
POST="$ROOT/outputs/posttrain_h100_phase_seed17_top2_v2"
unset CUDA_LAUNCH_BLOCKING HF_HUB_OFFLINE TRANSFORMERS_OFFLINE
export PYTHONUNBUFFERED=1

background() {
  local label="$1"
  shift
  mkdir -p "$POST/launches"
  local log="$POST/launches/${label}_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
  FW_TOP2_EXIT="${log%.log}.exit" nohup bash -c '
    "$@"
    result=$?
    printf "%s\n" "$result" > "$FW_TOP2_EXIT"
    exit "$result"
  ' top2-job "$@" > "$log" 2>&1 < /dev/null &
  printf '%s\n' "$log" > "$POST/latest_${label}_log.txt"
  printf 'PID=%s\nLog=%s\nExit=%s\n' "$!" "$log" "${log%.log}.exit"
}

case "$ACTION" in
  watch)
    case "${2:-}" in
      prepare) pointer="$POST/latest_environment_log.txt" ;;
      qualify) pointer="$QUAL/latest_log.txt" ;;
      run) pointer="$POST/latest_log.txt" ;;
      *) echo 'Usage: launch_top2.sh watch prepare|qualify|run' >&2; exit 2 ;;
    esac
    "$PY" - "$pointer" <<'PY'
import sys
import time
from pathlib import Path
pointer = Path(sys.argv[1])
if not pointer.is_file():
    raise SystemExit(f'No launch log recorded: {pointer}')
log = Path(pointer.read_text().strip())
exit_path = log.with_suffix('.exit')
print(f'Log: {log}\nCtrl-C stops this log viewer only.', flush=True)
try:
    with log.open('rb') as stream:
        stream.seek(max(0, log.stat().st_size-32768))
        tail = stream.read().splitlines(keepends=True)[-40:]
        sys.stdout.buffer.write(b''.join(tail))
        sys.stdout.flush()
        while True:
            data = stream.read()
            if data:
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            if exit_path.is_file():
                data = stream.read()
                if data:
                    sys.stdout.buffer.write(data)
                    sys.stdout.flush()
                code = int(exit_path.read_text().strip())
                print(f'\nExit code: {code}', flush=True)
                raise SystemExit(code)
            time.sleep(1)
except KeyboardInterrupt:
    print('\nLog viewer stopped; background job unchanged.', flush=True)
PY
    exit ;;
  prepare)
    background environment bash scripts/memory_s1/portable/prepare_fused_env.sh
    exit ;;
  status)
    for output in "$QUAL" "$POST"; do
      printf '\nOutput: %s\n' "$output"
      if [[ -f "$output/status.json" ]]; then
        "$PY" -m fastwam.memory_s1.posttrain status --output "$output"
      else
        echo 'Not started.'
      fi
      if [[ -f "$output/latest_log.txt" ]]; then
        log="$(cat "$output/latest_log.txt")"
        printf 'Log: %s\n' "$log"
        if [[ -f "${log%.log}.exit" ]]; then printf 'Exit: '; cat "${log%.log}.exit"; fi
      fi
    done
    exit ;;
  stop)
    for output in "$QUAL" "$POST"; do
      if [[ -f "$output/launcher.json" ]]; then
        "$PY" scripts/memory_s1/portable/selection_control.py --output "$output" --mode now --grace-seconds 10
      fi
    done
    exit ;;
  backup)
    background backup "$PY" -u -m fastwam.memory_s1.posttrain backup --output "$POST" --phase selection
    exit ;;
esac

[[ -x /opt/rmbench-fused-env/bin/python && -f "$ROOT/outputs/fused_environment_h100_v1/COMPLETE.json" ]] || {
  echo 'Fused environment not ready. Run launch_top2.sh prepare and wait for exit 0.' >&2; exit 1;
}
mkdir -p "$POST"
# Persist the chosen inputs so restarts cannot silently switch scene banks.
"$PY" - "$ROOT" "$POST/INPUTS.json" <<'PY'
import json
import sys
from pathlib import Path
root, output = Path(sys.argv[1]), Path(sys.argv[2])
if output.exists():
    value = json.loads(output.read_text())
    for key in ('scenes', 'offline'):
        if not Path(value[key]).exists():
            raise FileNotFoundError(f'Saved {key} missing: {value[key]}')
else:
    banks = [
        'posttrain_h100_phase_seed17_fused_v1/frozen_scenes.json',
        'posttrain_h100_phase_seed17_selection_v2/selection/base/scenes.json',
        'selection_resident_qualification_h100_v2/qualification_scenes.json',
        'posttrain_h100_phase_seed17/selection/base/scenes.json',
    ]
    scenes = None
    for name in banks:
        path = root/'outputs'/name
        if not path.exists():
            continue
        rows = json.loads(path.read_text()).get('scenes', [])
        if len(rows) == 20 and all(sum(r['task'] == t for r in rows) == 10 for t in ('put_back_block', 'swap_blocks')):
            scenes = path
            break
    offline = root/'outputs/posttrain_h100_phase_seed17'
    if scenes is None:
        raise FileNotFoundError('No complete saved twenty-scene bank; expert search is disabled')
    if not (offline/'identity.json').exists() or not all(
        (offline/f'offline/step_{s:06d}/T{t}.json').exists()
        for s in (500, 1000, 1500, 2000) for t in (1, 4, 8, 16)
    ):
        raise FileNotFoundError(f'Existing offline evidence is incomplete: {offline}; no offline evaluation started')
    value = {'scenes': str(scenes), 'offline': str(offline)}
    temporary = output.with_suffix('.json.partial')
    temporary.write_text(json.dumps(value, indent=2)+'\n')
    temporary.replace(output)
print(json.dumps(value, indent=2))
PY
SCENES="$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["scenes"])' "$POST/INPUTS.json")"
OFFLINE="$("$PY" -c 'import json,sys; print(json.load(open(sys.argv[1]))["offline"])' "$POST/INPUTS.json")"
COMMON=(--config "$CFG" --run "$RUN" --runtime-profile fused-resident --frozen-scenes "$SCENES" --gpus 0 --episode-timeout 3600 --resume --hf-results)
if [[ "$ACTION" == qualify ]]; then
  bash scripts/memory_s1/launch_posttrain.sh "${COMMON[@]}" --output "$QUAL" --phase qualify
else
  "$PY" - "$QUAL" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
assert json.loads((root/'status.json').read_text())['state'] == 'complete', 'Qualification has not completed'
assert json.loads((root/'QUALIFICATION.json').read_text())['passed'] is True, 'Qualification did not pass'
PY
  bash scripts/memory_s1/launch_posttrain.sh "${COMMON[@]}" --output "$POST" --phase selection \
    --qualification-report "$QUAL/QUALIFICATION.json" --offline-from "$OFFLINE"
fi
