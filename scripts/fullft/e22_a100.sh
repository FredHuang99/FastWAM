#!/usr/bin/env bash
# 11-20 17:40 BJ (Opus; plan v15 section 5.1 "A100 takes the A40's test-time groups it cannot fit, whole groups, visible
# and hidden never split"; user 11-20 17:04: the A40 is full with another user's jobs since ~10:00, move to the A100).
# E22a (pause 256 / 1024) runs whole on the A100; its cells reach the A40, where the registered e22_verdict.py --part a
# reads them next to the 64-frame cells of E5 / E1 (A40). Each cell's visible / hidden pair is on one machine.
#   e22_a100.sh time1024        A100: the 1024-frame smoke episode's wall time; exit 0 if <= 25 min (plan v15 E22a:
#                               over ~20 min per episode -> use 768 instead; 5 min of model loading allowed for)
#   e22_a100.sh pack <tag>      A100: closed_loop/e22 (result.json, stress.jsonl, decisions.jsonl, executed_actions.jsonl
#                               of every episode; nothing else) -> E22_A100_<tag>.tar.gz + its sha256 + the first 50
#                               seeds of the swap / put banks -> relay diag/e22_a100
#   e22_a100.sh fetch <tag>     A40: wait for that pack on the relay (heartbeat every 5 min), check the sha256 and that
#                               the A100's first 50 seeds equal the A40's (else stop: no verdict from mixed banks), then
#                               unpack into closed_loop/ (existing files are kept, never overwritten)
set -u
R=/workspace/FastWAM-memory2
CL=$R/outputs/memory_v2/closed_loop
OUT=$R/outputs/fullft
PY=/opt/mwam/bin/python
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=$PY
RELAY="$HFPY $R/scripts/memory_v2/migrate/relay.py"
PFX=diag/e22_a100
say() { echo "[e22a100] $(TZ=Asia/Shanghai date '+%F %T') $*"; }
cd $R
seeds() {        # first 50 seeds of the swap / put banks as e22_verdict.py sees them
  PYTHONPATH=src $PY - <<'PY'
import importlib.util, json, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("e1v", "scripts/fullft/e1_verdict.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(json.dumps({t: m.seeds_of(t, 50) for t in ("swap_blocks", "put_back_block")}))
PY
}

case "${1:-}" in
  time1024)
    f=$(ls $CL/e22smoke/ar2_clock_e30_p1024_vis/on/swap_blocks/seed_*/result.json 2>/dev/null | head -1)
    [ -n "$f" ] || { say "no smoke episode"; exit 1; }
    w=$($PY -c "import json,sys; print(int(json.load(open(sys.argv[1])).get('wall_seconds', 1e9)))" "$f")
    say "1024-frame pause smoke episode: wall $w s (limit 1500 s), success $($PY -c "import json,sys; print(json.load(open(sys.argv[1])).get('success'))" "$f")"
    [ "$w" -le 1500 ] ;;
  pack)
    tag=${2:?tag}
    T=$OUT/E22_A100_$tag.tar.gz
    (cd $CL && find e22 -path '*/seed_*/*' \( -name result.json -o -name stress.jsonl -o -name decisions.jsonl \
        -o -name executed_actions.jsonl \) -print | sort > $OUT/E22_A100_$tag.list)
    say "$(wc -l < $OUT/E22_A100_$tag.list) files; episodes per label:"
    (cd $CL && find e22 -name result.json | awk -F/ '{print $2}' | sort | uniq -c)
    (cd $CL && tar czf $T -T $OUT/E22_A100_$tag.list) || { say "tar failed"; exit 1; }
    (cd $OUT && sha256sum $(basename $T) > $(basename $T).sha256)
    seeds > $OUT/E22_A100_${tag}_seeds.json
    $RELAY put $T.sha256 $OUT/E22_A100_${tag}_seeds.json $T --prefix $PFX 2>&1 | grep "\[relay\]" || exit 1
    say "pack $tag on the relay ($(du -h $T | cut -f1))" ;;
  fetch)
    tag=${2:?tag}
    IN=$OUT/relay_in/e22_a100; mkdir -p $IN
    n=E22_A100_$tag.tar.gz
    until $RELAY ls --prefix $PFX 2>/dev/null | grep -q "^$n "; do
      say "waiting for $PFX/$n (the A100 uploads it after its E22a cards)"; sleep 300
    done
    sleep 60                               # the archive is put last; give the upload a minute
    $RELAY get --prefix $PFX --out $IN 2>&1 | grep -v "Processing\|Download\|%|" | tail -n 3
    (cd $IN && sha256sum -c $n.sha256) || { say "sha256 mismatch"; exit 1; }
    mine=$(seeds); theirs=$(cat $IN/E22_A100_${tag}_seeds.json)
    if [ "$mine" != "$theirs" ]; then say "the A100's first 50 seeds differ from the A40's: NOT unpacked"; exit 1; fi
    say "same first 50 seeds (swap / put) on both machines"
    (cd $CL && tar xzf $IN/$n --skip-old-files) || { say "unpack failed"; exit 1; }
    echo "$(TZ=Asia/Shanghai date '+%F %T') unpacked $n from the A100 (plan v15 5.1 move, user 11-20 17:04)" >> $CL/e22/FROM_A100.txt
    say "unpacked; episodes per label now:"
    (cd $CL && find e22 -name result.json | awk -F/ '{print $2}' | sort | uniq -c) ;;
  *) sed -n 2,14p "$0"; exit 2 ;;
esac
