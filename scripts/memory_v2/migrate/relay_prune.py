"""Free HF storage on our relay account (11-21 15:20, Opus). Since 11-20 ~22:45 every export upload fails with
403 "set up automatic credit recharge to use more storage"; relay_usage.py (5090, 15:09): account PRO, 990 GB
stored. DRY RUN by default: prints what would go and how many bytes. Deletes ONLY with --yes, and only the targets
named below (fixed in the code, nothing from the command line), each of which is a finished one-time transfer whose
source still exists elsewhere (per the project records):
  repo   hhyfred/memwam-h100-migration-v1   (124 GB) A100 -> H100 workspace payload (11-0x); also fetched by the GaaS
                                             (~/mwam/hf/payload, fetch_2task.sh / setup_parity.pbs, 11-17)
  repo   hhyfred/memwam-5090-delta-v1       (53 GB)  the 5090's delta payload (11-0x)
  folder hhyfred/memwam-fullft:ckpt/ar_2task_e30 (72 GB) ar_2task's resume.pt in parts, old H200 -> GaaS (11-17), joined
                                             there for ar2_long (finished 11-20); the original stays on the old H200
A whole repo is deleted with delete_repo. The folder is deleted from the current revision AND its LFS objects are
permanently deleted (permanently_delete_lfs_files), because files removed only from the current revision keep
counting against storage. Irreversible: run with --yes only after the user's explicit confirmation.
The token is read by huggingface_hub from the container's login and never printed.
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_prune.py          (dry run)
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_prune.py --yes    (deletes)
"""
from __future__ import annotations

import argparse

REPOS = ("hhyfred/memwam-h100-migration-v1", "hhyfred/memwam-5090-delta-v1")
FOLDERS = (("hhyfred/memwam-fullft", "ckpt/ar_2task_e30"),)


def gb(n):
    return f"{n / 1e9:.1f} GB"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--yes", action="store_true", help="really delete (irreversible)")
    args = ap.parse_args()
    from huggingface_hub import HfApi
    import huggingface_hub
    api = HfApi()
    print(f"[prune] huggingface_hub {huggingface_hub.__version__}; account {api.whoami()['name']}; "
          f"{'DELETING' if args.yes else 'dry run'}")
    total = 0
    for rid in REPOS:
        try:
            size = sum(int(getattr(f, "size", 0) or 0) for f in api.list_repo_tree(rid, recursive=True))
        except Exception as e:                                      # noqa: BLE001
            print(f"[prune] repo {rid}: cannot list ({type(e).__name__}); skipped")
            continue
        total += size
        print(f"[prune] repo {rid}: {gb(size)}")
        if args.yes:
            api.delete_repo(rid, repo_type="model")
            print(f"[prune] repo {rid}: DELETED")
    for rid, folder in FOLDERS:
        pre = folder.rstrip("/") + "/"
        if not hasattr(api, "permanently_delete_lfs_files"):
            print(f"[prune] {rid}:{folder}: this huggingface_hub cannot delete LFS objects permanently; skipped")
            continue
        lfs = [f for f in api.list_lfs_files(rid) if (getattr(f, "filename", None) or "").startswith(pre)]
        size = sum(int(f.size or 0) for f in lfs)
        head = [x.path for x in api.list_repo_tree(rid, path_in_repo=folder, recursive=True)
                if getattr(x, "size", None) is not None]
        total += size
        print(f"[prune] {rid}:{folder}: {len(head)} files at HEAD; {len(lfs)} LFS objects, {gb(size)}")
        if args.yes:
            if head:
                api.delete_folder(folder, repo_id=rid, commit_message=f"prune {folder} (user-confirmed, HF storage full)")
            if lfs:
                api.permanently_delete_lfs_files(rid, lfs)
            print(f"[prune] {rid}:{folder}: DELETED")
    print(f"[prune] {'freed' if args.yes else 'would free'} about {gb(total)}")


if __name__ == "__main__":
    main()
