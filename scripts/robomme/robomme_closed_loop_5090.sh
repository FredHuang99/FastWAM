#!/usr/bin/env bash
# 5090 HOST (outside the containers), 11-28 (Opus; plan v22 6.6 steps 4/5: RoboMME closed loop). One GPU (G, default
# 1). The policy runs in mwam5090 (src/fastwam/fullft/robomme_policy.py), the simulator only in RoboMME's own image
# (scripts/robomme/robomme_client.py, copied out of mwam5090 into a host folder and mounted; nothing of ours is
# installed in the image). They talk over TCP on 127.0.0.1: the client container joins mwam5090's network namespace
# (docker run --network container:mwam5090), so no shared folder is needed; the auth key is random per run.
#   1 waits until no 5090-queue task runs on GPU G and G holds < 2000 MiB; then pauses the 5090 queue (Q5090_STOP: no
#     new task starts; running ones continue) and checks again after 150 s (a queue round already in progress may
#     still have started one: then it resumes the queue and waits again)
#   2 the policy server in mwam5090 (docker exec -d); waits for "listening" in its log (<= 25 min)
#   3 the client in robomme:582ab30 on the same GPU (ManiSkill's renderer), RoboMME's test episodes, ee_pose, 1300 steps
#   4 prints SUMMARY.json; the server exits on the client's "close"; the 5090 queue is resumed on every exit path
# Env: CK (the export inside mwam5090, required), TASK (PickXtimes), EPISODES ("" = all 50; "0 1" for a smoke),
#      EXECUTE (8), MAXSTEPS (1300), LABEL (default <export folder name>_<TASK>), G (1), PORT (47613), IMG.
#   docker exec mwam5090 bash -c 'cd /workspace/FastWAM-memory2 && git -c safe.directory="*" pull -q --ff-only origin memory2' && CK=<export> EPISODES="0 1" nohup bash -c "$(docker exec mwam5090 cat /workspace/FastWAM-memory2/scripts/robomme/robomme_closed_loop_5090.sh)" > ~/robomme_cl.log 2>&1 &
# Logs: ~/robomme_cl.log (this script; last line DONE / FAILED), ~/robomme_cl/<LABEL>/client.log, episodes.jsonl,
#       SUMMARY.json; inside mwam5090 outputs/robomme/closed_loop/<LABEL>/policy.log and decisions.jsonl.
set -u
C=mwam5090
R=/workspace/FastWAM-memory2
IMG=${IMG:-robomme:582ab30}
G=${G:-1}
PORT=${PORT:-47613}
CK=${CK:?CK=<export inside mwam5090>}
TASK=${TASK:-PickXtimes}
EPISODES=${EPISODES:-}
EXECUTE=${EXECUTE:-8}
MAXSTEPS=${MAXSTEPS:-1300}
LABEL=${LABEL:-$(basename "$(dirname "$CK")")_${TASK}}
IN=$R/outputs/robomme/closed_loop/$LABEL
HO=$HOME/robomme_cl/$LABEL
PAUSED=0
say() { echo "[robomme-cl] $(date '+%F %T') $*"; }
resume() { [ $PAUSED = 1 ] && docker exec $C bash -c "rm -f $R/outputs/fullft/Q5090_STOP $R/outputs/fullft/Q5090_PAUSED" && say "5090 queue resumed"; PAUSED=0; }
fail() { say "FAILED: $*"; exit 1; }
trap 'resume' EXIT
qgpu() {    # ids of live 5090-queue tasks on GPU $G
  docker exec $C bash -c "for f in $R/outputs/fullft/q5090/*.running; do [ -f \"\$f\" ] || continue; set -- \$(cat \"\$f\"); kill -0 \$1 2>/dev/null && [ \"\$2\" = gpu$G ] && basename \"\$f\" .running; done" 2>/dev/null
}
used() { nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i $G 2>/dev/null | tr -d ' '; }
say "start; code $(docker exec $C git -c safe.directory='*' -C $R log --oneline -1 | cut -c1-60); export $CK; task $TASK; episodes ${EPISODES:-all}; execute $EXECUTE; GPU $G; port $PORT"
docker exec $C test -f "$CK" || fail "no $CK inside $C"
docker exec $C test -s $R/outputs/robomme/dense_robomme_v1/NORM_STATS.json || fail "no NORM_STATS.json (robomme_norm.py first)"
docker image inspect $IMG > /dev/null 2>&1 || fail "no image $IMG"
mkdir -p "$HO" && docker exec $C mkdir -p $IN || fail "mkdir"
docker cp $C:$R/scripts/robomme/robomme_client.py "$HO/robomme_client.py" || fail "docker cp of the client script"

