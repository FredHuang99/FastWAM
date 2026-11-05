#!/usr/bin/env bash
# AWS 8-GPU evaluation host (plan v7 P0): p5.48xlarge (8 x H100) or p5en.48xlarge (8 x H200), Deep Learning Base
# AMI with Single CUDA, Ubuntu 24.04, user ubuntu. Same as h100_host.sh (one H100) except: any number of H100 / H200,
# container name mwam-aws, and a CPU-count report (closed-loop throughput is bound by CPU: about 3 simulator copies
# per GPU need >= 8 cores each). No disk is formatted and no driver is changed. Then, in the container, the same
# h100_restore.sh steps (system | download | code | env | verify | simulator), and the pool with lane aws:
#   bash scripts/memory_v2/jobs/host_pool.sh start --lanes aws --gpus 0,1,2,3,4,5,6,7     (on the host, C=mwam-aws)
set -euo pipefail
IMAGE=${IMAGE:-nvcr.io/nvidia/pytorch:25.11-py3}      # same image family as the dense receipt (torch 2.10 nv25.11)
BASE=/mnt/fastwam/hhy/aws
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
names=$(nvidia-smi --query-gpu=name --format=csv,noheader)
echo "$names" | grep -Eq 'H100|H200' || { echo "expected H100 / H200 GPUs, got: $names"; exit 1; }
echo "GPUs: $(echo "$names" | wc -l)   CPU cores: $(nproc)   RAM: $(free -g | awk '/Mem:/{print $2}') GiB"
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
if sudo docker container inspect mwam-aws >/dev/null 2>&1; then
  echo 'mwam-aws exists: sudo docker start mwam-aws && sudo docker exec -it mwam-aws bash'; exit 0
fi
sudo docker run -d --name mwam-aws --restart unless-stopped --gpus all --ipc=host --network=host \
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
sudo docker exec mwam-aws python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.device_count(), torch.cuda.get_device_name(0))"
echo 'ready: sudo docker exec -it mwam-aws bash   (then h100_restore.sh steps inside)'
