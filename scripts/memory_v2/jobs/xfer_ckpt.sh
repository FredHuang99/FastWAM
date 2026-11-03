#!/usr/bin/env bash
# A100 HOST (root): copy the inference-only (slim) checkpoint of a memory_v2 run to the H200, with a sha256 file that the
# H200 waiting tasks (W-x2b-ckpt / W-t2-ckpt) check. Optionally waits for a training task's verdict first.
# Writes its own log: /root/mwam_reports/xfer_<run>_<time>.log
#
#   bash /root/mwam_reports/xfer_ckpt.sh a2C_nopairs_ours update_002010.pt              # now
#   setsid nohup bash /root/mwam_reports/xfer_ckpt.sh a2C_onestage_6ep update_004020.pt T2 >/dev/null 2>&1 &
#                                                     # waits for T2's verdict (PASS required), then copies
set -u
RUN=${1:?run name}; FILE=${2:?checkpoint file, e.g. update_002010.pt}; WAIT=${3:-}
C=${C:-6e4b37a15066}
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
H=${H200:-air@10.97.176.167}
K="-i /root/.ssh/id_h200 -o BatchMode=yes"
HO=/storage/ssd/hhy/mwam2/FastWAM-memory2/outputs/memory_v2
mkdir -p /root/mwam_reports
LOG=/root/mwam_reports/xfer_${RUN}_$(date +%Y%m%d_%H%M).log
exec >> "$LOG" 2>&1
say() { echo "[xfer] $(date '+%F %T') $*"; }
say "run $RUN file $FILE wait ${WAIT:-none}; log $LOG"
if [ -n "$WAIT" ]; then
  while :; do
    v=$(docker exec $C /opt/mwam/bin/python -c "import json; s=json.load(open('$O/queue5/state/$WAIT.json')); print(s.get('status'), s.get('verdict'))" 2>/dev/null)
    case "$v" in
      "done PASS") say "$WAIT: PASS"; break ;;
      done*) say "$WAIT finished without PASS ($v): nothing copied"; exit 1 ;;
      *) sleep 300 ;;
    esac
  done
fi
SRC=$O/$RUN/checkpoints/$FILE
docker exec $C test -f "$SRC" || { say "missing $SRC"; docker exec $C ls -la "$O/$RUN/checkpoints/"; exit 1; }
say "slim $SRC"
docker exec $C bash -lc "cd $R && mkdir -p $O/xfer && PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/slim_checkpoint.py $SRC $O/xfer/${RUN}_$FILE" || { say "slim failed"; exit 1; }
STAGE=/root/xfer_$RUN
rm -rf "$STAGE" && mkdir -p "$STAGE"
docker cp "$C:$O/xfer/${RUN}_$FILE" "$STAGE/$FILE" || exit 1
(cd "$STAGE" && sha256sum "$FILE" > "$FILE.sha256") && cat "$STAGE/$FILE.sha256"
ls -la "$STAGE"
ssh -n $K $H "mkdir -p $HO/$RUN/checkpoints && rm -f $HO/$RUN/checkpoints/$FILE.sha256" || exit 1
say "scp -> $H:$HO/$RUN/checkpoints/ (checkpoint first, sha256 last: the H200 task starts only when both are there)"
scp $K "$STAGE/$FILE" "$H:$HO/$RUN/checkpoints/$FILE" && scp $K "$STAGE/$FILE.sha256" "$H:$HO/$RUN/checkpoints/$FILE.sha256" || { say "scp failed"; exit 1; }
ssh -n $K $H "cd $HO/$RUN/checkpoints && sha256sum -c $FILE.sha256" && say "DONE: verified on the H200" || { say "sha256 check FAILED on the H200"; exit 1; }
