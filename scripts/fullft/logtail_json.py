"""Copy the tails of some log files into a small JSON in outputs/fullft (the results push carries small JSON only).
Read-only. 11-27 17:45 (Opus): gen800b failed in 1 s ('gen exit code 1') and its generator log is in gen_obs/.
  /opt/mwam/bin/python scripts/fullft/logtail_json.py --out GEN800B_LOGTAIL.json outputs/fullft/gen_obs/gen800b.log ...
"""
import argparse
import json
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--lines", type=int, default=80)
ap.add_argument("files", nargs="+")
a = ap.parse_args()
R = Path("/workspace/FastWAM-memory2")
out = {}
for f in a.files:
    p = R / f
    out[f] = p.read_text(errors="replace").splitlines()[-a.lines:] if p.exists() else "missing"
(R / "outputs/fullft" / a.out).write_text(json.dumps(out, indent=1) + "\n")
print(f"LOGTAIL -> {a.out}: {len(out)} files")
