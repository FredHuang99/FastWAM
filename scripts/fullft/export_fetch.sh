#!/usr/bin/env bash
# Any machine with the HF login (A100 queue card FT-fetch-<tag>, plan v12): wait until the relay holds
# exports/<RUN>_<TAG>/export_<TAG>.pt.sha256 (export_watch.sh on the H200 uploads it last), fetch the export once,
# check its sha256. Prints a heartbeat every poll (the pool stops tasks that write nothing for a long time).
#   RUN=ar_2task TAG=e10 bash /workspace/FastWAM-memory2/scripts/fullft/export_fetch.sh
set -u
R=/workspace/FastWAM-memory2
RUN=${RUN:?}; TAG=${TAG:?}; POLL=${POLL:-300}
E=$R/outputs/fullft/exports/${RUN}_${TAG}
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
cd $R
if [ -f $E/export_${TAG}.pt ] && (cd $E && sha256sum -c export_${TAG}.pt.sha256 >/dev/null 2>&1); then
  echo "[fetch] $(date '+%F %T') ${RUN}_${TAG} already here and checked"; exit 0
fi
until $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${RUN}_${TAG} --repo hhyfred/memwam-fullft 2>/dev/null \
      | grep -q "^export_${TAG}.pt.sha256 "; do
  echo "[fetch] $(date '+%F %T') waiting for exports/${RUN}_${TAG} on the relay"; sleep $POLL
done
for attempt in 1 2 3; do
  echo "[fetch] $(date '+%F %T') fetching ${RUN}_${TAG} (attempt $attempt)"
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/${RUN}_${TAG} --repo hhyfred/memwam-fullft --out $E \
    2>&1 | grep -v "Processing\|Download\|%|"
  (cd $E && sha256sum -c export_${TAG}.pt.sha256) && { ls -la $E; exit 0; }
  echo "[fetch] sha256 mismatch: deleting the export file and retrying"; rm -f $E/export_${TAG}.pt; sleep 60
done
exit 1
