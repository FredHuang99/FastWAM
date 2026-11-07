"""press_button pilot, step 1 (week plan v6 2.5): RMBench demo_clean of one task at the pinned dataset revision.

Downloads data/<task>/demo_clean.zip of TianxingChen/RMBench at the revision in /workspace/FastWAM/resources/
download_lock.json (5d8ff210...), into OUR folder:
    outputs/memory_v2/press/demo_clean/<task>/aloha_agilex/{data,video,instruction}/...
    outputs/memory_v2/press/demo_clean/<task>/DOWNLOAD.json   revision, zip sha256 (checked against the hub's LFS
                                                             sha256), every hdf5's sha256, counts
Codex's resources/RMBench/data and the two-task dense cache are not touched. Nothing from the archive is executed.
Then (also with --inspect-only) it describes the data: hdf5 layout of episode 0 next to a put_back episode, episode
lengths, the instruction file, the datasets that could locate the presses (end-effector poses), disk use.
Writes its own report: outputs/memory_v2/report/PRESS_FETCH_<time>.txt

    /opt/mwam/bin/python scripts/memory_v2/press/fetch.py [--task press_button] [--inspect-only] [--keep-zip]

11-07 (plan v8 D7-3, the other RMBench tasks; same folder layout, same checks):
    --list                 every data/<task>/demo_clean.zip at the pinned revision (size, downloaded here or not); nothing
                           is downloaded
    --task A B ...         several tasks in a row; a task that fails is reported and the next one still runs (exit code 1
                           if any failed)
    --task all             every task on the hub except put_back_block / swap_blocks (those two live in
                           resources/RMBench/data/demo_clean); tasks already downloaded are only inspected
    Report: RMB_FETCH_<time>.txt when it is not the single press_button task.
"""
import argparse
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile

REPO_ID = "TianxingChen/RMBench"
LOCK = Path("/workspace/FastWAM/resources/download_lock.json")
PINNED = "5d8ff21038fba32ea549e9eee8497aaba9aab5cf"
OUT = Path(os.environ.get("MEMV2_OUT", "/workspace/FastWAM-memory2/outputs/memory_v2")) / "press"
PUT_EP0 = Path("/workspace/FastWAM/resources/RMBench/data/demo_clean/put_back_block/aloha_agilex/data/episode_0000000.hdf5")
PYTHONS = ["/opt/mwam/bin/python", "/opt/rmbench-fused-env/bin/python", "/opt/rmbench-a100-env/bin/python", "python3"]
BJ = timezone(timedelta(hours=8))
LINES = []


def say(*parts):
    line = " ".join(str(p) for p in parts)
    print(line, flush=True)
    LINES.append(line)


