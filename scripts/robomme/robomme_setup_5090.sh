#!/usr/bin/env bash
# 5090 HOST (outside the containers), 11-22 18:40 (Opus; plan v19 R0 step 1; user 18:36: install RoboMME in a separate
# environment). The separate environment is RoboMME's own Docker image, built from its repository at a pinned commit;
# the mwam5090 container, its Python and its files are not touched. RoboMME's code runs only inside that image.
#   1 clone RoboMME/robomme_benchmark into $D/robomme_benchmark at 582ab30 (Apache-2.0; HEAD of main on 11-22, read
#     before this script was written)
#   2 docker build -t robomme:582ab30 (its Dockerfile: CUDA 12.8 base, Python 3.11, torch 2.9.1, the ManiSkill fork
#     pinned in uv.lock)
#   3 smoke: its scripts/run_example.py on PickXtimes, test episode 0, joint_angle, its built-in sample actions (small
#     jitter in place, so the episode ends by time-out) on GPU $G; prints the task goal and outcome, saves a video in
#     $D/runs
#   4 sizes of the two copies of the training data on Hugging Face, no download: Yinpei/robomme_data_h5 (HDF5, with
#     depth) and lerobot/robomme (LeRobot v3.0, video), via the mwam5090 container's hf-tools Python
# Env: D (default /mnt/hf/robomme if /mnt/hf exists, else ~/robomme), G (GPU, default 1; the smoke needs < 2 GB).
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && nohup bash -c "$(docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/robomme_setup_5090.sh)" > ~/robomme_setup.log 2>&1 &
# Log: ~/robomme_setup.log ; the last line says DONE or FAILED.
set -u
if [ -d /mnt/hf ]; then D=${D:-/mnt/hf/robomme}; else D=${D:-$HOME/robomme}; fi
G=${G:-1}
COMMIT=582ab30fa95ce5503261e03dbc7d4f37937dc39e
IMG=robomme:582ab30
say() { echo "[robomme] $(date '+%F %T') $*"; }
fail() { say "FAILED: $*"; exit 1; }
mkdir -p $D/runs || fail "cannot create $D"
say "start on $(hostname); dir $D ($(df -h $D | tail -n 1 | awk '{print $4}') free); GPU $G"
command -v docker > /dev/null || fail "no docker on this host"

say "===== 1 clone at ${COMMIT:0:7}"
if [ ! -d $D/robomme_benchmark/.git ]; then
  git clone -q https://github.com/RoboMME/robomme_benchmark $D/robomme_benchmark || fail "git clone"
fi
git -C $D/robomme_benchmark fetch -q origin $COMMIT 2>/dev/null || git -C $D/robomme_benchmark fetch -q origin
git -C $D/robomme_benchmark checkout -q $COMMIT || fail "checkout $COMMIT"
say "checked out $(git -C $D/robomme_benchmark log --oneline -1 | cut -c1-70); license: $(head -n 1 $D/robomme_benchmark/LICENSE | tr -s ' ')"

say "===== 2 docker build $IMG (first time: about 10-30 min, several GB)"
if docker image inspect $IMG > /dev/null 2>&1; then say "$IMG exists"
else
  (cd $D/robomme_benchmark && docker build -t $IMG . > $D/BUILD.log 2>&1) || { tail -n 25 $D/BUILD.log; fail "docker build (log $D/BUILD.log)"; }
  say "built: $(docker image inspect $IMG --format '{{.Size}}' | awk '{printf "%.1f GB", $1/1e9}')"
fi

say "===== 3 smoke: PickXtimes test episode 0, joint_angle, sample actions, GPU $G"
used=$(nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader -i $G 2>/dev/null)
say "GPU $G now: $used"
docker run --rm --gpus "device=$G" -e NVIDIA_DRIVER_CAPABILITIES=compute,graphics,utility,video -v $D/runs:/app/runs $IMG \
  bash -c 'uv run --no-sync python -c "import torch, sapien, mani_skill; print(\"versions torch\", torch.__version__, \"sapien\", sapien.__version__, \"mani_skill\", mani_skill.__version__)" && uv run --no-sync scripts/run_example.py --dataset test --task-id PickXtimes --episode-idx 0 --action-space-type joint_angle' \
  > $D/SMOKE.log 2>&1 || { tail -n 30 $D/SMOKE.log; fail "smoke (log $D/SMOKE.log)"; }
grep -E "^versions|Task goal|Outcome|Saved video|Running task" $D/SMOKE.log
grep -c "^Action:" $D/SMOKE.log | sed 's/^/[robomme] steps taken: /'

say "===== 4 training data sizes on Hugging Face (no download)"
docker exec -i mwam5090 /opt/hf-tools/bin/python - <<'PY' || say "(size listing failed; not needed for the smoke)"
from collections import defaultdict
from huggingface_hub import HfApi
api = HfApi()
for repo in ("Yinpei/robomme_data_h5", "lerobot/robomme"):
    try:
        info = api.dataset_info(repo, files_metadata=True)
    except Exception as e:                                        # noqa: BLE001
        print(f"{repo}: {type(e).__name__}: {str(e)[:200]}"); continue
    files = [(s.rfilename, s.size or 0) for s in info.siblings]
    tot = sum(x for _, x in files)
    print(f"{repo}: {len(files)} files, {tot / 1e9:.1f} GB, last modified {info.last_modified}")
    by = defaultdict(int)
    for f, x in files:
        key = next((t for t in ("BinFill", "PickXtimes", "SwingXtimes", "StopCube") if t in f), None)
        if key: by[key] += x
    if by: print("   counting tasks:", {k: f"{v / 1e9:.1f} GB" for k, v in sorted(by.items())})
    print("   first files:", [f for f, _ in files[:6]])
PY
say "DONE (image $IMG; logs $D/BUILD.log, $D/SMOKE.log; video under $D/runs)"
