#!/usr/bin/env bash
# 11-25 (Opus): exit 0 if the relay (hhyfred/memwam-fullft) holds exports/<name> with its sha256 file, for q5090.txt
# conditions. One listing of exports/ per 20 minutes (cached in outputs/fullft/RELAY_EXPORTS.txt), not one call per check.
#   bash scripts/fullft/relay_has.sh press_told_e10
set -u
R=${R:-/workspace/FastWAM-memory2}
C=$R/outputs/fullft/RELAY_EXPORTS.txt
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
if [ ! -s $C ] || [ $(( $(date +%s) - $(stat -c %Y $C) )) -ge 1200 ]; then
  timeout 300 $HFPY -c "
from huggingface_hub import HfApi
for x in HfApi().list_repo_tree('hhyfred/memwam-fullft', path_in_repo='exports', repo_type='model', recursive=True):
    if hasattr(x, 'size'):
        print(x.path)" > $C.tmp 2> /dev/null && [ -s $C.tmp ] && mv $C.tmp $C
  touch $C
fi
grep -q "exports/$1/export_.*\.pt\.sha256" $C
