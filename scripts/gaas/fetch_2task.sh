#!/bin/bash
# NTU GaaS login node, 11-17 20:05 (user approved: E5 ar2_clock and E7 ar2_long train here). Downloads what the two
# runs need (transfers only, no computing on the login node; the sha256 checks run inside the jobs) and submits each
# run's job (gaas_run.pbs, one GPU) as soon as its data is here, so no GPU waits idle for a download:
#   1 the two-task training cache s1_dense_joint_h100_v1 (RECORDS.json, IDENTITY.json, cache/*; about 10-44 GB) from
#     the payload repo hhyfred/memwam-h100-migration-v1 -> ~/mwam/hf/payload/workspace/FastWAM/outputs/... (= the
#     container's /workspace/FastWAM/outputs/...); sizes checked against the repo MANIFEST
#   2 the put / swap event files (relay diag/events_2task, sent by the old H200) -> outputs/fullft/events/
#      (never overwrites)
#   -> qsub -v RUN=ar2_clock gaas_run.pbs (once)
#   3 ar_2task/resume.pt in parts (relay ckpt/ar_2task_e30, sent by the old H200; waits for its SEND_DONE, up to 10 h)
#      -> ~/mwam/dl/ar_2task_e30 ; sizes checked against the relay listing
#   -> qsub -v RUN=ar2_long gaas_run.pbs (once)
# Safe to run again (downloads resume; a run already submitted is not submitted twice: outputs/fullft/<run>/GAAS_JOB).
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && nohup bash scripts/gaas/fetch_2task.sh > /dev/null 2>&1 &
# Log: ~/mwam/logs/FETCH_2TASK_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
mkdir -p $W/logs $W/dl
LOG=$W/logs/FETCH_2TASK_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[fetch] $(date '+%F %T') $*"; }
cd $R
C=$W/hf/payload/workspace/FastWAM/outputs/s1_dense_joint_h100_v1
submit() {      # run: one job per run, once
  local run=$1 j
  mkdir -p $R/outputs/fullft/$run
  if [ -s $R/outputs/fullft/$run/GAAS_JOB ]; then say "$run: already submitted ($(cat $R/outputs/fullft/$run/GAAS_JOB))"; return 0; fi
  j=$(cd $W && qsub -v RUN=$run $R/scripts/gaas/gaas_run.pbs) || { say "$run: qsub FAILED"; return 1; }
  echo "$j" > $R/outputs/fullft/$run/GAAS_JOB
  say "$run: submitted job $j"
}

say "1 two-task training cache -> $C"
$HFPY - "$W/hf" <<'PY' || { say "FAILED: cache download"; exit 1; }
import sys
from huggingface_hub import hf_hub_download, snapshot_download
repo, out = "hhyfred/memwam-h100-migration-v1", sys.argv[1]
hf_hub_download(repo, "MANIFEST.json", local_dir=out)
base = "payload/workspace/FastWAM/outputs/s1_dense_joint_h100_v1/"
snapshot_download(repo, allow_patterns=[base + "RECORDS.json", base + "IDENTITY.json", base + "cache/*"],
                  local_dir=out, max_workers=8)
PY
$HFPY scripts/memory_v2/migrate/manifest.py verify --manifest $W/hf/MANIFEST.json --root $W/hf --no-hash \
  --prefix /workspace/FastWAM/outputs/s1_dense_joint_h100_v1/cache /workspace/FastWAM/outputs/s1_dense_joint_h100_v1/RECORDS.json \
  2>&1 | tail -n 3
[ ${PIPESTATUS[0]} -eq 0 ] || { say "FAILED: cache sizes (see above)"; exit 1; }
$HFPY - "$C" <<'PY' || { say "FAILED: cache incomplete"; exit 1; }
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
rows = [r for r in json.loads((root / "RECORDS.json").read_text()) if r["task"] in ("put_back_block", "swap_blocks")]
miss = [r["episode_id"] for r in rows
        if not ((root / "cache" / r["episode_id"].replace("/", "_") / "COMPLETE.json").is_file()
                and (root / "cache" / r["episode_id"].replace("/", "_") / "encodings.pt").is_file())]
by = {t: sum(r["task"] == t for r in rows) for t in ("put_back_block", "swap_blocks")}
print(f"[fetch] episodes {by}; missing {len(miss)} {miss[:3]}")
sys.exit(1 if miss or not rows else 0)
PY
du -sh $C

say "2 event files (relay diag/events_2task)"
mkdir -p $R/outputs/fullft/events $W/dl/events_2task
for i in $(seq 1 72); do
  $HFPY scripts/memory_v2/migrate/relay.py get --prefix diag/events_2task --out $W/dl/events_2task --repo hhyfred/memwam-fullft \
    > /dev/null 2>&1
  [ -s $W/dl/events_2task/events_put_back_block.json ] && [ -s $W/dl/events_2task/events_swap_blocks.json ] && break
  [ $i = 1 ] && say "not on the relay yet; looking every 5 min (up to 6 h)"
  sleep 300
done
for e in events_put_back_block events_swap_blocks; do
  [ -s $W/dl/events_2task/$e.json ] || { say "FAILED: $e.json never came (old H200: h200_send_resume.sh)"; exit 1; }
  if [ -f $R/outputs/fullft/events/$e.json ]; then
    cmp -s $W/dl/events_2task/$e.json $R/outputs/fullft/events/$e.json && say "$e.json in place (same)" \
      || say "$e.json: a DIFFERENT file is in place; kept it"
  else
    cp $W/dl/events_2task/$e.json $R/outputs/fullft/events/ && say "$e.json copied"
  fi
done
submit ar2_clock

say "3 ar_2task/resume.pt parts (relay ckpt/ar_2task_e30; waits for SEND_DONE)"
D=$W/dl/ar_2task_e30
mkdir -p $D
ls_relay() { $HFPY scripts/memory_v2/migrate/relay.py ls --prefix ckpt/ar_2task_e30 --repo hhyfred/memwam-fullft 2>/dev/null; }
for i in $(seq 1 120); do
  ls_relay | grep -q '^SEND_DONE ' && break
  [ $i = 1 ] && say "SEND_DONE not on the relay yet; looking every 5 min (up to 10 h)"
  sleep 300
done
ls_relay | grep -q '^SEND_DONE ' || { say "FAILED: the old H200 never finished sending (SEND_RESUME log there)"; exit 1; }
ls_relay
$HFPY - "$D" <<'PY' || { say "FAILED: parts download"; exit 1; }
import sys
from huggingface_hub import snapshot_download
snapshot_download("hhyfred/memwam-fullft", allow_patterns=["ckpt/ar_2task_e30/*"], local_dir=sys.argv[1], max_workers=8)
PY
bad=0
while read -r name size; do
  got=$(stat -c %s $D/ckpt/ar_2task_e30/$name 2>/dev/null || echo 0)
  [ "$got" = "$size" ] || { say "$name: $got bytes here, $size on the relay"; bad=1; }
done < <(ls_relay)
[ $bad = 0 ] || { say "FAILED: part sizes"; exit 1; }
say "parts here: $(ls $D/ckpt/ar_2task_e30 | tr '\n' ' ')"
submit ar2_long
say "done"
