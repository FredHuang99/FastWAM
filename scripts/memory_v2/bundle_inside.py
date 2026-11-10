"""Container side of jobs/bundle.sh (11-10): read-only review material of this machine for the last <hours>.

Piped in by bundle.sh (python - <hours>), so it runs on any checkout, also one older than this file. Prints:
  verdicts   every queue5 task that finished in the window (end time, verdict, rc), oldest first
  autopsies  for each of them: autopsy.py --id <id> --no-phase (rewrites autopsy/AUTOPSY_<id>.md; verdict and ledger
             unchanged), then the file
  running    train tasks: the in-training eval curve (queue5.py curve when this checkout has it, else the last eval
             lines of metrics.jsonl); closed loops: loop_peek.py when present (read-only), else the episode count
  reports    every outputs/memory_v2/report/ file written in the window (REPORT_ / BUNDLE_ excluded), 300 lines each
Nothing is started, stopped, reset or updated.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

H = float(sys.argv[1]) if len(sys.argv) > 1 else 120.0
R = Path("/workspace/FastWAM-memory2")
O = R / "outputs/memory_v2"
Q = O / "queue5"
PY = "/opt/mwam/bin/python"
BJ = timezone(timedelta(hours=8))
now = datetime.now(BJ)
since = now - timedelta(hours=H)
since_s = since.strftime("%Y-%m-%d %H:%M")
ENV = dict(os.environ, PYTHONPATH=str(R / "src"))


def sec(title):
    print(f"\n===== {title}", flush=True)


def run(cmd, timeout=900):
    try:
        r = subprocess.run(cmd, cwd=R, env=ENV, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)
    except Exception as e:                                  # noqa: BLE001
        return 1, f"{type(e).__name__}: {e}"


def tail(path, n):
    try:
        lines = Path(path).read_text(errors="replace").splitlines()
    except OSError as e:
        return f"(cannot read {path}: {e})"
    head = f"({len(lines)} lines; last {n})\n" if len(lines) > n else ""
    return head + "\n".join(lines[-n:])


states = {}
for p in sorted((Q / "state").glob("*.json")):
    try:
        states[p.stem] = json.loads(p.read_text())
    except (OSError, ValueError):
        pass
try:
    import yaml
    doc = yaml.safe_load((R / "scripts/memory_v2/jobs/queue5_tasks.yaml").read_text())
    tasks = {t["id"]: t for t in (doc.get("tasks", []) if isinstance(doc, dict) else doc)}
except Exception:                                           # noqa: BLE001
    tasks = {}

sec(f"verdicts finished since {since_s} (Beijing), oldest first")
recent = sorted((k for k, s in states.items() if s.get("status") == "done" and str(s.get("end") or "") >= since_s),
                key=lambda k: str(states[k].get("end")))
for k in recent:
    s = states[k]
    print(f"- {s.get('end')}  {k:<22} {str(s.get('verdict')):<13} rc={s.get('rc')}  attempt={s.get('attempt')}")
running = [k for k, s in states.items() if s.get("status") == "running"]
held = [k for k, t in tasks.items() if t.get("hold")]
print(f"running: {running}\non hold in this checkout's task file: {held}")

for k in recent:
    sec(f"autopsy {k}")
    rc, out = run([PY, "scripts/memory_v2/autopsy.py", "--id", k, "--no-phase"])
    f = O / "autopsy" / f"AUTOPSY_{k}.md"
    if rc != 0:
        print(f"(autopsy.py rc={rc}: {out.strip().splitlines()[-1] if out.strip() else ''})")
    print(tail(f, 160) if f.exists() else "(no autopsy file)")

has_curve = "def cmd_curve" in (R / "scripts/memory_v2/queue5.py").read_text(errors="replace")
has_peek = (R / "scripts/memory_v2/loop_peek.py").exists()
for k in running:
    t = tasks.get(k, {})
    sec(f"running {k} ({t.get('kind')})")
    if t.get("kind") == "train":
        if has_curve:
            print(run([PY, "scripts/memory_v2/queue5.py", "curve", k])[1])
        else:
            m = O / t.get("run", "?") / "metrics.jsonl"
            evals = [l for l in (m.read_text().splitlines() if m.exists() else []) if '"eval' in l]
            print("\n".join(evals[-6:]) or f"(no eval lines in {m})")
        print(tail(O / t.get("run", "?") / "stdout.log", 15))
    elif t.get("kind") == "closed_loop":
        if has_peek and t.get("output") and t.get("label"):
            print(run([PY, "scripts/memory_v2/loop_peek.py", "--folder", t["output"], "--label", t["label"],
                       "--out", "/dev/null"])[1])
        else:
            out = O / t.get("output", "?")
            print(f"{len(list(out.glob(t.get('label', '*') + '/*/*/seed_*/result.json')))} episodes with result.json in {out}")
    else:
        print(tail(Q / "tasks" / f"{k}.log", 30))

sec(f"report files written since {since_s}")
files = [p for p in sorted((O / "report").glob("*"), key=lambda p: p.stat().st_mtime)
         if p.is_file() and p.stat().st_mtime >= since.timestamp() and not p.name.startswith(("REPORT_", "BUNDLE_"))
         and p.suffix in (".md", ".txt")]
print("\n".join(f"  {datetime.fromtimestamp(p.stat().st_mtime, BJ):%m-%d %H:%M}  {p.name}" for p in files) or "  (none)")
for p in files:
    sec(f"file {p.name}")
    print(tail(p, 300))
