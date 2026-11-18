#!/usr/bin/env bash
# mwam-a40 (plan v13 E6, 11-18 Opus): before the first closed loop of a task the A40 has not evaluated yet (card
# A40-prep-<task>, CPU only): (1) its official scene bank is here and complete (100 scenes; the banks came with the
# 5090 delta, delta_lite.sh group "scenes"); (2) the instruction text the closed loop reads with MWAM_TEXT_SOURCE=cache
# (text_fetch.py: RECORDS.json + one episode's encodings.pt from the cache relay, sha256 against its manifest); (3) the
# text fingerprint, to compare with any other machine. Stops at the first failure (exit 1, reason printed).
#   bash /workspace/FastWAM-memory2/scripts/fullft/a40_prep_task.sh battery_try
set -u
R=/workspace/FastWAM-memory2
cd $R
T=${1:?task}
B=outputs/memory_v2/closed_loop/scenes_seed42_n100_$T
echo "[prep] $(date '+%F %T') $T; disk: $(df -h $R/outputs | tail -1)"
/opt/mwam/bin/python scripts/memory_v2/official_scenes.py complete $B $T 100 \
  || { echo "[prep] $T: no complete scene bank at $B: stop"; exit 1; }
P=/opt/hf-tools/bin/python; [ -x $P ] || P=/opt/mwam/bin/python
$P scripts/fullft/text_fetch.py --task $T || { echo "[prep] $T: text fetch failed"; exit 1; }
PYTHONPATH=src /opt/mwam/bin/python scripts/fullft/text_fetch.py --task $T --fingerprint || { echo "[prep] $T: fingerprint failed"; exit 1; }
echo "[prep] $(date '+%F %T') $T ready"
