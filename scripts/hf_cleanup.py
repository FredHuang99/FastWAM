"""Hugging Face storage clean-up for hhyfred's backup repos.

    python3 hf_cleanup.py inventory            # step 1, read-only: every model / dataset repo of the account
    python3 hf_cleanup.py prune --repo R --keep PREFIX [--keep PREFIX ...] [--execute]
                                               # step 2: keep only PREFIX... at HEAD, purge unneeded LFS objects
    python3 hf_cleanup.py delete-repo --repo R [--execute]
    (prune / delete-repo are dry runs unless --execute, and --execute asks to type the repo name)

Nothing is deleted. Output in ~/hf_cleanup/:
    REPORT_<time>.md                     what is stored where, pointers, proposed plan (send this file back)
    inventory_<owner>__<repo>_<time>.json   every file at HEAD + every LFS object (incl. history) + the plan

How the plan is built ("restore from the latest state on HF"):
  * pointer files (LATEST*.json, *_READY.json) say what the latest state is. KEEP every pointer and what it
    references: a ready / migration package (its folder), or a training checkpoint (LATEST_COMPLETE.json: the pointed
    checkpoint folder + every file listed in its backup_manifest.json, at the pinned revision);
  * resources/** (base weights, RMBench assets and envs, prepared data, PyTorch3D, download_lock.json) are inputs: KEEP;
  * SAFE delete: sibling folders a pointer has superseded (older checkpoints of the same run, older ready / migration
    snapshots) and LFS objects that only old commits reference (overwritten or deleted files still use storage);
  * REVIEW: everything else (other runs, posttrain / grasp evidence packages, top-level code copies, ...): decided by
    hand from this report before step 2.
Pinned revisions in the kept pointers stay valid: step 2 deletes LFS objects without rewriting git history.
"""
import argparse
import getpass
import json
import os
import re
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path

try:
    import huggingface_hub as hub
    from huggingface_hub import HfApi, hf_hub_download
except ImportError:
    sys.exit("huggingface_hub is missing: python3 -m pip install -U huggingface_hub")

OUT = Path.home() / "hf_cleanup"
STAMP = time.strftime("%Y%m%d_%H%M%S")
HEX40 = re.compile(r"[0-9a-f]{40}")
POINTER = re.compile(r"(^LATEST.*\.json$)|(_READY\.json$)")


def gib(n):
    return f"{(n or 0) / 2**30:,.1f} GiB"


def login(api):
    """Use the cached token; otherwise ask for one (hidden input) and cache it like `hf auth login`."""
    if hub.get_token() is None:
        print("No Hugging Face token cached. Paste a token with WRITE access (https://huggingface.co/settings/tokens);"
              " the input is hidden.")
        token = getpass.getpass("HF token: ").strip()
        hub.login(token=token, add_to_git_credential=False)
    return api.whoami()["name"]


def lfs_sha(item):
    lfs = getattr(item, "lfs", None)
    if lfs is None:
        return None
    return getattr(lfs, "sha256", None) or (lfs.get("sha256") if isinstance(lfs, dict) else None)


def tree(api, repo, kind, revision):
    files = {}
    for item in api.list_repo_tree(repo, repo_type=kind, revision=revision, recursive=True):
        if hasattr(item, "size") and not hasattr(item, "tree_id"):
            files[item.path] = {"size": int(item.size or 0), "sha": lfs_sha(item), "xet": getattr(item, "xet_hash", None)}
    return files


def read_json(api, repo, kind, path, revision, cache):
    try:
        return json.loads(Path(hf_hub_download(repo, path, revision=revision, repo_type=kind, cache_dir=cache)).read_text())
    except Exception as error:                         # noqa: BLE001
        return {"_error": repr(error)[:300]}


def strings(value):
    if isinstance(value, dict):
        for k, v in value.items():
            yield from ((k2 or k, s) for k2, s in strings(v))
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)
    elif isinstance(value, str):
        yield None, value


