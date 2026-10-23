"""Complete the partial RMBench checkout from the official repository, at the exact commit it was taken from.

The A100's resources/RMBench is a file subset of RoboTwin-Platform/RMBench (layout with scripts/, env_cfg/,
data/decode_image_bit.py) and no saved source archive exists on this machine. This script
  1. clones the official repository (blobs fetched lazily) next to our outputs,
  2. hashes every local file as a git blob and finds the commit whose tree matches the checkout best
     (local files patched by the earlier simulator setup show up as "differs" and are left alone),
  3. lists every file of that commit missing locally in the evaluation folders (env_cfg, envs, scripts,
     description, data/*.py, task_config), and with --apply adds them (add-only: no existing file is changed).

    /opt/mwam/bin/python scripts/memory_v2/sim/rmbench_from_git.py            # report
    /opt/mwam/bin/python scripts/memory_v2/sim/rmbench_from_git.py --apply    # add the missing files
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
from collections import Counter
from pathlib import Path

URL = "https://github.com/RoboTwin-Platform/RMBench.git"
R = Path("/workspace/FastWAM/resources/RMBench")
CLONE = Path("/workspace/FastWAM-memory2/outputs/memory_v2/closed_loop/rmbench_official")
SCOPE = ("env_cfg", "envs", "scripts", "description", "data", "task_config")


def git(*args, binary=False):
    env = {**os.environ, "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"}
    out = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(CLONE), *args], check=True, capture_output=True, env=env)
    return out.stdout if binary else out.stdout.decode()


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def local_files():
    out = {}
    for p in R.rglob("*"):
        if not p.is_file() or p.is_symlink() or "__pycache__" in p.parts or ".git" in p.parts:
            continue
        rel = p.relative_to(R).as_posix()
        top = rel.split("/")[0]
        if top in ("assets", "policy", "XPolicyLab") or rel.startswith("data/demo_") or p.suffix in (".pyc", ".hdf5", ".pkl"):
            continue
        if p.stat().st_size > 64 << 20:
            continue
        out[rel] = blob_sha(p.read_bytes())
    return out


def tree(commit):
    rows = {}
    for line in git("ls-tree", "-r", "-z", commit).split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        mode, kind, sha = meta.split()
        rows[path] = (mode, kind, sha)
    return rows


def in_scope(path: str) -> bool:
    top = path.split("/")[0]
    if top not in SCOPE:
        return False
    if top == "data":
        return path.count("/") == 1 and path.endswith(".py")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    print(f"== RMBench from git  apply={args.apply}  checkout={R}  {time.strftime('%F %T')} UTC")
    if not CLONE.exists():
        CLONE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", URL, str(CLONE)], check=True,
                       env={**os.environ, "GIT_LFS_SKIP_SMUDGE": "1", "GIT_TERMINAL_PROMPT": "0"})
    else:
        git("fetch", "-q", "--all")
    local = local_files()
    print(f"-- local files hashed: {len(local)}  {dict(Counter(p.split('/')[0] for p in local).most_common(8))}")
    scores = []
    for commit in git("rev-list", "--all").split():
        t = tree(commit)
        match = sum(1 for p, s in local.items() if p in t and t[p][2] == s)
        differ = sum(1 for p, s in local.items() if p in t and t[p][2] != s)
        scores.append((match - differ, match, differ, commit, t))
    scores.sort(key=lambda x: (x[0], x[1]), reverse=True)
    print("-- best matching commits: score | identical | differ | commit | date subject")
    for score, match, differ, commit, _ in scores[:5]:
        print(f"   {score:>4} {match:>5} {differ:>5}  {commit[:10]}  {git('log', '-1', '--format=%ad %s', '--date=short', commit).strip()}")
    _, match, differ, best, t = scores[0]
    local_only = sorted(p for p in local if p not in t)
    differs = sorted(p for p in local if p in t and t[p][2] != local[p])
    missing = sorted(p for p, (mode, kind, _) in t.items() if kind == "blob" and in_scope(p) and not (R / p).exists())
    print(f"-- chosen {best[:10]}: identical {match}, differ {differ} (left unchanged), local-only {len(local_only)}")
    for p in differs[:15]:
        print(f"   ~ {p}")
    tied = [x for x in scores if (x[0], x[1]) == (scores[0][0], scores[0][1])]
    ambiguous = [p for p in missing if len({x[4].get(p, (None, None, None))[2] for x in tied}) > 1]
    print(f"-- {len(tied)} commit(s) tie with the best score; missing files whose content differs among them: "
          f"{len(ambiguous)} {ambiguous[:10]}")
    print(f"-- missing locally and present in {best[:10]} (evaluation folders): {len(missing)}  "
          f"{dict(Counter(p.split('/')[0] for p in missing))}")
    for p in missing[:80]:
        print(f"   + {p}")
    if len(missing) > 80:
        print(f"   ... {len(missing) - 80} more")
    if args.apply and missing:
        written, lfs = [], []
        for p in missing:
            data = git("cat-file", "blob", t[p][2], binary=True)
            if data.startswith(b"version https://git-lfs"):
                lfs.append(p)
                continue
            target = R / p
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                continue
            tmp = target.with_name(target.name + ".partial")
            tmp.write_bytes(data)
            if t[p][0] == "100755":
                tmp.chmod(0o755)
            tmp.replace(target)
            written.append({"file": p, "blob": t[p][2]})
        report = CLONE.parent / f"rmbench_added_{best[:10]}.json"
        report.write_text(json.dumps({"repository": URL, "commit": best, "identical": match, "differ": differs,
                                      "added": written, "skipped_lfs_pointers": lfs,
                                      "note": "add-only; no existing checkout file was changed"}, indent=1))
        print(f"-- ADDED {len(written)} files (LFS pointers skipped: {len(lfs)}); report {report}")
    required = ["env_cfg/task_config/demo_clean.yml", "data/decode_image_bit.py", "scripts/eval_policy.py"]
    absent = [p for p in required if not (R / p).exists()]
    if absent:
        print(f"-- still missing: {absent}")
    print("COMPLETE" if not absent and (args.apply or not missing) else "INCOMPLETE")


if __name__ == "__main__":
    main()
