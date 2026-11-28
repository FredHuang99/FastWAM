#!/usr/bin/env bash
# mwam5090, 11-28 (Opus; plan v22 card 30, P1, registered reading in gaas_queue.txt above the obs_cf800 line).
# 800 training scenes as counterfactual groups, as card 25: the 45 official training demos + 151 table layouts x 5
# targets, recorded by the benchmark's own scripted expert (gen_demos.py through `online gen --gen-target K`, the same
# hook as card 25). 2 further complete groups are kept out of every training (probe groups).
# Seeds from 30,000,000 upwards: disjoint from the seed-42 evaluation bank (4.3M+), the 5090 development banks
# (0.8M+, 1.8-2.1M), the official demos' seeds, card 8 / obs_s800 / obs_s1600's generated scenes (10,000,000+) and
# card 25's (20,000,000+, check and generation).
# Checks (card 25's, with the threshold the user approved on 11-27 for card 25: card 8's "> 8 levels on < 2 % of the
# pixels" on every camera; card25_check.py --gate8), run on the generated groups BEFORE any cache is built:
#   1 target fixed; 2 same table (first 40 common seeds, 4 pairs each); 3 expert >= 90 % per target; 4 card 8's render
#   gate re-run on the official seeds 0-2 with the current code. FAIL -> stop, nothing is cached or uploaded (report).
# Groups = seeds whose table holds 5 candidates and whose expert succeeded for all 5 targets, by seed; the first 151 ->
# dense_observe_and_pickup_cf755_v1 (755 scenes; + the 45 official demos = 800), the next 2 ->
# dense_observe_and_pickup_cf10probe2_v1 (never trained on). Both to the cache relay. Episode ids gen_cf_<seed>_t<K>.
# Batches of 60 seeds x 5 targets until 153 complete groups (at most 6 batches; fewer -> plan v22b part 3 section 6:
# report; the registration is then amended before training with the real count). Resumable.
#   q5090.txt: card30-gen | gpu1 | - | export GPU=$(bash scripts/fullft/cuda_ordinal.sh $GPU); bash scripts/fullft/card30_5090.sh
# Own log: outputs/fullft/CARD30_5090_<time>.txt ; generator logs outputs/fullft/gen_cf800/*.log
set -u
# (no pipefail: the relay checks pipe into grep -q, which may end its producer early)
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
P=$R/outputs/memory_v2/press
G=$F/gen_cf800
LOG=$F/CARD30_5090_$(date +%Y%m%d_%H%M).txt
mkdir -p $G
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[c30] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
T=observe_and_pickup
GPU=${GPU:-1}
START=30000000; BATCH=60; NEED=153; NTRAIN=151; MAXB=6
TRAIN_NAME=dense_${T}_cf755_v1; PROBE_NAME=dense_${T}_cf10probe2_v1
say() { echo "[c30] $(date '+%F %T') $*"; }
say "checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $GPU"
gen() {     # out, extra args...
  local out=$1; shift
  CUDA_VISIBLE_DEVICES=$GPU $PY -m fastwam.memory_v2.online gen --tasks $T --output $out "$@" >> $out.log 2>&1
}
OFF=""
for d in /workspace/FastWAM/resources/RMBench/data/demo_clean/$T/aloha_agilex $P/demo_clean/$T/aloha_agilex; do
  [ -f $d/seed.txt ] && [ -d $d/data ] && { OFF=$d; break; }
done
[ -n "$OFF" ] || { say "no official seed.txt: the render gate cannot be re-run; stop (report)"; exit 1; }
# check 4 first (cheap): card 8's render gate with the current code
RS=$(cat $OFF/seed.txt | tr -s ' \n' ' ' | xargs -n1 | head -n 3 | tr '\n' ' ')
if [ ! -f $G/render/demo_clean/$T/aloha_agilex/data/episode_0000002.hdf5 ]; then
  mkdir -p $G/render; gen $G/render --gen-seeds $RS; say "render seeds $RS: gen exit $?"
fi
$PY scripts/fullft/gen_check.py --gen $G/render/demo_clean/$T/aloha_agilex/data --official $OFF/data --n 3 \
  --gate background --out $G/GEN_CHECK_RENDER.json; say "card 8's render gate (background): exit $?"
B=$G/cf
groups() {  # -> complete groups (seed list) from what exists (card 25's rule)
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
N=0
while :; do
  have=$(groups | wc -w)
  [ $have -ge $NEED ] && break
  if [ $N -ge $MAXB ]; then say "only $have complete groups after $MAXB batches: stop (report; the registration is amended before training)"; exit 1; fi
  B0=$((START + BATCH * N))
  # a batch already generated for all 5 targets (resume) is skipped
  if [ -f $B/t4/demo_clean/$T/aloha_agilex/seed.txt ] && grep -qw $((B0 + BATCH - 1)) $B/t4/demo_clean/$T/aloha_agilex/seed.txt; then
    N=$((N + 1)); continue
  fi
  # 11-28 20:34 fix: gen_demos.py's --seeds wants len(seeds) expert-successful seeds IN TOTAL (seed.txt included), so a
  # batch must pass every seed from START on (done ones are skipped, failed ones re-tried); the 16:49-17:43 run passed
  # one batch's 60 and got 56 + 3 + 0 + 0 + 0 + 0 groups.
  SEEDS=$(seq $START $((B0 + BATCH - 1)) | tr '\n' ' ')
  say "batch $N: seeds $B0-$((B0 + BATCH - 1)) x 5 targets (complete groups so far $have)"
  for K in 0 1 2 3 4; do mkdir -p $B/t$K; gen $B/t$K --gen-seeds $SEEDS --gen-target $K; say "  target $K exit $?"; done
  N=$((N + 1))
done
ALL=$(groups | xargs -n1 | head -n $NEED | tr '\n' ' ')
TRAIN=$(echo $ALL | xargs -n1 | head -n $NTRAIN | tr '\n' ' '); PROBE=$(echo $ALL | xargs -n1 | tail -n 2 | tr '\n' ' ')
say "groups: $(echo $TRAIN | wc -w) train, probe $PROBE"
echo "{\"train\": \"$TRAIN\", \"probe\": \"$PROBE\"}" > $G/GROUPS.json
# checks 1-3 on the generated groups (+ 4 read from GEN_CHECK_RENDER.json); the TOP-LEVEL pass only
$PY scripts/fullft/card25_check.py --base $B --render $G/GEN_CHECK_RENDER.json --out $G/CARD30_CHECK.json --gate8 --max-seeds 40
$PY -c "import json,sys; sys.exit(0 if json.load(open('$G/CARD30_CHECK.json'))['pass'] is True else 1)" \
  || { say "CARD30 CHECK FAIL: nothing cached or uploaded (report)"; exit 1; }
say "CARD30 CHECK PASS"
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
[ -f $P/$TRAIN_NAME/CACHE.json ] && $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx $TRAIN_NAME \
  || link $TRAIN_NAME $TRAIN || exit 1
[ -f $P/$PROBE_NAME/CACHE.json ] && $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx $PROBE_NAME \
  || link $PROBE_NAME $PROBE || exit 1
say "CARD30 GEN DONE ($(echo $TRAIN | wc -w) groups x 5 = $(( $(echo $TRAIN | wc -w) * 5 )) scenes + 45 official)"
