#!/usr/bin/env bash
# mwam5090 container, 5090 diagnosis D2 (11-12): waits for GPU ${GPU:-0} to be empty, then
#   1 dumps this machine's frame-0 requests (dump_first.sh: put 31-35, put 1-5, swap 1-5; replay policy, no model)
#   2 sanity: X7 and N7 e10 decide on these requests -> must equal the 5090's logged decision 0 (probe = closed loop)
#   3 if the A100's requests are on the relay (queue card D2-a100-dump): the same two policies decide on the A100's
#     requests -> compared with the A100's logged decision 0 = policy numerics only (same images, text, noise, proprio)
# Reading (written 11-12 before any probe): Nnum = median arm RMSE of step 3 (normalized units, as D1).
#   Nnum <= 0.25 N (D1: X7 put N = 0.0024)  -> the residual is the GPU ray tracing, not the policy numerics
#   Nnum >= 0.75 N                            -> the residual is the policy numerics (VAE / T5 / DiT on the two GPUs)
#   between                                   -> both
#   docker exec -d -e GPU=0 mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/d2_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft/align/first
LOG=$R/outputs/fullft/align/D2_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[d2] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
GPU=${GPU:-0}
export PYTHONPATH=$R/src
PY=/opt/mwam/bin/python
E10=$R/outputs/fullft/exports/ar_2task_e10/export_e10.pt
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $GPU | tr -d ' '; }
until [ "$(used)" -lt 2000 ]; do echo "[d2] $(date '+%F %T') GPU $GPU busy; waiting"; sleep 300; done
echo "[d2] $(date '+%F %T') ===== 1 dump this machine's frame-0 requests"
MACHINE=5090 GPU=$GPU bash scripts/fullft/dump_first.sh > /dev/null 2>&1; tail -n 3 $(ls -t $R/outputs/fullft/align/DUMP_FIRST_5090_*.txt | head -1)
OWN="closed_loop/dumpfirst/dumpfirst_5090/on/*/seed_*/request_000000.pkl"
cmpf() { $PY scripts/fullft/first_actions.py compare $1.json $2.json 2>&1 | grep -vE "^  timing"; }
echo "[d2] $(date '+%F %T') ===== 2 sanity: the probe on the 5090's own requests vs the 5090's logged decision 0"
CUDA_VISIBLE_DEVICES=$GPU $PY scripts/fullft/numerics_probe.py --name probe_5090own_x7 --policy x7 --requests "$OWN" | tail -n 1
CUDA_VISIBLE_DEVICES=$GPU $PY scripts/fullft/numerics_probe.py --name probe_5090own_e10 --policy $E10 --requests "$OWN" | tail -n 1
cmpf 5090_x7 probe_5090own_x7
cmpf 5090_e10 probe_5090own_e10
echo "[d2] $(date '+%F %T') ===== 3 the A100's requests (numerics only)"
mkdir -p $O/closed_loop/dumpfirst_in
/opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py get --prefix diag/first_requests --out /tmp/d2_in 2>&1 | tail -1
if [ -f /tmp/d2_in/dumpfirst_a100.tgz ]; then
  tar xzf /tmp/d2_in/dumpfirst_a100.tgz -C $O/closed_loop/dumpfirst_in
  IN="closed_loop/dumpfirst_in/dumpfirst_a100/on/*/seed_*/request_000000.pkl"
  CUDA_VISIBLE_DEVICES=$GPU $PY scripts/fullft/numerics_probe.py --name probe_5090_on_a100_x7 --policy x7 --requests "$IN" | tail -n 1
  CUDA_VISIBLE_DEVICES=$GPU $PY scripts/fullft/numerics_probe.py --name probe_5090_on_a100_e10 --policy $E10 --requests "$IN" | tail -n 1
  cmpf a100_x7_ref_put probe_5090_on_a100_x7
  cmpf a100_x7_ref_swap probe_5090_on_a100_x7
  cmpf a100_e10 probe_5090_on_a100_e10
else
  echo "the A100's requests are not on the relay yet (queue card D2-a100-dump waits for an empty A100 GPU); rerun this script then"
fi
