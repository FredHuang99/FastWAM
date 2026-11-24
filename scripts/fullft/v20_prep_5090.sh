#!/usr/bin/env bash
# mwam5090, 11-24 (Opus; plan v20 section 5 "前置"): what the new H200's slot jobs fetch from the relays tonight.
#   1 the training caches of rearrange and swap_T (cards 1, 3) on the cache relay: present -> nothing; absent -> put from
#     this machine (cache_relay.py put: sha256 manifest, uploaded last); diag/events_b1 must hold events_swap_T.json
#   2 the timely writer's events files (task_v3c_events.py --relay, D2's writer: delta 0.012, min_path 0.015,
#     provisional 0.002) for blocks_ranking_try (card 4) and put_back_block + swap_blocks (card 2) -> relay diag/<task>_v3c
#   3 checks: events per demo (ranking against its 69 record entries), episode keys against each task's rule-A file
#     events_<task>.json here (same demos), and diag/rearrange_blocks_v3c still on the relay (card 1)
# CPU / network only. Own log: outputs/fullft/V20_PREP_5090_<time>.txt
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/v20_prep_5090.sh
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
P=$R/outputs/memory_v2/press
HFPY=/opt/hf-tools/bin/python; [ -x $HFPY ] || HFPY=/opt/mwam/bin/python
LOG=$F/V20_PREP_5090_$(date +%Y%m%d_%H%M).txt
mkdir -p $F/events
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[v20prep] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
say() { echo "[v20prep] $(date '+%F %T') $*"; }
cd $R
export PYTHONPATH=$R/src HF_HUB_DOWNLOAD_TIMEOUT=60
say "checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); disk $(df -h $R | tail -n 1 | awk '{print $4}') free"
ON=$($HFPY scripts/fullft/cache_relay.py ls 2>/dev/null)
say "cache relay holds: $(echo $ON | tr '\n' ' ')"
for t in rearrange_blocks swap_T; do
  N=dense_${t}_v1
  if echo "$ON" | grep -qx "$N"; then say "$N: on the cache relay"; continue; fi
  if [ -f $P/$N/CACHE.json ]; then
    say "$N: NOT on the cache relay -> uploading from here ($(du -sh $P/$N | cut -f1))"
    $HFPY scripts/fullft/cache_relay.py put $P/$N 2>&1 | tail -n 3
    $HFPY scripts/fullft/cache_relay.py ls 2>/dev/null | grep -qx "$N" && say "$N: now on the cache relay" || say "$N: UPLOAD FAILED"
  else
    say "$N: neither on the cache relay nor here ($P/$N): card $([ $t = swap_T ] && echo 3 || echo 1) cannot start"
  fi
done
say "diag/events_b1: $($HFPY scripts/memory_v2/migrate/relay.py ls --prefix diag/events_b1 2>/dev/null | tr '\n' ' ')"
say "diag/rearrange_blocks_v3c: $($HFPY scripts/memory_v2/migrate/relay.py ls --prefix diag/rearrange_blocks_v3c 2>/dev/null | tr '\n' ' ')"
for t in blocks_ranking_try put_back_block swap_blocks; do
  say "===== $t"
  /opt/mwam/bin/python scripts/fullft/task_v3c_events.py --task $t --relay 2>&1 | tail -n 4
  /opt/mwam/bin/python - $t <<'PY'
import json, sys
from pathlib import Path
t = sys.argv[1]
F = Path("/workspace/FastWAM-memory2/outputs/fullft/events")
new = json.loads((F / f"events_{t}_v3c.json").read_text())["episodes"]
n = sorted(len(v) for v in new.values())
print(f"[v20prep] {t}: {len(new)} demos; events per demo min {n[0]} median {n[len(n) // 2]} max {n[-1]}"
      + (f"; record entries 69 -> {sum(x > 69 for x in n)} demos above" if t == "blocks_ranking_try" else
         f"; record entries 32 -> {sum(x > 32 for x in n)} demos above"))
old = F / f"events_{t}.json"
if old.exists():
    o = json.loads(old.read_text())
    o = o.get("episodes", o)
    a, b = set(new), set(o)
    print(f"[v20prep] {t}: keys vs events_{t}.json (rule A): same {len(a & b)}, only new {len(a - b)}, only old {len(b - a)}"
          f"; e.g. new {sorted(a)[:2]} old {sorted(b)[:2]}")
else:
    print(f"[v20prep] {t}: no rule-A events_{t}.json here to compare keys with")
PY
  say "relay diag/${t}_v3c: $($HFPY scripts/memory_v2/migrate/relay.py ls --prefix diag/${t}_v3c 2>/dev/null | tr '\n' ' ')"
done
say "DONE"
