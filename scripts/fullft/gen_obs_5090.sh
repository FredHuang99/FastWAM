#!/usr/bin/env bash
# mwam5090, 11-24 (Opus; plan v20 card 8; user 11-24: the benchmark's own generation script may be run, > 50 demos).
# observe_and_pickup scenes from the benchmark's own scripted expert, on GPU ${GEN_GPU:-0}:
#   1 render check FIRST: the first 3 seeds of the official demos' seed.txt regenerated (fastwam.memory_v2.online gen:
#     RMBench's collect_data.py unmodified, its seed loop moved, the closed loop's render environment) and compared with
#     the official episodes 0-2 (gen_check.py: per camera mean |diff| <= 1 level, > 8 levels on < 2 % of the pixels).
#     FAIL -> stop and report; nothing generated is used for training
#   2 155 new scenes from seed 10,000,000 upwards (disjoint from the official demos' seeds, the seed-42 evaluation bank
#     (4,300,000+) and the 5090 development banks (1,800,000-2,100,000)) -> with the 45 official training demos = 200
#   3 their dense cache (build_dense.py build --val 0 on a folder of renamed links gen_<seed>, so episode ids never clash
#     with the official ones) -> the cache relay (cache_relay.py put) as dense_observe_and_pickup_gen155_v1
#   4 then 600 more (for 800), cached the same way as dense_observe_and_pickup_gen600_v1
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/gen_obs_5090.sh
# GEN_GATE=background (11-24 19:30; ONLY after the user agrees): the render check compares the head camera outside the
#   shelf and table boxes (gen_check.py --gate background), and before each cache is built and uploaded the overall
#   statistics must pass (gen_stats.py). Default GEN_GATE=pixel = the original check.
# GEN_HOLD=1 (11-24 20:05): generate only -- the render check and the statistics are run and printed but block nothing,
#   and NO cache is built, NOTHING is uploaded (a training slot can only pick an uploaded cache). Generation is resumable:
#   the later run without GEN_HOLD (after the user agrees) skips what exists and goes on to the checks, cache, upload.
# GEN_BUILD=gen155 | gen600 (11-24 20:40, user 20:31 "card 8: the backup gate"): no generation -- the statistics check,
#   the cache and the upload of one batch already generated (runs beside a generating process; uses GEN_GPU too).
# Own log: outputs/fullft/GEN_OBS_5090_<time>.txt ; generator logs outputs/fullft/gen_obs/*.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
P=$R/outputs/memory_v2/press
G=$F/gen_obs
LOG=$F/GEN_OBS_5090_$(date +%Y%m%d_%H%M).txt
mkdir -p $G
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[genobs] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=observe_and_pickup
GPU=${GEN_GPU:-0}
GATE=${GEN_GATE:-pixel}
HOLD=${GEN_HOLD:-0}
say() { echo "[genobs] $(date '+%F %T') $*"; }
say "checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $GPU ($(nvidia-smi -i $GPU --query-gpu=name,memory.used --format=csv,noheader 2>&1))"
OFF=""
for d in /workspace/FastWAM/resources/RMBench/data/demo_clean/$T/aloha_agilex $P/demo_clean/$T/aloha_agilex; do
  [ -f $d/seed.txt ] && [ -d $d/data ] && { OFF=$d; break; }
done
[ -n "$OFF" ] || { say "no official seed.txt next to the official demos: the seed-matched render check is impossible; stop (report)"; exit 1; }
SEEDS=$(cat $OFF/seed.txt | tr -s ' \n' ' ' | xargs -n1 | head -n 3 | tr '\n' ' ')
say "official demos $OFF ($(ls $OFF/data/*.hdf5 | wc -l) hdf5); first seeds: $SEEDS; their max $(cat $OFF/seed.txt | xargs -n1 | sort -n | tail -1)"
gen() {     # out, extra args...
  local out=$1; shift
  CUDA_VISIBLE_DEVICES=$GPU $PY -m fastwam.memory_v2.online gen --tasks $T --output $out "$@" >> $out.log 2>&1
}
C=$G/check
if [ ! -f $G/GEN_CHECK.json ] || ! grep -q '"pass": true' $G/GEN_CHECK.json || ! grep -q "\"gate\": \"$GATE\"" $G/GEN_CHECK.json; then
  say "===== 1 render check ($GATE): seeds $SEEDS"
  if [ ! -f $C/demo_clean/$T/aloha_agilex/data/episode_0000002.hdf5 ]; then
    mkdir -p $C; gen $C --gen-seeds $SEEDS; say "gen exit code $? ($(tail -n 1 $C.log | cut -c1-160))"
  fi
  if ! $PY scripts/fullft/gen_check.py --gen $C/demo_clean/$T/aloha_agilex/data --official $OFF/data --n 3 --gate $GATE; then
    [ "$HOLD" = 1 ] || { say "RENDER CHECK FAILED: stop; nothing generated goes into training (report to Opus)"; exit 1; }
    say "render check ($GATE) FAILED -- HOLD mode: generating anyway; nothing is built or uploaded"
  else
    say "render check ($GATE) passed"
  fi
