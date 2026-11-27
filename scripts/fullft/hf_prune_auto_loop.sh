#!/usr/bin/env bash
# A40, 11-27 13:30 (Opus; user 11-27 13:19 agreed to the automatic pruning of intermediate exports above 85 %, see
# hf_prune_auto.py). Every 60 min until 11-28 14:00 (Beijing; the user takes over then): refresh HF_USAGE.json
# (hf_usage.py, read-only), then hf_prune_auto.py (does nothing at <= 85 %). A failed attempt is logged and retried at
# the next hour; it never stops the loop. Log: outputs/fullft/HF_PRUNE_AUTO.log (results push carries HF_PRUNE_AUTO.json).
# 11-27 22:10: every line now also goes to stdout (the queue5 job log): the pool stops a task whose job log is not
# written for 120 min, and the first version wrote only to HF_PRUNE_AUTO.log -> stopped 3 times, ERROR at 19:59.
# The longest silent stretch is now max(hf_usage 20 min, hf_prune_auto 90 min, sleep 60 min) < 120 min.
set -u
R=/workspace/FastWAM-memory2
cd $R
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
LOG=$R/outputs/fullft/HF_PRUNE_AUTO.log
END=$(TZ=Asia/Shanghai date -d '2026-11-28 14:00' +%s)
while [ "$(date +%s)" -lt "$END" ]; do
  {
    echo "[autoprune-loop] $(TZ=Asia/Shanghai date '+%F %T') usage refresh + check"
    timeout 1200 $HFPY scripts/fullft/hf_usage.py > /dev/null 2>&1 || echo "[autoprune-loop] hf_usage.py failed (exit $?)"
    echo "[autoprune-loop] $(TZ=Asia/Shanghai date '+%F %T') usage refreshed; prune check"
    timeout 5400 $HFPY scripts/fullft/hf_prune_auto.py 2>&1 | tail -n 20 || echo "[autoprune-loop] hf_prune_auto.py failed"
    echo "[autoprune-loop] $(TZ=Asia/Shanghai date '+%F %T') next check in 60 min"
  } 2>&1 | tee -a $LOG
  sleep 3600
done
echo "[autoprune-loop] $(TZ=Asia/Shanghai date '+%F %T') window over (11-28 14:00)" | tee -a $LOG
