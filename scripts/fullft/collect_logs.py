"""Collect one machine's logs and summaries since a cut-off into a zip (11-13; read-only for every run and episode).

Per machine (A100 container 6e4b37a15066, H200 mwam2, 5090 mwam5090):
  00_machine.txt      host, time, checkout, nvidia-smi, our processes (token-like words redacted), disk, memory
  01_pool_status.txt  pool5 status and a 30 h report (when this machine runs the pool)
  files/...           every .txt .log .json .jsonl .md .yaml .csv under outputs/ modified since --since (BJ), episode
                      folders, checkpoints, exports and data caches skipped; a file over 4 MB keeps its last 4 MB
  analysis/...        per recently written closed-loop label: stage export (JSON, as export_stages.py), loop_peek text,
                      press_gap (N7 labels), decision-0 export (first_actions.py)
  MANIFEST.txt        every file, its size, truncation, and each analysis command's exit code
--relay PREFIX puts the zip on the HF relay; --combine PREFIX (run last, on the 5090) fetches the other machines' zips
from the relay and writes ONE zip with all three machines: outputs/collect/MemWAM_logs_<time>.zip.
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/collect_logs.py --machine a100 --relay diag/collect_1113
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/collect_logs.py --machine 5090 --combine diag/collect_1113
"""
from __future__ import annotations

import argparse
import os
import re
import socket
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
OUTPUTS = R / "outputs"
O = OUTPUTS / "memory_v2"
BJ = timezone(timedelta(hours=8))
EXT = {".txt", ".log", ".json", ".jsonl", ".md", ".yaml", ".yml", ".csv"}
CAP = 4 * 2 ** 20
PRUNE = re.compile(r"^(seed_.*|checkpoints?|ckpt.*|exports|caches?|replay|dumpfirst.*|frames|videos|__pycache__|\.git|"
                   r"dense.*|text|collect|hf_cache|wandb)$")
FOLDERS = ["closed_loop/g1", "closed_loop/textab", "closed_loop/al3", "closed_loop/al3b", "closed_loop/al3b_first",
           "closed_loop/execlen", "closed_loop/x7c12", "closed_loop/s1pre", "closed_loop/al5", "closed_loop/rep",
           "closed_loop/w1"]
PAIRS = [("ar2_prop_e10", "ar_2task_e10_fx"), ("ar2_prop_e10", "ar_2task_e10"), ("ar2_prop_e20", "ar_2task_e20"),
         ("ar2_prop_e30", "ar_2task_e30")]          # 11-14: ledger arm vs AR control on the same machine (progress)
PY = sys.executable
HFPY = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else PY
SECRET = re.compile(r"(?i)(hf_[A-Za-z0-9]{8,}|token\S*|password\S*)")


def sh(cmd, timeout=900, env=None):
    try:
        p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout, cwd=str(R),
                           env=dict(os.environ, PYTHONPATH=str(R / "src"), **(env or {})))
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as error:                     # noqa: BLE001
        return -1, f"{type(error).__name__}: {error}"


def machine_text(machine):
    parts = [f"machine {machine}; host {socket.gethostname()}; {datetime.now(BJ):%Y-%m-%d %H:%M:%S} BJ"]
    for title, cmd in (("checkout", "git -c safe.directory='*' log --oneline -8"),
                       ("nvidia-smi", "nvidia-smi"),
                       ("gpu apps", "nvidia-smi --query-compute-apps=pid,used_memory,name --format=csv"),
                       ("processes", "ps -eo pid,etime,pcpu,rss,args --sort=start_time | grep -E 'python|bash' | grep -v grep"),
                       ("disk", "df -h /workspace /tmp"), ("memory", "free -h")):
        rc, out = sh(cmd, timeout=60)
        parts.append(f"\n===== {title} (rc {rc})\n{SECRET.sub('<redacted>', out)}")
    return "\n".join(parts)


def sweep(since, bundle, manifest):
    for root, dirs, files in os.walk(OUTPUTS):
        dirs[:] = [d for d in dirs if not PRUNE.match(d)]
        if len(files) > 3000:                     # a cache-like folder: only its newest few log files
            files = sorted(files, key=lambda f: -os.path.getmtime(os.path.join(root, f)))[:50]
        for name in files:
            p = Path(root) / name
            if p.suffix not in EXT:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_mtime < since:
                continue
            rel = p.relative_to(OUTPUTS)
            dest = bundle / "files" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if st.st_size > CAP:
                with open(p, "rb") as fh:
                    fh.seek(st.st_size - CAP)
                    data = fh.read()
                dest.write_bytes(f"[collect] truncated: last {CAP} of {st.st_size} bytes\n".encode() + data)
                manifest.append(f"files/{rel}\t{st.st_size}\tTRUNCATED to last 4 MB")
            else:
                dest.write_bytes(p.read_bytes())
                manifest.append(f"files/{rel}\t{st.st_size}")


def recent_labels(since):
    out = []
    for folder in FOLDERS:
        base = O / folder
        if not base.is_dir():
            continue
        for label in sorted(d for d in base.iterdir() if (d / "on").is_dir()):
            mt = max([t.stat().st_mtime for t in (label / "on").iterdir() if t.is_dir()] or [0])
            if mt >= since:
                out.append((folder, label.name))
    return out


