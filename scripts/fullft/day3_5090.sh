#!/usr/bin/env bash
# mwam5090, 11-13: W1 (plan v11/v12) + the N8b diagnosis.
#  1 fetch the Obs-AR export (obs_ar e30, H200 relay; sha256 checked)
#  2 W1: observe_and_pickup official scenes 1-50, execute 8, 10 steps, fixed pipeline (OIDN 2.0.1); shard 0/2 on GPU0 and
#    1/2 on GPU1 in parallel (each GPU must be empty for 90 s first); instruction text from the model's training cache
#    when the bank instruction is in it, else this machine's CPU T5 (logged)
#    Reading (plan v11 W1, unchanged): success >= 19/50 -> "win" level; 8-18 -> the usual WAM level; < 8 -> below peers.
#    Floor: finished >= 48/50; "grasped any object >= 25/50" needs an observe_and_pickup stage parser that does not
#    exist yet -> reported as NOT MEASURED (no verdict on that floor until the parser is written)
#  3 N8b diagnosis (plan v12, pre-registered): hist_probe.py on N7 e30 (ar_2task) -> history used or not (2 % rule)
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/day3_5090.sh
# Own log: outputs/fullft/DAY3_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$R/outputs/fullft/DAY3_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[day3] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=observe_and_pickup
E=$R/outputs/fullft/exports/obs_ar_e30
CK=$E/export_e30.pt
BANK=$O/closed_loop/scenes_seed42_n100_$T
L=obs_ar_e30
echo "[day3] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ -d $BANK ] || { echo "no scene bank $BANK: stopping"; exit 1; }
if [ ! -f $CK ]; then
  echo "[day3] $(date '+%F %T') ===== 1 fetching obs_ar e30"
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/obs_ar_e30 --repo hhyfred/memwam-fullft --out $E 2>&1 | grep -v "Processing\|Download\|%|"
fi
(cd $E && sha256sum -c export_e30.pt.sha256) || { echo "sha256 mismatch: delete $E and rerun"; exit 1; }
SRC=$($PY - <<'PYTXT'
import json, sys
from pathlib import Path
sys.path.insert(0, "/workspace/FastWAM-memory2/scripts/fullft")
from text_check import bank_instruction
want = bank_instruction("observe_and_pickup")
rows = json.loads(Path("/workspace/FastWAM-memory2/outputs/memory_v2/press/dense_observe_and_pickup_v1/RECORDS.json").read_text())
have = {r.get("instruction") for r in rows}
print("cache" if want and all(w in have for w in want) else "t5", len(want), sum(w in have for w in want), file=sys.stdout)
PYTXT
)
export MWAM_TEXT_SOURCE=${SRC%% *}
echo "[day3] bank instructions / found in the training cache: ${SRC#* } -> MWAM_TEXT_SOURCE=$MWAM_TEXT_SOURCE"
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
n_done() { ls $O/closed_loop/w1/$L/on/$T/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
lane() {   # GPU, shard
  until empty $1 && sleep 90 && empty $1; do sleep 120; done
  echo "[day3] $(date '+%F %T') ===== 2 W1 shard $2 on GPU $1"
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$1 $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L --scenes $BANK --tasks $T \
      --limit 50 --shard $2 --execute 8 --output $O/closed_loop/w1 >> $O/closed_loop/w1_${L}_$1.log 2>&1
    echo "[day3] $(date '+%F %T') shard $2 pass $pass exit code $?; finished $(n_done)"
  done
}
lane 0 0/2 & P0=$!
lane 1 1/2 & P1=$!
wait $P0 $P1      # never a bare `wait` after `exec > >(tee)`
echo "[day3] $(date '+%F %T') ===== W1 result (obs_ar e30, $T 1-50)"
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/w1 --label $L --out /dev/null 2>/dev/null | grep -E "/on|n=|errors" | head -n 6
$PY - <<'PYW1'
import json
from pathlib import Path
d = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/w1/obs_ar_e30/on/observe_and_pickup")
res = [json.loads(p.read_text()) for p in sorted(d.glob("seed_*/result.json")) if p.parent.name[5:].isdigit()]
n, s = len(res), sum(bool(r.get("success")) for r in res)
level = "win level (>= 19)" if s >= 19 else ("usual WAM level (8-18)" if s >= 8 else "below peers (< 8)")
print(f"W1: finished {n}/50 (floor >= 48: {'met' if n >= 48 else 'NOT met'}); success {s}/50 -> {level}; "
      f"grasp floor (>= 25/50 grasped any object): NOT MEASURED (no observe_and_pickup stage parser yet)")
PYW1
echo "[day3] $(date '+%F %T') ===== 3 N8b diagnosis: history used? (N7 e30, validation anchors)"
until empty 0 && sleep 90 && empty 0; do sleep 120; done
CUDA_VISIBLE_DEVICES=0 $PY scripts/fullft/hist_probe.py --export $R/outputs/fullft/exports/ar_2task_e30/export_e30.pt 2>&1 \
  | grep -vi warn | tail -n 6
