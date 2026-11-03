#!/usr/bin/env bash
# Inside the A100 container, read-only: what a press_button pilot (week plan v6 2.5) would reuse.
# Dense-joint delivery code, the two-task dense output / identity / records, the raw demo layout, the RMBench
# dataset revision and its press_button files, the simulator task files, disk. Writes its own report:
#   outputs/memory_v2/report/PRESS_INVENTORY_<time>.txt (the path is printed at the end)
set -u
FW=/workspace/FastWAM
M=/workspace/FastWAM-memory2
D=/restore-tmp/dense_joint_v1
DO=$FW/outputs/s1_dense_joint_h100_v1
PY=/opt/mwam/bin/python
OUT=$M/outputs/memory_v2/report/PRESS_INVENTORY_$(date +%Y%m%d_%H%M).txt
mkdir -p "$(dirname "$OUT")"
{
echo "== $(date '+%F %T') press_button inventory"
echo; echo "== 1. dense-joint delivery code ($D)"
ls -la "$D"
for f in "$D"/*.py "$D"/*.sh; do
  [ -f "$f" ] || continue
  echo; echo "--- $f ($(wc -l < "$f") lines)"
  head -20 "$f"
  echo "  .. entry points / task names:"
  grep -n "argparse\|add_argument\|def main\|^def \|TASKS\|put_back_block\|swap_blocks\|demo_clean\|hdf5" "$f" | head -40
done
echo; echo "== 2. two-task dense output ($DO)"
ls -la "$DO" | head -50
$PY - "$DO" <<'PY'
import json, sys
from collections import Counter
from pathlib import Path
d = Path(sys.argv[1])
for name in ("IDENTITY.json", "RECORDS.json"):
    p = d / name
    if not p.exists():
        print(f"{name}: missing"); continue
    v = json.loads(p.read_text())
    if name == "IDENTITY.json":
        print("IDENTITY keys:", sorted(v))
        print("IDENTITY config:", json.dumps(v.get("config"), indent=1)[:3000])
    else:
        rows = v.get("records", v) if isinstance(v, dict) else v
        print("RECORDS:", type(v).__name__, "keys" if isinstance(v, dict) else "", sorted(v)[:10] if isinstance(v, dict) else "")
        if isinstance(rows, list):
            print("records:", len(rows), Counter(r.get("task") for r in rows if isinstance(r, dict)))
            print("first record:", json.dumps(rows[0], indent=1)[:1500])
PY
echo; echo "== 3. raw demos and prepared caches"
ls -la $FW/resources/RMBench/data 2>&1 | head -20
for t in put_back_block swap_blocks press_button; do
  p=$FW/resources/RMBench/data/demo_clean/$t/aloha_agilex/data
  echo "$t: $(ls $p 2>/dev/null | wc -l) hdf5 in $p"
done
ls -la $FW/resources 2>&1 | head -30
echo; echo "== 4. RMBench dataset revision (download lock) and press_button files on the hub"
$PY - "$FW/resources/download_lock.json" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
lock = json.loads(p.read_text()) if p.exists() else {}
print("lock repositories:", json.dumps(lock.get("repositories"), indent=1))
rev = (lock.get("repositories") or {}).get("TianxingChen/RMBench:dataset") or next(
    (v for k, v in (lock.get("repositories") or {}).items() if "RMBench" in k), None)
try:
    from huggingface_hub import HfApi
    files = HfApi().list_repo_files("TianxingChen/RMBench", repo_type="dataset", revision=rev)
    press = [f for f in files if "press_button" in f]
    print(f"hub revision {rev}: {len(files)} files, press_button: {len(press)}")
    print("\n".join(press[:40]))
except Exception as error:
    print("hub listing failed:", repr(error)[:300])
PY
ls -la $FW/resources/RMBench/data/_download.py 2>&1; head -40 $FW/resources/RMBench/data/_download.py 2>/dev/null
echo; echo "== 5. simulator task files for press_button"
ls $FW/resources/RMBench/envs 2>/dev/null | grep -i -E "press|button" ; ls $FW/resources/RMBench/task_config 2>/dev/null | grep -i -E "press|button"
f=$FW/resources/RMBench/envs/press_button.py; [ -f $f ] && { echo "--- $f"; sed -n 1,140p $f; }
echo; echo "== 6. memory_v2 bindings to the dense output"
grep -n -A4 "^dense:" $M/configs/memory_v2/*.yaml
grep -n "TASKS\|put_back_block\|swap_blocks" $M/src/fastwam/memory_v2/dense.py $M/src/fastwam/memory_v2/pairs.py $M/scripts/memory_v2/find_pairs.py | head -20
echo; echo "== 7. disk"
df -h $FW/outputs $M/outputs /restore-tmp 2>/dev/null
} > "$OUT" 2>&1
echo "PRESS_INVENTORY: $OUT ($(wc -l < "$OUT") lines)"
