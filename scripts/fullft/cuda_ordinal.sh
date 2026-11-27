#!/usr/bin/env bash
# 11-27 17:50 (Opus): the 5090's GPU 0 has dropped out of nvidia-smi again (11-26 17:58 too); the q5090 runner then gives
# tasks nvidia-smi index 1, but CUDA numbers the GPUs it can see from 0, so CUDA_VISIBLE_DEVICES=1 fails ("CUDA unknown
# error"; dev-* and gen800b failed 11-27 12:28-16:54). Prints the CUDA ordinal of nvidia-smi index $1 = its position among
# the indices nvidia-smi lists now (both present: unchanged).
i=${1:-0}
n=0
for x in $(nvidia-smi --query-gpu=index --format=csv,noheader 2>/dev/null | tr -d ' ' | sort -n); do
  [ "$x" = "$i" ] && { echo $n; exit 0; }
  n=$((n + 1))
done
echo "$i"