def under(path, prefix):
    return path == prefix.rstrip("/") or path.startswith(prefix.rstrip("/") + "/")


def analyse(api, repo, kind, cache):
    info = api.repo_info(repo, repo_type=kind)
    used = None
    try:
        used = getattr(api.repo_info(repo, repo_type=kind, expand=["usedStorage"]), "used_storage", None)
    except Exception:                                  # noqa: BLE001
        pass
    print(f"[{repo}] HEAD {info.sha[:10]}: listing files ...", flush=True)
    head = tree(api, repo, kind, info.sha)
    try:
        commits = list(api.list_repo_commits(repo, repo_type=kind))
    except Exception as error:                         # noqa: BLE001
        commits, _ = [], print(f"  ! list_repo_commits failed: {error!r}")
    print(f"[{repo}] {len(head)} files at HEAD ({gib(sum(f['size'] for f in head.values()))}); LFS objects ...", flush=True)
    lfs, lfs_error = [], None
    try:
        for x in api.list_lfs_files(repo, repo_type=kind):
            lfs.append({"oid": getattr(x, "oid", None), "file_oid": getattr(x, "file_oid", None),
                        "filename": getattr(x, "filename", None), "size": int(getattr(x, "size", 0) or 0),
                        "pushed_at": str(getattr(x, "pushed_at", "")), "ref": getattr(x, "ref", None)})
    except Exception as error:                         # noqa: BLE001
        lfs_error = repr(error)[:300]

    keep, safe, why = {}, {}, {}
    pinned = defaultdict(set)                          # revision -> paths that must stay downloadable there
    families = []                                      # (family folder, kept item folder, pointer)
    pointers = {}
    for path, f in sorted(head.items()):
        if not POINTER.search(path.rsplit("/", 1)[-1]) or f["size"] > 2**20:
            continue
        content = read_json(api, repo, kind, path, info.sha, cache)
        pointers[path] = content
        keep[path], why[path] = "pointer", "pointer"
        refs, revision = set(), None
        for key, value in strings(content):
            if HEX40.fullmatch(value) and key and "revision" in key.lower() and revision is None:
                revision = value
            elif value in head or ("/" in value.strip("/") and any(p.startswith(value.rstrip("/") + "/") for p in head)):
                refs.add(value)
        if isinstance(content, dict):
            for key in ("checkpoint_revision", "package_revision", "revision"):
                if isinstance(content.get(key), str) and HEX40.fullmatch(content[key]):
                    revision = content[key]
                    break
        if path.endswith("LATEST_COMPLETE.json") and isinstance(content, dict) and content.get("directory"):
            run = path.rsplit("/", 1)[0]
            ck = f"{run}/checkpoints/{content['directory']}"
            refs.add(ck)
            families.append((f"{run}/checkpoints", ck, path))
            if revision:
                manifest = read_json(api, repo, kind, f"{ck}/backup_manifest.json", revision, cache)
                for remote in (manifest.get("files") or {}):
                    refs.add(f"{run}/{remote}")
        if isinstance(content, dict) and isinstance(content.get("package"), str):
            item = content["package"].rsplit("/", 1)[0]
            refs.add(item)
            if "/" in item:
                families.append((item.rsplit("/", 1)[0], item, path))
        for ref in refs:
            for p in head:
                if under(p, ref) and p not in keep:
                    keep[p], why[p] = "referenced", f"referenced by {path}"
            if revision:
                pinned[revision].add(ref)
    for p in head:
        if p not in keep and p.startswith("resources/"):
            keep[p], why[p] = "resource", "input resource"
    for family, item, pointer in families:
        for p in head:
            if p in keep or not under(p, family) or under(p, item) or "/" not in p[len(family) + 1:]:
                continue
            safe[p], why[p] = "superseded", f"superseded by {pointer} (keeps {item})"
    review = {p: "review" for p in head if p not in keep and p not in safe}

    # pinned revisions: the exact LFS objects a kept pointer downloads must survive
    pinned_sha, pinned_rows, missing = set(), [], []
    for revision, refs in pinned.items():
        got = files_at(api, repo, kind, revision, refs)
        pinned_sha |= {f["sha"] for f in got.values() if f["sha"]}
        pinned_rows.append({"revision": revision, "refs": sorted(refs)[:20], "files": len(got),
                            "bytes": sum(f["size"] for f in got.values())})
        missing += [f"{ref} (pinned {revision[:10]}: not found there)" for ref in refs
                    if not any(under(p, ref) for p in got)]
    for path, content in pointers.items():
        if isinstance(content, dict) and isinstance(content.get("package"), str) and content["package"] not in head:
            missing.append(f"{content['package']} (pointed by {path}): not at HEAD")

    def ids(x):
        return {x["oid"], x["file_oid"]} - {None}
    sha_of = lambda paths: {head[p]["sha"] for p in paths if head[p]["sha"]}   # noqa: E731
    keep_sha, safe_sha, review_sha = sha_of(keep), sha_of(safe), sha_of(review)
    protected_now = sha_of(head) | pinned_sha
    history_only = [x for x in lfs if not ids(x) & protected_now]
    listed = set().union(*(ids(x) for x in lfs)) if lfs else set()
    head_lfs = sha_of(head)
    after_safe = [x for x in lfs if not ids(x) & (keep_sha | review_sha | pinned_sha)]
    after_all = [x for x in lfs if not ids(x) & (keep_sha | pinned_sha)]
    size = lambda paths: sum(head[p]["size"] for p in paths)                  # noqa: E731
    return {"repo": repo, "type": kind, "private": info.private, "head": info.sha, "used_storage": used,
            "commits": len(commits), "first_commit": str(commits[-1].created_at) if commits else None,
            "last_commit": str(commits[0].created_at) if commits else None,
            "head_bytes": size(head), "lfs_bytes": sum(x["size"] for x in lfs), "lfs_count": len(lfs), "lfs_error": lfs_error,
            "keep_bytes": size(keep), "safe_bytes": size(safe), "review_bytes": size(review),
            "history_only_bytes": sum(x["size"] for x in history_only),
            "lfs_free_after_safe": sum(x["size"] for x in after_safe),
            "lfs_free_after_safe_and_review": sum(x["size"] for x in after_all),
            "pointers": pointers, "pinned": pinned_rows, "missing": missing,
            "head_lfs_files": len(head_lfs), "head_lfs_found_in_listing": len(head_lfs & listed),
            "head_xet_only": sum(1 for f in head.values() if f["xet"] and not f["sha"]),
            "files": {p: {**head[p], "class": (keep.get(p) or safe.get(p) or "review"), "why": why.get(p, "")}
                      for p in sorted(head)},
            "lfs": lfs, "history_only": history_only, "lfs_sample": lfs[:3]}


