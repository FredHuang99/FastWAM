#!/usr/bin/env bash
# Condition of the press_fast line in h200_queue.txt (exit 0 = the H200 queue may start it). User approval: option A,
# 11-16 19:43 BJ ("批准A"), marker outputs/fullft/GO_press_fast. Registered 11-16 19:55 (status doc 11-16 section 9):
# press_fast is trained next only if LAT-T showed that ledger timing or recording matters, i.e. some e20 arm read
# IMPLICIT or WAITS, or the e30 arm read RECORDING EXPLAINS E30 or PARTIAL (lat_verdict.py); otherwise press_arev.
# Steps (quiet; DEBUG=1 prints them; the last state is always written to outputs/fullft/PRESS_FAST_READY_STATUS.txt):
#   GO marker and the press cache -> the three files from the relay (diag/press_fast, put there by the 5090's
#   press_fast_5090.sh): LAT_VERDICT.json, PRESS_FAST_RULE.json, events_press_button_fast.json -> the registered
#   LAT condition -> files into place -> ledger_ready.py on the fast events file (READY_press_fast, once).
#   bash scripts/fullft/press_fast_ready.sh; echo $?        (by hand: DEBUG=1 to see why it waits)
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
IN=$F/press_fast_in
cd $R
state() { echo "$(date '+%F %T') $*" > $F/PRESS_FAST_READY_STATUS.txt; [ "${DEBUG:-0}" = 1 ] && echo "[press_fast_ready] $*"; }
[ -f $F/GO_press_fast ] || { state "waits: no GO_press_fast (user approval marker)"; exit 1; }
[ -f $R/outputs/memory_v2/press/dense_press_button_v1/.verified ] || { state "waits: press cache not verified"; exit 1; }
mkdir -p $IN
if [ ! -s $IN/LAT_VERDICT.json ] || [ ! -s $IN/PRESS_FAST_RULE.json ] || [ ! -s $IN/events_press_button_fast.json ]; then
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py get --prefix diag/press_fast --out $IN >/dev/null 2>&1
fi
for f in LAT_VERDICT.json PRESS_FAST_RULE.json events_press_button_fast.json; do
  [ -s $IN/$f ] || { state "waits: $f not on the relay yet (diag/press_fast)"; exit 1; }
done
if ! WHY=$(/opt/mwam/bin/python - $IN/LAT_VERDICT.json <<'PY'
import json, sys
v = json.load(open(sys.argv[1]))
hits = [f"{k}: {x['reading']}" for k, x in v.items()
        if (x.get("reference") == "press_arprop_e20" and x.get("reading") in ("IMPLICIT", "WAITS"))
        or (x.get("reference") == "press_arprop_e30" and x.get("reading") in ("RECORDING EXPLAINS E30", "PARTIAL"))]
print("; ".join(hits) if hits else "; ".join(f"{k}: {x.get('reading')}" for k, x in v.items()))
sys.exit(0 if hits else 1)
PY
); then
  state "NO GO by the registered LAT condition ($WHY): press_arev goes first"; exit 1
fi
cp -f $IN/PRESS_FAST_RULE.json $F/PRESS_FAST_RULE.json
mkdir -p $F/events && cp -f $IN/events_press_button_fast.json $F/events/events_press_button_fast.json
if [ ! -f $F/READY_press_fast ]; then
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/ledger_ready.py --variant press_fast --tasks press_button \
    --events $F/events/events_press_button_fast.json > $F/PRESS_FAST_READY_CHECK.txt 2>&1 \
    || { state "ledger_ready failed on the fast events file (see PRESS_FAST_READY_CHECK.txt)"; exit 1; }
fi
state "GO ($WHY); rule $(cat $F/PRESS_FAST_RULE.json)"
exit 0
