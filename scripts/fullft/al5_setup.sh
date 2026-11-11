#!/usr/bin/env bash
# A100 container 6e4b37a15066 (plan v12 AL5, written 11-11 20:30 before any AL5 run): can the A100's own closed loop
# be moved by the denoiser VERSION alone? This script prepares and checks the switch; the closed loops are the queue
# cards AL5-put-s0/s1, AL5-swap-s0/s1 (env MWAM_OIDN_LIB=/opt/oidn-2.3.3-al5/lib) and AL5-verdict.
#   1 Intel OIDN 2.3.3 (official release tarball, the same one the 5090 uses) -> /opt/oidn-2.3.3-al5. NOT /opt/oidn-2.3.3:
#     online.py loads that folder automatically, which would change every A100 run. Only runs that set MWAM_OIDN_LIB
#     load this one; nothing else in the container changes.
#   2 frame 0 of official put_back seed 4300030, default render (rt / 32 spp / OIDN), with SAPIEN's bundled 2.0.1
#     (no preload) vs the A100's own frame-0 request of 11-11 (FR-a100): is the A100 render reproducible?
#   3 the same with OIDN 2.3.3 preloaded: does the version alone reproduce the 5090's frame-0 gap (0.49 levels)?
# Readings (frame 0 only; the closed loop decides AL5):
#   step 3 has "OIDN Error" lines            -> 2.3.3 cannot run here: AL5 cannot test the hypothesis (exit 1)
#   step 2 mean |diff| > 0.05                -> the A100 render is not reproducible against its own reference (reported)
#   step 3 mean |diff| >= 0.34               -> the version alone reproduces the 5090's frame-0 gap (0.49 +- 0.15)
#   step 3 mean |diff| <= 0.10               -> the version does not change the A100's frame 0
#   otherwise                                -> partial
# GPU ${GPU:-0}, must be empty. Own log: outputs/fullft/align/AL5_SETUP_<time>.txt
#   docker exec -e GPU=1 6e4b37a15066 bash /workspace/FastWAM-memory2/scripts/fullft/al5_setup.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
A=$R/outputs/fullft/align
mkdir -p $A
LOG=$A/AL5_SETUP_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[al5] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[al5] $(date '+%F %T') ===== $*"; }
GPU=${GPU:-0}
used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i "$GPU" | tr -d ' ')
echo "GPU $GPU: $used MiB in use; checkout $(git -C $R -c safe.directory='*' log --oneline -1 | cut -c1-60)"
[ "$used" -lt 2000 ] || { echo "GPU $GPU is not empty: stopping"; exit 1; }
DEST=/opt/oidn-2.3.3-al5
URL=https://github.com/RenderKit/oidn/releases/download/v2.3.3/oidn-2.3.3.x86_64.linux.tar.gz
REF=$O/closed_loop/check_a100/x7_first_a100/on/put_back_block/seed_4300030/request_000000.pkl

step "1 OIDN 2.3.3 -> $DEST"
if [ ! -e "$DEST/lib/libOpenImageDenoise.so.2" ]; then
  mkdir -p $DEST
  curl -fL --retry 3 -o /tmp/oidn-2.3.3-al5.tar.gz "$URL" || { echo "download failed"; exit 1; }
  ls -la /tmp/oidn-2.3.3-al5.tar.gz; sha256sum /tmp/oidn-2.3.3-al5.tar.gz
  tar -xzf /tmp/oidn-2.3.3-al5.tar.gz -C $DEST --strip-components=1 || { echo "unpack failed"; exit 1; }
  rm -f /tmp/oidn-2.3.3-al5.tar.gz
fi
ls $DEST/lib | head -20
[ -e /opt/oidn-2.3.3/lib/libOpenImageDenoise.so.2 ] && echo "WARNING: /opt/oidn-2.3.3 exists on this machine: every A100 closed loop loads it (online.py OIDN_FIX)"

