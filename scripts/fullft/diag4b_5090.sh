#!/usr/bin/env bash
# mwam5090, 11-27 02:15 (Opus; plan v21 6.5 diagnostic 4(b), zero training, DESCRIBED ONLY, this machine only): the
# "count written into the instruction" version (press_told e30, MWAM_TOLD_COUNTS=1) with the TRUE count and no write
# delay added on top (MWAM_LEDGER=oracle: the press entries come from the simulator's counters, online.py oracle_presses),
# 30 development scenes (seed 7 bank, dev_eval_5090.sh's), beside the same model without the oracle on the same scenes.
# Per button: over / right / under (closed_loop_stages.py; D2's definitions) and success. Question: with the target and
# the count both given, does it still press too often?
#   q5090.txt line: diag4b | gpu | - | bash scripts/fullft/diag4b_5090.sh
# Output closed_loop/diag4b/{press_told_e30, press_told_e30_oracle}; own log outputs/fullft/DIAG4B_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
C=$O/closed_loop
LOG=$F/DIAG4B_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[d4b] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK MWAM_TOLD_COUNTS MWAM_OBJECT_LOG
PY=/opt/mwam/bin/python
G=${GPU:-${PF_GPUS:-1}}
B=$C/scenes_seed7_n30_press_button
echo "[d4b] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"
$PY scripts/memory_v2/official_scenes.py complete $B press_button 30 > /dev/null 2>&1 || { echo "[d4b] dev bank $B incomplete (dev_eval_5090.sh builds it)"; exit 1; }
RUN=press_told TAG=e30 POLL=60 bash scripts/fullft/export_fetch.sh || { echo "[d4b] press_told_e30 fetch failed"; exit 1; }
CK=$F/exports/press_told_e30/export_e30.pt
for arm in plain oracle; do
  L=press_told_e30; EXTRA="MWAM_TOLD_COUNTS=1"
  [ $arm = oracle ] && { L=press_told_e30_oracle; EXTRA="MWAM_TOLD_COUNTS=1 MWAM_LEDGER=oracle"; }
  for pass in 1 2; do
    env $EXTRA CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L --modes on \
      --scenes $B --tasks press_button --limit 30 --execute 8 --output $C/diag4b >> $C/diag4b_$L.log 2>&1
    echo "[d4b] $(date '+%F %T') $L pass $pass exit $?; episodes $(ls -d $C/diag4b/$L/on/press_button/seed_*/result.json 2>/dev/null | wc -l)"
  done
done
for L in press_told_e30 press_told_e30_oracle; do
  $PY - <<PYEOF
import json, subprocess, sys
from collections import Counter
out = "$F/align/diag4b_$L.json"
subprocess.run([sys.executable, "scripts/memory_v2/migrate/export_stages.py", "--label", "$L", "--mode", "on",
                "--folders", "$C/diag4b", "--out", out], check=True, stdout=subprocess.DEVNULL)
st = json.load(open(out))["episodes"].get("press_button", {})
r = {"episodes": len(st), "success": sum(bool(v.get("success")) for v in st.values())}
for k in ("n1_error", "n2_error"):
    e = [v[k] for v in st.values() if isinstance(v.get(k), int)]
    r[k] = {"over": sum(x > 0 for x in e), "right": sum(x == 0 for x in e), "under": sum(x < 0 for x in e)}
print("[d4b] $L", json.dumps(r))
PYEOF
done
echo "[d4b] $(date '+%F %T') DIAG 4B done (this machine only; never a verdict, never the main table)"
