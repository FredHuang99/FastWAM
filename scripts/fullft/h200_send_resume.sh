#!/usr/bin/env bash
# old H200 (mwam2), 11-17 20:05 (user approved: plan v13 E5 ar2_clock and E7 ar2_long train on the GaaS H200; the two
# H200s read IDENTICAL at 19:32, parity_h200b.py): send what only this machine has, through the relay
# (hhyfred/memwam-fullft, private):
#   1 events_put_back_block.json, events_swap_blocks.json -> diag/events_2task (READY_e5 on GaaS checks them)
#   2 outputs/fullft/ar_2task/resume.pt (72 GB, update 20077 = E7's seed) in 15 GB parts (one HF file must stay below
#     50 GB) + the sha256 of the whole file and of every part -> ckpt/ar_2task_e30/ ; parts are written to
#     outputs/fullft/xfer_ar_2task/ (kept; deleting them is the user's call). Three parts upload at a time; a part counts
#     as sent when the relay lists it with the right size (3 tries). Last: SEND_DONE (the receiver waits for it).
# CPU / disk / network only (GPU0 keeps training). Safe to run again: parts already on the relay are skipped.
#   docker exec -d mwam2 bash /workspace/FastWAM-memory2/scripts/fullft/h200_send_resume.sh
# Log: outputs/fullft/SEND_RESUME_<time>.txt ; the last line says SEND DONE or FAILED
set -u
R=${R:-/workspace/FastWAM-memory2}
F=$R/outputs/fullft
cd $R
LOG=$F/SEND_RESUME_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
HFPY=${HFPY:-/opt/hf-tools/bin/python}; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
REPO=hhyfred/memwam-fullft
P=ckpt/ar_2task_e30
say() { echo "[send] $(date '+%F %T') $*"; }
relay() { $HFPY scripts/memory_v2/migrate/relay.py "$@" --repo $REPO; }
on_relay() { relay ls --prefix $P 2>/dev/null | awk -v f="$1" '$1 == f {print $2}'; }

say "1 event files of put / swap -> diag/events_2task ($HFPY)"
for e in events_put_back_block events_swap_blocks; do
  [ -s $F/events/$e.json ] || { say "FAILED: no $F/events/$e.json"; exit 1; }
done
relay put $F/events/events_put_back_block.json $F/events/events_swap_blocks.json --prefix diag/events_2task 2>&1 | tail -n 2
relay ls --prefix diag/events_2task

say "2 ar_2task/resume.pt -> $P"
SRC=$F/ar_2task/resume.pt
X=$F/xfer_ar_2task
mkdir -p $X
[ -s $SRC ] || { say "FAILED: no $SRC"; exit 1; }
ls -la --time-style=+%F_%T $SRC
if [ ! -s $X/resume.pt.sha256 ]; then
  say "sha256 of the whole file (a few minutes)"
  (cd $F/ar_2task && sha256sum resume.pt) > $X/resume.pt.sha256.tmp && mv $X/resume.pt.sha256.tmp $X/resume.pt.sha256
fi
cat $X/resume.pt.sha256
if [ ! -f $X/.split_done ]; then
  say "split into 15 GB parts"
  split -b 15G -d -a 2 $SRC $X/resume.pt.part_ || { say "FAILED: split"; exit 1; }
  (cd $X && sha256sum resume.pt.part_*) > $X/parts.sha256
  touch $X/.split_done
fi
cat $X/parts.sha256
send_one() {
  local p=$1 sz n t
  sz=$(stat -c %s $X/$p)
  for t in 1 2 3; do
    n=$(on_relay $p)
    [ "$n" = "$sz" ] && { say "$p on the relay ($sz bytes)"; return 0; }
    say "$p upload, try $t"
    relay put $X/$p --prefix $P 2>&1 | tail -n 1
  done
  n=$(on_relay $p)
  [ "$n" = "$sz" ] && { say "$p on the relay ($sz bytes)"; return 0; }
  say "$p NOT on the relay after 3 tries"; return 1
}
PARTS=$(cd $X && ls resume.pt.part_*)
PIDS=()                                       # explicit pids: a bare `wait` would also wait for the log's tee
for p in $PARTS; do
  send_one $p > $X/.send_$p.log 2>&1 &
  PIDS+=($!)
  if [ ${#PIDS[@]} -ge 3 ]; then wait ${PIDS[0]}; PIDS=("${PIDS[@]:1}"); fi
done
for q in "${PIDS[@]}"; do wait $q; done
cat $X/.send_*.log | grep 'on the relay\|NOT on'
relay put $X/resume.pt.sha256 $X/parts.sha256 --prefix $P 2>&1 | tail -n 1
bad=0
for p in $PARTS; do [ "$(on_relay $p)" = "$(stat -c %s $X/$p)" ] || bad=1; done
[ "$(on_relay parts.sha256)" ] || bad=1
if [ $bad = 1 ]; then say "FAILED: not every part is on the relay (run this script again)"; exit 1; fi
echo "$PARTS" > $X/SEND_DONE
relay put $X/SEND_DONE --prefix $P 2>&1 | tail -n 1
relay ls --prefix $P
say "SEND DONE"
