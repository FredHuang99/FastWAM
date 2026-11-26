"""Machine-made appendix of the leaderboard data package (11-26 18:40, Opus; user 18:32: a weekly brief for the Fable
switch, Fable analyses the data Opus collects). Read-only, runs in the cloud session on unpacked results snapshots:
every verdict / report JSON of the A40 (and the 5090's few) -> one markdown row each, numbers copied, nothing judged.
  python3 scripts/fullft/leaderboard_appendix.py <snapshot dir with a40/ g5090/ ...> > appendix.md
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKIP = {"HF_USAGE.json", "HF_PRUNE.json", "HF_OFFLOAD.json", "RESULTS_PUSH.json"}


def cmp(c):
    if not isinstance(c, dict) or "new" not in c or "ref" not in c:
        return ""
    ci = c.get("ci95") or ["", ""]
    s = f"{c['new']} vs {c['ref']} of {c.get('scenes', '?')}, D {c.get('D')}, CI [{ci[0]}, {ci[1]}]"
    if "sign_p" in c:
        s += f", sign p {c['sign_p']}"
    return s


def row(machine, f: Path):
    try:
        d = json.loads(f.read_text())
    except Exception as e:                                                   # noqa: BLE001
        return f"| {machine} | {f.name} | (unreadable: {type(e).__name__}) | | |"
    if not isinstance(d, dict):
        return f"| {machine} | {f.name} | (not a dict) | | |"
    run = str(d.get("run", ""))[:90]
    verdict = str(d.get("verdict", d.get("reading", "")))[:160]
    parts = []
    m = cmp(d.get("main"))
    if m:
        parts.append("MAIN " + m)
    for k, v in d.items():
        if k in ("main", "run", "verdict", "finished", "sesoi"):
            continue
        c = cmp(v)
        if c:
            parts.append(f"{k}: {c}")
        elif isinstance(v, (int, float, str)) and k.startswith(("success", "unmasked", "control")):
            parts.append(f"{k}: {v}")
        elif isinstance(v, dict) and "verdict" in v and "main" in v:
            parts.append(f"{k}: {cmp(v['main'])} -> {v['verdict']}")
    return f"| {machine} | {f.name} | {run} | {verdict} | {'; '.join(parts)[:600]} |"


def main():
    root = Path(sys.argv[1])
    print("| 机器 | 文件 | run | 判定 / 读法（原文） | 数（原文） |")
    print("|---|---|---|---|---|")
    for machine in ("a40", "g5090", "a100"):
        d = root / machine / "snap" / "fullft"
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.json")):
            if f.name in SKIP:
                continue
            print(row(machine, f))
    stamp = {m: (root / m / "snap" / "STAMP.txt").read_text().split("\n")[0][:40]
             for m in ("a40", "g5090") if (root / m / "snap" / "STAMP.txt").is_file()}
    print(f"\n快照：{stamp}")


if __name__ == "__main__":
    main()