else
  say "render check ($GATE) passed earlier"
fi
build() {   # name, source dir (demo_clean/<task>/aloha_agilex), offset
  local name=$1 src=$2 L=$G/links_$1
  [ -f $P/$name/CACHE.json ] && { say "$name cached already"; return 0; }
  if [ "$GATE" = background ] || [ "$HOLD" = 1 ]; then
    $PY scripts/fullft/gen_stats.py --gen $src --official $OFF 2>&1 | grep -v "Warning\|warn("
    st=${PIPESTATUS[0]}
    [ "$HOLD" = 1 ] && { say "$name: HOLD -- statistics printed (exit $st); no cache, no upload until the user agrees"; return 0; }
    [ $st = 0 ] || { say "$name: OVERALL STATISTICS FAILED: no cache, no upload (report to Opus)"; return 1; }
  fi
  rm -rf $L; mkdir -p $L/data $L/instruction
  for f in $src/data/episode_*.hdf5; do
    k=$(basename $f .hdf5); k=${k#episode_}; s=$(cat $src/seed.txt | xargs -n1 | sed -n "$((10#$k + 1))p")
    ln -s $f $L/data/gen_$s.hdf5
    [ -f $src/instruction/episode_$k.json ] && cp $src/instruction/episode_$k.json $L/instruction/gen_$s.json
  done
  say "$name: $(ls $L/data | wc -l) episodes -> build_dense (val 0)"
  CUDA_VISIBLE_DEVICES=$GPU $PY scripts/memory_v2/press/build_dense.py build --task $T --raw $L/data --out $P/$name --val 0 \
    > $G/build_$name.log 2>&1; say "build exit code $? ($(tail -n 1 $G/build_$name.log | cut -c1-160))"
  [ -f $P/$name/CACHE.json ] || { say "$name: no CACHE.json"; return 1; }
  $HFPY scripts/fullft/cache_relay.py put $P/$name 2>&1 | tail -n 2
  $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx $name && say "$name on the cache relay" || say "$name: UPLOAD FAILED"
}
if [ -n "${GEN_BUILD:-}" ]; then
  [ "$GATE" = background ] && [ "$HOLD" != 1 ] || { say "GEN_BUILD needs GEN_GATE=background without GEN_HOLD: stop"; exit 1; }
  S=$G/$GEN_BUILD/demo_clean/$T/aloha_agilex
  [ -f $S/GEN.json ] && grep -q '"finished"' $S/GEN.json || { say "$GEN_BUILD: generation not finished ($S/GEN.json): stop"; exit 1; }
  say "===== build only: $GEN_BUILD ($(ls $S/data/*.hdf5 | wc -l) hdf5); GPU $GPU $(nvidia-smi -i $GPU --query-gpu=memory.used,memory.total --format=csv,noheader)"
  build dense_${T}_${GEN_BUILD}_v1 $S; rc=$?
  say "build only $GEN_BUILD: exit code $rc"
  exit $rc
fi
A=$G/gen155
say "===== 2 155 scenes from seed 10000000"
gen $A --start-seed 10000000 --episodes 155; say "gen exit code $?; $(ls $A/demo_clean/$T/aloha_agilex/data/*.hdf5 2>/dev/null | wc -l) hdf5"
build dense_${T}_gen155_v1 $A/demo_clean/$T/aloha_agilex || exit 1
B=$G/gen600
NEXT=$(( $(cat $A/demo_clean/$T/aloha_agilex/seed.txt | xargs -n1 | sort -n | tail -1) + 1 ))
say "===== 4 600 more from seed $NEXT"
gen $B --start-seed $NEXT --episodes 600; say "gen exit code $?; $(ls $B/demo_clean/$T/aloha_agilex/data/*.hdf5 2>/dev/null | wc -l) hdf5"
build dense_${T}_gen600_v1 $B/demo_clean/$T/aloha_agilex
say "DONE"
