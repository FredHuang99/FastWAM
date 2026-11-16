#!/usr/bin/env bash
# 11-16 (NTU boxes): HF download with a stall watchdog. On 11-15 the payload downloads on GPU18 and gpu24 were still
# "running" 10+ hours after their expected end. snapshot_download resumes (finished files are skipped through the
# local_dir metadata, .incomplete files continue), so a stalled attempt is killed and started again.
#   stall: /mnt/hf plus the HF cache (xet chunks) has not grown for STALL_MIN minutes -> kill, wait 30 s, retry
#   up to MAX_TRY attempts; WORKERS parallel files (default 8); NO_XET=1 downloads over plain HTTPS instead of xet
#   ALLOW=<file>: only the paths listed in that file (one per line), as delta_lite.sh
# The last line is "[restore] <time> step download finished, exit code N" like h100_restore.sh download.
#   RESTORE_LOG=/mnt/tmp/restore_download2.log bash scripts/memory_v2/migrate/dl_watch.sh
set -u
LOG=${RESTORE_LOG:-/mnt/tmp/restore_download2.log}
mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1
REPO=${HF_REPO:-hhyfred/memwam-h100-migration-v1}
DEST=${DEST:-/mnt/hf}
STALL=${STALL_MIN:-15}
MAXTRY=${MAX_TRY:-20}
WORKERS=${WORKERS:-8}
ALLOW=${ALLOW:-}
HFPY=${HFPY:-/opt/hf-tools/bin/python}
[ "${NO_XET:-0}" = 1 ] && export HF_HUB_DISABLE_XET=1
rc=1
trap 'echo "[restore] $(date "+%F %T") step download finished, exit code $rc"' EXIT
size() { du -sb "$DEST" "${HF_HOME:-/root/.cache/huggingface}" 2>/dev/null | awk '{s += $1} END {print s + 0}'; }
gib() { awk -v b="$1" 'BEGIN {printf "%.1f GiB", b / 2 ^ 30}'; }
echo "[restore] $(date '+%F %T') download $REPO -> $DEST (workers $WORKERS, stall $STALL min, xet $([ "${NO_XET:-0}" = 1 ] && echo off || echo on)${ALLOW:+, only the paths in $ALLOW})"
for try in $(seq 1 "$MAXTRY"); do
  start=$(size)
  echo "[restore] $(date '+%F %T') attempt $try: $(gib "$start") on disk"
  HF_HUB_DISABLE_PROGRESS_BARS=1 $HFPY - "$REPO" "$DEST" "$WORKERS" "$ALLOW" <<'PY' &
import sys
from huggingface_hub import snapshot_download
repo, dest, workers, allow = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
pats = [p for p in open(allow).read().split("\n") if p] if allow else None
print(snapshot_download(repo_id=repo, repo_type="model", local_dir=dest, max_workers=workers, allow_patterns=pats))
PY
  pid=$!
  last=$start; moved=$(date +%s); tick=0
  while kill -0 "$pid" 2>/dev/null; do
    sleep 60
    now=$(size)
    [ "$now" != "$last" ] && { last=$now; moved=$(date +%s); }
    tick=$((tick + 1))
    [ $((tick % 15)) = 0 ] && echo "[restore] $(date '+%F %T') attempt $try: $(gib "$now") on disk, +$(( (now - start) / 2 ** 20 )) MiB this attempt"
    if [ $(( $(date +%s) - moved )) -ge $((STALL * 60)) ]; then
      echo "[restore] $(date '+%F %T') attempt $try: no growth for $STALL min -> stopping it"
      kill "$pid" 2>/dev/null; sleep 10; kill -9 "$pid" 2>/dev/null
    fi
  done
  wait "$pid"; rc=$?
  echo "[restore] $(date '+%F %T') attempt $try ended, exit code $rc; $(gib "$(size)") on disk"
  [ "$rc" = 0 ] && break
  sleep 30
done
exit "$rc"