def files_at(api, repo, kind, revision, refs):
    """{path: file} at `revision` under each referenced path (a file or a folder)."""
    try:
        files = tree(api, repo, kind, revision)
    except Exception as error:                         # noqa: BLE001
        print(f"  ! tree at {revision[:10]} failed: {error!r}")
        return {}
    return {p: f for p, f in files.items() if any(under(p, r) for r in refs)}


def prefixes(files, depth, cls=None):
    agg = defaultdict(lambda: [0, 0])
    for p, f in files.items():
        if cls and f["class"] not in cls:
            continue
        key = "/".join(p.split("/")[:depth]) + ("/" if p.count("/") >= depth else "")
        agg[key][0] += f["size"]
        agg[key][1] += 1
    return sorted(agg.items(), key=lambda kv: -kv[1][0])


def report(results, user):
    lines = [f"# HF inventory {STAMP} (account {user}, huggingface_hub {hub.__version__})", "",
             "| repo | type | storage used | HEAD | all LFS (incl. history) | history-only LFS | keep | safe delete | review |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['repo']} | {r['type']} | {gib(r['used_storage']) if r['used_storage'] else '?'} | "
                     f"{gib(r['head_bytes'])} | {gib(r['lfs_bytes'])} ({r['lfs_count']}) | {gib(r['history_only_bytes'])} | "
                     f"{gib(r['keep_bytes'])} | {gib(r['safe_bytes'])} | {gib(r['review_bytes'])} |")
    for r in results:
        lines += ["", f"## {r['repo']} ({r['type']}, private={r['private']})", "",
                  f"HEAD {r['head']}; commits {r['commits']} ({r['first_commit']} .. {r['last_commit']}); "
                  f"LFS listing error: {r['lfs_error']}; HEAD LFS files {r['head_lfs_files']}, found in the LFS listing "
                  f"{r['head_lfs_found_in_listing']} (must be equal, else the plan's LFS numbers are wrong); "
                  f"HEAD files with Xet hash only {r['head_xet_only']}",
                  f"Referenced but missing: {r['missing'] or 'none'}",
                  f"Storage freed: history-only LFS {gib(r['history_only_bytes'])}; + SAFE deletions "
                  f"{gib(r['lfs_free_after_safe'])}; + SAFE and every REVIEW item {gib(r['lfs_free_after_safe_and_review'])}.",
                  "", "### HEAD by folder (depth 1 / 2 / 3)", "", "| folder | size | files |", "|---|---|---|"]
        for depth in (1, 2, 3):
            for key, (b, n) in prefixes(r["files"], depth)[:25]:
                if b >= 2**20 or depth == 1:
                    lines.append(f"| {key} | {gib(b)} | {n} |")
        lines += ["", "### Pointers (latest state)", ""]
        for path, content in r["pointers"].items():
            lines += [f"- `{path}`", "```json", json.dumps(content, indent=1)[:1500], "```"]
        lines += ["", f"Pinned revisions checked: {json.dumps(r['pinned'])[:1500]}", ""]
        for title, cls in (("KEEP", ("pointer", "referenced", "resource")), ("SAFE delete (superseded)", ("superseded",)),
                           ("REVIEW (not referenced by any pointer, not resources/)", ("review",))):
            lines += [f"### {title}", "", "| folder | size | files |", "|---|---|---|"]
            for key, (b, n) in prefixes(r["files"], 3, cls)[:40]:
                lines.append(f"| {key} | {gib(b)} | {n} |")
            lines.append("")
        lines += ["### History-only LFS objects (largest 40)", "", "| filename (as pushed) | size | pushed |", "|---|---|---|"]
        for x in sorted(r["history_only"], key=lambda x: -x["size"])[:40]:
            lines.append(f"| {x['filename']} | {gib(x['size'])} | {x['pushed_at'][:16]} |")
        agg = defaultdict(lambda: [0, 0])
        for x in r["history_only"]:
            key = "/".join(str(x["filename"]).split("/")[:2])
            agg[key][0] += x["size"]
            agg[key][1] += 1
        lines += ["", "History-only LFS by folder:", "", "| folder | size | objects |", "|---|---|---|"]
        lines += [f"| {k} | {gib(b)} | {n} |" for k, (b, n) in sorted(agg.items(), key=lambda kv: -kv[1][0])[:25]]
        lines += ["", f"LFS object sample (field check): {json.dumps(r['lfs_sample'], default=str)[:800]}"]
    return "\n".join(lines) + "\n"


