"""Free space on the HF relay (11-25, Opus; HF storage 978.9 GB of 1000 GB at 14:24, HF_USAGE.txt on the A40). Runs ONLY
after the user's explicit yes to the exact list (a permanent deletion; user rule). On the A40 (its huggingface_hub login;
the token is never printed). For every name in the list file (an exports/<name> folder of hhyfred/memwam-fullft):
  1 the A40's own copy outputs/fullft/exports/<name>/export_<tag>.pt exists, its sha256 (computed now) equals its local
    .sha256 file AND the relay's .sha256 file -> else the name is skipped (nothing deleted for it)
  2 all checked names are deleted in ONE commit
  3 --squash: super_squash_history of the repo (old LFS versions stop counting; HF says the quota shows it within 36 h)
Writes outputs/fullft/HF_PRUNE.json; prints HF PRUNE done / nothing.
  /opt/hf-tools/bin/python scripts/fullft/hf_prune.py --list scripts/fullft/hf_prune_list.txt [--squash] [--dry]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

R = Path(__file__).resolve().parents[2]
REPO = "hhyfred/memwam-fullft"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--squash", action="store_true")
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    from huggingface_hub import CommitOperationDelete, HfApi, hf_hub_download
    api = HfApi()
    names = [x.split("#")[0].strip() for x in Path(args.list).read_text().splitlines()]
    names = [x for x in names if x]
    tree = {x.path for x in api.list_repo_tree(REPO, path_in_repo="exports", repo_type="model", recursive=True) if hasattr(x, "size")}
    ok, skipped = [], {}
    for n in names:
        tag = n.rsplit("_", 1)[-1]
        local = R / "outputs/fullft/exports" / n / f"export_{tag}.pt"
        relay_sha = f"exports/{n}/export_{tag}.pt.sha256"
        if relay_sha not in tree:
            skipped[n] = "not on the relay"
            continue
        if not local.exists():
            skipped[n] = "no A40 copy"
            continue
        want_local = (local.parent / (local.name + ".sha256")).read_text().split()[0] if (local.parent / (local.name + ".sha256")).exists() else ""
        want_relay = Path(hf_hub_download(REPO, relay_sha, repo_type="model")).read_text().split()[0]
        got = sha(local)
        if not (got == want_local == want_relay):
            skipped[n] = f"sha256 differs (A40 file {got[:12]}, A40 .sha256 {want_local[:12]}, relay {want_relay[:12]})"
            continue
        ok.append(n)
        print(f"[prune] {n}: A40 copy verified ({got[:16]})", flush=True)
    for n, why in skipped.items():
        print(f"[prune] {n}: SKIPPED ({why})", flush=True)
    out = {"time": time.strftime("%F %T"), "verified": ok, "skipped": skipped, "deleted": [], "squashed": False}
    if ok and not args.dry:
        ops = [CommitOperationDelete(path_in_repo=f"exports/{n}/") for n in ok]
        api.create_commit(REPO, repo_type="model", operations=ops,
                          commit_message=f"prune {len(ok)} exports kept on the A40 (user-confirmed 11-25)")
        out["deleted"] = ok
        print(f"[prune] deleted {len(ok)} folders in one commit", flush=True)
        if args.squash:
            api.super_squash_history(repo_id=REPO, repo_type="model")
            out["squashed"] = True
            print("[prune] history squashed (the quota reflects it within 36 h)", flush=True)
    (R / "outputs/fullft/HF_PRUNE.json").write_text(json.dumps(out, indent=1) + "\n")
    print("HF PRUNE " + ("done" if out["deleted"] else "nothing deleted"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