def sha256(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                return h.hexdigest()
            h.update(b)


def pinned_revision():
    try:
        repos = json.loads(LOCK.read_text()).get("repositories") or {}
        rev = repos.get("dataset:TianxingChen/RMBench")
        if rev and rev != PINNED:
            say(f"WARNING lock file revision {rev} differs from the one this script was written for ({PINNED}); using the lock")
        return rev or PINNED
    except (OSError, ValueError):
        return PINNED


SKIP_ALL = ("put_back_block", "swap_blocks")


def hub_tasks(rev):
    """[(task, zip bytes)] for every data/<task>/demo_clean.zip at the revision."""
    from huggingface_hub import HfApi
    api = HfApi()
    folders = sorted(e.path.split("/", 1)[1] for e in api.list_repo_tree(REPO_ID, path_in_repo="data", repo_type="dataset",
                                                                           revision=rev, recursive=False)
                     if getattr(e, "tree_id", None) is not None or not hasattr(e, "size"))
    names = [f"data/{t}/demo_clean.zip" for t in folders]
    info = {i.path: int(getattr(i, "size", 0) or 0)
            for i in api.get_paths_info(REPO_ID, names, repo_type="dataset", revision=rev)} if names else {}
    return [(t, info[f"data/{t}/demo_clean.zip"]) for t in folders if f"data/{t}/demo_clean.zip" in info]


def download(task, rev, keep_zip):
    from huggingface_hub import HfApi, hf_hub_download
    top = OUT / "demo_clean" / task
    dest = top / "aloha_agilex"
    name = f"data/{task}/demo_clean.zip"
    info = HfApi().get_paths_info(REPO_ID, [name], repo_type="dataset", revision=rev)
    if not info:
        raise SystemExit(f"{name} not found at revision {rev}")
    size = int(getattr(info[0], "size", 0) or 0)
    lfs = getattr(info[0], "lfs", None)
    lfs_sha = (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else None
    OUT.mkdir(parents=True, exist_ok=True)
    free = shutil.disk_usage(OUT).free
    say(f"hub: {name} @ {rev[:12]}: {size / 1e9:.2f} GB (LFS sha256 {lfs_sha}); free here {free / 1e12:.2f} TB")
    reserve = float(os.environ.get("PRESS_RESERVE_GB", "50")) * 1e9
    if size and free < 3 * size + reserve:
        raise SystemExit(f"not enough disk for zip + extraction + {reserve / 1e9:.0f} GB reserve")
    t0 = time.time()
    zpath = Path(hf_hub_download(REPO_ID, name, repo_type="dataset", revision=rev, local_dir=str(OUT / "download")))
    say(f"downloaded {zpath} in {(time.time() - t0) / 60:.1f} min")
    zsha = sha256(zpath)
    if lfs_sha and zsha != lfs_sha:
        raise SystemExit(f"zip sha256 {zsha} != hub LFS sha256 {lfs_sha}: corrupted download, nothing extracted")
    stage = OUT / f"extract_{task}.partial"
    shutil.rmtree(stage, ignore_errors=True)
    with ZipFile(zpath) as z:
        names = z.namelist()
        z.extractall(stage)                         # zipfile drops absolute paths and '..' parts
    say(f"zip: {len(names)} entries; first: {names[:6]}")
    hdf5 = sorted(stage.rglob("*.hdf5"))
    parents = sorted({h.parent for h in hdf5})
    if len(parents) != 1 or parents[0].name != "data":
        raise SystemExit(f"unexpected layout: hdf5 under {[str(p.relative_to(stage)) for p in parents][:5]} "
                         f"(left in {stage} for a look)")
    root = parents[0].parent                       # .../aloha_agilex (data/, video/, instruction/)
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    root.rename(dest)
    shutil.rmtree(stage, ignore_errors=True)
    files = sorted((dest / "data").glob("*.hdf5"))
    marker = {"repo": REPO_ID, "revision": rev, "file": name, "zip_bytes": zpath.stat().st_size, "zip_sha256": zsha,
              "lfs_sha256": lfs_sha, "layout_root_in_zip": str(root.relative_to(stage)), "time": datetime.now(BJ).isoformat(),
              "counts": {d: len(list((dest / d).glob("*"))) for d in ("data", "video", "instruction") if (dest / d).exists()},
              "hdf5_sha256": {f.name: sha256(f) for f in files}}
    (top / "DOWNLOAD.json").write_text(json.dumps(marker, indent=1))
    say(f"-> {dest}: {marker['counts']}; DOWNLOAD.json written")
    if not keep_zip:
        zpath.unlink()
        say("zip removed (its sha256 is in DOWNLOAD.json; --keep-zip keeps it)")


def describe_h5(path):
    import h5py
    rows = []
    with h5py.File(path, "r") as f:
        def visit(name, obj):
            if isinstance(obj, h5py.Dataset):
                rows.append((name, tuple(obj.shape), str(obj.dtype)))
        f.visititems(visit)
        attrs = {k: str(v)[:80] for k, v in f.attrs.items()}
    return rows, attrs


def length_of(path):
    import h5py
    with h5py.File(path, "r") as f:
        for key in ("joint_action/vector", "joint_action/left_arm", "observation/head_camera/rgb"):
            if key in f:
                return int(f[key].shape[0])
        best = []
        f.visititems(lambda n, o: best.append(o.shape[0]) if isinstance(o, h5py.Dataset) and o.ndim >= 1 else None)
        return int(statistics.mode(best)) if best else None


def inspect(task):
    top = OUT / "demo_clean" / task
    dest = top / "aloha_agilex"
    if (top / "DOWNLOAD.json").exists():
        m = json.loads((top / "DOWNLOAD.json").read_text())
        say(f"\n== {top}/DOWNLOAD.json: revision {m['revision'][:12]}, zip sha256 {m['zip_sha256'][:16]}.. "
            f"(hub {str(m.get('lfs_sha256'))[:16]}..), counts {m['counts']}")
    files = sorted((dest / "data").glob("*.hdf5"))
    if not files:
        say(f"no hdf5 under {dest / 'data'}")
        return
    say(f"names: {files[0].name} .. {files[-1].name}")
    try:
        import h5py  # noqa: F401
    except ImportError:
        for py in PYTHONS:
            if Path(py).exists() and py != sys.executable and subprocess.run(
                    [py, "-c", "import h5py"], capture_output=True).returncode == 0:
                say(f"(h5py missing in {sys.executable}; inspecting with {py})")
                r = subprocess.run([py, "-I", __file__, "--task", task, "--inspect-only", "--no-report"],
                                   capture_output=True, text=True)
                for line in (r.stdout + r.stderr).splitlines():
                    say(line)
                return
        say("h5py not found in any known Python: layout not inspected")
        return
    press, attrs = describe_h5(files[0])
    put, _ = describe_h5(PUT_EP0) if PUT_EP0.exists() else ([], {})
    pk, uk = {r[0]: r for r in press}, {r[0]: r for r in put}
    say(f"\n== hdf5 layout: {files[0].name} ({task}) vs {PUT_EP0.name} (put_back)  attrs {attrs}")
    for k in sorted(set(pk) | set(uk)):
        a, b = pk.get(k), uk.get(k)
        say(f"  {k:48s} {task[:6]} {str(a[1:]) if a else '-':34s} put_back {str(b[1:]) if b else '-'}")
    lengths = [length_of(f) for f in files]
    ok = [x for x in lengths if x]
    if ok:
        say(f"\n== episode lengths ({len(ok)} files): min {min(ok)} median {statistics.median(ok)} max {max(ok)}; "
            f"total {sum(ok)} frames (put_back demos: see RECORDS length, e.g. 347)")
    pose = [k for k in pk if any(w in k.lower() for w in ("endpose", "ee_pose", "eef", "end_pose", "tcp"))]
    say(f"end-effector pose datasets (to locate presses in the demos): {pose or 'none found'}")
    ins = sorted((dest / "instruction").glob("*.json"))
    if ins:
        txt = ins[0].read_text(errors="replace")
        say(f"\n== instruction {ins[0].name} ({len(ins)} files): {txt[:700]}")
    vids = sorted((dest / "video").glob("*"))
    say(f"videos: {len(vids)} ({vids[0].name if vids else '-'})")
    used = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file())
    say(f"disk: {used / 1e9:.2f} GB in {dest}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", nargs="+", default=["press_button"])
    ap.add_argument("--list", action="store_true", help="list the hub's tasks (size, downloaded here or not) and stop")
    ap.add_argument("--inspect-only", action="store_true")
    ap.add_argument("--keep-zip", action="store_true")
    ap.add_argument("--no-report", action="store_true")
    args = ap.parse_args()
    prefix = "PRESS_FETCH" if args.task == ["press_button"] and not args.list else "RMB_FETCH"
    say(f"== {datetime.now(BJ):%F %T} RMBench fetch: task {' '.join(args.task)}, out {OUT}")
    failed = []
    try:
        rev = pinned_revision()
        if args.list or args.task == ["all"]:
            listed = hub_tasks(rev)
            say(f"hub {REPO_ID} @ {rev[:12]}: {len(listed)} tasks with data/<task>/demo_clean.zip")
            for t, size in listed:
                here = (OUT / "demo_clean" / t / "DOWNLOAD.json").exists()
                say(f"  {t:28s} {size / 1e9:6.2f} GB  {'downloaded here' if here else '-'}"
                    f"{'  (lives in resources/RMBench/data/demo_clean)' if t in SKIP_ALL else ''}")
            if args.list:
                return
            args.task = [t for t, _ in listed if t not in SKIP_ALL]
            say(f"all -> {' '.join(args.task)}")
        for task in args.task:
            say(f"\n######## {task}")
            try:
                if not args.inspect_only:
                    if (OUT / "demo_clean" / task / "DOWNLOAD.json").exists():
                        say("already downloaded (DOWNLOAD.json present): not downloading again")
                    else:
                        download(task, rev, args.keep_zip)
                inspect(task)
            except SystemExit as stop:
                say(f"STOPPED {task}: {stop}")
                failed.append(task)
            except Exception as err:                          # one bad task does not stop the others
                say(f"FAILED {task}: {type(err).__name__}: {err}")
                failed.append(task)
        say(f"\n== {datetime.now(BJ):%F %T} done: {len(args.task) - len(failed)}/{len(args.task)} tasks ok"
            f"{'; failed: ' + ' '.join(failed) if failed else ''}")
    finally:
        if not args.no_report:
            rep = OUT.parent / "report" / f"{prefix}_{datetime.now(BJ):%Y%m%d_%H%M}.txt"
            rep.parent.mkdir(parents=True, exist_ok=True)
            rep.write_text("\n".join(LINES) + "\n")
            print(f"{prefix}: {rep}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
