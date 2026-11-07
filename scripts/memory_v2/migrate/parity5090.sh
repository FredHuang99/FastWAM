#!/usr/bin/env bash
# mwam5090 container (11-07): offline numerics parity RTX 5090 vs A100, before any 5090 result is used in a verdict.
# X7 (a2C_6ep/update_004020, the weights-only copy shipped by delta_5090) is evaluated on ALL val windows with the
# run's saved config, exactly as the A100's S1-offline (steps_sweep.py, 11-06 22:12) did, at 10 and 1 Euler steps,
# modes on / null, the same per-window noise. Each result is compared with the A100's JSON
# (a2C_6ep/eval_steps/steps_<k>/update_004020.json) by manifest.py compare: PASS when every arm-RMSE metric is within
# 3 % (relative; the tolerance of the H100 migration check), else FAIL. The A100 files are never overwritten.
# Own log: /workspace/FastWAM-memory2/outputs/memory_v2/parity_5090/PARITY.log (append; last line = exit code).
#   GPU=<container GPU index, default 1> bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/parity5090.sh
set -euo pipefail
O=/workspace/FastWAM-memory2/outputs/memory_v2
OUT=$O/parity_5090
RUN=$O/a2C_6ep
CK=$RUN/checkpoints/update_004020.pt
PY=/opt/mwam/bin/python
mkdir -p "$OUT"
exec > >(tee -a "$OUT/PARITY.log") 2>&1
trap 'rc=$?; echo "[parity] $(date "+%F %T") finished, exit code $rc"' EXIT
step() { echo "[parity] $(date '+%F %T') $*"; }
cd /workspace/FastWAM-memory2
export PYTHONPATH=/workspace/FastWAM-memory2/src CUDA_VISIBLE_DEVICES=${GPU:-1}
for f in "$CK" "$RUN/CONFIG.json" "$RUN/eval_steps/steps_10/update_004020.json" "$RUN/eval_steps/steps_1/update_004020.json"; do
  [ -f "$f" ] || { step "missing $f (shipped by delta_5090; rerun h100_restore.sh delta)"; exit 1; }
done
$PY - "$RUN/CONFIG.json" "$OUT/run_config.yaml" <<'PY'
import json, sys
saved = json.load(open(sys.argv[1]))
open(sys.argv[2], "w").write(json.dumps(saved["config"], indent=1))   # JSON is valid YAML (load_config reads JSON first)
PY
fail=0
for k in 10 1; do
  target=$OUT/steps_$k/update_004020.json
  if [ ! -f "$target" ]; then
    step "evaluate X7 at $k Euler steps on all val windows (GPU $CUDA_VISIBLE_DEVICES)"
    $PY -m fastwam.memory_v2.train_v2 evaluate --config "$OUT/run_config.yaml" --checkpoint "$CK" --windows 0 \
      --output "$OUT/steps_$k" --set memory_v2.guidance.steps=$k --set 'eval.modes=["on","null"]' --set 'eval.guidance_scales=[]'
  fi
  step "steps=$k: A100 (S1-offline, 11-06) vs 5090"
  /opt/hf-tools/bin/python /workspace/FastWAM-memory2/scripts/memory_v2/migrate/manifest.py compare \
    "$RUN/eval_steps/steps_$k/update_004020.json" "$target" --tol 0.03 | sed 's/A100        H100/A100        5090/' || fail=1
done
if [ $fail = 0 ]; then step "PARITY PASS: 5090 offline errors within 3 % of the A100 at 10 and 1 steps"; else step "PARITY FAIL (see the tables above)"; fi
exit $fail
