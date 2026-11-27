#!/usr/bin/env bash
# mwam5090, 11-27 02:35 (Opus; plan v21 card 25, P1; user 11-27 01:03 approved generated training data for find-same).
# The SAME table recorded once per candidate as the target ("同一张桌面换参照物"), by the benchmark's own scripted
# expert (gen_demos.py, RMBench collect_data.py unmodified; --gen-target K = the target hook: the benchmark's draw kept,
# only its value replaced). Seeds from 20,000,000 upwards: disjoint from the seed-42 evaluation bank (4.3M+), the 5090
# development banks (0.8M+, 1.8-2.1M), the official demos' seeds and card 8's (10,000,000+).
#   PART=check  10 seeds x 5 targets + card 8's render gate re-run on the official seeds 0-2 with the current code ->
#               card25_check.py (target fixed / same table pixel-identical / expert >= 90 % per target / render gate).
#               FAIL -> stop and report; nothing is generated for training.
#   PART=gen    only after CARD25_CHECK.json says pass: candidate seeds from 20,000,100 x 5 targets; groups = seeds whose
#               table holds 5 candidates and whose expert succeeded for all 5 targets; the first 33 groups by seed:
#               31 -> dense_observe_and_pickup_cf155_v1 (155 scenes; + the 45 official training demos = 200), the last 2
#               -> dense_observe_and_pickup_cf10probe_v1 (never trained on: the probe's held-out groups); both to the cache
#               relay. Episode ids gen_cf_<seed>_t<K>. Resumable.
#   q5090.txt lines: card25-check | gpu | - | PART=check bash scripts/fullft/card25_5090.sh   (then card25-gen)
# Own log: outputs/fullft/CARD25_5090_<part>_<time>.txt ; generator logs outputs/fullft/gen_cf/*.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
P=$R/outputs/memory_v2/press
G=$F/gen_cf
PART=${PART:?PART=check|gen}
LOG=$F/CARD25_5090_${PART}_$(date +%Y%m%d_%H%M).txt
mkdir -p $G
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c25] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=observe_and_pickup
GPU=${GPU:-${GEN_GPU:-1}}
say() { echo "[c25] $(date '+%F %T') $*"; }
say "part $PART; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $GPU"
gen() {     # out, extra args...
  local out=$1; shift
  CUDA_VISIBLE_DEVICES=$GPU $PY -m fastwam.memory_v2.online gen --tasks $T --output $out "$@" >> $out.log 2>&1
}
OFF=""
for d in /workspace/FastWAM/resources/RMBench/data/demo_clean/$T/aloha_agilex $P/demo_clean/$T/aloha_agilex; do
  [ -f $d/seed.txt ] && [ -d $d/data ] && { OFF=$d; break; }
done
if [ "$PART" = check ]; then
  [ -n "$OFF" ] || { say "no official seed.txt: the render gate cannot be re-run; stop (report)"; exit 1; }
  RS=$(cat $OFF/seed.txt | tr -s ' \n' ' ' | xargs -n1 | head -n 3 | tr '\n' ' ')
  if [ ! -f $G/render/demo_clean/$T/aloha_agilex/data/episode_0000002.hdf5 ]; then
    mkdir -p $G/render; gen $G/render --gen-seeds $RS; say "render seeds $RS: gen exit $?"
  fi
  $PY scripts/fullft/gen_check.py --gen $G/render/demo_clean/$T/aloha_agilex/data --official $OFF/data --n 3 \
    --gate background --out $G/GEN_CHECK_RENDER.json; say "card 8's render gate (background, user 11-24): exit $?"
  SEEDS=$(seq 20000000 20000009 | tr '\n' ' ')
  for K in 0 1 2 3 4; do
    if [ -f $G/check/t$K/demo_clean/$T/aloha_agilex/GEN.json ] && grep -q '"finished"' $G/check/t$K/demo_clean/$T/aloha_agilex/GEN.json; then
      say "target $K: generated earlier"; continue; fi
    mkdir -p $G/check/t$K; gen $G/check/t$K --gen-seeds $SEEDS --gen-target $K
    say "target $K: gen exit $?; $(ls $G/check/t$K/demo_clean/$T/aloha_agilex/data/*.hdf5 2>/dev/null | wc -l) episodes"
  done
  $PY scripts/fullft/card25_check.py --base $G/check
  exit $?
