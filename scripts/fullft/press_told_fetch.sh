#!/usr/bin/env bash
# A40 / 5090 container, 11-24 (plan v20 card 5): the press_told text table from the relay (diag/press_told, written by
# press_told_text.py on the 5090) into outputs/fullft/press_told/, sha256 against TOLD_TEXT.json; waits (up to 72 h)
# until it is there. An existing file with the right sha256 is kept. Exit 0 = in place.
set -u
R=/workspace/FastWAM-memory2
D=$R/outputs/fullft/press_told
IN=$R/outputs/fullft/relay_in/press_told
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
mkdir -p $D $IN
ok() { local want got; want=$(grep -o '"pt_sha256": "[0-9a-f]*"' $1/TOLD_TEXT.json 2>/dev/null | cut -d'"' -f4)
       got=$(sha256sum $1/TOLD_TEXT.pt 2>/dev/null | cut -d' ' -f1); [ -n "$want" ] && [ "$want" = "$got" ]; }
for i in $(seq 1 432); do
  ok $D && { echo "[told-fetch] $(date '+%F %T') text table in place (sha256 ok)"; exit 0; }
  (cd $R && HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/press_told --out $IN 2>&1 | grep "\[relay\]" | tail -n 2)
  if ok $IN; then cp $IN/TOLD_TEXT.pt $IN/TOLD_TEXT.json $D/ && continue; fi
  echo "[told-fetch] $(date '+%F %T') not on the relay yet; next look in 10 min"; sleep 600
done
exit 1
