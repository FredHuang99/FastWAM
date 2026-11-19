#!/usr/bin/env bash
# mwam2 (old H200), 11-19 (Opus, plan v14 E14): condition of the queue line press_v3c (exit 0 = runnable). press_v3c =
# press_count's recipe (lag 0, count code 16) with the writer press_writer_scan.py chose on the demos (the A40 card
# A40-E14-writer-verdict puts PRESS_V3C_RULE.json + events_press_button_v3c.json on the relay, diag/press_v3c, only when
# a plug-in threshold writer was chosen). Base = press_count by plan v14 E14's rule ("E4's numbers not out yet -> v3c";
# the A40 press table is not out when this line can start). Cheap when ready (marker READY_press_v3c); otherwise at most
# one attempt per 30 min: relay get -> files into place -> ledger_ready.py on the new events file. This machine has no
# /opt/hf-tools. Log: outputs/fullft/V3C_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
[ -f $F/READY_press_v3c ] && [ -s $F/PRESS_V3C_RULE.json ] && [ -s $F/events/events_press_button_v3c.json ] && exit 0
[ -f outputs/memory_v2/press/dense_press_button_v1/.verified ] || exit 1
T=$F/V3C_READY_TRIED
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 1800 ]; then exit 1; fi
touch $T
exec >> $F/V3C_READY.log 2>&1
echo "[v3c] $(TZ=Asia/Shanghai date '+%F %T') attempt"
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
IN=$F/press_v3c_in; mkdir -p $IN $F/events
$HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/press_v3c --out $IN 2>&1 | tail -n 2
[ -s $IN/PRESS_V3C_RULE.json ] && [ -s $IN/events_press_button_v3c.json ] || { echo "[v3c] not on the relay (no plug-in writer chosen yet)"; exit 1; }
cp -f $IN/PRESS_V3C_RULE.json $F/PRESS_V3C_RULE.json
cp -f $IN/events_press_button_v3c.json $F/events/events_press_button_v3c.json
PYTHONPATH=src CUDA_VISIBLE_DEVICES= $PY scripts/fullft/ledger_ready.py --variant press_v3c --tasks press_button \
  --events $F/events/events_press_button_v3c.json 2>&1 | grep -v '^\.\+$' | tail -n 8
[ -f $F/READY_press_v3c ] && { echo "[v3c] READY: rule $(cat $F/PRESS_V3C_RULE.json)"; exit 0; }
echo "[v3c] NOT READY (see above)"; exit 1
