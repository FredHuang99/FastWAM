"""Plan v20 card 5 (press_told), 11-24 Opus: the instruction texts with the two press counts written in. GPU (T5 only).
Runs in mwam5090 (the press_button demos, its dense cache and the T5 of the released recipe are there).
  1 per training demo: its own press counts, no annotation: every 'bottom' event of the events file the control trained
    on (events_press_button_v3c.json) belongs to the button whose x the pressing arm's end-effector is nearest at that
    frame (left -0.15 / middle 0.0 / check 0.15, as repeat_theta.py; > 5 cm from all = unclear -> reported, stop);
    N1 = presses of the left button, N2 = of the middle one; the demo must have N1 in 1..9, N2 in 1..10-N1 and one
    check press (the env's expert presses exactly the card values), else stop
  2 texts: each base instruction of the cache (and of the 5090 / A40 seed-42 press bank if found) + told.py's sentence,
    for every demo's own counts and for all 45 (N1, N2) pairs the env can draw (the closed loop uses the scene's cards)
  3 T5 exactly as the dense cache (fastwam.memory_s1.model.encode_text, the recipe's T5 / tokenizer, seq 128):
    pipeline check first -- each base instruction re-encoded must equal the cache's own text of a demo with it (exact;
    else stop); every told text must keep its last 32 positions padding (the ledger's slots; data.check_ledger_slots)
  4 outputs/fullft/press_told/TOLD_TEXT.pt {"episodes": {episode_id: instruction}, "by_instruction": {instruction:
    {"text" [L, D] bf16, "text_valid" [L] bool}}, "meta"} + TOLD_TEXT.json (counts, checks, sha256); with --relay both go
    to the relay as diag/press_told (the new H200 and the A40 fetch them)
  PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/press_told_text.py [--relay]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
R = Path("/workspace/FastWAM-memory2")
ROOT = R / "outputs/memory_v2/press/dense_press_button_v1"
EVENTS = R / "outputs/fullft/events/events_press_button_v3c.json"
OUT = R / "outputs/fullft/press_told"
BUTTON_X = (-0.15, 0.0, 0.15)
UNCLEAR = 0.05
SLOTS = 32


def told_module():
    spec = importlib.util.spec_from_file_location("mwam_told", REPO / "scripts/memory_v2/sim/told.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--events", default=str(EVENTS))
    ap.add_argument("--relay", action="store_true")
    args = ap.parse_args()
    import events_stats as es
    from fastwam.fullft.data import check_ledger_slots
    told = told_module()
    OUT.mkdir(parents=True, exist_ok=True)
    root = Path(args.root)
    records = json.loads((root / "RECORDS.json").read_text())
    ev = json.loads(Path(args.events).read_text())
    ev = ev.get("episodes", ev)
    demos = {f"press_button/{p.stem}": p for p in es.demo_files("press_button")}
    counts, problems = {}, []
    for r in records:
        eid = r["episode_id"]
        path = demos.get(eid) or (Path(r["raw"]) if r.get("raw") and Path(r["raw"]).exists() else None)
        if path is None or eid not in ev:
            problems.append(f"{eid}: {'no demo file' if path is None else 'no events'}")
            continue
        _, pos = es.read_demo(path)
        n = [0, 0, 0]
        for e in ev[eid]:
            if e.get("kind") != "bottom":
                continue
            x = float(pos[min(int(e["frame"]), len(pos) - 1)][int(e["arm"])][0])
            k = min(range(3), key=lambda i: abs(x - BUTTON_X[i]))
            if abs(x - BUTTON_X[k]) > UNCLEAR:
                problems.append(f"{eid}: a press at x {x:.3f} is near no button")
            n[k] += 1
        counts[eid] = n
        if not (1 <= n[0] <= 9 and 1 <= n[1] <= 10 - n[0]):
            problems.append(f"{eid}: counts left {n[0]} middle {n[1]} are not a drawable card pair")
        if n[2] != 1:
            print(f"[told] note: {eid} has {n[2]} check presses in its events (the counts used are left / middle only)")
    print(f"[told] {len(counts)} demos counted; pairs {sorted({(a, b) for a, b, _ in counts.values()})}", flush=True)
    if problems:
        print("[told] STOP:\n  " + "\n  ".join(problems[:20]))
        return 1
    bases = sorted({r["instruction"] for r in records})
    for bank in (R / "outputs/memory_v2/closed_loop/scenes_seed42_n100_press_button/press_button.json",):
        if bank.exists():
            rows = json.loads(bank.read_text()).get("scenes", [])
            extra = sorted({str(x.get("instruction")) for x in rows if x.get("instruction")} - set(bases))
            print(f"[told] seed-42 press bank: {len(rows)} scenes; instructions not in the cache: {extra}")
            bases += extra
    print(f"[told] base instructions: {bases}", flush=True)
    episodes = {r["episode_id"]: r["instruction"] + told.told_sentence(*counts[r["episode_id"]][:2]) for r in records}
    texts = sorted(set(episodes.values()) | {b + told.told_sentence(a, c) for b in bases for a, c in told.combos()})
    print(f"[told] {len(texts)} texts to encode ({len(told.combos())} pairs x {len(bases)} bases + the demos' own)")
    from fastwam.memory_v2 import dense
    from fastwam.models.wan22.helpers.loader import _load_registered_model
    from fastwam.models.wan22.wan_video_text_encoder import HuggingfaceTokenizer
    from fastwam.memory_s1.model import encode_text
    spec = dense.DenseSpec()
    cfg = dense.dense_config(spec)

    def path(key):
        v = Path(cfg["paths"][key])
        return str(v if v.is_absolute() else Path(spec.root) / v)
    t5 = _load_registered_model(path("t5"), "wan_video_text_encoder", torch.bfloat16, "cuda:0").eval().requires_grad_(False)
    tok = HuggingfaceTokenizer(path("tokenizer"), seq_len=128, clean="whitespace", local_files_only=True)
    with torch.no_grad():
        for b in bases:
            rec = next((r for r in records if r["instruction"] == b), None)
            if rec is None:
                continue
            enc = torch.load(root / "cache" / rec["episode_id"].replace("/", "_") / "encodings.pt", map_location="cpu",
                             weights_only=True, mmap=True)
            f, v = encode_text(t5, tok, b, "cuda:0")
            same = torch.equal(f[0].cpu().to(enc["text"].dtype), enc["text"]) and torch.equal(v[0].cpu().bool(), enc["text_valid"].bool())
            diff = float((f[0].float().cpu() - enc["text"].float()).abs().max())
            print(f"[told] pipeline check '{b[:60]}...': {'EXACT' if same else 'DIFFERS'} (max |diff| {diff:.3g}; "
                  f"cache dtype {enc['text'].dtype}, shape {tuple(enc['text'].shape)})", flush=True)
            if not same:
                print("[told] STOP: the re-encoded base instruction differs from the cache's text")
                return 1
            dtype = enc["text"].dtype
        table = {}
        for k, t in enumerate(texts):
            f, v = encode_text(t5, tok, t, "cuda:0")
            text = f[0].cpu().to(dtype)
            check_ledger_slots(text, SLOTS, f"(told text {k}: {t[-70:]})")
            table[t] = {"text": text.contiguous(), "text_valid": v[0].cpu().bool().contiguous()}
            used = int(v[0].sum())
            if k < 3 or k == len(texts) - 1:
                print(f"[told] text {k}: {used} tokens used of {text.shape[0]}, last {SLOTS} padding OK: ...{t[-70:]}")
    longest = max(int(r["text_valid"].sum()) for r in table.values())
    meta = {"events": str(args.events), "events_sha256": sha(args.events), "root": str(root), "slots_checked": SLOTS,
            "longest_tokens": longest, "texts": len(table), "episodes": len(episodes), "bases": bases,
            "sentence_example": told.told_sentence(3, 4)}
    pt = OUT / "TOLD_TEXT.pt"
    torch.save({"episodes": episodes, "by_instruction": table, "meta": meta}, pt)
    js = OUT / "TOLD_TEXT.json"
    js.write_text(json.dumps({"meta": meta, "counts": counts, "episodes": episodes, "pt_sha256": sha(pt)}, indent=1) + "\n")
    print(f"[told] -> {pt} ({pt.stat().st_size} bytes, sha256 {sha(pt)[:16]}); longest text {longest} tokens; "
          f"last {SLOTS} positions padding in all {len(table)}")
    if args.relay:
        hf = "/opt/hf-tools/bin/python" if Path("/opt/hf-tools/bin/python").exists() else sys.executable
        rc = 0
        for f in (pt, js):
            rc |= subprocess.run([hf, str(REPO / "scripts/memory_v2/migrate/relay.py"), "put", str(f),
                                  "--prefix", "diag/press_told"]).returncode
        print(f"[told] relay put exit code {rc}")
        return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
