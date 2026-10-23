"""H100 -> HF: build a COMPLETE manifest (previous payload + everything produced on the H100) for an
incremental upload to the same repo. Unchanged files are already on the hub and are skipped by the
uploader; only new/changed files travel. Reuses manifest.py stage/upload.

    python h100_save.py --mig /mnt/tmp/save_h100 --old /mnt/hf/MANIFEST.json [--env-tar PATH ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import FEATURES, FW, MEM2, gib, secret, walk  # noqa: E402

FINAL = "update_001340.pt"


def run_complete(run_dir: Path) -> bool:
    try:
        return '"complete": true' in (run_dir / "train.log").read_text(errors="replace")
    except OSError:
        return False


def keep_checkpoint(path: str) -> bool:
    """Final checkpoints; for unfinished runs also the latest one (resume with --resume)."""
    p = Path(path)
    if p.suffix != ".pt" or "checkpoints" not in p.parts:
        return not path.endswith(".partial")
    if p.name == FINAL:
        return True
    run = p.parent.parent
    if run_complete(run):
        return False
    try:
        return json.loads((p.parent / "LATEST.json").read_text())["file"] == p.name
    except (OSError, ValueError, KeyError):
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mig", required=True)
    ap.add_argument("--old", required=True, help="MANIFEST.json of the previous upload")
    ap.add_argument("--env-tar", nargs="*", default=[], help="environment tarballs to include under /envs/")
    args = ap.parse_args()
    mig = Path(args.mig)
    mig.mkdir(parents=True, exist_ok=True)
    old = json.loads(Path(args.old).read_text())
    files, owner, trusted = [], set(), {}

    def add(path, group, sha=None, real=None):
        real = real or path
        if path in owner or secret(path) or not os.path.isfile(real):
            return
        owner.add(path)
        st = os.stat(real)
        files.append({"path": path, "real": os.path.realpath(real), "size": st.st_size, "group": group})
        if sha:
            trusted[f"{os.path.realpath(real)}|{st.st_size}|{st.st_mtime_ns}"] = sha

    # 1. previous payload: large static inputs keep their recorded sha when the size is unchanged
    missing = 0
    for f in old["files"]:
        p = f["path"]
        if not os.path.isfile(p):
            missing += 1
            continue
        static = not p.startswith(MEM2 + "/outputs/")
        add(p, f["group"], f["sha256"] if static and os.path.getsize(p) == f["size"] else None)
    # 2. everything produced since (new runs, PR/eval results, reports, logs)
    save_dir = os.path.realpath(mig)
    for p in walk(MEM2 + "/outputs", skip_dirs=(FEATURES, MEM2 + "/outputs/migration_h100_v1/stage"),
                  keep=lambda p: keep_checkpoint(p) and not os.path.realpath(p).startswith(save_dir)):
        add(p, "h100_outputs")
    # 3. simulator sources completed on the H100 (CuRobo C++/CUDA sources, PyTorch3D, ready package)
    for top, group in ((FW + "/resources/RMBench", "simulator_h100"), (FW + "/resources/PyTorch3D", "simulator_h100"),
                       (FW + "/outputs/recovery_aws_h100", "recovery_h100")):
        skip = [top + "/data"] if top.endswith("RMBench") else []
        for p in walk(top, skip_dirs=skip):
            add(p, group)
    # 4. built environments
    for tar in args.env_tar:
        add("/envs/" + os.path.basename(tar), "envs", real=tar)

    total = sum(f["size"] for f in files)
    groups = {}
    for f in files:
        g = groups.setdefault(f["group"], [0, 0])
        g[0] += 1
        g[1] += f["size"]
    print(f"{'group':<18}{'files':>8}{'size':>14}")
    for g, (n, s) in sorted(groups.items()):
        print(f"{g:<18}{n:>8}{gib(s):>14}")
    print(f"{'TOTAL':<18}{len(files):>8}{gib(total):>14}   (previous files no longer on disk: {missing})")
    draft = {"version": 2, "base_manifest": args.old, "logical_roots": old.get("logical_roots"),
             "total_bytes": total, "files": files}
    (mig / "MANIFEST.draft.json").write_text(json.dumps(draft, indent=1))
    cache = mig / "hash_cache.json"
    known = json.loads(cache.read_text()) if cache.exists() else {}
    known.update(trusted)
    cache.write_text(json.dumps(known))
    print(f"[save] {mig / 'MANIFEST.draft.json'}; {len(trusted)} sha256 reused from the previous manifest")


if __name__ == "__main__":
    main()
