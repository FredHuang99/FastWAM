#!/usr/bin/env bash
# mwam5090 container, 5090 fix F1 (11-12; the user approved downloading Intel's official OIDN 2.0.1 source):
# build Open Image Denoise 2.0.1 -- the version the A100 reference pipeline uses -- so that it runs on the RTX 5090.
# Why the bundled 2.0.1 fails there: its CUDA device accepts compute capability 7.0-9.9 only (devices/cuda/cuda_device.h
# maxSMArch = 99; the 5090 is 12.0) and it ships no PTX ("We do not generate PTX", devices/cuda/CMakeLists.txt).
# Patches (nothing else changes; same source, same embedded 2.0.1 weights, same CUTLASS sm80 kernels as the A100):
#   maxSMArch 99 -> 999; the SM70 kernel file compiled for sm_75 (CUDA 13 cannot target sm_70; never used here);
#   ARCH=sass120 (default): + sm_120 machine code;  ARCH=ptx80: + compute_80 PTX instead (the driver JITs it once).
# Steps: 1 download + sha256 check  2 patch  3 cmake + ninja (CPU only)  4 wait for an empty GPU (not while
#   d2_5090.sh runs), render frame 0 of put 4300030 with the new library, compare with the A100's 2.0.1 frame 0.
# Reading (written 11-12 before the build): the candidate passes the render step if there is no "OIDN Error" line AND
#   frame-0 mean |diff| <= 0.10 levels AND pixels > 8 levels <= 0.05 % (today 0.49 levels / 0.5 %; the two GPUs'
#   ray-tracing residual measured with the same denoiser on both is 0.064 levels).
# Own log: outputs/fullft/align/OIDN201_BUILD_<arch>_<time>.txt
#   docker exec -d mwam5090 bash /workspace/FastWAM-memory2/scripts/fullft/oidn201_build.sh
set -u
R=/workspace/FastWAM-memory2
A=$R/outputs/fullft/align
ARCH=${ARCH:-sass120}
LOG=$A/OIDN201_BUILD_${ARCH}_$(date +%Y%m%d_%H%M).txt
exec > >(tee -a "$LOG") 2>&1
trap 'rc=$?; echo "[oidn] $(date "+%F %T") finished, exit code $rc; log $LOG"' EXIT
step() { echo; echo "[oidn] $(date '+%F %T') ===== $*"; }
SRC=/opt/src
PREFIX=/opt/oidn-2.0.1-$ARCH
URL=https://github.com/RenderKit/oidn/releases/download/v2.0.1/oidn-2.0.1.src.tar.gz
SHA=328eeb9809d18e835dca7203224af3748578794784c026940c02eea09c695b90
mkdir -p $SRC && cd $SRC

step "1 download the official source"
[ -f oidn-2.0.1.src.tar.gz ] || curl -sSL -o oidn-2.0.1.src.tar.gz $URL
echo "$SHA  oidn-2.0.1.src.tar.gz" | sha256sum -c - || { echo "sha256 differs from the tarball inspected on 11-12: stopping"; exit 1; }
D=$SRC/oidn-2.0.1-$ARCH
rm -rf $D && mkdir -p $D && tar xzf oidn-2.0.1.src.tar.gz -C $D --strip-components=1

step "2 patch ($ARCH)"
cd $D
sed -i 's/static constexpr int maxSMArch = 99;/static constexpr int maxSMArch = 999;/' devices/cuda/cuda_device.h
sed -i 's/set(OIDN_NVCC_SM70_FLAGS "-gencode arch=compute_70,code=sm_70")/set(OIDN_NVCC_SM70_FLAGS "-gencode arch=compute_75,code=sm_75")/' devices/cuda/CMakeLists.txt
if [ "$ARCH" = ptx80 ]; then EXTRA="-gencode arch=compute_80,code=compute_80"; else EXTRA="-gencode arch=compute_120,code=sm_120"; fi
sed -i "s/set(OIDN_NVCC_SM90_FLAGS \"-gencode arch=compute_90,code=sm_90\")/set(OIDN_NVCC_SM90_FLAGS \"-gencode arch=compute_90,code=sm_90 $EXTRA\")/" devices/cuda/CMakeLists.txt
grep -n "maxSMArch" devices/cuda/cuda_device.h
grep -n "OIDN_NVCC_SM.._FLAGS \"" devices/cuda/CMakeLists.txt
grep -q "maxSMArch = 999" devices/cuda/cuda_device.h && grep -q "$EXTRA" devices/cuda/CMakeLists.txt || { echo "patch did not apply: stopping"; exit 1; }

step "3 build (CPU only)"
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DOIDN_DEVICE_CPU=OFF -DOIDN_DEVICE_CUDA=ON -DOIDN_APPS=OFF \
  -DOIDN_FILTER_RTLIGHTMAP=OFF -DCMAKE_INSTALL_PREFIX=$PREFIX -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc \
  > $SRC/cmake_$ARCH.log 2>&1 || { echo "cmake failed:"; tail -n 40 $SRC/cmake_$ARCH.log; exit 1; }
ninja -C build -j ${JOBS:-24} > $SRC/ninja_$ARCH.log 2>&1 || { echo "build failed:"; grep -m 15 -E "error" $SRC/ninja_$ARCH.log; tail -n 25 $SRC/ninja_$ARCH.log; exit 1; }
ninja -C build install > $SRC/install_$ARCH.log 2>&1 || { tail -n 20 $SRC/install_$ARCH.log; exit 1; }
LIB=$(dirname "$(find $PREFIX -name 'libOpenImageDenoise.so.2' | head -1)")
ls -la $LIB
[ -f $LIB/libOpenImageDenoise_device_cuda.so.2.0.1 ] || { echo "no CUDA device module installed: stopping"; exit 1; }

step "4 frame 0 of put 4300030 with the new library vs the A100's 2.0.1"
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $1 | tr -d ' '; }
G=""
until [ -n "$G" ]; do
  if ! pgrep -f "d2_509[0]" >/dev/null; then for g in 0 1; do [ "$(used $g)" -lt 2000 ] && { G=$g; break; }; done; fi
  [ -n "$G" ] || { echo "[oidn] $(date '+%F %T') no empty GPU (or d2 running); waiting"; sleep 120; }
done
SIM=/opt/rmbench-fused-env/bin/python
(cd /workspace/FastWAM/resources/RMBench && CUDA_VISIBLE_DEVICES=$G LD_PRELOAD=$LIB/libOpenImageDenoise.so.2 LD_LIBRARY_PATH=$LIB \
  $SIM -B -u $R/scripts/memory_v2/migrate/render_check.py --task put_back_block --seed 4300030 --variants default \
  > $A/oidn201_${ARCH}_render.log 2>&1)
echo "render_check exit code $? on GPU $G; OIDN error lines: $(grep -c 'OIDN Error' $A/oidn201_${ARCH}_render.log)"
grep -m 3 "OIDN Error" $A/oidn201_${ARCH}_render.log
RC=$(grep -o "RENDER_CHECK: .*\.md" $A/oidn201_${ARCH}_render.log | tail -1 | sed 's/^RENDER_CHECK: //; s/RENDER_CHECK_\(.*\)\.md$/render_check_\1/')
[ -n "$RC" ] && /opt/mwam/bin/python $R/scripts/fullft/npz_diff.py --ref a100_oidn201=$A/al2/a100_oidn201_default.npz --glob "$RC/default.npz"
echo "library folder for the closed loop: MWAM_OIDN_LIB=$LIB"
