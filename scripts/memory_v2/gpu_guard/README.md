# GPU guard (host side)

`deploy_guard.sh` (generated from `guard.py`, which it embeds) recreates the `hhy-gpu2-guard`
container on the host. While our training container uses host GPUs 1/2/4, any other compute
process that appears on them is SIGKILLed. A GPU is released 10 min after our jobs leave it
(30 min if they never appear); when all are released the guard writes `/var/lib/hhy-gpu2-guard/state/DONE`
and exits 0, and `--restart on-failure` leaves the container stopped (a crash restarts it).

```bash
# on the host
docker cp 6e4b37a15066:/workspace/FastWAM-memory2/scripts/memory_v2/gpu_guard/deploy_guard.sh /tmp/deploy_guard.sh
GUARD_UUIDS=GPU-aaa,GPU-bbb bash /tmp/deploy_guard.sh   # UUIDs from nvidia-smi -L; DRY_RUN=1 to only log
docker logs -f --tail 50 hhy-gpu2-guard      # KILL / RELEASE / 10-min status lines
# a second, independent guard (the existing hhy-gpu2-guard is left alone), e.g. for one more GPU
GUARD_NAME=hhy-gpu0-guard GUARD_UUIDS=GPU-ccc bash /tmp/deploy_guard.sh
# hold GPUs until a fixed deadline (idle time ignored; all released at the deadline):
RELEASE_AT=2026-10-27T00:00:00+08:00 GUARD_UUIDS=GPU-aaa,GPU-bbb bash /tmp/deploy_guard.sh
# manual teardown at any time
docker update --restart=no hhy-gpu2-guard && docker stop hhy-gpu2-guard
```
It refuses to start while another user's process is already on a guarded GPU (it would be killed at
once); `GRANDFATHER_EXISTING=1` deploys anyway and never kills those processes (new arrivals still are);
`ALLOW_KILL_EXISTING=1` deploys and kills them. Regenerate `deploy_guard.sh` after editing `guard.py` (the heredoc must match the file).
