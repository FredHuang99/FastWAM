#!/usr/bin/env bash
set -euo pipefail
MODE="${1:?Use resources or run}"
REPO_ROOT="${2:?Pass the absolute FastWAM root}"
OUTPUT="${3:?Pass a new output package directory outside the resource/run folder}"
REPO_ROOT="$(realpath "$REPO_ROOT")"
OUTPUT="$(realpath -m "$OUTPUT")"
case "$OUTPUT/" in "$REPO_ROOT/resources/"*|"$REPO_ROOT/outputs/"*)
  echo 'Package destination must be outside resource/run input folders.' >&2; exit 1;;
esac
if [[ -e "$OUTPUT" ]]; then echo "Package directory already exists; refuse to overwrite." >&2; exit 1; fi
mkdir -p "$OUTPUT"
NAME="fastwam-s1-$MODE-$(date -u +%Y%m%dT%H%M%SZ)"
if [[ "$MODE" == resources ]]; then
  ITEMS=(resources/base resources/encoders resources/tokenizer resources/RMBench/data/download_cache resources/RMBench/assets resources/cache_s1 resources/prepared resources/download_lock.json)
elif [[ "$MODE" == run ]]; then
  if [[ -f "$REPO_ROOT/outputs/memory_s1_seed17/launcher.pid" ]] && kill -0 "$(cat "$REPO_ROOT/outputs/memory_s1_seed17/launcher.pid")" 2>/dev/null; then
    echo "Launcher is alive. Complete safe stop before packaging mutable training state." >&2; exit 1
  fi
  ITEMS=(src/fastwam/memory_s1 src/fastwam/models/wan22 scripts/memory_s1 configs/memory_s1 configs/model/fastwam.yaml pyproject.toml .gitignore requirements/memory_s1.txt docs/memory_s1_runbook_zh.md outputs/memory_s1_seed17)
else
  echo "Unknown package mode: $MODE" >&2; exit 1
fi
for ITEM in "${ITEMS[@]}"; do [[ -e "$REPO_ROOT/$ITEM" ]] || { echo "Missing package input: $ITEM" >&2; exit 1; }; done
tar -C "$REPO_ROOT" --exclude='*/.cache/*' --exclude='*/__pycache__/*' --exclude='*.tmp' --exclude='*.sock' --exclude='*.pid' \
  -I 'zstd -T4 -3' -cf "$OUTPUT/$NAME.tar.zst" "${ITEMS[@]}"
if [[ "$MODE" == resources ]]; then
  split --bytes=4G --numeric-suffixes=0 --suffix-length=4 "$OUTPUT/$NAME.tar.zst" "$OUTPUT/$NAME.tar.zst.part-"
  rm -- "$OUTPUT/$NAME.tar.zst"
fi
(cd "$OUTPUT"; sha256sum ./* > "$NAME.sha256")
du -h "$OUTPUT"
echo "Package: $OUTPUT. Credentials, Docker images and duplicate extracted raw episodes are excluded."
