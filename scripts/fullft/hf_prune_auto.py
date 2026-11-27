"""Automatic pruning of INTERMEDIATE exports on the HF relay (11-27 13:30, Opus). User 11-27 13:19 agreed, verbatim to
the question "能否允许巡检在超过 85% 时，自动删掉'评测机已评完、而且评测机上有核对过副本的中间存档'（10 轮、20 轮这类，
最终的 30 轮不删）？" -> "同意". Runs on the A40 (its huggingface_hub login; the token is never printed). Nothing happens
unless HF storage is above 85 % of the quota (HF_USAGE.json, refreshed by hf_usage.py just before). An export
exports/<run>_<tag>/ of hhyfred/memwam-fullft is deleted only when ALL hold:
  1 intermediate: <tag> is not e30 and is below the run's last export (schedule.export_at_epochs of its queue line in
    gaas_queue.txt / h100_queue.txt / h200_queue.txt; default 10, 20, 30); a run found in no queue file is never touched
  2 the A40 holds outputs/fullft/exports/<run>_<tag>/export_<tag>.pt whose sha256 (computed now) equals its local .sha256
    AND the relay's .sha256 (as hf_prune.py)
  3 evaluated on the A40: at least one queue5 task uses that checkpoint, and every such task not on hold is done
  4 the relay copy is older than 24 h (the 5090's early looks / probes fetch new exports from the relay)
Oldest first, until the projected usage is at most 80 %. One commit, then super_squash_history (the quota reflects it
within 36 h; an export deleted once is never counted again). Writes outputs/fullft/HF_PRUNE_AUTO.json.
  /opt/hf-tools/bin/python scripts/fullft/hf_prune_auto.py [--dry]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

R = Path(__file__).resolve().parents[2]
REPO = "hhyfred/memwam-fullft"
OUT = R / "outputs/fullft"
QUEUES = ["scripts/gaas/gaas_queue.txt", "scripts/fullft/h100_queue.txt", "scripts/fullft/h200_queue.txt"]
START, STOP = 0.85, 0.80


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def last_exports() -> dict:
    """run -> its last export epoch (from the queue lines' schedule.export_at_epochs; default 30)."""
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


def evaluated(ckpt: str):
    """(used, all_done) over the queue5 tasks whose checkpoint is ckpt (held tasks ignored)."""
    import yaml
    tasks = yaml.safe_load((R / "scripts/memory_v2/jobs/queue5_tasks.yaml").read_text())["tasks"]
    used, done = 0, True
    for t in tasks:
        if t.get("checkpoint") != ckpt or t.get("hold"):
            continue
        used += 1
        st = R / "outputs/memory_v2/queue5/state" / f"{t['id']}.json"
        s = json.loads(st.read_text()).get("status") if st.exists() else None
        done = done and s == "done"
    return used, done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    out = {"time": time.strftime("%F %T"), "rule": "user 11-27 13:19 (see the docstring)", "deleted": [], "skipped": {}}
    use = json.loads((OUT / "HF_USAGE.json").read_text())
    frac, quota = float(use["used_fraction"]), float(use["quota_gb"]) * 1e9
    out["used_fraction"] = frac
    if frac <= START:
        out["action"] = f"none: {frac:.1%} <= 85 %"
        (OUT / "HF_PRUNE_AUTO.json").write_text(json.dumps(out, indent=1) + "\n")
        print(f"HF PRUNE AUTO: {frac:.1%} <= 85 %, nothing to do")
        return 0
    from huggingface_hub import CommitOperationDelete, HfApi, hf_hub_download
    api = HfApi()
    files = {}
    try:
        tree = list(api.list_repo_tree(REPO, path_in_repo="exports", repo_type="model", recursive=True, expand=True))
    except TypeError:                         # an older huggingface_hub without expand: ages from the A40 copies below
        tree = list(api.list_repo_tree(REPO, path_in_repo="exports", repo_type="model", recursive=True))
    for x in tree:
        if hasattr(x, "size"):
            files[x.path] = x
    last = last_exports()
    now = time.time()
    cands = []
    for path, f in files.items():
        m = re.fullmatch(r"exports/([A-Za-z0-9_]+)_e(\d+)/export_e(\d+)\.pt", path)
        if not m:
            continue
        name, run, tag = f"{m.group(1)}_e{m.group(2)}", m.group(1), int(m.group(2))
        if run not in last:
            out["skipped"][name] = "run in no queue file"
            continue
        if tag >= 30 or tag >= last[run]:
            continue                                            # final exports are never touched
        local = OUT / "exports" / name / f"export_e{tag}.pt"
        date = getattr(getattr(f, "last_commit", None), "date", None)
        when = date.timestamp() if date else (local.stat().st_mtime if local.exists() else None)   # A40 copy: fetched later
        age_h = (now - when) / 3600 if when else None
        if age_h is None or age_h < 24:
            out["skipped"][name] = f"relay copy younger than 24 h ({age_h})"
            continue
        ckpt = f"/workspace/FastWAM-memory2/outputs/fullft/exports/{name}/export_e{tag}.pt"
        used, done = evaluated(ckpt)
        if not used or not done:
            out["skipped"][name] = f"A40 evaluation not complete ({used} tasks, all done {done})"
            continue
        if not local.exists() or not (local.parent / (local.name + ".sha256")).exists():
            out["skipped"][name] = "no A40 copy"
            continue
        cands.append((when, name, tag, local, int(f.size or 0)))
    cands.sort()
    used_b, target, ok = frac * quota, STOP * quota, []
    for _, name, tag, local, size in cands:
        if used_b <= target:
            break
        want_local = (local.parent / (local.name + ".sha256")).read_text().split()[0]
        want_relay = Path(hf_hub_download(REPO, f"exports/{name}/export_e{tag}.pt.sha256", repo_type="model")).read_text().split()[0]
        got = sha(local)
        if not (got == want_local == want_relay):
            out["skipped"][name] = f"sha256 differs ({got[:12]} / {want_local[:12]} / {want_relay[:12]})"
            continue
        ok.append(name)
        used_b -= size
        print(f"[autoprune] {name}: A40 copy verified ({got[:16]}), {size / 1e9:.1f} GB", flush=True)
    out["projected_fraction_after"] = round(used_b / quota, 4)
    if ok and not args.dry:
        api.create_commit(REPO, repo_type="model", operations=[CommitOperationDelete(path_in_repo=f"exports/{n}/") for n in ok],
                          commit_message=f"auto-prune {len(ok)} intermediate exports kept on the A40 (user rule 11-27 13:19)")
        api.super_squash_history(repo_id=REPO, repo_type="model")
        out["deleted"] = ok
    out["action"] = ("dry run: would delete " if args.dry else "deleted ") + str(ok)
    (OUT / "HF_PRUNE_AUTO.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"HF PRUNE AUTO: {out['action']}; projected {out['projected_fraction_after']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
