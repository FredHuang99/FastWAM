"""Small-file relay between our machines through a private HF model repo (11-08, 5090 online diagnosis).

The machines cannot reach each other; each has `hf auth login` done in its container (the token is read from there
by huggingface_hub and never printed or written by this script).
  put FILE ... --prefix diag/<tag>      upload the files to <repo>/<prefix>/<file name> (repo created private if missing)
  get --prefix diag/<tag> --out DIR     download every file under <prefix> into DIR (flat)
Run with the HF tools python: /opt/hf-tools/bin/python scripts/memory_v2/migrate/relay.py ...
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

REPO = "hhyfred/memwam-diag-v1"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("put", "get"))
    ap.add_argument("files", nargs="*")
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--out", default=".")
    ap.add_argument("--repo", default=REPO)
    args = ap.parse_args()
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    prefix = args.prefix.strip("/")
    if args.cmd == "put":
        api.create_repo(args.repo, repo_type="model", private=True, exist_ok=True)
        for f in args.files:
            p = Path(f)
            api.upload_file(path_or_fileobj=str(p), path_in_repo=f"{prefix}/{p.name}", repo_id=args.repo,
                            repo_type="model", commit_message=f"{prefix}/{p.name}")
            print(f"[relay] put {p} ({p.stat().st_size} bytes) -> {args.repo}/{prefix}/{p.name}", flush=True)
        return
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    names = [x.path for x in api.list_repo_tree(args.repo, path_in_repo=prefix, repo_type="model", recursive=True)
             if hasattr(x, "size")]
    if not names:
        raise SystemExit(f"[relay] nothing under {args.repo}/{prefix}")
    for name in names:
        local = hf_hub_download(args.repo, name, repo_type="model")
        dst = out / Path(name).name
        shutil.copyfile(local, dst)
        print(f"[relay] get {args.repo}/{name} -> {dst} ({dst.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
