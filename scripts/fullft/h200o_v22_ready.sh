#!/usr/bin/env bash
# mwam2 (old H200), 11-29 00:33 (Opus, plan v22 patrol 2): queue-line condition for a v22 run moved from the new H200's
# slot lists to the old H200 (the same H200 class). Fetches what the new H200's slot job (gaas_run.pbs prepare_data)
# would fetch for that run, so the old H200 trains the identical line:
#   * every data.events file events_<x>_v3[a-z].json missing here <- relay diag/<x>_v3[a-z] (copied unchanged)
#   * data.text_table (press_told's TOLD_TEXT.pt) missing here <- relay diag/press_told, sha256 checked against
#     TOLD_TEXT.json's pt_sha256 (as gaas_run.pbs)
#   * the dense caches of data.roots under outputs/memory_v2/press: cache_ready.sh <GO file> (verify / cache relay)
#   usage: bash scripts/fullft/h200o_v22_ready.sh <GO file under scripts/fullft/> <run name in h200_queue.txt>
#   exit 0 = everything is here (the queue may start the run); at most one fetch attempt per 30 min per run.
# Log: outputs/fullft/H200O_V22_READY.log
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
cd $R
GO=${1:?GO file}; RUN=${2:?run}
[ -f scripts/fullft/$GO ] || exit 1
LINE=$(grep "^$RUN |" scripts/fullft/h200_queue.txt | head -n 1)
[ -n "$LINE" ] || exit 1
SETS=$(echo "$LINE" | cut -d'|' -f2)
need=0
EVS=$(echo "$SETS" | grep -o 'data.events=\[[^]]*\]' | sed 's/data.events=\[//; s/\]//' | tr ',' ' ')
for ev in $EVS; do [ -s $R/${ev#/workspace/FastWAM-memory2/} ] || need=1; done
TT=$(echo "$SETS" | grep -o 'data.text_table=[^ ]*' | sed 's/data.text_table=//')
[ -z "$TT" ] || [ -s $R/${TT#/workspace/FastWAM-memory2/} ] || need=1
CACHES=$(echo "$SETS" | grep -o 'data.roots=\[[^]]*\]' | sed 's/data.roots=\[//; s/\]//' | tr ',' '\n' | grep '/outputs/memory_v2/press/' | xargs -n1 basename 2>/dev/null | tr '\n' ' ')
for c in $CACHES; do [ -f outputs/memory_v2/press/$c/.verified ] || need=1; done
[ $need = 0 ] && exit 0
T=$F/H200O_V22_READY_TRIED_$RUN
if [ -f $T ] && [ $(( $(date +%s) - $(stat -c %Y $T) )) -lt 1800 ]; then exit 1; fi
touch $T
exec >> $F/H200O_V22_READY.log 2>&1
say() { echo "[h200o-ready] $(TZ=Asia/Shanghai date '+%F %T') $RUN: $*"; }
PY=/opt/mwam/bin/python
ok=1
for ev in $EVS; do
  E=$R/${ev#/workspace/FastWAM-memory2/}; [ -s $E ] && continue
  stem=$(basename $E .json); task=${stem#events_}
  case "$stem" in *_v3[a-z]) ;; *) say "$stem.json missing and not a relay events file: not fetched"; ok=0; continue;; esac
  IN=$F/relay_in/$task; mkdir -p $IN $(dirname $E)
  HF_HUB_DOWNLOAD_TIMEOUT=60 $PY scripts/memory_v2/migrate/relay.py get --prefix diag/$task --out $IN 2>&1 | grep "\[relay\]" | tail -n 2
  if [ -s $IN/$stem.json ]; then cp $IN/$stem.json $E && say "$stem.json fetched (sha256 $(sha256sum $E | cut -c1-16))"; else say "$stem.json not on the relay"; ok=0; fi
done
if [ -n "$TT" ] && [ ! -s $R/${TT#/workspace/FastWAM-memory2/} ]; then
  E=$R/${TT#/workspace/FastWAM-memory2/}; IN=$F/relay_in/press_told; mkdir -p $IN $(dirname $E)
  HF_HUB_DOWNLOAD_TIMEOUT=60 $PY scripts/memory_v2/migrate/relay.py get --prefix diag/press_told --out $IN 2>&1 | grep "\[relay\]" | tail -n 2
  want=$(grep -o '"pt_sha256": "[0-9a-f]*"' $IN/TOLD_TEXT.json 2>/dev/null | cut -d'"' -f4)
  got=$([ -s $IN/$(basename $E) ] && sha256sum $IN/$(basename $E) | cut -d' ' -f1)
  if [ -n "$want" ] && [ "$want" = "$got" ]; then cp $IN/$(basename $E) $E && cp $IN/TOLD_TEXT.json $(dirname $E)/ && say "text table fetched (sha256 ${got:0:16})"
  else say "text table sha256 '$got' != TOLD_TEXT.json's '$want'"; ok=0; fi
fi
if [ -n "$CACHES" ]; then bash scripts/fullft/cache_ready.sh $GO $CACHES || { say "caches $CACHES not ready (cache_ready.sh)"; ok=0; }; fi
[ $ok = 1 ] && say "ready" && exit 0
exit 1
