#!/usr/bin/env bash
# Old H200 HOST, 11-23 15:10 (Opus; user 14:53 "排序更重要就先训排序", 15:04 "同意用放得下的最大值" = 69 entries:
# text_slots.py, the ranking instruction leaves 69 empty text positions). Puts the ranking body record before the
# seed-18 replicate that the queue started at 00:20 (it keeps its progress and resumes after ranking). Steps (stops at
# the first failed check; nothing is deleted except our own STOP flag after use):
#   1 ranking ready with 69 entries: ledger_ready.py (event file vs cache, 69 text slots) -> READY marker; else stop
#     (the seed-18 run keeps training)
#   2 stop the queue loop (h200_queue.sh, ours) so that it does not retry the seed-18 run when it stops
#   3 ar2_prop_s18/STOP: the trainer saves resume.pt and exits (wait up to 40 min); our STOP flag is then removed
#   4 start the queue again: its first runnable line is now ranking_arprop (69 entries); ar2_prop_s18 has no
#     SUMMARY.json, so it resumes from resume.pt after ranking. Queue log after 3 min.
#   docker exec mwam2 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && bash -c "$(docker exec mwam2 cat /workspace/FastWAM-memory2/scripts/fullft/h200_ranking_first.sh)" 2>&1 | tee ~/h200_ranking_first.log
set -u
C=mwam2
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
say() { echo "[rank1st] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
inside() { docker exec $C bash -c "$1"; }
fail() { say "STOP: $*"; exit 1; }
inside "grep -q 'history.event_max=69' $R/scripts/fullft/h200_queue.txt" || fail "the queue file still says 80 (git pull in $C first)"
say "1 ranking readiness with 69 entries"
inside "cd $R && PYTHONPATH=src CUDA_VISIBLE_DEVICES= /opt/mwam/bin/python scripts/fullft/ledger_ready.py --variant arprop --tasks blocks_ranking_try --event-max 69 --marker READY_arprop_blocks_ranking_try --skip-tests 2>&1 | grep -v '^\.\+\$' | tail -n 5"
inside "test -f $F/READY_arprop_blocks_ranking_try" || fail "ranking not ready (above); the seed-18 run keeps training"
say "ranking READY"
say "2 stop the queue loop"
inside "pkill -f '[s]cripts/fullft/h200_queue.sh'"; sleep 3
inside "pgrep -f '[s]cripts/fullft/h200_queue.sh' > /dev/null" && fail "the queue loop is still running"
say "3 seed-18 run: save and stop"
inside "test -d $F/ar2_prop_s18" || fail "no ar2_prop_s18 folder"
inside "touch $F/ar2_prop_s18/STOP"
for i in $(seq 1 80); do
  inside "pgrep -f '[f]astwam.fullft.train' > /dev/null" || break
  [ $i = 80 ] && fail "the trainer still runs after 40 min (STOP flag left in place; queue NOT restarted)"
  sleep 30
done
inside "rm -f $F/ar2_prop_s18/STOP"
say "trainer stopped; $(inside "grep -a 'resume checkpoint saved' $F/QUEUE_ar2_prop_s18.log | tail -n 1 | cut -c1-120")"
inside "ls -la --time-style=+%H:%M $F/ar2_prop_s18/resume.pt | awk '{print \"resume.pt\", \$5, \"bytes,\", \$6}'"
say "4 queue again"
docker exec -d $C bash $R/scripts/fullft/h200_queue.sh
sleep 180
inside "tail -n 8 \$(ls -t $F/H200_QUEUE_*.txt | head -1)"
say "done"
