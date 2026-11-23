#!/usr/bin/env bash
# 5090 HOST, 11-23 (Opus; scheduled task approved by the user 16:10; plan R0 section 3 "data conversion", step 1).
#   1 convert PickXtimes and BinFill (robomme_convert.py) inside RoboMME's own image robomme:582ab30, CPU only, no GPU:
#     reads $D/data/record_dataset_<Task>.h5 read-only, writes only $D/convert (per-episode .npz + .json, events files,
#     RECORDS.json, IDENTITY.json); resumable; nothing is deleted. The mwam5090 container only supplies three of our
#     files (events.py, h5_events.py, robomme_convert.py; read with docker exec ... cat) and the commit id.
#   2 Fast-WAM's LIBERO base (user 16:10 approved the download): libero_optional_idm_2cam224.pt and its
#     _dataset_stats.json from the public Hugging Face model repo yuanty/fastwam (the location Fast-WAM's README gives)
#     into mwam5090's /workspace/FastWAM/resources/base (next to the RoboTwin base), with mwam5090's hf-tools Python; a
#     file already there is kept; sha256 written next to each file. Needed later by the encoding step.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && nohup bash -c "$(docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/robomme_convert_5090.sh)" > ~/robomme_convert.log 2>&1 &
# Log: ~/robomme_convert.log ; the last line says DONE or FAILED.
set -u
if [ -d /mnt/hf ]; then D=${D:-/mnt/hf/robomme}; else D=${D:-$HOME/robomme}; fi
IMG=robomme:582ab30
C=mwam5090
R=/workspace/FastWAM-memory2
TASKS="PickXtimes BinFill"
BASE=/workspace/FastWAM/resources/base
say() { echo "[robomme-convert] $(date '+%F %T') $*"; }
fail() { say "FAILED: $*"; exit 1; }
docker image inspect $IMG > /dev/null 2>&1 || fail "no image $IMG"
for t in $TASKS; do [ -e $D/data/record_dataset_$t.h5 ] || fail "no $D/data/record_dataset_$t.h5 (robomme_data_5090.sh first)"; done
mkdir -p $D/tools $D/convert
COMMIT=$(docker exec $C git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-12)
say "start; code $COMMIT; dir $D ($(df -h $D | tail -n 1 | awk '{print $4}') free)"

say "===== 1 conversion (PickXtimes, BinFill; CPU)"
docker exec $C cat $R/src/fastwam/fullft/events.py > $D/tools/events.py || fail "copy events.py"
docker exec $C cat $R/scripts/robomme/h5_events.py > $D/tools/h5_events.py || fail "copy h5_events.py"
docker exec $C cat $R/scripts/robomme/robomme_convert.py > $D/tools/robomme_convert.py || fail "copy robomme_convert.py"
docker run --rm -v $D/data:/data:ro -v $D/tools:/tools:ro -v $D/convert:/out $IMG uv run --no-sync python \
  /tools/robomme_convert.py --data /data --out /out --metadata /app/src/robomme/env_metadata --tasks $TASKS \
  --commit "$COMMIT" || fail "robomme_convert.py"
say "converted: $(du -sh $D/convert | cut -f1) in $D/convert"

say "===== 2 Fast-WAM LIBERO base -> $C:$BASE"
HFPY=$(docker exec $C bash -c '[ -x /opt/hf-tools/bin/python ] && echo /opt/hf-tools/bin/python || echo /opt/mwam/bin/python')
docker exec $C bash -c "mkdir -p $BASE && cd $BASE && HF_HUB_DOWNLOAD_TIMEOUT=60 $HFPY - <<'PY'
import hashlib, os
from huggingface_hub import hf_hub_download
for name in ('libero_optional_idm_2cam224.pt', 'libero_optional_idm_2cam224_dataset_stats.json'):
    if os.path.exists(name):
        print('[base] kept', name, os.path.getsize(name), 'bytes')
    else:
        hf_hub_download(repo_id='yuanty/fastwam', filename=name, local_dir='.')
        print('[base] downloaded', name, os.path.getsize(name), 'bytes')
    if not os.path.exists(name + '.sha256'):
        h = hashlib.sha256()
        with open(name, 'rb') as f:
            for b in iter(lambda: f.read(1 << 24), b''):
                h.update(b)
        open(name + '.sha256', 'w').write(h.hexdigest() + '  ' + name + '\n')
    print('[base] sha256', open(name + '.sha256').read().split()[0], name)
PY" || fail "LIBERO base download (the conversion in step 1 is complete)"
say "DONE (conversion $D/convert; LIBERO base $C:$BASE)"
