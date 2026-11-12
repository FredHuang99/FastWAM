#!/usr/bin/env bash
# mwam5090, 5090 fix acceptance AL3 (11-12 13:50). Runs after the OIDN 2.0.1 render check PASSED (OIDN201_BUILD_sass120_
# 20261112_0409: 0 OIDN error lines; frame 0 vs the A100's 2.0.1: mean 0.062 levels, 0.00 % pixels > 8 levels; the
# pre-written bar was <= 0.10 levels and <= 0.05 %; 2.3.3 had 0.49 levels / 0.5 %).
# X7 (a2C_6ep update 4020), on, 10 steps, execute 8, with the fixed render pipeline MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib,
# on the scenes the A100 reference holds: put = the first 20 put scenes of the A100 export in bank order (= 31-50, as
# eq5090b RERUN), swap 1-20. Label x7_al3_oidn201, folder closed_loop/al3. Then
#   (a) decision 0 vs the A100's logged decision 0 (first_actions.py; refs relayed by diag_first.sh)
#   (b) pair_eq.py --rule n1 vs the A100's official X7 stages (check_from_a100/x7_official_stages.json)
# Readings (written 11-12 13:50, before the run):
#   (a) median arm RMSE of decision 0 vs the A100 (normalized units): target <= 0.003 per task. Expected from D1: about
#       N = 0.0024 (put) / 0.0047 (swap): the denoiser-version part V (0.0071 / 0.0126) should be gone, the rest is GPU ray
#       tracing + policy numerics (D2's A100 half splits them). With 2.3.3 it was 0.0066 / 0.0154.
#   (b) AL3 = plan v12 rule n1, unchanged: per task |mean paired progress diff| <= 0.05 and the 95 % CI contains 0, and
#       the 5090's key stage (put lifted, swap s1) >= 18/20; floor the A100's key stage >= 18/20. EQUIVALENT only if both
#       tasks pass. With 2.3.3 (eq5090b): put -0.117, swap -0.175. Expected: swap moves to about 0 (AL5: the denoiser
#       version is the CAUSE of swap); put is the open question (AL5: NOT CAUSE).
# Resumable (finished episodes are kept; two passes retry failed episodes).
#   docker exec -d -e GPU=0 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/al3_5090.sh
# Own log: outputs/fullft/align/AL3_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft/align/first
LOG=$R/outputs/fullft/align/AL3_5090_$(date +%Y%m%d_%H%M).txt
mkdir -p $R/outputs/fullft/align
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[al3] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[al3] $(date '+%F %T') ===== $*"; }
cd $R
GPU=${GPU:-0}
LIB=/opt/oidn-2.0.1-sass120/lib
[ -e $LIB/libOpenImageDenoise.so.2 ] || { echo "$LIB has no libOpenImageDenoise.so.2: run oidn201_build.sh first"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=$LIB
PY=/opt/mwam/bin/python
CK=$O/a2C_6ep/checkpoints/update_004020.pt
REF=$O/closed_loop/check_from_a100/x7_official_stages.json
OUT=$O/closed_loop/al3
L=x7_al3_oidn201
[ -f $REF ] || { echo "missing $REF (relay diag/a100_x7_stages)"; exit 1; }
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU | tr -d ' '; }
until [ "$(used)" -lt 2000 ]; do echo "[al3] $(date '+%F %T') GPU $GPU busy; waiting"; sleep 300; done
echo "GPU $GPU: $(used) MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); MWAM_OIDN_LIB=$MWAM_OIDN_LIB"

PUT_SEEDS=$($PY - <<'PYSEEDS'
import json
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
ref = json.loads((O / "closed_loop/check_from_a100/x7_official_stages.json").read_text())["episodes"]["put_back_block"]
order = []
for f in sorted((O / "closed_loop/scenes_seed42_n100_put_back_block").glob("*.json")):
    v = json.loads(f.read_text())
    sc = v.get("scenes") if isinstance(v, dict) else v
    order += [int(s["seed"]) for s in (sc if isinstance(sc, list) else []) if s["task"] == "put_back_block"]
pick = [s for s in order if str(s) in ref][:20]
print(" ".join(f"put_back_block:{s}" for s in pick))
PYSEEDS
)
[ -n "$PUT_SEEDS" ] || { echo "no A100 put scenes found: stopping"; exit 1; }
echo "put scenes (first 20 the A100 export holds, bank order): $PUT_SEEDS"

run_bank() {   # task, N, optional seed list
  step "closed loop $1 (X7 on, 10 steps, execute 8, OIDN 2.0.1 sass120)"
  for pass in 1 2; do
    $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L --scenes $O/closed_loop/scenes_seed42_n100_$1 \
      --tasks "$1" --limit "$2" ${3:+--seeds $3} --execute 8 --output $OUT >> $OUT.log 2>&1
    echo "pass $pass exit code $?; finished: $(ls $OUT/$L/on/$1/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
  done
}
mkdir -p $OUT
run_bank put_back_block 20 "$PUT_SEEDS"
echo "denoiser line: $(grep -m1 'Open Image Denoise' $OUT.log)"
echo "OIDN errors so far: $(grep -c 'OIDN Error' $OUT.log)"
$PY scripts/fullft/first_actions.py export --name 5090_x7_oidn201 --folders closed_loop/al3 --label $L
cmpf() { [ -f $F/$1.json ] && [ -f $F/$2.json ] && $PY scripts/fullft/first_actions.py compare $1.json $2.json 2>&1 | grep -v "^  timing" || echo "missing $1 or $2"; }
step "(a) decision 0, put: vs the A100 (target <= 0.003), and vs this machine with 2.3.3"
cmpf a100_x7_ref_put 5090_x7_oidn201
cmpf 5090_x7 5090_x7_oidn201
run_bank swap_blocks 20
echo "OIDN errors in the run log: $(grep -c 'OIDN Error' $OUT.log)"
$PY scripts/fullft/first_actions.py export --name 5090_x7_oidn201 --folders closed_loop/al3 --label $L
step "(a) decision 0, both tasks: vs the A100 (target <= 0.003), and vs this machine with 2.3.3"
cmpf a100_x7_ref_put 5090_x7_oidn201
cmpf a100_x7_ref_swap 5090_x7_oidn201
cmpf 5090_x7 5090_x7_oidn201
step "(b) AL3 verdict (rule n1, plan v12, unchanged)"
$PY scripts/fullft/pair_eq.py --name al3_oidn201 --rule n1 --a-folders closed_loop/al3 --a-label $L --b-json $REF \
  --tasks put_back_block swap_blocks 2>&1 | grep -vi warn | tail -n 12
