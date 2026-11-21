"""Which of the big files on our HF relay does THIS machine hold? (11-21 15:40, Opus; user 15:15: before freeing HF
storage, know where each big file also lives; NTU machines (old H200, A100, 5090) are the safe places, the new
H200 (GaaS) home may be reclaimed, H100 and A40 are NUS machines.) Read-only on HF and on disk; writes only its own
report outputs/fullft/RELAY_INVENTORY_<machine>.json. The token is read by huggingface_hub, never printed.

HF side: every file >= 1 MB of the relay repos (LFS sha256 and size from the repo tree), grouped:
  fullft:exports/<run>_<tag>     local  outputs/fullft/exports/<run>_<tag>/<file>  or  outputs/fullft/<run>/<file>
  fullft:ckpt/ar_2task_e30        local  outputs/fullft/ar_2task/resume.pt (the joined parts; size = sum of parts)
  caches:<name>                   local  a folder <name> under outputs/ (depth <= 4), same relative paths
  h100mig / 5090delta:payload/workspace/<a>/<b>/<c>   local  /workspace/<rel> (the payload mirrors /workspace)
Per file: 'sha' = sha256 equal to HF's (from a .sha256 sidecar naming the same hash, or computed with --hash),
'size' = same size only, 'mismatch' = present but different size or hash, absent otherwise.
--hash computes sha256 of files >= 1 GB that have no sidecar (exports, the ar_2task resume; 4 threads, nice/ionice
from the caller); caches and payloads are matched by size (thousands of files).
  PYTHONPATH=src /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_inventory.py --machine 5090 [--hash]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

W = Path(os.environ.get("MWAM_WORKSPACE", "/workspace"))       # override only for the self-test
R = W / "FastWAM-memory2"
OUT = R / "outputs"
REPOS = {"fullft": "hhyfred/memwam-fullft", "caches": "hhyfred/memwam-caches",
         "h100mig": "hhyfred/memwam-h100-migration-v1", "5090delta": "hhyfred/memwam-5090-delta-v1"}
MIN = 1 << 20


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def sidecar(p: Path):
    s = p.with_name(p.name + ".sha256")
    try:
        return s.read_text().split()[0].strip().lower() if s.exists() else None
    except Exception:                                               # noqa: BLE001
        return None


def group_of(key, path):
    parts = path.split("/")
    if key == "fullft":
        return f"fullft:{'/'.join(parts[:2])}"
    if key == "caches":
        return f"caches:{parts[0]}"
    return f"{key}:{'/'.join(parts[2:5])}"                         # payload/workspace/<a>/<b>/<c>


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--machine", required=True)
    ap.add_argument("--hash", action="store_true")
    ap.add_argument("--show-absent", action="store_true",
                    help="no HF call: read this machine's last report and print the groups with files NOT held here")
    args = ap.parse_args()
    if args.show_absent:
        d = json.loads((OUT / "fullft" / f"RELAY_INVENTORY_{args.machine}.json").read_text())
        miss = defaultdict(lambda: [0, 0, None])
        for f in d["files"]:
            if f["state"] not in ("sha", "size"):
                m = miss[f["group"]]
                m[0] += f["size"]; m[1] += 1; m[2] = m[2] or f["path"]
        print(f"[inv] {args.machine} ({d['time']}): {sum(m[0] for m in miss.values()) / 1e9:.1f} GB of HF files not held here")
        for g, (b, n, ex) in sorted(miss.items(), key=lambda x: -x[1][0]):
            print(f"  {b / 1e9:7.2f} GB {n:5d} files  {g}   e.g. {ex}")
        return
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    t0 = time.time()
    hf = []                                                          # (key, path, size, sha)
    for key, rid in REPOS.items():
        try:
            for f in api.list_repo_tree(rid, recursive=True):
                size = getattr(f, "size", None)
                if size is None or size < MIN:
                    continue
                lfs = getattr(f, "lfs", None)
                sha = (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else None
                hf.append((key, f.path, int(size), (sha or "").lower() or None))
        except Exception as e:                                      # noqa: BLE001
            print(f"[inv] {rid}: cannot list ({type(e).__name__}: {str(e)[:120]})")
    print(f"[inv] {args.machine}: {len(hf)} HF files >= 1 MB listed in {time.time() - t0:.0f} s")

    cache_dirs = {}                                                  # folder name -> path (first found, depth <= 4)
    for root, dirs, _ in os.walk(OUT):
        depth = len(Path(root).relative_to(OUT).parts)
        if depth >= 4:
            dirs[:] = []
        for d in dirs:
            cache_dirs.setdefault(d, Path(root) / d)
    try:                                                             # small text file: the joined file's sha256
        p = hf_hub_download(REPOS["fullft"], "ckpt/ar_2task_e30/resume.pt.sha256")
        resume_sha = Path(p).read_text().split()[0].lower()
    except Exception:                                               # noqa: BLE001
        resume_sha = None

    rows = []
    to_hash = []
    ckpt_parts = 0
    for key, path, size, sha in hf:
        parts = path.split("/")
        cands = []
        if key == "fullft" and parts[0] == "exports" and len(parts) == 3:
            run, tag = parts[1].rsplit("_", 1) if "_" in parts[1] else (parts[1], "")
            cands = [OUT / "fullft" / "exports" / parts[1] / parts[2], OUT / "fullft" / run / parts[2]]
        elif key == "fullft" and parts[0] == "ckpt":
            ckpt_parts += size
            continue                                                 # judged as one file below
        elif key == "caches":
            d = cache_dirs.get(parts[0])
            cands = [d / "/".join(parts[1:])] if d else []
        elif parts[:2] == ["payload", "workspace"]:
            cands = [W / "/".join(parts[2:])]
        hit = next((c for c in cands if c.is_file()), None)
        st = "absent"
        if hit is not None:
            ls = hit.stat().st_size
            if ls != size:
                st = "mismatch"
            else:
                sc = sidecar(hit)
                if sha and sc == sha:
                    st = "sha"
                elif sha and sc and sc != sha:
                    st = "mismatch"
                else:
                    st = "size"
                    if args.hash and sha and size >= (1 << 30):
                        to_hash.append(len(rows))
        rows.append({"key": key, "path": path, "size": size, "sha": sha, "local": str(hit) if hit else None,
                     "state": st, "group": group_of(key, path)})
    rp = OUT / "fullft" / "ar_2task" / "resume.pt"
    if ckpt_parts:
        st, hit = "absent", None
        if rp.is_file():
            hit = str(rp)
            st = "size" if rp.stat().st_size == ckpt_parts else "mismatch"
            if st == "size" and resume_sha and args.hash:
                to_hash.append(len(rows))
        rows.append({"key": "fullft", "path": "ckpt/ar_2task_e30 (joined)", "size": ckpt_parts, "sha": resume_sha,
                     "local": hit, "state": st, "group": "fullft:ckpt/ar_2task_e30"})
    if to_hash:
        t1 = time.time()
        with ThreadPoolExecutor(4) as ex:
            got = list(ex.map(lambda i: sha256(Path(rows[i]["local"])), to_hash))
        for i, h in zip(to_hash, got):
            rows[i]["state"] = "sha" if h == rows[i]["sha"] else "mismatch"
            rows[i]["computed"] = True
        print(f"[inv] hashed {len(to_hash)} files ({sum(rows[i]['size'] for i in to_hash) / 1e9:.0f} GB) in "
              f"{time.time() - t1:.0f} s")

    groups = defaultdict(lambda: {"n": 0, "bytes": 0, "sha": 0, "size": 0, "mismatch": 0, "absent": 0, "lbytes": 0})
    for r in rows:
        g = groups[r["group"]]
        g["n"] += 1; g["bytes"] += r["size"]; g[r["state"]] += 1
        if r["state"] in ("sha", "size"):
            g["lbytes"] += r["size"]
    held = sum(g["lbytes"] for g in groups.values())
    print(f"[inv] {args.machine}: holds {held / 1e9:.0f} of {sum(g['bytes'] for g in groups.values()) / 1e9:.0f} GB "
          f"(groups with nothing here are not printed; sha = hash equal, size = size equal only)")
    for name, g in sorted(groups.items()):
        if g["sha"] + g["size"] + g["mismatch"] == 0:
            continue
        print(f"  {name:48s} {g['bytes'] / 1e9:6.1f} GB  files {g['n']:5d}: sha {g['sha']}, size {g['size']}, "
              f"mismatch {g['mismatch']}, absent {g['absent']}")
    rep = OUT / "fullft" / f"RELAY_INVENTORY_{args.machine}.json"
    rep.write_text(json.dumps({"machine": args.machine, "time": time.strftime("%F %T"), "hashed": bool(args.hash),
                               "groups": groups, "files": rows}, indent=0) + "\n")
    print(f"[inv] wrote {rep}")


if __name__ == "__main__":
    main()
