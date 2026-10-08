#!/usr/bin/env bash
set -euo pipefail
SNAPSHOT_RUN="${1:?Pass the downloaded runs/run_id directory}"
REPO_ROOT="${2:?Pass the destination FastWAM root}"
REPO_ROOT="$(realpath "$REPO_ROOT")"
[[ -f "$SNAPSHOT_RUN/identity.json" ]] || { echo 'Missing downloaded identity.json' >&2; exit 1; }
[[ -d "$SNAPSHOT_RUN/code/src/fastwam/memory_s1" ]] || { echo 'Missing backed-up implementation' >&2; exit 1; }
if [[ -n "$(git -C "$REPO_ROOT" status --porcelain)" ]]; then
  echo 'Destination repository has local changes. Preserve them before restoring backup code.' >&2; exit 1
fi
for ITEM in src/fastwam/memory_s1 src/fastwam/models/wan22 scripts/memory_s1 configs/memory_s1 configs/model requirements docs; do
  if [[ -d "$SNAPSHOT_RUN/code/$ITEM" ]]; then
    mkdir -p "$REPO_ROOT/$ITEM"
    cp -a "$SNAPSHOT_RUN/code/$ITEM/." "$REPO_ROOT/$ITEM/"
  fi
done
cp -a "$SNAPSHOT_RUN/code/pyproject.toml" "$REPO_ROOT/pyproject.toml"
cp -a "$SNAPSHOT_RUN/code/.gitignore" "$REPO_ROOT/.gitignore"
echo 'Restored backed-up S1 code. Check the frozen backbone git commit before resuming.'
