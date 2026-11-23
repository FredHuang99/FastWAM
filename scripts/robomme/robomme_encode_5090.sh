#!/usr/bin/env bash
# 5090 HOST, 11-23 19:40 (Opus; plan R0 section 3, the step after the conversion; the user's scheduled task: encode once
# the conversion and the LIBERO base are in place, both done 17:34). One GPU (PF_GPUS, default 1), several hours.
#   1 the conversion ($D/convert, robomme_convert_5090.sh) made visible inside mwam5090: when a mount of mwam5090
#     already shows it, that path is used; otherwise it is copied once with docker cp into
#     /workspace/FastWAM-memory2/outputs/robomme/convert (28 GB; an existing copy with RECORDS.json is kept)
#   2 waits until the GPU holds < 2000 MiB, then robomme_encode.py inside mwam5090: pipeline check on the RMBench cache
#     dense_observe_and_pickup_v1 (re-encodes its episode 0 from the delivery's images; stops if it does not match), the
#     image-pipeline self-test, then PickXtimes + BinFill -> /workspace/FastWAM-memory2/outputs/robomme/dense_robomme_v1
#     (resumable; finished episodes are kept). Nothing is deleted.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && nohup bash -c "$(docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/robomme_encode_5090.sh)" > ~/robomme_encode.log 2>&1 &
# Log: ~/robomme_encode.log ; result lines start with [check] / [encode]; the last line says DONE or FAILED.
set -u
if [ -d /mnt/hf ]; then D=${D:-/mnt/hf/robomme}; else D=${D:-$HOME/robomme}; fi
C=mwam5090
R=/workspace/FastWAM-memory2
G=${PF_GPUS:-1}
OUT=$R/outputs/robomme/dense_robomme_v1
say() { echo "[robomme-encode] $(date '+%F %T') $*"; }
fail() { say "FAILED: $*"; exit 1; }
[ -s $D/convert/RECORDS.json ] || fail "no $D/convert/RECORDS.json (robomme_convert_5090.sh first)"
say "start; code $(docker exec $C git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-60); GPU $G"

say "===== 1 the conversion inside $C"
IN=""; best=0
while read -r src dst; do
  [ -n "$src" ] || continue
  case "$D/convert/" in "${src%/}/"*)
    if [ ${#src} -gt $best ]; then best=${#src}; rest=${D#"${src%/}"}; IN="${dst%/}$rest/convert"; fi;; esac
done < <(docker inspect $C --format '{{range .Mounts}}{{.Source}} {{.Destination}}{{"\n"}}{{end}}')
if [ -n "$IN" ] && docker exec $C test -s $IN/RECORDS.json; then
  say "mounted: $D/convert is $IN inside $C"
else
  IN=$R/outputs/robomme/convert
  if docker exec $C test -s $IN/RECORDS.json; then
    say "copy already inside $C: $IN"
  else
    docker exec $C mkdir -p $R/outputs/robomme || fail "mkdir"
    docker exec $C test -e $IN && fail "$IN exists without RECORDS.json (an unfinished copy?): left for the user"
    say "copying $(du -sh $D/convert | cut -f1) into $C:$IN (docker cp)"
    docker cp $D/convert $C:$IN || fail "docker cp"
    docker exec $C test -s $IN/RECORDS.json || fail "copy has no RECORDS.json"
    say "copied: $(docker exec $C du -sh $IN | cut -f1)"
  fi
fi

say "===== 2 encoding (GPU $G)"
until u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G | tr -d ' ') && [ "$u" -lt 2000 ]; do
  say "GPU $G in use ($u MiB); waiting 5 min"; sleep 300; done
docker exec $C bash -c "cd $R && PYTHONPATH=src CUDA_VISIBLE_DEVICES=$G PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
  /opt/mwam/bin/python scripts/robomme/robomme_encode.py --convert $IN --out $OUT" 2>&1 | grep -v "Warning\|warn("
rc=${PIPESTATUS[0]}
[ "$rc" = 0 ] || fail "robomme_encode.py exit code $rc (see the [check] / [encode] lines above)"
say "DONE ($C:$OUT; $(docker exec $C du -sh $OUT | cut -f1))"
