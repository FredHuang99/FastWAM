#!/bin/bash
# NTU GaaS login node, 11-19 13:45 (plan v15, Fable 11-19 noon; user 13:21: execute Fable's plan). New H200 line B after
# cover_ar (~11-21 08:30): E24 press_clock (~17 h), then E25 ar2_tw (~35 h); 2 GPUs at a time throughout.
#   1 the press_button training cache dense_press_button_v1 from the cache relay (hhyfred/memwam-caches) ->
#     ~/mwam/FastWAM-memory2/outputs/memory_v2/press/dense_press_button_v1, under the stall watchdog of fetch_b1.sh
#     (nothing new for 10 min -> restart, plain HTTPS from the second try, 5 tries); sizes against its RELAY_MANIFEST
#     (the sha256 check runs inside the job, gaas_run.pbs step 2)
#   2 qsub press_clock with PBS depend=afterany on cover_ar's job, then ar2_tw with depend=afterany on press_clock's job.
#     If the press cache did not arrive, ar2_tw follows cover_ar directly and press_clock is not submitted (the log
#     says so; rerun this script later). A run already submitted is not submitted twice (GAAS_JOB). If cover_ar's job
#     is no longer queued, NOTHING is submitted (a plain qsub would take a third GPU); the log says so.
#   The jobs run the repository's current gaas_run.pbs at start (git pull + hand-over, 11-19), so fixes pushed before
#   Saturday still apply.
#   cd ~/mwam/FastWAM-memory2 && git pull -q --ff-only origin memory2 && nohup bash scripts/gaas/fetch_b2.sh > /dev/null 2>&1 &
# Log: ~/mwam/logs/FETCH_B2_<time>.txt
set -u
W=$HOME/mwam
R=$W/FastWAM-memory2
HFPY=$W/envs/hf-tools/bin/python
P=$R/outputs/memory_v2/press
mkdir -p $W/logs $P
LOG=$W/logs/FETCH_B2_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
say() { echo "[b2] $(date '+%F %T') $*"; }
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
print(f"[b2] {d.name}: {len(m['files']) - len(bad)}/{len(m['files'])} files with the right size, {m['total_bytes'] / 2 ** 30:.2f} GiB")
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

lane_job() {     # the queued / running job of run $1, else empty
  local a
  a=$(cat $R/outputs/fullft/$1/GAAS_JOB 2>/dev/null)
  [ -n "$a" ] && qstat "$a" > /dev/null 2>&1 && echo "$a"
}
submit_after() { # run, job id to follow
  local run=$1 dep=$2 j
  mkdir -p $R/outputs/fullft/$run
  if [ -s $R/outputs/fullft/$run/GAAS_JOB ]; then say "$run: already submitted ($(cat $R/outputs/fullft/$run/GAAS_JOB))"; return 0; fi
  j=$(cd $W && qsub -W depend=afterany:$dep -v RUN=$run $R/scripts/gaas/gaas_run.pbs) || { say "$run: qsub FAILED"; return 1; }
  echo "$j" > $R/outputs/fullft/$run/GAAS_JOB
  say "$run: submitted job $j (depend=afterany:$dep)"
}

COVER=$(lane_job cover_ar)
[ -n "$COVER" ] || { say "cover_ar's job is not queued any more: nothing submitted (would take a third GPU); tell Opus"; qstat -u "${USER:-$(id -un)}"; exit 1; }
say "line B is held by cover_ar's job $COVER"
name=dense_press_button_v1
say "$name -> $P/$name"
press_ok=0
if download $name $W/logs/dl_cache_relay.py $name $P && sizes_ok $P/$name; then
  du -sh $P/$name
  press_ok=1
else
  say "FAILED: $name (download or sizes); press_clock not submitted"
fi
if [ $press_ok = 1 ]; then
  submit_after press_clock $COVER
  NEXT=$(lane_job press_clock)
else
  NEXT=""
fi
submit_after ar2_tw ${NEXT:-$COVER}
qstat -u "${USER:-$(id -un)}"
say "done"
