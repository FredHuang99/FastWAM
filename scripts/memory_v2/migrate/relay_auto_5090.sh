#!/usr/bin/env bash
# mwam5090 container, 11-21 16:20 (Opus; user 16:01: "automate it; mind the accuracy of what is deleted and the
# completeness of the download"; user 15:46: the 5090 stores everything, HF keeps only what is necessary).
#   0 wait until the mirror started 15:53 (relay_mirror.py) has ended
#   1 relay_mirror.py again (resumable: fetches whatever is missing or failed), up to 3 runs, until it exits 0
#   2 relay_mirror.py --finalize: every file on HF gets its own file under /mnt/hf/relay_mirror (files the 5090 held
#     are hard-linked there, else copied) and every one is sha256-checked against HF; must exit 0
#   3 relay_prune.py dry run: the deletion plan; every file to delete re-hashed on the 5090 copy; must exit 0
#   4 stop here if /mnt/hf/relay_mirror/NO_DELETE exists (the user's off switch)
#   5 relay_prune.py --yes: delete the two migration repos and the mirrored exports/ + ckpt/ of memwam-fullft
#     (kept: memwam-caches, memwam-diag-v1, fastwam-memory-s1-backup, and anything uploaded after the mirror)
#   6 relay_prune.py dry run again (must find nothing left to delete) and relay_usage.py (what HF stores now)
# Any failure before 5 stops the chain with nothing deleted. The scripts are copied at the start, so later pushes
# do not change a running chain. Log /mnt/hf/relay_mirror/AUTO_<time>.txt; last exit code in AUTO_RESULT.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/relay_auto_5090.sh
set -u
R=/workspace/FastWAM-memory2
D=/mnt/hf/relay_mirror
mkdir -p $D
LOG=$D/AUTO_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[auto] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
trap 'rc=$?; say "finished, exit code $rc; log $LOG"; echo "$rc $(date +%F_%T)" > $D/AUTO_RESULT' EXIT
P=/opt/hf-tools/bin/python; [ -x $P ] || P=/opt/mwam/bin/python
export HF_HUB_DISABLE_PROGRESS_BARS=1
cd $R
C=$D/code_$(git -c safe.directory='*' log --format=%h -1)
mkdir -p $C && cp scripts/memory_v2/migrate/relay_mirror.py scripts/memory_v2/migrate/relay_prune.py \
  scripts/memory_v2/migrate/relay_usage.py $C/
say "start; code $(basename $C); free $(df -h $D | tail -n 1 | awk '{print $4}')"
mkdir $D/.auto_lock 2>/dev/null || { say "another chain holds $D/.auto_lock: stop"; trap - EXIT; exit 1; }
trap 'rc=$?; rmdir $D/.auto_lock; say "finished, exit code $rc; log $LOG"; echo "$rc $(date +%F_%T)" > $D/AUTO_RESULT' EXIT

say "0 waiting for the running mirror to end"
while pgrep -f "[r]elay_mirror.py --dest" > /dev/null; do sleep 300; done
say "0 mirror ended: $(tail -n 1 $(ls -t $D/MIRROR_*.txt | head -1))"

ok=0
for run in 1 2 3; do
  say "1 mirror pass $run"
  nice -n 10 $P $C/relay_mirror.py --dest $D > $D/MIRROR_auto$run.txt 2>&1
  rc=$?; say "1 mirror pass $run exit code $rc: $(tail -n 1 $D/MIRROR_auto$run.txt)"
  [ $rc = 0 ] && { ok=1; break; }
  sleep 600
done
[ $ok = 1 ] || { say "STOP: the mirror is not complete after 3 passes; nothing deleted"; exit 2; }

say "2 finalize (own copy of every HF file, sha256 against HF)"
nice -n 10 $P $C/relay_mirror.py --dest $D --finalize; rc=$?
[ $rc = 0 ] || { say "STOP: finalize exit code $rc; nothing deleted"; exit 2; }

say "3 deletion plan (dry run, every copy re-hashed)"
nice -n 10 $P $C/relay_prune.py; rc=$?
[ $rc = 0 ] || { say "STOP: the plan did not pass its checks (exit code $rc); nothing deleted"; exit 2; }

[ -f $D/NO_DELETE ] && { say "STOP: $D/NO_DELETE exists (the user's off switch); nothing deleted"; exit 0; }

say "5 deleting on HF (irreversible)"
$P $C/relay_prune.py --yes; rc=$?
[ $rc = 0 ] || { say "the deletion step exited $rc: see above (step 6 still shows what HF holds)"; }

say "6 check: nothing left to delete; what HF stores now"
$P $C/relay_prune.py 2>&1 | grep -E "delete|REFUSED|does not exist|total"
$P $C/relay_usage.py --top 10
say "done; the mirror is $D ($(du -sh $D | cut -f1)), manifest $D/MIRROR_MANIFEST.json"
