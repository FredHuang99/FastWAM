#!/usr/bin/env bash
# A40 (11-16 21:10 BJ): the migration payload carried some A100 closed-loop episodes (result.json) into the A40's
# closed_loop/g1; the closed-loop runner skips any seed that already has a result.json, so those seeds would enter
# A40-EQ as A100 numbers. This moves every episode folder of the given labels whose result.json is older than CUTOFF
# (container clock = UTC; 12:00 = 20:00 BJ, before the A40 dispatcher started at 20:31 BJ) to
# closed_loop/<FOLDER>_pre_a40/<label>/... (moved, never deleted); the fill cards A40-lp30-fill / A40-lp30p-fill then
# run those seeds on the A40, and A40-EQ-verdict waits for them.
#   bash /workspace/FastWAM-memory2/scripts/memory_v2/jobs/a40_quarantine.sh ar2_prop_e30
set -u
CL=/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop
CUTOFF=${CUTOFF:-"2026-11-16 12:00"}
FOLDER=${FOLDER:-g1}
for label in "$@"; do
  n=0; skipped=0
  while IFS= read -r f; do
    d=$(dirname "$f"); rel=${d#$CL/$FOLDER/}
    dest=$CL/${FOLDER}_pre_a40/$rel
    if [ -e "$dest" ]; then skipped=$((skipped + 1)); continue; fi
    mkdir -p "$(dirname "$dest")" && mv "$d" "$dest" && n=$((n + 1)) && echo "  moved $rel"
  done < <(find $CL/$FOLDER/$label -path "*/seed_*/result.json" ! -newermt "$CUTOFF" 2>/dev/null | sort)
  echo "[quarantine] $label: moved $n episode folders (older than $CUTOFF) to $CL/${FOLDER}_pre_a40/$label; $skipped already there"
  for t in swap_blocks put_back_block; do
    echo "  $t: $(find $CL/$FOLDER/$label/on/$t -name result.json 2>/dev/null | wc -l) results left (all written on the A40)"
  done
done
