"""HF relay: move exports off the relay to the 5090's disk (11-25 14:55, user: "the other 12: download them to the 5090,
then delete; automatic, one downloaded, one deleted"). Runs on the 5090 (its huggingface_hub login; the token is never
printed). For each name in the list (an exports/<name> folder of hhyfred/memwam-fullft), in order:
  1 every file of the folder -> outputs/fullft/exports_hf_backup/exports/<name>/ ; the .pt's sha256 (computed now) must
    equal the folder's .sha256 file, else stop for that name (nothing deleted for it)
  2 delete that folder on the relay (one commit; 3 tries a few minutes apart -- another machine may be committing)
then (--squash) super_squash_history so the freed space counts (HF: the quota shows it within 36 h). Re-runnable: a name
already gone from the relay with a verified backup is skipped. Writes outputs/fullft/HF_OFFLOAD.json.
  /opt/hf-tools/bin/python scripts/fullft/hf_offload.py --list scripts/fullft/hf_offload_list.txt [--squash]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

R = Path(__file__).resolve().parents[2]
REPO = "hhyfred/memwam-fullft"
BK = R / "outputs/fullft/exports_hf_backup"


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def retry(fn, what, tries=3, wait=300):
    for k in range(tries):
        try:
            return fn()
        except Exception as e:                                                       # noqa: BLE001
            print(f"[offload] {what}: try {k + 1} failed ({type(e).__name__}: {str(e)[:160]})", flush=True)
            if k + 1 < tries:
                time.sleep(wait)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--squash", action="store_true")
    args = ap.parse_args()
    from huggingface_hub import CommitOperationDelete, HfApi, hf_hub_download
    api = HfApi()
    names = [x.split("#")[0].strip() for x in Path(args.list).read_text().splitlines()]
    names = [x for x in names if x]
    out = {"started": time.strftime("%F %T"), "done": [], "skipped": {}, "squashed": False}
    for n in names:
        tag = n.rsplit("_", 1)[-1]
        files = [x.path for x in api.list_repo_tree(REPO, path_in_repo=f"exports/{n}", repo_type="model", recursive=True)
                 if hasattr(x, "size")]
        local = BK / "exports" / n
        pt = local / f"export_{tag}.pt"
        if not files:
            if pt.exists() and (local / f"export_{tag}.pt.sha256").exists():
                out["skipped"][n] = "already off the relay (backup present)"
            else:
                out["skipped"][n] = "not on the relay and no backup"
            print(f"[offload] {n}: {out['skipped'][n]}", flush=True)
            continue
        for f in files:
            if retry(lambda: hf_hub_download(REPO, f, repo_type="model", local_dir=str(BK)), f"get {f}") is None:
                break
        want = (local / f"export_{tag}.pt.sha256").read_text().split()[0] if (local / f"export_{tag}.pt.sha256").exists() else ""
        got = sha(pt) if pt.exists() else ""
        if not want or got != want:
            out["skipped"][n] = f"backup not verified (file {got[:12]}, .sha256 {want[:12]}): NOT deleted"
            print(f"[offload] {n}: {out['skipped'][n]}", flush=True)
            continue
        print(f"[offload] {n}: backup verified ({got[:16]}, {pt.stat().st_size} bytes) -> deleting on the relay", flush=True)
        ok = retry(lambda: api.create_commit(REPO, repo_type="model",
                                             operations=[CommitOperationDelete(path_in_repo=f"exports/{n}/")],
                                             commit_message=f"offload {n} to the 5090 (user-confirmed 11-25)"), f"delete {n}")
        if ok is None:
            out["skipped"][n] = "backup verified, relay delete failed (kept on the relay)"
            continue
        out["done"].append(n)
        (R / "outputs/fullft/HF_OFFLOAD.json").write_text(json.dumps(out, indent=1) + "\n")
    if args.squash and out["done"]:
        if retry(lambda: api.super_squash_history(repo_id=REPO, repo_type="model"), "squash") is not None:
            out["squashed"] = True
            print("[offload] history squashed (quota within 36 h)", flush=True)
    out["finished"] = time.strftime("%F %T")
    (R / "outputs/fullft/HF_OFFLOAD.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"HF OFFLOAD: {len(out['done'])} moved to the 5090, {len(out['skipped'])} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
