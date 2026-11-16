"""After delta_lite.sh (11-16, GPU18): the payload verify (h100_restore.sh verify) reports BAD files that the 5090 delta
REPLACED on purpose (group 'changed': RMBench / PyTorch3D sources changed since the October payload). Read the BAD
lines of that verify log and check each such file: it must be in the delta-lite manifest (same stage path) and match
the DELTA entry (size + sha256). Prints one line per BAD file and a last line
  "VERIFY OK: <n> payload files superseded by the delta, all match the delta manifest"  (exit 0)
or "VERIFY FAILED: <k> BAD files not explained by the delta" (exit 1). Read-only.
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/verify_superseded.py --log /mnt/tmp/restore_verify.log \
      --payload /mnt/hf/MANIFEST.json --delta /mnt/hf/MANIFEST_5090_DELTA_LITE.json --root /mnt/hf
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", required=True)
    ap.add_argument("--payload", required=True)
    ap.add_argument("--delta", required=True)
    ap.add_argument("--root", required=True)
    args = ap.parse_args()
    text = Path(args.log).read_text(errors="replace")
    bad = [m.group(2) for m in re.finditer(r"^\s*BAD (.+) (\S+)\s*$", text, re.M)]
    total = re.findall(r"\[verify\] (\d+)/(\d+) OK", text)
    if not total:
        sys.exit("no '[verify] n/m OK' line in the log")
    ok, n = map(int, total[-1])
    if n - ok != len(bad):
        sys.exit(f"VERIFY FAILED: the log lists {len(bad)} BAD lines but {n - ok} files failed (more than 50?)")
    payload = {f["path"]: f for f in json.loads(Path(args.payload).read_text())["files"]}
    delta = {f["stage_path"]: f for f in json.loads(Path(args.delta).read_text())["files"]}
    unexplained = 0
    for path in bad:
        stage = (payload.get(path) or {}).get("stage_path")
        d = delta.get(stage) if stage else None
        if d is None:
            print(f"  NOT IN DELTA {path}")
            unexplained += 1
            continue
        p = Path(args.root) / stage
        good = p.is_file() and p.stat().st_size == d["size"] and sha256(p) == d["sha256"]
        print(f"  {'superseded, matches the delta' if good else 'DOES NOT MATCH the delta'} ({d.get('group')}): {path}")
        unexplained += 0 if good else 1
    if unexplained:
        print(f"VERIFY FAILED: {unexplained} BAD files not explained by the delta")
        sys.exit(1)
    print(f"VERIFY OK: {len(bad)} payload files superseded by the delta, all match the delta manifest")


if __name__ == "__main__":
    main()