step "2-3 frame 0 with the bundled 2.0.1, then with 2.3.3 preloaded"
ls -la "$REF" || { echo "no A100 frame-0 reference ($REF): run FR-a100 first"; exit 1; }
SIM=${SIM_PY:-$(/opt/mwam/bin/python -c "import json; print(json.load(open('/workspace/FastWAM/outputs/s1_dense_joint_h100_v1/IDENTITY.json'))['config']['closed_loop']['simulator_python'])" 2>/dev/null)}
[ -x "$SIM" ] || SIM=""                                  # the closed loop's own simulator python (SIM_PY, else the dense config)
for py in /opt/rmbench-fused-env/bin/python /opt/rmbench-a100-env/bin/python /opt/rmbench-env/bin/python; do
  [ -n "$SIM" ] && break; [ -x "$py" ] && SIM=$py
done
[ -n "$SIM" ] || { echo "no simulator python found"; exit 1; }
echo "simulator python: $SIM"
cd /workspace/FastWAM/resources/RMBench || exit 1
declare -A MEAN OVER ERR
for v in bundled oidn233; do
  OUTLOG=$A/al5_render_$v.log
  if [ $v = oidn233 ]; then
    CUDA_VISIBLE_DEVICES=$GPU LD_PRELOAD=$DEST/lib/libOpenImageDenoise.so.2 LD_LIBRARY_PATH=$DEST/lib:${LD_LIBRARY_PATH:-} \
      $SIM -B -u $R/scripts/memory_v2/migrate/render_check.py --task put_back_block --seed 4300030 --reference "$REF" \
      --variants default > $OUTLOG 2>&1
  else
    CUDA_VISIBLE_DEVICES=$GPU $SIM -B -u $R/scripts/memory_v2/migrate/render_check.py --task put_back_block --seed 4300030 \
      --reference "$REF" --variants default > $OUTLOG 2>&1
  fi
  echo "$v: render_check exit code $?"
  ERR[$v]=$(grep -c "OIDN Error" $OUTLOG)
  J=$(grep -o "RENDER_CHECK: .*\.md" $OUTLOG | tail -1 | sed 's/^RENDER_CHECK: //; s/\.md$/.json/')
  read MEAN[$v] OVER[$v] < <(/opt/mwam/bin/python -c "import json,sys; r=json.load(open(sys.argv[1]))['default']['vs_a100']; print(round(r['mean'],3), round(r['over8'],3))" "$J" 2>/dev/null || echo "nan nan")
  echo "$v: OIDN error lines ${ERR[$v]}; frame 0 vs the A100 reference: mean |diff| ${MEAN[$v]} levels, ${OVER[$v]} % pixels > 8 ($J)"
  grep -E "^\| default" $OUTLOG
  sleep 61                                              # render_check names its report by the minute
done

step "readings"
[ "${ERR[oidn233]}" = 0 ] || { echo "READING: OIDN 2.3.3 reports errors on this GPU -> AL5 cannot test the hypothesis"; exit 1; }
/opt/mwam/bin/python - "${MEAN[bundled]}" "${MEAN[oidn233]}" <<'PY'
import math, sys
b, v = (float(x) for x in sys.argv[1:3])
if math.isnan(b) or math.isnan(v):
    print("READING: a render comparison is missing (see the logs)"); raise SystemExit(1)
print("READING (reproducibility): " + ("the A100 render reproduces its own reference" if b <= 0.05 else
      f"the A100 render is NOT reproducible against its own reference ({b:.3f} > 0.05)"))
print("READING (version alone): " + ("reproduces the 5090's frame-0 gap" if v >= 0.34 else
      "does not change the A100's frame 0" if v <= 0.10 else "partial") + f" ({v:.3f} levels; 5090 vs A100 was 0.49)")
PY
echo "AL5 SETUP OK: the AL5 closed loops can start (MWAM_OIDN_LIB=$DEST/lib)"
