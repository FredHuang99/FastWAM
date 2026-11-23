#!/usr/bin/env bash
# mwam5090, 11-23 15:00 (Opus; user 14:53: find the root cause of the history failing on observe_and_pickup; the
# rearrange timely writer approved). Read-only for every model; nothing is deleted. GPU: PF_GPUS (default 1), waits
# until it is empty (< 2000 MiB). Steps:
#   1 rearrange timely writer's event file: task_v3c_events.py --task rearrange_blocks --relay (CPU; the H100 line
#     rearr_v3c starts from it)
#   2 observe_and_pickup, closed loop, does the model's frame 0 show the reference? One episode (scene 1, obs_ar e30,
#     30 targets) with the camera frames saved; in the reference box (x 0.395-0.675, y 0.06-0.34 of the head camera)
#     the share of wall-coloured pixels in frame 0 and in the last frame; a side-by-side PNG for viewing
#     (outputs/fullft/align/F0CHECK.png)
#   3 obs_probe.py on obs_ar e30 and obs_arprop e30: action loss in the choice window (before the first grasp) with
#     frame 0 true / swapped with another demo's frame 0 / no history -> is frame 0 used at the choice?
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/diag_1123_5090.sh
# Own log: outputs/fullft/DIAG_1123_5090_<time>.txt ; the result lines start with "[v3c]", "F0CHECK", "OBS PROBE".
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
F=$R/outputs/fullft
LOG=$F/DIAG_1123_5090_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[diag] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
cd $R
export PYTHONPATH=$R/src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True MWAM_OIDN_LIB=/opt/oidn-2.0.1-sass120/lib MWAM_TEXT_SOURCE=cache
unset MWAM_LEDGER MWAM_NOISE_SALT MWAM_LEDGER_LAG MWAM_EVENT_DELTA MWAM_EVENT_MIN_PATH MWAM_EVENT_PROVISIONAL MWAM_OBJECT_LOG
PY=/opt/mwam/bin/python
G=${PF_GPUS:-1}
say() { echo "[diag] $(date '+%F %T') $*"; }
say "start; checkout $(git -c safe.directory='*' log --oneline -1 | cut -c1-60); GPU $G"

say "===== 1 rearrange timely writer's event file"
CUDA_VISIBLE_DEVICES= $PY scripts/fullft/task_v3c_events.py --task rearrange_blocks --relay || say "step 1 FAILED (the H100 line waits)"

export_of() {
  local E=$F/exports/$1 M=/mnt/hf/relay_mirror/memwam-fullft/exports/$1
  [ -f $E/export_e30.pt ] || E=$M
  (cd $E && sha256sum -c --quiet export_e30.pt.sha256) >&2 && echo $E/export_e30.pt
}
until u=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G | tr -d ' ') && [ "$u" -lt 2000 ]; do
  say "GPU $G in use ($u MiB); waiting 5 min"; sleep 300; done

say "===== 2 closed-loop frame 0 of observe_and_pickup (scene 1, obs_ar e30, 30 targets, frames saved)"
CK=$(export_of obs_ar_e30) || { say "no checked obs_ar_e30 export"; exit 1; }
OUT=$O/closed_loop/f0check
CUDA_VISIBLE_DEVICES=$G $PY -m fastwam.memory_v2.online run --checkpoint $CK --label obs_ar_e30 \
  --scenes $O/closed_loop/scenes_seed42_n100_observe_and_pickup --tasks observe_and_pickup --limit 1 --execute 8 \
  --max-targets 30 --record-frames --output $OUT > $O/closed_loop/f0check.log 2>&1 || say "closed loop exit code $? (log closed_loop/f0check.log)"
$PY - "$OUT" <<'PY'
import sys
from pathlib import Path
import numpy as np
from PIL import Image
heads = sorted(Path(sys.argv[1]).rglob("head_*.png"))
if not heads:
    print("F0CHECK: no saved head-camera frames found under", sys.argv[1]); sys.exit(0)
def wall_share(p):
    a = np.asarray(Image.open(p).convert("RGB")).astype(int)
    h, w = a.shape[:2]
    box = a[int(0.06 * h):int(0.34 * h), int(0.395 * w):int(0.675 * w)]
    r, g, b = box[..., 0], box[..., 1], box[..., 2]
    wall = (r > 225) & (g > 200) & (b > 200) & (r - g > 8) & (abs(g - b) < 20)
    return float(wall.mean()), box
first, last = heads[0], heads[-1]
s0, b0 = wall_share(first)
s1, b1 = wall_share(last)
print(f"F0CHECK: {len(heads)} head frames; reference box wall-coloured share: first frame {first.name} {100 * s0:.0f} %, "
      f"last frame {last.name} {100 * s1:.0f} %  (the wall should cover the box later, not at frame 0)")
out = Path("/workspace/FastWAM-memory2/outputs/fullft/align/F0CHECK.png"); out.parent.mkdir(parents=True, exist_ok=True)
im0, im1 = Image.open(first).convert("RGB"), Image.open(last).convert("RGB")
side = Image.new("RGB", (im0.width + im1.width, max(im0.height, im1.height))); side.paste(im0, (0, 0)); side.paste(im1, (im0.width, 0))
side.save(out); print("F0CHECK image:", out)
PY

say "===== 3 is frame 0 used at the choice? (obs_probe.py)"
for L in obs_ar_e30 obs_arprop_e30; do
  CK=$(export_of $L) || { say "no checked $L export: skipped"; continue; }
  CUDA_VISIBLE_DEVICES=$G $PY scripts/fullft/obs_probe.py --export $CK 2>&1 | grep -v "Warning\|warn("
done
say "DONE"