def cmd_inventory(args):
    api = HfApi()
    user = login(api)
    OUT.mkdir(parents=True, exist_ok=True)
    repos = [(args.repo, args.type)] if args.repo else \
        [(m.id, "model") for m in api.list_models(author=user)] + [(d.id, "dataset") for d in api.list_datasets(author=user)]
    spaces = [] if args.repo else [s.id for s in api.list_spaces(author=user)]
    print(f"account {user}: {len(repos)} model/dataset repos {[r for r, _ in repos]}; spaces {spaces}", flush=True)
    results = []
    with tempfile.TemporaryDirectory() as cache:
        for repo, kind in repos:
            try:
                r = analyse(api, repo, kind, cache)
            except Exception as error:                 # noqa: BLE001
                print(f"[{repo}] FAILED: {error!r}")
                continue
            path = OUT / f"inventory_{repo.replace('/', '__')}_{STAMP}.json"
            path.write_text(json.dumps(r, indent=1, default=str))
            print(f"[{repo}] HEAD {gib(r['head_bytes'])}, LFS {gib(r['lfs_bytes'])}, history-only {gib(r['history_only_bytes'])}; "
                  f"keep {gib(r['keep_bytes'])}, safe {gib(r['safe_bytes'])}, review {gib(r['review_bytes'])} -> {path}",
                  flush=True)
            results.append(r)
    rep = OUT / f"REPORT_{STAMP}.md"
    rep.write_text(report(results, user) + (f"\nSpaces (not analysed): {spaces}\n" if spaces else ""))
    print(f"\nREPORT: {rep}  (nothing was deleted)")


