#!/bin/bash
# NTU GaaS login node, 11-18 17:08 (user approved: the B1 AR runs of cover and ranking train on the new H200, ~3x the
# H100's speed). Transfers only (the sha256 check runs inside the job, gaas_run.pbs):
#   1 per task: the dense training cache dense_<task>_v1 from the cache relay (hhyfred/memwam-caches, uploaded by the
#     5090 / H100 chain earlier) -> ~/mwam/FastWAM-memory2/outputs/memory_v2/press/dense_<task>_v1 (= the container's
#     /workspace/FastWAM-memory2/outputs/...), under the stall watchdog of fetch_2task.sh (nothing new for 10 min ->
#     restart, plain HTTPS from the second try, 5 tries); sizes against the folder's RELAY_MANIFEST.json
#   2 qsub the run with PBS depend=afterany on the job now holding the lane: ranking_ar after E5 (ar2_clock, ends ~04:30),
#     cover_ar after E7 (ar2_long, ~06:30) -> the longer run takes the earlier lane; 2 GPUs at a time throughout.
#     If that job has already left the queue, plain qsub. A run already submitted is not submitted twice (GAAS_JOB).
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && nohup bash scripts/gaas/fetch_b1.sh > /dev/null 2>&1 &
# Log: ~/mwam/logs/FETCH_B1_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
P=$R/outputs/memory_v2/press
mkdir -p $W/logs $P
LOG=$W/logs/FETCH_B1_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[b1] $(date '+%F %T') $*"; }
cd $R
export HF_HUB_DOWNLOAD_TIMEOUT=60
grown() { du -sb $P $HOME/.cache/huggingface 2>/dev/null | awk '{s += $1} END {print s + 0}'; }
download() {    # label python-file args...: run it under the stall watchdog (as in fetch_2task.sh)
  local label=$1 py=$2 try pid last now idle
  shift 2
  for try in 1 2 3 4 5; do
    say "$label: download try $try$([ "${HF_HUB_DISABLE_XET:-0}" = 1 ] && echo ' (plain HTTPS)')"
    $HFPY $py "$@" &
    pid=$!
    last=$(grown); idle=0
    while kill -0 $pid 2>/dev/null; do
      sleep 60
      now=$(grown)
      if [ "$now" = "$last" ]; then idle=$((idle + 1)); else idle=0; last=$now; fi
      if [ $idle -ge 10 ]; then
        say "$label: nothing new on disk for 10 min: restart"
        kill $pid 2>/dev/null; sleep 10; kill -9 $pid 2>/dev/null
        break
      fi
    done
    if [ $idle -lt 10 ] && wait $pid; then say "$label: download finished"; return 0; fi
    [ $idle -ge 10 ] || say "$label: download ended with an error"
    export HF_HUB_DISABLE_XET=1
    sleep 30
  done
  return 1
}
cat > $W/logs/dl_cache_relay.py <<'PY'
import sys
from huggingface_hub import snapshot_download
name, dest = sys.argv[1], sys.argv[2]
snapshot_download("hhyfred/memwam-caches", repo_type="model", allow_patterns=[f"{name}/*"], local_dir=dest, max_workers=8)
PY
sizes_ok() {    # folder: every manifest file present with its size (no hashing on the login node)
  $HFPY - "$1" <<'PY'
import json, sys
from pathlib import Path
d = Path(sys.argv[1]); m = json.loads((d / "RELAY_MANIFEST.json").read_text())
bad = [rel for rel, f in m["files"].items() if not (d / rel).is_file() or (d / rel).stat().st_size != f["size"]]
print(f"[b1] {d.name}: {len(m['files']) - len(bad)}/{len(m['files'])} files with the right size, {m['total_bytes'] / 2 ** 30:.2f} GiB")
sys.exit(1 if bad else 0)
PY
}
submit() {      # run, the run whose job holds the lane now
  local run=$1 after=$2 dep="" j a
  mkdir -p $R/outputs/fullft/$run
  if [ -s $R/outputs/fullft/$run/GAAS_JOB ]; then say "$run: already submitted ($(cat $R/outputs/fullft/$run/GAAS_JOB))"; return 0; fi
  a=$(cat $R/outputs/fullft/$after/GAAS_JOB 2>/dev/null)
  if [ -n "$a" ] && qstat "$a" > /dev/null 2>&1; then dep="-W depend=afterany:$a"; fi
  j=$(cd $W && qsub $dep -v RUN=$run $R/scripts/gaas/gaas_run.pbs) || { say "$run: qsub FAILED"; return 1; }
  echo "$j" > $R/outputs/fullft/$run/GAAS_JOB
  [ -n "$dep" ] || dep="(no dependency: the job of $after is no longer queued)"
  say "$run: submitted job $j $dep"
}

for pair in "blocks_ranking_try ranking_ar ar2_clock" "cover_blocks cover_ar ar2_long"; do
  set -- $pair
  task=$1; run=$2; after=$3; name=dense_${task}_v1
  say "$name -> $P/$name"
  download $name $W/logs/dl_cache_relay.py $name $P || { say "FAILED: $name download (5 tries)"; continue; }
  sizes_ok $P/$name || { say "FAILED: $name sizes"; continue; }
  du -sh $P/$name
  submit $run $after
done
qstat -u "${USER:-$(id -un)}"
say "done"
