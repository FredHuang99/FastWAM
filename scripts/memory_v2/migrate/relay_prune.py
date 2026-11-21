"""Keep only what is necessary on the HF relay, after the 5090 holds a checked copy of everything (11-21 16:05, Opus;
user 15:46: "5090 stores it; HF keeps only what is necessary"). DRY RUN by default; deletes ONLY with --yes, which is
run only after the user has confirmed the printed list.

Kept on HF (whole repos): memwam-caches (the GaaS may train on more tasks), memwam-diag-v1, fastwam-memory-s1-backup.
Deleted:
  repos hhyfred/memwam-h100-migration-v1, hhyfred/memwam-5090-delta-v1 (one-time transfers)       -> delete_repo
  hhyfred/memwam-fullft: every file under exports/ and ckpt/ that is in the 5090 mirror manifest  -> removed from the
      current revision AND its LFS objects permanently deleted (else they keep counting against storage)
Guard (per file, before anything is deleted): its entry in /mnt/hf/relay_mirror/MIRROR_MANIFEST.json must be
  finalized (relay_mirror.py --finalize: its own file under the mirror folder, sha256 = HF's), the file must still be
  there with HF's size, and its sha256 is computed again here and must equal HF's current one (files without an LFS
  sha256, i.e. small text, by size). Files
  uploaded after the mirror ran (e.g. the backlog exports) are not in the manifest and are never touched.
One unchecked or different file -> nothing at all is deleted (exit 2).
The token is read by huggingface_hub from the container's login, never printed.
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_prune.py          (dry run: the plan and the checks)
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_prune.py --yes    (deletes; irreversible)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MANIFEST = Path(os.environ.get("MWAM_MIRROR_MANIFEST", "/mnt/hf/relay_mirror/MIRROR_MANIFEST.json"))
DELETE_REPOS = ("hhyfred/memwam-h100-migration-v1", "hhyfred/memwam-5090-delta-v1")
FULLFT = "hhyfred/memwam-fullft"
FULLFT_PREFIXES = ("exports/", "ckpt/")
KEEP_REPOS = ("hhyfred/memwam-caches", "hhyfred/memwam-diag-v1", "hhyfred/fastwam-memory-s1-backup")


def gb(n):
    return f"{n / 1e9:.1f} GB"


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="really delete (irreversible)")
    args = ap.parse_args()
    from huggingface_hub import CommitOperationDelete, HfApi
    api = HfApi()
    man = json.loads(MANIFEST.read_text())
    print(f"[prune] {'DELETING' if args.yes else 'dry run'}; mirror manifest {MANIFEST} ({len(man)} entries)", flush=True)
    plan = {}                                                        # repo -> [(path, size, sha)]
    kept_sha = set()                                                 # LFS objects still used by kept fullft files
    gone = set()
    for rid in DELETE_REPOS + (FULLFT,):
        rows = []
        try:
            tree = list(api.list_repo_tree(rid, recursive=True))
        except Exception as e:                                      # noqa: BLE001
            if rid in DELETE_REPOS and ("404" in str(e) or "NotFound" in type(e).__name__):
                print(f"[prune] {rid}: does not exist (deleted before)", flush=True)
                gone.add(rid)
                plan[rid] = []
                continue
            raise
        for f in tree:
            size = getattr(f, "size", None)
            if size is None:
                continue
            lfs = getattr(f, "lfs", None)
            sha = (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else None
            rows.append((f.path, int(size), (sha or "").lower() or None))
        if rid == FULLFT:                                            # only exports/ and ckpt/ the mirror has seen
            keep = [r for r in rows if not (r[0].startswith(FULLFT_PREFIXES) and f"{rid}:{r[0]}" in man)]
            kept_sha = {r[2] for r in keep if r[2]}
            rows = [r for r in rows if r not in keep]
        plan[rid] = rows
    bad, to_hash = [], []
    for rid in DELETE_REPOS:                 # a whole repo goes: today's listing must hold every file the mirror saw
        if rid in gone:
            continue
        seen = {k.split(":", 1)[1] for k in man if k.startswith(rid + ":")}
        now = {r[0] for r in plan[rid]}
        if not seen or seen - now:
            bad.append(f"{rid}: the mirror saw {len(seen)} files, today's listing lacks {len(seen - now)} of them")
    for rid, rows in plan.items():                                   # every file: its own finalized copy on the 5090
        for path, size, sha in rows:
            e = man.get(f"{rid}:{path}")
            w = Path(e["where"]) if e and e.get("where") else None
            if not e or not e.get("verified") or not e.get("finalized") or e.get("copy") not in ("link", "copy", True):
                bad.append(f"{rid}:{path} (no finalized copy: {e and (e.get('verified'), e.get('copy'))})")
            elif int(e.get("size", -1)) != size or not w.is_file() or w.stat().st_size != size:
                bad.append(f"{rid}:{path} (copy missing or of another size: {w})")
            elif sha:
                to_hash.append((rid, path, sha, str(w)))             # hashed again here, independently of the mirror
    if to_hash:
        print(f"[prune] re-hashing {len(to_hash)} copies on the 5090 "
              f"({sum(Path(w).stat().st_size for *_, w in to_hash) / 1e9:.0f} GB)", flush=True)
        with ThreadPoolExecutor(6) as ex:
            got = list(ex.map(lambda t: sha256(t[3]), to_hash))
        bad += [f"{r}:{p} (sha256 of the copy differs from HF: {w})" for (r, p, s, w), h in zip(to_hash, got) if h != s]
    for rid, rows in plan.items():
        print(f"[prune] {rid}: delete {len(rows)} files, {gb(sum(r[1] for r in rows))}", flush=True)
    for rid in KEEP_REPOS:
        print(f"[prune] {rid}: kept", flush=True)
    if bad:
        print(f"[prune] REFUSED: {len(bad)} files not checked against the 5090 copy, nothing deleted:", flush=True)
        for b in bad[:20]:
            print(f"    {b}")
        return 2
    print(f"[prune] every file to delete has a checked copy on the 5090; total {gb(sum(r[1] for rows in plan.values() for r in rows))}",
          flush=True)
    if not args.yes:
        return 0
    for rid in DELETE_REPOS:
        if rid in gone:
            continue
        api.delete_repo(rid, repo_type="model")
        print(f"[prune] repo {rid}: DELETED", flush=True)
    rows = plan[FULLFT]
    paths = {r[0] for r in rows}
    for i in range(0, len(rows), 200):
        api.create_commit(FULLFT, operations=[CommitOperationDelete(path_in_repo=r[0]) for r in rows[i:i + 200]],
                          commit_message=f"prune {len(rows[i:i + 200])} mirrored files (user-confirmed; copy on the 5090)")
    lfs = [f for f in api.list_lfs_files(FULLFT) if getattr(f, "filename", None) in paths
           and (getattr(f, "oid", "") or "").lower() not in kept_sha]
    if lfs:
        api.permanently_delete_lfs_files(FULLFT, lfs)
    print(f"[prune] {FULLFT}: {len(rows)} files removed, {len(lfs)} LFS objects permanently deleted", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
