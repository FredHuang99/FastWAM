#!/usr/bin/env bash
# mwam5090, 11-24 evening, GPU 0 (user 18:52: GPU 0 may be used). After gpu0_night stopped at two checks (19:04):
#   1 card 5's text table again (press_told_text.py --relay): T5 now loaded from the press cache's own config, and the
#     pipeline check accepts the same tokens + relative L2 < 5 % (the first run: max |diff| 0.488, not bit-exact)
#   2 card 7's match-frame cache (match_build_5090.sh on GPU 0: checks, 50 episodes, then the cache relay)
#   3 card 8's render-check diagnosis (gen_diff.py, CPU, read-only): where the head camera differs; nothing generated
#     is used or uploaded
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/gpu0_fix_5090.sh
# Own log: outputs/fullft/GPU0_FIX_5090_<time>.txt (match_build writes MATCH_BUILD_5090_<time>.txt as well)
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/GPU0_FIX_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[fix] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo "[fix] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); $(nvidia-smi -i 0 --query-gpu=name,memory.used --format=csv,noheader)"
echo "[fix] ===== 1 card 5 text table"
CUDA_VISIBLE_DEVICES=0 /opt/mwam/bin/python scripts/fullft/press_told_text.py --relay 2>&1 | grep -v "Warning\|warn(\|has 0 check presses"
echo "[fix] press_told_text exit code ${PIPESTATUS[0]}"
echo "[fix] ===== 2 card 7 match cache"
MB_GPUS=0 bash scripts/fullft/match_build_5090.sh 2>&1 | tail -n 10
echo "[fix] match_build exit code ${PIPESTATUS[0]}"
echo "[fix] ===== 3 card 8 render-check diagnosis"
C=$F/gen_obs/check/demo_clean/observe_and_pickup/aloha_agilex/data
O=$R/outputs/memory_v2/press/demo_clean/observe_and_pickup/aloha_agilex/data
/opt/mwam/bin/python scripts/fullft/gen_diff.py --gen $C --official $O --n 3 2>&1 | grep -v "Warning\|warn("
echo "[fix] gen_diff exit code ${PIPESTATUS[0]}"
