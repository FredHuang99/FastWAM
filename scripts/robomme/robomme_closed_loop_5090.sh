#!/usr/bin/env bash
# 5090 HOST (outside the containers), 11-28 17:31 (Opus; plan v22 6.6 step 4/5: RoboMME closed loop). One GPU (G,
# default 1). The policy runs in mwam5090 (src/fastwam/fullft/robomme_policy.py), the simulator only in RoboMME's own
# image (scripts/robomme/robomme_client.py; nothing of ours is installed there, the script is mounted read-only); they
# talk over an AF_UNIX socket in a folder both see (the host folder behind mwam5090's closed-loop output folder).
#   1 waits until GPU G holds < 2000 MiB (the 5090 queue's tasks keep their GPU)
#   2 key file (random) + the policy server in mwam5090 (docker exec -d); waits for "listening" in policy.log (<= 20 min)
#   3 the client in robomme:582ab30 (docker run --rm, the same GPU for ManiSkill's renderer), RoboMME's test episodes
#   4 prints SUMMARY.json; the policy exits on the client's "close"
# Env: CK (the export inside mwam5090, required), TASK (PickXtimes), EPISODES ("" = all 50; e.g. "0 1" for a smoke),
#      EXECUTE (8), MAXSTEPS (1300), LABEL (default <export folder name>_<TASK>), G (1), IMG (robomme:582ab30).
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && CK=<export> EPISODES="0 1" nohup bash -c "$(docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/robomme_closed_loop_5090.sh)" > ~/robomme_cl.log 2>&1 &
# Log: ~/robomme_cl.log (this script), <folder>/policy.log, <folder>/client.log, <folder>/episodes.jsonl; last line DONE / FAILED.
set -u
C=mwam5090
R=/workspace/FastWAM-memory2
IMG=${IMG:-robomme:582ab30}
G=${G:-1}
CK=${CK:?CK=<export inside mwam5090>}
TASK=${TASK:-PickXtimes}
EPISODES=${EPISODES:-}
EXECUTE=${EXECUTE:-8}
MAXSTEPS=${MAXSTEPS:-1300}
LABEL=${LABEL:-$(basename "$(dirname "$CK")")_${TASK}}
IN=$R/outputs/robomme/closed_loop/$LABEL
say() { echo "[robomme-cl] $(date '+%F %T') $*"; }
fail() { say "FAILED: $*"; exit 1; }
host_path() {   # container path -> the host path behind it (longest bind-mount prefix), or empty
  local want=$1 best=0 out=""
  while read -r src dst; do
    [ -n "$src" ] || continue
    case "$want/" in "${dst%/}/"*)
      if [ ${#dst} -gt $best ]; then best=${#dst}; out="${src%/}${want#"${dst%/}"}"; fi;; esac
  done < <(docker inspect $C --format '{{range .Mounts}}{{.Source}} {{.Destination}}{{"\n"}}{{end}}')
  echo "$out"
}
say "start; code $(docker exec $C git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-60); export $CK; task $TASK; episodes ${EPISODES:-all}; execute $EXECUTE; GPU $G"
docker exec $C test -f "$CK" || fail "no $CK inside $C"
docker exec $C test -s $R/outputs/robomme/dense_robomme_v1/NORM_STATS.json || fail "no NORM_STATS.json (robomme_norm.py first)"
docker image inspect $IMG > /dev/null 2>&1 || fail "no image $IMG"
docker exec $C mkdir -p $IN || fail "mkdir $IN"
HOST_IN=$(host_path $IN); HOST_SCRIPTS=$(host_path $R/scripts/robomme)
[ -n "$HOST_IN" ] && [ -d "$HOST_IN" ] || fail "$IN is not on a host bind mount of $C (the socket folder must be shared)"
[ -n "$HOST_SCRIPTS" ] && [ -f "$HOST_SCRIPTS/robomme_client.py" ] || fail "scripts/robomme is not on a host bind mount of $C"
say "shared folder $HOST_IN (= $IN in $C); client script from $HOST_SCRIPTS"

say "===== 1 wait for GPU $G"
while true; do
  used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G 2>/dev/null | tr -d ' ')
  [ -n "$used" ] || fail "nvidia-smi cannot read GPU $G"
  [ "$used" -lt 2000 ] && break
  say "GPU $G holds $used MiB: waiting"; sleep 120
done

say "===== 2 policy server"
docker exec $C bash -c "head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n' > $IN/rpc.key" || fail "key file"
CG=$(docker exec $C bash $R/scripts/fullft/cuda_ordinal.sh $G)
docker exec -d $C bash -c "cd $R && CUDA_VISIBLE_DEVICES=$CG PYTHONPATH=src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True /opt/mwam/bin/python -m fastwam.fullft.robomme_policy --checkpoint $CK --socket $IN/rpc.sock --key-file $IN/rpc.key --execute $EXECUTE --log $IN > $IN/policy.log 2>&1"
for i in $(seq 1 120); do
  docker exec $C grep -q "listening on" $IN/policy.log 2>/dev/null && break
  if docker exec $C grep -q "Traceback\|Error" $IN/policy.log 2>/dev/null && ! docker exec $C pgrep -f robomme_policy > /dev/null; then
    docker exec $C tail -n 30 $IN/policy.log; fail "the policy server stopped before listening"
  fi
  sleep 10
done
docker exec $C grep -q "listening on" $IN/policy.log || { docker exec $C tail -n 30 $IN/policy.log; fail "no 'listening' after 20 min"; }
docker exec $C grep "\[robomme-policy\]" $IN/policy.log | head -n 2

say "===== 3 client in $IMG"
EP_ARG=""; [ -n "$EPISODES" ] && EP_ARG="--episodes $EPISODES"
docker run --rm --gpus "device=$G" -e NVIDIA_DRIVER_CAPABILITIES=compute,graphics,utility,video \
  -v "$HOST_IN":/cl -v "$HOST_SCRIPTS":/mwam:ro $IMG \
  bash -c "uv run --no-sync python /mwam/robomme_client.py --socket /cl/rpc.sock --key-file /cl/rpc.key --task $TASK $EP_ARG --max-steps $MAXSTEPS --out /cl" \
  > "$HOST_IN/client.log" 2>&1
rc=$?
tail -n 15 "$HOST_IN/client.log"
sleep 5
docker exec $C pgrep -f "robomme_policy.*$IN" > /dev/null && say "note: the policy server is still running (the client did not close it)"
[ $rc -eq 0 ] && [ -s "$HOST_IN/SUMMARY.json" ] || fail "client exit $rc (logs $HOST_IN/client.log, $HOST_IN/policy.log)"
say "SUMMARY $(tr -d '\n ' < "$HOST_IN/SUMMARY.json")"
say "DONE ($HOST_IN)"