def analyses(machine, since, bundle, manifest):
    a = bundle / "analysis"
    (a / "first").mkdir(parents=True, exist_ok=True)
    for folder, label in recent_labels(since):
        tag = f"{folder.split('/')[-1]}__{label}"
        jobs = [("stages", f"{PY} scripts/memory_v2/migrate/export_stages.py --label {label} --mode on "
                           f"--folders {O / folder} --out {a / (tag + '_stages.json')}"),
                ("peek", f"{PY} scripts/memory_v2/loop_peek.py --folder {folder} --label {label} --out /dev/null"),
                ("first", f"{PY} scripts/fullft/first_actions.py export --name {machine}__{tag} --folders {folder} --label {label}")]
        if label.startswith(("ar_2task", "ar2_")):
            jobs.append(("press_gap", f"{PY} scripts/fullft/press_gap.py --folder {folder} --label {label}"))
        for kind, cmd in jobs:
            start = time.monotonic()
            rc, out = sh(cmd, env={"FIRST_OUT": str(a / "first")})
            if kind != "stages":
                (a / f"{tag}_{kind}.txt").write_text(f"$ {cmd}\n(rc {rc})\n{out}", encoding="utf-8")
            manifest.append(f"analysis {tag} {kind}: rc {rc} ({time.monotonic() - start:.0f} s)")
            print(f"  {tag} {kind}: rc {rc}", flush=True)


def ledger_progress(bundle, manifest):
    a = bundle / "analysis"
    for arm, ctrl in PAIRS:
        if (O / "closed_loop/g1" / arm).is_dir() and (O / "closed_loop/g1" / ctrl).is_dir():
            cmd = (f"{PY} scripts/fullft/ledger_verdict.py --folder closed_loop/g1 --arm {arm} --control {ctrl} "
                   f"--progress --n 100")
            rc, out = sh(cmd)
            (a / f"LEDGER_PROGRESS_{arm}_vs_{ctrl}.txt").write_text(f"$ {cmd}\n(rc {rc})\n{out}", encoding="utf-8")
            manifest.append(f"analysis ledger progress {arm} vs {ctrl}: rc {rc}")
            print(f"  ledger progress {arm} vs {ctrl}: rc {rc}", flush=True)


def zip_dir(src, dest, prefix):
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, f"{prefix}/{p.relative_to(src)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--machine", required=True, choices=("a100", "h200", "5090"))
    ap.add_argument("--since", default="2026-11-12 16:00", help="Beijing time")
    ap.add_argument("--relay", default="")
    ap.add_argument("--combine", default="")
    args = ap.parse_args()
    since = datetime.strptime(args.since, "%Y-%m-%d %H:%M").replace(tzinfo=BJ).timestamp()
    stamp = datetime.now(BJ).strftime("%m%d_%H%M")
    work = OUTPUTS / "collect" / f"{args.machine}_{stamp}"
    bundle = work / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    manifest = [f"collect {args.machine} since {args.since} BJ, made {stamp} BJ"]
    (bundle / "00_machine.txt").write_text(machine_text(args.machine), encoding="utf-8")
    if (O / "queue5" / "pool.json").exists():
        rc1, st = sh(f"{PY} scripts/memory_v2/pool5.py status", timeout=300)
        rc2, rep = sh(f"{PY} scripts/memory_v2/pool5.py report --hours 30", timeout=600)
        (bundle / "01_pool_status.txt").write_text(f"(status rc {rc1})\n{st}\n\n(report rc {rc2})\n{rep}", encoding="utf-8")
    print(f"[collect] {args.machine}: sweeping outputs/ since {args.since} BJ", flush=True)
    sweep(since, bundle, manifest)
    print(f"[collect] {args.machine}: analyses of the closed-loop labels written since then", flush=True)
    analyses(args.machine, since, bundle, manifest)
    ledger_progress(bundle, manifest)
    (bundle / "MANIFEST.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
    own = OUTPUTS / "collect" / f"collect_{args.machine}_{stamp}.zip"
    zip_dir(bundle, own, args.machine)
    print(f"[collect] {own} ({own.stat().st_size / 2 ** 20:.1f} MB, {len(manifest) - 1} entries)", flush=True)
    if args.relay:
        rc, out = sh([HFPY, str(R / "scripts/memory_v2/migrate/relay.py"), "put", str(own), "--prefix", args.relay], timeout=1800)
        print(f"[collect] relay put {args.relay}: rc {rc} {out.strip().splitlines()[-1] if out.strip() else ''}", flush=True)
    if args.combine:
        others = work / "others"
        others.mkdir(exist_ok=True)
        rc, out = sh([HFPY, str(R / "scripts/memory_v2/migrate/relay.py"), "get", "--prefix", args.combine, "--out", str(others)],
                     timeout=1800)
        found = sorted(others.rglob("collect_*.zip"))
        final = OUTPUTS / "collect" / f"MemWAM_logs_{stamp}.zip"
        with zipfile.ZipFile(final, "w", zipfile.ZIP_DEFLATED) as z:
            for src in [own] + found:
                with zipfile.ZipFile(src) as zin:
                    for item in zin.infolist():
                        z.writestr(item, zin.read(item.filename))
        names = ", ".join(p.name for p in found) or "NONE (run the A100 and H200 commands first)"
        print(f"[collect] relay get {args.combine}: rc {rc}; other machines: {names}")
        print(f"COMBINED: {final} ({final.stat().st_size / 2 ** 20:.1f} MB)")


if __name__ == "__main__":
    main()
