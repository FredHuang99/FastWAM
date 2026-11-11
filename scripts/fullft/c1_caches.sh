#!/usr/bin/env bash
# mwam5090 container, GPU ${GPU:-1} (plan v10 node C1): dense caches (single-frame latents, clip latents of every
# anchor, text, normalised proprio / actions) of the 7 RMBench tasks that have none yet, in the exact two-task format
# (scripts/memory_v2/press/build_dense.py build; 45 train / 5 val, seed-17 split). Resumable: a finished episode is
# skipped, a finished task too. The full fine-tuning trainer (fullft/data.py) reads these folders as data.roots.
# Pre-registered (F.1 C1): per task, cached frames == demo frames (CACHE.json) and every episode has COMPLETE.json;
# non-degenerate floor: >= 45 episodes per task. A task that fails is reported and the next one runs.
# Own log: outputs/memory_v2/report/C1_CACHES_<time>.txt
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/c1_caches.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/C1_CACHES_$(date +%Y%m%d_%H%M).txt
mkdir -p $O/report
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c1] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
GPU=${GPU:-1}
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU
PY=/opt/mwam/bin/python
TASKS=${TASKS:-"observe_and_pickup swap_T rearrange_blocks battery_try cover_blocks blocks_ranking_try place_block_mat"}
for t in $TASKS; do
  echo; echo "[c1] $(date '+%F %T') ===== $t"
  n=$(ls $O/press/demo_clean/$t/aloha_agilex/data/*.hdf5 2>/dev/null | wc -l)
  echo "[c1] demos: $n"
  [ "$n" -ge 45 ] || { echo "[c1] $t: fewer than 45 demos (floor): skipped"; continue; }
  if [ -f $O/press/dense_${t}_v1/CACHE.json ]; then echo "[c1] $t: already cached"; else
    $PY scripts/memory_v2/press/build_dense.py build --task $t > $O/report/c1_${t}.log 2>&1
    echo "[c1] build exit code $?"; tail -n 3 $O/report/c1_${t}.log
  fi
  done_eps=$(ls $O/press/dense_${t}_v1/cache/*/COMPLETE.json 2>/dev/null | wc -l)
  echo "[c1] $t: episodes with COMPLETE.json $done_eps / $n; CACHE.json: $(cat $O/press/dense_${t}_v1/CACHE.json 2>/dev/null)"
done
du -sh $O/press/dense_*_v1 2>/dev/null
