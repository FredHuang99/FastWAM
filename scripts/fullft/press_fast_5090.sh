#!/usr/bin/env bash
# mwam5090, 11-16 19:50 BJ (user approved option A at 19:43): make sure LAT-T runs (lat_5090.sh is started here unless
# it is already running or has finished), wait for it (at most 10 h), then put the three files the H200's
# press_fast condition needs on the relay (diag/press_fast): LAT_VERDICT.json, PRESS_FAST_RULE.json and
# events_press_button_fast.json (when the sweep kept rule A: a copy of the rule-A events file, whose "rule" field
# then matches PRESS_FAST_RULE.json, so press_fast = the write lag 0 alone).
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/press_fast_5090.sh
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/PRESS_FAST_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[pf] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
echo "[pf] $(date '+%F %T') start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
if pgrep -f "[l]at_5090.sh" >/dev/null; then
  echo "[pf] lat_5090.sh already running: waiting for it"
elif [ -f $F/LAT_VERDICT.json ]; then
  echo "[pf] LAT_VERDICT.json already there: relaying"
else
  setsid nohup bash scripts/fullft/lat_5090.sh > /dev/null 2>&1 < /dev/null &
  sleep 20; pgrep -f "[l]at_5090.sh" >/dev/null && echo "[pf] $(date '+%F %T') lat_5090.sh started" \
    || { echo "[pf] lat_5090.sh did not start"; exit 1; }
fi
i=0
while pgrep -f "[l]at_5090.sh" >/dev/null && [ $i -lt 120 ]; do sleep 300; i=$((i + 1)); done
pgrep -f "[l]at_5090.sh" >/dev/null && { echo "[pf] lat_5090.sh still running after 10 h: not relaying"; exit 1; }
[ -s $F/LAT_VERDICT.json ] && [ -s $F/PRESS_FAST_RULE.json ] || { echo "[pf] LAT_VERDICT.json / PRESS_FAST_RULE.json missing"; exit 1; }
cat $F/LAT_VERDICT.json | /opt/mwam/bin/python -c "import json,sys; [print('[pf]', k, v['reading']) for k, v in json.load(sys.stdin).items()]"
echo "[pf] pick: $(cat $F/PRESS_FAST_RULE.json)"
if [ ! -s $F/events/events_press_button_fast.json ]; then
  /opt/mwam/bin/python -c "import json,sys; p=json.load(open('$F/PRESS_FAST_RULE.json')); sys.exit(0 if (p['delta'], p['min_path']) == (0.015, 0.03) else 1)" \
    || { echo "[pf] the pick is not rule A but events_press_button_fast.json is missing"; exit 1; }
  cp $F/events/events_press_button.json $F/events/events_press_button_fast.json
  echo "[pf] rule A kept: events_press_button_fast.json = copy of events_press_button.json"
fi
/opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py put $F/LAT_VERDICT.json $F/PRESS_FAST_RULE.json \
  $F/events/events_press_button_fast.json --prefix diag/press_fast
