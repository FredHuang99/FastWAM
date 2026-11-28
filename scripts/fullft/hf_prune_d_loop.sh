#!/usr/bin/env bash
# mwam5090, 11-28 (Opus; plan v22 decision D): hf_prune_d.py once an hour until 12-01 12:00 (Beijing). It deletes
# nothing unless the relay is above 75 % (rules in its docstring). Own log outputs/fullft/HF_PRUNE_D_LOOP.log; the
# q5090 task log gets every line too (tee).
#   q5090.txt: hf-prune-d-loop | cpu | - | bash scripts/fullft/hf_prune_d_loop.sh
set -u
R=/workspace/FastWAM-memory2
cd $R
END=$(TZ=Asia/Shanghai date -d '2026-12-01 12:00' +%s)
while [ "$(date +%s)" -lt "$END" ]; do
  echo "[prune-d-loop] $(TZ=Asia/Shanghai date '+%F %T') run"
  timeout 3h /opt/hf-tools/bin/python scripts/fullft/hf_prune_d.py 2>&1 | tail -n 20
  echo "[prune-d-loop] $(TZ=Asia/Shanghai date '+%F %T') exit ${PIPESTATUS[0]}; next in 60 min"
  sleep 3600
done 2>&1 | tee -a outputs/fullft/HF_PRUNE_D_LOOP.log
echo "[prune-d-loop] window over (12-01 12:00)"
