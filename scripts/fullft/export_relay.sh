#!/usr/bin/env bash
# mwam2 container (H200): put one fullft bf16 export on the private HF relay so the evaluation machine (5090) can
# fetch it (the machines cannot reach each other). Usage (own log outputs/fullft/RELAY_<time>.txt):
#   docker exec -d -e RUN=ar_2task -e TAG=e10 mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/export_relay.sh
set -u
R=/workspace/FastWAM-memory2
OUT=$R/outputs/fullft
LOG=$OUT/RELAY_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[relay] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
F=$OUT/${RUN:?}/export_${TAG:?}.pt
ls -la "$F" || { echo "missing export $F"; exit 1; }
sha256sum "$F" | tee "$F.sha256"
cd $R && /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py put "$F" "$F.sha256" \
  --prefix exports/${RUN}_${TAG} --repo hhyfred/memwam-fullft 2>&1 | grep -v "Processing\|Upload\|Validating\|%|"
