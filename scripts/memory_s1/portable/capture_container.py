"""Capture a whitelist of actual Docker metadata on the host, without secrets."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import platform
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--container", default="mwam")
    args = parser.parse_args()
    container = json.loads(subprocess.check_output(["docker", "inspect", args.container], text=True))[0]
    image = json.loads(subprocess.check_output(["docker", "image", "inspect", container["Image"]], text=True))[0]
    mount = next(m for m in container["Mounts"] if m["Destination"] == "/workspace/FastWAM")
    if mount["Type"] != "bind" or not container["State"]["Running"]:
        raise ValueError("Expected a running mwam container with a bind-mounted FastWAM checkout.")
    value = {"captured_unix": time.time(), "container_id": container["Id"], "name": container["Name"],
        "image_id": container["Image"], "image_reference": container["Config"]["Image"],
        "repo_digests": image.get("RepoDigests", []), "mounts": container["Mounts"],
        "host_os": platform.platform(), "host_kernel": platform.release(),
        "runtime": {key: container["HostConfig"].get(key) for key in
                    ("IpcMode", "NetworkMode", "Ulimits", "DeviceRequests", "ShmSize")},
        "lease_start": "See existing lease.json; capture time is not the rental start."}
    if not value["repo_digests"]:
        raise ValueError("Docker has no recorded repository digest for the running image.")
    output = Path(mount["Source"]) / "outputs/recovery_aws_h100/container-host.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2), encoding="utf-8")
    temporary.replace(output)
    print(output)


if __name__ == "__main__":
    main()
