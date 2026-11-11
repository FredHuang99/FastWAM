#!/usr/bin/env bash
# mwam5090 container (11-11, plan v10 N1, fix A, user OK 14:06): the 5090 renders WITHOUT denoising because SAPIEN
# 3.0.0b1's bundled Open Image Denoise has no CUDA kernels for this GPU generation ("OIDN Error: unsupported device
# type: CUDA" at every render; default == rt32_none, 3.86 levels from the A100; RENDER_CHECK_20261111_1359). OIDN
# added NVIDIA Blackwell support in v2.3.3 (release notes). This script
#   1 shows how pysapien gets OIDN (separate shared library or built in): find / ldd / readelf
#   2 downloads Intel's official oidn-2.3.3.x86_64.linux.tar.gz (github.com/RenderKit/oidn releases) to
#     /opt/oidn-2.3.3 (once; size and sha256 printed); nothing in the simulator environment is modified
#   3 re-runs render_check.py with that OIDN loaded first (LD_PRELOAD of its libOpenImageDenoise.so.2 +
#     LD_LIBRARY_PATH), variants default and rt256_none, 2 training demos
# Pre-registered reading of step 3: no "OIDN Error" lines AND default within 1.0 level (mean) of the A100 with
# < 2 % of pixels > 8 levels -> fixed (next: eq5090b closed loop, plan v10 N1); OIDN errors gone but default still
# >= 2 levels away -> denoiser runs but differs (version / weights): try fix B (high samples, no denoiser);
# OIDN errors remain -> the library is built into pysapien (step 1 shows it): fix B.
# GPU 0 only. Own log: report/OIDN_FIX_<time>.txt
#   docker exec mwam5090 bash /workspace/FastWAM-memory2/scripts/memory_v2/migrate/oidn_fix.sh
set -u
R=/workspace/FastWAM-memory2
O=$R/outputs/memory_v2
LOG=$O/report/OIDN_FIX_$(date +%Y%m%d_%H%M).txt
mkdir -p "$O/report"
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[oidn] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[oidn] $(date '+%F %T') ===== $*"; }
PY=/opt/rmbench-fused-env/bin/python
SP=/opt/rmbench-fused-env/lib/python3.10/site-packages
DEST=/opt/oidn-2.3.3
URL=https://github.com/RenderKit/oidn/releases/download/v2.3.3/oidn-2.3.3.x86_64.linux.tar.gz

step "1 how pysapien loads OIDN"
find $SP/sapien $SP/sapien.libs -name "*.so*" 2>/dev/null | sort
echo "--- ldd (denoise / oidn / tbb / cuda):"
ldd $SP/sapien/pysapien*.so 2>/dev/null | grep -i -E "denoise|oidn|tbb|cuda" || echo "(no OIDN library among pysapien's dynamic dependencies)"
echo "--- readelf dynamic section:"
readelf -d $SP/sapien/pysapien*.so 2>/dev/null | grep -i -E "rpath|runpath|needed" | head -20
echo "--- OIDN libraries anywhere:"
find / -xdev -name "libOpenImageDenoise*" 2>/dev/null | grep -v "^$DEST" | head

step "2 Intel OIDN 2.3.3 -> $DEST"
if [ ! -e "$DEST/lib/libOpenImageDenoise.so.2" ]; then
  mkdir -p $DEST && cd /tmp
  curl -fL --retry 3 -o /tmp/oidn-2.3.3.tar.gz "$URL" || { echo "download failed"; exit 1; }
  ls -la /tmp/oidn-2.3.3.tar.gz
  sha256sum /tmp/oidn-2.3.3.tar.gz
  tar -xzf /tmp/oidn-2.3.3.tar.gz -C $DEST --strip-components=1 || { echo "unpack failed"; exit 1; }
  rm -f /tmp/oidn-2.3.3.tar.gz
fi
ls -la $DEST/lib | head -30
du -sh $DEST

step "3 render_check with OIDN 2.3.3 loaded first"
cd /workspace/FastWAM/resources/RMBench
CUDA_VISIBLE_DEVICES=0 LD_PRELOAD=$DEST/lib/libOpenImageDenoise.so.2 LD_LIBRARY_PATH=$DEST/lib:${LD_LIBRARY_PATH:-} \
  $PY -B -u $R/scripts/memory_v2/migrate/render_check.py --task put_back_block --seed 4300030 \
  --variants default rt256_none --demos 2 > $O/report/oidn_fix_render.log 2>&1
echo "render_check exit code $?"
echo "OIDN error lines: $(grep -c 'OIDN Error' $O/report/oidn_fix_render.log)"
grep -v -E "OIDN Error|UserWarning|warn\(" $O/report/oidn_fix_render.log | sed -n '/## (a)/,$p'
