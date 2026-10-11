"""Read progress and lease estimates without starting workers or contacting the Hub."""
from __future__ import annotations
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--run", required=True)
    args = parser.parse_args()
    root = Path(args.run)
    for name in ("TRAINING_STATUS.json", "PREPARATION.json", "LATEST_LOCAL.json", "LATEST_REMOTE.json", "BEST.json", "UPLOAD_FAILED.json"):
        path = root / name
        if path.exists():
            print(name, json.dumps(json.loads(path.read_text()), indent=2))
    metrics = root / "metrics.jsonl"
    if metrics.exists():
        last = None
        with metrics.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.endswith("\n"):
                    continue
                row = json.loads(line)
                if row.get("kind") == "train":
                    last = row
        if last:
            fields = ("step", "loss", "update_seconds", "eta_seconds", "eta_provisional",
                      "gpu_peak_gib", "lease_remaining_seconds", "lease_margin_seconds")
            print("latest_update", json.dumps({key: last.get(key) for key in fields}, indent=2))
    latest = root / "latest_log.txt"
    if latest.exists():
        log = Path(latest.read_text().strip())
        exit_file = log.with_suffix(".exit")
        print("log", log)
        print("exit", exit_file.read_text().strip() if exit_file.exists() else "not_written_yet")


if __name__ == "__main__":
    main()