# ============================================================================ step 2: apply
def confirm(text, word):
    print(text)
    answer = input(f"Type {word} to go ahead (anything else stops): ").strip()
    if answer != word:
        sys.exit("stopped: nothing changed")


def cmd_prune(args):
    """Keep only the --keep prefixes of one repo at HEAD, then permanently delete every LFS object that neither the
    new HEAD nor a kept pointer's pinned revision needs. Git history is NOT rewritten (pinned revisions stay valid)."""
    import inspect
    from huggingface_hub import CommitOperationDelete
    api = HfApi()
    purge_api = getattr(api, "permanently_delete_lfs_files", None)
    if purge_api is None or "rewrite_history" not in inspect.signature(purge_api).parameters:
        sys.exit("this huggingface_hub cannot purge LFS objects without rewriting history: pip install -U huggingface_hub")
    login(api)
    repo, kind, keeps = args.repo, args.type, [k.rstrip("/") for k in args.keep]
    info = api.repo_info(repo, repo_type=kind)
    head = tree(api, repo, kind, info.sha)
    kept = {p for p in head if any(under(p, k) for k in keeps)}
    drop = sorted(set(head) - kept)
    missing = [k for k in keeps if not any(under(p, k) for p in head)]
    if missing:
        sys.exit(f"keep prefixes not found at HEAD (typo?): {missing}; nothing changed")
    # pinned revisions named by kept pointers: their files under the kept prefixes must stay downloadable
    protect = {f["sha"] for p, f in head.items() if p in kept and f["sha"]}
    with tempfile.TemporaryDirectory() as cache:
        for p in sorted(kept):
            if p.endswith(".json") and head[p]["size"] < 2**20:
                content = read_json(api, repo, kind, p, info.sha, cache)
                rev = content.get("revision") if isinstance(content, dict) else None
                if isinstance(rev, str) and HEX40.fullmatch(rev):
                    at = files_at(api, repo, kind, rev, keeps)
                    protect |= {f["sha"] for f in at.values() if f["sha"]}
                    print(f"pointer {p}: pinned revision {rev[:10]} -> {len(at)} kept files protected")
    lfs = list(api.list_lfs_files(repo, repo_type=kind))
    ident = lambda x: {getattr(x, "oid", None), getattr(x, "file_oid", None)} - {None}   # noqa: E731
    purge = [x for x in lfs if not ident(x) & protect]
    print(f"\n{repo}: HEAD {len(head)} files {gib(sum(f['size'] for f in head.values()))}")
    print(f"  keep   {len(kept)} files {gib(sum(head[p]['size'] for p in kept))} under {keeps}")
    print(f"  delete {len(drop)} files {gib(sum(head[p]['size'] for p in drop))} from HEAD (one commit per 1000 files)")
    agg = defaultdict(lambda: [0, 0])
    for p in drop:
        key = "/".join(p.split("/")[:2])
        agg[key][0] += head[p]["size"]
        agg[key][1] += 1
    for key, (b, n) in sorted(agg.items(), key=lambda kv: -kv[1][0]):
        print(f"      {gib(b):>12}  {n:5d} files  {key}")
    print(f"  LFS objects: {len(lfs)} ({gib(sum(int(x.size) for x in lfs))}); permanently delete {len(purge)} "
          f"({gib(sum(int(x.size) for x in purge))}); keep {len(lfs) - len(purge)}")
    if not args.execute:
        print("\nDRY RUN: nothing changed (add --execute to do it)")
        return
    confirm(f"\nThis permanently deletes the files and LFS objects above from {repo}.", repo.split("/")[-1])
    for start in range(0, len(drop), 1000):
        chunk = drop[start:start + 1000]
        commit = api.create_commit(repo, repo_type=kind, operations=[CommitOperationDelete(path_in_repo=p) for p in chunk],
                                   commit_message=f"clean-up: keep only {keeps} ({start + 1}-{start + len(chunk)})")
        print(f"  deleted {start + len(chunk)}/{len(drop)} files (commit {commit.oid[:10]})", flush=True)
    new_head = tree(api, repo, kind, api.repo_info(repo, repo_type=kind).sha)
    if set(new_head) != kept:
        sys.exit(f"HEAD after the commits differs from the plan ({len(new_head)} vs {len(kept)} files): LFS purge NOT done")
    protect |= {f["sha"] for f in new_head.values() if f["sha"]}
    purge = [x for x in api.list_lfs_files(repo, repo_type=kind) if not ident(x) & protect]
    for start in range(0, len(purge), 100):
        api.permanently_delete_lfs_files(repo, purge[start:start + 100], rewrite_history=False, repo_type=kind)
        print(f"  purged {min(start + 100, len(purge))}/{len(purge)} LFS objects", flush=True)
    left = list(api.list_lfs_files(repo, repo_type=kind))
    print(f"\nDONE {repo}: HEAD {len(new_head)} files {gib(sum(f['size'] for f in new_head.values()))}; "
          f"LFS left {len(left)} ({gib(sum(int(x.size) for x in left))}). The storage number on the website can lag.")


