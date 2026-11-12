#!/usr/bin/env bash
# 5090 diagnosis D2 (11-12): frame-0 requests of fixed scenes, dumped by the closed loop itself (online.py --dump-first)
# with the REPLAY policy: no model is loaded, only the simulator renders frame 0 (GPU memory a few GB). The probe
# (numerics_probe.py) can then feed the very same request to either machine's policy.
# Scenes: put 31-35 (X7 logged on both machines), put 1-5 and swap 1-5 (N7 e10 on both; X7 swap on both).
# The replay packs come from this machine's own episodes; their targets do not matter (frame 0 is dumped before any).
#   A100 (queue card D2-a100-dump, GPU from the pool): GPU={GPU} MACHINE=a100 RELAY=1 bash .../dump_first.sh
#   5090: docker exec -e MACHINE=5090 -e GPU=0 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/dump_first.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
A=$R/outputs/fullft/align
P=$A/replay
mkdir -p $P
LOG=$A/DUMP_FIRST_${MACHINE:?}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[dump] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=${GPU:-0} PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
PY=/opt/mwam/bin/python
PUTB=$O/closed_loop/scenes_seed42_n100_put_back_block
SWAPB=$O/closed_loop/scenes_seed42_n100_swap_blocks
NAME=${NAME:-dumpfirst_$MACHINE}
if [ "$MACHINE" = a100 ]; then X7F="closed_loop/official/put_x7_s0 closed_loop/official/put_x7_s1"; X7L=a2C6_e6
else X7F=closed_loop/eq5090b; X7L=x7_eq5090b; fi
$PY scripts/fullft/replay_pack.py pack --name $NAME --folders $X7F --label $X7L --task put_back_block --bank $PUTB --from-scene 31 --limit 5
$PY scripts/fullft/replay_pack.py pack --name $NAME --merge --folders closed_loop/g1 --label ar_2task_e10 --task put_back_block --bank $PUTB --limit 5
$PY scripts/fullft/replay_pack.py pack --name $NAME --merge --folders closed_loop/g1 --label ar_2task_e10 --task swap_blocks --bank $SWAPB --limit 5
for spec in "$PUTB put_back_block 31" "$PUTB put_back_block 1" "$SWAPB swap_blocks 1"; do
  set -- $spec
  $PY -m fastwam.memory_v2.online run --checkpoint replay:$P/$NAME.json.gz --label $NAME --scenes $1 --tasks $2 \
    --from-scene $3 --limit 5 --execute 8 --max-targets 8 --dump-first --output $O/closed_loop/dumpfirst \
    >> $O/closed_loop/dumpfirst_$MACHINE.log 2>&1
  echo "$2 from scene $3: exit code $?"
done
echo "requests: $(ls $O/closed_loop/dumpfirst/$NAME/on/*/seed_*/request_000000.pkl 2>/dev/null | wc -l)"
if [ "${RELAY:-0}" = 1 ]; then
  tar czf /tmp/$NAME.tgz -C $O/closed_loop/dumpfirst $(cd $O/closed_loop/dumpfirst && ls $NAME/on/*/seed_*/request_000000.pkl)
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py put /tmp/$NAME.tgz --prefix diag/first_requests 2>&1 | tail -1
fi
