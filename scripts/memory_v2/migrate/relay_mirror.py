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
from concurrent.futures import ThreadPoolExecutor
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


ALIASES = tuple(tuple(x.split("=", 1)) for x in os.environ.get(
    "MWAM_MIRROR_ALIASES", "/workspace/FastWAM-memory2=/mnt/hf/payload/workspace/FastWAM-memory2,"
                           "/workspace/FastWAM=/mnt/hf/payload/workspace/FastWAM").split(","))


def own_copy(src: Path, out: Path) -> str:
    """A copy of src at out that survives deleting src: a hard link through the path of src on the same mount as
    out (the 5090 mounts /database/mwam/hf at /mnt/hf and its payload/workspace/... again at /workspace/...), else a
    full copy. Returns 'link' or 'copy'."""
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        if src.exists() and os.path.samefile(src, out):
            return "link"
        out.unlink()
    for a, b in ALIASES:
        if str(src).startswith(a + "/"):
            alias = Path(b + str(src)[len(a):])
            if alias.exists() and os.path.samefile(alias, src):
                try:
                    os.link(alias, out)
                    return "link"
                except OSError:
                    break
    tmp = out.with_name(out.name + ".part")
    shutil.copyfile(src, tmp)
    tmp.rename(out)
    return "copy"


def finalize(todo, dest: Path, man_p: Path, man: dict) -> int:
    """Download completeness: every file listed on HF now must have its own file under DEST with HF's sha256 (LFS)
    or size (small files). Files the 5090 held before get a hard link (or copy) under DEST first."""
    t0 = time.time()
    missing, linked, copied = [], 0, 0
    jobs = []
    for rid, path, size, sha in todo:
        key = f"{rid}:{path}"
        e = man.get(key)
        out = dest / rid.split("/")[1] / path
        if not e:
            missing.append(f"{key} (not in the manifest)")
            continue
        if not e.get("copy"):
            src = Path(e["where"])
            if not src.is_file():
                missing.append(f"{key} (held file gone: {src})")
                continue
            how = own_copy(src, out)
            linked += how == "link"; copied += how == "copy"
            e.update(src=str(src), where=str(out), copy=how)
        if not out.is_file() or out.stat().st_size != size:
            missing.append(f"{key} (no file of the right size at {out})")
            e["verified"] = False
            continue
        jobs.append((key, out, sha))
    with ThreadPoolExecutor(6) as ex:
        got = list(ex.map(lambda j: sha256(j[1]) if j[2] else None, jobs))
    bad = []
    for (key, out, sha), h in zip(jobs, got):
        ok = (h == sha) if sha else True
        man[key]["verified"] = ("sha" if sha else "size") if ok else False
        man[key]["finalized"] = time.strftime("%F %T")
        if not ok:
            bad.append(f"{key} (sha256 differs)")
    man_p.write_text(json.dumps(man, indent=0) + "\n")
    hashed = sum(1 for j in jobs if j[2])
    print(f"[mirror] {time.strftime('%F %T')} finalize: {len(todo)} files on HF; own copies under {dest}: "
          f"{len(jobs)} ({linked} hard links and {copied} copies of files the 5090 already held); sha256 checked "
          f"{hashed}; missing {len(missing)}; sha256 different {len(bad)}; {time.time() - t0:.0f} s", flush=True)
    for x in (missing + bad)[:20]:
        print(f"    {x}", flush=True)
    return 0 if not missing and not bad else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--finalize", action="store_true",
                    help="after the download: every HF file gets its own copy under DEST (files the 5090 held are "
                         "hard-linked, else copied), and every copy is sha256-checked against HF; exit 0 only if all")
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
    if args.finalize:
        return finalize(todo, dest, man_p, man)
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
            if man.get(key, {}).get("copy") in ("link", "copy") and man[key].get("verified"):
                continue                                             # finalized before: own copy under DEST
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
