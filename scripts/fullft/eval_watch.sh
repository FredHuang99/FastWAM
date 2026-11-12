#!/usr/bin/env bash
# mwam5090 container (plan v11 N8 / G1, Opus checklist 6 in its minimal form): evaluate the N7 exports with nobody at
# the keyboard. For each tag in order:
#   1 wait until the relay lists exports/<RUN>_<TAG>/export_<TAG>.pt.sha256 (export_watch.sh on the H200 uploads it
#     last), fetch the export once and check its sha256
#   2 e10, e20: progress checks, no verdict: e10 ran N=20; from 11-12 N=NPRE (50), put on GPU1 and swap on GPU0
#     (one-task runs, so no G1 line)
#     e30: N=50 = G1. put on GPU0 and swap on GPU1 in parallel (each waits for its GPU), then the verdict pass
#     (g1_loop.sh VERDICT_ONLY=1, pre-registered G1 rule unchanged)
# Resumable: finished episodes are kept; a tag with its marker outputs/fullft/exports/<RUN>_<TAG>/.evaluated is skipped.
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/eval_watch.sh
# Env: RUN (ar_2task), TAGS ("e10 e20 e30"), POLL seconds (300), MWAM_TEXT_SOURCE (cache), MWAM_OIDN_LIB (2.0.1 sass120 if built). Own log: outputs/memory_v2/report/EVAL_WATCH_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
RUN=${RUN:-ar_2task}; TAGS=${TAGS:-"e10 e20 e30"}; POLL=${POLL:-300}
LOG=$O/report/EVAL_WATCH_$(date +%Y%m%d_%H%M).txt
mkdir -p $O/report
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[eval] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
HFPY=/opt/hf-tools/bin/python
# 11-12 12:35 (user: 改): from e20 on, the instruction's text features come from the dense TRAINING cache on both machines
# (identical inputs, and what training saw) instead of this machine's CPU T5 (2.4% off the cache). Inherited by g1_loop.sh.
export MWAM_TEXT_SOURCE=${MWAM_TEXT_SOURCE:-cache}
# 11-12 13:50: the simulator loads the OIDN 2.0.1 built here for RTX 50 (oidn201_build.sh; frame 0 vs the A100's 2.0.1:
# 0.062 levels, 0.00 % > 8 levels; 2.3.3 had 0.49 / 0.5 %) instead of 2.3.3. MWAM_OIDN_LIB set by the caller wins.
NEWLIB=/opt/oidn-2.0.1-sass120/lib
[ -z "${MWAM_OIDN_LIB:-}" ] && [ -e $NEWLIB/libOpenImageDenoise.so.2 ] && export MWAM_OIDN_LIB=$NEWLIB
echo "[eval] $(date '+%F %T') start; tags $TAGS; text source $MWAM_TEXT_SOURCE; denoiser ${MWAM_OIDN_LIB:-default (2.3.3 fix folder)}"
cd $R
free_gpu() { for g in "$@"; do u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $g | tr -d ' ');
             [ "$u" -lt 2000 ] && { echo $g; return 0; }; done; return 1; }
free_stable() { [ -n "$(free_gpu $1)" ] || return 1; sleep 90; [ -n "$(free_gpu $1)" ]; }
done_n() { ls $O/closed_loop/g1/${RUN}_${TAG}/on/$1/seed_*/result.json 2>/dev/null | grep -cE 'seed_[0-9]+/result.json'; }
for TAG in $TAGS; do
  E=$R/outputs/fullft/exports/${RUN}_${TAG}
  [ -f $E/.evaluated ] && { echo "[eval] $TAG: already evaluated"; continue; }
  echo "[eval] $(date '+%F %T') waiting for exports/${RUN}_${TAG} on the relay"
  until $HFPY scripts/memory_v2/migrate/relay.py ls --prefix exports/${RUN}_${TAG} --repo hhyfred/memwam-fullft 2>/dev/null \
        | grep -q "^export_${TAG}.pt.sha256 "; do sleep $POLL; done
  if [ ! -f $E/export_${TAG}.pt ]; then
    echo "[eval] $(date '+%F %T') fetching $TAG"
    $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/${RUN}_${TAG} --repo hhyfred/memwam-fullft --out $E \
      2>&1 | grep -v "Processing\|Download\|%|"
  fi
  (cd $E && sha256sum -c export_${TAG}.pt.sha256) || { echo "[eval] $TAG sha256 mismatch: delete $E, the next run refetches"; exit 1; }
  # 11-12 16:05: one task per GPU (e30: put GPU0, swap GPU1; progress checks: put GPU1, swap GPU0), a GPU counts as
  # empty only if it is still empty 90 s later (16:00 the e20 put started on GPU0 in the 6 s gap between AL3's put and
  # swap runs, both crashed, and the tag was marked evaluated with nothing run), up to 3 attempts per task, and the tag
  # is marked evaluated only when every task has N finished episodes. Progress checks: N=NPRE (50), no G1 line.
  if [ "$TAG" = e30 ]; then N=50; PAIRS="0:put_back_block 1:swap_blocks"; else N=${NPRE:-50}; PAIRS="1:put_back_block 0:swap_blocks"; fi
  pids=""
  for pair in $PAIRS; do
    g=${pair%%:*}; t=${pair#*:}
    ( for attempt in 1 2 3; do
        until free_stable $g; do sleep $POLL; done
        echo "[eval] $(date '+%F %T') $TAG: $t scenes 1-$N on GPU $g (attempt $attempt)"
        RUN=$RUN TAG=$TAG N=$N GPU=$g TASKS=$t SKIP_SMOKE=$([ $t = swap_blocks ] && echo 1 || echo 0) \
          bash scripts/fullft/g1_loop.sh > /dev/null 2>&1
        n=$(done_n $t)
        [ "$n" -ge "$N" ] && { echo "[eval] $(date '+%F %T') $TAG: $t finished $n/$N"; exit 0; }
        echo "[eval] $(date '+%F %T') $TAG: $t only $n/$N finished; retry"; sleep $POLL
      done; exit 1 ) &
    pids="$pids $!"
  done
  wait $pids      # 11-12: a bare `wait` also waits for the tee process substitution of `exec > >(tee)` and never returns
  ok=1; for pair in $PAIRS; do t=${pair#*:}; [ "$(done_n $t)" -ge "$N" ] || ok=0; done
  if [ $ok != 1 ]; then echo "[eval] $(date '+%F %T') $TAG incomplete after 3 attempts: NOT marked; rerun this script"; continue; fi
  [ "$TAG" = e30 ] && RUN=$RUN TAG=$TAG N=50 VERDICT_ONLY=1 bash scripts/fullft/g1_loop.sh > /dev/null 2>&1
  touch $E/.evaluated
  L=$(ls -t $O/report/G1_${RUN}_${TAG}*_*.txt | head -1)
  echo "[eval] $(date '+%F %T') $TAG done; newest log $L:"; grep -E "finished [0-9]|success|G1 " $L | tail -n 6
done
