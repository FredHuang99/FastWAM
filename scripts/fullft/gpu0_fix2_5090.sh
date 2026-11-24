#!/usr/bin/env bash
# mwam5090, 11-24 19:30, GPU 0. After gpu0_fix (19:26): the text table is on the relay; two things left:
#   1 card 7's match cache: the plain zoom cache lives in zoom_dense_observe_and_pickup_v1_02102ba0 on this machine (the
#     builder looked for zoom_obs_02102ba0, its relay name) -> fixed; fetched from the relay if neither folder is here
#   2 card 8's diagnosis again (gen_diff.py, CPU, read-only): the first run's "OUTSIDE ..." line was wrong (a box past the
#     image edge wrapped around); now: the part outside both boxes, and whether the objects sit at the same places
#   also prints the text table's pipeline-check line (relative L2) from the 19:13 log
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/gpu0_fix2_5090.sh
# Own log: outputs/fullft/GPU0_FIX2_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/GPU0_FIX2_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[fix2] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo "[fix2] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); $(nvidia-smi -i 0 --query-gpu=name,memory.used --format=csv,noheader)"
echo "[fix2] text table, from $(ls -t $F/GPU0_FIX_5090_*.txt | head -1):"
grep "pipeline check\|told texts\|demo texts" $(ls -t $F/GPU0_FIX_5090_*.txt | head -1) | cut -c1-300
echo "[fix2] ===== 1 card 7 match cache"
MB_GPUS=0 bash scripts/fullft/match_build_5090.sh 2>&1 | grep -v "Warning\|warn(" | grep -v "^\[match-build\] [a-z_]*/episode_00000\(0[3-9]\|[1-3][0-9]\|4[0-8]\): " | tail -n 16
echo "[fix2] match_build exit code ${PIPESTATUS[0]}"
echo "[fix2] ===== 2 card 8 render-check diagnosis"
C=$F/gen_obs/check/demo_clean/observe_and_pickup/aloha_agilex/data
O=$R/outputs/memory_v2/press/demo_clean/observe_and_pickup/aloha_agilex/data
/opt/mwam/bin/python scripts/fullft/gen_diff.py --gen $C --official $O --n 3 2>&1 | grep -v "Warning\|warn(\|glob order"
echo "[fix2] gen_diff exit code ${PIPESTATUS[0]}"
