#!/usr/bin/env bash
set -euo pipefail
MODE="${1:?Use resources or run}"
REPO_ROOT="$(realpath "${2:?Pass the FastWAM root}")"
OUTPUT="$(realpath -m "${3:?Pass a NEW package directory}")"
CONFIG="${4:-configs/memory_s1/s1_variable_t.yaml}"
cd "$REPO_ROOT"
export FW_ROOT="$REPO_ROOT"
[[ ! -e "$OUTPUT" ]] || { echo 'Package directory already exists.' >&2; exit 1; }
# Build a configuration-derived list; every archive member stays relative to the repository.
ITEM_LIST="$(python - "$MODE" "$CONFIG" "$OUTPUT" <<'PY'
import sys
from pathlib import Path
from fastwam.memory_s1.common import load_config
from fastwam.memory_s1.eval_state import is_alive, process_identity
cfg = load_config(sys.argv[2])
root, output = Path(cfg["root"]).resolve(), Path(sys.argv[3]).resolve()
if sys.argv[1] == "resources":
    sys.path.insert(0, str(root / "scripts/memory_s1"))
    from storage_plan import resource_paths
    paths = resource_paths(cfg)
elif sys.argv[1] == "run":
    run = Path(cfg["paths"]["run"])
    pid_path = run / "launcher.pid"
    if pid_path.exists() and process_identity(int(pid_path.read_text())) is not None:
        raise RuntimeError("Complete safe stop before packaging mutable training state.")
    if not (run / "provenance/source.bundle").is_file():
        raise RuntimeError("Complete step-0 backup first; source.bundle is required.")
    paths = [root / name for name in ("src", "scripts/memory_s1", "configs", "requirements", "pyproject.toml", ".gitignore")]
    paths += [run]
else:
    raise ValueError("Unknown package mode")
for path in paths:
    logical = path.absolute()
    actual = path.resolve()
    if output == actual or actual in output.parents:
        raise ValueError("Package destination overlaps an input tree.")
    if not path.exists():
        raise FileNotFoundError(path)
    print(logical.relative_to(root))
PY
)"
mapfile -t ITEMS <<< "$ITEM_LIST"
[[ ${#ITEMS[@]} -gt 0 ]] || { echo 'Package list failed; inspect the error above.' >&2; exit 1; }
mkdir -p "$OUTPUT"
NAME="fastwam-s1-$MODE-$(date -u +%Y%m%dT%H%M%SZ)"
tar --dereference -C "$REPO_ROOT" --exclude='*/.cache/*' --exclude='*/__pycache__/*' --exclude='*.tmp' --exclude='*.sock' \
    --exclude='*.pid' --exclude='*.lock' --exclude='*/frames/*' --exclude='*/interrupted_logs/*' --exclude='*/interrupted_artifacts/*' \
    -I 'zstd -T4 -3' -cf "$OUTPUT/$NAME.tar.zst" "${ITEMS[@]}"
if [[ "$MODE" == resources ]]; then
  split --bytes=4G --numeric-suffixes=0 --suffix-length=4 "$OUTPUT/$NAME.tar.zst" "$OUTPUT/$NAME.tar.zst.part-"
  rm -- "$OUTPUT/$NAME.tar.zst"
fi
(cd "$OUTPUT"; sha256sum ./* > "$NAME.sha256")
du -h "$OUTPUT"
printf 'Package: %s\n' "$OUTPUT"
