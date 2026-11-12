#!/usr/bin/env bash
# mwam5090 container, night 11-12 (plan v12, written 00:50 before any of these runs): keep both 5090 GPUs busy until
# the e20 export (~13:45) with work the plan uses. Runs after the AL1 replay (al1_5090.sh) on GPU1; GPU0 belongs to
# eval_watch.sh until its e10 screening is marked .evaluated.
#   1 C2 check (AL2 candidate, ~5 min, GPU1): frame 0 of put seed 4300030 rendered with SAPIEN's BUNDLED OIDN 2.0.1
#     forced to the CPU device (OIDN_DEFAULT_DEVICE=cpu, no 2.3.3 preload) vs the A100's 2.0.1 frame 0 (npz_diff).
#     Reading (AL2 candidate rule, v12 F.1): no "OIDN Error" lines AND mean <= 0.05 levels AND > 8 levels <= 0.01 %
#     -> C2 qualifies (AL3 next, scheduled by Opus); OIDN errors -> SAPIEN does not take the CPU device this way.
#   2 S1 pre-read on e10 (GPU1, descriptive; the S1 verdict stays on e30): N7 epoch 10 with the denoiser OFF
#     (MWAM_OIDN=off), put + swap scenes 1-20 = the scenes of the e10 screening (2.3.3) on GPU0; paired report:
#     brittle = delta <= -0.15 with CI upper < 0, robust = |delta| <= 0.05 (v11 S-E wording); a base robust to NO
#     denoiser is robust to a denoiser VERSION, i.e. a strong hint for AL4
#   3 e10 screening extended to scenes 21-50 (descriptive: more new-base episodes for K0b and the progress curve), put
#     on GPU0 and swap on GPU1 in parallel (g1_loop.sh N=50, resumable; scenes 1-20 already done)
# Own log: outputs/fullft/NIGHT_5090_<time>.txt
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/night_5090.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
A=$R/outputs/fullft/align
LOG=$R/outputs/fullft/NIGHT_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[night] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[night] $(date '+%F %T') ===== $*"; }
cd $R
PY=/opt/mwam/bin/python
SIM=/opt/rmbench-fused-env/bin/python
E=$R/outputs/fullft/exports/ar_2task_e10
empty() { u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' '); [ "$u" -lt 2000 ]; }

step "0 wait for the AL1 replay (GPU1) to finish"
while pgrep -f al1_5090.sh >/dev/null; do sleep 300; done
until empty 1; do echo "[night] GPU1 busy; waiting"; sleep 300; done
tail -n 3 $(ls -t $A/AL1_5090_*.txt | head -1)

step "1 C2 check: bundled OIDN 2.0.1 on the CPU device, frame 0 vs the A100's 2.0.1"
(cd /workspace/FastWAM/resources/RMBench && CUDA_VISIBLE_DEVICES=1 OIDN_DEFAULT_DEVICE=cpu \
  $SIM -B -u $R/scripts/memory_v2/migrate/render_check.py --task put_back_block --seed 4300030 --variants default \
  > $A/c2_render.log 2>&1)
echo "render_check exit code $?; OIDN error lines: $(grep -c 'OIDN Error' $A/c2_render.log)"
grep -m3 "OIDN Error" $A/c2_render.log
RC=$(grep -o "RENDER_CHECK: .*\.md" $A/c2_render.log | tail -1 | sed 's/^RENDER_CHECK: //; s/RENDER_CHECK_\(.*\)\.md$/render_check_\1/')
[ -n "$RC" ] && $PY scripts/fullft/npz_diff.py --ref a100_oidn201=$A/al2/a100_oidn201_default.npz --glob "$RC/default.npz"

step "2 S1 pre-read on e10 (denoiser OFF, GPU1): waiting for the e10 export"
until [ -f $E/export_e10.pt ] && (cd $E && sha256sum -c export_e10.pt.sha256 >/dev/null 2>&1); do
  echo "[night] $(date '+%F %T') e10 not here yet"; sleep 300; done
for t in put_back_block swap_blocks; do
  for pass in 1 2; do
    CUDA_VISIBLE_DEVICES=1 MWAM_OIDN=off PYTHONPATH=src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      $PY -m fastwam.memory_v2.online run --checkpoint $E/export_e10.pt --label ar_2task_e10_oidnoff \
      --scenes $O/closed_loop/scenes_seed42_n100_$t --tasks $t --limit 20 --execute 8 --output $O/closed_loop/s1pre \
      >> $O/closed_loop/s1pre_run.log 2>&1
  done
  echo "[night] $(date '+%F %T') $t finished: $(ls $O/closed_loop/s1pre/ar_2task_e10_oidnoff/on/$t/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
done

step "3 e10 screening extended to scenes 21-50 (put GPU0, swap GPU1), after eval_watch marks e10 evaluated"
until [ -f $E/.evaluated ]; do echo "[night] $(date '+%F %T') e10 screening (eval_watch) still running"; sleep 300; done
PYTHONPATH=src $PY scripts/fullft/pair_eq.py --name s1pre_e10 --rule report --a-folders closed_loop/s1pre \
  --a-label ar_2task_e10_oidnoff --b-folders closed_loop/g1 --b-label ar_2task_e10
until empty 0; do sleep 120; done
( RUN=ar_2task TAG=e10 N=50 GPU=0 TASKS=put_back_block SKIP_SMOKE=1 bash scripts/fullft/g1_loop.sh > /dev/null 2>&1 ) &
P1=$!
( RUN=ar_2task TAG=e10 N=50 GPU=1 TASKS=swap_blocks SKIP_SMOKE=1 bash scripts/fullft/g1_loop.sh > /dev/null 2>&1 ) &
P2=$!
wait $P1 $P2      # 11-12: a bare `wait` also waits for the tee process substitution and never returns (hung here 11-12 05:18)
for t in put_back_block swap_blocks; do
  echo "[night] e10 $t finished: $(ls $O/closed_loop/g1/ar_2task_e10/on/$t/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json')"
done
$PY scripts/memory_v2/loop_peek.py --folder closed_loop/g1 --label ar_2task_e10 --out /dev/null | tail -n 12
echo "[night] done; both GPUs free for the e20 screening (eval_watch picks it up)"
