"""Relay auto-clean, rule D (11-28 17:04, Opus; plan v22 1.12 decision D, user 11-28 15:52: "你的默认我同意" to the
recommendation: also delete intermediate exports that have a sha256-checked copy on the 5090 and that no pending task
uses, when the relay is above 75 %; final exports are never deleted). Runs on the 5090 (its huggingface_hub login; the
token is never printed). Nothing happens unless HF storage is above 75 % of the quota (HF_USAGE.json, refreshed by
hf_usage.py when older than 3 h; a usage figure older than 3 h after that refusal = nothing deleted: the 11-28 audit's
stale-usage guard). An export exports/<run>_e<k>/ of hhyfred/memwam-fullft is deleted only when ALL hold:
  1 intermediate: k < 30 and k below the run's last export (schedule.export_at_epochs of its queue line in
    gaas_queue.txt / h100_queue.txt / h200_queue.txt; default 10, 20, 30); a run found in no queue file is never touched
  2 a copy on the 5090 whose sha256 (computed, cached by path + size + mtime) equals the relay's .sha256: the export
    folder, the offload backup, or the relay mirror; when none exists it is first downloaded into the offload backup
    (outputs/fullft/exports_hf_backup/exports/<name>/) and checked the same way
  3 no pending task uses it: every queue5 task (A40 and A100) whose checkpoint is that file or whose command fetches it
    (RUN=<run> TAG=e<k>) is done or on hold (states from the machines' results branches; a task in no state table and
    not on hold counts as pending), and every q5090 line that names it is done
Oldest copy first, until the projected usage is at most 70 %. One commit, then super_squash_history (retried; its None
return is success). Writes outputs/fullft/HF_PRUNE_D.json and appends HF_PRUNE_D.log (what was deleted, when, why).
  /opt/hf-tools/bin/python scripts/fullft/hf_prune_d.py [--dry]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

R = Path(__file__).resolve().parents[2]
REPO = "hhyfred/memwam-fullft"
OUT = R / "outputs/fullft"
BK = OUT / "exports_hf_backup/exports"
MIRROR = Path("/mnt/hf/relay_mirror/memwam-fullft/exports")
QUEUES = ["scripts/gaas/gaas_queue.txt", "scripts/fullft/h100_queue.txt", "scripts/fullft/h200_queue.txt"]
START, STOP, MAX_AGE_H = 0.75, 0.70, 3.0
SHA_CACHE = OUT / "HF_PRUNE_D_SHA.json"


def sha(p: Path) -> str:
    cache = json.loads(SHA_CACHE.read_text()) if SHA_CACHE.exists() else {}
    st = p.stat()
    key = f"{p}|{st.st_size}|{int(st.st_mtime)}"
    if key in cache:
        return cache[key]
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    cache[key] = h.hexdigest()
    SHA_CACHE.write_text(json.dumps(cache, indent=1) + "\n")
    return cache[key]


def last_exports() -> dict:
    out = {}
    for q in QUEUES:
        p = R / q
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if line.lstrip().startswith("#") or "|" not in line:
                continue
            run = line.split("|")[0].strip()
            if not re.fullmatch(r"[A-Za-z0-9_]+", run):
                continue
            m = re.search(r"schedule\.export_at_epochs=\[([0-9., ]+)\]", line)
            eps = [float(x) for x in m.group(1).split(",")] if m else [10.0, 20.0, 30.0]
            out[run] = max(eps)
    return out


def states() -> dict:
    """task id -> state, from the A40 and A100 results branches (fetched now)."""
    out = {}
    for m in ("a40", "a100"):
        subprocess.run(["git", "-c", "safe.directory=*", "-C", str(R), "fetch", "-q", "origin",
                        f"+results-{m}:refs/remotes/origin/results-{m}"], capture_output=True, timeout=300)
        r = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(R), "show",
                            f"refs/remotes/origin/results-{m}:snap/report/STATES.tsv"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            f = line.split("\t")
            if len(f) >= 2:
                out[f[0]] = f[1]
    return out


def pending(name: str, run: str, tag: int, tasks, st) -> list:
    ckpt = f"/workspace/FastWAM-memory2/outputs/fullft/exports/{name}/export_e{tag}.pt"
    fetch = f"RUN={run} TAG=e{tag} "
    out = []
    for t in tasks:
        uses = t.get("checkpoint") == ckpt or fetch in str(t.get("command", "")) or ckpt in str(t.get("command", ""))
        if uses and not t.get("hold") and st.get(t["id"]) != "done":
            out.append(f"{t['id']} ({st.get(t['id'], 'no state')})")
    qf = R / "scripts/fullft/q5090.txt"
    for line in qf.read_text().splitlines() if qf.exists() else []:
        if line.lstrip().startswith("#") or "|" not in line:
            continue
        if re.search(rf"\b{re.escape(name)}\b|RUN={re.escape(run)} TAG=e{tag}\b", line):
            qid = line.split("|")[0].strip()
            if not (OUT / "q5090" / f"{qid}.done").exists() and not (OUT / "q5090" / f"{qid}.failed").exists():
                out.append(f"q5090 {qid}")
    return out


def usage(out) -> float | None:
    p = OUT / "HF_USAGE.json"
    age = (time.time() - p.stat().st_mtime) / 3600 if p.exists() else 1e9
    if age > MAX_AGE_H:
        subprocess.run(["/opt/hf-tools/bin/python", str(R / "scripts/fullft/hf_usage.py")], capture_output=True,
                       timeout=900, cwd=str(R))
        age = (time.time() - p.stat().st_mtime) / 3600 if p.exists() else 1e9
    out["usage_age_h"] = round(age, 2)
    if age > MAX_AGE_H:
        return None
    return float(json.loads(p.read_text())["used_fraction"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    out = {"time": time.strftime("%F %T"), "rule": "user decision D 11-28 15:52 (see the docstring)", "deleted": [],
           "skipped": {}}
    frac = usage(out)
    if frac is None:
        out["action"] = f"none: the usage figure is older than {MAX_AGE_H} h (refresh failed)"
    elif frac <= START:
        out["action"] = f"none: {frac:.1%} <= {START:.0%}"
    if "action" in out:
        (OUT / "HF_PRUNE_D.json").write_text(json.dumps(out, indent=1) + "\n")
        print(f"HF PRUNE D: {out['action']}")
        return 0
    out["used_fraction"] = frac
    import yaml
    from huggingface_hub import CommitOperationDelete, HfApi, hf_hub_download
    api = HfApi()
    quota = float(json.loads((OUT / "HF_USAGE.json").read_text())["quota_gb"]) * 1e9
    files = {x.path: x for x in api.list_repo_tree(REPO, path_in_repo="exports", repo_type="model", recursive=True)
             if hasattr(x, "size")}
    last, st = last_exports(), states()
    tasks = yaml.safe_load((R / "scripts/memory_v2/jobs/queue5_tasks.yaml").read_text())["tasks"]
    cands = []
    for path, f in files.items():
        m = re.fullmatch(r"exports/([A-Za-z0-9_]+)_e(\d+)/export_e(\d+)\.pt", path)
        if not m:
            continue
        run, tag = m.group(1), int(m.group(2))
        name = f"{run}_e{tag}"
        if run not in last:
            out["skipped"][name] = "run in no queue file"
            continue
        if tag >= 30 or tag >= last[run]:
            continue
        p = pending(name, run, tag, tasks, st)
        if p:
            out["skipped"][name] = "pending: " + ", ".join(p[:4]) + (f" (+{len(p) - 4})" if len(p) > 4 else "")
            continue
        cands.append((name, run, tag, int(f.size or 0)))
    used_b, target, ok = frac * quota, STOP * quota, []
    order = []
    for name, run, tag, size in cands:
        locs = [OUT / "exports" / name / f"export_e{tag}.pt", BK / name / f"export_e{tag}.pt", MIRROR / name / f"export_e{tag}.pt"]
        have = [p for p in locs if p.exists()]
        order.append(((have[0].stat().st_mtime if have else 0), name, run, tag, size, have))
    order.sort()
    for _, name, run, tag, size, have in order:
        if used_b <= target:
            break
        want = Path(hf_hub_download(REPO, f"exports/{name}/export_e{tag}.pt.sha256", repo_type="model")).read_text().split()[0]
        if not have:                 # no copy here yet: download into the offload backup (local_dir keeps the repo path)
            for fn in (f"export_e{tag}.pt.sha256", f"export_e{tag}.pt"):
                hf_hub_download(REPO, f"exports/{name}/{fn}", repo_type="model", local_dir=str(BK.parent))
            p = BK / name / f"export_e{tag}.pt"
            have = [p] if p.exists() else []
            if not have:
                out["skipped"][name] = "download to the 5090 failed"
                continue
        got = sha(have[0])
        if got != want:
            out["skipped"][name] = f"sha256 of the 5090 copy {got[:12]} != relay {want[:12]} ({have[0]})"
            continue
        ok.append(name)
        used_b -= size
        print(f"[prune-d] {name}: 5090 copy {have[0]} verified ({got[:16]}), {size / 1e9:.1f} GB", flush=True)
    out["projected_fraction_after"] = round(used_b / quota, 4)
    if ok and not a.dry:
        api.create_commit(REPO, repo_type="model", operations=[CommitOperationDelete(path_in_repo=f"exports/{n}/") for n in ok],
                          commit_message=f"auto-clean D: {len(ok)} intermediate exports kept on the 5090 (user decision D 11-28)")
        out["deleted"] = ok
        for i in range(3):
            try:
                api.super_squash_history(repo_id=REPO, repo_type="model")
                out["squashed"] = True
                break
            except Exception as e:                               # noqa: BLE001 (retried; reported)
                out["squash_error"] = f"{type(e).__name__}: {e}"[:300]
                time.sleep(120)
    out["action"] = ("dry run: would delete " if a.dry else "deleted ") + str(ok)
    (OUT / "HF_PRUNE_D.json").write_text(json.dumps(out, indent=1) + "\n")
    with open(OUT / "HF_PRUNE_D.log", "a") as f:
        f.write(f"{out['time']} {out['action']}; usage {frac:.1%} -> projected {out['projected_fraction_after']:.1%}\n")
    print(f"HF PRUNE D: {out['action']}; projected {out['projected_fraction_after']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
