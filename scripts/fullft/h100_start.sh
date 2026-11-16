#!/usr/bin/env bash
# mwam-h100n (gpu24, 4x H100 NVL; 11-16): start the training queue once the environment chain is through.
#   checks: h100_restore.sh test passed (/mnt/tmp/restore_test.log) and the newest cache fetch finished with exit 0;
#   else NOT READY, exit 1. Then, detached: the battery_try training cache from the relay (cache_fetch.sh, waits for
#   it if needed) and h100_queue.sh (smoke for the micro batch first, then the lines of h100_queue.txt as GPUs free up)
#   docker exec mwam-h100n bash /workspace/FastWAM-memory2/scripts/fullft/h100_start.sh
set -u
R=/workspace/FastWAM-memory2
cd $R
grep -q "step test finished, exit code 0" /mnt/tmp/restore_test.log 2>/dev/null \
  || { echo "NOT READY: the environment chain has not passed its tests (/mnt/tmp/restore_test.log)"; exit 1; }
F=$(ls -t outputs/fullft/CACHE_FETCH_*.txt 2>/dev/null | head -1)
grep -q "finished, exit code 0" "$F" 2>/dev/null || { echo "NOT READY: cache fetch not finished ($F)"; tail -n 3 "$F" 2>/dev/null; exit 1; }
git -c safe.directory='*' pull -q --ff-only origin memory2 && git -c safe.directory='*' log --oneline -1 | cut -c1-60
pgrep -f "[h]100_queue.sh" >/dev/null && { echo "h100_queue.sh already runs"; exit 0; }
setsid bash -c "TASKS=battery_try HFPY=/opt/hf-tools/bin/python bash $R/scripts/fullft/cache_fetch.sh > /dev/null 2>&1" &
setsid bash $R/scripts/fullft/h100_queue.sh > /dev/null 2>&1 &
sleep 20
echo "started: battery cache fetch + h100_queue.sh"
tail -n 5 "$(ls -t outputs/fullft/H100_QUEUE_*.txt | head -1)"
