#!/usr/bin/env bash
# mwam5090 container (11-08): the 5090 side, after firstrender_a100.sh has relayed the A100's frame-0 request of
# put_back seed 4300030. Pre-registered reading (written before either result):
#   - the 5090 policy on the A100's image reproduces the A100's first chunk (lag-0 arm RMSE <= 0.01) while on its own
#     image it lags by 2 -> the 5090 RENDERS differently (camera images), the policy is fine; next: render settings
#   - the 5090 policy on the A100's image still lags / differs (lag-0 RMSE > 0.01) -> not the image: the 5090's policy
#     numerics on the online path (offline parity only covered cached inputs)
#   1 relay get diag/a100_4300030 -> closed_loop/check_from_a100
#   2 request_diff.py: A100 vs 5090 camera images of the same frame (numbers + difference pictures)
#   3 first_decision.py on the A100's request (dense cache text and CPU T5) vs the A100's first 8 targets
# GPU 0 only (outside the pool's allowed GPUs). Own log: report/FIRSTRENDER_5090_<time>.txt
#   docker exec mwam5090 bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/firstrender_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/FIRSTRENDER_5090_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[firstrender] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[firstrender] $(date '+%F %T') ===== $*"; }
cd "$R"
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=0
PY=/opt/mwam/bin/python
IN=$O/closed_loop/check_from_a100
MINE=$O/closed_loop/check5090b/x7_first5090b/on/put_back_block/seed_4300030/request_000000.pkl

step "1 relay get"
/opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py get --prefix diag/a100_4300030 --out $IN || exit 1

step "2 camera images: A100 vs 5090, same scene, frame 0"
$PY scripts/memory_v2/migrate/request_diff.py $IN/request_000000.pkl $MINE --names a100 5090 --out $O/report/render_diff

step "3 the 5090 policy on the A100's request"
$PY scripts/memory_v2/migrate/first_decision.py --request $IN/request_000000.pkl --variants cache cpu \
  --ref scripts/memory_v2/migrate/ref_a100_put_4300030.json --replayed $IN/executed_actions.jsonl

step "A100's own replay of the same request (relayed report)"
sed -n '/## first 8 targets/,$p' $IN/FIRST_DECISION_A100.md
