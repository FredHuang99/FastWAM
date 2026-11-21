"""Mirror our HF relay onto the 5090's big disk (11-21 16:00, Opus; user 15:46: "5090 has a 4 TB disk to store it;
then keep only what is necessary on HF, so it is safe"). The 5090 is an NTU machine.

Every file of the relay repos is either already on the 5090 (its RELAY_INVENTORY_5090.json says sha / size: recorded,
not copied) or downloaded into DEST/<repo name>/<path> and checked: LFS files by sha256 against HF, small files by
size. Exports first (those are the ones only NUS machines or the new H200 hold), then the rest. Resumable: a file
already in DEST with the right size and a 'verified' entry in the manifest is skipped. Nothing on HF is changed.
Writes DEST/MIRROR_MANIFEST.json (repo, path, size, sha256, where, verified) after every file, and a log line each.
The token is read by huggingface_hub from the container's login, never printed.
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_mirror.py --dest /mnt/xxx/mwam_relay_mirror [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import time
from pathlib import Path

REPOS = ("hhyfred/memwam-fullft", "hhyfred/memwam-caches", "hhyfred/memwam-h100-migration-v1",
         "hhyfred/memwam-5090-delta-v1", "hhyfred/memwam-diag-v1", "hhyfred/fastwam-memory-s1-backup")
INV_KEY = {"hhyfred/memwam-fullft": "fullft", "hhyfred/memwam-caches": "caches",
           "hhyfred/memwam-h100-migration-v1": "h100mig", "hhyfred/memwam-5090-delta-v1": "5090delta"}
INV = Path(os.environ.get("MWAM_INV", "/workspace/FastWAM-memory2/outputs/fullft/RELAY_INVENTORY_5090.json"))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)
    man_p = dest / "MIRROR_MANIFEST.json"
    man = json.loads(man_p.read_text()) if man_p.exists() else {}
    held = {}
    if INV.exists():
        for f in json.loads(INV.read_text())["files"]:
            if f["state"] in ("sha", "size") and f.get("local") and "(joined)" not in f["path"]:
                held[(f["key"], f["path"])] = (f["local"], f["state"])
    todo = []
    for rid in REPOS:
        try:
            for f in api.list_repo_tree(rid, recursive=True):
                size = getattr(f, "size", None)
                if size is None:
                    continue
                lfs = getattr(f, "lfs", None)
                sha = (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else None
                todo.append((rid, f.path, int(size), (sha or "").lower() or None))
        except Exception as e:                                      # noqa: BLE001
            print(f"[mirror] {rid}: cannot list ({type(e).__name__}: {str(e)[:120]})", flush=True)
            return 1
    todo.sort(key=lambda x: (not x[1].startswith("exports/"), x[0], x[1]))
    total = sum(x[2] for x in todo)
    already = sum(x[2] for x in todo if (INV_KEY.get(x[0]), x[1]) in held)
    print(f"[mirror] {len(todo)} files, {total / 1e9:.1f} GB on HF; on the 5090 already {already / 1e9:.1f} GB; "
          f"free in {dest}: {shutil.disk_usage(dest).free / 1e9:.0f} GB", flush=True)
    if args.dry_run:
        return 0
    got = 0
    t0 = time.time()
    for i, (rid, path, size, sha) in enumerate(todo, 1):
        key = f"{rid}:{path}"
        h = held.get((INV_KEY.get(rid), path))
        if h:
            man[key] = {"size": size, "sha256": sha, "where": h[0], "verified": h[1], "copy": False}
            continue
        out = dest / rid.split("/")[1] / path
        if man.get(key, {}).get("verified") and out.is_file() and out.stat().st_size == size:
            continue
        for attempt in (1, 2, 3):
            try:
                p = Path(hf_hub_download(rid, path, local_dir=str(dest / rid.split("/")[1])))
                ok = p.stat().st_size == size and (sha is None or sha256(p) == sha)
            except Exception as e:                                  # noqa: BLE001
                ok, p = False, None
                print(f"[mirror] {key}: try {attempt} {type(e).__name__}: {str(e)[:160]}", flush=True)
            if ok:
                break
            time.sleep(30)
        man[key] = {"size": size, "sha256": sha, "where": str(out), "verified": "sha" if ok and sha else
                    ("size" if ok else False), "copy": True}
        man_p.write_text(json.dumps(man, indent=0) + "\n")
        got += size if ok else 0
        if size >= (1 << 30) or not ok:
            el = time.time() - t0
            print(f"[mirror] {time.strftime('%F %T')} {i}/{len(todo)} {key} {size / 1e9:.1f} GB "
                  f"{'OK' if ok else 'FAILED'}; {got / 1e9:.0f} GB fetched, {got / 1e6 / max(el, 1):.0f} MB/s", flush=True)
    man_p.write_text(json.dumps(man, indent=0) + "\n")
    bad = [k for k, v in man.items() if not v.get("verified")]
    print(f"[mirror] {time.strftime('%F %T')} done: {len(man)} files recorded, {got / 1e9:.0f} GB fetched, "
          f"{len(bad)} not verified{': ' + ', '.join(bad[:10]) if bad else ''}", flush=True)
    return 0 if not bad else 2


if __name__ == "__main__":
    raise SystemExit(main())
