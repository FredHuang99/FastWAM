#!/usr/bin/env bash
# mwam5090, 11-12 evening, between the e20 progress check and the e30 export (~01:40). Two lanes, one per GPU. Each lane
# first waits until eval_watch's e20 run on ITS GPU has 50 finished episodes (so it never races eval_watch for a card, as
# at 14:43), then until its GPU has been empty for 90 s.
#   GPU1: T0 -> T1 -> T2 (AL3b) -> X2-put          GPU0: X2-swap -> X1
# Common: X7 = a2C_6ep update 4020; render fix MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib; on, 10 steps, execute 8.
#
# T (written 11-12 16:25, after AL3 = NOT EQUIVALENT: put -0.067 [-0.200, +0.050], swap -0.133 [-0.242, -0.033];
#    decision 0 vs the A100 put 0.0025, swap 0.0069). Hypothesis: the largest input difference left is the instruction
#    text: the X7 policy encodes it with T5 on the GPU on the A100 (40 GB card) and on the CPU on the 5090 (32 GB).
#  T0 encode the two bank instructions on this machine's GPU once (text_dump.py; the A100's path), also vs the CPU path.
#  T1 decision 0 only (--max-targets 8) with that text (MWAM_TEXT_FILE), AL3's scenes (put = the first 20 A100-held put
#     scenes = 31-50, swap 1-20), vs the A100's logged decision 0. Reading: median arm RMSE vs the A100
#       <= 0.5 x the CPU-text value on both tasks (put <= 0.00125, swap <= 0.0035) -> the text was the main residual
#       >= 0.8 x on both                                                         -> the text is minor (ray tracing, VAE, DiT)
#       otherwise                                                                -> partial
#  T2 = AL3b, a NEW verdict registered here before the run (AL3 stays NOT EQUIVALENT as judged): AL3's runs with the
#     GPU-encoded text, label x7_al3b_t5gpu (closed_loop/al3b), plan v12 rule n1 unchanged (per task |mean paired
#     progress diff| <= 0.05 and CI contains 0, the 5090's key stage >= 18/20; floor the A100's key stage >= 18/20).
#     EQUIVALENT -> for X7-type policies the 5090 needs the GPU-encoded text (precomputed) on top of the render fix.
# X2 (text source A/B on the new base, descriptive): N7 e20, MWAM_TEXT_SOURCE=t5 (this machine's CPU T5, as e10 ran),
#   scenes 1-50, both tasks, label ar_2task_e20_t5 (closed_loop/textab), paired with the cache run (ar_2task_e20) by
#   pair_eq --rule report. Reading: |mean| <= 0.05 and CI contains 0 on both tasks -> the text source does not move the
#   new base; otherwise it does, and the cache switch removed a real difference.
# X1 (AL3 extension, descriptive): X7 with the CPU text as AL3, put = the NEXT 50 A100-held put scenes (51-100), same
#   label as AL3 -> paired n = 70. Reading: CI upper < 0 -> a real residual put gap with the CPU text; |mean| <= 0.05 and
#   CI contains 0 -> the n = 20 gap was chance; otherwise undetermined.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/night2_5090.sh
# Own log: outputs/fullft/NIGHT2_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft/align/first
LOG=$R/outputs/fullft/NIGHT2_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[night2] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib
PY=/opt/mwam/bin/python
X7=$O/a2C_6ep/checkpoints/update_004020.pt
E20=$R/outputs/fullft/exports/ar_2task_e20/export_e20.pt
REF=$O/closed_loop/check_from_a100/x7_official_stages.json
TXT=$R/outputs/fullft/align/text/x7_t5gpu_5090.pt
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
put_seeds() {   # the A100-held put scenes in bank order, [from:to)
  $PY - $1 $2 <<'PYSEEDS'
import json, sys
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
ref = json.loads((O / "closed_loop/check_from_a100/x7_official_stages.json").read_text())["episodes"]["put_back_block"]
order = []
for f in sorted((O / "closed_loop/scenes_seed42_n100_put_back_block").glob("*.json")):
    v = json.loads(f.read_text())
    sc = v.get("scenes") if isinstance(v, dict) else v
    order += [int(s["seed"]) for s in (sc if isinstance(sc, list) else []) if s["task"] == "put_back_block"]
pick = [s for s in order if str(s) in ref][int(sys.argv[1]):int(sys.argv[2])]
print(" ".join(f"put_back_block:{s}" for s in pick))
PYSEEDS
}
cmpf() { [ -f $F/$1.json ] && [ -f $F/$2.json ] && $PY scripts/fullft/first_actions.py compare $1.json $2.json 2>&1 | grep -v "^  timing" || echo "missing $1 or $2"; }
lane1() {
  claim 1 put_back_block
  P20=$(put_seeds 0 20)
  echo "[night2] $(date '+%F %T') ===== T0 instruction text on this GPU (the A100's path)"
  CUDA_VISIBLE_DEVICES=1 $PY scripts/fullft/text_dump.py --device cuda --out $TXT --cpu-too 2>&1 | grep -vi warn
  [ -f $TXT ] || { echo "[night2] T0 failed: T1 / T2 skipped"; }
  if [ -f $TXT ]; then
    echo "[night2] $(date '+%F %T') ===== T1 decision 0 with the GPU-encoded text"
    MWAM_TEXT_FILE=$TXT loop 1 x7_t5gpu_first $X7 put_back_block al3b_first --seeds $P20 --max-targets 8
    MWAM_TEXT_FILE=$TXT loop 1 x7_t5gpu_first $X7 swap_blocks al3b_first --limit 20 --max-targets 8
    $PY scripts/fullft/first_actions.py export --name 5090_x7_t5gpu --folders closed_loop/al3b_first --label x7_t5gpu_first
    cmpf a100_x7_ref_put 5090_x7_t5gpu
    cmpf a100_x7_ref_swap 5090_x7_t5gpu
    echo "  (CPU text, AL3: put 0.0025, swap 0.0069; the text alone, CPU vs GPU text on the same images:)"
    cmpf 5090_x7_oidn201 5090_x7_t5gpu
    echo "[night2] $(date '+%F %T') ===== T2 = AL3b closed loop with the GPU-encoded text"
    MWAM_TEXT_FILE=$TXT loop 1 x7_al3b_t5gpu $X7 put_back_block al3b --seeds $P20
    MWAM_TEXT_FILE=$TXT loop 1 x7_al3b_t5gpu $X7 swap_blocks al3b --limit 20
    echo "OIDN errors in the AL3b logs: $(cat $O/closed_loop/al3b_*.log | grep -c 'OIDN Error')"
    echo "[night2] $(date '+%F %T') ===== AL3b verdict (rule n1, registered 11-12 16:25)"
    $PY scripts/fullft/pair_eq.py --name al3b_t5gpu --rule n1 --a-folders closed_loop/al3b --a-label x7_al3b_t5gpu \
      --b-json $REF --tasks put_back_block swap_blocks 2>&1 | grep -vi warn | tail -n 4
  fi
  MWAM_TEXT_SOURCE=t5 loop 1 ar_2task_e20_t5 $E20 put_back_block textab --limit 50
}
lane0() {
  claim 0 swap_blocks
  MWAM_TEXT_SOURCE=t5 loop 0 ar_2task_e20_t5 $E20 swap_blocks textab --limit 50
  P70=$(put_seeds 20 70)
  echo "[night2] X1 put scenes: $(echo $P70 | wc -w)"
  loop 0 x7_al3_oidn201 $X7 put_back_block al3 --seeds $P70
  echo "[night2] $(date '+%F %T') ===== X1 paired vs the A100 (n = 70 put; report)"
  $PY scripts/fullft/pair_eq.py --name al3x_put70 --rule report --a-folders closed_loop/al3 --a-label x7_al3_oidn201 \
    --b-json $REF --tasks put_back_block 2>&1 | grep -vi warn | tail -n 3
}
lane1 & P1=$!
lane0 & P0=$!
wait $P1 $P0     # never a bare `wait` after `exec > >(tee)`
echo "[night2] $(date '+%F %T') ===== X2 text source: t5 (A) vs cache (B), e20, scenes 1-50 (report)"
$PY scripts/fullft/pair_eq.py --name textab_e20 --rule report --a-folders closed_loop/textab --a-label ar_2task_e20_t5 \
  --b-folders closed_loop/g1 --b-label ar_2task_e20 --tasks put_back_block swap_blocks 2>&1 | grep -vi warn | tail -n 4
