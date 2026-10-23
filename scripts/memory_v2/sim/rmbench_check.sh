#!/usr/bin/env bash
# Why does `from data.decode_image_bit import images_encoding` (RMBench envs/utils/pkl2hdf5.py) fail on the A100?
# Read-only diagnosis, plus one safe repair: if RMBench/data/decode_image_bit.py is missing and an identical copy
# exists elsewhere on this machine (other RMBench copy / git checkout), copy it in (never overwrites). Ends with
# an import test of the exact chain sim_eval.load_official uses.  Prints READY or NOT READY as the last line.
#   bash /workspace/FastWAM-memory2/scripts/memory_v2/sim/rmbench_check.sh
set -u
R=/workspace/FastWAM/resources/RMBench
SPY=/opt/rmbench-fused-env/bin/python
F=$R/data/decode_image_bit.py
echo "== RMBench data package  $(date -u '+%F %T') UTC"
echo "-- top level of $R/data (python files and folders)"
ls -la $R/data | grep -v -E '\.hdf5$|\.pkl$' | head -30
echo "-- which 'data' package the simulator python resolves (same sys.path as sim_eval.load_official)"
(cd $R && env -u PYTHONPATH $SPY - <<'PY'
import sys, importlib.util
from pathlib import Path
root = Path.cwd()
sys.path[:0] = [str(root), str(root / "policy"), str(root / "description/utils"), "/workspace/FastWAM/scripts/memory_s1"]
spec = importlib.util.find_spec("data")
print("  data spec:", spec.origin if spec else None, list(spec.submodule_search_locations or []) if spec else None)
for entry in sys.path:
    p = Path(entry or ".") / "data"
    if p.is_dir() or p.with_suffix(".py").exists():
        print(f"  candidate on sys.path: {p}{'.py' if p.with_suffix('.py').exists() else ''}  __init__={ (p / '__init__.py').exists() }")
PY
)
echo "-- is $R a git checkout?"
git -c safe.directory='*' -C $R remote -v 2>&1 | head -2
git -c safe.directory='*' -C $R log --oneline -1 2>&1 | head -1
echo "-- expected sha256 of the decoder recorded by the data preparation"
EXPECTED=$(grep -rhoE '"decoder_sha256": *"[0-9a-f]{64}"' /workspace/FastWAM/resources/prepared_dense_h100_v1 /workspace/FastWAM/outputs/s1_dense_joint_h100_v1/IDENTITY.json 2>/dev/null | grep -oE '[0-9a-f]{64}' | sort -u | head -1)
echo "  expected: ${EXPECTED:-unknown}"
echo "-- copies of decode_image_bit.py on this machine (bounded search)"
timeout 240 find /workspace /restore-tmp /migration /root /opt /home -maxdepth 7 -name decode_image_bit.py -not -path '*/proc/*' 2>/dev/null \
  | while read -r p; do echo "  $(sha256sum "$p" | cut -c1-64)  $p"; done
if [ -f "$F" ]; then
  echo "-- $F exists: $(sha256sum $F | cut -c1-64)"
else
  echo "-- $F is MISSING"
  SRC=""
  if git -c safe.directory='*' -C $R cat-file -e HEAD:data/decode_image_bit.py 2>/dev/null; then
    git -c safe.directory='*' -C $R show HEAD:data/decode_image_bit.py > $F.from_git && SRC=git
    mv -n $F.from_git $F
  else
    for p in $(timeout 240 find /workspace /restore-tmp /migration /root /opt /home -maxdepth 7 -name decode_image_bit.py 2>/dev/null); do
      [ "$p" = "$F" ] && continue
      s=$(sha256sum "$p" | cut -c1-64)
      if [ -z "$EXPECTED" ] || [ "$s" = "$EXPECTED" ]; then cp -n "$p" "$F" && SRC=$p && break; fi
    done
  fi
  if [ -f "$F" ]; then echo "  RESTORED from ${SRC}: $(sha256sum $F | cut -c1-64)"; else echo "  no usable copy found"; fi
fi
echo "-- import test: envs (the chain that failed)"
(cd $R && timeout 300 env -u PYTHONPATH $SPY - <<'PY' 2>&1 | grep -v -E "UserWarning|warn\(" | tail -n 8
import sys
from pathlib import Path
root = Path.cwd()
sys.path[:0] = [str(root), str(root / "policy"), str(root / "description/utils"), "/workspace/FastWAM/scripts/memory_s1"]
from envs import CONFIGS_PATH
import data.decode_image_bit as d
print("IMPORT OK", CONFIGS_PATH, d.__file__)
PY
) | tee /tmp/rmbench_import_test.txt
if grep -q "IMPORT OK" /tmp/rmbench_import_test.txt; then echo "READY"; else echo "NOT READY"; fi
