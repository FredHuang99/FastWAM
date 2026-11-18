"""11-18 (Opus, plan v13 E6 on the A40): the instruction text a new task's closed loop needs, without its whole cache.

MWAM_TEXT_SOURCE=cache (every A40 evaluation) gives the model the text features of the first training episode with the
scene bank's instruction (fullft/online.py _cache_text: first the joint put/swap cache, then the model's own
data.roots = outputs/memory_v2/press/dense_<task>_v1: RECORDS.json + cache/<episode>/encodings.pt). The A40 has the
joint cache but not the per-task caches (tens of GB each, on the cache relay hhyfred/memwam-caches). This fetches only
RELAY_MANIFEST.json, RECORDS.json and the encodings.pt of that first episode per bank instruction into the same path,
checks each against the folder's RELAY_MANIFEST (size + sha256), and writes the marker .text_only (never .verified:
the folder is not a full cache and no trainer may use it). A folder with .verified (a full cache) is left alone.
  P=/opt/hf-tools/bin/python; [ -x $P ] || P=/opt/mwam/bin/python
  $P scripts/fullft/text_fetch.py --task battery_try
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/text_fetch.py --task battery_try --fingerprint   (needs torch)
--fingerprint prints, per instruction, the 12-hex fingerprint the closed loop prints ("[fullft] text from the training
cache (...; fingerprint ...)"): the same on two machines = bit-identical text input. Exit 0 only if everything checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"
REPO = "hhyfred/memwam-caches"


def bank_instructions(task):
    found = set()
    for f in sorted((O / f"closed_loop/scenes_seed42_n100_{task}").glob("*.json")):
        v = json.loads(f.read_text())
        v = (v.get("scenes") if isinstance(v, dict) else v) or []
        found |= {x["instruction"] for x in v if isinstance(x, dict) and x.get("task") == task and "instruction" in x}
    return sorted(found)


def sha256(path: Path, chunk: int = 1 << 24) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                return h.hexdigest()
            h.update(block)


def matches(path: Path, want: dict) -> bool:
    return path.is_file() and path.stat().st_size == want["size"] and sha256(path) == want["sha256"]


def needed(task, folder: Path):
    """[(instruction, relative path of the encodings.pt the closed loop will read)]"""
    records = json.loads((folder / "RECORDS.json").read_text(encoding="utf-8"))
    out = []
    for ins in bank_instructions(task):
        recs = [r for r in records if r.get("instruction") == ins]
        if not recs:
            raise SystemExit(f"[text] {task}: no training episode in RECORDS.json has the bank instruction {ins!r}")
        out.append((ins, f"cache/{recs[0]['episode_id'].replace('/', '_')}/encodings.pt", len(recs)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task", required=True)
    ap.add_argument("--fingerprint", action="store_true")
    args = ap.parse_args()
    name = f"dense_{args.task}_v1"
    folder = O / "press" / name
    if not bank_instructions(args.task):
        raise SystemExit(f"[text] {args.task}: no scene bank with instructions in "
                         f"{O / f'closed_loop/scenes_seed42_n100_{args.task}'}")
    if args.fingerprint:
        import torch
        for ins, rel, n in needed(args.task, folder):
            enc = torch.load(folder / rel, map_location="cpu", weights_only=True, mmap=True)
            text = enc["text"].to(torch.bfloat16).contiguous()
            valid = enc["text_valid"].bool().contiguous()
            fp = hashlib.sha256(text.view(torch.int16).cpu().numpy().tobytes() + valid.cpu().numpy().tobytes()).hexdigest()[:12]
            print(f"[text] {args.task}: {ins!r} -> {rel} ({n} training episodes share it); fingerprint {fp}")
        return
    if (folder / ".verified").exists():
        print(f"[text] {args.task}: the full cache is here and verified ({folder}); nothing to fetch")
        return
    from huggingface_hub import hf_hub_download
    folder.mkdir(parents=True, exist_ok=True)

    def get(rel):
        for attempt in (1, 2, 3):
            try:
                return Path(hf_hub_download(REPO, f"{name}/{rel}", repo_type="model", local_dir=str(folder.parent)))
            except Exception as error:                  # noqa: BLE001 (network; retried, then reported)
                print(f"[text] {rel}: download attempt {attempt} failed: {type(error).__name__}: {error}", flush=True)
        raise SystemExit(f"[text] {args.task}: could not download {name}/{rel}")

    get("RELAY_MANIFEST.json")
    manifest = json.loads((folder / "RELAY_MANIFEST.json").read_text())
    files = manifest["files"]
    want = ["RECORDS.json"]
    if not matches(folder / "RECORDS.json", files["RECORDS.json"]):
        get("RECORDS.json")
    bad = []
    for ins, rel, n in needed(args.task, folder):
        if rel not in files:
            raise SystemExit(f"[text] {args.task}: {rel} is not in the relay manifest of {name}")
        want.append(rel)
        if not matches(folder / rel, files[rel]):
            get(rel)
        print(f"[text] {args.task}: {ins!r} -> {rel} ({files[rel]['size'] / 2 ** 20:.0f} MiB; {n} training episodes "
              f"share the instruction)", flush=True)
    for rel in want:
        if not matches(folder / rel, files[rel]):
            bad.append(rel)
    if bad:
        raise SystemExit(f"[text] {args.task}: size / sha256 differ from the relay manifest: {bad}")
    (folder / ".text_only").write_text(json.dumps({"files": want, "manifest_created": manifest.get("created")}) + "\n")
    print(f"[text] {args.task}: {len(want)} files checked against {name}/RELAY_MANIFEST.json (sha256); marker .text_only")


if __name__ == "__main__":
    sys.exit(main())
