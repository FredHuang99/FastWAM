#!/usr/bin/env bash
# 11-15, evaluation box (GPU18 / mwam-a40): only the groups of the 5090 delta (hhyfred/memwam-5090-delta-v1) that a
# closed-loop evaluation box needs, instead of the whole delta (h100_restore.sh delta). Needed:
#   simkit        simulator patches + the A100's CuRobo / PyTorch3D build sources (sim5090.sh)
#   rmbench_data  RMBench data/ python modules the simulator imports
#   changed       RMBench / PyTorch3D sources changed since the October payload (simulator equal to the A100's)
#   scenes        closed_loop/scenes_* (official scene banks)
#   results       closed_loop/**/result.json, queue_state  (small; reference reads)
# Left out (large, not used by evaluation): runs (old memory_v2 checkpoints), data (press features / pairs / the A100's
# own press cache), demos. Same layout as the full delta, so every file lands on its logical path; verified (size +
# sha256) against a manifest filtered to these groups.
#   RESTORE_LOG=/mnt/tmp/restore_delta_lite.log bash scripts/memory_v2/migrate/delta_lite.sh
set -euo pipefail
if [ -n "${RESTORE_LOG:-}" ]; then
  exec > >(tee -a "$RESTORE_LOG") 2>&1
  trap 'rc=$?; echo "[restore] $(date "+%F %T") step delta_lite finished, exit code $rc"' EXIT
fi
D=${DELTA_REPO:-hhyfred/memwam-5090-delta-v1}
HF=/mnt/hf
HFPY=/opt/hf-tools/bin/python
KEEP=${KEEP_GROUPS:-"simkit rmbench_data changed scenes results queue_state"}
echo "[restore] $(date '+%F %T') delta_lite: groups $KEEP from $D"
$HFPY - "$D" "$HF" <<'PY'
import sys
from huggingface_hub import hf_hub_download
print(hf_hub_download(repo_id=sys.argv[1], filename="MANIFEST_5090_DELTA.json", repo_type="model", local_dir=sys.argv[2]))
PY
$HFPY - "$HF/MANIFEST_5090_DELTA.json" "$HF/MANIFEST_5090_DELTA_LITE.json" /mnt/tmp/delta_lite_paths.txt $KEEP <<'PY'
import collections, json, sys
src, dst, paths, keep = sys.argv[1], sys.argv[2], sys.argv[3], set(sys.argv[4:])
m = json.load(open(src))
by = collections.Counter(); size = collections.Counter()
for f in m["files"]:
    by[f["group"]] += 1; size[f["group"]] += f["size"]
for g in sorted(by):
    print(f"  {'KEEP' if g in keep else 'skip'} {g:<14} {by[g]:>6} files {size[g] / 2**30:8.2f} GiB")
sel = [f for f in m["files"] if f["group"] in keep]
missing = keep - set(by)
if missing:
    sys.exit(f"groups not in the manifest: {sorted(missing)}")
m2 = dict(m, files=sel, total_bytes=sum(f["size"] for f in sel))
json.dump(m2, open(dst, "w"), indent=1)
open(paths, "w").write("\n".join(f["stage_path"] for f in sel) + "\n")
print(f"  -> {len(sel)} files, {m2['total_bytes'] / 2**30:.2f} GiB")
PY
$HFPY - "$D" "$HF" /mnt/tmp/delta_lite_paths.txt <<'PY'
import sys
from huggingface_hub import snapshot_download
pats = [p for p in open(sys.argv[3]).read().split("\n") if p]
print(snapshot_download(repo_id=sys.argv[1], repo_type="model", local_dir=sys.argv[2], allow_patterns=pats, max_workers=16))
PY
echo "[restore] $(date '+%F %T') verify the selected files (size + sha256)"
$HFPY /workspace/FastWAM-memory2/scripts/memory_v2/migrate/manifest.py verify --manifest "$HF/MANIFEST_5090_DELTA_LITE.json" --root "$HF"
