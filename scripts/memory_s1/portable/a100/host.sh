#!/usr/bin/env bash
# Run explicitly on the new AWS Ubuntu host. No formatting or driver installation.
set -euo pipefail
[[ "$(uname -m)" == x86_64 ]]
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv
nvidia-smi topo -m
lsblk -o NAME,MODEL,SIZE,FSTYPE,MOUNTPOINTS
[[ "$(nvidia-smi --query-gpu=name --format=csv,noheader | grep -c A100)" == 8 ]] || { echo 'Expected eight A100 GPUs'; exit 1; }
nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | awk '$1 < 75000 {bad=1} END {exit bad}'
while IFS= read -r driver; do
  [[ "$(printf '%s\n' 580.95.05 "$driver" | sort -V | head -n 1)" == 580.95.05 ]] || {
    echo "Driver $driver does not meet this migration's conservative 580.95.05 policy; no driver upgrade performed"; exit 1;
  }
done < <(nvidia-smi --query-gpu=driver_version --format=csv,noheader)
command -v docker >/dev/null
sudo docker info >/dev/null
# DLAMI may already assemble the instance-store NVMe disks. Reuse only an actual mount.
if ! mountpoint -q /mnt/fastwam; then
  if mountpoint -q /opt/dlami/nvme; then
    sudo mkdir -p /mnt/fastwam
    sudo mount --bind /opt/dlami/nvme /mnt/fastwam
  else
    echo 'No existing data mount at /mnt/fastwam or /opt/dlami/nvme. Stop; send lsblk/findmnt output. No disk was formatted.'
    exit 1
  fi
fi
[[ "$(findmnt -n -o MAJ:MIN -T /mnt/fastwam)" != "$(findmnt -n -o MAJ:MIN -T /)" ]] || {
  echo 'Data path is on the root disk; stopping'; exit 1;
}
findmnt -T /mnt/fastwam
df -hT /mnt/fastwam
BASE=/mnt/fastwam/hhy/a100
sudo mkdir -p "$BASE"
sudo chown "$(id -u):$(id -g)" "$BASE"
if [[ ! -d "$BASE/FastWAM/.git" ]]; then
  GIT_TERMINAL_PROMPT=0 git clone --branch memory https://github.com/FredHuang99/FastWAM.git "$BASE/FastWAM"
fi
test -f "$BASE/FastWAM/scripts/memory_s1/portable/a100/launch.sh"
git -C "$BASE/FastWAM" rev-parse HEAD
mkdir -p "$BASE/envs" "$BASE/FastWAM/outputs/recovery_aws_a100_v1/tmp"
for name in mwam hf-tools miniforge rmbench-a100-env; do mkdir -p "$BASE/envs/$name"; done
IMAGE=nvcr.io/nvidia/pytorch:25.11-py3
sudo docker pull "$IMAGE"
DIGEST="$(sudo docker image inspect "$IMAGE" --format '{{index .RepoDigests 0}}')"
if sudo docker container inspect mwam-a100 >/dev/null 2>&1; then
  echo 'mwam-a100 already exists. Reuse it with docker start/docker exec after checking its mounts; no container changed.'
  exit 1
fi
sudo docker run -d --name mwam-a100 --gpus all --ipc=host --network=host \
  --ulimit memlock=-1 --ulimit stack=67108864 \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics \
  -e HF_HOME=/workspace/FastWAM/.cache/huggingface_a100 \
  -e TMPDIR=/workspace/FastWAM/outputs/recovery_aws_a100_v1/tmp \
  -v "$BASE/FastWAM:/workspace/FastWAM" \
  -v "$BASE/envs/mwam:/opt/mwam" -v "$BASE/envs/hf-tools:/opt/hf-tools" \
  -v "$BASE/envs/miniforge:/opt/miniforge" -v "$BASE/envs/rmbench-a100-env:/opt/rmbench-a100-env" \
  -w /workspace/FastWAM "$DIGEST" sleep infinity
sudo docker inspect mwam-a100 --format '{{json .Mounts}}' > "$BASE/FastWAM/outputs/recovery_aws_a100_v1/docker-mounts.json"
sudo docker image inspect "$DIGEST" --format '{{json .}}' > "$BASE/FastWAM/outputs/recovery_aws_a100_v1/docker-image.json"
sudo docker exec mwam-a100 git config --global --add safe.directory /workspace/FastWAM
sudo docker exec mwam-a100 python -c '
import torch
assert torch.cuda.device_count() == 8
for i in range(8):
    assert torch.cuda.get_device_capability(i) == (8, 0)
    assert torch.cuda.get_device_properties(i).total_memory >= 75 * 1024**3
    x = torch.ones(1, device=f"cuda:{i}")
    assert x.add(1).item() == 2
print("Container CUDA: eight A100 80GB devices usable")
'
printf 'Container ready: sudo docker exec -it mwam-a100 bash\n'
