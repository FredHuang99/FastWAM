#!/usr/bin/env bash
# Run on the HOST (a user that can run docker). Recreates the hhy-gpu2-guard container so it
# guards the GPUs listed in GUARD_UUIDS for the jobs of container $OWNER_REF:
#   - any compute process on those GPUs that is not from $OWNER_REF is SIGKILLed;
#   - a GPU is released 10 min after our jobs leave it (or 30 min if they never show up);
#   - when all are released the guard exits 0 and, with --restart on-failure, stays stopped.
# GPUs are given by UUID (identical on host and in containers; indices differ between them):
#   GUARD_UUIDS=GPU-aaa,GPU-bbb bash deploy_guard.sh
# Generated from scripts/memory_v2/gpu_guard/guard.py (embedded below, written to $DIR/guard.py).
(
set -euo pipefail

NAME=hhy-gpu2-guard
DIR=/var/lib/hhy-gpu2-guard
IMAGE=eec0906cea58
OWNER_REF="${OWNER_REF:-6e4b37a15066}"     # our training container (id or name)
RELEASE_AFTER_SECONDS="${RELEASE_AFTER_SECONDS:-600}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-1800}"
DRY_RUN="${DRY_RUN:-0}"
: "${GUARD_UUIDS:?set GUARD_UUIDS=GPU-...,GPU-... (UUIDs from nvidia-smi -L)}"

HOST_GPUS="$(nvidia-smi -L)"
IFS=, read -r -a UUIDS <<< "$GUARD_UUIDS"
for U in "${UUIDS[@]}"; do
    LINE="$(grep -F "$U" <<< "$HOST_GPUS" || true)"
    case "$LINE" in
        "") echo "UUID $U 不在本机 nvidia-smi -L 中；停止。"; exit 1 ;;
        *Display*) echo "UUID $U 是显示卡：$LINE；停止。"; exit 1 ;;
        *) echo "guard: $LINE" ;;
    esac
done
OWNER="$(docker inspect -f '{{.Id}}' "$OWNER_REF")"
echo "owner container: $OWNER"

# Install guard.py (old one backed up) and clear a previous DONE marker, via the guard image itself.
docker run --rm -i --network none --user 0:0 --entrypoint python3 -v "$DIR:/d" "$IMAGE" -c '
import os, shutil, sys, time
os.makedirs("/d/state", exist_ok=True)
if os.path.exists("/d/guard.py"):
    shutil.copy2("/d/guard.py", "/d/guard.py.bak." + time.strftime("%Y%m%d-%H%M%S"))
with open("/d/guard.py.new", "w") as f:
    f.write(sys.stdin.read())
os.replace("/d/guard.py.new", "/d/guard.py")
if os.path.exists("/d/state/DONE"):
    os.remove("/d/state/DONE")
print("installed /d/guard.py", os.path.getsize("/d/guard.py"), "bytes")
' <<'GUARD_PY'
"""GPU guard: keep our GPUs for our container's jobs, then step aside.

Runs in a small helper container started with --pid=host, CAP_KILL and the guarded
GPUs (see deploy_guard.sh). Every POLL_SECONDS it lists the compute processes on the
guarded GPUs (nvidia-smi, host PIDs) and

  * SIGKILLs any process whose cgroup does not belong to OWNER_CONTAINER_ID;
  * releases a GPU once our container has had no process on it for
    RELEASE_AFTER_SECONDS after having used it (or never used it within
    STARTUP_TIMEOUT_SECONDS) - from then on that GPU is not touched;
  * when every GPU is released: writes /state/DONE and exits 0. The container runs
    with --restart on-failure, so a clean exit stops it for good (a crash restarts it,
    and a restart that finds /state/DONE exits 0 immediately).

Environment
  GUARD_GPU_UUIDS            comma-separated GPU UUIDs to guard (required)
  OWNER_CONTAINER_ID         full 64-hex id of the container whose processes are ours (required)
  POLL_SECONDS               default 2
  RELEASE_AFTER_SECONDS      default 600
  STARTUP_TIMEOUT_SECONDS    default 1800
  DRY_RUN                    1 = log what would be killed, kill nothing
"""
import os
import signal
import subprocess
import sys
import time

STATE = os.environ.get("STATE_DIR", "/state")


def log(message):
    print(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message, flush=True)