def cmd_delete_repo(args):
    api = HfApi()
    login(api)
    info = api.repo_info(args.repo, repo_type=args.type)
    size = sum(f["size"] for f in tree(api, args.repo, args.type, info.sha).values())
    print(f"{args.repo}: {gib(size)} at HEAD")
    if not args.execute:
        print("DRY RUN: nothing changed (add --execute to delete the whole repo)")
        return
    confirm(f"This permanently deletes the whole repo {args.repo}.", args.repo.split("/")[-1])
    api.delete_repo(args.repo, repo_type=args.type)
    print(f"DONE: {args.repo} deleted")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("inventory")
    i.add_argument("--repo")
    i.add_argument("--type", default="model", choices=("model", "dataset"))
    pr = sub.add_parser("prune")
    pr.add_argument("--repo", required=True)
    pr.add_argument("--type", default="model", choices=("model", "dataset"))
    pr.add_argument("--keep", action="append", required=True, help="path prefix to keep (repeat)")
    pr.add_argument("--execute", action="store_true")
    d = sub.add_parser("delete-repo")
    d.add_argument("--repo", required=True)
    d.add_argument("--type", default="model", choices=("model", "dataset"))
    d.add_argument("--execute", action="store_true")
    args = ap.parse_args()
    {"inventory": cmd_inventory, "prune": cmd_prune, "delete-repo": cmd_delete_repo}[args.cmd](args)


if __name__ == "__main__":
    main()
