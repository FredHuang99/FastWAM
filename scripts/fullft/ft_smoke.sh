#!/usr/bin/env bash
# Any evaluation machine (11-11, before the first real N7 export arrives): the fullft closed loop end to end with an
# export built from the RELEASED FastWAM weights (fake_export.py; gates 0 = the released model, label *_smoke, numbers
# never compared): model files, VAE / T5 / tokenizer, encoders, the session, the simulator, the result summary.
#   1 fake export (CPU, ~10 GiB file, once)   2 closed loop: put scene 1, 16 targets, execute 8, on GPU ${GPU:-0}
#   PASS = a result.json with executed_targets 16 and no ERROR.json
#   docker exec -e GPU=0 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/ft_smoke.sh
# Own log: outputs/fullft/FT_SMOKE_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$R/outputs/fullft/FT_SMOKE_$(date +%Y%m%d_%H%M).txt
mkdir -p $R/outputs/fullft
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[smoke] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
E=$R/outputs/fullft/exports/release_smoke/export_e0.pt
$PY scripts/fullft/fake_export.py --out $E || exit 1
rm -rf $O/closed_loop/ft_smoke/release_smoke
$PY -m fastwam.memory_v2.online run --checkpoint $E --label release_smoke --scenes $O/closed_loop/scenes_seed42_n100_put_back_block \
  --tasks put_back_block --limit 1 --execute 8 --max-targets 16 --output $O/closed_loop/ft_smoke > $O/closed_loop/ft_smoke.log 2>&1
echo "run exit code $?"
grep -E "\[closed-loop\]|\[decide\]|Error|error" $O/closed_loop/ft_smoke.log | tail -n 12
D=$(ls -d $O/closed_loop/ft_smoke/release_smoke/on/put_back_block/seed_* 2>/dev/null | grep -E 'seed_[0-9]+$' | head -1)
if [ -n "$D" ] && [ -f $D/result.json ] && [ ! -f $D/ERROR.json ]; then
  echo "result: $(head -c 300 $D/result.json)"; echo "decisions logged: $(wc -l < $D/decisions.jsonl)"
  echo "FT SMOKE PASS"
else
  echo "FT SMOKE FAIL"; [ -n "$D" ] && cat $D/ERROR.json 2>/dev/null | head -c 3000; exit 1
fi
