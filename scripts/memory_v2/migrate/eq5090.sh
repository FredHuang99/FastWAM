#!/usr/bin/env bash
# mwam5090 container (11-10 night; plan v9 node N0): the two unknowns that decide what the two 5090s can do. Existing
# code only; read-only for the queue (no state, verdict or autopsy is written). GPU ${GPU:-0} only, which must be EMPTY
# and must stay out of the pool's allowed GPUs (it is: allowed = [1]).
#   1 Does X7's stage-2 training (action expert trainable) fit in 32 GB at a smaller micro batch? profile_step dry runs
#     (3 updates): x7_nopairs_m2, x7_m2 (the X7 recipe at micro batch 2), x7 (as saved: micro batch 4, 30.5-32.5 GiB on
#     the A100, expected to run out of memory here). -> report/PROFILE_X7_5090_<time>.md
#   2 Is the 5090 closed loop behaviourally equivalent to the A100 / H200 at TEN Euler steps? S2 / S4 were 2 / 4 steps and
#     have no A100 counterpart (and one step collapsed on the A100 too: S1); the first-decision check found the A100's
#     chunk delayed by 2 targets, which may or may not matter over an episode. X7 (a2C_6ep), memory on, execute 8,
#     10 steps, the official scenes: put_back 1-60, then swap 1-40 (resumable: finished episodes are skipped).
#     -> closed_loop/eq5090, label x7_eq5090
# Reference (official table 11-03; A100 / H200, 100 scenes, same checkpoint and settings):
#   put_back X7 on: lifted 98 centre 95 pressed 46 regrasp 40 returned 28 success 17, progress 0.528
#   swap     X7 on: lifted 100 s1 100 s2 90 s3 52 pressed 48 success 37, progress 0.693
# Coarse reading, written before the run (UNPAIRED, binomial bands with both samples' errors; the verdict of N0a is the
# paired comparison on the same scenes, once the A100's per-scene progress is exported):
#   put_back (n = 60)  looks equivalent: lifted >= 54 and centre >= 51 and pressed / centre in [0.32, 0.65]
#                      clearly different: lifted < 48 or pressed / centre < 0.20
#   swap (n = 40)      looks equivalent: s1 >= 36 and s2 >= 30 and success in [8, 22]
#                      clearly different: s2 < 24 or success <= 3
#   anything else: undecided until the paired comparison.
# Own log: /workspace/FastWAM-memory2/outputs/memory_v2/report/EQ5090_<time>.txt
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/eq5090.sh      (about 6-10 h)
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/EQ5090_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report" "$O/closed_loop"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[eq5090] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[eq5090] $(date '+%F %T') ===== $*"; }
cd "$R"
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping (choose an empty GPU that the pool may not use: GPU=<n>)"; exit 1; }
export PYTHONPATH=$R/src CUDA_VISIBLE_DEVICES=$GPU
PY=/opt/mwam/bin/python
CK=$O/a2C_6ep/checkpoints/update_004020.pt
ls -la "$CK" || { echo "X7 checkpoint missing"; exit 1; }

step "1 stage-2 training in 32 GB? (dry runs, 3 updates each; a failed case is reported and the next one runs)"
$PY scripts/memory_v2/profile_step.py --cases x7_nopairs_m2 x7_m2 x7 --updates 3 --tag X7_5090 \
  > $O/report/eq5090_profile_run.log 2>&1
echo "profile exit code $?"
grep -E '^\[profile\]|s / update|peak GPU memory|FAILED|^PROFILE:' $O/report/eq5090_profile_run.log | tail -n 30
grep -E 'OutOfMemory|out of memory|No such file|FileNotFoundError|Error:' $O/report/eq5090_profile_run.log | sort | uniq -c | tail -n 8

# The policy (about 24 GiB) and its simulator processes (about 7 GiB) fill the 32 GB card: S1 lost an episode here to an
# 80 MiB allocation with 0.5 GiB reserved but unallocated. Expandable segments avoid that fragmentation (no effect on
# the numbers); an episode that still fails is retried once by the second pass (finished episodes are skipped).
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
run_bank() {   # task, scenes folder, first N scenes
  step "2 closed loop $1: X7 on, 10 steps, execute 8, official scenes 1-$3"
  [ -d "$2" ] || [ -f "$2" ] || { echo "scene bank $2 missing: skipped"; return; }
  for pass in 1 2; do
    $PY -m fastwam.memory_v2.online run --checkpoint $CK --label x7_eq5090 --scenes "$2" --tasks "$1" --limit "$3" \
      --execute 8 --output $O/closed_loop/eq5090 >> $O/closed_loop/eq5090_run.log 2>&1
    echo "pass $pass exit code $?; finished episodes: $(ls $O/closed_loop/eq5090/x7_eq5090/on/$1/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
  done
  grep -E "ERROR" $O/closed_loop/eq5090_run.log | tail -n 3
}
run_bank put_back_block $O/closed_loop/scenes_seed42_n100_put_back_block 60
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/eq5090 --label x7_eq5090 --out /dev/null
run_bank swap_blocks $O/closed_loop/scenes_seed42_n100_swap_blocks 40

step "3 stage tables (compare with the reference lines and the reading in this script's header)"
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/eq5090 --label x7_eq5090 --out /dev/null
echo
echo "reference (A100 / H200, 100 scenes): put_back lifted 98 centre 95 pressed 46 regrasp 40 returned 28 success 17 (0.528);"
echo "                                     swap lifted 100 s1 100 s2 90 s3 52 pressed 48 success 37 (0.693)"
echo "reading (unpaired, coarse): put_back n=60 equivalent if lifted>=54, centre>=51, pressed/centre in [0.32,0.65];"
echo "  different if lifted<48 or pressed/centre<0.20. swap n=40 equivalent if s1>=36, s2>=30, success in [8,22];"
echo "  different if s2<24 or success<=3. Otherwise undecided until the paired comparison (plan v9 N0a)."
