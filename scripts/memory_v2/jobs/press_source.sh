#!/usr/bin/env bash
# Inside the A100 container, read-only (week plan v6 2.5, press_button cache builder): the full source of the dense
# delivery's data path (how raw demos become cache/<episode>/encodings.pt) and the exact schema of one prepared episode
# and one cache entry, so a memory_v2-side builder can write the same format for press_button into a NEW folder.
# Nothing is written outside the report: outputs/memory_v2/report/PRESS_SOURCE_<time>.txt (path printed at the end).
set -u
FW=/workspace/FastWAM
M=/workspace/FastWAM-memory2
D=/restore-tmp/dense_joint_v1
DO=$FW/outputs/s1_dense_joint_h100_v1
PY=/opt/mwam/bin/python
OUT=$M/outputs/memory_v2/report/PRESS_SOURCE_$(date +%Y%m%d_%H%M).txt
mkdir -p "$(dirname "$OUT")"
{
echo "== $(date '+%F %T') press_button: dense data-path source + cache schema (read-only)"
for f in data_path.py common.py audit.py manage.py training.py recipe.json run_step.sh download.sh; do
  echo; echo "=================== FILE $D/$f ($(wc -l < "$D/$f" 2>/dev/null) lines)"
  cat -n "$D/$f" 2>&1
done
echo; echo "=================== FILE $FW/resources/RMBench/data/_download.py"
cat -n $FW/resources/RMBench/data/_download.py 2>&1
echo; echo "== dense output receipts ($DO)"
for f in PREPARED.json PLAN.json PACKAGE.json REPORT.json episodes.csv; do echo "--- $f"; head -c 5000 "$DO/$f" 2>&1; echo; done
$PY - "$DO" <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1])
v = json.loads((d / "IDENTITY.json").read_text())
for k in ("schema", "recipe", "frozen", "code", "encoder_software", "source_checkpoint", "git"):
    print(f"--- IDENTITY.{k}:", json.dumps(v.get(k), indent=1)[:3000])
sf = v.get("source_files")
print("--- IDENTITY.source_files:", type(sf).__name__, len(sf) if hasattr(sf, "__len__") else "",
      json.dumps(sf if not isinstance(sf, dict) else dict(list(sf.items())[:15]), indent=1)[:2500])
rec = json.loads((d / "RECORDS.json").read_text())
from collections import Counter
print("--- RECORDS:", len(rec), Counter((r["task"], r.get("split")) for r in rec))
print("--- RECORDS keys:", sorted(rec[0]))
print("--- lengths:", {t: sorted(r["length"] for r in rec if r["task"] == t)[::10] for t in sorted({r["task"] for r in rec})})
PY
echo; echo "== prepared episodes ($FW/resources/prepared_dense_h100_v1)"
ls -la $FW/resources/prepared_dense_h100_v1 | head; ls $FW/resources/prepared_dense_h100_v1/* | head -5
du -sh $FW/resources/prepared_dense_h100_v1 $DO/cache $M/outputs/memory_v2/features_dense_v1 2>&1
echo; echo "== one prepared episode and one cache entry: keys, shapes, dtypes, value ranges"
$PY - "$FW" "$DO" <<'PY'
import json, sys
from pathlib import Path
import torch
fw, do = Path(sys.argv[1]), Path(sys.argv[2])
rec = json.loads((do / "RECORDS.json").read_text())[0]
def show(x, pre=""):
    if isinstance(x, torch.Tensor):
        s = f"{pre}: tensor {tuple(x.shape)} {x.dtype}"
        if x.numel() and x.dtype.is_floating_point:
            s += f" min {x.min().item():.4g} max {x.max().item():.4g} mean {x.float().mean().item():.4g}"
        elif x.numel():
            s += f" first {x.flatten()[:6].tolist()}"
        print(s)
    elif isinstance(x, dict):
        for k, v in x.items():
            show(v, f"{pre}.{k}" if pre else str(k))
    elif isinstance(x, (list, tuple)):
        print(f"{pre}: {type(x).__name__} len {len(x)}" + (f" first {str(x[:3])[:200]}" if x and not isinstance(x[0], (torch.Tensor, dict)) else ""))
        if x and isinstance(x[0], (torch.Tensor, dict)):
            show(x[0], pre + "[0]")
    else:
        print(f"{pre}: {type(x).__name__} {str(x)[:200]}")
for base in (fw / "resources/prepared_dense_h100_v1", fw / "resources/prepared_dense_h100_v1/episodes"):
    p = base / Path(rec["file"]).name
    if not p.exists():
        p = base / rec["file"]
    if p.exists():
        print(f"--- prepared {p} ({p.stat().st_size / 1e6:.1f} MB)")
        show(torch.load(p, map_location="cpu", weights_only=False))
        break
else:
    print("--- prepared episode file not found for", rec["file"])
c = do / "cache" / rec["episode_id"].replace("/", "_")
print(f"--- cache {c}:", sorted(x.name for x in c.iterdir()))
for f in sorted(c.glob("*.json")):
    print(f"--- {f.name}:", f.read_text()[:2500])
for f in sorted(c.glob("*.pt")):
    print(f"--- {f.name} ({f.stat().st_size / 1e6:.1f} MB)")
    show(torch.load(f, map_location="cpu", weights_only=True))
PY
echo; echo "== simulator-side logging used by the memory_v2 closed loop (frozen memory_s1 helpers, read-only)"
grep -n "def object_snapshot" -A45 $FW/scripts/memory_s1/sim_feedback.py 2>&1 | head -60
grep -n "def object_contacts" -A25 $FW/scripts/memory_s1/sim_instrumentation.py 2>&1 | head -30
grep -n "def check_success\|press_cnt\|def play_once" -A3 $FW/resources/RMBench/envs/press_button.py 2>&1 | head -60
echo; echo "== disk"; df -h $FW/outputs $M/outputs 2>/dev/null
} > "$OUT" 2>&1
echo "PRESS_SOURCE: $OUT ($(wc -l < "$OUT") lines)"
