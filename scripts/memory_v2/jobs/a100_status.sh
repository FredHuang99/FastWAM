#!/usr/bin/env bash
# Read-only status of the Phase-3 A100 lanes: which GPU each lane runs on, progress, s/update (last 20 updates),
# training ETA, finished post-training steps, and who holds each GPU.
#   bash /workspace/FastWAM-memory2/scripts/memory_v2/jobs/a100_status.sh
O=/workspace/FastWAM-memory2/outputs/memory_v2
echo "== $(date -u '+%F %T') UTC  load average: $(cut -d' ' -f1-3 /proc/loadavg)  cores: $(nproc)"
echo "-- training processes in this container (pid, GPU, run)"
for pid in $(pgrep -f "python.*fastwam.memory_v2.train_v2"); do
  gpu=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | sed -n 's/^CUDA_VISIBLE_DEVICES=//p')
  what=$(tr '\0' '\n' < /proc/$pid/cmdline | grep -E '^(train|evaluate|pr|features)$|^name=|^output=' | tr '\n' ' ')
  echo "  pid $pid  CUDA_VISIBLE_DEVICES=$gpu  $what  elapsed $(ps -o etime= -p $pid | tr -d ' ')"
done
echo "-- GPUs (index, used, total, util) and compute processes (pid as nvidia-smi reports it)"
nvidia-smi --query-gpu=index,uuid,memory.used,memory.total,utilization.gpu --format=csv,noheader
nvidia-smi --query-compute-apps=gpu_uuid,pid,used_memory --format=csv,noheader | while IFS=, read -r uuid pid mem; do
  pid=$(echo $pid | tr -d ' ')
  if [ -d /proc/$pid ]; then who="in this container: $(ps -o etime=,args= -p $pid | cut -c1-120)"; else who="NOT in this container (another user/container)"; fi
  echo "  $uuid pid $pid $mem -> $who"
done
/opt/mwam/bin/python - <<'PY'
import json, time
from pathlib import Path
O = Path("/workspace/FastWAM-memory2/outputs/memory_v2")
LANES = {"A": ["v2_A_anchor_cf", "v2_A_anchor"], "B": ["v2_A_cf_s19"], "C": ["v2_A_bfull_s19"]}
TOTAL = 1340
print("-- lanes: run | update | s/update (last 20) | training ETA | post-training files")
for lane, runs in LANES.items():
    done_file = O / f"RESULTS_3_{lane}.txt"
    for run in runs:
        d = O / run
        m = d / "metrics.jsonl"
        if not m.exists():
            print(f"  lane {lane}  {run:<16} not started")
            continue
        rows = [json.loads(l) for l in m.read_text().splitlines() if l.strip()]
        last = rows[-1]["update"] if rows else 0
        secs = [r["seconds"] for r in rows[-20:] if "seconds" in r]
        mean = sum(secs) / len(secs) if secs else None
        age = time.time() - m.stat().st_mtime
        eta = (TOTAL - last) * mean if mean and last < TOTAL else 0
        finish = time.strftime("%m-%d %H:%M", time.gmtime(time.time() + eta + 8 * 3600)) if eta else "-"
        post = [p for p in ("eval_full/update_001340.json",) if (d / p).exists()]
        post += [p.name for p in sorted((O / "pr" / run).glob("pr_*_val*.json"))]
        print(f"  lane {lane}  {run:<16} {last:>5}/{TOTAL}  {mean or float('nan'):6.1f} s  "
              f"ETA {eta / 3600:4.1f} h (~{finish} Beijing)  last write {age / 60:4.1f} min ago  done: {post or '-'}")
    print(f"  lane {lane}  queue finished: {done_file.exists()}  ({done_file})")
PY
