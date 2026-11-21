"""How much of the HF account's storage do our relay repos use? (11-16 night, Opus; read-only: lists, never writes.
11-21: export uploads fail with 403 "set up automatic credit recharge to use more storage"; adds LFS over history.)

Hugging Face counts private repos against the account's private storage (docs, Nov 2026: free 100 GB, PRO 1 TB, then
pay-as-you-go). This prints, for every model / dataset repo of the logged-in account: files and GB in the current
revision, the biggest folders (two path levels, e.g. exports/press_ar_e10), and the total. Files deleted from a repo
still count until its history is squashed, so the account page (huggingface.co/settings/storage) can show more.
The token comes from the container's `hf auth login` and is never printed.
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay_usage.py [--top 25]
"""
from __future__ import annotations

import argparse
from collections import defaultdict


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()
    from huggingface_hub import HfApi
    api = HfApi()
    me = api.whoami()
    name = me.get("name")
    plan = "PRO" if me.get("isPro") else "free (or not reported)"
    print(f"account {name}; plan {plan}; orgs {[o.get('name') for o in me.get('orgs', [])]}")
    repos = [("model", r.id) for r in api.list_models(author=name)] + \
            [("dataset", r.id) for r in api.list_datasets(author=name)]
    total, folders = 0, defaultdict(int)
    hist_total = [0]
    for kind, rid in repos:
        size = n = 0
        try:
            for f in api.list_repo_tree(rid, repo_type=kind, recursive=True):
                s = getattr(f, "size", None)
                if s is None:
                    continue
                size += int(s); n += 1
                parts = f.path.split("/")
                folders[f"{rid}/{'/'.join(parts[:2]) if len(parts) > 2 else parts[0]}"] += int(s)
        except Exception as e:                                       # noqa: BLE001
            print(f"  {kind} {rid}: cannot list ({type(e).__name__})")
            continue
        total += size
        hist = ""                       # 11-21: LFS bytes kept over the whole history (what storage counts), if listable
        if hasattr(api, "list_lfs_files"):
            try:
                hb = sum(int(getattr(x, "size", 0) or 0) for x in api.list_lfs_files(rid, repo_type=kind))
                hist_total[0] += hb
                hist = f"; LFS over history {hb / 1e9:.1f} GB"
            except Exception as e:                                   # noqa: BLE001
                hist = f"; LFS over history: cannot list ({type(e).__name__})"
        print(f"  {kind:7s} {rid}: {n} files, {size / 1e9:.1f} GB{hist}")
    print(f"TOTAL (current revisions): {total / 1e9:.1f} GB")
    print(f"TOTAL LFS over history (0 = not listable with this huggingface_hub): {hist_total[0] / 1e9:.1f} GB")
    print(f"biggest folders:")
    for k, v in sorted(folders.items(), key=lambda x: -x[1])[:args.top]:
        print(f"  {v / 1e9:7.1f} GB  {k}")


if __name__ == "__main__":
    main()
