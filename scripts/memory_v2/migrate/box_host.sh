#!/usr/bin/env bash
# 11-15: our two new shared NTU boxes (user in the docker group, no sudo, host folders not writable). All our data lives
# in ONE docker named volume (under the docker root) mounted with volume subpaths on the same logical paths as every
# other machine (layout of aws_host.sh: hf/payload/...). No GPU process is started; nothing outside the volume and the
# container is written.
#   a40    GPU18, 8 x A40: EVALUATION box. Image = the A100's policy stack (nvcr.io/nvidia/pytorch:24.12-py3, torch
#          2.6.0a0 nv24.12, python 3.12): the A40 (Ampere, sm_86) is checked against the A100 (sm_80) before any of
#          its numbers are used next to the A100's. Simulator: the A100-exact env (sim5090.sh SIM_PROFILE=a40).
#   h100n  gpu24, 4 x H100 NVL 94 GB: TRAINING box. Image = the H200's stack (nvcr.io/nvidia/pytorch:25.11-py3, torch
#          2.10), so a run here uses the same software as the H200 runs; 94 GB < the H200's 93.8 GiB peak at
#          micro-batch 8, so runs here use micro-batch 4 x accumulation 16 (the same 64 samples per update).
#   curl -fsSL https://raw.githubusercontent.com/FredHuang99/FastWAM/memory2/scripts/memory_v2/migrate/box_host.sh \
#     -o ~/box_host.sh && bash ~/box_host.sh a40        (or h100n)
# Then in the container: scripts/memory_v2/migrate/h100_restore.sh steps (system | download | delta | code | env | verify).
set -euo pipefail
PROFILE=${1:?a40 | h100n}
case "$PROFILE" in
  a40)   IMAGE=${IMAGE:-nvcr.io/nvidia/pytorch:24.12-py3}; VOL=${VOL:-mwam_a40}; NAME=${NAME:-mwam-a40} ;;
  h100n) IMAGE=${IMAGE:-nvcr.io/nvidia/pytorch:25.11-py3}; VOL=${VOL:-mwam_h100n}; NAME=${NAME:-mwam-h100n} ;;
  *) echo "profile must be a40 or h100n"; exit 2 ;;
esac
echo "[box] $(date '+%F %T') host $(hostname); user $(id -un); docker $(docker version --format '{{.Server.Version}}')"
nvidia-smi --query-gpu=index,name,memory.total,memory.used,driver_version --format=csv,noheader
ROOT=$(docker info --format '{{.DockerRootDir}}')
echo "CPU cores: $(nproc); RAM: $(free -g | awk '/Mem:/{print $2}') GiB; docker root: $ROOT"
# the docker root itself may not be readable for us (gpu24): fall back to its parent (a mount point we can stat)
FREE_GB=$( (df -BG --output=avail "$ROOT" 2>/dev/null || df -BG --output=avail "$(dirname "$ROOT")" 2>/dev/null) \
           | tail -1 | tr -dc '0-9' || true)
(df -h "$ROOT" 2>/dev/null || df -h "$(dirname "$ROOT")" 2>/dev/null || true) | tail -1
if [ -z "$FREE_GB" ]; then echo "[box] cannot read the free space of the docker root $ROOT: send: df -h /mnt/*"; exit 1; fi
if [ "$FREE_GB" -lt 150 ]; then echo "[box] only ${FREE_GB} GB free on the docker root: stop (the image + our data need >= 150 GB)"; exit 1; fi
echo "[box] docker root has ${FREE_GB} GB free"
echo "[box] Vulkan / GL driver pieces on the host (the container gets them through NVIDIA_DRIVER_CAPABILITIES=all):"
ls /usr/share/vulkan/icd.d/ /etc/vulkan/icd.d/ 2>&1 | sed 's/^/   /' || true
ldconfig -p | grep -E "libGLX_nvidia|libEGL_nvidia|libnvidia-glcore" | sed 's/^/   /' || echo "   (no NVIDIA GL / Vulkan driver libraries registered)"
if docker container inspect "$NAME" >/dev/null 2>&1; then
  echo "[box] $NAME exists: docker start $NAME && docker exec -it $NAME bash"; exit 0
fi
echo "[box] $(date '+%F %T') pulling $IMAGE (about 20-25 GB onto the docker root)"
docker pull -q "$IMAGE"
docker volume create "$VOL" >/dev/null
SUBS="hf/payload/workspace/FastWAM hf/payload/workspace/FastWAM-memory2 hf/payload/restore-tmp
      hf/payload/root/dot-cache-huggingface tmp envs/mwam envs/hf-tools envs/miniforge envs/rmbench-env"
docker run --rm -v "$VOL:/v" "$IMAGE" bash -c "cd /v && mkdir -p $(echo $SUBS) && chmod 1777 tmp && ls"
m() { echo "--mount type=volume,src=$VOL,dst=$2,volume-subpath=$1"; }
docker run -d --name "$NAME" --restart unless-stopped --gpus all --ipc=host --network=host \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -e NVIDIA_DRIVER_CAPABILITIES=all -e TMPDIR=/mnt/tmp \
  $(m hf /mnt/hf) $(m tmp /mnt/tmp) \
  $(m hf/payload/workspace/FastWAM /workspace/FastWAM) \
  $(m hf/payload/workspace/FastWAM-memory2 /workspace/FastWAM-memory2) \
  $(m hf/payload/restore-tmp /restore-tmp) \
  $(m hf/payload/root/dot-cache-huggingface /root/.cache/huggingface) \
  $(m envs/mwam /opt/mwam) $(m envs/hf-tools /opt/hf-tools) \
  $(m envs/miniforge /opt/miniforge) $(m envs/rmbench-env /opt/rmbench-env) \
  -w /workspace/FastWAM-memory2 "$IMAGE" sleep infinity
docker exec "$NAME" python -c "import torch, sys; print('python', sys.version.split()[0], 'torch', torch.__version__, 'cuda', torch.version.cuda, 'gpus', torch.cuda.device_count(), torch.cuda.get_device_name(0))"
docker exec "$NAME" bash -c 'ls /etc/vulkan/icd.d/ /usr/share/vulkan/icd.d/ 2>&1 | sed "s/^/   container ICD: /"; df -h /workspace/FastWAM-memory2 | tail -1'
echo "[box] $(date '+%F %T') ready: docker exec -it $NAME bash"
