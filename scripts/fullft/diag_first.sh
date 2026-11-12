#!/usr/bin/env bash
# 5090 diagnosis step D1 (11-12): decision-0 action chunks of every X7 / e10 run on both machines (first_actions.py).
# CPU and network only, read-only for the episodes. Run on the A100 first (exports + relay put), then on the 5090
# (exports + relay get + the comparisons). Prints everything; own log outputs/fullft/align/DIAG_FIRST_<machine>_<time>.txt
#   docker exec -e MACHINE=a100 6e4b37a15066 bash /workspace/FastWAM-memory2/scripts/fullft/diag_first.sh
#   docker exec -e MACHINE=5090 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/diag_first.sh
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft/align/first
mkdir -p $F
LOG=$R/outputs/fullft/align/DIAG_FIRST_${MACHINE:?}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
cd $R
export PYTHONPATH=$R/src
PY=/opt/mwam/bin/python
HF=/opt/hf-tools/bin/python
ex() { $PY scripts/fullft/first_actions.py export "$@"; }
cmp() { [ -f $F/$1.json ] && [ -f $F/$2.json ] && $PY scripts/fullft/first_actions.py compare $1.json $2.json || echo "missing $1 or $2"; }
if [ "$MACHINE" = a100 ]; then
  ex --name a100_x7_ref_put --folders closed_loop/official/put_x7_s0 closed_loop/official/put_x7_s1 --label a2C6_e6
  ex --name a100_x7_ref_swap --folders closed_loop/official/swap8_x7_s0 closed_loop/official/swap8_x7_s1 closed_loop/official/swap8_x7_s2 --label a2C6_e6_exec8
  ex --name a100_x7_oidn233 --folders closed_loop/al5 --label x7_al5_oidn233
  ex --name a100_x7_rerun --folders closed_loop/al5 --label x7_al5_ctrl
  ex --name a100_e10 --folders closed_loop/g1 --label ar_2task_e10
  for n in a100_x7_ref_put a100_x7_ref_swap a100_x7_oidn233 a100_x7_rerun a100_e10; do
    $HF scripts/memory_v2/migrate/relay.py put $F/$n.json --prefix diag/first_actions 2>&1 | tail -1
  done
  echo "D1 a100 side done"
else
  ex --name 5090_x7 --folders closed_loop/eq5090b --label x7_eq5090b
  ex --name 5090_e10 --folders closed_loop/g1 --label ar_2task_e10
  ex --name 5090_e10_oidnoff --folders closed_loop/s1pre --label ar_2task_e10_oidnoff
  $HF scripts/memory_v2/migrate/relay.py get --prefix diag/first_actions --out $F 2>&1 | tail -1
  echo; echo "== X7 put (31-50): floor, denoiser version, residual + numerics, total"
  cmp a100_x7_ref_put a100_x7_rerun
  cmp a100_x7_ref_put a100_x7_oidn233
  cmp a100_x7_oidn233 5090_x7
  cmp a100_x7_ref_put 5090_x7
  echo; echo "== X7 swap (1-20)"
  cmp a100_x7_ref_swap a100_x7_oidn233
  cmp a100_x7_ref_swap 5090_x7
  echo; echo "== new base e10 (1-20): A100 vs 5090; 5090 denoiser on vs off (scale of a large render change)"
  cmp a100_e10 5090_e10
  cmp 5090_e10 5090_e10_oidnoff
  echo "D1 5090 side done"
fi
