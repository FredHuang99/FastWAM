#!/usr/bin/env bash
# mwam5090 fillers, 11-12 evening (DESCRIPTIVE, no verdict), between the e20 progress check and the e30 export (~01:40).
# Two lanes, one per GPU. Each lane first waits until eval_watch's e20 run of ITS GPU has 50 finished episodes (so it never
# races eval_watch for a card, as happened at 14:43), then until its GPU has been empty for 90 s.
#   GPU1: X1, then X2-put        GPU0: X2-swap
# X1 (AL3 extension): X7 (a2C_6ep update 4020), fixed pipeline (OIDN 2.0.1 sass120), on, 10 steps, execute 8, put scenes
#   = the NEXT 50 put scenes of the A100's official X7 export in bank order (after the 20 AL3 ran: scenes 51-100); same
#   label as AL3 (x7_al3_oidn201, closed_loop/al3), so the paired table vs the A100 grows to n = 70. AL3 stays as judged.
#   Reading (written 11-12 16:20, before the run), paired progress difference 5090 - A100 at n = 70:
#     CI upper < 0                         -> a real residual put gap of X7 on the 5090 after the fix
#                                             (X7 tables stay on the A100, as now)
#     |mean| <= 0.05 and CI contains 0     -> the n = 20 gap (-0.067) was chance
#     otherwise                            -> undetermined
# X2 (text source A/B on the new base): N7 e20, MWAM_TEXT_SOURCE=t5 (this machine's CPU T5, as e10 ran; 2.4 % off the
#   training text), OIDN 2.0.1, scenes 1-50, both tasks, label ar_2task_e20_t5 (closed_loop/textab), paired with the cache
#   run (ar_2task_e20, closed_loop/g1, eval_watch) by pair_eq --rule report.
#   Reading (written before the run): |mean| <= 0.05 and CI contains 0 on both tasks -> the text source does not move the
#   new base (the 2.5 % shift is harmless); otherwise it does, and the cache switch removed a real difference.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/night2_5090.sh
# Own log: outputs/fullft/NIGHT2_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$R/outputs/fullft/NIGHT2_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[night2] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib
PY=/opt/mwam/bin/python
X7=$O/a2C_6ep/checkpoints/update_004020.pt
E20=$R/outputs/fullft/exports/ar_2task_e20/export_e20.pt
REF=$O/closed_loop/check_from_a100/x7_official_stages.json
[ -e $MWAM_OIDN_LIB/libOpenImageDenoise.so.2 ] && [ -f $X7 ] && [ -f $E20 ] && [ -f $REF ] || { echo "missing input: stopping"; exit 1; }
echo "[night2] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
n_done() { ls $1/on/$2/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
empty() { [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' ')" -lt 2000 ]; }
claim() {   # GPU, task of eval_watch's e20 run on it
  until [ "$(n_done $O/closed_loop/g1/ar_2task_e20 $2)" -ge 50 ]; do sleep 300; done
  until empty $1 && sleep 90 && empty $1; do sleep 120; done
  echo "[night2] $(date '+%F %T') GPU $1 claimed"
}
loop() {    # GPU, label, checkpoint, task, output folder, extra args...
  local g=$1 l=$2 ck=$3 t=$4 out=$5; shift 5
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=$g $PY -m fastwam.memory_v2.online run --checkpoint $ck --label $l \
      --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --execute 8 --output $O/closed_loop/$out "$@" \
      >> $O/closed_loop/${out}_$l.log 2>&1
    echo "[night2] $(date '+%F %T') $l $t pass $pass exit code $?; finished $(n_done $O/closed_loop/$out/$l $t)"
  done
}
lane1() {
  claim 1 put_back_block
  SEEDS=$($PY - <<'PYSEEDS'
import json
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
ref = json.loads((O / "closed_loop/check_from_a100/x7_official_stages.json").read_text())["episodes"]["put_back_block"]
order = []
for f in sorted((O / "closed_loop/scenes_seed42_n100_put_back_block").glob("*.json")):
    v = json.loads(f.read_text())
    sc = v.get("scenes") if isinstance(v, dict) else v
    order += [int(s["seed"]) for s in (sc if isinstance(sc, list) else []) if s["task"] == "put_back_block"]
pick = [s for s in order if str(s) in ref][20:70]
print(" ".join(f"put_back_block:{s}" for s in pick))
PYSEEDS
)
  echo "[night2] X1 put scenes ($(echo $SEEDS | wc -w)): $(echo $SEEDS | cut -c1-80) ..."
  loop 1 x7_al3_oidn201 $X7 put_back_block al3 --seeds $SEEDS
  echo "[night2] $(date '+%F %T') ===== X1 paired vs the A100 (n = 70 put; report)"
  $PY scripts/fullft/pair_eq.py --name al3x_put70 --rule report --a-folders closed_loop/al3 --a-label x7_al3_oidn201 \
    --b-json $REF --tasks put_back_block 2>&1 | grep -vi warn | tail -n 3
  MWAM_TEXT_SOURCE=t5 loop 1 ar_2task_e20_t5 $E20 put_back_block textab --limit 50
}
lane0() {
  claim 0 swap_blocks
  MWAM_TEXT_SOURCE=t5 loop 0 ar_2task_e20_t5 $E20 swap_blocks textab --limit 50
}
lane1 & P1=$!
lane0 & P0=$!
wait $P1 $P0     # never a bare `wait` after `exec > >(tee)`
echo "[night2] $(date '+%F %T') ===== X2 text source: t5 (A) vs cache (B), e20, scenes 1-50 (report)"
$PY scripts/fullft/pair_eq.py --name textab_e20 --rule report --a-folders closed_loop/textab --a-label ar_2task_e20_t5 \
  --b-folders closed_loop/g1 --b-label ar_2task_e20 --tasks put_back_block swap_blocks 2>&1 | grep -vi warn | tail -n 4
