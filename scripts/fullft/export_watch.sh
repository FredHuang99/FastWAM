#!/usr/bin/env bash
# mwam2 container (H200; plan v11 N8, Opus checklist 6): wait for each N7 export and put it on the relay
# (export_relay.sh), so the 5090 evaluates it with nobody at the keyboard (e10 ~ 03:00, e20 ~ 14:00, e30 ~ 11-13 02:00).
# The trainer writes exports atomically (tmp file + rename), so "the file exists" means it is complete.
# A tag counts as relayed only when the relay lists both export_<tag>.pt and its .sha256; up to 3 tries per tag.
# Resumable (marker outputs/fullft/<run>/.relayed_<tag>). CPU / network only.
#   docker exec -d mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/export_watch.sh
# Env: RUN (ar_2task), TAGS ("e10 e20 e30"), POLL seconds (300). Own log: outputs/fullft/EXPORT_WATCH_<time>.txt
set -u
R=/workspace/FastWAM-memory2
OUT=$R/outputs/fullft
RUN=${RUN:-ar_2task}; TAGS=${TAGS:-"e10 e20 e30"}; POLL=${POLL:-300}
LOG=$OUT/EXPORT_WATCH_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[watch] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
cd $R
listed() { $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${RUN}_$1 --repo hhyfred/memwam-fullft 2>/dev/null; }
for TAG in $TAGS; do
  F=$OUT/$RUN/export_$TAG.pt; M=$OUT/$RUN/.relayed_$TAG
  [ -f $M ] && { echo "[watch] $TAG: already relayed"; continue; }
  echo "[watch] $(date '+%F %T') waiting for $F"
  until [ -f $F ]; do sleep $POLL; done
  echo "[watch] $(date '+%F %T') $TAG appeared ($(du -h $F | cut -f1))"
  for try in 1 2 3; do
    RUN=$RUN TAG=$TAG bash scripts/fullft/export_relay.sh > /dev/null 2>&1
    L=$(listed $TAG)
    if echo "$L" | grep -q "^export_$TAG.pt " && echo "$L" | grep -q "^export_$TAG.pt.sha256 "; then
      touch $M; echo "[watch] $(date '+%F %T') $TAG relayed (try $try):"; echo "$L"; break; fi
    echo "[watch] $(date '+%F %T') $TAG try $try not complete on the relay (see the newest outputs/fullft/RELAY_*.txt)"
    sleep 600
  done
  [ -f $M ] || echo "[watch] $TAG NOT RELAYED after 3 tries"
done
