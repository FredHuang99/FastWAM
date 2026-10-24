#!/usr/bin/env bash
# PR on the within-episode pairs (pre-press vs post-press in put_back; arms at home between moves in swap):
# does the memory tell two moments of the SAME episode apart when they look alike now?
#   bash pr_within.sh <gpu>
# 1) CPU: where the pairs sit (scripts/memory_v2/inspect_within.py)
# 2) GPU: PR (val within pairs, both directions) for the C+256 base (memory_v2 off), D s17/s18/s19,
#    B-full s17/s18/s19, B0; then one table.
set -u
G=${1:?container GPU index}
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-8} MKL_NUM_THREADS=${MKL_NUM_THREADS:-8}
PY=/opt/mwam/bin/python
CFG=configs/memory_v2/train_v2_A.yaml
O=/workspace/FastWAM-memory2/outputs/memory_v2
PAIRS=$O/motion/pairs_within.json
OUT=$O/pr_within
log() { echo "[pr-within] $(date '+%F %T') $*"; }

used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G | tr -d ' ')
if [ "${used:-99999}" -gt 2000 ]; then
  log "GPU $G already has ${used} MiB in use: not starting (pick a free GPU)"; nvidia-smi; exit 1
fi
export CUDA_VISIBLE_DEVICES=$G
mkdir -p $OUT

log "where the pairs sit (CPU)"
$PY scripts/memory_v2/inspect_within.py $PAIRS

BFULL=$($PY -c "
import json; o=json.load(open('$O/v2_A_bfull/CONFIG.json'))['config']['memory_v2']['objective']
print(' '.join(f'--set memory_v2.objective.{k}={json.dumps(v)}' for k,v in o.items()))")

pr() { local run=$1 modes=$2; shift 2
  local ck=init; [ "$run" != base ] && ck=$O/$run/checkpoints/update_001340.pt
  if [ "$run" != base ] && [ ! -f "$ck" ]; then log "skip $run (no checkpoint)"; return; fi
  if ls $OUT/$run/pr_*_val.json >/dev/null 2>&1; then log "$run exists"; return; fi
  log "PR $run modes=$modes"
  $PY -m fastwam.memory_v2.train_v2 pr --config $CFG "$@" --checkpoint $ck --pairs $PAIRS --pair-split val \
    --set "eval.modes=$modes" --output $OUT/$run 2>&1 | grep -v "^\[pr\] [0-9]*/"
}
pr base '["off"]'
for s in "" _s18 _s19; do pr v2_A_cf$s '["on"]'; done
for s in "" _s18 _s19; do pr v2_A_bfull$s '["on"]' $BFULL; done
pr v2_A_b0 '["on"]'

log "table"
$PY - $OUT <<'PY'
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
print(f"{'run/mode':<22}{'task':<16}{'n':>4}{'own':>7}{'switch':>8}{'PR':>7}{'resp':>7}")
for d in sorted(out.iterdir()):
    for f in sorted(d.glob("pr_*_val.json")):
        s = json.loads(f.read_text())["summary"]
        for task in ("all", "put_back_block", "swap_blocks"):
            if task not in s:
                continue
            for mode, v in s[task].items():
                if mode == "n":
                    continue
                print(f"{d.name + '/' + mode:<22}{task:<16}{s[task]['n']:>4}{v['own_correct']:>7.2f}{v['switch']:>8.2f}"
                      f"{v['pr']:>7.2f}{v['response_median']:>7.2f}")
PY
log "all done"
