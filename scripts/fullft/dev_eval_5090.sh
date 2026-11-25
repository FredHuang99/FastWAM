#!/usr/bin/env bash
# mwam5090, 11-24 (Opus; plan v20 section 5 "开发场景快评", v19 R2): 30 development scenes per task, another seed set
# (seed 7 -> RMBench's rule 100000 x (1 + 7) = 800,000 upwards; disjoint from the official seed-42 bank 4.3M+, the
# older 5090 banks 1.8-2.1M, the demos' and card 8's 10M+), on this machine only (5090 = its own comparison group;
# never a verdict, never the main table). Used to look early at e10 / e20 and to pick checkpoints.
#   DEV_RUNS="label:task[:K=V,K=V] ..."  (11-25: an optional third field = env for that run only, e.g.
#   press_told_e10:press_button:MWAM_TOLD_COUNTS=1)  each = an export exports/<label> (here, else the relay mirror, else the relay;
#   sha256 checked) on its task's 30 dev scenes, execute 8, default noise -> closed_loop/dev7/<label>
#   Results: one line per run in outputs/fullft/DEV_EVAL.tsv (time, label, task, successes, finished)
#   docker exec -d -e DEV_RUNS="ranking_ar_e30:blocks_ranking_try" mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/dev_eval_5090.sh
# GPU: PF_GPUS (default 1), waits until it is empty. Own log: outputs/fullft/DEV_EVAL_5090_<time>.txt
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
C=$O/closed_loop
OUT=$C/dev7
LOG=$F/DEV_EVAL_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[dev] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_HIST_MASK MWAM_TOLD_COUNTS MWAM_OBJECT_LOG
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python
G=${PF_GPUS:-1}
say() { echo "[dev] $(date '+%F %T') $*"; }
empty() { local u; u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 2>/dev/null | tr -d ' '); [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ]; }
export_of() {       # label (run_tag) -> checked export path
  local L=$1 tag=${1##*_} E=$F/exports/$1 M=/mnt/hf/relay_mirror/memwam-fullft/exports/$1
  if [ ! -f $E/export_$tag.pt ] && [ -f $M/export_$tag.pt ]; then E=$M; fi
  if [ ! -f $E/export_$tag.pt ]; then
    E=$F/exports/$L; mkdir -p $E
    $HFPY scripts/memory_v2/migrate/relay.py get --prefix exports/$L --repo hhyfred/memwam-fullft --out $E 2>&1 | grep -v "Processing\|Download\|%|" >&2
  fi
  (cd $E && sha256sum -c --quiet export_$tag.pt.sha256) >&2 && echo $E/export_$tag.pt
}
bank() {            # task -> complete 30-scene dev bank
  local t=$1 B=$C/scenes_seed7_n30_$1
  $PY scripts/memory_v2/official_scenes.py complete $B $t 30 > /dev/null 2>&1 && { echo $B; return 0; }
  for i in $(seq 1 40); do
    $PY scripts/memory_v2/official_scenes.py complete $B $t 30 > /dev/null 2>&1 && break
    CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online plan --seed 7 --episodes 30 --tasks $t --output $B >> $C/dev7_bank_$t.log 2>&1 && continue
    $PY scripts/memory_v2/official_scenes.py skip-expert-error $B $t > /dev/null 2>&1; [ $? -eq 1 ] && return 1
  done
  $PY scripts/memory_v2/official_scenes.py complete $B $t 30 > /dev/null 2>&1 && echo $B
}
say "checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G; runs: ${DEV_RUNS:-none}"
[ -n "${DEV_RUNS:-}" ] || { say "DEV_RUNS is empty: nothing to do"; exit 0; }
BAD=0
mkdir -p $OUT; [ -f $F/DEV_EVAL.tsv ] || printf 'time\tlabel\ttask\tsuccess\tfinished\n' > $F/DEV_EVAL.tsv
for item in $DEV_RUNS; do
  L=${item%%:*}; T=${item#*:}; EV=""
  case $T in *:*) EV=${T#*:}; T=${T%%:*};; esac
  until empty $G; do say "GPU $G in use; waiting 5 min"; sleep 300; done
  B=$(bank $T) || { say "$T: dev bank failed (see $C/dev7_bank_$T.log)"; continue; }
  CK=$(export_of $L) || true
  [ -n "$CK" ] || { say "$L: no checked export"; continue; }
  for pass in 1 2; do
    env $(echo "$EV" | tr ',' ' ') CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label $L \
      --scenes $B --tasks $T --limit 30 --execute 8 --output $OUT >> $C/dev7_$L.log 2>&1
  done
  n=$(ls $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | wc -l)
  k=$(cat $OUT/$L/on/$T/seed_*/result.json 2>/dev/null | grep -c '"success": true')
  printf '%s\t%s\t%s\t%s\t%s\n' "$(date '+%F %T')" "$L" "$T" "$k" "$n" >> $F/DEV_EVAL.tsv
  say "DEV $L on $T: $k / $n (30 dev scenes; 5090 only)"
  if [ "$n" = 0 ]; then       # 11-25: nothing finished -> the run's own error, and a non-zero exit for the 5090 queue
    say "no episode finished; the last lines of $C/dev7_$L.log:"; tail -n 25 $C/dev7_$L.log | cut -c1-300
    BAD=1
  fi
done
exit $BAD
