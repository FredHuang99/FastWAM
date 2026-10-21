#!/usr/bin/env bash
# AWS p5.4xlarge host (Deep Learning Base AMI with Single CUDA, Ubuntu 24.04), user ubuntu.
# Checks the GPU/driver, puts all data on the instance-store NVMe, starts the mwam-h100 container.
# No disk is formatted and no driver is changed.
set -euo pipefail
IMAGE=${IMAGE:-nvcr.io/nvidia/pytorch:25.11-py3}      # same image family as the dense receipt (torch 2.10 nv25.11)
BASE=/mnt/fastwam/hhy/h100
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
[[ "$(nvidia-smi --query-gpu=name --format=csv,noheader)" == *H100* ]] || { echo 'expected one H100'; exit 1; }
driver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1)
[[ "$(printf '%s\n' 580.0 "$driver" | sort -V | head -1)" == 580.0 ]] || { echo "driver $driver < 580: $IMAGE (CUDA 13) will not start"; exit 1; }
if ! mountpoint -q /mnt/fastwam; then
  mountpoint -q /opt/dlami/nvme || { echo 'no /opt/dlami/nvme mount; send: lsblk; findmnt'; exit 1; }
  sudo mkdir -p /mnt/fastwam && sudo mount --bind /opt/dlami/nvme /mnt/fastwam
fi
df -hT /mnt/fastwam /
sudo mkdir -p "$BASE" && sudo chown "$(id -u):$(id -g)" "$BASE"
mkdir -p "$BASE/hf/payload/workspace/FastWAM" "$BASE/hf/payload/workspace/FastWAM-memory2" \
         "$BASE/hf/payload/restore-tmp" "$BASE/hf/payload/root/dot-cache-huggingface" "$BASE/tmp" \
         "$BASE/envs/mwam" "$BASE/envs/hf-tools" "$BASE/envs/miniforge" "$BASE/envs/rmbench-env"
# Docker images live on the root EBS: keep >= 60 GiB free there (launch with a 200 GiB root volume).
sudo docker info --format 'docker root {{.DockerRootDir}}'
df -h "$(sudo docker info --format '{{.DockerRootDir}}')"
sudo docker pull "$IMAGE"
if sudo docker container inspect mwam-h100 >/dev/null 2>&1; then
  echo 'mwam-h100 exists: sudo docker start mwam-h100 && sudo docker exec -it mwam-h100 bash'; exit 0
fi
sudo docker run -d --name mwam-h100 --restart unless-stopped --gpus all --ipc=host --network=host \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics -e TMPDIR=/mnt/tmp \
  -v "$BASE/hf:/mnt/hf" -v "$BASE/tmp:/mnt/tmp" \
  -v "$BASE/hf/payload/workspace/FastWAM:/workspace/FastWAM" \
  -v "$BASE/hf/payload/workspace/FastWAM-memory2:/workspace/FastWAM-memory2" \
  -v "$BASE/hf/payload/restore-tmp:/restore-tmp" \
  -v "$BASE/hf/payload/root/dot-cache-huggingface:/root/.cache/huggingface" \
  -v "$BASE/envs/mwam:/opt/mwam" -v "$BASE/envs/hf-tools:/opt/hf-tools" \
  -v "$BASE/envs/miniforge:/opt/miniforge" -v "$BASE/envs/rmbench-env:/opt/rmbench-env" \
  -w /workspace/FastWAM-memory2 "$IMAGE" sleep infinity
sudo docker exec mwam-h100 python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0))"
echo 'ready: sudo docker exec -it mwam-h100 bash'