def compute_apps():
    """[(gpu_uuid, pid, used_mib, name)] from nvidia-smi (host PIDs with --pid=host)."""
    out = subprocess.run(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid,used_memory,process_name",
                          "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=30, check=True).stdout
    apps = []
    for line in out.strip().splitlines():
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 2 or not parts[1].isdigit():
            continue
        used = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else -1
        apps.append((parts[0], int(parts[1]), used, ",".join(parts[3:]) if len(parts) > 3 else ""))
    return apps


def read(path):
    try:
        with open(path, "rb") as f:
            return f.read().decode(errors="replace")
    except OSError:
        return None


def process_info(pid):
    cgroup = read(f"/proc/{pid}/cgroup")
    if cgroup is None:
        return None
    stat = read(f"/proc/{pid}/stat") or ""
    status = read(f"/proc/{pid}/status") or ""
    uid = next((line.split()[1] for line in status.splitlines() if line.startswith("Uid:")), "?")
    cmdline = (read(f"/proc/{pid}/cmdline") or "").replace("\0", " ").strip()
    start = stat.rsplit(")", 1)[-1].split()[19] if ")" in stat else "?"
    return {"cgroup": cgroup, "uid": uid, "cmdline": cmdline[:300], "start": start}


class Guard:
    def __init__(self, uuids, owner, release_after=600.0, startup_timeout=1800.0, dry_run=False,
                 apps=compute_apps, info=process_info, kill=os.kill, clock=time.time):
        if len(owner) < 12:
            raise ValueError("OWNER_CONTAINER_ID must be the container id (64 hex chars preferred).")
        self.owner = owner
        self.release_after = release_after
        self.startup_timeout = startup_timeout
        self.dry_run = dry_run
        self.apps, self.info, self.kill, self.clock = apps, info, kill, clock
        now = clock()
        self.gpus = {u: {"start": now, "seen": False, "last_ours": None, "released": False, "kills": 0} for u in uuids}

    def ours(self, info):
        return self.owner in info["cgroup"]

    def step(self):
        now = self.clock()
        apps = self.apps()
        for uuid, g in self.gpus.items():
            if g["released"]:
                continue
            for _gpu, pid, used, name in (a for a in apps if a[0] == uuid):
                if pid <= 1 or pid == os.getpid():
                    continue
                info = self.info(pid)
                if info is None:                       # already gone
                    continue
                if self.ours(info):
                    g["seen"], g["last_ours"] = True, now
                    continue
                again = self.info(pid)                 # re-check right before killing (PID reuse)
                if again is None or self.ours(again) or again["start"] != info["start"]:
                    continue
                verb = "WOULD KILL" if self.dry_run else "KILL"
                log(f"{verb} pid={pid} uid={info['uid']} gpu={uuid} used={used}MiB name={name} cmd={info['cmdline']!r}")
                if not self.dry_run:
                    try:
                        self.kill(pid, signal.SIGKILL)
                        g["kills"] += 1
                    except ProcessLookupError:
                        pass
                    except PermissionError as error:
                        log(f"cannot kill pid={pid}: {error}")
            if g["seen"] and now - g["last_ours"] >= self.release_after:
                g["released"] = True
                log(f"RELEASE {uuid}: our jobs left it {now - g['last_ours']:.0f}s ago (kills={g['kills']})")
            elif not g["seen"] and now - g["start"] >= self.startup_timeout:
                g["released"] = True
                log(f"RELEASE {uuid}: none of our jobs appeared within {self.startup_timeout:.0f}s")
        return all(g["released"] for g in self.gpus.values())

    def status(self):
        now = self.clock()
        parts = []
        for uuid, g in self.gpus.items():
            state = "released" if g["released"] else ("guarding" if g["seen"] else "waiting")
            idle = "" if g["last_ours"] is None else f" idle={now - g['last_ours']:.0f}s"
            parts.append(f"{uuid[:12]} {state}{idle} kills={g['kills']}")
        return "; ".join(parts)


def main():
    done = os.path.join(STATE, "DONE")
    if os.path.exists(done):
        log(f"{done} exists: guard already finished; exiting 0 (container stays stopped).")
        return 0
    uuids = [u.strip() for u in os.environ["GUARD_GPU_UUIDS"].split(",") if u.strip()]
    guard = Guard(uuids, os.environ["OWNER_CONTAINER_ID"].strip(),
                  release_after=float(os.environ.get("RELEASE_AFTER_SECONDS", "600")),
                  startup_timeout=float(os.environ.get("STARTUP_TIMEOUT_SECONDS", "1800")),
                  dry_run=os.environ.get("DRY_RUN", "0") == "1")
    poll = float(os.environ.get("POLL_SECONDS", "2"))
    log(f"guarding {uuids} for container {guard.owner[:12]} (release after {guard.release_after:.0f}s idle, "
        f"startup timeout {guard.startup_timeout:.0f}s, dry_run={guard.dry_run})")
    last_status = 0.0
    while True:
        finished = guard.step()
        if time.time() - last_status >= 600:
            log("status: " + guard.status())
            last_status = time.time()
        if finished:
            log("all GPUs released; writing DONE and exiting 0 (on-failure restart policy will not restart).")
            try:
                os.makedirs(STATE, exist_ok=True)
                with open(done, "w") as f:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
            except OSError as error:
                log(f"could not write {done}: {error}")
            return 0
        time.sleep(poll)


if __name__ == "__main__":
    sys.exit(main())
GUARD_PY

# Replace the old guard container.
if docker container inspect "$NAME" >/dev/null 2>&1; then
    docker update --restart=no "$NAME" >/dev/null
    docker stop -t 20 "$NAME" >/dev/null || true
    docker rm "$NAME" >/dev/null
fi

docker run -d \
    --name "$NAME" \
    --restart on-failure \
    --pid=host \
    --user 0:0 \
    --cap-drop ALL \
    --cap-add KILL \
    --security-opt no-new-privileges \
    --security-opt apparmor=unconfined \
    --gpus "\"device=$GUARD_UUIDS\"" \
    --network none \
    --read-only \
    --tmpfs /tmp:rw,nosuid,nodev,size=64m \
    --log-driver json-file \
    --log-opt max-size=10m \
    --log-opt max-file=3 \
    -e PYTHONUNBUFFERED=1 \
    -e GUARD_GPU_UUIDS="$GUARD_UUIDS" \
    -e OWNER_CONTAINER_ID="$OWNER" \
    -e RELEASE_AFTER_SECONDS="$RELEASE_AFTER_SECONDS" \
    -e STARTUP_TIMEOUT_SECONDS="$STARTUP_TIMEOUT_SECONDS" \
    -e DRY_RUN="$DRY_RUN" \
    --mount "type=bind,src=$DIR/guard.py,dst=/guard.py,readonly" \
    --mount "type=bind,src=$DIR/state,dst=/state" \
    --entrypoint python3 \
    "$IMAGE" -u /guard.py

sleep 5
docker logs --tail 20 "$NAME"
docker inspect -f 'restart={{.HostConfig.RestartPolicy.Name}} status={{.State.Status}}' "$NAME"
)