fi
[ "$PART" = gen ] || { say "unknown PART"; exit 2; }
# 11-27 04:10: the TOP-LEVEL pass only (a grep for '"pass": true' also matched a single passed check: the 11-27 02:26 BJ run (machine clock 11-26 18:26)
# generated although check 2 had failed)
$PY -c "import json,sys; sys.exit(0 if json.load(open('$G/CARD25_CHECK.json'))['pass'] is True else 1)" 2>/dev/null \
  || { say "CARD25_CHECK.json does not pass: nothing generated (report)"; exit 1; }
B=$G/cf; N=0; START=20000100; NEED=33
groups() {  # -> complete groups (seed list) from what exists
  $PY - "$B" <<'PYEOF'
import json, sys
from pathlib import Path
b = Path(sys.argv[1]); ok = None; five = set()
for k in range(5):
    d = b / f"t{k}" / "demo_clean" / "observe_and_pickup" / "aloha_agilex"
    seeds = [int(x) for x in (d / "seed.txt").read_text().split()] if (d / "seed.txt").exists() else []
    saved = {s for i, s in enumerate(seeds) if (d / "data" / f"episode_{i:07d}.hdf5").exists()}
    ok = saved if ok is None else ok & saved
    if (d / "targets.jsonl").exists():
        for x in map(json.loads, (d / "targets.jsonl").read_text().splitlines()):
            if x["phase"] == "plan" and x["candidates"] == 5:
                five.add(x["seed"])
print(" ".join(str(s) for s in sorted((ok or set()) & five)))
PYEOF
}
while :; do
  have=$(groups | wc -w)
  [ $have -ge $NEED ] && break
  [ $N -ge 4 ] && { say "only $have complete groups after 4 batches: stop (report)"; exit 1; }
  SEEDS=$(seq $((START + 45 * N)) $((START + 45 * N + 44)) | tr '\n' ' ')
  say "batch $N: seeds $((START + 45 * N))-$((START + 45 * N + 44)) x 5 targets (complete groups so far $have)"
  for K in 0 1 2 3 4; do mkdir -p $B/t$K; gen $B/t$K --gen-seeds $SEEDS --gen-target $K; say "  target $K exit $?"; done
  N=$((N + 1))
done
ALL=$(groups | xargs -n1 | head -n $NEED | tr '\n' ' ')
TRAIN=$(echo $ALL | xargs -n1 | head -n 31 | tr '\n' ' '); PROBE=$(echo $ALL | xargs -n1 | tail -n 2 | tr '\n' ' ')
say "groups: train $TRAIN | probe $PROBE"
echo "{\"train\": \"$TRAIN\", \"probe\": \"$PROBE\"}" > $G/GROUPS.json
link() {    # name, seeds
  local name=$1 L=$G/links_$1; shift
  rm -rf $L; mkdir -p $L/data $L/instruction
  for s in $@; do for K in 0 1 2 3 4; do
    d=$B/t$K/demo_clean/$T/aloha_agilex; i=$(cat $d/seed.txt | xargs -n1 | grep -nx $s | cut -d: -f1); i=$((i - 1))
    f=$(printf "%s/data/episode_%07d.hdf5" $d $i); ln -s $f $L/data/gen_cf_${s}_t$K.hdf5
    j=$(printf "%s/instruction/episode_%d.json" $d $i); [ -f $j ] && cp $j $L/instruction/gen_cf_${s}_t$K.json
  done; done
  say "$name: $(ls $L/data | wc -l) episodes -> build_dense (val 0)"
  CUDA_VISIBLE_DEVICES=$GPU $PY scripts/memory_v2/press/build_dense.py build --task $T --raw $L/data --out $P/$name --val 0 \
    > $G/build_$name.log 2>&1; say "build exit $? ($(tail -n 1 $G/build_$name.log | cut -c1-160))"
  [ -f $P/$name/CACHE.json ] || { say "$name: no CACHE.json"; return 1; }
  $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx $name && { say "$name on the cache relay"; return 0; }
  $HFPY scripts/fullft/cache_relay.py put $P/$name 2>&1 | tail -n 2
  $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx $name && say "$name on the cache relay" || { say "$name: UPLOAD FAILED"; return 1; }
}
[ -f $P/dense_${T}_cf155_v1/CACHE.json ] || link dense_${T}_cf155_v1 $TRAIN || exit 1
[ -f $P/dense_${T}_cf10probe_v1/CACHE.json ] || link dense_${T}_cf10probe_v1 $PROBE || exit 1
say "CARD25 GEN DONE (register the 6.3 reading verbatim, then train)"
