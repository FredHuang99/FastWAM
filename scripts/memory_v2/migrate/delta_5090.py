"""A100 -> 5090 workstation delta (11-07): what the 5090 needs beyond the October payload
(hhyfred/memwam-h100-migration-v1, already restored on the 5090).

  build : <mig>/MANIFEST.draft.json for manifest.py stage / upload (same format as the October payload), plus
          weights-only copies of the large LATEST checkpoints under <mig>/slim (the only new bytes on the A100 disk).

Groups (logical paths, so the 5090 bind mounts put every file back where the code looks for it):
  runs        finished runs in RUNS: everything in the run folder except checkpoints/*.pt, plus the LATEST checkpoint
              (>= 6 GB: weights-only copy, stored under the original file name; smaller: the file itself).
              Unfinished runs (no COMPLETE.json) are listed as skipped; rerun build after they finish.
  data        press training data and pairs (DATA_DIRS)
  demos       RMBench demo_clean (the payload left out RMBench data/)
  scenes      closed_loop/scenes_* (scene banks)
  results     closed_loop/**/result.json (what compare / reference read; videos and logs stay on the A100)
  simkit      outputs/migration_5090_v1/simkit (sim_kit_a100.py): simulator patches, CuRobo / PyTorch3D build sources
  changed     files of the October payload's roots that are new or changed since its manifest (RMBench simulator
              sources, FastWAM repo files), so the 5090 simulator equals the A100's

Run with the training python (torch, for the slim copies):
  PYTHONPATH=src /opt/mwam/bin/python scripts/memory_v2/migrate/delta_5090.py build
then (HF tools python):
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/manifest.py stage  --mig <mig> --name MANIFEST_5090_DELTA.json
  /opt/hf-tools/bin/python scripts/memory_v2/migrate/manifest.py upload --mig <mig> --name MANIFEST_5090_DELTA.json \
      --repo hhyfred/memwam-5090-delta-v1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from manifest import FW, MEM2, NEVER_DIRS, gib, secret  # noqa: E402

OUT = MEM2 + "/outputs/memory_v2"
MIG = Path(MEM2 + "/outputs/migration_5090_v1")
OLD_MANIFEST = Path(MEM2 + "/outputs/migration_h100_v1/stage/MANIFEST.json")
RUNS = ["a2C_6ep", "a2B0_6ep", "press_6ep", "press_6ep_lm8", "press_6ep_mix",
        "v2_press_cf", "v2_press_cf_lm8", "v2_press_cf_mix", "x7_distill_e3"]
DATA_DIRS = ["features_press_v1", "press", "pairs"]
DEMOS = [FW + "/resources/RMBench/data/demo_clean"]
CHANGED_ROOTS = [FW + "/resources/RMBench", FW + "/resources/PyTorch3D"]
CHANGED_SKIP = (FW + "/resources/RMBench/data/",)
SLIM_MIN = float(os.environ.get("DELTA_SLIM_MIN", 6e9))   # override only for tests
KEEP = ("update", "memory", "action", "config", "backend")
BJ = timezone(timedelta(hours=8))


def walk(top):
    """Files under a logical folder (the root may be a symlink; symlinked sub-folders are not followed)."""
    for root, dirs, files in os.walk(top):
        dirs[:] = sorted(d for d in dirs if d not in NEVER_DIRS)
        for name in sorted(files):
            p = os.path.join(root, name)
            if os.path.isfile(p) and not secret(p) and not name.endswith(".partial"):
                yield p


def entry(path, group, real=None):
    real = real or os.path.realpath(path)
    return {"path": path, "real": real, "size": os.path.getsize(real), "group": group}


def slim_copy(src: Path, dst: Path, log):
    """Weights-only copy of src at dst (reused when its sidecar records the same source size / mtime)."""
    import torch
    side = dst.with_name(dst.name + ".source.json")
    st = src.stat()
    stamp = {"source": str(src), "size": st.st_size, "mtime_ns": st.st_mtime_ns}
    if dst.exists() and side.exists() and json.loads(side.read_text()) == stamp:
        return
    t0 = time.time()
    dst.parent.mkdir(parents=True, exist_ok=True)
    state = torch.load(src, map_location="cpu", weights_only=False, mmap=True)
    if "raw" in state:
        log(f"  note {src}: distillation checkpoint, memory / action = EMA (what evaluation and the closed loop use)")
    slim = {k: state[k] for k in KEEP if k in state}
    slim["slimmed_from"] = {"file": str(src), "bytes": st.st_size, "time": datetime.now(BJ).isoformat(timespec="seconds")}
    tmp = dst.with_name(dst.name + ".partial")
    torch.save(slim, tmp)
    back = torch.load(tmp, map_location="cpu", weights_only=False)
    for part in ("memory", "action"):
        a, b = state.get(part), back.get(part)
        if (a is None) != (b is None) or (a is not None and (a.keys() != b.keys() or
                                                             not all(torch.equal(a[k], b[k]) for k in a))):
            tmp.unlink(missing_ok=True)
            raise SystemExit(f"slim copy of {src} differs in {part}")
    os.replace(tmp, dst)
    side.write_text(json.dumps(stamp))
    log(f"  slim copy {src.name}: {st.st_size / 1e9:.1f} -> {dst.stat().st_size / 1e9:.1f} GB ({time.time() - t0:.0f} s)")


def cmd_build(args):
    MIG.mkdir(parents=True, exist_ok=True)
    logf = (MIG / "DELTA_LOG.txt").open("a", encoding="utf-8")

    def log(msg):
        line = f"[delta] {datetime.now(BJ):%F %T} {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    files, skipped = [], []
    log(f"build -> {MIG / 'MANIFEST.draft.json'}")
    for run in RUNS:
        d = Path(OUT) / run
        if not d.is_dir():
            skipped.append(f"{run}: no folder")
            continue
        if not (d / "COMPLETE.json").exists():
            skipped.append(f"{run}: not finished (no COMPLETE.json); rerun build after it finishes")
            continue
        ck = d / "checkpoints"
        latest = json.loads((ck / "LATEST.json").read_text())["file"]
        for p in walk(str(d)):
            if p.startswith(str(ck) + "/") and p.endswith(".pt"):
                continue
            files.append(entry(p, "runs"))
        src = ck / latest
        logical = f"{OUT}/{run}/checkpoints/{latest}"
        if src.stat().st_size >= SLIM_MIN:
            dst = MIG / "slim" / run / latest
            slim_copy(src, dst, log)
            files.append(entry(logical, "runs", real=str(dst)))
        else:
            files.append(entry(logical, "runs"))
    for name in DATA_DIRS:
        files += [entry(p, "data") for p in walk(f"{OUT}/{name}")]
    for top in DEMOS:
        files += [entry(p, "demos") for p in walk(top)]
    if (MIG / "simkit" / "KIT.json").exists():            # sim_kit_a100.py output (simulator rebuild on the 5090)
        files += [entry(p, "simkit") for p in walk(str(MIG / "simkit"))]
    else:
        skipped.append("simkit: run sim_kit_a100.py first (needed only for the 5090 simulator)")
    cl = f"{OUT}/closed_loop"
    for name in sorted(os.listdir(cl)):
        if name.startswith("scenes_"):
            files += [entry(p, "scenes") for p in walk(f"{cl}/{name}")]
    files += [entry(p, "results") for p in walk(cl) if os.path.basename(p) == "result.json"]
    if OLD_MANIFEST.exists():
        old = {f["path"]: f["size"] for f in json.loads(OLD_MANIFEST.read_text())["files"]}
        n = 0
        for top in CHANGED_ROOTS:
            if not os.path.isdir(top):
                continue
            for p in walk(top):
                if p.startswith(CHANGED_SKIP):
                    continue
                if old.get(p) != os.path.getsize(p):
                    files.append(entry(p, "changed"))
                    n += 1
        log(f"changed vs the October manifest: {n} files under {', '.join(CHANGED_ROOTS)}")
    else:
        skipped.append(f"changed: {OLD_MANIFEST} not found (simulator sources not compared)")
    seen, unique = set(), []
    for f in files:
        if f["path"] not in seen:
            seen.add(f["path"])
            unique.append(f)
    by = {}
    for f in unique:
        by[f["group"]] = by.get(f["group"], 0) + f["size"]
    total = sum(by.values())
    for g, b in sorted(by.items()):
        log(f"  {g:<8} {gib(b)}  ({sum(1 for f in unique if f['group'] == g)} files)")
    log(f"  total    {gib(total)}  ({len(unique)} files)")
    for s in skipped:
        log(f"  skipped: {s}")
    draft = {"created": datetime.now(BJ).isoformat(timespec="seconds"), "purpose": "A100 -> 5090 delta",
             "base": "hhyfred/memwam-h100-migration-v1", "skipped": skipped, "total_bytes": total, "files": unique}
    (MIG / "MANIFEST.draft.json").write_text(json.dumps(draft, indent=1))
    log(f"draft written: {MIG / 'MANIFEST.draft.json'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    args = ap.parse_args()
    {"build": cmd_build}[args.cmd](args)


if __name__ == "__main__":
    main()
