#!/usr/bin/env bash
# mwam-h100n (H100), 11-23 15:00 (Opus; user 14:53 approved): condition of the queue line rearr_v3c (exit 0 = runnable).
# rearr_v3c = rearrange_arprop's line (H100, the same machine class as rearrange_ar / rearrange_arprop) with the timely
# writer of D2 / press_v3c: lag 0, delta 0.012, min_path 0.015, provisional 0.002, and its event file
# events_rearrange_blocks_v3c.json (written on the 5090 by task_v3c_events.py --relay, relay diag/rearrange_blocks_v3c).
# Cheap when ready (marker READY_rearr_v3c); otherwise at most one attempt per 30 min: relay get -> file into place ->
# ledger_ready.py (event file vs this machine's cache, --check3 subset as for rearrange before). CPU only.
# Log: outputs/fullft/REARR_V3C_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
E=$F/events/events_rearrange_blocks_v3c.json
[ -f $F/READY_rearr_v3c ] && [ -s $E ] && exit 0
[ -f outputs/memory_v2/press/dense_rearrange_blocks_v1/.verified ] || exit 1
T=$F/REARR_V3C_READY_TRIED
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 1800 ]; then exit 1; fi
touch $T
exec >> $F/REARR_V3C_READY.log 2>&1
echo "[rv3c] $(TZ=Asia/Shanghai date '+%F %T') attempt"
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
IN=$F/rearr_v3c_in; mkdir -p $IN $F/events
if [ ! -s $E ]; then
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/rearrange_blocks_v3c --out $IN 2>&1 | tail -n 2
  [ -s $IN/events_rearrange_blocks_v3c.json ] || { echo "[rv3c] not on the relay yet (5090: task_v3c_events.py --relay)"; exit 1; }
  cp $IN/events_rearrange_blocks_v3c.json $E
fi
PYTHONPATH=src CUDA_VISIBLE_DEVICES= $PY scripts/fullft/ledger_ready.py --variant arprop --tasks rearrange_blocks \
  --events $E --check3 subset --marker READY_rearr_v3c --skip-tests 2>&1 | grep -v '^\.\+$' | tail -n 8
[ -f $F/READY_rearr_v3c ] && { echo "[rv3c] READY"; exit 0; }
echo "[rv3c] NOT READY (see above)"; exit 1
