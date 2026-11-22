#!/usr/bin/env bash
# 5090 HOST, 11-22 21:17 (Opus; plan v19 R0 step 1 continued, after robomme_setup_5090.sh passed at 19:11). Runs
# RoboMME's code only inside its own image robomme:582ab30 (user 18:36); the mwam5090 container only supplies two of
# our files (read with docker exec ... cat). Nothing is deleted.
#   1 download the four counting tasks' training demos (HDF5, 13.7 GB as .tar.xz: BinFill, PickXtimes, StopCube,
#     SwingXtimes) from Yinpei/robomme_data_h5 into $D/data, and unpack them there (the archives stay)
#   2 our event rule on every demo (scripts/robomme/h5_events.py + src/fastwam/fullft/events.py, copied to $D/tools):
#     per task and per count N in the goal, how many close / open / bottom / top events; for the SwingXtimes question
#     (does our 'bottom' rule see each landing?)
#   3 RoboMME's own replay check (scripts/dataset_replay.py): the first 3 demos of each counting task replayed with
#     joint_angle actions; prints each outcome (should be success); videos in $D/runs/replay_videos
# GPU: the replay pins itself to GPU 1 (its own code); it needs little memory.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && nohup bash -c "$(docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/robomme_data_5090.sh)" > ~/robomme_data.log 2>&1 &
# Log: ~/robomme_data.log ; the last line says DONE or FAILED.
set -u
if [ -d /mnt/hf ]; then D=${D:-/mnt/hf/robomme}; else D=${D:-$HOME/robomme}; fi
IMG=robomme:582ab30
TASKS="BinFill PickXtimes StopCube SwingXtimes"
say() { echo "[robomme-data] $(date '+%F %T') $*"; }
fail() { say "FAILED: $*"; exit 1; }
docker image inspect $IMG > /dev/null 2>&1 || fail "no image $IMG (run robomme_setup_5090.sh first)"
mkdir -p $D/data $D/tools $D/runs
say "start; dir $D ($(df -h $D | tail -n 1 | awk '{print $4}') free)"

say "===== 1 download + unpack"
files=""; for t in $TASKS; do files="$files record_dataset_$t.h5.tar.xz"; done
docker run --rm -v $D/data:/data $IMG uv run --no-sync hf download Yinpei/robomme_data_h5 $files --repo-type dataset \
  --local-dir /data > $D/DOWNLOAD.log 2>&1 || { tail -n 15 $D/DOWNLOAD.log; fail "download (log $D/DOWNLOAD.log)"; }
for t in $TASKS; do
  a=$D/data/record_dataset_$t.h5.tar.xz
  [ -f $a ] || fail "missing $a"
  if [ ! -f $D/data/record_dataset_$t.h5 ]; then tar -xJf $a -C $D/data || fail "unpack $a"; fi
  h=$(find $D/data -name "record_dataset_$t.h5" | head -n 1)
  [ -n "$h" ] || fail "no record_dataset_$t.h5 after unpacking $a"
  [ "$h" = $D/data/record_dataset_$t.h5 ] || ln -sf "${h#$D/data/}" $D/data/record_dataset_$t.h5   # relative: the containers mount $D/data elsewhere
  say "$t: archive $(du -h $a | cut -f1), h5 $(du -hL $D/data/record_dataset_$t.h5 | cut -f1)"
done

say "===== 2 our event rule on every demo"
docker exec mwam5090 cat /workspace/FastWAM-memory2/src/fastwam/fullft/events.py > $D/tools/events.py || fail "copy events.py"
docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/h5_events.py > $D/tools/h5_events.py || fail "copy h5_events.py"
docker run --rm -v $D/data:/data:ro -v $D/tools:/tools:ro $IMG uv run --no-sync python /tools/h5_events.py --data /data \
  > $D/EVENTS.txt 2>&1 || { tail -n 15 $D/EVENTS.txt; fail "h5_events.py"; }
cat $D/EVENTS.txt

say "===== 3 RoboMME's replay check (3 demos per counting task, joint_angle)"
docker run --rm --gpus all -e NVIDIA_DRIVER_CAPABILITIES=compute,graphics,utility,video -v $D/data:/app/data/robomme_data_h5:ro \
  -v $D/runs:/app/runs $IMG uv run --no-sync scripts/dataset_replay.py --h5-data-dir /app/data/robomme_data_h5 \
  --action-space-type joint_angle --replay-number 3 > $D/REPLAY.log 2>&1 || { tail -n 20 $D/REPLAY.log; fail "replay (log $D/REPLAY.log)"; }
grep -E "^Task:|Task goal|Outcome|Error" $D/REPLAY.log
say "replay outcomes: $(grep -o 'Outcome: [a-z]*' $D/REPLAY.log | sort | uniq -c | tr '\n' ' ')"
say "DONE (data $D/data; events $D/EVENTS.txt; replay $D/REPLAY.log)"
