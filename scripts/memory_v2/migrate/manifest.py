"""A100 -> H100 migration manifest: build, stage, upload (A100); verify, compare (H100).

Paths are stored as the *logical* paths the code uses (/workspace/FastWAM, /workspace/FastWAM-memory2,
/restore-tmp), whatever symlinks/RAID mounts they resolve to on the A100 server. On the H100 they are
downloaded to <hf>/payload/<logical path> and bind-mounted back to the same logical paths.

  build   : groups from fixed roots + file traces (trace_run.py) -> <mig>/MANIFEST.draft.json, size table
  stage   : sha256 (cached) + hardlink/symlink tree <mig>/stage/payload/..., <mig>/stage/MANIFEST.json
  upload  : private HF model repo, resumable upload_large_folder of <mig>/stage
  verify  : (H100) every manifest file present with the same size and sha256
  compare : two evaluate JSONs (A100 reference vs H100)
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import fnmatch
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MEM2 = "/workspace/FastWAM-memory2"
FW = "/workspace/FastWAM"
RESTORE = "/restore-tmp"
LOGICAL_ROOTS = (MEM2, FW, RESTORE)
DENSE_CODE = RESTORE + "/dense_joint_v1"
DENSE_OUT = FW + "/outputs/s1_dense_joint_h100_v1"
FEATURES = MEM2 + "/outputs/memory_v2/features_dense_v1"
HF_CACHE = "/root/.cache/huggingface"
SYSTEM = ("/usr/", "/opt/", "/proc/", "/sys/", "/dev/", "/etc/", "/lib", "/bin/", "/sbin/", "/run/", "/var/",
          "/tmp/", "/snap/")
SECRET = ("token", "stored_tokens", "*.pem", "*.key", "auth.json", ".netrc", ".git-credentials", "id_rsa*",
          "id_ed25519*", "*.secret", ".env")
NEVER_DIRS = {"__pycache__", ".git", ".cache", ".ipynb_checkpoints"}
MAX_HF_FILE = 45 * 1024 ** 3
FINAL_CHECKPOINT = "update_001340.pt"


def stage_path(path: str) -> str:
    """Repo path of a logical path (HF upload ignores '.cache/huggingface', so that dir is renamed)."""
    return "payload/" + path.lstrip("/").replace(".cache/huggingface", "dot-cache-huggingface")


def gib(n):
    return f"{n / 2 ** 30:8.2f} GiB"


def secret(path: str) -> bool:
    name = os.path.basename(path)
    return any(fnmatch.fnmatch(name, p) for p in SECRET) or "/.cache/huggingface/token" in path


def _real_roots():
    out = []
    for r in LOGICAL_ROOTS:
        if os.path.exists(r):
            out.append((os.path.realpath(r), r))
    return sorted(out, key=lambda x: -len(x[0]))


REAL_ROOTS = _real_roots()


def logical(path: str) -> str:
    """Map a (possibly resolved) path back to its logical root; other paths are returned resolved."""
    if any(path == r or path.startswith(r + "/") for r in LOGICAL_ROOTS):
        return os.path.normpath(path)
    real = os.path.realpath(path)
    for rr, lr in REAL_ROOTS:
        if real == rr or real.startswith(rr + "/"):
            return lr + real[len(rr):]
    return real


def walk(top: str, skip_dirs=(), keep=lambda p: True):
    if not os.path.isdir(top):
        return
    skip = {os.path.normpath(s) for s in skip_dirs}
    for dirpath, dirnames, filenames in os.walk(top):
        dirnames[:] = [d for d in dirnames if d not in NEVER_DIRS and os.path.join(dirpath, d) not in skip]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if os.path.isfile(p) and not secret(p) and keep(p):
                yield p


def git_files(repo: str, exclude_prefixes=("resources/", "outputs/"), max_bytes=100 * 2 ** 20):
    if not os.path.isdir(os.path.join(repo, ".git")):
        for sub in ("src", "configs", "scripts"):
            yield from walk(os.path.join(repo, sub))
        return
    run = subprocess.run(["git", "-c", "safe.directory=*", "-C", repo, "ls-files", "-co", "--exclude-standard", "-z"],
                         capture_output=True)
    if run.returncode != 0:                      # e.g. not a usable git checkout: fall back to the source folders
        print(f"[build] git ls-files failed in {repo}: {run.stderr.decode().strip()[:300]}; walking src/configs/scripts")
        for sub in ("src", "configs", "scripts"):
            yield from walk(os.path.join(repo, sub))
        return
    out = run.stdout.decode().split("\0")
    for rel in out:
        if not rel or rel.startswith(exclude_prefixes):
            continue
        p = os.path.join(repo, rel)
        if os.path.isfile(p) and not secret(p) and os.path.getsize(p) <= max_bytes:
            yield p


def traced(trace_dir: Path):
    files, failed = set(), []
    for t in sorted(trace_dir.glob("*.json")):
        value = json.loads(t.read_text())
        if value.get("returncode") not in (0, None):
            failed.append(t.name)
        files.update(value["files"])
    return files, failed


def cmd_build(args):
    mig = Path(args.mig)
    traces, failed = traced(mig / "traces")
    if failed and not args.allow_failed_traces:
        raise SystemExit(f"traces with a non-zero exit: {failed} (fix them, or --allow-failed-traces)")
    trace_logical = {logical(p) for p in traces if os.path.isfile(p)}
    groups, owner = {}, {}

    def add(group, paths):
        for p in paths:
            p = logical(p)
            if p in owner or secret(p):
                continue
            owner[p] = group
            groups.setdefault(group, []).append(p)

    stage_dir = str(mig / "stage")
    add("dense_code", walk(DENSE_CODE))
    add("restore_traced", [p for p in trace_logical if p.startswith(RESTORE + "/")])
    add("fastwam_repo", git_files(FW))
    add("dense_output", walk(DENSE_OUT, keep=lambda p: "optim_states" not in os.path.basename(p) or logical(p) in trace_logical))
    res = sorted(p for p in trace_logical if p.startswith(FW + "/resources/"))
    siblings = set(res)
    for p in res:                                # configs/tokenizer files next to every weight the code read
        d = os.path.dirname(p)
        siblings.update(os.path.join(d, f) for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)))
    add("resources", sorted(siblings))
    add("fastwam_traced", [p for p in trace_logical if p.startswith(FW + "/")])

    def keep_output(p):
        parts = p.split("/")
        if "checkpoints" in parts and p.endswith(".pt"):
            return os.path.basename(p) == FINAL_CHECKPOINT or p in trace_logical
        return True
    add("memory2_outputs", walk(MEM2 + "/outputs", skip_dirs=(FEATURES, stage_dir, str(mig / "probe_train"),
                                                              str(mig / "probe_pr")), keep=keep_output))
    add("memory2_traced", [p for p in trace_logical if p.startswith(MEM2 + "/")
                           and not p.startswith(MEM2 + "/src/") and not p.startswith(FEATURES)])
    if "features" not in args.skip:
        add("features", walk(FEATURES))
    if "simulator" not in args.skip:
        add("simulator", walk(FW + "/resources/RMBench", skip_dirs=[FW + "/resources/RMBench/" + d for d in ("data", "datasets", "build")]))
        add("simulator", walk(FW + "/resources/PyTorch3D", skip_dirs=[FW + "/resources/PyTorch3D/build"]))
    add("hf_cache", [p for p in trace_logical if p.startswith(HF_CACHE + "/")])
    for pattern in args.exclude:
        for g in groups:
            groups[g] = [p for p in groups[g] if not fnmatch.fnmatch(p, pattern)]
    other = sorted(p for p in trace_logical if p not in owner and not p.startswith(SYSTEM) and "site-packages" not in p
                   and "dist-packages" not in p and not p.startswith((MEM2 + "/src/", FEATURES)) and not secret(p))
    for g in args.skip:
        groups.pop(g, None)

    files, total = [], 0
    print(f"{'group':<18}{'files':>8}{'size':>14}")
    for g, paths in groups.items():
        size = 0
        for p in paths:
            s = os.path.getsize(p)
            if s > MAX_HF_FILE:
                raise SystemExit(f"{p}: {gib(s)} > 45 GiB single-file limit; split it or --exclude it")
            size += s
            files.append({"path": p, "real": os.path.realpath(p), "size": s, "group": g})
        total += size
        print(f"{g:<18}{len(paths):>8}{gib(size):>14}")
    print(f"{'TOTAL':<18}{len(files):>8}{gib(total):>14}")
    big = {}
    for f in files:
        top = "/".join(f["path"].split("/")[:6])
        big[top] = big.get(top, 0) + f["size"]
    print("\nlargest directories (depth 5):")
    for k, v in sorted(big.items(), key=lambda x: -x[1])[:15]:
        print(f"  {gib(v)}  {k}")
    if other:
        print(f"\nWARNING {len(other)} traced files outside the known roots are NOT included (first 30):")
        for p in other[:30]:
            print("  ", p)
    if failed:
        print(f"\nWARNING traces with non-zero exit: {failed}")
    draft = {"version": 1, "logical_roots": list(LOGICAL_ROOTS), "real_roots": {lr: rr for rr, lr in REAL_ROOTS},
             "skipped_groups": list(args.skip), "excluded": list(args.exclude), "untracked_traced": other,
             "total_bytes": total, "files": files}
    (mig / "MANIFEST.draft.json").write_text(json.dumps(draft, indent=1))
    print(f"\n[build] {mig / 'MANIFEST.draft.json'}")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(64 * 2 ** 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd_stage(args):
    mig = Path(args.mig)
    draft = json.loads((mig / "MANIFEST.draft.json").read_text())
    cache_path = mig / "hash_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    def key(f):
        st = os.stat(f["real"])
        return f"{f['real']}|{st.st_size}|{st.st_mtime_ns}"

    todo = [f for f in draft["files"] if key(f) not in cache]
    print(f"[stage] hashing {len(todo)} of {len(draft['files'])} files ({gib(sum(f['size'] for f in todo))})", flush=True)
    done = 0
    with cf.ThreadPoolExecutor(args.workers) as pool:
        for f, digest in zip(todo, pool.map(lambda f: sha256(f["real"]), todo)):
            cache[key(f)] = digest
            done += 1
            if done % 200 == 0:
                cache_path.write_text(json.dumps(cache))
                print(f"[stage] hashed {done}/{len(todo)}", flush=True)
    cache_path.write_text(json.dumps(cache))
    stage = mig / "stage"
    linked = 0
    for f in draft["files"]:
        f["sha256"] = cache[key(f)]
        f["stage_path"] = stage_path(f["path"])
        dst = stage / f["stage_path"]
        if dst.exists() or dst.is_symlink():
            if dst.exists() and os.path.samefile(dst, f["real"]):
                continue
            dst.unlink()
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(f["real"], dst)
        except OSError:
            os.symlink(f["real"], dst)
        linked += 1
    manifest = {k: v for k, v in draft.items() if k != "files"}
    manifest["files"] = [{k: f[k] for k in ("path", "stage_path", "size", "sha256", "group")} for f in draft["files"]]
    (stage / "MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    print(f"[stage] {linked} new links; {stage / 'MANIFEST.json'}; total {gib(manifest['total_bytes'])}")


def cmd_upload(args):
    from huggingface_hub import HfApi
    stage = Path(args.mig) / "stage"
    if not (stage / "MANIFEST.json").exists():
        raise SystemExit("run stage first")
    api = HfApi()
    print("[upload] as", api.whoami()["name"], "->", args.repo, flush=True)
    api.create_repo(args.repo, repo_type="model", private=True, exist_ok=True)
    api.upload_large_folder(repo_id=args.repo, folder_path=str(stage), repo_type="model", private=True,
                            num_workers=args.workers)
    remote = {x.path: getattr(x, "lfs", None) for x in api.list_repo_tree(args.repo, recursive=True, repo_type="model")
              if hasattr(x, "size")}
    manifest = json.loads((stage / "MANIFEST.json").read_text())
    missing = [f["path"] for f in manifest["files"] if f["stage_path"] not in remote]
    print(f"[upload] remote files {len(remote)}; manifest files missing remotely: {len(missing)}")
    for p in missing[:20]:
        print("  missing", p)
    if missing:
        raise SystemExit(1)
    print("[upload] complete")


def cmd_verify(args):
    manifest = json.loads(Path(args.manifest).read_text())
    root = Path(args.root)
    bad = []

    def check(f):
        p = root / f["stage_path"]
        if not p.is_file():
            return f["path"], "missing"
        if p.stat().st_size != f["size"]:
            return f["path"], f"size {p.stat().st_size} != {f['size']}"
        if not args.no_hash and sha256(str(p)) != f["sha256"]:
            return f["path"], "sha256 mismatch"
        return None
    with cf.ThreadPoolExecutor(args.workers) as pool:
        for i, r in enumerate(pool.map(check, manifest["files"]), 1):
            if r:
                bad.append(r)
            if i % 500 == 0:
                print(f"[verify] {i}/{len(manifest['files'])}", flush=True)
    for p, why in bad[:50]:
        print("  BAD", why, p)
    print(f"[verify] {len(manifest['files']) - len(bad)}/{len(manifest['files'])} OK, {gib(manifest['total_bytes'])}")
    sys.exit(1 if bad else 0)


def cmd_compare(args):
    a = json.loads(Path(args.a).read_text())["overall"]
    b = json.loads(Path(args.b).read_text())["overall"]
    worst = 0.0
    print(f"{'metric':<34}{'A100':>12}{'H100':>12}{'rel':>9}")
    for k in sorted(set(a) & set(b)):
        if not isinstance(a[k], (int, float)):
            continue
        rel = abs(a[k] - b[k]) / max(abs(a[k]), 1e-12)
        if "arm_rmse" in k:
            worst = max(worst, rel)
        print(f"{k:<34}{a[k]:>12.5f}{b[k]:>12.5f}{rel:>9.2%}")
    print(f"[compare] worst arm-RMSE relative difference {worst:.2%} (tolerance {args.tol:.0%})")
    sys.exit(0 if worst <= args.tol else 1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--mig", required=True)
    b.add_argument("--skip", nargs="*", default=[], help="groups to leave out, e.g. features simulator")
    b.add_argument("--exclude", nargs="*", default=[], help="fnmatch patterns on logical paths")
    b.add_argument("--allow-failed-traces", action="store_true")
    s = sub.add_parser("stage")
    s.add_argument("--mig", required=True)
    s.add_argument("--workers", type=int, default=8)
    u = sub.add_parser("upload")
    u.add_argument("--mig", required=True)
    u.add_argument("--repo", required=True)
    u.add_argument("--workers", type=int, default=8)
    v = sub.add_parser("verify")
    v.add_argument("--manifest", required=True)
    v.add_argument("--root", required=True, help="download folder (contains payload/)")
    v.add_argument("--workers", type=int, default=16)
    v.add_argument("--no-hash", action="store_true")
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    c.add_argument("--tol", type=float, default=0.03)
    args = p.parse_args()
    {"build": cmd_build, "stage": cmd_stage, "upload": cmd_upload, "verify": cmd_verify, "compare": cmd_compare}[args.cmd](args)


if __name__ == "__main__":
    main()
