#!/usr/bin/env bash
# mwam5090, 11-24 (Opus; plan v20). Two things, in order:
#   1 card 4 = ranking_v3a (user 18:32, option b): the ranking events file with rule A's thresholds and the provisional
#     write (task_v3c_events.py --delta 0.015 --min-path 0.03 --tag v3a --relay -> relay diag/blocks_ranking_try_v3a);
#     the new H200's slot job fetches it (CPU, seconds)
#   2 card 13a, the find-same match probe FS-P1 (match_probe.py): colour histogram and a frozen public image encoder
#     (facebook/dinov2-base by default; transformers' native Dinov2Model from safetensors, no remote code; the name,
#     revision and file sha256 go to the log and MATCH_PROBE.json). GPU ${MP_GPU:-1}, a few minutes.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/match_probe_5090.sh
# Own log: outputs/fullft/MATCH_PROBE_5090_<time>.txt ; results outputs/fullft/match_probe/ (MATCH_PROBE.json, sheet_*.png)
set -u
R=/workspace/FastWAM-memory2
F=$R/outputs/fullft
LOG=$F/MATCH_PROBE_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[mp] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
echo "[mp] $(date '+%F %T') checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60)"
echo "[mp] ===== 1 ranking events, rule A thresholds + provisional write (card 4 = ranking_v3a)"
/opt/mwam/bin/python scripts/fullft/task_v3c_events.py --task blocks_ranking_try --delta 0.015 --min-path 0.03 \
  --provisional 0.002 --tag v3a --relay 2>&1 | tail -n 8
echo "[mp] ===== 2 card 13a match probe (GPU ${MP_GPU:-1})"
/opt/mwam/bin/python -c "import transformers, huggingface_hub; print('[mp] transformers', transformers.__version__, 'huggingface_hub', huggingface_hub.__version__)"
CUDA_VISIBLE_DEVICES=${MP_GPU:-1} /opt/mwam/bin/python scripts/fullft/match_probe.py --device cuda:0 2>&1 \
  | grep -v "Warning\|warn(\|it/s\]"
ls -la outputs/fullft/match_probe/ | head -8
echo "[mp] $(date '+%F %T') DONE"
