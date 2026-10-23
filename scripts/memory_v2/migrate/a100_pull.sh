#!/usr/bin/env bash
# A100 container (root@6e4b37a15066): bring the H100 results back from HF into the same logical paths.
# Files the A100 already has are never overwritten (its own runs are the originals); only missing files
# are added: the H100 runs (v2_A_bfull_cf, v2_A_cf_s18, v2_A_bfull_s18, the interrupted v2_A_anchor_cf),
# their eval/PR results, RESULTS_*.txt and the H100 records. The 33 GB feature cache is not downloaded.
set -euo pipefail
trap 'echo "[pull] FAILED (exit $?) at line $LINENO: $BASH_COMMAND" >&2' ERR
REPO=${HF_REPO:-hhyfred/memwam-h100-migration-v1}
PULL=/workspace/FastWAM-memory2/outputs/_h100_pull
HFPY=/opt/hf-tools/bin/python
OUT=/workspace/FastWAM-memory2/outputs
step() { echo "[pull] $(date '+%F %T') $*"; }
mkdir -p "$PULL"
step "download results from $REPO -> $PULL"
$HFPY - "$REPO" "$PULL" <<'PY'
import sys
from huggingface_hub import snapshot_download
print(snapshot_download(repo_id=sys.argv[1], repo_type="model", local_dir=sys.argv[2], max_workers=16,
      allow_patterns=["MANIFEST.json",
                      "payload/workspace/FastWAM-memory2/outputs/memory_v2/**",
                      "payload/workspace/FastWAM-memory2/outputs/migration_h100_v1/records/**",
                      "payload/workspace/FastWAM-memory2/outputs/migration_h100_v1/reference_*/**"],
      ignore_patterns=["payload/workspace/FastWAM-memory2/outputs/memory_v2/features_dense_v1/**"]))
PY
step "copy into $OUT (no overwrite)"
before=$(find "$OUT" -type f | wc -l)
cp -rn "$PULL/payload/workspace/FastWAM-memory2/outputs/." "$OUT/"
after=$(find "$OUT" -type f | wc -l)
step "added $((after - before)) files"
step "verify the H100 runs against the HF manifest"
$HFPY - "$PULL/MANIFEST.json" <<'PY'
import hashlib, json, os, sys
m = json.load(open(sys.argv[1]))
want = [f for f in m["files"] if f["path"].startswith("/workspace/FastWAM-memory2/outputs/memory_v2/")
        and "/features_dense_v1/" not in f["path"]]
bad = 0
for f in want:
    p = f["path"]
    if not os.path.isfile(p) or os.path.getsize(p) != f["size"]:
        bad += 1; print("  MISSING/SIZE", p); continue
    if p.endswith((".pt", ".json")):
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for block in iter(lambda: fh.read(1 << 24), b""):
                h.update(block)
        if h.hexdigest() != f["sha256"]:
            bad += 1; print("  SHA", p)
print(f"[pull] {len(want) - bad}/{len(want)} result files present and identical to the hub (checkpoints/json hashed)")
sys.exit(1 if bad else 0)
PY
for run in v2_A_bfull_cf v2_A_cf_s18 v2_A_bfull_s18 v2_A_anchor_cf; do
  printf '%-16s ' "$run"; tail -n 1 "$OUT/memory_v2/$run/train.log" 2>/dev/null || echo "(no train.log)"
done
step "done; the download copy can be removed later: rm -rf $PULL"