say "===== 1 GPU $G free of other work"
while true; do
  busy=$(qgpu); u=$(used)
  [[ "$u" =~ ^[0-9]+$ ]] || fail "nvidia-smi cannot read GPU $G"
  if [ -z "$busy" ] && [ "$u" -lt 2000 ]; then
    docker exec $C touch $R/outputs/fullft/Q5090_STOP; PAUSED=1
    say "5090 queue paused (Q5090_STOP); checking again in 150 s"; sleep 150
    busy=$(qgpu); u=$(used)
    [ -z "$busy" ] && [[ "$u" =~ ^[0-9]+$ ]] && [ "$u" -lt 2000 ] && break
    say "a queue task started meanwhile ($busy, $u MiB)"; resume
  else
    say "GPU $G: ${busy:-no queue task} / $u MiB: waiting"
  fi
  sleep 120
done

say "===== 2 policy server"
KEY=$(head -c 24 /dev/urandom | od -An -tx1 | tr -d ' \n')
CG=$(docker exec $C bash $R/scripts/fullft/cuda_ordinal.sh $G)
docker exec -d -e MWAM_RPC_KEY=$KEY $C bash -c "cd $R && CUDA_VISIBLE_DEVICES=$CG PYTHONPATH=src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True exec /opt/mwam/bin/python -m fastwam.fullft.robomme_policy --checkpoint $CK --socket 127.0.0.1:$PORT --execute $EXECUTE --log $IN > $IN/policy.log 2>&1"
ok=0
for i in $(seq 1 150); do
  docker exec $C grep -q "listening on" $IN/policy.log 2>/dev/null && { ok=1; break; }
  if [ $i -gt 3 ] && ! docker exec $C pgrep -f "robomme_policy.*$PORT" > /dev/null; then break; fi
  sleep 10
done
[ $ok = 1 ] || { docker exec $C tail -n 30 $IN/policy.log; fail "the policy server is not listening (log above)"; }
docker exec $C grep "\[robomme-policy\]" $IN/policy.log | head -n 3

say "===== 3 client in $IMG"
EP_ARG=""; [ -n "$EPISODES" ] && EP_ARG="--episodes $EPISODES"
docker run --rm --gpus "device=$G" --network container:$C -e NVIDIA_DRIVER_CAPABILITIES=compute,graphics,utility,video \
  -e MWAM_RPC_KEY=$KEY -v "$HO":/cl $IMG \
  bash -c "uv run --no-sync python /cl/robomme_client.py --socket 127.0.0.1:$PORT --task $TASK $EP_ARG --max-steps $MAXSTEPS --out /cl" \
  > "$HO/client.log" 2>&1
rc=$?
tail -n 15 "$HO/client.log"
sleep 5
docker exec $C pgrep -f "robomme_policy.*$PORT" > /dev/null && say "note: the policy server is still running (the client did not close it)"
docker exec $C tail -n 5 $IN/policy.log
[ $rc -eq 0 ] && [ -s "$HO/SUMMARY.json" ] || fail "client exit $rc (logs $HO/client.log; $IN/policy.log in $C)"
say "SUMMARY $(tr -d '\n ' < "$HO/SUMMARY.json")"
say "DONE ($HO)"
