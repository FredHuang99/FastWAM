"""HF storage report (11-25, Opus; user 14:08: "watch the 1 TB HF space so it never fills up"). Read-only: lists every
repo of the logged-in account (models, datasets, spaces; private ones included) with huggingface_hub, sums the file sizes
(LFS sizes for LFS files), and breaks the big repos down by top-level folder. The token is huggingface_hub's own login;
it is never printed or written. Writes outputs/fullft/HF_USAGE.json and HF_USAGE.txt (WARN at >= 80 %, BAD at >= 90 % of
the quota). Deletes nothing: freeing space is the user's decision (a permanent deletion needs the user's explicit yes).
  python scripts/fullft/hf_usage.py [--quota-gb 1000]
"""
from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "outputs/fullft"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quota-gb", type=float, default=1000.0)
    args = ap.parse_args()
    from huggingface_hub import HfApi
    api = HfApi()
    me = api.whoami()["name"]
    repos = []
    for kind, lister in (("model", api.list_models), ("dataset", api.list_datasets), ("space", api.list_spaces)):
        try:
            repos += [(kind, r.id) for r in lister(author=me)]
        except Exception as e:                                                       # noqa: BLE001
            repos.append((kind, f"<list failed: {type(e).__name__}>"))
    rows, total = [], 0
    for kind, rid in repos:
        if rid.startswith("<"):
            rows.append({"repo": rid, "type": kind, "bytes": None})
            continue
        folders, subs, size, files = defaultdict(int), defaultdict(int), 0, 0
        try:
            for x in api.list_repo_tree(rid, repo_type=kind, recursive=True):
                s = getattr(x, "size", None)
                lfs = getattr(x, "lfs", None)
                if lfs is not None:
                    s = getattr(lfs, "size", None) or (lfs.get("size") if isinstance(lfs, dict) else s)
                if s is None or not hasattr(x, "blob_id"):
                    continue
                files += 1
                size += int(s)
                parts = x.path.split("/")
                folders[parts[0] if len(parts) > 1 else "."] += int(s)
                if len(parts) > 2:
                    subs["/".join(parts[:2])] += int(s)
        except Exception as e:                                                       # noqa: BLE001
            rows.append({"repo": rid, "type": kind, "bytes": None, "error": f"{type(e).__name__}: {e}"[:200]})
            continue
        total += size
        top = sorted(folders.items(), key=lambda kv: -kv[1])[:40]
        top2 = sorted(subs.items(), key=lambda kv: -kv[1])[:60]
        rows.append({"repo": rid, "type": kind, "bytes": size, "files": files,
                     "top_folders": [{"name": k, "gb": round(v / 1e9, 2)} for k, v in top],
                     "top_subfolders": [{"name": k, "gb": round(v / 1e9, 2)} for k, v in top2]})
    quota = args.quota_gb * 1e9
    frac = total / quota
    status = "BAD" if frac >= 0.90 else "WARN" if frac >= 0.80 else "ok"
    stamp = time.strftime("%F %T")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "HF_USAGE.json").write_text(json.dumps({"time": stamp, "account": "(logged-in account)", "total_bytes": total,
                                                   "quota_gb": args.quota_gb, "used_fraction": round(frac, 4),
                                                   "status": status, "repos": rows}, indent=1) + "\n")
    lines = [f"{status if status != 'ok' else 'ok  '} HF storage {total / 1e9:.1f} GB of {args.quota_gb:.0f} GB "
             f"({100 * frac:.1f} %), free {max(0.0, quota - total) / 1e9:.1f} GB; {stamp}"]
    for r in sorted(rows, key=lambda r: -(r.get("bytes") or 0)):
        if r.get("bytes") is None:
            lines.append(f"     {r['repo']} ({r['type']}): size unknown {r.get('error', '')}")
            continue
        lines.append(f"     {r['repo']} ({r['type']}): {r['bytes'] / 1e9:.1f} GB, {r['files']} files")
        for t in r["top_folders"][:12]:
            lines.append(f"         {t['gb']:8.2f} GB  {t['name']}/")
        for t in r["top_subfolders"][:15]:
            lines.append(f"           {t['gb']:8.2f} GB  {t['name']}/")
    (OUT / "HF_USAGE.txt").write_text("\n".join(lines) + "\n")
    print(lines[0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
